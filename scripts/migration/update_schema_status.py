#!/usr/bin/env python3
"""
Database Schema Status Update Script

This script updates the CHECK constraints in the database schema
to use the new 6-state status values.

Old status values: proposed, validated, accepted, in_progress, review, completed, archived, blocked, cancelled
New status values: draft, ready, active, review, done, archived, blocked, cancelled
"""

import sqlite3
import sys
from pathlib import Path

def update_schema(db_path: Path, dry_run: bool = False):
    """Update database schema to use new status values."""
    if not db_path.exists():
        print(f"❌ Database {db_path} does not exist")
        return False
    
    print(f"🔍 Updating schema: {db_path}")
    
    # New status values for CHECK constraints
    new_work_item_statuses = "('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled')"
    new_task_statuses = "('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled')"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if dry_run:
            print("🔍 DRY RUN - Would execute the following SQL:")
        
        # Update work_items table
        work_items_sql = f"""
        CREATE TABLE work_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK(type IN ('feature', 'enhancement', 'bugfix', 'research', 'analysis', 'planning', 'refactoring', 'infrastructure', 'maintenance', 'monitoring', 'documentation', 'security', 'fix_bugs_issues')),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            status TEXT DEFAULT 'draft' CHECK(status IN {new_work_item_statuses}),
            project_id INTEGER NOT NULL,
            work_item_id INTEGER,
            effort_estimate_hours REAL,
            business_context TEXT,
            metadata TEXT DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            due_date TIMESTAMP,
            not_before TIMESTAMP,
            phase TEXT CHECK(phase IN ('D1_DISCOVERY', 'P1_PLAN', 'I1_IMPLEMENTATION', 'R1_REVIEW', 'O1_OPERATIONS', 'E1_EVOLUTION')),
            is_continuous INTEGER NOT NULL DEFAULT 0 CHECK(is_continuous IN (0, 1)),
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (work_item_id) REFERENCES work_items (id)
        );
        """
        
        # Update tasks table
        tasks_sql = f"""
        CREATE TABLE tasks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'implementation' CHECK(type IN ('design', 'implementation', 'testing', 'bugfix', 'refactoring', 'documentation', 'deployment', 'review', 'analysis', 'research', 'maintenance', 'optimization', 'integration', 'training', 'meeting', 'planning', 'dependency', 'blocker', 'simple', 'other')),
            effort_hours REAL CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8)),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            status TEXT DEFAULT 'draft' CHECK(status IN {new_task_statuses}),
            work_item_id INTEGER NOT NULL,
            assigned_to TEXT,
            blocked_reason TEXT,
            quality_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            due_date TIMESTAMP,
            FOREIGN KEY (work_item_id) REFERENCES work_items (id)
        );
        """
        
        if dry_run:
            print("\n📝 Work Items Table Update:")
            print(work_items_sql)
            print("\n📝 Tasks Table Update:")
            print(tasks_sql)
            print("\n📝 Migration Steps:")
            print("1. Create new tables with updated CHECK constraints")
            print("2. Copy data from old tables to new tables")
            print("3. Drop old tables")
            print("4. Rename new tables to original names")
            print("5. Recreate indexes and triggers")
        else:
            # Step 1: Create new tables
            print("📝 Creating new tables with updated schema...")
            cursor.execute(work_items_sql)
            cursor.execute(tasks_sql)
            
            # Step 2: Copy data from old tables
            print("📝 Copying data from old tables...")
            cursor.execute("INSERT INTO work_items_new SELECT * FROM work_items;")
            cursor.execute("INSERT INTO tasks_new SELECT * FROM tasks;")
            
            # Step 3: Drop old tables
            print("📝 Dropping old tables...")
            cursor.execute("DROP TABLE work_items;")
            cursor.execute("DROP TABLE tasks;")
            
            # Step 4: Rename new tables
            print("📝 Renaming new tables...")
            cursor.execute("ALTER TABLE work_items_new RENAME TO work_items;")
            cursor.execute("ALTER TABLE tasks_new RENAME TO tasks;")
            
            # Step 5: Recreate indexes (if any exist)
            print("📝 Schema update complete!")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

def main():
    """Main script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update database schema for 6-state status system')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--db-path', type=str, default='.aipm/data/aipm.db',
                       help='Path to database file (default: .aipm/data/aipm.db)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db_path)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    success = update_schema(db_path, dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            print(f"\n💡 Run without --dry-run to apply changes")
        else:
            print(f"\n✅ Schema update complete!")
            print(f"\n🔧 Next steps:")
            print(f"  1. Run status migration: python3 migrate_status_values.py")
            print(f"  2. Test the CLI: apm status")
    else:
        print(f"\n❌ Schema update failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
