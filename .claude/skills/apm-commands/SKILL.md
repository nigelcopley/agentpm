---
name: APM Commands Assistant
description: Comprehensive APM V2 command reference and guidance. Use when working with apm commands, work items, tasks, context, agents, rules, testing, or when user needs help with APM (Agent Project Manager) CLI operations. 
Triggers: "apm", "work-item", "task", "status", "context", "agent", "command help", "how do I"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# APM Commands Assistant

## Purpose

This skill provides expert guidance on APM (Agent Project Manager) command-line interface operations. It serves as a comprehensive reference for all `apm` commands, workflow patterns, and integration strategies. The skill references the authoritative quick reference document at `docs/reference/apm-commands-quick-reference.md` and provides context-aware assistance for developers and AI agents working with APM (Agent Project Manager).

## When to Use This Skill

Activate this skill when:

- User asks about `apm` command syntax or usage
- User needs help with work items, tasks, ideas, or context management
- User wants to understand APM (Agent Project Manager) workflows (D1→P1→I1→R1→O1→E1)
- User needs guidance on phase progression and quality gates
- User is troubleshooting command issues or errors
- User asks "how do I..." questions related to project management
- User needs examples of common workflow patterns
- User wants to configure agents, rules, or testing standards
- User needs to understand hybrid automatic vs explicit command patterns
- User is searching across entities or managing dependencies

## Core Capabilities

### 1. Command Syntax and Examples
Provide accurate, copy-pasteable command syntax with explanations of options and parameters.

### 2. Workflow Guidance
Explain APM (Agent Project Manager)'s phase-based workflow:
- **D1_DISCOVERY**: Requirements definition (business_context, AC≥3, risks, 6W confidence≥0.70)
- **P1_PLAN**: Planning and task creation (estimates, dependencies, mitigations)
- **I1_IMPLEMENTATION**: Development and testing (code, tests, docs)
- **R1_REVIEW**: Quality validation (AC verification, test pass, quality gates)
- **O1_OPERATIONS**: Deployment and monitoring (version, health checks, telemetry)
- **E1_EVOLUTION**: Continuous improvement (analysis, feedback, backlog)

### 3. Entity Lifecycle Management
Guide users through state transitions:
- **Work Items**: `draft → validated → accepted → in_progress → review → completed`
- **Tasks**: Same lifecycle, but at atomic work unit granularity
- **Ideas**: `idea → research → design → accepted → converted` (or `rejected`)

### 4. Quality Gate Requirements
Explain gate requirements for phase advancement:
- **D1 Gate**: business_context ≥50 chars, AC≥3, risks≥1, 6W≥0.70
- **P1 Gate**: Tasks created, estimates complete, dependencies mapped
- **I1 Gate**: Tests updated, code complete, docs updated
- **R1 Gate**: AC verified, tests pass, quality checks pass
- **O1 Gate**: Deployed, health checks pass, monitoring active
- **E1 Gate**: Telemetry analyzed, improvements identified

### 5. Time-Boxing Enforcement
Explain task time limits and work breakdown:
- **Implementation tasks**: ≤4 hours (STRICT)
- **Testing tasks**: ≤6 hours (Recommended)
- **Design tasks**: ≤8 hours (Recommended)
- **Documentation tasks**: ≤4 hours (Recommended)
- **Bugfix tasks**: ≤4 hours (STRICT)
- **Refactoring tasks**: ≤4 hours (STRICT)

### 6. Filtering and Querying
Demonstrate advanced filtering patterns across entities.

### 7. Integration with AI Agents
Explain agent delegation, role assignment, and context delivery patterns.

## Command Categories Quick Reference

### Core Workflow
- **init**: Initialize AIPM project with database and rules
- **status**: Project dashboard with active work, tasks, and metrics
- **work-item**: Manage features, bugs, research (17 subcommands)
- **task**: Manage atomic work units (15 subcommands)
- **context**: Hierarchical context access (project→work item→task)

### Idea Management
- **idea**: Lightweight brainstorming before formal work items (10 subcommands)

### Session & Continuity
- **session**: Track AI agent sessions with decisions and outcomes (7 subcommands)
- **summary**: Hierarchical summaries across all entities (5 subcommands)
- **memory**: Claude memory file management (3 subcommands)

### Documentation & Knowledge
- **document**: Document reference management with metadata (6 subcommands)
- **template**: JSON template access and customization (3 subcommands)
- **search**: Vector search across all entities with semantic matching

