"""
Migration 0039: Document Content Storage for Hybrid System

Adds content storage columns to document_references table to support
hybrid storage where database is source of truth and files are synchronized cache.

New Fields:
- content: Full document text content (source of truth)
- filename: Base filename for path construction
- storage_mode: Storage strategy (database_only, file_only, hybrid)
- content_updated_at: When content was last modified
- last_synced_at: When file was last synced from database
- sync_status: Synchronization state (synced, pending, conflict, error)

Full-Text Search:
- document_content_fts: FTS5 virtual table for fast content search
- Supports searching across content, title, and filename

Migration 0039
Dependencies: Migration 0031 (documentation system), Migration 0032 (docs path)
"""

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    """Add document content storage and sync tracking columns"""
    print("Migration 0039: Add document content storage columns")

    # Check if columns already exist (idempotent migration)
    cursor = conn.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = []

    # Content storage column
    if 'content' not in existing_columns:
        columns_to_add.append(
            ("content", "TEXT", "Full document content (source of truth)")
        )

    # Filename column (for path construction)
    if 'filename' not in existing_columns:
        columns_to_add.append(
            ("filename", "TEXT", "Base filename for path construction")
        )

    # Storage mode (database_only, file_only, hybrid)
    if 'storage_mode' not in existing_columns:
        columns_to_add.append(
            ("storage_mode", "TEXT DEFAULT 'hybrid'", "Storage strategy")
        )

    # Content update timestamp
    if 'content_updated_at' not in existing_columns:
        columns_to_add.append(
            ("content_updated_at", "DATETIME", "When content was last modified")
        )

    # Last sync timestamp
    if 'last_synced_at' not in existing_columns:
        columns_to_add.append(
            ("last_synced_at", "DATETIME", "When file was last synced from database")
        )

    # Sync status
    if 'sync_status' not in existing_columns:
        columns_to_add.append(
            ("sync_status", "TEXT DEFAULT 'synced'", "Synchronization state")
        )

    # Add columns
    if columns_to_add:
        print(f"  Adding {len(columns_to_add)} new columns...")
        for column_name, column_def, description in columns_to_add:
            conn.execute(f"""
                ALTER TABLE document_references
                ADD COLUMN {column_name} {column_def}
            """)
            print(f"  Created column: {column_name} ({description})")
    else:
        print("  All columns already exist, skipping column creation")

    # Create indexes for performance
    print("  Creating indexes...")

    # Check existing indexes
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references'"
    )
    existing_indexes = {row[0] for row in cursor.fetchall()}

    indexes_to_create = []

    # Index on content_hash for deduplication
    if 'idx_document_content_hash' not in existing_indexes:
        indexes_to_create.append(
            ("idx_document_content_hash", "content_hash", "Content deduplication")
        )

    # Index on filename for path construction
    if 'idx_document_filename' not in existing_indexes:
        indexes_to_create.append(
            ("idx_document_filename", "filename", "Filename lookup")
        )

    # Index on sync_status for finding documents needing sync
    if 'idx_document_sync_status' not in existing_indexes:
        indexes_to_create.append(
            ("idx_document_sync_status", "sync_status", "Sync queue lookup")
        )

    # Composite index on storage_mode + sync_status
    if 'idx_document_storage_sync' not in existing_indexes:
        indexes_to_create.append(
            ("idx_document_storage_sync", "storage_mode, sync_status", "Storage and sync filtering")
        )

    if indexes_to_create:
        for index_name, columns, description in indexes_to_create:
            conn.execute(f"""
                CREATE INDEX {index_name}
                ON document_references({columns})
            """)
            print(f"  Created index: {index_name} ({description})")
    else:
        print("  All indexes already exist, skipping index creation")

    # Create FTS5 virtual table for full-text search
    print("  Creating FTS5 virtual table...")

    # Check if FTS table already exists
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='document_content_fts'"
    )
    fts_exists = cursor.fetchone() is not None

    if not fts_exists:
        conn.execute('''
            CREATE VIRTUAL TABLE document_content_fts USING fts5(
                document_id UNINDEXED,
                filename,
                title,
                content,
                tokenize='unicode61 remove_diacritics 2'
            )
        ''')
        print("  Created FTS5 table: document_content_fts")
        print("    Indexed columns: filename, title, content")
        print("    Tokenizer: unicode61 with diacritic removal")
    else:
        print("  FTS5 table already exists, skipping creation")

    print("  Migration 0039 completed successfully")
    print(f"  Added {len(columns_to_add)} columns and {len(indexes_to_create)} indexes")
    print("  Hybrid storage: Database is source of truth, files are sync'd cache")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove document content storage columns and FTS table"""
    print("Migration 0039 downgrade: Remove document content storage")

    # Drop FTS table first
    print("  Dropping FTS5 virtual table...")
    try:
        conn.execute("DROP TABLE IF EXISTS document_content_fts")
        print("  Dropped table: document_content_fts")
    except sqlite3.Error as e:
        print(f"  Could not drop FTS table: {e}")

    # Drop indexes
    print("  Dropping indexes...")

    indexes_to_drop = [
        'idx_document_content_hash',
        'idx_document_filename',
        'idx_document_sync_status',
        'idx_document_storage_sync',
    ]

    for index_name in indexes_to_drop:
        try:
            conn.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"  Dropped index: {index_name}")
        except sqlite3.Error as e:
            print(f"  Could not drop index {index_name}: {e}")

    # SQLite doesn't support DROP COLUMN directly
    # Need to recreate table without new columns
    print("  Recreating table without content columns...")

    # Create backup table with original schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_references_backup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT,
            title TEXT,
            description TEXT,
            file_size_bytes INTEGER,
            content_hash TEXT,
            format TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            document_type_dir TEXT,
            segment_type TEXT,
            component TEXT,
            domain TEXT,
            audience TEXT,
            maturity TEXT,
            priority TEXT,
            tags TEXT,
            phase TEXT,
            work_item_id INTEGER,
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0),
            UNIQUE(entity_type, entity_id, file_path)
        )
    """)

    # Copy data (only original columns, excluding new content columns)
    conn.execute("""
        INSERT INTO document_references_backup (
            id, entity_type, entity_id, file_path, document_type,
            title, description, file_size_bytes, content_hash, format,
            created_by, created_at, updated_at,
            category, document_type_dir, segment_type, component, domain,
            audience, maturity, priority, tags, phase, work_item_id
        )
        SELECT
            id, entity_type, entity_id, file_path, document_type,
            title, description, file_size_bytes, content_hash, format,
            created_by, created_at, updated_at,
            category, document_type_dir, segment_type, component, domain,
            audience, maturity, priority, tags, phase, work_item_id
        FROM document_references
    """)

    # Drop old table
    conn.execute("DROP TABLE document_references")

    # Rename backup to original name
    conn.execute("ALTER TABLE document_references_backup RENAME TO document_references")

    print("  Table recreated without content columns")
    print("  Migration 0039 downgrade completed successfully")
