"""
Idea Element Adapter - Model ↔ Database Conversion

Handles conversion between IdeaElement domain models and database rows.
Includes enum conversions and CRUD operations.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from ..models.idea_element import IdeaElement
from ..enums import TaskType


class IdeaElementAdapter:
    """Handles IdeaElement model <-> Database row conversions + CRUD operations"""

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, element: IdeaElement) -> IdeaElement:
        """
        Create a new idea element (CLI entry point).

        Args:
            service: DatabaseService instance
            element: Validated IdeaElement Pydantic model

        Returns:
            Created IdeaElement with database ID

        Example:
            >>> from agentpm.core.database.adapters import IdeaElementAdapter
            >>> element = IdeaElement(idea_id=1, title="Component", ...)
            >>> created = IdeaElementAdapter.create(db, element)
        """
        from ..methods import idea_elements as element_methods
        return element_methods.create_idea_element(service, element)

    @staticmethod
    def get(service, element_id: int) -> Optional[IdeaElement]:
        """
        Get idea element by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            element_id: Element ID

        Returns:
            IdeaElement if found, None otherwise
        """
        from ..methods import idea_elements as element_methods
        return element_methods.get_idea_element(service, element_id)

    @staticmethod
    def list(
        service,
        idea_id: int,
        include_completed: bool = True,
        order_by: str = "order_index"
    ) -> List[IdeaElement]:
        """
        List idea elements for an idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID to get elements for
            include_completed: Whether to include completed elements
            order_by: Sort field (order_index, created_at, effort_hours)

        Returns:
            List of IdeaElement models
        """
        from ..methods import idea_elements as element_methods
        return element_methods.list_idea_elements(
            service,
            idea_id=idea_id,
            include_completed=include_completed,
            order_by=order_by
        )

    @staticmethod
    def update(service, element: IdeaElement) -> IdeaElement:
        """
        Update idea element (CLI entry point).

        Args:
            service: DatabaseService instance
            element: Updated IdeaElement model

        Returns:
            Updated IdeaElement
        """
        from ..methods import idea_elements as element_methods
        return element_methods.update_idea_element(service, element)

    @staticmethod
    def mark_completed(service, element_id: int) -> IdeaElement:
        """
        Mark idea element as completed (CLI entry point).

        Args:
            service: DatabaseService instance
            element_id: Element ID

        Returns:
            Updated IdeaElement with completed status
        """
        from ..methods import idea_elements as element_methods
        return element_methods.mark_element_completed(service, element_id)

    @staticmethod
    def mark_incomplete(service, element_id: int) -> IdeaElement:
        """
        Mark idea element as incomplete (CLI entry point).

        Args:
            service: DatabaseService instance
            element_id: Element ID

        Returns:
            Updated IdeaElement with incomplete status
        """
        from ..methods import idea_elements as element_methods
        return element_methods.mark_element_incomplete(service, element_id)

    @staticmethod
    def reorder(service, idea_id: int, element_orders: List[Tuple[int, int]]) -> List[IdeaElement]:
        """
        Reorder idea elements within an idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            element_orders: List of (element_id, new_order_index) tuples

        Returns:
            List of updated IdeaElement models
        """
        from ..methods import idea_elements as element_methods
        return element_methods.reorder_elements(service, idea_id, element_orders)

    @staticmethod
    def delete(service, element_id: int) -> bool:
        """
        Delete idea element (CLI entry point).

        Args:
            service: DatabaseService instance
            element_id: Element ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import idea_elements as element_methods
        return element_methods.delete_idea_element(service, element_id)

    @staticmethod
    def get_completion_stats(service, idea_id: int) -> Dict[str, Any]:
        """
        Get completion statistics for an idea's elements (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID

        Returns:
            Dictionary with completion statistics
        """
        from ..methods import idea_elements as element_methods
        return element_methods.get_idea_completion_stats(service, idea_id)

    @staticmethod
    def delete(service, element_id: int) -> bool:
        """
        Delete idea element (Web interface entry point).

        Args:
            service: DatabaseService instance
            element_id: Element ID to delete

        Returns:
            True if deleted successfully
        """
        from ..methods import idea_elements as element_methods
        return element_methods.delete_idea_element(service, element_id)

    # ============================================================================
    # CONVERSION METHODS
    # ============================================================================

    @staticmethod
    def to_db(element: IdeaElement) -> Dict[str, Any]:
        """
        Convert IdeaElement model to database row format.

        Args:
            element: IdeaElement domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'idea_id': element.idea_id,
            'title': element.title,
            'description': element.description,
            'type': element.type.value,
            'effort_hours': element.effort_hours,
            'order_index': element.order_index,
            'is_completed': 1 if element.is_completed else 0,
            'completed_at': element.completed_at.isoformat() if element.completed_at else None,
            # Note: created_at, updated_at set by triggers
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> IdeaElement:
        """
        Convert database row to IdeaElement model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated IdeaElement model
        """
        return IdeaElement(
            id=row.get('id'),
            idea_id=row['idea_id'],
            title=row['title'],
            description=row.get('description'),
            type=TaskType(row.get('type', TaskType.IMPLEMENTATION.value)),
            effort_hours=row.get('effort_hours', 0.0),
            order_index=row.get('order_index', 0),
            is_completed=bool(row.get('is_completed', 0)),
            completed_at=_parse_datetime(row.get('completed_at')),
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
        )


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse datetime from database value"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None