### AI Integration
- **agents**: Agent management and file generation (6 subcommands)
- **claude-code**: Claude Code integration (14 subcommands)
- **provider**: IDE provider integration (Cursor, VSCode, Zed) (5 subcommands)
- **skills**: Claude Code skills management (5 subcommands)
- **commands**: Slash command installation (3 subcommands)

### Configuration
- **rules**: Database-driven rule management (4 subcommands)
- **testing**: Testing standards configuration (6 subcommands)

### Database & Maintenance
- **migrate**: Run database migrations
- **migrate-v1-to-v2**: V1 to V2 migration (4-phase atomic)

## Workflow Patterns

### Quick Start

**Initialize a new project:**
```bash
# 1. Initialize project
apm init

# 2. Check project status
apm status

# 3. Create your first work item
apm work-item create "User authentication" --type=feature

# 4. Create a task
apm task create "Implement login endpoint" --work-item=1 --type=implementation

# 5. Check status again
apm status
```

### Daily Workflow

**Session management and progression:**
```bash
# Morning: Start session and review context
apm session start --description "Implement authentication feature"
apm context show --level=project
apm status

# During work: Progress tasks
apm task next 1                              # Auto-advance task state
apm session add-decision --decision "Use JWT tokens" --rationale "Stateless, scalable"

# Afternoon: Record progress
apm session add-next-step --step "Write integration tests"
apm work-item add-summary 1 --type=progress --content "Login flow complete"

# Evening: End session
apm session end --summary "Login endpoint complete, tests passing"
apm session add-next-step --step "Deploy to staging tomorrow"

# Next morning: Review
apm session history --limit=1
apm context show --level=work-item --id=1
```

### Feature Development (Full Lifecycle)

**D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION:**

```bash
# Phase D1: DISCOVERY
apm work-item create "Two-factor authentication" --type=feature
# Work item starts in 'draft' status, 'D1_DISCOVERY' phase

# Complete D1 requirements (business_context, AC≥3, risks, 6W)
apm work-item update 1 --description "Enable 2FA for enhanced security..."
# (Add acceptance criteria, risks, context through application)

# Validate D1 gate and advance to P1
apm work-item next 1                         # draft → validated (D1 complete)
apm work-item next 1                         # validated → accepted (enter P1_PLAN)

# Phase P1: PLAN
# Create tasks with estimates and dependencies
apm task create "Design 2FA flow" --work-item=1 --type=design --estimate=6
apm task create "Implement TOTP generation" --work-item=1 --type=implementation --estimate=4
apm task create "Create 2FA tests" --work-item=1 --type=testing --estimate=4
apm task create "Document 2FA setup" --work-item=1 --type=documentation --estimate=3

# Validate P1 gate and advance to I1
apm work-item phase-validate 1 --phase=P1_PLAN
apm work-item next 1                         # accepted → in_progress (enter I1_IMPLEMENTATION)

# Phase I1: IMPLEMENTATION
# Execute tasks
apm task next 1                              # Progress design task
apm task next 2                              # Progress implementation task
apm task next 3                              # Progress testing task
apm task next 4                              # Progress documentation task

# Validate I1 gate and advance to R1
apm work-item phase-validate 1 --phase=I1_IMPLEMENTATION
apm work-item next 1                         # in_progress → review (enter R1_REVIEW)

# Phase R1: REVIEW
# Quality validation
apm work-item phase-status 1                 # Check gate requirements
apm testing validate --work-item=1           # Validate test compliance

# Approve or request changes
apm work-item approve 1                      # review → completed (enter O1_OPERATIONS)
# OR
# apm work-item request-changes 1 --reason "Need integration tests"

# Phase O1: OPERATIONS
# (Deployment and monitoring tasks)

# Phase E1: EVOLUTION
# (Continuous improvement and feedback)
```

### Troubleshooting a Blocked Task

**Identify and resolve blockers:**
```bash
# Check task status
apm task show 5

# Add blocker
apm task add-blocker 5 --reason "Waiting for API endpoint deployment"

# List all blockers
apm task list-blockers 5

# Check dependencies
apm task list-dependencies 5

# Resolve blocker when ready
apm task resolve-blocker 5 --blocker-id 12 --resolution "API endpoint deployed to staging"

# Continue task
apm task next 5
```

### Searching Across Entities

