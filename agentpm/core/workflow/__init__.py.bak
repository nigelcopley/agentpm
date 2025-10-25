"""
Workflow Module

State management and transition validation for projects, work items, and tasks.

Usage:
    from agentpm.core.workflow import WorkflowService

    workflow = WorkflowService(db_service)

    # Transition task to in progress
    task = workflow.start_task(task_id=123)

    # Block task with reason
    task = workflow.block_task(task_id=123, blocked_reason="Waiting for API")

    # Complete work item (validates all tasks done)
    work_item = workflow.complete_work_item(work_item_id=45)
"""

from .service import WorkflowService, WorkflowError
from .state_machine import StateMachine
from .validators import StateRequirements, DependencyValidator, ValidationResult

__all__ = [
    "WorkflowService",
    "WorkflowError",
    "StateMachine",
    "StateRequirements",
    "DependencyValidator",
    "ValidationResult",
]