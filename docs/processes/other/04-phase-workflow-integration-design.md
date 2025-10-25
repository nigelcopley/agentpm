# Phase-Workflow Integration Design

**Analysis Date**: 2025-10-16
**Purpose**: Design professional phase-based workflow with proper information capture
**Based On**: Code analysis (not documentation assumptions)

---

## 🎯 **Design Goals**

1. **Professional Workflow**: Each phase captures complete information before advancement
2. **Quality Assurance**: Cannot bypass phase gates or skip required information
3. **Clear Semantics**: Phase and status have defined relationship (no nonsensical combinations)
4. **Database-Driven**: All validation from database (no file-based checks)
5. **Agent-Driven**: Mini-orchestrators enforce phase requirements

---

## 📊 **Current State Analysis**

### **What EXISTS Today**

✅ **Phase Enum** (6 phases):
```python
Phase.D1_DISCOVERY       # Requirements gathering
Phase.P1_PLAN            # Planning and design
Phase.I1_IMPLEMENTATION  # Build and code
Phase.R1_REVIEW          # Quality validation
Phase.O1_OPERATIONS      # Deployment
Phase.E1_EVOLUTION       # Continuous improvement
```

✅ **PhaseValidator** (1,125 LOC):
- Type-specific phase sequences (FEATURE: all 6, BUGFIX: 2, RESEARCH: 2)
- Phase requirements registry (NEW)
- Validation logic for phase progression
- Required task types per phase
- Completion criteria with evidence requirements

✅ **Phase Field on work_items**:
```sql
phase TEXT  -- Nullable, no CHECK constraint yet
```

✅ **PHASE_TO_ORCHESTRATOR Routing**:
```python
{
    Phase.D1_DISCOVERY: 'definition-orch',
    Phase.P1_PLAN: 'planning-orch',
    Phase.I1_IMPLEMENTATION: 'implementation-orch',
    Phase.R1_REVIEW: 'review-test-orch',
    Phase.O1_OPERATIONS: 'release-ops-orch',
    Phase.E1_EVOLUTION: 'evolution-orch'
}
```

### **What's MISSING**

❌ **Phase Gate Enforcement**: PhaseValidator not called by WorkflowService
❌ **Phase-Status Coupling**: No validation preventing nonsensical combinations
❌ **Automatic Phase Progression**: Phase must be manually updated
❌ **Information Capture Requirements**: Gates designed but not enforced
❌ **Phase on Tasks**: Only work_items have phase, tasks don't

---

## 🏗️ **Proposed Architecture: Phase-Driven Status**

### **Core Decision: Phase is Source of Truth**

**Principle**: **Phase advancement drives status changes**, not vice versa

**Rationale**:
1. Phase has validation (PhaseValidator with gate requirements)
2. Phase has orchestrators (PHASE_TO_ORCHESTRATOR routing)
3. Phase has information capture (PHASE_REQUIREMENTS registry)
4. Status is simpler (just lifecycle state)

### **Phase-to-Status Mapping** (Deterministic)

```python
PHASE_TO_STATUS = {
    None: WorkItemStatus.DRAFT,                    # No phase = drafting ideas
    Phase.D1_DISCOVERY: WorkItemStatus.DRAFT,      # Gathering requirements
    Phase.P1_PLAN: WorkItemStatus.READY,           # Plan validated, ready to start
    Phase.I1_IMPLEMENTATION: WorkItemStatus.ACTIVE, # Building solution
    Phase.R1_REVIEW: WorkItemStatus.REVIEW,        # Quality validation
    Phase.O1_OPERATIONS: WorkItemStatus.DONE,      # Deployed successfully
    Phase.E1_EVOLUTION: WorkItemStatus.ARCHIVED,   # Historical + learning
}

# Administrative overrides (manual):
# - BLOCKED: Can be set at ANY phase (workflow exception)
# - CANCELLED: Can be set at ANY phase (work abandoned)
```