**Find information using vector search:**
```bash
# Search all entities
apm search "authentication security"

# Search specific entity type
apm search "performance optimization" --scope=tasks --limit=20

# High-confidence matches only
apm search "database migration" --min-relevance=0.8 --include-content

# Export results for analysis
apm search "API changes" --format=json --include-content > api-changes.json

# Search sessions for decisions
apm search "architecture decision" --scope=sessions
```

### Configuring Agents

**Manage agent definitions:**
```bash
# List agents by tier
apm agents list --tier=1                     # Sub-agents
apm agents list --tier=2                     # Specialists
apm agents list --tier=3                     # Orchestrators

# View agent details
apm agents show aipm-python-cli-developer --format=json

# Generate agent files
apm agents generate --role=all --output=.claude/agents/

# Validate agent definition
apm agents validate --file=.claude/agents/specialists/custom-agent.md
```

### Running Quality Gates

**Validate compliance:**
```bash
# Check work item gate status
apm work-item phase-status 1

# Validate specific phase
apm work-item phase-validate 1 --phase=P1_PLAN

# Check testing compliance
apm testing validate --work-item=1
apm testing status
apm testing rules-status

# List relevant rules
apm rules list --enforcement=BLOCK
apm rules show TES-001
```

### Generating Context for AI

**Prepare context for agent delegation:**
```bash
# Project-level context (all active work)
apm context show --level=project

# Work item context (tasks, progress, dependencies)
apm context show --level=work-item --id=1

# Task context (implementation details)
apm context show --level=task --id=5

# Refresh context after changes
apm context refresh --work-item=1

# Rich formatted output
apm context rich --work-item=1

# Interactive context builder
apm context wizard
```

## Hybrid Command Pattern

APM (Agent Project Manager) supports two command interfaces: **automatic** (recommended) and **explicit** (advanced control).

### Automatic Progression (Recommended)

**Use `next` to auto-advance to the next logical state:**

```bash
# Task lifecycle - simple progression
apm task next 1                              # draft → validated
apm task next 1                              # validated → accepted
apm task next 1                              # accepted → in_progress
apm task next 1                              # in_progress → review
apm task next 1                              # review → completed

# Work item lifecycle - simple progression
apm work-item next 1                         # draft → validated (D1 complete)
apm work-item next 1                         # validated → accepted (enter P1)
apm work-item next 1                         # accepted → in_progress (enter I1)
apm work-item next 1                         # in_progress → review (enter R1)
apm work-item next 1                         # review → completed (enter O1)
```

**When to use automatic:**
- Happy path workflows (most common)
- Quick development iteration
- Simple state progression
- Solo development
- Reduced command complexity

### Explicit State Control (Advanced)

**Use specific commands for precise control:**

```bash
# Task lifecycle - explicit commands
apm task validate 1                          # PROPOSED → VALIDATED
apm task accept 1 --agent "implementation-orch"  # VALIDATED → ACCEPTED (requires --agent)
apm task start 1                             # ACCEPTED → IN_PROGRESS
apm task submit-review 1                     # IN_PROGRESS → REVIEW
apm task approve 1                           # REVIEW → COMPLETED
# OR
apm task request-changes 1 --reason "Missing error handling"  # REVIEW → IN_PROGRESS

# Work item lifecycle - explicit commands
apm work-item validate 1
apm work-item accept 1 --agent "planning-orch"
apm work-item start 1
apm work-item submit-review 1
apm work-item approve 1
# OR
apm work-item request-changes 1 --reason "Needs integration tests"
```

**When to use explicit:**
- Agent assignments (need `accept --agent` flag)
- Review workflows (need `request-changes --reason` or `approve`)
- Complex workflows with specific requirements
- Audit trail with detailed reasons
- Production environments with strict controls
- Team collaboration with role-based access

## Practical Examples

### Example 1: Creating a Feature from Scratch

