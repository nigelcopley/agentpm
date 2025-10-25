"""
Document Audit Log Model

Tracks all document lifecycle actions for comprehensive audit trail.
Supports document publishing workflow (WI-164).

Pattern: Pydantic model for type safety and validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentAuditLog(BaseModel):
    """
    Audit log entry for document actions.

    Records all document lifecycle transitions, review actions,
    and publication events with full context.

    Example:
        entry = DocumentAuditLog(
            document_id=123,
            action="publish",
            actor="system",
            from_state="approved",
            to_state="published",
            details={"source": ".agentpm/docs/...", "destination": "docs/..."},
            comment="Auto-published per type-based rule"
        )
    """

    id: Optional[int] = None
    document_id: int = Field(..., gt=0, description="Document reference ID")

    # Action details
    action: str = Field(..., min_length=1, max_length=50, description="Action type (create, submit_review, approve, reject, publish, unpublish, update, archive)")
    actor: str = Field(..., min_length=1, max_length=200, description="User email or agent identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")

    # State transition
    from_state: Optional[str] = Field(None, max_length=50, description="Previous lifecycle state")
    to_state: Optional[str] = Field(None, max_length=50, description="New lifecycle state")

    # Action metadata
    details: Optional[Dict[str, Any]] = Field(None, description="Action-specific details (JSON)")
    comment: Optional[str] = Field(None, description="Human-readable comment")

    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "document_id": 123,
                "action": "publish",
                "actor": "system",
                "from_state": "approved",
                "to_state": "published",
                "details": {
                    "source": ".agentpm/docs/guides/user_guide/getting-started.md",
                    "destination": "docs/guides/user_guide/getting-started.md",
                    "trigger": "auto_publish_on_approved"
                },
                "comment": "Auto-published per type-based rule"
            }
        }
