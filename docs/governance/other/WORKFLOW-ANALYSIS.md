# Workflow Analysis: Gates, Phases, and Orchestrators

**Date**: 2025-10-12
**Scope**: Relationship between workflow gates, phases, orchestrators, and status enums
**Goal**: Assess opportunities for phase-based orchestration routing

---

## Executive Summary

**Current State**: APM (Agent Project Manager) has a **dual routing system** (Status + Phase) with **partial implementation**. Phase gates (D1-E1) exist but are **underutilized** for orchestration routing.

**Recommendation**: **Unify on Phase-based routing** with Status as a derived/secondary indicator. This aligns perfectly with the three-tier orchestration architecture already defined in CLAUDE.md.

**Impact**:
- ✅ Simplifies routing logic (6 phases vs 9 statuses)
- ✅ Direct phase → mini-orchestrator mapping
- ✅ Type-specific workflows easier to encode
- ✅ Gate enforcement becomes natural (phase completion = gate pass)

---

## 1. Current Gate System

### 1.1 Gate Definitions (PhaseGateValidator)

**Location**: `agentpm/core/workflow/validators.py:505-154`

```python
PHASE_GATE_REQUIREMENTS = {
    WorkItemStatus.PROPOSED: [],                                    # No gates
    WorkItemStatus.VALIDATED: ['D1_ready'],                        # Design gate
    WorkItemStatus.ACCEPTED: ['D1_ready', 'P1_plan'],             # Planning gate
    WorkItemStatus.IN_PROGRESS: ['D1_ready', 'P1_plan'],          # Begin work
    WorkItemStatus.REVIEW: ['D1_ready', 'P1_plan', 'I1_build'],  # Implementation complete
    WorkItemStatus.DONE: ['D1_ready', 'P1_plan', 'I1_build', 'R1_accept'],  # Review accepted
}
```

**Gate Codes**:
- `D1_ready` (Design/Discovery): Feasibility confirmed
- `P1_plan` (Planning): Execution plan ready
- `I1_build` (Implementation): Code complete
- `R1_accept` (Review): Acceptance criteria met
- `O1_ops` (Operations): Deployed successfully (post-completion tracking)
- `E1_eval` (Evaluation): Outcome measured (post-completion tracking)

**Gate Storage**: `metadata.gates` JSON structure in `work_items` table:
```json
{
  "gates": {
    "D1_ready": {
      "status": "done",
      "completion": 100,
      "validated_at": "2025-10-12T10:30:00Z"
    }
  }
}
```

**Enforcement**: Gates are **cumulative** - each status requires ALL previous gates.

### 1.2 Gate-Check Agents

**Pattern**: Each mini-orchestrator has a gate-check sub-agent:
- `definition-gate-check` → Validates D1 criteria
- `planning-gate-check` → Validates P1 criteria
- `implementation-gate-check` → Validates I1 criteria
- `quality-gatekeeper` → Validates R1 criteria
- `operability-gatecheck` → Validates O1 criteria
- `evolution-gate-check` → Validates E1 criteria

**Key Insight**: Gate validation is **delegated** to agents, not performed by orchestrator.

---

## 2. Phase vs Status Analysis

### 2.1 Current Dual System

**Phase Enum** (`agentpm/core/database/enums/types.py:186-203`):
```python
class Phase(str, Enum):
    D1_DISCOVERY = "D1_discovery"
    P1_PLAN = "P1_plan"
    I1_IMPLEMENTATION = "I1_implementation"
    R1_REVIEW = "R1_review"
    O1_OPERATIONS = "O1_operations"
    E1_EVOLUTION = "E1_evolution"
```

**WorkItemStatus Enum** (`agentpm/core/database/enums/status.py:43-68`):
```python
class WorkItemStatus(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "done"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
```

### 2.2 Semantic Differences

