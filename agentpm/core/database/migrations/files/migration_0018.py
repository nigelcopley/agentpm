"""
Migration 0018: Consolidated Schema Migration (Enum-Driven)

Self-contained migration that creates the complete APM (Agent Project Manager) database schema
using enum helpers to generate CHECK constraints directly from Pydantic enums.

This ensures database constraints always match Python enum definitions.

Replaces the previous 17-migration chain with a single source of truth.
"""

import sqlite3
from agentpm.core.database.utils.enum_helpers import generate_check_constraint
from agentpm.core.database.enums import (
    # Status enums
    ProjectStatus,
    WorkItemStatus,
    TaskStatus,
    # Idea enums
    IdeaStatus,
    IdeaSource,
    # Type enums
    WorkItemType,
    TaskType,
    EntityType,
    ContextType,
    ResourceType,
    DocumentType,
    DocumentFormat,
    EnforcementLevel,
    Phase,
    SourceType,
    EventType,
    AgentTier,
    ConfidenceBand,
)


def upgrade(conn: sqlite3.Connection) -> None:
    """
    Create complete APM (Agent Project Manager) database schema using enum helpers.

    All CHECK constraints are generated from Pydantic enums to ensure
    database and code stay in sync.

    Args:
        conn: SQLite database connection
    """
    print("🚀 Migration 0018: Consolidated Schema Migration (Enum-Driven)")
    print("   - Creating complete APM (Agent Project Manager) database schema")
    print("   - Using enum helpers for CHECK constraints")
    print("   - Replacing 17 previous migrations with single source of truth")

    # Core entity tables
    _create_projects_table(conn)
    _create_work_items_table(conn)
    _create_tasks_table(conn)
    _create_agents_table(conn)
    _create_contexts_table(conn)
    _create_rules_table(conn)
    _create_ideas_table(conn)
    _create_document_references_table(conn)
    _create_session_events_table(conn)
    _create_evidence_sources_table(conn)
    _create_sessions_table(conn)

    # Agent relationship tables
    _create_agent_relationships_table(conn)
    _create_agent_tools_table(conn)

    # Relationship tables
    _create_task_dependencies_table(conn)
    _create_task_blockers_table(conn)
    _create_work_item_dependencies_table(conn)

    # Temporal context tables
    _create_work_item_summaries_table(conn)

    # System table
    _create_schema_migrations_table(conn)

    # Performance indexes
    _create_indexes(conn)

    # Triggers for automation
    _create_triggers(conn)

    # Clear the old migration records and insert our consolidated one
    conn.execute("DELETE FROM schema_migrations")
    conn.execute("""
        INSERT INTO schema_migrations (version, description, applied_at, applied_by)
        VALUES ('0018_consolidated', 'Consolidated schema migration (enum-driven)', datetime('now'), 'migration_system')
    """)

    print("✅ Migration 0018: Consolidated Schema Migration Complete")
    print("   - All 18 tables created with enum-driven constraints")
    print("   - Rich context system fully integrated")
    print("   - Session events and agent relationships added")
    print("   - Database ready for APM (Agent Project Manager) operations")


def downgrade(conn: sqlite3.Connection) -> None:
    """
    Downgrade by dropping all tables.

    Args:
        conn: SQLite database connection
    """
    print("⚠️  Downgrading: Dropping all tables")

    # Drop all tables in reverse order (respecting foreign keys)
    tables = [
        'work_item_summaries',
        'work_item_dependencies',
        'task_blockers',
        'task_dependencies',
        'agent_tools',
        'agent_relationships',
        'session_events',
        'evidence_sources',
        'sessions',
        'document_references',
        'ideas',
        'rules',
        'contexts',
        'agents',
        'tasks',
        'work_items',
        'projects',
        'schema_migrations'
    ]

    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    print("✅ Downgrade complete: All tables dropped")


