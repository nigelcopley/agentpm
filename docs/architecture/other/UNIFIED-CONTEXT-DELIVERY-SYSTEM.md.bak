# Unified Context Delivery System

**Design Document**
**Version**: 1.0.0
**Date**: 2025-10-17
**Status**: Architecture Design

---

## Executive Summary

Design for a unified context delivery system that provides **consistent, hierarchical, and stage-appropriate** context across all entity types (Project, WorkItem, Task, Idea) to support rapid multi-agent AI development workflows.

**Key Goals**:
- ✅ Consistent API pattern across all entity types
- ✅ Hierarchical context inheritance (Project → WorkItem → Task)
- ✅ Stage-specific filtering (D1-E1) for token efficiency
- ✅ Multi-agent coordination without context conflicts
- ✅ Quality metrics (confidence, completeness, freshness)

---

## 1. System Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────┐
│            UnifiedContextService (Core API)             │
│  Single entry point: get_context(type, id, filters)    │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Context    │  │   Multi-     │  │   Quality    │
│  Inheritance │  │   Agent      │  │   Metrics    │
│   Builder    │  │ Coordinator  │  │  Calculator  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Database   │  │    Plugin    │  │    Event     │
│   Service    │  │  Orchestra-  │  │     Bus      │
│              │  │     tor      │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 Unified Context Schema

**Standard structure returned for ALL entity types**:

```json
{
  "entity": {
    "type": "project|work_item|task|idea",
    "id": 123,
    "title": "Feature name",
    "status": "IN_PROGRESS",
    "created_at": "2025-10-17T10:00:00Z",
    "updated_at": "2025-10-17T14:30:00Z"
    // Entity-specific fields (flexible)
  },

  "context": {
    "six_w": {
      "who": {
        "stakeholders": ["user-role-1", "user-role-2"],
        "agents": ["implementer", "reviewer"]
      },
      "what": {
        "objectives": ["Deliver feature X"],
        "deliverables": ["Code", "Tests", "Docs"]
      },
      "when": {
        "timeline": {"start": "...", "end": "..."},
        "milestones": [{"name": "...", "date": "..."}]
      },
      "where": {
        "scope": {"modules": ["auth", "api"]},
        "boundaries": ["No database schema changes"]
      },
      "why": {
        "value": "Improve user experience by...",
        "risks": ["Risk if not delivered: ..."]
      },
      "how": {
        "approach": "Use existing auth middleware",
        "constraints": ["Must be backward compatible"]
      }
    },
    "inheritance": {
      "project_context": {/* Root context */},
      "parent_context": {/* Direct parent context */},
      "overrides": {/* Fields overridden at this level */}
    },
    "stage": {
      "current": "P1",  // D1|P1|I1|R1|O1|E1
      "gates": {
        "passed": ["D1"],
        "pending": ["P1"],
        "blocked": []
      }
    }
  },

  "supporting": {
    "documents": [
      {"id": 1, "title": "PRD", "type": "requirement"}
    ],
    "evidence": [
      {"id": 1, "source": "user-interview", "excerpt": "..."}
    ],
    "events": [
      {"id": 1, "type": "status_change", "timestamp": "..."}
    ],
    "summaries": [
      {"id": 1, "type": "weekly", "content": "..."}
    ],
    "dependencies": {
      "blockers": [{"task_id": 42, "reason": "..."}],
      "blocked_by": []
    }
  },

  "code": {
    "plugin_facts": {
      "languages": ["python"],
      "frameworks": ["django"],
      "test_frameworks": ["pytest"],
      "patterns": ["hexagonal"]
    },
    "amalgamations": {
      "python_classes": "/path/to/classes.txt",
      "python_functions": "/path/to/functions.txt"
    },
    "patterns": [
      {"type": "service_pattern", "confidence": 0.9}
    ]
  },

  "quality": {
    "confidence": 0.85,      // 0.0-1.0
    "completeness": 0.90,    // 0.0-1.0
    "freshness": 0.95,       // 0.0-1.0
    "last_validated": "2025-10-17T14:00:00Z",
    "warnings": [
      "Missing acceptance criteria for edge case X"
    ]
  },

  "meta": {
    "generated_at": "2025-10-17T14:30:00Z",
    "format_version": "1.0.0",
    "entity_type": "task",
    "entity_id": 123,
    "agent_role": "code-implementer",  // Optional
    "stage_filter": "I1"               // Optional
  }
}
```

---

## 2. Context Inheritance Chain

### 2.1 Inheritance Flow

```
Project (Root)
  ├─ Global tech stack
  ├─ Global patterns
  └─ Global constraints
     │
     ├─→ WorkItem (Feature)
     │     ├─ Feature scope
     │     ├─ Feature timeline
     │     └─ Inherits project context
     │        │
     │        ├─→ Task (Implementation)
     │        │     ├─ Task-specific details
     │        │     └─ Inherits WorkItem + Project
     │        │
     │        └─→ Task (Testing)
     │              ├─ Test-specific details
     │              └─ Inherits WorkItem + Project
     │
     └─→ Idea (Standalone)
           ├─ Problem statement
           ├─ Research findings
           └─ Converts to → WorkItem (on acceptance)
```

