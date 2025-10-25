# WorkItem Model Lifecycle Context Tracking Analysis

**Date**: 2025-10-17
**Objective**: Evaluate current WorkItem model and recommend improvements for better lifecycle context tracking

---

## Executive Summary

The current WorkItem model captures basic lifecycle information but **lacks comprehensive tracking** of lifecycle events, decisions, and temporal context. While the foundation exists (metadata JSON field, events system), **lifecycle history is fragmented** across multiple systems without a unified view.

**Key Findings**:
- ✅ **Strong foundation**: Pydantic models, event system, workflow service
- ⚠️ **Gap**: No unified lifecycle history on WorkItem
- ⚠️ **Gap**: Metadata usage is ad-hoc and inconsistent
- ⚠️ **Gap**: Missing: decision points, effort tracking, blocker history
- ✅ **Opportunity**: Events system exists but not integrated into WorkItem

**Recommended Approach**: **Enhance metadata structure + Add lifecycle_history field + Integrate events**

---

## 1. Current WorkItem Model Structure

### 1.1 Model Fields (agentpm/core/database/models/work_item.py)

```python
class WorkItem(BaseModel):
    # Identity
    id: Optional[int]
    project_id: int
    parent_work_item_id: Optional[int]

    # Core
    name: str (1-200 chars)
    description: Optional[str]
    type: WorkItemType  # feature/analysis/objective/research
    business_context: Optional[str]

    # Configuration (WI-40 consolidation)
    metadata: Optional[str] = '{}'  # JSON TEXT field
    is_continuous: bool = False

    # Planning
    effort_estimate_hours: Optional[float]
    priority: int (1-5)

    # Lifecycle
    status: WorkItemStatus  # draft/ready/active/review/done/archived

    # NEW (Migration 0011)
    phase: Optional[Phase]  # D1/P1/I1/R1/O1/E1
    due_date: Optional[datetime]
    not_before: Optional[datetime]

    # Timestamps
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

### 1.2 Database Schema

```sql
CREATE TABLE work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    parent_work_item_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    business_context TEXT,
    metadata TEXT DEFAULT '{}',  -- JSON storage
    effort_estimate_hours REAL,
    priority INTEGER DEFAULT 3,
    status TEXT DEFAULT 'draft',
    is_continuous INTEGER DEFAULT 0,
    phase TEXT,  -- NEW: Phase tracking
    due_date TIMESTAMP,
    not_before TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
);

