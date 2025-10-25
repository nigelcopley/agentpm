"""
Tests for migration 0044 - Document Visibility System

Tests the migration that adds visibility, lifecycle, and audit trail
support for documents.
"""

import sqlite3
import pytest
from pathlib import Path
from agentpm.core.database.migrations.files import migration_0044_document_visibility_system as migration


@pytest.fixture
def test_db(tmp_path):
    """Create a test database with minimal document_references table."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)

    # Create minimal document_references table (similar to existing schema)
    conn.execute("""
        CREATE TABLE document_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT,
            title TEXT,
            description TEXT,
            created_by TEXT DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            audience TEXT
        )
    """)

    conn.commit()
    yield conn
    conn.close()


def test_upgrade_adds_columns(test_db):
    """Test that upgrade adds all required columns to document_references."""
    # Run migration
    migration.upgrade(test_db)

    # Verify columns added
    cursor = test_db.execute("PRAGMA table_info(document_references)")
    columns = {row[1] for row in cursor.fetchall()}

    # Check new visibility/lifecycle columns
    assert 'visibility' in columns, "visibility column should be added"
    assert 'lifecycle_stage' in columns, "lifecycle_stage column should be added"
    assert 'published_path' in columns, "published_path column should be added"
    assert 'published_date' in columns, "published_date column should be added"
    assert 'unpublished_date' in columns, "unpublished_date column should be added"
    assert 'review_status' in columns, "review_status column should be added"
    assert 'reviewer_id' in columns, "reviewer_id column should be added"
    assert 'review_comment' in columns, "review_comment column should be added"
    assert 'auto_publish' in columns, "auto_publish column should be added"

    # Verify audience column still exists (it was already there)
    assert 'audience' in columns, "audience column should still exist"


def test_upgrade_creates_tables(test_db):
    """Test that upgrade creates required tables."""
    # Run migration
    migration.upgrade(test_db)

    # Verify tables created
    cursor = test_db.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('document_visibility_policies', 'document_audit_log')
    """)
    tables = {row[0] for row in cursor.fetchall()}

    assert 'document_visibility_policies' in tables, "Policies table should be created"
    assert 'document_audit_log' in tables, "Audit log table should be created"


def test_upgrade_creates_indexes(test_db):
    """Test that upgrade creates performance indexes."""
    # Run migration
    migration.upgrade(test_db)

    # Verify indexes created
    cursor = test_db.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index'
    """)
    indexes = {row[0] for row in cursor.fetchall()}

    expected_indexes = [
        'idx_doc_visibility',
        'idx_doc_lifecycle',
        'idx_doc_review_status',
        'idx_audit_log_document',
        'idx_audit_log_timestamp',
        'idx_audit_log_action',
        'idx_visibility_policy_lookup',
    ]

    for index_name in expected_indexes:
        assert index_name in indexes, f"Index {index_name} should be created"


def test_upgrade_populates_default_policies(test_db):
    """Test that default visibility policies are populated."""
    # Run migration
    migration.upgrade(test_db)

    # Check policies populated
    cursor = test_db.execute("SELECT COUNT(*) FROM document_visibility_policies")
    count = cursor.fetchone()[0]

    assert count >= 30, f"Should have at least 30 default policies, got {count}"

    # Check specific policies - guides should be public
    cursor = test_db.execute("""
        SELECT default_visibility, force_public, requires_review
        FROM document_visibility_policies
        WHERE category='guides' AND doc_type='user_guide'
    """)
    row = cursor.fetchone()

    assert row is not None, "user_guide policy should exist"
    assert row[0] == 'public', "user_guide should default to public"
    assert row[1] == 1, "user_guide should be force_public"
    assert row[2] == 1, "user_guide should require review"

    # Check planning docs should be private
    cursor = test_db.execute("""
        SELECT default_visibility, force_private, requires_review
        FROM document_visibility_policies
        WHERE category='planning' AND doc_type='requirements'
    """)
    row = cursor.fetchone()

    assert row is not None, "requirements policy should exist"
    assert row[0] == 'private', "requirements should default to private"
    assert row[1] == 1, "requirements should be force_private"
    assert row[2] == 0, "requirements should not require review"


def test_visibility_policies_schema(test_db):
    """Test that document_visibility_policies table has correct schema."""
    # Run migration
    migration.upgrade(test_db)

    # Check schema
    cursor = test_db.execute("PRAGMA table_info(document_visibility_policies)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type

    expected_columns = {
        'id': 'INTEGER',
        'category': 'TEXT',
        'doc_type': 'TEXT',
        'default_visibility': 'TEXT',
        'default_audience': 'TEXT',
        'requires_review': 'BOOLEAN',
        'auto_publish_on_approved': 'BOOLEAN',
        'base_score': 'INTEGER',
        'force_private': 'BOOLEAN',
        'force_public': 'BOOLEAN',
        'description': 'TEXT',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP',
    }

    for col_name, col_type in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        assert columns[col_name] == col_type, f"Column {col_name} should be {col_type}"


def test_audit_log_schema(test_db):
    """Test that document_audit_log table has correct schema."""
    # Run migration
    migration.upgrade(test_db)

    # Check schema
    cursor = test_db.execute("PRAGMA table_info(document_audit_log)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type

    expected_columns = {
        'id': 'INTEGER',
        'document_id': 'INTEGER',
        'action': 'TEXT',
        'actor': 'TEXT',
        'timestamp': 'TIMESTAMP',
        'from_state': 'TEXT',
        'to_state': 'TEXT',
        'details': 'TEXT',
        'comment': 'TEXT',
    }

    for col_name, col_type in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        assert columns[col_name] == col_type, f"Column {col_name} should be {col_type}"


def test_audit_log_foreign_key(test_db):
    """Test that document_audit_log has foreign key to document_references."""
    # Run migration
    migration.upgrade(test_db)

    # Check foreign keys
    cursor = test_db.execute("PRAGMA foreign_key_list(document_audit_log)")
    foreign_keys = list(cursor.fetchall())

    assert len(foreign_keys) > 0, "Should have foreign key constraint"
    assert foreign_keys[0][2] == 'document_references', "Should reference document_references"


def test_downgrade_removes_tables(test_db):
    """Test that downgrade removes created tables."""
    # Upgrade then downgrade
    migration.upgrade(test_db)
    migration.downgrade(test_db)

    # Verify tables removed
    cursor = test_db.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('document_visibility_policies', 'document_audit_log')
    """)
    tables = list(cursor.fetchall())

    assert len(tables) == 0, "New tables should be removed after downgrade"