### 2.2 Inheritance Algorithm

```python
def build_context_with_inheritance(entity):
    """Build context with full inheritance chain"""

    # 1. Start with root (project) context
    context = get_project_context(entity.project_id)

    # 2. Layer parent context (if not project-level entity)
    if entity.parent_id:
        parent_context = get_entity_context(entity.parent_id)
        context = merge_contexts(context, parent_context)

    # 3. Apply entity-specific overrides
    entity_context = get_entity_specific_context(entity)
    context, overrides = merge_with_tracking(context, entity_context)

    # 4. Return with inheritance metadata
    return {
        "six_w": context,
        "inheritance": {
            "project_context": get_project_context(entity.project_id),
            "parent_context": parent_context if entity.parent_id else {},
            "overrides": overrides
        }
    }
```

### 2.3 Override Tracking

**Purpose**: Maintain audit trail of context changes at each level

```python
def merge_with_tracking(base_context, override_context):
    """Merge contexts and track what was overridden"""

    overrides = {}
    merged = {}

    for key, base_value in base_context.items():
        if key in override_context:
            override_value = override_context[key]

            # Only track if actually different
            if override_value != base_value:
                overrides[key] = {
                    "original": base_value,
                    "override": override_value,
                    "reason": f"Overridden at {entity.type} level"
                }
                merged[key] = override_value
            else:
                merged[key] = base_value
        else:
            merged[key] = base_value

    # Add new keys from override
    for key, value in override_context.items():
        if key not in base_context:
            merged[key] = value

    return merged, overrides
```

**Benefits**:
- Clear audit trail of context changes
- Easy to understand context source
- Supports debugging and validation
- Enables context rollback if needed

---

## 3. Stage-Specific Context Filtering

### 3.1 Workflow Stages

```
D1 (Discovery)     → Minimal context (problem, research)
P1 (Planning)      → Planning context (deps, estimates)
I1 (Implementation)→ Implementation context (code, patterns)
R1 (Review)        → Review context (ACs, quality)
O1 (Operations)    → Deployment context (infra, monitoring)
E1 (Evolution)     → Analytics context (metrics, feedback)
```

### 3.2 Stage Filter Definitions

```python
STAGE_FILTERS = {
    "D1": {  # Discovery - Minimal context
        "entity": ["type", "id", "title", "description"],
        "context": ["six_w.why", "six_w.what.objectives"],
        "supporting": ["documents", "evidence"],
        "code": [],  # No code context at discovery
        "quality": ["confidence"]
    },

    "P1": {  # Planning - Full context except code
        "entity": ["type", "id", "title", "status", "priority"],
        "context": ["six_w", "inheritance.parent_context", "stage"],
        "supporting": ["documents", "evidence", "dependencies"],
        "code": ["plugin_facts"],  # Tech stack only
        "quality": ["confidence", "completeness"]
    },

    "I1": {  # Implementation - Full code context
        "entity": ["type", "id", "title", "status", "assigned_agent"],
        "context": ["six_w.what", "six_w.how", "inheritance"],
        "supporting": ["documents", "dependencies"],
        "code": ["plugin_facts", "amalgamations", "patterns"],  # All code
        "quality": ["confidence", "completeness", "freshness"]
    },

    "R1": {  # Review - Quality focus
        "entity": ["type", "id", "title", "status", "acceptance_criteria"],
        "context": ["six_w.what", "stage.gates"],
        "supporting": ["evidence", "events", "summaries"],
        "code": ["patterns"],  # Code quality patterns
        "quality": ["confidence", "completeness", "freshness", "warnings"]
    },

    "O1": {  # Operations - Deployment focus
        "entity": ["type", "id", "title", "status", "deployment_info"],
        "context": ["six_w.where", "six_w.how", "stage"],
        "supporting": ["events", "summaries"],
        "code": ["plugin_facts"],  # Infrastructure context
        "quality": ["freshness", "warnings"]
    },

    "E1": {  # Evolution - Analytics focus
        "entity": ["type", "id", "title", "metrics"],
        "context": ["six_w.why", "stage.gates"],
        "supporting": ["events", "summaries", "evidence"],
        "code": [],
        "quality": ["confidence", "completeness", "freshness"]
    }
}
```

### 3.3 Token Efficiency Gains

| Stage | Full Context | Filtered Context | Reduction |
|-------|-------------|------------------|-----------|
| D1    | ~15K tokens | ~3K tokens       | 80%       |
| P1    | ~15K tokens | ~8K tokens       | 47%       |
| I1    | ~15K tokens | ~12K tokens      | 20%       |
| R1    | ~15K tokens | ~6K tokens       | 60%       |
| O1    | ~15K tokens | ~5K tokens       | 67%       |
| E1    | ~15K tokens | ~7K tokens       | 53%       |

**Average reduction: 54% token savings while maintaining stage-appropriate context**

