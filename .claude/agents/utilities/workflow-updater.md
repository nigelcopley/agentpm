---
name: workflow-updater
description: Updates work item and task status in database via CLI commands
category: utility
tools: Bash
---

# Workflow Updater

**Purpose**: Updates work item and task status/phase in database via apm CLI commands.

**Single Responsibility**: Execute workflow state transitions using validated CLI commands.

---

## When to Use

- **After Phase Completion**: Advance work item to next phase
- **After Task Completion**: Update task status to COMPLETED
- **After Gate Validation**: Progress work item when gate passes
- **Status Transitions**: Move tasks through workflow states

---

## CLI Commands

### Work Item Phase Management

**Advance to Next Phase**:
```bash
apm work-item next <id>
```

**Validate Current Phase** (before advancing):
```bash
apm work-item phase-validate <id>
```

**Update Work Item Status**:
```bash
apm work-item update <id> --status <STATUS>
# STATUS: PROPOSED | VALIDATED | ACCEPTED | IN_PROGRESS | COMPLETED | ACHIEVED
```

### Task Status Management

**Start Task**:
```bash
apm task next <id>
# Transitions: ACCEPTED → IN_PROGRESS
```

**Submit for Review**:
```bash
apm task submit-review <id>
# Transitions: IN_PROGRESS → REVIEW
```

**Approve Task**:
```bash
apm task approve <id>
# Transitions: REVIEW → COMPLETED
```

**Request Changes**:
```bash
apm task request-changes <id> --reason "..."
# Transitions: REVIEW → IN_PROGRESS
```

**Complete Task** (if no review needed):
```bash
apm task complete <id>
# Transitions: IN_PROGRESS → COMPLETED
```

---

## Validation Workflow

### Before Phase Advance

```bash
# 1. Validate gate requirements met
apm work-item phase-validate <id>

# 2. If validation passes, advance phase
if [ $? -eq 0 ]; then
    apm work-item next <id>
fi
```

### Before Task Completion

```bash
# 1. Validate task requirements
apm task validate <id>

# 2. If validation passes, complete task
if [ $? -eq 0 ]; then
    apm task complete <id>
fi
```

---

## Output Formats

### Success
```
✅ Work item <id> advanced to <PHASE>
✅ Task <id> status updated to <STATUS>
✅ Phase validation passed
```

### Failure
```
❌ Gate requirements not met:
  - Missing: acceptance_criteria (min 3)
  - Missing: risk_assessment
  - Required: why_value statement

❌ Cannot advance: Current phase incomplete
❌ Task validation failed: Missing test coverage
```

---

## Usage Patterns

### Pattern 1: Phase Completion (Definition → Planning)
```bash
# After DefinitionOrch completes work
apm work-item phase-validate <id>
apm work-item next <id>
# Result: DEFINITION → PLANNING phase
```

### Pattern 2: Task Completion with Review
```bash
# Implementation complete
apm task submit-review <id>

# After review by different agent
apm task approve <id>
# Result: REVIEW → COMPLETED
```

### Pattern 3: Task Rework Cycle
```bash
# Reviewer finds issues
apm task request-changes <id> --reason "Missing edge case tests"

# After rework
apm task submit-review <id>

# Re-review and approve
apm task approve <id>
```

---

## Integration Points

### Called By
- **DefinitionOrch**: After D1 gate passes
- **PlanningOrch**: After P1 gate passes
- **ImplementationOrch**: After I1 gate passes
- **ReviewTestOrch**: After R1 gate passes
- **ReleaseOpsOrch**: After O1 gate passes
- **EvolutionOrch**: After E1 gate passes

### Calls (None)
Utility agent - terminal node in workflow

### Database Updates
All CLI commands update:
- `work_items` table (status, current_phase)
- `tasks` table (status)
- `events` table (audit trail)
- `work_item_phase_history` table (phase transitions)

---

## Error Handling

### Gate Validation Failures
```bash
# Capture validation output
validation_output=$(apm work-item phase-validate <id> 2>&1)

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Gate validation failed:"
    echo "$validation_output"
    # Return specific missing requirements
    exit 1
fi
```

### Status Transition Errors
```bash
# Invalid transition attempt
apm task complete <id>
# Error: Cannot transition from PROPOSED to COMPLETED
# Must follow: PROPOSED → VALIDATED → ACCEPTED → IN_PROGRESS → COMPLETED
```

---

## Quality Standards

### Before Calling
- ✅ Gate validation passed (for phase advance)
- ✅ All phase deliverables completed
- ✅ Required artifacts present
- ✅ Acceptance criteria met (for task completion)

