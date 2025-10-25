"""
Projects CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Project entities using:
- Pydantic models for type safety
- Adapters for model ↔ database conversion
- State validation for workflow enforcement

Pattern: Type-safe method signatures with Project model
Reference: /aipm-cli-backup/aipm_cli/services/database/methods/projects.py
"""

from typing import Optional, List
import sqlite3

from ..models import Project
from ..adapters import ProjectAdapter
from ..enums import ProjectStatus


def create_project(service, project: Project) -> Project:
    """
    Create a new project.

    Type-safe: accepts Project model, returns Project model.

    Args:
        service: DatabaseService instance
        project: Project model to create

    Returns:
        Created Project with database ID

    Raises:
        ValidationError: If project data is invalid
        TransactionError: If database operation fails

    Example:
        project = Project(name="APM (Agent Project Manager)", path="/path/to/project")
        created = create_project(service, project)
        print(f"Created project {created.id}")
    """
    # Convert model to database format
    db_data = ProjectAdapter.to_db(project)

    # Execute insert
    query = """
        INSERT INTO projects (name, description, path, tech_stack,
                             detected_frameworks, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['name'],
        db_data['description'],
        db_data['path'],
        db_data['tech_stack'],
        db_data['detected_frameworks'],
        db_data['status'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        project_id = cursor.lastrowid

    # Return created project with ID
    return get_project(service, project_id)


def get_project(service, project_id: int) -> Optional[Project]:
    """
    Get project by ID.

    Args:
        service: DatabaseService instance
        project_id: Project ID

    Returns:
        Project model or None if not found

    Example:
        project = get_project(service, 1)
        if project:
            print(f"Found: {project.name}")
    """
    query = "SELECT * FROM projects WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (project_id,))
        row = cursor.fetchone()

    if not row:
        return None

    # Convert row to validated Project model
    return ProjectAdapter.from_db(dict(row))


def get_project_by_name(service, name: str) -> Optional[Project]:
    """
    Get project by name.

    Args:
        service: DatabaseService instance
        name: Project name

    Returns:
        Project model or None if not found
    """
    query = "SELECT * FROM projects WHERE name = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (name,))
        row = cursor.fetchone()

    if not row:
        return None

    return ProjectAdapter.from_db(dict(row))


def update_project(service, project_id: int, **updates) -> Optional[Project]:
    """
    Update project with keyword arguments.

    Type-safe: Pydantic validates before database update.

    Args:
        service: DatabaseService instance
        project_id: Project ID
        **updates: Fields to update (name, description, status, etc.)

    Returns:
        Updated Project model or None if project not found

    Example:
        updated = update_project(service, 1, status=ProjectStatus.ACTIVE)
        updated = update_project(service, 1, tech_stack=["Python", "Django"])
    """
    # Get existing project
    existing = get_project(service, project_id)
    if not existing:
        return None

    # Apply updates to model (Pydantic validates)
    updated_project = existing.model_copy(update=updates)

    # Convert to database format
    db_data = ProjectAdapter.to_db(updated_project)

    # Build update query
    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE projects SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), project_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_project(service, project_id)


def delete_project(service, project_id: int) -> bool:
    """
    Delete project by ID.

    Cascades to work_items, tasks, contexts, rules via foreign keys.

    Args:
        service: DatabaseService instance
        project_id: Project ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM projects WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (project_id,))
        return cursor.rowcount > 0


def list_projects(service, status: Optional[ProjectStatus] = None) -> List[Project]:
    """
    List all projects, optionally filtered by status.

    Args:
        service: DatabaseService instance
        status: Optional status filter

    Returns:
        List of Project models

    Example:
        all_projects = list_projects(service)
        active_projects = list_projects(service, status=ProjectStatus.ACTIVE)
    """
    if status:
        query = "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC"
        params = (status.value,)
    else:
        query = "SELECT * FROM projects ORDER BY created_at DESC"
        params = ()

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

    return [ProjectAdapter.from_db(dict(row)) for row in rows]


def update_tech_stack(service, project_id: int, tech_stack: List[str]) -> Optional[Project]:
    """
    Update project tech stack (detected technologies).

    Args:
        service: DatabaseService instance
        project_id: Project ID
        tech_stack: List of technologies

    Returns:
        Updated Project or None if not found

    Example:
        updated = update_tech_stack(service, 1, ["Python", "Django", "PostgreSQL"])
    """
    return update_project(service, project_id, tech_stack=tech_stack)


def update_status(service, project_id: int, new_status: ProjectStatus) -> Optional[Project]:
    """
    Update project status with validation.

    Args:
        service: DatabaseService instance
        project_id: Project ID
        new_status: New status

    Returns:
        Updated Project or None if not found

    Note: State transition validation will be added in utils/state_validators.py
    """
    return update_project(service, project_id, status=new_status)