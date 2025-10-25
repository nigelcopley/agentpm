"""Session adapter for Pydantic ↔ SQLite conversion.

This module provides type-safe conversion between Session Pydantic models
and SQLite database rows. Part of the three-layer pattern:
- Layer 1: Pydantic models (validation)
- Layer 2: Adapters (conversion) ← THIS FILE
- Layer 3: Methods (CRUD operations)
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path

from agentpm.core.database.models.session import (
    Session,
    SessionMetadata,
    SessionTool,
    LLMModel,
    SessionType,
    SessionStatus
)


class SessionAdapter:
    """Convert between Session Pydantic models and SQLite rows.

    This adapter handles all type conversions:
    - Enums → strings (to_db)
    - datetime → ISO strings (to_db)
    - SessionMetadata → JSON (to_db)
    - Reverse conversions (from_db)
    - CRUD operations (CLI entry points)
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(db, session: Session) -> Session:
        """
        Create a new session (CLI entry point).

        Args:
            db: DatabaseService instance
            session: Validated Session Pydantic model

        Returns:
            Created Session with database ID

        Example:
            >>> from agentpm.core.database.adapters import SessionAdapter
            >>> session = Session(session_id="test", project_id=1, ...)
            >>> created = SessionAdapter.create(db, session)
        """
        from ..methods import sessions as session_methods
        return session_methods.create_session(db, session)

    @staticmethod
    def get(db, session_id: str) -> Optional[Session]:
        """
        Get session by ID (CLI entry point).

        Args:
            db: DatabaseService instance
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        from ..methods import sessions as session_methods
        return session_methods.get_session(db, session_id)

    @staticmethod
    def get_current(db) -> Optional[Session]:
        """
        Get current active session (CLI entry point).

        Args:
            db: DatabaseService instance

        Returns:
            Current Session if found, None otherwise
        """
        from ..methods import sessions as session_methods
        return session_methods.get_current_session(db)

    @staticmethod
    def get_current_id(db) -> Optional[str]:
        """
        Get current session ID (CLI entry point).

        Args:
            db: DatabaseService instance

        Returns:
            Current session ID if found, None otherwise
        """
        from ..methods import sessions as session_methods
        return session_methods.get_current_session_id(db)

    @staticmethod
    def set_current(db, session_id: str) -> None:
        """
        Set current session ID (CLI entry point).

        Args:
            db: DatabaseService instance
            session_id: Session ID to set as current
        """
        from ..methods import sessions as session_methods
        return session_methods.set_current_session(db, session_id)

    @staticmethod
    def clear_current(db) -> None:
        """
        Clear current session (CLI entry point).

        Args:
            db: DatabaseService instance
        """
        from ..methods import sessions as session_methods
        return session_methods.clear_current_session(db)

    @staticmethod
    def list(db, project_id: Optional[int] = None, status: Optional[str] = None) -> List[Session]:
        """
        List sessions with optional filters (CLI entry point).

        Args:
            db: DatabaseService instance
            project_id: Optional project ID to filter by
            status: Optional status to filter by

        Returns:
            List of Session models
        """
        from ..methods import sessions as session_methods
        return session_methods.list_sessions(db, project_id=project_id, status=status)

    @staticmethod
    def get_active_sessions(db, project_id: int) -> List[Session]:
        """
        Get active sessions for a project (CLI entry point).

        Args:
            db: DatabaseService instance
            project_id: Project ID

        Returns:
            List of active Session models
        """
        from ..methods import sessions as session_methods
        return session_methods.get_active_sessions(db, project_id)

    @staticmethod
    def update(db, session: Session) -> Session:
        """
        Update session (CLI entry point).

        Args:
            db: DatabaseService instance
            session: Updated Session model

        Returns:
            Updated Session
        """
        from ..methods import sessions as session_methods
        return session_methods.update_session(db, session)

    @staticmethod
    def update_current(db, **updates) -> Optional[Session]:
        """
        Update current session (CLI entry point).

        Args:
            db: DatabaseService instance
            **updates: Field updates

        Returns:
            Updated Session or None if no current session
        """
        from ..methods import sessions as session_methods
        return session_methods.update_current_session(db, **updates)

    @staticmethod
    def end(db, session_id: str, exit_reason: Optional[str] = None, summary: Optional[str] = None) -> Session:
        """
        End a session (CLI entry point).

        Args:
            db: DatabaseService instance
            session_id: Session ID to end
            exit_reason: Optional exit reason
            summary: Optional session summary

        Returns:
            Ended Session
        """
        from ..methods import sessions as session_methods
        return session_methods.end_session(db, session_id, exit_reason=exit_reason, summary=summary)

    @staticmethod
    def delete(db, session_id: str) -> bool:
        """
        Delete session (CLI entry point).

        Args:
            db: DatabaseService instance
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import sessions as session_methods
        return session_methods.delete_session(db, session_id)

    @staticmethod
    def get_by_date_range(db, start_date: str, end_date: str, project_id: Optional[int] = None) -> List[Session]:
        """
        Get sessions by date range (CLI entry point).

        Args:
            db: DatabaseService instance
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            project_id: Optional project ID filter

        Returns:
            List of Session models
        """
        from ..methods import sessions as session_methods
        return session_methods.get_sessions_by_date_range(db, start_date, end_date, project_id=project_id)

    @staticmethod
    def get_by_work_item(db, work_item_id: int) -> List[Session]:
        """
        Get sessions by work item (CLI entry point).

        Args:
            db: DatabaseService instance
            work_item_id: Work item ID

        Returns:
            List of Session models
        """
        from ..methods import sessions as session_methods
        return session_methods.get_sessions_by_work_item(db, work_item_id)

    @staticmethod
    def get_by_developer(db, developer_name: str, project_id: Optional[int] = None) -> List[Session]:
        """
        Get sessions by developer (CLI entry point).

        Args:
            db: DatabaseService instance
            developer_name: Developer name
            project_id: Optional project ID filter

        Returns:
            List of Session models
        """
        from ..methods import sessions as session_methods
        return session_methods.get_sessions_by_developer(db, developer_name, project_id=project_id)

    @staticmethod
    def search_decisions(db, query: str, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search decisions in sessions (CLI entry point).

        Args:
            db: DatabaseService instance
            query: Search query
            project_id: Optional project ID filter

        Returns:
            List of decision dictionaries
        """
        from ..methods import sessions as session_methods
        return session_methods.search_decisions(db, query, project_id=project_id)

    @staticmethod
    def get_stats(db, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get session statistics (CLI entry point).

        Args:
            db: DatabaseService instance
            project_id: Optional project ID filter

        Returns:
            Dictionary of statistics
        """
        from ..methods import sessions as session_methods
        return session_methods.get_session_stats(db, project_id=project_id)

    @staticmethod
    def validate_completeness(session: Session) -> tuple[bool, List[str]]:
        """
        Validate session completeness (CLI entry point).

        Args:
            session: Session to validate

        Returns:
            Tuple of (is_complete, list of missing fields)
        """
        from ..methods import sessions as session_methods
        return session_methods.validate_session_completeness(session)

    # ============================================================================
    # CONVERSION METHODS
    # ============================================================================

    @staticmethod
    def to_db(session: Session) -> Dict[str, Any]:
        """Convert Session model to SQLite dict.

        Args:
            session: Session Pydantic model

        Returns:
            Dictionary ready for SQLite INSERT/UPDATE

        Example:
            >>> session = Session(session_id="test", project_id=1, ...)
            >>> data = SessionAdapter.to_db(session)
            >>> cursor.execute("INSERT INTO sessions ...", data)
        """
        return {
            'id': session.id,
            'session_id': session.session_id,
            'project_id': session.project_id,
            'tool_name': session.tool_name.value,
            'llm_model': session.llm_model.value if session.llm_model else None,
            'tool_version': session.tool_version,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'duration_minutes': session.duration_minutes,
            'status': session.status.value,  # 🔥 NEW: Session status
            'session_type': session.session_type.value,
            'exit_reason': session.exit_reason,
            'developer_name': session.developer_name,
            'developer_email': session.developer_email,
            'metadata': json.dumps(session.metadata.model_dump()),
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Session:
        """Convert SQLite row to Session model.

        Args:
            row: SQLite row as dict (use sqlite3.Row or row_factory)

        Returns:
            Session Pydantic model with all validations applied

        Example:
            >>> cursor.execute("SELECT * FROM sessions WHERE id = ?", (1,))
            >>> row = cursor.fetchone()
            >>> session = SessionAdapter.from_db(row)
        """
        # Parse metadata JSON → SessionMetadata Pydantic model
        metadata_dict = json.loads(row['metadata']) if row.get('metadata') else {}
        metadata = SessionMetadata(**metadata_dict)

        return Session(
            id=row['id'],
            session_id=row['session_id'],
            project_id=row['project_id'],
            status=SessionStatus(row.get('status', 'active')),  # 🔥 NEW: Default to active for old records
            session_type=SessionType(row['session_type']),
            tool=SessionTool(row['tool_name']),
            llm_model=LLMModel(row['llm_model']) if row.get('llm_model') else None,
            metadata=metadata,
            started_at=row.get('start_time'),  # Keep as string to match model
            ended_at=row.get('end_time'),      # Keep as string to match model
            created_at=row.get('created_at'),  # Keep as string to match model
            
            # Additional fields for compatibility
            tool_name=SessionTool(row['tool_name']),
            tool_version=row.get('tool_version'),
            duration_minutes=row.get('duration_minutes'),
            exit_reason=row.get('exit_reason'),
            developer_name=row.get('developer_name'),
            developer_email=row.get('developer_email'),
            updated_at=row.get('updated_at'),
        )

    @staticmethod
    def to_db_partial(updates: Dict[str, Any]) -> Dict[str, Any]:
        """Convert partial updates to SQLite-compatible format.

        Useful for UPDATE operations where only some fields change.
        Handles enum and datetime conversions automatically.

        Args:
            updates: Dict of field names to new values

        Returns:
            Dict with converted values ready for SQLite

        Example:
            >>> updates = {'end_time': datetime.now(), 'duration_minutes': 120}
            >>> db_updates = SessionAdapter.to_db_partial(updates)
            >>> cursor.execute("UPDATE sessions SET ... WHERE ...", db_updates)
        """
        result = {}

        for key, value in updates.items():
            if value is None:
                result[key] = None
            elif key == 'tool_name' and isinstance(value, SessionTool):
                result[key] = value.value
            elif key == 'llm_model' and isinstance(value, LLMModel):
                result[key] = value.value
            elif key == 'session_type' and isinstance(value, SessionType):
                result[key] = value.value
            elif key == 'status' and isinstance(value, SessionStatus):
                result[key] = value.value
            elif key in ('start_time', 'end_time', 'created_at', 'updated_at') and isinstance(value, datetime):
                result[key] = value.isoformat()
            elif key == 'metadata' and isinstance(value, SessionMetadata):
                result[key] = json.dumps(value.model_dump())
            else:
                result[key] = value

        return result
