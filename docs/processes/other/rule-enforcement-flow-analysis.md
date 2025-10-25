# Rule Enforcement Flow Analysis

**Objective**: Understand actual rule flow from database to agent behavior
**Date**: 2025-10-17
**Analyzer**: Code Analyzer Agent

---

## Executive Summary

**Critical Findings**:
1. ✅ Rules are enforced at workflow transition points (WorkflowService._check_rules)
2. ❌ Rules are NOT embedded in agent SOPs automatically
3. ❌ Rules are NOT included in ContextPayload by default
4. ⚠️ Agent visibility of rules depends on manual CLI checks (`apm rules list`)

**Recommendation**: Rules need to be injected into context delivery pipeline to ensure agents see them during task execution.

---

## 1. Rule Enforcement Flow (Current Implementation)

### 1.1 Database Storage (Single Source of Truth)

**Location**: SQLite database (`aipm.db`)
**Table**: `rules`
**Schema**:
```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    rule_id TEXT NOT NULL,           -- e.g., "DP-001"
    name TEXT NOT NULL,               -- e.g., "time-boxing-implementation"
    description TEXT,
    category TEXT,                    -- e.g., "development_principles"
    enforcement_level TEXT NOT NULL,  -- BLOCK, LIMIT, GUIDE, ENHANCE
    validation_logic TEXT,            -- Pattern for evaluation
    error_message TEXT,
    config TEXT,                      -- JSON config
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);
```

**Loading at Init**:
- `apm init` calls `DefaultRulesLoader.load_from_catalog()`
- Loads rules from YAML catalog (`agentpm/core/rules/config/rules_catalog.yaml`)
- Stores in database (245 rules in catalog, preset determines which are enabled)

**Key Insight**: Rules are populated ONCE during `apm init`, then database is single source of truth.

---

### 1.2 Runtime Enforcement (WorkflowService)

**File**: `agentpm/core/workflow/service.py`
**Method**: `WorkflowService._check_rules()`
**Line**: 798-876

**When Rules Are Checked**:
1. **Work Item Transitions**: Lines 182-187 in `transition_work_item()`
2. **Task Transitions**: Lines 317-323 in `transition_task()`

**Enforcement Logic**:
```python
def _check_rules(self, entity_type: EntityType, entity: Task | WorkItem, transition: dict[str, str]) -> None:
    # Load enabled rules from database
    rules = rule_methods.list_rules(self.db, project_id=project_id, enabled_only=True)

    # If no rules, load defaults
    if not rules:
        self._ensure_default_rules_loaded(project_id)
        rules = rule_methods.list_rules(self.db, project_id=project_id, enabled_only=True)

    # Evaluate each rule
    for rule in rules:
        result = self._evaluate_rule(rule, entity, transition)

        if result['violated']:
            if rule.enforcement_level == EnforcementLevel.BLOCK:
                violations.append((rule, result))
            elif rule.enforcement_level == EnforcementLevel.LIMIT:
                warnings.append((rule, result))
            elif rule.enforcement_level == EnforcementLevel.GUIDE:
                guides.append((rule, result))

    # Handle violations
    if violations:
        error_msg = self._format_blocking_error(violations)
        raise WorkflowError(error_msg)

    # Show warnings/guidance (non-blocking)
    if warnings: self._show_warnings(warnings)
    if guides: self._show_guidance(guides)
```

**Enforcement Levels**:
- **BLOCK**: Hard constraint - raises `WorkflowError`, operation fails
- **LIMIT**: Soft constraint - shows warning via Rich console, operation succeeds
- **GUIDE**: Suggestion - shows info via Rich console, no enforcement
- **ENHANCE**: Context enrichment - no enforcement, metadata only

**Rule Evaluation Patterns** (lines 897-1023):
1. **Time-boxing**: `entity.effort_hours > rule.config['max_hours']`
2. **Test coverage**: `entity.quality_metadata.get('coverage_percent') < threshold`
3. **Category coverage**: Calls validation function for specific code categories

