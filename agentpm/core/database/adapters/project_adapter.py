"""
Project Adapter - Model ↔ Database Conversion

Handles conversion between Project domain models and database rows.
Clean separation: business logic (model) != persistence (database).

Pattern: Adapter with to_db() and from_db() methods + CRUD operations
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.project import Project
from ..enums import ProjectStatus, ProjectType


class ProjectAdapter:
    """
    Handles Project model <-> Database row conversions.

    Responsibilities:
    - Convert Pydantic models to database dictionaries
    - Convert database rows to Pydantic models
    - Handle JSON serialization (tech_stack, rules_config)
    - Handle enum conversion (status, development_philosophy)
    - Handle datetime formatting
    - Provide CRUD operations (CLI entry points)
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, project: Project) -> Project:
        """
        Create a new project (CLI entry point).

        Args:
            service: DatabaseService instance
            project: Validated Project Pydantic model

        Returns:
            Created Project with database ID

        Example:
            >>> from agentpm.core.database.adapters import ProjectAdapter
            >>> project = Project(name="AIPM", path="/path/to/project")
            >>> created = ProjectAdapter.create(db, project)
        """
        from ..methods import projects as project_methods
        return project_methods.create_project(service, project)

    @staticmethod
    def get(service, project_id: int) -> Optional[Project]:
        """
        Get project by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID

        Returns:
            Project if found, None otherwise
        """
        from ..methods import projects as project_methods
        return project_methods.get_project(service, project_id)

    @staticmethod
    def get_by_name(service, name: str) -> Optional[Project]:
        """
        Get project by name (CLI entry point).

        Args:
            service: DatabaseService instance
            name: Project name

        Returns:
            Project if found, None otherwise
        """
        from ..methods import projects as project_methods
        return project_methods.get_project_by_name(service, name)

    @staticmethod
    def list(service, status: Optional[ProjectStatus] = None) -> List[Project]:
        """
        List projects with optional status filter (CLI entry point).

        Args:
            service: DatabaseService instance
            status: Optional status to filter by

        Returns:
            List of Project models
        """
        from ..methods import projects as project_methods
        return project_methods.list_projects(service, status=status)

    @staticmethod
    def update(service, project_id: int, **updates) -> Optional[Project]:
        """
        Update project fields (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID to update
            **updates: Field updates

        Returns:
            Updated Project or None if not found
        """
        from ..methods import projects as project_methods
        return project_methods.update_project(service, project_id, **updates)

    @staticmethod
    def delete(service, project_id: int) -> bool:
        """
        Delete project (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import projects as project_methods
        return project_methods.delete_project(service, project_id)

    @staticmethod
    def update_tech_stack(service, project_id: int, tech_stack: List[str]) -> Optional[Project]:
        """
        Update project tech stack (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            tech_stack: List of technologies

        Returns:
            Updated Project or None if not found
        """
        from ..methods import projects as project_methods
        return project_methods.update_tech_stack(service, project_id, tech_stack)

    @staticmethod
    def update_status(service, project_id: int, new_status: ProjectStatus) -> Optional[Project]:
        """
        Update project status (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            new_status: New status

        Returns:
            Updated Project or None if not found
        """
        from ..methods import projects as project_methods
        return project_methods.update_status(service, project_id, new_status)

    # ============================================================================
    # CONVERSION METHODS
    # ============================================================================

    @staticmethod
    def to_db(project: Project) -> Dict[str, Any]:
        """
        Convert Project model to database row format.

        Args:
            project: Project domain model

        Returns:
            Dictionary ready for database insertion/update

        Example:
            project = Project(name="AIPM", path="/path/to/project")
            db_data = ProjectAdapter.to_db(project)
            # db_data = {'name': 'AIPM', 'path': '/path/to/project', ...}
        """
        return {
            'name': project.name,
            'description': project.description,
            'path': project.path,

            # JSON serialization for lists
            'tech_stack': json.dumps(project.tech_stack) if project.tech_stack else '[]',
            'detected_frameworks': json.dumps(project.detected_frameworks) if project.detected_frameworks else '[]',

            # Configuration metadata (WI-40)
            'metadata': project.metadata or '{}',

            # Enum to string
            'status': project.status.value,

            # NEW (Migration 0011): Business and team fields
            'business_domain': project.business_domain,
            'business_description': project.business_description,
            'project_type': project.project_type.value if project.project_type else None,
            'team': project.team,

            # Note: timestamps handled by database (CURRENT_TIMESTAMP)
            # We don't include created_at/updated_at in inserts/updates
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Project:
        """
        Convert database row to Project model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Project model

        Example:
            cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (1,))
            row = dict(cursor.fetchone())
            project = ProjectAdapter.from_db(row)
            # project is validated Pydantic model
        """
        # Parse project_type enum
        project_type_value = row.get('project_type')
        project_type = ProjectType(project_type_value) if project_type_value else None

        return Project(
            id=row.get('id'),
            name=row['name'],
            description=row.get('description'),
            path=row['path'],

            # JSON deserialization for lists
            tech_stack=json.loads(row.get('tech_stack', '[]')),
            detected_frameworks=json.loads(row.get('detected_frameworks', '[]')),

            # Configuration metadata (WI-40)
            metadata=row.get('metadata', '{}'),

            # String to enum
            status=ProjectStatus(row.get('status', ProjectStatus.INITIATED.value)),

            # NEW (Migration 0011): Business and team fields
            business_domain=row.get('business_domain'),
            business_description=row.get('business_description'),
            project_type=project_type,
            team=row.get('team'),

            # Datetime fields
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
        )


def _parse_datetime(value: Any) -> datetime | None:
    """
    Parse datetime from database value.

    SQLite stores datetimes as strings, this converts them back.

    Args:
        value: String datetime from database or None

    Returns:
        datetime object or None
    """
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    # SQLite datetime format: "YYYY-MM-DD HH:MM:SS"
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None