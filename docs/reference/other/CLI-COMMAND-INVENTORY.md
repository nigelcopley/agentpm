# APM (Agent Project Manager) CLI Command Inventory

**Complete reference of all existing `apm` commands extracted from actual code.**

**Purpose**: Authoritative command reference for agents and developers
**Source**: `agentpm/cli/commands/` (code analysis, not documentation)
**Last Updated**: 2025-10-17

---

## Command Groups Overview

| Group | Commands | Purpose |
|-------|----------|---------|
| **Core** | init, status, migrate | Project initialization and management |
| **Work Items** | 16 commands | Feature, bug, research management |
| **Tasks** | 17 commands | Atomic work units with time-boxing |
| **Ideas** | 10 commands | Lightweight brainstorming |
| **Context** | 5 commands | AI agent context assembly |
| **Sessions** | 8 commands | Development session tracking |
| **Agents** | 5 commands | AI agent management |
| **Rules** | 4 commands | Project rules configuration |
| **Documents** | 5 commands | Document reference management |
| **Summary** | 6 commands | Hierarchical summaries |
| **Testing** | 7 commands | Testing configuration |
| **Utilities** | template, principles, hooks, commands | System utilities |

**Total Commands**: 88+ (counting subcommands)

---

## Core Commands

### `apm init`
Initialize AIPM project with database and plugin detection.

**Syntax**:
```bash
apm init PROJECT_NAME [PATH] [OPTIONS]
```

**Arguments**:
- `PROJECT_NAME` (required) - Project name
- `PATH` (optional) - Project path (default: current directory)

**Options**:
- `--description`, `-d` - Project description
- `--skip-questionnaire` - Skip rules questionnaire, use default preset

**What it does**:
- Creates `.aipm/` directory structure
- Initializes SQLite database with complete schema
- Runs plugin detection (frameworks, languages, tools)
- Generates project-specific agents
- Optionally runs rules questionnaire
- Creates testing configuration

**Performance**: <5 seconds with progress feedback

**Example**:
```bash
apm init "My Project"                    # Initialize in current directory
apm init "API Server" ./backend          # Initialize in specific path
apm init "Website" . -d "E-commerce"     # With description
apm init "CLI Tool" --skip-questionnaire # Skip questionnaire
```

---

### `apm status`
Show project health dashboard.

**Syntax**:
```bash
apm status [OPTIONS]
```

**Options**:
- `--format` - Output format: `dashboard` (default) or `json`

**What it does**:
- Displays project overview (name, path, status)
- Work items summary (by type and status)
- Tasks overview (by status, time-boxing compliance)
- Quality metrics

**Performance**: <1 second

**Example**:
```bash
apm status                # Full dashboard
apm status --format=json  # JSON output for scripts
```

---

### `apm migrate`
Run database migrations.

**Syntax**:
```bash
apm migrate [OPTIONS]
```

**What it does**:
- Applies pending database schema migrations
- Ensures database schema is up to date

---

### `apm migrate-v1-to-v2`
Migrate from AIPM v1 to v2.

**Syntax**:
```bash
apm migrate-v1-to-v2 [OPTIONS]
```

**What it does**:
- Migrates projects from v1 database schema to v2
- Preserves existing data and relationships

---

## Work Item Commands (`apm work-item`)

Work items are the primary organizational unit for delivering value.

**Work Item Types**:
- `feature` - New functionality (requires DESIGN+IMPL+TEST+DOC)
- `bugfix` - Bug fixes (requires ANALYSIS+BUGFIX+TESTING)
- `research` - Investigation (requires ANALYSIS+DOCUMENTATION)
- `planning` - Planning (forbids IMPLEMENTATION)
- `refactoring` - Code improvement (requires ANALYSIS+REFACTORING+TESTING)
- `infrastructure` - DevOps (requires DESIGN+DEPLOYMENT+TESTING+DOC)
- `enhancement` - Improvements (requires IMPLEMENTATION+TESTING)

### `apm work-item create`
Create new work item with type-specific quality gates.

**Syntax**:
```bash
apm work-item create NAME --type=TYPE [OPTIONS]
```

**Arguments**:
- `NAME` (required) - Work item name

**Required Options**:
- `--type`, `-t` - Work item type (see types above)