**Key Insight**: Rules are enforced ONLY at workflow transition points. Agents don't see rules unless they trigger a transition.

---

### 1.3 Default Rule Loading (Lazy Initialization)

**File**: `agentpm/core/workflow/service.py`
**Method**: `_ensure_default_rules_loaded()`
**Lines**: 878-895

```python
def _ensure_default_rules_loaded(self, project_id: int) -> None:
    try:
        from ..rules import DefaultRulesLoader
        loader = DefaultRulesLoader(self.db)
        loader.load_defaults(project_id=project_id, overwrite=False)
    except Exception:
        # Fail open - workflow continues without rule enforcement
        pass
```

**Behavior**:
- If no rules exist in database, loads 25 default rules (hardcoded in `loader.py`)
- If loading fails, **fails open** (workflow continues, no enforcement)
- This ensures rules are always available for enforcement

---

## 2. Agent SOP Generation (Current Implementation)

### 2.1 Agent Table Schema

**Location**: SQLite database (`agents` table)
**Schema**:
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL,              -- e.g., "python-developer"
    display_name TEXT,
    description TEXT,
    sop_content TEXT,                -- Stores SOP markdown (optional)
    capabilities TEXT,               -- JSON array
    is_active BOOLEAN DEFAULT 1,
    agent_type TEXT,
    file_path TEXT,                  -- Path to .md file (e.g., ".claude/agents/python-developer.md")
    generated_at TIMESTAMP,
    tier TEXT,                       -- "sub-agent", "specialist", "orchestrator"
    last_used_at TIMESTAMP,
    metadata TEXT,                   -- JSON metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);
```

**Key Fields**:
- `sop_content`: Stores SOP markdown (optional, not widely used)
- `file_path`: Path to SOP file (e.g., `.claude/agents/python-developer.md`)

**Critical Finding**: Agent table does NOT have a `rules_snapshot` or `applicable_rules` field.

---

### 2.2 Agent SOP Loading (Runtime)

**File**: `agentpm/core/context/sop_injector.py`
**Class**: `AgentSOPInjector`
**Method**: `load_sop()`
**Lines**: 41-110

**SOP Loading Strategy**:
1. Validate agent exists and is active (database check)
2. Check database for custom SOP path (`agent.file_path`)
3. Fallback to default location (`.claude/agents/{role}.md`)
4. Check filesystem cache before reading file
5. Return None if SOP not found (graceful degradation)

**Critical Finding**: SOP loading does NOT inject rules into the SOP content. It only reads the static `.md` file.

**SOP File Format** (example: `.claude/agents/python-developer.md`):
```markdown
# Python Developer Agent

## Role
Expert Python developer specializing in backend development.

## Capabilities
- Python 3.10+ development
- Type hints and Pydantic models
- Pytest testing
- Database integration

## Workflow
1. Read task requirements
2. Implement solution
3. Write tests
4. Submit for review

## Quality Standards
- Follow PEP 8
- 100% type coverage
- Comprehensive docstrings
```

**Key Insight**: Rules are NOT embedded in agent SOPs. SOPs are static markdown files that don't change based on project rules.

---

## 3. Context Assembly (Task Execution)

### 3.1 Context Assembly Service

**File**: `agentpm/core/context/assembly_service.py`
**Class**: `ContextAssemblyService`
**Method**: `assemble_task_context()`
**Lines**: 87-139

**11-Step Assembly Pipeline**:
1. Load entities (task, work item, project) - CRITICAL
2. Load 6W contexts (all three levels) - IMPORTANT
3. Merge 6W hierarchically (task > work_item > project) - 5ms
4. Load plugin facts - 20ms cached / 100ms fresh
5. Get amalgamation paths - 10ms
6. Calculate freshness - 5ms
7. Calculate confidence - 10ms
8. **Inject agent SOP** (if agent assigned) - 10-20ms
9. Load temporal context (session summaries) - 10ms
10. Filter by agent role - 5-10ms
11. Return payload

**Critical Finding**: Rules are NOT included in any of these 11 steps. Context assembly does not load or inject rules.

---

### 3.2 ContextPayload Structure

**File**: `agentpm/core/context/models.py`
**Class**: `ContextPayload`

**Fields**:
```python
class ContextPayload(BaseModel):
    project: Dict[str, Any]
    work_item: Dict[str, Any]
    task: Dict[str, Any]
    merged_6w: UnifiedSixW
    plugin_facts: Dict[str, Any]
    amalgamations: Dict[str, str]  # {type: file_path}
    agent_sop: Optional[str]       # Markdown content
    assigned_agent: Optional[str]
    temporal_context: List[Dict[str, Any]]
    confidence_score: float
    confidence_band: ConfidenceBand
    confidence_breakdown: Dict[str, Any]
    warnings: List[str]
    assembled_at: datetime
    assembly_duration_ms: float
    cache_hit: bool
