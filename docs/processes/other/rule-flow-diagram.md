# Rule Enforcement Flow Diagram

## Current Implementation (What Exists)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RULE LIFECYCLE                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. INITIALIZATION (apm init)
   ┌──────────────────────────────────────────────────────────┐
   │ DefaultRulesLoader                                       │
   │  ├─ Load from rules_catalog.yaml (245 rules)            │
   │  ├─ Filter by preset (minimal/standard/professional)     │
   │  └─ Write to database (rules table)                      │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ SQLite Database (aipm.db)                               │
   │ ┌──────────────────────────────────────────────────────┐ │
   │ │ rules table                                          │ │
   │ │  - rule_id (e.g., DP-001)                           │ │
   │ │  - name (e.g., time-boxing-implementation)          │ │
   │ │  - enforcement_level (BLOCK/LIMIT/GUIDE/ENHANCE)    │ │
   │ │  - validation_logic (pattern for evaluation)        │ │
   │ │  - config (JSON: {"max_hours": 4.0})               │ │
   │ │  - enabled (boolean)                                │ │
   │ └──────────────────────────────────────────────────────┘ │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼

2. RUNTIME ENFORCEMENT (Workflow Transitions)
   ┌──────────────────────────────────────────────────────────┐
   │ WorkflowService.transition_task()                        │
   │  ├─ task.status != new_status?                          │
   │  └─ YES → _check_rules()                                │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ WorkflowService._check_rules()                           │
   │  ├─ Load enabled rules from database                    │
   │  ├─ Evaluate each rule against entity/transition        │
   │  ├─ BLOCK violations → raise WorkflowError              │
   │  ├─ LIMIT violations → show warning (Rich console)      │
   │  └─ GUIDE violations → show info (Rich console)         │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ Rule Evaluation (_evaluate_rule)                        │
   │  ├─ Time-boxing: effort_hours > max_hours              │
   │  ├─ Test coverage: coverage_percent < threshold        │
   │  ├─ Category coverage: validate by path patterns       │
   │  └─ Return violation result (violated: bool, message)   │
   └──────────────────────────────────────────────────────────┘

3. CLI VISIBILITY (Manual Agent Access)
   ┌──────────────────────────────────────────────────────────┐
   │ apm rules list                                           │
   │  ├─ Load rules from database                            │
   │  ├─ Filter by enforcement/category (optional)           │
   │  └─ Display in Rich table                               │
   └──────────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────┐
   │ apm rules show <rule-id>                                 │
   │  ├─ Load specific rule from database                    │
   │  └─ Display detailed info (validation logic, config)    │
   └──────────────────────────────────────────────────────────┘

4. AGENT CONTEXT (Current - NO RULES)
   ┌──────────────────────────────────────────────────────────┐
   │ ContextAssemblyService.assemble_task_context()           │
   │  ├─ Load entities (task, work_item, project)            │
   │  ├─ Load 6W contexts                                     │
   │  ├─ Merge 6W hierarchically                             │
   │  ├─ Load plugin facts                                   │
   │  ├─ Get amalgamation paths                              │
   │  ├─ Inject agent SOP                                    │
   │  └─ Return ContextPayload                               │
   │      ❌ NO RULES INCLUDED                               │
   └──────────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────┐
   │ AgentSOPInjector.load_sop()                              │
   │  ├─ Read .claude/agents/{role}.md                       │
   │  ├─ Static markdown content                             │
   │  └─ NO RULES EMBEDDED                                   │
   │      ❌ Agent must manually call 'apm rules list'       │
   └──────────────────────────────────────────────────────────┘