**Basic Options**:
- `--description`, `-d` - Work item description
- `--priority`, `-p` - Priority (1=highest, 5=lowest, default=3)
- `--continuous/--no-continuous` - Mark as continuous backlog (defaults by type)

**Business Context Options**:
- `--business-context` - Business justification and impact
- `--acceptance-criteria` - JSON array of acceptance criteria

**6W Framework Options**:
- `--who` - WHO: Target users/stakeholders
- `--what` - WHAT: What is being built
- `--where` - WHERE: System boundaries/locations
- `--when` - WHEN: Timeline/deadlines
- `--why` - WHY: Business value/rationale
- `--how` - HOW: Technical approach

**Quality & Metadata Options**:
- `--quality-target` - JSON object with quality standards
- `--ownership` - JSON object with RACI roles
- `--scope` - JSON object with in_scope/out_of_scope arrays
- `--artifacts` - JSON object with code_paths/docs_paths arrays
- `--phase` - Phase in lifecycle (D1, P1, I1, R1, O1, E1)
- `--metadata-template` - Seed metadata from template ID

**Example**:
```bash
# Basic work item
apm work-item create "Add OAuth2" --type=feature

# With business context
apm work-item create "Add OAuth2" --type=feature \
  --business-context "Enable personalized dashboards"

# With full 6W context
apm work-item create "User Authentication" \
  --type=feature \
  --priority=1 \
  --business-context "Secure user access" \
  --acceptance-criteria '["Users can login", "JWT tokens issued"]' \
  --who "Small business owners, Enterprise customers" \
  --what "OAuth2 authentication system" \
  --where "auth-service, user-api, frontend" \
  --when "Q2 2025, Before product launch" \
  --why "Protect user data, Enable personalization" \
  --how "OAuth2 flow, JWT tokens, Redis session store"
```

---

### `apm work-item list`
List work items with filters.

**Syntax**:
```bash
apm work-item list [OPTIONS]
```

**Options**:
- `--type` - Filter by work item type
- `--status` - Filter by status
- `--priority` - Filter by priority
- `--format` - Output format: `table` (default) or `json`

**Example**:
```bash
apm work-item list                              # All work items
apm work-item list --type=feature               # Only features
apm work-item list --status=in_progress         # Active work items
apm work-item list --priority=1                 # High priority items
apm work-item list --format=json                # JSON output
```

---

### `apm work-item show`
Display work item details.

**Syntax**:
```bash
apm work-item show ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Work item ID

**What it shows**:
- Full work item details
- Associated tasks
- Quality gates status
- 6W context (if available)
- Progress tracking

**Example**:
```bash
apm work-item show 123
```

---

### `apm work-item validate`
Validate work item against quality gates.

**Syntax**:
```bash
apm work-item validate ID
```

**Arguments**:
- `ID` (required) - Work item ID

**What it does**:
- Checks if work item meets all quality gates
- Validates required tasks exist
- Checks acceptance criteria
- Reports validation errors

---

### `apm work-item accept`
Accept validated work item (VALIDATED → ACCEPTED).

**Syntax**:
```bash
apm work-item accept ID --agent AGENT
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- `--agent` (required) - Agent role accepting the work item

---

### `apm work-item start`
Start work item (ACCEPTED → IN_PROGRESS).

**Syntax**:
```bash
apm work-item start ID
```

**Arguments**:
- `ID` (required) - Work item ID

---

### `apm work-item submit-review`
Submit work item for review (IN_PROGRESS → REVIEW).

**Syntax**:
```bash
apm work-item submit-review ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- `--notes` - Submission notes

---

### `apm work-item approve`
Approve work item (REVIEW → COMPLETED).

**Syntax**:
```bash
apm work-item approve ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- `--notes` - Approval notes

---

### `apm work-item request-changes`
Request changes to work item (REVIEW → IN_PROGRESS).

**Syntax**:
```bash
apm work-item request-changes ID --reason REASON
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- `--reason` (required) - Reason for requesting changes

---

### `apm work-item update`
Update work item details.

**Syntax**:
```bash
apm work-item update ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- All options from `create` command can be used to update

---

### `apm work-item next`
Get next work item to work on (smart prioritization).

**Syntax**:
```bash
apm work-item next [OPTIONS]
```

