# Agent Methods Module

**Location**: `agentpm/core/database/methods/agents.py`
**Work Item**: WI-32 (Agent Registry Agent)
**Status**: ✅ Complete (100% test coverage)

---

## Overview

Type-safe CRUD operations for Agent entities with lifecycle management and workflow integration. Implements AIPM's three-layer pattern (Pydantic → Adapters → Methods) for managing specialized agents assigned to tasks.

**Key Features**:
- 9 agent methods (create, read, update, delete, validate, generate tracking)
- CI-001 integration (agent validation gate for task assignment)
- Lifecycle management (draft → active → inactive → archived)
- Generation tracking (staleness detection for regeneration)
- Performance optimized (<10ms queries with 4 indexes)

---

## Quick Reference

### Import

```python
from agentpm.core.database import DatabaseService
from agentpm.core.database.methods import agents as agent_methods
from agentpm.core.database.models import Agent
```

### Common Operations

```python
# CREATE agent
agent = Agent(project_id=1, role="python-implementer", display_name="Python Implementer")
created = agent_methods.create_agent(db, agent)

# READ by role (most common)
agent = agent_methods.get_agent_by_role(db, project_id=1, role="python-implementer")

# LIST active agents
active = agent_methods.list_agents(db, project_id=1, active_only=True)

# VALIDATE agent (CI-001 gate)
valid, error = agent_methods.validate_agent_exists(db, project_id=1, role="python-implementer")

# MARK as generated
agent_methods.mark_agent_generated(db, agent_id=1, file_path=".claude/agents/python-implementer.md")

# GET stale agents (need regeneration)
stale = agent_methods.get_stale_agents(db, project_id=1, threshold_days=7)
```

---

## API Reference

### CREATE

#### `create_agent(service, agent: Agent) -> Agent`

Create new agent with validation.

**Validations**:
- Project must exist (FOREIGN KEY check)
- Role must be unique per project (UNIQUE constraint)
- Pydantic validates all field constraints

**Example**:
```python
agent = Agent(
    project_id=1,
    role="aipm-database-developer",
    display_name="Database Developer",
    description="Implements three-layer database pattern",
    capabilities=["database", "pydantic", "testing"],
    is_active=True,
    agent_type="implementer"
)
created = agent_methods.create_agent(db, agent)
print(f"Created agent ID: {created.id}")
```

---

### READ

#### `get_agent(service, agent_id: int) -> Optional[Agent]`

Get agent by database ID.

**Returns**: Agent if found, None otherwise

**Example**:
```python
agent = agent_methods.get_agent(db, agent_id=1)
if agent:
    print(f"Agent: {agent.display_name}")
```

#### `get_agent_by_role(service, project_id: int, role: str) -> Optional[Agent]`

Get agent by role within project (most common query pattern).

**Performance**: <10ms (indexed on role)

**Example**:
```python
agent = agent_methods.get_agent_by_role(db, project_id=1, role="aipm-database-developer")
if agent and agent.is_active:
    print(f"Agent available: {agent.display_name}")
```

#### `list_agents(service, project_id: Optional[int], active_only: bool) -> List[Agent]`

List agents with optional filtering.

**Parameters**:
- `project_id`: Filter by project (required)
- `active_only`: If True, only return is_active=True agents

**Returns**: List of agents (empty if none found), sorted by role

**Performance**: <20ms for typical 5-10 agents per project

**Examples**:
```python
# All agents
all_agents = agent_methods.list_agents(db, project_id=1)

# Active agents only
active = agent_methods.list_agents(db, project_id=1, active_only=True)

# Iterate agents
for agent in active:
    print(f"{agent.role}: {agent.display_name}")
```

---

### UPDATE

#### `update_agent(service, agent_id: int, **updates) -> Optional[Agent]`

Update agent fields with Pydantic validation.

**Parameters**:
- `agent_id`: Agent to update
- `**updates`: Fields to update (any Agent model field)

**Returns**: Updated Agent if found, None otherwise

**Examples**:
```python
# Update description
updated = agent_methods.update_agent(
    db,
    agent_id=1,
    description="Enhanced implementation specialist with security focus"
)

# Update capabilities
updated = agent_methods.update_agent(
    db,
    agent_id=1,
    capabilities=["database", "pydantic", "testing", "security"]
)

# Deactivate agent (soft delete)
updated = agent_methods.update_agent(db, agent_id=1, is_active=False)

# Reactivate agent
updated = agent_methods.update_agent(db, agent_id=1, is_active=True)
```