| Concept | Phase | Status |
|---------|-------|--------|
| **Purpose** | **Work domain** (what type of work) | **Workflow state** (where in process) |
| **Cardinality** | 6 values | 9 values |
| **Lifecycle** | Linear progression (D1→P1→I1→R1→O1→E1) | Linear + exceptional (blocked, cancelled) |
| **Type-Specific** | **YES** (RESEARCH may skip I1) | **NO** (all types use same states) |
| **Agent Routing** | **NATURAL** (phase → orchestrator) | **INDIRECT** (status → infer phase) |
| **Gate Alignment** | **PERFECT** (D1 phase = D1 gate) | **APPROXIMATE** (VALIDATED ~= D1) |

### 2.3 Current Database State

**Query**: `SELECT phase, status, COUNT(*) FROM work_items GROUP BY phase, status;`

**Results**:
```
phase           | status        | count
----------------|---------------|------
NULL            | accepted      | 1
NULL            | archived      | 9
NULL            | completed     | 24
NULL            | in_progress   | 1
NULL            | proposed      | 18
NULL            | review        | 1
D1_discovery    | completed     | 1
I1_implementation| completed    | 1
O1_operations   | completed     | 1
P1_plan         | in_progress   | 1
R1_review       | in_progress   | 1
```

**Key Observations**:
1. **Most work items (54/59 = 91%) have NULL phase** → Phase is underutilized
2. **Phase is set for only 5 work items** → Recent implementation, not yet adopted
3. **Status is always set** → Current routing uses status exclusively
4. **Phase + Status combinations are consistent** → When phase is set, status aligns (e.g., P1_plan + in_progress)

---

## 3. Orchestrator Mapping Analysis

### 3.1 Current Artifact-Based Routing (CLAUDE.md)

**Master Orchestrator Routing Table**:
```
Incoming Artifact    → Mini-Orchestrator  → Outgoing Artifact
request.raw          → DefinitionOrch     → workitem.ready
workitem.ready       → PlanningOrch       → plan.snapshot
plan.snapshot        → ImplementationOrch → build.bundle
build.bundle         → ReviewTestOrch     → review.approved
review.approved      → ReleaseOpsOrch     → release.deployed
telemetry.snapshot   → EvolutionOrch      → evolution.backlog_delta
```

**Issues with Artifact-Based Routing**:
1. **Artifact types are abstract** (not database fields) - `request.raw`, `workitem.ready` don't exist in schema
2. **No persistence** - artifacts are ephemeral agent communication structures
3. **No auditability** - can't query "which artifacts exist for work item 355"
4. **Routing logic unclear** - how to map work item state → artifact type?

### 3.2 Proposed Phase-Based Routing

**Direct Phase → Orchestrator Mapping**:
```python
PHASE_ORCHESTRATOR_MAP = {
    None:                DefinitionOrch,      # No phase → needs definition
    Phase.D1_DISCOVERY:  DefinitionOrch,      # D1 work → definition orchestrator
    Phase.P1_PLAN:       PlanningOrch,        # P1 work → planning orchestrator
    Phase.I1_IMPLEMENTATION: ImplementationOrch, # I1 work → implementation orchestrator
    Phase.R1_REVIEW:     ReviewTestOrch,      # R1 work → review/test orchestrator
    Phase.O1_OPERATIONS: ReleaseOpsOrch,      # O1 work → release/ops orchestrator
    Phase.E1_EVOLUTION:  EvolutionOrch,       # E1 work → evolution orchestrator
}
```

**Routing Logic**:
```python
def route_by_phase(work_item: WorkItem) -> MiniOrchestrator:
    """Route work item to appropriate mini-orchestrator based on phase"""
    return PHASE_ORCHESTRATOR_MAP[work_item.phase]
```

**Benefits**:
1. ✅ **Database-backed** - phase is a column, queryable, auditable
2. ✅ **Type-safe** - Phase enum prevents invalid values
3. ✅ **Simple** - O(1) lookup, no complex logic
4. ✅ **Clear semantics** - "work item is in P1 phase" is unambiguous
5. ✅ **Gate alignment** - phase completion = gate pass = advance to next orchestrator

