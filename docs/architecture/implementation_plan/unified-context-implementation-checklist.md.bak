# Unified Context Delivery - Implementation Checklist

**Quick Reference for Implementation Teams**

---

## Phase 1: Core Service (2-3 days)

### 1.1 Create UnifiedContextService

- [ ] **File**: `agentpm/core/context/unified_service.py`
- [ ] **Class**: `UnifiedContextService`
- [ ] **Init**: `__init__(db_service, project_path)`
  - [ ] Initialize plugin orchestrator
  - [ ] Initialize temporal loader
  - [ ] Initialize cache (5min TTL)
  - [ ] Initialize event bus

### 1.2 Implement Core API

- [ ] **Method**: `get_context(entity_type, entity_id, **filters)`
  - [ ] Support entity types: `project`, `work_item`, `task`, `idea`
  - [ ] Cache key generation
  - [ ] Cache lookup (return if hit)
  - [ ] Entity retrieval
  - [ ] Context building with inheritance
  - [ ] Supporting data loading
  - [ ] Code context loading
  - [ ] Quality metrics calculation
  - [ ] Apply format filter (minimal, compact, rich)
  - [ ] Apply stage filter (D1-E1)
  - [ ] Apply agent filter (role-specific)
  - [ ] Cache result
  - [ ] Return unified schema

### 1.3 Context Inheritance

- [ ] **Method**: `_build_hierarchical_context(entity)`
  - [ ] Get project (root) context
  - [ ] Get parent context (if applicable)
  - [ ] Get entity-specific context
  - [ ] Merge with override tracking
  - [ ] Add stage information
  - [ ] Return context with inheritance metadata

- [ ] **Method**: `_merge_contexts(project, parent, entity)`
  - [ ] Merge three levels
  - [ ] Track overrides explicitly
  - [ ] Return merged context + overrides dict

### 1.4 Supporting Data Loading

- [ ] **Method**: `_load_supporting_data(entity)`
  - [ ] Load documents
  - [ ] Load evidence
  - [ ] Load events
  - [ ] Load summaries
  - [ ] Load dependencies
  - [ ] Return supporting dict

### 1.5 Code Context Loading

- [ ] **Method**: `_load_code_context(entity)`
  - [ ] Get plugin facts from orchestrator
  - [ ] Get amalgamations (for tasks)
  - [ ] Detect code patterns
  - [ ] Return code dict

### 1.6 Quality Metrics

- [ ] **Method**: `_calculate_confidence(context)`
  - [ ] Evidence coverage (40%)
  - [ ] Validation recency (30%)
  - [ ] Stakeholder confirmation (20%)
  - [ ] Plugin verification (10%)
  - [ ] Return float 0.0-1.0

- [ ] **Method**: `_calculate_completeness(entity, context)`
  - [ ] Get stage requirements
  - [ ] Check required fields
  - [ ] Calculate percentage
  - [ ] Return float 0.0-1.0

- [ ] **Method**: `_calculate_freshness(entity)`
  - [ ] Time since update (70%)
  - [ ] Active status (30%)
  - [ ] Return float 0.0-1.0

- [ ] **Method**: `_get_quality_warnings(entity, context)`
  - [ ] Check for missing required fields
  - [ ] Check for low confidence areas
  - [ ] Check for stale data
  - [ ] Return list of warning strings

### 1.7 Stage Filtering

- [ ] **Constant**: `STAGE_FILTERS` dictionary
  - [ ] D1 filter definition
  - [ ] P1 filter definition
  - [ ] I1 filter definition
  - [ ] R1 filter definition
  - [ ] O1 filter definition
  - [ ] E1 filter definition

- [ ] **Function**: `apply_stage_filter(context, stage)`
  - [ ] Get filter spec for stage
  - [ ] Extract allowed fields
  - [ ] Build filtered context
  - [ ] Return filtered dict

### 1.8 Testing

- [ ] **File**: `tests/core/context/test_unified_service.py`
- [ ] Test: `test_get_context_returns_consistent_schema()`
  - [ ] All entity types return same top-level keys
  - [ ] Schema validation
- [ ] Test: `test_context_inheritance_preserves_parent_values()`
  - [ ] Task inherits from work item and project
  - [ ] Override tracking works
- [ ] Test: `test_stage_filter_reduces_context_size()`
  - [ ] D1 significantly smaller than full
  - [ ] I1 has code context, D1 doesn't
- [ ] Test: `test_quality_metrics_calculation()`
  - [ ] Confidence score in 0.0-1.0 range
  - [ ] Completeness score calculation
  - [ ] Freshness score calculation
- [ ] Test: `test_cache_improves_query_performance()`
  - [ ] Cached queries much faster
  - [ ] Same results from cache

**Coverage Target**: >90%

---

## Phase 2: Multi-Agent Support (2 days)

### 2.1 Agent-Scoped Filtering

