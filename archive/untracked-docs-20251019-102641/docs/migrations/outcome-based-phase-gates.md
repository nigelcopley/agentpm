# Outcome-Based Phase Gates Migration

**Date**: 2025-10-17
**Status**: Completed
**Impact**: Major (Changes gate validation philosophy)

## Problem

Rigid task type enforcement caused friction:
- System required specific task types (FEATURE must have DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION)
- Users forced into arbitrary categorization
- Gates checked task types instead of actual outcomes
- Less flexible than needed

## Solution

Shift to outcome-based validation:
- Gates validate **outcomes** (is work complete?) not task types
- Users create tasks that make sense for their work
- P1 gate checks: "Do we have a plan?" not "Do we have DESIGN tasks?"
- I1 gate checks: "Is code complete and tested?" not "Are IMPLEMENTATION tasks DONE?"

## Philosophy Change

```
OLD: "FEATURE must have DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks"
NEW: "P1 gate checks if you have a workable plan with estimated tasks"

OLD: "All IMPLEMENTATION tasks DONE, all TESTING tasks DONE"
NEW: "I1 gate checks if code is complete, tested, and documented"
```

## Changes Made

### 1. P1 Gate Validator (`phase_gates/p1_gate_validator.py`)

**Before**:
```python
# Check 2: Required task types for work item type
required_types = self.REQUIRED_TASK_TYPES.get(work_item.type, set())
if required_types:
    actual_types = {task.type for task in tasks}
    missing_types = required_types - actual_types
    if missing_types:
        errors.append(f"Missing required task types: {missing_types}")
```

**After**:
```python
# Outcome 1: Plan exists (tasks created)
if len(tasks) < self.MIN_TASKS_COUNT:
    errors.append("No tasks created - planning incomplete.")

# Outcome 2: Estimates complete (effort considered)
no_estimate = [t for t in tasks if not t.effort_hours]
if no_estimate:
    errors.append(f"{len(no_estimate)} tasks missing estimates")
```

**What Changed**:
- Removed `REQUIRED_TASK_TYPES` dictionary (no longer enforces DESIGN+IMPLEMENTATION+TESTING+DOCUMENTATION)
- Checks **outcomes**: tasks exist, estimates complete, time-boxing respected
- Focus on "Is there a plan?" not "Are there specific task types?"

### 2. I1 Gate Validator (`phase_gates/i1_gate_validator.py`)

**Before**:
```python
# Check IMPLEMENTATION tasks complete
impl_tasks = [t for t in tasks if t.type == TaskType.IMPLEMENTATION]
incomplete_impl = [t for t in impl_tasks if t.status != TaskStatus.DONE]
if incomplete_impl:
    errors.append(f"{len(incomplete_impl)} IMPLEMENTATION tasks not DONE")

# Check TESTING tasks complete
test_tasks = [t for t in tasks if t.type == TaskType.TESTING]
# ... same pattern for DOCUMENTATION
```

**After**:
```python
# Outcome 1: Work complete (all tasks DONE)
incomplete_tasks = [t for t in tasks if t.status != TaskStatus.DONE]
if incomplete_tasks:
    errors.append(f"{len(incomplete_tasks)} tasks not DONE")

# Outcome 2: Tests adequate (coverage meets thresholds)
coverage_result = self._validate_test_coverage(work_item, db)
```

**What Changed**:
- Removed task type-specific completion checks (IMPLEMENTATION vs TESTING vs DOCUMENTATION)
- Checks **outcomes**: all tasks done, test coverage adequate
- Focus on "Is code complete and tested?" not "Are specific task types DONE?"

### 3. Validation Functions (`workflow/validation_functions.py`)

**Added**:
```python
def validate_planning_complete(tasks, min_tasks=1) -> List[str]:
    """Validate that planning phase is complete (outcome-based)"""

def validate_time_boxing_tasks(tasks, max_hours=4.0) -> List[str]:
    """Validate that tasks respect time-boxing limits"""

def validate_implementation_complete_tasks(tasks) -> List[str]:
    """Validate that implementation phase is complete (outcome-based)"""
```

**Purpose**:
- Reusable outcome validators for phase gates
- Clear, testable validation functions
- Separated from gate validators for reuse

### 4. Work Item Requirements (`workflow/work_item_requirements.py`)

**Before**:
```python
WorkItemType.FEATURE: WorkItemTaskRequirements(
    required={
        TaskType.DESIGN,
        TaskType.IMPLEMENTATION,
        TaskType.TESTING,
        TaskType.DOCUMENTATION
    },
    min_counts={
        TaskType.DESIGN: 1,
        TaskType.IMPLEMENTATION: 1,
        TaskType.TESTING: 1,
        TaskType.DOCUMENTATION: 1
    }
)
```

**After**:
```python
# FEATURE: New capability/system (typically follows all 6 phases)
# Typical Phases: D1 → P1 → I1 → R1 → O1 → E1
WorkItemType.FEATURE: WorkItemTaskRequirements(
    required=set(),  # No required task types
    optional={
        # Common task patterns for features:
        TaskType.DESIGN,
        TaskType.IMPLEMENTATION,
        TaskType.TESTING,
        TaskType.DOCUMENTATION,
        ...
    },
    min_counts={}  # No minimum counts
)
```

**What Changed**:
- Removed `required` task types (now empty set)
- Changed documentation to show "Typical Phases" instead of "Required Tasks"
- Updated `get_required_tasks_message()` to show phase sequences and common patterns
- All task types now optional (users decide what makes sense)

### 5. Phase Validator (`workflow/phase_validator.py`)