def _create_projects_table(conn: sqlite3.Connection) -> None:
    """Create projects table with enum-driven constraints"""
    status_check = generate_check_constraint(ProjectStatus, 'status')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            path TEXT NOT NULL,

            -- Technical context (JSON arrays)
            tech_stack TEXT DEFAULT '[]',
            detected_frameworks TEXT DEFAULT '[]',

            -- Lifecycle
            status TEXT DEFAULT 'initiated' {status_check},

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _create_work_items_table(conn: sqlite3.Connection) -> None:
    """Create work_items table with enum-driven constraints"""
    type_check = generate_check_constraint(WorkItemType, 'type')
    status_check = generate_check_constraint(WorkItemStatus, 'status')
    phase_check = generate_check_constraint(Phase, 'phase')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS work_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_work_item_id INTEGER,

            -- Work item details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL {type_check},

            -- Business context
            business_context TEXT,
            metadata TEXT DEFAULT '{{}}',  -- WI-40: Consolidated configuration metadata (JSON)

            -- Planning
            effort_estimate_hours REAL,
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),

            -- Lifecycle
            status TEXT DEFAULT 'proposed' {status_check},
            phase TEXT {phase_check},
            due_date TIMESTAMP,
            not_before TIMESTAMP,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)


def _create_tasks_table(conn: sqlite3.Connection) -> None:
    """Create tasks table with enum-driven constraints"""
    type_check = generate_check_constraint(TaskType, 'type')
    status_check = generate_check_constraint(TaskStatus, 'status')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,

            -- Task details
            name TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'implementation' {type_check},

            -- Quality gate tracking (JSON)
            quality_metadata TEXT,

            -- Planning
            effort_hours REAL CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8)),
            priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
            due_date TIMESTAMP,

            -- Assignment
            assigned_to TEXT,

            -- Lifecycle
            status TEXT DEFAULT 'proposed' {status_check},
            blocked_reason TEXT,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,

            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)


def _create_agents_table(conn: sqlite3.Connection) -> None:
    """Create agents table with enum-driven constraints"""
    tier_check = generate_check_constraint(AgentTier, 'tier')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Agent identity
            role TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,

            -- SOP and capabilities
            sop_content TEXT,
            capabilities TEXT DEFAULT '[]',  -- JSON array

            -- Tier classification
            tier TEXT {tier_check},

            -- Status
            is_active INTEGER DEFAULT 1,

            -- File generation tracking (WI-009.3)
            agent_type TEXT DEFAULT NULL,
            file_path TEXT DEFAULT NULL,
            generated_at TIMESTAMP DEFAULT NULL,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            UNIQUE(project_id, role)
        )
    """)


def _create_contexts_table(conn: sqlite3.Connection) -> None:
    """Create contexts table with enum-driven constraints"""
    context_type_check = generate_check_constraint(ContextType, 'context_type')

    # For nullable fields, generate the values list directly
    entity_type_values = ",".join(f"'{v}'" for v in EntityType.choices())
    resource_type_values = ",".join(f"'{v}'" for v in ResourceType.choices())
    confidence_band_values = ",".join(f"'{v}'" for v in ConfidenceBand.choices())

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS contexts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Context type (discriminator)
            context_type TEXT NOT NULL {context_type_check},

            -- Resource file fields (for context_type = 'resource_file')
            file_path TEXT,
            file_hash TEXT,
            resource_type TEXT CHECK(resource_type IS NULL OR resource_type IN ({resource_type_values})),

            -- Entity context fields (for project_context, work_item_context, task_context)
            entity_type TEXT CHECK(entity_type IS NULL OR entity_type IN ({entity_type_values})),
            entity_id INTEGER,

            -- UnifiedSixW structure (JSON, for entity contexts)
            six_w_data TEXT,

            -- Integrated confidence scoring (for entity contexts)
            confidence_score REAL CHECK(confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),
            confidence_band TEXT CHECK(confidence_band IS NULL OR confidence_band IN ({confidence_band_values})),
            confidence_factors TEXT,  -- JSON: breakdown of scoring factors

            -- Rich context data storage (for new context types)
            context_data TEXT,  -- JSON: rich context data

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

            -- Constraint: resource files must have file_path
            CHECK (
                (context_type = 'resource_file' AND file_path IS NOT NULL) OR
                (context_type IN ('project_context', 'work_item_context', 'task_context', 'business_pillars_context', 'market_research_context', 'competitive_analysis_context', 'quality_gates_context', 'stakeholder_context', 'technical_context', 'implementation_context', 'idea_context', 'idea_to_work_item_mapping'))
            ),

            -- Constraint: entity contexts must have entity_type + entity_id
            CHECK (
                (context_type = 'resource_file') OR
                (context_type IN ('project_context', 'work_item_context', 'task_context', 'business_pillars_context', 'market_research_context', 'competitive_analysis_context', 'quality_gates_context', 'stakeholder_context', 'technical_context', 'implementation_context', 'idea_context', 'idea_to_work_item_mapping') AND entity_type IS NOT NULL AND entity_id IS NOT NULL)
            ),

            -- Unique constraint for entity contexts (one context per entity)
            UNIQUE(context_type, entity_type, entity_id)
        )
    """)


