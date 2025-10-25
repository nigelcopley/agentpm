# ADR-014: Phase-Status Relationship in Work Item Lifecycle

**Status:** Accepted
**Date:** 2025-10-16
**Deciders:** APM (Agent Project Manager) Architecture Team
**Technical Story:** Define how phase and status fields interact in work item lifecycle management

---

## Context

APM (Agent Project Manager) uses a **phase-driven workflow system** where work items progress through phases (D1_DISCOVERY, P1_PLAN, I1_IMPLEMENTATION, R1_REVIEW, O1_OPERATIONS, E1_EVOLUTION) with validation gates between phases. Work items also have a **status field** (DRAFT, READY, ACTIVE, REVIEW, DONE, ARCHIVED) for lifecycle state management.

### Current State

The system currently has **two independent fields**:

1. **Phase (WorkItemPhase enum)**
   - Represents **what stage of analysis/work** the item is in
   - Values: D1_DISCOVERY, P1_PLAN, I1_IMPLEMENTATION, R1_REVIEW, O1_OPERATIONS, E1_EVOLUTION
   - Has validation logic (PhaseValidator)
   - Has orchestrators (PHASE_TO_ORCHESTRATOR mapping)
   - Has requirements (PHASE_REQUIREMENTS registry)
   - Enforces quality gates before progression

2. **Status (WorkItemStatus enum)**
   - Represents **lifecycle state** of the work item
   - Values: DRAFT, READY, ACTIVE, REVIEW, DONE, ARCHIVED
   - Simpler field, less validation logic
   - Used for filtering and workflow state

### The Problem

**These fields are currently independent with no validation**, leading to nonsensical combinations:

```python
# NONSENSICAL STATES (currently allowed):
WorkItem(phase=D1_DISCOVERY, status=DONE)        # Done but still in discovery?
WorkItem(phase=O1_OPERATIONS, status=DRAFT)      # Operations but draft status?
WorkItem(phase=E1_EVOLUTION, status=READY)       # Evolution but not started?
WorkItem(phase=P1_PLAN, status=ARCHIVED)         # Planning but archived?
```

**This creates issues**:
- **Workflow integrity**: No guarantee of semantic consistency
- **Query confusion**: Status filters may show inappropriate items
- **UI ambiguity**: Users confused by contradictory fields
- **Audit trail gaps**: Can't determine true state from fields alone
- **Business logic errors**: Code must handle nonsensical combinations

### Requirements

1. **Prevent nonsensical combinations**: Phase and status must be semantically aligned
2. **Single source of truth**: One field should drive the other to avoid desynchronization
3. **Clear semantics**: Users should understand what phase + status means
4. **Workflow integrity**: State transitions must maintain consistency
5. **Administrative flexibility**: Allow overrides for blocked/cancelled items
6. **Backward compatibility**: Migration path for existing work items

---

## Decision

We will implement a **Phase-Driven Status Model** where:

1. **Phase is the primary field** driving work item progression
2. **Status is derived from phase** (with validation enforcement)
3. **Phase advancement automatically updates status** (or validates alignment)
4. **Administrative states (BLOCKED, CANCELLED)** can override status independently

### Core Principle

> **Phase progression drives status changes. Status is either derived from phase or administratively set.**

### Phase-Status Alignment Rules

```python
PHASE_STATUS_ALIGNMENT = {
    # Phase -> Valid Status Values
    WorkItemPhase.D1_DISCOVERY: [
        WorkItemStatus.DRAFT,        # Initial discovery, not validated
        WorkItemStatus.READY,        # Discovery complete, ready for planning
    ],
    WorkItemPhase.P1_PLAN: [
        WorkItemStatus.READY,        # Plan validated, ready for implementation
        WorkItemStatus.ACTIVE,       # Planning in progress
    ],
    WorkItemPhase.I1_IMPLEMENTATION: [
        WorkItemStatus.ACTIVE,       # Implementation in progress
        WorkItemStatus.REVIEW,       # Implementation complete, under review
    ],
    WorkItemPhase.R1_REVIEW: [
        WorkItemStatus.REVIEW,       # Under quality review
        WorkItemStatus.DONE,         # Review passed, implementation complete
    ],
    WorkItemPhase.O1_OPERATIONS: [
        WorkItemStatus.DONE,         # Deployed to production
        WorkItemStatus.ARCHIVED,     # Operations complete, archived
    ],
    WorkItemPhase.E1_EVOLUTION: [
        WorkItemStatus.DONE,         # Evolution analysis complete
        WorkItemStatus.ARCHIVED,     # Insights captured, work archived
    ],
}

# Administrative states (override phase-status alignment)
ADMINISTRATIVE_STATUSES = [
    WorkItemStatus.BLOCKED,          # Work blocked, any phase
    WorkItemStatus.CANCELLED,        # Work cancelled, any phase
]
```

