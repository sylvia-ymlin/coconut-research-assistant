"""Request and response schemas for the research API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import SearchAPI


class ResearchRequest(BaseModel):
    """Payload for triggering a research run."""

    topic: str = Field(..., description="Research topic supplied by the user")
    search_api: SearchAPI | None = Field(
        default=None,
        description="Override the default search backend configured via env",
    )


class ResearchResponse(BaseModel):
    """HTTP response containing the generated report and structured tasks."""

    session_id: int | None = Field(
        default=None,
        description="Persistent session identifier for looking up this research run",
    )
    report_markdown: str = Field(
        ..., description="Markdown-formatted research report including sections"
    )
    todo_items: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured TODO items with summaries and sources",
    )


class TodoItemResponse(BaseModel):
    """Serializable representation of a persisted task."""

    id: int
    title: str
    intent: str
    query: str
    status: str
    summary: str | None = None
    sources_summary: str | None = None
    notices: list[str] = Field(default_factory=list)
    note_id: str | None = None
    note_path: str | None = None


class ResearchSessionSummaryResponse(BaseModel):
    """Compact session data for history listings."""

    session_id: int
    topic: str
    status: str
    search_api: str | None = None
    created_at: datetime
    updated_at: datetime
    task_count: int
    completed_task_count: int
    report_available: bool


class ResearchSessionDetailResponse(ResearchSessionSummaryResponse):
    """Full session payload for viewing a historical research run."""

    report_markdown: str = ""
    error_detail: str | None = None
    report_note_id: str | None = None
    report_note_path: str | None = None
    todo_items: list[TodoItemResponse] = Field(default_factory=list)
