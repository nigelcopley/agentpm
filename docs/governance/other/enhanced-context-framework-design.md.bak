# Enhanced Work Item Context Framework Design

**Version**: 1.0
**Date**: 2025-10-17
**Status**: PROPOSED

## Executive Summary

This document proposes an enhanced work item context framework that goes beyond the basic 6W model (15 fields) to capture complete work understanding through **aspect-oriented context composition**. The recommended approach (Option C) provides a core 6W baseline with five optional context aspects that are required based on work type, phase, and complexity.

**Key Benefits**:
- **Agent Effectiveness**: 40-60% improvement in decision quality (estimated)
- **Context Completeness**: Captures discovery, decisions, risks, quality, and stakeholders
- **Flexibility**: Aspects compose based on work characteristics
- **Queryability**: Hybrid storage enables both structured queries and flexible evolution
- **Migration Path**: Non-breaking transition from current unified_six_w

---

## Current State Analysis

### UnifiedSixW Structure (15 fields)

```python
class UnifiedSixW(BaseModel):
    # WHO (3 fields)
    end_users: List[str]           # Who will use/benefit
    implementers: List[str]        # Who will build
    reviewers: List[str]           # Who will validate

    # WHAT (3 fields)
    functional_requirements: str   # What functionality
    technical_constraints: str     # What limitations
    acceptance_criteria: List[str] # What defines done

    # WHERE (3 fields)
    affected_services: List[str]   # Where changes occur
    repositories: List[str]        # Where code lives
    deployment_targets: List[str]  # Where deployed

    # WHEN (2 fields)
    deadline: Optional[str]        # When needed
    dependencies_timeline: str     # When dependencies resolve

    # WHY (2 fields)
    business_value: str            # Why doing this
    risk_if_delayed: str           # Why now

    # HOW (2 fields)
    suggested_approach: str        # How to implement
    existing_patterns: List[str]   # How similar work done
```

### Limitations Identified

1. **Missing Discovery Context**: No place for user research, market analysis, technical spikes
2. **No Decision Trail**: Can't capture alternatives considered, trade-offs analyzed
3. **Shallow Risk Context**: Only "risk_if_delayed", no risk register or mitigations
4. **Implicit Quality Context**: Acceptance criteria scattered, no test strategy or success metrics
5. **Limited Stakeholder Context**: Only end_users, no stakeholder management info

---

## Enhancement Proposal: Five Context Aspects

### 1. Discovery Context

**Purpose**: Capture research and learning that informed the work

```python
class DiscoveryContext(BaseModel):
    """Evidence gathered during discovery phase"""

    user_research: List[ResearchItem]
    """User interviews, surveys, feedback sessions"""

    market_analysis: List[MarketInsight]
    """Competitor analysis, market trends, positioning"""

    technical_discovery: List[TechnicalSpike]
    """POCs, prototypes, feasibility studies"""

    constraints: List[Constraint]
    """Budget, timeline, resource, regulatory constraints"""

    confidence_level: float  # 0.0-1.0
    """How confident are we in the discovery?"""

    gaps_identified: List[str]
    """What we still don't know"""

class ResearchItem(BaseModel):
    source: str              # "User interview with John"
    method: str              # "Interview", "Survey", "Analytics"
    finding: str             # Key insight (≤100 words)
    evidence_url: Optional[str]
    date: str
    confidence: float

class MarketInsight(BaseModel):
    competitor: Optional[str]
    trend: str
    implication: str
    source: str
    date: str

class TechnicalSpike(BaseModel):
    question: str            # What we investigated
    approach: str            # How we investigated
    finding: str             # What we learned
    code_url: Optional[str]  # Link to POC
    date: str

class Constraint(BaseModel):
    type: str                # "budget", "timeline", "resource", "regulatory"
    description: str
    severity: str            # "soft", "hard"
    source: str              # Who imposed constraint
```

**Required For**: FEATURE (DEFINITION phase), ANALYSIS (always)
**Optional For**: TECHNICAL_IMPROVEMENT, OBJECTIVE
**Skip For**: BUG (discovery is minimal)

---

### 2. Decision Trail Context

**Purpose**: Capture architectural and approach decisions with rationale

```python
class DecisionTrailContext(BaseModel):
    """History of key decisions and their rationale"""

    decisions_made: List[Decision]
    """Decisions finalized"""

    alternatives_considered: List[Alternative]
    """Options evaluated but not chosen"""

    trade_offs: List[TradeOff]
    """Pros/cons analysis"""

    assumptions: List[Assumption]
    """Key assumptions documented"""

    adr_references: List[str]
    """Links to Architecture Decision Records"""

class Decision(BaseModel):
    id: str                  # "DEC-001"
    title: str               # "Use PostgreSQL over MongoDB"
    rationale: str           # Why this decision (≤200 words)
    decided_by: str          # Who made decision
    decided_at: str          # When
    impacts: List[str]       # What this affects
    reversibility: str       # "easy", "costly", "irreversible"

class Alternative(BaseModel):
    option: str              # "MongoDB"
    pros: List[str]
    cons: List[str]
    why_rejected: str        # Specific reason

class TradeOff(BaseModel):
    dimension: str           # "Performance vs Maintainability"
    choice: str              # Which side we chose
    justification: str       # Why
    measurement: Optional[str] # How we'll validate

class Assumption(BaseModel):
    statement: str           # "Users have stable internet"
    confidence: float        # 0.0-1.0
    validation_plan: str     # How we'll test assumption
    risk_if_wrong: str       # Impact if assumption false
```

**Required For**: FEATURE (PLANNING phase), TECHNICAL_IMPROVEMENT (always)
**Optional For**: ANALYSIS, OBJECTIVE
**Skip For**: BUG (decisions are tactical)

---

### 3. Risk Context

**Purpose**: Comprehensive risk identification, assessment, and mitigation