### Status Derivation from Phase

```python
def derive_status_from_phase(phase: WorkItemPhase) -> WorkItemStatus:
    """
    Derive the appropriate status when phase changes.

    This provides the "default" status for a given phase.
    Actual status may differ if administratively set.
    """
    PHASE_DEFAULT_STATUS = {
        WorkItemPhase.D1_DISCOVERY: WorkItemStatus.DRAFT,
        WorkItemPhase.P1_PLAN: WorkItemStatus.ACTIVE,
        WorkItemPhase.I1_IMPLEMENTATION: WorkItemStatus.ACTIVE,
        WorkItemPhase.R1_REVIEW: WorkItemStatus.REVIEW,
        WorkItemPhase.O1_OPERATIONS: WorkItemStatus.DONE,
        WorkItemPhase.E1_EVOLUTION: WorkItemStatus.DONE,
    }
    return PHASE_DEFAULT_STATUS[phase]
```

### Validation Logic

```python
def validate_phase_status_alignment(
    phase: WorkItemPhase,
    status: WorkItemStatus
) -> ValidationResult:
    """
    Validate that status is semantically aligned with phase.

    Returns:
        ValidationResult with is_valid=True if aligned, else error message
    """
    # Administrative statuses always valid
    if status in ADMINISTRATIVE_STATUSES:
        return ValidationResult(is_valid=True)

    # Check phase-status alignment
    valid_statuses = PHASE_STATUS_ALIGNMENT.get(phase, [])
    if status not in valid_statuses:
        return ValidationResult(
            is_valid=False,
            error=f"Status {status} invalid for phase {phase}. "
                  f"Valid statuses: {', '.join(s.value for s in valid_statuses)}"
        )

    return ValidationResult(is_valid=True)
```

### Phase Progression with Status Update

```python
def advance_phase(
    work_item: WorkItem,
    target_phase: WorkItemPhase,
    force_status: Optional[WorkItemStatus] = None
) -> WorkItem:
    """
    Advance work item to target phase with automatic status update.

    Args:
        work_item: Work item to advance
        target_phase: Target phase to advance to
        force_status: Optional status override (must be valid for phase)

    Returns:
        Updated work item with new phase and aligned status
    """
    # Validate phase progression (existing PhaseValidator logic)
    validation = PhaseValidator.validate_progression(
        work_item.phase, target_phase
    )
    if not validation.is_valid:
        raise InvalidPhaseTransition(validation.error)

    # Determine new status
    if force_status:
        # Validate forced status aligns with target phase
        status_validation = validate_phase_status_alignment(
            target_phase, force_status
        )
        if not status_validation.is_valid:
            raise InvalidStatusForPhase(status_validation.error)
        new_status = force_status
    else:
        # Derive status from phase
        new_status = derive_status_from_phase(target_phase)

    # Update work item
    work_item.phase = target_phase
    work_item.status = new_status
    work_item.updated_at = datetime.utcnow()

    # Log phase transition
    log_phase_transition(work_item, target_phase, new_status)

    return work_item
```

### Administrative Status Changes

```python
def set_administrative_status(
    work_item: WorkItem,
    status: WorkItemStatus,
    reason: str
) -> WorkItem:
    """
    Set administrative status (BLOCKED, CANCELLED) regardless of phase.

    Args:
        work_item: Work item to update
        status: Administrative status to set
        reason: Required reason for administrative status

    Returns:
        Updated work item with administrative status
    """
    if status not in ADMINISTRATIVE_STATUSES:
        raise ValueError(
            f"Status {status} is not administrative. "
            f"Use advance_phase() for phase-driven status changes."
        )

    if not reason:
        raise ValueError("Reason required for administrative status change")

    # Update status (phase remains unchanged)
    work_item.status = status
    work_item.updated_at = datetime.utcnow()

    # Log administrative status change
    log_administrative_status(work_item, status, reason)

    return work_item
```

