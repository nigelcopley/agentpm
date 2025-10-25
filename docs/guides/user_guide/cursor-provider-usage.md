---
title: Cursor Provider User Guide
category: user_guide
version: 1.0.0
status: active
author: AIPM Documentation
date: 2025-10-20
related:
  - docs/guides/setup_guide/cursor-provider-setup.md
  - docs/reference/api/cursor-provider-reference.md
  - docs/operations/troubleshooting/cursor-provider-issues.md
tags:
  - cursor
  - provider
  - usage
  - workflow
---

# Cursor Provider User Guide

## Overview

The Cursor Provider creates a seamless integration between APM (Agent Project Manager)'s database-driven workflow and Cursor IDE's AI-powered features. This guide explains how to use the provider effectively in your daily development workflow.

**What This Guide Covers**:
- How the provider works (architecture overview)
- Using the 6 auto-attach rules
- Working with custom modes
- Leveraging @-symbols for context
- Memory sync workflow
- Guardrails configuration
- Hook behavior and customization
- Best practices and workflows

---

## How the Provider Works

### Architecture Overview

The Cursor Provider operates on four integration layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Cursor IDE                           │
│  (AI Chat, Code Editing, Terminal, Search)              │
└─────────────────┬───────────────────────┬───────────────┘
                  │                       │
         ┌────────▼────────┐     ┌───────▼────────┐
         │  Rules System   │     │  Custom Modes  │
         │  (6 .mdc files) │     │  (6 modes)     │
         └────────┬────────┘     └───────┬────────┘
                  │                       │
         ┌────────▼───────────────────────▼────────┐
         │         @-Symbols + Memories            │
         │    (@aipm-context, @aipm-rules, etc.)   │
         └────────┬───────────────────────┬────────┘
                  │                       │
         ┌────────▼────────┐     ┌───────▼────────┐
         │     Hooks       │     │   Guardrails   │
         │  (Context Inject)│     │  (Auto-Run)    │
         └────────┬────────┘     └───────┬────────┘
                  │                       │
         ┌────────▼───────────────────────▼────────┐
         │           APM (Agent Project Manager) Database              │
         │  (Work Items, Tasks, Rules, Contexts)   │
         └─────────────────────────────────────────┘
```

**Key Principles**:
- **AIPM controls workflow**: Phase gates, task validation, quality checks
- **Cursor provides execution**: AI-powered coding, intelligent search, context assembly
- **Provider bridges both**: Bi-directional sync, context injection, guardrails

---

## Rule System

### What Are Cursor Rules?

Cursor rules are instruction files (`.mdc` format) that auto-attach to every chat session, providing the AI with project-specific context and patterns.

### 6 AIPM Rules

The provider installs 6 consolidated rules in `.cursor/rules/`:

| Rule File | Purpose | Key Instructions |
|-----------|---------|------------------|
| **aipm-master.mdc** | Core AIPM orchestration patterns | Database-first, workflow phases, agent delegation |
| **python-implementation.mdc** | Python coding standards | Three-layer architecture, Pydantic models, type hints |
| **testing-standards.mdc** | Test requirements | AAA pattern, 90% coverage, fixtures, project-relative imports |
| **cli-development.mdc** | Click CLI patterns | Command structure, Rich output, three-layer flow |
| **database-patterns.mdc** | Database architecture | Models → Adapters → Methods, migration patterns |
| **documentation-quality.mdc** | Documentation standards | Google-style docstrings, examples, API docs |

### Rule Behavior

**Auto-Attach**: All 6 rules automatically attach to every Cursor chat session.

**Precedence**: Rules are loaded in order (master first, then specialists).

**Context Window**: Rules consume ~5KB of context per session.

### Using Rules Effectively

**Implicit Usage** (Recommended):

Rules guide the AI automatically. Just ask naturally:

```
You: "Implement a new task status transition method"

AI: [Follows three-layer architecture from rules]
     [Creates Pydantic model]
     [Implements adapter]
     [Creates business logic method]
     [Writes tests with AAA pattern]
```

**Explicit Reference**:

Reference rules directly when needed:

```
You: "Following the database-patterns rule, create a migration for adding a 'metadata' column to tasks table"

