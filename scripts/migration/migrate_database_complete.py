#!/usr/bin/env python3
"""
Complete Database Migration Script

This script migrates the database from the old 9-state system to the new 6-state system
by updating both the data and the schema constraints.
"""

import sqlite3
import sys
from pathlib import Path

# Status mappings for the 6-state system
STATUS_MAPPINGS = {
    'proposed': 'draft',
    'accepted': 'active',
    'in_progress': 'active',
    'completed': 'done',
    # These remain unchanged
    'review': 'review',
    'archived': 'archived',
    'cancelled': 'cancelled',
}

def migrate_database(db_path: Path, dry_run: bool = False):
    """Complete database migration to 6-state system."""
    if not db_path.exists():
        print(f"❌ Database {db_path} does not exist")
        return False
    
    print(f"🔍 Migrating database: {db_path}")
    print(f"📋 Status mappings:")
    for old, new in STATUS_MAPPINGS.items():
        if old != new:
            print(f"  {old} → {new}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if dry_run:
            print("🔍 DRY RUN - Would execute the following:")
        
        # Step 1: Update data first (temporarily disable constraints)
        print("📝 Step 1: Updating status values in data...")
        
        if not dry_run:
            # Temporarily disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=OFF;")
            
            # Update work items
            work_item_changes = 0
            for old_status, new_status in STATUS_MAPPINGS.items():
                if old_status != new_status:
                    cursor.execute("SELECT COUNT(*) FROM work_items WHERE status = ?;", (old_status,))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  Work items: {count} records '{old_status}' → '{new_status}'")
                        cursor.execute("UPDATE work_items SET status = ? WHERE status = ?;", 
                                     (new_status, old_status))
                        work_item_changes += count
            
            # Update tasks
            task_changes = 0
            for old_status, new_status in STATUS_MAPPINGS.items():
                if old_status != new_status:
                    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?;", (old_status,))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  Tasks: {count} records '{old_status}' → '{new_status}'")
                        cursor.execute("UPDATE tasks SET status = ? WHERE status = ?;", 
                                     (new_status, old_status))
                        task_changes += count
            
            print(f"  Total changes: {work_item_changes} work items, {task_changes} tasks")
        
        # Step 2: Update schema constraints
        print("📝 Step 2: Updating schema constraints...")
        
        if not dry_run:
            # Get current schemas
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='work_items';")
            work_items_schema = cursor.fetchone()[0]
            
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks';")
            tasks_schema = cursor.fetchone()[0]
            
            # Update work_items schema
            new_work_items_schema = work_items_schema.replace(
                "CHECK(status IN ('proposed', 'validated', 'accepted', 'in_progress', 'review', 'completed', 'archived', 'blocked', 'cancelled'))",
                "CHECK(status IN ('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled'))"
            ).replace(
                "DEFAULT 'proposed'",
                "DEFAULT 'draft'"
            )
            
            # Update tasks schema
            new_tasks_schema = tasks_schema.replace(
                "CHECK(status IN ('proposed', 'validated', 'accepted', 'in_progress', 'review', 'completed', 'archived', 'blocked', 'cancelled'))",
                "CHECK(status IN ('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled'))"
            ).replace(
                "DEFAULT 'proposed'",
                "DEFAULT 'draft'"
            )
            
            # Create new tables with updated constraints
            cursor.execute("DROP TABLE IF EXISTS work_items_new;")
            cursor.execute("DROP TABLE IF EXISTS tasks_new;")
            
            # Replace CREATE TABLE IF NOT EXISTS with CREATE TABLE
            new_work_items_schema = new_work_items_schema.replace("CREATE TABLE IF NOT EXISTS", "CREATE TABLE")
            new_tasks_schema = new_tasks_schema.replace("CREATE TABLE IF NOT EXISTS", "CREATE TABLE")
            
            cursor.execute(new_work_items_schema.replace('"work_items"', 'work_items_new'))
            cursor.execute(new_tasks_schema.replace('"tasks"', 'tasks_new'))
            
            # Copy data to new tables
            cursor.execute("INSERT INTO work_items_new SELECT * FROM work_items;")
            cursor.execute("INSERT INTO tasks_new SELECT * FROM tasks;")
            
            # Replace old tables
            cursor.execute("DROP TABLE work_items;")
            cursor.execute("DROP TABLE tasks;")
            cursor.execute("ALTER TABLE work_items_new RENAME TO work_items;")
            cursor.execute("ALTER TABLE tasks_new RENAME TO tasks;")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX idx_work_items_project ON work_items(project_id);")
            cursor.execute("CREATE INDEX idx_work_items_parent ON work_items(parent_work_item_id);")
            cursor.execute("CREATE INDEX idx_work_items_status ON work_items(status);")
            cursor.execute("CREATE INDEX idx_work_items_type ON work_items(type);")
            cursor.execute("CREATE INDEX idx_work_items_priority ON work_items(priority);")
            cursor.execute("CREATE INDEX idx_work_items_continuous ON work_items(is_continuous);")
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON;")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        return False

def main():
    """Main script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete database migration to 6-state status system')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--db-path', type=str, default='.aipm/data/aipm.db',
                       help='Path to database file (default: .aipm/data/aipm.db)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db_path)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    success = migrate_database(db_path, dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            print(f"\n💡 Run without --dry-run to apply changes")
        else:
            print(f"\n✅ Complete database migration finished!")
            print(f"\n🔧 Next steps:")
            print(f"  1. Test the CLI: apm status")
            print(f"  2. Verify all status values are correct")
    else:
        print(f"\n❌ Migration failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
