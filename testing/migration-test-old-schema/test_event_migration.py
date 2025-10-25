#!/usr/bin/env python3
"""
Test event type migration from old format to new format.
"""

import sqlite3

def test_event_migration():
    """Test migrating event types from old format to new format."""
    
    # Event type mapping from old to new format
    event_type_mapping = {
        'session_start': 'session.started',
        'session_end': 'session.ended',
        'task_start': 'task.started',
        'task_complete': 'task.completed',
        'work_item_start': 'work_item.started',
        'work_item_complete': 'work_item.completed',
        'dependency_added': 'dependency.added',
        'blocker_created': 'blocker.added',
        'error_occurred': 'error.encountered',
        'decision_made': 'decision.made',
        'evidence_added': 'evidence.added',
        'rule_triggered': 'rule.triggered',
        'workflow_transition': 'workflow.transition',
        'agent_action': 'agent.action',
        'gate_execution': 'gate.execution',
        'context_refresh': 'context.refresh'
    }
    
    conn = sqlite3.connect('.aipm/data/aipm.db')
    
    # Get all events from old table
    cursor = conn.execute("SELECT * FROM events")
    events = cursor.fetchall()
    
    print(f"Found {len(events)} events in old events table")
    
    for event in events:
        event_id, project_id, event_type, event_category, event_severity, session_id, timestamp, source, event_data, work_item_id, task_id, created_at = event
        
        # Map old event type to new event type
        new_event_type = event_type_mapping.get(event_type, event_type)
        
        print(f"Migrating event {event_id}: '{event_type}' -> '{new_event_type}'")
        
        # Try to insert into new table
        try:
            conn.execute("""
                INSERT INTO session_events (project_id, event_type, event_category, event_severity, 
                                          session_id, timestamp, source, event_data, work_item_id, task_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, new_event_type, event_category, event_severity, session_id, 
                  timestamp, source, event_data, work_item_id, task_id, created_at))
            print(f"  ✅ Successfully migrated")
        except sqlite3.IntegrityError as e:
            print(f"  ❌ Failed to migrate: {e}")
    
    conn.commit()
    conn.close()
    
    # Check results
    conn = sqlite3.connect('.aipm/data/aipm.db')
    cursor = conn.execute("SELECT COUNT(*) FROM session_events")
    new_count = cursor.fetchone()[0]
    cursor = conn.execute("SELECT COUNT(*) FROM events")
    old_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\nMigration results:")
    print(f"  Old events table: {old_count} records")
    print(f"  New session_events table: {new_count} records")

if __name__ == "__main__":
    test_event_migration()
