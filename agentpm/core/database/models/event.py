"""
Event Model

Pydantic model for Event entity (audit trail and event tracking).
Part of the three-layer pattern:
- Layer 1: Pydantic models (validation) ← THIS FILE
- Layer 2: Adapters (conversion)
- Layer 3: Methods (CRUD operations)

Events provide an audit trail of all system activities including:
- Workflow transitions
- Agent actions
- Gate executions
- Context refreshes
- Dependency changes
- Blocker management
- Entity creation

This model is used temporarily until the events system is fully implemented.
It provides basic event tracking capabilities for audit and debugging.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from agentpm.core.database.enums import EventType, EventCategory, EventSeverity


class Event(BaseModel):
    """
    Event entity for audit trail and system monitoring.

    Tracks all significant system activities for debugging, auditing,
    and workflow analysis.

    Attributes:
        id: Unique identifier (auto-assigned)
        event_type: Type of event (workflow, agent action, etc.)
        event_category: Category for grouping (workflow, agent, gate, etc.)
        event_severity: Severity level (debug, info, warning, error, critical)
        session_id: Optional session identifier
        work_item_id: Optional work item identifier
        task_id: Optional task identifier
        source: Event source (agent name, service name, etc.)
        event_data: Additional event data (JSON)
        message: Human-readable event description
        timestamp: Event timestamp (ISO 8601)
        created_at: Creation timestamp (ISO 8601)

    Example:
        >>> event = Event(
        ...     event_type=EventType.WORKFLOW_TRANSITION,
        ...     event_category=EventCategory.WORKFLOW,
        ...     event_severity=EventSeverity.INFO,
        ...     source="workflow_service",
        ...     message="Task 593 transitioned to IN_PROGRESS",
        ...     event_data={"task_id": 593, "from_state": "PROPOSED", "to_state": "IN_PROGRESS"}
        ... )
    """

    id: Optional[int] = Field(None, description="Unique identifier (auto-assigned)")
    event_type: EventType = Field(..., description="Event type classification")
    event_category: EventCategory = Field(..., description="Event category for grouping")
    event_severity: EventSeverity = Field(
        EventSeverity.INFO,
        description="Event severity level"
    )
    session_id: Optional[int] = Field(None, description="Associated session ID")
    work_item_id: Optional[int] = Field(None, description="Associated work item ID")
    task_id: Optional[int] = Field(None, description="Associated task ID")
    source: str = Field(..., description="Event source (agent, service, etc.)")
    event_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional event data (JSON)"
    )
    message: str = Field(..., description="Human-readable event description")
    timestamp: Optional[str] = Field(
        None,
        description="Event timestamp (ISO 8601, defaults to now)"
    )
    created_at: Optional[str] = Field(
        None,
        description="Creation timestamp (ISO 8601, defaults to now)"
    )

    @field_validator("timestamp", "created_at", mode="before")
    @classmethod
    def ensure_timestamp(cls, v: Optional[str]) -> str:
        """Ensure timestamps are populated (default to now if None)."""
        if v is None:
            return datetime.utcnow().isoformat() + "Z"
        return v

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "event_type": "workflow_transition",
                "event_category": "workflow",
                "event_severity": "info",
                "source": "workflow_service",
                "message": "Task 593 started",
                "event_data": {"task_id": 593, "action": "start"},
            }
        }