**What it does**:
- Suggests next work item based on priority, status, and dependencies

---

### Work Item Phase Commands

#### `apm work-item phase-status`
Show phase gate status for work item.

**Syntax**:
```bash
apm work-item phase-status ID
```

---

#### `apm work-item phase-validate`
Validate if work item can advance to next phase.

**Syntax**:
```bash
apm work-item phase-validate ID --phase PHASE
```

**Options**:
- `--phase` (required) - Target phase (D1, P1, I1, R1, O1, E1)

---

#### `apm work-item phase-advance`
Advance work item to next phase.

**Syntax**:
```bash
apm work-item phase-advance ID --phase PHASE
```

**Options**:
- `--phase` (required) - Target phase

---

### Work Item Summary Commands

#### `apm work-item add-summary`
Add summary to work item.

**Syntax**:
```bash
apm work-item add-summary ID --content CONTENT [OPTIONS]
```

**Arguments**:
- `ID` (required) - Work item ID

**Options**:
- `--content` (required) - Summary content
- `--type` - Summary type (progress, milestone, decision)

---

#### `apm work-item show-history`
Show work item summary history.

**Syntax**:
```bash
apm work-item show-history ID
```

**Arguments**:
- `ID` (required) - Work item ID

---

### Work Item Dependency Commands

#### `apm work-item add-dependency`
Add dependency to work item.

**Syntax**:
```bash
apm work-item add-dependency ID --depends-on OTHER_ID
```

**Options**:
- `--depends-on` (required) - ID of work item this depends on

---

#### `apm work-item list-dependencies`
List work item dependencies.

**Syntax**:
```bash
apm work-item list-dependencies ID
```

**Arguments**:
- `ID` (required) - Work item ID

---

#### `apm work-item remove-dependency`
Remove dependency from work item.

**Syntax**:
```bash
apm work-item remove-dependency ID --dependency-id DEP_ID
```

**Options**:
- `--dependency-id` (required) - Dependency ID to remove

---

## Task Commands (`apm task`)

Tasks are atomic units of work with strict time-boxing.

**Task Types & Time Limits**:
- `implementation` - Code changes (≤4h STRICT)
- `testing` - Test coverage (≤6h)
- `design` - Architecture/design (≤8h)
- `documentation` - Docs/guides (≤4h)
- `bugfix` - Bug fixes (≤4h)
- `analysis` - Investigation (≤6h)
- `review` - Code review (≤2h)
- `deployment` - Deployment tasks (≤4h)
- `refactoring` - Code improvement (≤6h)
- `research` - Research tasks (≤8h)

### `apm task create`
Create new task with time-box validation.

**Syntax**:
```bash
apm task create NAME --type=TYPE [OPTIONS]
```

**Arguments**:
- `NAME` (required) - Task name

**Required Options**:
- `--type`, `-t` - Task type (see types above)

**Basic Options**:
- `--work-item-id` - Work item ID (required for non-bugfix tasks)
- `--effort` - Estimated effort in hours (validates against time-box limits)
- `--description`, `-d` - Task description
- `--priority`, `-p` - Priority (1=highest, 5=lowest, default=3)

**Quality Options**:
- `--acceptance-criteria` - JSON array of acceptance criteria
- `--implementation-notes` - Implementation guidance
- `--test-requirements` - JSON object with test requirements
- `--quality-template` - Seed quality metadata from template ID

**What it does**:
- Creates task with strict time-box validation
- IMPLEMENTATION tasks ≤4h enforced
- Auto-attaches bugfix tasks to continuous backlog if no work-item-id
- Validates task type is allowed for parent work item

**Example**:
```bash
# Basic task
apm task create "Design auth schema" \
  --work-item-id=1 \
  --type=design \
  --effort=3

# With acceptance criteria
apm task create "Implement User model" \
  --work-item-id=1 \
  --type=implementation \
  --effort=3.5 \
  --acceptance-criteria '["User model created", "Migrations generated"]'

# With implementation notes
apm task create "Add JWT endpoint" \
  --work-item-id=1 \
  --type=implementation \
  --effort=3 \
  --implementation-notes "Follow src/auth/views.py pattern"

# With test requirements
apm task create "Write auth tests" \
  --work-item-id=1 \
  --type=testing \
  --effort=4 \
  --test-requirements '{"min_coverage": 0.95, "test_types": ["unit"]}'
```

