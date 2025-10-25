"""
Migration 0043: Fix Document Type Constraint

This migration recreates the document_references table with the correct
document_type constraint that includes the new types and removes deprecated ones.
"""

import sqlite3

VERSION = "0043"
DESCRIPTION = "Fix document_type constraint to include new types and remove deprecated ones"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Recreate document_references table with correct constraint.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Disable foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys=OFF")
    
    # Create backup table
    cursor.execute("""
        CREATE TABLE document_references_backup AS 
        SELECT * FROM document_references
    """)
    
    # Update the backup table with new type names
    cursor.execute("""
        UPDATE document_references_backup 
        SET document_type = 'architecture_doc' 
        WHERE document_type = 'architecture'
    """)
    
    cursor.execute("""
        UPDATE document_references_backup 
        SET document_type = 'design_doc' 
        WHERE document_type = 'design'
    """)
    
    cursor.execute("""
        UPDATE document_references_backup 
        SET document_type = 'technical_spec' 
        WHERE document_type = 'technical_specification'
    """)
    
    # Drop the original table
    cursor.execute("DROP TABLE document_references")
    
    # Recreate the table with updated constraint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "document_references" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT CHECK(document_type IN (
                'idea', 'requirements', 'user_story', 'use_case',
                'architecture_doc', 'design_doc', 'adr', 'technical_spec',
                'implementation_plan', 'refactoring_guide', 'migration_guide', 'integration_guide',
                'test_plan', 'test_report', 'coverage_report', 'validation_report',
                'runbook', 'deployment_guide', 'monitoring_guide', 'incident_report',
                'user_guide', 'admin_guide', 'api_doc', 'developer_guide', 'troubleshooting', 'faq',
                'research_report', 'analysis_report', 'investigation_report', 'assessment_report',
                'feasibility_study', 'competitive_analysis',
                'session_summary', 'status_report', 'progress_report', 'milestone_report', 'retrospective_report',
                'business_pillars', 'market_research', 'stakeholder_analysis', 'quality_gates_spec',
                'specification', 'other'
            )),
            format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),
            title TEXT,
            description TEXT,
            created_by TEXT DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size_bytes INTEGER,
            content_hash TEXT,
            category TEXT,
            document_type_dir TEXT,
            segment_type TEXT,
            component TEXT,
            domain TEXT,
            audience TEXT,
            maturity TEXT,
            priority TEXT,
            tags TEXT,
            phase TEXT,
            work_item_id INTEGER,
            content TEXT,
            filename TEXT,
            storage_mode TEXT DEFAULT 'hybrid',
            content_updated_at DATETIME,
            last_synced_at DATETIME,
            sync_status TEXT DEFAULT 'synced',
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0)
        )
    """)
    
    # Copy data back
    cursor.execute("""
        INSERT INTO document_references 
        SELECT * FROM document_references_backup
    """)
    
    # Drop backup table
    cursor.execute("DROP TABLE document_references_backup")
    
    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys=ON")
    
    print("Recreated document_references table with updated constraint")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Restore original table structure.
    
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
    
    # Create backup table
    cursor.execute("""
        CREATE TABLE document_references_backup AS 
        SELECT * FROM document_references
    """)
    
    # Drop the current table
    cursor.execute("DROP TABLE document_references")
    
    # Recreate with original constraint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "document_references" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT CHECK(document_type IN ('idea', 'requirements', 'refactoring_guide', 'user_story', 'use_case', 'architecture', 'design', 'specification', 'api_doc', 'user_guide', 'admin_guide', 'troubleshooting', 'adr', 'test_plan', 'migration_guide', 'runbook', 'business_pillars', 'market_research', 'competitive_analysis', 'quality_gates_spec', 'stakeholder_analysis', 'technical_specification', 'implementation_plan', 'other')),
            format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),
            title TEXT,
            description TEXT,
            created_by TEXT DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size_bytes INTEGER,
            content_hash TEXT,
            category TEXT,
            document_type_dir TEXT,
            segment_type TEXT,
            component TEXT,
            domain TEXT,
            audience TEXT,
            maturity TEXT,
            priority TEXT,
            tags TEXT,
            phase TEXT,
            work_item_id INTEGER,
            content TEXT,
            filename TEXT,
            storage_mode TEXT DEFAULT 'hybrid',
            content_updated_at DATETIME,
            last_synced_at DATETIME,
            sync_status TEXT DEFAULT 'synced',
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0)
        )
    """)
    
    # Copy data back
    cursor.execute("""
        INSERT INTO document_references 
        SELECT * FROM document_references_backup
    """)
    
    # Drop backup table
    cursor.execute("DROP TABLE document_references_backup")
    
    print("Restored original document_references table structure")