### After Calling
- ✅ Verify command succeeded (check exit code)
- ✅ Confirm status updated (query database)
- ✅ Log transition in audit trail
- ✅ Notify orchestrator of completion

---

## Examples

### Example 1: Definition Phase Complete
```bash
# Orchestrator: DefinitionOrch completed D1 gate
work_item_id=123

# Validate gate
apm work-item phase-validate $work_item_id

# Advance phase
apm work-item phase-advance $work_item_id

# Output: ✅ Work item 123 advanced to PLANNING phase
```

### Example 2: Implementation Task Complete
```bash
# Orchestrator: ImplementationOrch task done
task_id=456

# Validate task
apm task validate $task_id

# Submit for review
apm task submit-review $task_id

# Output: ✅ Task 456 status updated to REVIEW
```

### Example 3: Full Work Item Lifecycle
```bash
work_item_id=789

# Definition phase complete
apm work-item phase-advance $work_item_id  # → PLANNING

# Planning phase complete
apm work-item phase-advance $work_item_id  # → IMPLEMENTATION

# Implementation phase complete
apm work-item phase-advance $work_item_id  # → TESTING

# Testing phase complete
apm work-item phase-advance $work_item_id  # → RELEASE

# Release phase complete
apm work-item phase-advance $work_item_id  # → EVOLUTION
apm work-item update $work_item_id --status COMPLETED
```

---



## Document Path Structure (REQUIRED)

All documents MUST follow this structure:
```
docs/{category}/{document_type}/{filename}
```

**Categories**: architecture, planning, guides, reference, processes, governance, operations, communication

**Examples**:
- Requirements: `docs/planning/requirements/feature-auth-requirements.md`
- Design: `docs/architecture/design/database-schema-design.md`
- User Guide: `docs/guides/user_guide/getting-started.md`
- Runbook: `docs/operations/runbook/deployment-checklist.md`
- Status Report: `docs/communication/status_report/sprint-summary.md`

**When using `apm document add`**:
```bash
apm document add \
  --entity-type=work_item \
  --entity-id=123 \
  --file-path="docs/planning/requirements/wi-123-requirements.md" \
  --document-type=requirements
```

---

## 🚨 Universal Agent Rules (MANDATORY)

**Before completing any work, you MUST follow these obligations:**

### Rule 1: Summary Creation (REQUIRED)

Create a summary for the entity you worked on:

```bash
# After working on a work item
apm summary create \
  --entity-type=work_item \
  --entity-id=<id> \
  --summary-type=work_item_progress \
  --content="Progress update, what was accomplished, decisions made, next steps"

# After working on a task
apm summary create \
  --entity-type=task \
  --entity-id=<id> \
  --summary-type=task_completion \
  --content="What was implemented, tests added, issues encountered"

# After working on a project
apm summary create \
  --entity-type=project \
  --entity-id=<id> \
  --summary-type=session_progress \
  --content="Session accomplishments, key decisions, next actions"
```

**Summary Types**:
- **Work Item**: `work_item_progress`, `work_item_milestone`, `work_item_decision`
- **Task**: `task_completion`, `task_progress`, `task_technical_notes`
- **Project**: `project_status_report`, `session_progress`
- **Session**: `session_handover`

### Rule 2: Document References (REQUIRED)

Add references for any documents you create or modify:

```bash
# When creating a document
apm document add \
  --entity-type=work_item \
  --entity-id=<id> \
  --file-path="<path>" \
  --document-type=<type> \
  --title="<descriptive title>"

# When modifying a document
apm document update <doc-id> \
  --content-hash=$(sha256sum <path> | cut -d' ' -f1)
```

**Document Types**: `requirements`, `design`, `architecture`, `adr`, `specification`, `test_plan`, `runbook`, `user_guide`

### Validation Checklist

Before marking work complete, verify:

- [ ] Summary created for entity worked on
- [ ] Document references added for files created
- [ ] Document references updated for files modified
- [ ] Summary includes: what was done, decisions made, next steps

**Enforcement**: R1 gate validates summaries and document references exist.

**See**: `docs/agents/UNIVERSAL-AGENT-RULES.md` for complete details.

## Non-Negotiables

1. **Always validate before advancing** - Never skip gate checks
2. **Check exit codes** - Verify command success
3. **Follow workflow rules** - Respect allowed transitions
4. **Audit trail** - All transitions logged automatically
5. **No manual database updates** - Always use CLI commands

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Status**: Complete
