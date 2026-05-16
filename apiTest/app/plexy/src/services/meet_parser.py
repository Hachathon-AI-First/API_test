"""
MeetParser — extracts plain text from a Google Doc and parses
Google Meet Gemini-generated notes into structured MeetingMetadata.
"""
import logging
import re
from typing import List, Optional, Tuple

from src.domain.models import MeetingMetadata, Participant

logger = logging.getLogger(__name__)

_DATE_PATTERNS = [
    re.compile(r"\d{4}-\d{2}-\d{2}"),                            # 2026-03-17
    re.compile(r"\d{1,2}/\d{1,2}/\d{4}"),                        # 17/03/2026
    re.compile(r"\d{1,2}\s+de\s+\w+\.?\s+de\s+\d{4}", re.I),    # 16 de jan. de 2026
]

# Date embedded in the Google Meet file name: "... - 2026/03/23 14:27 GMT-03:00 - ..."
_DATE_FROM_FILENAME_RE = re.compile(r"(\d{4}/\d{2}/\d{2})")

_PARTICIPANT_RE = re.compile(
    r"^(?:Convidados|Attendees|Participants|Participantes)\s+(.+)",
    re.IGNORECASE,
)

_SKIP_SECTION_KEYWORDS = ("convidados", "anexos", "resumo", "detalhes")

_SUMMARY_RE = re.compile(
    r"(?:^|\n)(?:Resumo|Summary)\s*\n(.*?)(?:\n(?:Detalhes|Details|Pr\u00f3ximas etapas|Suggested next steps|Next steps)|\Z)",
    re.IGNORECASE | re.DOTALL,
)

_NEXT_STEPS_RE = re.compile(
    r"(?:^|\n)(?:Pr\u00f3ximas etapas sugeridas|Suggested next steps|Pr\u00f3ximas etapas)\s*\n(.*?)(?:\nRevise|\nEnvie|\nReview|\Z)",
    re.IGNORECASE | re.DOTALL,
)


_DOCS_BASE = "https://docs.googleapis.com/v1"