---

### `apm task list`
List tasks with filters.

**Syntax**:
```bash
apm task list [OPTIONS]
```

**Options**:
- `--work-item-id` - Filter by work item
- `--type` - Filter by task type
- `--status` - Filter by status
- `--format` - Output format: `table` (default) or `json`

**Example**:
```bash
apm task list                              # All tasks
apm task list --work-item-id=1             # Tasks for work item
apm task list --type=implementation        # Implementation tasks
apm task list --status=in_progress         # Active tasks
```

---

### `apm task show`
Display task details.

**Syntax**:
```bash
apm task show ID
```

**Arguments**:
- `ID` (required) - Task ID

---

### `apm task validate`
Validate task (DRAFT → PROPOSED).

**Syntax**:
```bash
apm task validate ID
```

**Arguments**:
- `ID` (required) - Task ID

---

### `apm task accept`
Accept task (VALIDATED → ACCEPTED).

**Syntax**:
```bash
apm task accept ID --agent AGENT
```

**Arguments**:
- `ID` (required) - Task ID

**Options**:
- `--agent` (required) - Agent role accepting the task

---

### `apm task start`
Start task (ACCEPTED → IN_PROGRESS).

**Syntax**:
```bash
apm task start ID
```

**Arguments**:
- `ID` (required) - Task ID

---

### `apm task submit-review`
Submit task for review (IN_PROGRESS → REVIEW).

**Syntax**:
```bash
apm task submit-review ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Task ID

**Options**:
- `--notes` - Submission notes

---

### `apm task approve`
Approve task (REVIEW → COMPLETED).

**Syntax**:
```bash
apm task approve ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Task ID

**Options**:
- `--notes` - Approval notes

---

### `apm task request-changes`
Request changes to task (REVIEW → IN_PROGRESS).

**Syntax**:
```bash
apm task request-changes ID --reason REASON
```

**Arguments**:
- `ID` (required) - Task ID

**Options**:
- `--reason` (required) - Reason for requesting changes

---

### `apm task complete`
Mark task as completed (legacy, use approve).

**Syntax**:
```bash
apm task complete ID
```

**Arguments**:
- `ID` (required) - Task ID

---

### `apm task update`
Update task details.

**Syntax**:
```bash
apm task update ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Task ID

**Options**:
- All options from `create` command can be used to update

---

### `apm task next`
Get next task to work on (smart prioritization).

**Syntax**:
```bash
apm task next [OPTIONS]
```

**Options**:
- `--work-item-id` - Limit to specific work item

---

### Task Dependency Commands

#### `apm task add-dependency`
Add dependency to task.

**Syntax**:
```bash
apm task add-dependency ID --depends-on OTHER_ID
```

**Options**:
- `--depends-on` (required) - ID of task this depends on

---

#### `apm task add-blocker`
Add blocker to task.

**Syntax**:
```bash
apm task add-blocker ID --reason REASON
```

**Options**:
- `--reason` (required) - Reason for blocker

---

#### `apm task list-dependencies`
List task dependencies.

**Syntax**:
```bash
apm task list-dependencies ID
```

**Arguments**:
- `ID` (required) - Task ID

---

#### `apm task list-blockers`
List task blockers.

**Syntax**:
```bash
apm task list-blockers ID
```

**Arguments**:
- `ID` (required) - Task ID

---

#### `apm task resolve-blocker`
Resolve task blocker.

**Syntax**:
```bash
apm task resolve-blocker ID --blocker-id BLOCKER_ID
```

**Options**:
- `--blocker-id` (required) - Blocker ID to resolve

---

## Idea Commands (`apm idea`)

Ideas support lightweight brainstorming before formal work items.

**Idea Lifecycle**:
- `idea` → `research` → `design` → `accepted` → `converted` (terminal)
- Any state → `rejected` (terminal)

### `apm idea create`
Create new idea for lightweight brainstorming.

**Syntax**:
```bash
apm idea create TITLE [OPTIONS]
```

**Arguments**:
- `TITLE` (required) - Idea title

**Options**:
- `--description`, `-d` - Detailed description
- `--source`, `-s` - Origin of idea (user, ai_suggestion, brainstorming_session, customer_feedback, competitor_analysis, other)
- `--created-by` - Creator identifier (username, email, agent name)
- `--tags`, `-t` - Tags for categorization (can be specified multiple times)

**Example**:
```bash
# Simple idea
apm idea create "Add OAuth2 authentication"

