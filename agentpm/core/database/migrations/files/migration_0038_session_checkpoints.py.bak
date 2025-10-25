"""
Migration 0038: Session Checkpoints

Add session_checkpoints table for Claude Code checkpointing system.

Enables session state preservation and restoration.
"""

from typing import Any
import sqlite3


VERSION = "0038"
DESCRIPTION = "Add session_checkpoints table for state preservation"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Add session_checkpoints table.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Create session_checkpoints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_checkpoints (
            -- Primary key
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Session reference
            session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

            -- Checkpoint identification
            checkpoint_name TEXT NOT NULL CHECK(length(checkpoint_name) >= 1 AND length(checkpoint_name) <= 200),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            -- State snapshots (JSON blobs)
            work_items_snapshot TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(work_items_snapshot)),
            tasks_snapshot TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(tasks_snapshot)),
            context_snapshot TEXT NOT NULL DEFAULT '{}' CHECK(json_valid(context_snapshot)),

            -- Metadata
            session_notes TEXT DEFAULT '' CHECK(length(session_notes) <= 1000),
            created_by TEXT DEFAULT 'unknown' CHECK(length(created_by) <= 200),
            restore_count INTEGER DEFAULT 0 CHECK(restore_count >= 0),
            size_bytes INTEGER DEFAULT 0 CHECK(size_bytes >= 0),

            -- Audit
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for efficient queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_checkpoints_session
        ON session_checkpoints(session_id, created_at DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_checkpoints_name
        ON session_checkpoints(session_id, checkpoint_name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_checkpoints_created
        ON session_checkpoints(created_at DESC)
    """)

    # Create trigger to auto-update updated_at timestamp
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_checkpoints_timestamp
        AFTER UPDATE ON session_checkpoints
        BEGIN
            UPDATE session_checkpoints
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END
    """)

    conn.commit()


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Remove session_checkpoints table.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Drop trigger
    cursor.execute("DROP TRIGGER IF EXISTS update_checkpoints_timestamp")

    # Drop indexes
    cursor.execute("DROP INDEX IF EXISTS idx_checkpoints_created")
    cursor.execute("DROP INDEX IF EXISTS idx_checkpoints_name")
    cursor.execute("DROP INDEX IF EXISTS idx_checkpoints_session")

    # Drop table
    cursor.execute("DROP TABLE IF EXISTS session_checkpoints")

    conn.commit()


def verify(conn: sqlite3.Connection) -> bool:
    """
    Verify migration was applied correctly.

    Args:
        conn: SQLite database connection

    Returns:
        True if verification successful
    """
    cursor = conn.cursor()

    # Check table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='session_checkpoints'
    """)

    if not cursor.fetchone():
        return False

    # Check indexes exist
    expected_indexes = [
        'idx_checkpoints_session',
        'idx_checkpoints_name',
        'idx_checkpoints_created'
    ]

    for index_name in expected_indexes:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name=?
        """, (index_name,))

        if not cursor.fetchone():
            return False

    # Check trigger exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='trigger' AND name='update_checkpoints_timestamp'
    """)

    if not cursor.fetchone():
        return False

    return True
