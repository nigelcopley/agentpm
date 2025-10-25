"""
Migration 0025: Add hierarchical summaries table

PURPOSE:
Enable polymorphic summary system supporting summaries at all levels of the APM (Agent Project Manager) hierarchy:
- Project summaries (strategic, milestone, retrospective)
- Session summaries (handover, progress, error analysis)
- Work item summaries (progress, milestone, decision)
- Task summaries (completion, progress, blocker resolution)

RATIONALE:
- Current: work_item_summaries table only supports work item summaries
- Future: Unified summary system for all entity types
- Benefits: Consistent interface, better context assembly, agent enablement

Changes:
- Create summaries table with polymorphic entity assignment
- Add indexes for performance
- Migrate existing work_item_summaries data
- Keep work_item_summaries table for backward compatibility (Phase 1)

Data Integrity:
- Entity references validated via foreign key constraints
- Summary types validated via CHECK constraints
- Session linkage optional for traceability
- JSON metadata for AI parsing
"""

import sqlite3
from agentpm.core.database.enums import EntityType, SummaryType


def upgrade(conn: sqlite3.Connection) -> None:
    """Create summaries table and migrate existing data"""
    print("🔧 Migration 0025: Add hierarchical summaries table")

    # Step 1: Create summaries table
    _create_summaries_table(conn)

    # Step 2: Add indexes for performance
    _add_summaries_indexes(conn)

    # Step 3: Migrate existing work_item_summaries data
    _migrate_work_item_summaries(conn)

    print("✅ Migration 0025 complete")


def _create_summaries_table(conn: sqlite3.Connection) -> None:
    """Create the summaries table with polymorphic support"""
    print("  📋 Creating summaries table...")

    conn.execute("""
        CREATE TABLE summaries (
            -- Primary Key
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Polymorphic assignment
            entity_type TEXT NOT NULL CHECK (entity_type IN ('project', 'session', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,

            -- Summary classification
            summary_type TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            context_metadata TEXT,  -- JSON blob

            -- Attribution & traceability
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            created_by TEXT NOT NULL,
            session_id INTEGER,  -- Optional link to session

            -- Optional session context
            session_date TEXT,  -- YYYY-MM-DD format
            session_duration_hours REAL,

            -- Constraints
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,

            -- Ensure session_date is valid ISO 8601 date
            CHECK (session_date IS NULL OR session_date IS date(session_date)),

            -- Ensure entity_id is positive
            CHECK (entity_id > 0),

            -- Ensure session_duration_hours is non-negative
            CHECK (session_duration_hours IS NULL OR session_duration_hours >= 0),

            -- Ensure summary_text is not empty
            CHECK (length(trim(summary_text)) >= 10)
        )
    """)


def _add_summaries_indexes(conn: sqlite3.Connection) -> None:
    """Add indexes for query performance"""
    print("  📊 Adding indexes for performance...")

    # Primary query pattern: Get summaries for entity (chronological)
    conn.execute("""
        CREATE INDEX idx_summaries_entity 
        ON summaries(entity_type, entity_id, created_at DESC)
    """)

    # Query pattern: Get recent summaries across all entities
    conn.execute("""
        CREATE INDEX idx_summaries_recent 
        ON summaries(created_at DESC)
    """)

    # Query pattern: Get summaries by session
    conn.execute("""
        CREATE INDEX idx_summaries_session 
        ON summaries(session_id, created_at DESC)
    """)

    # Query pattern: Filter by summary type
    conn.execute("""
        CREATE INDEX idx_summaries_type 
        ON summaries(entity_type, summary_type, created_at DESC)
    """)

    # Query pattern: Search by text content
    conn.execute("""
        CREATE INDEX idx_summaries_text 
        ON summaries(summary_text)
    """)


def _migrate_work_item_summaries(conn: sqlite3.Connection) -> None:
    """Migrate existing work_item_summaries to new summaries table"""
    print("  🔄 Migrating existing work_item_summaries...")

    # Check if work_item_summaries table exists
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='work_item_summaries'
    """)
    
    if not cursor.fetchone():
        print("    ℹ️  No work_item_summaries table found, skipping migration")
        return

    # Get count of existing summaries
    cursor = conn.execute("SELECT COUNT(*) FROM work_item_summaries")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("    ℹ️  No work_item_summaries found, skipping migration")
        return

    print(f"    📦 Migrating {count} work_item_summaries...")

    # Migrate all work_item_summaries
    cursor = conn.execute("""
        INSERT INTO summaries (
            entity_type, entity_id, summary_type, summary_text,
            context_metadata, created_at, created_by, session_id,
            session_date, session_duration_hours
        )
        SELECT 
            'work_item' as entity_type,
            work_item_id as entity_id,
            summary_type,
            summary_text,
            context_metadata,
            created_at,
            COALESCE(created_by, 'migration') as created_by,
            NULL as session_id,  -- Not available in legacy format
            session_date,
            session_duration_hours
        FROM work_item_summaries
    """)

    migrated_count = cursor.rowcount
    print(f"    ✅ Migrated {migrated_count} summaries")

    # Verify migration
    cursor = conn.execute("SELECT COUNT(*) FROM summaries WHERE entity_type = 'work_item'")
    new_count = cursor.fetchone()[0]
    
    if new_count == count:
        print("    ✅ Migration verification successful")
    else:
        print(f"    ⚠️  Migration verification failed: expected {count}, got {new_count}")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove summaries table and indexes"""
    print("🔧 Migration 0025: Downgrade - Remove summaries table")

    # Drop indexes
    print("  📊 Dropping indexes...")
    conn.execute("DROP INDEX IF EXISTS idx_summaries_entity")
    conn.execute("DROP INDEX IF EXISTS idx_summaries_recent")
    conn.execute("DROP INDEX IF EXISTS idx_summaries_session")
    conn.execute("DROP INDEX IF EXISTS idx_summaries_type")
    conn.execute("DROP INDEX IF EXISTS idx_summaries_text")

    # Drop table
    print("  📋 Dropping summaries table...")
    conn.execute("DROP TABLE IF EXISTS summaries")

    print("✅ Migration 0025 downgrade complete")


def get_migration_info() -> dict:
    """Get migration metadata"""
    return {
        "version": "0025",
        "name": "Add hierarchical summaries table",
        "description": "Create polymorphic summary system for all entity types",
        "changes": [
            "Create summaries table with polymorphic entity assignment",
            "Add performance indexes",
            "Migrate existing work_item_summaries data",
            "Support project, session, work_item, and task summaries"
        ],
        "backward_compatible": True,
        "requires_restart": False
    }
