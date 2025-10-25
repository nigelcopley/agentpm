"""
Task Adapter - Model ↔ Database Conversion

Handles conversion between Task domain models and database rows.
Includes quality_metadata JSON serialization.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.task import Task
from ..enums import TaskStatus, TaskType


class TaskAdapter:
    """
    Handles Task model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, task: Task) -> Task:
        """
        Create a new task (CLI entry point).

        Three-layer pattern:
          1. Validate Pydantic model (automatic via type hints)
          2. Delegate to methods layer (includes auto-assignment logic)
          3. Return validated Task

        Args:
            service: DatabaseService instance
            task: Validated Task Pydantic model

        Returns:
            Created Task with database ID

        Raises:
            ValidationError: If work_item_id invalid or assigned_to agent not found

        Example:
            >>> from agentpm.core.database.adapters import TaskAdapter
            >>> task = Task(name="Implement auth", type=TaskType.IMPLEMENTATION, ...)
            >>> created = TaskAdapter.create(db, task)
        """
        from ..methods import tasks as task_methods
        return task_methods.create_task(service, task)

    @staticmethod
    def get(service, task_id: int) -> Optional[Task]:
        """
        Get task by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        from ..methods import tasks as task_methods
        return task_methods.get_task(service, task_id)

    @staticmethod
    def list(service, work_item_id: Optional[int] = None) -> List[Task]:
        """
        List tasks with optional work item filter (CLI entry point).

        Args:
            service: DatabaseService instance
            work_item_id: Optional work item ID to filter by

        Returns:
            List of Task models
        """
        from ..methods import tasks as task_methods
        return task_methods.list_tasks(service, work_item_id=work_item_id)

    @staticmethod
    def update(service, task_id: int, **updates) -> Task:
        """
        Update task fields (CLI entry point).

        Args:
            service: DatabaseService instance
            task_id: Task ID to update
            **updates: Field updates (e.g., name="New Name", status=TaskStatus.IN_PROGRESS)

        Returns:
            Updated Task

        Raises:
            ValidationError: If task_id not found
        """
        from ..methods import tasks as task_methods
        return task_methods.update_task(service, task_id, **updates)

    @staticmethod
    def delete(service, task_id: int) -> bool:
        """
        Delete task by ID (CLI entry point).

        Three-layer pattern:
          1. Validate task exists
          2. Delegate to methods layer
          3. Return success status

        Args:
            service: DatabaseService instance
            task_id: Task ID to delete

        Returns:
            True if deleted, False if not found

        Example:
            >>> from agentpm.core.database.adapters import TaskAdapter
            >>> success = TaskAdapter.delete(db, 123)
        """
        from ..methods import tasks as task_methods
        return task_methods.delete_task(service, task_id)

    # ============================================================================
    # MODEL CONVERSION (Internal Use)
    # ============================================================================

    @staticmethod
    def to_db(task: Task) -> Dict[str, Any]:
        """
        Convert Task model to database row format.

        Args:
            task: Task domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'work_item_id': task.work_item_id,
            'name': task.name,
            'description': task.description,
            'type': task.type.value,
            'quality_metadata': json.dumps(task.quality_metadata) if task.quality_metadata else None,
            'effort_hours': task.effort_hours,
            'priority': task.priority,
            'assigned_to': task.assigned_to,
            'status': task.status.value,
            'blocked_reason': task.blocked_reason,
            # NEW (Migration 0011): Scheduling field
            'due_date': task.due_date.isoformat() if task.due_date else None,
            # Note: started_at, completed_at set by triggers
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Task:
        """
        Convert database row to Task model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Task model
        """
        # Parse quality_metadata - handle both string (from DB) and dict (from memory)
        quality_meta = row.get('quality_metadata')
        if quality_meta:
            if isinstance(quality_meta, str):
                # Parse JSON - handle double-encoding if present
                quality_meta = json.loads(quality_meta)
                # If still a string after first parse, parse again (double-encoded)
                if isinstance(quality_meta, str):
                    quality_meta = json.loads(quality_meta)
            # else: already a dict, use as-is
        else:
            quality_meta = None

        return Task(
            id=row.get('id'),
            work_item_id=row['work_item_id'],
            name=row['name'],
            description=row.get('description'),
            type=TaskType(row.get('type', TaskType.IMPLEMENTATION.value)),
            quality_metadata=quality_meta,
            effort_hours=row.get('effort_hours'),
            priority=row.get('priority', 3),
            assigned_to=row.get('assigned_to'),
            status=TaskStatus(row.get('status', TaskStatus.DRAFT.value)),
            blocked_reason=row.get('blocked_reason'),
            # NEW (Migration 0011): Scheduling field
            due_date=_parse_datetime(row.get('due_date')),
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
            started_at=_parse_datetime(row.get('started_at')),
            completed_at=_parse_datetime(row.get('completed_at')),
        )


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from database value"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None