- [ ] **Constant**: `AGENT_FILTERS` dictionary
  - [ ] code-implementer filter
  - [ ] test-runner filter
  - [ ] quality-gatekeeper filter
  - [ ] doc-toucher filter
  - [ ] dependency-mapper filter

- [ ] **Function**: `apply_agent_filter(context, agent_role)`
  - [ ] Get filter spec for agent
  - [ ] Focus on relevant sections
  - [ ] Exclude irrelevant sections
  - [ ] Return agent-scoped context

### 2.2 Parallel Agent Coordinator

- [ ] **File**: `agentpm/core/context/agent_coordinator.py`
- [ ] **Class**: `ParallelAgentCoordinator`
- [ ] **Method**: `coordinate_parallel_execution(work_item_id, task_assignments)`
  - [ ] Get shared work item context
  - [ ] Get agent-specific task contexts (parallel)
  - [ ] Build dependency graph
  - [ ] Determine execution order
  - [ ] Return coordination package

### 2.3 Context Update Propagator

- [ ] **File**: `agentpm/core/context/update_propagator.py`
- [ ] **Class**: `ContextUpdatePropagator`
- [ ] **Method**: `propagate_update(entity_type, entity_id, update)`
  - [ ] Update entity context in database
  - [ ] Invalidate all caches (pattern matching)
  - [ ] Publish ContextUpdatedEvent
  - [ ] Cascade to children if update.cascade=True
  - [ ] Return None

### 2.4 Context Update API

- [ ] **Method**: `UnifiedContextService.update_context()`
  - [ ] Validate update data
  - [ ] Apply updates to entity
  - [ ] Call propagator
  - [ ] Return None

### 2.5 Event System Integration

- [ ] **Event**: `ContextUpdatedEvent`
  - [ ] entity_type field
  - [ ] entity_id field
  - [ ] updates dict
  - [ ] timestamp field
  - [ ] affects_children boolean

- [ ] **Handler**: Subscribe to context update events
  - [ ] Invalidate caches
  - [ ] Notify active agents
  - [ ] Log for audit

### 2.6 Testing

- [ ] **File**: `tests/core/context/test_agent_coordination.py`
- [ ] Test: `test_parallel_agent_coordination()`
  - [ ] Multiple agents get consistent shared context
  - [ ] Each agent gets role-specific context
  - [ ] Dependencies tracked correctly
- [ ] Test: `test_agent_filter_focuses_context()`
  - [ ] Implementer gets full code
  - [ ] Tester gets acceptance criteria focus
- [ ] Test: `test_context_update_propagates_to_children()`
  - [ ] Parent update cascades to children
  - [ ] Children see updated inherited context
  - [ ] Event published correctly

**Coverage Target**: >90%

---

## Phase 3: CLI Integration (1 day)

### 3.1 Update Task Show Command

- [ ] **File**: `agentpm/cli/commands/task/show.py`
- [ ] Add options:
  - [ ] `--format=json|yaml|rich`
  - [ ] `--stage=D1|P1|I1|R1|O1|E1`
  - [ ] `--agent=<role>`
  - [ ] `--include-children`
  - [ ] `--include-inheritance`
  - [ ] `--quality-only`
  - [ ] `--compact`
- [ ] Use `UnifiedContextService.get_context("task", id, **filters)`
- [ ] Render output based on format

### 3.2 Update WorkItem Show Command

- [ ] **File**: `agentpm/cli/commands/work_item/show.py`
- [ ] Add same options as task show
- [ ] Use `UnifiedContextService.get_context("work_item", id, **filters)`
- [ ] Render output

### 3.3 Update Project Show Command

- [ ] **File**: `agentpm/cli/commands/project/show.py`
- [ ] Add same options
- [ ] Use `UnifiedContextService.get_context("project", id, **filters)`
- [ ] Render output

### 3.4 Create Idea Show Command

- [ ] **File**: `agentpm/cli/commands/idea/show.py`
- [ ] Create show command
- [ ] Add same options
- [ ] Use `UnifiedContextService.get_context("idea", id, **filters)`
- [ ] Render output

### 3.5 Rich Output Rendering

- [ ] **Function**: `render_rich_context(context)`
  - [ ] Pretty-print entity section
  - [ ] Pretty-print context section (6W)
  - [ ] Show inheritance chain (if included)
  - [ ] Show supporting data summary
  - [ ] Show code context summary
  - [ ] Highlight quality metrics
  - [ ] Color coding for quality scores

### 3.6 Testing

- [ ] **File**: `tests/cli/test_unified_context_commands.py`
- [ ] Test: `test_task_show_with_stage_filter()`
  - [ ] JSON output includes filtered context
  - [ ] Stage filter applied correctly
- [ ] Test: `test_task_show_with_agent_filter()`
  - [ ] Agent-scoped context returned
- [ ] Test: `test_all_entity_types_consistent_output()`
  - [ ] Project, WorkItem, Task, Idea all work
  - [ ] Same options work for all
- [ ] Test: `test_quality_only_flag()`
  - [ ] Only quality section returned

**Coverage Target**: >85%

---