AI: [Creates migration following exact pattern from rule]
```

**Rule Querying**:

Ask about rule content:

```
You: "What does the testing-standards rule say about coverage?"

AI: "The testing-standards rule requires ≥90% coverage for all implementations..."
```

---

## Custom Modes

### What Are Custom Modes?

Custom modes are pre-configured tool + instruction combinations in Cursor. APM provides 6 modes matching workflow phases.

### 6 AIPM Modes

#### 1. AIPM Discovery (D1 Phase)

**Purpose**: Define requirements, analyze context, identify risks

**Enabled Tools**:
- Codebase Search
- File Read
- Web Search
- Documentation

**Auto-Includes**:
- `@aipm-context`
- `@Recent Changes`

**Use When**:
- Starting new work item
- Analyzing requirements
- Researching integration points
- Identifying risks

**Example Workflow**:

```
[Switch to AIPM Discovery mode]

You: "Analyze requirements for adding task priority feature"

AI: [Searches codebase for related patterns]
    [Reviews recent changes]
    [Suggests acceptance criteria]
    [Identifies integration points]
    [Lists potential risks]

You: "@aipm-context"

AI: [Shows current work item WI-125 context]

You: "Draft acceptance criteria"

AI: [Creates 3+ acceptance criteria]
    [Includes validation rules]
    [References existing patterns]
```

#### 2. AIPM Planning (P1 Phase)

**Purpose**: Break down work, estimate effort, map dependencies

**Enabled Tools**:
- Codebase Search
- File Read
- Terminal

**Auto-Includes**:
- `@aipm-context`

**Use When**:
- Creating implementation plan
- Breaking work into tasks
- Estimating effort
- Mapping dependencies

**Example Workflow**:

```
[Switch to AIPM Planning mode]

You: "Create implementation plan for WI-125 (task priority)"

AI: [Reviews acceptance criteria]
    [Analyzes affected components]
    [Suggests 4 tasks:]
      1. Add priority field to task model (1.5h)
      2. Create migration for priority column (0.5h)
      3. Update CLI commands to support priority (1h)
      4. Add priority tests (1h)
    [Maps dependencies]
    [Identifies risks]

You: "Estimate effort for task 3"

AI: "CLI command updates: 1 hour
     - Add --priority flag to task create
     - Update task list to show priority
     - Modify task show output
     Following cli-development patterns"
```

#### 3. AIPM Implementation (I1 Phase)

**Purpose**: Build features, write tests, update docs

**Enabled Tools**:
- Codebase Search
- File Read
- Code Edit
- Terminal

**Auto-Includes**:
- `@aipm-context`
- `@Lint Errors`

**Guardrails**:
- Auto-apply edits: **Yes**
- Auto-run commands: **Yes** (with allowlist)

**Use When**:
- Implementing features
- Writing tests
- Fixing bugs
- Refactoring code

**Example Workflow**:

```
[Switch to AIPM Implementation mode]

You: "Implement priority field addition (Task 652)"

AI: [Reads task acceptance criteria]
    [Creates Pydantic model update]
    [Implements adapter changes]
    [Adds business logic method]
    [Writes migration]
    [Auto-applies edits]

You: "Write tests for priority field"

AI: [Creates test file with AAA pattern]
    [Adds fixtures]
    [Tests validation]
    [Tests database storage]
    [Auto-runs pytest]

You: "Run coverage check"

AI: [Executes: pytest --cov=agentpm --cov-report=term]
    [Shows 92% coverage]
```

**Auto-Run Allowlist**:
- `pytest`
- `mypy`
- `pylint`
- `black`
- `ruff`
- `apm status`
- `apm work-item show`
- `apm task show`

#### 4. AIPM Review (R1 Phase)

**Purpose**: Validate quality, verify acceptance criteria, run tests

**Enabled Tools**:
- Codebase Search
- File Read
- Terminal

**Auto-Includes**:
- `@aipm-context`
- `@Git`
- `@Lint Errors`

**Guardrails**:
- Auto-apply edits: **No**
- Auto-run commands: **Yes** (tests only)

**Use When**:
- Reviewing implementations
- Validating acceptance criteria
- Running quality checks
- Approving/rejecting work

**Example Workflow**:

```
[Switch to AIPM Review mode]

