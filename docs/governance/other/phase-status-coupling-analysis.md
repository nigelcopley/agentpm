# Phase-Status Coupling Analysis: Code-Based Truth

**Date**: 2025-10-16
**Objective**: Understand actual phase-status interaction in codebase (ignore documentation assumptions)

---

## Executive Summary

**Critical Finding**: Phase and status are **COMPLETELY DECOUPLED** in the codebase.

- Phase field: **READ-ONLY** (never written by code)
- Status field: **FREQUENTLY WRITTEN** (workflow service manages transitions)
- No coupling logic exists between phase and status changes
- Phase gates validate status transitions, but don't advance phase
- Orchestrator routing reads phase, but doesn't update it

**Gap**: Phase progression is **MANUAL ONLY** - no automatic advancement exists.

---

## 1. Phase Field Usage Analysis

### 1.1 Where Phase is READ

**Session Start Hook** (`session-start.py:82-86`):
```python
if not work_item.phase:
    return None, None

orchestrator = PHASE_TO_ORCHESTRATOR.get(work_item.phase)
```
- **Purpose**: Route to appropriate orchestrator based on current phase
- **Frequency**: Every session start
- **Side Effects**: None (read-only)

**Phase Validator** (`phase_validator.py:889-894`):
```python
if not hasattr(work_item, 'phase') or work_item.phase is None:
    return allowed_sequence[0] if allowed_sequence else None

current_index = allowed_sequence.index(work_item.phase)
```
- **Purpose**: Validate phase transitions are sequential
- **Frequency**: On phase change attempts
- **Side Effects**: None (validation only)

**Phase Gate Validator** (`validators.py:644, 658`):
```python
if hasattr(work_item, 'phase') and work_item.phase is not None:
    current_phase_level = phase_order.get(work_item.phase, 0)
```
- **Purpose**: Validate status transitions require phase completion
- **Frequency**: Every status transition
- **Side Effects**: None (validation only)

**Web Templates** (`work-items/list.html:180`, `work-items/form.html:180-185`):
```html
<option value="D1" {{ 'selected' if work_item and work_item.phase == 'D1' else '' }}>
```
- **Purpose**: Display current phase, allow manual selection
- **Frequency**: UI rendering
- **Side Effects**: None (read-only display)

### 1.2 Where Phase is WRITTEN

**Database Methods** (`work_items.py:75`):
```python
db_data.get('phase'),  # Migration 0011
```
- **Context**: INSERT statement during work item creation
- **Source**: Accepts phase from caller, doesn't generate it
- **Default**: NULL (no default phase on creation)

**Adapter Conversion** (`work_item_adapter.py:41`):
```python
'phase': work_item.phase.value if work_item.phase else None,
```
- **Context**: Model → DB conversion
- **Source**: Passes through existing phase value
- **Logic**: None (pure serialization)

**Update Method** (`work_items.py:119-122`):
```python
updated_work_item = existing.model_copy(update=updates)
db_data = WorkItemAdapter.to_db(updated_work_item)
```
- **Context**: UPDATE statement with arbitrary field updates
- **Source**: Accepts phase in `**updates` dict
- **Logic**: No validation or automatic advancement

### 1.3 Phase Nullability

**Model Definition** (`work_item.py:83`):
```python
phase: Optional[Phase] = None
```
- **Default**: NULL
- **Validation**: None (any Phase enum value or NULL)
- **Migration**: Added in migration_0011

**Database Schema**:
```sql
phase TEXT  -- No NOT NULL constraint, no DEFAULT
```

### 1.4 Default Phase on Creation

**NO DEFAULT PHASE EXISTS**

Work items are created with `phase=NULL`:
```python
backlog = WorkItem(
    project_id=project_id,
    name="Fix Bugs & Issues",
    # No phase specified → defaults to None
)
```

Phase must be explicitly set by caller:
```python
wi = WorkItem(..., phase=Phase.D1_DISCOVERY)
```

---

## 2. Status Field Usage Analysis

### 2.1 Where Status is READ

