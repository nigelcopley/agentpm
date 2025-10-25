"""
Migration 0023: Fix event type schema mismatch + add phase indexes

CRITICAL FIXES:
1. Event Type Mismatch: Pydantic EventType has 38 values, database CHECK constraint only allows 9
   - This causes INSERT failures for most event types
   - EventAdapter performs lossy mapping (40 types → 9 generic values)

2. Phase Field Performance: work_items.phase has no index
   - Queries filtering by phase will be O(n) at scale
   - Dashboard phase filtering will degrade with >1000 work items

3. Phase Enum Constraint: No CHECK constraint on work_items.phase
   - Allows typos and invalid phase values
   - Should enforce D1_discovery, P1_plan, etc.

Changes:
- Expand session_events.event_type CHECK constraint to all 38 EventType values
- Add index on work_items.phase
- Add composite index on work_items(phase, status) for common queries
- Add CHECK constraint on work_items.phase (enum validation)

Data Integrity:
- All existing event data preserved (migration is additive)
- All existing work items preserved
- New indexes improve performance without data changes
"""

import sqlite3
from agentpm.core.database.enums import Phase
from agentpm.core.events.models import EventType


def upgrade(conn: sqlite3.Connection) -> None:
    """Expand event types and add phase indexes"""
    print("🔧 Migration 0023: Fix event type mismatch + add phase indexes")

    # Step 1: Fix event type schema mismatch
    _expand_event_type_constraint(conn)

    # Step 2: Add phase indexes for performance
    _add_phase_indexes(conn)

    # Step 3: Add phase enum constraint
    _add_phase_constraint(conn)

    print("✅ Migration 0023 complete")