---

### DELETE

#### `delete_agent(service, agent_id: int) -> bool`

Delete agent (hard delete, prefer deactivation).

**Returns**: True if deleted, False if not found

**Note**: Prefer deactivation (`is_active=False`) over deletion to preserve audit trail.

**Example**:
```python
# Hard delete (rare, only for cleanup)
deleted = agent_methods.delete_agent(db, agent_id=1)

# Prefer soft delete instead
agent_methods.update_agent(db, agent_id=1, is_active=False)
```

---

### VALIDATION

#### `validate_agent_exists(service, project_id: int, role: str) -> tuple[bool, Optional[str]]`

Validate agent exists and is active (CI-001 gate).

**Used by**: WorkflowService before task assignment

**Returns**: `(is_valid, error_message)`
- `(True, None)` if agent exists and active
- `(False, error)` otherwise

**Error messages**:
- `"Agent 'role' not found"` - Agent doesn't exist
- `"Agent 'role' is inactive (is_active=False)"` - Agent deactivated

**Examples**:
```python
# Validate before assignment
valid, error = agent_methods.validate_agent_exists(
    db,
    project_id=1,
    role="aipm-database-developer"
)

if valid:
    # Assign agent to task
    task.assigned_to = "aipm-database-developer"
else:
    print(f"Cannot assign: {error}")
    # Suggest fix: apm agents list
```

**WorkflowService Integration**:
```python
# In WorkflowService.transition_task()
if new_status == TaskStatus.ACTIVE:
    valid, error = validate_agent_exists(db, project_id, task.assigned_to)
    if not valid:
        raise WorkflowError(
            f"Cannot start task: {error}\n"
            "Fix: apm agents list"
        )
```

---

### GENERATION TRACKING

#### `mark_agent_generated(service, agent_id: int, file_path: str) -> Optional[Agent]`

Mark agent as generated with file path and timestamp.

**Called after**: Successfully writing agent SOP file to filesystem

**Updates**:
- `file_path`: Path to generated `.md` file
- `generated_at`: Current UTC timestamp

**Example**:
```python
# After writing SOP file
file_path = ".claude/agents/python-implementer.md"
with open(file_path, 'w') as f:
    f.write(sop_content)

# Mark as generated
agent = agent_methods.mark_agent_generated(db, agent_id=1, file_path=file_path)
print(f"Agent generated at: {agent.generated_at}")
```

#### `get_stale_agents(service, project_id: int, threshold_days: int) -> List[Agent]`

Get agents needing regeneration (stale or never generated).

**Staleness Criteria**:
- `generated_at IS NULL` - Never generated
- `(NOW - generated_at) >= threshold_days` - Too old

**Default**: 7 days threshold

**Returns**: List of agents needing regeneration

**Example**:
```python
# Find stale agents
stale = agent_methods.get_stale_agents(db, project_id=1, threshold_days=7)

if stale:
    print(f"⚠️  {len(stale)} agents need regeneration:")
    for agent in stale:
        if not agent.generated_at:
            print(f"   - {agent.role}: Never generated")
        else:
            age_days = (datetime.utcnow() - agent.generated_at).days
            print(f"   - {agent.role}: {age_days} days old")
```

---

## Database Schema

### agents Table