```

**Critical Finding**: ContextPayload does NOT have a `rules` or `applicable_rules` field.

---

### 3.3 6W Context Structure (HOW Dimension)

**File**: `agentpm/core/database/models/context.py`
**Class**: `UnifiedSixW`

**HOW Dimension**:
```python
class UnifiedSixW(BaseModel):
    # ... other dimensions ...

    how: Optional[Dict[str, Any]] = None  # Approach, patterns, technical constraints

    # Example:
    # how: {
    #     'suggested_approach': 'Use three-layer pattern...',
    #     'existing_patterns': ['Models → Adapters → Methods'],
    #     'plugin_facts': {...},
    #     'technical_constraints': [...]
    # }
```

**Critical Finding**: Rules are NOT stored in the HOW dimension of 6W context. Plugin facts are stored there, but rules are not.

---

## 4. CLI Commands (Agent-Facing)

### 4.1 apm rules list

**File**: `agentpm/cli/commands/rules/list.py`
**Output**: Rich table with rules

```
📋 Project Rules (71 of 71)
┌──────────┬──────────────────┬──────────────┬────────────────────────┐
│ Rule ID  │ Category         │ Enforcement  │ Description            │
├──────────┼──────────────────┼──────────────┼────────────────────────┤
│ DP-001   │ Development...   │ BLOCK        │ IMPLEMENTATION ≤4h     │
│ DP-012   │ Development...   │ BLOCK        │ Test coverage ≥90%     │
│ ...      │ ...              │ ...          │ ...                    │
└──────────┴──────────────────┴──────────────┴────────────────────────┘

Summary: BLOCK: 15 | LIMIT: 30 | GUIDE: 20 | ENHANCE: 6
```

**Agent Discovery**: Agents must explicitly call `apm rules list` to see rules.

---

### 4.2 apm rules show <rule-id>

**Output**: Detailed rule information

```
📋 Rule Details: DP-001

Name: time-boxing-implementation
Category: Development Principles
Enforcement: BLOCK

Description:
IMPLEMENTATION tasks must be ≤4 hours

Validation Logic:
effort_hours > 4.0

Error Message:
IMPLEMENTATION tasks limited to ≤4 hours

Configuration:
{
    "max_hours": 4.0,
    "task_type": "IMPLEMENTATION"
}

