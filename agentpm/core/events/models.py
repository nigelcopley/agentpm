"""Event models for session tracking.

This module provides Pydantic models for event-driven session tracking:
- EventType: 40+ event types across 6 categories
- EventCategory: Event classification (workflow, tool, decision, reasoning, error, session)
- EventSeverity: Event severity (debug, info, warning, error, critical)
- Event: Base event model with typed event_data
- Specific event data models (ErrorEventData, WorkflowEventData, etc.)

Design Principles:
- Minimal required fields (id, type, timestamp)
- Flexible payload (event_data JSON)
- Queryable metadata (category, severity, source)
- Immutable once created (audit trail)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type taxonomy (40+ event types)."""

    # Workflow events (10 types)
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_DONE = "task.completed"
    TASK_BLOCKED = "task.blocked"
    TASK_UNBLOCKED = "task.unblocked"

    WORK_ITEM_STARTED = "work_item.started"
    WORK_ITEM_DONE = "work_item.completed"

    DEPENDENCY_ADDED = "dependency.added"
    BLOCKER_ADDED = "blocker.added"
    BLOCKER_RESOLVED = "blocker.resolved"

    # Tool events (8 types)
    READ_FILE = "tool.read_file"
    WRITE_FILE = "tool.write_file"
    EDIT_FILE = "tool.edit_file"
    BASH_COMMAND = "tool.bash_command"
    GREP_SEARCH = "tool.grep_search"
    GLOB_SEARCH = "tool.glob_search"

    TOOL_SUCCESS = "tool.success"
    TOOL_FAILURE = "tool.failure"

    # Decision events (4 types)
    DECISION_MADE = "decision.made"
    APPROACH_CHOSEN = "decision.approach_chosen"
    APPROACH_REJECTED = "decision.approach_rejected"
    TRADE_OFF_ANALYZED = "decision.trade_off_analyzed"

    # Reasoning events (4 types)
    REASONING_STARTED = "reasoning.started"
    REASONING_COMPLETE = "reasoning.complete"
    HYPOTHESIS_FORMED = "reasoning.hypothesis_formed"
    HYPOTHESIS_TESTED = "reasoning.hypothesis_tested"

    # Error events (5 types)
    ERROR_ENCOUNTERED = "error.encountered"
    ERROR_RESOLVED = "error.resolved"
    IMPORT_FAILED = "error.import_failed"
    TEST_FAILED = "error.test_failed"
    BUILD_FAILED = "error.build_failed"
    SYNTAX_ERROR = "error.syntax_error"

    # Session events (6 types)
    SESSION_STARTED = "session.started"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_ENDED = "session.ended"
    MILESTONE_REACHED = "session.milestone"
    PHASE_TRANSITION = "session.phase_transition"


class EventCategory(str, Enum):
    """Event categories for filtering and analytics."""

    WORKFLOW = "workflow"
    TOOL_USAGE = "tool_usage"
    DECISION = "decision"
    REASONING = "reasoning"
    ERROR = "error"
    SESSION_LIFECYCLE = "session_lifecycle"


class EventSeverity(str, Enum):
    """Event severity for filtering and alerting."""

    DEBUG = "debug"       # Low-level tool events
    INFO = "info"         # Normal workflow events
    WARNING = "warning"   # Potential issues (blocked tasks)
    ERROR = "error"       # Failures (tool errors, import errors)
    CRITICAL = "critical" # Major issues (session crash, data loss)


class Event(BaseModel):
    """Base event model for all session events.

    Design Principles:
    - Minimal required fields (id, type, timestamp)
    - Flexible payload (event_data JSON)
    - Queryable metadata (category, severity, source)
    - Immutable once created (audit trail)
    """

    # Primary key (auto-assigned)
    id: Optional[int] = None

    # Event classification
    event_type: EventType = Field(..., description="Event type from taxonomy")
    event_category: EventCategory = Field(..., description="Event category")
    event_severity: EventSeverity = Field(default=EventSeverity.INFO)

    # Session context
    session_id: int = Field(..., gt=0, description="Foreign key to sessions.id")

    # Event metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = Field(..., description="Event source (workflow, cli, hook, tool)")

    # Event payload (flexible JSON)
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data (flexible schema)"
    )

    # Optional entity references (for fast queries)
    project_id: Optional[int] = None
    work_item_id: Optional[int] = None
    task_id: Optional[int] = None

    # Audit
    created_at: Optional[datetime] = None

    class Config:
        validate_assignment = True


# Event-Specific Models (typed event_data schemas)


class ErrorEventData(BaseModel):
    """Typed event data for error events.

    Tracks error details, resolution, and impact for error analysis.
    """

    error_type: str = Field(..., description="Error type (ImportError, SyntaxError, etc.)")
    error_message: str = Field(..., min_length=1, max_length=2000)

    # Error context
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    traceback: Optional[str] = Field(default=None, max_length=5000)

    # Resolution tracking
    resolution: Optional[str] = Field(default=None, max_length=1000)
    resolved_at: Optional[datetime] = None
    resolution_duration_minutes: Optional[int] = None

    # Impact assessment
    impact: Optional[str] = Field(
        default=None,
        description="Impact description (e.g., 'Blocked task #238 for 5 minutes')"
    )
    task_blocked: Optional[int] = None
    work_blocked: Optional[int] = None


class WorkflowEventData(BaseModel):
    """Typed event data for workflow events."""

    entity_type: str  # "task" or "work_item"
    entity_id: int
    entity_name: str
    previous_status: str
    new_status: str
    agent_assigned: Optional[str] = None
    transition_reason: Optional[str] = None


class ToolEventData(BaseModel):
    """Typed event data for tool usage events."""

    tool_name: str  # "Read", "Write", "Edit", "Bash", etc.
    operation: str  # Specific operation (e.g., "read_file", "write_file")

    # Tool parameters (simplified)
    file_path: Optional[str] = None
    command: Optional[str] = None

    # Tool results
    success: bool
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

    # Impact metrics
    lines_added: Optional[int] = None
    lines_removed: Optional[int] = None
    files_changed: Optional[int] = None


class DecisionEventData(BaseModel):
    """Typed event data for decision events."""

    decision: str = Field(..., min_length=10, max_length=500)
    rationale: str = Field(..., min_length=10, max_length=1000)

    alternatives_considered: List[str] = Field(default_factory=list)
    trade_offs: Optional[str] = None

    # Decision context
    task_id: Optional[int] = None
    work_item_id: Optional[int] = None

    # Decision outcome
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reversible: bool = True


class ReasoningEventData(BaseModel):
    """Typed event data for reasoning events."""

    reasoning_type: str  # "analysis", "design", "debugging", "planning"
    summary: str = Field(..., min_length=20, max_length=2000)

    # Reasoning details
    hypothesis: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    conclusion: Optional[str] = None

    # Performance
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