You: "Review Task 652 implementation"

AI: [Loads task context]
    [Checks all AC verified]
    [Runs full test suite]
    [Executes coverage check (92%)]
    [Runs mypy (no errors)]
    [Runs pylint (score 9.8/10)]
    [Reviews git changes]
    [Summary: All gates passed]

You: "Any issues found?"

AI: "No issues. All acceptance criteria verified:
     ✓ Priority field added to model
     ✓ Migration created and tested
     ✓ CLI commands support --priority
     ✓ Tests written (92% coverage)
     ✓ Documentation updated

     Recommendation: Approve task"
```

#### 5. AIPM Operations (O1 Phase)

**Purpose**: Deploy, version, monitor

**Enabled Tools**:
- Codebase Search
- File Read
- Code Edit
- Terminal

**Auto-Includes**:
- `@aipm-context`
- `@Git`

**Guardrails**:
- Auto-apply edits: **No** (manual confirm for versions)
- Auto-run commands: **No** (deployment is manual)

**Use When**:
- Bumping versions
- Creating releases
- Deploying to production
- Setting up monitoring

**Example Workflow**:

```
[Switch to AIPM Operations mode]

You: "Prepare release for WI-125"

AI: [Suggests version bump: 2.1.0 → 2.2.0]
    [Updates setup.py]
    [Updates __version__]
    [Updates CHANGELOG.md]
    [Waits for confirmation before applying]

You: "Apply version changes"

AI: [Applies edits]
    [Suggests git commands:]
      git add .
      git commit -m "chore: bump version to 2.2.0"
      git tag -a v2.2.0 -m "Release v2.2.0"
    [Waits for manual execution]
```

#### 6. AIPM Evolution (E1 Phase)

**Purpose**: Analyze telemetry, identify improvements, capture learnings

**Enabled Tools**:
- Codebase Search
- File Read
- Terminal
- Web Search

**Auto-Includes**:
- `@aipm-context`
- `@Recent Changes`

**Use When**:
- Analyzing production metrics
- Reviewing completed work
- Identifying improvements
- Capturing learnings

**Example Workflow**:

```
[Switch to AIPM Evolution mode]

You: "Analyze results of WI-125 (priority feature)"

AI: [Reviews completed work item]
    [Analyzes code changes]
    [Checks test coverage trends]
    [Suggests improvements:]
      1. Add priority sorting to task list
      2. Create priority-based notifications
      3. Add priority analytics
    [Captures learnings:]
      - Migration pattern worked well
      - Test coverage remained high
      - CLI UX needs improvement

You: "Sync learnings to Cursor Memories"

AI: [Executes: apm provider sync-memories cursor]
    [Creates memory entries]
```

---

## @-Symbols for Context

### Built-in Cursor Symbols

| Symbol | Purpose | Example |
|--------|---------|---------|
| `@Code` | Reference specific functions/classes | `@Code TaskModel` |
| `@Files` | Include specific files | `@Files agentpm/core/workflow/` |
| `@Git` | Reference PRs, commits | `@Git WI-125` |
| `@Docs` | Access documentation | `@Docs workflow phases` |
| `@Web` | Search current information | `@Web pydantic validation` |
| `@Link <url>` | Embed web content | `@Link https://docs.python.org/3/library/enum.html` |
| `@Recent Changes` | Recently modified files | `@Recent Changes` |
| `@Past Chats` | Previous conversations | `@Past Chats task priority` |
| `@Lint Errors` | Current linting issues | `@Lint Errors` |

### APM Custom Symbols

The provider adds 4 custom @-symbols:

#### @aipm-context

**Purpose**: Current work item context (6W analysis, AC, tasks, risks)

**Usage**:
```
@aipm-context
```

