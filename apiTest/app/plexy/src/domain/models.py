"""
Domain models for the Drive → BigQuery connector.

These typed Pydantic models are used throughout the pipeline to ensure
data consistency from webhook reception to BigQuery insertion.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DriveNotification(BaseModel):
    """
    Represents the JSON payload published to Pub/Sub by the webhook handler.
    Maps directly to the message produced in api/main.py.
    """
    state: str = Field(..., description="Drive resource state (e.g. 'update', 'add')")
    resource_id: str = Field(..., description="Drive resource ID of the changed file")
    channel_id: str = Field(..., description="Webhook channel ID")


class Participant(BaseModel):
    """A meeting participant with name and optional email."""
    name: str = Field(..., description="Display name of the participant")
    email: Optional[str] = Field(None, description="Email address of the participant")


class MeetingMetadata(BaseModel):
    """
    Structured metadata extracted from a Google Meet summary document.
    All fields are optional to allow graceful fallback when the doc format
    is not fully recognized.
    """
    meeting_title: Optional[str] = Field(None, description="Title of the meeting")
    date: Optional[str] = Field(None, description="Meeting date")
    participants: List[Participant] = Field(default_factory=list, description="List of participants with name and email")
    summary_text: Optional[str] = Field(None, description="Main body / summary text of the meeting")
    suggested_next_steps: Optional[str] = Field(None, description="Next steps from 'Próximas etapas sugeridas' section")


class TranscriptionRecord(BaseModel):
    """
    Represents a single transcription row to be inserted into BigQuery.
    """
    file_id: str = Field(..., description="Google Doc file ID")
    file_name: str = Field(..., description="Google Doc file name")
    text_content: str = Field(..., description="Extracted plain text from the document")
    inserted_at: str = Field(..., description="ISO 8601 timestamp of when the record was inserted")
    meeting_metadata: Optional[MeetingMetadata] = Field(
        None, description="Structured meeting metadata parsed from the document"
    )
