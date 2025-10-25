"""
Migration 0041: FTS5 Full-Text Search Index for Summaries Table

Creates FTS5 virtual table and triggers to enable high-performance full-text
search across all summaries (project, session, work item, task, idea summaries).

New Tables:
- summaries_fts: FTS5 virtual table for summary full-text search

Features:
- BM25 relevance scoring for summary search
- Search across summary_text and context_metadata
- Entity type and summary type filtering
- Automatic synchronization via triggers
- Unicode tokenization with diacritic normalization

Migration 0041
Dependencies: Migration 0040 (FTS5 search system)
"""

import sqlite3
import json
from typing import List, Tuple


def upgrade(conn: sqlite3.Connection) -> None:
    """Create FTS5 index for summaries table"""
    print("Migration 0041: Create FTS5 summaries index")

    # Check FTS5 availability
    if not _check_fts5_availability(conn):
        print("⚠️  FTS5 not available - skipping summaries FTS index creation")
        print("   Summary search will fall back to LIKE queries")
        return

    print("✅ FTS5 available - creating summaries search index")

    # Create FTS5 virtual table for summaries
    _create_summaries_fts_table(conn)

    # Create synchronization triggers
    _create_summaries_triggers(conn)

    # Populate with existing data
    _populate_summaries_index(conn)

    print("✅ Summaries FTS5 index created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove FTS5 summaries index"""
    print("Migration 0041: Remove FTS5 summaries index")

    # Drop triggers
    _drop_summaries_triggers(conn)

    # Drop FTS5 table
    _drop_summaries_fts_table(conn)

    print("✅ Summaries FTS5 index removed")


def _check_fts5_availability(conn: sqlite3.Connection) -> bool:
    """Check if FTS5 is available in this SQLite build"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT fts5(?)", ("test",))
        return True
    except sqlite3.OperationalError:
        return False


def _create_summaries_fts_table(conn: sqlite3.Connection) -> None:
    """Create FTS5 virtual table for summaries search

    FTS5 Schema:
    - summary_id: UNINDEXED (just a reference, not searchable)
    - entity_type: Searchable (project, session, work_item, task, idea)
    - entity_id: UNINDEXED (numeric ID, not useful for text search)
    - summary_type: Searchable (e.g., 'work_item_progress', 'task_completion')
    - summary_text: Searchable (main content for full-text search)
    - context_metadata: Searchable (JSON metadata as text)

    Tokenization:
    - unicode61: Unicode-aware tokenization
    - remove_diacritics 2: Normalize accented characters for better search
    """
    cursor = conn.cursor()

    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS summaries_fts")

    # Create FTS5 virtual table
    # Note: UNINDEXED columns are stored but not searchable (saves space/time)
    cursor.execute("""
        CREATE VIRTUAL TABLE summaries_fts USING fts5(
            summary_id UNINDEXED,
            entity_type,
            entity_id UNINDEXED,
            summary_type,
            summary_text,
            context_metadata,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    print("✅ Created summaries_fts FTS5 virtual table")


def _create_summaries_triggers(conn: sqlite3.Connection) -> None:
    """Create triggers for automatic FTS index synchronization

    Triggers ensure that FTS5 index stays in sync with summaries table:
    - INSERT: Add new summary to FTS index
    - UPDATE: Update FTS index when summary changes
    - DELETE: Remove from FTS index when summary deleted
    """
    cursor = conn.cursor()

    # Drop existing triggers (for idempotent migration)
    _drop_summaries_triggers(conn)

    # INSERT trigger - index new summaries
    cursor.execute("""
        CREATE TRIGGER summaries_fts_insert
        AFTER INSERT ON summaries
        BEGIN
            INSERT INTO summaries_fts(
                summary_id,
                entity_type,
                entity_id,
                summary_type,
                summary_text,
                context_metadata
            )
            VALUES (
                NEW.id,
                NEW.entity_type,
                NEW.entity_id,
                NEW.summary_type,
                NEW.summary_text,
                COALESCE(NEW.context_metadata, '')
            );
        END
    """)

    # UPDATE trigger - reindex updated summaries
    cursor.execute("""
        CREATE TRIGGER summaries_fts_update
        AFTER UPDATE ON summaries
        BEGIN
            UPDATE summaries_fts
            SET
                entity_type = NEW.entity_type,
                entity_id = NEW.entity_id,
                summary_type = NEW.summary_type,
                summary_text = NEW.summary_text,
                context_metadata = COALESCE(NEW.context_metadata, '')
            WHERE summary_id = NEW.id;
        END
    """)

    # DELETE trigger - remove from FTS index
    cursor.execute("""
        CREATE TRIGGER summaries_fts_delete
        AFTER DELETE ON summaries
        BEGIN
            DELETE FROM summaries_fts
            WHERE summary_id = OLD.id;
        END
    """)

    print("✅ Created summaries FTS synchronization triggers")


def _populate_summaries_index(conn: sqlite3.Connection) -> None:
    """Populate FTS5 index with existing summaries

    Indexes all existing summaries from the summaries table.
    Uses batch processing for performance with large datasets.
    """
    cursor = conn.cursor()

    print("📊 Populating summaries FTS index with existing data...")

    # Get total count for progress reporting
    cursor.execute("SELECT COUNT(*) FROM summaries")
    total_count = cursor.fetchone()[0]

    if total_count == 0:
        print("  ℹ️  No existing summaries to index")
        return

    # Populate FTS index with all existing summaries
    cursor.execute("""
        INSERT INTO summaries_fts(
            summary_id,
            entity_type,
            entity_id,
            summary_type,
            summary_text,
            context_metadata
        )
        SELECT
            id,
            entity_type,
            entity_id,
            summary_type,
            summary_text,
            COALESCE(context_metadata, '')
        FROM summaries
    """)

    indexed_count = cursor.rowcount
    print(f"  ✅ Indexed {indexed_count} summaries")

    # Verify counts match
    if indexed_count != total_count:
        print(f"  ⚠️  Warning: Indexed {indexed_count} but expected {total_count}")

    # Report breakdown by entity type
    cursor.execute("""
        SELECT entity_type, COUNT(*)
        FROM summaries
        GROUP BY entity_type
        ORDER BY COUNT(*) DESC
    """)

    print("  📊 Breakdown by entity type:")
    for entity_type, count in cursor.fetchall():
        print(f"     - {entity_type}: {count}")

    print(f"✅ Total indexed: {total_count} summaries")


def _drop_summaries_triggers(conn: sqlite3.Connection) -> None:
    """Drop all summaries FTS synchronization triggers"""
    cursor = conn.cursor()

    triggers_to_drop = [
        'summaries_fts_insert',
        'summaries_fts_update',
        'summaries_fts_delete'
    ]

    for trigger_name in triggers_to_drop:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")

    print("✅ Dropped summaries FTS triggers")


def _drop_summaries_fts_table(conn: sqlite3.Connection) -> None:
    """Drop summaries FTS5 virtual table"""
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS summaries_fts")

    print("✅ Dropped summaries_fts table")


# Migration metadata
MIGRATION_ID = "0041"
MIGRATION_NAME = "summaries_fts_index"
DEPENDENCIES = ["0040"]  # FTS5 search system
DESCRIPTION = "Create FTS5 full-text search index for summaries table with automatic synchronization"