---

## Rationale

### Why Phase-Driven (Not Status-Driven)?

We chose **phase as the primary driver** because:

1. **Phase has richer validation logic**
   - PhaseValidator enforces gate requirements
   - PHASE_REQUIREMENTS registry defines expectations
   - Phase gates ensure quality and completeness

2. **Phase has orchestration infrastructure**
   - PHASE_TO_ORCHESTRATOR mapping routes work
   - Each phase has specialized orchestrator
   - Orchestrators drive mini-agents and sub-agents

3. **Phase represents work state more precisely**
   - Discovery → Planning → Implementation → Review → Operations → Evolution
   - Clear progression with validation checkpoints
   - Each phase has specific deliverables and gates

4. **Status is simpler and less specific**
   - DRAFT → READY → ACTIVE → REVIEW → DONE → ARCHIVED
   - Lifecycle states, not work stages
   - Less validation logic, more UI-focused

5. **Architecture alignment**
   - Current system already phase-centric
   - PhaseProgressionService manages advancement
   - Phase gates are primary quality control

### Why Not Independent Fields?

**Independent fields create dual tracking burden**:
- Must maintain synchronization manually
- No guarantee of semantic consistency
- Ambiguous state when fields conflict
- Harder to query and reason about state

### Why Allow Administrative Overrides?

**Real-world workflow needs**:
- Work gets **blocked** (dependencies, decisions, resources)
- Work gets **cancelled** (priorities change, requirements invalidated)
- These states cross-cut phases (can be blocked in any phase)

**Administrative statuses**:
- Are explicit (require reason)
- Are tracked (audit log of status changes)
- Don't affect phase progression logic
- Can be cleared to resume normal workflow

---

## Consequences

### Positive Consequences

1. **No Desynchronization**
   - Single source of truth (phase) drives status
   - Automatic alignment prevents contradictions
   - Clear semantics for each state combination

2. **Simplified State Management**
   - Fewer valid states (phase + aligned status)
   - Easier to reason about workflow state
   - Less error-prone state transitions

3. **Better Validation**
   - Enforce phase-status alignment in database layer
   - Catch invalid combinations at write time
   - Prevent nonsensical states in queries

4. **Clearer Workflow Semantics**
   - Phase progression is primary workflow
   - Status reflects phase appropriately
   - Administrative states are explicit exceptions

5. **Improved Query Logic**
   - Status filters return semantically correct items
   - Phase queries have predictable status values
   - Clearer UI state representation

6. **Architectural Consistency**
   - Aligns with existing phase-centric design
   - Leverages PhaseValidator and PhaseProgressionService
   - Works with PHASE_TO_ORCHESTRATOR infrastructure

### Negative Consequences

1. **Status Becomes Derived (Less Flexible)**
   - Can't set arbitrary status values
   - Must follow phase-status alignment rules
   - Some use cases may require workarounds

2. **Migration Complexity**
   - Existing work items may have misaligned phase/status
   - Need migration to fix nonsensical combinations
   - Backward compatibility concerns

3. **Learning Curve**
   - Users must understand phase-status relationship
   - Administrative statuses are special case
   - More complex than fully independent fields

### Mitigation Strategies

1. **Clear Documentation**
   - Document phase-status alignment rules
   - Explain administrative statuses clearly
   - Provide migration guide for existing items

2. **Validation Messaging**
   - Clear error messages for invalid combinations
   - Suggest valid statuses when phase changes
   - Explain administrative status purpose

3. **Migration Tooling**
   - Automated migration for existing work items
   - Report on items with misaligned states
   - Provide manual override for edge cases

4. **UI Affordances**
   - Show valid statuses for current phase
   - Highlight administrative statuses differently
   - Provide tooltips explaining constraints

---

## Implementation

### Database Schema Changes

```python
# Add validation constraint to work_items table
class WorkItem(Base):
    __tablename__ = "work_items"

    phase = Column(Enum(WorkItemPhase), nullable=False)
    status = Column(Enum(WorkItemStatus), nullable=False)

    @validates('status')
    def validate_status_alignment(self, key, status):
        """Validate status aligns with phase"""
        if hasattr(self, 'phase') and self.phase:
            result = validate_phase_status_alignment(self.phase, status)
            if not result.is_valid:
                raise ValueError(result.error)
        return status
```

### WorkflowService Integration