```

---

## Gaps in Current Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VISIBILITY GAPS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

GAP 1: Rules Not in ContextPayload
   ┌──────────────────────────────────────────────────────────┐
   │ Agent reads context via:                                 │
   │  - assemble_task_context()                              │
   │  - apm task show <task-id>                              │
   │                                                          │
   │ Gets:                                                    │
   │  ✅ Task details                                        │
   │  ✅ Work item context                                   │
   │  ✅ Project context                                     │
   │  ✅ 6W intelligence                                     │
   │  ✅ Plugin facts                                        │
   │  ✅ Agent SOP                                           │
   │  ❌ NO RULES                                            │
   │                                                          │
   │ Result: Agent unaware of time-boxing, coverage rules    │
   └──────────────────────────────────────────────────────────┘

GAP 2: Rules Not in Agent SOPs
   ┌──────────────────────────────────────────────────────────┐
   │ Agent SOP (.claude/agents/python-developer.md):         │
   │                                                          │
   │ # Python Developer Agent                                │
   │                                                          │
   │ ## Role                                                  │
   │ Expert Python developer...                              │
   │                                                          │
   │ ## Capabilities                                          │
   │ - Python 3.10+                                          │
   │ - Pytest testing                                        │
   │                                                          │
   │ ## Workflow                                              │
   │ 1. Read task                                            │
   │ 2. Implement                                            │
   │ 3. Test                                                 │
   │                                                          │
   │ ❌ NO RULES SECTION                                     │
   │    - No time-boxing limits                              │
   │    - No test coverage requirements                      │
   │    - No code quality standards                          │
   └──────────────────────────────────────────────────────────┘

GAP 3: Rules Not in 6W HOW Dimension
   ┌──────────────────────────────────────────────────────────┐
   │ 6W Context (HOW dimension):                              │
   │                                                          │
   │ how: {                                                   │
   │   'suggested_approach': 'Use three-layer pattern...',   │
   │   'existing_patterns': ['Models → Adapters → Methods'], │
   │   'plugin_facts': {...},                                │
   │   ❌ NO 'governance_rules' field                        │
   │ }                                                        │
   │                                                          │
   │ Result: Rules disconnected from technical context       │
   └──────────────────────────────────────────────────────────┘

GAP 4: No Rule Filtering by Agent Role
   ┌──────────────────────────────────────────────────────────┐
   │ apm rules list                                           │
   │  ├─ Shows ALL 71 rules to ALL agents                    │
   │  └─ No capability-based filtering                       │
   │                                                          │
   │ Example:                                                 │
   │  Frontend developer sees:                               │
   │   ✅ UI standards (relevant)                            │
   │   ❌ Database rules (irrelevant)                        │
   │   ❌ Python-specific rules (irrelevant)                 │
   │                                                          │
   │ Result: Cognitive overload - too many irrelevant rules  │
   └──────────────────────────────────────────────────────────┘
```

---

## Proposed Solution (What Should Be Added)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED RULE DELIVERY (PROPOSED)                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. ContextPayload with Rules (P0 - 4 hours)
   ┌──────────────────────────────────────────────────────────┐
   │ ContextAssemblyService.assemble_task_context()           │
   │  ├─ ... (existing 10 steps)                             │
   │  └─ NEW STEP 11: Load applicable rules                  │
   │      ├─ Load enabled rules from database                │
   │      ├─ Filter by agent capability                      │
   │      └─ Add to ContextPayload.applicable_rules          │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ ContextPayload (ENHANCED)                                │
   │  ├─ project: {...}                                      │
   │  ├─ work_item: {...}                                    │
   │  ├─ task: {...}                                         │
   │  ├─ merged_6w: {...}                                    │
   │  ├─ plugin_facts: {...}                                 │
   │  ├─ agent_sop: "..."                                    │
   │  └─ ✅ NEW: applicable_rules: [...]                     │
   │      ├─ rule_id: "DP-001"                               │
   │      ├─ enforcement_level: "BLOCK"                      │
   │      ├─ description: "IMPLEMENTATION ≤4h"               │
   │      └─ applies_to_task: true                           │
   └──────────────────────────────────────────────────────────┘

2. Rule Filtering by Capability (P1 - 6 hours)
   ┌──────────────────────────────────────────────────────────┐
   │ RuleFilter.filter_rules()                                │
   │  ├─ Get agent capabilities from agents table            │
   │  ├─ Match rule categories to capabilities               │
   │  └─ Return relevant rules only                          │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ Filtering Logic                                          │
   │                                                          │
   │ python-developer:                                        │
   │  ✅ development_principles (DP-*)                       │
   │  ✅ code_quality (CQ-*)                                 │
   │  ✅ testing (TEST-*)                                    │
   │  ✅ workflow (WR-*)                                     │
   │  ❌ ui_standards                                        │
   │  ❌ accessibility                                       │
   │                                                          │
   │ frontend-developer:                                      │
   │  ✅ ui_standards (UI-*)                                 │
   │  ✅ accessibility (ACC-*)                               │
   │  ✅ testing (TEST-*)                                    │
   │  ✅ workflow (WR-*)                                     │
   │  ❌ database_standards                                  │
   │  ❌ python_specific                                     │
   └──────────────────────────────────────────────────────────┘