### 3.3 Mini-Orchestrator Gate Validation

**Current Pattern** (from `definition-orch.md` and `planning-orch.md`):

Each mini-orchestrator:
1. Receives work item in their phase
2. Delegates work to sub-agents
3. Calls `{phase}-gate-check` agent to validate
4. If gate passes: updates `metadata.gates` + advances phase
5. If gate fails: returns to Master with missing artifacts

**Phase Advancement Logic**:
```python
def complete_phase(work_item: WorkItem, phase: Phase, gate: str):
    """Complete phase by marking gate as ready and advancing phase"""
    # Mark gate complete in metadata
    work_item.metadata['gates'][gate] = {
        'status': 'done',
        'completion': 100,
        'validated_at': datetime.utcnow().isoformat()
    }

    # Advance to next phase
    work_item.phase = NEXT_PHASE_MAP[phase]

    # Update status to align with new phase
    work_item.status = PHASE_STATUS_MAP[work_item.phase]
```

**Phase Advancement Sequence**:
```
NULL → D1_DISCOVERY (D1_ready gate passed)
D1_DISCOVERY → P1_PLAN (P1_plan gate passed)
P1_PLAN → I1_IMPLEMENTATION (tasks created, plan complete)
I1_IMPLEMENTATION → R1_REVIEW (I1_build gate passed)
R1_REVIEW → O1_OPERATIONS (R1_accept gate passed)
O1_OPERATIONS → E1_EVOLUTION (O1_ops tracking, work item completed)
```

---

## 4. Type-Specific Workflow Analysis

### 4.1 Work Item Type Requirements

**Current Implementation**: `agentpm/core/workflow/work_item_requirements.py`

**Type-Specific Required Tasks**:
```python
FEATURE:        DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION
ENHANCEMENT:    IMPLEMENTATION, TESTING
BUGFIX:         ANALYSIS, BUGFIX, TESTING
RESEARCH:       ANALYSIS, DOCUMENTATION  # Forbidden: IMPLEMENTATION, TESTING
PLANNING:       ANALYSIS, DESIGN, DOCUMENTATION, REVIEW  # Forbidden: IMPLEMENTATION
REFACTORING:    ANALYSIS, REFACTORING, TESTING
INFRASTRUCTURE: DESIGN, IMPLEMENTATION, DEPLOYMENT, DOCUMENTATION
```

**Key Insight**: Type-specific requirements are **task-level**, not **phase-level**. All types use the same phase sequence (D1→P1→I1→R1), but create different task types during P1 (planning).

### 4.2 Phase Applicability by Type

**Question**: Do all work item types need all phases?

| Type | D1 Discovery | P1 Planning | I1 Implementation | R1 Review | O1 Operations | E1 Evolution |
|------|--------------|-------------|-------------------|-----------|---------------|--------------|
| FEATURE | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Optional |
| ENHANCEMENT | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ⚠️ Optional | ✅ Optional |
| BUGFIX | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ⚠️ Merged with feature deploy | ❌ Skip |
| RESEARCH | ✅ Required | ✅ Required | ⚠️ **SKIP** (no implementation) | ✅ Required (findings review) | ❌ Skip | ❌ Skip |
| PLANNING | ✅ Required | ✅ Required | ⚠️ **SKIP** (no implementation) | ✅ Required (plan review) | ❌ Skip | ❌ Skip |
| REFACTORING | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ⚠️ Merged with feature deploy | ❌ Skip |
| INFRASTRUCTURE | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Optional |

**Phase Variation by Type**:
- **Universal phases**: D1, P1, R1 (all types need discovery, planning, review)
- **Implementation (I1)**: RESEARCH and PLANNING **skip** (no code to implement)
- **Operations (O1)**: Only FEATURE and INFRASTRUCTURE **require** (others piggyback on feature deploys)
- **Evolution (E1)**: Only FEATURE and INFRASTRUCTURE **track** (optional for all)

