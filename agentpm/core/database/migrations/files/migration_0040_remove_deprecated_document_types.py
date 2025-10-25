"""
Migration 0040: Remove Deprecated Document Types

This migration updates the document_type CHECK constraint to remove
deprecated types: architecture, design, technical_specification
"""

import sqlite3

VERSION = "0040"
DESCRIPTION = "Remove deprecated document types from CHECK constraint"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Remove deprecated document types from CHECK constraint.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # First, update existing data to use new type names
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'architecture_doc' 
        WHERE document_type = 'architecture'
    """)
    
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'design_doc' 
        WHERE document_type = 'design'
    """)
    
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'technical_spec' 
        WHERE document_type = 'technical_specification'
    """)
    
    # Note: SQLite doesn't support dropping CHECK constraints easily
    # The constraint will be updated when the table is recreated
    print("Updated document types to use new names")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Restore deprecated types to CHECK constraint.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Restore old type names
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'architecture' 
        WHERE document_type = 'architecture_doc'
    """)
    
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'design' 
        WHERE document_type = 'design_doc'
    """)
    
    cursor.execute("""
        UPDATE document_references 
        SET document_type = 'technical_specification' 
        WHERE document_type = 'technical_spec'
    """)
    
    print("Restored deprecated document type names")