### **Status Derivation** (Automatic)

```python
# In WorkItem model
@property
def status(self) -> WorkItemStatus:
    """Derive status from phase (with administrative overrides)"""

    # Check for administrative override
    if self._manual_status in {WorkItemStatus.BLOCKED, WorkItemStatus.CANCELLED}:
        return self._manual_status

    # Derive from phase
    return PHASE_TO_STATUS.get(self.phase, WorkItemStatus.DRAFT)

# Or simpler: Keep status as field but validate alignment
def validate_status_phase_alignment(self):
    expected_status = PHASE_TO_STATUS.get(self.phase, WorkItemStatus.DRAFT)
    if self.status not in {expected_status, WorkItemStatus.BLOCKED, WorkItemStatus.CANCELLED}:
        raise ValueError(f"Status {self.status} incompatible with phase {self.phase}")
```

---

## 🔒 **Phase Gate Requirements** (Information Capture)

### **D1 Gate: Discovery → Planning**

**Required Information**:
```yaml
business_context:
  min_length: 50 characters
  format: Prose explaining WHY this matters
  validation: Must answer "business value" and "user value"

acceptance_criteria:
  min_count: 3
  format: GIVEN/WHEN/THEN or validation rules
  validation: Each AC must be testable (objective pass/fail)

risks:
  min_count: 1
  structure:
    - risk: Description of risk
      mitigation: How to address
      severity: LOW|MEDIUM|HIGH|CRITICAL
  validation: Each risk has mitigation strategy

six_w_context:
  required_fields: [who, what, when, where, why, how]
  min_confidence: 0.70
  validation: UnifiedSixW completeness check
```

**Gate Validator**:
```python
class D1GateValidator:
    def validate(self, work_item: WorkItem, db: DatabaseService) -> GateResult:
        errors = []

        # Check business_context
        if not work_item.business_context or len(work_item.business_context) < 50:
            errors.append("business_context required (≥50 characters)")

        # Check acceptance_criteria
        metadata = json.loads(work_item.metadata) if work_item.metadata else {}
        ac_list = metadata.get('acceptance_criteria', [])
        if len(ac_list) < 3:
            errors.append("Need ≥3 acceptance criteria")

        # Check risks
        risks = metadata.get('risks', [])
        if len(risks) < 1:
            errors.append("At least 1 risk must be identified")

        # Check 6W context
        context = context_methods.get_entity_context(db, EntityType.WORK_ITEM, work_item.id)
        if not context or context.confidence_score < 0.70:
            errors.append("6W context confidence must be ≥70%")

        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=self._calculate_confidence(work_item, context)
        )
```

**Mini-Orchestrator Integration**:
```python
# definition-orch (CLAUDE.md.backup-20251018 section 3.1)
def execute(work_item_id):
    # Delegate to sub-agents
    intent = intent-triage(work_item_id)
    problem = problem-framer(work_item_id)
    value = value-articulator(work_item_id)  # Fills business_context
    acs = ac-writer(work_item_id)            # Creates ≥3 ACs
    risks = risk-notary(work_item_id)        # Identifies risks

    # Validate gate
    gate_result = definition-gate-check(work_item_id)

    if gate_result.passed:
        # Advance phase
        wi_methods.update_work_item(db, work_item_id, phase=Phase.P1_PLAN)
        # Status automatically becomes READY (derived from P1_PLAN)
        return ArtifactResult(artifact='workitem.ready')
    else:
        # Return missing requirements for user action
        return ArtifactResult(
            artifact='workitem.incomplete',
            missing=gate_result.missing_requirements
        )
```

---

### **P1 Gate: Planning → Implementation**