# With description and tags
apm idea create "Add OAuth2 authentication" \
  --description "Support Google/GitHub sign-in" \
  --tags security --tags ux --tags quick-win

# From customer feedback
apm idea create "Dark mode support" \
  --source customer_feedback \
  --created-by "jane@company.com" \
  --tags ui --tags accessibility
```

---

### `apm idea list`
List ideas with filters.

**Syntax**:
```bash
apm idea list [OPTIONS]
```

**Options**:
- `--status` - Filter by status
- `--source` - Filter by source
- `--tags` - Filter by tags

---

### `apm idea show`
Display idea details.

**Syntax**:
```bash
apm idea show ID
```

**Arguments**:
- `ID` (required) - Idea ID

---

### `apm idea vote`
Vote on idea (+1/-1).

**Syntax**:
```bash
apm idea vote ID [--upvote|--downvote]
```

**Arguments**:
- `ID` (required) - Idea ID

**Options**:
- `--upvote` - Upvote the idea (+1)
- `--downvote` - Downvote the idea (-1)

---

### `apm idea update`
Update idea details.

**Syntax**:
```bash
apm idea update ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Idea ID

**Options**:
- All options from `create` command

---

### `apm idea transition`
Move idea through workflow.

**Syntax**:
```bash
apm idea transition ID STATUS
```

**Arguments**:
- `ID` (required) - Idea ID
- `STATUS` (required) - Target status (research, design, accepted)

---

### `apm idea reject`
Reject idea with reason.

**Syntax**:
```bash
apm idea reject ID --reason REASON
```

**Arguments**:
- `ID` (required) - Idea ID

**Options**:
- `--reason` (required) - Rejection reason

---

### `apm idea convert`
Convert idea to work item.

**Syntax**:
```bash
apm idea convert ID --type TYPE
```

**Arguments**:
- `ID` (required) - Idea ID

**Options**:
- `--type` (required) - Work item type

---

### `apm idea context`
Show context for idea.

**Syntax**:
```bash
apm idea context ID
```

**Arguments**:
- `ID` (required) - Idea ID

---

### `apm idea next`
Get next idea to review (smart prioritization).

**Syntax**:
```bash
apm idea next [OPTIONS]
```

---

## Context Commands (`apm context`)

Access hierarchical project context for AI agents.

**Context Hierarchy**:
- Project → Governance, tech stack, standards
- Work Item → Business requirements, acceptance criteria
- Task → Implementation details, code files, patterns

### `apm context show`
Display hierarchical context with confidence scoring.

**Syntax**:
```bash
apm context show [OPTIONS]
```

**Options**:
- `--project` - Show project-level context
- `--work-item-id` - Show work item context
- `--task-id` - Show task context
- `--format` - Output format: `rich` (default) or `json`

**Example**:
```bash
apm context show --project               # Project context
apm context show --work-item-id=1        # Work item context
apm context show --task-id=5             # Task context
apm context show --task-id=5 --format=json  # JSON output
```

---

### `apm context refresh`
Regenerate context (trigger plugin detection).

**Syntax**:
```bash
apm context refresh [OPTIONS]
```

**Options**:
- `--task-id` - Refresh task context
- `--work-item-id` - Refresh work item context

---

### `apm context status`
Show context freshness and quality metrics.

**Syntax**:
```bash
apm context status [OPTIONS]
```

---

### `apm context rich`
Display rich context visualization.

**Syntax**:
```bash
apm context rich [OPTIONS]
```

**Options**:
- `--task-id` - Show rich task context
- `--work-item-id` - Show rich work item context

---

### `apm context wizard`
Interactive context assembly wizard.

**Syntax**:
```bash
apm context wizard [OPTIONS]
```

---

## Session Commands (`apm session`)

Manage development sessions and history.

Sessions are automatically tracked via hooks (SessionStart/SessionEnd).

### `apm session status`
Show current active session with activity summary.

**Syntax**:
```bash
apm session status
```

---

### `apm session start`
Manually start session (hooks do this automatically).

