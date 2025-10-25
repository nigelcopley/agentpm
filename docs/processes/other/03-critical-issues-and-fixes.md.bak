# Critical Issues and Recommended Fixes

**Analysis Date**: 2025-10-16
**Priority**: Issues ranked by severity and impact
**Confidence**: HIGH (code-based analysis)

---

## 🚨 **HIGH PRIORITY** (Must Fix Before Production)

### **Issue #1: Phase-Status Desynchronization Risk**

**Severity**: 🔴 HIGH
**Impact**: Workflow integrity
**Effort**: 3 hours

**Problem**:
Phase (D1/P1/I1/R1/O1/E1) and Status (draft/ready/active/review/done/archived) are completely independent fields with no validation linking them.

**Evidence**:
```python
# Permitted but nonsensical:
work_item = WorkItem(
    status=WorkItemStatus.DONE,      # Completed
    phase=Phase.D1_DISCOVERY         # Still discovering?
)
# Database allows this, no CHECK constraint prevents it
```

**Root Cause**:
- `work_items.phase` has no CHECK constraint referencing status
- `WorkflowService.transition_work_item()` doesn't validate phase alignment
- `PhaseValidator` only checks phase sequence, not status compatibility

**Impact**:
- Confusing semantics: "Is this work done or still discovering?"
- Dashboard ambiguity: Which field shows truth?
- Agent handoff confusion: Which phase should agent work in?
- Analytics broken: Cannot reliably track workflow progression

**Recommended Fix**:

```python
# Add to WorkflowService.transition_work_item()
def _validate_phase_status_alignment(
    self,
    work_item: WorkItem,
    new_status: WorkItemStatus
) -> None:
    """Prevent nonsensical phase-status combinations"""

    if not work_item.phase:
        return  # NULL phase is always valid

    # Define forbidden combinations
    FORBIDDEN_COMBINATIONS = {
        (WorkItemStatus.DONE, Phase.D1_DISCOVERY),
        (WorkItemStatus.DONE, Phase.P1_PLAN),
        (WorkItemStatus.ARCHIVED, Phase.D1_DISCOVERY),
        (WorkItemStatus.ARCHIVED, Phase.P1_PLAN),
        (WorkItemStatus.ARCHIVED, Phase.I1_IMPLEMENTATION),
        (WorkItemStatus.DRAFT, Phase.O1_OPERATIONS),
        (WorkItemStatus.DRAFT, Phase.E1_EVOLUTION),
    }

    if (new_status, work_item.phase) in FORBIDDEN_COMBINATIONS:
        raise WorkflowError(
            f"Invalid state-phase combination: {new_status.value} + {work_item.phase.value}\n\n"
            f"Fix: Advance phase before changing status, or reset phase to NULL"
        )
```

**Files to Change**:
- `agentpm/core/workflow/service.py:112-197` (add validation call)
- Add tests: `tests-BAK/core/workflow/test_phase_status_alignment.py`

---

### **Issue #2: Event Type Schema Mismatch**

**Severity**: 🔴 HIGH
**Impact**: Data integrity, analytics capability
**Effort**: 1 hour

**Problem**:
Pydantic `Event` model defines 40+ event types, but database CHECK constraint only allows 9 types. EventAdapter performs **lossy mapping**.

**Evidence**:
```python
# Pydantic model (core/events/models.py)
class EventType(str, Enum):
    # Workflow events (12 types)
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    # ... 37 more types

# Database schema (migration_0022.py)
event_type TEXT CHECK(event_type IN (
    'workflow_transition',  # Generic!
    'agent_action',
    'gate_execution',
    # ... only 9 types total
))

# EventAdapter (database/adapters/event_adapter.py)
def to_db(event):
    # Lossy mapping: 40 types → 9
    if event.event_type in [TASK_STARTED, TASK_COMPLETED, ...]:
        return 'workflow_transition'  # Lost specificity!
```

