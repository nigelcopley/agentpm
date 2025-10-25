"""
Idea Adapter - Model ↔ Database Conversion

Handles conversion between Idea domain models and database rows.
Includes tags JSON serialization and enum conversions + CRUD operations.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.idea import Idea
from ..enums import IdeaStatus, IdeaSource, WorkItemType


class IdeaAdapter:
    """Handles Idea model <-> Database row conversions + CRUD operations"""

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, idea: Idea) -> Idea:
        """
        Create a new idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea: Validated Idea Pydantic model

        Returns:
            Created Idea with database ID

        Example:
            >>> from agentpm.core.database.adapters import IdeaAdapter
            >>> idea = Idea(title="New Feature", project_id=1, ...)
            >>> created = IdeaAdapter.create(db, idea)
        """
        from ..methods import ideas as idea_methods
        return idea_methods.create_idea(service, idea)

    @staticmethod
    def get(service, idea_id: int) -> Optional[Idea]:
        """
        Get idea by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID

        Returns:
            Idea if found, None otherwise
        """
        from ..methods import ideas as idea_methods
        return idea_methods.get_idea(service, idea_id)

    @staticmethod
    def list(
        service,
        project_id: Optional[int] = None,
        status: Optional[IdeaStatus] = None,
        tags: Optional[List[str]] = None,
        source: Optional[IdeaSource] = None,
        sort_by: str = "created_at",
        ascending: bool = False
    ) -> List[Idea]:
        """
        List ideas with optional filters (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Optional project ID to filter by
            status: Optional status to filter by
            tags: Optional list of tags to filter by
            source: Optional source to filter by
            sort_by: Sort field (default: created_at)
            ascending: Sort direction (default: False)

        Returns:
            List of Idea models
        """
        from ..methods import ideas as idea_methods
        return idea_methods.list_ideas(
            service,
            project_id=project_id,
            status=status,
            tags=tags,
            source=source,
            sort_by=sort_by,
            ascending=ascending
        )

    @staticmethod
    def update(service, idea: Idea) -> Idea:
        """
        Update idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea: Updated Idea model

        Returns:
            Updated Idea
        """
        from ..methods import ideas as idea_methods
        return idea_methods.update_idea(service, idea)

    @staticmethod
    def vote(service, idea_id: int, delta: int = 1) -> Idea:
        """
        Vote on idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            delta: Vote delta (+1 for upvote, -1 for downvote)

        Returns:
            Updated Idea with new vote count
        """
        from ..methods import ideas as idea_methods
        return idea_methods.vote_on_idea(service, idea_id, delta=delta)

    @staticmethod
    def transition(service, idea_id: int, new_status: IdeaStatus) -> Idea:
        """
        Transition idea to new status (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            new_status: New status

        Returns:
            Updated Idea

        Raises:
            ValueError: If transition is not allowed
        """
        from ..methods import ideas as idea_methods
        return idea_methods.transition_idea(service, idea_id, new_status)

    @staticmethod
    def reject(service, idea_id: int, reason: str) -> Idea:
        """
        Reject idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            reason: Rejection reason

        Returns:
            Updated Idea with rejected status
        """
        from ..methods import ideas as idea_methods
        return idea_methods.reject_idea(service, idea_id, reason)

    @staticmethod
    def convert_to_work_item(
        service,
        idea_id: int,
        work_item_type: WorkItemType,
        transfer_context: bool = True
    ) -> tuple[Idea, 'WorkItem']:
        """
        Convert idea to work item (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            work_item_type: Type of work item to create
            transfer_context: Whether to transfer rich context

        Returns:
            Tuple of (updated Idea, created WorkItem)
        """
        from ..methods import ideas as idea_methods
        return idea_methods.convert_idea_to_work_item(
            service,
            idea_id,
            work_item_type,
            transfer_context=transfer_context
        )

    @staticmethod
    def delete(service, idea_id: int) -> bool:
        """
        Delete idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import ideas as idea_methods
        return idea_methods.delete_idea(service, idea_id)

    @staticmethod
    def create_rich_context(
        service,
        idea_id: int,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create rich context for idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID
            context_data: Context data dictionary

        Returns:
            Created context dictionary
        """
        from ..methods import ideas as idea_methods
        return idea_methods.create_idea_rich_context(service, idea_id, context_data)

    @staticmethod
    def get_rich_contexts(service, idea_id: int) -> List[Dict[str, Any]]:
        """
        Get rich contexts for idea (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID

        Returns:
            List of context dictionaries
        """
        from ..methods import ideas as idea_methods
        return idea_methods.get_idea_rich_contexts(service, idea_id)

    @staticmethod
    def validate_context_completeness(service, idea_id: int) -> tuple[bool, List[str]]:
        """
        Validate idea context completeness (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID

        Returns:
            Tuple of (is_complete, list of missing fields)
        """
        from ..methods import ideas as idea_methods
        return idea_methods.validate_idea_context_completeness(service, idea_id)

    @staticmethod
    def assemble_context(service, idea_id: int) -> Dict[str, Any]:
        """
        Assemble complete idea context (CLI entry point).

        Args:
            service: DatabaseService instance
            idea_id: Idea ID

        Returns:
            Complete context dictionary
        """
        from ..methods import ideas as idea_methods
        return idea_methods.assemble_idea_context(service, idea_id)

    # ============================================================================
    # CONVERSION METHODS
    # ============================================================================

    @staticmethod
    def to_db(idea: Idea) -> Dict[str, Any]:
        """
        Convert Idea model to database row format.

        Args:
            idea: Idea domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'project_id': idea.project_id,
            'title': idea.title,
            'description': idea.description,
            'source': idea.source.value,
            'created_by': idea.created_by,
            'votes': idea.votes,
            'tags': json.dumps(idea.tags) if idea.tags else '[]',
            'status': idea.status.value,
            'rejection_reason': idea.rejection_reason,
            'converted_to_work_item_id': idea.converted_to_work_item_id,
            'converted_at': idea.converted_at.isoformat() if idea.converted_at else None,
            # Note: created_at, updated_at set by triggers
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Idea:
        """
        Convert database row to Idea model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Idea model
        """
        # Parse tags JSON
        tags_value = row.get('tags', '[]')
        if isinstance(tags_value, str):
            tags = json.loads(tags_value)
        else:
            tags = tags_value if tags_value else []

        return Idea(
            id=row.get('id'),
            project_id=row['project_id'],
            title=row['title'],
            description=row.get('description'),
            source=IdeaSource(row.get('source', IdeaSource.USER.value)),
            created_by=row.get('created_by'),
            votes=row.get('votes', 0),
            tags=tags,
            status=IdeaStatus(row.get('status', IdeaStatus.IDEA.value)),
            rejection_reason=row.get('rejection_reason'),
            converted_to_work_item_id=row.get('converted_to_work_item_id'),
            converted_at=_parse_datetime(row.get('converted_at')),
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
