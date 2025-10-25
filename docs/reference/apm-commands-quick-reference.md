# APM Commands Quick Reference

> Comprehensive guide to all APM (Agent Project Manager) commands

## Table of Contents

1. [Command Overview](#command-overview)
2. [Core Workflow Commands](#1-core-workflow-commands)
3. [Idea Management](#2-idea-management)
4. [Session & Continuity](#3-session--continuity)
5. [Documentation & Knowledge](#4-documentation--knowledge)
6. [Agent & AI Integration](#5-agent--ai-integration)
7. [Configuration & Rules](#6-configuration--rules)
8. [Database & Maintenance](#7-database--maintenance)
9. [Quick Command Patterns](#quick-command-patterns)
10. [Appendices](#appendices)

---

## Command Overview

| Command | Purpose | Subcommands |
|---------|---------|-------------|
| `init` | Initialize AIPM project | - |
| `status` | Project dashboard | - |
| `work-item` | Work item management | 17 |
| `task` | Task management | 15 |
| `idea` | Lightweight brainstorming | 10 |
| `context` | Context access | 5 |
| `session` | Session management | 7 |
| `summary` | Hierarchical summaries | 5 |
| `memory` | Claude memory files | 3 |
| `document` | Document references | 6 |
| `template` | JSON templates | 3 |
| `search` | Vector search | 1 |
| `agents` | Agent management | 6 |
| `claude-code` | Claude Code integration | 14 |
| `provider` | IDE providers | 5 |
| `skills` | Claude Code skills | 5 |
| `commands` | Slash commands | 3 |
| `rules` | Rule management | 4 |
| `testing` | Testing configuration | 6 |
| `migrate` | Database migrations | - |
| `migrate-v1-to-v2` | V1 to V2 migration | - |

---

## 1. Core Workflow Commands

### `apm init`

**Purpose**: Initialize AIPM project with database, rules, and configuration

**Syntax**: `apm init [OPTIONS]`

**Key Options**:
- `--force`: Reinitialize existing project
- `--skip-rules`: Skip rule population

**Example**:
```bash
apm init                    # Initialize new project
apm init --force            # Reinitialize existing
```

---

### `apm status`

**Purpose**: Display project dashboard with active work items, tasks, and metrics

**Syntax**: `apm status [OPTIONS]`

**Key Options**:
- `--format {table|json}`: Output format
- `--detailed`: Include more metrics

**Example**:
```bash
apm status                  # Quick dashboard
apm status --format=json    # Machine-readable output
```

---

### `apm work-item`

**Purpose**: Manage work items (features, bugs, research) through lifecycle

**Lifecycle**: `draft → validated → accepted → in_progress → review → completed`

**Phases**: `D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION`

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `create` | Create new work item | `apm work-item create "Add login" --type=feature` |
| `list` | List work items with filters | `apm work-item list --status=in_progress --phase=I1_IMPLEMENTATION` |
| `show` | Display work item details | `apm work-item show 123` |
| `update` | Update work item fields | `apm work-item update 123 --description "New desc"` |
| `next` | Auto-advance to next state | `apm work-item next 123` |
| `validate` | Move draft → validated | `apm work-item validate 123` |
| `accept` | Move validated → accepted | `apm work-item accept 123 --agent "planning-orch"` |
| `start` | Move accepted → in_progress | `apm work-item start 123` |
| `submit-review` | Move in_progress → review | `apm work-item submit-review 123` |
| `approve` | Move review → completed | `apm work-item approve 123` |
| `request-changes` | Move review → in_progress | `apm work-item request-changes 123 --reason "Missing tests"` |
| `phase-status` | Show phase gate status | `apm work-item phase-status 123` |
| `phase-validate` | Validate phase gates | `apm work-item phase-validate 123 --phase P1_PLAN` |
| `add-dependency` | Add work item dependency | `apm work-item add-dependency 123 --blocks 456` |
| `list-dependencies` | Show dependency graph | `apm work-item list-dependencies 123` |
| `remove-dependency` | Remove dependency | `apm work-item remove-dependency 123 --dependency-id 789` |
| `show-history` | Display audit trail | `apm work-item show-history 123` |
| `add-summary` | Add hierarchical summary | `apm work-item add-summary 123 --type progress --content "..."` |
| `types` | List available work item types | `apm work-item types` |

**Common Patterns**:
```bash
# Create and start work item
apm work-item create "Feature name" --type=feature
apm work-item next 1                        # draft → validated
apm work-item next 1                        # validated → accepted
apm work-item next 1                        # accepted → in_progress

# Query work items
apm work-item list --type=feature --status=in_progress
apm work-item list --phase=I1_IMPLEMENTATION --format=json

# Manage dependencies
apm work-item add-dependency 123 --blocks 456
apm work-item list-dependencies 123 --format=table
```

---

### `apm task`

**Purpose**: Manage atomic work units within work items

**Lifecycle**: `draft → validated → accepted → in_progress → review → completed`

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `create` | Create new task | `apm task create "Write tests" --work-item=123 --type=testing` |
| `list` | List tasks with filters | `apm task list --work-item=123 --status=in_progress` |
| `show` | Display task details | `apm task show 456` |
| `update` | Update task fields | `apm task update 456 --objective "New goal"` |
| `next` | Auto-advance to next state | `apm task next 456` |
| `validate` | Move draft → validated | `apm task validate 456` |
| `accept` | Move validated → accepted | `apm task accept 456 --agent "implementation-orch"` |
| `start` | Move accepted → in_progress | `apm task start 456` |
| `submit-review` | Move in_progress → review | `apm task submit-review 456` |
| `approve` | Move review → completed | `apm task approve 456` |
| `request-changes` | Move review → in_progress | `apm task request-changes 456 --reason "Needs refactor"` |
| `complete` | Mark task complete (legacy) | `apm task complete 456` |
| `add-dependency` | Add task dependency | `apm task add-dependency 456 --blocks 789` |
| `list-dependencies` | Show dependency graph | `apm task list-dependencies 456` |
| `add-blocker` | Add blocker issue | `apm task add-blocker 456 --reason "Waiting for API"` |
| `list-blockers` | Show active blockers | `apm task list-blockers 456` |
| `resolve-blocker` | Mark blocker resolved | `apm task resolve-blocker 456 --blocker-id 12` |
| `types` | List available task types | `apm task types` |

**Common Patterns**:
```bash
# Create and complete task
apm task create "Implement login" --work-item=123 --type=implementation
apm task next 1                             # Auto-advance through states

# Query tasks
apm task list --work-item=123 --type=testing
apm task list --status=in_progress --format=json

# Manage blockers
apm task add-blocker 456 --reason "Database migration pending"
apm task list-blockers 456
apm task resolve-blocker 456 --blocker-id 12 --resolution "Migration complete"
```

---

### `apm context`

**Purpose**: Access hierarchical context (project → work item → task)

**Hierarchy**: Project context includes active work items; work item context includes tasks; task context includes implementation details.

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `show` | Display context at level | `apm context show --level=work-item --id=123` |
| `status` | Context system health | `apm context status` |
| `refresh` | Rebuild context cache | `apm context refresh --work-item=123` |
| `rich` | Rich formatted output | `apm context rich --work-item=123` |
| `wizard` | Interactive context builder | `apm context wizard` |

**Common Patterns**:
```bash
# View project context
apm context show --level=project

# View work item context
apm context show --level=work-item --id=123

# View task context
apm context show --level=task --id=456

# Refresh context after changes
apm context refresh --work-item=123
```

---

## 2. Idea Management

### `apm idea`

**Purpose**: Lightweight brainstorming and idea tracking before formal work items

**Lifecycle**: `idea → research → design → accepted → converted` (or `rejected` at any stage)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `create` | Create new idea | `apm idea create "Dark mode toggle"` |
| `list` | List ideas with filters | `apm idea list --status=research --format=table` |
| `show` | Display idea details | `apm idea show 789` |
| `update` | Update idea fields | `apm idea update 789 --description "Updated description"` |
| `next` | Auto-advance lifecycle | `apm idea next 789` |
| `transition` | Manual state transition | `apm idea transition 789 --to-status=design` |
| `convert` | Convert to work item | `apm idea convert 789 --type=feature` |
| `reject` | Reject idea | `apm idea reject 789 --reason "Out of scope"` |
| `vote` | Vote on idea (up/down) | `apm idea vote 789 --vote=up` |
| `context` | Get idea context | `apm idea context 789` |
| `elements` | Show idea elements | `apm idea elements 789` |

**Common Patterns**:
```bash
# Brainstorm and refine
apm idea create "Real-time notifications"
apm idea next 1                             # idea → research
apm idea update 1 --description "Research WebSocket vs SSE"
apm idea next 1                             # research → design

# Convert to work item
apm idea convert 1 --type=feature           # Creates work item

# Vote on ideas
apm idea vote 1 --vote=up
apm idea list --sort-by=votes
```

---

## 3. Session & Continuity

### `apm session`

**Purpose**: Track AI agent sessions with decisions, outcomes, and next steps

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `start` | Start new session | `apm session start --description "Implement login"` |
| `show` | Display session details | `apm session show 101` |
| `status` | Current active session | `apm session status` |
| `update` | Update session metadata | `apm session update 101 --outcomes "Tests passing"` |
| `end` | End active session | `apm session end --summary "Completed feature"` |
| `history` | List past sessions | `apm session history --limit=10` |
| `add-decision` | Record decision | `apm session add-decision 101 --decision "Use JWT tokens" --rationale "..."` |
| `add-next-step` | Add next action | `apm session add-next-step 101 --step "Deploy to staging"` |

**Common Patterns**:
```bash
# Session lifecycle
apm session start --description "Implement auth"
apm session add-decision --decision "Use bcrypt" --rationale "Industry standard"
apm session add-next-step --step "Write integration tests"
apm session end --summary "Auth system complete"

# Review history
apm session history --work-item=123
apm session show 101 --format=json
```

---

### `apm summary`

**Purpose**: Create hierarchical summaries (session → task → work item → project)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `create` | Create summary | `apm summary create --type=session --entity-id=101 --content "..."` |
| `list` | List summaries | `apm summary list --type=work_item --entity-id=123` |
| `show` | Display summary | `apm summary show 555` |
| `search` | Search summary content | `apm summary search "authentication" --type=task` |
| `delete` | Delete summary | `apm summary delete 555` |
| `stats` | Summary statistics | `apm summary stats` |
| `types` | List summary types | `apm summary types` |

**Summary Types**: `session`, `task`, `work_item`, `project`, `progress`, `outcome`, `decision`, `context`

**Common Patterns**:
```bash
# Create hierarchical summaries
apm summary create --type=session --entity-id=101 --content "Implemented login flow"
apm summary create --type=task --entity-id=456 --content "All tests passing"
apm summary create --type=work_item --entity-id=123 --content "Feature complete"

# Search and analyze
apm summary search "performance" --type=work_item
apm summary list --type=decision --entity-id=123
apm summary stats --format=json
```

---

### `apm memory`

**Purpose**: Manage Claude memory files for continuity

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `export` | Export memory to file | `apm memory export --output=.claude/memory/project.md` |
| `import` | Import memory from file | `apm memory import --file=memory-backup.md` |
| `show` | Display current memory | `apm memory show` |

**Common Patterns**:
```bash
# Backup and restore
apm memory export --output=backup.md
apm memory import --file=backup.md

# View current memory
apm memory show --format=markdown
```

---

## 4. Documentation & Knowledge

### `apm document`

**Purpose**: Manage document references with metadata and relationships

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `add` | Add document reference | `apm document add "API Guide" --path=docs/api.md --type=api_docs` |
| `list` | List documents | `apm document list --type=architecture --format=table` |
| `show` | Display document details | `apm document show 888` |
| `update` | Update document metadata | `apm document update 888 --description "Updated API guide"` |
| `delete` | Delete document reference | `apm document delete 888` |
| `migrate-to-structure` | Migrate to new structure | `apm document migrate-to-structure` |
| `types` | List document types | `apm document types` |

**Document Types**: `architecture`, `design`, `specification`, `user_guide`, `api_docs`, `test_plan`, `deployment_guide`, `troubleshooting`, `changelog`, `adr`, `requirements`, `user_story`, `other`

**Formats**: `markdown`, `html`, `pdf`, `text`, `json`, `yaml`, `other`

**Common Patterns**:
```bash
# Add documentation
apm document add "Architecture Decision Record" \
  --path=docs/adr/001-database-choice.md \
  --type=adr \
  --format=markdown

# Query documents
apm document list --type=api_docs
apm document show 888 --format=json

# Link to work items
apm document add "Feature Spec" --path=docs/login-spec.md --work-item=123
```

---

### `apm template`

**Purpose**: Access JSON templates for work items, tasks, and contexts

**Location**: `agentpm/templates/json` → `.aipm/templates/json` (customization)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | List available templates | `apm template list` |
| `show` | Display template content | `apm template show work_item_feature` |
| `pull` | Copy template for customization | `apm template pull work_item_feature --output=.aipm/templates/json/` |

**Common Patterns**:
```bash
# View templates
apm template list
apm template show task_implementation

# Customize template
apm template pull work_item_feature --output=.aipm/templates/json/
# Edit .aipm/templates/json/work_item_feature.json
```

---

### `apm search`

**Purpose**: Vector search across all entities with semantic matching

**Scopes**: `all` (default), `work_items`, `tasks`, `ideas`, `documents`, `summaries`, `evidence`, `sessions`

#### Command

| Syntax | Purpose | Example |
|--------|---------|---------|
| `apm search QUERY [OPTIONS]` | Semantic search | `apm search "authentication" --scope=work_items --limit=10` |

**Key Options**:
- `--scope {all,work_items,tasks,ideas,documents,summaries,evidence,sessions}`: Search scope
- `--limit N`: Max results (default: 10)
- `--format {table|list|json}`: Output format
- `--min-relevance 0.0-1.0`: Relevance threshold
- `--include-content`: Include full content in results

**Common Patterns**:
```bash
# Search all entities
apm search "login security"

# Scope to specific entity type
apm search "performance" --scope=tasks --limit=20

# High relevance only
apm search "authentication" --min-relevance=0.8 --include-content

# Export results
apm search "API changes" --format=json > results.json
```

---

## 5. Agent & AI Integration

### `apm agents`

**Purpose**: Manage AI agent definitions and metadata

**Agent Tiers**:
1. **Sub-agents**: Single-purpose specialists (e.g., `ac-writer`, `test-runner`)
2. **Specialist**: Domain experts (e.g., `aipm-python-cli-developer`, `aipm-testing-specialist`)
3. **Master orchestrators**: Phase orchestrators (e.g., `definition-orch`, `implementation-orch`)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | List agents with filters | `apm agents list --tier=2 --format=table` |
| `show` | Display agent details | `apm agents show aipm-python-cli-developer` |
| `roles` | List available roles | `apm agents roles` |
| `types` | List agent types | `apm agents types` |
| `generate` | Generate agent .md files | `apm agents generate --role=implementation-orch --output=.claude/agents/` |
| `load` | Load agent from database | `apm agents load --role=testing-specialist` |
| `validate` | Validate agent definition | `apm agents validate --file=.claude/agents/specialists/custom.md` |

**Generation Process**: Database (agent_types + Jinja2 templates) → `.md` files in `.claude/agents/{tier}/{role}.md`

**Common Patterns**:
```bash
# List agents by tier
apm agents list --tier=1                    # Sub-agents
apm agents list --tier=2                    # Specialists
apm agents list --tier=3                    # Orchestrators

# View agent details
apm agents show context-delivery --format=json

# Generate agent files
apm agents generate --role=all --output=.claude/agents/
apm agents generate --role=implementation-orch --output=.claude/agents/orchestrators/
```

---

### `apm claude-code`

**Purpose**: Claude Code integration (checkpoints, settings, stats)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `init` | Initialize Claude Code integration | `apm claude-code init` |
| `status` | Integration status | `apm claude-code status` |
| `stats` | Usage statistics | `apm claude-code stats` |
| `settings` | View/update settings | `apm claude-code settings --key=max_tokens --value=8000` |
| `checkpoint` | Create checkpoint | `apm claude-code checkpoint --message "Before refactor"` |
| `sync` | Sync with Claude | `apm claude-code sync` |
| `validate` | Validate integration | `apm claude-code validate` |
| `export` | Export integration data | `apm claude-code export --output=claude-backup.json` |
| `import-integration` | Import integration data | `apm claude-code import-integration --file=backup.json` |
| `list-integrations` | List integrations | `apm claude-code list-integrations` |
| `generate` | Generate Claude files | `apm claude-code generate --type=memory` |
| `generate-agent` | Generate agent file | `apm claude-code generate-agent --role=testing-specialist` |
| `generate-project` | Generate project context | `apm claude-code generate-project` |
| `clear-cache` | Clear cache | `apm claude-code clear-cache` |
| `hooks` | Manage Git hooks | `apm claude-code hooks install` |
| `show` | Show integration details | `apm claude-code show` |

**Common Patterns**:
```bash
# Setup and verify
apm claude-code init
apm claude-code validate
apm claude-code status

# Create checkpoints
apm claude-code checkpoint --message "Pre-deployment state"

# Generate files
apm claude-code generate-project
apm claude-code generate-agent --role=all
```

---

### `apm provider`

**Purpose**: Manage IDE provider integrations (Cursor, VSCode, Zed)

**Supported Providers**: `cursor` (active), `vscode` (coming), `zed` (coming)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | List available providers | `apm provider list` |
| `status` | Provider status | `apm provider status --provider=cursor` |
| `install` | Install provider integration | `apm provider install --provider=cursor` |
| `uninstall` | Uninstall provider | `apm provider uninstall --provider=cursor` |
| `sync-memories` | Sync memory files | `apm provider sync-memories --provider=cursor` |
| `verify` | Verify provider setup | `apm provider verify --provider=cursor` |

**Common Patterns**:
```bash
# Setup Cursor integration
apm provider install --provider=cursor
apm provider verify --provider=cursor

# Sync memory files
apm provider sync-memories --provider=cursor

# Check status
apm provider status --provider=cursor
```

---

### `apm skills`

**Purpose**: Manage Claude Code skills (specialized capabilities)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list-skills` | List available skills | `apm skills list-skills` |
| `show` | Display skill details | `apm skills show doc-update-author` |
| `generate` | Generate skill files | `apm skills generate --skill=doc-quality-reviewer` |
| `remove` | Remove skill | `apm skills remove --skill=doc-impact-analyzer` |
| `clear` | Clear all skills | `apm skills clear` |

**Common Patterns**:
```bash
# List and explore
apm skills list-skills
apm skills show doc-update-author

# Generate skills
apm skills generate --skill=all
apm skills generate --skill=doc-quality-reviewer
```

---

### `apm commands`

**Purpose**: Manage slash commands for IDE

**Installation Location**: `~/.claude/commands/aipm/`

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | List available commands | `apm commands list` |
| `install` | Install commands | `apm commands install` |
| `update` | Update commands | `apm commands update` |

**Common Patterns**:
```bash
# Setup commands
apm commands install                        # Install to ~/.claude/commands/aipm/

# Update commands
apm commands update

# List installed
apm commands list
```

---

## 6. Configuration & Rules

### `apm rules`

**Purpose**: Manage project rules (database-driven)

**Enforcement Levels**: `BLOCK` (must comply), `WARN` (should comply), `INFO` (informational)

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | List rules | `apm rules list --enforcement=BLOCK --format=table` |
| `show` | Display rule details | `apm rules show DP-001` |
| `create` | Create custom rule | `apm rules create --code=CUSTOM-001 --title="..." --enforcement=WARN` |
| `configure` | Update rule settings | `apm rules configure DP-001 --enforcement=BLOCK` |

**Rule Categories**:
- **DP-001 to DP-008**: Development Principles (Hexagonal, DDD, Service Registry)
- **TES-001 to TES-010**: Testing Standards (AAA pattern, Coverage >90%)
- **SEC-001 to SEC-006**: Security Requirements (Input validation, Encryption)
- **WF-001 to WF-008**: Workflow Governance (Phase gates, Time-boxing)
- **CI-001 to CI-006**: Continuous Integration (Git conventions, Coverage gates)

**Common Patterns**:
```bash
# Query rules
apm rules list --enforcement=BLOCK
apm rules list --category=testing --format=json

# View rule details
apm rules show TES-001

# Configure rules
apm rules configure TES-001 --enforcement=BLOCK
```

---

### `apm testing`

**Purpose**: Configure testing standards and validate compliance

#### Subcommands

| Command | Purpose | Example |
|---------|---------|---------|
| `status` | Testing status | `apm testing status` |
| `show` | Display config | `apm testing show` |
| `export` | Export test results | `apm testing export --output=test-report.json` |
| `install` | Install test infrastructure | `apm testing install` |
| `validate` | Validate test compliance | `apm testing validate --work-item=123` |
| `configure-rules` | Configure test rules | `apm testing configure-rules --coverage-threshold=90` |
| `rules-status` | Test rules status | `apm testing rules-status` |

**Common Patterns**:
```bash
# Check testing status
apm testing status
apm testing rules-status

# Configure standards
apm testing configure-rules --coverage-threshold=90 --require-integration-tests=true

# Validate work item
apm testing validate --work-item=123
```

---

## 7. Database & Maintenance

### `apm migrate`

**Purpose**: Run pending database migrations

**Location**: `migrations/files/` with `upgrade()` and `downgrade()` functions

#### Command

| Syntax | Purpose | Example |
|--------|---------|---------|
| `apm migrate` | Run pending migrations | `apm migrate` |
| `apm migrate --list` | List pending | `apm migrate --list` |
| `apm migrate --show-applied` | Show history | `apm migrate --show-applied` |

**Common Patterns**:
```bash
# Check pending migrations
apm migrate --list

# Apply migrations
apm migrate

# View history
apm migrate --show-applied
```

---

### `apm migrate-v1-to-v2`

**Purpose**: Migrate from AIPM V1 (file-based) to V2 (database-driven)

**Process**: 4-phase atomic migration
1. **Backup**: Create safety backup
2. **Migrate**: Move data (rules, summaries, work items)
3. **Validate**: Verify data integrity
4. **Cleanup/Rollback**: Clean up or restore on failure

**Migrations**:
- `_RULES/*.md` → `rules` table
- `STATUS.md` → `summaries` table
- `NEXT-SESSION.md` → `summaries` table
- Work items and tasks to new schema

#### Command

| Syntax | Purpose | Example |
|--------|---------|---------|
| `apm migrate-v1-to-v2` | Run migration | `apm migrate-v1-to-v2` |
| `apm migrate-v1-to-v2 --dry-run` | Preview only | `apm migrate-v1-to-v2 --dry-run` |
| `apm migrate-v1-to-v2 --force` | Force migration | `apm migrate-v1-to-v2 --force` |

**Common Patterns**:
```bash
# Preview migration
apm migrate-v1-to-v2 --dry-run

# Run migration
apm migrate-v1-to-v2

# Force if already partially migrated
apm migrate-v1-to-v2 --force
```

---

## Quick Command Patterns

### Workflow Progression

**Create Feature Start to Finish**:
```bash
# 1. Create work item
apm work-item create "User authentication" --type=feature

# 2. Progress through states (using 'next' for simplicity)
apm work-item next 1                        # draft → validated
apm work-item next 1                        # validated → accepted
apm work-item next 1                        # accepted → in_progress

# 3. Create and complete tasks
apm task create "Implement login" --work-item=1 --type=implementation
apm task next 1                             # Auto-advance to completion

# 4. Submit and approve work item
apm work-item next 1                        # in_progress → review
apm work-item next 1                        # review → completed (if approved)
```

**Or Using Explicit Commands** (more control):
```bash
# 1. Create and validate
apm work-item create "Feature" --type=feature
apm work-item validate 1

# 2. Accept with agent assignment
apm work-item accept 1 --agent "implementation-orch"

# 3. Start work
apm work-item start 1

# 4. Submit for review
apm work-item submit-review 1

# 5. Approve or request changes
apm work-item approve 1
# OR
apm work-item request-changes 1 --reason "Missing tests"
```

---

### Filtering & Querying

**Common Filter Patterns**:
```bash
# By status
apm work-item list --status=in_progress
apm task list --status=review

# By type
apm work-item list --type=feature
apm task list --type=testing

# By phase
apm work-item list --phase=I1_IMPLEMENTATION

# By date
apm work-item list --created-after=2025-10-01
apm task list --updated-before=2025-10-23

# By assigned agent
apm task list --agent="aipm-testing-specialist"

# Combining filters
apm work-item list --type=feature --status=in_progress --phase=I1_IMPLEMENTATION

# Output formats
apm work-item list --format=json
apm task list --format=table
```

---

### Output Formats

**Commands Supporting Multiple Formats**:
- `--format=table`: Human-readable table (default)
- `--format=json`: Machine-readable JSON
- `--format=list`: Simple list

**Examples**:
```bash
# JSON for scripting
apm status --format=json | jq '.work_items[] | select(.status=="in_progress")'

# Table for viewing
apm work-item list --format=table

# List for simple output
apm agents list --format=list
```

---

### Session Management Patterns

**Daily Workflow**:
```bash
# Morning: Start session
apm session start --description "Implement authentication feature"
apm context show --level=project              # Review context

# During work: Record decisions
apm session add-decision --decision "Use JWT tokens" --rationale "Stateless, scalable"
apm session add-next-step --step "Write integration tests"

# Evening: End session
apm session end --summary "Login flow complete, tests passing"
apm session add-next-step --step "Deploy to staging tomorrow"

# Next morning: Review history
apm session history --limit=1
apm session show $(apm session history --limit=1 --format=json | jq -r '.[0].id')
```

---

### Dependency Management

**Work Item Dependencies**:
```bash
# Add dependency
apm work-item add-dependency 123 --blocks 456

# View dependency graph
apm work-item list-dependencies 123

# Remove dependency
apm work-item remove-dependency 123 --dependency-id 789
```

**Task Dependencies**:
```bash
# Add dependency
apm task add-dependency 456 --requires 789

# Add blocker
apm task add-blocker 456 --reason "Waiting for API endpoint"

# List blockers
apm task list-blockers 456

# Resolve blocker
apm task resolve-blocker 456 --blocker-id 12 --resolution "API deployed"
```

---

### Context and Search

**Hierarchical Context Access**:
```bash
# Project-level context (all active work)
apm context show --level=project

# Work item context (tasks, progress)
apm context show --level=work-item --id=123

# Task context (implementation details)
apm context show --level=task --id=456

# Refresh after changes
apm context refresh --work-item=123
```

**Search Across Entities**:
```bash
# Find all mentions of "authentication"
apm search "authentication" --include-content

# Search specific entity type
apm search "performance" --scope=tasks

# High-confidence matches only
apm search "security" --min-relevance=0.8

# Export results
apm search "API changes" --format=json > search-results.json
```

---

## Appendices

### A. Work Item Types

| Type | Required Tasks | Time-Boxing | Use Case |
|------|----------------|-------------|----------|
| `feature` | DESIGN + IMPL + TEST + DOC | DESIGN ≤8h, IMPL ≤4h, TEST ≤6h | New functionality |
| `bugfix` | ANALYSIS + BUGFIX + TESTING | BUGFIX ≤4h, TEST ≤6h | Fix defects |
| `research` | ANALYSIS + DOC | ANALYSIS ≤8h | Investigation |
| `planning` | (no IMPL) | DESIGN ≤8h | Architecture, planning |
| `refactoring` | ANALYSIS + REFACTORING + TEST | Each ≤4h | Code improvement |
| `infrastructure` | DESIGN + DEPLOY + TEST + DOC | DESIGN ≤8h, DEPLOY ≤4h | DevOps, tooling |
| `enhancement` | IMPL + TEST | IMPL ≤4h, TEST ≤6h | Improve existing feature |

**Quality Gates**:
- **D1_DISCOVERY**: `business_context` (≥50 chars), `acceptance_criteria` (≥3), `risks` (≥1), 6W confidence (≥0.70)
- **P1_PLAN**: Tasks created, estimates complete, dependencies mapped
- **I1_IMPLEMENTATION**: Code complete, tests updated, docs updated
- **R1_REVIEW**: All AC verified, tests pass, quality checks pass
- **O1_OPERATIONS**: Deployed, health checks pass, monitoring active
- **E1_EVOLUTION**: Telemetry analyzed, improvements identified

---

### B. Task Types & Time Limits

| Task Type | Time Limit | Enforcement | Use Case |
|-----------|------------|-------------|----------|
| `implementation` | ≤4 hours | STRICT | Code implementation |
| `testing` | ≤6 hours | Recommended | Test creation |
| `design` | ≤8 hours | Recommended | Design work |
| `documentation` | ≤4 hours | Recommended | Documentation |
| `bugfix` | ≤4 hours | STRICT | Bug fixes |
| `analysis` | ≤8 hours | Recommended | Research, analysis |
| `deployment` | ≤4 hours | Recommended | Deployment tasks |
| `review` | ≤2 hours | Recommended | Code review |
| `refactoring` | ≤4 hours | STRICT | Refactoring |

**Time-Boxing Violations**:
- **BLOCK-level rules** will prevent task creation if time limit exceeded
- Tasks exceeding limits should be broken down into smaller tasks

---

### C. Entity Lifecycle States

#### Work Item States

```
draft → validated → accepted → in_progress → review → completed
  ↓         ↓          ↓           ↓           ↓
  └─────────┴──────────┴───────────┴───────────┴────→ cancelled
```

**State Transitions**:
- `draft → validated`: Work item definition complete
- `validated → accepted`: Assigned to agent, planning complete
- `accepted → in_progress`: Active implementation
- `in_progress → review`: Implementation complete, ready for QA
- `review → completed`: All checks pass, approved
- `review → in_progress`: Changes requested
- `any → cancelled`: Work abandoned

**Phase Progression** (parallel to states):
```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION
```

---

#### Task States

```
draft → validated → accepted → in_progress → review → completed
  ↓         ↓          ↓           ↓           ↓
  └─────────┴──────────┴───────────┴───────────┴────→ cancelled
```

**State Transitions**: Same as work items, but at task granularity

---

#### Idea Lifecycle

```
idea → research → design → accepted → converted
  ↓       ↓         ↓         ↓
  └───────┴─────────┴─────────┴───────────────→ rejected
```

**State Transitions**:
- `idea → research`: Start investigation
- `research → design`: Start design work
- `design → accepted`: Design approved
- `accepted → converted`: Create work item (terminal state)
- `any → rejected`: Idea rejected (terminal state)

---

### D. Search Scopes

| Scope | Description | Searchable Fields |
|-------|-------------|-------------------|
| `all` | All entities (default) | All fields across all entities |
| `work_items` | Work items only | name, description, business_context, acceptance_criteria |
| `tasks` | Tasks only | objective, description, acceptance_criteria |
| `ideas` | Ideas only | title, description, rationale |
| `documents` | Documents only | title, description, path, content |
| `summaries` | Summaries only | type, content |
| `evidence` | Evidence only | type, source, excerpt |
| `sessions` | Sessions only | description, decisions, outcomes, next_steps |

**Search Features**:
- **Semantic matching**: Uses embeddings for meaning-based search
- **Relevance scoring**: Results ranked by relevance (0.0-1.0)
- **Cross-entity search**: Search across multiple entity types simultaneously
- **Content filtering**: `--min-relevance` threshold for quality
- **Full content**: `--include-content` to return complete records

**Examples**:
```bash
# Find authentication work across all entities
apm search "authentication" --min-relevance=0.7

# Find performance-related tasks
apm search "performance optimization" --scope=tasks --limit=20

# Find design decisions in sessions
apm search "architecture decision" --scope=sessions --include-content

# Export comprehensive search results
apm search "security" --format=json --include-content > security-audit.json
```

---

## See Also

- **User Guide**: `docs/user-guide/` - Comprehensive usage documentation
- **Developer Guide**: `docs/developer-guide/` - Development patterns and architecture
- **CLAUDE.md**: Project instructions for AI agents
- **Rules Reference**: `apm rules list` - Live database of project rules
- **Agent Reference**: `.claude/agents/` - Agent SOPs and definitions

---

**Version**: 5.0.0
**Last Updated**: 2025-10-23
**Format**: Quick Reference
**Target**: Developers and AI agents needing rapid command lookup