```python
class WorkflowService:
    """Enhanced workflow service with phase-status validation"""

    def advance_work_item_phase(
        self,
        work_item_id: int,
        target_phase: WorkItemPhase,
        force_status: Optional[WorkItemStatus] = None
    ) -> WorkItem:
        """
        Advance work item to target phase with aligned status.

        Enforces phase-status alignment automatically.
        """
        work_item = self.db.get_work_item(work_item_id)
        return advance_phase(work_item, target_phase, force_status)

    def set_work_item_blocked(
        self,
        work_item_id: int,
        reason: str
    ) -> WorkItem:
        """Set work item to BLOCKED status (administrative)"""
        work_item = self.db.get_work_item(work_item_id)
        return set_administrative_status(
            work_item, WorkItemStatus.BLOCKED, reason
        )

    def set_work_item_cancelled(
        self,
        work_item_id: int,
        reason: str
    ) -> WorkItem:
        """Set work item to CANCELLED status (administrative)"""
        work_item = self.db.get_work_item(work_item_id)
        return set_administrative_status(
            work_item, WorkItemStatus.CANCELLED, reason
        )
```

### CLI Commands

```bash
# Phase advancement (automatic status update)
apm work-item advance <id> --phase P1_PLAN
# → Sets status=ACTIVE automatically

# Force specific status during phase change
apm work-item advance <id> --phase R1_REVIEW --status REVIEW
# → Validates status=REVIEW is valid for phase=R1_REVIEW

# Administrative status (any phase)
apm work-item block <id> --reason "Waiting on architecture decision"
# → Sets status=BLOCKED, preserves phase

apm work-item cancel <id> --reason "Requirements invalidated"
# → Sets status=CANCELLED, preserves phase

# Resume from administrative status
apm work-item resume <id>
# → Restores status to phase-appropriate value
```

### Migration Script

```python
def migrate_phase_status_alignment():
    """
    Migrate existing work items to aligned phase-status combinations.

    Strategy:
    1. Identify misaligned items
    2. Derive correct status from phase
    3. Update status (preserve phase)
    4. Log migration actions
    """
    db = DatabaseService()
    work_items = db.get_all_work_items()

    migrated_count = 0
    for item in work_items:
        # Skip administrative statuses
        if item.status in ADMINISTRATIVE_STATUSES:
            continue

        # Check alignment
        validation = validate_phase_status_alignment(item.phase, item.status)
        if not validation.is_valid:
            # Derive correct status from phase
            correct_status = derive_status_from_phase(item.phase)

            # Log migration
            logger.info(
                f"Migrating work_item {item.id}: "
                f"phase={item.phase}, status={item.status} → {correct_status}"
            )

            # Update status
            item.status = correct_status
            item.updated_at = datetime.utcnow()
            db.session.commit()

            migrated_count += 1

    logger.info(f"Migrated {migrated_count} work items to aligned phase-status")
```

---

## Alternatives Considered

### Alternative 1: Status-Driven Phase

**Approach:** Status is primary, phase is derived from status

**Pros:**
- Simpler mental model (single lifecycle state)
- Familiar workflow (draft → active → done)

**Cons:**
- Status lacks validation infrastructure
- No orchestrators for status
- Loses phase-specific gates and requirements
- Doesn't align with current architecture

**Rejected because:** Phase has richer validation and orchestration infrastructure

### Alternative 2: Independent with Guards

**Approach:** Keep fields independent, add validation guards to prevent nonsensical combinations

**Pros:**
- Maximum flexibility
- Can handle complex edge cases
- No forced derivation

**Cons:**
- Dual tracking burden (maintain both fields)
- No single source of truth
- More complex validation logic
- Prone to desynchronization bugs
- Harder to reason about state

**Rejected because:** Dual tracking creates more problems than it solves

### Alternative 3: Single Unified State

**Approach:** Merge phase and status into single unified state enum

**Pros:**
- Single source of truth
- No alignment issues
- Simpler state management

