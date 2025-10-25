"""
Migration 0039: Hybrid Document Storage

Add content storage and sync tracking to document_references table.

Enables database-first document storage with bidirectional file synchronization.
Adds full-text search capability via FTS5 virtual table.

Changes:
- Add content column for full document storage
- Add filename column for efficient indexing
- Add storage_mode column (hybrid, database_only, file_only)
- Add sync tracking columns (content_updated_at, last_synced_at, sync_status)
- Add content_size_bytes for monitoring
- Create FTS5 virtual table for full-text search
- Create performance indexes
- Create auto-update triggers

Related: WI-133, Task #710
"""

from typing import Any
import sqlite3


VERSION = "0039"
DESCRIPTION = "Add hybrid document storage with content and sync tracking"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Add hybrid document storage capabilities.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # ========================================================================
    # 1. Add new columns to document_references table
    # ========================================================================

    # Content storage (authoritative source)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN content TEXT DEFAULT NULL
    """)

    # Filename extraction (for efficient indexing)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN filename TEXT DEFAULT NULL
    """)

    # Storage mode (hybrid, database_only, file_only)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN storage_mode TEXT DEFAULT 'file_only'
        CHECK(storage_mode IN ('hybrid', 'database_only', 'file_only'))
    """)

    # Content timestamp (separate from entity updated_at)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN content_updated_at TEXT DEFAULT NULL
    """)

    # Sync timestamp (last successful sync)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN last_synced_at TEXT DEFAULT NULL
    """)

    # Sync status (state machine)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN sync_status TEXT DEFAULT 'synced'
        CHECK(sync_status IN (
            'synced',
            'db_newer',
            'file_newer',
            'conflict',
            'missing_file',
            'missing_db'
        ))
    """)

    # Content size (for monitoring)
    cursor.execute("""
        ALTER TABLE document_references
        ADD COLUMN content_size_bytes INTEGER DEFAULT NULL
    """)

    # ========================================================================
    # 2. Create performance indexes
    # ========================================================================

    # Hash lookup (find by content hash)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_content_hash
        ON document_references(content_hash)
    """)

    # Filename lookup (common queries)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_filename
        ON document_references(filename)
    """)

    # Sync status (find out-of-sync documents)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_sync_status
        ON document_references(sync_status)
        WHERE sync_status != 'synced'
    """)

    # Storage mode (query by mode)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_storage_mode
        ON document_references(storage_mode)
    """)

    # Content size (monitor database growth)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_content_size
        ON document_references(content_size_bytes)
        WHERE content_size_bytes IS NOT NULL
    """)

    # Composite index for sync operations
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_document_sync_composite
        ON document_references(storage_mode, sync_status, last_synced_at)
    """)

    # ========================================================================
    # 3. Create FTS5 virtual table for full-text search
    # ========================================================================

    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS document_content_fts
        USING fts5(
            document_id UNINDEXED,
            filename,
            title,
            content,
            category UNINDEXED,
            document_type UNINDEXED,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    # ========================================================================
    # 4. Create triggers for FTS index auto-sync
    # ========================================================================

    # Trigger: Insert into FTS on document insert
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_fts_insert
        AFTER INSERT ON document_references
        WHEN NEW.content IS NOT NULL AND NEW.storage_mode != 'file_only'
        BEGIN
            INSERT INTO document_content_fts(
                document_id,
                filename,
                title,
                content,
                category,
                document_type
            )
            VALUES (
                NEW.id,
                NEW.filename,
                NEW.title,
                NEW.content,
                NEW.category,
                NEW.document_type
            );
        END
    """)

    # Trigger: Update FTS on document update
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_fts_update
        AFTER UPDATE ON document_references
        WHEN NEW.content IS NOT NULL AND NEW.storage_mode != 'file_only'
        BEGIN
            -- Delete old entry
            DELETE FROM document_content_fts WHERE document_id = OLD.id;

            -- Insert updated entry
            INSERT INTO document_content_fts(
                document_id,
                filename,
                title,
                content,
                category,
                document_type
            )
            VALUES (
                NEW.id,
                NEW.filename,
                NEW.title,
                NEW.content,
                NEW.category,
                NEW.document_type
            );
        END
    """)

    # Trigger: Delete from FTS on document delete
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_fts_delete
        AFTER DELETE ON document_references
        BEGIN
            DELETE FROM document_content_fts WHERE document_id = OLD.id;
        END
    """)

    # ========================================================================
    # 5. Create triggers for auto-extract filename
    # ========================================================================

    # Trigger: Extract filename on insert
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_extract_filename_insert
        AFTER INSERT ON document_references
        WHEN NEW.filename IS NULL AND NEW.file_path IS NOT NULL
        BEGIN
            UPDATE document_references
            SET filename = (
                SELECT CASE
                    WHEN instr(NEW.file_path, '/') > 0 THEN
                        substr(
                            NEW.file_path,
                            -- Find last slash position
                            length(NEW.file_path) - instr(reverse(NEW.file_path), '/') + 2
                        )
                    ELSE
                        NEW.file_path
                END
            )
            WHERE id = NEW.id;
        END
    """)

    # Trigger: Extract filename on update
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_extract_filename_update
        AFTER UPDATE OF file_path ON document_references
        WHEN NEW.filename IS NULL AND NEW.file_path IS NOT NULL
        BEGIN
            UPDATE document_references
            SET filename = (
                SELECT CASE
                    WHEN instr(NEW.file_path, '/') > 0 THEN
                        substr(
                            NEW.file_path,
                            length(NEW.file_path) - instr(reverse(NEW.file_path), '/') + 2
                        )
                    ELSE
                        NEW.file_path
                END
            )
            WHERE id = NEW.id;
        END
    """)

    # ========================================================================
    # 6. Create triggers for auto-calculate content_size_bytes
    # ========================================================================

    # Trigger: Calculate size on insert
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_calc_content_size_insert
        AFTER INSERT ON document_references
        WHEN NEW.content IS NOT NULL
        BEGIN
            UPDATE document_references
            SET content_size_bytes = length(NEW.content)
            WHERE id = NEW.id;
        END
    """)

    # Trigger: Calculate size on update
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS document_calc_content_size_update
        AFTER UPDATE OF content ON document_references
        WHEN NEW.content IS NOT NULL
        BEGIN
            UPDATE document_references
            SET content_size_bytes = length(NEW.content)
            WHERE id = NEW.id;
        END
    """)

    conn.commit()


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Remove hybrid document storage capabilities.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # ========================================================================
    # Drop triggers (must drop before dropping tables)
    # ========================================================================

    cursor.execute("DROP TRIGGER IF EXISTS document_calc_content_size_update")
    cursor.execute("DROP TRIGGER IF EXISTS document_calc_content_size_insert")
    cursor.execute("DROP TRIGGER IF EXISTS document_extract_filename_update")
    cursor.execute("DROP TRIGGER IF EXISTS document_extract_filename_insert")
    cursor.execute("DROP TRIGGER IF EXISTS document_fts_delete")
    cursor.execute("DROP TRIGGER IF EXISTS document_fts_update")
    cursor.execute("DROP TRIGGER IF EXISTS document_fts_insert")

    # ========================================================================
    # Drop FTS virtual table
    # ========================================================================

    cursor.execute("DROP TABLE IF EXISTS document_content_fts")

    # ========================================================================
    # Drop indexes
    # ========================================================================

    cursor.execute("DROP INDEX IF EXISTS idx_document_sync_composite")
    cursor.execute("DROP INDEX IF EXISTS idx_document_content_size")
    cursor.execute("DROP INDEX IF EXISTS idx_document_storage_mode")
    cursor.execute("DROP INDEX IF EXISTS idx_document_sync_status")
    cursor.execute("DROP INDEX IF EXISTS idx_document_filename")
    cursor.execute("DROP INDEX IF EXISTS idx_document_content_hash")

    # ========================================================================
    # Remove columns (SQLite doesn't support DROP COLUMN directly)
    # ========================================================================

    # SQLite limitation: Cannot drop columns in ALTER TABLE
    # Must recreate table without the columns

    # 1. Create backup table with original schema
    cursor.execute("""
        CREATE TABLE document_references_backup AS
        SELECT
            id,
            entity_type,
            entity_id,
            file_path,
            document_type,
            title,
            description,
            file_size_bytes,
            content_hash,
            format,
            created_by,
            created_at,
            updated_at,
            category,
            document_type_dir,
            segment_type,
            component,
            domain,
            audience,
            maturity,
            priority,
            tags,
            phase,
            work_item_id
        FROM document_references
    """)

    # 2. Drop original table
    cursor.execute("DROP TABLE document_references")

    # 3. Rename backup to original
    cursor.execute("ALTER TABLE document_references_backup RENAME TO document_references")

    # 4. Recreate original indexes (from migration_0031/0032)
    cursor.execute("""
        CREATE INDEX idx_doc_category
        ON document_references(category)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_type_dir
        ON document_references(document_type_dir)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_cat_type
        ON document_references(category, document_type_dir)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_component
        ON document_references(component)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_domain
        ON document_references(domain)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_work_item
        ON document_references(work_item_id)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_audience
        ON document_references(audience)
    """)

    cursor.execute("""
        CREATE INDEX idx_doc_maturity
        ON document_references(maturity)
    """)

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

    # ========================================================================
    # Check columns exist
    # ========================================================================

    cursor.execute("PRAGMA table_info(document_references)")
    columns = {row[1] for row in cursor.fetchall()}

    required_columns = {
        'content',
        'filename',
        'storage_mode',
        'content_updated_at',
        'last_synced_at',
        'sync_status',
        'content_size_bytes'
    }

    if not required_columns.issubset(columns):
        missing = required_columns - columns
        print(f"Missing columns: {missing}")
        return False

    # ========================================================================
    # Check FTS table exists
    # ========================================================================

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='document_content_fts'
    """)

    if not cursor.fetchone():
        print("FTS table not found")
        return False

    # ========================================================================
    # Check indexes exist
    # ========================================================================

    expected_indexes = [
        'idx_document_content_hash',
        'idx_document_filename',
        'idx_document_sync_status',
        'idx_document_storage_mode',
        'idx_document_content_size',
        'idx_document_sync_composite'
    ]

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='document_references'
    """)

    existing_indexes = {row[0] for row in cursor.fetchall()}

    for index_name in expected_indexes:
        if index_name not in existing_indexes:
            print(f"Missing index: {index_name}")
            return False

    # ========================================================================
    # Check triggers exist
    # ========================================================================

    expected_triggers = [
        'document_fts_insert',
        'document_fts_update',
        'document_fts_delete',
        'document_extract_filename_insert',
        'document_extract_filename_update',
        'document_calc_content_size_insert',
        'document_calc_content_size_update'
    ]

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='trigger'
    """)

    existing_triggers = {row[0] for row in cursor.fetchall()}

    for trigger_name in expected_triggers:
        if trigger_name not in existing_triggers:
            print(f"Missing trigger: {trigger_name}")
            return False

    # ========================================================================
    # Verify default values
    # ========================================================================

    # Check storage_mode defaults to 'file_only' for existing records
    cursor.execute("""
        SELECT COUNT(*) FROM document_references
        WHERE storage_mode IS NULL
    """)

    if cursor.fetchone()[0] > 0:
        print("Found documents with NULL storage_mode")
        return False

    # ========================================================================
    # All checks passed
    # ========================================================================

    return True