```python
class RiskContext(BaseModel):
    """Risk register and mitigation strategies"""

    identified_risks: List[Risk]
    """All known risks"""

    mitigations: List[Mitigation]
    """Risk reduction strategies"""

    dependencies: List[Dependency]
    """External dependencies that could block"""

    blockers: List[Blocker]
    """Current and historical blockers"""

    risk_score: float  # 0.0-1.0 (computed)
    """Overall risk level"""

class Risk(BaseModel):
    id: str                  # "RISK-001"
    category: str            # "technical", "resource", "schedule", "quality"
    description: str
    probability: float       # 0.0-1.0
    impact: float            # 0.0-1.0
    score: float             # probability × impact
    status: str              # "identified", "mitigated", "accepted", "occurred"

class Mitigation(BaseModel):
    risk_id: str             # Which risk this addresses
    strategy: str            # "avoid", "reduce", "transfer", "accept"
    action: str              # Specific mitigation action
    owner: str               # Who responsible
    effectiveness: float     # 0.0-1.0 (how much risk reduced)

class Dependency(BaseModel):
    id: str                  # "DEP-001"
    type: str                # "work_item", "external_team", "vendor", "regulation"
    description: str
    owner: str               # Who owns dependency
    status: str              # "pending", "in_progress", "resolved", "blocked"
    impact_if_delayed: str
    alternative_plan: Optional[str]

class Blocker(BaseModel):
    id: str                  # "BLOCK-001"
    description: str
    identified_at: str
    resolved_at: Optional[str]
    resolution: Optional[str]
    impact: str              # How much delay caused
```

**Required For**: All work types except low-risk bugs
**Triggers**: risk_score > 0.5, effort > 8 hours, external dependencies present

---

### 4. Quality Context

**Purpose**: Define what "done" means and how to validate

```python
class QualityContext(BaseModel):
    """Quality requirements and validation strategy"""

    acceptance_criteria: List[AcceptanceCriterion]
    """Testable criteria (from unified_six_w, enhanced)"""

    success_metrics: List[Metric]
    """How we measure success"""

    quality_standards: List[Standard]
    """Quality requirements beyond functional"""

    test_strategy: TestStrategy
    """Testing approach"""

    quality_gates: List[QualityGate]
    """Gates that must pass"""

class AcceptanceCriterion(BaseModel):
    id: str                  # "AC-001"
    description: str         # Given/When/Then format
    priority: str            # "must", "should", "could"
    testable: bool
    test_reference: Optional[str]  # Link to test case

class Metric(BaseModel):
    name: str                # "Page load time"
    target: str              # "< 2 seconds"
    measurement_method: str  # How we measure
    baseline: Optional[str]  # Current state
    importance: str          # "critical", "important", "nice-to-have"

class Standard(BaseModel):
    category: str            # "performance", "security", "accessibility", "maintainability"
    requirement: str         # Specific standard
    validation_method: str   # How we check
    tools: List[str]         # Tools used to validate

class TestStrategy(BaseModel):
    unit_testing: str        # Approach
    integration_testing: str
    e2e_testing: str
    performance_testing: str
    security_testing: str
    coverage_target: float   # 0.0-1.0
    automation_level: str    # "full", "partial", "manual"

class QualityGate(BaseModel):
    gate_id: str             # "CI-004"
    description: str
    criteria: List[str]      # What must pass
    automated: bool
    enforcement: str         # "blocking", "warning"
```

**Required For**: All work types (varies by complexity)
**Minimal For**: Simple bugs (only acceptance_criteria)
**Comprehensive For**: FEATURE, TECHNICAL_IMPROVEMENT

---

### 5. Stakeholder Context

**Purpose**: Manage communication and approvals

```python
class StakeholderContext(BaseModel):
    """Stakeholder management and communication"""

    stakeholders: List[Stakeholder]
    """All interested parties"""

    communication_plan: CommunicationPlan
    """How to keep stakeholders informed"""

    approval_chain: List[ApprovalRequirement]
    """Who needs to approve what"""

    feedback_log: List[Feedback]
    """Stakeholder input received"""

class Stakeholder(BaseModel):
    name: str
    role: str                # "sponsor", "user", "reviewer", "observer"
    interest: str            # "high", "medium", "low"
    influence: str           # "high", "medium", "low"
    concerns: List[str]      # Their specific concerns
    preferred_communication: str  # "email", "slack", "demo"

class CommunicationPlan(BaseModel):
    frequency: str           # "weekly", "at milestones", "on request"
    method: str              # "dashboard", "email", "meetings"
    content: str             # What to share
    owner: str               # Who responsible for communication

class ApprovalRequirement(BaseModel):
    phase: str               # "DEFINITION", "PLANNING", "IMPLEMENTATION", etc.
    approver: str            # Who must approve
    criteria: str            # What they're approving
    type: str                # "formal", "informal"

class Feedback(BaseModel):
    stakeholder: str
    date: str
    feedback: str
    action_taken: Optional[str]
    status: str              # "open", "addressed", "deferred"
```

**Required For**: FEATURE (with external stakeholders), OBJECTIVE (always)
**Optional For**: ANALYSIS, TECHNICAL_IMPROVEMENT
**Minimal For**: BUG (usually just reviewers)

---

## Three Design Options

### Option A: Extend UnifiedSixW (Monolithic)

**Approach**: Add all new fields directly to UnifiedSixW structure

```python
class ExtendedUnifiedSixW(BaseModel):
    # Original 15 fields
    end_users: List[str]
    implementers: List[str]
    # ... (all original fields)

    # New fields (25+ additional)
    user_research: List[ResearchItem]
    market_analysis: List[MarketInsight]
    decisions_made: List[Decision]
    identified_risks: List[Risk]
    acceptance_criteria: List[AcceptanceCriterion]
    stakeholders: List[Stakeholder]
    # ... (40+ total fields)
```

**Pros**:
- ✅ Simple conceptually (one structure)
- ✅ Backward compatible (just add fields)
- ✅ Easy to query (all in one place)
- ✅ No relationship management needed

