"""
Migration 0032: Enforce docs/ path structure with CHECK constraint

Adds CHECK constraint to document_references.file_path to ensure all new documents
follow the standardized docs/ directory structure established in migration 0031.

Allows exceptions for:
- Project root files (CHANGELOG.md, *.md artifacts)
- Module documentation (agentpm/*/README.md)
- Test reports (testing/*, tests/*)
- Test code (tests/**/*.py)

All other documents must start with 'docs/' prefix.
"""

import sqlite3
from datetime import datetime


def upgrade(conn: sqlite3.Connection) -> None:
    """Add CHECK constraint to enforce docs/ path structure"""
    print("🔧 Migration 0032: Enforce docs/ path structure")

    # SQLite doesn't support ADD CONSTRAINT for CHECK constraints
    # Must recreate table with new constraint

    # Step 1: Create new table with CHECK constraint
    print("  📋 Creating new table with path constraint...")
    conn.execute("""
        CREATE TABLE document_references_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT CHECK(document_type IN ('idea', 'requirements', 'refactoring_guide', 'user_story', 'use_case', 'architecture', 'design', 'specification', 'api_doc', 'user_guide', 'admin_guide', 'troubleshooting', 'adr', 'test_plan', 'migration_guide', 'runbook', 'business_pillars_analysis', 'market_research_report', 'competitive_analysis', 'quality_gates_specification', 'stakeholder_analysis', 'technical_specification', 'implementation_plan', 'other')),
            title TEXT,
            description TEXT,
            file_size_bytes INTEGER,
            content_hash TEXT,
            format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0),
            CHECK (
                -- Primary rule: Must start with 'docs/'
                file_path LIKE 'docs/%'
                -- Exception 1: Project root markdown files
                OR file_path IN ('CHANGELOG.md', 'README.md', 'LICENSE.md')
                -- Exception 2: Project root artifacts (deployment, gates, etc.)
                OR (file_path LIKE '%.md' AND file_path NOT LIKE '%/%')
                -- Exception 3: Module documentation
                OR file_path GLOB 'agentpm/*/README.md'
                -- Exception 4: Test reports and test code
                OR file_path LIKE 'testing/%'
                OR file_path LIKE 'tests/%'
            ),
            UNIQUE(entity_type, entity_id, file_path)
        )
    """)

    # Step 2: Copy all data from old table
    # Need to detect if migration 0031 columns exist
    print("  📋 Copying data to new table...")
    cursor = conn.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Check if migration 0031 ran (category column exists)
    has_extended_columns = 'category' in existing_columns

    if has_extended_columns:
        # Migration 0031 ran - copy all 24 columns
        conn.execute("""
            INSERT INTO document_references_new
            SELECT * FROM document_references
        """)
    else:
        # Migration 0031 didn't run - copy only base 13 columns
        # Extended columns will be NULL
        conn.execute("""
            INSERT INTO document_references_new (
                id, entity_type, entity_id, file_path, document_type,
                title, description, file_size_bytes, content_hash, format,
                created_by, created_at, updated_at
            )
            SELECT
                id, entity_type, entity_id, file_path, document_type,
                title, description, file_size_bytes, content_hash, format,
                created_by, created_at, updated_at
            FROM document_references
        """)

    # Step 3: Drop old table
    print("  📋 Dropping old table...")
    conn.execute("DROP TABLE document_references")

    # Step 4: Rename new table
    print("  📋 Renaming new table...")
    conn.execute("ALTER TABLE document_references_new RENAME TO document_references")

    # Step 5: Recreate indexes
    print("  📋 Recreating indexes...")
    conn.execute("""
        CREATE INDEX idx_doc_category
        ON document_references(category)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_type_dir
        ON document_references(document_type_dir)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_cat_type
        ON document_references(category, document_type_dir)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_component
        ON document_references(component)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_domain
        ON document_references(domain)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_work_item
        ON document_references(work_item_id)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_audience
        ON document_references(audience)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_maturity
        ON document_references(maturity)
    """)

    print("  ✅ CHECK constraint added successfully")
    print("  📋 All new documents must start with 'docs/' (with exceptions)")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove CHECK constraint (revert to original schema)"""
    print("🔧 Migration 0032 downgrade: Remove docs/ path constraint")

    # Step 1: Create table without docs/ CHECK constraint
    print("  📋 Creating table without path constraint...")
    conn.execute("""
        CREATE TABLE document_references_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
            entity_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            document_type TEXT CHECK(document_type IN ('idea', 'requirements', 'refactoring_guide', 'user_story', 'use_case', 'architecture', 'design', 'specification', 'api_doc', 'user_guide', 'admin_guide', 'troubleshooting', 'adr', 'test_plan', 'migration_guide', 'runbook', 'business_pillars_analysis', 'market_research_report', 'competitive_analysis', 'quality_gates_specification', 'stakeholder_analysis', 'technical_specification', 'implementation_plan', 'other')),
            title TEXT,
            description TEXT,
            file_size_bytes INTEGER,
            content_hash TEXT,
            format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0),
            UNIQUE(entity_type, entity_id, file_path)
        )
    """)

    # Step 2: Copy all data
    print("  📋 Copying data back...")
    # Check if migration 0031 columns exist
    cursor = conn.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    has_extended_columns = 'category' in existing_columns

    if has_extended_columns:
        conn.execute("""
            INSERT INTO document_references_old
            SELECT * FROM document_references
        """)
    else:
        conn.execute("""
            INSERT INTO document_references_old (
                id, entity_type, entity_id, file_path, document_type,
                title, description, file_size_bytes, content_hash, format,
                created_by, created_at, updated_at
            )
            SELECT
                id, entity_type, entity_id, file_path, document_type,
                title, description, file_size_bytes, content_hash, format,
                created_by, created_at, updated_at
            FROM document_references
        """)

    # Step 3: Drop new table
    print("  📋 Dropping constrained table...")
    conn.execute("DROP TABLE document_references")

    # Step 4: Rename old table
    print("  📋 Renaming table...")
    conn.execute("ALTER TABLE document_references_old RENAME TO document_references")

    # Step 5: Recreate indexes
    print("  📋 Recreating indexes...")
    conn.execute("""
        CREATE INDEX idx_doc_category
        ON document_references(category)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_type_dir
        ON document_references(document_type_dir)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_cat_type
        ON document_references(category, document_type_dir)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_component
        ON document_references(component)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_domain
        ON document_references(domain)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_work_item
        ON document_references(work_item_id)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_audience
        ON document_references(audience)
    """)
    conn.execute("""
        CREATE INDEX idx_doc_maturity
        ON document_references(maturity)
    """)

    print("  ✅ Constraint removed successfully")
