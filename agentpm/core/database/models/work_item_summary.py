"""
Work Item Summary Model - Session Context Storage

Pydantic model for work_item_summaries table with:
- Session identification (date, duration)
- Summary narrative (markdown text)
- Structured metadata (JSON for AI parsing)
- Attribution tracking (created_by, created_at)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class WorkItemSummary(BaseModel):
    """
    Work item session summary model.

    Stores session-level context including:
    - Session narrative (markdown text)
    - Structured metadata (decisions, changes, blockers)
    - Timeline tracking (date, duration)
    - Attribution (who created, when)

    Used by session-start agents to gather efficient context
    from previous work sessions.
    """

    # Identity
    id: Optional[int] = None
    work_item_id: int = Field(..., gt=0, description="Work item this summarizes")

    # Session Info
    session_date: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Session date in YYYY-MM-DD format"
    )
    session_duration_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Session duration in hours"
    )

    # Content
    summary_text: str = Field(
        ...,
        min_length=10,
        description="Markdown-formatted session summary"
    )
    context_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured metadata (decisions, changes, blockers)"
    )

    # Attribution
    created_at: Optional[datetime] = None
    created_by: Optional[str] = Field(
        default=None,
        description="Agent identifier or username"
    )
    summary_type: str = Field(
        default='session',
        description="Summary type: session, milestone, decision, retrospective"
    )

    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "work_item_id": 6,
                "session_date": "2025-10-06",
                "session_duration_hours": 7.5,
                "summary_text": "# Session Summary\n\nCompleted plugin documentation...",
                "context_metadata": {
                    "key_decisions": ["Approved 8h integration scope"],
                    "tasks_completed": [11, 13, 14],
                    "blockers_resolved": ["Import issues fixed"]
                },
                "created_by": "aipm-database-developer",
                "summary_type": "session"
            }
        }
