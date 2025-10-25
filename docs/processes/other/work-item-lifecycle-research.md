# Work Item Lifecycle Tracking Research
## Comparative Analysis of Leading PM Systems

**Date**: 2025-10-17
**Focus**: Lifecycle tracking patterns, not general features
**Systems Analyzed**: Jira, GitHub Issues, Linear, Asana

---

## Executive Summary

All leading PM systems track work item lifecycle through **timestamp fields** (created, modified, completed) and **transition history**. However, they differ significantly in their approaches:

- **Jira**: Two-table design (transaction groups + field changes) with comprehensive changelog
- **GitHub**: Event sourcing pattern with timeline events API
- **Linear**: Built-in cycle time tracking with duration comparators
- **Asana**: Simpler timestamp-based tracking with custom fields

**Key Finding**: Modern systems favor **immutable event logs** over mutable status fields for accurate lifecycle analysis.

---

## Feature Comparison Matrix

| Feature | Jira | GitHub | Linear | Asana |
|---------|------|--------|--------|-------|
| **Core Timestamps** |
| Created timestamp | ✅ `CREATED` | ✅ `created_at` | ✅ `createdAt` | ✅ `created_at` |
| Modified timestamp | ✅ (via history) | ✅ `updated_at` | ✅ (via history) | ✅ `modified_at` |
| Completed timestamp | ✅ `resolutiondate` | ✅ `closed_at` | ✅ `completedAt` | ✅ `completed_at` |
| **History/Changelog** |
| Change history API | ✅ `expand=changelog` | ✅ Timeline Events API | ✅ Issue history GraphQL | ❌ No native API |
| Field-level tracking | ✅ Old/new values | ✅ Event-specific | ✅ State transitions | ⚠️ Via audit logs |
| User attribution | ✅ `AUTHOR` | ✅ `actor` | ✅ `user` | ✅ `modified_by` |
| **Database Schema** |
| History storage | Two tables:<br/>- changegroup<br/>- changeitem | Event sourcing:<br/>- Event log<br/>- Transaction metadata | GraphQL schema:<br/>- Temporal fields<br/>- History queries | Single table:<br/>- Timestamp fields<br/>- Audit logs |
| Change granularity | Field-level | Event-level | State-level | Task-level |
| **Metrics** |
| Cycle time | ⚠️ Calculated | ⚠️ Calculated | ✅ Built-in | ⚠️ Calculated |
| Lead time | ⚠️ Calculated | ⚠️ Calculated | ✅ Built-in | ⚠️ Calculated |
| Time in status | ✅ From history | ✅ From events | ✅ Built-in | ❌ Not native |
| **API Features** |
| Pagination | 100-item limit | Cursor-based | GraphQL pagination | Page-based |
| Filtering | ✅ JQL queries | ✅ Timeline filters | ✅ GraphQL filters | ✅ `modified_since` |
| Sorting | ⚠️ Manual required | ✅ Chronological | ✅ Built-in | ✅ By timestamp |
| **Advanced Features** |
| Status categories | ✅ Backlog/Progress/Done | ✅ Open/Closed | ✅ 5 categories | ⚠️ Custom only |
| Workflow transitions | ✅ Full history | ✅ State events | ✅ State changes | ❌ Binary only |
| Dependencies tracking | ✅ Link types | ✅ Linked issues | ✅ Blocks/blocked by | ✅ Dependencies array |
| Custom fields | ✅ Extensive | ✅ Issue templates | ✅ Team fields | ✅ 6 field types |

---

## Common Patterns Identified

### 1. **Core Temporal Triad**
All systems track three fundamental timestamps:
- **Created**: When work item entered the system
- **Modified**: Last change to any field
- **Completed**: When work item finished

```sql
-- Universal pattern
CREATE TABLE work_items (
    created_at    TIMESTAMP NOT NULL,
    modified_at   TIMESTAMP NOT NULL,
    completed_at  TIMESTAMP NULL
);
```