def _expand_event_type_constraint(conn: sqlite3.Connection) -> None:
    """Expand session_events.event_type CHECK constraint to support all 38 EventType values"""
    print("  📋 Expanding event_type constraint...")

    # Clean up any orphaned tables from previous failed attempts
    conn.execute("DROP TABLE IF EXISTS session_events_new")

    # Get all event type values from Pydantic enum
    event_types = [et.value for et in EventType]

    # Create new table with expanded constraint
    event_type_check = "CHECK(event_type IN ('" + "', '".join(event_types) + "'))"

    conn.execute(f"""
        CREATE TABLE session_events_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            event_type TEXT NOT NULL {event_type_check},
            event_category TEXT NOT NULL CHECK(event_category IN (
                'workflow', 'tool_usage', 'decision', 'reasoning', 'error', 'session_lifecycle'
            )),
            event_severity TEXT NOT NULL CHECK(event_severity IN (
                'debug', 'info', 'warning', 'error', 'critical'
            )),
            session_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            event_data TEXT NOT NULL,
            work_item_id INTEGER,
            task_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)

    # Copy existing data
    conn.execute("""
        INSERT INTO session_events_new
        SELECT * FROM session_events
    """)

    # Drop old table and rename new one
    conn.execute("DROP TABLE session_events")
    conn.execute("ALTER TABLE session_events_new RENAME TO session_events")

    # Recreate indexes
    conn.execute("""
        CREATE INDEX idx_session_events_session
        ON session_events(session_id, timestamp DESC)
    """)
    conn.execute("""
        CREATE INDEX idx_session_events_type
        ON session_events(event_type, timestamp DESC)
    """)
    conn.execute("""
        CREATE INDEX idx_session_events_category
        ON session_events(event_category, timestamp DESC)
    """)
    conn.execute("""
        CREATE INDEX idx_session_events_entity
        ON session_events(work_item_id, task_id, timestamp DESC)
    """)

    print(f"  ✅ Event types expanded: 9 → {len(event_types)} types")


def _add_phase_indexes(conn: sqlite3.Connection) -> None:
    """Add indexes on work_items.phase for query performance"""
    print("  📋 Adding phase indexes...")

    # Add single-column index on phase
    conn.execute("CREATE INDEX idx_work_items_phase ON work_items(phase)")

    # Add composite index on (phase, status) for common queries
    # Example query: SELECT * FROM work_items WHERE phase='I1_implementation' AND status='active'
    conn.execute("CREATE INDEX idx_work_items_phase_status ON work_items(phase, status)")

    print("  ✅ Phase indexes created")


def _add_phase_constraint(conn: sqlite3.Connection) -> None:
    """Add CHECK constraint on work_items.phase to enforce enum values"""
    print("  📋 Adding phase enum constraint...")

    # Get all phase values from enum
    phase_values = [p.value for p in Phase]

    # SQLite doesn't support ALTER TABLE ADD CONSTRAINT for CHECK
    # Instead, we need to recreate the table (like migration_0022 pattern)

    # Create phase check constraint
    phase_check = "CHECK(phase IS NULL OR phase IN ('" + "', '".join(phase_values) + "'))"

    # Check if originated_from_idea_id exists in source table
    cursor = conn.execute("PRAGMA table_info(work_items)")
    columns = [row[1] for row in cursor.fetchall()]
    has_idea_link = 'originated_from_idea_id' in columns

    # Create new table with phase constraint (include idea link if exists)
    conn.execute(f"""
        CREATE TABLE work_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_work_item_id INTEGER,
            {"originated_from_idea_id INTEGER," if has_idea_link else ""}

            -- Work item details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK(type IN (
                'feature', 'enhancement', 'bugfix', 'research', 'analysis', 'planning',
                'refactoring', 'infrastructure', 'maintenance', 'monitoring',
                'documentation', 'security', 'fix_bugs_issues'
            )),

            -- Business context
            business_context TEXT,
            metadata TEXT DEFAULT '{{}}',

            -- Planning
            effort_estimate_hours REAL,
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),

            -- Lifecycle
            status TEXT DEFAULT 'draft' CHECK(status IN (
                'draft', 'ready', 'active', 'review', 'done', 'archived', 'blocked', 'cancelled'
            )),
            phase TEXT {phase_check},
            due_date TIMESTAMP,
            not_before TIMESTAMP,
            is_continuous INTEGER NOT NULL DEFAULT 0 CHECK(is_continuous IN (0, 1)),

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
            {"FOREIGN KEY (originated_from_idea_id) REFERENCES ideas(id) ON DELETE SET NULL" if has_idea_link else ""}
        )
    """)

    # Copy data with explicit column list (handles schema differences)
    if has_idea_link:
        conn.execute("""
            INSERT INTO work_items_new
            SELECT * FROM work_items
        """)
    else:
        # Old schema without idea link - specify columns explicitly
        conn.execute("""
            INSERT INTO work_items_new (
                id, project_id, parent_work_item_id,
                name, description, type,
                business_context, metadata,
                effort_estimate_hours, priority,
                status, phase, due_date, not_before, is_continuous,
                created_at, updated_at
            )
            SELECT
                id, project_id, parent_work_item_id,
                name, description, type,
                business_context, metadata,
                effort_estimate_hours, priority,
                status, phase, due_date, not_before, is_continuous,
                created_at, updated_at
            FROM work_items
        """)

    # Drop old table and rename new one
    conn.execute("DROP TABLE work_items")
    conn.execute("ALTER TABLE work_items_new RENAME TO work_items")

    # Recreate existing indexes (from migration_0022)
    conn.execute("CREATE INDEX idx_work_items_status ON work_items(status)")
    conn.execute("CREATE INDEX idx_work_items_type ON work_items(type)")
    conn.execute("CREATE INDEX idx_work_items_project_id ON work_items(project_id)")

    # Add new phase indexes (already added in _add_phase_indexes, but recreating table removed them)
    conn.execute("CREATE INDEX idx_work_items_phase ON work_items(phase)")
    conn.execute("CREATE INDEX idx_work_items_phase_status ON work_items(phase, status)")

    print(f"  ✅ Phase constraint added ({len(phase_values)} valid values)")


def downgrade(conn: sqlite3.Connection) -> None:
    """Downgrade not supported - this fixes critical bugs"""
    raise NotImplementedError(
        "Downgrade not supported for migration 0023. "
        "This migration fixes critical event type mismatch that causes "
        "INSERT failures. Downgrading would reintroduce the bug."
    )