Status: Enabled
```

---

### 4.3 apm task show <task-id>

**File**: `agentpm/cli/commands/task/show.py`
**Output**: Complete task context (9 sections)

**Sections**:
1. Task Details (type, status, effort, priority, assigned agent)
2. Work Item Context (type, phase, status, business value)
3. Project Context (tech stack, frameworks, business domain)
4. 6W Context (who, what, where, when, why, how)
5. Related Documents (ADRs, specs, designs)
6. Evidence & Research (sources, excerpts)
7. Recent Activity (last 5 events)
8. Latest Progress (most recent summary)
9. Code Context (amalgamation file paths)

**Critical Finding**: `apm task show` does NOT display applicable rules. Rules are missing from agent-facing context.

---

## 5. Rule Visibility Gaps

### 5.1 Gap: Rules Not in Agent SOPs

**Problem**: Agent SOPs are static markdown files that don't change based on project rules.

**Example**: Python developer SOP says "Follow PEP 8", but project rules might specify stricter standards (e.g., "No Dict[str, Any] in public APIs" from DP-030).

**Impact**: Agents may violate rules because they don't see them in their SOPs.

**Fix**: Generate agent SOPs dynamically, injecting relevant rules.

---

### 5.2 Gap: Rules Not in ContextPayload

**Problem**: ContextPayload doesn't include rules, so agents don't see them during task execution.

**Example**: Agent reads task context via `apm task show`, gets all context except rules.

**Impact**: Agents must explicitly call `apm rules list` to discover rules. This is error-prone.

**Fix**: Add `applicable_rules` field to ContextPayload, filtered by agent capabilities.

---

### 5.3 Gap: Rules Not in 6W HOW Dimension

**Problem**: 6W HOW dimension stores plugin facts and patterns, but not rules.

**Example**: HOW dimension says "Use three-layer pattern", but doesn't mention time-boxing rules.

**Impact**: Rules are disconnected from technical context.

**Fix**: Inject rules into HOW dimension as "governance constraints".

---

### 5.4 Gap: No Rule Filtering by Agent Role

**Problem**: All rules are shown to all agents, even if irrelevant.

**Example**: Frontend developer sees database rules, database developer sees UI rules.

**Impact**: Cognitive overload - agents see too many irrelevant rules.

**Fix**: Filter rules by agent capabilities (similar to amalgamation filtering).

---

## 6. Recommended Fixes

### 6.1 Immediate Fix: Add Rules to ContextPayload

**File**: `agentpm/core/context/models.py`

```python
class ContextPayload(BaseModel):
    # ... existing fields ...

    # NEW: Applicable rules for this agent
    applicable_rules: List[Dict[str, Any]] = Field(default_factory=list)

    # Example:
    # applicable_rules: [
    #     {
    #         'rule_id': 'DP-001',
    #         'name': 'time-boxing-implementation',
    #         'enforcement_level': 'BLOCK',
    #         'description': 'IMPLEMENTATION tasks ≤4h',
    #         'applies_to_task': True,
    #         'validation_logic': 'effort_hours > 4.0',
    #         'error_message': '...'
    #     }
    # ]
```

**Implementation**: Add step to `ContextAssemblyService.assemble_task_context()`:

```python
# Step 11: Load applicable rules (NEW)
applicable_rules = self._load_applicable_rules(
    project_id=project.id,
    agent_role=effective_agent_role,
    task_type=task.type
)
```

---

### 6.2 Short-Term Fix: Rule Filtering by Capability

**File**: `agentpm/core/context/role_filter.py` (NEW)

```python
class RuleFilter:
    """Filter rules by agent capabilities."""

    def filter_rules(
        self,
        project_id: int,
        agent_role: str,
        all_rules: List[Rule]
    ) -> List[Rule]:
        """Filter rules relevant to this agent."""

        # Get agent capabilities
        agent = agents.get_agent_by_role(self.db, project_id, agent_role)
        if not agent:
            return all_rules  # No filtering

        capabilities = agent.capabilities or []

        # Filter rules by category
        filtered = []
        for rule in all_rules:
            if self._rule_applies_to_agent(rule, capabilities):
                filtered.append(rule)

        return filtered

    def _rule_applies_to_agent(self, rule: Rule, capabilities: List[str]) -> bool:
        """Check if rule applies to agent capabilities."""

        # Example: Python developer sees Python/testing rules
        # Frontend developer sees UI/testing rules

        if 'python' in capabilities:
            if rule.category in ['development_principles', 'code_quality', 'testing']:
                return True

        if 'react' in capabilities:
            if rule.category in ['ui_standards', 'accessibility', 'testing']:
                return True

        # Always show workflow rules (apply to all agents)
        if rule.category == 'workflow':
            return True

        return False