### 2. **Separate History Tables**
Both Jira and audit trail best practices use separate tables for history:

**Jira Pattern**:
```sql
-- Transaction group
CREATE TABLE changegroup (
    id         BIGINT PRIMARY KEY,
    issueid    BIGINT NOT NULL,
    author     VARCHAR(255),
    created    TIMESTAMP NOT NULL
);

-- Individual field changes
CREATE TABLE changeitem (
    id         BIGINT PRIMARY KEY,
    groupid    BIGINT NOT NULL,  -- FK to changegroup
    field      VARCHAR(255),     -- Field name
    oldvalue   TEXT,             -- Previous value ID
    oldstring  TEXT,             -- Previous value display
    newvalue   TEXT,             -- New value ID
    newstring  TEXT              -- New value display
);
```

### 3. **Immutable Event Logs**
GitHub and event sourcing patterns favor immutable event streams:

```sql
-- Event log pattern
CREATE TABLE events (
    id              BIGINT PRIMARY KEY,
    transaction_id  BIGINT NOT NULL,
    entity_type     VARCHAR(50),
    entity_id       BIGINT,
    event_type      VARCHAR(50),  -- 'created', 'assigned', 'closed', etc.
    actor_id        BIGINT,
    created_at      TIMESTAMP NOT NULL,
    payload         JSONB         -- Event-specific data
);
```

### 4. **Calculated vs Built-in Metrics**
- **Jira/GitHub/Asana**: Calculate cycle/lead time from timestamps
- **Linear**: Stores pre-calculated duration fields

```sql
-- Calculated approach (Jira, GitHub, Asana)
SELECT
    completed_at - created_at AS lead_time,
    completed_at - started_at AS cycle_time
FROM work_items;

-- Pre-calculated approach (Linear)
SELECT cycle_time_duration  -- Already computed
FROM issues;
```

### 5. **Status Categories**
Most systems group statuses into high-level categories:
- **Backlog** → Not started
- **Planned** → Scheduled
- **Started/In Progress** → Active work
- **Completed** → Done
- **Canceled** → Abandoned

### 6. **User Attribution**
All systems track WHO made changes:
- Jira: `AUTHOR` field
- GitHub: `actor` field
- Linear: `user` field
- Asana: `modified_by` field

---

## Novel Ideas Worth Considering

### 1. **Jira's Two-Table Design** ⭐⭐⭐⭐⭐
**What**: Separate transaction groups from field changes
**Why**: Allows atomic transaction tracking + detailed field-level history
**Benefit**: Can query "what changed together" vs "what changed over time"

```sql
-- Single transaction changing multiple fields
changegroup: {id: 1001, issueid: 42, author: "dev", created: "2025-10-17T10:30:00Z"}
changeitem:  {id: 5001, groupid: 1001, field: "status", old: "In Progress", new: "Done"}
changeitem:  {id: 5002, groupid: 1001, field: "assignee", old: "dev", new: "qa"}
```

### 2. **Linear's Duration Comparators** ⭐⭐⭐⭐
**What**: `NullableDurationComparator` type for cycle time
**Why**: First-class support for duration queries
**Benefit**: Enables efficient queries like "cycle_time > 3 days"

```graphql
query {
  issues(filter: {
    cycleTime: { gt: "P3D" }  # ISO 8601 duration
  }) {
    nodes {
      title
      cycleTime
    }
  }
}
```

### 3. **GitHub's Transaction ID Polling** ⭐⭐⭐⭐
**What**: Use `pg_current_xact_id()` for reliable event polling
**Why**: Prevents missing events in distributed systems
**Benefit**: Guaranteed consistency for webhooks/integrations

```sql
-- Every event gets transaction context
INSERT INTO events (entity_id, type, txn_id)
VALUES (42, 'status_changed', pg_current_xact_id());

-- Poll for new events reliably
SELECT * FROM events WHERE txn_id > :last_seen_txn;
```

