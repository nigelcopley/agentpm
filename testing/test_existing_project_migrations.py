#!/usr/bin/env python3
"""
Test migration of existing AIPM projects to current schema.

This script tests-BAK migrating existing projects that have old schemas
to the current consolidated migration schema.
"""

import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

def get_project_info(project_path: Path) -> Dict[str, Any]:
    """Get information about an existing project's database."""
    db_path = project_path / ".aipm" / "data" / "aipm.db"
    
    if not db_path.exists():
        return {"error": "Database not found"}
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get migration history
        cursor = conn.execute("SELECT version, description FROM schema_migrations ORDER BY version")
        migrations = cursor.fetchall()
        
        # Get table count
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for specific tables
        has_events = 'events' in tables
        has_session_events = 'session_events' in tables
        has_agent_relationships = 'agent_relationships' in tables
        has_agent_tools = 'agent_tools' in tables
        
        conn.close()
        
        return {
            "migrations": migrations,
            "table_count": len(tables),
            "tables": sorted(tables),
            "has_events": has_events,
            "has_session_events": has_session_events,
            "has_agent_relationships": has_agent_relationships,
            "has_agent_tools": has_agent_tools,
            "needs_migration": len(tables) < 19 or not has_agent_relationships or not has_agent_tools
        }
    except Exception as e:
        return {"error": str(e)}

def test_project_migration(project_path: Path) -> bool:
    """Test migrating a specific project."""
    print(f"\n🔍 Testing migration for: {project_path.name}")
    
    # Get before state
    before = get_project_info(project_path)
    if "error" in before:
        print(f"❌ Error getting project info: {before['error']}")
        return False
    
    print(f"   Before migration:")
    print(f"   - Tables: {before['table_count']}")
    print(f"   - Migrations: {len(before['migrations'])}")
    print(f"   - Has events: {before['has_events']}")
    print(f"   - Has session_events: {before['has_session_events']}")
    print(f"   - Has agent_relationships: {before['has_agent_relationships']}")
    print(f"   - Has agent_tools: {before['has_agent_tools']}")
    print(f"   - Needs migration: {before['needs_migration']}")
    
    if not before['needs_migration']:
        print("   ✅ Project already up to date")
        return True
    
    # Run migration using AIPM CLI
    try:
        print("   🚀 Running migration...")
        result = subprocess.run([
            'python', '-c', f'''
import sys
sys.path.insert(0, "/Users/nigelcopley/.project_manager/aipm-v2")
from agentpm.core.database import DatabaseService
from agentpm.core.database.migrations import MigrationManager

# Create database service for this project
db_path = "{project_path / '.aipm' / 'data' / 'aipm.db'}"
db = DatabaseService(db_path)

# Run migrations
migration_manager = MigrationManager(db)
success_count, failure_count = migration_manager.run_all_pending()

print(f"Migration results: {{success_count}} successful, {{failure_count}} failed")
'''
            ], capture_output=True, text=True, cwd=project_path)
        
        if result.returncode != 0:
            print(f"   ❌ Migration failed: {result.stderr}")
            return False
        
        print(f"   {result.stdout.strip()}")
        
    except Exception as e:
        print(f"   ❌ Migration error: {e}")
        return False
    
    # Get after state
    after = get_project_info(project_path)
    if "error" in after:
        print(f"   ❌ Error getting post-migration info: {after['error']}")
        return False
    
    print(f"   After migration:")
    print(f"   - Tables: {after['table_count']}")
    print(f"   - Migrations: {len(after['migrations'])}")
    print(f"   - Has events: {after['has_events']}")
    print(f"   - Has session_events: {after['has_session_events']}")
    print(f"   - Has agent_relationships: {after['has_agent_relationships']}")
    print(f"   - Has agent_tools: {after['has_agent_tools']}")
    
    # Check if migration was successful
    success = (
        after['table_count'] >= 19 and
        after['has_session_events'] and
        after['has_agent_relationships'] and
        after['has_agent_tools']
    )
    
    if success:
        print("   ✅ Migration successful!")
    else:
        print("   ❌ Migration incomplete")
    
    return success

def main():
    """Test migration of all existing projects."""
    testing_dir = Path("/Users/nigelcopley/.project_manager/aipm-v2/testing")
    
    # Find all projects with AIPM databases
    projects = []
    for item in testing_dir.iterdir():
        if item.is_dir() and (item / ".aipm" / "data" / "aipm.db").exists():
            projects.append(item)
    
    print(f"🔍 Found {len(projects)} existing AIPM projects")
    
    # Test each project
    results = []
    for project in projects:
        success = test_project_migration(project)
        results.append((project.name, success))
    
    # Summary
    print(f"\n📊 Migration Test Results:")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for project_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {project_name}")
    
    print(f"\n🎯 Summary: {successful}/{total} projects migrated successfully")
    
    if successful == total:
        print("🎉 All existing projects migrated successfully!")
        return 0
    else:
        print("⚠️  Some projects failed to migrate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
