"""
Migration 0049: Align Provider Files Schema for Multi-Provider Support

Aligns existing provider_files table with multi-provider requirements:
- Renames file_hash → content_hash
- Updates file_type CHECK constraint for multi-provider values
- Adds missing columns: generated_at, last_verified_at, modification_detected

Background:
- Migration 0047 created new schema but existing table has old structure
- Current schema: file_hash, file_type CHECK('rule', 'mode', 'hook', 'config', 'memory')
- Required schema: content_hash, file_type CHECK('agent', 'hook', 'settings', 'rules', 'config', 'other')
- Missing columns needed for integrity verification and drift detection

SQLite Limitation: Cannot rename columns or modify CHECK constraints directly.
Solution: Create new table with correct schema, migrate data, swap tables.

Part of WI-165: Provider System Migration
Task: Align provider_files schema with multi-provider requirements
"""

import sqlite3
from datetime import datetime

VERSION = "0049"
DESCRIPTION = "Align provider_files schema for multi-provider support"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply migration changes.

    Changes:
    1. Check current provider_files schema
    2. Create new provider_files_new table with correct schema
    3. Migrate data from old table (file_hash → content_hash, map file_type values)
    4. Drop old table and rename new table
    5. Recreate indexes
    6. Validate schema
    """
    print("🔧 Migration 0049: Align Provider Files Schema")
    cursor = conn.cursor()

    # 1. Check if provider_files exists and needs migration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_files'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("  ⚠️  provider_files table doesn't exist, skipping migration")
        return

    # Check current schema
    cursor.execute("PRAGMA table_info(provider_files)")
    current_columns = {row[1] for row in cursor.fetchall()}

    # Check if already migrated (has content_hash instead of file_hash)
    if 'content_hash' in current_columns and 'file_hash' not in current_columns:
        print("  ✅ provider_files table already has correct schema, skipping migration")
        return

    print("  📋 Current schema has 'file_hash', migrating to 'content_hash'...")

    # Count existing records
    cursor.execute("SELECT COUNT(*) FROM provider_files")
    record_count = cursor.fetchone()[0]
    print(f"  📊 Found {record_count} records to migrate")

    # 2. Create new table with correct schema
    print("  📋 Creating provider_files_new with updated schema...")
    cursor.execute("""
        CREATE TABLE provider_files_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            installation_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL CHECK(file_type IN ('agent', 'hook', 'settings', 'rules', 'config', 'other')),
            content_hash TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_verified_at TIMESTAMP,
            modification_detected INTEGER DEFAULT 0 CHECK(modification_detected IN (0, 1)),

            FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
            UNIQUE(installation_id, file_path)
        )
    """)
    print("  ✅ Created provider_files_new table")

    # 3. Migrate data with column and value transformations
    print("  📋 Migrating data from provider_files to provider_files_new...")

    # File type mapping: old values → new values
    file_type_mapping = {
        'rule': 'rules',      # rule → rules
        'mode': 'agent',      # mode → agent (closest match)
        'hook': 'hook',       # hook → hook (no change)
        'config': 'config',   # config → config (no change)
        'memory': 'other',    # memory → other (not in new schema)
    }

    # Get all existing records
    cursor.execute("""
        SELECT id, installation_id, file_path, file_hash, file_type, installed_at
        FROM provider_files
    """)
    records = cursor.fetchall()

    migrated_count = 0
    skipped_count = 0

    for record in records:
        old_id, installation_id, file_path, file_hash, old_file_type, installed_at = record

        # Map old file_type to new file_type
        new_file_type = file_type_mapping.get(old_file_type, 'other')

        # Insert into new table
        try:
            cursor.execute("""
                INSERT INTO provider_files_new (
                    id, installation_id, file_path, file_type, content_hash,
                    generated_at, last_verified_at, modification_detected
                )
                VALUES (?, ?, ?, ?, ?, ?, NULL, 0)
            """, (
                old_id,
                installation_id,
                file_path,
                new_file_type,
                file_hash,  # file_hash becomes content_hash
                installed_at  # installed_at becomes generated_at
            ))
            migrated_count += 1
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not migrate record {old_id}: {e}")
            skipped_count += 1

    print(f"  ✅ Migrated {migrated_count} records")
    if skipped_count > 0:
        print(f"  ⚠️  Skipped {skipped_count} records due to errors")

    # Show file type mapping summary
    print("  📊 File type mapping applied:")
    for old_type, new_type in file_type_mapping.items():
        cursor.execute(f"""
            SELECT COUNT(*) FROM provider_files_new
            WHERE file_type = ?
        """, (new_type,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"      '{old_type}' → '{new_type}': {count} records")

    # 4. Drop old table and rename new table
    print("  📋 Swapping tables...")

    # Drop indexes on old table first
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='provider_files'
        AND name LIKE 'idx_provider_files_%'
    """)
    old_indexes = [row[0] for row in cursor.fetchall()]

    for index_name in old_indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"      Dropped old index: {index_name}")
        except sqlite3.Error as e:
            print(f"      ⚠️  Could not drop index {index_name}: {e}")

    # Drop old table
    cursor.execute("DROP TABLE provider_files")
    print("  ✅ Dropped old provider_files table")

    # Rename new table
    cursor.execute("ALTER TABLE provider_files_new RENAME TO provider_files")
    print("  ✅ Renamed provider_files_new → provider_files")

    # 5. Recreate indexes
    print("  📋 Creating indexes on new table...")

    indexes = [
        ("idx_provider_files_installation", "installation_id"),
        ("idx_provider_files_hash", "content_hash"),
        ("idx_provider_files_type", "file_type"),
    ]

    for index_name, column_name in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX {index_name}
                ON provider_files({column_name})
            """)
            print(f"  ✅ Created index: {index_name}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not create index {index_name}: {e}")

    # 6. Validate schema
    print("  📋 Validating new schema...")

    cursor.execute("PRAGMA table_info(provider_files)")
    new_columns = {row[1] for row in cursor.fetchall()}

    expected_columns = {
        'id', 'installation_id', 'file_path', 'file_type', 'content_hash',
        'generated_at', 'last_verified_at', 'modification_detected'
    }

    if expected_columns.issubset(new_columns):
        print("  ✅ All expected columns present")
    else:
        missing = expected_columns - new_columns
        print(f"  ⚠️  WARNING: Missing columns: {missing}")

    # Verify no file_hash column remains
    if 'file_hash' not in new_columns:
        print("  ✅ Old 'file_hash' column removed")
    else:
        print("  ⚠️  WARNING: Old 'file_hash' column still exists!")

    # Verify record count matches
    cursor.execute("SELECT COUNT(*) FROM provider_files")
    final_count = cursor.fetchone()[0]

    if final_count == record_count:
        print(f"  ✅ Record count verified: {final_count} records")
    else:
        print(f"  ⚠️  WARNING: Record count mismatch! Before: {record_count}, After: {final_count}")

    conn.commit()
    print("  ✅ Migration 0049 completed successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration changes.

    Reverts provider_files table to old schema:
    - Renames content_hash → file_hash
    - Reverts file_type CHECK constraint
    - Removes new columns: generated_at, last_verified_at, modification_detected

    Warning: This will lose data in the new columns.
    """
    print("🔧 Migration 0049 downgrade: Revert Provider Files Schema")
    print("  ⚠️  WARNING: This will lose generated_at, last_verified_at, and modification_detected data")

    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_files'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("  ⚠️  provider_files table doesn't exist, nothing to downgrade")
        return

    # Check if we need to downgrade (has content_hash, not file_hash)
    cursor.execute("PRAGMA table_info(provider_files)")
    current_columns = {row[1] for row in cursor.fetchall()}

    if 'file_hash' in current_columns and 'content_hash' not in current_columns:
        print("  ✅ Table already has old schema, nothing to downgrade")
        return

    print("  📋 Reverting to old schema...")

    # Count records
    cursor.execute("SELECT COUNT(*) FROM provider_files")
    record_count = cursor.fetchone()[0]
    print(f"  📊 Found {record_count} records to migrate")

    # Create old schema table
    print("  📋 Creating provider_files_old with legacy schema...")
    cursor.execute("""
        CREATE TABLE provider_files_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            installation_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            file_type TEXT NOT NULL CHECK(file_type IN ('rule', 'mode', 'hook', 'config', 'memory')),
            installed_at TEXT NOT NULL,

            FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
            UNIQUE(installation_id, file_path)
        )
    """)
    print("  ✅ Created provider_files_old table")

    # Reverse file type mapping
    reverse_file_type_mapping = {
        'rules': 'rule',
        'agent': 'mode',
        'hook': 'hook',
        'config': 'config',
        'settings': 'config',  # settings → config (closest match)
        'other': 'memory',
    }

    # Migrate data back
    print("  📋 Migrating data back to old schema...")

    cursor.execute("""
        SELECT id, installation_id, file_path, content_hash, file_type, generated_at
        FROM provider_files
    """)
    records = cursor.fetchall()

    migrated_count = 0
    skipped_count = 0

    for record in records:
        old_id, installation_id, file_path, content_hash, new_file_type, generated_at = record

        # Map new file_type back to old file_type
        old_file_type = reverse_file_type_mapping.get(new_file_type, 'memory')

        # Use generated_at as installed_at, or current timestamp if NULL
        installed_at = generated_at if generated_at else datetime.utcnow().isoformat()

        try:
            cursor.execute("""
                INSERT INTO provider_files_old (
                    id, installation_id, file_path, file_hash, file_type, installed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                old_id,
                installation_id,
                file_path,
                content_hash,  # content_hash becomes file_hash
                old_file_type,
                installed_at
            ))
            migrated_count += 1
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not migrate record {old_id}: {e}")
            skipped_count += 1

    print(f"  ✅ Migrated {migrated_count} records back")
    if skipped_count > 0:
        print(f"  ⚠️  Skipped {skipped_count} records due to errors")

    # Drop indexes
    print("  📋 Dropping indexes on current table...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='provider_files'
        AND name LIKE 'idx_provider_files_%'
    """)
    indexes = [row[0] for row in cursor.fetchall()]

    for index_name in indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not drop index {index_name}: {e}")

    # Swap tables
    cursor.execute("DROP TABLE provider_files")
    print("  ✅ Dropped new provider_files table")

    cursor.execute("ALTER TABLE provider_files_old RENAME TO provider_files")
    print("  ✅ Renamed provider_files_old → provider_files")

    # Recreate old indexes
    print("  📋 Recreating legacy indexes...")
    cursor.execute("""
        CREATE INDEX idx_provider_files_installation
        ON provider_files(installation_id)
    """)
    cursor.execute("""
        CREATE INDEX idx_provider_files_hash
        ON provider_files(file_hash)
    """)
    print("  ✅ Recreated legacy indexes")

    # Validate
    cursor.execute("SELECT COUNT(*) FROM provider_files")
    final_count = cursor.fetchone()[0]

    if final_count == record_count:
        print(f"  ✅ Record count verified: {final_count} records")
    else:
        print(f"  ⚠️  WARNING: Record count mismatch! Before: {record_count}, After: {final_count}")

    conn.commit()
    print("  ✅ Migration 0049 downgrade completed")
