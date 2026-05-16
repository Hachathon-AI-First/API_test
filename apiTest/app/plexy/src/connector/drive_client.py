import logging
import uuid
from typing import List, Optional

from google.auth.transport.requests import AuthorizedSession

logger = logging.getLogger(__name__)

_DRIVE_BASE = "https://www.googleapis.com/drive/v3"


class DriveConnector:
    def __init__(self, session: AuthorizedSession):
        self._session = session

    def watch_folder(
        self,
        folder_id: str,
        webhook_url: str,
        token: Optional[str] = None,
        expiration_ms: int = 604_800_000,
    ) -> dict:
        """
        Creates a push notification channel for the given folder.

        Returns a dict with channel_id, folder_id, expiration_ms and the raw
        API response.
        """
        channel_id = str(uuid.uuid4())
        body: dict = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "expiration": expiration_ms,
        }
        if token:
            body["token"] = token

        logger.info("Registering watch channel for folder %s", folder_id)

        resp = self._session.post(
            f"{_DRIVE_BASE}/files/{folder_id}/watch",
            params={"supportsAllDrives": "true"},
            json=body,
        )
        resp.raise_for_status()
        response = resp.json()

        logger.info(
            "Watch channel created: channel_id=%s resource_id=%s",
            channel_id,
            response.get("resourceId"),
        )

        return {
            "channel_id": channel_id,
            "folder_id": folder_id,
            "expiration_ms": expiration_ms,
            "response": response,
        }

    def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """
        Returns metadata for a single file.

        Returns a dict with keys: id, name, mimeType, modifiedTime, parents.
        Returns None if the file is not found or an error occurs.
        """
        try:
            resp = self._session.get(
                f"{_DRIVE_BASE}/files/{file_id}",
                params={
                    "fields": "id,name,mimeType,modifiedTime,parents",
                    "supportsAllDrives": "true",
                },
            )
            resp.raise_for_status()
            meta = resp.json()
            logger.debug("Fetched metadata for file %s: %s", file_id, meta)
            return meta
        except Exception:
            logger.exception("Failed to fetch metadata for file %s", file_id)
            return None


    def list_folder_files(
        self,
        folder_id: str,
        mime_type: str = "application/vnd.google-apps.document",
    ) -> List[dict]:
        """
        lists all files of *mime_type* that are direct children of *folder_id*,
        including files referenced by shortcuts in the folder.

        returns a list of file metadata dicts (id, name, mimeType, modifiedTime).
        """
        query = (
            f"'{folder_id}' in parents"
            f" and mimeType = '{mime_type}'"
            f" and trashed = false"
        )
        files: List[dict] = []
        page_token: Optional[str] = None

        while True:
            params: dict = {
                "q": query,
                "fields": "nextPageToken,files(id,name,mimeType,modifiedTime)",
                "orderBy": "modifiedTime desc",
                "includeItemsFromAllDrives": "true",
                "supportsAllDrives": "true",
                "corpora": "allDrives",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = self._session.get(f"{_DRIVE_BASE}/files", params=params)
                resp.raise_for_status()
                result = resp.json()
            except Exception:
                logger.exception("Failed to list files in folder %s", folder_id)
                break

            files.extend(result.get("files", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        # Resolve shortcuts that point to the target mime type.
        shortcut_targets = self._resolve_folder_shortcuts(folder_id, mime_type)
        seen_ids = {f["id"] for f in files}
        for target in shortcut_targets:
            if target["id"] not in seen_ids:
                seen_ids.add(target["id"])
                files.append(target)

        logger.info(
            "Found %d file(s) in folder %s (%d direct, %d via shortcuts)",
            len(files), folder_id,
            len(files) - len(shortcut_targets), len(shortcut_targets),
        )
        return files

    def _resolve_folder_shortcuts(
        self,
        folder_id: str,
        target_mime_type: str,
    ) -> List[dict]:
        """
        Finds shortcuts inside folder_id whose target matches
        target_mime_type, then fetches and returns the real file metadata
        for each target.
        """
        query = (
            f"'{folder_id}' in parents"
            f" and mimeType = 'application/vnd.google-apps.shortcut'"
            f" and trashed = false"
        )
        shortcuts: List[dict] = []
        page_token: Optional[str] = None

        while True:
            params: dict = {
                "q": query,
                "fields": "nextPageToken,files(id,name,shortcutDetails)",
                "includeItemsFromAllDrives": "true",
                "supportsAllDrives": "true",
                "corpora": "allDrives",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = self._session.get(f"{_DRIVE_BASE}/files", params=params)
                resp.raise_for_status()
                result = resp.json()
            except Exception:
                logger.exception("Failed to list shortcuts in folder %s", folder_id)
                break

            shortcuts.extend(result.get("files", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        if not shortcuts:
            return []

        # Resolve each shortcut to its target document.
        resolved: List[dict] = []
        for sc in shortcuts:
            details = sc.get("shortcutDetails", {})
            target_id = details.get("targetId")
            target_mime = details.get("targetMimeType", "")

            if not target_id or target_mime != target_mime_type:
                continue

            meta = self.get_file_metadata(target_id)
            if meta:
                resolved.append(meta)
                logger.debug(
                    "Resolved shortcut '%s' -> '%s' (%s)",
                    sc.get("name"), meta.get("name"), target_id,
                )

        logger.info(
            "Resolved %d shortcut(s) targeting %s in folder %s",
            len(resolved), target_mime_type, folder_id,
        )
        return resolved

    def list_shared_meet_files(
        self,
        name_substrings: tuple,
        mime_type: str = "application/vnd.google-apps.document",
    ) -> List[dict]:
        """
        Searches for Meet transcript files shared with the authenticated user,
        regardless of their parent folder.

        This is necessary because Google Meet notes created by other users
        are shared with the user but live in the organizer's Drive. From this account's
        perspective the Drive API returns parents=[] for those files, so they
        cannot be found via a folder-parent query.
        """
        name_clauses = " or ".join(
            f"name contains '{kw}'" for kw in name_substrings
        )
        query = (
            f"({name_clauses})"
            f" and mimeType = '{mime_type}'"
            f" and trashed = false"
        )
        files: List[dict] = []
        page_token: Optional[str] = None

        while True:
            params: dict = {
                "q": query,
                "fields": "nextPageToken,files(id,name,mimeType,modifiedTime)",
                "orderBy": "modifiedTime desc",
                "corpora": "user",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "false",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = self._session.get(f"{_DRIVE_BASE}/files", params=params)
                resp.raise_for_status()
                result = resp.json()
            except Exception:
                logger.exception("Failed to search shared Meet files")
                break

            files.extend(result.get("files", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        logger.info("Found %d shared Meet file(s) via name search", len(files))
        return files

    def export_file_as_text(self, file_id: str) -> Optional[str]:
        """
        Exports a Google Doc as plain text using the Drive export endpoint.
        This is a fallback for when the Docs API is unavailable.
        Returns the plain-text content or None on error.
        """
        try:
            resp = self._session.get(
                f"{_DRIVE_BASE}/files/{file_id}/export",
                params={"mimeType": "text/plain"},
            )
            resp.raise_for_status()
            return resp.text
        except Exception:
            logger.exception("Failed to export file %s as text", file_id)
            return None
