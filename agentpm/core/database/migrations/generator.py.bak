"""
Migration Generator

Generates migration files from schema changes detected by SchemaDiffer.

Features:
- Auto-increments migration version (0002, 0003, ...)
- Creates migration_NNNN.py files with upgrade/downgrade functions
- Validates migration code before writing
- Detects and warns about irreversible/destructive operations

Design:
- Takes list of SchemaChange objects from SchemaDiffer
- Generates Python code with proper formatting
- Writes to migrations/files/ directory
- Follows migration file template pattern

Reference: Task #111 - Migration Auto-Generation
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from .differ import (
    SchemaChange,
    ChangeType,
    TableChange,
    ColumnChange,
    IndexChange,
    TriggerChange
)


class MigrationGenerationError(Exception):
    """Migration generation failed"""
    pass


class MigrationGenerator:
    """
    Generates migration files from schema changes.

    Usage:
        from agentpm.core.database import DatabaseService
        from agentpm.core.database.migrations import SchemaDiffer, MigrationGenerator

        db = DatabaseService("path/to/db.sqlite")
        differ = SchemaDiffer(db)
        generator = MigrationGenerator(db)

        # Detect changes
        changes = differ.compare_schemas(target_schema)

        # Generate migration file
        migration_file = generator.generate_migration_file(
            changes=changes,
            description="Add quality_metadata column"
        )

        print(f"Generated: {migration_file}")
    """

    def __init__(
        self,
        db_service: 'DatabaseService',  # type: ignore
        migrations_dir: Optional[Path] = None
    ):
        """
        Initialize migration generator.

        Args:
            db_service: Database service instance
            migrations_dir: Path to migrations/files/ directory (auto-detected if None)
        """
        self.db_service = db_service

        if migrations_dir is None:
            # Auto-detect: agentpm/core/database/migrations/files/
            package_dir = Path(__file__).parent
            self.migrations_dir = package_dir / "files"
        else:
            self.migrations_dir = Path(migrations_dir)

        # Ensure directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def generate_migration_file(
        self,
        changes: List[SchemaChange],
        description: str,
        author: Optional[str] = None
    ) -> Path:
        """
        Generate a migration file from schema changes.

        Args:
            changes: List of schema changes
            description: Human-readable description of migration
            author: Optional author name (defaults to "auto-generated")

        Returns:
            Path to generated migration file

        Raises:
            MigrationGenerationError: If generation fails
        """
        if not changes:
            raise MigrationGenerationError("No schema changes to generate migration from")

        # Get next version number
        version = self.get_next_version()

        # Generate migration code
        upgrade_code = self._generate_upgrade_code(changes)
        downgrade_code = self._generate_downgrade_code(changes)

        # Write migration file
        migration_file = self.write_migration_file(
            version=version,
            description=description,
            upgrade_code=upgrade_code,
            downgrade_code=downgrade_code,
            author=author or "auto-generated"
        )

        return migration_file

    def get_next_version(self) -> str:
        """
        Get next migration version number.

        Scans existing migration files and returns next version.

        Returns:
            Next version as 4-digit string (e.g., "0006")
        """
        # Scan for existing migration files
        existing_versions = []

        for file_path in self.migrations_dir.glob("migration_*.py"):
            # Extract version from filename: migration_0001.py → 0001
            version_str = file_path.stem.split("_")[1]
            try:
                existing_versions.append(int(version_str))
            except ValueError:
                # Skip malformed filenames
                continue

        # Next version = max + 1 (or 0001 if no migrations exist)
        next_version = max(existing_versions, default=0) + 1

        # Format as 4-digit string
        return f"{next_version:04d}"

    def write_migration_file(
        self,
        version: str,
        description: str,
        upgrade_code: str,
        downgrade_code: str,
        author: str = "auto-generated"
    ) -> Path:
        """
        Write migration file to disk.

        Args:
            version: Migration version (e.g., "0006")
            description: Human-readable description
            upgrade_code: Python code for upgrade() function
            downgrade_code: Python code for downgrade() function
            author: Author name

        Returns:
            Path to written migration file

        Raises:
            MigrationGenerationError: If file already exists or write fails
        """
        # Construct filename
        filename = f"migration_{version}.py"
        file_path = self.migrations_dir / filename

        # Check if file already exists
        if file_path.exists():
            raise MigrationGenerationError(
                f"Migration file {filename} already exists"
            )

        # Generate complete migration file content
        content = self._generate_migration_template(
            version=version,
            description=description,
            upgrade_code=upgrade_code,
            downgrade_code=downgrade_code,
            author=author
        )

        # Validate generated code (basic syntax check)
        try:
            compile(content, filename, 'exec')
        except SyntaxError as e:
            raise MigrationGenerationError(
                f"Generated migration has syntax error: {e}"
            ) from e

        # Write to file
        try:
            file_path.write_text(content, encoding='utf-8')
        except IOError as e:
            raise MigrationGenerationError(
                f"Failed to write migration file: {e}"
            ) from e

        return file_path

    def detect_conflicts(self, changes: List[SchemaChange]) -> List[str]:
        """
        Detect conflicting changes.

        Args:
            changes: List of schema changes

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Group changes by object name
        changes_by_object = {}
        for change in changes:
            key = change.object_name
            if key not in changes_by_object:
                changes_by_object[key] = []
            changes_by_object[key].append(change)

        # Check for conflicts
        for object_name, object_changes in changes_by_object.items():
            if len(object_changes) <= 1:
                continue

            change_types = [c.change_type for c in object_changes]

            # Conflict: ADD + DROP same object
            if ChangeType.ADD_TABLE in change_types and ChangeType.DROP_TABLE in change_types:
                conflicts.append(
                    f"Conflict: {object_name} has both ADD and DROP table operations"
                )

            # Conflict: ADD + DROP column on same table
            if isinstance(object_changes[0], ColumnChange):
                table_name = object_changes[0].table_name
                if ChangeType.ADD_COLUMN in change_types and ChangeType.DROP_COLUMN in change_types:
                    conflicts.append(
                        f"Conflict: {table_name}.{object_name} has both ADD and DROP column operations"
                    )

        return conflicts

    def warn_destructive_operations(self, changes: List[SchemaChange]) -> List[str]:
        """
        Identify destructive operations that lose data.

        Args:
            changes: List of schema changes

        Returns:
            List of warning messages
        """
        warnings = []

        for change in changes:
            if change.destructive:
                warnings.append(
                    f"WARNING: {change.change_type.value} on {change.object_name} is destructive (loses data)"
                )

            if not change.reversible:
                warnings.append(
                    f"WARNING: {change.change_type.value} on {change.object_name} is not reversible"
                )

        return warnings

    def _generate_upgrade_code(self, changes: List[SchemaChange]) -> str:
        """
        Generate Python code for upgrade() function.

        Args:
            changes: List of schema changes

        Returns:
            Python code as string
        """
        lines = []

        for change in changes:
            sql = change.to_sql()

            if sql.startswith("--"):
                # Comment line (e.g., SQLite limitation)
                lines.append(f"    # {sql[3:]}")
            else:
                # Actual SQL statement
                # Escape triple quotes in SQL
                sql_escaped = sql.replace('"""', r'\"\"\"')
                lines.append(f'    conn.execute("""{sql_escaped}""")')

        return "\n".join(lines) if lines else "    pass  # No operations"

    def _generate_downgrade_code(self, changes: List[SchemaChange]) -> str:
        """
        Generate Python code for downgrade() function.

        Args:
            changes: List of schema changes

        Returns:
            Python code as string
        """
        lines = []

        # Process changes in reverse order
        for change in reversed(changes):
            rollback_sql = change.to_rollback_sql()

            if rollback_sql is None:
                # Not reversible
                lines.append(
                    f"    # WARNING: Cannot reverse {change.change_type.value} on {change.object_name}"
                )
            elif rollback_sql.startswith("--"):
                # Comment line
                lines.append(f"    # {rollback_sql[3:]}")
            else:
                # Actual SQL statement
                sql_escaped = rollback_sql.replace('"""', r'\"\"\"')
                lines.append(f'    conn.execute("""{sql_escaped}""")')

        return "\n".join(lines) if lines else "    pass  # No rollback operations"

    def _generate_migration_template(
        self,
        version: str,
        description: str,
        upgrade_code: str,
        downgrade_code: str,
        author: str
    ) -> str:
        """
        Generate complete migration file content.

        Args:
            version: Migration version (e.g., "0006")
            description: Human-readable description
            upgrade_code: Code for upgrade() function body
            downgrade_code: Code for downgrade() function body
            author: Author name

        Returns:
            Complete Python file content
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        template = f'''"""
Migration {version}: {description}

Auto-generated migration file.

Author: {author}
Date: {date_str}
"""

import sqlite3

VERSION = "{version}"
DESCRIPTION = "{description}"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply forward migration.
    """
{upgrade_code}


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration.
    """
{downgrade_code}


def validate_pre(conn: sqlite3.Connection) -> bool:
    """
    Pre-migration validation (optional).

    Returns:
        True if safe to proceed
    """
    return True


def validate_post(conn: sqlite3.Connection) -> bool:
    """
    Post-migration validation (optional).

    Returns:
        True if migration succeeded
    """
    return True
'''

        return template
