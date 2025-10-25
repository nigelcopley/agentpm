# APM (Agent Project Manager) API Reference Index

**Version:** 1.0
**Last Updated:** 2025-10-21
**API Version:** 2.0.0

---

## Overview

This document provides a comprehensive index of all APM (Agent Project Manager) APIs across CLI, REST, and Python SDK interfaces.

**API Surfaces:**
- **CLI Commands:** 101 commands across 12 groups
- **REST API:** 77 endpoints (Flask web interface)
- **Python SDK:** Direct access to core methods
- **Provider APIs:** Multi-LLM integration interfaces

---

## Table of Contents

1. [CLI Commands Reference](#cli-commands-reference)
2. [REST API Endpoints](#rest-api-endpoints)
3. [Python SDK Usage](#python-sdk-usage)
4. [Provider Interfaces](#provider-interfaces)
5. [Database Schema Reference](#database-schema-reference)

---

## CLI Commands Reference

### Command Groups (12 Groups, 101 Commands)

#### Work Item Commands (16 commands)

**Lifecycle Management:**
```bash
apm work-item create <name> --type=<type> [options]
    # Create new work item
    # Options: --business-context, --acceptance-criteria, --priority

apm work-item list [--status=<status>] [--type=<type>] [--phase=<phase>]
    # List work items with optional filtering

apm work-item show <id>
    # Display work item details

apm work-item update <id> [options]
    # Update work item metadata
    # Options: --name, --business-context, --priority

apm work-item next <id>
    # Advance work item to next phase/status
```

**Phase & Status Management:**
```bash
apm work-item validate <id>
    # Transition: DRAFT → READY

apm work-item accept <id> --agent <role>
    # Transition: READY → ACTIVE (requires agent assignment)

apm work-item start <id>
    # Start active work on work item

apm work-item submit-review <id>
    # Transition: ACTIVE → REVIEW

apm work-item approve <id>
    # Transition: REVIEW → DONE

apm work-item request-changes <id> --reason <reason>
    # Transition: REVIEW → ACTIVE (rework)
```

**Additional Operations:**
```bash
apm work-item add-summary <id> --content <content> --summary-type <type>
    # Add progress summary

apm work-item show-history <id>
    # Display work item history

apm work-item types
    # List available work item types

apm work-item phase-status <id>
    # Show current phase and status

apm work-item phase-validate <id>
    # Validate phase gate requirements
```

**Dependency Management:**
```bash
apm work-item add-dependency <id> --depends-on <other_id>
apm work-item list-dependencies <id>
apm work-item remove-dependency <id> --depends-on <other_id>
```

#### Task Commands (13 commands)

**Lifecycle Management:**
```bash
apm task create <name> --work-item-id=<id> --type=<type> [options]
    # Create new task
    # Options: --effort-hours, --assigned-to, --due-date

apm task list [--work-item-id=<id>] [--status=<status>] [--type=<type>]
    # List tasks with optional filtering

apm task show <id>
    # Display task details

apm task update <id> [options]
    # Update task metadata

apm task next <id>
    # Advance task to next status
```

**State Transitions:**
```bash
apm task validate <id>
    # Transition: DRAFT → READY

apm task accept <id> --agent <role>
    # Transition: READY → ACTIVE

apm task start <id>
    # Start active work

apm task submit-review <id>
    # Transition: ACTIVE → REVIEW

apm task approve <id>
    # Transition: REVIEW → DONE

apm task request-changes <id> --reason <reason>
    # Transition: REVIEW → ACTIVE (rework)

apm task complete <id>
    # Mark task as complete
```

**Additional:**
```bash
apm task types
    # List available task types
```

#### Idea Commands (10 commands)

```bash
apm idea create <title> --description <desc> [--tags <tags>]
apm idea list [--status=<status>]
apm idea show <id>
apm idea convert <id> --to-work-item
apm idea update <id> [options]
apm idea vote <id> --score <1-5>
apm idea reject <id> --reason <reason>
apm idea next <id>
apm idea context <id>
apm idea transition <id> --to-status <status>
```

#### Session Commands (8 commands)

```bash
apm session start <name> [--duration=<minutes>]
apm session show <id>
apm session status
apm session end [<id>]
apm session update <id> [options]
apm session add-decision <id> --content <content>
apm session add-next-step <id> --content <content>
apm session history [--limit=<n>]
```

#### Document Commands (7 commands)

```bash
apm document add <file-path> --entity-type=<type> --entity-id=<id>
apm document list [--entity-type=<type>] [--entity-id=<id>]
apm document show <id>
apm document update <id> [options]
apm document delete <id>
apm document types
apm document migrate [options]  # Migrate v1 documents
```

#### Agent Commands (7 commands)

```bash
apm agents list [--tier=<1|2|3>] [--show-files]
apm agents show <role>
apm agents validate [--file=<path>]
apm agents generate [--all] [--llm=<claude|mock>] [--force]
apm agents load --dir=<path>
apm agents roles
apm agents types
```

#### Summary Commands (7 commands)

```bash
apm summary create <work-item-id> --content <content> --type=<type>
apm summary list [--work-item-id=<id>] [--type=<type>]
apm summary show <id>
apm summary delete <id>
apm summary search <query>
apm summary stats
apm summary types
```

#### Context Commands (5 commands)

```bash
apm context show [--work-item-id=<id>] [--task-id=<id>]
apm context status
apm context refresh [--entity-type=<type>] [--entity-id=<id>]
apm context wizard
apm context rich [--work-item-id=<id>]
```

#### Dependency Commands (5 commands)

```bash
apm dependencies add-dependency <task-id> --depends-on <other-task-id>
apm dependencies list-dependencies <task-id>
apm dependencies add-blocker <task-id> --blocked-by <reason>
apm dependencies list-blockers <task-id>
apm dependencies resolve-blocker <task-id> --blocker-id <id>
```

#### Rules Commands (4 commands)

```bash
apm rules list [--enforcement=<BLOCK|LIMIT|GUIDE>] [--category=<cat>]
apm rules show <rule-id>
apm rules create <rule-id> --name <name> [options]
apm rules configure <rule-id> [options]
```

#### Root Commands (16 commands)

**System Management:**
```bash
apm init [--project-name=<name>]
    # Initialize AIPM in current project

apm status
    # Display project dashboard

apm migrate [--to-version=<version>]
    # Run database migrations

apm migrate-v1-to-v2
    # Migrate from AIPM V1
```

**Command Extensions:**
```bash
apm commands install <command-name>
    # Install slash command

apm commands list
    # List available commands
```

**Testing & Quality:**
```bash
apm testing run [--coverage]
    # Run test suite

apm principle-check [--rule-id=<id>]
    # Validate against principles

apm principles list
    # List all principles
```

**Utilities:**
```bash
apm template list
    # List available templates

apm search <query> [--scope=<GLOBAL|PROJECT|...>]
    # Full-text search

apm hooks list
    # List Claude Code hooks

apm skills list
    # List available skills

apm claude-code status
    # Claude Code integration status

apm provider list
    # List LLM providers

apm memory list
    # List memory files
```

---

## REST API Endpoints

### Web Interface (77+ Endpoints)

#### Main Routes (6 endpoints)

```
GET  /                           # Dashboard (primary project overview)
GET  /project/<id>               # Project detail
GET  /project/<id>/context       # 6W framework view
GET  /test-toasts                # Toast notification test
POST /test-toast/<type>          # HTMX toast trigger
GET  /test/interactions          # Enhanced interactions demo
```

#### Projects Routes (4 endpoints)

```
GET  /project/<id>               # Complete project view
GET  /project/<id>/settings      # Project configuration
GET  /project/<id>/analytics     # Analytics dashboard
POST /project/<id>/update        # Update project metadata
```

#### Entities Routes (15+ endpoints)

```
# Projects
GET  /projects                   # Projects list view

# Work Items
GET  /work-items-debug           # Debug work items listing
GET  /work-item/<id>             # Work item detail
GET  /work-item/<id>/summary     # Summary timeline
GET  /work-item/<id>/dependencies # Dependency graph

# Tasks
GET  /tasks                      # Tasks list (filterable)
GET  /task/<id>                  # Task detail view
GET  /task/<id>/dependencies     # Task dependencies
```

#### Configuration Routes (12+ endpoints)

```
# Rules
GET  /rules                      # Rules list with enforcement levels
POST /rules/<id>/toggle          # Toggle rule (BLOCK/GUIDE)

# Agents
GET  /agents                     # Agents dashboard
POST /agents/generate            # Generate agent definitions
GET  /agents/<id>                # Agent detail
POST /agents/<id>/toggle         # Toggle agent

# Projects
GET  /projects/<id>/settings     # Project settings (inline editing)
```

#### System Routes (8+ endpoints)

```
GET  /health                     # Health check
GET  /system/database            # Database metrics
GET  /system/workflow            # Workflow state machine
GET  /system/context-files       # Context file browser
GET  /system/context-files/<name>/preview # File preview
POST /system/export              # Data export endpoint
```

#### Research Routes (9+ endpoints)

```
GET  /evidence                   # Evidence sources list
GET  /evidence/<id>              # Evidence detail
GET  /events                     # Events timeline
GET  /events/<id>                # Event detail
GET  /documents                  # Document references list
GET  /documents/<id>             # Document detail
```

#### Sessions Routes (8+ endpoints)

```
GET  /sessions                   # Sessions list
GET  /sessions/<id>              # Session detail
GET  /sessions/timeline          # Timeline view
GET  /sessions/<id>/export       # Export session
```

#### Contexts Routes (10+ endpoints)

```
GET  /contexts                   # Contexts list
GET  /contexts/<id>              # Context detail
GET  /work-item/<id>/context     # Hierarchical context view
POST /contexts/<id>/refresh      # Refresh context
```

#### Ideas Routes (5+ endpoints)

```
GET  /ideas                      # Ideas list
GET  /ideas/<id>                 # Idea detail
GET  /ideas/<id>/context         # Idea context
POST /ideas/<id>/convert         # Convert to work item
```

---

## Python SDK Usage

### Direct Method Access

**Import Pattern:**

```python
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import work_items, tasks, agents
from agentpm.core.database.models import WorkItem, Task, Agent

# Initialize database service
db = DatabaseService('.aipm/data/aipm.db')
```

### Work Item Methods

```python
# Create work item
wi = WorkItem(
    project_id=1,
    name="Feature Name",
    type=WorkItemType.FEATURE,
    status=WorkItemStatus.DRAFT,
    acceptance_criteria=["AC1", "AC2", "AC3"],
)
result = work_items.create_work_item(db, wi)

# List work items
work_item_list = work_items.list_work_items(
    db, project_id=1, status=WorkItemStatus.ACTIVE
)

# Get work item
wi = work_items.get_work_item(db, work_item_id=1)

# Update work item
work_items.update_work_item(db, work_item_id=1, name="New Name")

# Transition work item
work_items.transition_work_item(db, work_item_id=1, new_status=WorkItemStatus.READY)
```

### Task Methods

```python
# Create task
task = Task(
    work_item_id=1,
    name="Implement feature",
    type=TaskType.IMPLEMENTATION,
    effort_hours=3.5,
)
result = tasks.create_task(db, task)

# List tasks
task_list = tasks.list_tasks(db, work_item_id=1)

# Update task
tasks.update_task(db, task_id=1, effort_hours=4.0)
```

### Agent Methods

```python
# List agents
agent_list = agents.list_agents(db, project_id=1, tier=1)

# Get agent
agent = agents.get_agent(db, role='code-implementer')

# Generate agents
from agentpm.core.agents.generator import generate_and_store_agents

generate_and_store_agents(db, project_id=1, use_claude=False)
```

### Context Assembly

```python
from agentpm.core.context.assembly_service import ContextAssemblyService

# Initialize service
assembler = ContextAssemblyService(db, project_path='/path/to/project')

# Assemble task context
context = assembler.assemble_task_context(task_id=355, agent_role='implementer')

# Access context data
print(context.six_w_data)  # 6W framework
print(context.plugin_facts)  # Tech stack facts
print(context.confidence)  # Confidence score
```

### Security Utilities

```python
from agentpm.core.security import InputValidator, OutputSanitizer

# Validate input
validated_name = InputValidator.validate_project_name("my-project")
validated_path = InputValidator.validate_file_path("docs/design/spec.md")

# Sanitize output
sanitized_text = OutputSanitizer.sanitize_text(output_with_secrets)
sanitized_dict = OutputSanitizer.sanitize_dict(data_dict)
```

---

## Provider Interfaces

### Base Provider Interface

```python
from agentpm.providers.base import BaseProvider


class CustomProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "custom"

    @property
    def display_name(self) -> str:
        return "Custom LLM"

    def generate_agent_files(self, agents, output_dir):
        """Generate provider-specific agent files"""
        ...

    def format_context(self, context):
        """Format context for this provider's LLM"""
        ...

    def get_hook_templates(self):
        """Get provider-specific hook templates"""
        ...
```

### Anthropic Provider

```python
from agentpm.providers.anthropic import AnthropicFormatter, AnthropicAdapter

# Format task context
formatter = AnthropicFormatter()
formatted = formatter.format_task(
    context_payload,
    token_allocation=adapter.plan_tokens(context_payload)
)

# Token allocation
adapter = AnthropicAdapter()
allocation = adapter.plan_tokens(context_payload)
# Returns: TokenAllocation(prompt=120k, completion=40k, reserve=40k)
```

### Cursor Provider

```python
from agentpm.providers.cursor import CursorProvider

# Initialize provider
provider = CursorProvider(db)

# Install Cursor configuration
result = provider.install(
    project_path='/path/to/project',
    config=CursorConfig(
        project_name='my-project',
        rules_enabled=True,
        memory_sync_enabled=True,
    )
)

# Verify installation
verify_result = provider.verify(project_path='/path/to/project')

# Sync memories
sync_result = provider.sync_memories(
    project_path='/path/to/project',
    direction=MemorySyncDirection.TO_CURSOR
)
```

---

## Database Schema Reference

### Core Tables (40+ tables)

#### Projects Table
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tech_stack TEXT DEFAULT '[]',  -- JSON array
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Work Items Table
```sql
CREATE TABLE work_items (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('FEATURE', 'ENHANCEMENT', 'BUGFIX', ...)),
    status TEXT CHECK(status IN ('DRAFT', 'READY', 'ACTIVE', ...)),
    phase TEXT CHECK(phase IN ('D1_DISCOVERY', 'P1_PLAN', ...)),
    business_context TEXT,
    acceptance_criteria TEXT DEFAULT '[]',  -- JSON array
    metadata TEXT DEFAULT '{}',             -- JSON object
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    work_item_id INTEGER,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('RESEARCH', 'DESIGN', 'IMPLEMENTATION', ...)),
    status TEXT CHECK(status IN ('DRAFT', 'READY', 'ACTIVE', ...)),
    effort_hours REAL,
    assigned_to TEXT,
    due_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);
```

#### Agents Table
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    role TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    agent_type TEXT,
    tier INTEGER CHECK(tier IN (1, 2, 3)),
    capabilities TEXT DEFAULT '[]',  -- JSON array
    is_active BOOLEAN DEFAULT 1,
    file_path TEXT,
    generated_at TIMESTAMP,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (project_id) REFERENCES projects(id),
    UNIQUE(project_id, role)
);
```

#### Rules Table
```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    rule_id TEXT NOT NULL,
    name TEXT,
    description TEXT,
    enforcement_level TEXT CHECK(enforcement_level IN ('BLOCK', 'LIMIT', 'GUIDE')),
    category TEXT,
    config TEXT DEFAULT '{}',  -- JSON object
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### Contexts Table
```sql
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY,
    entity_type TEXT CHECK(entity_type IN ('PROJECT', 'WORK_ITEM', 'TASK', 'AGENT')),
    entity_id INTEGER,
    six_w_data TEXT DEFAULT '{}',         -- JSON object
    plugin_facts TEXT DEFAULT '{}',       -- JSON object
    confidence_factors TEXT DEFAULT '{}', -- JSON object
    assembled_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

### Key Enums

**WorkItemType:**
```
FEATURE, ENHANCEMENT, BUGFIX, RESEARCH, PLANNING, ANALYSIS,
REFACTORING, INFRASTRUCTURE, MAINTENANCE, MONITORING,
DOCUMENTATION, SECURITY, FIX_BUGS_ISSUES
```

**WorkItemStatus:**
```
DRAFT, READY, ACTIVE, REVIEW, DONE, ARCHIVED, BLOCKED, CANCELLED
```

**Phase:**
```
D1_DISCOVERY, P1_PLAN, I1_IMPLEMENTATION, R1_REVIEW,
O1_OPERATIONS, E1_EVOLUTION
```

**TaskType:**
```
RESEARCH, DESIGN, PLANNING, ANALYSIS, IMPLEMENTATION,
TESTING, DOCUMENTATION
```

**TaskStatus:**
```
DRAFT, READY, ACTIVE, REVIEW, DONE, ARCHIVED, BLOCKED, CANCELLED
```

---

## Example Workflows

### Complete Feature Development Workflow

```bash
# 1. Create work item
apm work-item create "User Authentication" --type=FEATURE

# 2. Move to planning
apm work-item next 1  # DRAFT → READY

# 3. Create tasks
apm task create "Design auth flow" --work-item-id=1 --type=DESIGN
apm task create "Implement auth" --work-item-id=1 --type=IMPLEMENTATION
apm task create "Write tests" --work-item-id=1 --type=TESTING

# 4. Start implementation
apm task next 2  # DRAFT → READY → ACTIVE

# 5. Submit for review
apm task submit-review 2  # ACTIVE → REVIEW

# 6. Approve
apm task approve 2  # REVIEW → DONE

# 7. Check status
apm work-item show 1
apm task list --work-item-id=1
```

### Python SDK Workflow

```python
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import work_items, tasks
from agentpm.core.database.models import WorkItem, Task, WorkItemType, TaskType

# Initialize
db = DatabaseService('.aipm/data/aipm.db')

# Create work item
wi = work_items.create_work_item(db, WorkItem(
    project_id=1,
    name="User Authentication",
    type=WorkItemType.FEATURE,
    acceptance_criteria=["AC1", "AC2", "AC3"],
))

# Create tasks
task1 = tasks.create_task(db, Task(
    work_item_id=wi.id,
    name="Design auth flow",
    type=TaskType.DESIGN,
    effort_hours=2.0,
))

task2 = tasks.create_task(db, Task(
    work_item_id=wi.id,
    name="Implement auth",
    type=TaskType.IMPLEMENTATION,
    effort_hours=4.0,
))

# Transition work item
work_items.transition_work_item(db, wi.id, WorkItemStatus.READY)

# List tasks
task_list = tasks.list_tasks(db, work_item_id=wi.id)
print(f"Created {len(task_list)} tasks")
```

---

## Error Codes

### HTTP Status Codes (REST API)

```
200 OK                  # Successful GET/POST
201 Created             # Resource created
400 Bad Request         # Validation error
404 Not Found           # Resource not found
500 Internal Error      # Server error
```

### CLI Exit Codes

```
0   Success
1   General error
2   Command error
3   Validation error
4   Security error
```

---

## Rate Limits & Quotas

**Current Implementation:**
- No rate limiting (single-user CLI)
- Database limits: ~1 million rows per table
- File size limits: None enforced (recommendation: <100MB per document)

**Future (Multi-User Mode):**
- API rate limits: 1000 requests/hour per user
- Database connection pooling
- File upload limits: 100MB

---

## Versioning

**API Version:** 2.0.0

**Versioning Strategy:**
- Major version: Breaking changes
- Minor version: New features (backward compatible)
- Patch version: Bug fixes

**Deprecation Policy:**
- Features deprecated: 2 release warning period
- Breaking changes: Major version bump only

---

## Additional Resources

### Detailed API Documentation
- **CLI Commands:** `apm <command> --help`
- **Python SDK:** Docstrings in `agentpm/core/database/methods/`
- **REST API:** Docstrings in `agentpm/web/routes/`

### Schema Documentation
- **Database Schema:** `docs/components/database/schema.md`
- **Pydantic Models:** `agentpm/core/database/models/`

### Integration Guides
- **Provider Integration:** `docs/components/providers/`
- **Plugin Development:** `docs/components/plugins/`

---

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Next Review:** Quarterly
**Maintained By:** APM (Agent Project Manager) API Team
