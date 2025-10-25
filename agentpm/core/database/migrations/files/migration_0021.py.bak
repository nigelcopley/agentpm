"""
Migration 0021: Continuous work item support

Changes:
- Extend WorkItemType enum CHECK constraint with new continuous types
- Add is_continuous flag to work_items table (BOOLEAN)
- Backfill continuous flag based on new WorkItemType values
"""

import sqlite3

from agentpm.core.database.enums import WorkItemStatus, WorkItemType
from agentpm.core.database.utils.enum_helpers import generate_check_constraint


def upgrade(conn: sqlite3.Connection) -> None:
    print("🚀 Migration 0021: Adding continuous work item support")
    conn.execute("PRAGMA foreign_keys = OFF")

    _upgrade_work_items_table(conn)

    conn.execute("PRAGMA foreign_keys = ON")
    print("✅ Migration 0021 complete")


def _upgrade_work_items_table(conn: sqlite3.Connection) -> None:
    """Recreate work_items table with is_continuous flag and updated enum constraints."""
    type_constraint = generate_check_constraint(WorkItemType, 'type')
    status_constraint = generate_check_constraint(WorkItemStatus, 'status')
    continuous_values = ", ".join(f"'{wt.value}'" for wt in WorkItemType.continuous_types())

    conn.execute(f"""
        CREATE TABLE work_items_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_work_item_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL {type_constraint},
            business_context TEXT,
            metadata TEXT DEFAULT '{{}}',
            effort_estimate_hours REAL,
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            status TEXT DEFAULT 'proposed' {status_constraint},
            is_continuous INTEGER NOT NULL DEFAULT 0 CHECK(is_continuous IN (0, 1)),
            phase TEXT,
            due_date TIMESTAMP,
            not_before TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)

    conn.execute(f"""
        INSERT INTO work_items_new (
            id, project_id, parent_work_item_id, name, description, type,
            business_context, metadata, effort_estimate_hours, priority, status,
            is_continuous, phase, due_date, not_before, created_at, updated_at
        )
        SELECT
            id, project_id, parent_work_item_id, name, description, type,
            business_context, metadata, effort_estimate_hours, priority, status,
            CASE
                WHEN type IN ({continuous_values}) THEN 1
                ELSE 0
            END AS is_continuous,
            phase, due_date, not_before, created_at, updated_at
        FROM work_items
    """)

    conn.execute("DROP TABLE work_items")
    conn.execute("ALTER TABLE work_items_new RENAME TO work_items")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_parent ON work_items(parent_work_item_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_type ON work_items(type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_priority ON work_items(priority)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_continuous ON work_items(is_continuous)")