**Impact**:
- Cannot query for specific event types (all workflow events become "workflow_transition")
- Analytics limited (cannot distinguish TASK_STARTED from WORK_ITEM_CREATED)
- Event data stored in JSON but type is generic
- Historical data ambiguous

**Recommended Fix**:

```python
# Migration 0023: Expand event_type constraint
def upgrade(conn):
    # Create new table with ALL event types
    conn.execute("""
        CREATE TABLE session_events_new (
            id INTEGER PRIMARY KEY,
            event_type TEXT CHECK(event_type IN (
                -- Workflow (12 types)
                'task_started', 'task_completed', 'task_blocked',
                'work_item_started', 'work_item_done',
                -- Tool usage (10 types)
                'tool_read', 'tool_write', 'tool_edit', 'tool_bash',
                -- Decision (4 types)
                'decision_made', 'decision_reversed',
                -- Reasoning (4 types)
                'hypothesis_formed', 'hypothesis_validated',
                -- Error (6 types)
                'error_occurred', 'error_resolved',
                -- Session (4 types)
                'session_started', 'session_ended'
                -- ... all 40+ types
            )),
            -- ... other columns
        )
    """)

    # Copy data (old generic types preserved)
    conn.execute("INSERT INTO session_events_new SELECT * FROM session_events")

    # Swap tables
    conn.execute("DROP TABLE session_events")
    conn.execute("ALTER TABLE session_events_new RENAME TO session_events")
```

**Files to Change**:
- Create: `agentpm/core/database/migrations/files/migration_0023.py`
- Update: `agentpm/core/database/adapters/event_adapter.py` (remove lossy mapping)

---

### **Issue #3: EventBus Lifecycle Leak**

**Severity**: 🔴 HIGH
**Impact**: Memory leak potential
**Effort**: 2 hours

**Problem**:
New `EventBus` instance created for every state transition, each spawning a daemon worker thread with no cleanup.

**Evidence**:
```python
# WorkflowService._emit_workflow_event() line 1087-1175
def _emit_workflow_event(self, ...):
    event_bus = EventBus(self.db)  # NEW INSTANCE!
    event_bus.emit(event)
    # No shutdown call
    # Thread continues running
```

**Impact**:
- Thread accumulation over time
- Memory leak (1 thread per transition)
- Resource exhaustion (OS thread limit ~2000-4000)
- In typical session: 50-100 transitions = 50-100 threads

**Recommended Fix**:

**Option A: Singleton Pattern** (Recommended)
```python
# core/sessions/event_bus.py
class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_service):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(db_service)
            return cls._instance

    def _initialize(self, db_service):
        if hasattr(self, '_initialized'):
            return
        self.db = db_service
        self._queue = queue.Queue(maxsize=1000)
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._worker_thread.start()
        self._initialized = True
```

**Option B: Thread Pool** (Alternative)
```python
# Use existing worker thread, just emit to queue
class EventBus:
    _queue = queue.Queue(maxsize=1000)  # Class-level
    _worker_started = False

    def __init__(self, db_service):
        self.db = db_service
        self._ensure_worker_started()

    def _ensure_worker_started(self):
        if not EventBus._worker_started:
            threading.Thread(target=self._process_queue, daemon=True).start()
            EventBus._worker_started = True
```

**Files to Change**:
- `agentpm/core/sessions/event_bus.py:30-120` (add singleton or pool)
- `agentpm/core/workflow/service.py:1167` (use singleton)
- Add tests: `tests-BAK/core/sessions/test_event_bus_lifecycle.py`

---

### **Issue #4: Phase Gate Validation Not Enforced**

**Severity**: 🔴 HIGH
**Impact**: Quality gates can be bypassed
**Effort**: 4 hours

**Problem**:
`PhaseValidator` exists with comprehensive phase gate requirements, but `WorkflowService` doesn't call it before status transitions.