**Required Information**:
```yaml
tasks_created:
  min_count: 1
  task_types: Based on work_item.type:
    - FEATURE: [DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION]
    - BUGFIX: [IMPLEMENTATION, TESTING]
    - RESEARCH: [ANALYSIS, DOCUMENTATION]
  validation: All tasks have effort_hours ≤ 4.0 (for IMPLEMENTATION type)

dependencies_mapped:
  validation: All tasks have dependencies identified
  graph: Must be DAG (no circular dependencies)
  critical_path: Longest sequence identified

risk_mitigations:
  validation: Each D1 risk has corresponding mitigation task
  effort: Mitigation tasks must have effort estimates

estimates_complete:
  validation: 100% of tasks have effort_hours
  total_effort: Sum of all task efforts
```

**Gate Validator**:
```python
class P1GateValidator:
    def validate(self, work_item: WorkItem, db: DatabaseService) -> GateResult:
        errors = []

        # Get tasks for this work item
        tasks = task_methods.list_tasks(db, work_item_id=work_item.id)

        # Check minimum tasks exist
        if len(tasks) < 1:
            errors.append("Need ≥1 task")

        # Check required task types based on work item type
        required_types = self._get_required_task_types(work_item.type)
        actual_types = {task.type for task in tasks}
        missing_types = required_types - actual_types

        if missing_types:
            errors.append(f"Missing required task types: {missing_types}")

        # Check all tasks have estimates
        no_estimate = [t for t in tasks if not t.effort_hours]
        if no_estimate:
            errors.append(f"{len(no_estimate)} tasks missing effort_hours")

        # Check time-boxing (IMPLEMENTATION ≤4.0h)
        over_limit = [t for t in tasks
                      if t.type == TaskType.IMPLEMENTATION and t.effort_hours > 4.0]
        if over_limit:
            errors.append(f"{len(over_limit)} IMPLEMENTATION tasks exceed 4.0h limit")

        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=self._calculate_confidence(work_item, tasks)
        )
```

---

### **I1 Gate: Implementation → Review**

**Required Information**:
```yaml
code_complete:
  validation: All IMPLEMENTATION tasks = DONE
  evidence: Task completion timestamps

tests_written:
  validation: All TESTING tasks = DONE
  coverage: Category-specific thresholds met (WI-81 rules)

docs_updated:
  validation: All DOCUMENTATION tasks = DONE
  completeness: API docs + user guides exist

migrations_created:
  validation: If database schema changed, migrations exist
  reversibility: All migrations have downgrade() method
```

**Gate Validator**:
```python
class I1GateValidator:
    def validate(self, work_item: WorkItem, db: DatabaseService) -> GateResult:
        errors = []
        tasks = task_methods.list_tasks(db, work_item_id=work_item.id)

        # Check IMPLEMENTATION tasks complete
        impl_tasks = [t for t in tasks if t.type == TaskType.IMPLEMENTATION]
        incomplete_impl = [t for t in impl_tasks if t.status != TaskStatus.DONE]
        if incomplete_impl:
            errors.append(f"{len(incomplete_impl)} IMPLEMENTATION tasks not DONE")

        # Check TESTING tasks complete
        test_tasks = [t for t in tasks if t.type == TaskType.TESTING]
        incomplete_test = [t for t in test_tasks if t.status != TaskStatus.DONE]
        if incomplete_test:
            errors.append(f"{len(incomplete_test)} TESTING tasks not DONE")

        # Check DOCUMENTATION tasks complete
        doc_tasks = [t for t in tasks if t.type == TaskType.DOCUMENTATION]
        incomplete_doc = [t for t in doc_tasks if t.status != TaskStatus.DONE]
        if incomplete_doc:
            errors.append(f"{len(incomplete_doc)} DOCUMENTATION tasks not DONE")

        # Check test coverage (via rules system)
        coverage_met = self._validate_test_coverage(work_item, db)
        if not coverage_met:
            errors.append("Test coverage does not meet category-specific thresholds")

        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            tasks_summary={'total': len(tasks), 'done': len([t for t in tasks if t.status == TaskStatus.DONE])}
        )
```

---

### **R1 Gate: Review → Operations**