-- Indexes for queries
CREATE INDEX idx_work_items_project ON work_items(project_id);
CREATE INDEX idx_work_items_parent ON work_items(parent_work_item_id);
CREATE INDEX idx_work_items_status ON work_items(status);
CREATE INDEX idx_work_items_type ON work_items(type);
CREATE INDEX idx_work_items_priority ON work_items(priority);
CREATE INDEX idx_work_items_continuous ON work_items(is_continuous);
```

---

## 2. Metadata Usage Analysis

### 2.1 Current Metadata Patterns (from production database)

**Pattern 1: Structured metadata (WI-40 consolidation)**
```json
{
  "why_value": {
    "problem": "...",
    "desired_outcome": "...",
    "business_impact": "...",
    "target_metrics": [...]
  },
  "ownership": {
    "raci": {
      "responsible": "...",
      "accountable": "...",
      "consulted": [...],
      "informed": [...]
    }
  },
  "scope": {
    "in_scope": [...],
    "out_of_scope": [...]
  },
  "artifacts": {
    "code_paths": [...],
    "docs_paths": [...]
  }
}
```

**Pattern 2: Migration metadata** (temporary)
```json
{
  "migration_0015": {
    "original_phase": null,
    "migrated_at": "2025-10-12T15:46:03.650603",
    "inferred_from": "status",
    "original_status": "accepted"
  }
}
```

**Pattern 3: Ad-hoc metadata** (inconsistent)
```json
{
  "gates": {
    "D1": {
      "status": "done",
      "completion": 100
    }
  }
}
```

### 2.2 Metadata Problems

| Issue | Impact | Example |
|-------|--------|---------|
| **No schema validation** | Inconsistent structure | Some have `why_value`, some don't |
| **No lifecycle history** | Can't see state transitions | When did draft→ready happen? |
| **No decision tracking** | Lost context | Why was approach X chosen? |
| **No effort tracking** | Can't compare estimate vs actual | Planned 16h, actually took 24h |
| **Blocker history missing** | Can't analyze patterns | What blocked this work item? |
| **Mixed concerns** | Hard to query | Migration data + business data |

---

## 3. Lifecycle Information Currently Tracked

### 3.1 What IS Tracked

| Data | Where | Quality |
|------|-------|---------|
| **Status** | `work_items.status` | ✅ Strong - enum validated |
| **Phase** | `work_items.phase` | ✅ Strong - enum validated (NEW) |
| **Creation time** | `work_items.created_at` | ✅ Strong - automatic |
| **Update time** | `work_items.updated_at` | ✅ Strong - automatic |
| **Effort estimate** | `work_items.effort_estimate_hours` | ✅ Good - stored |
| **Priority** | `work_items.priority` | ✅ Strong - validated |
| **Business context** | `work_items.business_context` | ⚠️ Weak - unstructured text |
| **Workflow events** | `session_events` table | ✅ Strong - event system |

### 3.2 What is NOT Tracked

| Missing Data | Impact | Use Case |
|--------------|--------|----------|
| **Status transition history** | Can't see progression | "When did this become active?" |
| **Phase transition history** | Can't track phase gates | "When did we pass P1 gate?" |
| **Decision history** | Lost context | "Why did we choose React over Vue?" |
| **Blocker history** | Can't analyze delays | "What blocked this for 2 weeks?" |
| **Effort actual** | Can't improve estimates | "How long did this really take?" |
| **Agent assignments over time** | No accountability | "Who worked on this?" |
| **Rework cycles** | Can't improve quality | "How many times did we rework?" |
| **Gate completion metadata** | No progress visibility | "What % of P1 requirements met?" |

---

## 4. Events System (Existing Infrastructure)

### 4.1 Event System Architecture

**Events Table** (session_events):
```sql
CREATE TABLE session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- 40+ event types
    event_category TEXT NOT NULL,  -- workflow/tool/decision/reasoning/error/session
    event_severity TEXT NOT NULL DEFAULT 'info',
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL,
    event_data TEXT NOT NULL,  -- JSON payload
    project_id INTEGER,
    work_item_id INTEGER,  -- Can filter by work item
    task_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
);
```

**Event Types** (40+ types across 6 categories):
- **Workflow**: `WORK_ITEM_STARTED`, `WORK_ITEM_DONE`, `TASK_STARTED`, `TASK_DONE`, `BLOCKER_ADDED`, `BLOCKER_RESOLVED`
- **Tool**: `READ_FILE`, `WRITE_FILE`, `EDIT_FILE`, `BASH_COMMAND`
- **Decision**: `DECISION_MADE`, `APPROACH_CHOSEN`, `TRADE_OFF_ANALYZED`
- **Reasoning**: `REASONING_STARTED`, `HYPOTHESIS_FORMED`
- **Error**: `ERROR_ENCOUNTERED`, `ERROR_RESOLVED`, `TEST_FAILED`
- **Session**: `SESSION_STARTED`, `MILESTONE_REACHED`, `PHASE_TRANSITION`

**Event Capture** (WI-35 Task #173 - Integrated):
```python
# WorkflowService automatically emits events on state transitions
def transition_work_item(...):
    # ... validation logic ...

    # NEW: Emit workflow event
    self._emit_workflow_event(
        entity_type='work_item',
        entity_id=updated.id,
        entity_name=updated.name,
        previous_status=work_item.status.value,
        new_status=new_status.value,
        work_item_id=updated.id,
        project_id=updated.project_id
    )
