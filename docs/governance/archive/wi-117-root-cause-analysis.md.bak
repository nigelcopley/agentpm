# WI-117 Root Cause Analysis: Boilerplate Task Metadata

**Investigation Date**: 2025-10-20
**Investigator**: code-analyzer agent
**Task**: #628 - Investigate boilerplate metadata root cause

---

## Executive Summary

**ROOT CAUSE IDENTIFIED**: Task creation commands use `--quality-template=auto` by default, which loads JSON templates from `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/templates/json/tasks/` directory. These templates contain **example metadata** intended as documentation, but are being applied literally to real tasks.

**Impact**: Tasks 608, 609, 611 (and potentially others) have irrelevant acceptance criteria about "filter results" and "400ms API responses" despite being about POC creation, testing infrastructure, and documentation verification.

**Severity**: HIGH - Metadata pollution undermines task tracking and quality gates.

---

## Investigation Findings

### 1. Source Location Identified

**File**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/templates/json/tasks/implementation.json`

**Lines 3-17**: Boilerplate acceptance criteria
```json
{
  "acceptance_criteria": [
    {
      "criterion": "Users can filter results by at least five dimensions.",
      "met": false,
      "evidence": null
    },
    {
      "criterion": "Filter selections persist across refresh and new sessions.",
      "met": false,
      "evidence": null
    },
    {
      "criterion": "API returns results within 400ms p95 under load.",
      "met": false,
      "evidence": null
    }
  ],
  "technical_approach": "Outline core modules, data flow, and performance considerations for implementing the filters service.",
  "test_plan": "Unit test filter builders, integration test search endpoint, regression test analytics emissions.",
  ...
}
```

**Purpose**: This template was intended as an **example** of what quality metadata *could* look like for a hypothetical search/filter feature.

**Problem**: When used via `--quality-template=auto`, this **example metadata** is copied verbatim into real tasks.

---

### 2. Template Loading Mechanism

**Code Path**: `agentpm/cli/commands/task/create.py` (lines 172-192)

**Mechanism**:
1. User runs: `apm task create "Task Name" --type=implementation`
2. Default flag: `--quality-template=auto` (line 90)
3. `auto` resolves to: `tasks/implementation` for implementation tasks (line 38-42)
4. Template loaded via: `load_template(template_id, project_root)` (line 180)
5. Template data **deep copied** into `quality_metadata` (line 192)
6. Task created with this metadata (line 228)

**Code Evidence**:
```python
# Line 37-42: Template mapping by task type
TASK_TEMPLATE_BY_TYPE = {
    'implementation': 'tasks/implementation',
    'bugfix': 'tasks/bugfix',
    'testing': 'tasks/testing',
    'design': 'tasks/design',
}

# Line 173-192: Template loading logic
quality_metadata = {}
template_choice = (quality_template or '').strip().lower()
if template_choice not in ('', 'none', 'off'):
    if template_choice in ('auto', 'default'):
        template_id = TASK_TEMPLATE_BY_TYPE.get(task_type, 'tasks/generic')
    else:
        template_id = quality_template
    try:
        template_data = load_template(template_id, project_root=project_root)
    ...
    quality_metadata = deepcopy(template_data)
```

---

### 3. Affected Tasks

**Confirmed Cases** (from database query):
- **Task 608**: "Create POC demonstrating selected tools" (type: implementation)
- **Task 609**: "Implement production testing infrastructure" (type: implementation)
- **Task 611**: "Verify documentation testing infrastructure" (type: testing)

**Query Results**:
```sql
SELECT id, name, type, quality_metadata FROM tasks WHERE id IN (608, 609, 611);
```

All three tasks show identical boilerplate:
- Acceptance criteria about "filter results by five dimensions"
- Technical approach about "filters service"
- Test plan about "filter builders" and "search endpoint"

**None of these tasks are related to search/filter functionality.**

---

### 4. Template Files Audit

**Location**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/templates/json/tasks/`

**Files**:
1. `implementation.json` - Contains "search/filter" example metadata ❌ PROBLEMATIC
2. `testing.json` - Contains "search filters" test coverage targets ❌ PROBLEMATIC
3. `bugfix.json` - Contains "filter builder" bug scenario ❌ PROBLEMATIC
4. `design.json` - Contains "search filtering" architecture ❌ PROBLEMATIC
5. `generic.json` - Contains placeholder text ✅ ACCEPTABLE