## Phase 4: Testing & Validation (2 days)

### 4.1 Comprehensive Unit Tests

- [ ] Test all `UnifiedContextService` methods
- [ ] Test all helper methods
- [ ] Test error handling
- [ ] Test edge cases
- [ ] **Coverage**: Aim for >90%

### 4.2 Integration Tests

- [ ] Test full workflow (create entity → get context)
- [ ] Test multi-agent scenarios
- [ ] Test context inheritance chain
- [ ] Test cache effectiveness
- [ ] Test event propagation

### 4.3 Performance Testing

- [ ] Benchmark query speed (uncached)
- [ ] Benchmark query speed (cached)
- [ ] Measure cache hit rate
- [ ] Measure token reduction (stage filters)
- [ ] Measure token reduction (agent filters)
- [ ] Measure update propagation time

**Performance Targets**:
- [ ] Uncached query: <200ms
- [ ] Cached query: <2ms
- [ ] Cache hit rate: >70%
- [ ] Token reduction: >50% average
- [ ] Update propagation: <100ms

### 4.4 Token Efficiency Validation

- [ ] Measure full context token count
- [ ] Measure D1 filtered token count (expect 80% reduction)
- [ ] Measure P1 filtered token count (expect 47% reduction)
- [ ] Measure I1 filtered token count (expect 20% reduction)
- [ ] Measure R1 filtered token count (expect 60% reduction)
- [ ] Measure O1 filtered token count (expect 67% reduction)
- [ ] Measure E1 filtered token count (expect 53% reduction)

### 4.5 Schema Validation

- [ ] Validate all entity types return consistent schema
- [ ] Validate required fields present
- [ ] Validate field types correct
- [ ] Validate quality metrics in 0.0-1.0 range

### 4.6 Documentation

- [ ] API documentation (docstrings)
- [ ] Usage examples in docs
- [ ] Update system architecture docs
- [ ] Update CLI command docs
- [ ] Add troubleshooting guide

---

## Success Criteria Checklist

### Functional Requirements

- [ ] ✅ Consistent API across all entity types
- [ ] ✅ Unified schema (same structure for all)
- [ ] ✅ Context inheritance tracking
- [ ] ✅ Stage-specific filtering (D1-E1)
- [ ] ✅ Agent-specific filtering
- [ ] ✅ Multi-agent coordination without conflicts
- [ ] ✅ Quality metrics calculation
- [ ] ✅ CLI commands updated

### Performance Requirements

- [ ] ✅ Query speed: <200ms uncached, <2ms cached
- [ ] ✅ Cache hit rate: >70%
- [ ] ✅ Token efficiency: >50% average reduction
- [ ] ✅ Update propagation: <100ms
- [ ] ✅ Database load: 80% reduction

### Quality Requirements

- [ ] ✅ Test coverage: >90%
- [ ] ✅ Schema compliance: 100%
- [ ] ✅ Documentation: Complete
- [ ] ✅ Backward compatibility: Maintained
- [ ] ✅ Error handling: Graceful

---

## Quick Start Commands

### Development

```bash
# Run tests
pytest tests/core/context/test_unified_service.py -v

# Run with coverage
pytest tests/core/context/ --cov=agentpm.core.context --cov-report=html

# Performance benchmark
pytest tests/core/context/test_performance.py -v --benchmark-only

# Integration tests
pytest tests/integration/test_unified_context.py -v
```

### Usage

```bash
# Get task context (JSON)
apm task show 42 --format=json

# Get task context for implementer (I1 stage)
apm task show 42 --stage=I1 --agent=code-implementer

# Get work item with all child tasks
apm work-item show 10 --include-children

# Get quality metrics only
apm task show 42 --quality-only

# Compact view
apm task show 42 --compact
```

---

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Core Service | 2-3 days | UnifiedContextService, tests |
| Phase 2: Multi-Agent | 2 days | Agent coordination, events |
| Phase 3: CLI | 1 day | Updated commands |
| Phase 4: Testing | 2 days | Complete test suite, docs |
| **Total** | **7 days** | **Production-ready system** |

---

## Risk Mitigation

### Risk: Breaking existing code

**Mitigation**: Backward-compatible wrappers
```python
def get_task_context(self, task_id):
    """DEPRECATED: Use get_context("task", task_id)"""
    return self.get_context("task", task_id)
```

### Risk: Performance degradation

**Mitigation**:
- Aggressive caching (5min TTL)
- Query optimization (single query with joins)
- Lazy loading (load supporting data only if needed)

### Risk: Cache invalidation bugs

**Mitigation**:
- Pattern-based invalidation (invalidate all views)
- Event-driven updates (single source of truth)
- Cache versioning (detect stale data)

---

## Notes

- **Code Style**: Follow existing AIPM patterns
- **Testing**: TDD approach recommended
- **Documentation**: Update as you implement
- **Reviews**: Request review after each phase
- **Performance**: Benchmark early and often

---

**Last Updated**: 2025-10-17
**Status**: Ready for Implementation
