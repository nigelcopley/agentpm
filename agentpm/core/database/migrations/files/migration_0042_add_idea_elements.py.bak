"""
Migration 0042: Add idea_elements table

Adds support for idea elements - components/parts of ideas that can be
broken down into tasks when ideas are converted to work items.

This enables structured breakdown of complex ideas into manageable
components, providing better estimation and planning capabilities.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict


def upgrade(conn: sqlite3.Connection) -> None:
    """Add idea_elements table to support idea component breakdown"""
    
    # Create idea_elements table
    conn.execute("""
        CREATE TABLE idea_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            
            -- Core fields
            title TEXT NOT NULL CHECK(length(title) >= 3 AND length(title) <= 200),
            description TEXT,
            
            -- Element classification
            type TEXT NOT NULL CHECK(type IN (
                'analysis', 'bugfix', 'deployment', 'design', 'documentation',
                'implementation', 'maintenance', 'refactoring', 'research',
                'review', 'testing'
            )),
            
            -- Effort estimation
            effort_hours REAL NOT NULL CHECK(effort_hours >= 0.1 AND effort_hours <= 1000.0),
            
            -- Ordering and completion
            order_index INTEGER NOT NULL CHECK(order_index >= 0),
            is_completed INTEGER DEFAULT 0 CHECK(is_completed IN (0, 1)),
            completed_at TIMESTAMP,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
            
            -- Completion constraint: completed_at requires is_completed=1
            CHECK (
                (is_completed = 1 AND completed_at IS NOT NULL) OR
                (is_completed = 0)
            )
        )
    """)
    
    # Create index for efficient querying by idea_id
    conn.execute("""
        CREATE INDEX idx_idea_elements_idea_id ON idea_elements(idea_id)
    """)
    
    # Create index for ordering elements within an idea
    conn.execute("""
        CREATE INDEX idx_idea_elements_idea_order ON idea_elements(idea_id, order_index)
    """)
    
    # Create trigger to update updated_at timestamp
    conn.execute("""
        CREATE TRIGGER idea_elements_updated_at
        AFTER UPDATE ON idea_elements
        BEGIN
            UPDATE idea_elements 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END
    """)


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove idea_elements table and related objects"""
    
    # Drop trigger
    conn.execute("DROP TRIGGER IF EXISTS idea_elements_updated_at")
    
    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_idea_elements_idea_order")
    conn.execute("DROP INDEX IF EXISTS idx_idea_elements_idea_id")
    
    # Drop table
    conn.execute("DROP TABLE IF EXISTS idea_elements")


def get_migration_info() -> Dict[str, Any]:
    """Get migration metadata"""
    return {
        'version': '0042',
        'name': 'add_idea_elements',
        'description': 'Add idea_elements table for idea component breakdown',
        'upgrade_sql': Path(__file__).read_text(),
        'downgrade_sql': 'DROP TABLE IF EXISTS idea_elements',
        'dependencies': ['0041'],  # Previous migration
        'created_at': '2025-01-20T10:00:00Z'
    }
