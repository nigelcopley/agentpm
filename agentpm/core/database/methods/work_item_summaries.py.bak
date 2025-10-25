"""
Work Item Summaries CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for WorkItemSummary entities with:
- Work item existence validation
- Recent summaries query for session-start agents
- Type filtering (session/milestone/decision)

Pattern: Type-safe method signatures with WorkItemSummary model
"""

from typing import Optional, List
import sqlite3

from ..models.work_item_summary import WorkItemSummary
from ..adapters.work_item_summary_adapter import WorkItemSummaryAdapter


def create_summary(service, summary: WorkItemSummary) -> WorkItemSummary:
    """
    Create a new work item summary with validation.

    Validates:
    - work_item_id exists

    Args:
        service: DatabaseService instance
        summary: WorkItemSummary model to create

    Returns:
        Created WorkItemSummary with database ID

    Raises:
        ValidationError: If work item doesn't exist
    """
    # Validate work item exists
    work_item_exists = _check_work_item_exists(service, summary.work_item_id)
    if not work_item_exists:
        from ..service import ValidationError
        raise ValidationError(f"Work item {summary.work_item_id} does not exist")

    # Convert model to database format
    db_data = WorkItemSummaryAdapter.to_db(summary)

    # Execute insert
    query = """
        INSERT INTO work_item_summaries (
            work_item_id, session_date, session_duration_hours,
            summary_text, context_metadata, created_by, summary_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['work_item_id'],
        db_data['session_date'],
        db_data['session_duration_hours'],
        db_data['summary_text'],
        db_data['context_metadata'],
        db_data['created_by'],
        db_data['summary_type'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        summary_id = cursor.lastrowid

    return get_summary(service, summary_id)


def get_summary(service, summary_id: int) -> Optional[WorkItemSummary]:
    """
    Get summary by ID.

    Args:
        service: DatabaseService instance
        summary_id: Summary ID

    Returns:
        WorkItemSummary or None if not found
    """
    query = "SELECT * FROM work_item_summaries WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (summary_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return WorkItemSummaryAdapter.from_db(dict(row))


def list_summaries(
    service,
    work_item_id: Optional[int] = None,
    summary_type: Optional[str] = None,
    limit: int = 100
) -> List[WorkItemSummary]:
    """
    List summaries with optional filters.

    Args:
        service: DatabaseService instance
        work_item_id: Filter by work item (optional)
        summary_type: Filter by type (session/milestone/decision) (optional)
        limit: Maximum results (default: 100)

    Returns:
        List of WorkItemSummary models (chronological, newest first)
    """
    query = "SELECT * FROM work_item_summaries WHERE 1=1"
    params = []

    if work_item_id is not None:
        query += " AND work_item_id = ?"
        params.append(work_item_id)

    if summary_type is not None:
        query += " AND summary_type = ?"
        params.append(summary_type)

    query += " ORDER BY session_date DESC, id DESC LIMIT ?"
    params.append(limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [WorkItemSummaryAdapter.from_db(dict(row)) for row in rows]


def get_recent_summaries(
    service,
    work_item_id: int,
    limit: int = 5
) -> List[WorkItemSummary]:
    """
    Get N most recent summaries for work item.

    Optimized query for session-start agents needing
    recent context from previous sessions.

    Args:
        service: DatabaseService instance
        work_item_id: Work item ID
        limit: Number of recent summaries (default: 5)

    Returns:
        List of WorkItemSummary models (newest first)
    """
    return list_summaries(service, work_item_id=work_item_id, limit=limit)


def delete_summary(service, summary_id: int) -> bool:
    """
    Delete summary by ID.

    Args:
        service: DatabaseService instance
        summary_id: Summary ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM work_item_summaries WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (summary_id,))
        return cursor.rowcount > 0


def _check_work_item_exists(service, work_item_id: int) -> bool:
    """Check if work item exists"""
    query = "SELECT 1 FROM work_items WHERE id = ?"

    with service.connect() as conn:
        cursor = conn.execute(query, (work_item_id,))
        return cursor.fetchone() is not None