**Pattern**: All templates (except `generic.json`) use a **consistent fictional scenario** (search/filter feature) to demonstrate metadata structure.

**Intent**: These were meant as **documentation examples**, not production defaults.

---

### 5. Agent Usage Pattern

**Agent**: backlog-curator (sub-agent)
**Location**: `.claude/agents/sub-agents/backlog-curator.md`

**Responsibility**: Create work items and tasks via `apm` commands (lines 55-62)

**Command Pattern** (line 58):
```bash
apm task create --work-item-id <id> --title "..." --type <type> --estimate <hours>
```

**Observation**: Agent instructions **do not mention `--quality-template` flag**, meaning they use the **implicit default** (`auto`).

**Result**: Every task created by backlog-curator inherits boilerplate metadata automatically.

---

### 6. Why This Wasn't Caught Earlier

**Factors**:
1. **Default flag**: `--quality-template=auto` is the default (line 90-92 in create.py)
2. **No validation**: Template content is not validated for relevance to task
3. **Silent application**: No warning when template metadata doesn't match task name
4. **Agent unawareness**: Agents don't know templates are being applied
5. **Documentation gap**: Templates look like production defaults, not examples

---

## Root Cause Statement

**Primary Cause**: Template files in `agentpm/templates/json/tasks/` contain **example metadata from a fictional search/filter feature** and are being applied **by default** to all tasks via `--quality-template=auto`.

**Contributing Causes**:
1. Template files contain **scenario-specific examples** instead of **generic placeholders**
2. Default behavior is **template=auto** instead of **template=none**
3. No validation that template content matches task name/description
4. Agent instructions omit `--quality-template` flag guidance
5. No warning when boilerplate is detected

---

## Impact Analysis

### Metadata Integrity
- **Polluted tasks**: Unknown number (at least 3 confirmed, potentially more)
- **Quality gates**: Gates may fail if checking AC relevance
- **Searchability**: Searching for "filter" returns unrelated tasks
- **Trustworthiness**: Developers ignore metadata if it's often wrong

### Developer Experience
- **Confusion**: Acceptance criteria don't match task goals
- **Rework**: Developers must manually fix metadata post-creation
- **Distrust**: Metadata system loses credibility

### System Integrity
- **Data quality**: Database contains incorrect business logic metadata
- **Reporting**: Metrics based on AC completion are unreliable
- **Automation**: Automated workflows depending on AC will behave incorrectly

---

## Recommended Fixes

### Fix 1: Replace Example Content with Generic Placeholders (IMMEDIATE)

**Action**: Update template files to use **generic, task-agnostic placeholders**

**Files to Update**:
- `agentpm/templates/json/tasks/implementation.json`
- `agentpm/templates/json/tasks/testing.json`
- `agentpm/templates/json/tasks/bugfix.json`
- `agentpm/templates/json/tasks/design.json`

**Example Replacement** (implementation.json):
```json
{
  "acceptance_criteria": [
    {
      "criterion": "Primary deliverable is complete and functional",
      "met": false,
      "evidence": null
    },
    {
      "criterion": "Unit tests cover core functionality (>80% coverage)",
      "met": false,
      "evidence": null
    },
    {
      "criterion": "Documentation updated to reflect changes",
      "met": false,
      "evidence": null
    }
  ],
  "technical_approach": "Describe the implementation strategy, key modules, and integration points.",
  "test_plan": "List test types (unit, integration, e2e) and coverage targets.",
  "risks": [
    {
      "description": "Identify potential technical or business risks",
      "mitigation": "Describe mitigation strategy"
    }
  ],
  "notes": "Add any implementation notes, caveats, or follow-up tasks."
}
```

**Priority**: IMMEDIATE (prevents future pollution)

---

### Fix 2: Change Default to `--quality-template=none` (RECOMMENDED)

**Action**: Modify `create.py` line 90 to default to `none` instead of `auto`

