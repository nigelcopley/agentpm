# AIPM CLI Command Reference

**Complete Command Documentation** | Version 2.0 | Real Examples from fullstack-ecommerce Project

All command examples are from actual walkthrough and testing.

---

## Table of Contents

1. [System Commands](#system-commands)
2. [Work Item Commands](#work-item-commands)
3. [Task Commands](#task-commands)
4. [Phase Commands](#phase-commands)
5. [Context Commands](#context-commands)
6. [Session Commands](#session-commands)
7. [Agent Commands](#agent-commands)
8. [Rules Commands](#rules-commands)
9. [Testing Commands](#testing-commands)
10. [Document Commands](#document-commands)

---

## System Commands

### `apm --help`

Show main help and list all available command groups.

**Example**:
```bash
apm --help
```

**Output** (condensed):
```
🤖 APM (Agent Project Manager) - AI Project Manager

Commands:
  init         Initialize AIPM project
  status       Show project dashboard
  work-item    Manage work items
  task         Manage tasks
  context      Access project context
  agents       Manage AI agents
  rules        Manage project rules
  session      Manage sessions
  ...
```

### `apm --version`

Show AIPM version.

**Example**:
```bash
apm --version
```

**Performance**: <100ms (lazy loading)

---

### `apm init`

Initialize AIPM in a project directory.

**Syntax**:
```bash
apm init PROJECT_NAME [PATH] [OPTIONS]
```

**Options**:
- `-d, --description TEXT` - Project description
- `--skip-questionnaire` - Skip rules questionnaire and use defaults

**Real Example**:
```bash
cd testing/fullstack-ecommerce
apm init "Fullstack Ecommerce" \
  -d "Full-stack e-commerce platform with Django backend and React frontend"
```

**What It Creates**:
```
.aipm/
├── data/
│   └── aipm.db              # SQLite database
├── contexts/                # Plugin-generated contexts
└── cache/                   # Temporary cache

.claude/
└── agents/                  # 13 project-specific agent SOPs
```

**Real Output**:
```
🚀 Initializing AIPM project: Fullstack Ecommerce
📁 Location: /Users/nigelcopley/.project_manager/aipm-v2/testing/fullstack-ecommerce

✅ Migration 0018: Consolidated Schema Migration Complete
  Creating directory structure... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Database schema up to date      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Generating project-specific agents...
   ✓ Generated 13 agents

✅ Project initialized successfully!

           🔍 Detected Technologies
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Technology ┃ Confidence ┃ Plugin           ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Django     │        60% │ framework:django │
│ Python     │        66% │ lang:python      │
│ React      │        60% │ framework:react  │
└────────────┴────────────┴──────────────────┘

📊 Detected 9 technologies in 27ms

💾 Database: .aipm/data/aipm.db
📁 Project ID: 1
```

**Performance**: <5 seconds with progress bars

---

### `apm status`

Show project health dashboard with metrics.

**Syntax**:
```bash
apm status
```

**Real Output**:
```
╭─────────────────────── 🤖 APM (Agent Project Manager) Project Dashboard ───────────────────────╮
│ Fullstack Ecommerce                                                        │
│ 📁 /Users/nigelcopley/.project_manager/aipm-v2/testing/fullstack-ecommerce │
│ Status: active                                                             │
╰────────────────────────────────────────────────────────────────────────────╯

Work Items: 1 (1 feature)
Tasks: 4 (1 design, 1 implementation, 1 testing, 1 documentation)
Current Phase: D1_DISCOVERY

📚 Quick Commands:
   apm work-item list          # View all work items
   apm task list               # View all tasks
   apm work-item show 1        # Check quality gates
```

**Performance**: <1s (indexed queries)

---

## Work Item Commands

### `apm work-item create`

Create a new work item (feature, bug, research, etc.).

**Syntax**:
```bash
apm work-item create NAME --type=TYPE [OPTIONS]
```

**Work Item Types**:

| Type | Purpose | Typical Phase Sequence |
|------|---------|------------------------|
| `feature` | New functionality | D1 → P1 → I1 → R1 → O1 → E1 (full lifecycle) |
| `bugfix` | Bug fixes | I1 → R1 (implementation + review) |
| `research` | Investigation | D1 → P1 (discovery + planning) |
| `enhancement` | Improvements | P1 → I1 → R1 (plan, implement, review) |
| `refactoring` | Code improvement | P1 → I1 → R1 → O1 (plan through ops) |
| `infrastructure` | DevOps work | D1 → P1 → I1 → R1 → O1 (full ops lifecycle) |
| `planning` | Planning work | D1 → P1 (discovery and planning phases) |
| `maintenance` | Maintenance tasks | Flexible sequence based on needs |
| `security` | Security work | D1 → P1 → I1 → R1 (analyze, plan, implement, validate) |

**Note**: Phase gates validate outcomes, not task types. Create tasks as needed to achieve phase goals.

**Options**:
- `--type TYPE` - Work item type (required)
- `-d, --description TEXT` - Description
- `-p, --priority INTEGER` - Priority (1-5, default=3)
- `--continuous / --no-continuous` - Mark as continuous backlog
- `--business-context TEXT` - Business justification
- `--acceptance-criteria TEXT` - JSON array of criteria
- `--who TEXT` - Target users/stakeholders
- `--what TEXT` - What is being built
- `--where TEXT` - System boundaries/locations
- `--when TEXT` - Timeline/deadlines
- `--why TEXT` - Business value/rationale
- `--how TEXT` - Technical approach
- `--quality-target TEXT` - JSON quality standards
- `--ownership TEXT` - JSON RACI roles
- `--scope TEXT` - JSON in_scope/out_of_scope
- `--artifacts TEXT` - JSON code_paths/docs_paths
- `--phase PHASE` - Initial phase (D1/P1/I1/R1/O1/E1)
- `--metadata-template TEXT` - Seed from template

**Real Example** (Basic):
```bash
apm work-item create "Product Catalog API" --type=feature --priority=1
```

**Real Example** (Full Context):
```bash
apm work-item create "Product Catalog API" \
  --type=feature \
  --priority=1 \
  -d "Build REST API endpoints for product catalog with search, filtering, and pagination" \
  --business-context "Enable customers to browse and discover products efficiently, supporting 1000+ SKUs" \
  --who "E-commerce customers, Product managers, Frontend developers" \
  --what "RESTful API for product catalog operations" \
  --where "backend/api/products/, backend/models.py, backend/serializers.py" \
  --when "Sprint 1, Week 1-2, Foundation for Q1 2025 launch" \
  --why "Core business functionality, Revenue generation, Customer satisfaction" \
  --how "Django REST Framework, PostgreSQL full-text search, Redis caching"
```

**Real Output**:
```
✅ Work item created: Product Catalog API
   ID: 1
   Type: feature
   Status: draft
   Priority: 1
   Business Context: ✓
   6W Context: ✓ (stored in contexts table)

📋 Phase-based workflow:
   • Progress through phases: D1 → P1 → I1 → R1 → O1 → E1
   • Phase gates validate outcomes (code complete? tests passing?)
   • Create tasks as needed to achieve phase goals

📚 Next step:
   apm work-item next 1  # Start D1 (Discovery) phase
   apm task create "Task name" --work-item-id=1  # Create tasks as needed
```

---

### `apm work-item list`

List all work items with optional filters.

**Syntax**:
```bash
apm work-item list [OPTIONS]
```

**Options**:
- `--type TYPE` - Filter by type (feature, bugfix, etc.)
- `--status STATUS` - Filter by status (draft, ready, in_progress, etc.)
- `--priority INTEGER` - Filter by priority (1-5)
- `--phase PHASE` - Filter by phase (D1/P1/I1/R1/O1/E1)

**Examples**:
```bash
# All work items
apm work-item list

# Only features
apm work-item list --type=feature

# Only in-progress
apm work-item list --status=in_progress

# High priority only
apm work-item list --priority=1

# In implementation phase
apm work-item list --phase=i1_implementation
```

---

### `apm work-item show`

Show complete work item details including tasks and quality gates.

**Syntax**:
```bash
apm work-item show WORK_ITEM_ID
```

**Real Example**:
```bash
apm work-item show 1
```

**Real Output**:
```
📋 Work Item #1

Name: Product Catalog API
Type: feature
Status: draft
Priority: 1
Phase: D1_DISCOVERY

Description:
Build REST API endpoints for product catalog with search, filtering, and
pagination capabilities

Tasks (4):
  •  Document Product Catalog API (draft)
  •  Test Product Catalog API (draft)
  •  Implement Product API Endpoints (draft)
  •  Design Product Catalog API Architecture (draft)

Quality Gates:
  FEATURE work items require:
    ✅ DESIGN task
    ✅ IMPLEMENTATION task
    ✅ TESTING task
    ✅ DOCUMENTATION task
```

---

### `apm work-item update`

Update work item fields.

**Syntax**:
```bash
apm work-item update WORK_ITEM_ID [OPTIONS]
```

**Options**:
- `--name TEXT` - Update name
- `-d, --description TEXT` - Update description
- `--business-context TEXT` - Update business context
- `-p, --priority INTEGER` - Update priority (1-5)
- `--phase PHASE` - Update phase
- `--ownership TEXT` - JSON RACI roles
- `--scope TEXT` - JSON in_scope/out_of_scope
- `--artifacts TEXT` - JSON code_paths/docs_paths
- `--metadata TEXT` - Complete metadata JSON

**Examples**:
```bash
# Update name
apm work-item update 1 --name "Updated Feature Name"

# Update priority
apm work-item update 1 --priority=1

# Update description
apm work-item update 1 -d "New detailed description"

# Update metadata with phase gates
apm work-item update 1 --metadata '{"why_value": {...}, "gates": {...}}'
```

**Real Output**:
```
✅ Work item updated: #1
   Metadata: → Updated

📚 Next steps:
   apm work-item show 1  # View updated details
```

---

### `apm work-item validate`

Validate work item and transition to validated status.

**Syntax**:
```bash
apm work-item validate WORK_ITEM_ID
```

**Example**:
```bash
apm work-item validate 1
```

**Validation Checks**:
- Description ≥50 characters
- Required tasks present for work item type
- Business context (if applicable)
- Acceptance criteria (if applicable)

**Note**: In current implementation, validation may require phase-based workflow instead.

---

### `apm work-item accept`

Accept work item and transition to accepted status.

**Syntax**:
```bash
apm work-item accept WORK_ITEM_ID --agent AGENT_NAME
```

**Example**:
```bash
apm work-item accept 1 --agent python-implementer
```

---

### `apm work-item start`

Start working on work item (transition to in_progress).

**Syntax**:
```bash
apm work-item start WORK_ITEM_ID
```

**Example**:
```bash
apm work-item start 1
```

**Prerequisite**: Work item must be in `accepted` status.

---

### `apm work-item submit-review`

Submit work item for review.

**Syntax**:
```bash
apm work-item submit-review WORK_ITEM_ID
```

**Example**:
```bash
apm work-item submit-review 1
```

---

### `apm work-item approve`

Approve work item and transition to completed status.

**Syntax**:
```bash
apm work-item approve WORK_ITEM_ID
```

**Example**:
```bash
apm work-item approve 1
```

---

### `apm work-item request-changes`

Request changes to work item (transition back to in_progress).

**Syntax**:
```bash
apm work-item request-changes WORK_ITEM_ID --reason "Reason for changes"
```

**Example**:
```bash
apm work-item request-changes 1 --reason "Missing security analysis"
```

---

### `apm work-item next`

Automatically transition work item to next logical state.

**Syntax**:
```bash
apm work-item next WORK_ITEM_ID
```

**Example**:
```bash
apm work-item next 1
```

**State Progression**: draft → ready → accepted → in_progress → review → completed

---

## Phase Commands

### `apm work-item phase-status`

Show current phase status and requirements.

**Syntax**:
```bash
apm work-item phase-status WORK_ITEM_ID
```

**Real Example**:
```bash
apm work-item phase-status 1
```

**Real Output**:
```
Work Item #1: Product Catalog API
Type: feature
Current Phase: NULL (not started)
Current Status: draft
Next Phase: D1_DISCOVERY

Phase Sequence for FEATURE:
  D1_DISCOVERY (future)
  P1_PLAN (future)
  I1_IMPLEMENTATION (future)
  R1_REVIEW (future)
  O1_OPERATIONS (future)
  E1_EVOLUTION (future)

Next Phase (D1_DISCOVERY) Requirements:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Available Actions:
  apm work-item next 1  # Advance to next phase (automatic)
  apm work-item show 1  # View full details
```

---

### `apm work-item phase-validate`

Validate if work item is ready to advance to next phase.

**Syntax**:
```bash
apm work-item phase-validate WORK_ITEM_ID
```

**Example**:
```bash
apm work-item phase-validate 1
```

**Checks**: Phase gate requirements, required tasks, quality standards

---

### `apm work-item next`

Automatically advance work item to next phase.

**Syntax**:
```bash
apm work-item next WORK_ITEM_ID
```

**Real Example**:
```bash
apm work-item next 1
```

**Real Output**:
```
Advancing Work Item #1: Product Catalog API
Current Phase: NULL
Current Status: draft

Advancing: NULL → D1_DISCOVERY

Validating phase gate requirements...
✅ Phase gate validation PASSED

✅ Phase advanced successfully

Phase: NULL → D1_DISCOVERY
Status: draft → draft

Now in D1_DISCOVERY phase:
Define user needs, validate market fit, gather requirements, assess technical
feasibility

Required task types:
  • analysis
  • research
  • design

Next Steps:
  apm work-item phase-status 1  # View phase requirements
  apm task list --work-item-id=1  # View tasks
  apm work-item next 1   # Advance when ready
```

**Phase Progression**: NULL → D1 → P1 → I1 → R1 → O1 → E1

---

## Task Commands

### `apm task create`

Create a new task within a work item.

**Syntax**:
```bash
apm task create NAME --work-item-id=ID --type=TYPE --effort=HOURS [OPTIONS]
```

**Task Types**:

| Type | Max Effort | Purpose |
|------|-----------|---------|
| `design` | 8h | Architecture, system design |
| `implementation` | 4h | Code changes |
| `testing` | 6h | Test coverage |
| `documentation` | 8h | Docs, guides |
| `analysis` | 8h | Investigation |
| `bugfix` | 4h | Bug fixes |
| `refactoring` | 4h | Code improvement |
| `deployment` | 6h | Deployment work |
| `review` | 4h | Code review |
| `planning` | 8h | Planning work |

**Options**:
- `--work-item-id INTEGER` - Parent work item ID (required)
- `--type TYPE` - Task type (required)
- `--effort FLOAT` - Effort estimate in hours (required)
- `-d, --description TEXT` - Task description
- `-p, --priority INTEGER` - Priority (1-5, default=3)
- `--blocking / --no-blocking` - Mark as blocking task

**Real Examples**:
```bash
# Design task
apm task create "Design Product Catalog API Architecture" \
  --work-item-id=1 \
  --type=design \
  --effort=3 \
  -d "Design REST API endpoints, data models, caching strategy, and search implementation"

# Implementation task
apm task create "Implement Product API Endpoints" \
  --work-item-id=1 \
  --type=implementation \
  --effort=4 \
  -d "Implement Django REST Framework views, serializers, and URL patterns"

# Testing task
apm task create "Test Product Catalog API" \
  --work-item-id=1 \
  --type=testing \
  --effort=3 \
  -d "Write comprehensive test suite covering API endpoints and edge cases"

# Documentation task
apm task create "Document Product Catalog API" \
  --work-item-id=1 \
  --type=documentation \
  --effort=2 \
  -d "Create API documentation with OpenAPI spec and usage examples"
```

**Real Output**:
```
✅ Task created: Design Product Catalog API Architecture
   ID: 1
   Type: design
   Status: draft
   Effort: 3.0h
   Priority: 3

📚 Next steps:
   apm task list --work-item-id=1  # View all tasks
   apm task next 1                 # Start working on this task
   apm work-item show 1            # Check quality gates
```

---

### `apm task list`

List all tasks with optional filters.

**Syntax**:
```bash
apm task list [OPTIONS]
```

**Options**:
- `--work-item-id INTEGER` - Filter by work item
- `--type TYPE` - Filter by task type
- `--status STATUS` - Filter by status
- `--priority INTEGER` - Filter by priority

**Real Example**:
```bash
apm task list
```

**Real Output**:
```
                                  📋 Tasks (4)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━┓
┃ ID ┃ Name                            ┃ Type           ┃ Status ┃ Effort ┃ WI ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━┩
│ 4  │ Document Product Catalog API    │ documentation  │ draft  │ 2.0h   │ 1  │
│ 3  │ Test Product Catalog API        │ testing        │ draft  │ 3.0h   │ 1  │
│ 2  │ Implement Product API Endpoints │ implementation │ draft  │ 4.0h   │ 1  │
│ 1  │ Design Product Catalog API      │ design         │ draft  │ 3.0h   │ 1  │
│    │ Architecture                    │                │        │        │    │
└────┴─────────────────────────────────┴────────────────┴────────┴────────┴────┘
```

**Examples**:
```bash
# Tasks for specific work item
apm task list --work-item-id=1

# Only implementation tasks
apm task list --type=implementation

# Only in-progress tasks
apm task list --status=in_progress
```

---

### `apm task show`

Show complete task details.

**Syntax**:
```bash
apm task show TASK_ID
```

**Example**:
```bash
apm task show 1
```

---

### `apm task validate`

Validate task and transition to validated status.

**Syntax**:
```bash
apm task validate TASK_ID
```

**Real Example** (Error Case):
```bash
apm task validate 1
```

**Real Output** (When work item not ready):
```
❌ Validation failed:
❌ Cannot validate task: Work item #1 must be 'ready' (currently 'draft')

Fix: apm work-item validate 1

📋 Validation Requirements:
   ✅ Description: 103 characters
   ✅ Effort: 3.0h
   ✅ Time-boxing: 3.0h ≤ 8.0h (design)

💡 Fix the issues above, then run:
   apm task validate 1

Aborted!
```

---

### `apm task accept`

Accept task and assign to agent.

**Syntax**:
```bash
apm task accept TASK_ID --agent AGENT_NAME
```

**Example**:
```bash
apm task accept 1 --agent python-implementer
```

---

### `apm task start`

Start working on task (transition to in_progress).

**Syntax**:
```bash
apm task start TASK_ID
```

**Example**:
```bash
apm task start 1
```

---

### `apm task submit-review`

Submit task for review.

**Syntax**:
```bash
apm task submit-review TASK_ID
```

**Example**:
```bash
apm task submit-review 1
```

---

### `apm task approve`

Approve task and mark as completed.

**Syntax**:
```bash
apm task approve TASK_ID
```

**Example**:
```bash
apm task approve 1
```

---

### `apm task request-changes`

Request changes to task (transition back to in_progress).

**Syntax**:
```bash
apm task request-changes TASK_ID --reason "Reason for changes"
```

**Example**:
```bash
apm task request-changes 1 --reason "Missing edge case tests"
```

---

### `apm task next`

Automatically transition task to next logical state. This is the **recommended** command for most workflows.

**Syntax**:
```bash
apm task next TASK_ID
```

**Example**:
```bash
apm task next 1
```

**State Progression**:
- draft → validated → accepted → in_progress → review → completed

**When to use**:
- ✅ Standard workflow progression (most common)
- ✅ Quick iteration during development
- ✅ Solo development without complex review processes

**When to use explicit commands instead**:
- Agent assignment (requires `apm task accept --agent <name>`)
- Review workflows (requires `apm task request-changes --reason "..."`)
- Complex multi-step processes with specific requirements

---

## Additional Command Groups

### Agent Commands

**IMPORTANT**: AIPM uses a **three-stage agent system** (YAML → DB → Generate):

1. **YAML Catalog** (development time) - Agent definitions in `_RULES/agents/` (documentation only)
2. **Database Population** (init time) - Migration 0029 populates agents table during `apm init`
3. **File Generation** (post-init) - Run `apm agents generate --all` to create provider-specific files

**Complete Workflow**:
```bash
# 1. Initialize project (populates database with agents)
apm init "My Project"

# 2. Generate agent files from database
apm agents generate --all

# 3. Verify agents created
ls .claude/agents/
```

**Key Points**:
- ✅ Agent metadata stored in **database** (single source of truth)
- ❌ YAML files are **documentation only** (not used at runtime)
- ✅ Generated files are **provider-specific** (.claude/agents/*.md for Claude Code)
- ✅ Agents require **project to exist** (migration 0029 skips if no project)
- ✅ Regeneration is **safe** and **idempotent** (use `--force` to overwrite)

**Basic Commands**:
```bash
apm agents list              # List agents in database
apm agents generate --all    # Generate provider-specific files
apm agents show <role>       # Show agent details
```

**Generation Options**:
```bash
# Generate all agents (auto-detect provider)
apm agents generate --all

# Generate specific agent
apm agents generate --role context-generator

# Specify provider explicitly
apm agents generate --all --provider=claude-code

# Dry run (preview without writing)
apm agents generate --all --dry-run

# Force regeneration
apm agents generate --all --force
```

**Provider Detection Order**:
1. `AIPM_LLM_PROVIDER` environment variable
2. `.claude/` directory → `claude-code`
3. `.cursor/` directory → `cursor`
4. Default to `claude-code`

**Troubleshooting**:
```bash
# No agents in database?
apm agents list                    # Check if agents exist
apm db migrate                     # Run migrations if needed

# Provider not detected?
export AIPM_LLM_PROVIDER=claude-code
# or
mkdir .claude
# or
apm agents generate --all --provider=claude-code
```

For complete details, see [Agent Generation Workflow](agent-generation-workflow.md).

### Rules Commands

```bash
apm rules list               # List all project rules
apm rules list -e BLOCK      # Show only blocking rules
apm rules list -c code_quality  # Filter by category
apm rules show DP-001        # Show specific rule details
apm rules configure          # Configure project rules
```

### Context Commands

```bash
apm context show             # Show project context
apm context show --task-id=1 # Show task-specific context
apm context refresh          # Refresh context cache
```

### Session Commands

```bash
apm session list             # List all sessions
apm session show <id>        # Show session details
apm session create           # Create new session
apm session end <id>         # End session
```

### Document Commands

```bash
apm document list            # List all documents
apm document show <id>       # Show document details
apm document create "Title"  # Create new document
apm document update <id>     # Update document
apm document delete <id>     # Delete document
```

### Testing Commands

```bash
apm testing configure        # Configure testing rules
apm testing show             # Show testing configuration
```

### Template Commands

```bash
apm template list            # List available templates
apm template show <id>       # Show template details
```

---

## Performance Benchmarks

| Command | Target Performance |
|---------|-------------------|
| `apm --help` | <100ms |
| `apm --version` | <100ms |
| `apm status` | <1s |
| `apm init` | <5s |
| `apm work-item list` | <1s |
| `apm task list` | <1s |
| `apm work-item show` | <500ms |
| `apm task show` | <500ms |

**All performance targets from actual benchmarks on fullstack-ecommerce project.**

---

## See Also

- [Getting Started Guide](01-getting-started.md) - Learn the basics
- [Quick Reference Card](02-quick-reference.md) - Common workflows
- [Phase Workflow Guide](04-phase-workflow.md) - Detailed phase progression
- [Agent Generation Workflow](agent-generation-workflow.md) - Complete agent generation guide
- [Troubleshooting Guide](05-troubleshooting.md) - Solutions to common issues

---

**Generated**: 2025-10-17
**AIPM Version**: 2.0
**Real Examples**: All examples from live walkthrough of fullstack-ecommerce project