3. Dynamic Agent SOPs with Rules (P2 - 8 hours)
   ┌──────────────────────────────────────────────────────────┐
   │ AgentSOPBuilder.build_sop()                              │
   │  ├─ Load base template (.claude/agents/{role}.md)       │
   │  ├─ Load applicable rules (filtered)                    │
   │  ├─ Build rules section (markdown)                      │
   │  └─ Inject into template ({{RULES_SECTION}})            │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ Enhanced SOP (.claude/agents/python-developer.md)       │
   │                                                          │
   │ # Python Developer Agent                                │
   │                                                          │
   │ ## Role                                                  │
   │ Expert Python developer...                              │
   │                                                          │
   │ ## Capabilities                                          │
   │ - Python 3.10+                                          │
   │ - Pytest testing                                        │
   │                                                          │
   │ ✅ ## Project Rules                                     │
   │                                                          │
   │ ### ❌ Blocking Rules (MUST follow)                     │
   │ - **DP-001**: IMPLEMENTATION tasks ≤4 hours             │
   │ - **DP-012**: Test coverage ≥90%                        │
   │                                                          │
   │ ### ⚠️ Soft Constraints (recommended)                   │
   │ - **DP-027**: Type hints required                       │
   │ - **DP-028**: Docstrings required                       │
   │                                                          │
   │ ### ℹ️ Guidelines (informational)                       │
   │ - **DP-029**: No print() statements                     │
   │                                                          │
   │ ## Workflow                                              │
   │ 1. Read task                                            │
   │ 2. Check time-boxing (DP-001)                           │
   │ 3. Implement                                            │
   │ 4. Write tests (DP-012: ≥90% coverage)                  │
   └──────────────────────────────────────────────────────────┘

4. Rules in 6W HOW Dimension (P3 - 6 hours)
   ┌──────────────────────────────────────────────────────────┐
   │ SixWMerger.merge_hierarchical()                          │
   │  ├─ Merge project/work_item/task 6W contexts            │
   │  └─ ✅ Inject rules into HOW dimension                  │
   │      └─ how['governance_rules'] = [...]                 │
   └────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────────────────┐
   │ Enhanced 6W Context (HOW dimension)                      │
   │                                                          │
   │ how: {                                                   │
   │   'suggested_approach': 'Use three-layer pattern...',   │
   │   'existing_patterns': ['Models → Adapters → Methods'], │
   │   'plugin_facts': {...},                                │
   │   ✅ 'governance_rules': [                              │
   │     {                                                    │
   │       'rule_id': 'DP-001',                              │
   │       'enforcement_level': 'BLOCK',                     │
   │       'description': 'IMPLEMENTATION ≤4h'               │
   │     },                                                   │
   │     {                                                    │
   │       'rule_id': 'DP-012',                              │
   │       'enforcement_level': 'BLOCK',                     │
   │       'description': 'Test coverage ≥90%'               │
   │     }                                                    │
   │   ]                                                      │
   │ }                                                        │
   └──────────────────────────────────────────────────────────┘
```

---

## Rule Enforcement Points (Complete Flow)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHEN RULES ARE CHECKED                                    │
└─────────────────────────────────────────────────────────────────────────────┘

INITIALIZATION (apm init)
  └─> Load rules from YAML → Store in database

WORKFLOW TRANSITIONS
  ├─> Task: PROPOSED → VALIDATED
  │    └─> Check metadata requirements (CI-006)
  │
  ├─> Task: VALIDATED → ACCEPTED
  │    └─> Check agent assignment (CI-001)
  │
  ├─> Task: ACCEPTED → IN_PROGRESS
  │    ├─> Check time-boxing (DP-001 to DP-011)
  │    ├─> Check agent active (CI-001)
  │    └─> Check work item state gate
  │
  ├─> Task: IN_PROGRESS → REVIEW
  │    ├─> Check test coverage (DP-012, CI-004)
  │    └─> Check quality gates (WR-001)
  │
  ├─> Task: REVIEW → COMPLETED
  │    ├─> Check code review (WR-004)
  │    ├─> Check documentation (CI-006)
  │    └─> Check acceptance criteria
  │
  └─> Work Item: READY → ACTIVE
       ├─> Check required task types (WR-002, WR-003)
       └─> Check specification quality (CI-002)

AGENT CONTEXT ASSEMBLY (PROPOSED)
  └─> assemble_task_context()
       └─> ✅ Load applicable rules → Add to ContextPayload

AGENT SOP GENERATION (PROPOSED)
  └─> build_sop()
       └─> ✅ Inject rules into template

CLI COMMANDS (Manual)
  ├─> apm rules list
  └─> apm rules show <rule-id>
```