**Cons**:
- ❌ Monolithic (40+ fields, hard to navigate)
- ❌ Rigid (same structure for all work types)
- ❌ Hard to evolve (adding aspects requires schema changes)
- ❌ Poor separation of concerns (mixing discovery with execution)
- ❌ Always loads all data (performance impact)
- ❌ Forces population of irrelevant fields

**Verdict**: ❌ **Not Recommended** - Creates unwieldy structure that doesn't adapt to work type

---

### Option B: Composite Context (Separate Structures)

**Approach**: Core 6W + separate context objects joined by work_item_id

```python
class WorkItemContext(BaseModel):
    work_item_id: int
    unified_six_w: UnifiedSixW  # Core context
    discovery_context: Optional[DiscoveryContext]
    decision_context: Optional[DecisionTrailContext]
    risk_context: Optional[RiskContext]
    quality_context: Optional[QualityContext]
    stakeholder_context: Optional[StakeholderContext]
```

**Storage**:
```sql
-- Separate tables
work_items (id, title, type, phase, ...)
work_item_six_w (work_item_id, end_users, implementers, ...)
work_item_discovery (work_item_id, user_research, market_analysis, ...)
work_item_decisions (work_item_id, decisions_made, alternatives, ...)
work_item_risks (work_item_id, identified_risks, mitigations, ...)
work_item_quality (work_item_id, acceptance_criteria, success_metrics, ...)
work_item_stakeholders (work_item_id, stakeholders, communication_plan, ...)
```

**Pros**:
- ✅ Clean separation of concerns
- ✅ Can evolve independently (add new context tables)
- ✅ Can omit unused contexts (NULL foreign keys)
- ✅ Clear responsibility (each context has purpose)
- ✅ Can load contexts on demand (lazy loading)

**Cons**:
- ❌ Multiple tables to manage (6+ tables)
- ❌ Complex queries (join across tables)
- ❌ Need to define relationships
- ❌ Agents need to know which context to query
- ❌ More database operations (separate inserts/updates)

**Verdict**: ✅ **Good Option** - Clean architecture, but might be over-engineered for AIPM's scale

---

### Option C: Aspect-Oriented Context (Recommended)

**Approach**: Core 6W mandatory + optional aspects based on work type, phase, and complexity

```python
class WorkItemContext(BaseModel):
    """Core + composable aspects"""
    work_item_id: int

    # Core (always present)
    core: UnifiedSixW

    # Aspects (conditional based on work type/phase)
    aspects: Dict[str, Any]  # Flexible aspect storage

    # Aspect metadata
    required_aspects: List[str]  # Which aspects are required
    populated_aspects: List[str]  # Which aspects are populated

    def has_aspect(self, name: str) -> bool:
        return name in self.populated_aspects

    def get_aspect(self, name: str, aspect_class: Type[T]) -> Optional[T]:
        if name in self.aspects:
            return aspect_class(**self.aspects[name])
        return None
```

**Storage** (Hybrid):
```sql
-- Core in work_items table
work_items (
    id, title, type, phase, status,
    unified_six_w TEXT  -- JSON (existing)
)

-- Aspects in flexible table
work_item_contexts (
    id,
    work_item_id INTEGER REFERENCES work_items(id),
    aspect_type TEXT,  -- "discovery", "decision", "risk", "quality", "stakeholder"
    aspect_data TEXT,  -- JSONB (SQLite JSON)
    populated_at TEXT,
    populated_by TEXT,
    version INTEGER
)

-- Indexes for queryability
CREATE INDEX idx_aspect_type ON work_item_contexts(aspect_type);
CREATE INDEX idx_work_item_aspects ON work_item_contexts(work_item_id, aspect_type);
```

**Aspect Requirement Matrix**:

```python
ASPECT_REQUIREMENTS = {
    # (work_type, phase) -> required_aspects[]
    ("FEATURE", "DEFINITION"): ["discovery", "stakeholder"],
    ("FEATURE", "PLANNING"): ["discovery", "decision", "risk", "stakeholder"],
    ("FEATURE", "IMPLEMENTATION"): ["decision", "risk", "quality"],
    ("FEATURE", "REVIEW"): ["quality", "risk"],

    ("ANALYSIS", "DEFINITION"): ["discovery", "stakeholder"],
    ("ANALYSIS", "IN_PROGRESS"): ["discovery", "decision"],

    ("TECHNICAL_IMPROVEMENT", "PLANNING"): ["decision", "risk"],
    ("TECHNICAL_IMPROVEMENT", "IMPLEMENTATION"): ["decision", "quality"],

    ("BUG", "IN_PROGRESS"): ["quality"],  # Minimal
    ("BUG", "REVIEW"): ["quality"],

    ("OBJECTIVE", "DEFINITION"): ["stakeholder", "decision"],
    ("OBJECTIVE", "PLANNING"): ["stakeholder", "decision", "risk"],
}

# Also consider risk level and effort
def get_required_aspects(work_item: WorkItem) -> List[str]:
    base_aspects = ASPECT_REQUIREMENTS.get(
        (work_item.type, work_item.phase),
        []
    )

    # Add risk context if high risk or complex
    if work_item.risk_level == "HIGH" or work_item.effort_hours > 8:
        if "risk" not in base_aspects:
            base_aspects.append("risk")

    # Add quality context if effort > 4 hours
    if work_item.effort_hours > 4 and "quality" not in base_aspects:
        base_aspects.append("quality")

    return base_aspects
```

**Usage Example**:

```python
# Create work item with aspects
context = WorkItemContext(
    work_item_id=355,
    core=UnifiedSixW(...),  # Always populated
    aspects={
        "discovery": DiscoveryContext(...).dict(),
        "decision": DecisionTrailContext(...).dict(),
    },
    required_aspects=["discovery", "decision", "risk"],
    populated_aspects=["discovery", "decision"]  # risk still missing
)

# Query aspect
if context.has_aspect("discovery"):
    discovery = context.get_aspect("discovery", DiscoveryContext)
    print(f"Confidence: {discovery.confidence_level}")

# Validate completeness
missing = set(context.required_aspects) - set(context.populated_aspects)
if missing:
    print(f"Missing aspects: {missing}")  # ["risk"]
```