```

### 4.2 Event System Gap

**Problem**: Events are captured but **not surfaced on WorkItem model**

- ✅ Events stored: `session_events` table with `work_item_id` foreign key
- ✅ Query methods exist: `get_events_by_work_item(db, work_item_id)`
- ❌ **NOT integrated**: WorkItem model doesn't expose lifecycle history
- ❌ **Manual query required**: Must separately query events table

**Impact**: Rich lifecycle data exists but is **invisible to agents and UI**

---

## 5. Comparison with Best Practices

### 5.1 Jira Work Item Model

**Jira Tracks**:
- **History**: Full status transition log with timestamps, users, and reasons
- **Changelog**: All field changes (priority, assignee, estimates)
- **Comments**: Discussion and decisions tied to specific times
- **Worklogs**: Actual time spent (effort tracking)
- **Links**: Related issues, blockers, dependencies
- **Attachments**: Evidence and artifacts

**Key Feature**: **Rich history tab** showing complete lifecycle

### 5.2 GitHub Issue Model

**GitHub Tracks**:
- **Timeline**: Every status change, label change, assignment
- **Comments**: Discussion with timestamps and authors
- **Linked PRs**: Code changes tied to issue
- **Events**: Automatically generated timeline entries
- **Reactions**: Community engagement

**Key Feature**: **Unified timeline** combining manual and automatic events

### 5.3 Linear Issue Model

**Linear Tracks**:
- **Activity**: Status changes, assignments, priority changes
- **Estimates**: Original vs updated estimates
- **Cycles**: Which sprint/cycle the issue was in
- **Relations**: Blocks, blocked by, duplicates
- **Subscribers**: Who's watching the issue

**Key Feature**: **Smart estimates** based on historical data

### 5.4 AIPM Gaps vs Industry Leaders

| Feature | Jira | GitHub | Linear | AIPM | Gap Severity |
|---------|------|--------|--------|------|--------------|
| Status history | ✅ | ✅ | ✅ | ❌ | 🔴 Critical |
| Field change log | ✅ | ✅ | ✅ | ❌ | 🟡 Medium |
| Decision capture | ✅ (comments) | ✅ (comments) | ✅ (comments) | ⚠️ (metadata) | 🟡 Medium |
| Effort tracking | ✅ (worklogs) | ❌ | ✅ | ⚠️ (estimate only) | 🟡 Medium |
| Blocker history | ✅ | ✅ (labels) | ✅ | ❌ | 🟡 Medium |
| Timeline view | ✅ | ✅ | ✅ | ❌ | 🔴 Critical |
| Related work | ✅ | ✅ | ✅ | ✅ (parent_id) | 🟢 Good |

---

## 6. Schema Design Proposals

### 6.1 Option A: Enhance Metadata (Lightweight)

**Approach**: Structure metadata JSON with clear schema

**Metadata Schema**:
```json
{
  "business": {
    "why_value": {...},
    "ownership": {...},
    "scope": {...},
    "artifacts": {...}
  },
  "lifecycle": {
    "status_history": [
      {
        "status": "draft",
        "phase": null,
        "timestamp": "2025-10-12T10:00:00Z",
        "agent": "planner",
        "reason": "Initial creation"
      },
      {
        "status": "ready",
        "phase": "P1_PLAN",
        "timestamp": "2025-10-12T14:30:00Z",
        "agent": "specifier",
        "reason": "Planning complete, requirements validated"
      }
    ],
    "decisions": [
      {
        "decision": "Use React over Vue",
        "rationale": "Team expertise + ecosystem maturity",
        "alternatives": ["Vue", "Angular"],
        "timestamp": "2025-10-12T11:15:00Z",
        "confidence": 0.85
      }
    ],
    "blockers": [
      {
        "blocker": "API key approval pending",
        "blocked_at": "2025-10-13T09:00:00Z",
        "resolved_at": "2025-10-13T16:45:00Z",
        "resolution": "API key approved by security team",
        "duration_hours": 7.75
      }
    ],
    "effort": {
      "estimated_hours": 16.0,
      "actual_hours": 24.5,
      "variance_hours": 8.5,
      "variance_pct": 53.1,
      "time_entries": [
        {
          "date": "2025-10-14",
          "hours": 4.0,
          "agent": "implementer",
          "description": "Backend API implementation"
        }
      ]
    }
  },
  "gates": {
    "D1_DISCOVERY": {
      "status": "done",
      "completion_pct": 100,
      "completed_at": "2025-10-12T12:00:00Z",
      "requirements_met": ["why_value", "scope_defined", "risks_identified"]
    },
    "P1_PLAN": {
      "status": "in_progress",
      "completion_pct": 75,
      "requirements_met": ["tasks_decomposed", "estimates_provided"],
      "requirements_pending": ["dependencies_mapped"]
    }
  }
}
```

**Pros**:
- ✅ Minimal schema changes (reuse metadata field)
- ✅ Flexible structure (can evolve over time)
- ✅ Easy to query with JSON functions (`json_extract`)
- ✅ Backward compatible (existing metadata preserved)

**Cons**:
- ❌ Large JSON blobs (performance concern for frequent updates)
- ❌ No referential integrity (can't foreign key to agents/sessions)
- ❌ Hard to index (can't create indexes on JSON fields efficiently)
- ❌ Query complexity (JSON path expressions)

**Best For**: Quick iteration, prototyping, MVP

---

### 6.2 Option B: Add Dedicated Columns (Structured)

**Approach**: Add specific columns for lifecycle tracking

**New Columns**:
```sql
ALTER TABLE work_items ADD COLUMN lifecycle_history TEXT;  -- JSON array
ALTER TABLE work_items ADD COLUMN decisions TEXT;  -- JSON array
ALTER TABLE work_items ADD COLUMN blockers TEXT;  -- JSON array
ALTER TABLE work_items ADD COLUMN effort_actual_hours REAL;
ALTER TABLE work_items ADD COLUMN effort_variance_hours REAL;
ALTER TABLE work_items ADD COLUMN last_status_change TIMESTAMP;
ALTER TABLE work_items ADD COLUMN last_agent TEXT;  -- Foreign key to agents
ALTER TABLE work_items ADD COLUMN completion_percentage INTEGER DEFAULT 0;