---

## 4. Multi-Agent Coordination

### 4.1 Agent-Scoped Context Views

**Purpose**: Each agent gets context optimized for their role

```python
AGENT_FILTERS = {
    "code-implementer": {
        "focus": ["code", "context.six_w.how"],
        "supporting": ["documents", "dependencies"],
        "exclude": ["quality.warnings"]  # Reduce noise
    },

    "test-runner": {
        "focus": ["context.six_w.what", "entity.acceptance_criteria"],
        "supporting": ["evidence"],
        "exclude": ["code.amalgamations"]  # Don't need full code
    },

    "quality-gatekeeper": {
        "focus": ["quality", "context.stage.gates"],
        "supporting": ["evidence", "events", "summaries"],
        "exclude": []  # Needs full context
    },

    "doc-toucher": {
        "focus": ["context.six_w.what", "context.six_w.why"],
        "supporting": ["documents"],
        "exclude": ["code.amalgamations"]  # Not relevant for docs
    },

    "dependency-mapper": {
        "focus": ["supporting.dependencies", "context.six_w.when"],
        "supporting": ["events"],
        "exclude": ["code"]  # Focus on relationships, not implementation
    }
}
```

### 4.2 Parallel Agent Coordination

```python
class ParallelAgentCoordinator:
    """Coordinate multiple agents working on different tasks"""

    def coordinate_parallel_execution(
        self,
        work_item_id: int,
        task_assignments: Dict[str, int]  # agent_role → task_id
    ):
        """
        Coordinate parallel agent execution without context conflicts.

        Args:
            work_item_id: Parent work item
            task_assignments: {"code-implementer": 42, "test-runner": 43}

        Returns:
            Coordination package with shared + agent-specific contexts
        """

        # 1. Get shared work item context (all agents see this)
        shared_context = self.service.get_context(
            entity_type="work_item",
            entity_id=work_item_id
        )

        # 2. Get agent-specific task contexts (parallel)
        agent_contexts = {}
        for agent_role, task_id in task_assignments.items():
            agent_contexts[agent_role] = self.service.get_context(
                entity_type="task",
                entity_id=task_id,
                stage_filter=self._get_agent_stage(agent_role),
                agent_role=agent_role
            )

        # 3. Build dependency graph
        dependencies = self._build_dependency_graph(task_assignments.values())

        # 4. Return coordination package
        return {
            "shared_context": shared_context,
            "agent_contexts": agent_contexts,
            "coordination": {
                "work_item_id": work_item_id,
                "task_assignments": task_assignments,
                "dependencies": dependencies,
                "conflict_resolution": "event_based",  # Updates via events
                "execution_order": self._determine_execution_order(dependencies)
            }
        }
```

### 4.3 Context Update Propagation

```python
class ContextUpdatePropagator:
    """Ensure all agents see updated context immediately"""

    def propagate_update(
        self,
        entity_id: int,
        entity_type: str,
        update: Dict[str, Any]
    ):
        """
        Propagate context update to all interested parties.

        Flow:
        1. Update entity context in database
        2. Invalidate all caches (agent views)
        3. Publish event to notify active agents
        4. Cascade to children if hierarchical change
        """

        # 1. Update entity context
        self.service.update_context(entity_type, entity_id, update)

        # 2. Invalidate caches (all views of this entity)
        self.cache.invalidate_pattern(f"context:*:{entity_type}:{entity_id}")

        # 3. Publish event
        self.event_bus.publish(ContextUpdatedEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            update=update,
            timestamp=datetime.utcnow(),
            affects_children=update.get("cascade", False)
        ))

        # 4. Cascade to children if needed
        if update.get("cascade"):
            children = self._get_children(entity_type, entity_id)
            for child in children:
                self.propagate_update(
                    child.id,
                    child.type,
                    update
                )
```

### 4.4 Conflict Resolution

**Strategy**: Event-based updates with last-write-wins

```python
# Agents don't write context directly
# They emit update requests via event bus
# Single writer (ContextService) handles all updates
# This eliminates race conditions

# Example:
agent1.request_context_update(task_id, {"status": "IN_PROGRESS"})
agent2.request_context_update(task_id, {"progress": 0.5})

# Both updates queued and applied atomically
# No conflicts because single writer handles both
```

---

## 5. UnifiedContextService Implementation

### 5.1 Core API Design

