"""
Database Service - Gold Standard Service Pattern

This is the foundational service for APM (Agent Project Manager), implementing the service coordinator
pattern that all other V2 services will follow.

Architecture:
- Service coordinator (this file)
- Method modules (methods/)
- Data models (models/)
- Adapters (adapters/)

Pattern Reference: /aipm-cli-backup/aipm_cli/services/database/service.py
"""

import sqlite3
import json
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union
from datetime import datetime


class DatabaseService:
    """
    Unified database service with clean, modular method organization.

    Gold standard service pattern for all APM (Agent Project Manager) services:
    - Connection management with context managers
    - Transaction handling with auto-commit/rollback
    - JSON serialization utilities
    - Comprehensive error handling
    - Method module delegation

    Example:
        service = DatabaseService("~/.aipm/aipm.db")

        # Query with connection
        with service.connect() as conn:
            result = conn.execute("SELECT * FROM projects").fetchall()

        # Multi-operation transaction
        with service.transaction() as conn:
            conn.execute("INSERT INTO projects ...")
            conn.execute("INSERT INTO work_items ...")
            # Auto-commits if no exception
    """

    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize database service.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path).expanduser()
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing database service: {self.db_path}")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize schema if database doesn't exist, or run migrations if it does
        if not self.db_path.exists():
            self.logger.info("Database not found, initializing schema")
            self._initialize_schema()
        else:
            # Database exists - check for pending migrations
            self.logger.info("Database exists, checking for pending migrations")
            self._run_pending_migrations()

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Automatically closes connection after use.
        Enables foreign key constraints.
        Sets row_factory for dict-like access.

        Yields:
            sqlite3.Connection: Database connection

        Raises:
            ConnectionError: If connection fails

        Example:
            with service.connect() as conn:
                result = conn.execute("SELECT * FROM projects").fetchall()
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Dict-like row access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints

            try:
                yield conn
            finally:
                conn.close()

        except sqlite3.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database transactions.

        Automatically commits on success, rolls back on exception.

        Yields:
            sqlite3.Connection: Database connection with transaction

        Raises:
            TransactionError: If transaction fails

        Example:
            with service.transaction() as conn:
                conn.execute("INSERT INTO projects ...")
                conn.execute("INSERT INTO work_items ...")
                # Auto-commits if no exception, rolls back on error
        """
        with self.connect() as conn:
            try:
                yield conn
                conn.commit()
                self.logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                self.logger.error(f"Transaction rolled back due to error: {e}")
                raise TransactionError(f"Transaction failed: {e}") from e

    def serialize_json_field(self, value: Any) -> str:
        """
        Serialize value to JSON string for database storage.

        Handles datetime objects and None values properly.

        Args:
            value: Any Python object

        Returns:
            JSON string representation

        Example:
            tech_stack = ["Python", "Django", "PostgreSQL"]
            json_str = service.serialize_json_field(tech_stack)
            # Store json_str in database
        """
        if value is None:
            return "null"

        try:
            # default=str handles datetime and other non-serializable types
            return json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            self.logger.warning(f"JSON serialization failed for {value}: {e}")
            return "null"

    def deserialize_json_field(
        self,
        value: Optional[str],
        default: Any = None
    ) -> Any:
        """
        Deserialize JSON string from database.

        Args:
            value: JSON string from database
            default: Default value if deserialization fails

        Returns:
            Deserialized Python object

        Example:
            json_str = row["tech_stack"]
            tech_stack = service.deserialize_json_field(json_str, default=[])
        """
        if not value or value == "null":
            return default if default is not None else {}

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"JSON deserialization failed for '{value}': {e}")
            return default if default is not None else {}

    def _initialize_schema(self) -> None:
        """
        Initialize database schema using migration system.

        This method is called automatically if database doesn't exist.
        Uses the migration system to ensure consistency.
        """
        from .migrations import MigrationManager

        self.logger.info("Initializing database schema via migrations")
        
        # Create schema_migrations table first (chicken-and-egg problem)
        with self.transaction() as conn:
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
        
        # Run all pending migrations
        migration_manager = MigrationManager(self)
        success_count, failure_count = migration_manager.run_all_pending()
        
        if failure_count > 0:
            self.logger.warning(f"Schema initialization completed with {failure_count} migration failures")
        else:
            self.logger.info("Database schema initialized successfully via migrations")

    def _run_pending_migrations(self) -> None:
        """
        Run pending migrations for existing database.
        
        This method is called when a database already exists to ensure
        it's up to date with the latest schema.
        """
        from .migrations import MigrationManager

        self.logger.info("Checking for pending migrations")
        
        # Run all pending migrations
        migration_manager = MigrationManager(self)
        success_count, failure_count = migration_manager.run_all_pending()
        
        if failure_count > 0:
            self.logger.warning(f"Migration check completed with {failure_count} migration failures")
        elif success_count > 0:
            self.logger.info(f"Applied {success_count} pending migrations")
        else:
            self.logger.info("Database is up to date - no pending migrations")

    @property
    def sessions(self):
        """Access session tracking operations.

        Provides tool-agnostic session management supporting multiple AI tools
        (Claude Code, Cursor, Windsurf, Aider, manual CLI) and LLMs.

        Methods:
            - CRUD: create_session, end_session, get_session, update_session, delete_session
            - Queries: list_sessions, get_sessions_by_date_range, get_sessions_by_work_item, get_sessions_by_developer
            - Analytics: search_decisions, get_session_stats, get_active_sessions

        Example:
            >>> db = DatabaseService("path/to/db")
            >>> session = Session(session_id="uuid", project_id=1, tool_name=SessionTool.CLAUDE_CODE, ...)
            >>> created = db.sessions.create_session(db, session)
            >>> all_sessions = db.sessions.list_sessions(db, project_id=1)
        """
        if not hasattr(self, '_sessions'):
            from agentpm.core.database.methods import sessions as session_methods
            self._sessions = session_methods
        return self._sessions

    @property
    def ideas(self):
        """Access ideas operations (WI-50).

        Provides lightweight brainstorming entity before work items.
        Simple 6-state lifecycle: idea → research → design → accepted → converted OR rejected

        Methods:
            - CRUD: create_idea, get_idea, list_ideas, update_idea, delete_idea
            - Workflow: vote_on_idea, transition_idea, reject_idea
            - Conversion: convert_idea_to_work_item (creates work item with traceability)

        Example:
            >>> db = DatabaseService("path/to/db")
            >>> idea = Idea(project_id=1, title="Add OAuth2", tags=["security", "ux"])
            >>> created = db.ideas.create_idea(db, idea)
            >>> voted = db.ideas.vote_on_idea(db, idea_id=1, delta=+1)
            >>> converted_idea, work_item = db.ideas.convert_idea_to_work_item(db, idea_id=1)
        """
        if not hasattr(self, '_ideas'):
            from agentpm.core.database.methods import ideas as idea_methods
            self._ideas = idea_methods
        return self._ideas


# Custom Exceptions

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass


class ConnectionError(DatabaseError):
    """Database connection failed"""
    pass


class TransactionError(DatabaseError):
    """Transaction failed"""
    pass


class ValidationError(DatabaseError):
    """Data validation failed"""
    pass