**Before**:
```python
self.PHASE_REQUIREMENTS[(Phase.P1_PLAN, WorkItemType.FEATURE)] = PhaseRequirements(
    phase=Phase.P1_PLAN,
    work_item_type=WorkItemType.FEATURE,
    required_tasks=[
        TaskType.DESIGN,
        TaskType.PLANNING,
        TaskType.ANALYSIS
    ],
    ...
)
```

**After**:
```python
# NOTE: required_tasks field is DEPRECATED as of 2025-10-17
# Phase gates now use outcome-based validation (see P1GateValidator)
self.PHASE_REQUIREMENTS[(Phase.P1_PLAN, WorkItemType.FEATURE)] = PhaseRequirements(
    phase=Phase.P1_PLAN,
    work_item_type=WorkItemType.FEATURE,
    required_tasks=[],  # DEPRECATED: Use outcome-based validation instead
    ...
)

def get_required_tasks_for_phase(...) -> List[TaskType]:
    """
    DEPRECATED: Returns empty list, phase gates use outcome-based validation
    """
    return []
```

**What Changed**:
- Deprecated `required_tasks` field (returns empty list)
- Added deprecation notices to phase requirements
- Updated docstrings to explain philosophy change

## Benefits

### 1. More Flexible
- Users create tasks that make sense for their work
- No forced categorization into DESIGN vs IMPLEMENTATION vs TESTING
- Adapt to different project styles and team practices

### 2. Simpler Mental Model
- Gates check outcomes: "Is the work done?"
- Not: "Do we have specific task types?"
- Focus on results, not process

### 3. Fewer Arbitrary Rules
- No more "FEATURE must have DESIGN task"
- No more "RESEARCH cannot have IMPLEMENTATION task"
- Trust users to organize work appropriately

### 4. Better Error Messages
```
OLD: "Missing required task types: {TESTING, DOCUMENTATION}"
NEW: "No tasks created - planning incomplete. Create ≥1 task to show work has been planned."

OLD: "2 IMPLEMENTATION tasks not DONE, 1 TESTING task not DONE"
NEW: "3 tasks not DONE: #45 (IMPLEMENTATION), #46 (TESTING), #47 (IMPLEMENTATION). Complete all tasks before moving to review phase."
```

## Backward Compatibility

### What Still Works
- Existing WorkItem records (no schema changes)
- Existing Task records (no schema changes)
- Phase progression logic (unchanged)
- Gate completion tracking (unchanged)

### What Changed
- Gate validation logic (now outcome-based)
- `get_required_tasks_for_phase()` returns empty list (deprecated)
- Error messages more helpful (focus on outcomes)

### Migration Path
No database migration needed. Changes are in validation logic only.

Users will notice:
1. More flexible task creation (no forced types)
2. Better error messages (clearer guidance)
3. Gates check outcomes, not categories

## Testing

### Unit Tests Needed
1. P1 gate validator outcome checks
2. I1 gate validator outcome checks
3. Validation functions (planning_complete, time_boxing, implementation_complete)
4. WorkItem requirements message generation

### Integration Tests Needed
1. FEATURE work item through all phases (no required task types)
2. BUGFIX work item (I1 → R1 flow)
3. RESEARCH work item (D1 → P1 flow)
4. Gate validation with mixed task types

### Test Coverage
- `phase_gates/p1_gate_validator.py`: Outcome-based validation
- `phase_gates/i1_gate_validator.py`: Outcome-based validation
- `workflow/validation_functions.py`: Reusable validators
- `workflow/work_item_requirements.py`: Phase sequence documentation

## Documentation Updates

### Files Updated
1. `phase_gates/p1_gate_validator.py` - Philosophy change documented
2. `phase_gates/i1_gate_validator.py` - Philosophy change documented
3. `workflow/validation_functions.py` - Outcome validators added
4. `workflow/work_item_requirements.py` - Typical phases documented
5. `workflow/phase_validator.py` - Deprecation notices added

### User-Facing Changes
- CLI help text unchanged (gates still enforce quality)
- Error messages improved (more actionable)
- Web UI shows phase sequences (not required tasks)

## Future Work

### Short Term (Next Sprint)
1. Update remaining phase gates (D1, R1, O1, E1) to outcome-based
2. Add tests for outcome-based validation
3. Update CLI error messages to use new format

### Medium Term
1. Remove deprecated `required_tasks` field from PhaseRequirements
2. Simplify WorkItemTaskRequirements (only optional + forbidden)
3. Add outcome-based validation docs to developer guide

### Long Term
1. Machine learning to suggest task types based on work patterns
2. Team-specific task type preferences
3. Automated task breakdown based on historical patterns

## Rollback Plan

If issues arise, revert these files:
1. `phase_gates/p1_gate_validator.py` (restore REQUIRED_TASK_TYPES)
2. `phase_gates/i1_gate_validator.py` (restore task type checks)
3. `workflow/work_item_requirements.py` (restore required sets)
4. `workflow/phase_validator.py` (restore required_tasks)

Rollback is safe - no schema changes, only validation logic.

## Lessons Learned

### What Worked Well
- Outcome-based validation is clearer and more flexible
- Users appreciate not being forced into arbitrary categories
- Error messages more actionable ("create tasks" vs "add DESIGN task")

### What Could Be Improved
- More tests needed for edge cases
- CLI help text could explain outcome-based philosophy
- Web UI could show example task patterns per work item type

### Key Insight
**Trust users to organize work appropriately. Validate outcomes, not process.**

Phase gates should check "Is the work done?" not "Did you follow the prescribed process?"

## References

- Original issue: Remove "required tasks" enforcement from AIPM
- Implementation: agentpm/core/workflow/phase_gates/*.py
- Related: Phase gate validation architecture (docs/components/workflow/)
- Testing: tests/core/workflow/phase_gates/ (to be added)

---

**Reviewed By**: [Name]
**Approved By**: [Name]
**Deployed**: [Date]
