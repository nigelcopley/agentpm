"""
Migration 0024: Add phase field to tasks table

PURPOSE:
Enable phase-based task filtering and validation without requiring JOINs to work_items table.

RATIONALE:
- Currently: task.phase requires JOIN to work_items (slow at scale)
- Future: Direct phase queries on tasks (fast with index)
- Use case: "Show all tasks in I1_IMPLEMENTATION phase" (common dashboard query)

Changes:
- Add tasks.phase column (TEXT, nullable)
- Populate from parent work_items.phase
- Add trigger to keep task.phase in sync with work_item.phase
- Add index on tasks.phase for query performance

Data Integrity:
- Tasks without work items: Not possible (FK constraint)
- Tasks with NULL phase: Allowed (work item may not have phase yet)
- Phase values: Same as work_items (D1_discovery, P1_plan, etc.)
"""

import sqlite3
from agentpm.core.database.enums import Phase


def upgrade(conn: sqlite3.Connection) -> None:
    """Add phase field to tasks with sync trigger"""
    print("🔧 Migration 0024: Add phase field to tasks table")

    # Step 1: Add phase column to tasks
    _add_phase_column(conn)

    # Step 2: Populate from work_items.phase
    _populate_phase_from_work_items(conn)

    # Step 3: Create trigger to keep in sync
    _create_phase_sync_trigger(conn)

    # Step 4: Add index for performance
    _add_phase_index(conn)

    print("✅ Migration 0024 complete")


def _add_phase_column(conn: sqlite3.Connection) -> None:
    """Add phase column to tasks table"""
    print("  📋 Adding phase column to tasks...")

    # Get all phase values for CHECK constraint
    phase_values = [p.value for p in Phase]
    phase_check = "CHECK(phase IS NULL OR phase IN ('" + "', '".join(phase_values) + "'))"

    # SQLite ALTER TABLE limitations require table recreation
    # Get current tasks schema
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
    current_schema = cursor.fetchone()[0]

    # Create new table with phase column
    conn.execute(f"""
        CREATE TABLE tasks_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,

            -- Task details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'implementation' CHECK(type IN (
                'design', 'implementation', 'testing', 'bugfix', 'refactoring',
                'documentation', 'deployment', 'review', 'analysis', 'research',
                'maintenance', 'optimization', 'integration', 'training', 'meeting',
                'planning', 'dependency', 'blocker', 'simple', 'other'
            )),

            -- Quality gate tracking
            quality_metadata TEXT,

            -- Planning
            effort_hours REAL CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8)),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            due_date TIMESTAMP,

            -- Assignment
            assigned_to TEXT,

            -- Lifecycle
            status TEXT DEFAULT 'draft' CHECK(status IN (
                'draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled'
            )),
            blocked_reason TEXT,

            -- NEW: Phase field (from work_item)
            phase TEXT {phase_check},

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,

            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)

    # Copy all existing data
    conn.execute("""
        INSERT INTO tasks_new (
            id, work_item_id, name, description, type, quality_metadata,
            effort_hours, priority, due_date, assigned_to, status, blocked_reason,
            created_at, updated_at, started_at, completed_at
        )
        SELECT
            id, work_item_id, name, description, type, quality_metadata,
            effort_hours, priority, due_date, assigned_to, status, blocked_reason,
            created_at, updated_at, started_at, completed_at
        FROM tasks
    """)

    # Drop old table and rename
    conn.execute("DROP TABLE tasks")
    conn.execute("ALTER TABLE tasks_new RENAME TO tasks")

    # Recreate existing indexes (from migration_0022)
    conn.execute("CREATE INDEX idx_tasks_status ON tasks(status)")
    conn.execute("CREATE INDEX idx_tasks_blocked ON tasks(status) WHERE status = 'blocked'")
    conn.execute("CREATE INDEX idx_tasks_work_item_id ON tasks(work_item_id)")

    # Recreate existing triggers (from migration_0022)
    _recreate_task_triggers(conn)

    print("  ✅ Phase column added to tasks")


def _recreate_task_triggers(conn: sqlite3.Connection) -> None:
    """Recreate task triggers (needed after table recreation)"""
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

    print("  ✅ Task triggers recreated")


def _populate_phase_from_work_items(conn: sqlite3.Connection) -> None:
    """Populate task.phase from parent work_item.phase"""
    print("  📋 Populating phase from work items...")

    conn.execute("""
        UPDATE tasks
        SET phase = (
            SELECT work_items.phase
            FROM work_items
            WHERE work_items.id = tasks.work_item_id
        )
    """)

    # Count populated
    cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE phase IS NOT NULL")
    count = cursor.fetchone()[0]

    print(f"  ✅ Phase populated for {count} tasks")


def _create_phase_sync_trigger(conn: sqlite3.Connection) -> None:
    """Create trigger to keep task.phase in sync with work_item.phase"""
    print("  🔧 Creating phase sync trigger...")

    # Trigger: Update task.phase when work_item.phase changes
    conn.execute("""
        CREATE TRIGGER trigger_sync_task_phase_from_work_item
        AFTER UPDATE OF phase ON work_items
        BEGIN
            UPDATE tasks
            SET phase = NEW.phase
            WHERE work_item_id = NEW.id;
        END
    """)

    print("  ✅ Phase sync trigger created")


def _add_phase_index(conn: sqlite3.Connection) -> None:
    """Add index on tasks.phase for query performance"""
    print("  📋 Adding phase index...")

    conn.execute("CREATE INDEX idx_tasks_phase ON tasks(phase)")

    # Also add composite index for common queries
    # Example: SELECT * FROM tasks WHERE phase='I1_implementation' AND status='active'
    conn.execute("CREATE INDEX idx_tasks_phase_status ON tasks(phase, status)")

    print("  ✅ Phase indexes created")


def downgrade(conn: sqlite3.Connection) -> None:
    """Downgrade not supported - this is a schema enhancement"""
    raise NotImplementedError(
        "Downgrade not supported for migration 0024. "
        "This migration adds phase field to tasks for query performance. "
        "Downgrading would remove valuable query capability."
    )