**Required Information**:
```yaml
acceptance_criteria_verified:
  validation: All D1 ACs tested and passing
  evidence: Test results or manual verification

tests_passing:
  validation: 100% test pass rate
  coverage: Meets category-specific thresholds

quality_checks:
  static_analysis: Linters passing (no errors)
  security_scan: No HIGH/CRITICAL vulnerabilities
  code_review: Approved by DIFFERENT agent (no self-approval)
```

**Gate Validator**:
```python
class R1GateValidator:
    def validate(self, work_item: WorkItem, db: DatabaseService) -> GateResult:
        errors = []

        # Check all ACs verified
        metadata = json.loads(work_item.metadata)
        acs = metadata.get('acceptance_criteria', [])
        ac_results = metadata.get('ac_verification_results', {})

        for i, ac in enumerate(acs):
            if not ac_results.get(f'ac_{i}', {}).get('passed'):
                errors.append(f"AC #{i+1} not verified: {ac}")

        # Check test pass rate
        # (This would query test results from tasks or external CI)
        test_pass_rate = self._get_test_pass_rate(work_item, db)
        if test_pass_rate < 1.0:
            errors.append(f"Test pass rate {test_pass_rate:.0%} (need 100%)")

        # Check code review approval
        review_metadata = metadata.get('review', {})
        if not review_metadata.get('approved_by'):
            errors.append("Code review approval required")

        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors
        )
```

---

### **O1 Gate: Operations → Evolution**

**Required Information**:
```yaml
version_bumped:
  validation: Semver version incremented
  changelog: CHANGELOG.md updated

deployed:
  validation: Deployment successful
  health_check: System responding correctly

monitoring_active:
  validation: Alerts configured
  runbook: Operational procedures documented
```

---

### **E1 Gate: Evolution (Continuous)**

**Required Information**:
```yaml
telemetry_analyzed:
  validation: Production metrics reviewed
  insights: Performance/usage patterns identified

improvements_identified:
  validation: Technical debt or enhancements documented
  priority: Improvements ranked by impact

feedback_loop:
  validation: Learnings captured for future D1 phases
  documentation: Lessons learned documented
```

---

## 🔄 **Phase Advancement Workflow**

### **Automatic Phase Progression** (Recommended)

```python
class PhaseProgressionService:
    """
    Manages phase transitions with gate validation.

    Pattern: Gate validation → Phase advancement → Status derivation
    """

    def advance_to_next_phase(
        self,
        work_item_id: int,
        validate_only: bool = False
    ) -> PhaseTransitionResult:
        """
        Advance work item to next phase after validating current gate.

        Process:
        1. Get current phase
        2. Get next phase in type-specific sequence
        3. Validate current phase gate (all requirements met?)
        4. If valid: Advance phase → derive status → emit event
        5. If invalid: Return missing requirements

        Args:
            work_item_id: Work item to advance
            validate_only: If True, validate without advancing

        Returns:
            PhaseTransitionResult with:
            - success: bool
            - new_phase: Phase (if advanced)
            - new_status: WorkItemStatus (derived)
            - missing_requirements: List[str] (if validation failed)
            - confidence: float (gate validation confidence)
        """
        # Load work item
        work_item = wi_methods.get_work_item(self.db, work_item_id)
        if not work_item:
            raise ValueError(f"Work item {work_item_id} not found")

        # Get current and next phase
        validator = PhaseValidator()
        current_phase = work_item.phase
        next_phase = validator.get_next_allowed_phase(work_item)

        if not next_phase:
            # Already at final phase
            return PhaseTransitionResult(
                success=False,
                error="Work item already at final phase"
            )

        # Validate current phase gate (must pass before advancing)
        gate_validator = self._get_gate_validator(current_phase)
        gate_result = gate_validator.validate(work_item, self.db)

        if not gate_result.passed:
            return PhaseTransitionResult(
                success=False,
                missing_requirements=gate_result.missing_requirements,
                confidence=gate_result.confidence
            )

        # Validation passed - advance phase (if not validate_only)
        if validate_only:
            return PhaseTransitionResult(
                success=True,
                message="Gate validation passed (dry-run)"
            )

        # Update phase
        updated = wi_methods.update_work_item(
            self.db,
            work_item_id,
            phase=next_phase
        )

        # Derive and update status
        new_status = PHASE_TO_STATUS[next_phase]
        if updated.status != new_status:
            updated = wi_methods.update_work_item(
                self.db,
                work_item_id,
                status=new_status
            )

        # Emit phase advancement event
        self._emit_phase_advanced_event(work_item, current_phase, next_phase)

        return PhaseTransitionResult(
            success=True,
            new_phase=next_phase,
            new_status=new_status,
            confidence=gate_result.confidence
        )
```