```python
class UnifiedContextService:
    """
    Single API for all entity context operations.

    Replaces separate get_project_context, get_work_item_context, get_task_context
    with unified get_context(type, id, filters).
    """

    def __init__(self, db_service: DatabaseService, project_path: Path):
        self.db = db_service
        self.project_path = project_path
        self.plugin_orchestrator = PluginOrchestrator()
        self.temporal_loader = TemporalContextLoader()
        self.cache = ContextCache(ttl=300)  # 5min cache
        self.event_bus = EventBus()

    # ============================================================
    # CORE API: Single method for all entity types
    # ============================================================

    def get_context(
        self,
        entity_type: str,  # "project"|"work_item"|"task"|"idea"
        entity_id: int,
        format: str = "rich",  # "rich"|"compact"|"minimal"
        stage_filter: Optional[str] = None,  # "D1"|"P1"|"I1"|"R1"|"O1"|"E1"
        agent_role: Optional[str] = None,  # Agent-specific filtering
        include_children: bool = False,  # Include child entity contexts
        include_inheritance: bool = True  # Show full inheritance chain
    ) -> Dict[str, Any]:
        """
        Universal context retrieval for all entity types.

        Examples:
            # Get task context for implementer in I1 stage
            context = service.get_context(
                entity_type="task",
                entity_id=42,
                stage_filter="I1",
                agent_role="code-implementer"
            )

            # Get work item with all child tasks
            context = service.get_context(
                entity_type="work_item",
                entity_id=10,
                include_children=True
            )

            # Get minimal project overview
            context = service.get_context(
                entity_type="project",
                entity_id=1,
                format="minimal"
            )
        """

        # 1. Check cache
        cache_key = self._build_cache_key(
            entity_type, entity_id, format, stage_filter, agent_role
        )
        if cached := self.cache.get(cache_key):
            return cached

        # 2. Get base entity
        entity = self._get_entity(entity_type, entity_id)
        if not entity:
            return {}

        # 3. Build hierarchical context
        context = self._build_hierarchical_context(entity)

        # 4. Load supporting data
        supporting = self._load_supporting_data(entity)

        # 5. Load code context
        code = self._load_code_context(entity)

        # 6. Calculate quality metrics
        quality = self._calculate_quality_metrics(entity, context)

        # 7. Assemble unified structure
        unified = {
            "entity": self._serialize_entity(entity),
            "context": context,
            "supporting": supporting,
            "code": code,
            "quality": quality,
            "meta": {
                "generated_at": datetime.utcnow(),
                "format_version": "1.0.0",
                "entity_type": entity_type,
                "entity_id": entity_id
            }
        }

        # 8. Apply format (minimal, compact, rich)
        if format == "minimal":
            unified = self._apply_minimal_format(unified)
        elif format == "compact":
            unified = self._apply_compact_format(unified)

        # 9. Apply stage filter
        if stage_filter:
            unified = apply_stage_filter(unified, stage_filter)

        # 10. Apply agent filter
        if agent_role:
            unified = apply_agent_filter(unified, agent_role)

        # 11. Remove inheritance if not requested
        if not include_inheritance:
            unified["context"].pop("inheritance", None)

        # 12. Include children if requested
        if include_children:
            unified["children"] = self._load_children_contexts(entity)

        # 13. Cache and return
        self.cache.set(cache_key, unified)
        return unified

    # ============================================================
    # UPDATE API: Context modification
    # ============================================================

    def update_context(
        self,
        entity_type: str,
        entity_id: int,
        updates: Dict[str, Any],
        propagate: bool = True
    ) -> None:
        """
        Update context and propagate to children if needed.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            updates: Context updates to apply
            propagate: Whether to cascade to children
        """

        # 1. Update entity context in database
        entity = self._get_entity(entity_type, entity_id)
        self._apply_updates(entity, updates)

        # 2. Invalidate caches (all views of this entity)
        self.cache.invalidate_entity(entity_type, entity_id)

        # 3. Publish event
        self.event_bus.publish(ContextUpdatedEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            updates=updates,
            timestamp=datetime.utcnow()
        ))

        # 4. Propagate to children (if hierarchical change)
        if propagate and updates.get("affects_children"):
            children = self._get_children(entity)
            for child in children:
                self.update_context(
                    child.__class__.__name__.lower(),
                    child.id,
                    updates,
                    propagate=True
                )

    # ============================================================
    # INTERNAL: Helper methods
    # ============================================================

    def _build_hierarchical_context(self, entity) -> Dict[str, Any]:
        """Build context with inheritance chain"""
        # Implementation similar to existing service
        # But with explicit override tracking
        pass

    def _load_supporting_data(self, entity) -> Dict[str, Any]:
        """Load documents, evidence, events, etc."""
        return {
            "documents": self._get_documents(entity),
            "evidence": self._get_evidence(entity),
            "events": self._get_events(entity),
            "summaries": self._get_summaries(entity),
            "dependencies": self._get_dependencies(entity)
        }

    def _load_code_context(self, entity) -> Dict[str, Any]:
        """Load plugin facts and amalgamations"""
        return {
            "plugin_facts": self._get_plugin_facts(entity),
            "amalgamations": self._get_amalgamations(entity),
            "patterns": self._detect_patterns(entity)
        }

    def _calculate_quality_metrics(
        self,
        entity,
        context
    ) -> Dict[str, Any]:
        """Calculate confidence, completeness, freshness"""
        return {
            "confidence": self._calculate_confidence(context),
            "completeness": self._calculate_completeness(entity, context),
            "freshness": self._calculate_freshness(entity),
            "last_validated": entity.updated_at,
            "warnings": self._get_quality_warnings(entity, context)
        }
```

