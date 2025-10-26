#!/usr/bin/env python3
"""
Document Visibility Migration Script

Auto-assigns visibility_scope to existing documents based on path and type.

Work Item: #164 - Auto-Generate Document File Paths
Task: #1084 - Create Document Migration Script

Migration Logic:
  1. Path-based assignment:
     - .agentpm/docs/* → 'private'
     - docs/* → 'public'

  2. Type-based override (force private regardless of path):
     - testing types (test_plan, test_report, coverage_report)
     - research types (analysis_report, competitive_analysis, market_research)
     - planning types (idea, requirements)

  3. Published state:
     - docs/* → set published_date to created_at
     - .agentpm/docs/* → published_date remains NULL

Safety Features:
  - Dry-run mode (default)
  - Transaction safety with rollback
  - Detailed logging
  - Validation after migration
  - Statistics reporting

Usage:
  # Preview migration (dry-run)
  python migrate_document_visibility.py --dry-run

  # Execute migration
  python migrate_document_visibility.py --execute

  # As CLI command
  apm document migrate-visibility --dry-run
  apm document migrate-visibility --execute
"""

import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DocumentVisibilityUpdate:
    """Represents a visibility update for a document."""
    doc_id: int
    current_path: str
    document_type: Optional[str]
    old_visibility: Optional[str]
    new_visibility: str
    set_published: bool
    reason: str


# Document types that should ALWAYS be private (type-based override)
FORCE_PRIVATE_TYPES = {
    # Testing
    'test_plan',
    'test_report',
    'coverage_report',

    # Research & Analysis (contains sensitive internal data)
    'analysis_report',
    'competitive_analysis',
    'market_research',
    'feasibility_study',

    # Planning (internal decision-making)
    'idea',
    'requirements',
    'stakeholder_analysis',
}