**Workflow Service** (`service.py:145, 243-274`):
```python
if work_item.status != new_status:
    self._check_rules(...)

if task.status != new_status:
    self._validate_work_item_state(task, new_status)
```
- **Purpose**: Validate transitions, check current state
- **Frequency**: Every transition attempt
- **Side Effects**: Rule enforcement, gate validation

**State Machine** (`state_machine.py`):
```python
if current_status == new_status:
    return ValidationResult(valid=False)
```
- **Purpose**: Validate status transition rules
- **Frequency**: Every transition
- **Side Effects**: None (validation only)

### 2.2 Where Status is WRITTEN

**Workflow Service** (`service.py:102-108, 180-186, 319-324`):
```python
# Project transitions
updated = projects.update_project(self.db, project_id, status=new_status)

# Work item transitions
updated = work_items.update_work_item(self.db, work_item_id, status=new_status)

# Task transitions
updated = tasks.update_task(self.db, task_id, **update_params)
```
- **Context**: Status transition commands
- **Frequency**: High (all workflow transitions)
- **Logic**: Validation → Write → Event emission

**Database Methods** (`work_items.py:126-127`):
```python
query = f"UPDATE work_items SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
conn.execute(query, params)
```
- **Context**: Generic update method
- **Source**: Workflow service or CLI commands
- **Validation**: Model-level only (enum values)

### 2.3 Status Validation Logic

**State Machine Transitions** (`state_machine.py`):
```python
WORK_ITEM_TRANSITIONS = {
    WorkItemStatus.DRAFT: [WorkItemStatus.READY],
    WorkItemStatus.READY: [WorkItemStatus.ACTIVE],
    WorkItemStatus.ACTIVE: [WorkItemStatus.ACTIVE, WorkItemStatus.REVIEW],
    # ... full state machine
}
```
- **Enforcement**: Validates allowed transitions
- **Location**: `state_machine.py` (centralized)
- **Phase Coupling**: None (status-only logic)

---

## 3. Phase-Status Coupling Points

### 3.1 Coupling in Code: NONE

**No Direct Coupling Exists**:
- ❌ Status change does NOT trigger phase change
- ❌ Phase change does NOT trigger status change
- ❌ No code enforces phase-status alignment
- ❌ No automatic phase progression exists

### 3.2 Coupling in Validation: GATES ONLY

**Phase Gate Validator** (`validators.py:558-860`):
```python
STATUS_TO_REQUIRED_PHASE = {
    WorkItemStatus.DRAFT: None,
    WorkItemStatus.READY: Phase.D1_DISCOVERY,
    WorkItemStatus.ACTIVE: Phase.P1_PLAN,
    WorkItemStatus.REVIEW: Phase.I1_IMPLEMENTATION,
    WorkItemStatus.DONE: Phase.R1_REVIEW,
}

required_phase = cls.STATUS_TO_REQUIRED_PHASE.get(new_status)
if current_phase_level < required_phase_level:
    return ValidationResult(valid=False, reason="...")
```

**Validation Logic**:
1. Status transition attempted (e.g., READY → ACTIVE)
2. Validator checks: "Does current phase >= required phase?"
3. If phase NULL or insufficient → **BLOCK transition**
4. If phase sufficient → **ALLOW transition**

**Key Point**: Gates **BLOCK** status transitions based on phase, but **DON'T ADVANCE** phase.

### 3.3 Coupling in Routing: READ ONLY

**Session Start Hook** (`session-start.py:30-37`):
```python
PHASE_TO_ORCHESTRATOR = {
    Phase.D1_DISCOVERY: 'definition-orch',
    Phase.P1_PLAN: 'planning-orch',
    Phase.I1_IMPLEMENTATION: 'implementation-orch',
    Phase.R1_REVIEW: 'review-test-orch',
    Phase.O1_OPERATIONS: 'release-ops-orch',
    Phase.E1_EVOLUTION: 'evolution-orch'
}
```

**Routing Logic**:
1. Session starts
2. Get highest priority active work item
3. Read `work_item.phase` field
4. Map to orchestrator name
5. **NO PHASE MODIFICATION**

---

## 4. Phase Progression Logic