### 4. **Temporal Tables with Exclusion Constraints** ⭐⭐⭐⭐
**What**: PostgreSQL exclusion constraints on tsrange
**Why**: Prevents overlapping history entries
**Benefit**: Database-level guarantee of history integrity

```sql
CREATE TABLE work_item_history (
    work_item_id BIGINT NOT NULL,
    status VARCHAR(50),
    valid_during TSTZRANGE NOT NULL,
    EXCLUDE USING GIST (work_item_id WITH =, valid_during WITH &&)
);
```

### 5. **Linear's Status Categories** ⭐⭐⭐
**What**: 5 categories (Backlog, Planned, Started, Completed, Canceled)
**Why**: Standardized lifecycle phases across all teams
**Benefit**: Consistent metrics even with custom statuses

### 6. **Jira's Field Type Awareness** ⭐⭐⭐
**What**: `changeitem.FIELDTYPE` distinguishes system vs custom fields
**Why**: Different handling for different field types
**Benefit**: Type-safe history queries

### 7. **GitHub's Event Type Taxonomy** ⭐⭐⭐⭐
**What**: Comprehensive event type system (40+ types)
**Why**: Precise tracking of all actions
**Examples**:
- `committed` - Code changes
- `cross-referenced` - Linked to other issue
- `merged` - PR merged
- `review_requested` - Review requested

---

## Recommended Features for AIPM

### **Tier 1: Must-Have (Foundation)**

#### 1. **Core Temporal Fields**
```sql
ALTER TABLE work_items ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE work_items ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE work_items ADD COLUMN completed_at TIMESTAMP NULL;
ALTER TABLE work_items ADD COLUMN started_at TIMESTAMP NULL;  -- For cycle time
ALTER TABLE work_items ADD COLUMN canceled_at TIMESTAMP NULL;
```

**Why**: Industry standard, enables basic lifecycle analysis
**Effort**: Low (1-2 hours)
**Value**: High (required for any metrics)

#### 2. **Separate Event Log Table** (GitHub/Event Sourcing Pattern)
```sql
CREATE TABLE work_item_events (
    id              BIGSERIAL PRIMARY KEY,
    work_item_id    BIGINT NOT NULL REFERENCES work_items(id),
    event_type      VARCHAR(50) NOT NULL,  -- 'created', 'status_changed', 'assigned', etc.
    actor_id        BIGINT REFERENCES users(id),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Event-specific data
    old_value       TEXT,
    new_value       TEXT,
    metadata        JSONB,  -- Flexible storage for event-specific details

    -- Transaction tracking (GitHub pattern)
    transaction_id  BIGINT DEFAULT txid_current(),

    INDEX idx_work_item_events_item (work_item_id),
    INDEX idx_work_item_events_type (event_type),
    INDEX idx_work_item_events_created (created_at),
    INDEX idx_work_item_events_txn (transaction_id)
);
```

**Why**:
- Immutable audit trail
- Enables accurate lifecycle reconstruction
- Supports webhooks/integrations
- Future-proof for analytics

**Effort**: Medium (4-8 hours)
**Value**: Very High (foundation for all advanced features)

#### 3. **Status Category Mapping** (Linear Pattern)
```sql
ALTER TABLE work_items ADD COLUMN status_category VARCHAR(20)
    CHECK (status_category IN ('BACKLOG', 'PLANNED', 'STARTED', 'COMPLETED', 'CANCELED'));

-- Auto-update status_category when status changes
CREATE TRIGGER update_status_category
BEFORE UPDATE ON work_items
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION sync_status_category();
```

**Why**: Consistent metrics across custom statuses
**Effort**: Low (2-3 hours)
**Value**: High (enables cross-team comparisons)

---

### **Tier 2: Should-Have (Enhanced Analytics)**

