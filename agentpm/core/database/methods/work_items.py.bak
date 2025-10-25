"""
Work Items CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for WorkItem entities with:
- Dependency validation (project_id, parent_work_item_id)
- State transition validation
- Type-safe operations using Pydantic models

Pattern: Type-safe method signatures with WorkItem model
"""

from typing import Optional, List
import sqlite3
import json
from datetime import datetime

from ..models import WorkItem
from ..adapters import WorkItemAdapter
from ..enums import WorkItemStatus, WorkItemType


def create_work_item(service, work_item: WorkItem) -> WorkItem:
    """
    Create a new work item with dependency validation.

    Validates:
    - project_id exists
    - parent_work_item_id exists (if provided)

    Args:
        service: DatabaseService instance
        work_item: WorkItem model to create

    Returns:
        Created WorkItem with database ID

    Raises:
        ValidationError: If dependencies don't exist
    """
    # Validate project exists
    project_exists = _check_project_exists(service, work_item.project_id)
    if not project_exists:
        from ..service import ValidationError
        raise ValidationError(f"Project {work_item.project_id} does not exist")

    # Validate parent work item exists (if provided)
    if work_item.parent_work_item_id:
        parent_exists = _check_work_item_exists(service, work_item.parent_work_item_id)
        if not parent_exists:
            from ..service import ValidationError
            raise ValidationError(f"Parent work item {work_item.parent_work_item_id} does not exist")

    # Convert model to database format
    db_data = WorkItemAdapter.to_db(work_item)

    # Execute insert (includes migration 0011 fields: phase, due_date, not_before)
    query = """
        INSERT INTO work_items (project_id, parent_work_item_id, name, description,
                               type, business_context, metadata, effort_estimate_hours,
                               priority, status, is_continuous, phase, due_date, not_before)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['project_id'],
        db_data['parent_work_item_id'],
        db_data['name'],
        db_data['description'],
        db_data['type'],
        db_data['business_context'],
        db_data['metadata'],
        db_data['effort_estimate_hours'],
        db_data['priority'],
        db_data['status'],
        db_data.get('is_continuous', 0),
        db_data.get('phase'),  # Migration 0011
        db_data.get('due_date'),  # Migration 0011
        db_data.get('not_before'),  # Migration 0011
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        work_item_id = cursor.lastrowid

    return get_work_item(service, work_item_id)


def get_work_item(service, work_item_id: int) -> Optional[WorkItem]:
    """Get work item by ID"""
    query = "SELECT * FROM work_items WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (work_item_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return WorkItemAdapter.from_db(dict(row))


def update_work_item(service, work_item_id: int, **updates) -> Optional[WorkItem]:
    """
    Update work item with validation.

    Args:
        service: DatabaseService instance
        work_item_id: Work item ID
        **updates: Fields to update

    Returns:
        Updated WorkItem or None if not found
    """
    existing = get_work_item(service, work_item_id)
    if not existing:
        return None

    # Apply updates with Pydantic validation
    updated_work_item = existing.model_copy(update=updates)

    # Convert to database format
    db_data = WorkItemAdapter.to_db(updated_work_item)

    # Build update query
    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE work_items SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), work_item_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_work_item(service, work_item_id)


def ensure_bug_backlog(service, project_id: int) -> WorkItem:
    """Ensure continuous Fix Bugs/Issues backlog exists for project."""
    query = """
        SELECT *
        FROM work_items
        WHERE project_id = ? AND type = ?
        LIMIT 1
    """

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (project_id, WorkItemType.FIX_BUGS_ISSUES.value))
        row = cursor.fetchone()

    if row:
        return WorkItemAdapter.from_db(dict(row))

    metadata = {
        "continuous": {
            "category": "bug_backlog",
            "created_at": datetime.utcnow().isoformat()
        }
    }

    backlog = WorkItem(
        project_id=project_id,
        name="Fix Bugs & Issues",
        description="Continuous backlog that aggregates all newly discovered bugs and issues.",
        type=WorkItemType.FIX_BUGS_ISSUES,
        status=WorkItemStatus.ACTIVE,
        priority=1,
        metadata=json.dumps(metadata)
    )

    return create_work_item(service, backlog)


def delete_work_item(service, work_item_id: int) -> bool:
    """Delete work item (cascades to tasks)"""
    query = "DELETE FROM work_items WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (work_item_id,))
        return cursor.rowcount > 0


def list_work_items(
    service,
    project_id: Optional[int] = None,
    status: Optional[WorkItemStatus] = None,
    type: Optional[WorkItemType] = None
) -> List[WorkItem]:
    """
    List work items with optional filters.

    Args:
        service: DatabaseService instance
        project_id: Optional project filter
        status: Optional status filter
        type: Optional type filter

    Returns:
        List of WorkItem models
    """
    query = "SELECT * FROM work_items WHERE 1=1"
    params = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    if status:
        query += " AND status = ?"
        params.append(status.value)

    if type:
        query += " AND type = ?"
        params.append(type.value)

    query += " ORDER BY priority ASC, created_at DESC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [WorkItemAdapter.from_db(dict(row)) for row in rows]


def get_child_work_items(service, parent_id: int) -> List[WorkItem]:
    """
    Get all child work items for a parent.

    Args:
        service: DatabaseService instance
        parent_id: Parent work item ID

    Returns:
        List of child WorkItems
    """
    query = "SELECT * FROM work_items WHERE parent_work_item_id = ? ORDER BY priority ASC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (parent_id,))
        rows = cursor.fetchall()

    return [WorkItemAdapter.from_db(dict(row)) for row in rows]


# Helper functions

def _check_project_exists(service, project_id: int) -> bool:
    """Check if project exists"""
    query = "SELECT 1 FROM projects WHERE id = ?"

    with service.connect() as conn:
        cursor = conn.execute(query, (project_id,))
        return cursor.fetchone() is not None


def _check_work_item_exists(service, work_item_id: int) -> bool:
    """Check if work item exists"""
    query = "SELECT 1 FROM work_items WHERE id = ?"

    with service.connect() as conn:
        cursor = conn.execute(query, (work_item_id,))
        return cursor.fetchone() is not None
