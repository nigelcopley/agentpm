"""
Migration 0037: Claude Memory File System

Creates memory_files table for Claude's persistent memory system.
Tracks generated memory files that provide Claude with always-current
access to APM (Agent Project Manager) database content (rules, agents, workflow, contexts, etc.).

Part of WI-114: Claude Persistent Memory System
"""

import sqlite3
from datetime import datetime


def upgrade(conn: sqlite3.Connection) -> None:
    """Create memory_files table for Claude persistent memory system"""
    print("🔧 Migration 0037: Create memory_files table")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            session_id INTEGER,

            -- Memory file metadata
            file_type TEXT NOT NULL CHECK(file_type IN (
                'rules',           -- RULES.md - Governance rules
                'principles',      -- PRINCIPLES.md - Development principles
                'workflow',        -- WORKFLOW.md - Quality-gated workflow
                'agents',          -- AGENTS.md - Agent system
                'context',         -- CONTEXT.md - Context assembly
                'project',         -- PROJECT.md - Project information
                'ideas'            -- IDEAS.md - Ideas analysis
            )),
            file_path TEXT NOT NULL,  -- Relative path in .claude/ directory
            file_hash TEXT,           -- SHA-256 hash for change detection

            -- Content metadata
            content TEXT NOT NULL,                    -- Generated markdown content
            source_tables TEXT NOT NULL DEFAULT '[]', -- JSON array of source tables
            template_version TEXT NOT NULL DEFAULT '1.0.0',

            -- Quality metadata
            confidence_score REAL DEFAULT 1.0 CHECK(confidence_score BETWEEN 0.0 AND 1.0),
            completeness_score REAL DEFAULT 1.0 CHECK(completeness_score BETWEEN 0.0 AND 1.0),
            validation_status TEXT NOT NULL DEFAULT 'pending' CHECK(validation_status IN (
                'pending', 'validated', 'stale', 'failed'
            )),

            -- Generation metadata
            generated_by TEXT NOT NULL,  -- Agent or service that generated file
            generation_duration_ms INTEGER,

            -- Timestamps
            generated_at TEXT NOT NULL,
            validated_at TEXT,
            expires_at TEXT,  -- Optional expiry for cache management
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            -- Foreign keys
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,

            -- Constraints
            UNIQUE(project_id, file_type)  -- One file per type per project
        )
    """)

    # Indexes for fast lookups
    print("  📋 Creating indexes...")

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_files_project
        ON memory_files(project_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_files_type
        ON memory_files(file_type)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_files_validation
        ON memory_files(validation_status)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_files_generated
        ON memory_files(generated_at)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_memory_files_expires
        ON memory_files(expires_at)
    """)

    print("  ✅ Memory files table created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Drop memory_files table"""
    print("🔧 Migration 0037 downgrade: Drop memory_files table")

    conn.execute("DROP TABLE IF EXISTS memory_files")

    print("  ✅ Memory files table dropped successfully")