### 4.1 PhaseValidator: VALIDATION ONLY

**What It Does** (`phase_validator.py:554-686`):
```python
@classmethod
def validate_phase_progression(cls, work_item: any, new_phase: str):
    # Check phase in allowed sequence for type
    # Check prior phases complete (metadata.gates)
    # Return ValidationResult(is_valid=True/False)
```

**What It DOESN'T Do**:
- ❌ Advance phase automatically
- ❌ Trigger phase changes
- ❌ Update work_item.phase field
- ❌ Write to database

**Purpose**: Validate phase transitions are sequential when **manually attempted**.

### 4.2 PhaseGateValidator: BLOCKING ONLY

**What It Does** (`validators.py:558-686`):
```python
@classmethod
def validate_phase_gates(cls, work_item, new_status):
    required_phase = STATUS_TO_REQUIRED_PHASE.get(new_status)
    if current_phase < required_phase:
        return ValidationResult(valid=False)  # BLOCK
```

**What It DOESN'T Do**:
- ❌ Advance phase when gate passes
- ❌ Update work_item.phase
- ❌ Trigger phase progression
- ❌ Suggest next phase

**Purpose**: Prevent status advancement until phase completes.

### 4.3 WorkflowService: STATUS ONLY

**What It Does** (`service.py:113-198`):
```python
def transition_work_item(self, work_item_id, new_status):
    # Validate transition (includes phase gates)
    # Update status
    # Emit event
    return updated
```

**What It DOESN'T Do**:
- ❌ Check if phase should advance
- ❌ Advance phase after status change
- ❌ Update work_item.phase field

**Purpose**: Manage status transitions only.

---

## 5. Orchestrator Routing

### 5.1 PHASE_TO_ORCHESTRATOR Mapping

**Definition** (`session-start.py:30-37`):
```python
PHASE_TO_ORCHESTRATOR = {
    Phase.D1_DISCOVERY: 'definition-orch',
    Phase.P1_PLAN: 'planning-orch',
    Phase.I1_IMPLEMENTATION: 'implementation-orch',
    Phase.R1_REVIEW: 'review-test-orch',
    Phase.O1_OPERATIONS: 'release-ops-orch',
    Phase.E1_EVOLUTION: 'evolution-orch'
}
```

**Usage**:
```python
orchestrator = PHASE_TO_ORCHESTRATOR.get(work_item.phase)
```

### 5.2 Routing Behavior

**Current Implementation** (`session-start.py:54-105`):
```python
def determine_orchestrator(db):
    active_wis = list_work_items(db, status=WorkItemStatus.ACTIVE)
    work_item = min(active_wis, key=lambda wi: wi.priority)

    if not work_item.phase:
        return None, None  # NO ROUTING if phase NULL

    orchestrator = PHASE_TO_ORCHESTRATOR.get(work_item.phase)
    return orchestrator, wi_dict
```

**Routing Rules**:
1. Get active work items
2. Select highest priority (lowest number)
3. Read phase field
4. Map to orchestrator
5. **NO PHASE UPDATE**

**If phase NULL**:
- Returns `(None, None)`
- No orchestrator routing
- Session proceeds without routing

**Routing is**:
- ✅ Automatic (on session start)
- ✅ Priority-based (highest first)
- ❌ NOT phase-advancing (read-only)

---

## 6. Code Flow Analysis

### 6.1 Status Transition Flow

```
User: apm work-item start 355
    ↓
CLI: work_item/start.py
    ↓
WorkflowService.transition_work_item(355, WorkItemStatus.ACTIVE)
    ↓
    ├─ Load work_item (phase=P1_PLAN, status=READY)
    ├─ Check rules (governance)
    ├─ Validate transition (state machine)
    ├─ PhaseGateValidator.validate_phase_gates()
    │   ├─ Required phase for ACTIVE: P1_PLAN
    │   ├─ Current phase: P1_PLAN ✅
    │   └─ Allow transition ✅
    ├─ Update status: READY → ACTIVE
    ├─ Emit WORK_ITEM_STARTED event
    └─ Return updated work_item (phase=P1_PLAN, status=ACTIVE)

Result: Status changed, phase UNCHANGED
```