**Rationale**:
- Forces explicit template selection
- Prevents accidental boilerplate injection
- Aligns with principle of "explicit is better than implicit"

**Code Change** (`agentpm/cli/commands/task/create.py`):
```python
# Line 88-93 (BEFORE)
@click.option(
    '--quality-template',
    default='auto',  # ❌ PROBLEMATIC DEFAULT
    show_default=True,
    help='Seed quality metadata from template ID. Use "auto" to pick based on task type, or "none" to disable.'
)

# Line 88-93 (AFTER)
@click.option(
    '--quality-template',
    default='none',  # ✅ SAFE DEFAULT
    show_default=True,
    help='Seed quality metadata from template ID. Use "auto" to pick based on task type, or "none" to disable.'
)
```

**Trade-off**: Users must explicitly opt-in to templates, but this prevents silent metadata corruption.

**Priority**: HIGH (architectural decision)

---

### Fix 3: Add Boilerplate Detection Validation (RECOMMENDED)

**Action**: Add validation logic to detect known boilerplate patterns and warn users

**Location**: `agentpm/cli/commands/task/create.py` (after line 228)

**Implementation**:
```python
# After line 228 (task created)
BOILERPLATE_PATTERNS = [
    "Users can filter results by at least five dimensions",
    "Filter selections persist across refresh",
    "API returns results within 400ms p95",
    "Performance benchmark shows <10% degradation",
]

def detect_boilerplate(quality_metadata: dict, task_name: str) -> list:
    """Detect known boilerplate patterns in metadata."""
    issues = []
    if 'acceptance_criteria' in quality_metadata:
        for ac in quality_metadata['acceptance_criteria']:
            criterion = ac.get('criterion', '') if isinstance(ac, dict) else ac
            for pattern in BOILERPLATE_PATTERNS:
                if pattern.lower() in criterion.lower():
                    issues.append(f"Criterion contains boilerplate: '{criterion}'")
    return issues

# Check for boilerplate
if quality_metadata:
    boilerplate_issues = detect_boilerplate(quality_metadata, name)
    if boilerplate_issues:
        console.print("\n⚠️  [yellow]WARNING: Possible boilerplate detected in metadata:[/yellow]")
        for issue in boilerplate_issues:
            console.print(f"   • {issue}")
        console.print("\n   Consider updating with task-specific criteria:")
        console.print(f"   apm task update {created_task.id} --quality-metadata '{{...}}'")
        console.print()
```

**Priority**: MEDIUM (safety net)

---

### Fix 4: Update Agent Instructions (RECOMMENDED)

**Action**: Update `backlog-curator.md` to include `--quality-template=none` in examples

**File**: `.claude/agents/sub-agents/backlog-curator.md`

**Change** (line 58):
```markdown
# BEFORE
apm task create --work-item-id <id> --title "..." --type <type> --estimate <hours>

# AFTER
apm task create --work-item-id <id> --title "..." --type <type> --estimate <hours> --quality-template=none
```

**Rationale**: Agents should explicitly disable templates and craft task-specific metadata.

**Priority**: MEDIUM (agent behavior correction)

---

### Fix 5: Clean Up Existing Polluted Tasks (DATA CLEANUP)

**Action**: Identify and fix existing tasks with boilerplate metadata

**Query to Find Affected Tasks**:
```sql
SELECT id, name, type, quality_metadata
FROM tasks
WHERE quality_metadata LIKE '%Users can filter results by at least five dimensions%'
   OR quality_metadata LIKE '%Filter selections persist across refresh%'
   OR quality_metadata LIKE '%API returns results within 400ms%';
```

**Cleanup Options**:
1. **Manual review**: Use `/validate-task-metadata <id>` command to generate specific criteria
2. **Bulk update**: Set `quality_metadata=NULL` for affected tasks
3. **Archive**: Flag tasks as needing metadata review

**Priority**: MEDIUM (data hygiene)

---

## Implementation Plan

### Phase 1: Immediate (Prevent Further Pollution)
1. ✅ Complete root cause analysis (Task 628)
2. ⏳ Update template files with generic placeholders (Fix 1)
3. ⏳ Update agent instructions to use `--quality-template=none` (Fix 4)