**Pros**:
- ✅ Core 6W always present (backward compatible)
- ✅ Flexible aspect composition (adapts to work type)
- ✅ Natural evolution path (add aspects over time)
- ✅ Clear requirement rules (matrix defines when aspects needed)
- ✅ Queryable (indexes on aspect_type)
- ✅ Lazy loading (load aspects on demand)
- ✅ Validation built-in (required vs populated)
- ✅ Storage efficient (only store populated aspects)

**Cons**:
- ⚠️ Need to define aspect requirements carefully
- ⚠️ Agents need to check has_aspect() before using
- ⚠️ JSONB querying less efficient than structured columns (acceptable trade-off)

**Verdict**: ✅ **RECOMMENDED** - Best balance of flexibility, queryability, and evolution

---

## Recommended Approach: Option C (Aspect-Oriented)

### Why Option C Wins

1. **Agent Effectiveness**: Agents get exactly the context they need for each work type/phase
2. **Flexibility**: Easy to add new aspects without schema changes
3. **Storage Efficiency**: Only store what's populated (no NULL columns)
4. **Queryability**: Indexes on aspect_type + JSONB expressions
5. **Evolution**: Can introduce new aspects without breaking existing work items
6. **Validation**: Built-in completeness checking (required vs populated)

### Implementation Details

#### Database Schema

```sql
-- Existing work_items table (add aspect tracking)
ALTER TABLE work_items
ADD COLUMN required_aspects TEXT;  -- JSON array ["discovery", "decision"]

-- New work_item_contexts table
CREATE TABLE work_item_contexts (
    id INTEGER PRIMARY KEY,
    work_item_id INTEGER NOT NULL,
    aspect_type TEXT NOT NULL,  -- "discovery" | "decision" | "risk" | "quality" | "stakeholder"
    aspect_data TEXT NOT NULL,  -- JSON blob
    populated_at TEXT NOT NULL,
    populated_by TEXT,
    version INTEGER DEFAULT 1,

    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
    UNIQUE (work_item_id, aspect_type)  -- One aspect per work item
);

CREATE INDEX idx_aspect_type ON work_item_contexts(aspect_type);
CREATE INDEX idx_work_item_aspects ON work_item_contexts(work_item_id, aspect_type);
```

#### Pydantic Models

```python
# agentpm/core/database/models/context.py

class AspectType(str, Enum):
    DISCOVERY = "discovery"
    DECISION = "decision"
    RISK = "risk"
    QUALITY = "quality"
    STAKEHOLDER = "stakeholder"

class WorkItemContextModel(BaseModel):
    """Database model for work item context"""
    id: Optional[int] = None
    work_item_id: int
    aspect_type: AspectType
    aspect_data: Dict[str, Any]  # Serialized aspect
    populated_at: str
    populated_by: Optional[str]
    version: int = 1

class WorkItemContextService:
    """Service for managing work item contexts"""

    def get_aspect(
        self,
        work_item_id: int,
        aspect_type: AspectType,
        aspect_class: Type[T]
    ) -> Optional[T]:
        """Retrieve and deserialize an aspect"""
        row = self.db.execute(
            "SELECT aspect_data FROM work_item_contexts "
            "WHERE work_item_id = ? AND aspect_type = ?",
            (work_item_id, aspect_type.value)
        ).fetchone()

        if row:
            return aspect_class(**json.loads(row[0]))
        return None

    def set_aspect(
        self,
        work_item_id: int,
        aspect: Union[DiscoveryContext, DecisionTrailContext, ...]
    ) -> None:
        """Store an aspect"""
        aspect_type = self._get_aspect_type(aspect)
        self.db.execute(
            "INSERT OR REPLACE INTO work_item_contexts "
            "(work_item_id, aspect_type, aspect_data, populated_at) "
            "VALUES (?, ?, ?, ?)",
            (
                work_item_id,
                aspect_type.value,
                json.dumps(aspect.dict()),
                datetime.now().isoformat()
            )
        )

    def get_required_aspects(self, work_item: WorkItem) -> List[AspectType]:
        """Determine which aspects are required"""
        return ASPECT_REQUIREMENTS.get(
            (work_item.type, work_item.phase),
            []
        )

    def validate_completeness(self, work_item_id: int) -> Dict[str, Any]:
        """Check if all required aspects are populated"""
        work_item = self.work_item_service.get(work_item_id)
        required = self.get_required_aspects(work_item)

        populated = [
            AspectType(row[0])
            for row in self.db.execute(
                "SELECT aspect_type FROM work_item_contexts "
                "WHERE work_item_id = ?",
                (work_item_id,)
            ).fetchall()
        ]

        missing = set(required) - set(populated)

        return {
            "complete": len(missing) == 0,
            "required": [a.value for a in required],
            "populated": [a.value for a in populated],
            "missing": [a.value for a in missing]
        }
```

#### Query Examples

```python
# Find all FEATUREs with high-risk contexts
high_risk_features = db.execute("""
    SELECT wi.id, wi.title, wic.aspect_data
    FROM work_items wi
    JOIN work_item_contexts wic ON wi.id = wic.work_item_id
    WHERE wi.type = 'FEATURE'
      AND wic.aspect_type = 'risk'
      AND json_extract(wic.aspect_data, '$.risk_score') > 0.7
""").fetchall()

# Find work items missing required aspects
incomplete_work = db.execute("""
    SELECT wi.id, wi.title, wi.required_aspects
    FROM work_items wi
    WHERE wi.required_aspects IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM work_item_contexts wic
          WHERE wic.work_item_id = wi.id
            AND wic.aspect_type IN (
                SELECT value FROM json_each(wi.required_aspects)
            )
          GROUP BY wic.work_item_id
          HAVING COUNT(DISTINCT wic.aspect_type) = json_array_length(wi.required_aspects)
      )
""").fetchall()

# Get all aspects for a work item
all_contexts = db.execute("""
    SELECT aspect_type, aspect_data
    FROM work_item_contexts
    WHERE work_item_id = ?
""", (355,)).fetchall()
```