def analyze_documents(db_path: Path) -> Tuple[List[DocumentVisibilityUpdate], Dict[str, int]]:
    """
    Analyze all documents and determine visibility updates needed.

    Args:
        db_path: Path to SQLite database

    Returns:
        Tuple of (updates_list, statistics_dict)
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all documents
    cursor.execute("""
        SELECT id, file_path, document_type, visibility, created_at, published_date
        FROM document_references
        ORDER BY id
    """)

    documents = cursor.fetchall()
    conn.close()

    updates: List[DocumentVisibilityUpdate] = []
    stats = {
        'total': len(documents),
        'needs_update': 0,
        'already_correct': 0,
        'private_by_path': 0,
        'public_by_path': 0,
        'private_by_type': 0,
        'will_set_published': 0,
    }

    for doc in documents:
        doc_id = doc['id']
        file_path = doc['file_path']
        document_type = doc['document_type']
        current_visibility = doc['visibility']
        published_date = doc['published_date']

        # Determine new visibility
        new_visibility, reason, set_published = _determine_visibility(
            file_path, document_type, published_date
        )

        # Track statistics
        if new_visibility == current_visibility and (not set_published or published_date):
            stats['already_correct'] += 1
        else:
            stats['needs_update'] += 1
            updates.append(DocumentVisibilityUpdate(
                doc_id=doc_id,
                current_path=file_path,
                document_type=document_type,
                old_visibility=current_visibility,
                new_visibility=new_visibility,
                set_published=set_published,
                reason=reason
            ))

            # Track reason statistics
            if 'type override' in reason:
                stats['private_by_type'] += 1
            elif '.agentpm/docs/' in file_path:
                stats['private_by_path'] += 1
            elif 'docs/' in file_path:
                stats['public_by_path'] += 1

            if set_published:
                stats['will_set_published'] += 1

    return updates, stats


def _determine_visibility(
    file_path: str,
    document_type: Optional[str],
    published_date: Optional[str]
) -> Tuple[str, str, bool]:
    """
    Determine visibility for a document.

    Args:
        file_path: Document file path
        document_type: Document type (may be None)
        published_date: Current published date (may be None)

    Returns:
        Tuple of (visibility, reason, set_published_date)
    """
    set_published = False

    # Type-based override (HIGHEST PRIORITY)
    if document_type and document_type in FORCE_PRIVATE_TYPES:
        return 'private', f'type override ({document_type})', False

    # Path-based assignment
    if file_path.startswith('.agentpm/docs/'):
        return 'private', 'path (.agentpm/docs/)', False

    if file_path.startswith('docs/'):
        # Public documents should have published_date set
        set_published = (published_date is None)
        return 'public', 'path (docs/)', set_published

    # Fallback: treat as private (safety default)
    return 'private', 'fallback (unknown path)', False


def migrate_document_visibility(db_path: Path, dry_run: bool = True) -> bool:
    """
    Migrate document visibility settings.

    Args:
        db_path: Path to SQLite database
        dry_run: If True, only analyze and report (no changes)

    Returns:
        True if successful, False otherwise
    """
    print(f"{'=' * 80}")
    print(f"Document Visibility Migration")
    print(f"{'=' * 80}")
    print(f"Database: {db_path}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE (applying changes)'}")
    print()

    # Validate database exists
    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        return False

    # Analyze documents
    print("📊 Analyzing documents...")
    try:
        updates, stats = analyze_documents(db_path)
    except Exception as e:
        print(f"❌ Error analyzing documents: {e}")
        return False

    # Display statistics
    print()
    print(f"{'─' * 80}")
    print(f"Analysis Complete")
    print(f"{'─' * 80}")
    print(f"Total documents:           {stats['total']}")
    print(f"Already correct:           {stats['already_correct']}")
    print(f"Needs update:              {stats['needs_update']}")
    print()
    print(f"Update breakdown:")
    print(f"  - Private (path-based):  {stats['private_by_path']} (.agentpm/docs/)")
    print(f"  - Public (path-based):   {stats['public_by_path']} (docs/)")
    print(f"  - Private (type-based):  {stats['private_by_type']} (internal types)")
    print(f"  - Will set published:    {stats['will_set_published']}")
    print(f"{'─' * 80}")
    print()

    if not updates:
        print("✅ All documents already have correct visibility settings!")
        return True

    # Display sample updates (first 20)
    print(f"📋 Sample Updates (showing first {min(20, len(updates))} of {len(updates)}):")
    print()
    for i, update in enumerate(updates[:20], 1):
        print(f"{i:3}. ID {update.doc_id:4} | {update.old_visibility or 'NULL':9} → {update.new_visibility:7} | {update.current_path}")
        print(f"     Reason: {update.reason}")
        if update.set_published:
            print(f"     + Will set published_date")
        print()

    if len(updates) > 20:
        print(f"     ... and {len(updates) - 20} more updates")
        print()

    # Dry-run mode: stop here
    if dry_run:
        print("🔍 DRY RUN complete - no changes made")
        print()
        print("To execute migration, run with --execute flag:")
        print("  python migrate_document_visibility.py --execute")
        print("  OR")
        print("  apm document migrate-visibility --execute")
        return True

    # Execute mode: apply updates
    print(f"{'─' * 80}")
    print(f"Applying Updates...")
    print(f"{'─' * 80}")
    print()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        success_count = 0
        error_count = 0

        for update in updates:
            try:
                if update.set_published:
                    # Get created_at timestamp for published_date
                    cursor.execute(
                        "SELECT created_at FROM document_references WHERE id = ?",
                        (update.doc_id,)
                    )
                    row = cursor.fetchone()
                    created_at = row[0] if row else None

                    # Update with published_date
                    cursor.execute("""
                        UPDATE document_references
                        SET visibility = ?,
                            published_date = ?
                        WHERE id = ?
                    """, (update.new_visibility, created_at, update.doc_id))
                else:
                    # Update visibility only
                    cursor.execute("""
                        UPDATE document_references
                        SET visibility = ?
                        WHERE id = ?
                    """, (update.new_visibility, update.doc_id))

                success_count += 1

            except Exception as e:
                print(f"❌ Error updating document {update.doc_id}: {e}")
                error_count += 1

        if error_count > 0:
            print(f"⚠️  Errors encountered: {error_count}")
            print("Rolling back transaction...")
            conn.rollback()
            conn.close()
            return False

        # Commit transaction
        conn.commit()
        conn.close()

        print(f"✅ Successfully updated {success_count} documents")
        print()

        # Validate migration
        print(f"{'─' * 80}")
        print(f"Validating Migration...")
        print(f"{'─' * 80}")
        validation_success = validate_migration(db_path)

        if validation_success:
            print("✅ Validation passed - migration completed successfully!")
            return True
        else:
            print("⚠️  Validation failed - please review results")
            return False

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


def validate_migration(db_path: Path) -> bool:
    """
    Validate migration results.

    Args:
        db_path: Path to SQLite database

    Returns:
        True if validation passes, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check 1: All documents have visibility set
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM document_references
            WHERE visibility IS NULL
        """)
        null_visibility_count = cursor.fetchone()['count']

        if null_visibility_count > 0:
            print(f"⚠️  Found {null_visibility_count} documents with NULL visibility")
            return False
        else:
            print(f"✓ All documents have visibility set")

        # Check 2: Private documents should NOT have published_date
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM document_references
            WHERE visibility = 'private'
            AND published_date IS NOT NULL
        """)
        private_published_count = cursor.fetchone()['count']

        if private_published_count > 0:
            print(f"⚠️  Found {private_published_count} private documents with published_date set")
            # This is a warning, not a failure

        # Check 3: Public docs/ documents should have published_date
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM document_references
            WHERE visibility = 'public'
            AND file_path LIKE 'docs/%'
            AND published_date IS NULL
        """)
        public_unpublished_count = cursor.fetchone()['count']

        if public_unpublished_count > 0:
            print(f"⚠️  Found {public_unpublished_count} public docs/ documents without published_date")
            # This is a warning, not a failure
        else:
            print(f"✓ All public docs/ documents have published_date set")

        # Check 4: Type-based overrides respected
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM document_references
            WHERE document_type IN ({','.join('?' * len(FORCE_PRIVATE_TYPES))})
            AND visibility != 'private'
        """, list(FORCE_PRIVATE_TYPES))
        type_override_violations = cursor.fetchone()['count']

        if type_override_violations > 0:
            print(f"❌ Found {type_override_violations} documents with forced-private types that are not private!")
            conn.close()
            return False
        else:
            print(f"✓ All forced-private document types are correctly private")

        # Display final statistics
        cursor.execute("""
            SELECT
                visibility,
                COUNT(*) as count
            FROM document_references
            GROUP BY visibility
            ORDER BY visibility
        """)

        print()
        print("Final visibility distribution:")
        for row in cursor.fetchall():
            visibility = row['visibility'] or 'NULL'
            count = row['count']
            print(f"  {visibility:10} : {count:4} documents")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    """Main entry point for standalone script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate document visibility settings based on path and type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview migration (default)
  python migrate_document_visibility.py --dry-run

  # Execute migration
  python migrate_document_visibility.py --execute

  # Specify custom database
  python migrate_document_visibility.py --execute --db-path /path/to/agentpm.db

Migration Logic:
  Path-based:
    .agentpm/docs/* → private
    docs/*          → public

  Type-based (override):
    Internal types (testing, analysis, planning) → private (always)

  Published state:
    Public docs/ → published_date = created_at
    Private      → published_date = NULL
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Preview migration without making changes (default if neither flag specified)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        default=False,
        help='Execute migration and apply changes'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        default=None,
        help='Path to database (default: .agentpm/data/agentpm.db in current directory)'
    )

    args = parser.parse_args()

    # Determine mode
    if args.execute:
        dry_run = False
    else:
        # Default to dry-run if neither specified
        dry_run = True

    # Determine database path
    if args.db_path:
        db_path = args.db_path
    else:
        db_path = Path.cwd() / '.agentpm' / 'data' / 'agentpm.db'

    # Run migration
    success = migrate_document_visibility(db_path, dry_run=dry_run)

    print()
    if success:
        print("✅ Migration completed successfully!")
        return 0
    else:
        print("❌ Migration failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
