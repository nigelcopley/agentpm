# APM Database Schema Reference

> **Database-First Architecture**: Production-ready SQLite database with type-safe Pydantic models
>
> **Location**: `.agentpm/data/agentpm.db`
> **Pattern**: Three-layer architecture (Models → Adapters → Methods)
> **Coverage**: 93% test coverage
> **Last Updated**: 2025-10-25

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Three-Layer Architecture](#three-layer-architecture)
3. [Core Tables](#core-tables)
4. [Entity Relationships](#entity-relationships)
5. [Migration System](#migration-system)
6. [Full Table Reference](#full-table-reference)
7. [Common Query Patterns](#common-query-patterns)
8. [Database Maintenance](#database-maintenance)

---

## Schema Overview

APM uses **SQLite** with a **database-first architecture** where the database is the single source of truth for all operational data.

### Database Statistics

- **Total Tables**: 57 (33 entity tables + 24 FTS5 indexes)
- **Core Entity Tables**: 18
- **Relationship Tables**: 5
- **Full-Text Search Tables**: 6 (+ FTS5 internals)
- **Size**: Typically 5-20 MB for active projects
- **Location**: `.agentpm/data/agentpm.db`

### Design Principles

1. **Type Safety**: All tables backed by Pydantic models with validation
2. **Referential Integrity**: Foreign keys enforce relationship constraints
3. **Denormalization**: Strategic duplication (e.g., `phase` in tasks) for query performance
4. **JSON Flexibility**: Structured metadata fields for extensibility
5. **Full-Text Search**: FTS5 indexes on key text fields
6. **Migration-Based Evolution**: All schema changes via versioned migrations

---

## Three-Layer Architecture

APM follows a strict three-layer pattern separating concerns:

```
┌─────────────────────────────────────────────┐
│  Layer 3: Database Methods                  │
│  agentpm/core/database/methods/             │
│  - CRUD operations (create, read, update)   │
│  - Business logic (state transitions)       │
│  - Query optimization                       │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│  Layer 2: Database Adapters                 │
│  agentpm/core/database/adapters/            │
│  - Pydantic ↔ SQLite conversion             │
│  - Enum serialization                       │
│  - JSON encoding/decoding                   │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│  Layer 1: Pydantic Models                   │
│  agentpm/core/database/models/              │
│  - Type-safe domain models                  │
│  - Field validation (min_length, ge, le)    │
│  - Business rule enforcement                │
└─────────────────────────────────────────────┘
```

### Layer 1: Pydantic Models

**Purpose**: Type-safe domain models with validation

**Location**: `agentpm/core/database/models/`

**Example**:
```python
from pydantic import BaseModel, Field
from agentpm.core.database.enums import TaskStatus

class Task(BaseModel):
    """Task domain model with validation"""

    id: Optional[int] = None
    work_item_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.DRAFT
    effort_hours: Optional[float] = Field(None, ge=0, le=8)

    class Config:
        validate_assignment = True  # Validate on updates
```

**Benefits**:
- Runtime validation (invalid data rejected before database)
- IDE autocomplete and type checking
- Self-documenting field constraints
- Separation of domain logic from database logic

### Layer 2: Database Adapters

**Purpose**: Convert between Pydantic models and SQLite rows

**Location**: `agentpm/core/database/adapters/`

**Example**:
```python
class TaskAdapter:
    """Convert Task model to/from SQLite"""

    @staticmethod
    def to_dict(task: Task) -> Dict[str, Any]:
        """Pydantic → SQLite dictionary"""
        return {
            'id': task.id,
            'work_item_id': task.work_item_id,
            'name': task.name,
            'status': task.status.value,  # Enum → string
            'effort_hours': task.effort_hours
        }

    @staticmethod
    def from_row(row: sqlite3.Row) -> Task:
        """SQLite row → Pydantic model"""
        return Task(
            id=row['id'],
            work_item_id=row['work_item_id'],
            name=row['name'],
            status=TaskStatus(row['status']),  # String → Enum
            effort_hours=row['effort_hours']
        )
```

**Benefits**:
- Clean separation of concerns
- Consistent conversion logic
- Easy to test in isolation
- Handles type coercion (datetime, enums, JSON)

### Layer 3: Database Methods

**Purpose**: Type-safe CRUD operations with business logic

**Location**: `agentpm/core/database/methods/`

**Example**:
```python
class TaskMethods:
    """Task database operations"""

    def create(self, db: DatabaseService, task: Task) -> Task:
        """Create task with validation"""
        data = TaskAdapter.to_dict(task)

        cursor = db.execute(
            """INSERT INTO tasks (work_item_id, name, status, effort_hours)
               VALUES (?, ?, ?, ?)""",
            (data['work_item_id'], data['name'], data['status'], data['effort_hours'])
        )

        task.id = cursor.lastrowid
        task.created_at = datetime.now()
        return task

    def get(self, db: DatabaseService, task_id: int) -> Optional[Task]:
        """Retrieve task by ID"""
        row = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        return TaskAdapter.from_row(row) if row else None
```

**Benefits**:
- Type-safe interfaces (Task in, Task out)
- Business logic encapsulation
- Transaction management
- Query optimization in one place

---

## Core Tables

### Hierarchy Overview

```
projects (top-level organizational unit)
  ├── work_items (features, objectives, research)
  │     ├── tasks (atomic units of work)
  │     │     ├── task_dependencies (task → task relationships)
  │     │     └── task_blockers (blocking issues)
  │     ├── work_item_dependencies (work item → work item relationships)
  │     └── summaries (progress tracking)
  ├── ideas (lightweight brainstorming)
  │     └── idea_elements (structured breakdown)
  ├── contexts (6W framework data)
  ├── agents (AI assistants with SOPs)
  ├── rules (governance enforcement)
  ├── sessions (development sessions)
  ├── evidence_sources (research traceability)
  └── document_references (file tracking)
```

### Primary Entity Tables

| Table | Purpose | Key Fields | Row Count (typical) |
|-------|---------|------------|---------------------|
| `projects` | Top-level organizational unit | name, path, status, tech_stack | 1-10 |
| `work_items` | Features, analyses, objectives | name, type, status, phase | 50-500 |
| `tasks` | Atomic units of work | name, type, status, effort_hours | 200-2000 |
| `agents` | AI assistants with roles/SOPs | role, display_name, sop_content | 20-50 |
| `ideas` | Brainstorming before work items | title, votes, status | 10-100 |
| `contexts` | 6W framework data | entity_type, entity_id, six_w | 50-200 |
| `rules` | Governance enforcement | rule_id, enforcement_level | 30-100 |
| `sessions` | Development session tracking | session_id, tool, started_at | 100-1000 |

### Supporting Tables

| Table | Purpose | Relationships |
|-------|---------|---------------|
| `task_dependencies` | Task prerequisites | tasks.id ← → tasks.id |
| `task_blockers` | Blocking issues | tasks.id → tasks.id (optional) |
| `work_item_dependencies` | Work item prerequisites | work_items.id ← → work_items.id |
| `evidence_sources` | Research traceability | Polymorphic: project/work_item/task |
| `document_references` | File metadata | Polymorphic: project/work_item/task |
| `summaries` | Progress tracking | Polymorphic: project/session/work_item/task |
| `idea_elements` | Idea structured breakdown | ideas.id |

### Full-Text Search Tables

APM uses **SQLite FTS5** for high-performance text search:

| FTS5 Table | Indexed Content | Use Case |
|------------|-----------------|----------|
| `search_index` | All searchable entities | Unified search across projects |
| `document_content_fts` | Document file content | Search within documentation |
| `summaries_fts` | Summary text | Find summaries by keyword |
| `evidence_fts` | Evidence excerpts | Research source lookup |
| `sessions_fts` | Session metadata | Session search and filtering |

---

## Entity Relationships

### ER Diagram (Text Format)

```
┌─────────────┐
│  projects   │
│  (id)       │
└─────┬───────┘
      │
      │ 1:N (project_id FK)
      │
      ├─────────────────────────────────────────────────────────────┐
      │                                                               │
      ▼                                                               ▼
┌─────────────┐                                               ┌─────────────┐
│ work_items  │                                               │    ideas    │
│ (id)        │                                               │ (id)        │
└─────┬───────┘                                               └─────┬───────┘
      │                                                               │
      │ 1:N (work_item_id FK)                                        │ 1:N
      │                                                               │
      ▼                                                               ▼
┌─────────────┐                                         ┌──────────────────┐
│    tasks    │                                         │  idea_elements   │
│    (id)     │                                         │                  │
└─────┬───────┘                                         └──────────────────┘
      │
      │ Self-referencing (task_id → depends_on_task_id)
      │
      ├────────────────────────┬──────────────────────┐
      │                        │                      │
      ▼                        ▼                      ▼
┌────────────────┐   ┌─────────────────┐   ┌────────────────┐
│task_dependencies│   │ task_blockers   │   │work_item_deps  │
│                │   │                 │   │                │
└────────────────┘   └─────────────────┘   └────────────────┘

Polymorphic Relationships (entity_type + entity_id):
  - contexts → project | work_item | task
  - evidence_sources → project | work_item | task
  - document_references → project | work_item | task
  - summaries → project | session | work_item | task
  - events → project | work_item | task | agent | rule
```

### Key Relationships

**Projects ↔ Work Items** (One-to-Many)
```sql
-- Foreign Key Constraint
work_items.project_id → projects.id (ON DELETE CASCADE)

-- Example: Get all work items for a project
SELECT * FROM work_items WHERE project_id = ?
```

**Work Items ↔ Tasks** (One-to-Many)
```sql
-- Foreign Key Constraint
tasks.work_item_id → work_items.id (ON DELETE CASCADE)

-- Example: Get all tasks for a work item
SELECT * FROM tasks WHERE work_item_id = ?
```

**Tasks ↔ Task Dependencies** (Self-Referencing Many-to-Many)
```sql
-- Foreign Key Constraints
task_dependencies.task_id → tasks.id
task_dependencies.depends_on_task_id → tasks.id

-- Example: Get all dependencies for a task
SELECT t.* FROM tasks t
JOIN task_dependencies td ON t.id = td.depends_on_task_id
WHERE td.task_id = ?
```

**Polymorphic Relationships** (entity_type + entity_id pattern)
```sql
-- contexts table (supports project, work_item, task)
entity_type TEXT CHECK(entity_type IN ('project', 'work_item', 'task'))
entity_id INTEGER NOT NULL

-- Example: Get context for a work item
SELECT * FROM contexts
WHERE entity_type = 'work_item' AND entity_id = ?
```

### Referential Integrity

**Cascade Deletions**:
```sql
-- When a project is deleted:
projects.id → work_items.project_id (CASCADE)
  → tasks.work_item_id (CASCADE)
    → task_dependencies (CASCADE)
    → task_blockers (CASCADE)
  → work_item_dependencies (CASCADE)

-- Polymorphic entities (contexts, evidence_sources, etc.) are NOT cascaded
-- (must be explicitly handled in application logic)
```

**Check Constraints**:
```sql
-- Status validation
status CHECK(status IN ('draft', 'validated', 'accepted', 'active', ...))

-- Effort hours validation
effort_hours CHECK(effort_hours IS NULL OR (effort_hours >= 0 AND effort_hours <= 8))

-- Dependency type validation
dependency_type CHECK(dependency_type IN ('hard', 'soft'))
```

---

## Migration System

APM uses a **versioned migration system** for schema evolution.

### Migration File Structure

**Location**: `agentpm/core/database/migrations/files/`

**Naming Convention**: `migration_NNNN[_description].py`
- `NNNN`: Zero-padded version number (0001, 0002, ..., 0043)
- `_description`: Optional human-readable description

**Example**:
```
migration_0024.py
migration_0031_documentation_system.py
migration_0039_hybrid_document_storage.py
migration_0043_fix_document_type_constraint.py
```

### Migration File Template

```python
"""
Migration NNNN: [Title]

PURPOSE:
[Why this migration is needed]

RATIONALE:
- [Design decision 1]
- [Design decision 2]

Changes:
- [Change 1]
- [Change 2]

Data Integrity:
- [Constraint 1]
- [Constraint 2]
"""

import sqlite3
from agentpm.core.database.enums import SomeEnum

DESCRIPTION = "Brief migration description"


def upgrade(conn: sqlite3.Connection) -> None:
    """Apply schema changes (forward migration)"""
    print(f"🔧 Migration NNNN: {DESCRIPTION}")

    # Step 1: Add new columns/tables
    _add_new_table(conn)

    # Step 2: Migrate existing data
    _migrate_data(conn)

    # Step 3: Add constraints/indexes
    _add_indexes(conn)

    print("✅ Migration NNNN complete")


def downgrade(conn: sqlite3.Connection) -> None:
    """Rollback schema changes (backward migration)"""
    print(f"⏪ Rolling back Migration NNNN")

    # Reverse operations (drop tables, remove columns)
    conn.execute("DROP TABLE IF EXISTS new_table")

    print("✅ Migration NNNN rolled back")


def _add_new_table(conn: sqlite3.Connection) -> None:
    """Helper: Create new table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _migrate_data(conn: sqlite3.Connection) -> None:
    """Helper: Migrate existing data"""
    # Copy data from old structure to new
    pass


def _add_indexes(conn: sqlite3.Connection) -> None:
    """Helper: Add performance indexes"""
    conn.execute("CREATE INDEX IF NOT EXISTS idx_new_table_name ON new_table(name)")
```

### Running Migrations

**Automatic (on database initialization)**:
```python
from agentpm.core.database import DatabaseService

db = DatabaseService(".agentpm/data/agentpm.db")
db.initialize_schema()  # Runs pending migrations automatically
```

**Manual (via migration manager)**:
```python
from agentpm.core.database.migrations import MigrationManager

manager = MigrationManager(db_path=".agentpm/data/agentpm.db")

# Check migration status
pending = manager.get_pending_migrations()
print(f"Pending migrations: {len(pending)}")

# Apply all pending migrations
manager.migrate()

# Rollback last migration
manager.rollback()
```

**Via CLI** (future):
```bash
# Check migration status
apm db status

# Apply pending migrations
apm db migrate

# Rollback last migration
apm db rollback

# Show migration history
apm db history
```

### Migration Tracking

Migrations are tracked in the `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Example data
INSERT INTO schema_migrations VALUES
  (24, '0024', '2025-10-15 14:23:11', 'Add phase field to tasks'),
  (31, '0031', '2025-10-18 09:14:33', 'Documentation system'),
  (39, '0039', '2025-10-22 16:45:22', 'Hybrid document storage');
```

**Query migration status**:
```sql
-- List applied migrations
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY version DESC;

-- Check if specific migration applied
SELECT EXISTS(
    SELECT 1 FROM schema_migrations WHERE version = '0039'
);
```

### Migration Best Practices

1. **Always test migrations on a copy of the database first**
2. **Include both upgrade() and downgrade() functions**
3. **Use transactions for data migrations**
4. **Add indexes AFTER bulk data operations**
5. **Document breaking changes in migration docstring**
6. **Test with real data, not empty databases**
7. **SQLite limitations**: Cannot drop columns or modify CHECK constraints
   - Workaround: Create new table, copy data, drop old, rename new

### Current Migration Version

**Latest Applied**: `0043` (Fix document type constraint)
**Total Migrations**: 43
**Database Version**: Check with:
```sql
SELECT MAX(version) FROM schema_migrations;
```

---

## Full Table Reference

### projects

**Purpose**: Top-level organizational unit for managing development projects

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique project identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Project name (must be unique) |
| `description` | TEXT | | Optional project description |
| `path` | TEXT | NOT NULL | Filesystem path to project directory |
| `tech_stack` | TEXT | DEFAULT '[]' | JSON array of detected technologies |
| `detected_frameworks` | TEXT | DEFAULT '[]' | JSON array of detected frameworks |
| `status` | TEXT | CHECK(status IN (...)) | Project lifecycle status |
| `metadata` | TEXT | DEFAULT '{}' | JSON configuration metadata |
| `business_domain` | TEXT | | Business domain (e.g., "e-commerce", "fintech") |
| `business_description` | TEXT | | Business description |
| `project_type` | TEXT | CHECK(project_type IN (...)) | Project classification |
| `team` | TEXT | | Team name |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Status Values**: `initiated`, `active`, `on_hold`, `completed`, `archived`

**Project Types**: `greenfield`, `brownfield`, `maintenance`, `research`

**Indexes**:
- `UNIQUE(name)` - Enforce unique project names

**Sample Row**:
```json
{
  "id": 1,
  "name": "AgentPM",
  "description": "AI-powered project management system",
  "path": "/Users/dev/Projects/AgentPM",
  "tech_stack": "[\"python\", \"sqlite\", \"pydantic\"]",
  "detected_frameworks": "[\"click\", \"pytest\"]",
  "status": "active",
  "business_domain": "developer-tools",
  "project_type": "greenfield",
  "team": "Core Development"
}
```

---

### work_items

**Purpose**: Features, analyses, objectives, and research units

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique work item identifier |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `parent_work_item_id` | INTEGER | FK → work_items.id | Optional parent (for breakdown) |
| `originated_from_idea_id` | INTEGER | FK → ideas.id | Originating idea (if converted) |
| `name` | TEXT | NOT NULL, max 200 chars | Work item title |
| `description` | TEXT | | Detailed description |
| `type` | TEXT | CHECK(type IN (...)) | Work item classification |
| `business_context` | TEXT | | Business rationale and value |
| `metadata` | TEXT | DEFAULT '{}' | JSON configuration metadata |
| `is_continuous` | INTEGER | DEFAULT 0 | Continuous backlog flag (never completes) |
| `effort_estimate_hours` | REAL | CHECK(effort >= 0) | Estimated effort in hours |
| `priority` | INTEGER | CHECK(priority BETWEEN 1 AND 5) | Priority level (1=highest) |
| `status` | TEXT | CHECK(status IN (...)) | Work item workflow status |
| `phase` | TEXT | CHECK(phase IN (...)) | Project phase (D1, P1, I1, R1, O1, E1) |
| `due_date` | TIMESTAMP | | Optional deadline |
| `not_before` | TIMESTAMP | | Earliest start date |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Work Item Types**: `feature`, `improvement`, `fix`, `analysis`, `objective`, `research`, `maintenance`, `monitoring`, `documentation`, `security`

**Status Values**: `draft`, `validated`, `accepted`, `active`, `review`, `done`, `archived`

**Phase Values**: `D1_discovery`, `P1_plan`, `I1_implementation`, `R1_review`, `O1_operations`, `E1_evolution`

**Indexes**:
- `idx_work_items_project` on `(project_id)`
- `idx_work_items_status` on `(status)`
- `idx_work_items_phase` on `(phase)`
- `idx_work_items_parent` on `(parent_work_item_id)`

---

### tasks

**Purpose**: Atomic units of work (typically 2-4 hours)

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique task identifier |
| `work_item_id` | INTEGER | NOT NULL, FK → work_items.id | Parent work item |
| `name` | TEXT | NOT NULL, max 200 chars | Task title |
| `description` | TEXT | | Detailed description |
| `type` | TEXT | CHECK(type IN (...)) | Task classification |
| `quality_metadata` | TEXT | | JSON quality gate tracking |
| `effort_hours` | REAL | CHECK(0 <= effort <= 8) | Estimated effort (max 8 hours) |
| `priority` | INTEGER | CHECK(priority BETWEEN 1 AND 5) | Priority level (1=highest) |
| `assigned_to` | TEXT | | Agent role or user name |
| `status` | TEXT | CHECK(status IN (...)) | Task workflow status |
| `blocked_reason` | TEXT | | Reason if status is BLOCKED |
| `phase` | TEXT | CHECK(phase IN (...)) | Denormalized from work_item (performance) |
| `due_date` | TIMESTAMP | | Optional deadline |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `started_at` | TIMESTAMP | | When moved to in_progress |
| `completed_at` | TIMESTAMP | | Completion timestamp |

**Task Types**: `design`, `implementation`, `testing`, `bugfix`, `refactoring`, `documentation`, `deployment`, `review`, `analysis`, `research`, `maintenance`, `optimization`, `integration`, `training`, `meeting`, `planning`, `dependency`, `blocker`, `simple`, `other`

**Status Values**: `draft`, `validated`, `accepted`, `active`, `blocked`, `review`, `done`, `cancelled`, `archived`

**Indexes**:
- `idx_tasks_work_item` on `(work_item_id)`
- `idx_tasks_status` on `(status)`
- `idx_tasks_assigned` on `(assigned_to)`
- `idx_tasks_phase` on `(phase)`

**Trigger**: `sync_task_phase_from_work_item` - Keeps `tasks.phase` in sync with `work_items.phase`

---

### agents

**Purpose**: AI assistants with roles and Standard Operating Procedures (SOPs)

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique agent identifier |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `role` | TEXT | NOT NULL, max 100 chars | Agent role (e.g., 'aipm-database-developer') |
| `display_name` | TEXT | NOT NULL, max 200 chars | Human-readable name |
| `description` | TEXT | | Agent purpose and responsibilities |
| `sop_content` | TEXT | | Standard Operating Procedure (markdown) |
| `capabilities` | TEXT | DEFAULT '[]' | JSON array of capabilities |
| `is_active` | INTEGER | DEFAULT 1 | Whether agent is currently active |
| `agent_type` | TEXT | | Base template type (e.g., 'implementer', 'tester') |
| `file_path` | TEXT | | Generated file path (e.g., '.claude/agents/...') |
| `generated_at` | TIMESTAMP | | When agent file was last generated |
| `tier` | TEXT | CHECK(tier IN (...)) | Agent tier (1=sub-agent, 2=specialist, 3=orchestrator) |
| `last_used_at` | TIMESTAMP | | When agent was last assigned to a task |
| `metadata` | TEXT | DEFAULT '{}' | JSON metadata |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Agent Tiers**: `tier_1_sub_agent`, `tier_2_specialist`, `tier_3_orchestrator`

**Indexes**:
- `idx_agents_project` on `(project_id)`
- `idx_agents_role` on `(role)`
- `idx_agents_tier` on `(tier)`

---

### ideas

**Purpose**: Lightweight brainstorming before work items (WI-50)

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique idea identifier |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `title` | TEXT | NOT NULL, 3-200 chars | Idea title |
| `description` | TEXT | | Detailed description |
| `source` | TEXT | CHECK(source IN (...)) | Origin of idea |
| `created_by` | TEXT | | Creator identifier (username, email, agent) |
| `votes` | INTEGER | DEFAULT 0, CHECK(votes >= 0) | Team votes (higher = more popular) |
| `tags` | TEXT | DEFAULT '[]' | JSON array of tags |
| `status` | TEXT | CHECK(status IN (...)) | Idea lifecycle state |
| `rejection_reason` | TEXT | | Required when status='rejected' |
| `converted_to_work_item_id` | INTEGER | FK → work_items.id | Set when converted |
| `converted_at` | TIMESTAMP | | Timestamp of conversion |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Idea Sources**: `user`, `ai_suggestion`, `customer_feedback`, `competitive_analysis`, `brainstorming`, `retrospective`

**Idea Status**: `idea`, `research`, `design`, `accepted`, `converted` (terminal), `rejected` (terminal)

**Indexes**:
- `idx_ideas_project` on `(project_id)`
- `idx_ideas_status` on `(status)`
- `idx_ideas_votes` on `(votes DESC)` - For popularity ranking

---

### contexts

**Purpose**: Unified 6W framework context data (WHO, WHAT, WHERE, WHEN, WHY, HOW)

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique context identifier |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `context_type` | TEXT | CHECK(context_type IN (...)) | Type of context |
| `entity_type` | TEXT | CHECK(entity_type IN (...)) | Polymorphic entity type |
| `entity_id` | INTEGER | | Polymorphic entity ID |
| `file_path` | TEXT | | For resource_file contexts |
| `file_hash` | TEXT | | SHA256 hash for change detection |
| `resource_type` | TEXT | CHECK(resource_type IN (...)) | Resource classification |
| `six_w` | TEXT | | JSON UnifiedSixW structure |
| `confidence_score` | REAL | CHECK(0.0 <= score <= 1.0) | Confidence score (0.0-1.0) |
| `confidence_band` | TEXT | CHECK(band IN (...)) | RED/YELLOW/GREEN |
| `confidence_factors` | TEXT | | JSON breakdown of scoring factors |
| `context_data` | TEXT | | JSON rich context data |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Context Types**: `resource_file`, `project_context`, `work_item_context`, `task_context`, `idea_context`, `business_pillars_context`, `market_research_context`, `competitive_analysis_context`, `quality_gates_context`, `stakeholder_context`, `technical_context`, `implementation_context`, `idea_to_work_item_mapping`

**Resource Types**: `sop`, `code`, `specification`, `documentation`

**Confidence Bands**: `RED` (<0.6), `YELLOW` (0.6-0.79), `GREEN` (≥0.8)

**Indexes**:
- `idx_contexts_entity` on `(entity_type, entity_id)` - Polymorphic lookup
- `idx_contexts_type` on `(context_type)`

---

### rules

**Purpose**: Governance rules enforcement system

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique rule identifier |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `rule_id` | TEXT | NOT NULL, pattern: XX-NNN | Unique rule ID (e.g., 'DP-001') |
| `name` | TEXT | NOT NULL, kebab-case | Machine-readable name |
| `description` | TEXT | | Human-readable explanation |
| `category` | TEXT | | Rule category (e.g., 'development_principles') |
| `enforcement_level` | TEXT | CHECK(level IN (...)) | Enforcement strictness |
| `validation_logic` | TEXT | | Pattern-based validation logic |
| `error_message` | TEXT | | Message when rule is violated |
| `config` | TEXT | | JSON rule-specific configuration |
| `enabled` | INTEGER | DEFAULT 1 | Whether rule is active |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Enforcement Levels**:
- `BLOCK`: Hard constraint (operation fails if violated)
- `LIMIT`: Soft constraint (warning but succeeds)
- `GUIDE`: Suggestion (informational only)
- `ENHANCE`: Context enrichment (no enforcement)

**Rule ID Pattern**: `[A-Z]{2,4}-\d{3}` (e.g., `DP-001`, `TEST-042`, `SEC-005`)

**Indexes**:
- `UNIQUE(project_id, rule_id)` - One rule per project

**Sample Row**:
```json
{
  "id": 1,
  "project_id": 1,
  "rule_id": "DP-001",
  "name": "time-boxing-implementation",
  "description": "IMPLEMENTATION tasks must be ≤4 hours",
  "enforcement_level": "BLOCK",
  "config": "{\"max_hours\": 4.0}",
  "enabled": 1
}
```

---

### sessions

**Purpose**: Track development sessions for analytics and handovers

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique session identifier |
| `session_id` | TEXT | NOT NULL, UNIQUE | Human-readable session ID |
| `project_id` | INTEGER | NOT NULL, FK → projects.id | Parent project |
| `status` | TEXT | CHECK(status IN (...)) | Session status |
| `session_type` | TEXT | CHECK(type IN (...)) | Session classification |
| `tool` | TEXT | CHECK(tool IN (...)) | Tool used (claude_code, cursor, cli) |
| `tool_name` | TEXT | | Tool name (legacy) |
| `tool_version` | TEXT | | Tool version |
| `llm_model` | TEXT | | LLM model if applicable |
| `metadata` | TEXT | | JSON session metadata |
| `developer_name` | TEXT | | Developer name |
| `developer_email` | TEXT | | Developer email |
| `duration_minutes` | INTEGER | | Session duration in minutes |
| `exit_reason` | TEXT | | Reason for session exit |
| `started_at` | TEXT | | Start timestamp (ISO 8601) |
| `ended_at` | TEXT | | End timestamp (ISO 8601) |
| `created_at` | TEXT | | Creation timestamp |
| `updated_at` | TEXT | | Last update timestamp |

**Session Status**: `active`, `completed`, `abandoned`

**Session Types**: `development`, `coding`, `planning`, `review`, `operations`

**Tools**: `claude_code`, `claude-code` (legacy), `cursor`, `cli`, `web_admin`

**LLM Models**: `claude-sonnet-4-5`, `claude-sonnet-3-5`, `gpt-4`, `none`

**Indexes**:
- `idx_sessions_project` on `(project_id)`
- `idx_sessions_status` on `(status)`
- FTS5: `sessions_fts` for full-text search

---

### evidence_sources

**Purpose**: Research traceability and decision rationale

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique evidence identifier |
| `entity_type` | TEXT | CHECK(entity_type IN (...)) | Polymorphic entity type |
| `entity_id` | INTEGER | NOT NULL | Polymorphic entity ID |
| `url` | TEXT | | Source URL |
| `source_type` | TEXT | CHECK(source_type IN (...)) | Source classification |
| `excerpt` | TEXT | | Key quote or summary (max 1000 chars) |
| `captured_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When evidence was captured |
| `content_hash` | TEXT | | SHA256 hash for change detection |
| `confidence` | REAL | CHECK(0.0 <= confidence <= 1.0) | Confidence in source |
| `created_by` | TEXT | | Agent or user who added evidence |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Entity Types**: `project`, `work_item`, `task`

**Source Types**: `documentation`, `research`, `meeting`, `email`, `chat`, `code_review`, `internal`

**Indexes**:
- `idx_evidence_entity` on `(entity_type, entity_id)` - Polymorphic lookup
- FTS5: `evidence_fts` on `(excerpt)` for full-text search

---

### document_references

**Purpose**: Universal documentation system file tracking

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique document identifier |
| `entity_type` | TEXT | CHECK(entity_type IN (...)) | Polymorphic entity type |
| `entity_id` | INTEGER | NOT NULL | Polymorphic entity ID |
| `category` | TEXT | | Top-level category (planning, architecture, etc.) |
| `document_type` | TEXT | CHECK(document_type IN (...)) | Document classification |
| `document_type_dir` | TEXT | | Physical subdirectory under category |
| `file_path` | TEXT | NOT NULL | Path: docs/{category}/{type}/{filename} |
| `title` | TEXT | | Human-readable title |
| `description` | TEXT | | Document description |
| `file_size_bytes` | INTEGER | CHECK(file_size >= 0) | File size in bytes |
| `content_hash` | TEXT | | SHA256 hash for change detection |
| `format` | TEXT | CHECK(format IN (...)) | Document format |
| `content` | TEXT | | Full document content (hybrid storage) |
| `filename` | TEXT | | Base filename for path construction |
| `storage_mode` | TEXT | CHECK(mode IN (...)) | Storage strategy |
| `content_updated_at` | TIMESTAMP | | When content was last modified |
| `last_synced_at` | TIMESTAMP | | When file was last synced from database |
| `sync_status` | TEXT | CHECK(sync_status IN (...)) | Synchronization state |
| `segment_type` | TEXT | | Content segment (functional, technical, business) |
| `component` | TEXT | | Related component (auth, payment, workflow) |
| `domain` | TEXT | | Business/technical domain |
| `audience` | TEXT | | Target audience (developer, user, admin) |
| `maturity` | TEXT | | Lifecycle state (draft, review, approved) |
| `priority` | TEXT | | Priority level |
| `tags` | TEXT | DEFAULT '[]' | JSON array of tags |
| `phase` | TEXT | | SDLC phase (D1, P1, I1, R1, O1, E1) |
| `work_item_id` | INTEGER | FK → work_items.id | Originating work item |
| `created_by` | TEXT | | Agent or user who created document |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Document Categories**: `planning`, `architecture`, `guides`, `references`, `processes`, `reports`, `templates`, `root`

**Document Types**: `requirements`, `design`, `user_guide`, `developer_guide`, `api_reference`, `runbook`, `adr`, `specification`, `test_plan`, `deployment_guide`, `troubleshooting`, `release_notes`

**Document Formats**: `markdown`, `text`, `json`, `yaml`, `pdf`, `image`

**Storage Modes**: `database_only`, `file_only`, `hybrid`

**Sync Status**: `synced`, `pending`, `conflict`, `error`

**Indexes**:
- `idx_doc_refs_entity` on `(entity_type, entity_id)` - Polymorphic lookup
- `idx_doc_refs_category` on `(category)`
- `idx_doc_refs_type` on `(document_type)`
- `idx_doc_refs_path` on `(file_path)`
- FTS5: `document_content_fts` on `(content)` for full-text search

---

### summaries

**Purpose**: Polymorphic summary system for all entity types

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique summary identifier |
| `entity_type` | TEXT | CHECK(entity_type IN (...)) | Polymorphic entity type |
| `entity_id` | INTEGER | NOT NULL | Polymorphic entity ID |
| `summary_type` | TEXT | CHECK(summary_type IN (...)) | Summary classification |
| `summary_text` | TEXT | NOT NULL, min 10 chars | Markdown-formatted summary content |
| `context_metadata` | TEXT | | JSON structured metadata for AI parsing |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `created_by` | TEXT | NOT NULL | Creator identifier (username, email, agent) |
| `session_id` | INTEGER | FK → sessions.id | Optional session link for traceability |
| `session_date` | TEXT | pattern: YYYY-MM-DD | Optional session date |
| `session_duration_hours` | REAL | CHECK(duration >= 0) | Optional session duration |

**Entity Types**: `project`, `session`, `work_item`, `task`

**Summary Types**:
- Session: `session_handover`, `session_progress`, `session_error_analysis`
- Work Item: `work_item_progress`, `work_item_milestone`, `work_item_decision`, `work_item_retrospective`
- Task: `task_completion`, `task_progress`, `task_blocker_resolution`
- Project: `project_strategic`, `project_milestone`, `project_retrospective`
- Legacy: `session`, `milestone`, `decision`, `retrospective`

**Indexes**:
- `idx_summaries_entity` on `(entity_type, entity_id)` - Polymorphic lookup
- `idx_summaries_type` on `(summary_type)`
- `idx_summaries_session` on `(session_id)`
- FTS5: `summaries_fts` on `(summary_text)` for full-text search

---

### Relationship Tables

#### task_dependencies

**Purpose**: Task prerequisite relationships

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Dependency ID |
| `task_id` | INTEGER | NOT NULL, FK → tasks.id | Dependent task (this task) |
| `depends_on_task_id` | INTEGER | NOT NULL, FK → tasks.id | Prerequisite task (must complete first) |
| `dependency_type` | TEXT | CHECK(type IN ('hard', 'soft')) | Dependency strictness |
| `notes` | TEXT | | Why this dependency exists |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Constraints**: `UNIQUE(task_id, depends_on_task_id)` - Prevent duplicate dependencies

#### task_blockers

**Purpose**: Task blocking issues (internal or external)

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Blocker ID |
| `task_id` | INTEGER | NOT NULL, FK → tasks.id | Blocked task |
| `blocker_type` | TEXT | CHECK(type IN ('task', 'external')) | Blocker classification |
| `blocker_task_id` | INTEGER | FK → tasks.id | Blocking task (if type='task') |
| `blocker_description` | TEXT | | External blocker description |
| `blocker_reference` | TEXT | | External reference (ticket, URL) |
| `is_resolved` | INTEGER | DEFAULT 0 | Resolution status |
| `resolved_at` | TIMESTAMP | | Resolution timestamp |
| `resolution_notes` | TEXT | | How blocker was resolved |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Check Constraint**: Either `blocker_task_id` OR `blocker_description` must be set

#### work_item_dependencies

**Purpose**: Work item prerequisite relationships

**Columns**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Dependency ID |
| `work_item_id` | INTEGER | NOT NULL, FK → work_items.id | Dependent work item |
| `depends_on_work_item_id` | INTEGER | NOT NULL, FK → work_items.id | Prerequisite work item |
| `dependency_type` | TEXT | CHECK(type IN ('hard', 'soft')) | Dependency strictness |
| `notes` | TEXT | | Why this dependency exists |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Constraints**: `UNIQUE(work_item_id, depends_on_work_item_id)` - Prevent duplicate dependencies

---

## Common Query Patterns

### Hierarchical Queries

**Get all work items and tasks for a project**:
```sql
-- Work items
SELECT * FROM work_items
WHERE project_id = ?
ORDER BY priority ASC, created_at DESC;

-- Tasks for all work items in project
SELECT t.*
FROM tasks t
JOIN work_items wi ON t.work_item_id = wi.id
WHERE wi.project_id = ?
ORDER BY wi.priority, t.priority;
```

**Get task dependency tree**:
```sql
-- Direct dependencies
SELECT t.*
FROM tasks t
JOIN task_dependencies td ON t.id = td.depends_on_task_id
WHERE td.task_id = ?;

-- Recursive dependency tree (requires CTE in application logic)
-- SQLite supports recursive CTEs:
WITH RECURSIVE task_tree AS (
  SELECT id, name, work_item_id, 0 as depth
  FROM tasks
  WHERE id = ?

  UNION ALL

  SELECT t.id, t.name, t.work_item_id, tt.depth + 1
  FROM tasks t
  JOIN task_dependencies td ON t.id = td.depends_on_task_id
  JOIN task_tree tt ON td.task_id = tt.id
  WHERE tt.depth < 10  -- Prevent infinite loops
)
SELECT * FROM task_tree;
```

### Polymorphic Entity Queries

**Get all contexts for a work item**:
```sql
SELECT * FROM contexts
WHERE entity_type = 'work_item' AND entity_id = ?;
```

**Get all evidence for a task**:
```sql
SELECT * FROM evidence_sources
WHERE entity_type = 'task' AND entity_id = ?
ORDER BY confidence DESC;
```

**Get all documents for any entity**:
```sql
SELECT * FROM document_references
WHERE entity_type = ? AND entity_id = ?
ORDER BY created_at DESC;
```

### Status and Phase Filtering

**Get all active work items in I1 phase**:
```sql
SELECT * FROM work_items
WHERE status = 'active'
  AND phase = 'I1_implementation'
ORDER BY priority ASC;
```

**Get all blocked tasks**:
```sql
SELECT t.*, b.blocker_description
FROM tasks t
LEFT JOIN task_blockers b ON t.id = b.task_id AND b.is_resolved = 0
WHERE t.status = 'blocked'
ORDER BY t.priority ASC;
```

**Get tasks ready to work (no blockers, no unmet dependencies)**:
```sql
SELECT t.*
FROM tasks t
WHERE t.status = 'accepted'
  AND NOT EXISTS (
    SELECT 1 FROM task_blockers b
    WHERE b.task_id = t.id AND b.is_resolved = 0
  )
  AND NOT EXISTS (
    SELECT 1 FROM task_dependencies td
    JOIN tasks dep ON td.depends_on_task_id = dep.id
    WHERE td.task_id = t.id
      AND dep.status NOT IN ('done', 'cancelled')
  )
ORDER BY t.priority ASC;
```

### Full-Text Search

**Search across all documents**:
```sql
SELECT d.id, d.title, d.file_path,
       snippet(document_content_fts, 0, '<mark>', '</mark>', '...', 64) as snippet
FROM document_content_fts fts
JOIN document_references d ON fts.rowid = d.id
WHERE document_content_fts MATCH 'database schema'
ORDER BY rank
LIMIT 20;
```

**Search summaries**:
```sql
SELECT s.id, s.summary_type, s.entity_type, s.entity_id,
       snippet(summaries_fts, 0, '<mark>', '</mark>', '...', 64) as snippet
FROM summaries_fts fts
JOIN summaries s ON fts.rowid = s.id
WHERE summaries_fts MATCH 'migration'
ORDER BY rank
LIMIT 20;
```

### Aggregation Queries

**Work item progress summary**:
```sql
SELECT
  wi.id,
  wi.name,
  COUNT(t.id) as total_tasks,
  SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_tasks,
  SUM(CASE WHEN t.status = 'active' THEN 1 ELSE 0 END) as active_tasks,
  SUM(CASE WHEN t.status = 'blocked' THEN 1 ELSE 0 END) as blocked_tasks,
  ROUND(100.0 * SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as completion_percentage
FROM work_items wi
LEFT JOIN tasks t ON wi.id = t.work_item_id
WHERE wi.project_id = ?
GROUP BY wi.id, wi.name
ORDER BY wi.priority ASC;
```

**Agent workload**:
```sql
SELECT
  assigned_to as agent,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_tasks,
  SUM(effort_hours) as total_effort_hours
FROM tasks
WHERE assigned_to IS NOT NULL
  AND status NOT IN ('done', 'cancelled', 'archived')
GROUP BY assigned_to
ORDER BY total_effort_hours DESC;
```

---

## Database Maintenance

### Backup

**Manual backup**:
```bash
# Copy database file
cp .agentpm/data/agentpm.db .agentpm/data/agentpm_backup_$(date +%Y%m%d).db

# SQLite backup command (better for active databases)
sqlite3 .agentpm/data/agentpm.db ".backup .agentpm/data/agentpm_backup.db"
```

**Automated backup** (future):
```bash
apm db backup
apm db backup --compress
apm db restore backup_20251025.db
```

### Vacuum and Optimization

**Reclaim unused space**:
```sql
-- Rebuild database to reclaim space
VACUUM;

-- Analyze for query optimizer statistics
ANALYZE;
```

**Rebuild FTS5 indexes**:
```sql
-- If full-text search becomes slow
INSERT INTO document_content_fts(document_content_fts) VALUES('rebuild');
INSERT INTO summaries_fts(summaries_fts) VALUES('rebuild');
INSERT INTO evidence_fts(evidence_fts) VALUES('rebuild');
```

### Integrity Checks

**Check database integrity**:
```sql
PRAGMA integrity_check;
-- Should return: ok

PRAGMA foreign_key_check;
-- Should return empty (no FK violations)
```

**Check for orphaned records**:
```sql
-- Tasks without work items
SELECT t.* FROM tasks t
LEFT JOIN work_items wi ON t.work_item_id = wi.id
WHERE wi.id IS NULL;

-- Work items without projects
SELECT wi.* FROM work_items wi
LEFT JOIN projects p ON wi.project_id = p.id
WHERE p.id IS NULL;
```

### Performance Monitoring

**Check index usage**:
```sql
-- List all indexes
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type = 'index'
ORDER BY tbl_name, name;

-- Explain query plan
EXPLAIN QUERY PLAN
SELECT * FROM tasks WHERE work_item_id = 42;
```

**Database statistics**:
```sql
-- Table sizes
SELECT
  name,
  (SELECT COUNT(*) FROM sqlite_master sm WHERE sm.tbl_name = m.name AND sm.type = 'table') as row_count
FROM sqlite_master m
WHERE m.type = 'table'
ORDER BY name;

-- Database file size
SELECT page_count * page_size as size_bytes
FROM pragma_page_count(), pragma_page_size();
```

---

## Appendix: Enum Values Reference

### Status Enums

**ProjectStatus**:
- `initiated` - Project created, initial setup
- `active` - Active development
- `on_hold` - Temporarily paused
- `completed` - Development complete
- `archived` - No longer active

**WorkItemStatus**:
- `draft` - Initial creation
- `validated` - Requirements validated
- `accepted` - Ready for work
- `active` - In progress
- `review` - Under review
- `done` - Completed
- `archived` - Historical record

**TaskStatus**:
- `draft` - Initial creation
- `validated` - Requirements validated
- `accepted` - Ready to start
- `active` - Currently being worked on
- `blocked` - Cannot proceed (see blocker)
- `review` - Under review
- `done` - Completed successfully
- `cancelled` - Abandoned
- `archived` - Historical record

**IdeaStatus**:
- `idea` - Initial brainstorm
- `research` - Under investigation
- `design` - Being designed
- `accepted` - Approved for conversion
- `converted` - Converted to work item (terminal)
- `rejected` - Not pursuing (terminal)

### Type Enums

**WorkItemType**:
- `feature` - New functionality
- `improvement` - Enhancement to existing feature
- `fix` - Bug fix or correction
- `analysis` - Research or investigation
- `objective` - Goal or milestone
- `research` - Exploration or study
- `maintenance` - Ongoing upkeep
- `monitoring` - System monitoring
- `documentation` - Documentation work
- `security` - Security enhancement

**TaskType**:
- `design` - Design work
- `implementation` - Code implementation
- `testing` - Test creation/execution
- `bugfix` - Bug fix
- `refactoring` - Code refactoring
- `documentation` - Documentation
- `deployment` - Deployment tasks
- `review` - Code/design review
- `analysis` - Analysis work
- `research` - Research task
- `maintenance` - Maintenance
- `optimization` - Performance optimization
- `integration` - System integration
- `training` - Training/learning
- `meeting` - Meeting/discussion
- `planning` - Planning activity
- `dependency` - External dependency
- `blocker` - Blocking issue
- `simple` - Simple task
- `other` - Miscellaneous

**Phase**:
- `D1_discovery` - Requirements discovery
- `P1_plan` - Planning and design
- `I1_implementation` - Development
- `R1_review` - Review and QA
- `O1_operations` - Deployment and operations
- `E1_evolution` - Continuous improvement

**ProjectType**:
- `greenfield` - New project from scratch
- `brownfield` - Existing codebase
- `maintenance` - Maintenance mode
- `research` - Research project

---

**End of Database Schema Reference**

For implementation examples and usage patterns, see:
- `agentpm/core/database/README.md` - Implementation guide
- `agentpm/core/database/models/` - Pydantic model source code
- `tests/core/database/` - Comprehensive test examples