**Evidence**:
```python
# PhaseValidator EXISTS with requirements:
validator = PhaseValidator()
requirements = validator.get_phase_requirements(
    Phase.I1_IMPLEMENTATION,
    WorkItemType.FEATURE
)
# Returns: required_tasks=[IMPLEMENTATION, TESTING, DOCUMENTATION]
#          completion_criteria=[code_complete, tests_passing, docs_updated]

# But WorkflowService NEVER CALLS IT:
def transition_work_item(self, work_item_id, new_status):
    validation = self._validate_transition(...)  # State machine only
    # [MISSING] phase_validation = PhaseGateValidator.validate(work_item, new_status)
    if not validation.valid:
        raise WorkflowError(...)
```

**Impact**:
- Can transition to DONE without completing I1_IMPLEMENTATION phase
- Can skip required tasks (DESIGN, IMPLEMENTATION, TESTING for FEATURE)
- Phase requirements system unused (comprehensive code, zero enforcement)
- Quality gates designed but not activated

**Recommended Fix**:

```python
# Add to WorkflowService._validate_transition()
def _validate_transition(
    self,
    entity_type: EntityType,
    entity_id: int,
    current_status: Any,
    new_status: Any,
    reason: Optional[str] = None,
    entity: Optional[Any] = None
) -> ValidationResult:
    # ... existing validation steps 1-4 ...

    # NEW: Step 5 - Phase gate validation (for work items only)
    if entity_type == EntityType.WORK_ITEM and entity and entity.phase:
        # Check if phase gate passed before status advancement
        phase_result = PhaseGateValidator.validate_phase_gates(
            entity,
            new_status,
            self.db
        )
        if not phase_result.valid:
            return ValidationResult(
                valid=False,
                reason=f"Phase gate not passed: {phase_result.error_message}"
            )

    # ... existing validation steps 5-6 (now 6-7) ...
```

**Files to Change**:
- `agentpm/core/workflow/service.py:388-487` (add phase gate validation)
- `agentpm/core/workflow/validators.py:148-156` (already has PhaseGateValidator)
- Add tests: `tests-BAK/core/workflow/test_phase_gate_enforcement.py`

---

## 🟡 **MEDIUM PRIORITY** (Address Next Week)

### **Issue #5: Tasks Have No Phase Field**

**Severity**: 🟡 MEDIUM
**Impact**: Query performance, data model clarity
**Effort**: 2 hours + migration

**Problem**:
Only `WorkItem` has `phase` field. Tasks must query parent work item to determine phase.

**Evidence**:
```python
# work_items table
phase TEXT  -- EXISTS

# tasks table
# [NO PHASE FIELD]

# To get task phase:
task = task_methods.get_task(db, 355)
work_item = wi_methods.get_work_item(db, task.work_item_id)  # Extra query!
task_phase = work_item.phase
```