---

## 🎯 **CLI Integration**

### **New Commands**

```bash
# View current phase and gate status
apm work-item phase-status 81
# Output:
# Work Item #81: Implement Value-Based Testing
# Type: bugfix
# Current Phase: I1_IMPLEMENTATION
# Current Status: active (derived from phase)
# Next Phase: R1_REVIEW
# Gate Requirements:
#   ✅ All IMPLEMENTATION tasks complete (3/3)
#   ✅ All TESTING tasks complete (2/2)
#   ⚠️  Test coverage: 87% (need 95% for critical paths)
# Confidence: 85% (YELLOW - adequate but has gaps)

# Validate if ready to advance (dry-run)
apm work-item phase-validate 81
# Output:
# ❌ Cannot advance to R1_REVIEW
# Missing requirements:
#   - Test coverage below threshold (87% vs 95% for critical paths)
# Fix: Add tests to agentpm/core/workflow/service.py (critical path)

# Advance to next phase (delegates to orchestrator)
apm work-item phase-advance 81
# Output:
# 🎯 Routing to implementation-orch (I1 gate validation)
# Validating I1_IMPLEMENTATION gate requirements...
# ✅ All IMPLEMENTATION tasks complete
# ✅ All TESTING tasks complete
# ✅ Test coverage meets thresholds
# ✅ Documentation updated
#
# Advancing phase: I1_IMPLEMENTATION → R1_REVIEW
# Updating status: active → review (derived from R1_REVIEW)
#
# ✅ Work item #81 advanced to R1_REVIEW phase
# Next: Quality review by aipm-quality-validator agent

# Manual phase override (for recovery scenarios)
apm work-item set-phase 81 --phase P1_PLAN --force
# Output:
# ⚠️  Manual phase override (bypasses gate validation)
# Old phase: I1_IMPLEMENTATION
# New phase: P1_PLAN
# Status updated: active → ready (derived from P1_PLAN)
# ⚠️  Use only for recovery - normal workflow should use `phase-advance`
```

---

## 🔗 **Integration with Existing Systems**

### **1. WorkflowService Integration**

```python
# Modify WorkflowService.transition_work_item()
def transition_work_item(
    self,
    work_item_id: int,
    new_status: WorkItemStatus,
    reason: Optional[str] = None
) -> WorkItem:
    work_item = wi_methods.get_work_item(self.db, work_item_id)

    # NEW: Check if status transition requires phase advancement
    if self._requires_phase_advancement(work_item.status, new_status):
        # Validate current phase gate before allowing status change
        phase_service = PhaseProgressionService(self.db)
        validation = phase_service.advance_to_next_phase(
            work_item_id,
            validate_only=True
        )

        if not validation.success:
            raise WorkflowError(
                f"Cannot transition to {new_status.value}: "
                f"Phase gate not passed\n\n"
                f"Missing requirements:\n" +
                "\n".join(f"  - {req}" for req in validation.missing_requirements)
            )

    # Existing validation pipeline continues...
    validation = self._validate_transition(...)
    # ...
```

### **2. Orchestrator Auto-Routing**