-- Indexes for queries
CREATE INDEX idx_work_items_last_status_change ON work_items(last_status_change);
CREATE INDEX idx_work_items_completion ON work_items(completion_percentage);
```

**Pros**:
- ✅ Efficient queries (can index columns)
- ✅ Type safety (REAL, INTEGER, TIMESTAMP)
- ✅ Clear intent (explicit columns = explicit tracking)
- ✅ Better performance (no JSON parsing)

**Cons**:
- ❌ Schema rigidity (requires migrations for changes)
- ❌ Still uses JSON for arrays (lifecycle_history, decisions)
- ❌ More columns = wider table (potential row size issues)

**Best For**: Stable requirements, production-ready system

---

### 6.3 Option C: Separate Tables (Normalized)

**Approach**: Create dedicated tables for lifecycle events

**New Tables**:
```sql
-- Status transition history
CREATE TABLE work_item_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    from_phase TEXT,
    to_phase TEXT,
    agent TEXT,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

-- Decision history
CREATE TABLE work_item_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    alternatives TEXT,  -- JSON array
    confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent TEXT,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
);

-- Blocker history
CREATE TABLE work_item_blockers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER NOT NULL,
    blocker TEXT NOT NULL,
    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution TEXT,
    duration_hours REAL,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
);

-- Effort tracking (time entries)
CREATE TABLE work_item_time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER NOT NULL,
    date DATE NOT NULL,
    hours REAL NOT NULL CHECK(hours > 0),
    agent TEXT,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_status_history_work_item ON work_item_status_history(work_item_id, timestamp);
CREATE INDEX idx_decisions_work_item ON work_item_decisions(work_item_id, timestamp);
CREATE INDEX idx_blockers_work_item ON work_item_blockers(work_item_id);
CREATE INDEX idx_time_entries_work_item ON work_item_time_entries(work_item_id, date);
```

**Pros**:
- ✅ Fully normalized (proper relational design)
- ✅ Efficient queries (dedicated indexes)
- ✅ Referential integrity (foreign keys everywhere)
- ✅ Scalable (can store unlimited history)
- ✅ Easy to aggregate (SUM hours, COUNT transitions)

**Cons**:
- ❌ Most complex (4 new tables + migrations)
- ❌ Multiple queries required (join overhead)
- ❌ More code to maintain (CRUD for each table)

**Best For**: Production system, long-term scalability, complex analytics

---

### 6.4 Option D: Hybrid Approach (Recommended)

**Approach**: Combine enhanced metadata + event integration + selective columns

**Changes**:
1. **Enhance metadata** with structured lifecycle schema (Option A)
2. **Add key columns** for performance (Option B subset)
3. **Integrate events** into WorkItem model (compute from session_events)
4. **Defer normalization** until scale requires it (Option C future)

**Specific Changes**:

**1. Add Computed Properties to WorkItem Model**:
```python
class WorkItem(BaseModel):
    # ... existing fields ...

    # NEW: Computed lifecycle properties (not stored, computed from events)
    @property
    def lifecycle_history(self) -> List[dict]:
        """
        Get status transition history from events system.

        Returns:
            List of status transitions with timestamps, agents, reasons
        """
        # Query session_events for WORK_ITEM_STARTED, WORK_ITEM_DONE, etc.
        # Return structured list
        pass

    @property
    def current_phase_progress(self) -> dict:
        """
        Get current phase completion status.

        Returns:
            {
                'phase': 'P1_PLAN',
                'completion_pct': 75,
                'requirements_met': [...],
                'requirements_pending': [...]
            }
        """
        pass

    @property
    def effort_variance(self) -> dict:
        """
        Get effort estimate vs actual variance.

        Returns:
            {
                'estimated': 16.0,
                'actual': 24.5,
                'variance': 8.5,
                'variance_pct': 53.1
            }
        """
        pass