---

## Migration Strategy

### Phase 1: Foundation (Non-Breaking)

**Goal**: Add new tables and models without disrupting existing system

**Actions**:
1. Create `work_item_contexts` table
2. Add `required_aspects` column to `work_items`
3. Implement `WorkItemContextService`
4. Add aspect models (DiscoveryContext, DecisionTrailContext, etc.)
5. Keep `unified_six_w` unchanged

**Timeline**: 1 week
**Risk**: Low (additive changes only)

```python
# Migration script
def migration_0023_add_context_aspects():
    db.execute("""
        CREATE TABLE work_item_contexts (
            id INTEGER PRIMARY KEY,
            work_item_id INTEGER NOT NULL,
            aspect_type TEXT NOT NULL,
            aspect_data TEXT NOT NULL,
            populated_at TEXT NOT NULL,
            populated_by TEXT,
            version INTEGER DEFAULT 1,
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
            UNIQUE (work_item_id, aspect_type)
        )
    """)

    db.execute("CREATE INDEX idx_aspect_type ON work_item_contexts(aspect_type)")
    db.execute("CREATE INDEX idx_work_item_aspects ON work_item_contexts(work_item_id, aspect_type)")

    db.execute("ALTER TABLE work_items ADD COLUMN required_aspects TEXT")
```

### Phase 2: Parallel Run

**Goal**: Support both old and new context systems simultaneously

**Actions**:
1. Update CLI commands to optionally populate aspects
2. Add `apm context add-aspect` command
3. Create aspect population tools for existing work items
4. Update agent prompts to check for aspects
5. APIs return both `unified_six_w` and `aspects`

**Timeline**: 2-3 weeks
**Risk**: Medium (dual system complexity)

```bash
# New CLI commands
apm context add-aspect discovery --work-item 355 --interactive
apm context add-aspect decision --work-item 355 --from-file decision.yaml
apm context show --work-item 355 --aspects  # Show all aspects
apm context validate --work-item 355  # Check completeness
```

```python
# Agent usage (backward compatible)
def get_work_context(work_item_id: int) -> Dict:
    """Get context with fallback to unified_six_w"""
    context = {
        "core": work_item.unified_six_w,  # Always available
        "aspects": {}
    }

    # Try to load aspects
    for aspect_type in AspectType:
        aspect = context_service.get_aspect(work_item_id, aspect_type)
        if aspect:
            context["aspects"][aspect_type.value] = aspect

    return context
```

### Phase 3: Deprecation

**Goal**: Make aspects primary, unified_six_w computed/readonly

**Actions**:
1. `unified_six_w` becomes computed from aspects
2. New APIs only use aspects
3. Old format marked deprecated
4. Migration tool for remaining unified_six_w data

**Timeline**: 4-6 weeks
**Risk**: Low (gradual transition)

```python
# Computed unified_six_w (for backward compatibility)
@property
def unified_six_w(self) -> UnifiedSixW:
    """Compute from aspects for backward compatibility"""
    core = self._get_core_six_w()

    # Enhance from aspects if available
    if self.has_aspect("quality"):
        quality = self.get_aspect("quality", QualityContext)
        core.acceptance_criteria = [
            ac.description for ac in quality.acceptance_criteria
        ]

    if self.has_aspect("stakeholder"):
        stakeholder = self.get_aspect("stakeholder", StakeholderContext)
        core.end_users = [s.name for s in stakeholder.stakeholders if s.role == "user"]
        core.reviewers = [s.name for s in stakeholder.stakeholders if s.role == "reviewer"]

    return core
```

---

## Example Populated Contexts

### Example 1: FEATURE Work Item (Full Context)

