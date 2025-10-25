# Unified Context Delivery System - Visual Reference

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED CONTEXT SERVICE                       │
│         Single API: get_context(type, id, filters)               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────┐     ┌───────────┐     ┌──────────┐
    │ Context  │     │Multi-Agent│     │ Quality  │
    │Inheritance│    │Coordinator│     │ Metrics  │
    └──────────┘     └───────────┘     └──────────┘
```

## Context Inheritance Flow

```
Project (Root)
  ├─ Tech Stack: [Python, Django]
  ├─ Patterns: [Hexagonal]
  └─ Constraints: [No breaking changes]
        │
        ├─→ WorkItem: Feature X
        │     ├─ Feature Scope: API endpoints
        │     ├─ Timeline: 2 weeks
        │     └─ Inherits: Project context
        │           │
        │           ├─→ Task 42: Implement auth
        │           │     ├─ Agent: code-implementer
        │           │     ├─ Stage: I1
        │           │     └─ Inherits: WorkItem + Project
        │           │
        │           └─→ Task 43: Write tests
        │                 ├─ Agent: test-runner
        │                 ├─ Stage: I1
        │                 └─ Inherits: WorkItem + Project
        │
        └─→ Idea → converts_to → WorkItem
```

## Stage Filtering (Token Reduction)

```
Full Context: ~15K tokens
    │
    ├─→ D1 (Discovery)      →  3K tokens (80% reduction)
    │   Focus: Why, Problem statement
    │
    ├─→ P1 (Planning)       →  8K tokens (47% reduction)
    │   Focus: 6W analysis, Dependencies
    │
    ├─→ I1 (Implementation) → 12K tokens (20% reduction)
    │   Focus: Code, Patterns, How
    │
    ├─→ R1 (Review)         →  6K tokens (60% reduction)
    │   Focus: Quality, Tests, Gates
    │
    ├─→ O1 (Operations)     →  5K tokens (67% reduction)
    │   Focus: Infrastructure, Monitoring
    │
    └─→ E1 (Evolution)      →  7K tokens (53% reduction)
        Focus: Metrics, Feedback, Improvements
```

## Agent-Scoped Views

```
Task 42 (Full Context)
    │
    ├─→ code-implementer
    │   ├─ Code context: Full
    │   ├─ How/What: Detailed
    │   └─ Quality warnings: Hidden
    │
    ├─→ test-runner
    │   ├─ Acceptance criteria: Full
    │   ├─ Code: Summary only
    │   └─ Evidence: Test-related
    │
    ├─→ quality-gatekeeper
    │   ├─ Quality metrics: Full
    │   ├─ Gate status: Detailed
    │   └─ All context: Available
    │
    └─→ doc-toucher
        ├─ What/Why: Detailed
        ├─ Code: Excluded
        └─ Documents: Full
```

## Multi-Agent Coordination

```
WorkItem 10: Feature X
    │
    ├─→ Shared Context (all agents see)
    │   ├─ Feature scope
    │   ├─ Acceptance criteria
    │   └─ Dependencies
    │
    ├─→ Task 42: Implement
    │   └─→ Agent: code-implementer
    │       └─ Stage: I1 context
    │
    ├─→ Task 43: Test
    │   └─→ Agent: test-runner
    │       └─ Stage: I1 context
    │
    └─→ Task 44: Document
        └─→ Agent: doc-toucher
            └─ Stage: I1 context

Coordination:
- Shared context (read-only)
- Agent contexts (role-scoped)
- Dependencies (execution order)
- Event propagation (updates)
```

## Context Update Propagation

```
Update: Project tech_stack += ["FastAPI"]
    │
    ├─→ 1. Update Project context
    │
    ├─→ 2. Invalidate caches
    │   ├─ Project views
    │   ├─ WorkItem views
    │   └─ Task views
    │
    ├─→ 3. Publish event
    │   └─→ ContextUpdatedEvent
    │       ├─ entity_type: "project"
    │       ├─ entity_id: 1
    │       └─ cascade: true
    │
    └─→ 4. Propagate to children
        ├─→ WorkItem 10 (inherits new tech)
        │   └─→ Task 42 (sees FastAPI)
        │   └─→ Task 43 (sees FastAPI)
        │
        └─→ WorkItem 11 (inherits new tech)
            └─→ Task 44 (sees FastAPI)

Timeline: <100ms for full propagation
```

## CLI Command Flow

```
$ apm task show 42 --stage=I1 --agent=code-implementer

    │
    ├─→ 1. Parse command
    │   ├─ entity_type: "task"
    │   ├─ entity_id: 42
    │   ├─ stage_filter: "I1"
    │   └─ agent_role: "code-implementer"
    │
    ├─→ 2. Call UnifiedContextService
    │   └─ get_context("task", 42, stage_filter="I1", agent_role="code-implementer")
    │
    ├─→ 3. Build context
    │   ├─ Load entity (Task 42)
    │   ├─ Build inheritance (Project → WorkItem → Task)
    │   ├─ Load supporting (docs, evidence, events)
    │   ├─ Load code (plugin facts, amalgamations)
    │   └─ Calculate quality (confidence, completeness)
    │
    ├─→ 4. Apply filters
    │   ├─ Stage filter (I1: keep code, how, what)
    │   └─ Agent filter (code-implementer: focus code)
    │
    ├─→ 5. Cache result
    │   └─ TTL: 5 minutes
    │
    └─→ 6. Output
        └─ Format: JSON | YAML | Rich

