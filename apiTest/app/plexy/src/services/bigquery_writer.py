"""
BigQueryWriter — persists TranscriptionRecord rows into a BigQuery table.
"""

import logging
from datetime import datetime, timezone

from src.core.config import Settings
from src.domain.models import MeetingMetadata, TranscriptionRecord

logger = logging.getLogger(__name__)


class BigQueryWriter:
    def __init__(self, bq_client, settings: Settings):
        self._client = bq_client
        self._table_id = (
            f"{settings.PROJECT_ID}"
            f".{settings.BQ_DATASET}"
            f".{settings.BQ_TABLE}"
        )

    def batch_exists(self, file_ids: list[str]) -> set[str]:
        """
        Returns the subset of file_ids that already exist in BigQuery.
        Runs a single query with an in clause instead of one query per file
        """
        if not file_ids:
            return set()

        id_list = ", ".join(f"'{fid}'" for fid in file_ids)
        query = f"SELECT file_id FROM `{self._table_id}` WHERE file_id IN ({id_list})"
        try:
            rows = list(self._client.query(query).result())
            return {row["file_id"] for row in rows}
        except Exception as exc:
            logger.error("Failed to batch-query BQ for exists check: %s", exc)
            return set()

    def write(self, file_meta: dict, text: str, meeting_meta: MeetingMetadata) -> None:
        """Build and insert a TranscriptionRecord into BigQuery."""
        record = self._build_record(file_meta, text, meeting_meta)
        self._insert(record)

    def _build_record(
        self, file_meta: dict, text: str, meeting_meta: MeetingMetadata
    ) -> TranscriptionRecord:
        now_iso = datetime.now(timezone.utc).isoformat()
        return TranscriptionRecord(
            file_id=file_meta["id"],
            file_name=file_meta.get("name", ""),
            text_content=text,
            inserted_at=now_iso,
            meeting_metadata=meeting_meta,
        )

    def _insert(self, record: TranscriptionRecord) -> None:
        logger.info("Inserting '%s' into %s", record.file_name, self._table_id)
        errors = self._client.insert_rows_json(
            self._table_id, [record.model_dump()], row_ids=[record.file_id]
        )
        if errors:
            raise RuntimeError(f"BigQuery errors for {record.file_id}: {errors}")
