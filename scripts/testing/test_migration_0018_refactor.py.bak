#!/usr/bin/env python3
"""
Test Script: Verify Migration 0018 Refactor

Verifies that the refactored migration_0018.py:
1. Creates all tables successfully
2. Uses enum-generated CHECK constraints
3. Constraints match Pydantic enum values
4. No dependency on schema.py
"""

import sqlite3
import tempfile
import os
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from agentpm.core.database.migrations.files import migration_0018
from agentpm.core.database.utils.enum_helpers import validate_all_enum_constraints
from agentpm.core.database.enums import (
    ProjectStatus,
    WorkItemType,
    WorkItemStatus,
    TaskType,
    TaskStatus,
    IdeaStatus,
    IdeaSource,
    EnforcementLevel,
)


def test_migration_creates_all_tables():
    """Test that migration creates all 18 tables"""
    print("\n=== Test 1: Table Creation ===")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    try:
        conn = sqlite3.connect(db_path)

        # Run migration
        migration_0018.upgrade(conn)

        # Check tables exist
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            'agent_relationships',
            'agent_tools',
            'agents',
            'contexts',
            'document_references',
            'evidence_sources',
            'ideas',
            'projects',
            'rules',
            'schema_migrations',
            'session_events',
            'sessions',
            'task_blockers',
            'task_dependencies',
            'tasks',
            'work_item_dependencies',
            'work_item_summaries',
            'work_items'
        ]

        missing = set(expected_tables) - set(tables)
        extra = set(tables) - set(expected_tables)

        if missing:
            print(f"  ❌ FAIL: Missing tables: {missing}")
            return False
        if extra:
            print(f"  ⚠️  WARNING: Extra tables: {extra}")

        print(f"  ✅ PASS: All {len(expected_tables)} tables created")
        conn.close()
        return True

    finally:
        os.unlink(db_path)


def test_enum_constraints_sync():
    """Test that CHECK constraints match enum values"""
    print("\n=== Test 2: Enum Constraint Synchronization ===")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    try:
        conn = sqlite3.connect(db_path)

        # Run migration
        migration_0018.upgrade(conn)

        # Validate all enum constraints
        issues = validate_all_enum_constraints(conn)

        if issues:
            print(f"  ❌ FAIL: Found {len(issues)} constraint mismatches:")
            for location, diffs in issues.items():
                print(f"    - {location}: {diffs}")
            conn.close()
            return False

        print(f"  ✅ PASS: All enum constraints synchronized")
        conn.close()
        return True

    finally:
        os.unlink(db_path)


def test_sample_data_insertion():
    """Test that enum values work in actual inserts"""
    print("\n=== Test 3: Sample Data Insertion ===")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    try:
        conn = sqlite3.connect(db_path)

        # Run migration
        migration_0018.upgrade(conn)

        # Test project with enum status
        try:
            conn.execute("""
                INSERT INTO projects (name, path, status)
                VALUES (?, ?, ?)
            """, ("Test Project", "/tmp/test", ProjectStatus.ACTIVE.value))

            conn.execute("""
                INSERT INTO work_items (project_id, name, type, status)
                VALUES (?, ?, ?, ?)
            """, (1, "Test WorkItem", WorkItemType.FEATURE.value, WorkItemStatus.IN_PROGRESS.value))

            conn.execute("""
                INSERT INTO tasks (work_item_id, name, type, status)
                VALUES (?, ?, ?, ?)
            """, (1, "Test Task", TaskType.IMPLEMENTATION.value, TaskStatus.IN_PROGRESS.value))

            conn.execute("""
                INSERT INTO ideas (project_id, title, status, source)
                VALUES (?, ?, ?, ?)
            """, (1, "Test Idea", IdeaStatus.IDEA.value, IdeaSource.USER.value))

            conn.execute("""
                INSERT INTO rules (project_id, rule_id, name, enforcement_level)
                VALUES (?, ?, ?, ?)
            """, (1, "TEST-001", "Test Rule", EnforcementLevel.GUIDE.value))

            conn.commit()
            print(f"  ✅ PASS: Sample data inserted successfully")

        except sqlite3.IntegrityError as e:
            print(f"  ❌ FAIL: Constraint violation: {e}")
            conn.close()
            return False

        # Test invalid enum value rejection
        try:
            conn.execute("""
                INSERT INTO projects (name, path, status)
                VALUES (?, ?, ?)
            """, ("Bad Project", "/tmp/bad", "invalid_status"))
            conn.commit()
            print(f"  ❌ FAIL: Accepted invalid enum value")
            conn.close()
            return False

        except sqlite3.IntegrityError:
            print(f"  ✅ PASS: Invalid enum values correctly rejected")

        conn.close()
        return True

    finally:
        os.unlink(db_path)


def test_no_schema_py_dependency():
    """Test that migration doesn't import from schema.py"""
    print("\n=== Test 4: No schema.py Dependency ===")

    import inspect
    source = inspect.getsource(migration_0018)

    if "from agentpm.core.database.utils.schema import" in source:
        print(f"  ❌ FAIL: Migration still imports from schema.py")
        return False

    if "initialize_schema" in source and "import" in source[:500]:
        print(f"  ❌ FAIL: Migration still references initialize_schema")
        return False

    print(f"  ✅ PASS: Migration is self-contained")
    return True


def test_downgrade():
    """Test that downgrade properly drops all tables"""
    print("\n=== Test 5: Downgrade Cleanup ===")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    try:
        conn = sqlite3.connect(db_path)

        # Run migration
        migration_0018.upgrade(conn)

        # Verify tables exist
        cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        if table_count == 0:
            print(f"  ❌ FAIL: No tables created before downgrade")
            conn.close()
            return False

        # Run downgrade
        migration_0018.downgrade(conn)

        # Verify tables dropped
        cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        if table_count > 0:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            remaining = [row[0] for row in cursor.fetchall()]
            print(f"  ❌ FAIL: {table_count} tables remain after downgrade: {remaining}")
            conn.close()
            return False

        print(f"  ✅ PASS: All tables dropped on downgrade")
        conn.close()
        return True

    finally:
        os.unlink(db_path)


def main():
    """Run all tests-BAK"""
    print("=" * 60)
    print("Testing Migration 0018 Refactor")
    print("=" * 60)

    tests = [
        test_migration_creates_all_tables,
        test_enum_constraints_sync,
        test_sample_data_insertion,
        test_no_schema_py_dependency,
        test_downgrade,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ FAIL: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")

    if passed == total:
        print("  ✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"  ❌ {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
