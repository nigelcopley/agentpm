"""
Tests for migration 0049 - Align Provider Files Schema

Tests the migration that aligns existing provider_files table with
multi-provider requirements:
- Renames file_hash → content_hash
- Updates file_type CHECK constraint
- Adds missing columns: generated_at, last_verified_at, modification_detected
"""

import sqlite3
import pytest
from datetime import datetime
from agentpm.core.database.migrations.files import migration_0049_align_provider_files_schema as migration


@pytest.fixture
def test_db_with_old_schema(tmp_path):
    """Create a test database with OLD provider_files schema."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)

    # Create provider_installations table (required for foreign key)
    conn.execute("""
        CREATE TABLE provider_installations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            provider_name TEXT NOT NULL,
            version TEXT NOT NULL,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create OLD provider_files schema (as it exists before migration)
    conn.execute("""
        CREATE TABLE provider_files (
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

    # Insert test data with OLD schema values
    conn.execute("""
        INSERT INTO provider_installations (id, project_id, provider_name, version)
        VALUES (1, 1, 'cursor', '1.0.0')
    """)

    test_records = [
        (1, 1, '.cursorrules', 'abc123hash', 'rule', '2025-10-27T10:00:00'),
        (2, 1, '.cursorrules/modes/code-review.md', 'def456hash', 'mode', '2025-10-27T10:00:00'),
        (3, 1, '.cursor/hooks/pre-commit.py', 'ghi789hash', 'hook', '2025-10-27T10:00:00'),
        (4, 1, '.cursor/config.json', 'jkl012hash', 'config', '2025-10-27T10:00:00'),
        (5, 1, '.cursor/memory/context.json', 'mno345hash', 'memory', '2025-10-27T10:00:00'),
    ]

    for record in test_records:
        conn.execute("""
            INSERT INTO provider_files (id, installation_id, file_path, file_hash, file_type, installed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, record)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def test_db_already_migrated(tmp_path):
    """Create a test database with NEW provider_files schema (already migrated)."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)

    # Create provider_installations table
    conn.execute("""
        CREATE TABLE provider_installations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            provider_name TEXT NOT NULL,
            version TEXT NOT NULL,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create NEW provider_files schema (already migrated)
    conn.execute("""
        CREATE TABLE provider_files (
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

    conn.commit()
    yield conn
    conn.close()


def test_upgrade_renames_file_hash_to_content_hash(test_db_with_old_schema):
    """Test that file_hash column is renamed to content_hash."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Verify schema
    cursor = test_db_with_old_schema.execute("PRAGMA table_info(provider_files)")
    columns = {row[1] for row in cursor.fetchall()}

    assert 'content_hash' in columns, "content_hash column should exist"
    assert 'file_hash' not in columns, "file_hash column should be removed"


def test_upgrade_adds_new_columns(test_db_with_old_schema):
    """Test that new columns are added."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Verify new columns exist
    cursor = test_db_with_old_schema.execute("PRAGMA table_info(provider_files)")
    columns = {row[1] for row in cursor.fetchall()}

    assert 'generated_at' in columns, "generated_at column should be added"
    assert 'last_verified_at' in columns, "last_verified_at column should be added"
    assert 'modification_detected' in columns, "modification_detected column should be added"


def test_upgrade_updates_file_type_check_constraint(test_db_with_old_schema):
    """Test that file_type CHECK constraint is updated with new values."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Try inserting with new valid file_type values
    test_db_with_old_schema.execute("""
        INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
        VALUES (1, 'test/agent.md', 'agent', 'testhash123', '2025-10-27T12:00:00')
    """)

    test_db_with_old_schema.execute("""
        INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
        VALUES (1, 'test/settings.json', 'settings', 'testhash456', '2025-10-27T12:00:00')
    """)

    test_db_with_old_schema.execute("""
        INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
        VALUES (1, 'test/rules.md', 'rules', 'testhash789', '2025-10-27T12:00:00')
    """)

    test_db_with_old_schema.commit()

    # Verify inserts succeeded
    cursor = test_db_with_old_schema.execute("SELECT file_type FROM provider_files WHERE file_path LIKE 'test/%'")
    new_types = {row[0] for row in cursor.fetchall()}

    assert 'agent' in new_types
    assert 'settings' in new_types
    assert 'rules' in new_types

    # Try inserting with old invalid file_type values (should fail)
    with pytest.raises(sqlite3.IntegrityError):
        test_db_with_old_schema.execute("""
            INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
            VALUES (1, 'test/invalid.md', 'mode', 'testhash999', '2025-10-27T12:00:00')
        """)


def test_upgrade_migrates_file_type_values(test_db_with_old_schema):
    """Test that old file_type values are mapped to new values."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Verify file type mapping
    cursor = test_db_with_old_schema.execute("""
        SELECT file_path, file_type FROM provider_files ORDER BY id
    """)
    results = cursor.fetchall()

    # Mapping: rule → rules, mode → agent, hook → hook, config → config, memory → other
    expected_mappings = {
        '.cursorrules': 'rules',  # rule → rules
        '.cursorrules/modes/code-review.md': 'agent',  # mode → agent
        '.cursor/hooks/pre-commit.py': 'hook',  # hook → hook
        '.cursor/config.json': 'config',  # config → config
        '.cursor/memory/context.json': 'other',  # memory → other
    }

    for file_path, file_type in results:
        assert file_path in expected_mappings, f"Unexpected file_path: {file_path}"
        assert file_type == expected_mappings[file_path], \
            f"File type mismatch for {file_path}: expected {expected_mappings[file_path]}, got {file_type}"


def test_upgrade_preserves_data(test_db_with_old_schema):
    """Test that all data is preserved during migration."""
    # Count records before migration
    cursor = test_db_with_old_schema.execute("SELECT COUNT(*) FROM provider_files")
    count_before = cursor.fetchone()[0]

    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Count records after migration
    cursor = test_db_with_old_schema.execute("SELECT COUNT(*) FROM provider_files")
    count_after = cursor.fetchone()[0]

    assert count_after == count_before, f"Record count mismatch: before={count_before}, after={count_after}"

    # Verify specific records preserved
    cursor = test_db_with_old_schema.execute("""
        SELECT id, installation_id, file_path, content_hash
        FROM provider_files
        WHERE id = 1
    """)
    record = cursor.fetchone()

    assert record is not None, "Record with id=1 should exist"
    assert record[0] == 1, "ID should be preserved"
    assert record[1] == 1, "installation_id should be preserved"
    assert record[2] == '.cursorrules', "file_path should be preserved"
    assert record[3] == 'abc123hash', "content_hash (formerly file_hash) should be preserved"


def test_upgrade_sets_default_values(test_db_with_old_schema):
    """Test that new columns have appropriate default values."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Check default values
    cursor = test_db_with_old_schema.execute("""
        SELECT modification_detected, last_verified_at, generated_at
        FROM provider_files
        WHERE id = 1
    """)
    record = cursor.fetchone()

    assert record is not None
    assert record[0] == 0, "modification_detected should default to 0 (false)"
    assert record[1] is None, "last_verified_at should be NULL"
    assert record[2] is not None, "generated_at should be set (from installed_at)"


def test_upgrade_creates_indexes(test_db_with_old_schema):
    """Test that indexes are created on new table."""
    # Run migration
    migration.upgrade(test_db_with_old_schema)

    # Verify indexes created
    cursor = test_db_with_old_schema.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='provider_files'
    """)
    indexes = {row[0] for row in cursor.fetchall()}

    expected_indexes = [
        'idx_provider_files_installation',
        'idx_provider_files_hash',
        'idx_provider_files_type',
    ]

    for index_name in expected_indexes:
        assert index_name in indexes, f"Index {index_name} should be created"


def test_upgrade_idempotent(test_db_already_migrated):
    """Test that migration is idempotent (can run multiple times safely)."""
    # Run migration on already-migrated database
    migration.upgrade(test_db_already_migrated)

    # Verify schema unchanged
    cursor = test_db_already_migrated.execute("PRAGMA table_info(provider_files)")
    columns = {row[1] for row in cursor.fetchall()}

    expected_columns = {
        'id', 'installation_id', 'file_path', 'file_type', 'content_hash',
        'generated_at', 'last_verified_at', 'modification_detected'
    }

    assert expected_columns.issubset(columns), "All expected columns should exist"
    assert 'file_hash' not in columns, "Old file_hash column should not reappear"


def test_downgrade_reverts_to_old_schema(test_db_already_migrated):
    """Test that downgrade reverts table to old schema."""
    # Insert a test record in NEW schema
    test_db_already_migrated.execute("""
        INSERT INTO provider_installations (id, project_id, provider_name, version)
        VALUES (1, 1, 'cursor', '1.0.0')
    """)
    test_db_already_migrated.execute("""
        INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at, modification_detected)
        VALUES (1, 'test/file.md', 'rules', 'hash123', '2025-10-27T12:00:00', 0)
    """)
    test_db_already_migrated.commit()

    # Run downgrade
    migration.downgrade(test_db_already_migrated)

    # Verify old schema restored
    cursor = test_db_already_migrated.execute("PRAGMA table_info(provider_files)")
    columns = {row[1] for row in cursor.fetchall()}

    assert 'file_hash' in columns, "file_hash column should be restored"
    assert 'content_hash' not in columns, "content_hash column should be removed"
    assert 'generated_at' not in columns, "generated_at column should be removed"
    assert 'last_verified_at' not in columns, "last_verified_at column should be removed"
    assert 'modification_detected' not in columns, "modification_detected column should be removed"

    # Verify data preserved
    cursor = test_db_already_migrated.execute("SELECT file_path, file_hash FROM provider_files")
    record = cursor.fetchone()

    assert record is not None
    assert record[0] == 'test/file.md', "file_path should be preserved"
    assert record[1] == 'hash123', "file_hash (formerly content_hash) should be preserved"


def test_downgrade_reverses_file_type_mapping(test_db_already_migrated):
    """Test that downgrade reverses file_type value mapping."""
    # Insert test records with NEW file_type values
    test_db_already_migrated.execute("""
        INSERT INTO provider_installations (id, project_id, provider_name, version)
        VALUES (1, 1, 'cursor', '1.0.0')
    """)

    new_types = [
        ('file1.md', 'rules', 'hash1'),
        ('file2.md', 'agent', 'hash2'),
        ('file3.md', 'hook', 'hash3'),
        ('file4.md', 'config', 'hash4'),
        ('file5.md', 'other', 'hash5'),
    ]

    for file_path, file_type, content_hash in new_types:
        test_db_already_migrated.execute("""
            INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
            VALUES (1, ?, ?, ?, '2025-10-27T12:00:00')
        """, (file_path, file_type, content_hash))

    test_db_already_migrated.commit()

    # Run downgrade
    migration.downgrade(test_db_already_migrated)

    # Verify reverse mapping
    cursor = test_db_already_migrated.execute("""
        SELECT file_path, file_type FROM provider_files ORDER BY file_path
    """)
    results = cursor.fetchall()

    expected_reverse_mappings = {
        'file1.md': 'rule',  # rules → rule
        'file2.md': 'mode',  # agent → mode
        'file3.md': 'hook',  # hook → hook
        'file4.md': 'config',  # config → config
        'file5.md': 'memory',  # other → memory
    }

    for file_path, file_type in results:
        assert file_path in expected_reverse_mappings, f"Unexpected file_path: {file_path}"
        assert file_type == expected_reverse_mappings[file_path], \
            f"File type mismatch for {file_path}: expected {expected_reverse_mappings[file_path]}, got {file_type}"


def test_downgrade_preserves_data_count(test_db_already_migrated):
    """Test that downgrade preserves all records."""
    # Insert test data
    test_db_already_migrated.execute("""
        INSERT INTO provider_installations (id, project_id, provider_name, version)
        VALUES (1, 1, 'cursor', '1.0.0')
    """)

    for i in range(5):
        test_db_already_migrated.execute("""
            INSERT INTO provider_files (installation_id, file_path, file_type, content_hash, generated_at)
            VALUES (1, ?, 'rules', ?, '2025-10-27T12:00:00')
        """, (f'file{i}.md', f'hash{i}'))

    test_db_already_migrated.commit()

    # Count before downgrade
    cursor = test_db_already_migrated.execute("SELECT COUNT(*) FROM provider_files")
    count_before = cursor.fetchone()[0]

    # Run downgrade
    migration.downgrade(test_db_already_migrated)

    # Count after downgrade
    cursor = test_db_already_migrated.execute("SELECT COUNT(*) FROM provider_files")
    count_after = cursor.fetchone()[0]

    assert count_after == count_before, f"Record count mismatch: before={count_before}, after={count_after}"