### 4.3 Phase Skipping Logic

**Implementation Approach**:
```python
PHASE_SEQUENCE_BY_TYPE = {
    WorkItemType.FEATURE: [D1, P1, I1, R1, O1, E1],
    WorkItemType.RESEARCH: [D1, P1, R1],  # Skip I1 (no code), O1 (no deploy), E1 (no ops)
    WorkItemType.PLANNING: [D1, P1, R1],  # Skip I1 (no code), O1 (no deploy), E1 (no ops)
    # ... other types
}

def get_next_phase(work_item: WorkItem) -> Phase:
    """Get next phase for work item based on type"""
    sequence = PHASE_SEQUENCE_BY_TYPE[work_item.type]
    current_index = sequence.index(work_item.phase)
    return sequence[current_index + 1] if current_index + 1 < len(sequence) else None
```

**Gate Validation by Type**:
```python
def validate_phase_gate(work_item: WorkItem, gate: str) -> ValidationResult:
    """Validate gate, but only if phase is in type's sequence"""
    if work_item.phase not in PHASE_SEQUENCE_BY_TYPE[work_item.type]:
        return ValidationResult(valid=True)  # Skip validation for skipped phases
    return PhaseGateValidator.validate_phase_gates(work_item, gate)
```

---

## 5. Recommendations

### 5.1 Migrate to Phase-Based Routing

**Action**: Make `phase` the primary routing field, derive `status` from phase + gate state.

**Changes Required**:

1. **Database Migration**:
   ```sql
   -- Make phase NOT NULL (require all work items have phase)
   ALTER TABLE work_items ALTER COLUMN phase SET NOT NULL;

   -- Add CHECK constraint for phase-status alignment
   ALTER TABLE work_items ADD CONSTRAINT phase_status_alignment
     CHECK (
       (phase = 'D1_discovery' AND status IN ('proposed', 'validated')) OR
       (phase = 'P1_plan' AND status IN ('validated', 'accepted', 'in_progress')) OR
       (phase = 'I1_implementation' AND status = 'in_progress') OR
       (phase = 'R1_review' AND status = 'review') OR
       (phase = 'O1_operations' AND status = 'done') OR
       (phase = 'E1_evolution' AND status = 'done')
     );
   ```

2. **Master Orchestrator Routing**:
   ```python
   # BEFORE (artifact-based, abstract)
   def master_orchestrate(incoming_artifact):
       orch = route_by_artifact_type(incoming_artifact.type)
       result = delegate_to_mini_orch(orch, incoming_artifact)

   # AFTER (phase-based, concrete)
   def master_orchestrate(work_item_id: int):
       work_item = db.get_work_item(work_item_id)
       orch = PHASE_ORCHESTRATOR_MAP[work_item.phase]
       result = delegate_to_mini_orch(orch, work_item)
       if result.gate_passed:
           work_item.phase = get_next_phase(work_item)
           db.update_work_item(work_item)
   ```

3. **Phase-Specific Gate Requirements**:
   ```python
   GATE_REQUIREMENTS_BY_PHASE = {
       Phase.D1_DISCOVERY: 'D1_ready',
       Phase.P1_PLAN: 'P1_plan',
       Phase.I1_IMPLEMENTATION: 'I1_build',
       Phase.R1_REVIEW: 'R1_accept',
       Phase.O1_OPERATIONS: 'O1_ops',
       Phase.E1_EVOLUTION: 'E1_eval',
   }
   ```

4. **Type-Specific Phase Sequences**:
   ```python
   # Implement phase skipping for RESEARCH and PLANNING types
   def advance_phase(work_item: WorkItem):
       sequence = PHASE_SEQUENCE_BY_TYPE[work_item.type]
       current_idx = sequence.index(work_item.phase)
       work_item.phase = sequence[current_idx + 1]  # Skip phases not in sequence
   ```

### 5.2 Eliminate Artifact-Based Routing

