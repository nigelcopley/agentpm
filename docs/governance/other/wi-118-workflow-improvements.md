# WI-118 Workflow Improvements Discovered

**Work Item**: WI-118 "Full Cursor Integration"
**Date**: 2025-10-20
**Phase**: I1_IMPLEMENTATION → R1_REVIEW

## Executive Summary

During execution of WI-118, we discovered **5 critical workflow friction points** that reduce efficiency and cause errors. These improvements would significantly streamline the AIPM development experience.

---

## Improvement #1: Task-Type-Aware Test Requirements

### Issue
CI-004 gate requires `tests_passing=true` for **all task types**, including DESIGN tasks that produce no testable code.

### Current Behavior
```bash
apm task next 634  # Design task
# ❌ Error: CI-004 Failed: Tests not validated
```

### Problem
- DESIGN tasks create specifications, not code
- DOCUMENTATION tasks create markdown, not code
- No tests exist to run, but system demands test validation

### Impact
- **Severity**: Medium
- **Frequency**: Every DESIGN and DOCUMENTATION task
- **Workaround Time**: 2-3 minutes per task (manual override)

### Proposed Solution
Make test requirements task-type aware:

```python
# agentpm/core/workflow/validators.py
def _check_ci004_tests(self, task: Task) -> tuple[bool, str]:
    # Tasks that don't produce testable code
    NON_TESTABLE_TYPES = ['design', 'documentation', 'research', 'planning']

    if task.type in NON_TESTABLE_TYPES:
        return True, "Test validation not required for {task.type} tasks"

    # Existing test validation logic for implementation/bugfix tasks
    ...
```

### Benefits
- Eliminates unnecessary manual overrides
- Clearer workflow expectations
- Faster task progression
- Better developer experience

---

## Improvement #2: Auto-Populate Acceptance Criteria

### Issue
IMPLEMENTATION tasks require `acceptance_criteria` in `quality_metadata` before starting, but this structure isn't auto-populated.

### Current Behavior
```bash
apm task next 635  # Implementation task
# ❌ Error: IMPLEMENTATION tasks require acceptance_criteria in quality_metadata
```

### Problem
- Developers must manually construct JSON structure
- Easy to forget or format incorrectly
- No template provided
- Blocks task start unnecessarily

### Impact
- **Severity**: Medium
- **Frequency**: Every IMPLEMENTATION task
- **Workaround Time**: 3-5 minutes per task (craft JSON manually)

### Proposed Solution
Auto-populate metadata structure when creating tasks:

```python
# agentpm/cli/commands/task.py
def create_task(task_type: str, ...):
    metadata = {}

    if task_type == 'implementation':
        metadata['acceptance_criteria'] = [
            {
                "criterion": "Code implemented according to spec",
                "met": False
            },
            {
                "criterion": "Tests written and passing",
                "met": False
            }
        ]
        metadata['tests_passing'] = False

    elif task_type == 'testing':
        metadata['test_plan'] = "Test plan to be defined"
        metadata['tests_passing'] = False
        metadata['coverage_percent'] = 0

    # Create task with pre-populated structure
    ...
```

### Benefits
- Zero manual JSON construction
- Consistent metadata structure
- Immediate task start capability
- Reduced errors from malformed JSON

---

## Improvement #3: Task-Type-Specific Metadata Templates

### Issue
TESTING tasks require `test_plan` in `quality_metadata` before starting, with no template or guidance.

### Current Behavior
```bash
apm task next 636  # Testing task
# ❌ Error: TESTING tasks require test_plan in quality_metadata
```

### Problem
- Each task type has different metadata requirements
- Requirements not documented or visible
- Developers discover requirements by hitting errors
- Trial-and-error approach wastes time

### Impact
- **Severity**: Medium
- **Frequency**: Every task of specific types
- **Workaround Time**: 5-10 minutes per task (research requirements, craft JSON)

### Proposed Solution
Provide task-type-specific templates in CLI help:

```bash
apm task create --type=testing --help

Required metadata for TESTING tasks:
  {
    "test_plan": "Description of testing approach",
    "tests_passing": false,
    "coverage_percent": 0,
    "acceptance_criteria": [
      {"criterion": "All tests pass", "met": false}
    ]
  }

Use --metadata-template to auto-generate:
  apm task create "Test feature" --type=testing --metadata-template
```

### Benefits
- Self-documenting requirements
- One-command template generation
- Reduced learning curve
- Fewer workflow errors

---

## Improvement #4: Task-Type-Aware Coverage Gates

### Issue
Coverage requirements apply to **all tasks**, even those testing configuration files or documentation.

### Current Behavior
```bash
apm task next 636  # Testing Cursor rules (.mdc files)
# ❌ Error: Category 'critical_paths' coverage 0.0% < 95.0%
# System runs pytest on entire codebase for config file testing
```

### Problem
- Coverage gates assume all work involves Python code
- TESTING-type tasks validating configs trigger pytest
- No way to specify "this task doesn't involve code coverage"
- Forces workarounds (changing task type)