```bash
# Initialize if needed
apm init

# Create work item
apm work-item create "Password reset functionality" --type=feature

# Check work item ID (assume it's 1)
apm work-item show 1

# Add business context (via update or through UI/API)
# Note: In real usage, these would be added through proper interfaces
# This example shows the workflow structure

# Progress through D1 (Discovery)
apm work-item next 1                         # draft → validated (D1 gate check)

# Enter P1 (Planning)
apm work-item next 1                         # validated → accepted

# Create tasks for implementation
apm task create "Design password reset flow" --work-item=1 --type=design --estimate=6
apm task create "Implement reset token generation" --work-item=1 --type=implementation --estimate=3
apm task create "Create password reset API endpoint" --work-item=1 --type=implementation --estimate=4
apm task create "Write password reset tests" --work-item=1 --type=testing --estimate=5
apm task create "Document password reset process" --work-item=1 --type=documentation --estimate=3

# Check plan
apm task list --work-item=1 --format=table

# Validate P1 gate
apm work-item phase-validate 1 --phase=P1_PLAN

# Start implementation (I1)
apm work-item next 1                         # accepted → in_progress

# Execute tasks (auto-progression)
apm task next 1                              # Design task
apm task next 2                              # Implementation task 1
apm task next 3                              # Implementation task 2
apm task next 4                              # Testing task
apm task next 5                              # Documentation task

# Check progress
apm status
apm work-item show 1

# Submit for review
apm work-item next 1                         # in_progress → review

# Quality validation
apm testing validate --work-item=1
apm work-item phase-status 1

# Approve
apm work-item approve 1                      # review → completed
```

### Example 2: Managing Dependencies

```bash
# Create dependent work items
apm work-item create "Database schema update" --type=infrastructure
apm work-item create "User profile page" --type=feature

# Work item 2 depends on work item 1
apm work-item add-dependency 1 --blocks 2

# View dependency graph
apm work-item list-dependencies 1
apm work-item list-dependencies 2

# Create dependent tasks
apm task create "Create user table migration" --work-item=1 --type=implementation
apm task create "Update user model" --work-item=2 --type=implementation

# Task 4 requires task 3 to be complete
apm task add-dependency 4 --requires 3

# Add blocker to task 4
apm task add-blocker 4 --reason "Waiting for database migration"

# Complete task 3
apm task next 3
# (Progress through states)

# Resolve blocker on task 4
apm task resolve-blocker 4 --blocker-id 1 --resolution "Migration complete"

# Continue task 4
apm task next 4
```

### Example 3: Session-Based Development

```bash
# Start development session
apm session start --description "Implement user notifications system"

# Review context
apm context show --level=project

# Create work item
apm work-item create "Real-time notifications" --type=feature

# Record decision during planning
apm session add-decision \
  --decision "Use WebSocket for real-time delivery" \
  --rationale "Lower latency than polling, native browser support"

# Progress work item to planning
apm work-item next 1
apm work-item next 1

# Create tasks
apm task create "Design notification schema" --work-item=1 --type=design --estimate=4
apm task create "Implement WebSocket server" --work-item=1 --type=implementation --estimate=4
apm task create "Create notification UI components" --work-item=1 --type=implementation --estimate=3

# Add next steps for future sessions
apm session add-next-step --step "Research notification queuing strategies"
apm session add-next-step --step "Design offline notification handling"

# End session
apm session end --summary "Designed notification system architecture, created implementation tasks"

# Next session: review history
apm session history --limit=5
apm session show 1 --format=json
```

### Example 4: Idea to Work Item Conversion

```bash
# Brainstorm idea
apm idea create "Dark mode theme support"

# Add initial thoughts
apm idea update 1 --description "Users have requested dark mode for better night-time usage"

# Vote on idea
apm idea vote 1 --vote=up

# Progress through idea lifecycle
apm idea next 1                              # idea → research

# Add research findings
apm idea update 1 --description "Research: CSS variables approach vs component-level theming. CSS variables more maintainable."

# Progress to design
apm idea next 1                              # research → design

# Add design details
apm idea update 1 --description "Design: Use CSS custom properties, system preference detection, manual toggle"

# Accept idea
apm idea next 1                              # design → accepted

# Convert to work item
apm idea convert 1 --type=feature

# New work item created (assume ID 5)
apm work-item show 5
```

### Example 5: Quality Gate Validation

```bash
# Check work item status
apm work-item show 1

# Check phase-specific gate status
apm work-item phase-status 1

# Validate D1 gate requirements
apm work-item phase-validate 1 --phase=D1_DISCOVERY
# Output shows:
# - business_context length check (≥50 chars)
# - acceptance_criteria count (≥3)
# - risks count (≥1)
# - 6W confidence score (≥0.70)

# Validate P1 gate requirements
apm work-item phase-validate 1 --phase=P1_PLAN
# Output shows:
# - Tasks created
# - Estimates complete
# - Dependencies mapped
# - Risk mitigations planned

# Check testing compliance for I1/R1
apm testing validate --work-item=1
# Output shows:
# - Test coverage (target >90%)
# - Test pass rate (target 100%)
# - Integration tests present
# - AAA pattern compliance

# Check specific rules
apm rules list --enforcement=BLOCK
apm rules show TES-001                       # AAA pattern requirement
apm rules show CI-003                        # Coverage gate requirement

# View testing rules status
apm testing rules-status
```

