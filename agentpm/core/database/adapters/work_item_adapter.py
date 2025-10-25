"""
WorkItem Adapter - Model ↔ Database Conversion

Handles conversion between WorkItem domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.work_item import WorkItem
from ..enums import WorkItemStatus, WorkItemType, Phase


class WorkItemAdapter:
    """
    Handles WorkItem model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, work_item: WorkItem) -> WorkItem:
        """
        Create a new work item (CLI entry point).

        Three-layer pattern:
          1. Validate Pydantic model (automatic via type hints)
          2. Delegate to methods layer
          3. Return validated WorkItem

        Args:
            service: DatabaseService instance
            work_item: Validated WorkItem Pydantic model

        Returns:
            Created WorkItem with database ID

        Raises:
            ValidationError: If project_id or parent_work_item_id invalid

        Example:
            >>> from agentpm.core.database.adapters import WorkItemAdapter
            >>> work_item = WorkItem(name="Feature", type=WorkItemType.FEATURE, ...)
            >>> created = WorkItemAdapter.create(db, work_item)
        """
        from ..methods import work_items as wi_methods
        return wi_methods.create_work_item(service, work_item)

    @staticmethod
    def get(service, work_item_id: int) -> Optional[WorkItem]:
        """
        Get work item by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            work_item_id: Work item ID

        Returns:
            WorkItem if found, None otherwise
        """
        from ..methods import work_items as wi_methods
        return wi_methods.get_work_item(service, work_item_id)

    @staticmethod
    def list(service, project_id: Optional[int] = None) -> List[WorkItem]:
        """
        List work items with optional project filter (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Optional project ID to filter by

        Returns:
            List of WorkItem models
        """
        from ..methods import work_items as wi_methods
        return wi_methods.list_work_items(service, project_id=project_id)

    @staticmethod
    def update(service, work_item_id: int, **updates) -> WorkItem:
        """
        Update work item fields (CLI entry point).

        Args:
            service: DatabaseService instance
            work_item_id: Work item ID to update
            **updates: Field updates (e.g., name="New Name", status=WorkItemStatus.IN_PROGRESS)

        Returns:
            Updated WorkItem

        Raises:
            ValidationError: If work_item_id not found
        """
        from ..methods import work_items as wi_methods
        return wi_methods.update_work_item(service, work_item_id, **updates)

    @staticmethod
    def delete(service, work_item_id: int) -> bool:
        """
        Delete work item by ID (CLI entry point).

        Three-layer pattern:
          1. Validate work item exists
          2. Delegate to methods layer (cascades to tasks)
          3. Return success status

        Args:
            service: DatabaseService instance
            work_item_id: Work item ID to delete

        Returns:
            True if deleted, False if not found

        Note:
            This will cascade delete all associated tasks.

        Example:
            >>> from agentpm.core.database.adapters import WorkItemAdapter
            >>> success = WorkItemAdapter.delete(db, 123)
        """
        from ..methods import work_items as wi_methods
        return wi_methods.delete_work_item(service, work_item_id)

    # ============================================================================
    # MODEL CONVERSION (Internal Use)
    # ============================================================================

    @staticmethod
    def to_db(work_item: WorkItem) -> Dict[str, Any]:
        """
        Convert WorkItem model to database row format.

        Args:
            work_item: WorkItem domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'project_id': work_item.project_id,
            'parent_work_item_id': work_item.parent_work_item_id,
            'name': work_item.name,
            'description': work_item.description,
            'type': work_item.type.value,
            'business_context': work_item.business_context,
            'metadata': work_item.metadata or '{}',  # WI-40 consolidation
            'effort_estimate_hours': work_item.effort_estimate_hours,
            'priority': work_item.priority,
            'status': work_item.status.value,
            'is_continuous': 1 if (work_item.is_continuous or WorkItemType.is_continuous_type(work_item.type)) else 0,
            # NEW (Migration 0011): Phase and scheduling fields
            'phase': work_item.phase.value if work_item.phase else None,
            'due_date': work_item.due_date.isoformat() if work_item.due_date else None,
            'not_before': work_item.not_before.isoformat() if work_item.not_before else None,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> WorkItem:
        """
        Convert database row to WorkItem model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated WorkItem model
        """
        # Parse phase enum
        phase_value = row.get('phase')
        phase = Phase(phase_value) if phase_value else None

        work_item_type = WorkItemType(row.get('type', WorkItemType.FEATURE.value))
        raw_continuous = row.get('is_continuous')
        is_continuous_flag = False
        if raw_continuous is not None:
            try:
                is_continuous_flag = int(raw_continuous) == 1
            except (TypeError, ValueError):
                is_continuous_flag = bool(raw_continuous)

        return WorkItem(
            id=row.get('id'),
            project_id=row['project_id'],
            parent_work_item_id=row.get('parent_work_item_id'),
            name=row['name'],
            description=row.get('description'),
            type=work_item_type,
            business_context=row.get('business_context'),
            metadata=row.get('metadata', '{}'),  # WI-40 consolidation
            effort_estimate_hours=row.get('effort_estimate_hours'),
            priority=row.get('priority', 3),
            status=WorkItemStatus(row.get('status', WorkItemStatus.DRAFT.value)),
            is_continuous=is_continuous_flag or WorkItemType.is_continuous_type(work_item_type),
            # NEW (Migration 0011): Phase and scheduling fields
            phase=phase,
            due_date=_parse_datetime(row.get('due_date')),
            not_before=_parse_datetime(row.get('not_before')),
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
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
