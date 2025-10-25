#!/usr/bin/env python3
"""
Migration Test Script

This script tests-BAK the consolidated migration in a real AIPM environment.
It verifies that all tables are created correctly and the rich context system works.
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

def test_database_tables():
    """Test that all expected tables exist in the database."""
    db_path = Path(".aipm/data/aipm.db")
    
    if not db_path.exists():
        print("❌ Database file not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    expected_tables = [
        'agents', 'projects', 'tasks', 'contexts', 'rules', 'work_item_dependencies',
        'document_references', 'schema_migrations', 'work_item_summaries', 'events',
        'sessions', 'work_items', 'evidence_sources', 'task_blockers', 'ideas',
        'task_dependencies'
    ]
    
    missing_tables = set(expected_tables) - set(tables)
    extra_tables = set(tables) - set(expected_tables)
    
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    
    if extra_tables:
        print(f"⚠️  Extra tables: {extra_tables}")
    
    print(f"✅ All {len(expected_tables)} expected tables found")
    return True

def test_rich_context_constraints():
    """Test that the contexts table has the correct CHECK constraints."""
    db_path = Path(".aipm/data/aipm.db")
    conn = sqlite3.connect(db_path)
    
    # Get the table definition
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contexts'")
    table_sql = cursor.fetchone()[0]
    conn.close()
    
    # Check for new context types in the constraint
    new_context_types = [
        'business_pillars_context',
        'market_research_context',
        'competitive_analysis_context',
        'quality_gates_context',
        'stakeholder_context',
        'technical_context',
        'implementation_context',
        'idea_context',
        'idea_to_work_item_mapping'
    ]
    
    missing_types = []
    for context_type in new_context_types:
        if context_type not in table_sql:
            missing_types.append(context_type)
    
    if missing_types:
        print(f"❌ Missing context types in constraint: {missing_types}")
        return False
    
    print("✅ All new context types found in CHECK constraint")
    return True

def test_rich_context_functionality():
    """Test that rich context commands work correctly."""
    try:
        # Test creating rich context (use different context type to avoid UNIQUE constraint)
        result = subprocess.run([
            'apm', 'context', 'rich', 'create',
            '--entity-type', 'work-item',
            '--entity-id', '1',
            '--context-type', 'quality_gates_context',
            '--data', '{"test": "data"}'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode != 0:
            print(f"❌ Rich context creation failed: {result.stderr}")
            return False
        
        # Test showing rich context
        result = subprocess.run([
            'apm', 'context', 'rich', 'show',
            '--entity-type', 'work-item',
            '--entity-id', '1'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode != 0:
            print(f"❌ Rich context show failed: {result.stderr}")
            return False
        
        print("✅ Rich context functionality working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Rich context test failed: {e}")
        return False

def test_migration_record():
    """Test that the migration record is correct."""
    db_path = Path(".aipm/data/aipm.db")
    conn = sqlite3.connect(db_path)
    
    cursor = conn.execute("SELECT version, description FROM schema_migrations")
    migrations = cursor.fetchall()
    conn.close()
    
    if not migrations:
        print("❌ No migration records found")
        return False
    
    # Check for consolidated migration
    consolidated_migration = next((m for m in migrations if 'consolidated' in m[1].lower()), None)
    if not consolidated_migration:
        print("❌ Consolidated migration record not found")
        print(f"   Found migrations: {migrations}")
        return False
    
    print(f"✅ Migration record found: {consolidated_migration[0]} - {consolidated_migration[1]}")
    return True

def main():
    """Run all migration tests-BAK."""
    print("🧪 Testing Consolidated Migration")
    print("=" * 50)
    
    tests = [
        ("Database Tables", test_database_tables),
        ("Rich Context Constraints", test_rich_context_constraints),
        ("Rich Context Functionality", test_rich_context_functionality),
        ("Migration Record", test_migration_record),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All migration tests-BAK passed!")
        return 0
    else:
        print("💥 Some migration tests-BAK failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