### 5.2 Migration from Existing Service

**Current**: Separate methods per entity type
```python
context = service.get_project_context(1)
context = service.get_work_item_context(10)
context = service.get_task_context(42)
```

**New**: Unified API
```python
context = service.get_context("project", 1)
context = service.get_context("work_item", 10)
context = service.get_context("task", 42)
```

**Migration Strategy**: Backward-compatible wrapper
```python
def get_task_context(self, task_id: int) -> Dict[str, Any]:
    """DEPRECATED: Use get_context("task", task_id) instead"""
    return self.get_context("task", task_id)
```

---

## 6. CLI Integration

### 6.1 Unified CLI Commands

```bash
# All entity types use same command pattern
apm project show <id> [options]
apm work-item show <id> [options]
apm task show <id> [options]
apm idea show <id> [options]

# Common options (consistent across all commands)
--format=json|yaml|rich         # Output format
--stage=D1|P1|I1|R1|O1|E1      # Stage filtering
--agent=<role>                  # Agent-scoped view
--include-children              # Include child contexts
--include-inheritance           # Show inheritance chain
--quality-only                  # Quality metrics only
--compact                       # Minimal output
```

### 6.2 Implementation Example

```python
# File: agentpm/cli/commands/context/show.py

import click
from agentpm.core.context.unified_service import UnifiedContextService


@click.command()
@click.argument('entity_id', type=int)
@click.option('--format', type=click.Choice(['json', 'yaml', 'rich']),
              default='rich')
@click.option('--stage', type=click.Choice(['D1', 'P1', 'I1', 'R1', 'O1', 'E1']))
@click.option('--agent', type=str, help='Agent role for scoped view')
@click.option('--include-children', is_flag=True)
@click.option('--include-inheritance', is_flag=True)
@click.option('--quality-only', is_flag=True)
@click.option('--compact', is_flag=True)
def show(entity_id, format, stage, agent, include_children,
         include_inheritance, quality_only, compact):
    """Show unified context for entity"""

    # Get service
    service = UnifiedContextService(db, project_path)

    # Get entity type from command group
    entity_type = click.get_current_context().parent.info_name

    # Get context
    context = service.get_context(
        entity_type=entity_type,
        entity_id=entity_id,
        format='compact' if compact else 'rich',
        stage_filter=stage,
        agent_role=agent,
        include_children=include_children
    )

    # Filter if needed
    if quality_only:
        context = {
            "quality": context["quality"],
            "meta": context["meta"]
        }

    if not include_inheritance and "context" in context:
        context["context"].pop("inheritance", None)

    # Output
    if format == 'json':
        click.echo(json.dumps(context, indent=2, default=str))
    elif format == 'yaml':
        click.echo(yaml.dump(context, default_flow_style=False))
    else:  # rich
        render_rich_context(context)
```

### 6.3 Usage Examples

```bash
# Get task context for implementer (I1 stage)
apm task show 42 --stage=I1 --agent=code-implementer --format=json

# Get work item with all child tasks
apm work-item show 10 --include-children --format=rich

# Get quality metrics only
apm task show 42 --quality-only

# Get compact view without inheritance
apm task show 42 --compact --include-inheritance=false

# Pipe to jq for filtering
apm task show 42 --format=json | jq '.context.six_w.what'
```

---

## 7. Quality Metrics Calculation

### 7.1 Confidence Score

**Formula**: Based on evidence coverage and validation

```python
def calculate_confidence(context: Dict[str, Any]) -> float:
    """
    Calculate confidence score (0.0-1.0).

    Factors:
    - Evidence coverage (% of 6W dimensions with evidence)
    - Validation recency (how recently validated)
    - Stakeholder confirmation (explicit approval)
    - Plugin fact verification (tech stack detected)
    """

    scores = []

    # 1. Evidence coverage (40%)
    six_w = context.get("six_w", {})
    dimensions_with_evidence = sum(
        1 for dim in ["who", "what", "where", "when", "why", "how"]
        if six_w.get(dim) and any(six_w[dim].values())
    )
    evidence_score = dimensions_with_evidence / 6.0
    scores.append(evidence_score * 0.4)

    # 2. Validation recency (30%)
    last_validated = context.get("last_validated")
    if last_validated:
        days_since = (datetime.utcnow() - last_validated).days
        recency_score = max(0, 1 - (days_since / 30))  # Decay over 30 days
        scores.append(recency_score * 0.3)

    # 3. Stakeholder confirmation (20%)
    stakeholder_confirmed = context.get("stakeholder_confirmed", False)
    scores.append(0.2 if stakeholder_confirmed else 0)

    # 4. Plugin verification (10%)
    plugin_facts = context.get("plugin_facts", {})
    verification_score = 1.0 if plugin_facts else 0.5
    scores.append(verification_score * 0.1)

    return sum(scores)
```

### 7.2 Completeness Score

**Formula**: Based on required fields population