```

**2. Structure metadata with clear schema**:
```python
# In metadata JSON (validated by Pydantic)
{
  "business": {
    "why_value": {...},  # Existing
    "ownership": {...},  # Existing
    "scope": {...},  # Existing
    "artifacts": {...}  # Existing
  },
  "lifecycle": {  # NEW
    "decisions": [...],
    "blockers": [...],
    "effort_entries": [...]
  },
  "gates": {  # NEW
    "D1_DISCOVERY": {...},
    "P1_PLAN": {...}
  }
}
```

**3. Add selective columns for performance**:
```sql
ALTER TABLE work_items ADD COLUMN effort_actual_hours REAL;
ALTER TABLE work_items ADD COLUMN last_status_change TIMESTAMP;
ALTER TABLE work_items ADD COLUMN completion_percentage INTEGER DEFAULT 0;
```

**4. Integrate events into queries**:
```python
def get_work_item_with_history(db, work_item_id: int) -> WorkItem:
    """
    Get work item with computed lifecycle history from events.
    """
    work_item = get_work_item(db, work_item_id)

    # Compute lifecycle_history from session_events
    events = get_events_by_work_item(db, work_item_id)
    work_item._lifecycle_events = events  # Cache for computed properties

    return work_item
```

**Pros**:
- ✅ **Best of all worlds**: Structured metadata + event integration + performance
- ✅ **Incremental**: Can implement in phases
- ✅ **Backward compatible**: Existing code works
- ✅ **Scalable**: Can normalize later if needed
- ✅ **Event-driven**: Leverages existing infrastructure

**Cons**:
- ⚠️ Complexity: Multiple data sources (metadata + events + columns)
- ⚠️ Consistency: Must keep metadata and events in sync

**Best For**: APM (Agent Project Manager) (balances flexibility + performance + maintainability)

---

## 7. Implementation Recommendations

### 7.1 Phase 1: Quick Wins (Week 1)

**Goal**: Surface existing lifecycle data

1. **Add computed properties to WorkItem model**:
   - `lifecycle_history` (from session_events)
   - `status_transitions` (from session_events)
   - `blocker_history` (from session_events)

2. **Enhance metadata schema validation**:
   - Create Pydantic models for metadata structure
   - Validate on write (catch schema errors early)
   - Provide migration script for existing records

3. **Add WorkItem method**: `get_lifecycle_summary()`
   ```python
   def get_lifecycle_summary(self) -> dict:
       return {
           'created_at': self.created_at,
           'status': self.status,
           'phase': self.phase,
           'days_in_current_status': ...,
           'total_lifecycle_days': ...,
           'status_transitions': len(self.lifecycle_history),
           'blockers_count': ...,
           'effort_variance': self.effort_variance
       }
   ```

**Impact**: Agents and UI can immediately see lifecycle context

### 7.2 Phase 2: Structured Tracking (Week 2-3)

**Goal**: Capture new lifecycle data systematically

1. **Enhance WorkflowService**:
   - Capture decision metadata on status transitions
   - Track blocker add/resolve events
   - Log effort entries on task completion

2. **Add CLI commands**:
   - `apm work-item decision add <id> "decision" "rationale"`
   - `apm work-item blocker add <id> "blocker description"`
   - `apm work-item time log <id> 4.5 "description"`

3. **Update web UI**:
   - Show lifecycle timeline on work item detail page
   - Display decisions and blockers
   - Show effort tracking (estimate vs actual)

**Impact**: Comprehensive lifecycle tracking for all new work

### 7.3 Phase 3: Normalization (Month 2-3)

**Goal**: Optimize for scale and analytics

1. **Evaluate performance**:
   - Measure query times for lifecycle data
   - Identify bottlenecks (JSON parsing, event queries)

2. **Normalize if needed**:
   - Create `work_item_status_history` table
   - Create `work_item_decisions` table
   - Migrate existing metadata to tables

3. **Add analytics**:
   - Status transition velocity (time in each status)
   - Blocker analysis (common blockers, resolution time)
   - Effort estimation accuracy (variance trends)

**Impact**: Scalable lifecycle tracking ready for production

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Metadata schema drift** | High | Medium | Pydantic validation + migration scripts |
| **Event/metadata sync issues** | Medium | High | Single source of truth (events), metadata caches |
| **Performance degradation** | Low | High | Selective indexing + computed properties cached |
| **Schema evolution complexity** | Medium | Medium | Incremental approach + version migrations |
| **Backward compatibility** | Low | High | Graceful degradation for missing data |

---

## 9. Trade-Off Analysis

### 9.1 Metadata vs Dedicated Tables

| Factor | Metadata (JSON) | Dedicated Tables |
|--------|----------------|------------------|
| **Flexibility** | ✅ High - easy to change structure | ❌ Low - requires migrations |
| **Performance** | ⚠️ Medium - JSON parsing overhead | ✅ High - indexed columns |
| **Query complexity** | ❌ High - JSON path expressions | ✅ Low - standard SQL |
| **Referential integrity** | ❌ None | ✅ Full - foreign keys |
| **Implementation time** | ✅ Fast - reuse existing field | ❌ Slow - new tables + CRUD |
| **Scalability** | ⚠️ Medium - large JSON blobs | ✅ High - normalized design |

**Recommendation**: Start with metadata (fast iteration), normalize when scale demands it

### 9.2 Events-Only vs Hybrid

| Factor | Events-Only | Hybrid (Events + Metadata) |
|--------|-------------|----------------------------|
| **Data duplication** | ✅ None - single source | ⚠️ Some - metadata caches events |
| **Query performance** | ❌ Slower - always join events | ✅ Faster - cached summaries |
| **Consistency** | ✅ Perfect - one source | ⚠️ Risk - sync needed |
| **Feature richness** | ⚠️ Limited - events only | ✅ Rich - events + business data |
| **Complexity** | ✅ Simple - one system | ⚠️ Medium - two systems |

**Recommendation**: Hybrid approach - events for history, metadata for summaries/business data

---

## 10. Success Metrics

### 10.1 Completion Criteria

- ✅ All WorkItems have structured lifecycle_history
- ✅ Agents can query "What blocked this work item?"
- ✅ UI shows complete timeline of status changes
- ✅ Decision history captured and searchable
- ✅ Effort variance tracked and analyzed
- ✅ No performance regression on work item queries

### 10.2 KPIs

| Metric | Target | Measure |
|--------|--------|---------|
| **Lifecycle visibility** | 100% of work items | % with lifecycle_history populated |
| **Decision capture** | >80% of major decisions | % work items with decisions logged |
| **Effort accuracy** | <20% variance | Avg effort variance across work items |
| **Query performance** | <100ms | Avg time to load work item with history |
| **Agent satisfaction** | >90% | Survey: "Can you understand work item history?" |

---

## 11. Conclusion

**Current State**: Foundation exists (events, metadata) but lifecycle tracking is fragmented

**Recommended Approach**: **Hybrid (Option D)** - Enhance metadata + integrate events + selective columns

**Rationale**:
1. **Fast iteration**: Leverage existing metadata field
2. **Event-driven**: Use existing session_events infrastructure
3. **Performance**: Add selective columns for common queries
4. **Scalable**: Can normalize later if scale demands it

**Next Steps**:
1. Implement Phase 1 (Quick Wins) - Add computed properties to WorkItem
2. Create metadata schema validation (Pydantic models)
3. Update WorkflowService to capture decisions/blockers
4. Build lifecycle timeline UI component

**Timeline**: 3 weeks to production-ready lifecycle tracking

---

**Questions for Discussion**:
1. Should we normalize immediately (Option C) or defer (Option D)?
2. Which lifecycle events are most critical to capture first?
3. How should we migrate existing work items to new schema?
4. Should effort tracking be automated (via session) or manual (via CLI)?