**Output**:
```markdown
## Work Item Context: WI-125

**Name**: Add task priority field
**Type**: feature
**Phase**: I1_IMPLEMENTATION
**Status**: in_progress

### Business Context
Enable users to prioritize tasks within work items, improving workflow management and focus allocation.

### Acceptance Criteria
1. Priority field added to task model (values: low, medium, high, critical)
2. CLI commands support --priority flag
3. Task list displays priority
4. Migration created for database schema
5. Tests achieve ≥90% coverage

### Active Tasks
- Task 652: Add priority field to model (in_progress, 2.0h)
- Task 653: Create priority migration (draft, 0.5h)
- Task 654: Update CLI commands (draft, 1.0h)
- Task 655: Write priority tests (draft, 1.0h)

### Risks
- Risk: Breaking existing task creation flows
  Mitigation: Default priority to 'medium', maintain backward compatibility

**6W Confidence**: 0.85
```

#### @aipm-rules

**Purpose**: Active AIPM rules from database

**Usage**:
```
@aipm-rules
```

**Output**:
```markdown
## Active AIPM Rules

### Development Principles
- **DP-001** (BLOCK): Hexagonal Architecture - Core must be framework-agnostic
- **DP-002** (BLOCK): Domain-Driven Design - Rich domain models, not anemic
- **DP-003** (BLOCK): Three-Layer Architecture - Models → Adapters → Methods

### Testing Standards
- **TES-001** (BLOCK): Project-Relative Imports in Tests
- **TES-004** (BLOCK): Test Coverage ≥90%
- **TES-006** (GUIDE): AAA Pattern in Tests

### Code Quality
- **CQ-001** (GUIDE): Descriptive Naming Conventions
- **CQ-005** (GUIDE): Functions are Verbs, Classes are Nouns
...
```

#### @aipm-phase

**Purpose**: Current workflow phase requirements

**Usage**:
```
@aipm-phase
```

**Output**:
```markdown
### I1 Implementation Phase Requirements

**Gate Requirements**:
- All implementation tasks complete
- All testing tasks complete
- Documentation updated
- Test coverage adequate (≥90%)

**Commands**:
- `apm task start <id>`
- `pytest tests/ -v --cov=agentpm`
- `apm task submit-review <id>`

**Next Phase**: R1_REVIEW (after all tasks complete)
```

#### @aipm-task

**Purpose**: Specific task details (AC, estimates, dependencies)

**Usage**:
```
@aipm-task 652
```

**Output**:
```markdown
## Task #652: Add priority field to model

**Type**: implementation
**Status**: in_progress
**Effort**: 2.0h / 4.0h max
**Assigned**: aipm-python-cli-developer

### Acceptance Criteria
1. Priority enum created (low, medium, high, critical)
2. TaskModel updated with priority field
3. TaskAdapter handles priority conversion
4. Default priority is 'medium'
5. Tests verify priority validation

### Dependencies
- None

### Estimated Effort
2.0 hours
- Model changes: 0.5h
- Adapter updates: 0.5h
- Validation logic: 0.5h
- Tests: 0.5h
```

### Symbol Best Practices

**Start Sessions with Context**:
```
@aipm-context
@aipm-phase
```

**Reference Code Precisely**:
```
@Code TaskModel
@Files agentpm/core/tasks/models.py
```

**Combine Symbols**:
```
@aipm-task 652
@Code TaskModel
@Lint Errors
```

**Use for Research**:
```
@Web pydantic enum validation
@Link https://docs.pydantic.dev/latest/concepts/models/#model-fields
```

---

## Memory Sync Workflow

### What Are Cursor Memories?

Cursor Memories are persistent knowledge files (`.cursor/memories/*.md`) that provide long-term project context across sessions.

### APM ↔ Cursor Sync

The provider enables bi-directional sync:

**AIPM → Cursor** (Export learnings to Cursor):
- Completed work items → Project context memories
- Captured decisions → Decision memories
- Evolution learnings → Learning memories
- Architectural patterns → Pattern memories

**Cursor → AIPM** (Import manual memories to AIPM):
- Manual memory files → AIPM evidence entries
- User-created learnings → Database storage

### Automatic Sync Triggers

Memory sync happens automatically on:

1. **Work Item Completion** (O1 → E1 transition):
   ```bash
   apm work-item complete 125
   # Automatically creates memory: project_context-125.md
   ```