#### 4. **Pre-calculated Metrics** (Linear Pattern)
```sql
ALTER TABLE work_items ADD COLUMN lead_time_seconds BIGINT;
ALTER TABLE work_items ADD COLUMN cycle_time_seconds BIGINT;
ALTER TABLE work_items ADD COLUMN time_to_start_seconds BIGINT;  -- created → started

-- Update trigger
CREATE TRIGGER calculate_lifecycle_metrics
AFTER UPDATE ON work_items
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status OR NEW.completed_at IS NOT NULL)
EXECUTE FUNCTION update_lifecycle_metrics();
```

**Why**: Fast queries without repeated calculations
**Effort**: Medium (3-4 hours)
**Value**: Medium-High (performance for dashboards)

#### 5. **Time in Status Tracking**
```sql
CREATE TABLE work_item_status_time (
    work_item_id    BIGINT NOT NULL REFERENCES work_items(id),
    status          VARCHAR(50) NOT NULL,
    entered_at      TIMESTAMP NOT NULL,
    exited_at       TIMESTAMP NULL,
    duration_seconds BIGINT,  -- Pre-calculated

    PRIMARY KEY (work_item_id, status, entered_at),
    INDEX idx_status_time_status (status),
    INDEX idx_status_time_duration (duration_seconds)
);
```

**Why**: Enables bottleneck analysis ("where do things get stuck?")
**Effort**: Medium (4-6 hours)
**Value**: High (identifies process improvements)

#### 6. **Event Type Taxonomy** (GitHub Pattern)
```yaml
event_types:
  lifecycle:
    - created
    - started
    - status_changed
    - completed
    - canceled
    - reopened

  assignment:
    - assigned
    - unassigned
    - agent_changed

  relationships:
    - linked
    - unlinked
    - blocked_by_added
    - blocked_by_removed

  metadata:
    - priority_changed
    - estimate_changed
    - description_updated

  collaboration:
    - commented
    - mentioned
    - subscribed
```

**Why**: Rich event analytics and filtering
**Effort**: Medium (4-6 hours for taxonomy + implementation)
**Value**: Medium (enables advanced queries)

---

### **Tier 3: Nice-to-Have (Advanced Features)**

#### 7. **Transaction Grouping** (Jira Two-Table Pattern)
```sql
CREATE TABLE work_item_transactions (
    id              BIGSERIAL PRIMARY KEY,
    work_item_id    BIGINT NOT NULL REFERENCES work_items(id),
    actor_id        BIGINT REFERENCES users(id),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_id  BIGINT DEFAULT txid_current(),

    INDEX idx_transactions_item (work_item_id),
    INDEX idx_transactions_created (created_at)
);

-- Events reference transactions
ALTER TABLE work_item_events
    ADD COLUMN transaction_group_id BIGINT REFERENCES work_item_transactions(id);
```

**Why**: Query "what changed together" in single operations
**Effort**: High (6-8 hours)
**Value**: Medium (useful for audit/debugging)

#### 8. **Temporal History Tables** (PostgreSQL System Versioning)
```sql
-- Enable temporal tracking
CREATE TABLE work_items_history (LIKE work_items);
ALTER TABLE work_items_history ADD COLUMN valid_from TIMESTAMP NOT NULL;
ALTER TABLE work_items_history ADD COLUMN valid_to TIMESTAMP NOT NULL;

-- Exclusion constraint (prevents overlaps)
ALTER TABLE work_items_history
    ADD CONSTRAINT work_items_history_no_overlap
    EXCLUDE USING GIST (id WITH =, tstzrange(valid_from, valid_to) WITH &&);

-- Trigger to maintain history
CREATE TRIGGER maintain_work_items_history
AFTER UPDATE ON work_items
FOR EACH ROW
EXECUTE FUNCTION archive_to_history();
```

**Why**: Point-in-time queries ("what did this look like on 2025-10-01?")
**Effort**: High (8-10 hours)
**Value**: Low-Medium (nice for reporting, rarely critical)