class MeetParser:
    """
    Extracts text from the Docs API and parses it into MeetingMetadata.

    Google Meet Gemini notes format:
        16 de jan. de 2026
        Meeting title
        Convidados Name1 Name2 Name3
        Anexos ...
        Registros da reunião Transcrição

        Resumo
        <summary>

        Detalhes
        <details>

        Próximas etapas sugeridas
        <next steps>
    """

    def __init__(self, session):
        self._session = session

    def extract_text_and_participants(
        self, document_id: str, drive_fallback=None
    ) -> Tuple[Optional[str], List[Participant], Optional[str]]:
        """
        Fetches the document from the Docs API and returns a 3-tuple:
          - plain text (str) from all structural elements
          - participants (List[Participant]) from person smart chips
          - meeting_date (str | None) from Google Calendar date smart chip

        Smart chips (person and date) are extracted directly from the Docs API
        JSON — they cannot be reliably recovered from plain text alone.

        Falls back to drive_fallback for text only (no chips) if the Docs API fails.
        """
        try:
            resp = self._session.get(f"{_DOCS_BASE}/documents/{document_id}")
            resp.raise_for_status()
            doc = resp.json()
            content = doc.get("body", {}).get("content", [])
            text = self._walk(content)
            participants = self._extract_person_chips(content)
            meeting_date = self._extract_date_chip(content)
            return text, participants, meeting_date
        except Exception as exc:
            logger.warning("Docs API failed for %s (%s) — trying export fallback.", document_id, exc)

        text = drive_fallback(document_id) if drive_fallback else None
        return text, [], None

    def parse(
        self,
        text: str,
        file_name: str,
        participants: List[Participant],
        meeting_date: Optional[str] = None,
    ) -> MeetingMetadata:
        """Parse raw document text into MeetingMetadata."""
        meta = MeetingMetadata(meeting_title=file_name, participants=participants)
        lines = [l.rstrip() for l in text.splitlines()]
        non_empty = [l for l in lines if l.strip()]

        # 1 - Date (priority: filename → calendar chip → regex in text)
        m = _DATE_FROM_FILENAME_RE.search(file_name)
        if m:
            meta.date = m.group(1)          # e.g. "2026/03/23"
        elif meeting_date:
            meta.date = meeting_date
        else:
            for line in non_empty[:8]:
                for pat in _DATE_PATTERNS:
                    m = pat.search(line)
                    if m:
                        meta.date = m.group(0)
                        break
                if meta.date:
                    break

        # 2 - Title
        if len(non_empty) >= 2:
            candidate = non_empty[1] if meta.date and meta.date in non_empty[0] else non_empty[0]
            if not any(candidate.lower().startswith(kw) for kw in _SKIP_SECTION_KEYWORDS):
                meta.meeting_title = candidate
        
        # 3 - Summary
        m = _SUMMARY_RE.search(text)
        meta.summary_text = m.group(1).strip() if m else None

        # 4 - Suggested next steps
        m = _NEXT_STEPS_RE.search(text)
        meta.suggested_next_steps = m.group(1).strip() if m else None

        return meta

    def _extract_date_chip(self, elements: list) -> Optional[str]:
        """
        Finds the Google Calendar date smart chip and returns its title string.

        In the Docs API, the date chip is a richLink whose URI contains
        'calendar.google.com'. The title is the human-readable date label
        (e.g. '19 de mar. de 2026').
        """
        def _recurse(els) -> Optional[str]:
            for el in els:
                if "paragraph" in el:
                    for run in el["paragraph"].get("elements", []):
                        if "richLink" in run:
                            props = run["richLink"].get("richLinkProperties", {})
                            uri   = props.get("uri", "")
                            title = props.get("title", "").strip()
                            if "calendar.google.com" in uri and title:
                                return title
                elif "table" in el:
                    for row in el["table"].get("tableRows", []):
                        for cell in row.get("tableCells", []):
                            result = _recurse(cell.get("content", []))
                            if result:
                                return result
                elif "tableOfContents" in el:
                    result = _recurse(el["tableOfContents"].get("content", []))
                    if result:
                        return result
            return None

        return _recurse(elements)

    def _extract_person_chips(self, elements: list) -> List[Participant]:
        """
        Walks the Docs API content tree and collects all person smart chips.
        Returns a deduplicated list of Participant objects (name + email).
        """
        seen_emails: set = set()
        participants: List[Participant] = []

        def _recurse(els):
            for el in els:
                if "paragraph" in el:
                    for run in el["paragraph"].get("elements", []):
                        if "person" in run:
                            props = run["person"].get("personProperties", {})
                            name  = props.get("name", "").strip()
                            email = props.get("email", "").strip() or None
                            key = email or name
                            if key not in seen_emails:
                                seen_emails.add(key)
                                participants.append(Participant(name=name, email=email))
                elif "table" in el:
                    for row in el["table"].get("tableRows", []):
                        for cell in row.get("tableCells", []):
                            _recurse(cell.get("content", []))
                elif "tableOfContents" in el:
                    _recurse(el["tableOfContents"].get("content", []))

        _recurse(elements)
        return participants

    def _walk(self, elements: list) -> str:
        """
        Extracts plain text from Docs API structural elements.

        Handles three types of ParagraphElement content:
        - textRun: regular text
        - person: smart chip for @mentions — extracts the display name into text
        - richLink: smart chip for links (calendar date chips) — extracts the title
        """
        text = ""
        for el in elements:
            if "paragraph" in el:
                for run in el["paragraph"].get("elements", []):
                    if "textRun" in run:
                        text += run["textRun"].get("content", "")
                    elif "person" in run:
                        name = run["person"].get("personProperties", {}).get("name", "")
                        if name:
                            text += name + " "
                    elif "richLink" in run:
                        title = run["richLink"].get("richLinkProperties", {}).get("title", "")
                        if title:
                            text += title + " "
            elif "table" in el:
                for row in el["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        text += self._walk(cell.get("content", []))
            elif "tableOfContents" in el:
                text += self._walk(el["tableOfContents"].get("content", []))
        return text
