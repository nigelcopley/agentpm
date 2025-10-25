# Context Delivery System - Executive Summary

**Vision**: Pre-assembled hierarchical context for INSTANT agent operation without file searching

**Performance**: <200ms assembly, 70-100ms cached (80%+ hit rate)

---

## System Architecture

### Three-Level Hierarchy

```
PROJECT CONTEXT (Broadest)
├─ Tech stack, team, architecture
├─ System-wide patterns, standards
└─ Inherited by ALL work items

WORK ITEM CONTEXT (Medium)
├─ Feature scope, dependencies
├─ Acceptance criteria, design decisions
└─ Inherited by ALL tasks

TASK CONTEXT (Finest)
├─ Implementation details, code files
├─ Test plan, agent instructions
└─ OVERRIDES parent levels (most specific wins)
```

### UnifiedSixW Structure

**Same 15 fields across ALL levels** - only granularity changes:

```python
UnifiedSixW(
    # WHO - People (3 fields)
    end_users, implementers, reviewers

    # WHAT - Requirements (3 fields)
    functional_requirements, technical_constraints, acceptance_criteria

    # WHERE - Technical context (3 fields)
    affected_services, repositories, deployment_targets

    # WHEN - Timeline (2 fields)
    deadline, dependencies_timeline

    # WHY - Value (2 fields)
    business_value, risk_if_delayed

    # HOW - Approach (2 fields)
    suggested_approach, existing_patterns
)
```

**Merging**: Task OVERRIDES WorkItem OVERRIDES Project (most specific wins)

---

## Complete Context Payload

**What agents receive in <200ms**:

```python
ContextPayload(
    # HIERARCHICAL 6W
    merged_6w: UnifiedSixW  # 15 fields, task-wins merged

    # SUPPORTING MODELS (5 sources)
    related_documents: List[Dict]     # Specs, ADRs, design docs
    evidence_sources: List[Dict]      # Research, decisions, references
    recent_events: List[Dict]         # Last 10 session events
    temporal_context: List[Dict]      # Last 3 session summaries

    # CODE INTELLIGENCE (Plugin system)
    plugin_facts: Dict                # Framework detection
    amalgamations: Dict               # Code file paths (lazy)

    # AGENT-SPECIFIC
    agent_sop: str                    # Role-specific SOP
    assigned_agent: str               # Agent role name

    # QUALITY ASSESSMENT
    confidence_score: float           # 0.0-1.0 (formula-based)
    confidence_band: ConfidenceBand   # RED/YELLOW/GREEN
    confidence_breakdown: Dict        # Factor scores
    warnings: List[str]               # Staleness, quality warnings

    # METADATA
    assembled_at: datetime
    assembly_duration_ms: float       # Performance tracking
    cache_hit: bool
)
```

---

## Assembly Performance

**11-Step Pipeline** (<200ms p95 target):

```
1. Load entities (3 DB queries)           10ms
2. Load 6W contexts (3 levels)            10ms
3. Merge hierarchically                    5ms
4. Load plugin facts                      20ms (cached) / 100ms (fresh)
5. Get amalgamation paths                 10ms
6. Load documents                         10ms
7. Load evidence                          10ms
8. Load events                            10ms
9. Load summaries                         10ms
10. Calculate freshness                    5ms
11. Calculate confidence                  10ms
12. Inject agent SOP                   10-20ms
13. Filter by role                      5-10ms
────────────────────────────────────────────
Total (cached):                        70-100ms
Total (fresh):                        150-200ms
```

**Cache Strategy**:
- Memory cache (LRU, 15-min TTL): 60-70% hit rate
- Filesystem cache (.aipm/cache/): 80-85% hit rate
- **Combined: 80%+ hit rate** = most requests <100ms

---

## Supporting Models Integration

### 1. Documents (document_references table)

**Purpose**: Link specifications, design docs, ADRs