---

## Benefit Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BEFORE vs AFTER                                           │
└─────────────────────────────────────────────────────────────────────────────┘

BEFORE (Current Implementation)
  Agent Workflow:
    1. Read task context via assemble_task_context()
    2. ❌ NO RULES VISIBLE - agent unaware of constraints
    3. Implement solution (may violate time-boxing, coverage rules)
    4. Submit for review
    5. ❌ WorkflowError at transition - rule violation detected too late
    6. Rework required - wasted time

  Problems:
    - Rules enforced ONLY at transitions (too late)
    - Agents must manually call 'apm rules list' (error-prone)
    - No filtering - all agents see all rules (cognitive overload)
    - SOPs are static - don't reflect project-specific rules

AFTER (Proposed Solution)
  Agent Workflow:
    1. Read task context via assemble_task_context()
    2. ✅ RULES VISIBLE in ContextPayload.applicable_rules
    3. ✅ RULES IN SOP - agent sees constraints upfront
    4. Implement solution (follows time-boxing, coverage rules)
    5. Submit for review
    6. ✅ No WorkflowError - rules followed proactively

  Benefits:
    - Rules visible BEFORE implementation (proactive compliance)
    - Automatic rule discovery (no manual CLI calls)
    - Capability-based filtering (relevant rules only)
    - Dynamic SOPs (project-specific rules embedded)

METRICS (Expected Improvement)
  - Rule violations: -80% (proactive vs reactive)
  - Agent cognitive load: -60% (filtered vs all rules)
  - Rework cycles: -50% (rules followed upfront)
  - Time to compliance: -70% (no manual discovery)
```

---

## Implementation Order

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ROLLOUT SEQUENCE                                          │
└─────────────────────────────────────────────────────────────────────────────┘

PHASE 1: Context Integration (P0, 4 hours)
  ├─> Add applicable_rules field to ContextPayload
  ├─> Implement _load_applicable_rules() in ContextAssemblyService
  └─> Update apm task show to display rules

  Test:
    └─> context = service.assemble_task_context(task_id=355)
        assert 'applicable_rules' in context
        assert len(context.applicable_rules) > 0

PHASE 2: Rule Filtering (P1, 6 hours)
  ├─> Create RuleFilter class (context/role_filter.py)
  ├─> Implement filter_rules() with capability matching
  └─> Integrate into ContextAssemblyService

  Test:
    └─> python_rules = filter.filter_rules(agent='python-developer')
        assert all(r.category in ['development_principles', 'testing'] for r in python_rules)

PHASE 3: Dynamic SOPs (P2, 8 hours)
  ├─> Create AgentSOPBuilder class (agents/builder.py)
  ├─> Update SOP templates with {{RULES_SECTION}} placeholder
  ├─> Implement build_sop() with rule injection
  └─> Update AgentSOPInjector to use builder

  Test:
    └─> sop = builder.build_sop(agent='python-developer')
        assert '## Project Rules' in sop
        assert 'DP-001' in sop

PHASE 4: 6W Integration (P3, 6 hours)
  ├─> Update SixWMerger.merge_hierarchical() to accept project_id
  ├─> Implement _load_project_rules() in merger
  └─> Inject rules into HOW dimension

  Test:
    └─> merged = merger.merge_hierarchical(project_id=1)
        assert 'governance_rules' in merged.how
        assert len(merged.how['governance_rules']) > 0

TOTAL EFFORT: ~24 hours (3 days)
```
