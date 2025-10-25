#!/usr/bin/env python3
"""
Database Status Migration Script

This script migrates old 9-state status values to the new 6-state system
in the APM (Agent Project Manager) database.

Old → New Status Mappings:
- proposed → draft
- accepted → active  
- in_progress → active
- completed → done
- review → review (unchanged)
- archived → archived (unchanged)
- cancelled → cancelled (unchanged)
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
    """Migrate status values in the database."""
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
        
        # Check current status values
        cursor.execute("SELECT DISTINCT status FROM work_items;")
        work_item_statuses = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT status FROM tasks;")
        task_statuses = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 Current status values:")
        print(f"  Work items: {work_item_statuses}")
        print(f"  Tasks: {task_statuses}")
        
        # Migrate work items
        work_item_changes = 0
        for old_status, new_status in STATUS_MAPPINGS.items():
            if old_status != new_status:
                cursor.execute("SELECT COUNT(*) FROM work_items WHERE status = ?;", (old_status,))
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  Work items: {count} records with status '{old_status}' → '{new_status}'")
                    if not dry_run:
                        cursor.execute("UPDATE work_items SET status = ? WHERE status = ?;", 
                                     (new_status, old_status))
                    work_item_changes += count
        
        # Migrate tasks
        task_changes = 0
        for old_status, new_status in STATUS_MAPPINGS.items():
            if old_status != new_status:
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?;", (old_status,))
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  Tasks: {count} records with status '{old_status}' → '{new_status}'")
                    if not dry_run:
                        cursor.execute("UPDATE tasks SET status = ? WHERE status = ?;", 
                                     (new_status, old_status))
                    task_changes += count
        
        if dry_run:
            print(f"\n🔍 DRY RUN - Would migrate:")
            print(f"  Work items: {work_item_changes} records")
            print(f"  Tasks: {task_changes} records")
        else:
            if work_item_changes > 0 or task_changes > 0:
                conn.commit()
                print(f"\n✅ Migration completed:")
                print(f"  Work items: {work_item_changes} records updated")
                print(f"  Tasks: {task_changes} records updated")
            else:
                print(f"\n✅ No migration needed - all status values are already current")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        return False

def main():
    """Main script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database status values to 6-state system')
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
            print(f"\n✅ Database migration complete!")
            print(f"\n🔧 Next steps:")
            print(f"  1. Test the CLI: apm status")
            print(f"  2. Verify all status values are correct")
    else:
        print(f"\n❌ Migration failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
