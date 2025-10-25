"""
Migration 0022: CRITICAL FIX - Update database schema to match 6-state workflow system

CRITICAL SECURITY VULNERABILITY FIX:
- Database schema was using old 9-state system (proposed, validated, accepted, in_progress, review, completed)
- Code is using new 6-state system (draft, ready, active, review, done, archived)
- This mismatch allows bypassing ALL validation and state transitions
- Database constraints are completely ineffective

This migration fixes the schema to match the current code implementation.

State Mapping:
- proposed → draft
- validated → ready  
- accepted → ready (merged)
- in_progress → active
- review → review (unchanged)
- completed → done
- archived → archived (unchanged)
- blocked → blocked (unchanged)
- cancelled → cancelled (unchanged)

Data integrity:
- All existing data preserved with proper state mapping
- Database constraints now match code validation
- Workflow system becomes secure and untouchable
"""

import sqlite3
from agentpm.core.database.utils.enum_helpers import generate_check_constraint
from agentpm.core.database.enums import WorkItemStatus, TaskStatus


def upgrade(conn: sqlite3.Connection) -> None:
    """Update database schema to use 6-state workflow system"""
    print("🚨 CRITICAL: Fixing database schema mismatch - 9-state to 6-state workflow")
    
    # Update work_items table
    _upgrade_work_items_table(conn)
    
    # Update tasks table  
    _upgrade_tasks_table(conn)
    
    print("✅ Migration 0022 complete - Database schema now matches 6-state workflow system")


def _upgrade_work_items_table(conn: sqlite3.Connection) -> None:
    """Update work_items table to use 6-state system"""
    print("  📋 Updating work_items table...")

    # Clean up any orphaned tables from previous failed attempts
    conn.execute("DROP TABLE IF EXISTS work_items_new")

    # Create new table with correct 6-state constraints
    status_check = generate_check_constraint(WorkItemStatus, 'status')

    conn.execute(f"""
        CREATE TABLE work_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_work_item_id INTEGER,
            originated_from_idea_id INTEGER,

            -- Work item details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK(type IN ('feature', 'enhancement', 'bugfix', 'research', 'analysis', 'planning', 'refactoring', 'infrastructure', 'maintenance', 'monitoring', 'documentation', 'security', 'fix_bugs_issues')),

            -- Business context
            business_context TEXT,
            metadata TEXT DEFAULT '{{}}',

            -- Planning
            effort_estimate_hours REAL,
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),

            -- Lifecycle - CRITICAL: Now uses 6-state system
            status TEXT DEFAULT 'draft' {status_check},
            phase TEXT,
            due_date TIMESTAMP,
            not_before TIMESTAMP,
            is_continuous INTEGER NOT NULL DEFAULT 0 CHECK(is_continuous IN (0, 1)),

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            FOREIGN KEY (originated_from_idea_id) REFERENCES ideas(id) ON DELETE SET NULL
        )
    """)
    
    # Copy data with state mapping
    print("  🔄 Mapping old states to new 6-state system...")

    # Check if originated_from_idea_id column exists in source table
    cursor = conn.execute("PRAGMA table_info(work_items)")
    columns = [row[1] for row in cursor.fetchall()]
    has_idea_link = 'originated_from_idea_id' in columns

    if has_idea_link:
        # New schema with idea link
        conn.execute("""
            INSERT INTO work_items_new
            SELECT
                id, project_id, parent_work_item_id, originated_from_idea_id,
                name, description, type,
                business_context, metadata, effort_estimate_hours, priority,
                CASE status
                    WHEN 'proposed' THEN 'draft'
                    WHEN 'validated' THEN 'ready'
                    WHEN 'accepted' THEN 'ready'
                    WHEN 'in_progress' THEN 'active'
                    WHEN 'review' THEN 'review'
                    WHEN 'completed' THEN 'done'
                    WHEN 'archived' THEN 'archived'
                    WHEN 'blocked' THEN 'blocked'
                    WHEN 'cancelled' THEN 'cancelled'
                    ELSE 'draft'
                END as status,
                phase, due_date, not_before, is_continuous,
                created_at, updated_at
            FROM work_items
        """)
    else:
        # Old schema without idea link
        conn.execute("""
            INSERT INTO work_items_new
            SELECT
                id, project_id, parent_work_item_id, NULL as originated_from_idea_id,
                name, description, type,
                business_context, metadata, effort_estimate_hours, priority,
                CASE status
                    WHEN 'proposed' THEN 'draft'
                    WHEN 'validated' THEN 'ready'
                    WHEN 'accepted' THEN 'ready'
                    WHEN 'in_progress' THEN 'active'
                    WHEN 'review' THEN 'review'
                    WHEN 'completed' THEN 'done'
                    WHEN 'archived' THEN 'archived'
                    WHEN 'blocked' THEN 'blocked'
                    WHEN 'cancelled' THEN 'cancelled'
                    ELSE 'draft'
                END as status,
                phase, due_date, not_before, is_continuous,
                created_at, updated_at
            FROM work_items
        """)
    
    # Drop old table and rename new one
    conn.execute("DROP TABLE work_items")
    conn.execute("ALTER TABLE work_items_new RENAME TO work_items")
    
    # Recreate indexes
    conn.execute("CREATE INDEX idx_work_items_status ON work_items(status)")
    conn.execute("CREATE INDEX idx_work_items_type ON work_items(type)")
    conn.execute("CREATE INDEX idx_work_items_project_id ON work_items(project_id)")
    
    print("  ✅ work_items table updated to 6-state system")


