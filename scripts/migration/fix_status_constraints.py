#!/usr/bin/env python3
"""
Fix database status constraints to use 6-state workflow system.
This script updates the CHECK constraints in the database schema.
"""

import sqlite3
import os

def fix_status_constraints():
    """Update database schema to use 6-state workflow system."""
    
    db_path = "./.aipm/data/aipm.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing status constraints for 6-state workflow system...")
        
        # First, let's check current constraints
        cursor.execute("PRAGMA table_info(work_items)")
        work_items_info = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_info = cursor.fetchall()
        
        print("📋 Current work_items table structure:")
        for col in work_items_info:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
        
        print("\n📋 Current tasks table structure:")
        for col in tasks_info:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
        
        # Get current schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='work_items'")
        work_items_schema = cursor.fetchone()[0]
        print(f"\n📋 Current work_items schema:\n{work_items_schema}")
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
        tasks_schema = cursor.fetchone()[0]
        print(f"\n📋 Current tasks schema:\n{tasks_schema}")
        
        # Create new tables with updated constraints
        print("\n🔧 Creating new tables with 6-state constraints...")
        
        # New work_items table with 6-state system
        new_work_items_schema = """
        CREATE TABLE work_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_work_item_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK(type IN ('feature', 'enhancement', 'bugfix', 'research', 'analysis', 'planning', 'refactoring', 'infrastructure', 'maintenance', 'monitoring', 'documentation', 'security', 'fix_bugs_issues')),
            business_context TEXT,
            metadata TEXT DEFAULT '{}',
            effort_estimate_hours REAL,
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled')),
            is_continuous INTEGER NOT NULL DEFAULT 0 CHECK(is_continuous IN (0, 1)),
            phase TEXT,
            due_date TIMESTAMP,
            not_before TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
        """
        
        # New tasks table with 6-state system (matching current structure)
        new_tasks_schema = """
        CREATE TABLE tasks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'implementation' CHECK(type IN ('design', 'implementation', 'testing', 'bugfix', 'refactoring', 'documentation', 'deployment', 'review', 'analysis', 'research', 'maintenance', 'optimization', 'integration', 'training', 'meeting', 'planning', 'dependency', 'blocker', 'simple', 'other')),
            quality_metadata TEXT,
            effort_hours REAL CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8)),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            due_date TIMESTAMP,
            assigned_to TEXT,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled')),
            blocked_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
        """
        
        # Drop new tables if they exist
        cursor.execute("DROP TABLE IF EXISTS work_items_new")
        cursor.execute("DROP TABLE IF EXISTS tasks_new")
        
        # Create new tables
        cursor.execute(new_work_items_schema)
        cursor.execute(new_tasks_schema)
        
        # Copy data from old tables to new tables
        print("📋 Copying data from old tables to new tables...")
        
        # Copy work_items data
        cursor.execute("""
            INSERT INTO work_items_new 
            SELECT * FROM work_items
        """)
        
        # Copy tasks data
        cursor.execute("""
            INSERT INTO tasks_new 
            SELECT * FROM tasks
        """)
        
        # Drop old tables
        print("🗑️ Dropping old tables...")
        cursor.execute("DROP TABLE work_items")
        cursor.execute("DROP TABLE tasks")
        
        # Rename new tables
        print("🔄 Renaming new tables...")
        cursor.execute("ALTER TABLE work_items_new RENAME TO work_items")
        cursor.execute("ALTER TABLE tasks_new RENAME TO tasks")
        
        # Recreate indexes
        print("📋 Recreating indexes...")
        cursor.execute("CREATE INDEX idx_work_items_project ON work_items(project_id)")
        cursor.execute("CREATE INDEX idx_work_items_parent ON work_items(parent_work_item_id)")
        cursor.execute("CREATE INDEX idx_work_items_status ON work_items(status)")
        cursor.execute("CREATE INDEX idx_work_items_type ON work_items(type)")
        cursor.execute("CREATE INDEX idx_work_items_priority ON work_items(priority)")
        cursor.execute("CREATE INDEX idx_work_items_continuous ON work_items(is_continuous)")
        
        cursor.execute("CREATE INDEX idx_tasks_work_item ON tasks(work_item_id)")
        cursor.execute("CREATE INDEX idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX idx_tasks_type ON tasks(type)")
        cursor.execute("CREATE INDEX idx_tasks_priority ON tasks(priority)")
        
        # Commit changes
        conn.commit()
        
        print("✅ Successfully updated database schema to 6-state workflow system!")
        
        # Verify the changes
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='work_items'")
        new_work_items_schema = cursor.fetchone()[0]
        print(f"\n📋 New work_items schema:\n{new_work_items_schema}")
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
        new_tasks_schema = cursor.fetchone()[0]
        print(f"\n📋 New tasks schema:\n{new_tasks_schema}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = fix_status_constraints()
    if success:
        print("\n🎉 Database schema update completed successfully!")
    else:
        print("\n💥 Database schema update failed!")
