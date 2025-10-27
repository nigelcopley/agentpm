"""
Migration 0047: Provider Tracking System

Adds database schema to track provider installations, generated files, and integrity hashes.
This enables the `apm provider install/sync/verify` workflow for managing multiple AI code providers.

This migration adds:
1. provider_installations table - Tracks which providers are installed (Claude Code, Cursor, Codex)
2. provider_files table - Tracks generated files with SHA-256 hashes for integrity verification
3. Indexes for performance on common queries

Background:
- APM (Agent Project Manager) now supports multiple AI code providers (Claude Code, Cursor, OpenAI Codex)
- Each provider generates agent files, hooks, settings, and rules
- Need to track what's installed, what files were generated, and verify integrity
- Supports provider sync, verification, and conflict detection

Part of WI-165: Document Management Fixes
Task: #1103 - Database Schema for Provider Tracking
"""

import sqlite3
from datetime import datetime

VERSION = "0047"
DESCRIPTION = "Add provider_installations and provider_files tables for multi-provider tracking"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply migration changes.

    Changes:
    1. Create provider_installations table
    2. Create provider_files table with SHA-256 tracking
    3. Create performance indexes
    4. Validate schema creation
    """
    print("🔧 Migration 0047: Provider Tracking System")
    cursor = conn.cursor()

    # Check if tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_installations'")
    installations_exists = cursor.fetchone() is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_files'")
    files_exists = cursor.fetchone() is not None

    # 1. Create provider_installations table
    if installations_exists:
        print("  ⚠️  Table provider_installations already exists, skipping creation")
    else:
        print("  📋 Creating provider_installations table...")
        cursor.execute("""
            CREATE TABLE provider_installations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                provider_name TEXT NOT NULL CHECK(provider_name IN ('claude-code', 'cursor', 'codex')),
                version TEXT NOT NULL,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                config JSON DEFAULT '{}',
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'deprecated', 'uninstalled')),
                last_synced_at TIMESTAMP,

                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, provider_name)
            )
        """)
        print("  ✅ Created table: provider_installations")

    # 2. Create provider_files table
    if files_exists:
        print("  ⚠️  Table provider_files already exists, skipping creation")
    else:
        print("  📋 Creating provider_files table...")
        cursor.execute("""
            CREATE TABLE provider_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                installation_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL CHECK(file_type IN ('agent', 'hook', 'settings', 'rules', 'config', 'other')),
                content_hash TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_verified_at TIMESTAMP,
                modification_detected INTEGER DEFAULT 0 CHECK(modification_detected IN (0, 1)),

                FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
                UNIQUE(installation_id, file_path)
            )
        """)
        print("  ✅ Created table: provider_files")

    # 3. Create performance indexes
    print("  📋 Creating indexes for provider tracking...")

    # Determine hash column name (content_hash for new, file_hash for old schema)
    cursor.execute("PRAGMA table_info(provider_files)")
    files_columns = {row[1] for row in cursor.fetchall()}
    hash_column = 'content_hash' if 'content_hash' in files_columns else 'file_hash'

    indexes = [
        ("idx_provider_installations_project", "provider_installations", "project_id"),
        ("idx_provider_installations_status", "provider_installations", "status"),
        ("idx_provider_files_installation", "provider_files", "installation_id"),
        ("idx_provider_files_hash", "provider_files", hash_column),
    ]

    created_indexes = []
    for index_name, table_name, column_name in indexes:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
        index_exists = cursor.fetchone() is not None

        if index_exists:
            print(f"  ⚠️  Index {index_name} already exists, skipping")
        else:
            try:
                cursor.execute(f"""
                    CREATE INDEX {index_name}
                    ON {table_name}({column_name})
                """)
                print(f"  ✅ Created index: {index_name}")
                created_indexes.append(index_name)
            except sqlite3.Error as e:
                print(f"  ⚠️  Could not create index {index_name}: {e}")

    # 4. Validate schema creation (only if tables were created by this migration)
    if not (installations_exists and files_exists):
        print("  📋 Validating schema creation...")

        # Verify provider_installations table structure
        cursor.execute("PRAGMA table_info(provider_installations)")
        installations_columns = {row[1] for row in cursor.fetchall()}
        expected_installations_columns = {
            'id', 'project_id', 'provider_name', 'version', 'installed_at',
            'config', 'status', 'last_synced_at'
        }

        if expected_installations_columns.issubset(installations_columns):
            print("  ✅ provider_installations table structure validated")
        else:
            missing = expected_installations_columns - installations_columns
            print(f"  ⚠️  WARNING: Missing columns in provider_installations: {missing}")

        # Verify provider_files table structure
        cursor.execute("PRAGMA table_info(provider_files)")
        files_columns = {row[1] for row in cursor.fetchall()}
        expected_files_columns = {
            'id', 'installation_id', 'file_path', 'file_type', 'content_hash',
            'generated_at', 'last_verified_at', 'modification_detected'
        }

        if expected_files_columns.issubset(files_columns):
            print("  ✅ provider_files table structure validated")
        else:
            missing = expected_files_columns - files_columns
            print(f"  ⚠️  WARNING: Missing columns in provider_files: {missing}")
    else:
        print("  ℹ️  Tables already existed, skipping validation (will be migrated by migration 0049)")

    # Show created indexes
    print("  📊 Provider Tracking Indexes:")
    for index_name, table_name, column_name in indexes:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
        exists = "✓" if cursor.fetchone() else "✗"
        print(f"      {exists} {index_name} on {table_name}({column_name})")

    conn.commit()
    print("  ✅ Migration 0047 completed successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration changes.

    Drops:
    1. All provider tracking indexes
    2. provider_files table (with CASCADE to remove file records)
    3. provider_installations table (with CASCADE to remove installations)

    Warning: This will DELETE all provider tracking data.
    """
    print("🔧 Migration 0047 downgrade: Remove Provider Tracking System")
    print("  ⚠️  WARNING: This will delete all provider installation and file tracking data")

    cursor = conn.cursor()

    # 1. Drop indexes
    print("  📋 Dropping provider tracking indexes...")
    indexes = [
        "idx_provider_installations_project",
        "idx_provider_installations_status",
        "idx_provider_files_installation",
        "idx_provider_files_hash",
    ]

    for index_name in indexes:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"  ✅ Dropped index: {index_name}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not drop index {index_name}: {e}")

    # 2. Drop provider_files table (must drop first due to foreign key)
    print("  📋 Dropping provider_files table...")
    try:
        cursor.execute("DROP TABLE IF EXISTS provider_files")
        print("  ✅ Dropped table: provider_files")
    except sqlite3.Error as e:
        print(f"  ⚠️  Could not drop provider_files table: {e}")

    # 3. Drop provider_installations table
    print("  📋 Dropping provider_installations table...")
    try:
        cursor.execute("DROP TABLE IF EXISTS provider_installations")
        print("  ✅ Dropped table: provider_installations")
    except sqlite3.Error as e:
        print(f"  ⚠️  Could not drop provider_installations table: {e}")

    conn.commit()
    print("  ✅ Migration 0047 downgrade completed")
