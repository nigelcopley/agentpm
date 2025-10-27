"""
Migration 0050: Skills System Database Schema

Creates skills and agent_skills tables for the skills management system.
Enables agents to have reusable capability modules with progressive loading.

Part of WI-171: Claude Code Provider Enhancement
Task #1130: Implementation: Skills Database Schema and Models
"""

import sqlite3
from datetime import datetime


def upgrade(conn: sqlite3.Connection) -> None:
    """Create skills and agent_skills tables with proper indexes"""
    print("🔧 Migration 0050: Create skills system tables")

    # ========================================================================
    # SKILLS TABLE
    # ========================================================================

    print("  📋 Creating skills table...")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            -- Primary key
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identifiers
            name TEXT NOT NULL,                          -- Kebab-case identifier (e.g., 'python-testing')
            display_name TEXT NOT NULL,                  -- Human-readable name (e.g., 'Python Testing')
            description TEXT NOT NULL,                   -- Brief description for discovery (~100 chars)
            category TEXT,                               -- Grouping (testing, database, api, documentation)

            -- Content sections (progressive loading: metadata → instructions → resources)
            instructions TEXT NOT NULL,                  -- Level 2: Main instructions (markdown, ~5-20 KB)
            resources TEXT,                              -- Level 3: JSON {examples: [], templates: [], docs: []}

            -- Provider-specific configuration
            provider_config TEXT,                        -- JSON {claude_code: {allowed_tools: []}, cursor: {}}

            -- State
            enabled BOOLEAN NOT NULL DEFAULT 1,          -- Enable/disable skill

            -- Audit timestamps
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),

            -- Constraints
            CONSTRAINT unique_skill_name UNIQUE (name),
            CONSTRAINT valid_category CHECK (category IN (
                'testing', 'database', 'api', 'documentation',
                'security', 'deployment', 'monitoring', 'project-management'
            ))
        )
    """)

    # Indexes for skills table
    print("  📋 Creating skills indexes...")

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_skills_category
        ON skills(category)
        WHERE category IS NOT NULL
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_skills_enabled
        ON skills(enabled)
        WHERE enabled = 1
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_skills_name_lookup
        ON skills(name)
    """)

    # ========================================================================
    # AGENT SKILLS JUNCTION TABLE
    # ========================================================================

    print("  📋 Creating agent_skills junction table...")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_skills (
            -- Primary key
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Foreign keys
            agent_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,

            -- Priority for loading order (higher = load earlier)
            priority INTEGER NOT NULL DEFAULT 50,        -- Range: 0-100

            -- Audit
            created_at TEXT NOT NULL DEFAULT (datetime('now')),

            -- Foreign key constraints
            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,

            -- Constraints
            CONSTRAINT unique_agent_skill UNIQUE (agent_id, skill_id),
            CONSTRAINT valid_priority CHECK (priority BETWEEN 0 AND 100)
        )
    """)

    # Indexes for agent_skills table
    print("  📋 Creating agent_skills indexes...")

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_skills_agent
        ON agent_skills(agent_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_skills_skill
        ON agent_skills(skill_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_skills_priority
        ON agent_skills(agent_id, priority DESC)
    """)

    # ========================================================================
    # TRIGGERS FOR TIMESTAMP MANAGEMENT
    # ========================================================================

    print("  📋 Creating update triggers...")

    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_skills_timestamp
        AFTER UPDATE ON skills
        BEGIN
            UPDATE skills
            SET updated_at = datetime('now')
            WHERE id = NEW.id;
        END
    """)

    print("  ✅ Skills system tables created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Drop skills and agent_skills tables"""
    print("🔧 Migration 0050 downgrade: Drop skills system tables")

    # Drop in reverse dependency order
    conn.execute("DROP TRIGGER IF EXISTS update_skills_timestamp")
    conn.execute("DROP TABLE IF EXISTS agent_skills")
    conn.execute("DROP TABLE IF EXISTS skills")

    print("  ✅ Skills system tables dropped successfully")