def _create_rules_table(conn: sqlite3.Connection) -> None:
    """Create rules table with enum-driven constraints"""
    enforcement_check = generate_check_constraint(EnforcementLevel, 'enforcement_level')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Rule identity
            rule_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,

            -- Rule enforcement
            enforcement_level TEXT NOT NULL {enforcement_check},
            validation_logic TEXT,
            error_message TEXT,

            -- Rule configuration (JSON)
            config TEXT,

            -- Status
            enabled INTEGER DEFAULT 1,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            UNIQUE(project_id, rule_id)
        )
    """)


def _create_ideas_table(conn: sqlite3.Connection) -> None:
    """Create ideas table with enum-driven constraints"""
    status_check = generate_check_constraint(IdeaStatus, 'status')
    source_check = generate_check_constraint(IdeaSource, 'source')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Core fields
            title TEXT NOT NULL CHECK(length(title) >= 3 AND length(title) <= 200),
            description TEXT,

            -- Attribution
            source TEXT {source_check},
            created_by TEXT,  -- Username, email, or agent identifier

            -- Social engagement
            votes INTEGER DEFAULT 0 CHECK(votes >= 0),
            tags TEXT DEFAULT '[]',  -- JSON array: ["ux", "backend", "quick-win"]

            -- Lifecycle
            status TEXT DEFAULT 'idea' {status_check},
            rejection_reason TEXT,  -- Required when status='rejected'

            -- Conversion tracking
            converted_to_work_item_id INTEGER,
            converted_at TIMESTAMP,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (converted_to_work_item_id) REFERENCES work_items(id) ON DELETE SET NULL,

            -- Conversion constraint: converted_to_work_item_id requires status='converted'
            CHECK (
                (status = 'converted' AND converted_to_work_item_id IS NOT NULL AND converted_at IS NOT NULL) OR
                (status != 'converted')
            )
        )
    """)


def _create_document_references_table(conn: sqlite3.Connection) -> None:
    """Create document_references table with enum-driven constraints"""
    entity_type_check = generate_check_constraint(EntityType, 'entity_type')
    document_type_check = generate_check_constraint(DocumentType, 'document_type')
    format_check = generate_check_constraint(DocumentFormat, 'format')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS document_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL {entity_type_check},
            entity_id INTEGER NOT NULL,

            -- Document details
            file_path TEXT NOT NULL,
            document_type TEXT {document_type_check},
            title TEXT,
            description TEXT,

            -- Metadata
            file_size_bytes INTEGER,
            content_hash TEXT,
            format TEXT {format_check},

            -- Attribution
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Constraints
            CHECK (entity_id > 0),
            CHECK (file_path IS NOT NULL AND length(file_path) > 0)
        )
    """)


def _create_session_events_table(conn: sqlite3.Connection) -> None:
    """Create session_events table with enum-driven constraints"""
    event_type_check = generate_check_constraint(EventType, 'event_type')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS session_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,

            -- Event classification
            event_type TEXT NOT NULL {event_type_check},
            event_category TEXT NOT NULL CHECK(event_category IN (
                'workflow', 'tool_usage', 'decision', 'reasoning', 'error', 'session'
            )),
            event_severity TEXT NOT NULL DEFAULT 'info' CHECK(event_severity IN (
                'debug', 'info', 'warning', 'error', 'critical'
            )),

            -- Session context
            session_id INTEGER,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,

            -- Event payload
            event_data TEXT NOT NULL,

            -- Optional entity references
            work_item_id INTEGER,
            task_id INTEGER,

            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)


def _create_evidence_sources_table(conn: sqlite3.Connection) -> None:
    """Create evidence_sources table with enum-driven constraints"""
    entity_type_check = generate_check_constraint(EntityType, 'entity_type')
    source_type_check = generate_check_constraint(SourceType, 'source_type')

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS evidence_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL {entity_type_check},
            entity_id INTEGER NOT NULL,

            -- Evidence details
            url TEXT,
            source_type TEXT {source_type_check},
            excerpt TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Verification
            content_hash TEXT,
            confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            created_by TEXT,

            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (entity_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)


def _create_sessions_table(conn: sqlite3.Connection) -> None:
    """Create sessions table with inline CHECK constraints"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            project_id INTEGER NOT NULL,

            -- Tool identification
            tool_name TEXT NOT NULL CHECK(tool_name IN (
                'claude-code', 'cursor', 'windsurf', 'aider', 'manual', 'other'
            )),
            llm_model TEXT CHECK(llm_model IN (
                'claude-sonnet-4-5', 'claude-opus-4', 'gpt-4', 'gpt-4-turbo',
                'gpt-4o', 'gemini-pro', 'gemini-ultra', 'deepseek', 'other'
            )),
            tool_version TEXT,

            -- Lifecycle
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration_minutes INTEGER CHECK(duration_minutes >= 0),
            status TEXT DEFAULT 'active' CHECK(status IN (
                'active', 'paused', 'completed', 'abandoned'
            )),
            session_type TEXT DEFAULT 'coding' CHECK(session_type IN (
                'coding', 'review', 'planning', 'research', 'debugging'
            )),
            exit_reason TEXT,

            -- Developer
            developer_name TEXT,
            developer_email TEXT,

            -- Metadata (JSON)
            metadata TEXT DEFAULT '{}',

            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)