**Syntax**:
```bash
apm session start [OPTIONS]
```

**Options**:
- `--work-item-id` - Associate with work item
- `--task-id` - Associate with task

---

### `apm session end`
Manually end session (hooks do this automatically).

**Syntax**:
```bash
apm session end [OPTIONS]
```

**Options**:
- `--summary` - Session summary

---

### `apm session show`
Display session details (current or specific).

**Syntax**:
```bash
apm session show [SESSION_ID]
```

**Arguments**:
- `SESSION_ID` (optional) - Specific session ID (defaults to current)

---

### `apm session update`
Update session summary and priority.

**Syntax**:
```bash
apm session update [OPTIONS]
```

**Options**:
- `--summary` - Update session summary
- `--priority` - Update priority

---

### `apm session add-decision`
Add key decision to current session.

**Syntax**:
```bash
apm session add-decision DECISION [OPTIONS]
```

**Arguments**:
- `DECISION` (required) - Decision description

**Options**:
- `--rationale` - Rationale for decision

**Example**:
```bash
apm session add-decision "Use Pydantic for validation" \
  --rationale "Type safety and better error messages"
```

---

### `apm session add-next-step`
Add action item for next session.

**Syntax**:
```bash
apm session add-next-step STEP
```

**Arguments**:
- `STEP` (required) - Next step description

---

### `apm session history`
View session history with filters.

**Syntax**:
```bash
apm session history [OPTIONS]
```

**Options**:
- `--days` - Last N days
- `--work-item` - Filter by work item ID
- `--search` - Search in decisions/summaries
- `--format` - Output format: `table` (default) or `json`

**Example**:
```bash
apm session history --days 7                # Last week
apm session history --work-item 35          # Sessions on WI-35
apm session history --search "pydantic"     # Search decisions
```

---

## Agent Commands (`apm agents`)

Manage AI agents for project specialization.

**Agent Tiers**:
- Tier 1: Sub-agents (Research & Analysis)
- Tier 2: Specialist agents (Implementation)
- Tier 3: Master orchestrators (Routing & Delegation)

### `apm agents list`
List all agents with filtering.

**Syntax**:
```bash
apm agents list [OPTIONS]
```

**Options**:
- `--tier` - Filter by tier (1, 2, 3)
- `--active-only` - Show only active agents
- `--format` - Output format: `table` (default) or `json`

**Example**:
```bash
apm agents list                    # All agents
apm agents list --tier 2           # Specialist agents only
apm agents list --active-only      # Active agents only
```

---

### `apm agents show`
Display detailed agent information.

**Syntax**:
```bash
apm agents show ROLE
```

**Arguments**:
- `ROLE` (required) - Agent role name

**Example**:
```bash
apm agents show aipm-database-developer
```

---

### `apm agents generate`
Generate agent .md files from database.

**Syntax**:
```bash
apm agents generate [OPTIONS]
```

**Options**:
- `--all` - Generate all agent files
- `--role` - Generate specific agent role
- `--llm` - LLM to use (claude, openai)
- `--force` - Overwrite existing files

**Example**:
```bash
# Generate all agents
apm agents generate --all --llm claude

# Generate single agent
apm agents generate --role aipm-python-cli-developer

# Force regeneration
apm agents generate --all --force
```

---

### `apm agents validate`
Validate agent against rules.

**Syntax**:
```bash
apm agents validate ROLE
```

**Arguments**:
- `ROLE` (required) - Agent role to validate

**Example**:
```bash
apm agents validate aipm-testing-specialist
```

---

### `apm agents roles`
Show all available agent roles.

**Syntax**:
```bash
apm agents roles
```

---

## Rules Commands (`apm rules`)

Manage project rules and configuration.

### `apm rules list`
List all active rules.

**Syntax**:
```bash
apm rules list [OPTIONS]
```

**Options**:
- `--enforcement`, `-e` - Filter by enforcement level (BLOCK, WARN, INFO, SUGGEST)
- `--category`, `-c` - Filter by category
- `--format` - Output format: `table` (default) or `json`

**Example**:
```bash
apm rules list                          # All rules
apm rules list -e BLOCK                 # Blocking rules only
apm rules list -c code_quality          # Category filter
```

---

### `apm rules show`
Display rule details.