### Example 6: Advanced Search and Analysis

```bash
# Find all authentication-related work
apm search "authentication security" --min-relevance=0.7

# Find performance-related tasks
apm search "performance optimization" --scope=tasks --format=table

# Find architectural decisions in sessions
apm search "architecture decision" --scope=sessions --include-content

# Find all documentation about APIs
apm search "API documentation" --scope=documents --limit=50

# Export comprehensive audit
apm search "security" --scope=all --format=json --include-content > security-audit.json

# Find work items by complex criteria
apm work-item list --type=feature --status=in_progress --phase=I1_IMPLEMENTATION

# Find blocked tasks
apm task list --status=in_progress | grep -A5 "blockers"

# Find tasks by agent
apm task list --agent="aipm-testing-specialist" --format=json
```

### Example 7: Agent and Rule Management

```bash
# List all agents
apm agents list --format=table

# View specific agent details
apm agents show aipm-python-cli-developer

# Generate all agent files
apm agents generate --role=all --output=.claude/agents/

# Generate specific tier
apm agents generate --tier=2 --output=.claude/agents/specialists/

# View agent roles and types
apm agents roles
apm agents types

# List rules by category
apm rules list --enforcement=BLOCK --format=table
apm rules list --category=testing

# View specific rule
apm rules show DP-001                        # Hexagonal Architecture
apm rules show TES-003                       # Coverage >90%

# Configure rule enforcement
apm rules configure TES-003 --enforcement=BLOCK

# Create custom rule
apm rules create \
  --code=CUSTOM-001 \
  --title="API versioning required" \
  --enforcement=WARN \
  --description="All APIs must use semantic versioning"
```

## Integration with AIPM Workflow

### Phase-Based Command Usage

Each phase has specific command patterns:

**D1_DISCOVERY**:
- Create work item: `apm work-item create`
- Add context: `apm work-item update`
- Validate gate: `apm work-item phase-validate --phase=D1_DISCOVERY`
- Progress: `apm work-item next`

**P1_PLAN**:
- Create tasks: `apm task create`
- Add dependencies: `apm task add-dependency`, `apm work-item add-dependency`
- Validate gate: `apm work-item phase-validate --phase=P1_PLAN`
- Progress: `apm work-item next`

**I1_IMPLEMENTATION**:
- Execute tasks: `apm task next`
- Track progress: `apm status`, `apm task list`
- Add blockers: `apm task add-blocker`
- Record decisions: `apm session add-decision`
- Validate gate: `apm work-item phase-validate --phase=I1_IMPLEMENTATION`

**R1_REVIEW**:
- Submit review: `apm work-item submit-review`
- Validate quality: `apm testing validate`
- Check gates: `apm work-item phase-status`
- Approve/reject: `apm work-item approve` or `apm work-item request-changes`

**O1_OPERATIONS**:
- Deploy: (external deployment tools)
- Monitor: Track via summaries and context
- Health checks: Validate via custom tasks

**E1_EVOLUTION**:
- Analyze: Use search and summaries
- Create improvements: `apm idea create` or `apm work-item create --type=enhancement`

### Quality Gate Validation Commands

**Pre-Advancement Checks**:
```bash
# Before D1 → P1
apm work-item phase-validate 1 --phase=D1_DISCOVERY

# Before P1 → I1
apm work-item phase-validate 1 --phase=P1_PLAN
apm task list --work-item=1                  # Verify tasks created

# Before I1 → R1
apm work-item phase-validate 1 --phase=I1_IMPLEMENTATION
apm testing validate --work-item=1           # Verify test compliance

# Before R1 → O1
apm work-item phase-status 1                 # All gates must be green
apm testing status                           # Overall testing status
```

### Time-Boxing Enforcement Commands