```python
# Enhanced session-start.py
def determine_orchestrator(db):
    """Route to orchestrator based on work item phase"""

    # Get highest priority active work item
    work_item = get_active_work_item(db)

    # If phase is NULL, set initial phase based on type
    if work_item.phase is None:
        initial_phase = PhaseValidator.get_initial_phase(work_item.type)
        wi_methods.update_work_item(db, work_item.id, phase=initial_phase)
        work_item.phase = initial_phase

    # Map phase → orchestrator (O(1) lookup)
    orchestrator = PHASE_TO_ORCHESTRATOR[work_item.phase]

    return orchestrator, {
        'id': work_item.id,
        'name': work_item.name,
        'phase': work_item.phase.value,
        'status': work_item.status.value
    }
```

---

## 📊 **Work Item Lifecycle with Phases**

```
┌────────────────────────────────────────────────────────────────┐
│                    Work Item Lifecycle                         │
│              (Phase-Driven Status with Gate Validation)        │
└────────────────────────────────────────────────────────────────┘

IDEA (manual brainstorming)
  ↓
DRAFT (phase=NULL, gathering thoughts)
  ↓
  │ User: apm work-item phase-advance 81
  │ System: Routes to definition-orch
  │ Orchestrator: Runs sub-agents (problem-framer, value-articulator, ac-writer, risk-notary)
  │ Gate: D1 validates (business_context, AC≥3, risks, 6W confidence≥70%)
  ↓
READY (phase=P1_PLAN, plan validated)
  ↓
  │ User: apm work-item phase-advance 81
  │ System: Routes to planning-orch
  │ Orchestrator: Runs sub-agents (decomposer, estimator, dependency-mapper, mitigation-planner)
  │ Gate: P1 validates (tasks created, estimates complete, dependencies mapped)
  ↓
ACTIVE (phase=I1_IMPLEMENTATION, building solution)
  ↓
  │ User: apm work-item phase-advance 81
  │ System: Routes to implementation-orch
  │ Orchestrator: Runs sub-agents (code-implementer, test-implementer, doc-toucher)
  │ Gate: I1 validates (code complete, tests written, docs updated)
  ↓
REVIEW (phase=R1_REVIEW, quality validation)
  ↓
  │ User: apm work-item phase-advance 81
  │ System: Routes to review-test-orch
  │ Orchestrator: Runs sub-agents (static-analyzer, test-runner, ac-verifier, quality-gatekeeper)
  │ Gate: R1 validates (all AC pass, tests green, review approved)
  ↓
DONE (phase=O1_OPERATIONS, deployed)
  ↓
  │ User: apm work-item phase-advance 81
  │ System: Routes to release-ops-orch
  │ Orchestrator: Runs sub-agents (versioner, deploy-orchestrator, health-verifier)
  │ Gate: O1 validates (deployed, health verified, monitoring active)
  ↓
DONE (O1_OPERATIONS ongoing) → E1_EVOLUTION (telemetry-driven improvement)
  ↓
  │ System: Routes to evolution-orch (applies to DONE/O1 work)
  │ Orchestrator: Runs sub-agents (signal-harvester, insight-synthesizer, debt-registrar)
  │ Gate: E1 validates (insights captured, improvements prioritized)
  │ Output: Creates new IDEA or WORK_ITEM (feedback loop)
  ↓
ARCHIVED (phase=None, terminal state)
  │ Historical reference only, no active phase
  ↓
(Cycle repeats for continuous improvement)

Administrative Overrides (any time):
  → BLOCKED (phase unchanged, status=blocked, blocked_reason required)
  → CANCELLED (phase unchanged, status=cancelled, reason required)
```

---

## 🔧 **Implementation Plan**

### **Phase 1: Foundation** (6 hours)

