"""
Migration 0036: Cursor Provider System

Creates tables for provider installation system:
1. provider_installations: Tracks installed providers (Cursor, VS Code, etc.)
2. provider_files: Tracks installed files and their hashes
3. cursor_memories: Manages Cursor memory files synced with AIPM learnings

Supports the new Cursor provider architecture (WI-120).
"""

import sqlite3
from datetime import datetime


def upgrade(conn: sqlite3.Connection) -> None:
    """Create provider system tables"""
    print("🔧 Migration 0036: Create Cursor provider system tables")

    # 1. Provider Installations Table
    print("  📋 Creating provider_installations table...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS provider_installations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            provider_type TEXT NOT NULL CHECK(provider_type IN ('cursor', 'vscode', 'zed', 'claude_code')),
            provider_version TEXT NOT NULL DEFAULT '1.0.0',

            -- Installation metadata
            install_path TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('installed', 'partial', 'failed', 'uninstalled')),
            config TEXT NOT NULL DEFAULT '{}',  -- JSON configuration

            -- File tracking
            installed_files TEXT NOT NULL DEFAULT '[]',  -- JSON array of file paths
            file_hashes TEXT NOT NULL DEFAULT '{}',  -- JSON map of file_path -> hash

            -- Timestamps
            installed_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_verified_at TEXT,

            -- Foreign keys
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

            -- Constraints
            UNIQUE(project_id, provider_type)  -- One provider per project
        )
    """)

    # Index for fast lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_provider_installations_project
        ON provider_installations(project_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_provider_installations_type
        ON provider_installations(provider_type)
    """)

    # 2. Provider Files Table
    print("  📋 Creating provider_files table...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS provider_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            installation_id INTEGER NOT NULL,

            -- File metadata
            file_path TEXT NOT NULL,  -- Relative path from provider root
            file_hash TEXT NOT NULL,  -- SHA-256 hash for integrity check
            file_type TEXT NOT NULL CHECK(file_type IN ('rule', 'mode', 'hook', 'config', 'memory')),

            -- Timestamps
            installed_at TEXT NOT NULL,

            -- Foreign keys
            FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,

            -- Constraints
            UNIQUE(installation_id, file_path)  -- No duplicate files per installation
        )
    """)

    # Index for fast file lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_provider_files_installation
        ON provider_files(installation_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_provider_files_type
        ON provider_files(file_type)
    """)

    # 3. Cursor Memories Table
    print("  📋 Creating cursor_memories table...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cursor_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Memory metadata
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',

            -- Memory content
            content TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',  -- JSON array of tags

            -- File metadata
            file_path TEXT NOT NULL,  -- Relative path in .cursor/memories/
            file_hash TEXT,  -- SHA-256 hash of file content

            -- Sync metadata
            source_learning_id INTEGER,  -- AIPM learning that generated this memory
            last_synced_at TEXT,

            -- Timestamps
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            -- Foreign keys
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (source_learning_id) REFERENCES learnings(id) ON DELETE SET NULL,

            -- Constraints
            UNIQUE(project_id, file_path)  -- No duplicate memory files
        )
    """)

    # Indexes for memory queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cursor_memories_project
        ON cursor_memories(project_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cursor_memories_category
        ON cursor_memories(category)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cursor_memories_source_learning
        ON cursor_memories(source_learning_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cursor_memories_sync
        ON cursor_memories(last_synced_at)
    """)

    print("  ✅ Provider system tables created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Drop provider system tables"""
    print("🔧 Migration 0036 downgrade: Drop provider system tables")

    # Drop tables in reverse order (respect foreign keys)
    conn.execute("DROP TABLE IF EXISTS cursor_memories")
    conn.execute("DROP TABLE IF EXISTS provider_files")
    conn.execute("DROP TABLE IF EXISTS provider_installations")

    print("  ✅ Provider system tables dropped successfully")