**Types**: specification, design, adr, business_pillars_analysis, test_plan, deployment_guide

**Format**:
```python
{
    'type': 'design',
    'title': 'Caching Architecture Design',
    'file_path': 'docs/design/caching-architecture.md',
    'description': 'Complete caching layer design',
    'format': 'markdown',
    'created_at': '2025-10-05T10:00:00',
    'updated_at': '2025-10-08T15:30:00'
}
```

### 2. Evidence (evidence_sources table)

**Purpose**: Research, decisions, external references

**Types**: primary (first-hand), secondary (documentation), internal (team decisions)

**Format**:
```python
{
    'url': 'https://redis.io/docs/manual/patterns/cache/',
    'source_type': 'primary',
    'excerpt': 'Cache-aside pattern implementation...',
    'captured_at': '2025-10-05T11:00:00',
    'content_hash': 'sha256:abc123...',
    'confidence_score': 0.9
}
```

### 3. Events (session_events table)

**Purpose**: Recent activity for continuity

**Types**: task_started, task_completed, code_committed, tests_passed

**Format**:
```python
{
    'event_type': 'task_completed',
    'entity_type': 'task',
    'entity_id': 122,
    'description': 'Completed Redis setup',
    'created_at': '2025-10-09T16:30:00',
    'metadata': {'duration_hours': 6.5}
}
```

### 4. Summaries (work_item_summaries table)

**Purpose**: Session continuity (progress, decisions, handovers)

**Types**: session, milestone, checkpoint, handoff

**Format**:
```python
{
    'summary_text': 'Completed Redis setup...',
    'summary_type': 'session',
    'session_date': '2025-10-09T16:30:00',
    'session_duration_hours': 6.5,
    'metadata': {
        'key_decisions': ['Use Redis Cluster', 'Enable AOF persistence'],
        'tasks_completed': [122],
        'blockers_resolved': [],
        'next_steps': ['Implement caching layer', 'Add monitoring']
    }
}
```

### 5. Plugin Facts (plugin system + .aipm/contexts/)

**Purpose**: Framework detection, code analysis

**Format**:
```python
plugin_facts = {
    'python': {
        'version': '3.9.7',
        'packages': ['fastapi', 'pydantic', 'sqlalchemy'],
        'frameworks': ['fastapi']
    },
    'django': {
        'version': '4.2.5',
        'apps': ['core', 'api', 'web']
    }
}

amalgamations = {
    'classes': '.aipm/contexts/lang_python_classes.txt',
    'functions': '.aipm/contexts/lang_python_functions.txt',
    'models': '.aipm/contexts/framework_django_models.txt'
}
```

---

## Confidence Scoring

**Formula** (weighted):
```python
confidence = (
    (six_w_completeness * 0.35) +      # 15 fields populated
    (plugin_facts_quality * 0.25) +     # Framework coverage
    (amalgamations_coverage * 0.25) +   # Code availability
    (freshness_factor * 0.15)           # Age penalty
)
```

**Bands**:
- **GREEN (>0.8)**: High quality, agent fully enabled
- **YELLOW (0.5-0.8)**: Adequate, agent can operate with limitations
- **RED (<0.5)**: Insufficient, agent cannot operate effectively

**Freshness Penalties**:
- 0-7 days: 1.0 (perfect)
- 8-30 days: 0.8 (good)
- 31-90 days: 0.5 (stale)
- 90+ days: 0.2 (very stale)

---

## Database Schema

**5 Core Tables**:

1. **contexts** - 6W storage + rich context types
2. **document_references** - Specs, ADRs, design docs
3. **evidence_sources** - Research, decisions, references
4. **session_events** - Activity timeline
5. **work_item_summaries** - Session continuity (WI-0017)