### 6.2 Phase Validation Flow (Manual Phase Change)

```
User: apm work-item update 355 --phase I1_IMPLEMENTATION
    ↓
CLI: work_item/update.py
    ↓
work_items.update_work_item(db, 355, phase=Phase.I1_IMPLEMENTATION)
    ↓
    ├─ Load existing work_item (phase=P1_PLAN)
    ├─ Apply updates: phase → I1_IMPLEMENTATION
    ├─ Pydantic validation (enum check)
    ├─ NO PHASE PROGRESSION VALIDATION ❌
    ├─ Update database
    └─ Return updated work_item (phase=I1_IMPLEMENTATION)

Result: Phase changed WITHOUT validation
```

**Gap**: No automatic phase progression validation on manual updates.

### 6.3 Session Start Routing Flow

```
Session Start Hook
    ↓
determine_orchestrator(db)
    ↓
    ├─ Get active work items
    ├─ Select highest priority
    ├─ work_item.phase == P1_PLAN
    ├─ PHASE_TO_ORCHESTRATOR[P1_PLAN] → 'planning-orch'
    └─ Return ('planning-orch', wi_dict)
    ↓
format_context()
    ↓
    └─ Display: "Route To: planning-orch"

Result: Routing suggestion displayed, NO PHASE UPDATE
```

---

## 7. Validation Logic Breakdown

### 7.1 Phase Gate Requirements

**Status → Required Phase Matrix** (`validators.py:581-590`):
```python
STATUS_TO_REQUIRED_PHASE = {
    WorkItemStatus.DRAFT:     None,                # No phase required
    WorkItemStatus.READY:     Phase.D1_DISCOVERY,   # Design complete
    WorkItemStatus.ACTIVE:    Phase.P1_PLAN,        # Planning complete
    WorkItemStatus.REVIEW:    Phase.I1_IMPLEMENTATION, # Build complete
    WorkItemStatus.DONE:      Phase.R1_REVIEW,      # Review complete
}
```

**Validation Logic**:
```python
required_phase = STATUS_TO_REQUIRED_PHASE.get(new_status)
current_phase_level = phase_order.get(work_item.phase, 0)
required_phase_level = phase_order.get(required_phase, 0)

if current_phase_level < required_phase_level:
    return ValidationResult(valid=False, reason="Phase incomplete")
```

**Phase Order**:
```python
phase_order = {
    Phase.D1_DISCOVERY: 1,
    Phase.P1_PLAN: 2,
    Phase.I1_IMPLEMENTATION: 3,
    Phase.R1_REVIEW: 4,
    Phase.O1_OPERATIONS: 5,
    Phase.E1_EVOLUTION: 6,
}
```

### 7.2 Legacy Gates (Deprecated)

**Metadata.gates Structure** (for backward compatibility):
```json
{
  "gates": {
    "D1_ready": {"status": "done", "completion": 100},
    "P1_plan": {"status": "done", "completion": 100}
  }
}
```

**Deprecation Timeline**:
- 2025-10-12: Phase column introduced
- 2025-12-31: Deprecation warnings logged
- 2026-01-31: metadata.gates removed

**Current Behavior**:
- If `work_item.phase` is set → use phase column
- If `work_item.phase` is NULL → fallback to metadata.gates
- Logs deprecation warning for legacy usage

---

## 8. Actual Coupling Points (Comprehensive)

### 8.1 Where Phase Affects Status

**Location**: `validators.py:558-686` (PhaseGateValidator)

**Coupling Type**: Validation (blocking)

**Logic**:
```python
# Status transition attempts
if new_status == WorkItemStatus.ACTIVE:
    required_phase = Phase.P1_PLAN
    if work_item.phase < required_phase:
        raise WorkflowError("Phase incomplete")
```

**Behavior**: Phase **BLOCKS** status transitions

**Example**:
```python
# Phase: D1_DISCOVERY, Status: READY
transition_work_item(355, WorkItemStatus.ACTIVE)
# → BLOCKED: Need P1_PLAN phase complete
```

### 8.2 Where Status Affects Phase