def _create_agent_relationships_table(conn: sqlite3.Connection) -> None:
    """Create agent_relationships table with inline CHECK constraints"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            related_agent_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL CHECK(relationship_type IN (
                'collaborates_with', 'reports_to', 'delegates_to', 'consults_with',
                'reviews_for', 'mentors', 'specializes_in', 'handles_escalation'
            )),
            metadata TEXT DEFAULT '{}',  -- JSON metadata

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            FOREIGN KEY (related_agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            UNIQUE(agent_id, related_agent_id, relationship_type)
        )
    """)


def _create_agent_tools_table(conn: sqlite3.Connection) -> None:
    """Create agent_tools table with inline CHECK constraints"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            phase TEXT NOT NULL CHECK(phase IN (
                'analysis', 'design', 'implementation', 'testing', 'deployment', 'maintenance'
            )),
            tool_name TEXT NOT NULL,
            priority INTEGER DEFAULT 1 CHECK(priority >= 1 AND priority <= 5),
            config TEXT DEFAULT '{}',  -- JSON configuration

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            UNIQUE(agent_id, phase, tool_name)
        )
    """)


def _create_task_dependencies_table(conn: sqlite3.Connection) -> None:
    """Create task_dependencies table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            depends_on_task_id INTEGER NOT NULL,
            dependency_type TEXT DEFAULT 'hard' CHECK(dependency_type IN ('hard', 'soft')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            UNIQUE(task_id, depends_on_task_id)
        )
    """)


def _create_task_blockers_table(conn: sqlite3.Connection) -> None:
    """Create task_blockers table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_blockers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            blocker_type TEXT NOT NULL CHECK(blocker_type IN ('task', 'external')),

            -- Task blocker fields
            blocker_task_id INTEGER,

            -- External blocker fields
            blocker_description TEXT,
            blocker_reference TEXT,

            -- Resolution tracking
            is_resolved INTEGER DEFAULT 0,
            resolved_at TIMESTAMP,
            resolution_notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (blocker_task_id) REFERENCES tasks(id) ON DELETE CASCADE,

            CHECK (
                (blocker_type = 'task' AND blocker_task_id IS NOT NULL) OR
                (blocker_type = 'external' AND blocker_description IS NOT NULL)
            )
        )
    """)


def _create_work_item_dependencies_table(conn: sqlite3.Connection) -> None:
    """Create work_item_dependencies table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS work_item_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,
            depends_on_work_item_id INTEGER NOT NULL,
            dependency_type TEXT DEFAULT 'hard' CHECK(dependency_type IN ('hard', 'soft')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            FOREIGN KEY (depends_on_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            UNIQUE(work_item_id, depends_on_work_item_id)
        )
    """)


