"""
Task Model - Pydantic Domain Model

Type-safe task model with validation.

Tasks are atomic units of work within work items.
They follow the complete workflow plus task-specific states (blocked, cancelled).

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from ..enums import TaskStatus, TaskType


class Task(BaseModel):
    """
    Task domain model with Pydantic validation.

    Tasks are atomic, granular units of work that comprise work items.
    Typical duration: 2-4 hours.

    Lifecycle: proposed → validated → accepted → in_progress → review → completed → archived
    Additional: blocked, cancelled

    Task type determines validation requirements:
    - FEATURE tasks require acceptance criteria and technical approach
    - BUGFIX tasks require bug description and reproduction steps
    - SIMPLE tasks have minimal requirements
    - RESEARCH tasks require research questions and findings

    Attributes:
        id: Database primary key (None for new tasks)
        work_item_id: Parent work item ID
        name: Task name (1-200 characters)
        description: Optional detailed description
        type: Task type (determines validation requirements)
        effort_hours: Estimated effort in hours (typically 2-4)
        status: Task workflow status (9 unified states)
        priority: Priority level (1-5, 1=highest)
        assigned_to: Optional agent/user assignment
        blocked_reason: Reason if status is BLOCKED
        due_date: Optional due date (Migration 0011)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        started_at: When moved to in_progress
        completed_at: Completion timestamp
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )

    # Primary key
    id: Optional[int] = None

    # Relationships
    work_item_id: int = Field(..., gt=0)

    # Core fields
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: TaskType = TaskType.IMPLEMENTATION  # Determines validation requirements

    # Quality gate tracking (type-specific structured data)
    quality_metadata: Optional[dict] = None

    # Planning
    effort_hours: Optional[float] = Field(default=None, ge=0, le=8)  # Max 8 hours per task
    priority: int = Field(default=3, ge=1, le=5)

    # Assignment
    assigned_to: Optional[str] = None  # Agent role or user name

    # Lifecycle
    status: TaskStatus = TaskStatus.DRAFT
    blocked_reason: Optional[str] = None

    # NEW (Migration 0011): Scheduling field
    due_date: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None  # When moved to in_progress
    completed_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if task is actively being worked on"""
        return self.status == TaskStatus.ACTIVE

    def is_blocked(self) -> bool:
        """Check if task is blocked"""
        return self.status == TaskStatus.BLOCKED

    def is_complete(self) -> bool:
        """Check if task is completed"""
        return TaskStatus.is_terminal_state(self.status)

    def can_start(self) -> bool:
        """Check if task can be started"""
        return self.status in (TaskStatus.ACTIVE, TaskStatus.DRAFT)