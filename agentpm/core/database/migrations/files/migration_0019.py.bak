"""
Migration 0019: Expand contexts table to support rich context types and ideas

Updates CHECK constraints for contexts.context_type and contexts.entity_type to
support new rich types (business_pillars_context, market_research_context, 
competitive_analysis_context, quality_gates_context, stakeholder_context,
technical_context, implementation_context, idea_context, idea_to_work_item_mapping)
and adds 'idea' to entity_type.

Approach: Recreate contexts table with the new schema and copy existing data.
"""

import sqlite3


NEW_CONTEXT_TYPES = (
    "'resource_file', 'project_context', 'work_item_context', 'task_context', "
    "'business_pillars_context', 'market_research_context', 'competitive_analysis_context', "
    "'quality_gates_context', 'stakeholder_context', 'technical_context', 'implementation_context', "
    "'idea_context', 'idea_to_work_item_mapping'"
)

NEW_ENTITY_TYPES = ("'project', 'work_item', 'task', 'idea'")


def upgrade(conn: sqlite3.Connection) -> None:
    print("🚀 Migration 0019: Expanding contexts table checks and columns")

    # Ensure foreign keys are enforced
    conn.execute("PRAGMA foreign_keys = OFF")

    # Read original create SQL to determine current columns (best-effort)
    # Recreate table to match utils.schema current definition

    # 1) Create new table with expanded checks
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS contexts_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Context type (discriminator)
            context_type TEXT NOT NULL CHECK(context_type IN ({NEW_CONTEXT_TYPES})),

            -- Resource file fields (for context_type = 'resource_file')
            file_path TEXT,
            file_hash TEXT,
            resource_type TEXT CHECK(resource_type IN ('sop', 'code', 'specification', 'documentation') OR resource_type IS NULL),

            -- Entity context fields (for project_context, work_item_context, task_context, idea_context, etc.)
            entity_type TEXT CHECK(entity_type IN ({NEW_ENTITY_TYPES}) OR entity_type IS NULL),
            entity_id INTEGER,

            -- UnifiedSixW structure (JSON, for entity contexts)
            six_w_data TEXT,

            -- Integrated confidence scoring (for entity contexts)
            confidence_score REAL CHECK(confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),
            confidence_band TEXT CHECK(confidence_band IN ('RED', 'YELLOW', 'GREEN') OR confidence_band IS NULL),
            confidence_factors TEXT,

            -- Rich context data storage (for new context types)
            context_data TEXT,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

            -- Constraint: resource files must have file_path
            CHECK (
                (context_type = 'resource_file' AND file_path IS NOT NULL) OR
                (context_type IN ({NEW_CONTEXT_TYPES}))
            ),

            -- Constraint: entity contexts must have entity_type + entity_id
            CHECK (
                (context_type = 'resource_file') OR
                (context_type IN ({NEW_CONTEXT_TYPES}) AND entity_type IS NOT NULL AND entity_id IS NOT NULL)
            ),

            -- Unique constraint for entity contexts (one context per entity)
            UNIQUE(context_type, entity_type, entity_id)
        )
        """
    )

    # 2) Copy data from old contexts table into new one (map columns safely)
    # Some older schemas may not have context_data column or column order differs.
    # Use explicit column list and COALESCE for missing fields.
    existing_cols = set(r[1] for r in conn.execute("PRAGMA table_info(contexts)").fetchall())

    # Build SELECT list with safe fallbacks
    def col(name: str) -> str:
        return name if name in existing_cols else f"NULL AS {name}"

    select_sql = f"""
        SELECT 
            id, 
            project_id, 
            context_type, 
            {col('file_path')}, 
            {col('file_hash')}, 
            {col('resource_type')}, 
            {col('entity_type')}, 
            {col('entity_id')}, 
            {col('six_w_data')}, 
            {col('confidence_score')}, 
            {col('confidence_band')}, 
            {col('confidence_factors')}, 
            {col('context_data')}, 
            {col('created_at')}, 
            {col('updated_at')}
        FROM contexts
    """

    conn.execute(
        """
        INSERT OR IGNORE INTO contexts_new (
            id, project_id, context_type, file_path, file_hash, resource_type,
            entity_type, entity_id, six_w_data, confidence_score, confidence_band,
            confidence_factors, context_data, created_at, updated_at
        )
        """ + select_sql
    )

    # 3) Replace old table
    conn.execute("DROP TABLE contexts")
    conn.execute("ALTER TABLE contexts_new RENAME TO contexts")

    # 4) Recreate indexes (match utils.schema)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_project ON contexts(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(context_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_entity ON contexts(entity_type, entity_id)")

    # 5) Record migration
    conn.execute(
        """
        INSERT INTO schema_migrations (version, description, applied_at, applied_by)
        VALUES ('0019_expand_context_types', 'Expand contexts table to support rich types and ideas', datetime('now'), 'migration_system')
        """
    )

    conn.execute("PRAGMA foreign_keys = ON")
    print("✅ Migration 0019 complete: contexts table expanded")


def downgrade(conn: sqlite3.Connection) -> None:
    print("⚠️  Downgrading 0019: Restoring legacy contexts constraints")
    conn.execute("PRAGMA foreign_keys = OFF")

    # Legacy schema (restricted types)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contexts_legacy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            context_type TEXT NOT NULL CHECK(context_type IN ('resource_file', 'project_context', 'work_item_context', 'task_context')),
            file_path TEXT,
            file_hash TEXT,
            resource_type TEXT CHECK(resource_type IN ('sop', 'code', 'specification', 'documentation') OR resource_type IS NULL),
            entity_type TEXT CHECK(entity_type IN ('project', 'work_item', 'task') OR entity_type IS NULL),
            entity_id INTEGER,
            six_w_data TEXT,
            confidence_score REAL CHECK(confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),
            confidence_band TEXT CHECK(confidence_band IN ('RED', 'YELLOW', 'GREEN') OR confidence_band IS NULL),
            confidence_factors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context_data TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            CHECK (
                (context_type = 'resource_file' AND file_path IS NOT NULL) OR
                (context_type IN ('project_context', 'work_item_context', 'task_context'))
            ),
            CHECK (
                (context_type = 'resource_file') OR
                (context_type IN ('project_context', 'work_item_context', 'task_context') AND entity_type IS NOT NULL AND entity_id IS NOT NULL)
            ),
            UNIQUE(context_type, entity_type, entity_id)
        )
        """
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO contexts_legacy (
            id, project_id, context_type, file_path, file_hash, resource_type,
            entity_type, entity_id, six_w_data, confidence_score, confidence_band,
            confidence_factors, created_at, updated_at, context_data
        )
        SELECT id, project_id, context_type, file_path, file_hash, resource_type,
               entity_type, entity_id, six_w_data, confidence_score, confidence_band,
               confidence_factors, created_at, updated_at, context_data
        FROM contexts
        """
    )

    conn.execute("DROP TABLE contexts")
    conn.execute("ALTER TABLE contexts_legacy RENAME TO contexts")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_project ON contexts(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(context_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_entity ON contexts(entity_type, entity_id)")

    conn.execute(
        """
        UPDATE schema_migrations 
        SET rollback_at = datetime('now'), rollback_reason='Reverted 0019'
        WHERE version = '0019_expand_context_types' AND rollback_at IS NULL
        """
    )

    conn.execute("PRAGMA foreign_keys = ON")
    print("✅ Downgrade 0019 complete: contexts restored to legacy checks")