```python
def calculate_completeness(
    entity,
    context: Dict[str, Any]
) -> float:
    """
    Calculate completeness score (0.0-1.0).

    Stage-specific requirements:
    - D1: Why value + What objectives
    - P1: All 6W dimensions + dependencies
    - I1: How approach + Code patterns
    - R1: Acceptance criteria + Test evidence
    - O1: Deployment info + Monitoring
    - E1: Metrics + Feedback
    """

    stage = context.get("stage", {}).get("current")
    required_fields = STAGE_REQUIREMENTS.get(stage, [])

    filled_fields = sum(
        1 for field in required_fields
        if get_nested(context, field) is not None
    )

    return filled_fields / len(required_fields) if required_fields else 0.5
```

### 7.3 Freshness Score

**Formula**: Based on update recency and change frequency

```python
def calculate_freshness(entity) -> float:
    """
    Calculate freshness score (0.0-1.0).

    Considers:
    - Time since last update (decay over time)
    - Update frequency (regular updates = higher score)
    - Active stage (IN_PROGRESS = fresher than COMPLETED)
    """

    # Time decay
    hours_since_update = (datetime.utcnow() - entity.updated_at).total_seconds() / 3600
    time_score = max(0, 1 - (hours_since_update / 168))  # 7 days

    # Status freshness
    status_scores = {
        "IN_PROGRESS": 1.0,
        "REVIEW": 0.9,
        "BLOCKED": 0.8,
        "COMPLETED": 0.5,
        "ARCHIVED": 0.0
    }
    status_score = status_scores.get(entity.status, 0.5)

    # Combine (weighted)
    return (time_score * 0.7) + (status_score * 0.3)
```

---

## 8. Implementation Roadmap

### Phase 1: Core Service (2-3 days)

**Goal**: Implement `UnifiedContextService` with basic functionality

**Tasks**:
1. Create `UnifiedContextService` class
2. Implement `get_context()` method (all entity types)
3. Implement context inheritance logic
4. Add stage filtering
5. Add quality metrics calculation
6. Write unit tests (>90% coverage)

**Deliverables**:
- `agentpm/core/context/unified_service.py` (new)
- Tests: `tests/core/context/test_unified_service.py`

### Phase 2: Multi-Agent Support (2 days)

**Goal**: Add agent coordination features

**Tasks**:
1. Implement agent-scoped filtering
2. Create `ParallelAgentCoordinator`
3. Implement `ContextUpdatePropagator`
4. Add event-based update system
5. Write integration tests

**Deliverables**:
- `agentpm/core/context/agent_coordinator.py` (new)
- `agentpm/core/context/update_propagator.py` (new)
- Tests: `tests/core/context/test_agent_coordination.py`

### Phase 3: CLI Integration (1 day)

**Goal**: Update CLI commands to use unified service

**Tasks**:
1. Update `apm task show` command
2. Update `apm work-item show` command
3. Update `apm project show` command
4. Add `apm idea show` command
5. Add consistent options to all commands
6. Write CLI integration tests

**Deliverables**:
- Updated: `agentpm/cli/commands/task/show.py`
- Updated: `agentpm/cli/commands/work_item/show.py`
- Updated: `agentpm/cli/commands/project/show.py`
- New: `agentpm/cli/commands/idea/show.py`
- Tests: `tests/cli/test_unified_context_commands.py`

### Phase 4: Testing & Validation (2 days)

**Goal**: Comprehensive testing and performance validation

**Tasks**:
1. Unit tests for all components (>90% coverage)
2. Integration tests for multi-agent scenarios
3. Performance testing (cache effectiveness)
4. Token efficiency validation
5. Documentation updates

**Deliverables**:
- Complete test suite
- Performance benchmarks
- Updated documentation

**Success Criteria**:
- ✅ Test coverage >90%
- ✅ All entity types return consistent schema
- ✅ Stage filtering reduces tokens by 40-80%
- ✅ Multi-agent parallel execution works without conflicts
- ✅ Cache hit rate >70% for repeated queries
- ✅ Context updates propagate in <100ms

---

## 9. Performance Considerations

### 9.1 Caching Strategy

**TTL Cache**: 5-minute expiry for context queries
```python
# Cache key format
cache_key = f"context:{entity_type}:{entity_id}:{stage}:{agent}"

# Invalidation triggers
- Entity update → Invalidate all views
- Hierarchical update → Invalidate entity + children
- Manual refresh → Invalidate specific entity
```

**Expected Performance**:
- First query: ~200ms (database + plugin system)
- Cached query: ~2ms (memory lookup)
- Cache hit rate: >70% (multi-agent scenarios)

### 9.2 Database Optimization

**Current Queries**: Multiple separate queries per entity
```python
# Before (N queries)
project = get_project(id)
context = get_context(id)
documents = get_documents(id)
evidence = get_evidence(id)
events = get_events(id)
```

**Optimized**: Single query with joins
```python
# After (1 query with joins)
unified = get_unified_context(entity_type, id)  # Single query
```

**Expected Performance**:
- Query reduction: 5-7 queries → 1 query
- Latency improvement: ~150ms → ~50ms
- Database load reduction: 80%