def test_downgrade_removes_indexes(test_db):
    """Test that downgrade removes created indexes."""
    # Upgrade then downgrade
    migration.upgrade(test_db)
    migration.downgrade(test_db)

    # Verify indexes removed
    cursor = test_db.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index'
    """)
    indexes = {row[0] for row in cursor.fetchall()}

    removed_indexes = [
        'idx_doc_visibility',
        'idx_doc_lifecycle',
        'idx_doc_review_status',
        'idx_audit_log_document',
        'idx_audit_log_timestamp',
        'idx_audit_log_action',
        'idx_visibility_policy_lookup',
    ]

    for index_name in removed_indexes:
        assert index_name not in indexes, f"Index {index_name} should be removed"


def test_migration_is_idempotent(test_db):
    """Test that running upgrade twice doesn't fail."""
    # Run migration twice
    migration.upgrade(test_db)
    migration.upgrade(test_db)  # Should not fail

    # Verify still works
    cursor = test_db.execute("SELECT COUNT(*) FROM document_visibility_policies")
    count = cursor.fetchone()[0]
    assert count >= 30, "Policies should still be populated"

    # Verify no duplicate policies
    cursor = test_db.execute("""
        SELECT category, doc_type, COUNT(*)
        FROM document_visibility_policies
        GROUP BY category, doc_type
        HAVING COUNT(*) > 1
    """)
    duplicates = list(cursor.fetchall())
    assert len(duplicates) == 0, "Should not have duplicate policies"


def test_existing_data_preserved(test_db):
    """Test that existing document records are preserved after migration."""
    # Insert test data
    test_db.execute("""
        INSERT INTO document_references
        (entity_type, entity_id, file_path, document_type, title, category, audience)
        VALUES
        ('project', 1, '/docs/test.md', 'user_guide', 'Test Guide', 'guides', 'users'),
        ('work_item', 42, '/docs/plan.md', 'requirements', 'Requirements', 'planning', 'internal')
    """)
    test_db.commit()

    # Run migration
    migration.upgrade(test_db)

    # Verify data preserved
    cursor = test_db.execute("""
        SELECT id, title, category, audience
        FROM document_references
        ORDER BY id
    """)
    rows = cursor.fetchall()

    assert len(rows) == 2, "Should have 2 records"
    assert rows[0][1] == 'Test Guide', "First record title preserved"
    assert rows[0][2] == 'guides', "First record category preserved"
    assert rows[0][3] == 'users', "First record audience preserved"
    assert rows[1][1] == 'Requirements', "Second record title preserved"


def test_default_values_applied(test_db):
    """Test that default values are applied to new columns."""
    # Insert test data before migration
    test_db.execute("""
        INSERT INTO document_references
        (entity_type, entity_id, file_path, document_type, title)
        VALUES ('project', 1, '/docs/test.md', 'user_guide', 'Test Guide')
    """)
    test_db.commit()

    # Run migration
    migration.upgrade(test_db)

    # Check default values applied
    cursor = test_db.execute("""
        SELECT visibility, lifecycle_stage, auto_publish
        FROM document_references
        WHERE id = 1
    """)
    row = cursor.fetchone()

    assert row[0] == 'private', "Default visibility should be 'private'"
    assert row[1] == 'draft', "Default lifecycle_stage should be 'draft'"
    assert row[2] == 0, "Default auto_publish should be 0 (False)"


def test_policy_unique_constraint(test_db):
    """Test that policies have unique constraint on (category, doc_type)."""
    # Run migration
    migration.upgrade(test_db)

    # Try to insert duplicate policy
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        test_db.execute("""
            INSERT INTO document_visibility_policies
            (category, doc_type, default_visibility, default_audience, base_score)
            VALUES ('guides', 'user_guide', 'public', 'users', 70)
        """)


def test_policies_by_category(test_db):
    """Test that policies are distributed across all major categories."""
    # Run migration
    migration.upgrade(test_db)

    # Check distribution
    cursor = test_db.execute("""
        SELECT category, COUNT(*)
        FROM document_visibility_policies
        GROUP BY category
        ORDER BY category
    """)
    categories = dict(cursor.fetchall())

    # Verify major categories have policies
    expected_categories = [
        'guides',
        'reference',
        'planning',
        'architecture',
        'implementation',
        'testing',
        'operations',
        'research',
        'communication',
        'governance',
    ]

    for category in expected_categories:
        assert category in categories, f"Category {category} should have policies"
        assert categories[category] > 0, f"Category {category} should have at least 1 policy"