def _create_work_item_summaries_table(conn: sqlite3.Connection) -> None:
    """Create work_item_summaries table for session-level context"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS work_item_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,

            -- Session identification
            session_date TEXT NOT NULL CHECK(session_date IS date(session_date)),
            session_duration_hours REAL CHECK(session_duration_hours IS NULL OR session_duration_hours >= 0),

            -- Summary content
            summary_text TEXT NOT NULL,
            context_metadata TEXT,  -- JSON blob

            -- Attribution
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            created_by TEXT,
            summary_type TEXT DEFAULT 'session' CHECK(summary_type IN ('session', 'milestone', 'decision', 'retrospective')),

            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)


def _create_schema_migrations_table(conn: sqlite3.Connection) -> None:
    """Create schema_migrations table with rollback tracking"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rollback_at TIMESTAMP DEFAULT NULL,
            rollback_reason TEXT DEFAULT NULL,
            applied_by TEXT DEFAULT NULL
        )
    """)


def _create_indexes(conn: sqlite3.Connection) -> None:
    """Create all performance indexes"""

    # Projects indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")

    # Work items indexes (5)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_parent ON work_items(parent_work_item_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_type ON work_items(type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_work_items_priority ON work_items(priority)")

    # Tasks indexes (6)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_work_item ON tasks(work_item_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_blocked ON tasks(status) WHERE status = 'blocked'")

    # Agents indexes (4)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_project ON agents(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_role ON agents(project_id, role)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type)")

    # Contexts indexes (3)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_project ON contexts(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(context_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contexts_entity ON contexts(entity_type, entity_id)")

    # Rules indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rules_project ON rules(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rules_enforcement ON rules(enforcement_level)")

    # Task dependencies indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_deps_task ON task_dependencies(task_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_deps_depends ON task_dependencies(depends_on_task_id)")

    # Task blockers indexes (3)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_blockers_task ON task_blockers(task_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_blockers_blocker ON task_blockers(blocker_task_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_blockers_resolved ON task_blockers(is_resolved)")

    # Work item dependencies indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wi_deps_wi ON work_item_dependencies(work_item_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wi_deps_depends ON work_item_dependencies(depends_on_work_item_id)")

    # Work item summaries indexes (3)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wi_summaries_wi ON work_item_summaries(work_item_id, session_date DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wi_summaries_date ON work_item_summaries(session_date DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wi_summaries_type ON work_item_summaries(work_item_id, summary_type, session_date DESC)")

    # Session events indexes (4)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_events_session ON session_events(session_id, timestamp DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_events_type ON session_events(event_type, timestamp DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_events_category ON session_events(event_category, timestamp DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_events_entity ON session_events(work_item_id, task_id, timestamp DESC)")

    # Agent relationships indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_relationships_agent ON agent_relationships(agent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_relationships_related ON agent_relationships(related_agent_id)")

    # Agent tools indexes (2)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_tools_agent ON agent_tools(agent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_tools_phase ON agent_tools(phase, priority)")


def _create_triggers(conn: sqlite3.Connection) -> None:
    """Create triggers for workflow automation"""

    # Trigger 1: Auto-resolve blockers when blocker task completes
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS auto_resolve_task_blockers
        AFTER UPDATE OF status ON tasks
        WHEN NEW.status IN ('completed', 'cancelled', 'archived')
        BEGIN
            UPDATE task_blockers
            SET is_resolved = 1,
                resolved_at = CURRENT_TIMESTAMP,
                resolution_notes = 'Blocker task ' || NEW.id || ' ' || NEW.status
            WHERE blocker_task_id = NEW.id
              AND is_resolved = 0;
        END;
    """)

    # Trigger 2: Set started_at when task moves to in_progress
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS set_task_started_at
        AFTER UPDATE OF status ON tasks
        WHEN NEW.status = 'in_progress' AND OLD.status != 'in_progress' AND NEW.started_at IS NULL
        BEGIN
            UPDATE tasks
            SET started_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 3: Set completed_at when task completes
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS set_task_completed_at
        AFTER UPDATE OF status ON tasks
        WHEN NEW.status = 'completed' AND OLD.status != 'completed' AND NEW.completed_at IS NULL
        BEGIN
            UPDATE tasks
            SET completed_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 4: Clear blocked_reason when unblocking
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS clear_blocked_reason
        AFTER UPDATE OF status ON tasks
        WHEN OLD.status = 'blocked' AND NEW.status != 'blocked'
        BEGIN
            UPDATE tasks
            SET blocked_reason = NULL
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 5: Automatically set updated_at on any task change
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_task_timestamp
        AFTER UPDATE ON tasks
        BEGIN
            UPDATE tasks
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 6: Automatically set updated_at on work item change
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_work_item_timestamp
        AFTER UPDATE ON work_items
        BEGIN
            UPDATE work_items
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 7: Automatically set updated_at on project change
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_project_timestamp
        AFTER UPDATE ON projects
        BEGIN
            UPDATE projects
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

    # Trigger 8: Automatically set updated_at on agent change
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS agents_updated_at
        AFTER UPDATE ON agents
        FOR EACH ROW
        BEGIN
            UPDATE agents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