#### 9. **Duration Comparator Types** (Linear Pattern)
```python
# API filter support
class DurationFilter:
    gt: Optional[timedelta]  # Greater than
    gte: Optional[timedelta]  # Greater than or equal
    lt: Optional[timedelta]  # Less than
    lte: Optional[timedelta]  # Less than or equal

# Usage
api.work_items.list(
    filter={
        "cycle_time": {"gt": timedelta(days=3)},
        "status_category": "COMPLETED"
    }
)
```

**Why**: Cleaner API for duration queries
**Effort**: Medium (4-5 hours for API layer)
**Value**: Low-Medium (nice ergonomics, not essential)

---

## Implementation Priorities

### **Phase 1: Foundation (Week 1)**
1. Add core timestamp fields (created_at, updated_at, completed_at, started_at)
2. Create work_item_events table with basic event types
3. Implement status_category field with sync trigger
4. Build event logging service

**Deliverables**:
- Basic lifecycle tracking operational
- Events logged for all status changes
- Status categories working

### **Phase 2: Analytics (Week 2)**
1. Add pre-calculated metric fields (lead_time, cycle_time)
2. Create work_item_status_time table
3. Implement metric calculation triggers
4. Build dashboard queries for cycle/lead time

**Deliverables**:
- Cycle time and lead time metrics available
- Time-in-status analytics working
- Basic bottleneck detection possible

### **Phase 3: Advanced (Week 3+)**
1. Expand event type taxonomy
2. Add transaction grouping (if needed)
3. Consider temporal history tables (if reporting requires)
4. Implement duration filter API

**Deliverables**:
- Rich event analytics
- Grouped transaction queries
- Advanced reporting capabilities

---

## Best Practices from Research

### 1. **Timestamp Hygiene**
- ✅ Use UTC for all timestamps (Asana pattern)
- ✅ Use ISO-8601 format for APIs (all systems)
- ✅ Store as TIMESTAMP WITH TIME ZONE in PostgreSQL
- ✅ Never update created_at or completed_at once set

### 2. **Event Immutability**
- ✅ Events are append-only (never UPDATE or DELETE)
- ✅ Use soft deletes if correction needed (add correction event)
- ✅ Store transaction_id for reliable polling (GitHub pattern)

### 3. **History Efficiency**
- ⚠️ Jira's 100-item pagination limit teaches us to plan for scale
- ✅ Index event tables by work_item_id, event_type, created_at
- ✅ Consider partitioning by date for large event volumes
- ✅ Archive old events to separate tables/storage

### 4. **Metrics Calculation**
- ✅ Pre-calculate common metrics (Linear pattern)
- ✅ Update metrics on status changes (trigger-based)
- ✅ Use percentiles (85th, 95th) not averages for reporting
- ✅ Store duration in seconds for precision, format for display

### 5. **Status Management**
- ✅ Separate custom statuses from status categories
- ✅ Allow teams to customize statuses within categories
- ✅ Validate status transitions (workflow enforcement)
- ✅ Track time in each status for bottleneck analysis

### 6. **API Design**
- ✅ Support expand/include patterns for history (Jira)
- ✅ Offer timeline-style endpoints (GitHub)
- ✅ Enable filtering by modified_since (Asana)
- ✅ Provide cursor-based pagination for large datasets

---

## Key Insights

### **What Everyone Does**
1. Core temporal triad (created/modified/completed)
2. Separate history/event storage
3. User attribution for all changes
4. Cycle time and lead time metrics
5. Status workflow management

### **What Separates Leaders**
1. **Jira**: Comprehensive field-level history with transaction grouping
2. **Linear**: Built-in metrics with excellent UX
3. **GitHub**: Event sourcing architecture with rich event types
4. **Asana**: Simplicity and custom fields flexibility

### **What's Missing from Most Systems**
- Point-in-time reconstruction ("what did this look like on X date?")
- Predictive metrics ("when will this be done based on history?")
- Automatic bottleneck detection ("this status has 2x avg time")
- Dependency impact analysis ("completing this unblocks 5 others")

---

## Recommendations for AIPM

