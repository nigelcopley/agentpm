"""
Migration 0031: Universal Documentation System with Path Structure

Adds comprehensive metadata fields to document_references table to support
the Universal Documentation System with hierarchical path structure.

Path Structure: docs/{category}/{document_type}/{filename}

Categories (8):
- planning: Requirements, analysis, research, roadmaps
- architecture: Design, ADRs, patterns, integration
- guides: User guides, developer guides, admin guides, troubleshooting
- reference: API docs, CLI reference, schema, configuration
- processes: Workflows, procedures, templates
- governance: Policies, standards, compliance
- operations: Runbooks, deployment guides, monitoring
- communication: Announcements, reports, presentations

New Fields:
- category: One of 8 top-level categories
- document_type_dir: Physical subdirectory under category
- segment_type: Content type (narrative, reference, procedural, analytical)
- component: Technical component this document relates to
- domain: Business/technical domain
- audience: Target audience (developer, user, admin, stakeholder)
- maturity: Document maturity (draft, review, approved, deprecated)
- priority: Importance level (critical, high, medium, low)
- tags: JSON array of searchable tags
- phase: SDLC phase (discovery, planning, implementation, review, ops, evolution)
- work_item_id: Link to related work item

All new columns are nullable for backward compatibility.
Existing records are preserved without modification.
"""

import sqlite3


def upgrade(conn: sqlite3.Connection) -> None:
    """Add Universal Documentation System metadata columns"""
    print("🔧 Migration 0031: Add Universal Documentation System columns")

    # Check if columns already exist (idempotent migration)
    cursor = conn.execute("PRAGMA table_info(document_references)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = []

    # Category field (top-level organization)
    if 'category' not in existing_columns:
        columns_to_add.append(
            ("category", "TEXT", "One of 8 top-level categories")
        )

    # Document type directory (physical subdirectory)
    if 'document_type_dir' not in existing_columns:
        columns_to_add.append(
            ("document_type_dir", "TEXT", "Physical subdirectory under category")
        )

    # Segment type (content classification)
    if 'segment_type' not in existing_columns:
        columns_to_add.append(
            ("segment_type", "TEXT", "Content type classification")
        )

    # Component (technical component)
    if 'component' not in existing_columns:
        columns_to_add.append(
            ("component", "TEXT", "Related technical component")
        )

    # Domain (business/technical domain)
    if 'domain' not in existing_columns:
        columns_to_add.append(
            ("domain", "TEXT", "Business or technical domain")
        )

    # Audience (target readers)
    if 'audience' not in existing_columns:
        columns_to_add.append(
            ("audience", "TEXT", "Target audience")
        )

    # Maturity (document lifecycle state)
    if 'maturity' not in existing_columns:
        columns_to_add.append(
            ("maturity", "TEXT", "Document maturity level")
        )

    # Priority (importance level)
    if 'priority' not in existing_columns:
        columns_to_add.append(
            ("priority", "TEXT", "Importance level")
        )

    # Tags (JSON array for search)
    if 'tags' not in existing_columns:
        columns_to_add.append(
            ("tags", "TEXT", "JSON array of tags")
        )

    # Phase (SDLC phase)
    if 'phase' not in existing_columns:
        columns_to_add.append(
            ("phase", "TEXT", "SDLC phase")
        )

    # Work item ID (link to work item)
    if 'work_item_id' not in existing_columns:
        columns_to_add.append(
            ("work_item_id", "INTEGER", "Related work item ID")
        )

    # Add columns
    if columns_to_add:
        print(f"  📋 Adding {len(columns_to_add)} new columns...")
        for column_name, column_type, description in columns_to_add:
            conn.execute(f"""
                ALTER TABLE document_references
                ADD COLUMN {column_name} {column_type}
            """)
            print(f"  ✅ Added column: {column_name} ({description})")
    else:
        print("  ✅ All columns already exist, skipping column creation")

    # Create indexes for efficient querying
    print("  📋 Creating indexes...")

    indexes_to_create = []

    # Check existing indexes
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='document_references'"
    )
    existing_indexes = {row[0] for row in cursor.fetchall()}

    # Index on category
    if 'idx_doc_category' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_category", "category", "Category lookup")
        )

    # Index on document_type_dir
    if 'idx_doc_type_dir' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_type_dir", "document_type_dir", "Document type directory lookup")
        )

    # Composite index on category and document_type_dir
    if 'idx_doc_cat_type' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_cat_type", "category, document_type_dir", "Category + type lookup")
        )

    # Index on component
    if 'idx_doc_component' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_component", "component", "Component lookup")
        )

    # Index on domain
    if 'idx_doc_domain' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_domain", "domain", "Domain lookup")
        )

    # Index on work_item_id for foreign key lookups
    if 'idx_doc_work_item' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_work_item", "work_item_id", "Work item association")
        )

    # Index on audience
    if 'idx_doc_audience' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_audience", "audience", "Audience filtering")
        )

    # Index on maturity
    if 'idx_doc_maturity' not in existing_indexes:
        indexes_to_create.append(
            ("idx_doc_maturity", "maturity", "Maturity filtering")
        )

    if indexes_to_create:
        for index_name, columns, description in indexes_to_create:
            conn.execute(f"""
                CREATE INDEX {index_name}
                ON document_references({columns})
            """)
            print(f"  ✅ Created index: {index_name} ({description})")
    else:
        print("  ✅ All indexes already exist, skipping index creation")

    print("  ✅ Migration 0031 completed successfully")
    print(f"  📊 Added {len(columns_to_add)} columns and {len(indexes_to_create)} indexes")
    print("  📁 Path structure: docs/{category}/{document_type}/{filename}")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove Universal Documentation System columns and indexes"""
    print("🔧 Migration 0031 downgrade: Remove Universal Documentation System columns")

    # Drop indexes first
    print("  📋 Dropping indexes...")

    indexes_to_drop = [
        'idx_doc_category',
        'idx_doc_type_dir',
        'idx_doc_cat_type',
        'idx_doc_component',
        'idx_doc_domain',
        'idx_doc_work_item',
        'idx_doc_audience',
        'idx_doc_maturity',
    ]

    for index_name in indexes_to_drop:
        try:
            conn.execute(f"DROP INDEX IF EXISTS {index_name}")
            print(f"  ✅ Dropped index: {index_name}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not drop index {index_name}: {e}")

    # SQLite doesn't support DROP COLUMN directly
    # We need to recreate the table without the new columns
    print("  📋 Recreating table without new columns...")

    # Create new table with original schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_references_backup (
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
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0),
            UNIQUE(entity_type, entity_id, file_path)
        )
    """)

    # Copy data (only original columns)
    conn.execute("""
        INSERT INTO document_references_backup (
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

    # Drop old table
    conn.execute("DROP TABLE document_references")

    # Rename backup to original name
    conn.execute("ALTER TABLE document_references_backup RENAME TO document_references")

    print("  ✅ Table recreated with original schema")
    print("  ✅ Migration 0031 downgrade completed successfully")