Result: Optimized context for implementer (8K tokens vs 15K full)
```

## Quality Metrics Calculation

```
Context Quality Assessment
    │
    ├─→ Confidence (0.0-1.0)
    │   ├─ Evidence coverage: 40%
    │   ├─ Validation recency: 30%
    │   ├─ Stakeholder confirm: 20%
    │   └─ Plugin verification: 10%
    │
    ├─→ Completeness (0.0-1.0)
    │   ├─ Required fields filled
    │   ├─ Stage-specific requirements
    │   └─ 6W dimension coverage
    │
    └─→ Freshness (0.0-1.0)
        ├─ Time since update: 70%
        └─ Active status: 30%

Output: Quality scores guide agent decisions
```

## Performance Characteristics

```
Query Performance:
├─ First query (uncached):  ~200ms
├─ Cached query:            ~2ms
└─ Cache hit rate:          >70%

Token Efficiency:
├─ Stage filtering:         40-80% reduction
├─ Agent filtering:         20-60% reduction
└─ Combined filtering:      up to 75% reduction

Update Propagation:
├─ Single entity update:    ~50ms
├─ Cascading update:        ~100ms
└─ Event delivery:          <10ms

Database Load:
├─ Query reduction:         5-7 queries → 1 query
├─ Latency improvement:     ~150ms → ~50ms
└─ Load reduction:          ~80%
```

## Implementation Phases

```
Phase 1: Core Service (2-3 days)
├─ UnifiedContextService
├─ Context inheritance
├─ Stage filtering
└─ Quality metrics

Phase 2: Multi-Agent (2 days)
├─ Agent-scoped filtering
├─ ParallelAgentCoordinator
├─ ContextUpdatePropagator
└─ Event-based updates

Phase 3: CLI Integration (1 day)
├─ Update show commands
├─ Add unified options
└─ Rich output rendering

Phase 4: Testing (2 days)
├─ Unit tests (>90% coverage)
├─ Integration tests
├─ Performance validation
└─ Documentation

Total: ~7 days
```

## API Comparison

### Before (Separate APIs)

```python
# Different methods for each entity type
project_context = service.get_project_context(1)
work_item_context = service.get_work_item_context(10)
task_context = service.get_task_context(42)

# Inconsistent structure
# Different field names
# Manual inheritance handling
```

### After (Unified API)

```python
# Single method for all entity types
project_context = service.get_context("project", 1)
work_item_context = service.get_context("work_item", 10)
task_context = service.get_context("task", 42)

# Consistent structure
# Same field names
# Automatic inheritance
# Optional filtering

# Advanced usage
task_context = service.get_context(
    entity_type="task",
    entity_id=42,
    stage_filter="I1",              # Stage-specific
    agent_role="code-implementer",  # Agent-scoped
    include_children=False,         # No child contexts
    include_inheritance=True        # Show full chain
)
```

## Success Metrics

```
✅ Functional:
├─ Consistent API across all entity types
├─ Unified schema (100% compliance)
├─ Inheritance tracking (explicit)
├─ Stage filtering (40-80% reduction)
├─ Agent filtering (role-specific views)
└─ Multi-agent coordination (zero conflicts)

✅ Performance:
├─ Query speed: <200ms uncached, <2ms cached
├─ Cache hit rate: >70%
├─ Token efficiency: >50% average reduction
├─ Update propagation: <100ms
└─ Database load: -80%

✅ Quality:
├─ Test coverage: >90%
├─ Schema compliance: 100%
├─ Documentation: Complete
├─ Backward compatibility: Maintained
└─ Error handling: Graceful
```

## Key Benefits Summary

```
┌────────────────────────────────────────────────┐
│  UNIFIED CONTEXT DELIVERY BENEFITS             │
├────────────────────────────────────────────────┤
│  1. Consistency                                │
│     • Single API for all entity types          │
│     • Predictable behavior                     │
│     • Easy to learn and use                    │
│                                                 │
│  2. Efficiency                                 │
│     • 50-75% token reduction                   │
│     • Stage-appropriate context                │
│     • Agent-scoped views                       │
│                                                 │
│  3. Coordination                               │
│     • Multi-agent parallel execution           │
│     • Zero context conflicts                   │
│     • Event-based updates                      │
│                                                 │
│  4. Quality                                    │
│     • Built-in metrics                         │
│     • Inheritance tracking                     │
│     • Audit trail                              │
│                                                 │
│  5. Performance                                │
│     • 70%+ cache hit rate                      │
│     • 80% database load reduction              │
│     • <100ms update propagation                │
└────────────────────────────────────────────────┘
```
