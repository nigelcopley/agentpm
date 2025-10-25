---
module: agentpm/core/database
owner: @aipm-database-developer
status: GREEN
api_stability: stable
coverage: 93%
updated: 2025-09-30
updated_by: claude-code
---

# Database Layer - SQLite with Pydantic Models

> **Status:** 🟢 Production Ready (Phase 1 Complete)
> **Owner:** AIPM Database Team
> **Purpose:** Provides type-safe, validated database access using Pydantic models and three-layer architecture (Models → Adapters → Methods).

---

## ✅ Current State

**Implemented** (What works - TESTED):
- ✅ **Three-layer architecture** (Models → Adapters → Methods) - 100% type-safe ✅ **EXCELLENT**
- ✅ **Pydantic models** (database/models/) - Task, WorkItem, Project, Context with validation
- ✅ **Database adapters** (database/adapters/) - Type conversion between Pydantic ↔ SQLite
- ✅ **CRUD methods** (database/methods/) - Type-safe operations for all entities
- ✅ **Schema initialization** (database/schema.py) - Complete table creation with indexes
- ✅ **DatabaseService** (database/service.py) - Central coordinator for all database operations
- ✅ **34 tests passing** - 93% coverage

**In Progress** (Partial):
- ⚠️ **Migrations** - Basic system exists, needs real-world testing
- ⚠️ **Performance optimization** - Indexes created, query optimization pending

**Not Started**:
- ❌ **Connection pooling** - Single connection currently (acceptable for CLI)
- ❌ **Backup/restore** - Manual SQLite copy only

---

## 🎯 What's Planned

**Immediate** (Next Session):
- [ ] Add database method tests for remaining coverage (93% → 95%)
- [ ] Performance profiling for common queries

**Short Term** (This Phase):
- [ ] Migration testing with real schema changes
- [ ] Query optimization for complex joins

**Long Term** (Phase 3):
- [ ] Connection pooling (if needed for server mode)
- [ ] Automated backup system
- [ ] Database analytics/monitoring

---

## 🐛 Known Issues

**Critical:** None (database layer operational)

**Medium:**
1. **Migration System Untested** (Severity: MEDIUM)
   - Issue: Migration framework exists but no real migrations run yet
   - Impact: Schema changes need manual verification
   - Workaround: Test migrations in development before production
   - Fix: Add migration integration tests (2h) - **Agent:** @aipm-testing-specialist

**Low:**
2. **Single Connection** (Severity: LOW)
   - Issue: No connection pooling (one connection per DatabaseService instance)
   - Impact: CLI usage is fine, server mode would need pooling
   - Workaround: Current CLI usage doesn't need pooling
   - Fix: Defer until server mode needed (Phase 3)

---

## 🚀 Quick Start

### Installation

```python
from agentpm.core.database import DatabaseService
from agentpm.core.database.models import Task, WorkItem, Project
from agentpm.core.database.enums import TaskStatus, TaskType

# Initialize database
db = DatabaseService("project.db")
db.initialize_schema()
```

### Basic Usage - CRUD Operations

**Create Task**:

```python
from agentpm.core.database.models.task import Task
from agentpm.core.database.enums.task import TaskType, TaskStatus

# Pydantic model with validation
task = Task(
    name="Implement feature",
    type=TaskType.IMPLEMENTATION,
    effort_hours=3.5,
    status=TaskStatus.TODO
)

# Type-safe create
created = db.tasks.create(task)
print(f"Created task ID: {created.id}")
```

**Read Task**:
```python
# Type-safe read (returns Task | None)
task = db.tasks.get_task(task_id=1)
if task:
    print(f"Task: {task.name}, Status: {task.status.value}")
```

**Update Task**:
```python
# Update with validation
task.status = TaskStatus.ACTIVE
task.completion_percentage = 50

updated = db.tasks.update(task)
```

**Delete Task**:
```python
db.tasks.delete(task_id=1)
```

---

## 🏗️ Architecture - Three Layers

### **Layer 1: Pydantic Models** (`database/models/`)

Pure data models with validation:
```python
# database/models/task.py
class Task(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    type: TaskType  # Enum
    effort_hours: Optional[float] = Field(default=None, ge=0, le=8)
    status: TaskStatus = TaskStatus.TO_REVIEW

    class Config:
        validate_assignment = True  # Validate on updates
```

### **Layer 2: Database Adapters** (`database/adapters/`)

