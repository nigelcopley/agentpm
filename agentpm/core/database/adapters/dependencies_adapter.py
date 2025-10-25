"""
Dependencies and Blockers Adapters - Model ↔ Database Conversion

Handles conversion for relationship models.

Pattern: Adapter with to_db() and from_db() methods
"""

from typing import Dict, Any
from datetime import datetime

from ..models.dependencies import TaskDependency, TaskBlocker, WorkItemDependency


class TaskDependencyAdapter:
    """Handles TaskDependency model <-> Database row conversions"""

    @staticmethod
    def to_db(dependency: TaskDependency) -> Dict[str, Any]:
        """Convert TaskDependency model to database row"""
        return {
            'task_id': dependency.task_id,
            'depends_on_task_id': dependency.depends_on_task_id,
            'dependency_type': dependency.dependency_type,
            'notes': dependency.notes
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> TaskDependency:
        """Convert database row to TaskDependency model"""
        return TaskDependency(
            id=row.get('id'),
            task_id=row['task_id'],
            depends_on_task_id=row['depends_on_task_id'],
            dependency_type=row.get('dependency_type', 'hard'),
            notes=row.get('notes'),
            created_at=_parse_datetime(row.get('created_at'))
        )


class TaskBlockerAdapter:
    """Handles TaskBlocker model <-> Database row conversions"""

    @staticmethod
    def to_db(blocker: TaskBlocker) -> Dict[str, Any]:
        """Convert TaskBlocker model to database row"""
        return {
            'task_id': blocker.task_id,
            'blocker_type': blocker.blocker_type,
            'blocker_task_id': blocker.blocker_task_id,
            'blocker_description': blocker.blocker_description,
            'blocker_reference': blocker.blocker_reference,
            'is_resolved': 1 if blocker.is_resolved else 0,
            'resolved_at': blocker.resolved_at,
            'resolution_notes': blocker.resolution_notes
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> TaskBlocker:
        """Convert database row to TaskBlocker model"""
        return TaskBlocker(
            id=row.get('id'),
            task_id=row['task_id'],
            blocker_type=row['blocker_type'],
            blocker_task_id=row.get('blocker_task_id'),
            blocker_description=row.get('blocker_description'),
            blocker_reference=row.get('blocker_reference'),
            is_resolved=bool(row.get('is_resolved', 0)),
            resolved_at=_parse_datetime(row.get('resolved_at')),
            resolution_notes=row.get('resolution_notes'),
            created_at=_parse_datetime(row.get('created_at'))
        )


class WorkItemDependencyAdapter:
    """Handles WorkItemDependency model <-> Database row conversions"""

    @staticmethod
    def to_db(dependency: WorkItemDependency) -> Dict[str, Any]:
        """Convert WorkItemDependency model to database row"""
        return {
            'work_item_id': dependency.work_item_id,
            'depends_on_work_item_id': dependency.depends_on_work_item_id,
            'dependency_type': dependency.dependency_type,
            'notes': dependency.notes
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> WorkItemDependency:
        """Convert database row to WorkItemDependency model"""
        return WorkItemDependency(
            id=row.get('id'),
            work_item_id=row['work_item_id'],
            depends_on_work_item_id=row['depends_on_work_item_id'],
            dependency_type=row.get('dependency_type', 'hard'),
            notes=row.get('notes'),
            created_at=_parse_datetime(row.get('created_at'))
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