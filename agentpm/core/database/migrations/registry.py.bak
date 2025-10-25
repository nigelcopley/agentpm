"""
Migration Registry

Tracks applied migrations in schema_migrations table.
"""

import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime

from .models import Migration


class MigrationRegistry:
    """
    Manages migration version tracking in database.

    Responsibilities:
    - Query applied migrations
    - Record new migrations
    - Track rollbacks
    """

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialize registry.

        Args:
            conn: Database connection
        """
        self.conn = conn

    def get_applied_versions(self) -> List[str]:
        """
        Get list of applied migration versions.

        Returns:
            List of version strings (e.g., ['0001', '0002'])
        """
        cursor = self.conn.execute("""
            SELECT version
            FROM schema_migrations
            WHERE rollback_at IS NULL
            ORDER BY version
        """)

        return [row[0] for row in cursor.fetchall()]

    def get_migration_info(self, version: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Get applied/rollback info for a version.

        Args:
            version: Migration version

        Returns:
            (applied_at, rollback_at) or None if not applied
        """
        try:
            cursor = self.conn.execute("""
                SELECT applied_at, rollback_at
                FROM schema_migrations
                WHERE version = ?
            """, (version,))

            row = cursor.fetchone()
            return (row[0], row[1]) if row else None
        except sqlite3.OperationalError as e:
            if "no such table: schema_migrations" in str(e):
                # Table doesn't exist yet - no migrations have been applied
                return None
            raise

    def record_migration(
        self,
        version: str,
        description: str,
        applied_by: Optional[str] = None
    ) -> None:
        """
        Record a migration as applied.

        Args:
            version: Migration version
            description: Migration description
            applied_by: Who applied the migration (optional)
        """
        self.conn.execute("""
            INSERT OR IGNORE INTO schema_migrations
            (version, description, applied_at, applied_by)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
        """, (version, description, applied_by))

    def record_rollback(
        self,
        version: str,
        reason: str = ""
    ) -> None:
        """
        Record a migration rollback.

        Args:
            version: Migration version to rollback
            reason: Rollback reason
        """
        self.conn.execute("""
            UPDATE schema_migrations
            SET rollback_at = CURRENT_TIMESTAMP,
                rollback_reason = ?
            WHERE version = ?
        """, (reason, version))

    def is_applied(self, version: str) -> bool:
        """
        Check if migration is applied (and not rolled back).

        Args:
            version: Migration version

        Returns:
            True if applied and not rolled back
        """
        cursor = self.conn.execute("""
            SELECT 1
            FROM schema_migrations
            WHERE version = ?
            AND rollback_at IS NULL
        """, (version,))

        return cursor.fetchone() is not None
