"""
State Machine - Workflow Transition Rules

Defines valid state transitions for projects, work items, and tasks.

Pattern: State machine with forward, backward, and forbidden transitions
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..database.enums import ProjectStatus, WorkItemStatus, TaskStatus, EntityType


class StateMachine:
    """
    Defines valid state transitions for all entity types.

    Includes:
    - Forward transitions (normal workflow progression)
    - Backward transitions (rework scenarios)
    - Forbidden transitions (policy enforcement)
    """

    # ========== FORWARD TRANSITIONS ==========

    PROJECT_TRANSITIONS: Dict[ProjectStatus, List[ProjectStatus]] = {
        ProjectStatus.INITIATED: [ProjectStatus.ACTIVE],
        ProjectStatus.ACTIVE: [ProjectStatus.ON_HOLD, ProjectStatus.DONE],
        ProjectStatus.ON_HOLD: [ProjectStatus.ACTIVE, ProjectStatus.DONE],
        ProjectStatus.DONE: [ProjectStatus.ARCHIVED],
        ProjectStatus.ARCHIVED: []  # Terminal
    }

    WORK_ITEM_TRANSITIONS: Dict[WorkItemStatus, List[WorkItemStatus]] = {
        WorkItemStatus.DRAFT: [WorkItemStatus.READY, WorkItemStatus.CANCELLED],
        WorkItemStatus.READY: [WorkItemStatus.ACTIVE, WorkItemStatus.DRAFT],  # Can go back for refinement
        WorkItemStatus.ACTIVE: [WorkItemStatus.REVIEW, WorkItemStatus.BLOCKED],
        WorkItemStatus.BLOCKED: [WorkItemStatus.ACTIVE, WorkItemStatus.CANCELLED],
        WorkItemStatus.REVIEW: [WorkItemStatus.ACTIVE, WorkItemStatus.DONE],  # Can rework
        WorkItemStatus.DONE: [WorkItemStatus.ARCHIVED],
        WorkItemStatus.CANCELLED: [WorkItemStatus.ARCHIVED],
        WorkItemStatus.ARCHIVED: []  # Terminal
    }

    TASK_TRANSITIONS: Dict[TaskStatus, List[TaskStatus]] = {
        TaskStatus.DRAFT: [TaskStatus.READY, TaskStatus.CANCELLED],
        TaskStatus.READY: [TaskStatus.ACTIVE, TaskStatus.DRAFT, TaskStatus.CANCELLED],  # Can revise
        TaskStatus.ACTIVE: [TaskStatus.BLOCKED, TaskStatus.REVIEW, TaskStatus.CANCELLED],
        TaskStatus.BLOCKED: [TaskStatus.ACTIVE, TaskStatus.CANCELLED],
        TaskStatus.REVIEW: [TaskStatus.ACTIVE, TaskStatus.DONE, TaskStatus.CANCELLED],  # Can rework
        TaskStatus.DONE: [TaskStatus.ARCHIVED],
        TaskStatus.CANCELLED: [TaskStatus.ARCHIVED],
        TaskStatus.ARCHIVED: []  # Terminal
    }

    # ========== BACKWARD TRANSITIONS (Rework) ==========

    BACKWARD_TRANSITIONS = {
        # Work items
        (WorkItemStatus.READY, WorkItemStatus.DRAFT): {
            'reason_required': True,
            'description': 'Validation revealed issues, revise proposal'
        },
        (WorkItemStatus.REVIEW, WorkItemStatus.ACTIVE): {
            'reason_required': True,
            'description': 'Review feedback requires rework'
        },

        # Tasks
        (TaskStatus.READY, TaskStatus.DRAFT): {
            'reason_required': True,
            'description': 'Technical approach needs revision'
        },
        (TaskStatus.REVIEW, TaskStatus.ACTIVE): {
            'reason_required': True,
            'description': 'Review feedback requires changes'
        },
        (TaskStatus.BLOCKED, TaskStatus.ACTIVE): {
            'reason_required': True,
            'description': 'Blocker unresolvable, task needs redesign'
        }
    }

    # ========== FORBIDDEN TRANSITIONS ==========

    FORBIDDEN_TRANSITIONS = {
        # Can't skip workflow stages (6-state system)
        (WorkItemStatus.DRAFT, WorkItemStatus.ACTIVE): "Must go through ready first",
        (WorkItemStatus.DRAFT, WorkItemStatus.REVIEW): "Must go through ready → active first",
        (WorkItemStatus.DRAFT, WorkItemStatus.DONE): "Must go through ready → active → review first",
        (WorkItemStatus.READY, WorkItemStatus.REVIEW): "Must go through active first",
        (WorkItemStatus.READY, WorkItemStatus.DONE): "Must go through active → review first",
        
        (TaskStatus.DRAFT, TaskStatus.ACTIVE): "Must go through ready first",
        (TaskStatus.DRAFT, TaskStatus.REVIEW): "Must go through ready → active first",
        (TaskStatus.DRAFT, TaskStatus.DONE): "Must go through ready → active → review first",
        (TaskStatus.READY, TaskStatus.REVIEW): "Must go through active first",
        (TaskStatus.READY, TaskStatus.DONE): "Must go through active → review first",

        # Can't reopen completed work
        (WorkItemStatus.DONE, WorkItemStatus.ACTIVE): "Completed work cannot be reopened (create new work item)",
        (WorkItemStatus.DONE, WorkItemStatus.REVIEW): "Completed work cannot go back to review",
        (WorkItemStatus.ARCHIVED, WorkItemStatus.ACTIVE): "Archived work cannot be reopened",
        (WorkItemStatus.ARCHIVED, WorkItemStatus.REVIEW): "Archived work cannot be reopened",
        (WorkItemStatus.ARCHIVED, WorkItemStatus.DONE): "Archived work cannot be reopened",
        
        (TaskStatus.DONE, TaskStatus.ACTIVE): "Completed tasks cannot be reopened (create new task)",
        (TaskStatus.DONE, TaskStatus.REVIEW): "Completed tasks cannot go back to review",
        (TaskStatus.ARCHIVED, TaskStatus.ACTIVE): "Archived tasks cannot be reopened",
        (TaskStatus.ARCHIVED, TaskStatus.REVIEW): "Archived tasks cannot be reopened",
        (TaskStatus.ARCHIVED, TaskStatus.DONE): "Archived tasks cannot be reopened",

        # Can't uncancel
        (WorkItemStatus.CANCELLED, WorkItemStatus.DRAFT): "Cancelled work items cannot be uncancelled (create new work item)",
        (WorkItemStatus.CANCELLED, WorkItemStatus.ACTIVE): "Cancelled work items are terminal",
        (WorkItemStatus.CANCELLED, WorkItemStatus.REVIEW): "Cancelled work items are terminal",
        (WorkItemStatus.CANCELLED, WorkItemStatus.DONE): "Cancelled work items are terminal",
        
        (TaskStatus.CANCELLED, TaskStatus.DRAFT): "Cancelled tasks cannot be uncancelled (create new task)",
        (TaskStatus.CANCELLED, TaskStatus.ACTIVE): "Cancelled tasks are terminal",
        (TaskStatus.CANCELLED, TaskStatus.REVIEW): "Cancelled tasks are terminal",
        (TaskStatus.CANCELLED, TaskStatus.DONE): "Cancelled tasks are terminal",

        # Can't skip review
        (WorkItemStatus.ACTIVE, WorkItemStatus.DONE): "Must go through review first",
        (TaskStatus.ACTIVE, TaskStatus.DONE): "Must go through review first",
    }

    # ========== VALIDATION METHODS ==========

    @classmethod
    def can_transition(
        cls,
        entity_type: EntityType,
        current_status: Enum,
        new_status: Enum
    ) -> bool:
        """
        Check if state transition is allowed by state machine.

        Checks forward transitions only (use is_backward_allowed for backward).

        Args:
            entity_type: PROJECT, WORK_ITEM, or TASK
            current_status: Current status enum
            new_status: Desired new status enum

        Returns:
            True if transition is in allowed list

        Example:
            can_transition(EntityType.TASK, TaskStatus.ACTIVE, TaskStatus.ACTIVE)
            # Returns: True

            can_transition(EntityType.TASK, TaskStatus.DRAFT, TaskStatus.DONE)
            # Returns: False
        """
        if entity_type == EntityType.PROJECT:
            allowed = cls.PROJECT_TRANSITIONS.get(current_status, [])
        elif entity_type == EntityType.WORK_ITEM:
            allowed = cls.WORK_ITEM_TRANSITIONS.get(current_status, [])
        elif entity_type == EntityType.TASK:
            allowed = cls.TASK_TRANSITIONS.get(current_status, [])
        else:
            return False

        return new_status in allowed

    @classmethod
    def get_valid_transitions(
        cls,
        entity_type: EntityType,
        current_status: Enum
    ) -> List[Enum]:
        """
        Get list of valid next states.

        Args:
            entity_type: Entity type
            current_status: Current status

        Returns:
            List of valid next statuses

        Example:
            get_valid_transitions(EntityType.TASK, TaskStatus.ACTIVE)
            # Returns: [TaskStatus.BLOCKED, TaskStatus.REVIEW, TaskStatus.CANCELLED]
        """
        if entity_type == EntityType.PROJECT:
            return cls.PROJECT_TRANSITIONS.get(current_status, [])
        elif entity_type == EntityType.WORK_ITEM:
            return cls.WORK_ITEM_TRANSITIONS.get(current_status, [])
        elif entity_type == EntityType.TASK:
            return cls.TASK_TRANSITIONS.get(current_status, [])
        return []

    @classmethod
    def is_backward_transition(
        cls,
        current_status: Enum,
        new_status: Enum
    ) -> bool:
        """Check if transition is backward (rework)"""
        return (current_status, new_status) in cls.BACKWARD_TRANSITIONS

    @classmethod
    def is_backward_allowed(
        cls,
        current_status: Enum,
        new_status: Enum,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if backward transition is allowed.

        Args:
            current_status: Current status
            new_status: Desired status
            reason: Reason for backward transition

        Returns:
            (allowed, error_message)

        Example:
            is_backward_allowed(WorkItemStatus.REVIEW, WorkItemStatus.ACTIVE, "Rework needed")
            # Returns: (True, None)

            is_backward_allowed(WorkItemStatus.REVIEW, WorkItemStatus.ACTIVE, None)
            # Returns: (False, "Reason required for backward transition")
        """
        transition_key = (current_status, new_status)

        if transition_key not in cls.BACKWARD_TRANSITIONS:
            return (False, "Backward transition not allowed")

        # Check if reason required
        if cls.BACKWARD_TRANSITIONS[transition_key]['reason_required'] and not reason:
            return (False, f"Reason required: {cls.BACKWARD_TRANSITIONS[transition_key]['description']}")

        return (True, None)

    @classmethod
    def is_forbidden(
        cls,
        current_status: Enum,
        new_status: Enum
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if transition is explicitly forbidden.

        Args:
            current_status: Current status
            new_status: Desired status

        Returns:
            (is_forbidden, reason)

        Example:
            is_forbidden(TaskStatus.DONE, TaskStatus.ACTIVE)
            # Returns: (True, "Completed tasks cannot be reopened")
        """
        transition_key = (current_status, new_status)

        if transition_key in cls.FORBIDDEN_TRANSITIONS:
            return (True, cls.FORBIDDEN_TRANSITIONS[transition_key])

        return (False, None)

    @classmethod
    def get_next_state(cls, entity_type: EntityType, current_status: str) -> Optional[str]:
        """
        Get the next state in the normal workflow progression for --next flag support.

        Args:
            entity_type: Type of entity (PROJECT, WORK_ITEM, TASK)
            current_status: Current status

        Returns:
            Next status in normal flow, or None if no automatic next state
        """
        if entity_type == EntityType.WORK_ITEM:
            from ..database.enums import WorkItemStatus
            try:
                current_enum = WorkItemStatus(current_status)
                next_enum = WorkItemStatus.get_next_state(current_enum)
                return next_enum.value if next_enum else None
            except ValueError:
                return None
        elif entity_type == EntityType.TASK:
            from ..database.enums import TaskStatus
            try:
                current_enum = TaskStatus(current_status)
                next_enum = TaskStatus.get_next_state(current_enum)
                return next_enum.value if next_enum else None
            except ValueError:
                return None
        else:
            # Projects don't have automatic next states
            return None