**Task 1.1: Create PhaseProgressionService** (3 hours)
```yaml
File: agentpm/core/workflow/phase_progression_service.py
Methods:
  - advance_to_next_phase(work_item_id, validate_only)
  - validate_current_gate(work_item_id)
  - get_gate_status(work_item_id)
  - get_missing_requirements(work_item_id)

Dependencies:
  - PhaseValidator (existing)
  - Gate validators (new, created in Task 1.2)
  - DatabaseService
  - WorkItem methods

Testing:
  - tests-BAK/core/workflow/test_phase_progression_service.py
  - 20+ test cases covering all phase transitions
```

**Task 1.2: Create Phase Gate Validators** (3 hours)
```yaml
Files:
  - agentpm/core/workflow/phase_gates/d1_gate_validator.py
  - agentpm/core/workflow/phase_gates/p1_gate_validator.py
  - agentpm/core/workflow/phase_gates/i1_gate_validator.py
  - agentpm/core/workflow/phase_gates/r1_gate_validator.py
  - agentpm/core/workflow/phase_gates/o1_gate_validator.py
  - agentpm/core/workflow/phase_gates/e1_gate_validator.py

Each validator:
  - validate(work_item, db) → GateResult
  - Checks phase-specific requirements
  - Returns missing requirements list
  - Calculates confidence score

Testing:
  - tests-BAK/core/workflow/phase_gates/test_d1_gate.py (etc.)
```

### **Phase 2: Integration** (8 hours)

**Task 2.1: Integrate with WorkflowService** (4 hours)
```yaml
File: agentpm/core/workflow/service.py
Changes:
  - Add _validate_phase_gate() method
  - Call phase validation in _validate_transition()
  - Add _validate_phase_status_alignment() method
  - Update transition_work_item() to check phase gates

Testing:
  - tests-BAK/core/workflow/test_phase_gate_integration.py
```

**Task 2.2: Add CLI Commands** (4 hours)
```yaml
Files:
  - agentpm/cli/commands/work_item/phase_status.py
  - agentpm/cli/commands/work_item/phase_validate.py
  - agentpm/cli/commands/work_item/phase_advance.py
  - agentpm/cli/commands/work_item/set_phase.py

Each command:
  - Uses PhaseProgressionService
  - Rich formatted output
  - Error handling with fix suggestions

Testing:
  - tests-BAK/cli/commands/test_work_item_phase_commands.py
```

### **Phase 3: Enhancement** (6 hours)

**Task 3.1: Add phase to tasks** (2 hours + migration)
```yaml
Migration: agentpm/core/database/migrations/files/migration_0024.py
Changes:
  - Add tasks.phase column
  - Populate from work_items.phase
  - Add trigger to keep in sync with work_item
  - Add index on tasks.phase

Model update: agentpm/core/database/models/task.py
Testing: tests-BAK/core/database/test_task_phase_field.py
```

**Task 3.2: Database constraints** (1 hour + migration)
```yaml
Migration: agentpm/core/database/migrations/files/migration_0023.py (combine with event fix)
Changes:
  - Add CHECK constraint on work_items.phase (enum values)
  - Add index on work_items.phase
  - Add composite index on (phase, status)

Testing: Verify constraint enforcement
```

**Task 3.3: Update Web UI** (3 hours)
```yaml
Files:
  - agentpm/web/routes/entities.py (add phase status endpoint)
  - agentpm/web/templates/work-items/detail.html (show phase info)
  - agentpm/web/templates/components/phase_status_badge.html (new component)

Features:
  - Phase progress indicator
  - Gate requirements checklist
  - "Advance Phase" button (delegates to orchestrator)
```

---

## 📋 **Validation Rules**

### **Phase-Status Alignment Rules**