### 9.3 Token Efficiency

**Stage Filtering Gains**:
```
Discovery (D1):   15K → 3K tokens  (80% reduction)
Planning (P1):    15K → 8K tokens  (47% reduction)
Implementation:   15K → 12K tokens (20% reduction)
Review (R1):      15K → 6K tokens  (60% reduction)
Operations (O1):  15K → 5K tokens  (67% reduction)
Evolution (E1):   15K → 7K tokens  (53% reduction)

Average: 54% token reduction
```

**Agent Filtering Gains**:
```
Code implementer: 12K → 8K tokens  (33% reduction)
Test runner:      12K → 5K tokens  (58% reduction)
Quality gate:     12K → 10K tokens (17% reduction)
Doc writer:       12K → 4K tokens  (67% reduction)

Average: 44% token reduction
```

**Combined Filtering**: Up to **75% token reduction** (stage + agent)

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# Test unified API consistency
def test_get_context_returns_consistent_schema():
    """All entity types return same schema structure"""

    project_ctx = service.get_context("project", 1)
    work_item_ctx = service.get_context("work_item", 10)
    task_ctx = service.get_context("task", 42)
    idea_ctx = service.get_context("idea", 5)

    # All must have same top-level keys
    expected_keys = {"entity", "context", "supporting", "code", "quality", "meta"}
    assert set(project_ctx.keys()) == expected_keys
    assert set(work_item_ctx.keys()) == expected_keys
    assert set(task_ctx.keys()) == expected_keys
    assert set(idea_ctx.keys()) == expected_keys

# Test inheritance chain
def test_context_inheritance_preserves_parent_values():
    """Task inherits work item and project context"""

    task_ctx = service.get_context("task", 42, include_inheritance=True)

    assert "project_context" in task_ctx["context"]["inheritance"]
    assert "parent_context" in task_ctx["context"]["inheritance"]
    assert "overrides" in task_ctx["context"]["inheritance"]

    # Verify inheritance chain
    project_tech = task_ctx["context"]["inheritance"]["project_context"]["tech_stack"]
    assert project_tech == ["python", "django"]  # Inherited

# Test stage filtering
def test_stage_filter_reduces_context_size():
    """Stage filtering reduces token usage"""

    full_ctx = service.get_context("task", 42)
    d1_ctx = service.get_context("task", 42, stage_filter="D1")
    i1_ctx = service.get_context("task", 42, stage_filter="I1")

    # D1 should be significantly smaller
    assert len(str(d1_ctx)) < len(str(full_ctx)) * 0.3

    # I1 should have code context, D1 should not
    assert i1_ctx["code"]["amalgamations"]
    assert not d1_ctx["code"]["amalgamations"]

# Test agent filtering
def test_agent_filter_focuses_context():
    """Agent filtering provides role-specific view"""

    impl_ctx = service.get_context("task", 42, agent_role="code-implementer")
    test_ctx = service.get_context("task", 42, agent_role="test-runner")

    # Implementer gets full code context
    assert impl_ctx["code"]["amalgamations"]

    # Tester gets acceptance criteria focus
    assert "acceptance_criteria" in test_ctx["entity"]
    assert not test_ctx["code"].get("amalgamations")  # Excluded
```

### 10.2 Integration Tests

```python
# Test multi-agent coordination
def test_parallel_agent_coordination():
    """Multiple agents work on tasks without conflicts"""

    coordinator = ParallelAgentCoordinator(service)

    # Setup parallel execution
    result = coordinator.coordinate_parallel_execution(
        work_item_id=10,
        task_assignments={
            "code-implementer": 42,
            "test-runner": 43,
            "doc-toucher": 44
        }
    )

    # All agents get consistent shared context
    assert result["shared_context"]["work_item"]["id"] == 10

    # Each agent gets role-specific context
    assert "code" in result["agent_contexts"]["code-implementer"]
    assert "acceptance_criteria" in result["agent_contexts"]["test-runner"]["entity"]
    assert "documents" in result["agent_contexts"]["doc-toucher"]["supporting"]

    # Dependencies tracked
    assert result["coordination"]["dependencies"]

# Test context update propagation
def test_context_update_propagates_to_children():
    """Updates cascade to child entities"""

    propagator = ContextUpdatePropagator(service, event_bus, cache)

    # Update work item (parent)
    propagator.propagate_update(
        entity_type="work_item",
        entity_id=10,
        update={"tech_stack": ["python", "fastapi"], "cascade": True}
    )

    # Verify child tasks see update
    task_ctx = service.get_context("task", 42)
    assert "fastapi" in task_ctx["context"]["inheritance"]["parent_context"]["tech_stack"]

    # Verify event published
    assert event_bus.events[-1].entity_type == "work_item"
    assert event_bus.events[-1].entity_id == 10
