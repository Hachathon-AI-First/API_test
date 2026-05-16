"""
DocsProcessor — orchestrates the Drive notification → BigQuery pipeline.

Responsibilities:
  1. Validate and route the incoming Pub/Sub notification.
  2. Determine which Google Doc(s) to process (folder or file notification).
  3. Filter for Google Meet Gemini transcripts only.
  4. Delegate text extraction + parsing to MeetParser.
  5. Delegate BigQuery persistence to BigQueryWriter.
"""

import logging
from typing import List
import time

from src.core.config import Settings
from src.connector.drive_client import DriveConnector
from src.domain.models import DriveNotification
from src.services.bigquery_writer import BigQueryWriter
from src.services.meet_parser import MeetParser

logger = logging.getLogger(__name__)

_GDOC_MIME   = "application/vnd.google-apps.document"
_FOLDER_MIME = "application/vnd.google-apps.folder"
_MEET_NAME_SUBSTRINGS = (
    "Anotações do Gemini",   # PT-BR
    "Gemini notes",          # EN
    "Notes by Gemini",       # EN alternative
    "by Gemini",             # EN catch-all
    "Google Meet notes",     # EN older format
    "Notas da reunião",      # PT older format
    "Meeting notes",         # EN older format
)


class DocsProcessor:
    """Entry point called by PubSubSubscriber for every incoming message."""

    def __init__(self, session, bq_client, settings: Settings):
        self._settings  = settings
        self._drive     = DriveConnector(session)
        self._parser    = MeetParser(session)
        self._bq_writer = BigQueryWriter(bq_client, settings)


    def process_notification(self, raw_payload: dict) -> None:
        try:
            notification = DriveNotification(**raw_payload)
        except Exception as exc:
            logger.error("Invalid Pub/Sub payload — skipping. Error: %s", exc)
            return

        logger.info("Notification: resource_id=%s state=%s", notification.resource_id, notification.state)

        if notification.state in ("sync", "remove"):
            return

        for doc_meta in self._resolve_docs(notification.resource_id):
            try:
                self._process_doc(doc_meta)
            except Exception:
                logger.exception("Failed to process doc %s.", doc_meta.get("id"))


    def _resolve_docs(self, resource_id: str) -> List[dict]:
        """Returns the Meet docs to process for a given resource_id."""
        meta = self._drive.get_file_metadata(resource_id)
        if not meta:
            logger.warning("Could not fetch metadata for %s — skipping.", resource_id)
            return []

        mime = meta.get("mimeType", "")

        if mime == _FOLDER_MIME:
            
            logger.info("Folder notification %s — waiting 5s for index to catch up...", resource_id)
            time.sleep(5)

            # Hybrid listing
            folder_docs = self._drive.list_folder_files(resource_id, mime_type=_GDOC_MIME)
            shared_docs = self._drive.list_shared_meet_files(_MEET_NAME_SUBSTRINGS)

            # Merge, dedup by file ID, keep Meet transcripts only.
            seen_ids: set = set()
            all_meet_docs = []
            for doc in folder_docs + shared_docs:
                if doc["id"] not in seen_ids and self._is_meet_transcript(doc):
                    seen_ids.add(doc["id"])
                    all_meet_docs.append(doc)

            logger.info(
                "Combined Meet transcripts visible to this account: %d "
                "(%d from folder, %d from shared name-search)",
                len(all_meet_docs), len(folder_docs), len(shared_docs),
            )

            candidate_ids = [doc["id"] for doc in all_meet_docs[:20]]
            already_synced = self._bq_writer.batch_exists(candidate_ids)

            new_docs = [doc for doc in all_meet_docs[:20] if doc["id"] not in already_synced]

            if not new_docs:
                logger.info("No un-synced Meet transcripts found in folder %s.", resource_id)
            else:
                logger.info("Found %d new Meet transcript(s) to process.", len(new_docs))

            return new_docs

        if mime != _GDOC_MIME:
            logger.info("Resource %s is not a Google Doc (mimeType=%s) — skipping.", resource_id, mime)
            return []

        if self._settings.DRIVER_FOLDER_ID not in meta.get("parents", []):
            logger.info("File %s is not in the watched folder — skipping.", resource_id)
            return []

        if not self._is_meet_transcript(meta):
            logger.info("File '%s' is not a Meet transcript — skipping.", meta.get("name"))
            return []

        # Skip if already persisted in BigQuery (guards against Pub/Sub redeliveries)
        if self._bq_writer.batch_exists([meta["id"]]):
            logger.info("File %s already exists in BigQuery — skipping.", resource_id)
            return []

        return [meta]


    def _is_meet_transcript(self, file_meta: dict) -> bool:
        name = file_meta.get("name", "").lower()
        return any(s.lower() in name for s in _MEET_NAME_SUBSTRINGS)


    def _process_doc(self, file_meta: dict) -> None:
        file_id   = file_meta["id"]
        file_name = file_meta.get("name", "")
        logger.info("Processing: '%s' (%s)", file_name, file_id)

        text, participants, meeting_date = self._parser.extract_text_and_participants(
            file_id,
            drive_fallback=self._drive.export_file_as_text,
        )
        if not text:
            logger.error("Could not extract text from %s — skipping.", file_id)
            return

        meeting_meta = self._parser.parse(text, file_name, participants, meeting_date)

        try:
            self._bq_writer.write(file_meta, text, meeting_meta)
            logger.info("Inserted '%s' into BigQuery.", file_name)
        except Exception as exc:
            logger.error("Failed to insert transcription to BigQuery for %s: %s", file_id, exc)
            raise

        
