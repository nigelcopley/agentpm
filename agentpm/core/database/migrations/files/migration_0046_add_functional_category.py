"""
Migration 0046: Add Functional Category to Agents

Replaces the confusing tier system (1/2/3) with clear functional categories.

This migration adds:
1. functional_category column to agents table
2. Data transformation to populate categories based on role/type inference
3. Performance index on functional_category
4. Validation that all agents are categorized

Functional Categories:
- planning: Orchestrators, planners, framers (define what to do)
- implementation: Developers, implementers, builders (build features)
- testing: Test specialists, verifiers, quality analyzers (validate quality)
- documentation: Documentation writers, curators (create docs)
- utilities: Support agents, helpers (enable other agents)

Part of WI-165: Document Management Fixes
Task: #1112 - Database Migration for Functional Categories
"""

import sqlite3
from datetime import datetime

VERSION = "0046"
DESCRIPTION = "Add functional_category column to agents table"


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Apply migration changes.

    Changes:
    1. Add functional_category column to agents table
    2. Populate functional_category based on role/type inference
    3. Create index on functional_category
    4. Validate all agents have categories
    """
    print("🔧 Migration 0046: Add Functional Category to Agents")
    cursor = conn.cursor()

    # Check existing columns
    print("  📋 Checking existing columns in agents table...")
    cursor.execute("PRAGMA table_info(agents)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # 1. Add functional_category column if it doesn't exist
    if "functional_category" in existing_columns:
        print("  ⚠️  Column functional_category already exists, skipping creation")
    else:
        print("  📋 Adding functional_category column to agents...")
        try:
            cursor.execute("""
                ALTER TABLE agents
                ADD COLUMN functional_category TEXT
                CHECK(functional_category IN ('planning', 'implementation', 'testing', 'documentation', 'utilities'))
            """)
            print("  ✅ Added column: functional_category")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  ⚠️  Column functional_category already exists, skipping")
            else:
                raise

    # 2. Populate functional_category based on role/type inference
    print("  📋 Populating functional_category based on role analysis...")

    # Get count before transformation
    cursor.execute("SELECT COUNT(*) FROM agents WHERE functional_category IS NULL")
    null_count_before = cursor.fetchone()[0]
    print(f"  📊 Found {null_count_before} agents needing categorization")

    # Planning category (orchestrators, planners, framers)
    cursor.execute("""
        UPDATE agents
        SET functional_category = 'planning'
        WHERE functional_category IS NULL
        AND (
            role LIKE '%orch%'
            OR role LIKE '%planner%'
            OR role LIKE '%framer%'
            OR role LIKE '%architect%'
            OR role LIKE '%designer%'
            OR role LIKE '%definition%'
            OR role LIKE '%planning%'
            OR role LIKE '%strategy%'
            OR role LIKE '%roadmap%'
            OR agent_type IN ('orchestrator', 'planner', 'framer', 'architect')
        )
    """)
    planning_count = cursor.rowcount
    print(f"  ✅ Categorized {planning_count} agents as 'planning'")

    # Implementation category (developers, implementers, builders)
    cursor.execute("""
        UPDATE agents
        SET functional_category = 'implementation'
        WHERE functional_category IS NULL
        AND (
            role LIKE '%developer%'
            OR role LIKE '%implementer%'
            OR role LIKE '%builder%'
            OR role LIKE '%coder%'
            OR role LIKE '%engineer%'
            OR role LIKE '%migration%'
            OR role LIKE '%schema%'
            OR role LIKE '%database%'
            OR role LIKE '%python%'
            OR role LIKE '%cli%'
            OR role LIKE '%code-impl%'
            OR agent_type IN ('developer', 'implementer', 'builder', 'engineer')
        )
    """)
    implementation_count = cursor.rowcount
    print(f"  ✅ Categorized {implementation_count} agents as 'implementation'")

    # Testing category (testers, verifiers, quality analyzers)
    cursor.execute("""
        UPDATE agents
        SET functional_category = 'testing'
        WHERE functional_category IS NULL
        AND (
            role LIKE '%test%'
            OR role LIKE '%verif%'
            OR role LIKE '%quality%'
            OR role LIKE '%validator%'
            OR role LIKE '%analyzer%'
            OR role LIKE '%review%'
            OR role LIKE '%gate%'
            OR role LIKE '%check%'
            OR agent_type IN ('tester', 'verifier', 'validator', 'analyzer', 'reviewer')
        )
    """)
    testing_count = cursor.rowcount
    print(f"  ✅ Categorized {testing_count} agents as 'testing'")

    # Documentation category (doc writers, curators)
    cursor.execute("""
        UPDATE agents
        SET functional_category = 'documentation'
        WHERE functional_category IS NULL
        AND (
            role LIKE '%doc%'
            OR role LIKE '%writer%'
            OR role LIKE '%curator%'
            OR role LIKE '%author%'
            OR role LIKE '%technical-writer%'
            OR role LIKE '%content%'
            OR agent_type IN ('writer', 'curator', 'author', 'documenter')
        )
    """)
    documentation_count = cursor.rowcount
    print(f"  ✅ Categorized {documentation_count} agents as 'documentation'")

    # Utilities category (everything else - support agents, helpers)
    cursor.execute("""
        UPDATE agents
        SET functional_category = 'utilities'
        WHERE functional_category IS NULL
    """)
    utilities_count = cursor.rowcount
    print(f"  ✅ Categorized {utilities_count} agents as 'utilities'")

    # 3. Create index on functional_category
    print("  📋 Creating index on functional_category...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_agents_functional_category'")
    index_exists = cursor.fetchone() is not None

    if index_exists:
        print("  ⚠️  Index idx_agents_functional_category already exists, skipping")
    else:
        cursor.execute("""
            CREATE INDEX idx_agents_functional_category
            ON agents(functional_category)
        """)
        print("  ✅ Created index: idx_agents_functional_category")

    # 4. Validate all agents are categorized
    print("  📋 Validating all agents have functional_category...")
    cursor.execute("SELECT COUNT(*) FROM agents WHERE functional_category IS NULL")
    null_count_after = cursor.fetchone()[0]

    if null_count_after > 0:
        print(f"  ⚠️  WARNING: {null_count_after} agents still have NULL functional_category")
        # Show which ones
        cursor.execute("SELECT id, role FROM agents WHERE functional_category IS NULL LIMIT 5")
        uncategorized = cursor.fetchall()
        for agent_id, role in uncategorized:
            print(f"      - Agent #{agent_id}: {role}")
    else:
        print("  ✅ All agents successfully categorized")

    # Show distribution
    print("  📊 Functional Category Distribution:")
    cursor.execute("""
        SELECT functional_category, COUNT(*) as count
        FROM agents
        WHERE functional_category IS NOT NULL
        GROUP BY functional_category
        ORDER BY count DESC
    """)
    for category, count in cursor.fetchall():
        print(f"      - {category}: {count} agents")

    conn.commit()
    print("  ✅ Migration 0046 completed successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Rollback migration changes.

    SQLite limitation: Can't drop columns directly.
    The functional_category column will remain but values will be cleared.
    The index will be dropped.

    To fully remove the column, the table would need to be recreated,
    which is too risky for simple column additions.
    """
    print("🔧 Migration 0046 downgrade: Remove Functional Category")
    print("  ⚠️  Note: SQLite does not support dropping columns directly")
    print("  ⚠️  The functional_category column will remain but values will be cleared")
    print("  ℹ️  To fully remove, the table would need to be recreated")

    cursor = conn.cursor()

    # Drop index
    print("  📋 Dropping index idx_agents_functional_category...")
    try:
        cursor.execute("DROP INDEX IF EXISTS idx_agents_functional_category")
        print("  ✅ Dropped index: idx_agents_functional_category")
    except sqlite3.Error as e:
        print(f"  ⚠️  Could not drop index: {e}")

    # Clear functional_category values
    print("  📋 Clearing functional_category values...")
    cursor.execute("""
        UPDATE agents
        SET functional_category = NULL
        WHERE functional_category IS NOT NULL
    """)
    cleared_count = cursor.rowcount
    print(f"  ✅ Cleared {cleared_count} functional_category values")

    conn.commit()
    print("  ✅ Migration 0046 downgrade completed")