```python
# Work Item: "Add OAuth2 Authentication"
# Type: FEATURE, Phase: PLANNING

# Core (unified_six_w - always present)
core = UnifiedSixW(
    end_users=["Application users", "API consumers"],
    implementers=["Backend team", "Security team"],
    reviewers=["Security architect", "Tech lead"],
    functional_requirements="Support OAuth2 authentication for web and API access",
    technical_constraints="Must integrate with existing Auth0 tenant, GDPR compliant",
    acceptance_criteria=[
        "Users can log in via Google and GitHub",
        "API requests authenticated with JWT tokens",
        "Token refresh works without re-authentication"
    ],
    affected_services=["auth-service", "api-gateway", "user-service"],
    repositories=["backend-api", "auth-lib"],
    deployment_targets=["staging", "production"],
    deadline="2025-11-15",
    dependencies_timeline="Auth0 tenant available by 2025-10-25",
    business_value="Reduce friction in user onboarding, improve security",
    risk_if_delayed="Delayed product launch, security audit failure",
    suggested_approach="Use passport.js with OAuth2 strategy",
    existing_patterns=["social-login-service pattern", "JWT middleware pattern"]
)

# Discovery Aspect
discovery = DiscoveryContext(
    user_research=[
        ResearchItem(
            source="User interviews (n=15)",
            method="Interview",
            finding="80% prefer social login over email/password, Google most requested",
            evidence_url="https://docs.example.com/user-research-2025-09",
            date="2025-09-15",
            confidence=0.85
        ),
        ResearchItem(
            source="Analytics: registration funnel",
            method="Analytics",
            finding="40% drop-off at email verification step",
            date="2025-09-20",
            confidence=0.95
        )
    ],
    market_analysis=[
        MarketInsight(
            competitor="Competitor A",
            trend="Offers Google, GitHub, Microsoft login",
            implication="Must match feature parity",
            source="Competitor analysis doc",
            date="2025-09-10"
        )
    ],
    technical_discovery=[
        TechnicalSpike(
            question="Can we integrate Auth0 with existing user model?",
            approach="Built POC with test Auth0 tenant",
            finding="Integration works, requires user.auth0_id field",
            code_url="https://github.com/example/auth-poc",
            date="2025-09-25"
        )
    ],
    constraints=[
        Constraint(
            type="regulatory",
            description="Must comply with GDPR for EU users",
            severity="hard",
            source="Legal team"
        ),
        Constraint(
            type="timeline",
            description="Launch dependent on Q4 product release",
            severity="soft",
            source="Product manager"
        )
    ],
    confidence_level=0.82,
    gaps_identified=["Token refresh UX not validated", "Error handling patterns unclear"]
)

# Decision Trail Aspect
decision = DecisionTrailContext(
    decisions_made=[
        Decision(
            id="DEC-001",
            title="Use Auth0 over self-hosted OAuth",
            rationale="Auth0 provides managed service with security updates, reduces operational burden, faster time-to-market",
            decided_by="Tech lead + Security architect",
            decided_at="2025-09-28",
            impacts=["auth-service", "infrastructure costs", "vendor dependency"],
            reversibility="costly"
        ),
        Decision(
            id="DEC-002",
            title="Support Google and GitHub initially",
            rationale="User research shows 95% preference for these two providers, reduces initial scope",
            decided_by="Product manager",
            decided_at="2025-09-30",
            impacts=["implementation timeline", "user satisfaction"],
            reversibility="easy"
        )
    ],
    alternatives_considered=[
        Alternative(
            option="Self-hosted OAuth server (Keycloak)",
            pros=["Full control", "No vendor lock-in", "Lower long-term cost"],
            cons=["Operational complexity", "Security maintenance burden", "Slower delivery"],
            why_rejected="Team lacks OAuth expertise, security risk too high"
        ),
        Alternative(
            option="Social login libraries (passport.js alone)",
            pros=["Lower cost", "More control"],
            cons=["More code to maintain", "Security updates manual", "Complex token management"],
            why_rejected="Doesn't scale, Auth0 provides better security guarantees"
        )
    ],
    trade_offs=[
        TradeOff(
            dimension="Cost vs Control",
            choice="Chose Auth0 (higher cost, less control)",
            justification="Security and speed to market outweigh cost concerns",
            measurement="Monitor Auth0 costs monthly"
        )
    ],
    assumptions=[
        Assumption(
            statement="Users have Google or GitHub accounts",
            confidence=0.90,
            validation_plan="Track login method usage after launch",
            risk_if_wrong="Need to add more providers (email/password fallback)"
        )
    ],
    adr_references=["ADR-012-oauth2-authentication.md"]
)

# Risk Aspect
risk = RiskContext(
    identified_risks=[
        Risk(
            id="RISK-001",
            category="technical",
            description="Auth0 API rate limits could block logins during peak traffic",
            probability=0.3,
            impact=0.8,
            score=0.24,
            status="identified"
        ),
        Risk(
            id="RISK-002",
            category="security",
            description="Token leakage if not stored securely in browser",
            probability=0.4,
            impact=0.9,
            score=0.36,
            status="mitigated"
        ),
        Risk(
            id="RISK-003",
            category="schedule",
            description="Auth0 tenant setup delayed by procurement",
            probability=0.5,
            impact=0.6,
            score=0.30,
            status="mitigated"
        )
    ],
    mitigations=[
        Mitigation(
            risk_id="RISK-001",
            strategy="reduce",
            action="Implement caching layer for token validation, upgrade Auth0 plan",
            owner="Backend lead",
            effectiveness=0.7
        ),
        Mitigation(
            risk_id="RISK-002",
            strategy="avoid",
            action="Use httpOnly cookies, implement CSP headers, security review",
            owner="Security architect",
            effectiveness=0.9
        ),
        Mitigation(
            risk_id="RISK-003",
            strategy="reduce",
            action="Parallel track: setup test tenant while procurement ongoing",
            owner="DevOps",
            effectiveness=0.8
        )
    ],
    dependencies=[
        Dependency(
            id="DEP-001",
            type="vendor",
            description="Auth0 tenant provisioning",
            owner="DevOps team",
            status="in_progress",
            impact_if_delayed="2 week delay to implementation",
            alternative_plan="Use test tenant for development, switch to prod tenant later"
        )
    ],
    blockers=[],
    risk_score=0.30  # Computed: max(risk.score for risk in identified_risks)
)

# Quality Aspect
quality = QualityContext(
    acceptance_criteria=[
        AcceptanceCriterion(
            id="AC-001",
            description="GIVEN unauthenticated user WHEN clicks 'Login with Google' THEN redirected to Google consent screen",
            priority="must",
            testable=True,
            test_reference="test_oauth_google_redirect.py"
        ),
        AcceptanceCriterion(
            id="AC-002",
            description="GIVEN authenticated user WHEN makes API request with valid JWT THEN request succeeds",
            priority="must",
            testable=True,
            test_reference="test_jwt_authentication.py"
        ),
        AcceptanceCriterion(
            id="AC-003",
            description="GIVEN expired JWT WHEN user refreshes page THEN new token issued without re-login",
            priority="must",
            testable=True,
            test_reference="test_token_refresh.py"
        )
    ],
    success_metrics=[
        Metric(
            name="Login success rate",
            target="> 95%",
            measurement_method="Track successful OAuth callbacks vs attempts",
            baseline="N/A (new feature)",
            importance="critical"
        ),
        Metric(
            name="Authentication latency",
            target="< 500ms (p95)",
            measurement_method="APM traces for auth-service",
            baseline="N/A",
            importance="important"
        ),
        Metric(
            name="Social login adoption",
            target="> 70% of new signups",
            measurement_method="Analytics tracking login method",
            baseline="0% (no social login today)",
            importance="important"
        )
    ],
    quality_standards=[
        Standard(
            category="security",
            requirement="OWASP Top 10 compliance",
            validation_method="SAST scan + manual security review",
            tools=["Snyk", "OWASP ZAP"]
        ),
        Standard(
            category="performance",
            requirement="Authentication latency < 500ms p95",
            validation_method="Load testing with k6",
            tools=["k6", "Datadog APM"]
        )
    ],
    test_strategy=TestStrategy(
        unit_testing="Test OAuth callback handling, token validation logic",
        integration_testing="Test Auth0 integration, user creation flow",
        e2e_testing="Test full login flow for Google and GitHub",
        performance_testing="Load test with 1000 concurrent logins",
        security_testing="SAST scan, penetration testing by security team",
        coverage_target=0.90,
        automation_level="full"
    ),
    quality_gates=[
        QualityGate(
            gate_id="CI-004",
            description="Test coverage > 90%",
            criteria=["Unit tests pass", "Integration tests pass", "Coverage report > 90%"],
            automated=True,
            enforcement="blocking"
        ),
        QualityGate(
            gate_id="SEC-001",
            description="Security scan passes",
            criteria=["No high/critical Snyk vulnerabilities", "Security review approved"],
            automated=True,
            enforcement="blocking"
        )
    ]
)

# Stakeholder Aspect
stakeholder = StakeholderContext(
    stakeholders=[
        Stakeholder(
            name="Product Manager",
            role="sponsor",
            interest="high",
            influence="high",
            concerns=["Launch date", "User adoption"],
            preferred_communication="slack"
        ),
        Stakeholder(
            name="Security Architect",
            role="reviewer",
            interest="high",
            influence="high",
            concerns=["GDPR compliance", "Token security"],
            preferred_communication="email"
        ),
        Stakeholder(
            name="Customer Success",
            role="observer",
            interest="medium",
            influence="low",
            concerns=["User support load", "Documentation"],
            preferred_communication="dashboard"
        )
    ],
    communication_plan=CommunicationPlan(
        frequency="weekly",
        method="slack updates + demo at milestones",
        content="Progress, blockers, upcoming milestones",
        owner="Tech lead"
    ),
    approval_chain=[
        ApprovalRequirement(
            phase="DEFINITION",
            approver="Product Manager",
            criteria="Feature scope and acceptance criteria",
            type="informal"
        ),
        ApprovalRequirement(
            phase="PLANNING",
            approver="Security Architect",
            criteria="Security design and compliance approach",
            type="formal"
        ),
        ApprovalRequirement(
            phase="REVIEW",
            approver="Security Architect + Tech Lead",
            criteria="Code review + security scan results",
            type="formal"
        )
    ],
    feedback_log=[
        Feedback(
            stakeholder="Security Architect",
            date="2025-10-01",
            feedback="Ensure tokens stored in httpOnly cookies, not localStorage",
            action_taken="Updated design to use httpOnly cookies",
            status="addressed"
        )
    ]
)
```