```

### 10.3 Performance Tests

```python
# Test cache effectiveness
def test_cache_improves_query_performance():
    """Repeated queries use cache"""

    # First query (no cache)
    start = time.time()
    ctx1 = service.get_context("task", 42)
    first_time = time.time() - start

    # Second query (cached)
    start = time.time()
    ctx2 = service.get_context("task", 42)
    cached_time = time.time() - start

    # Cache should be 10x+ faster
    assert cached_time < first_time * 0.1
    assert ctx1 == ctx2  # Same result

# Test token efficiency
def test_stage_filtering_token_reduction():
    """Stage filtering achieves expected token reduction"""

    full_ctx = service.get_context("task", 42)
    d1_ctx = service.get_context("task", 42, stage_filter="D1")

    full_tokens = estimate_tokens(str(full_ctx))
    d1_tokens = estimate_tokens(str(d1_ctx))

    reduction = (full_tokens - d1_tokens) / full_tokens
    assert reduction > 0.70  # Expect >70% reduction for D1
```

---

## 11. Future Enhancements

### 11.1 Context Versioning

**Purpose**: Track context changes over time for audit and rollback

```python
class ContextVersion:
    """Track context changes with version history"""

    def save_version(self, entity_type, entity_id, context):
        """Save context snapshot with version number"""
        pass

    def get_version(self, entity_type, entity_id, version):
        """Retrieve specific context version"""
        pass

    def diff_versions(self, entity_type, entity_id, v1, v2):
        """Show differences between versions"""
        pass
```

### 11.2 Context Templates

**Purpose**: Pre-defined context structures for common scenarios

```python
CONTEXT_TEMPLATES = {
    "api_feature": {
        "six_w": {
            "what": {"endpoints": [], "methods": []},
            "how": {"authentication": "JWT", "rate_limiting": True}
        },
        "supporting": {"documents": ["API design doc"]}
    },

    "bug_fix": {
        "six_w": {
            "what": {"bug_description": "", "reproduction_steps": []},
            "why": {"impact": "", "urgency": ""}
        }
    }
}
```

### 11.3 Context Validation Rules

**Purpose**: Enforce context quality standards

```python
VALIDATION_RULES = {
    "D1": {
        "required": ["six_w.why.value", "six_w.what.objectives"],
        "min_confidence": 0.6
    },

    "P1": {
        "required": ["six_w.when.timeline", "dependencies"],
        "min_completeness": 0.8
    },

    "I1": {
        "required": ["six_w.how.approach", "code.patterns"],
        "min_confidence": 0.7,
        "min_freshness": 0.8
    }
}
```

### 11.4 Context Recommendations

**Purpose**: AI-powered suggestions for context improvement

```python
class ContextRecommender:
    """Suggest context improvements using AI"""

    def analyze_gaps(self, context):
        """Identify missing or weak context areas"""
        pass

    def suggest_improvements(self, context):
        """Recommend specific context enhancements"""
        pass

    def auto_enrich(self, context):
        """Automatically fill gaps using AI + research"""
        pass
```

---

## 12. Success Criteria

### 12.1 Functional Requirements

- ✅ **Consistent API**: Single `get_context()` method handles all entity types
- ✅ **Unified Schema**: Same JSON structure for Project/WorkItem/Task/Idea
- ✅ **Inheritance Chain**: Explicit tracking (project → work_item → task)
- ✅ **Stage Filtering**: D1-E1 filters reduce tokens by 40-80%
- ✅ **Agent Filtering**: Role-specific views optimize context
- ✅ **Multi-Agent Safe**: Parallel execution without conflicts
- ✅ **Quality Metrics**: Confidence/completeness/freshness scores

### 12.2 Performance Requirements

- ✅ **Query Speed**: <50ms for cached queries, <200ms uncached
- ✅ **Cache Hit Rate**: >70% in multi-agent scenarios
- ✅ **Token Efficiency**: >50% average reduction with filtering
- ✅ **Update Propagation**: <100ms for context updates
- ✅ **Database Load**: 80% reduction via query optimization

### 12.3 Quality Requirements

- ✅ **Test Coverage**: >90% for all new code
- ✅ **API Consistency**: 100% schema compliance across entity types
- ✅ **Documentation**: Complete API docs + usage examples
- ✅ **Backward Compatibility**: Existing code continues to work
- ✅ **Error Handling**: Graceful degradation for missing data

---

## 13. Conclusion

This unified context delivery system provides:

1. **Consistency**: Single API, unified schema, predictable behavior
2. **Efficiency**: Stage/agent filtering reduces tokens by 50-75%
3. **Coordination**: Multi-agent parallel execution without conflicts
4. **Quality**: Built-in metrics for confidence/completeness/freshness
5. **Scalability**: Caching + optimization for performance
6. **Maintainability**: Clear architecture, comprehensive tests

The system enables **rapid multi-agent AI development** by providing agents with exactly the context they need, when they need it, in a consistent and efficient format.

**Next Steps**:
1. Review and approve design
2. Begin Phase 1 implementation (Core Service)
3. Iterate based on early feedback
4. Complete phased rollout (4 phases, ~7 days total)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-17
**Author**: System Architect
**Status**: Ready for Review & Implementation