```python
VALID_COMBINATIONS = {
    # Normal workflow progression
    (WorkItemStatus.DRAFT, None),                       # No phase yet
    (WorkItemStatus.DRAFT, Phase.D1_DISCOVERY),         # Discovering
    (WorkItemStatus.READY, Phase.P1_PLAN),              # Planning complete
    (WorkItemStatus.ACTIVE, Phase.I1_IMPLEMENTATION),   # Building
    (WorkItemStatus.REVIEW, Phase.R1_REVIEW),           # Quality check
    (WorkItemStatus.DONE, Phase.O1_OPERATIONS),         # Deployed
    # ARCHIVED has no phase - terminal state
    # E1_EVOLUTION applies to DONE/O1 ongoing work (continuous improvement)

    # Administrative states (override phase)
    (WorkItemStatus.BLOCKED, Phase.D1_DISCOVERY),       # Blocked discovery
    (WorkItemStatus.BLOCKED, Phase.P1_PLAN),            # Blocked planning
    (WorkItemStatus.BLOCKED, Phase.I1_IMPLEMENTATION),  # Blocked implementation
    (WorkItemStatus.BLOCKED, Phase.R1_REVIEW),          # Blocked review
    (WorkItemStatus.CANCELLED, None),                   # Cancelled (any phase)
    # ... all CANCELLED combinations
}

# Any combination not in VALID_COMBINATIONS = FORBIDDEN
```

### **Phase Advancement Triggers**

```python
# Automatic phase advancement on these status changes:
STATUS_TRIGGERS_PHASE_CHECK = {
    WorkItemStatus.DRAFT → WorkItemStatus.READY: "Must pass D1 gate",
    WorkItemStatus.READY → WorkItemStatus.ACTIVE: "Must pass P1 gate",
    WorkItemStatus.ACTIVE → WorkItemStatus.REVIEW: "Must pass I1 gate",
    WorkItemStatus.REVIEW → WorkItemStatus.DONE: "Must pass R1 gate",
    WorkItemStatus.DONE → WorkItemStatus.ARCHIVED: "Must pass O1 gate",
}

# Manual phase advancement:
apm work-item phase-advance <id>
  → PhaseProgressionService.advance_to_next_phase()
  → Validates current gate
  → Advances phase if passed
  → Derives status from new phase
```

---

## 🎯 **Benefits of This Design**

### **Quality Assurance**
✅ **Cannot skip gates**: Every phase advancement validates requirements
✅ **Information captured**: Gates enforce business_context, ACs, risks, estimates, etc.
✅ **Evidence-based**: All decisions backed by validation results
✅ **No guessing**: Clear requirements checklist at each phase

### **Workflow Integrity**
✅ **No desynchronization**: Status derived from phase (single source of truth)
✅ **Clear semantics**: Phase tells workflow stage, status tells lifecycle
✅ **Predictable**: Deterministic mapping (no ambiguity)
✅ **Recoverable**: Manual override for exceptional cases

### **Agent Coordination**
✅ **Automatic routing**: Phase → orchestrator mapping (no manual selection)
✅ **Clear handoffs**: Each orchestrator knows its phase responsibilities
✅ **Validation enforcement**: Orchestrators must pass gates
✅ **Audit trail**: All phase changes logged with events

### **Database Integrity**
✅ **Constraints enforced**: CHECK constraints on phase enum values
✅ **Indexed queries**: Fast filtering by phase (>1000 work items)
✅ **Audit logging**: All transitions tracked in session_events

---

## 🚀 **Rollout Strategy**

### **Week 1: Core Implementation**
- Create PhaseProgressionService
- Create 6 phase gate validators
- Add database constraints and indexes (migration 0023)

### **Week 2: Integration**
- Integrate with WorkflowService
- Add CLI commands
- Update Web UI

### **Week 3: Testing & Documentation**
- Comprehensive test suite (>90% coverage)
- User guide: Phase workflow explained
- Developer guide: Adding new phase gates

### **Week 4: Dogfooding**
- Use on WI-81 (Value-Based Testing Strategy)
- Iterate based on real usage
- Fix edge cases

**Total Effort**: 20 hours (~1 week)

---

**Key Takeaway**: Phase-driven status with gate validation creates professional workflow that **captures complete information** and **prevents quality bypass**.