```sql
CREATE TABLE agents (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Relationships
    project_id INTEGER NOT NULL,

    -- Core Fields
    role VARCHAR(100) NOT NULL,              -- e.g., 'aipm-database-developer'
    display_name VARCHAR(200) NOT NULL,      -- e.g., 'Database Developer'
    description TEXT,

    -- SOP and Capabilities
    sop_content TEXT,                        -- Optional (can be in filesystem)
    capabilities TEXT DEFAULT '[]',          -- JSON array: ["database", "pydantic"]

    -- Lifecycle State
    is_active INTEGER DEFAULT 1,             -- 1=active, 0=inactive

    -- Generation Tracking
    agent_type VARCHAR(50),                  -- 'implementer', 'tester', etc.
    file_path VARCHAR(500),                  -- e.g., '.claude/agents/python-implementer.md'
    generated_at TEXT,                       -- ISO8601: '2025-10-09T14:30:00'

    -- Audit Trail
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE (project_id, role)
);

-- Indexes for Performance
CREATE INDEX idx_agents_project ON agents(project_id);
CREATE INDEX idx_agents_role ON agents(role);
CREATE INDEX idx_agents_active ON agents(is_active);
CREATE INDEX idx_agents_type ON agents(agent_type);

-- Trigger: Update updated_at on modification
CREATE TRIGGER agents_updated_at
AFTER UPDATE ON agents
FOR EACH ROW
BEGIN
    UPDATE agents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

---

## Performance

### Query Performance (with indexes)

| Operation | Performance | Index Used |
|-----------|-------------|------------|
| `get_agent_by_role()` | <10ms | `idx_agents_role` |
| `list_agents()` | <20ms | `idx_agents_project` |
| `validate_agent_exists()` | <10ms | `idx_agents_role` |
| Agent validation in workflow | <10ms | `idx_agents_role` |

### Scalability

- **Typical**: 5-10 agents per project
- **Large**: 100 projects × 7 agents = 700 agents (handled efficiently)
- **Database size**: ~700KB for 700 agents (negligible)

---

## Integration Patterns

### WorkflowService Integration (CI-001)

```python
# In WorkflowService.transition_task()
if new_status == TaskStatus.ACTIVE:
    # Agent validation gate (CI-001)
    if not task.assigned_to:
        raise WorkflowError("Cannot start task: No agent assigned")

    valid, error = agent_methods.validate_agent_exists(
        db, project_id, task.assigned_to
    )

    if not valid:
        raise WorkflowError(f"Cannot start task: {error}")
```

### ContextService Integration (Future)

```python
# In ContextService.get_agent_context()
def get_agent_context(self, task_id: int) -> Dict[str, Any]:
    task = get_task(db, task_id)
    if task.assigned_to:
        agent = agent_methods.get_agent_by_role(
            db, project_id, task.assigned_to
        )
        if agent and agent.file_path:
            sop_content = read_file(agent.file_path)
            return {
                'role': agent.role,
                'display_name': agent.display_name,
                'capabilities': agent.capabilities,
                'sop': sop_content
            }
    return None
```

---

## Testing

**Coverage**: 100% (38 tests)
- 26 unit tests (method-level)
- 9 integration tests (workflow integration)
- 3 E2E tests (end-to-end scenarios)

**Test Location**: `tests/core/database/methods/test_agents.py`

**Run Tests**:
```bash
# All agent tests
pytest tests/core/database/methods/test_agents.py -v

# Specific test
pytest tests/core/database/methods/test_agents.py::test_create_agent -v

# Coverage report
pytest tests/core/database/methods/test_agents.py --cov=agentpm.core.database.methods.agents
```

---

## Migration

**Migration**: `migration_0005`
**Applied**: 2025-10-09

**Changes**:
- Added `idx_agents_type` index (filter by agent type)
- Added `agents_updated_at` trigger (automatic timestamp updates)

**Status**: ✅ Applied and tested

---

## Future Enhancements

### CLI Commands (Not Yet Implemented)

```bash
apm agents generate         # Generate agents from templates
apm agents list             # List all agents
apm agents list --active    # List active agents only
apm agents list --stale     # List agents needing regeneration
apm agents show <role>      # Show agent details and SOP
apm agents activate <role>  # Activate agent (set is_active=True)
apm agents deactivate <role> # Deactivate agent (set is_active=False)
apm agents regenerate <role> # Regenerate agent SOP file
apm agents regenerate --stale # Regenerate all stale agents
```

### Template Engine

Agent generation from templates (not yet implemented):
- Load template specifications from `docs/components/agents/specifications/`
- Expand templates with framework-specific values
- Write agent SOP files to `.claude/agents/*.md`
- Store metadata in agents table

---

## References

**Architecture Documentation**:
- `docs/components/agents/architecture/agent-registry-architecture.md` - Complete architecture
- `docs/components/agents/specifications/agent-priority-matrix.md` - 22 agents prioritized
- `docs/components/agents/specifications/agent-development-6w-framework.md` - Development template

**Work Item**: WI-32 (4 tasks, 6h total)
- Task #153: Design ✅ (1.5h)
- Task #154: Implementation ✅ (2.5h)
- Task #155: Testing ✅ (1.5h)
- Task #156: Documentation ✅ (0.5h)

**Next Steps**: WI-33 (Workflow Validator Agent) depends on this foundation