2. **Phase Transitions** (if configured):
   ```bash
   apm work-item next 125  # D1 → P1
   # Syncs updated context
   ```

3. **Provider Installation**:
   ```bash
   apm provider install cursor
   # Initial sync of existing learnings
   ```

### Manual Sync Commands

**Bi-Directional Sync** (default):
```bash
apm provider sync-memories cursor
```

**AIPM → Cursor Only**:
```bash
apm provider sync-memories cursor --direction=to-cursor
```

**Cursor → AIPM Only**:
```bash
apm provider sync-memories cursor --direction=from-cursor
```

**Generate Memory from Work Item**:
```bash
apm provider generate-memory cursor --work-item-id=125
```

**List Memories**:
```bash
# All memories
apm provider list-memories cursor

# By type
apm provider list-memories cursor --type=decision
apm provider list-memories cursor --type=learning
apm provider list-memories cursor --type=pattern
```

### Memory File Structure

**Example**: `.cursor/memories/project_context-125.md`

```markdown
# Add task priority field

**Type**: project_context
**Source**: aipm_context
**Confidence**: 0.85
**Created**: 2025-10-20
**Work Item**: WI-125
**Tags**: feature, tasks, priority

---

## Context

Feature to add priority field to tasks, enabling users to organize work by importance.

## Implementation Approach

Three-layer architecture:
1. **Model**: Added Priority enum and priority field to TaskModel
2. **Adapter**: Updated TaskAdapter for DB conversion
3. **Methods**: No business logic changes needed (priority is metadata)

## Key Decisions

**Default Priority**: Set to 'medium' for backward compatibility
**Enum Values**: low, medium, high, critical (4 levels, matches industry standard)
**Database Type**: TEXT (stores enum name, not value)

## Learnings

- Migration pattern worked smoothly (zero downtime)
- Test coverage remained high (92%)
- CLI UX could be improved (add color coding for priority levels)

## Patterns Applied

- Three-layer architecture (DP-003)
- Pydantic enum validation (CQ-013)
- AAA test pattern (TES-006)

---

*Generated by APM (Agent Project Manager) Cursor Provider*
```

### Using Memories Effectively

**Reference in Chat**:
```
You: "What did we learn from the priority feature implementation?"

AI: [Reads .cursor/memories/project_context-125.md]
    "From the priority feature (WI-125), we learned:
     - Migration pattern worked well
     - Default to 'medium' for backward compatibility
     - CLI UX needs color coding for priorities"
```

**Search Memories**:
```
You: "Search memories for migration patterns"

AI: [Searches all memory files]
    [Returns relevant patterns from past work]
```

**Memory-Guided Decisions**:
```
You: "Should we use the same enum pattern for task status?"

AI: [References pattern memory from WI-125]
    "Yes, following the pattern from WI-125 (priority field):
     - Use Pydantic enum
     - Store as TEXT in database
     - Provide default value
     - Validate in model, not adapter"
```

---

## Guardrails Configuration

### What Are Guardrails?

Guardrails control what Cursor can auto-execute without user confirmation. They provide safety while enabling productivity.

### Default Guardrails

**Auto-Run Enabled** (Safe Commands):
- `pytest` (tests are read-only)
- `mypy` (static analysis)
- `pylint` (linting)
- `bandit` (security scan)
- `ruff` (fast linter)
- `black` (formatter in check mode)
- `apm status` (read-only)
- `apm work-item show` (read-only)
- `apm task show` (read-only)
- `apm context show` (read-only)

**Manual Confirmation Required**:
- `git push` (destructive)
- `git push --force` (very destructive)
- `git tag` (version control)
- `git reset --hard` (destructive)
- `rm -rf` (destructive)
- `apm work-item approve` (workflow state change)
- `apm task approve` (workflow state change)
- Database operations (migrations, data changes)
- Deployment commands (production changes)

### Customizing Guardrails

Edit `.agentpm/providers/cursor.yml`:

```yaml
guardrails:
  # Enable/disable auto-run
  auto_run_safe_commands: true

  # Enable/disable auto-apply edits in Implementation mode
  auto_apply_edits_in_implementation: true

  # Add custom safe commands
  safe_commands:
    - pytest
    - mypy
    - your-custom-test-command

  # Add custom confirmation-required commands
  require_confirmation:
    - your-deployment-script
    - dangerous-operation

  # Protect specific files from auto-edit
  protected_files:
    - "*.db"
    - ".env"
    - "credentials.json"
    - "setup.py"  # Add if you want manual version control
```

**Apply Changes**:
```bash
apm provider configure cursor --reload
```

### Guardrail Examples

**Example 1: Auto-Run Test**

```
[AIPM Implementation mode]

You: "Run tests for priority feature"

AI: [Auto-executes: pytest tests/test_priority.py -v]
    [Shows results immediately]
    ✓ 12 tests passed
```

**Example 2: Manual Confirmation Required**

```
[AIPM Implementation mode]

You: "Push changes to remote"

AI: "I would run: git push origin feature/task-priority

    ⚠️ This requires manual confirmation (destructive operation)

    Run this command? [y/N]:"
```

**Example 3: Protected File**

```
[AIPM Implementation mode]

You: "Update database credentials in .env"

AI: "⚠️ Cannot auto-edit .env (protected file per guardrails)

    I can suggest changes for manual application:

    Add to .env:
    DATABASE_URL=sqlite:///new_path.db"
```

---

## Hook Behavior

### What Are Hooks?

Hooks are shell scripts that execute at specific Cursor events, enabling context injection and automation.

### 3 AIPM Hooks

#### beforeAgentRequest.sh

**Trigger**: Before every AI request in Cursor chat

**Purpose**: Inject AIPM context into request

**Actions**:
1. Detect current work item (from git branch or active status)
2. Load work item context from database
3. Load active rules
4. Load phase requirements
5. Inject as invisible context to AI request

**Example**:

```
[User types in Cursor chat]
You: "Implement priority field"

[Hook executes before sending to AI]
beforeAgentRequest.sh:
  - Detects: Currently on branch feature/WI-125-priority
  - Loads: Work item 125 context
  - Loads: I1 phase requirements
  - Injects: Context + phase requirements

[AI receives]
Hidden Context:
  Work Item: WI-125 (Add task priority field)
  Phase: I1_IMPLEMENTATION
  Active Task: 652 (Add priority field to model)
  Requirements: Three-layer architecture, ≥90% coverage

User Request:
  "Implement priority field"

[AI responds with full context awareness]
```

**Configuration**:

```yaml
hooks:
  beforeAgentRequest: true
  beforeAgentRequest_settings:
    inject_work_item_context: true
    inject_active_rules: true
    inject_phase_requirements: true
    inject_task_context: true  # If task ID detected
```

#### afterAgentRequest.sh

**Trigger**: After AI response in Cursor chat

**Purpose**: Update AIPM database based on interaction

**Actions**:
1. Parse AI response for completed actions
2. Update task status if work was completed
3. Log AI interaction for audit
4. Trigger memory sync if work item completed

**Example**:

```
[AI completes implementation]
AI: "I've implemented the priority field:
     - Added Priority enum
     - Updated TaskModel
     - Updated TaskAdapter
     - Created migration
     All changes applied."

[Hook executes after response]
afterAgentRequest.sh:
  - Detects: Code changes in agentpm/core/tasks/
  - Parses: Completed actions
  - Updates: Task 652 status → in_progress (if was draft)
  - Logs: AI interaction to audit log
  - Checks: If all task AC met (not yet)

[Database updated automatically]
```

**Configuration**:

```yaml
hooks:
  afterAgentRequest: true
  afterAgentRequest_settings:
    update_task_status: true
    log_ai_interactions: true
    auto_sync_memories: false  # Manual sync preferred
```

#### onFileSave.sh

**Trigger**: When any file is saved in Cursor

**Purpose**: Validate changes against AIPM rules

**Actions**:
1. Run linters (mypy, pylint) on saved file
2. Check test coverage if test file
3. Validate against active AIPM rules
4. Show warnings if violations found

**Example**:

