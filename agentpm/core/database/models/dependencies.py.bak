"""
Dependency and Blocker Models - Pydantic Domain Models

Type-safe models for task/work item relationships.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TaskDependency(BaseModel):
    """
    Task dependency relationship.

    Represents: Task X depends on Task Y completing first.

    Attributes:
        id: Database primary key
        task_id: The dependent task (this task)
        depends_on_task_id: The prerequisite task (must complete first)
        dependency_type: 'hard' (must complete) or 'soft' (should complete)
        notes: Why this dependency exists
        created_at: When dependency was added
    """
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = None
    task_id: int = Field(..., gt=0)
    depends_on_task_id: int = Field(..., gt=0)
    dependency_type: str = Field(default='hard', pattern='^(hard|soft)$')
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class TaskBlocker(BaseModel):
    """
    Task blocker relationship.

    Represents: Task X is blocked by Task Y or external factor.

    Attributes:
        id: Database primary key
        task_id: The blocked task
        blocker_type: 'task' (blocked by another task) or 'external' (external factor)
        blocker_task_id: The blocking task (if blocker_type='task')
        blocker_description: Description of blocker (if blocker_type='external')
        blocker_reference: External reference (ticket ID, URL, etc.)
        is_resolved: Whether blocker is resolved
        resolved_at: When blocker was resolved
        resolution_notes: How blocker was resolved
        created_at: When blocker was added
    """
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = None
    task_id: int = Field(..., gt=0)
    blocker_type: str = Field(..., pattern='^(task|external)$')

    # Task blocker
    blocker_task_id: Optional[int] = Field(default=None, gt=0)

    # External blocker
    blocker_description: Optional[str] = None
    blocker_reference: Optional[str] = None

    # Resolution
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    created_at: Optional[datetime] = None


class WorkItemDependency(BaseModel):
    """
    Work item dependency relationship.

    Represents: Work Item X depends on Work Item Y completing first.

    Attributes:
        id: Database primary key
        work_item_id: The dependent work item
        depends_on_work_item_id: The prerequisite work item
        dependency_type: 'hard' or 'soft'
        notes: Why this dependency exists
        created_at: When dependency was added
    """
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = None
    work_item_id: int = Field(..., gt=0)
    depends_on_work_item_id: int = Field(..., gt=0)
    dependency_type: str = Field(default='hard', pattern='^(hard|soft)$')
    notes: Optional[str] = None
    created_at: Optional[datetime] = None