### Example 2: BUG Work Item (Minimal Context)

```python
# Work Item: "Fix 500 error on user profile update"
# Type: BUG, Phase: IN_PROGRESS

# Core (simplified for bug)
core = UnifiedSixW(
    end_users=["Application users"],
    implementers=["Backend developer"],
    reviewers=["Tech lead"],
    functional_requirements="Fix 500 Internal Server Error when updating user profile with special characters",
    technical_constraints="Must not break existing profile update functionality",
    acceptance_criteria=[
        "Profile update succeeds with special characters (!@#$%)",
        "No 500 errors in error tracking",
        "Regression tests pass"
    ],
    affected_services=["user-service"],
    repositories=["backend-api"],
    deployment_targets=["production"],
    deadline="2025-10-20",
    dependencies_timeline="None",
    business_value="Prevent user frustration, reduce support tickets",
    risk_if_delayed="Continued user complaints, poor UX",
    suggested_approach="Sanitize input before database update",
    existing_patterns=["input-validation pattern"]
)

# Quality Aspect (only required aspect for bugs)
quality = QualityContext(
    acceptance_criteria=[
        AcceptanceCriterion(
            id="AC-001",
            description="GIVEN user profile with special chars WHEN update submitted THEN succeeds with 200 response",
            priority="must",
            testable=True,
            test_reference="test_profile_update_special_chars.py"
        ),
        AcceptanceCriterion(
            id="AC-002",
            description="GIVEN existing test suite WHEN run THEN all tests pass (no regression)",
            priority="must",
            testable=True,
            test_reference="pytest tests/user_service/"
        )
    ],
    success_metrics=[
        Metric(
            name="500 error rate",
            target="0 errors in production",
            measurement_method="Sentry error tracking",
            baseline="5-10 errors/day",
            importance="critical"
        )
    ],
    quality_standards=[
        Standard(
            category="security",
            requirement="Input sanitization prevents SQL injection",
            validation_method="Security review + SQLi testing",
            tools=["Manual review", "sqlmap"]
        )
    ],
    test_strategy=TestStrategy(
        unit_testing="Test input sanitization function",
        integration_testing="Test profile update API endpoint",
        e2e_testing="Not required for bug fix",
        performance_testing="Not required",
        security_testing="SQLi testing",
        coverage_target=0.90,
        automation_level="full"
    ),
    quality_gates=[
        QualityGate(
            gate_id="CI-004",
            description="Tests pass",
            criteria=["Unit tests pass", "Integration tests pass", "No regressions"],
            automated=True,
            enforcement="blocking"
        )
    ]
)

# No other aspects required for simple bug fix
```

---

## Queryability and Flexibility

### Query Patterns

#### 1. Find High-Risk Features
```python
# SQL
high_risk = db.execute("""
    SELECT wi.id, wi.title, wic.aspect_data
    FROM work_items wi
    JOIN work_item_contexts wic ON wi.id = wic.work_item_id
    WHERE wi.type = 'FEATURE'
      AND wic.aspect_type = 'risk'
      AND json_extract(wic.aspect_data, '$.risk_score') > 0.5
""").fetchall()

# Service
high_risk_features = [
    work_item for work_item in work_items
    if work_item.has_aspect("risk")
    and work_item.get_aspect("risk", RiskContext).risk_score > 0.5
]
```

#### 2. Find Work Missing Required Aspects
```python
incomplete = []
for work_item in active_work_items:
    validation = context_service.validate_completeness(work_item.id)
    if not validation["complete"]:
        incomplete.append({
            "work_item": work_item,
            "missing": validation["missing"]
        })
```