```
[User saves agentpm/core/tasks/models.py]

[Hook executes on save]
onFileSave.sh:
  - Runs: mypy agentpm/core/tasks/models.py
  - Runs: pylint agentpm/core/tasks/models.py
  - Checks: DP-003 (three-layer architecture) compliance
  - Result: All checks passed

[No warnings shown - silent success]
```

**Warning**: Can be slow on large projects. Disable if needed:

```yaml
hooks:
  onFileSave: false  # Disable for performance
```

### Hook Debugging

**Enable Debug Logging**:

```yaml
hooks:
  debug_logging: true
  log_file: .agentpm/logs/hooks.log
```

**View Hook Logs**:

```bash
tail -f .agentpm/logs/hooks.log
```

**Test Hooks Manually**:

```bash
# Test beforeAgentRequest hook
.cursor/hooks/beforeAgentRequest.sh

# Test afterAgentRequest hook
.cursor/hooks/afterAgentRequest.sh

# Test onFileSave hook
.cursor/hooks/onFileSave.sh path/to/file.py
```

---

## Best Practices

### 1. Start Every Session with Context

```
@aipm-context
@aipm-phase
```

This ensures the AI knows:
- What you're working on
- Which phase you're in
- What the requirements are

### 2. Use Phase-Appropriate Modes

Match Cursor mode to AIPM phase:

| AIPM Phase | Cursor Mode | Purpose |
|------------|-------------|---------|
| D1_DISCOVERY | AIPM Discovery | Research, analyze, define |
| P1_PLAN | AIPM Planning | Break down, estimate |
| I1_IMPLEMENTATION | AIPM Implementation | Build, test, document |
| R1_REVIEW | AIPM Review | Validate, verify |
| O1_OPERATIONS | AIPM Operations | Deploy, monitor |
| E1_EVOLUTION | AIPM Evolution | Learn, improve |

### 3. Sync Memories After Major Work

After completing significant work:

```bash
apm provider sync-memories cursor
```

This captures learnings for future reference.

### 4. Combine @-Symbols for Rich Context

```
@aipm-context
@aipm-task 652
@Code TaskModel
@Files agentpm/core/tasks/
@Lint Errors
```

More context = better AI responses.

### 5. Trust Guardrails in Implementation Mode

In AIPM Implementation mode:
- Let AI auto-run tests (safe)
- Let AI auto-apply edits (trackable via git)
- Review changes in git before committing

### 6. Use Rules for Consistency

Reference rules explicitly when consistency matters:

```
"Following the testing-standards rule, write tests for this feature"
```

### 7. Leverage Memories for Patterns

Ask AI to reference past work:

```
"How did we implement enum fields in the past?"
```

AI will search memories and provide consistent patterns.

---

## Common Workflows

### Workflow 1: Implement New Feature

```
# 1. Start work item (D1 phase)
apm work-item create "Add feature X" --type=feature
apm work-item next 123  # → P1

# 2. Switch to Discovery mode in Cursor
[AIPM Discovery mode]
@aipm-context
"Analyze requirements for feature X"

# 3. Create tasks (P1 phase)
[AIPM Planning mode]
@aipm-context
"Create implementation plan with tasks"

apm task create "Implement X" --work-item-id=123
# ... create all tasks ...
apm work-item next 123  # → I1

# 4. Implement (I1 phase)
[AIPM Implementation mode]
@aipm-task 652
"Implement feature X following three-layer architecture"

# AI implements, auto-runs tests, shows results

# 5. Review (R1 phase)
apm work-item next 123  # → R1
[AIPM Review mode]
@aipm-context
"Review implementation, run all quality checks"

# AI runs tests, coverage, linters, validates AC

# 6. Complete
apm work-item next 123  # → O1
# Memory auto-syncs to Cursor
```

### Workflow 2: Debug Issue

```
# 1. Get context
[AIPM Implementation mode]
@aipm-context
@Lint Errors
@Recent Changes

"Debug error: [paste error]"

# 2. AI analyzes
AI: [Searches codebase]
    [Checks recent changes]
    [Identifies root cause]
    [Suggests fix]

# 3. Apply fix
"Apply suggested fix"

# AI auto-applies, runs tests

# 4. Verify
"Run full test suite"

AI: [Auto-executes pytest]
    [Shows all tests passing]
```

