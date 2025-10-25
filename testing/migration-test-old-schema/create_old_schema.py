#!/usr/bin/env python3
"""
Create old schema with events table to test migration.
"""

import sqlite3
from pathlib import Path

def create_old_schema():
    """Create the old schema with events table instead of session_events."""
    db_path = Path(".aipm/data/aipm.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Create schema_migrations table first
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rollback_at TIMESTAMP DEFAULT NULL,
            rollback_reason TEXT DEFAULT NULL,
            applied_by TEXT DEFAULT NULL
        )
    """)
    
    # Create the old events table (with limited event types)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            event_type TEXT NOT NULL CHECK(event_type IN (
                'workflow_transition', 'agent_action', 'gate_execution',
                'context_refresh', 'dependency_added', 'blocker_created',
                'session_start', 'session_end', 'task_start', 'task_complete',
                'work_item_start', 'work_item_complete', 'error_occurred',
                'decision_made', 'evidence_added', 'rule_triggered'
            )),
            event_category TEXT NOT NULL CHECK(event_category IN (
                'workflow', 'tool_usage', 'error', 'decision', 'evidence',
                'session', 'task', 'work_item', 'agent', 'context'
            )),
            event_severity TEXT NOT NULL DEFAULT 'info' CHECK(event_severity IN (
                'debug', 'info', 'warning', 'error', 'critical'
            )),
            session_id INTEGER,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            event_data TEXT NOT NULL,
            work_item_id INTEGER,
            task_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    
    # Create a basic projects table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            tech_stack TEXT DEFAULT '[]',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert some test data
    conn.execute("INSERT OR IGNORE INTO projects (id, name, path) VALUES (1, 'Test Project', '/test')")
    conn.execute("""
        INSERT OR IGNORE INTO events (project_id, event_type, event_category, event_severity, 
                                     session_id, timestamp, source, event_data) 
        VALUES (1, 'session_start', 'session', 'info', 1, datetime('now'), 'test', '{"test": true}')
    """)
    
    # Insert old migration record
    conn.execute("""
        INSERT OR IGNORE INTO schema_migrations (version, description, applied_at) 
        VALUES ('0001_old', 'Old schema with events table', datetime('now'))
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Old schema created with events table")
    print("   - events table with limited event types")
    print("   - projects table")
    print("   - schema_migrations table")
    print("   - Test data inserted")

if __name__ == "__main__":
    create_old_schema()