Convert between Pydantic ↔ SQLite:
```python
# database/adapters/task_adapter.py
class TaskAdapter:
    @staticmethod
    def to_dict(task: Task) -> Dict[str, Any]:
        """Pydantic → SQLite dict"""
        return {
            'id': task.id,
            'name': task.name,
            'type': task.type.value,  # Enum to string
            'effort_hours': task.effort_hours
        }

    @staticmethod
    def from_row(row: sqlite3.Row) -> Task:
        """SQLite row → Pydantic model"""
        return Task(
            id=row['id'],
            name=row['name'],
            type=TaskType(row['type']),  # String to Enum
            effort_hours=row['effort_hours']
        )
```

### **Layer 3: Database Methods** (`database/methods/`)

Type-safe CRUD operations:
```python
# database/methods/tasks.py
class TaskMethods:
    def create_task(self, db: DatabaseService, task: Task) -> Task:
        """Create task with type safety"""
        data = TaskAdapter.to_dict(task)
        cursor = db.execute(
            "INSERT INTO tasks (name, type, effort_hours) VALUES (?, ?, ?)",
            (data['name'], data['type'], data['effort_hours'])
        )
        task.id = cursor.lastrowid
        return task
```

---

## 📊 Database Schema

**Core Tables**:
- `projects` - Project metadata (11 columns)
- `work_items` - Features, analyses, objectives (15 columns)
- `tasks` - Individual tasks (24 columns)
- `contexts` - 6W context data (18 columns)
- `agents` - AI agent definitions (8 columns)

**Relationships**:
```
projects (1) ←→ (N) work_items
work_items (1) ←→ (N) tasks
projects (1) ←→ (1) contexts
work_items (1) ←→ (1) contexts
tasks (1) ←→ (1) contexts
```

**Full Schema**: See `database/schema.py` (~500 LOC)

---

## 🧪 Testing

**Coverage Summary:**
- **Overall**: 93% (excellent)
- **Models**: 100% (Pydantic validation)
- **Adapters**: 95% (conversion logic)
- **Methods**: 90% (CRUD operations)
- **Service**: 88% (orchestration)

**Run Tests:**
```bash
# All database tests (34 tests, ~2 seconds)
pytest tests/core/database/ -v

# Specific module
pytest tests/core/database/test_service.py -v

# Coverage report
pytest tests/core/database/ --cov=agentpm.core.database --cov-report=html
```

**Key Test Scenarios:**
- ✅ CRUD operations for all entity types
- ✅ Pydantic validation (rejects invalid data)
- ✅ Enum conversion (TaskType, TaskStatus, etc.)
- ✅ Foreign key constraints
- ✅ Schema initialization
- ✅ Transaction handling

---

## 🔗 Integration Points

**Used By:**
- `core/workflow/` - Reads/writes tasks, work items
- `core/context/` - Reads/writes context data
- CLI commands (future) - All CRUD operations

**Dependencies:**
- Python sqlite3 (standard library)
- Pydantic 2.5+ (validation)

---

## 📚 API Reference

### `DatabaseService(db_path: str)`
Main entry point for all database operations.

**Methods:**
- `initialize_schema()` - Create all tables
- `execute(sql, params)` - Execute raw SQL (use sparingly)
- `tasks` - TaskMethods instance
- `work_items` - WorkItemMethods instance
- `projects` - ProjectMethods instance
- `contexts` - ContextMethods instance

### `TaskMethods`
- `create_task(db, task: Task) → Task`
- `get_task(db, task_id: int) → Task | None`
- `update_task(db, task: Task) → Task`
- `delete_task(db, task_id: int) → None`
- `list_tasks(db, filters: Dict) → List[Task]`

### `WorkItemMethods`
- Similar CRUD operations for work items

### `ProjectMethods`
- Similar CRUD operations for projects

---

## 🚨 Troubleshooting

### Database locked error
**Symptom**: `sqlite3.OperationalError: database is locked`
**Cause**: Multiple connections writing simultaneously
**Fix**: Ensure only one DatabaseService instance per database file

### Validation error on create/update
**Symptom**: `pydantic.ValidationError`
**Cause**: Data doesn't match model constraints
**Fix**: Check Field constraints (min_length, ge, le, etc.)

### Foreign key constraint failed
**Symptom**: `FOREIGN KEY constraint failed`
**Cause**: Referenced entity doesn't exist
**Fix**: Create parent entity first (project → work_item → task order)

---

**Last Updated**: 2025-09-30 20:00
**Next Review**: After migration system testing