**Answer**: NOWHERE

**No code exists** that:
- Advances phase based on status
- Updates phase when status changes
- Suggests phase changes
- Automatically progresses phases

### 8.3 Where Phase and Status are Validated Together

**Location**: `validators.py:84-223` (StateRequirements)

**Coupling**: Sequential validation (not mutual)

**Flow**:
```python
def validate_work_item_requirements(work_item, new_status):
    # Step 1: Basic requirements
    # Step 2: Why value validation
    # Step 3: Phase gate validation ← COUPLING POINT
    phase_gate_result = PhaseGateValidator.validate_phase_gates(work_item, new_status)
    if not phase_gate_result.valid:
        return phase_gate_result  # BLOCK
    # Step 4: Evidence validation
    # Step 5: Documentation validation
```

**Key Point**: Phase gates are ONE OF MANY validations, not exclusive coupling.

---

## 9. Summary: The Truth

### 9.1 What Phase Field Does

**Read Operations**:
- ✅ Routing: Session start hook maps phase → orchestrator
- ✅ Validation: Phase gates validate status transitions
- ✅ Display: Web UI shows current phase

**Write Operations**:
- ❌ NO automatic progression
- ❌ NO status-triggered updates
- ❌ Manual updates only (CLI commands)

**Default Behavior**:
- New work items: `phase=NULL`
- No automatic initialization
- Must be manually set

### 9.2 What Status Field Does

**Read Operations**:
- ✅ Workflow validation: Check current state
- ✅ State machine: Validate transitions
- ✅ Dependency checks: Parent/child relationships

**Write Operations**:
- ✅ Frequent: Every workflow transition
- ✅ Automatic: Via WorkflowService
- ✅ Event-driven: Triggers workflow events

**Default Behavior**:
- New work items: `status=DRAFT`
- Automatic transitions via CLI commands
- Fully managed lifecycle

### 9.3 Coupling Reality

**Phase → Status**: BLOCKING ONLY
- Phase gates **prevent** status transitions
- Phase **does not advance** status
- Validation-only relationship

**Status → Phase**: NONE
- Status changes **do not affect** phase
- No automatic phase progression
- No coupling logic exists

**Orchestrator Routing**: READ-ONLY
- Phase determines orchestrator selection
- No phase updates during routing
- Routing is informational only

### 9.4 The Gap

**Phase Progression**: MANUAL ONLY
- No automatic advancement
- No orchestrator-driven progression
- No status-triggered updates
- Must use: `apm work-item update <id> --phase <phase>`

**Implication**: Phase field is **STATIC** unless manually updated.

---

## 10. Recommendations

### 10.1 Document Current Behavior

**Reality**:
- Phase field is manual-only
- Status field is workflow-managed
- Phase gates validate, don't advance
- Orchestrator routing reads, doesn't write

**Documentation Should State**:
- "Phase must be manually advanced"
- "Phase gates block status transitions"
- "No automatic phase progression exists"

### 10.2 Potential Enhancements

**If Automatic Phase Progression Desired**:
1. Add phase advancement logic to WorkflowService
2. Trigger on status transitions (e.g., ACTIVE → advance to I1)
3. Validate sequential progression
4. Emit phase change events

**If Manual Phase Control Preferred**:
1. Add phase validation to update commands
2. Prevent skipping phases
3. Add CLI helper: `apm work-item next-phase <id>`
4. Show phase status in `apm status`

---

## Appendix: Code References

**Phase Field**:
- Model: `work_item.py:83`
- Database: `work_items.py:75` (INSERT), line 41 (adapter)
- Validation: `phase_validator.py:554-686`

**Status Field**:
- Model: `work_item.py:80`
- Transitions: `service.py:113-198`
- State Machine: `state_machine.py`

**Coupling Points**:
- Phase Gates: `validators.py:558-686`
- Orchestrator Routing: `session-start.py:30-105`

**No Coupling**:
- Status changes: `service.py` (no phase updates)
- Phase validation: `phase_validator.py` (no status updates)
- Update methods: `work_items.py` (independent fields)

---

**End of Analysis**
