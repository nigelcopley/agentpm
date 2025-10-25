#!/usr/bin/env python3
"""
Test script to verify the schema is working correctly.
"""

import sqlite3
import tempfile
from pathlib import Path

# Import the schema function
from agentpm.core.database.utils.schema import initialize_schema

def test_schema():
    """Test that the schema creates the correct constraint."""
    
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Create connection
        conn = sqlite3.connect(db_path)
        
        # Initialize schema
        print("Initializing schema...")
        initialize_schema(conn)
        print("Schema initialized")
        
        # Check the constraint
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contexts'")
        table_sql = cursor.fetchone()
        
        if table_sql:
            print("Contexts table SQL:")
            print(table_sql[0])
            
            # Check if the new context types are in the constraint
            if 'business_pillars_context' in table_sql[0]:
                print("✅ Schema has new context types")
            else:
                print("❌ Schema missing new context types")
        else:
            print("❌ Contexts table not found")
        
        # Try to insert a context with the new type
        try:
            conn.execute("""
                INSERT INTO contexts (project_id, context_type, entity_type, entity_id, context_data)
                VALUES (1, 'business_pillars_context', 'work_item', 1, '{"test": "data"}')
            """)
            conn.commit()
            print("✅ Insert with business_pillars_context succeeded")
        except Exception as e:
            print(f"❌ Insert failed: {e}")
        
    finally:
        # Clean up
        conn.close()
        Path(db_path).unlink()

if __name__ == "__main__":
    test_schema()