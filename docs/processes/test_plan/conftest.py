"""
Pytest fixtures for migration testing.

Provides reusable fixtures for testing database migrations with:
- Temporary SQLite databases
- Migration manager setup
- Test data factories
- Schema inspection utilities
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from typing import Generator, Dict, Any, List
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.migrations.manager import MigrationManager
from agentpm.core.database.migrations.registry import MigrationRegistry


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """
    Create a temporary SQLite database file.

    Yields:
        Path to temporary database file

    Cleanup:
        Automatically removes database file after test
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def fresh_db_service(temp_db_path: Path) -> DatabaseService:
    """
    Create a fresh DatabaseService with migrations applied.

    This fixture creates a new database and runs all migrations.
    Use this when you need a fully initialized database.

    Args:
        temp_db_path: Temporary database path fixture

    Returns:
        DatabaseService instance with all migrations applied
    """
    # Create database service (automatically runs migrations)
    return DatabaseService(temp_db_path)


@pytest.fixture
def empty_db_service(temp_db_path: Path) -> DatabaseService:
    """
    Create a DatabaseService WITHOUT running migrations.

    This fixture creates a database with only the schema_migrations table.
    Use this when you want to manually control which migrations run.

    Args:
        temp_db_path: Temporary database path fixture

    Returns:
        DatabaseService instance with no migrations applied
    """
    # Create empty database
    conn = sqlite3.connect(str(temp_db_path))

    # Create schema_migrations table only
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rollback_at TIMESTAMP DEFAULT NULL,
            rollback_reason TEXT DEFAULT NULL,
            applied_by TEXT DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()

    # Create service pointing to this database
    # We need to monkey-patch to prevent auto-migration
    class NoMigrationDatabaseService(DatabaseService):
        def _initialize_schema(self):
            pass  # Skip migration

        def _run_pending_migrations(self):
            pass  # Skip migration

    return NoMigrationDatabaseService(temp_db_path)


@pytest.fixture
def migration_manager(fresh_db_service: DatabaseService) -> MigrationManager:
    """
    Create a MigrationManager for testing.

    Args:
        fresh_db_service: DatabaseService fixture

    Returns:
        MigrationManager instance
    """
    return MigrationManager(fresh_db_service)


@pytest.fixture
def schema_inspector():
    """
    Factory for inspecting database schema.

    Returns:
        SchemaInspector instance with utility methods
    """
    class SchemaInspector:
        """Utility for inspecting SQLite schema"""

        @staticmethod
        def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
            """
            Get column information for a table.

            Args:
                conn: SQLite connection
                table_name: Table to inspect

            Returns:
                List of column info dicts with keys: cid, name, type, notnull, dflt_value, pk
            """
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                })
            return columns

        @staticmethod
        def column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
            """
            Check if a column exists in a table.

            Args:
                conn: SQLite connection
                table_name: Table to check
                column_name: Column to check

            Returns:
                True if column exists, False otherwise
            """
            columns = SchemaInspector.get_table_columns(conn, table_name)
            return any(col['name'] == column_name for col in columns)

        @staticmethod
        def get_column_info(conn: sqlite3.Connection, table_name: str, column_name: str) -> Dict[str, Any]:
            """
            Get detailed information about a column.

            Args:
                conn: SQLite connection
                table_name: Table containing column
                column_name: Column to inspect

            Returns:
                Column info dict or empty dict if not found
            """
            columns = SchemaInspector.get_table_columns(conn, table_name)
            for col in columns:
                if col['name'] == column_name:
                    return col
            return {}

        @staticmethod
        def get_table_indexes(conn: sqlite3.Connection, table_name: str) -> List[str]:
            """
            Get indexes for a table.

            Args:
                conn: SQLite connection
                table_name: Table to inspect

            Returns:
                List of index names
            """
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?",
                (table_name,)
            )
            return [row[0] for row in cursor.fetchall()]

        @staticmethod
        def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
            """
            Check if a table exists.

            Args:
                conn: SQLite connection
                table_name: Table to check

            Returns:
                True if table exists, False otherwise
            """
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None

    return SchemaInspector()


@pytest.fixture
def test_project_factory():
    """
    Factory for creating test project data.

    Returns:
        Function that inserts a test project and returns its ID
    """
    def create_test_project(conn: sqlite3.Connection, name: str = "Test Project") -> int:
        """
        Create a test project in the database.

        Args:
            conn: SQLite connection
            name: Project name

        Returns:
            Project ID
        """
        # Check if metadata column exists (it was added in migration 0018)
        cursor = conn.execute("PRAGMA table_info(projects)")
        columns = {row[1] for row in cursor.fetchall()}
        has_metadata = 'metadata' in columns

        if has_metadata:
            cursor = conn.execute("""
                INSERT INTO projects (
                    name, description, path, tech_stack, metadata,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                "Test project for migration testing",
                "/tmp/test-project",
                json.dumps(["Python", "SQLite"]),
                "{}",
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        else:
            # Older schema without metadata
            cursor = conn.execute("""
                INSERT INTO projects (
                    name, description, path, tech_stack,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                "Test project for migration testing",
                "/tmp/test-project",
                json.dumps(["Python", "SQLite"]),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        return cursor.lastrowid

    return create_test_project


@pytest.fixture
def test_agent_factory():
    """
    Factory for creating test agent data.

    Returns:
        Function that inserts a test agent and returns its ID
    """
    def create_test_agent(
        conn: sqlite3.Connection,
        project_id: int,
        role: str = "test-agent",
        **kwargs
    ) -> int:
        """
        Create a test agent in the database.

        Args:
            conn: SQLite connection
            project_id: Project to associate with
            role: Agent role
            **kwargs: Additional agent fields

        Returns:
            Agent ID
        """
        cursor = conn.execute("""
            INSERT INTO agents (
                project_id, role, display_name, description,
                is_active, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            role,
            kwargs.get('display_name', f"Test Agent {role}"),
            kwargs.get('description', "Test agent for migration testing"),
            kwargs.get('is_active', 1),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        return cursor.lastrowid

    return create_test_agent


@pytest.fixture
def migration_state_factory():
    """
    Factory for setting up specific migration states.

    Returns:
        Function that applies migrations up to a specific version
    """
    def apply_migrations_up_to(
        db_service: DatabaseService,
        target_version: str
    ) -> MigrationManager:
        """
        Apply migrations up to and including the target version.

        Args:
            db_service: DatabaseService instance
            target_version: Version to migrate to (e.g., "0026")

        Returns:
            MigrationManager instance
        """
        manager = MigrationManager(db_service)
        pending = manager.get_pending_migrations()

        target_version_int = int(target_version)

        for migration in pending:
            migration_version_int = int(migration.version)
            if migration_version_int <= target_version_int:
                manager.run_migration(migration)
            else:
                break

        return manager

    return apply_migrations_up_to