### Phase 2: Short-term (Improve Safety)
4. ⏳ Add boilerplate detection validation (Fix 3)
5. ⏳ Change default to `--quality-template=none` (Fix 2)
6. ⏳ Document template system and best practices

### Phase 3: Cleanup (Data Hygiene)
7. ⏳ Identify all polluted tasks via SQL query
8. ⏳ Create cleanup script or manual review process
9. ⏳ Update affected tasks with relevant criteria

---

## Lessons Learned

### Design Flaws
1. **Example data as defaults**: Templates should contain **placeholders**, not **examples**
2. **Implicit defaults**: `auto` behavior should require opt-in, not opt-out
3. **No validation**: System should detect when metadata doesn't match task context

### Process Gaps
1. **Template purpose unclear**: No distinction between "documentation examples" and "production templates"
2. **Agent instructions incomplete**: Agents unaware of template system behavior
3. **No quality checks**: No automated detection of boilerplate metadata

### Cultural Issues
1. **Convenience over correctness**: `auto` default prioritized ease over accuracy
2. **Trust in automation**: Assumed templates would be appropriate for all tasks
3. **Insufficient testing**: Metadata quality not validated in CI/CD

---

## Testing Strategy

### Validate Fix Effectiveness

**Test 1: Template Content**
```bash
# Verify templates use generic placeholders, not specific examples
cat agentpm/templates/json/tasks/implementation.json
# Should NOT contain: "filter", "search", "400ms"
```

**Test 2: Default Behavior**
```bash
# Create task without template flag
apm task create "Test Task" --work-item-id=1 --type=implementation --effort=2

# Verify NO boilerplate in metadata
apm task show <id> | grep -i "filter"
# Should return: no matches
```

**Test 3: Boilerplate Detection**
```bash
# Create task with legacy template (if preserved for testing)
apm task create "Test Task" --work-item-id=1 --type=implementation --effort=2 --quality-template=tasks/implementation_legacy

# Verify warning is displayed
# Expected output: "⚠️  WARNING: Possible boilerplate detected"
```

**Test 4: Agent Behavior**
```bash
# Run backlog-curator agent to create task
# Verify quality_metadata is NULL or contains task-specific content
apm task show <id> --json | jq '.quality_metadata'
```

---

## Metrics for Success

**Before Fix**:
- Tasks with boilerplate: ≥3 (tasks 608, 609, 611)
- Template content: Scenario-specific examples
- Default behavior: `auto` (applies templates by default)
- Warnings: None

**After Fix**:
- Tasks with boilerplate: 0 (new tasks)
- Template content: Generic placeholders
- Default behavior: `none` (no templates unless explicitly requested)
- Warnings: Displayed when boilerplate detected

**Validation Query**:
```sql
-- Find any tasks created after fix with boilerplate
SELECT COUNT(*) as polluted_tasks
FROM tasks
WHERE created_at > '2025-10-20'
  AND (quality_metadata LIKE '%Users can filter results%'
    OR quality_metadata LIKE '%Filter selections persist%');
-- Expected: 0
```

---

## Conclusion

**Root Cause**: Template JSON files contain scenario-specific example metadata (search/filter feature) that is applied verbatim to unrelated tasks via `--quality-template=auto` default.

**Location**: `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/templates/json/tasks/implementation.json` (and related template files)

**Fix Location**:
1. Template files themselves (replace examples with placeholders)
2. `agentpm/cli/commands/task/create.py` line 90 (change default to `none`)
3. `agentpm/cli/commands/task/create.py` after line 228 (add boilerplate detection)
4. `.claude/agents/sub-agents/backlog-curator.md` line 58 (update instructions)

**Recommended Approach**:
1. **Immediate**: Update template content (Fix 1) + agent instructions (Fix 4)
2. **Short-term**: Add validation (Fix 3) + change default (Fix 2)
3. **Ongoing**: Clean up existing polluted tasks (Fix 5)

**Status**: ✅ Root cause identified and documented. Ready for implementation of fixes.

---

**Investigation Task**: #628 - COMPLETE
**Next Action**: Create follow-up tasks for each fix (Fixes 1-5)
**Recommended Priority**: HIGH (data quality and system trust at stake)
