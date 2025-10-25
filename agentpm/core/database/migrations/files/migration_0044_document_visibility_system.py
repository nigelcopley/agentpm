"""
Migration 0044: Document Visibility System

Adds visibility, lifecycle, and audit trail support for documents.

This migration adds:
1. Visibility and lifecycle fields to document_references table
2. document_visibility_policies table for policy management
3. document_audit_log table for change tracking
4. Indexes for performance optimization
5. Default visibility policies for common document types

Part of WI-164: Auto-Generate Document File Paths
Task: #1077 - Create Database Schema Migration
"""

import sqlite3
from datetime import datetime

VERSION = "0044"
DESCRIPTION = "Add document visibility, lifecycle, and audit trail system"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply migration changes.

    Changes:
    1. Add visibility/lifecycle columns to document_references
    2. Create document_visibility_policies table
    3. Create document_audit_log table
    4. Create performance indexes
    5. Populate default policies
    """
    print("🔧 Migration 0044: Document Visibility System")
    cursor = conn.cursor()

    # 1. Add columns to document_references
    print("  📋 Adding visibility and lifecycle columns to document_references...")

    # Check existing columns to avoid duplicates
    cursor.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = [
        ("visibility", "TEXT DEFAULT 'private'", "Document visibility level"),
        # Note: 'audience' already exists in the table (column 18)
        ("lifecycle_stage", "TEXT DEFAULT 'draft'", "Document lifecycle stage"),
        ("published_path", "TEXT", "Path where public copy exists"),
        ("published_date", "TIMESTAMP", "When document was published"),
        ("unpublished_date", "TIMESTAMP", "When document was unpublished"),
        ("review_status", "TEXT", "Review status (pending/approved/rejected)"),
        ("reviewer_id", "TEXT", "Who is/was reviewing"),
        ("review_comment", "TEXT", "Reviewer feedback"),
        ("auto_publish", "BOOLEAN DEFAULT 0", "Auto-publish when approved"),
    ]

    for col_name, col_def, description in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE document_references ADD COLUMN {col_name} {col_def}")
                print(f"  ✅ Added column: {col_name} ({description})")
            except sqlite3.OperationalError as e:
                # Column might exist from partial migration
                if "duplicate column" not in str(e).lower():
                    raise
                print(f"  ⚠️  Column {col_name} already exists, skipping")
        else:
            print(f"  ⚠️  Column {col_name} already exists, skipping")

    # 2. Create document_visibility_policies table
    print("  📋 Creating document_visibility_policies table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_visibility_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            default_visibility TEXT NOT NULL DEFAULT 'private',
            default_audience TEXT NOT NULL DEFAULT 'internal',
            requires_review BOOLEAN NOT NULL DEFAULT 0,
            auto_publish_on_approved BOOLEAN NOT NULL DEFAULT 0,
            base_score INTEGER NOT NULL DEFAULT 50,
            force_private BOOLEAN NOT NULL DEFAULT 0,
            force_public BOOLEAN NOT NULL DEFAULT 0,
            description TEXT,
            rationale TEXT,
            auto_publish_trigger TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, doc_type)
        )
    """)
    print("  ✅ Created document_visibility_policies table")

    # 3. Create document_audit_log table
    print("  📋 Creating document_audit_log table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            from_state TEXT,
            to_state TEXT,
            details TEXT,
            comment TEXT,
            FOREIGN KEY (document_id) REFERENCES document_references(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Created document_audit_log table")

    # 4. Create indexes
    print("  📋 Creating indexes...")

    # Check existing indexes
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references'"
    )
    existing_indexes = {row[0] for row in cursor.fetchall()}

    indexes_to_create = [
        ("idx_doc_visibility", "document_references", "visibility", "Visibility filtering"),
        ("idx_doc_lifecycle", "document_references", "lifecycle_stage", "Lifecycle filtering"),
        ("idx_doc_review_status", "document_references", "review_status", "Review status lookup"),
        ("idx_audit_log_document", "document_audit_log", "document_id", "Document audit trail"),
        ("idx_audit_log_timestamp", "document_audit_log", "timestamp DESC", "Temporal audit queries"),
        ("idx_audit_log_action", "document_audit_log", "action", "Action-based queries"),
        ("idx_visibility_policy_lookup", "document_visibility_policies", "category, doc_type", "Policy lookup"),
    ]

    for index_name, table_name, columns, description in indexes_to_create:
        if index_name not in existing_indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {table_name}({columns})
            """)
            print(f"  ✅ Created index: {index_name} ({description})")
        else:
            print(f"  ⚠️  Index {index_name} already exists, skipping")

    # 5. Populate default visibility policies
    print("  📋 Populating default visibility policies...")

    default_policies = [
        # Guides - always public (force_public=1)
        ('guides', 'user_guide', 'public', 'users', 1, 1, 70, 0, 1,
         'User-facing guide - always public after review'),
        ('guides', 'developer_guide', 'public', 'contributors', 1, 1, 70, 0, 1,
         'Developer documentation - always public after review'),
        ('guides', 'admin_guide', 'public', 'users', 1, 1, 65, 0, 0,
         'Administrator guide - public after review'),
        ('guides', 'troubleshooting', 'public', 'users', 1, 1, 65, 0, 0,
         'Troubleshooting guide - public after review'),
        ('guides', 'faq', 'public', 'public', 1, 1, 60, 0, 1,
         'FAQ - always public after review'),

        # Reference - always public (force_public=1)
        ('reference', 'api_doc', 'public', 'public', 1, 1, 80, 0, 1,
         'API documentation - always public after review'),
        ('reference', 'integration_guide', 'public', 'contributors', 1, 1, 70, 0, 1,
         'Integration guide - always public after review'),

        # Planning - always private (force_private=1)
        ('planning', 'requirements', 'private', 'internal', 0, 0, 30, 1, 0,
         'Requirements document - always private'),
        ('planning', 'idea', 'private', 'internal', 0, 0, 20, 1, 0,
         'Initial ideas - always private'),
        ('planning', 'user_story', 'private', 'team', 0, 0, 35, 1, 0,
         'User stories - always private'),
        ('planning', 'use_case', 'private', 'team', 0, 0, 35, 1, 0,
         'Use cases - always private'),

        # Architecture - context-aware (can vary)
        ('architecture', 'adr', 'private', 'team', 1, 0, 50, 0, 0,
         'Architecture Decision Record - context-aware visibility'),
        ('architecture', 'architecture_doc', 'private', 'team', 1, 0, 55, 0, 0,
         'Architecture documentation - context-aware visibility'),
        ('architecture', 'design_doc', 'private', 'team', 1, 0, 50, 0, 0,
         'Design document - context-aware visibility'),
        ('architecture', 'technical_spec', 'private', 'team', 1, 0, 50, 0, 0,
         'Technical specification - context-aware visibility'),

        # Implementation - context-aware
        ('implementation', 'implementation_plan', 'private', 'team', 1, 0, 45, 0, 0,
         'Implementation plan - context-aware visibility'),
        ('implementation', 'refactoring_guide', 'private', 'team', 1, 0, 45, 0, 0,
         'Refactoring guide - context-aware visibility'),
        ('implementation', 'migration_guide', 'restricted', 'contributors', 1, 0, 55, 0, 0,
         'Migration guide - usually restricted after review'),

        # Testing - context-aware
        ('testing', 'test_plan', 'private', 'team', 1, 0, 40, 0, 0,
         'Test plan - context-aware visibility'),
        ('testing', 'test_report', 'restricted', 'team', 1, 0, 50, 0, 0,
         'Test report - usually restricted after review'),
        ('testing', 'coverage_report', 'restricted', 'team', 0, 1, 55, 0, 0,
         'Coverage report - usually restricted, auto-publish'),

        # Operations - context-aware
        ('operations', 'runbook', 'restricted', 'team', 1, 0, 60, 0, 0,
         'Runbook - usually restricted after review'),
        ('operations', 'deployment_guide', 'restricted', 'team', 1, 0, 60, 0, 0,
         'Deployment guide - usually restricted after review'),
        ('operations', 'monitoring_guide', 'restricted', 'team', 1, 0, 55, 0, 0,
         'Monitoring guide - usually restricted after review'),
        ('operations', 'incident_report', 'private', 'team', 1, 0, 45, 0, 0,
         'Incident report - context-aware visibility'),

        # Research - context-aware
        ('research', 'research_report', 'private', 'internal', 1, 0, 40, 0, 0,
         'Research report - context-aware visibility'),
        ('research', 'analysis_report', 'private', 'internal', 1, 0, 40, 0, 0,
         'Analysis report - context-aware visibility'),
        ('research', 'competitive_analysis', 'private', 'internal', 1, 0, 35, 1, 0,
         'Competitive analysis - always private'),
        ('research', 'market_research', 'private', 'internal', 1, 0, 35, 1, 0,
         'Market research - always private'),
        ('research', 'feasibility_study', 'private', 'internal', 1, 0, 40, 0, 0,
         'Feasibility study - context-aware visibility'),

        # Communication - context-aware
        ('communication', 'session_summary', 'restricted', 'team', 0, 0, 45, 0, 0,
         'Session summary - usually restricted'),
        ('communication', 'status_report', 'restricted', 'team', 1, 0, 50, 0, 0,
         'Status report - usually restricted after review'),
        ('communication', 'progress_report', 'restricted', 'team', 1, 0, 50, 0, 0,
         'Progress report - usually restricted after review'),

        # Governance - context-aware
        ('governance', 'quality_gates_spec', 'restricted', 'team', 1, 0, 65, 0, 0,
         'Quality gates specification - usually restricted after review'),
        ('governance', 'stakeholder_analysis', 'private', 'internal', 1, 0, 35, 1, 0,
         'Stakeholder analysis - always private'),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO document_visibility_policies
        (category, doc_type, default_visibility, default_audience, requires_review,
         auto_publish_on_approved, base_score, force_private, force_public, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, default_policies)

    print(f"  ✅ Populated {len(default_policies)} default visibility policies")

    conn.commit()
    print("  ✅ Migration 0044 completed successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration changes.

    SQLite limitation: Can't drop columns directly.
    Would need to recreate document_references table without new columns.
    For safety, we'll drop the new tables and indexes only.

    Note: New columns will remain in document_references but be unused.
    """
    print("🔧 Migration 0044 downgrade: Remove visibility system")
    cursor = conn.cursor()

    # Drop new tables
    print("  📋 Dropping new tables...")
    cursor.execute("DROP TABLE IF EXISTS document_audit_log")
    print("  ✅ Dropped document_audit_log table")

    cursor.execute("DROP TABLE IF EXISTS document_visibility_policies")
    print("  ✅ Dropped document_visibility_policies table")

    # Drop indexes
    print("  📋 Dropping indexes...")
    indexes_to_drop = [
        'idx_doc_visibility',
        'idx_doc_lifecycle',
        'idx_doc_review_status',
        'idx_audit_log_document',
        'idx_audit_log_timestamp',
        'idx_audit_log_action',
        'idx_visibility_policy_lookup',
    ]

    for index_name in indexes_to_drop:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"  ✅ Dropped index: {index_name}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not drop index {index_name}: {e}")

    # Note: Cannot easily drop columns from document_references in SQLite
    # They will remain but be unused after downgrade
    print("  ⚠️  Note: Columns remain in document_references (SQLite limitation)")

    conn.commit()
    print("  ✅ Migration 0044 downgrade completed successfully")