### **Adopt Immediately**
1. ✅ **Core temporal fields** - Industry standard, easy win
2. ✅ **Event log table** - Foundation for everything else
3. ✅ **Status categories** - Enables cross-team metrics
4. ✅ **Transaction ID tracking** - Future-proof for integrations

### **Adopt Soon**
1. ⚠️ **Pre-calculated metrics** - Performance benefit for dashboards
2. ⚠️ **Time in status tracking** - High-value analytics
3. ⚠️ **Event type taxonomy** - Rich event filtering

### **Consider Later**
1. 🔮 **Transaction grouping** - Nice for audit, adds complexity
2. 🔮 **Temporal history tables** - Powerful but over-engineered for MVP
3. 🔮 **Duration comparator types** - API ergonomics, not critical

### **Skip/Defer**
1. ❌ **Jira's changegroup/changeitem verbatim** - Too complex for our scale
2. ❌ **Full event sourcing** - Overkill unless doing CQRS architecture
3. ❌ **Asana's custom field complexity** - Focus on core lifecycle first

---

## Architecture Recommendation

```sql
-- RECOMMENDED SCHEMA FOR APM (Agent Project Manager)

-- 1. Add core temporal fields to work_items
ALTER TABLE work_items
    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN started_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN canceled_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN status_category VARCHAR(20) CHECK (status_category IN
        ('BACKLOG', 'PLANNED', 'STARTED', 'COMPLETED', 'CANCELED'));

-- 2. Create event log (immutable audit trail)
CREATE TABLE work_item_events (
    id BIGSERIAL PRIMARY KEY,
    work_item_id BIGINT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    actor_id BIGINT REFERENCES agents(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Change tracking
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,

    -- Event metadata
    metadata JSONB,
    transaction_id BIGINT DEFAULT txid_current(),

    INDEX idx_events_work_item (work_item_id, created_at DESC),
    INDEX idx_events_type (event_type),
    INDEX idx_events_created (created_at),
    INDEX idx_events_transaction (transaction_id)
);

-- 3. Pre-calculated metrics (updated by triggers)
ALTER TABLE work_items
    ADD COLUMN lead_time_seconds BIGINT,     -- created → completed
    ADD COLUMN cycle_time_seconds BIGINT,    -- started → completed
    ADD COLUMN time_to_start_seconds BIGINT; -- created → started

-- 4. Time in status tracking (optional, Phase 2)
CREATE TABLE work_item_status_history (
    work_item_id BIGINT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    status_category VARCHAR(20) NOT NULL,
    entered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    exited_at TIMESTAMP WITH TIME ZONE,
    duration_seconds BIGINT,

    PRIMARY KEY (work_item_id, status, entered_at),
    INDEX idx_status_history_status (status, duration_seconds),
    INDEX idx_status_history_category (status_category)
);
```

---

## Conclusion

The research reveals a **clear pattern** across leading PM systems:
1. **Immutable event logs** are superior to mutable status fields for lifecycle analysis
2. **Pre-calculated metrics** significantly improve dashboard performance
3. **Status categories** enable consistent metrics across custom workflows
4. **Transaction context** is essential for reliable integrations

**For APM (Agent Project Manager)**, the recommended approach is:
- ✅ Adopt core patterns from all systems (timestamps, events, categories)
- ✅ Implement Linear's pre-calculated metrics for performance
- ✅ Use GitHub's transaction ID pattern for reliability
- ✅ Keep Jira's comprehensive history without the complexity
- ⚠️ Defer advanced features (temporal tables, grouping) until proven need

This gives us **80% of the value with 20% of the complexity**.

---

**Research Sources**:
- Jira API Documentation & Database Schema
- GitHub REST API - Timeline Events & Issue Events
- Linear GraphQL API Schema
- Asana API Documentation
- Event Sourcing & Temporal Data Patterns
- Audit Trail Design Best Practices

**Next Steps**:
1. Review recommendations with team
2. Prioritize Phase 1 features for immediate implementation
3. Create migration plan for existing work_items
4. Design event logging service architecture
5. Build prototype with cycle time dashboard