**Cons:**
- State explosion (6 phases × 6 statuses = 36 states)
- Less composable (can't query by phase or status separately)
- Harder to extend (adding phase or status requires all combinations)
- Breaks existing API contracts

**Rejected because:** Too rigid, loses composability benefits

---

## Quality Gates Integration

### Phase Gate Validation

Phase gates (D1, P1, I1, R1, O1, E1) remain unchanged:
- Gates validate **phase progression** (existing PhaseValidator logic)
- Status is **automatically aligned** when phase advances
- Administrative statuses **don't bypass gates** (phase must still meet requirements)

### Status-Specific Validations

```python
def validate_status_transition(
    work_item: WorkItem,
    target_status: WorkItemStatus
) -> ValidationResult:
    """
    Validate status transition is valid for current phase.

    Example: Can't set status=DONE if phase=D1_DISCOVERY
    """
    # Administrative statuses always valid
    if target_status in ADMINISTRATIVE_STATUSES:
        return ValidationResult(is_valid=True)

    # Check phase-status alignment
    return validate_phase_status_alignment(work_item.phase, target_status)
```

---

## Monitoring and Metrics

### State Consistency Metrics

```python
def calculate_phase_status_consistency():
    """
    Calculate percentage of work items with aligned phase-status.

    Target: 100% (after migration and validation enforcement)
    """
    db = DatabaseService()
    work_items = db.get_all_work_items()

    total = len(work_items)
    aligned = 0

    for item in work_items:
        # Administrative statuses considered aligned
        if item.status in ADMINISTRATIVE_STATUSES:
            aligned += 1
            continue

        # Check phase-status alignment
        validation = validate_phase_status_alignment(item.phase, item.status)
        if validation.is_valid:
            aligned += 1

    consistency_rate = (aligned / total) * 100 if total > 0 else 100
    return consistency_rate
```

### Workflow Health Metrics

- **Phase Progression Rate**: Work items advancing through phases
- **Administrative Status Rate**: Percentage blocked/cancelled
- **Average Time per Phase**: Duration in each phase
- **Status Alignment Rate**: Consistency of phase-status alignment (target: 100%)

---

## Related Documents

- **ADR-013**: Agent-Driven Impact Analysis Workflow (phase-based workflow system)
- **Phase Validator**: `agentpm/core/workflow/phase_validator.py`
- **Workflow Service**: `agentpm/core/workflow/service.py`
- **Phase Requirements**: `agentpm/core/workflow/work_item_requirements.py`
- **State Machine**: `agentpm/core/workflow/state_machine.py`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-16 | Phase-driven status model | Phase has richer validation, orchestration, and gate infrastructure |
| 2025-10-16 | Allow administrative statuses (BLOCKED, CANCELLED) | Real-world workflow needs cross-cutting states |
| 2025-10-16 | Automatic status derivation from phase | Prevents desynchronization, single source of truth |
| 2025-10-16 | Validate phase-status alignment at database layer | Catch invalid combinations early |

---

## Implementation Timeline

### Week 1: Core Implementation (COMPLETED)
- ✅ Define PHASE_STATUS_ALIGNMENT mapping
- ✅ Implement validate_phase_status_alignment()
- ✅ Implement derive_status_from_phase()
- ✅ Implement advance_phase() with status update
- ✅ Implement administrative status functions

### Week 2: Integration
- ⏳ Integrate with WorkflowService
- ⏳ Add database validation constraints
- ⏳ Implement CLI commands
- ⏳ Create migration script

### Week 3: Testing & Documentation
- ⏳ Unit tests for alignment validation
- ⏳ Integration tests for phase advancement
- ⏳ Migration testing on dev database
- ⏳ User documentation and guides

### Week 4: Deployment
- ⏳ Run migration on production database
- ⏳ Monitor state consistency metrics
- ⏳ Address edge cases discovered
- ⏳ Update operational runbooks

---

## Success Criteria

1. **100% Phase-Status Alignment**: All work items have semantically consistent phase-status combinations
2. **No Nonsensical States**: Validation prevents invalid combinations at write time
3. **Smooth Migration**: Existing work items migrated without data loss
4. **Clear User Experience**: Users understand phase-status relationship
5. **Maintained Workflow Velocity**: Phase-status alignment doesn't slow development

---

**Status:** Accepted
**Implementation Status:** Core implementation complete (Week 1), integration in progress
**Next Steps:**
1. Complete WorkflowService integration
2. Add database constraints
3. Implement CLI commands
4. Run migration on production database

**Owner:** APM (Agent Project Manager) Workflow Team
**Reviewers:** Architecture Team, Database Team
**Last Updated:** 2025-10-16

---

*This ADR establishes phase as the primary driver of work item state, with status automatically aligned to ensure workflow integrity and prevent nonsensical state combinations.*