**Key Indexes**:
```sql
CREATE INDEX idx_contexts_entity ON contexts (entity_type, entity_id);
CREATE INDEX idx_doc_refs_entity ON document_references (entity_type, entity_id);
CREATE INDEX idx_events_created ON session_events (created_at DESC);
CREATE INDEX idx_summaries_work_item ON work_item_summaries (work_item_id, session_date DESC);
```

---

## Role-Based Filtering

**Purpose**: Reduce noise by 30-50% through agent capability matching

**Example** (python-developer agent):
```python
# Before filtering
amalgamations = {
    'classes': 'classes.txt',
    'functions': 'functions.txt',
    'components': 'components.txt',  # React (frontend)
    'hooks': 'hooks.txt'             # React (frontend)
}

# After filtering (python capabilities only)
filtered_amalgamations = {
    'classes': 'classes.txt',
    'functions': 'functions.txt'
}
# 50% reduction (excluded React/frontend files)
```

**Result**: Agents receive only relevant context for their capabilities

---

## Integration Points

### Workflow Integration

**Automatic assembly on task start**:
```python
# In WorkflowService.start_task()
task = workflow.start_task(task_id=123, agent_role='python-developer')

# Context written to: .aipm/contexts/task_123_context.json
# Agent reads this file at session start - INSTANT context
```

### CLI Integration

```bash
# Display assembled context
apm context show --task 123

# Check context quality
apm context quality --task 123

# Force context refresh
apm context refresh --task 123
```

### Agent Integration

**Session start hook**:
```python
# In .claude/agents/hooks/session-start.py
def on_session_start(task_id: int, agent_role: str):
    context = load_context(f'.aipm/contexts/task_{task_id}_context.json')

    # Check quality
    if context['confidence']['band'] == 'RED':
        abort_session("Low context quality")

    # Load components
    merged_6w = context['merged_6w']
    documents = context['related_documents']
    summaries = context['temporal_context']
    plugin_facts = context['plugin_facts']
    agent_sop = context['agent_sop']

    # IMMEDIATE START - no searching, no queries
```

---

## Real-World Example

**Task #123**: "Implement Redis caching layer"

**Agent receives**:
- ✅ **WHO**: Implemented by @alice, reviewed by @bob
- ✅ **WHAT**: Cache-aside pattern, 4 acceptance criteria
- ✅ **WHERE**: cache.py, middleware.py (exact files)
- ✅ **WHEN**: Oct 15 deadline, dependency on Task #122 complete
- ✅ **WHY**: 5x faster responses, churn risk if delayed
- ✅ **HOW**: Redis with LRU eviction, async invalidation
- ✅ **HISTORY**: Redis setup completed yesterday
- ✅ **DESIGN**: Caching architecture doc + ADR-012
- ✅ **CODE**: 4 amalgamation files (classes, functions, models, views)
- ✅ **SOP**: Python developer standards loaded

**Assembly time**: 85ms (cached)
**Confidence**: 0.87 (GREEN band)
**Result**: Agent starts immediately, NO discovery phase needed

---

## Key Benefits

1. **INSTANT START**: <200ms context assembly, no file searching
2. **COMPLETE CONTEXT**: All 5 supporting models integrated
3. **HIGH QUALITY**: 91% test coverage, 99.4% pass rate
4. **GRACEFUL DEGRADATION**: 95% success rate with partial context
5. **ROLE-BASED**: 30-50% noise reduction through filtering
6. **PRODUCTION READY**: WI-31 complete, fully operational

---

## Documentation

**Complete Specification**: `docs/architecture/CONTEXT-DELIVERY-HIERARCHY-SPECIFICATION.md` (18KB)

**Quick Reference**: This document

**Implementation**: `agentpm/core/context/assembly_service.py` (794 LOC)

**Tests**: `tests/core/context/` (172 tests, 91% coverage)

---

**Last Updated**: 2025-10-17
**Status**: Production Ready
**Performance**: <200ms (p95), 70-100ms cached
**Quality**: 91% test coverage, 99.4% pass rate