**Rationale**: Artifacts are useful for **sub-agent communication** (contract v1.0 deliverables), but should NOT be used for **orchestrator routing**.

**Recommended Approach**:
- **Keep artifacts** as sub-agent deliverables (e.g., `ac-writer` produces `acceptance_criteria` artifact)
- **Store artifacts** in `metadata.artifacts` or `document_references` table
- **Route by phase** (database field), not artifact type (ephemeral structure)

**Artifact Usage**:
```python
# Good: Sub-agent produces artifact
ac_writer.produce_artifact('acceptance_criteria', content)

# Good: Store artifact in metadata
work_item.metadata['artifacts']['acceptance_criteria'] = {
    'produced_by': 'ac-writer',
    'created_at': '...',
    'content_ref': 'path/to/ac.md'
}

# Bad: Route by artifact (ephemeral, not persisted)
if artifact.type == 'workitem.ready':
    route_to_planning_orch()
```

### 5.3 Simplify Status Enum

**Proposal**: Reduce status to **operational states** (exceptional conditions), derive normal flow from phase.

**Simplified Status Enum**:
```python
class WorkItemStatus(str, Enum):
    ACTIVE = "active"      # Normal progression (phase-driven)
    BLOCKED = "blocked"    # Exceptional: impediment exists
    CANCELLED = "cancelled" # Exceptional: work abandoned
    ARCHIVED = "archived"  # Terminal: no longer relevant
```

**Status Derivation**:
```python
def get_display_status(work_item: WorkItem) -> str:
    """Derive human-readable status from phase + exceptional state"""
    if work_item.status in [WorkItemStatus.BLOCKED, WorkItemStatus.CANCELLED, WorkItemStatus.ARCHIVED]:
        return work_item.status.value  # Show exceptional state

    # Derive from phase for normal flow
    phase_display_map = {
        Phase.D1_DISCOVERY: "Defining Requirements",
        Phase.P1_PLAN: "Planning Execution",
        Phase.I1_IMPLEMENTATION: "In Progress",
        Phase.R1_REVIEW: "Under Review",
        Phase.O1_OPERATIONS: "Deployed",
        Phase.E1_EVOLUTION: "Completed"
    }
    return phase_display_map.get(work_item.phase, "Unknown")
```

**Benefits**:
- ✅ Eliminates redundancy (phase + status encode same information)
- ✅ Simplifies validation (fewer state combinations)
- ✅ Clearer semantics (phase = work domain, status = exceptional condition)
- ✅ Better UX (display status derived from phase is more meaningful)

### 5.4 Implementation Roadmap

**Phase 1: Foundation** (1-2 days)
1. Add `PHASE_ORCHESTRATOR_MAP` to workflow service
2. Implement `get_next_phase()` with type-specific sequences
3. Update `PhaseGateValidator` to respect type-specific phase skipping
4. Add database constraint for phase NOT NULL (with migration to set phase for existing work items)

**Phase 2: Routing Migration** (2-3 days)
5. Update Master Orchestrator to route by phase (keep status routing as fallback)
6. Update mini-orchestrators to update phase on gate completion
7. Add audit logging for phase transitions
8. Test phase-based routing with all work item types

**Phase 3: Status Simplification** (3-4 days)
9. Add `get_display_status()` helper for UI/CLI
10. Update CLI commands to show derived status
11. Update web dashboard to display phase-derived status
12. Deprecate direct status transitions (except BLOCKED, CANCELLED, ARCHIVED)

**Phase 4: Artifact Cleanup** (2-3 days)
13. Remove artifact-based routing from CLAUDE.md
14. Document artifact usage for sub-agent communication only
15. Add artifact storage in `metadata.artifacts` structure
16. Update developer guide with phase-based routing patterns

**Total Estimated Effort**: 8-12 days (1.5-2 weeks)

---

## 6. Key Insights

### 6.1 Phases Are More Natural for Orchestration

