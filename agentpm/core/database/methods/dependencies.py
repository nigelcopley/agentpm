"""
Dependencies and Blockers CRUD Methods

Type-safe operations for managing task/work item relationships.

Pattern: Type-safe method signatures with dependency models
"""

from typing import List, Optional
import sqlite3

from ..models.dependencies import TaskDependency, TaskBlocker, WorkItemDependency
from ..adapters.dependencies_adapter import (
    TaskDependencyAdapter,
    TaskBlockerAdapter,
    WorkItemDependencyAdapter
)


# ========== TASK DEPENDENCIES ==========

def add_task_dependency(
    service,
    task_id: int,
    depends_on_task_id: int,
    dependency_type: str = 'hard',
    notes: Optional[str] = None
) -> TaskDependency:
    """
    Add dependency between tasks.

    Args:
        service: DatabaseService
        task_id: Task that has dependency
        depends_on_task_id: Task that must complete first
        dependency_type: 'hard' or 'soft'
        notes: Optional explanation

    Returns:
        Created TaskDependency

    Raises:
        ValidationError: If tasks don't exist or circular dependency
    """
    from . import tasks

    # Validate both tasks exist
    task = tasks.get_task(service, task_id)
    dep_task = tasks.get_task(service, depends_on_task_id)

    if not task or not dep_task:
        from ..service import ValidationError
        raise ValidationError("Task not found")

    # Prevent self-dependency
    if task_id == depends_on_task_id:
        from ..service import ValidationError
        raise ValidationError("Task cannot depend on itself")

    # Check for circular dependency
    if _would_create_cycle(service, task_id, depends_on_task_id):
        from ..service import ValidationError
        raise ValidationError(f"Would create circular dependency")

    # Create dependency
    dependency = TaskDependency(
        task_id=task_id,
        depends_on_task_id=depends_on_task_id,
        dependency_type=dependency_type,
        notes=notes
    )

    db_data = TaskDependencyAdapter.to_db(dependency)

    query = """
        INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type, notes)
        VALUES (?, ?, ?, ?)
    """
    params = (
        db_data['task_id'],
        db_data['depends_on_task_id'],
        db_data['dependency_type'],
        db_data['notes']
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        dep_id = cursor.lastrowid

    return get_task_dependency(service, dep_id)


def get_task_dependency(service, dependency_id: int) -> Optional[TaskDependency]:
    """Get dependency by ID"""
    query = "SELECT * FROM task_dependencies WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (dependency_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return TaskDependencyAdapter.from_db(dict(row))


def get_task_dependencies(service, task_id: int) -> List[TaskDependency]:
    """Get all dependencies for a task (what this task depends on)"""
    query = "SELECT * FROM task_dependencies WHERE task_id = ? ORDER BY created_at"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (task_id,))
        rows = cursor.fetchall()

    return [TaskDependencyAdapter.from_db(dict(row)) for row in rows]


def get_tasks_depending_on(service, task_id: int) -> List[TaskDependency]:
    """Get all tasks that depend on this task (reverse lookup)"""
    query = "SELECT * FROM task_dependencies WHERE depends_on_task_id = ? ORDER BY created_at"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (task_id,))
        rows = cursor.fetchall()

    return [TaskDependencyAdapter.from_db(dict(row)) for row in rows]


def remove_task_dependency(service, dependency_id: int) -> bool:
    """Remove dependency"""
    query = "DELETE FROM task_dependencies WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (dependency_id,))
        return cursor.rowcount > 0


def _would_create_cycle(service, task_id: int, depends_on_task_id: int) -> bool:
    """
    Check if adding dependency would create circular dependency.

    Uses depth-first search to detect cycles.
    """
    def has_path(from_id: int, to_id: int, visited: set) -> bool:
        """Check if path exists from from_id to to_id"""
        if from_id == to_id:
            return True

        if from_id in visited:
            return False

        visited.add(from_id)

        # Get what from_id depends on
        deps = get_task_dependencies(service, from_id)
        for dep in deps:
            if has_path(dep.depends_on_task_id, to_id, visited):
                return True

        return False

    # Check if depends_on_task_id has path back to task_id
    return has_path(depends_on_task_id, task_id, set())


# ========== TASK BLOCKERS ==========

