"""
Status Enumerations - Hierarchical Workflow States

Three lifecycle patterns:

1. **Projects** (simple lifecycle):
   initiated → active → on_hold → completed → archived

2. **Work Items & Tasks** (full workflow):
   ideas → proposed → validated → accepted → in_progress → review → completed → archived

3. **Task-specific** (additional states):
   blocked, cancelled

This approach provides appropriate granularity at each level.
"""

from enum import Enum
from typing import Optional


class ProjectStatus(str, Enum):
    """
    Project lifecycle states (simple, high-level).

    Flow:
        initiated → active → on_hold (optional) → completed → archived

    Projects don't need fine-grained workflow states - they're containers
    for work items that have the detailed workflow.
    """
    INITIATED = "initiated"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    DONE = "completed"
    ARCHIVED = "archived"

    @classmethod
    def is_active_state(cls, status: 'ProjectStatus') -> bool:
        """Check if project is in active development"""
        return status in (cls.INITIATED, cls.ACTIVE)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class WorkItemStatus(str, Enum):
    """
    Work item workflow states (streamlined 6-state model with phase gating).

    Flow:
        draft → ready → active → review → done → archived
        (+ blocked, cancelled as administrative states)

    Phase Gating:
        - draft: D1_DISCOVERY, P1_PLAN phases
        - ready: P1_PLAN phase (ready for implementation)
        - active: I1_IMPLEMENTATION phase
        - review: R1_REVIEW phase
        - done: O1_OPERATIONS, E1_EVOLUTION phases
        - archived: Historical record

    Work items follow the complete workflow as they represent discrete
    features, analyses, objectives, or research efforts.
    """
    DRAFT = "draft"
    READY = "ready"
    ACTIVE = "active"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal_state(cls, status: 'WorkItemStatus') -> bool:
        """Check if status is terminal"""
        return status in (cls.DONE, cls.CANCELLED, cls.ARCHIVED)

    @classmethod
    def get_phase_for_status(cls, status: 'WorkItemStatus') -> str:
        """Get the primary phase for a work item status"""
        phase_mapping = {
            cls.DRAFT: "D1_DISCOVERY",
            cls.READY: "P1_PLAN",
            cls.ACTIVE: "I1_IMPLEMENTATION",
            cls.REVIEW: "R1_REVIEW",
            cls.DONE: "O1_OPERATIONS",
            cls.ARCHIVED: None,  # Terminal state, no phase (E1 applies to O1 ongoing work)
            cls.BLOCKED: None,  # Administrative state
            cls.CANCELLED: None,  # Administrative state
        }
        return phase_mapping.get(status)

    @classmethod
    def get_next_state(cls, status: 'WorkItemStatus') -> Optional['WorkItemStatus']:
        """Get the next state in the normal workflow progression"""
        next_mapping = {
            cls.DRAFT: cls.READY,
            cls.READY: cls.ACTIVE,
            cls.ACTIVE: cls.REVIEW,
            cls.REVIEW: cls.DONE,
            cls.DONE: cls.ARCHIVED,
            # Administrative states don't have automatic next states
            cls.BLOCKED: None,
            cls.CANCELLED: None,
            cls.ARCHIVED: None,
        }
        return next_mapping.get(status)


    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class TaskStatus(str, Enum):
    """
    Task workflow states (streamlined 6-state model, same as work items).

    Flow:
        draft → ready → active → review → done → archived
        (+ blocked, cancelled as administrative states)

    Tasks use the same workflow as work items for consistency.
    Task status can depend on work item status (task can't complete if work item cancelled).
    """
    DRAFT = "draft"
    READY = "ready"
    ACTIVE = "active"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal_state(cls, status: 'TaskStatus') -> bool:
        """Check if status is terminal (done, cancelled, archived)"""
        return status in (cls.DONE, cls.CANCELLED, cls.ARCHIVED)

    @classmethod
    def get_next_state(cls, status: 'TaskStatus') -> Optional['TaskStatus']:
        """Get the next state in the normal workflow progression"""
        next_mapping = {
            cls.DRAFT: cls.READY,
            cls.READY: cls.ACTIVE,
            cls.ACTIVE: cls.REVIEW,
            cls.REVIEW: cls.DONE,
            cls.DONE: cls.ARCHIVED,
            # Administrative states don't have automatic next states
            cls.BLOCKED: None,
            cls.CANCELLED: None,
            cls.ARCHIVED: None,
        }
        return next_mapping.get(status)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")