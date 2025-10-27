"""
Migration 0045: Add Review Timestamp Columns

Adds missing review timestamp columns to the document_references table.

This migration adds:
1. reviewer_assigned_at TIMESTAMP column to track when a reviewer was assigned
2. review_completed_at TIMESTAMP column to track when review was completed

Background:
- Migration 0044 added reviewer_id, review_status, and review_comment
- However, reviewer_assigned_at and review_completed_at were missing from the schema
- These columns are needed to track the full review lifecycle timestamps

Part of WI-165: Document Management Fixes
Task: #1109 - Create Migration for Review Timestamp Columns
"""

import sqlite3
from datetime import datetime

VERSION = "0045"
DESCRIPTION = "Add reviewer_assigned_at and review_completed_at columns to document_references"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply migration changes.

    Changes:
    1. Add reviewer_assigned_at column to document_references table
    2. Add review_completed_at column to document_references table
    """
    print("🔧 Migration 0045: Add Review Timestamp Columns")
    cursor = conn.cursor()

    # Check existing columns
    print("  📋 Checking existing columns in document_references...")
    cursor.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = [
        ("reviewer_assigned_at", "When reviewer was assigned"),
        ("review_completed_at", "When review was completed"),
    ]

    added_columns = []

    for column_name, description in columns_to_add:
        if column_name in existing_columns:
            print(f"  ⚠️  Column {column_name} already exists, skipping")
            continue

        # Add column
        print(f"  📋 Adding {column_name} column to document_references...")
        try:
            cursor.execute(f"""
                ALTER TABLE document_references
                ADD COLUMN {column_name} TIMESTAMP
            """)
            print(f"  ✅ Added column: {column_name} ({description})")
            added_columns.append(column_name)

        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  ⚠️  Column {column_name} already exists, skipping")
            else:
                raise

    # Backfill reviewer_assigned_at if it was added
    if "reviewer_assigned_at" in added_columns:
        print("  📋 Backfilling reviewer_assigned_at for existing reviewed documents...")
        cursor.execute("""
            UPDATE document_references
            SET reviewer_assigned_at = updated_at
            WHERE reviewer_id IS NOT NULL
            AND reviewer_assigned_at IS NULL
        """)
        backfilled_count = cursor.rowcount
        if backfilled_count > 0:
            print(f"  ✅ Backfilled {backfilled_count} existing records")
        else:
            print("  ℹ️  No existing records needed backfilling")

    # Backfill review_completed_at if it was added
    if "review_completed_at" in added_columns:
        print("  📋 Backfilling review_completed_at for completed reviews...")
        cursor.execute("""
            UPDATE document_references
            SET review_completed_at = updated_at
            WHERE review_status IN ('approved', 'rejected')
            AND review_completed_at IS NULL
        """)
        backfilled_count = cursor.rowcount
        if backfilled_count > 0:
            print(f"  ✅ Backfilled {backfilled_count} completed reviews")
        else:
            print("  ℹ️  No completed reviews needed backfilling")

    conn.commit()
    print("  ✅ Migration 0045 completed successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration changes.

    SQLite limitation: Can't drop columns directly.
    The columns will remain in the table but be unused after downgrade.

    To fully remove the columns, the table would need to be recreated,
    which is too risky for simple column additions.
    """
    print("🔧 Migration 0045 downgrade: Remove Review Timestamp Columns")
    print("  ⚠️  Note: SQLite does not support dropping columns directly")
    print("  ⚠️  The reviewer_assigned_at and review_completed_at columns will remain but be unused")
    print("  ℹ️  To fully remove, the table would need to be recreated")

    cursor = conn.cursor()

    # Clear reviewer_assigned_at values
    cursor.execute("""
        UPDATE document_references
        SET reviewer_assigned_at = NULL
        WHERE reviewer_assigned_at IS NOT NULL
    """)
    cleared_count_1 = cursor.rowcount
    print(f"  ✅ Cleared {cleared_count_1} reviewer_assigned_at values")

    # Clear review_completed_at values
    cursor.execute("""
        UPDATE document_references
        SET review_completed_at = NULL
        WHERE review_completed_at IS NOT NULL
    """)
    cleared_count_2 = cursor.rowcount
    print(f"  ✅ Cleared {cleared_count_2} review_completed_at values")

    conn.commit()
    print("  ✅ Migration 0045 downgrade completed")