**Syntax**:
```bash
apm rules show RULE_ID
```

**Arguments**:
- `RULE_ID` (required) - Rule ID (e.g., DP-001)

**Example**:
```bash
apm rules show DP-001
```

---

### `apm rules configure`
Re-run rules questionnaire.

**Syntax**:
```bash
apm rules configure [OPTIONS]
```

**Options**:
- `--preset` - Use specific preset (standard, strict, relaxed)
- `--force` - Overwrite existing rules

---

### `apm rules create`
Create custom rule.

**Syntax**:
```bash
apm rules create [OPTIONS]
```

**Options**:
- `--rule-id` (required) - Rule ID
- `--title` (required) - Rule title
- `--category` (required) - Rule category
- `--enforcement` (required) - Enforcement level
- `--description` - Rule description

---

## Document Commands (`apm document`)

Manage document references for work items, tasks, and ideas.

**Document Types**:
- architecture, design, specification, user_guide, api_docs
- test_plan, deployment_guide, troubleshooting, changelog
- adr, requirements, user_story, other

**Document Formats**:
- markdown, html, pdf, text, json, yaml, other

### `apm document add`
Add document to entity.

**Syntax**:
```bash
apm document add [OPTIONS]
```

**Options**:
- `--entity-type` (required) - Entity type (work-item, task, idea)
- `--entity-id` (required) - Entity ID
- `--file-path` (required) - Document file path
- `--type` (required) - Document type
- `--title` - Document title
- `--description` - Document description

**Example**:
```bash
apm document add \
  --entity-type=work-item \
  --entity-id=5 \
  --file-path="docs/api-specification.md" \
  --type=specification \
  --title="API Specification"
```

---

### `apm document list`
List documents for entity.

**Syntax**:
```bash
apm document list [OPTIONS]
```

**Options**:
- `--entity-type` (required) - Entity type
- `--entity-id` (required) - Entity ID

**Example**:
```bash
apm document list --entity-type=task --entity-id=12
```

---

### `apm document show`
Show document details.

**Syntax**:
```bash
apm document show ID
```

**Arguments**:
- `ID` (required) - Document ID

---

### `apm document update`
Update document metadata.

**Syntax**:
```bash
apm document update ID [OPTIONS]
```

**Arguments**:
- `ID` (required) - Document ID

**Options**:
- `--title` - Update title
- `--description` - Update description
- `--type` - Update type

---

### `apm document delete`
Delete document reference.

**Syntax**:
```bash
apm document delete ID
```

**Arguments**:
- `ID` (required) - Document ID

---

## Summary Commands (`apm summary`)

Manage hierarchical summaries for projects, work items, tasks, and sessions.

### `apm summary create`
Create summary for entity.

**Syntax**:
```bash
apm summary create [OPTIONS]
```

**Options**:
- `--entity-type` (required) - Entity type (project, session, work-item, task)
- `--entity-id` (required) - Entity ID
- `--summary-type` (required) - Summary type (progress, milestone, decision, etc.)
- `--content` (required) - Summary content
- `--metadata` - JSON metadata

---

### `apm summary list`
List summaries for entity.

**Syntax**:
```bash
apm summary list [OPTIONS]
```

**Options**:
- `--entity-type` - Filter by entity type
- `--entity-id` - Filter by entity ID
- `--summary-type` - Filter by summary type

---

### `apm summary show`
Show summary details.

**Syntax**:
```bash
apm summary show ID
```

**Arguments**:
- `ID` (required) - Summary ID

---

### `apm summary search`
Search summaries by content.

**Syntax**:
```bash
apm summary search QUERY [OPTIONS]
```

**Arguments**:
- `QUERY` (required) - Search query

**Options**:
- `--entity-type` - Limit to entity type

---

### `apm summary delete`
Delete summary.

**Syntax**:
```bash
apm summary delete ID
```

**Arguments**:
- `ID` (required) - Summary ID

---

### `apm summary stats`
Show summary statistics.

**Syntax**:
```bash
apm summary stats [OPTIONS]
```

**Options**:
- `--entity-type` - Filter by entity type

---

## Testing Commands (`apm testing`)

Manage testing configuration and category-specific coverage requirements.

### `apm testing status`
Show testing configuration status and category information.