**Check Time Estimates**:
```bash
# View task estimates
apm task show 5                              # Shows estimate field

# List tasks exceeding limits (via filtering and analysis)
apm task list --work-item=1 --format=json | jq '.[] | select(.estimate > 4 and .type == "implementation")'

# Create time-boxed tasks
apm task create "Refactor auth module" --work-item=1 --type=refactoring --estimate=3  # Must be ≤4 hours

# BLOCK-level rules will prevent creation if time limit exceeded for STRICT types
```

### Agent Delegation Patterns

**Typical Agent Assignment Workflow**:
```bash
# Accept work item with agent assignment
apm work-item accept 1 --agent "planning-orch"

# Accept task with agent assignment
apm task accept 5 --agent "aipm-testing-specialist"

# List tasks by agent
apm task list --agent="aipm-python-cli-developer"

# Context delivery for agent handoff
apm context show --level=work-item --id=1    # Full context for agent
apm context rich --work-item=1               # Rich formatted context
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Command Not Found
**Symptom**: `apm: command not found`

**Solutions**:
```bash
# Check if apm is in PATH
which apm

# If not found, install/reinstall
pip install -e /Users/nigelcopley/.project_manager/aipm-v2

# Verify installation
apm --version

# Check Python environment
which python
python --version
```

#### 2. Permission Issues
**Symptom**: `Permission denied` when accessing `.aipm` directory

**Solutions**:
```bash
# Check .aipm directory permissions
ls -la .aipm/

# Fix permissions if needed
chmod -R u+rwX .aipm/

# Reinitialize if corrupted
apm init --force
```

#### 3. Database Errors
**Symptom**: `sqlite3.OperationalError` or database corruption

**Solutions**:
```bash
# Check database file
ls -la .aipm/aipm.db

# Run pending migrations
apm migrate

# List migration status
apm migrate --show-applied
apm migrate --list

# If migrations fail, check migration files
ls -la migrations/files/

# Last resort: backup and reinitialize
cp .aipm/aipm.db .aipm/aipm.db.backup
apm init --force
```

#### 4. Context Not Loading
**Symptom**: `apm context show` returns empty or stale data

**Solutions**:
```bash
# Refresh context cache
apm context refresh --work-item=1

# Check context system status
apm context status

# Rebuild context from scratch
apm context refresh --work-item=1 --force

# Verify work item exists
apm work-item show 1
```

#### 5. Gate Validation Failures
**Symptom**: `apm work-item next` fails with "Gate requirements not met"

**Solutions**:
```bash
# Check gate status
apm work-item phase-status 1

# Identify missing requirements
apm work-item phase-validate 1 --phase=D1_DISCOVERY

# Fix specific issues:
# - Add business context
apm work-item update 1 --description "Detailed business context explaining the WHY..."

# - Add acceptance criteria (via UI/API)
# - Add risks (via UI/API)
# - Improve 6W context (via research and planning)

# Retry validation
apm work-item phase-validate 1 --phase=D1_DISCOVERY
```

#### 6. Time-Boxing Violations
**Symptom**: Task creation fails with "Exceeds time limit"

**Solutions**:
```bash
# Check task type limits
apm task types

# Break down task into smaller units
# Instead of:
# apm task create "Implement entire auth system" --type=implementation --estimate=12
# Use:
apm task create "Implement login endpoint" --type=implementation --estimate=4
apm task create "Implement logout endpoint" --type=implementation --estimate=2
apm task create "Implement token refresh" --type=implementation --estimate=3

# Check rules for specific limits
apm rules show WF-003                        # Time-boxing rule
```

#### 7. Search Returning No Results
**Symptom**: `apm search` finds nothing despite known entities

**Solutions**:
```bash
# Try broader search
apm search "auth" --min-relevance=0.5        # Lower threshold

# Search specific scope
apm search "authentication" --scope=work_items

# Include content for debugging
apm search "login" --include-content --format=json

# Check if entities exist
apm work-item list --format=table
apm task list --format=table

# Verify search index (if applicable)
apm context status
```

#### 8. Agent Files Not Generating
**Symptom**: `apm agents generate` fails or produces no files

**Solutions**:
```bash
# Check output directory exists
mkdir -p .claude/agents/specialists
mkdir -p .claude/agents/orchestrators
mkdir -p .claude/agents/sub-agents

# Verify agent database entries
apm agents list --format=json

# Try specific agent generation
apm agents generate --role=context-delivery --output=.claude/agents/sub-agents/

# Check for template issues
ls -la agentpm/core/agents/templates/
```

#### 9. Session Commands Failing
**Symptom**: Session start/end/update commands error

**Solutions**:
```bash
# Check for active session
apm session status