```

---

### 6.3 Medium-Term Fix: Inject Rules into Agent SOPs

**File**: `agentpm/core/agents/builder.py` (NEW)

```python
class AgentSOPBuilder:
    """Generate agent SOPs with project rules embedded."""

    def build_sop(
        self,
        project_id: int,
        agent_role: str,
        template_path: Path
    ) -> str:
        """Generate agent SOP with rules injected."""

        # Load base template
        template = template_path.read_text()

        # Load applicable rules
        rules = rule_methods.list_rules(self.db, project_id, enabled_only=True)
        filtered_rules = self.rule_filter.filter_rules(project_id, agent_role, rules)

        # Group rules by enforcement level
        blocking_rules = [r for r in filtered_rules if r.enforcement_level == EnforcementLevel.BLOCK]
        limit_rules = [r for r in filtered_rules if r.enforcement_level == EnforcementLevel.LIMIT]
        guide_rules = [r for r in filtered_rules if r.enforcement_level == EnforcementLevel.GUIDE]

        # Build rules section
        rules_section = self._build_rules_section(blocking_rules, limit_rules, guide_rules)

        # Inject rules into template
        sop = template.replace('{{RULES_SECTION}}', rules_section)

        return sop

    def _build_rules_section(self, blocking, limit, guide) -> str:
        """Build markdown rules section."""

        lines = ["## Project Rules\n"]

        if blocking:
            lines.append("### ❌ Blocking Rules (MUST follow)\n")
            for rule in blocking:
                lines.append(f"- **{rule.rule_id}**: {rule.description}")

        if limit:
            lines.append("\n### ⚠️ Soft Constraints (recommended)\n")
            for rule in limit:
                lines.append(f"- **{rule.rule_id}**: {rule.description}")

        if guide:
            lines.append("\n### ℹ️ Guidelines (informational)\n")
            for rule in guide:
                lines.append(f"- **{rule.rule_id}**: {rule.description}")

        return "\n".join(lines)
```

**Template Update**: `.claude/agents/python-developer.md`

```markdown
# Python Developer Agent

## Role
Expert Python developer specializing in backend development.

## Capabilities
- Python 3.10+ development
- Type hints and Pydantic models
- Pytest testing
- Database integration

{{RULES_SECTION}}  <!-- Rules injected here -->

## Workflow
1. Read task requirements
2. Implement solution
3. Write tests
4. Submit for review
```

---

### 6.4 Long-Term Fix: Rules in 6W HOW Dimension

**File**: `agentpm/core/context/merger.py`

```python
def merge_hierarchical(
    self,
    project_6w: Optional[UnifiedSixW],
    work_item_6w: Optional[UnifiedSixW],
    task_6w: Optional[UnifiedSixW],
    project_id: Optional[int] = None  # NEW
) -> UnifiedSixW:
    """Merge 6W contexts hierarchically with rules injection."""

    # Existing merge logic...
    merged = self._merge_6w_contexts(project_6w, work_item_6w, task_6w)

    # NEW: Inject rules into HOW dimension
    if project_id:
        rules = self._load_project_rules(project_id)

        # Add rules to HOW dimension as governance constraints
        if merged.how is None:
            merged.how = {}

        merged.how['governance_rules'] = [
            {
                'rule_id': r.rule_id,
                'enforcement_level': r.enforcement_level.value,
                'description': r.description
            }
            for r in rules
        ]

    return merged