**Why Phases Work Better**:
1. **Semantic alignment**: Phase describes **what work** is being done, orchestrator manages **that work**
2. **Direct mapping**: 6 phases → 6 orchestrators (1:1 relationship)
3. **Gate alignment**: Phase completion = gate pass = orchestrator handoff
4. **Type variation**: Easy to encode (RESEARCH skips I1 phase)
5. **Auditability**: Phase is database field, queryable, indexed

**Why Status Is Problematic**:
1. **Overloaded semantics**: Status encodes both **workflow position** AND **exceptional conditions**
2. **Indirect mapping**: 9 statuses → 6 orchestrators (requires inference)
3. **Type-agnostic**: All work item types share same status values (doesn't capture type variation)
4. **Redundant with phase**: When phase exists, status is derivable

### 6.2 Gates Enforce Phase Completion

**Current State**: Gates are checked during status transitions (e.g., VALIDATED requires D1_ready)

**Proposed State**: Gates are checked during phase transitions (e.g., completing D1 phase requires D1_ready gate)

**Alignment**:
```
Phase Gate = Phase Completion = Orchestrator Handoff
D1_ready gate passes → D1 phase complete → hand off to P1 orchestrator
P1_plan gate passes → P1 phase complete → hand off to I1 orchestrator
I1_build gate passes → I1 phase complete → hand off to R1 orchestrator
R1_accept gate passes → R1 phase complete → hand off to O1 orchestrator
```

**Benefits**:
- ✅ **Natural semantics**: "Complete D1 phase" = "Pass D1 gate" = "Ready for P1"
- ✅ **Clear progression**: Phase advancement is explicit, auditable
- ✅ **Type flexibility**: RESEARCH skips I1 phase = no I1 gate check required

### 6.3 Type-Specific Workflows Encoded in Phase Sequences

**Current Approach**: Type-specific requirements are task-level (FEATURE needs DESIGN+IMPLEMENTATION+TESTING+DOCUMENTATION tasks)

**Proposed Addition**: Type-specific requirements are also phase-level (RESEARCH skips I1, O1, E1 phases)

**Implementation**:
```python
# Task-level requirements (existing)
FEATURE → requires DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks

# Phase-level requirements (new)
RESEARCH → phases: D1, P1, R1 (skip I1, O1, E1)
PLANNING → phases: D1, P1, R1 (skip I1, O1, E1)
```

**Benefits**:
- ✅ **Explicit variation**: Type-specific phase sequences encode workflow differences
- ✅ **Prevents invalid states**: Can't create IMPLEMENTATION task for RESEARCH work item (no I1 phase)
- ✅ **Simpler validation**: Check phase in type's sequence, not task types present

---

## 7. Conclusion

**Current System**: Dual routing (status + phase) with underutilized phase field (91% NULL).

**Root Cause**: Phase was added (migration 0011) but never adopted for routing. Status remains primary routing field.

**Recommended Path**: **Migrate to phase-based routing** with simplified status enum (exceptional states only).

**Alignment with Architecture**: Phase-based routing perfectly matches the three-tier orchestration architecture defined in CLAUDE.md (6 phases → 6 mini-orchestrators).

**Implementation Complexity**: **Moderate** (8-12 days) - requires database migration, routing logic update, CLI/web dashboard changes.

**Risk Level**: **Low** - phase already exists in schema, gate validation already implemented, orchestrators already defined.

**Expected Benefits**:
- 🎯 Simpler routing logic (O(1) phase lookup vs multi-field inference)
- 🎯 Better auditability (phase transitions = database changes)
- 🎯 Type-specific workflows easier to encode (phase sequences by type)
- 🎯 Gate enforcement more natural (phase completion = gate pass)
- 🎯 UI/UX improvement (derived status more meaningful)

**Next Steps**:
1. Review this analysis with team
2. Decide on phase-based routing adoption
3. Create implementation tasks (Phase 1-4 roadmap)
4. Begin Phase 1 foundation work

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Author**: AIPM Workflow Analyzer (via Claude Code)