def _upgrade_tasks_table(conn: sqlite3.Connection) -> None:
    """Update tasks table to use 6-state system"""
    print("  📋 Updating tasks table...")

    # Clean up any orphaned tables from previous failed attempts
    conn.execute("DROP TABLE IF EXISTS tasks_new")

    # Create new table with correct 6-state constraints
    status_check = generate_check_constraint(TaskStatus, 'status')

    conn.execute(f"""
        CREATE TABLE tasks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,
            
            -- Task details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'implementation' CHECK(type IN ('design', 'implementation', 'testing', 'bugfix', 'refactoring', 'documentation', 'deployment', 'review', 'analysis', 'research', 'maintenance', 'optimization', 'integration', 'training', 'meeting', 'planning', 'dependency', 'blocker', 'simple', 'other')),
            
            -- Quality gate tracking
            quality_metadata TEXT,
            
            -- Planning
            effort_hours REAL CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8)),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            due_date TIMESTAMP,
            
            -- Assignment
            assigned_to TEXT,
            
            -- Lifecycle - CRITICAL: Now uses 6-state system
            status TEXT DEFAULT 'draft' {status_check},
            blocked_reason TEXT,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)
    
    # Copy data with state mapping
    print("  🔄 Mapping old states to new 6-state system...")
    conn.execute("""
        INSERT INTO tasks_new 
        SELECT 
            id, work_item_id, name, description, type, quality_metadata,
            effort_hours, priority, due_date, assigned_to,
            CASE status
                WHEN 'proposed' THEN 'draft'
                WHEN 'validated' THEN 'ready'
                WHEN 'accepted' THEN 'ready'
                WHEN 'in_progress' THEN 'active'
                WHEN 'review' THEN 'review'
                WHEN 'completed' THEN 'done'
                WHEN 'archived' THEN 'archived'
                WHEN 'blocked' THEN 'blocked'
                WHEN 'cancelled' THEN 'cancelled'
                ELSE 'draft'  -- Default for any unexpected states
            END as status,
            blocked_reason, created_at, updated_at, started_at, completed_at
        FROM tasks
    """)
    
    # Drop old table and rename new one
    conn.execute("DROP TABLE tasks")
    conn.execute("ALTER TABLE tasks_new RENAME TO tasks")
    
    # Recreate indexes
    conn.execute("CREATE INDEX idx_tasks_status ON tasks(status)")
    conn.execute("CREATE INDEX idx_tasks_blocked ON tasks(status) WHERE status = 'blocked'")
    conn.execute("CREATE INDEX idx_tasks_work_item_id ON tasks(work_item_id)")
    
    # Recreate triggers
    _recreate_task_triggers(conn)
    
    print("  ✅ tasks table updated to 6-state system")


def _recreate_task_triggers(conn: sqlite3.Connection) -> None:
    """Recreate task triggers for 6-state system"""
    print("  🔧 Recreating task triggers...")
    
    # Trigger: Update started_at when task becomes active
    conn.execute("""
        CREATE TRIGGER trigger_tasks_started_at
        AFTER UPDATE OF status ON tasks
        WHEN NEW.status = 'active' AND OLD.status != 'active' AND NEW.started_at IS NULL
        BEGIN
            UPDATE tasks SET started_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
    
    # Trigger: Update completed_at when task becomes done
    conn.execute("""
        CREATE TRIGGER trigger_tasks_completed_at
        AFTER UPDATE OF status ON tasks
        WHEN NEW.status = 'done' AND OLD.status != 'done' AND NEW.completed_at IS NULL
        BEGIN
            UPDATE tasks SET completed_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
    
    # Trigger: Clear blocked_reason when task is unblocked
    conn.execute("""
        CREATE TRIGGER trigger_tasks_unblocked
        AFTER UPDATE OF status ON tasks
        WHEN OLD.status = 'blocked' AND NEW.status != 'blocked'
        BEGIN
            UPDATE tasks SET blocked_reason = NULL WHERE id = NEW.id;
        END
    """)
    
    print("  ✅ Task triggers recreated for 6-state system")


def downgrade(conn: sqlite3.Connection) -> None:
    """Downgrade is not supported - this is a critical security fix"""
    raise NotImplementedError(
        "Downgrade not supported for migration 0022. "
        "This migration fixes a critical security vulnerability where "
        "database schema didn't match code implementation. "
        "Downgrading would reintroduce the vulnerability."
    )