### Impact
- **Severity**: High (blocks workflow completely)
- **Frequency**: Config testing, integration testing, manual testing
- **Workaround Time**: 10-15 minutes (try multiple approaches, eventually change task type)

### Proposed Solution
Make coverage gates task-type and work-type aware:

```python
# agentpm/core/workflow/validators.py
def _check_coverage_requirements(self, task: Task) -> tuple[bool, str]:
    # Tasks that don't produce code coverage
    NO_COVERAGE_TYPES = ['design', 'documentation', 'research', 'planning']

    if task.type in NO_COVERAGE_TYPES:
        return True, "Coverage not applicable for {task.type} tasks"

    # Check if task explicitly marks coverage as N/A
    metadata = task.quality_metadata or {}
    if metadata.get('coverage_not_applicable'):
        return True, metadata.get('coverage_not_applicable_reason', 'Marked N/A')

    # For implementation/testing of code, check coverage
    if task.type in ['implementation', 'bugfix']:
        return self._check_code_coverage(task)

    return True, "Coverage check not required"
```

### Benefits
- Appropriate gates for task context
- No false failures on config/doc testing
- Clearer expectations
- Fewer workarounds needed

---

## Improvement #5: Flexible Test Execution

### Issue
The workflow service **hardcodes pytest execution** for all TESTING-type tasks, regardless of what's being tested.

### Current Behavior
```python
# agentpm/core/workflow/service.py (conceptual)
if task.type == 'testing':
    run_pytest()  # Always runs, even for config testing
    check_coverage()  # Always checks Python coverage
```

### Problem
- Not all testing involves pytest
- Config testing, integration testing, manual testing don't use pytest
- System forces pytest run even when not applicable
- Causes pytest errors and coverage failures

### Impact
- **Severity**: Critical (completely blocks workflow)
- **Frequency**: Any non-pytest testing task
- **Workaround Time**: 15+ minutes (change task type, bypass checks)

### Proposed Solution
Allow tasks to specify test execution type:

```python
# Task metadata
{
    "test_type": "pytest" | "integration" | "manual" | "config" | "e2e",
    "test_plan": "...",
    "test_execution": {
        "pytest": {
            "enabled": true,
            "coverage_required": true,
            "coverage_threshold": 90
        },
        "manual": {
            "enabled": false,
            "checklist": [...]
        }
    }
}
```

```python
# Validator
def _run_tests(self, task: Task):
    test_type = task.quality_metadata.get('test_type', 'pytest')

    if test_type == 'pytest':
        self._run_pytest()
    elif test_type == 'integration':
        self._run_integration_tests()
    elif test_type == 'manual':
        self._validate_manual_checklist()
    elif test_type == 'config':
        self._validate_config_files()
```

### Benefits
- Support diverse testing approaches
- No forced pytest execution
- Appropriate validation per test type
- Cleaner workflow progression

---

## Implementation Priority

| # | Improvement | Severity | Frequency | Workaround Time | Priority |
|---|-------------|----------|-----------|-----------------|----------|
| 5 | Flexible Test Execution | Critical | Medium | 15+ min | **P0** |
| 4 | Task-Type-Aware Coverage Gates | High | Medium | 10-15 min | **P0** |
| 2 | Auto-Populate AC | Medium | High | 3-5 min | **P1** |
| 3 | Metadata Templates | Medium | High | 5-10 min | **P1** |
| 1 | Task-Type-Aware Tests | Medium | Medium | 2-3 min | **P2** |

### Recommended Implementation Order

1. **Phase 1** (Critical - 1 week):
   - #5: Flexible Test Execution
   - #4: Task-Type-Aware Coverage Gates

2. **Phase 2** (High Impact - 1 week):
   - #2: Auto-Populate Acceptance Criteria
   - #3: Metadata Templates

3. **Phase 3** (Polish - 3 days):
   - #1: Task-Type-Aware Test Requirements

---

## Total Impact Analysis

### Current State (With Friction)
- Average task: 20-30 min overhead from workflow errors
- 4 tasks in WI-118: **~80-120 minutes of friction time**
- Developer frustration: High
- Workflow clarity: Low

### Future State (With Improvements)
- Average task: <5 min overhead (normal workflow)
- 4 tasks in WI-118: **~20 minutes total overhead**
- Time saved: **60-100 minutes per work item**
- Developer frustration: Low
- Workflow clarity: High

### ROI Calculation
- Development time for all 5 improvements: ~2-3 weeks
- Time saved per work item: ~1.5 hours
- Work items per month: ~10
- **Monthly time savings: ~15 hours**
- **Payback period: ~2 months**

---

## Conclusion

These 5 improvements would transform the AIPM workflow from "fighting the system" to "system supports the work." The current friction points are discoverable only through usage, making them perfect candidates for improvement based on real-world experience.

**Recommendation**: Implement all 5 improvements in 3 phases over 2-3 weeks. The ROI is clear and the developer experience improvement is substantial.

---

**Document Version**: 1.0
**Status**: Recommendations for implementation
**Next Steps**: Create work items for each improvement priority group
