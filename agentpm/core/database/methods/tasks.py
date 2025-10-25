"""
Tasks CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Task entities with:
- Dependency validation (work_item_id)
- Completion timestamp tracking
- Assignment management

Pattern: Type-safe method signatures with Task model
"""

from typing import Optional, List
import sqlite3
from datetime import datetime

from ..models import Task
from ..adapters import TaskAdapter
from ..enums import TaskStatus, TaskType


# TaskType to Sub-Agent Auto-Assignment Mapping
# Maps each TaskType to the appropriate sub-agent responsible for that work
# Import the mapping utility
from ..utils.task_agent_mapping import get_agent_for_task_type


def create_task(service, task: Task) -> Task:
    """
    Create a new task with dependency validation and auto-assignment.

    Validates:
    - work_item_id exists
    - assigned_to agent exists (if provided)

    Auto-assigns sub-agent based on TaskType if no agent specified.

    Args:
        service: DatabaseService instance
        task: Task model to create

    Returns:
        Created Task with database ID
    """
    # Validate work item exists
    work_item_exists = _check_work_item_exists(service, task.work_item_id)
    if not work_item_exists:
        from ..service import ValidationError
        raise ValidationError(f"Work item {task.work_item_id} does not exist")

    # Auto-assign sub-agent if not already assigned
    if not task.assigned_to and task.type:
        task.assigned_to = get_agent_for_task_type(task.type)

    # Validate assigned agent exists (if assigned and validation enabled)
    if task.assigned_to:
        from ...agents.registry_validator import validate_agent_with_suggestions
        agent_valid, error_msg = validate_agent_with_suggestions(task.assigned_to)
        if not agent_valid:
            from ..service import ValidationError
            raise ValidationError(error_msg)

    # Convert model to database format
    db_data = TaskAdapter.to_db(task)

    # Execute insert
    query = """
        INSERT INTO tasks (work_item_id, name, description, type, quality_metadata,
                          effort_hours, priority, assigned_to, status, blocked_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['work_item_id'],
        db_data['name'],
        db_data['description'],
        db_data['type'],
        db_data['quality_metadata'],
        db_data['effort_hours'],
        db_data['priority'],
        db_data['assigned_to'],
        db_data['status'],
        db_data['blocked_reason'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        task_id = cursor.lastrowid

    return get_task(service, task_id)


def get_task(service, task_id: int) -> Optional[Task]:
    """Get task by ID"""
    query = "SELECT * FROM tasks WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (task_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return TaskAdapter.from_db(dict(row))


def update_task(service, task_id: int, **updates) -> Optional[Task]:
    """
    Update task with validation.

    Automatically sets completed_at when status changes to DONE.

    Args:
        service: DatabaseService instance
        task_id: Task ID
        **updates: Fields to update

    Returns:
        Updated Task or None if not found
    """
    existing = get_task(service, task_id)
    if not existing:
        return None

    # Check if status is changing to DONE
    if 'status' in updates and updates['status'] == TaskStatus.DONE:
        if existing.status != TaskStatus.DONE:
            # First completion - set completed_at
            updates['completed_at'] = datetime.now()

    # Apply updates with Pydantic validation
    updated_task = existing.model_copy(update=updates)

    # Convert to database format
    db_data = TaskAdapter.to_db(updated_task)

    # Build update query (include completed_at if in updates)
    if 'completed_at' in updates:
        set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
        query = f"UPDATE tasks SET {set_clause}, completed_at = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params = (*db_data.values(), updates['completed_at'], task_id)
    else:
        set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
        query = f"UPDATE tasks SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params = (*db_data.values(), task_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_task(service, task_id)


def delete_task(service, task_id: int) -> bool:
    """Delete task by ID"""
    query = "DELETE FROM tasks WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (task_id,))
        return cursor.rowcount > 0


def list_tasks(
    service,
    work_item_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[str] = None
) -> List[Task]:
    """
    List tasks with optional filters.

    Args:
        service: DatabaseService instance
        work_item_id: Optional work item filter
        status: Optional status filter
        assigned_to: Optional assignment filter

    Returns:
        List of Task models
    """
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if work_item_id:
        query += " AND work_item_id = ?"
        params.append(work_item_id)

    if status:
        query += " AND status = ?"
        params.append(status.value)

    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)

    query += " ORDER BY priority ASC, created_at DESC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [TaskAdapter.from_db(dict(row)) for row in rows]


def mark_task_blocked(service, task_id: int, reason: str) -> Optional[Task]:
    """
    Mark task as blocked with reason.

    Args:
        service: DatabaseService instance
        task_id: Task ID
        reason: Blocking reason

    Returns:
        Updated Task or None if not found
    """
    return update_task(service, task_id, status=TaskStatus.BLOCKED, blocked_reason=reason)


def complete_task(service, task_id: int) -> Optional[Task]:
    """
    Mark task as completed (sets completed_at timestamp).

    Args:
        service: DatabaseService instance
        task_id: Task ID

    Returns:
        Completed Task or None if not found
    """
    return update_task(service, task_id, status=TaskStatus.DONE)


def assign_task(service, task_id: int, assigned_to: str) -> Optional[Task]:
    """
    Assign task to agent or user.

    Args:
        service: DatabaseService instance
        task_id: Task ID
        assigned_to: Agent role or user name

    Returns:
        Updated Task or None if not found
    """
    return update_task(service, task_id, assigned_to=assigned_to)


# Helper functions

def _check_work_item_exists(service, work_item_id: int) -> bool:
    """Check if work item exists"""
    query = "SELECT 1 FROM work_items WHERE id = ?"

    with service.connect() as conn:
        cursor = conn.execute(query, (work_item_id,))
        return cursor.fetchone() is not None


def _validate_agent_exists(agent_name: str) -> bool:
    """
    Validate that sub-agent exists in .claude/agents/sub-agents/ directory.

    Args:
        agent_name: Name of sub-agent (without .md extension)

    Returns:
        True if agent file exists, False otherwise
    """
    import os
    from pathlib import Path

    # Get project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    agents_dir = project_root / ".claude" / "agents" / "sub-agents"

    # Check if agent file exists
    agent_file = agents_dir / f"{agent_name}.md"
    return agent_file.exists()


def _get_valid_agents() -> List[str]:
    """
    Get list of all valid sub-agent names from .claude/agents/sub-agents/ directory.

    Returns:
        List of valid agent names (without .md extension)
    """
    import os
    from pathlib import Path

    # Get project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    agents_dir = project_root / ".claude" / "agents" / "sub-agents"

    # Get all .md files in sub-agents directory
    if not agents_dir.exists():
        return []

    agent_files = agents_dir.glob("*.md")
    return sorted([f.stem for f in agent_files])