```

---

## 7. Implementation Priority

### P0 (Critical): Add Rules to ContextPayload
- **Effort**: 4 hours
- **Impact**: Agents see rules during task execution
- **Files**: `context/assembly_service.py`, `context/models.py`

### P1 (High): Rule Filtering by Capability
- **Effort**: 6 hours
- **Impact**: Agents only see relevant rules (cognitive load reduction)
- **Files**: `context/role_filter.py`, `database/methods/rules.py`

### P2 (Medium): Inject Rules into Agent SOPs
- **Effort**: 8 hours
- **Impact**: Rules embedded in agent instructions
- **Files**: `agents/builder.py`, `.claude/agents/*.md` (templates)

### P3 (Low): Rules in 6W HOW Dimension
- **Effort**: 6 hours
- **Impact**: Rules integrated into technical context
- **Files**: `context/merger.py`

---

## 8. Testing Strategy

### Unit Tests
```python
def test_context_payload_includes_rules():
    """Verify rules are included in context payload."""
    service = ContextAssemblyService(db, project_path)
    context = service.assemble_task_context(task_id=355)

    assert 'applicable_rules' in context
    assert len(context['applicable_rules']) > 0
    assert context['applicable_rules'][0]['rule_id'] == 'DP-001'

def test_rule_filtering_by_capability():
    """Verify rules are filtered by agent capability."""
    filter = RuleFilter(db)

    # Python developer should see Python rules
    python_rules = filter.filter_rules(project_id=1, agent_role='python-developer', all_rules=rules)
    assert any(r.category == 'development_principles' for r in python_rules)

    # Frontend developer should NOT see database rules
    frontend_rules = filter.filter_rules(project_id=1, agent_role='frontend-developer', all_rules=rules)
    assert not any(r.category == 'database_standards' for r in frontend_rules)
```

### Integration Tests
```python
def test_agent_sop_includes_rules():
    """Verify agent SOPs include project rules."""
    builder = AgentSOPBuilder(db)
    sop = builder.build_sop(project_id=1, agent_role='python-developer', template_path=template)

    assert '## Project Rules' in sop
    assert 'DP-001' in sop  # Time-boxing rule
    assert 'DP-012' in sop  # Test coverage rule

def test_workflow_enforcement_with_context():
    """Verify workflow enforcement matches context rules."""
    # Create task that violates rule
    task = Task(effort_hours=6.0, type=TaskType.IMPLEMENTATION)

    # Attempt transition (should fail)
    with pytest.raises(WorkflowError) as exc:
        workflow.transition_task(task.id, TaskStatus.ACTIVE)

    assert 'DP-001' in str(exc.value)  # Time-boxing rule violation
```

---

## 9. Documentation Updates

### 9.1 Update: Context Assembly Documentation
**File**: `docs/components/context/context-assembly-service.md`

Add section:
```markdown
### Step 11: Load Applicable Rules

Context assembly includes project governance rules filtered by agent capabilities:

- Loads enabled rules from database
- Filters by agent role (e.g., python-developer sees Python/testing rules)
- Includes enforcement levels (BLOCK, LIMIT, GUIDE, ENHANCE)
- Adds to `ContextPayload.applicable_rules` field
```

### 9.2 Update: Agent SOP Documentation
**File**: `docs/components/agents/agent-builder-guide.md`

Add section:
```markdown
## Rules Integration

Agent SOPs include project-specific rules:

- **Template Variable**: `{{RULES_SECTION}}`
- **Auto-Generated**: Rules section built from database
- **Filtering**: Only relevant rules shown (by capability)
- **Enforcement Levels**: Clearly marked (BLOCK, LIMIT, GUIDE)
```

---

## 10. Conclusion

**Current State**:
- ✅ Rules are enforced at workflow transitions (robust)
- ❌ Rules are NOT visible to agents during task execution
- ❌ Agents must manually call `apm rules list` to discover rules
- ⚠️ Agent SOPs are static and don't include project rules

**Required Changes**:
1. Add `applicable_rules` to ContextPayload (P0, 4h)
2. Implement rule filtering by capability (P1, 6h)
3. Generate agent SOPs with rules (P2, 8h)
4. Inject rules into 6W HOW dimension (P3, 6h)

**Total Effort**: ~24 hours

**Expected Outcome**: Agents will see rules automatically during task execution, reducing rule violations and improving compliance.