### Workflow 3: Refactor Code

```
# 1. Create refactoring task
apm task create "Refactor X module" --type=refactoring

# 2. Analyze current code
[AIPM Implementation mode]
@Code ModuleX
@aipm-task 655

"Analyze code structure, suggest refactoring"

# 3. Apply refactoring
AI: [Suggests improvements]

"Apply refactoring, maintain test coverage"

AI: [Refactors code]
    [Updates tests]
    [Runs tests]
    [Shows coverage maintained]

# 4. Capture learning
apm work-item next <id>  # Complete
apm provider sync-memories cursor

[Memory created with refactoring pattern]
```

### Workflow 4: Research Solution

```
# 1. Start in Discovery mode
[AIPM Discovery mode]
@Web
@aipm-context

"Research best practices for [problem]"

# 2. AI researches
AI: [Searches web]
    [Reviews documentation]
    [Suggests approaches]

# 3. Validate against project
"How would this fit our three-layer architecture?"

AI: [References database-patterns rule]
    [Suggests integration approach]
    [Identifies risks]

# 4. Document decision
"Create memory for this architectural decision"

AI: [Suggests memory content]

# Manual memory creation or use:
apm provider generate-memory cursor --work-item-id=<id>
```

---

## Tips and Tricks

### Tip 1: Use @aipm-context as Default

Add to Cursor settings to always include:

Settings → Chat → Default includes:
```
@aipm-context
```

### Tip 2: Create Mode Shortcuts

Map keyboard shortcuts to custom modes:

Settings → Keyboard Shortcuts → Custom Modes:
- `Cmd+1`: AIPM Discovery
- `Cmd+2`: AIPM Planning
- `Cmd+3`: AIPM Implementation
- `Cmd+4`: AIPM Review

### Tip 3: Memory Tags for Organization

Add tags to memories for easy filtering:

```markdown
**Tags**: migration, database, pattern, priority
```

Search by tag:
```bash
apm provider list-memories cursor --tag=pattern
```

### Tip 4: Hook Logs for Debugging

Enable hook logging to understand context injection:

```yaml
hooks:
  debug_logging: true
```

View logs:
```bash
tail -f .agentpm/logs/hooks.log
```

### Tip 5: Disable Hooks When Not Needed

For exploratory work outside AIPM workflow:

```bash
# Temporarily disable hooks
apm provider configure cursor --hooks=disabled

# Re-enable
apm provider configure cursor --hooks=enabled
```

---

## Limitations and Considerations

### Context Window Limits

**Rule Size**: 6 rules ≈ 5KB context

**Memory Limit**: Cursor may limit memory file size

**Solution**: Keep memories focused and concise

### Guardrail False Positives

**Issue**: Safe commands blocked by overly strict guardrails

**Solution**: Add to safe_commands list in config

### Hook Performance

**Issue**: onFileSave hook slow on large projects

**Solution**: Disable onFileSave hook:
```yaml
hooks:
  onFileSave: false
```

### Memory Sync Conflicts

**Issue**: Manual memory edits overwritten by sync

**Solution**: Use `--direction=from-cursor` to import manual memories first

### Custom Mode Availability

**Issue**: Custom modes require Cursor 0.40.0+

**Solution**: Update Cursor to latest version

---

## Related Documentation

- **Setup Guide**: [cursor-provider-setup.md](../setup_guide/cursor-provider-setup.md)
- **API Reference**: [cursor-provider-reference.md](../../reference/api/cursor-provider-reference.md)
- **Troubleshooting**: [cursor-provider-issues.md](../../operations/troubleshooting/cursor-provider-issues.md)
- **Architecture**: [cursor-provider-architecture.md](../../architecture/design/cursor-provider-architecture.md)

---

## Support

**Issues**: `apm issue create "Cursor Provider: [description]"`

**Questions**: Check troubleshooting guide first

**Feature Requests**: `apm work-item create "Cursor Provider: [feature]" --type=improvement`

---

**Last Updated**: 2025-10-20
**Version**: 1.0.0
**Status**: Active