def add_task_blocker(
    service,
    task_id: int,
    blocker_type: str,
    blocker_task_id: Optional[int] = None,
    blocker_description: Optional[str] = None,
    blocker_reference: Optional[str] = None
) -> TaskBlocker:
    """
    Add blocker to task.

    Args:
        service: DatabaseService
        task_id: Task being blocked
        blocker_type: 'task' or 'external'
        blocker_task_id: Blocking task ID (if type='task')
        blocker_description: Description (if type='external')
        blocker_reference: External reference (if type='external')

    Returns:
        Created TaskBlocker
    """
    from . import tasks

    # Validate task exists
    task = tasks.get_task(service, task_id)
    if not task:
        from ..service import ValidationError
        raise ValidationError(f"Task {task_id} not found")

    # Validate blocker_task exists if type='task'
    if blocker_type == 'task':
        if not blocker_task_id:
            from ..service import ValidationError
            raise ValidationError("blocker_task_id required for task blockers")

        blocker_task = tasks.get_task(service, blocker_task_id)
        if not blocker_task:
            from ..service import ValidationError
            raise ValidationError(f"Blocker task {blocker_task_id} not found")

    # Validate external blocker has description
    if blocker_type == 'external' and not blocker_description:
        from ..service import ValidationError
        raise ValidationError("blocker_description required for external blockers")

    # Create blocker
    blocker = TaskBlocker(
        task_id=task_id,
        blocker_type=blocker_type,
        blocker_task_id=blocker_task_id,
        blocker_description=blocker_description,
        blocker_reference=blocker_reference
    )

    db_data = TaskBlockerAdapter.to_db(blocker)

    query = """
        INSERT INTO task_blockers (
            task_id, blocker_type, blocker_task_id,
            blocker_description, blocker_reference, is_resolved
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['task_id'],
        db_data['blocker_type'],
        db_data['blocker_task_id'],
        db_data['blocker_description'],
        db_data['blocker_reference'],
        db_data['is_resolved']
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        blocker_id = cursor.lastrowid

    return get_task_blocker(service, blocker_id)


def get_task_blocker(service, blocker_id: int) -> Optional[TaskBlocker]:
    """Get blocker by ID"""
    query = "SELECT * FROM task_blockers WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (blocker_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return TaskBlockerAdapter.from_db(dict(row))


def get_task_blockers(service, task_id: int, unresolved_only: bool = False) -> List[TaskBlocker]:
    """Get all blockers for a task"""
    query = "SELECT * FROM task_blockers WHERE task_id = ?"

    if unresolved_only:
        query += " AND is_resolved = 0"

    query += " ORDER BY created_at"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (task_id,))
        rows = cursor.fetchall()

    return [TaskBlockerAdapter.from_db(dict(row)) for row in rows]


def resolve_task_blocker(
    service,
    blocker_id: int,
    resolution_notes: str
) -> Optional[TaskBlocker]:
    """
    Mark blocker as resolved.

    Args:
        service: DatabaseService
        blocker_id: Blocker ID
        resolution_notes: How it was resolved

    Returns:
        Updated TaskBlocker
    """
    query = """
        UPDATE task_blockers
        SET is_resolved = 1,
            resolved_at = CURRENT_TIMESTAMP,
            resolution_notes = ?
        WHERE id = ?
    """

    with service.transaction() as conn:
        conn.execute(query, (resolution_notes, blocker_id))

    return get_task_blocker(service, blocker_id)


def remove_task_blocker(service, blocker_id: int) -> bool:
    """Remove blocker"""
    query = "DELETE FROM task_blockers WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (blocker_id,))
        return cursor.rowcount > 0


# ========== WORK ITEM DEPENDENCIES ==========

def add_work_item_dependency(
    service,
    work_item_id: int,
    depends_on_work_item_id: int,
    dependency_type: str = 'hard',
    notes: Optional[str] = None
) -> WorkItemDependency:
    """Add dependency between work items"""
    from . import work_items

    # Validate both exist
    wi = work_items.get_work_item(service, work_item_id)
    dep_wi = work_items.get_work_item(service, depends_on_work_item_id)

    if not wi or not dep_wi:
        from ..service import ValidationError
        raise ValidationError("Work item not found")

    # Prevent self-dependency
    if work_item_id == depends_on_work_item_id:
        from ..service import ValidationError
        raise ValidationError("Work item cannot depend on itself")

    # Create dependency
    dependency = WorkItemDependency(
        work_item_id=work_item_id,
        depends_on_work_item_id=depends_on_work_item_id,
        dependency_type=dependency_type,
        notes=notes
    )

    db_data = WorkItemDependencyAdapter.to_db(dependency)

    query = """
        INSERT INTO work_item_dependencies (
            work_item_id, depends_on_work_item_id, dependency_type, notes
        )
        VALUES (?, ?, ?, ?)
    """
    params = (
        db_data['work_item_id'],
        db_data['depends_on_work_item_id'],
        db_data['dependency_type'],
        db_data['notes']
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        dep_id = cursor.lastrowid

    return get_work_item_dependency(service, dep_id)


def get_work_item_dependency(service, dependency_id: int) -> Optional[WorkItemDependency]:
    """Get work item dependency by ID"""
    query = "SELECT * FROM work_item_dependencies WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (dependency_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return WorkItemDependencyAdapter.from_db(dict(row))


def get_work_item_dependencies(service, work_item_id: int) -> List[WorkItemDependency]:
    """Get all dependencies for a work item"""
    query = "SELECT * FROM work_item_dependencies WHERE work_item_id = ? ORDER BY created_at"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (work_item_id,))
        rows = cursor.fetchall()

    return [WorkItemDependencyAdapter.from_db(dict(row)) for row in rows]


def get_work_item_dependents(service, work_item_id: int) -> List[WorkItemDependency]:
    """Get all work items that depend on this work item"""
    query = "SELECT * FROM work_item_dependencies WHERE depends_on_work_item_id = ? ORDER BY created_at"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (work_item_id,))
        rows = cursor.fetchall()

    return [WorkItemDependencyAdapter.from_db(dict(row)) for row in rows]


def remove_work_item_dependency(service, dependency_id: int) -> bool:
    """Remove work item dependency"""
    query = "DELETE FROM work_item_dependencies WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (dependency_id,))
        return cursor.rowcount > 0