**Syntax**:
```bash
apm testing status [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path (default: current directory)

---

### `apm testing install`
Install testing configuration for the project.

**Syntax**:
```bash
apm testing install [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path
- `--force`, `-f` - Overwrite existing configuration

---

### `apm testing show`
Show detailed testing configuration.

**Syntax**:
```bash
apm testing show [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path
- `--category`, `-c` - Specific category to show details for

---

### `apm testing export`
Export testing configuration to JSON file.

**Syntax**:
```bash
apm testing export [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path
- `--output`, `-o` - Output file path (default: stdout)

---

### `apm testing validate`
Validate testing configuration and show any issues.

**Syntax**:
```bash
apm testing validate [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path

---

### `apm testing configure-rules`
Configure generic testing rules with project-specific path patterns.

**Syntax**:
```bash
apm testing configure-rules [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path
- `--force`, `-f` - Force reconfiguration

---

### `apm testing rules-status`
Show status of configured testing rules.

**Syntax**:
```bash
apm testing rules-status [OPTIONS]
```

**Options**:
- `--project-path`, `-p` - Project path

---

## Utility Commands

### `apm template`
Template management commands.

**Syntax**:
```bash
apm template SUBCOMMAND [OPTIONS]
```

**Subcommands**:
- `list` - List available templates
- `show` - Show template content
- `validate` - Validate template

---

### `apm principles`
Development principles management.

**Syntax**:
```bash
apm principles [SUBCOMMAND] [OPTIONS]
```

---

### `apm principle-check`
Check code against development principles.

**Syntax**:
```bash
apm principle-check [OPTIONS]
```

---

### `apm hooks`
Manage lifecycle hooks.

**Syntax**:
```bash
apm hooks SUBCOMMAND [OPTIONS]
```

**Subcommands**:
- `list` - List available hooks
- `enable` - Enable hook
- `disable` - Disable hook

---

### `apm commands`
Command system utilities.

**Syntax**:
```bash
apm commands SUBCOMMAND [OPTIONS]
```

---

## Command Patterns

### State Transition Pattern

Work items and tasks follow a consistent state machine:

```
DRAFT → PROPOSED → VALIDATED → ACCEPTED → IN_PROGRESS → REVIEW → COMPLETED
                                                              ↓
                                                        (rework loop)
```

**Commands**:
1. `validate` - DRAFT/PROPOSED → VALIDATED
2. `accept --agent <agent>` - VALIDATED → ACCEPTED (assign specialist)
3. `start` - ACCEPTED → IN_PROGRESS (begin work)
4. `submit-review` - IN_PROGRESS → REVIEW (work complete, request validation)
5. `approve` - REVIEW → COMPLETED (independent quality check)
6. `request-changes` - REVIEW → IN_PROGRESS (rework needed)

### Agent Separation Pattern

DIFFERENT agents handle implementation vs review:
- **Implementation agent**: Does work, submits for review
- **Quality validator agent**: Reviews work, approves or requests changes

This ensures independent quality validation and prevents self-approval bias.

---

## Global Options

All commands support:
- `-h`, `--help` - Show help message
- `-v`, `--verbose` - Enable verbose output (where applicable)

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Validation error
- `4` - Not found
- `5` - Conflict/state error

---

## Configuration Files

APM (Agent Project Manager) uses the following configuration:
- `.aipm/data/aipm.db` - SQLite database
- `.aipm/contexts/` - Plugin-generated context files
- `.aipm/cache/` - Temporary cache
- `.aipm/testing_config.json` - Testing configuration
- `.claude/agents/` - Generated agent SOPs

---

## Notes

1. **Time-boxing is STRICT**: Implementation tasks ≤4h, no exceptions
2. **Work item types have required tasks**: FEATURE needs DESIGN+IMPL+TEST+DOC
3. **State transitions are enforced**: Can't skip states in workflow
4. **Agent separation required**: Different agents for implementation vs review
5. **Quality gates checked**: Work items validate required tasks before completion
6. **Continuous backlogs**: BUGFIX work items auto-create if no work-item-id specified

---

**For detailed command help**:
```bash
apm COMMAND --help
apm COMMAND SUBCOMMAND --help
```

**Documentation Location**: `docs/project-plan/01-specifications/cli/`

**Generated From**: Actual code analysis of `agentpm/cli/commands/`