#### 3. Aggregate Discovery Confidence
```python
# Average confidence across all discovery contexts
avg_confidence = db.execute("""
    SELECT AVG(json_extract(aspect_data, '$.confidence_level'))
    FROM work_item_contexts
    WHERE aspect_type = 'discovery'
""").fetchone()[0]
```

### Evolution Scenarios

#### Adding New Aspect Type

```python
# 1. Define new aspect model
class PerformanceContext(BaseModel):
    load_targets: List[LoadTarget]
    scalability_requirements: List[ScalabilityReq]
    monitoring_strategy: MonitoringPlan

# 2. Add to AspectType enum
class AspectType(str, Enum):
    # ... existing
    PERFORMANCE = "performance"

# 3. Update requirement matrix
ASPECT_REQUIREMENTS[("FEATURE", "IMPLEMENTATION")] = [
    "decision", "risk", "quality", "performance"  # Added performance
]

# 4. No migration needed - existing work items unaffected
```

#### Enhancing Existing Aspect

```python
# Add field to DiscoveryContext
class DiscoveryContext(BaseModel):
    # ... existing fields
    regulatory_analysis: List[RegulatoryRequirement]  # NEW

# Backward compatible: existing aspects don't have this field (defaults to [])
# New work items can populate it
```

---

## Evaluation Against Criteria

| Criterion | Option A (Monolithic) | Option B (Composite) | Option C (Aspect-Oriented) |
|-----------|----------------------|---------------------|---------------------------|
| **Ease of Population** | ❌ Hard (40+ fields) | ✅ Good (separate forms) | ✅ Excellent (only populate needed) |
| **Value to Agents** | ⚠️ Medium (everything in one place) | ✅ Good (clear context types) | ✅ Excellent (context on demand) |
| **Queryability** | ✅ Simple (single table) | ❌ Complex (many joins) | ✅ Good (indexed JSONB) |
| **Flexibility** | ❌ Rigid (all fields for all types) | ✅ Good (can omit contexts) | ✅ Excellent (compose as needed) |
| **Evolution** | ❌ Hard (schema changes) | ✅ Good (add tables) | ✅ Excellent (add aspects) |
| **Storage Efficiency** | ❌ Poor (many NULLs) | ✅ Good (no unused tables) | ✅ Excellent (only populated) |
| **Backward Compatibility** | ✅ Perfect (extend existing) | ⚠️ Moderate (new tables) | ✅ Excellent (additive) |

**Winner**: Option C (Aspect-Oriented) - Best balance across all criteria

---

## Implementation Roadmap

### Week 1-2: Foundation
- [ ] Create `work_item_contexts` table migration
- [ ] Implement aspect models (DiscoveryContext, DecisionTrailContext, etc.)
- [ ] Implement `WorkItemContextService`
- [ ] Add unit tests for context service

### Week 3-4: CLI Integration
- [ ] Add `apm context add-aspect` command
- [ ] Add `apm context show --aspects` command
- [ ] Add `apm context validate` command
- [ ] Update work item creation to populate required_aspects

### Week 5-6: Agent Integration
- [ ] Update agent prompts to check for aspects
- [ ] Implement aspect fallback logic (aspects → unified_six_w)
- [ ] Add aspect population guides for agents
- [ ] Update context assembly service

### Week 7-8: Migration Tools
- [ ] Build aspect population wizard (interactive)
- [ ] Create bulk migration scripts for existing work items
- [ ] Add validation and completeness reports
- [ ] Documentation and examples

### Week 9-10: Refinement
- [ ] User feedback and iteration
- [ ] Performance optimization (JSONB indexes)
- [ ] Dashboard visualizations for context completeness
- [ ] API stabilization

---

## Success Metrics

### Agent Effectiveness
- **Target**: 40-60% improvement in decision quality
- **Measure**: Agent feedback surveys, decision revision rate
- **Baseline**: Current agent decision quality ratings

### Context Completeness
- **Target**: 80% of work items have all required aspects populated
- **Measure**: Validation queries showing complete vs incomplete
- **Baseline**: 0% (aspects don't exist today)

### Usage Adoption
- **Target**: 70% of new work items use aspects within 3 months
- **Measure**: Track aspect population rate for new work items
- **Baseline**: 0% (unified_six_w only today)

### Query Performance
- **Target**: Aspect queries < 100ms for 95th percentile
- **Measure**: Database query timing metrics
- **Baseline**: Current unified_six_w query performance

---

## Recommendations

### Immediate Next Steps

1. **Approve Option C (Aspect-Oriented)** - Best balance of all criteria
2. **Create migration 0023** - Add work_item_contexts table
3. **Implement aspect models** - Start with DiscoveryContext and QualityContext (highest value)
4. **Build CLI commands** - Interactive aspect population
5. **Update agent prompts** - Teach agents to use aspects

### Phased Rollout

**Phase 1 (Weeks 1-4)**: Foundation + basic CLI
**Phase 2 (Weeks 5-8)**: Agent integration + migration tools
**Phase 3 (Weeks 9-10)**: Refinement + documentation

### Risk Mitigation

- **Backward compatibility**: Keep unified_six_w for 6+ months
- **Gradual adoption**: Aspects optional initially, required only for new FEATUREs
- **Agent training**: Provide clear examples and fallback strategies
- **Performance monitoring**: Track query performance, optimize JSONB indexes if needed

---

## Appendix: Complete Aspect Specifications

See individual aspect models above for complete field specifications:
- **DiscoveryContext**: 6 top-level fields, 4 nested models
- **DecisionTrailContext**: 5 top-level fields, 4 nested models
- **RiskContext**: 5 top-level fields, 4 nested models
- **QualityContext**: 5 top-level fields, 6 nested models
- **StakeholderContext**: 4 top-level fields, 4 nested models

**Total**: 25 top-level fields, 22 nested models across 5 aspects

---

**Document Status**: READY FOR REVIEW
**Recommended Decision**: Approve Option C (Aspect-Oriented Context)
**Next Action**: Create migration 0023 and implement foundation (Week 1-2)