# End any orphaned sessions
apm session end --summary "Session terminated"

# Start fresh session
apm session start --description "New development session"

# View session history
apm session history --limit=10
```

#### 10. Dependency Cycles
**Symptom**: Cannot create dependency due to cycle detection

**Solutions**:
```bash
# View existing dependencies
apm work-item list-dependencies 1
apm task list-dependencies 5

# Remove incorrect dependency
apm work-item remove-dependency 1 --dependency-id 10
apm task remove-dependency 5 --dependency-id 8

# Recreate dependency in correct order
apm work-item add-dependency 1 --blocks 2   # 1 blocks 2 (1 must complete first)
```

## Reference Documentation

### Quick Reference Document
The authoritative command reference is maintained at:
```
docs/reference/apm-commands-quick-reference.md
```

Always consult this document for:
- Complete command syntax
- All subcommand options
- Parameter details
- Output format specifications
- Entity lifecycle state machines
- Quality gate requirements
- Time-boxing limits

### Using `--help`
Every command supports `--help` for detailed information:
```bash
apm --help                                   # Top-level help
apm work-item --help                         # Work item commands
apm work-item create --help                  # Specific subcommand help
apm task --help                              # Task commands
apm context --help                           # Context commands
```

### Dashboard
Quick project overview:
```bash
apm status                                   # Human-readable dashboard
apm status --format=json                     # Machine-readable status
apm status --detailed                        # Extended metrics
```

### Database-First Architecture
Remember: APM (Agent Project Manager) is **database-driven**. The `_RULES/` directory is documentation only. Rules are loaded from the database at runtime:
```bash
apm rules list                               # Query live database rules
```

### Related Documentation
- **CLAUDE.md**: Master orchestrator instructions at `/Users/nigelcopley/.project_manager/aipm-v2/CLAUDE.md`
- **User Guide**: `docs/user-guide/` (if exists)
- **Developer Guide**: `docs/developer-guide/` (if exists)
- **Agent Reference**: `.claude/agents/` (agent SOPs and definitions)
- **Database Schema**: `docs/components/database/schema.md` (if exists)

## Usage Instructions for This Skill

When activated, this skill should:

1. **Read the quick reference**: Always start by reading relevant sections from `docs/reference/apm-commands-quick-reference.md`

2. **Provide context-aware guidance**: Understand what the user is trying to accomplish and recommend appropriate commands

3. **Offer examples**: Provide copy-pasteable command examples relevant to the user's situation

4. **Explain workflows**: Show how commands fit into larger APM (Agent Project Manager) workflows

5. **Reference documentation**: Point users to authoritative sources for deeper understanding

6. **Validate assumptions**: Check the project state using `apm status` or related commands before providing guidance

7. **Troubleshoot systematically**: Follow the troubleshooting checklist when users encounter issues

8. **Respect database-first architecture**: Always emphasize that rules and state come from the database, not files

9. **Promote best practices**: Encourage proper workflow progression, quality gate validation, and time-boxing

10. **Stay current**: Use `apm --help` and the quick reference as sources of truth for command syntax

## Example Activation Scenarios

**User asks**: "How do I create a new feature?"
**Response**: Read quick reference work-item section → Provide feature creation workflow → Show D1→P1→I1→R1→O1→E1 progression → Include quality gate requirements

**User asks**: "My task is blocked, what do I do?"
**Response**: Show blocker management commands → Demonstrate `apm task add-blocker` and `apm task resolve-blocker` → Explain dependency patterns → Check task status with examples

**User asks**: "How do I check if I can move to the next phase?"
**Response**: Explain gate validation → Show `apm work-item phase-status` and `apm work-item phase-validate` → List gate requirements for current phase → Provide remediation steps if gates not met

**User asks**: "What commands are available?"
**Response**: Read and summarize command overview from quick reference → Organize by category → Highlight most commonly used commands → Suggest `apm --help` for details

**User encounters error**: "Database migration failed"
**Response**: Follow database troubleshooting steps → Check migration status with `apm migrate --show-applied` → Identify failed migration → Provide remediation strategy → Suggest backup and recovery if needed

---

**Skill Version**: 1.0.0
**Created**: 2025-10-23
**Quick Reference Version**: 5.0.0
**AIPM Version**: V2 (Database-driven, 50-agent architecture)