**Impact**:
- Cannot filter tasks by phase without JOIN
- Slower queries: `SELECT * FROM tasks WHERE phase='I1_implementation'` (impossible)
- Must always query work item to get phase context
- No database index on task phase (because field doesn't exist)

**Recommended Fix**:

```python
# Migration 0024: Add phase to tasks
def upgrade(conn):
    # Add phase column
    conn.execute("ALTER TABLE tasks ADD COLUMN phase TEXT")

    # Populate from parent work items
    conn.execute("""
        UPDATE tasks
        SET phase = (
            SELECT work_items.phase
            FROM work_items
            WHERE work_items.id = tasks.work_item_id
        )
    """)

    # Add foreign key constraint (enforce phase belongs to work item)
    conn.execute("""
        CREATE TRIGGER validate_task_phase
        BEFORE INSERT ON tasks
        BEGIN
            SELECT CASE
                WHEN NEW.phase IS NOT NULL AND (
                    SELECT phase FROM work_items WHERE id = NEW.work_item_id
                ) != NEW.phase
                THEN RAISE(ABORT, 'Task phase must match work item phase')
            END;
        END
    """)

    # Add index
    conn.execute("CREATE INDEX idx_tasks_phase ON tasks(phase)")
```

**Files to Change**:
- Create: `agentpm/core/database/migrations/files/migration_0024.py`
- Update: `agentpm/core/database/models/task.py:65` (add `phase: Optional[Phase]`)
- Update: `agentpm/core/database/adapters/task_adapter.py` (include phase in conversion)

---

### **Issue #6: Plugin Facts Not Stored in Database**

**Severity**: 🟡 MEDIUM
**Impact**: Context assembly performance, data persistence
**Effort**: 3 hours

**Problem**:
`PluginOrchestrator.extract_project_facts()` generates rich technical intelligence but doesn't persist it to database. Facts are regenerated each session.

**Evidence**:
```python
# Plugin extracts facts
facts = plugin.extract_project_facts(project_path)
# Returns: {
#   'python_version': '3.11',
#   'dependencies': {'django': '4.2', ...},
#   'package_manager': 'poetry',
#   'testing_framework': 'pytest'
# }

# But ContextAssemblyService._load_plugin_facts() returns empty
def _load_plugin_facts(self, project, project_ctx):
    # Try cached (doesn't exist)
    if project_ctx and project_ctx.confidence_factors:
        cached = project_ctx.confidence_factors.get('plugin_facts')
        if cached:
            return cached

    # No fallback to fresh detection
    return {}  # ← Always returns empty!
```

**Impact**:
- Context assembly missing 25% of confidence score (plugin facts component)
- Facts regenerated unnecessarily (slow)
- No historical tracking of technology evolution
- Agent context incomplete

**Recommended Fix**:

```python
# 1. Store facts during plugin enrichment
def enrich_context(self, project_path, detection):
    for plugin in self.load_plugins_for(detection):
        facts = plugin.extract_project_facts(project_path)

        # NEW: Store in database
        context_methods.store_context(
            self.db,
            entity_type=EntityType.PROJECT,
            entity_id=project.id,
            confidence_factors={
                'plugin_facts': {plugin.plugin_id: facts}
            }
        )

# 2. Update context assembly to load from database
def _load_plugin_facts(self, project, project_ctx):
    # Try database first
    if project_ctx and project_ctx.confidence_factors:
        return project_ctx.confidence_factors.get('plugin_facts', {})

    # Fallback to fresh detection (for first time)
    detection = DetectionService(self.project_path).detect()
    enrichment = PluginOrchestrator(self.db).enrich_context(self.project_path, detection)

    # Return newly generated facts (now in database)
    return enrichment.plugin_facts
```

**Files to Change**:
- `agentpm/core/plugins/orchestrator.py:200-250` (add database write)
- `agentpm/core/context/assembly_service.py:450-470` (add fallback to detection)
- Add tests: `tests-BAK/core/plugins/test_facts_persistence.py`

---

### **Issue #7: Agent SOP Loaded from Files** (Not Database)

**Severity**: 🟡 MEDIUM
**Impact**: Database-first principle violation
**Effort**: 2 hours

**Problem**:
`SOPInjector` reads agent SOPs from `.claude/agents/*.md` files instead of `agents.sop_content` column.

**Evidence**:
```python
# Database has SOP content
agent = agent_methods.get_agent_by_role(db, project_id, 'database-developer')
# agent.sop_content = "# Database Developer\n\n## Role\n..." (FULL SOP)

# But SOPInjector reads from file
def load_sop(self, agent_role):
    sop_path = self.project_path / '.claude' / 'agents' / f'{agent_role}.md'
    if sop_path.exists():
        return sop_path.read_text()  # ← Should query database!
```

**Impact**:
- Filesystem dependency (not pure database)
- Dual source of truth (database + files can differ)
- Cannot update SOP via database without regenerating file
- Staleness detection unused (agents.generated_at not checked)

**Recommended Fix**:

```python
# Update SOPInjector.load_sop()
def load_sop(self, project_id, agent_role, db):
    """Load agent SOP from database, fallback to file"""

    # Try database first (source of truth)
    try:
        agent = agent_methods.get_agent_by_role(db, project_id, agent_role)
        if agent and agent.sop_content:
            return agent.sop_content
    except Exception:
        pass  # Fallback to file

    # Fallback: Read from file (backward compatibility)
    sop_path = self.project_path / '.claude' / 'agents' / f'{agent_role}.md'
    if sop_path.exists():
        return sop_path.read_text()

    return None
```

**Files to Change**:
- `agentpm/core/context/sop_injector.py:80-120` (add database query)
- Update signature to accept `db` parameter
- Add tests: `tests-BAK/core/context/test_sop_database_loading.py`

---

### **Issue #8: No Index on work_items.phase**

**Severity**: 🟡 MEDIUM
**Impact**: Query performance at scale
**Effort**: 30 minutes

**Problem**:
`work_items.phase` column has no index. Queries filtering by phase will be slow at scale (>1000 work items).

**Evidence**:
```sql
-- Current schema (migration_0022.py)
CREATE TABLE work_items (
    ...
    phase TEXT
);

-- No index:
-- CREATE INDEX idx_work_items_phase ON work_items(phase);  ← MISSING
```

**Impact**:
- Dashboard filtering by phase: O(n) scan vs O(log n) index lookup
- Orchestrator routing query slow: `SELECT * FROM work_items WHERE phase='I1_implementation'`
- No performance issue now (database empty) but will degrade at scale

**Recommended Fix**:

```python
# Migration 0023 (combine with event type fix)
def upgrade(conn):
    # ... event type changes ...

    # Add phase index
    conn.execute("CREATE INDEX idx_work_items_phase ON work_items(phase)")

    # Add composite index for common queries
    conn.execute("CREATE INDEX idx_work_items_phase_status ON work_items(phase, status)")
```

**Files to Change**:
- `agentpm/core/database/migrations/files/migration_0023.py` (add index)

---

## 🟢 **LOW PRIORITY** (Future Enhancements)

### **Issue #9: Continuous Work Items Phase Semantics**

**Severity**: 🟢 LOW
**Impact**: Conceptual clarity
**Effort**: 1 hour (documentation)

**Problem**:
Unclear what "phase progression" means for continuous work items (maintenance, monitoring) that never complete.

**Evidence**:
```python
# Continuous work items:
work_item = WorkItem(
    type=WorkItemType.MAINTENANCE,
    is_continuous=True,
    status=WorkItemStatus.ACTIVE,  # Forever
    phase=Phase.I1_IMPLEMENTATION  # Can this advance?
)

# Workflow prevents completion:
if work_item.is_continuous and new_status in {DONE, ARCHIVED}:
    raise WorkflowError("Continuous work items cannot complete")

# But phase CAN advance:
# I1_IMPLEMENTATION → O1_OPERATIONS → E1_EVOLUTION (?)
```

**Impact**:
- Semantic confusion: Does phase mean "current work" or "maturity level"?
- Users unsure if they should advance phases for continuous work
- Dashboard unclear: "Phase: E1_EVOLUTION, Status: ACTIVE" (what does this mean?)

**Recommended Solution**:

**Option A: Phases as Maturity Levels** (Keep current design)
- D1_DISCOVERY: Setting up maintenance process
- P1_PLAN: Designed maintenance strategy
- I1_IMPLEMENTATION: Built initial tooling
- O1_OPERATIONS: Actively maintaining (steady state)
- E1_EVOLUTION: Continuously improving process

**Documentation**:
```markdown
# Continuous Work Items and Phases

Continuous work items (maintenance, monitoring, documentation, security)
use phases to track **process maturity**, not completion:

- **D1_DISCOVERY**: Setting up the continuous process
- **P1_PLAN**: Process designed and documented
- **I1_IMPLEMENTATION**: Initial tooling and automation built
- **O1_OPERATIONS**: Process is operational (steady state)
- **E1_EVOLUTION**: Process is mature and continuously improving

Phase advancement for continuous work items represents **process maturity**,
not work completion. Status remains ACTIVE throughout.
```

**Option B: No Phases for Continuous** (Simplify)
```python
# Set phase=NULL for continuous work items
if work_item.is_continuous:
    work_item.phase = None
```

**Recommendation**: **Option A** (phases as maturity) - more valuable semantically

**Files to Change**:
- Create: `docs/user-guides/continuous-work-items-phases.md` (documentation only)

---

### **Issue #10: Questionnaire Service Coverage Gap**

**Severity**: 🟢 LOW
**Impact**: Test coverage below CI-004 target
**Effort**: 4 hours

**Problem**:
Questionnaire service only has 60% test coverage (target: >90% per CI-004).

**Evidence**:
```bash
# Current coverage
pytest --cov=agentpm.core.rules.questionnaire --cov-report=term
# questionnaire.py: 60% (120/200 lines covered)
```

**Impact**:
- Cannot validate questionnaire edge cases
- Continue workflow untested (WI-77 task)
- Risk of regression during refactoring

**Recommended Fix**:

**Add tests for**:
1. Continue workflow (resume interrupted questionnaire)
2. Invalid answer handling
3. Detection-based defaults
4. Rule generation from answers
5. Database persistence

**Files to Create**:
- `tests-BAK/core/rules/test_questionnaire_continue.py`
- `tests-BAK/core/rules/test_questionnaire_edge_cases.py`

---

## 📋 **Issue Summary**

| # | Issue | Severity | Effort | Impact | Status |
|---|-------|----------|--------|--------|--------|
| 1 | Phase-status desync | 🔴 HIGH | 3h | Workflow integrity | Open |
| 2 | Event type mismatch | 🔴 HIGH | 1h | Data integrity | Open |
| 3 | EventBus lifecycle | 🔴 HIGH | 2h | Memory leak | Open |
| 4 | Phase gates not enforced | 🔴 HIGH | 4h | Quality bypass | Open |
| 5 | Tasks no phase field | 🟡 MEDIUM | 2h | Performance | Open |
| 6 | Plugin facts not persisted | 🟡 MEDIUM | 3h | Performance | Open |
| 7 | Agent SOP from files | 🟡 MEDIUM | 2h | Architecture | Open |
| 8 | No phase index | 🟡 MEDIUM | 0.5h | Performance | Open |
| 9 | Continuous phase semantics | 🟢 LOW | 1h | Clarity | Open |
| 10 | Questionnaire coverage | 🟢 LOW | 4h | Test quality | Open |

**Total Effort to Address All**: 22.5 hours (~3 days)

---

## 🎯 **Recommended Fix Priority**

### **Critical Path** (Must fix for production)

**Day 1** (6 hours):
1. Event type schema mismatch (1h) - Migration 0023
2. EventBus lifecycle leak (2h) - Singleton pattern
3. Phase-status alignment (3h) - Add validation guards

**Day 2** (8 hours):
4. Phase gates enforcement (4h) - Integrate PhaseGateValidator
5. Plugin facts persistence (3h) - Wire to database
6. Agent SOP database loading (2h) - Update SOPInjector
7. Add phase index (0.5h) - Include in migration 0023

**Day 3** (8 hours):
8. Add phase to tasks (2h) - Migration 0024
9. Test coverage improvements (4h) - Questionnaire tests
10. Documentation (2h) - Continuous work items

**Total**: 22 hours = **2-3 days of focused work**

---

## ✅ **Quality Gate Before Production**

**All HIGH priority issues MUST be resolved**:
- ✅ Phase-status alignment validated
- ✅ Event types accurate in database
- ✅ EventBus lifecycle managed (no leaks)
- ✅ Phase gates enforced in workflow

**MEDIUM priority issues recommended**:
- ✅ Plugin facts persisted
- ✅ Agent SOPs from database
- ✅ Phase index created

**LOW priority issues can defer**:
- Documentation improvements
- Test coverage enhancements (if >90% on critical paths)

---

**Next Action**: Choose which issues to tackle first based on your immediate needs.
