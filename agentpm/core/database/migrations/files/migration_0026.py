"""
Migration 0026: Add originated_from_idea_id to work_items (if not exists)

Ensures work_items table has the originated_from_idea_id column for idea conversion tracking.
This column was added to the Pydantic model but may not exist in all databases.

Safe to run multiple times (checks if column exists before adding).
"""

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    """Add originated_from_idea_id column if it doesn't exist"""
    print("🔧 Migration 0026: Add originated_from_idea_id column")

    # Check if column already exists
    cursor = conn.execute("PRAGMA table_info(work_items)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'originated_from_idea_id' in columns:
        print("  ✅ Column already exists, skipping")
        return

    # Add column
    print("  📋 Adding originated_from_idea_id column...")
    conn.execute("""
        ALTER TABLE work_items
        ADD COLUMN originated_from_idea_id INTEGER
        REFERENCES ideas(id) ON DELETE SET NULL
    """)

    print("  ✅ Column added successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove originated_from_idea_id column"""
    print("🔧 Migration 0026 downgrade: Remove originated_from_idea_id")

    # SQLite doesn't support DROP COLUMN easily
    # Would need to recreate table to remove column
    raise NotImplementedError(
        "Downgrade not supported for migration 0026. "
        "SQLite does not support DROP COLUMN. "
        "Would require table recreation."
    )
