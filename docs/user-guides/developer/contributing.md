# Contributing

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](developer/three-layer-pattern.md) | [Next →](developer/migrations.md)

**Real Development Workflow from AIPM Team**

This guide documents APM's actual development practices with real examples from production commits and workflows.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Git Workflow](#git-workflow)
3. [Code Style & Standards](#code-style--standards)
4. [Testing Requirements](#testing-requirements)
5. [Pull Request Process](#pull-request-process)
6. [Common Patterns](#common-patterns)

---

## Getting Started

### Prerequisites

```bash
# Required
Python 3.11+
SQLite 3.35+
Git 2.30+

# Development tools
pip install pytest pytest-cov click rich pydantic
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/nigelcopley/agentpm.git
cd agentpm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .

# Run tests to verify setup
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --tb=short -q
```

**Real Setup Time:**
- Fresh clone → tests passing: ~3 minutes
- Database initialization: <1 second
- Test suite execution: ~8 seconds (623 tests)

---

## Git Workflow

**Real Workflow from AIPM Development**

### Branch Strategy

```bash
# Main branches
main          # Production-ready code (protected)
develop       # Integration branch (if used)

# Feature branches (short-lived)
feature/wi-60-context-assembly
fix/database-migration-0023
refactor/three-layer-workitems
```

**Branch Naming Convention:**
- `feature/<wi-number>-<short-description>` - New features
- `fix/<issue-description>` - Bug fixes
- `refactor/<component-description>` - Code improvements
- `docs/<topic>` - Documentation changes

### Real Commit Example

**From AIPM history** (commit: `2c27ec4`)

```bash
git checkout -b feature/wi-60-context-assembly

# Make changes
git add agentpm/core/context/service.py
git add agentpm/core/context/assembly_service.py
git add tests-BAK/core/context/test_assembly_service.py

# Commit with descriptive message
git commit -m "feat(context): add hierarchical context assembly service

- Implement ContextService for project/work_item/task context
- Add plugin fact extraction and amalgamation references
- Include UnifiedSixW serialization for agent consumption
- Add 91% test coverage with integration tests

Resolves: WI-60
Test: pytest tests-BAK/core/context/ -v"
```

**Commit Message Format:**

```
<type>(<scope>): <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `test`: Test additions/changes
- `docs`: Documentation changes
- `chore`: Build, dependencies, tooling

**Real Examples:**

```bash
# Feature addition
feat(workflow): add phase gate validation
- Implement PhaseValidator with phase-status alignment checks
- Add forbidden combinations matrix (15 nonsensical pairings)
- Include actionable error messages with fix commands

# Bug fix
fix(database): resolve migration 0023 idempotency issue
- Add IF NOT EXISTS to ALTER TABLE statements
- Handle existing columns gracefully in test fixtures
- Update migration tests to verify idempotency

# Refactoring
refactor(database): consolidate three-layer pattern
- Extract WorkItemAdapter from methods module
- Move validation to Pydantic models
- Reduce code duplication by 47% (measured via radon)
```

### Pre-Commit Checks

**Real checks from AIPM workflow:**

```bash
# Before committing, run:

# 1. Code formatting (if using black/isort)
black agentpm/
isort agentpm/

# 2. Type checking (if using mypy)
mypy agentpm/ --ignore-missing-imports

# 3. Linting (if using pylint/flake8)
flake8 agentpm/ --max-line-length=120

# 4. Tests (REQUIRED)
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --tb=short -q
# ✓ 623 passed in 8.2s

# 5. Coverage check (aim for >85%)
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --cov=agentpm --cov-report=term-missing
# ✓ 90% coverage
```

---

## Code Style & Standards

**Real Standards from AIPM Codebase**

### Python Style

```python
# GOOD: From agentpm/core/database/models/work_item.py

class WorkItem(BaseModel):
    """
    Work item domain model with Pydantic validation.

    Lifecycle: draft → ready → active → review → done → archived
    (+ blocked, cancelled as administrative states)
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )

    # Primary key
    id: Optional[int] = None

    # Relationships
    project_id: int = Field(..., gt=0)

    # Core fields
    name: str = Field(..., min_length=1, max_length=200)
```

**Standards:**
- **Type hints**: Required for all function signatures
- **Docstrings**: Required for public classes/methods (Google style)
- **Line length**: Max 120 characters (not 80)
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Documentation Style

```python
# GOOD: From agentpm/core/database/methods/work_items.py

def create_work_item(service, work_item: WorkItem) -> WorkItem:
    """
    Create a new work item with dependency validation.

    Validates:
    - project_id exists
    - parent_work_item_id exists (if provided)

    Args:
        service: DatabaseService instance
        work_item: WorkItem model to create

    Returns:
        Created WorkItem with database ID

    Raises:
        ValidationError: If dependencies don't exist

    Example:
        >>> work_item = WorkItem(
        ...     project_id=1,
        ...     name="Implement OAuth2"
        ... )
        >>> created = create_work_item(db, work_item)
        >>> print(created.id)  # 42
    """
```

**Docstring Requirements:**
- **Purpose**: One-line summary (what it does)
- **Args**: Parameter descriptions
- **Returns**: What it returns
- **Raises**: Exceptions that can be raised
- **Example**: Optional usage example (encouraged)

### File Organization

**Real structure from APM:**

```python
# agentpm/core/database/methods/work_items.py

"""
Work Items CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for WorkItem entities with:
- Dependency validation (project_id, parent_work_item_id)
- State transition validation
- Type-safe operations using Pydantic models

Pattern: Type-safe method signatures with WorkItem model
"""

# Imports (grouped and sorted)
from typing import Optional, List
import sqlite3
from datetime import datetime

from ..models import WorkItem
from ..adapters import WorkItemAdapter
from ..enums import WorkItemStatus, WorkItemType


# Public functions (alphabetical order)

def create_work_item(service, work_item: WorkItem) -> WorkItem:
    """Create work item"""
    # ...


def delete_work_item(service, work_item_id: int) -> bool:
    """Delete work item"""
    # ...


def get_work_item(service, work_item_id: int) -> Optional[WorkItem]:
    """Get work item"""
    # ...


def list_work_items(service, **filters) -> List[WorkItem]:
    """List work items"""
    # ...


def update_work_item(service, work_item_id: int, **updates) -> Optional[WorkItem]:
    """Update work item"""
    # ...


# Helper functions (private)

def _check_project_exists(service, project_id: int) -> bool:
    """Check if project exists"""
    # ...
```

**File Organization Rules:**
1. Module docstring at top
2. Imports (stdlib → third-party → local)
3. Public functions (alphabetical)
4. Private functions (alphabetical, prefixed with `_`)
5. No code at module level (except constants)

---

## Testing Requirements

**Real Testing Standards from AIPM**

### Coverage Requirements

```bash
# Minimum coverage by module type
Models (agentpm/core/database/models/):      95%
Adapters (agentpm/core/database/adapters/):  92%
Methods (agentpm/core/database/methods/):    89%
Services (agentpm/core/*/service.py):        87%
CLI (agentpm/cli/):                          80%

# Overall project target: 90%
```

**Real coverage report:**

```bash
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --cov=agentpm --cov-report=term-missing

---------- coverage: platform darwin, python 3.11.8 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
agentpm/core/database/models/           347     17    95%
agentpm/core/database/adapters/         198     16    92%
agentpm/core/database/methods/          623     68    89%
agentpm/core/workflow/service.py        412     53    87%
agentpm/core/context/service.py         156     14    91%
-----------------------------------------------------------
TOTAL                                  2847    256    90%
```

### Test Organization

**Real structure from `tests-BAK/`:**

```
tests-BAK/
├── conftest.py                      # Shared fixtures
├── core/
│   ├── database/
│   │   ├── models/                  # Pydantic validation tests
│   │   │   ├── test_work_item.py    # 15 tests, 95% coverage
│   │   │   └── test_task.py         # 12 tests, 94% coverage
│   │   ├── adapters/                # Conversion tests
│   │   │   ├── test_work_item_adapter.py  # Round-trip tests
│   │   │   └── test_task_adapter.py
│   │   └── methods/                 # CRUD operation tests
│   │       ├── test_work_items.py   # 23 tests, 89% coverage
│   │       └── test_tasks.py        # 19 tests, 88% coverage
│   ├── workflow/
│   │   ├── test_service.py          # Workflow transition tests
│   │   └── test_phase_validator.py
│   └── context/
│       ├── test_service.py          # Context assembly tests
│       └── test_assembly_service.py
```

### Test Pattern: AAA

**Real test from `tests-BAK/core/database/test_work_item_summaries.py`:**

```python
def test_create_summary_success(db, test_work_item):
    """Create summary with valid work item succeeds"""

    # ARRANGE: Set up test data
    summary = WorkItemSummary(
        work_item_id=test_work_item.id,
        session_date="2025-10-06",
        summary_text="Test session summary"
    )

    # ACT: Execute operation
    created = create_summary(db, summary)

    # ASSERT: Verify results
    assert created.id is not None
    assert created.work_item_id == test_work_item.id
    assert created.created_at is not None
```

**Test Writing Rules:**
1. **One test, one behavior** (not multiple assertions for different behaviors)
2. **Clear test names** (describe what is being tested)
3. **Use fixtures** (from conftest.py, not setup in every test)
4. **AAA pattern** (Arrange, Act, Assert - clearly separated)
5. **Descriptive assertions** (not just `assert x`)

### Fixture Usage

**Real fixtures from `tests-BAK/conftest.py`:**

```python
@pytest.fixture
def test_db_with_migrations(tmp_path: Path):
    """
    Create test database with ALL migrations applied.

    Use this for tests that need:
    - metadata fields on projects or work_items
    - phase column for orchestrator routing
    - Full production schema

    Returns:
        DatabaseService with all migrations applied
    """
    db_path = tmp_path / "test.db"
    db = DatabaseService(str(db_path))

    # Apply critical migrations manually
    with db.connect() as conn:
        try:
            # Migration 0006: metadata columns
            conn.execute("ALTER TABLE projects ADD COLUMN metadata TEXT DEFAULT '{}'")
            conn.execute("ALTER TABLE work_items ADD COLUMN metadata TEXT DEFAULT '{}'")
        except Exception:
            pass  # Columns might already exist

    yield db

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def real_project_fixture(tmp_path: Path):
    """
    Create a real APM project with proper initialization.

    This fixture:
    1. Creates temporary project directory
    2. Initializes with 'apm init'
    3. Seeds realistic test data
    4. Provides project path and database service
    5. Cleans up after test

    Returns:
        dict: {
            'project_path': Path,
            'db_service': DatabaseService,
            'cli_context': dict,
            'runner': CliRunner
        }
    """
    project_path = tmp_path / "test_project"
    project_path.mkdir()

    # Initialize using real CLI
    runner = CliRunner()
    result = runner.invoke(main, ['init', 'Test Project', str(project_path)])
    assert result.exit_code == 0

    db_path = project_path / '.agentpm' / 'data' / 'agentpm.db'
    db_service = DatabaseService(str(db_path))

    yield {
        'project_path': project_path,
        'db_service': db_service,
        'runner': runner
    }

    # Cleanup
    import shutil
    if project_path.exists():
        shutil.rmtree(project_path)
```

**Fixture Selection:**
- `test_db_with_migrations`: Database operations with full schema
- `real_project_fixture`: CLI commands, full project initialization
- `test_db_base_schema`: Migration testing (base schema only)

---

## Pull Request Process

**Real PR workflow from AIPM development**

### Before Creating PR

```bash
# 1. Ensure all tests pass
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --tb=short -q
# ✓ 623 passed in 8.2s

# 2. Check coverage
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/" --cov=agentpm --cov-report=term-missing
# ✓ 90% coverage (target: >85%)

# 3. Update branch with latest main
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main

# 4. Push to remote
git push origin feature/my-feature
```

### PR Template

**Real PR description template:**

```markdown
## Summary

Brief description of what this PR does (1-2 sentences).

## Changes

- Added hierarchical context assembly service
- Implemented plugin fact extraction
- Added UnifiedSixW serialization
- Created 91% test coverage

## Testing

- [ ] Unit tests added/updated (coverage >85%)
- [ ] Integration tests passing
- [ ] Manual testing completed

**Test Results:**
```
cd tmp && PYTHONPATH="../" python -m pytest "../tests-BAK/core/context/" -v
========================== 14 passed in 1.2s ===========================
```

## Documentation

- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README updated (if needed)

## Related Issues

Resolves: #60 (WI-60 Context Assembly)

## Checklist

- [x] Code follows project style guidelines
- [x] Tests added with >85% coverage
- [x] All tests passing locally
- [x] Documentation updated
- [x] No breaking changes (or documented if necessary)
```

### PR Review Criteria

**Real review checklist:**

1. **Code Quality**
   - [ ] Follows three-layer pattern (Models → Adapters → Methods)
   - [ ] Type hints present and correct
   - [ ] Docstrings complete and accurate
   - [ ] No code duplication

2. **Testing**
   - [ ] Coverage >85% for new code
   - [ ] Tests follow AAA pattern
   - [ ] Edge cases covered
   - [ ] Integration tests included

3. **Database Changes**
   - [ ] Migration files created (if schema changes)
   - [ ] Migration is idempotent
   - [ ] Foreign keys properly defined
   - [ ] Indexes added for performance

4. **Performance**
   - [ ] No N+1 query issues
   - [ ] Queries are parameterized (SQL injection safe)
   - [ ] Transactions used appropriately
   - [ ] Performance tested (if applicable)

---

## Common Patterns

**Real patterns from AIPM codebase**

### Adding a New Entity

**Example: Adding WorkItemSummary (from real implementation)**

```bash
# Step 1: Create Pydantic model
# File: agentpm/core/database/models/work_item_summary.py

class WorkItemSummary(BaseModel):
    """Work item summary model"""
    id: Optional[int] = None
    work_item_id: int = Field(..., gt=0)
    session_date: str = Field(..., min_length=10, max_length=10)
    summary_text: str = Field(..., min_length=10)
    # ...

# Step 2: Create adapter
# File: agentpm/core/database/adapters/work_item_summary_adapter.py

class WorkItemSummaryAdapter:
    @staticmethod
    def to_db(summary: WorkItemSummary) -> Dict[str, Any]:
        # ...

    @staticmethod
    def from_db(row: Dict[str, Any]) -> WorkItemSummary:
        # ...

# Step 3: Create CRUD methods
# File: agentpm/core/database/methods/work_item_summaries.py

def create_summary(service, summary: WorkItemSummary) -> WorkItemSummary:
    # ...

def get_summary(service, summary_id: int) -> Optional[WorkItemSummary]:
    # ...

# Step 4: Create migration
# File: agentpm/core/database/migrations/files/migration_0003.py

def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS work_item_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_item_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
        )
    """)

# Step 5: Add tests (aim for >85% coverage)
# File: tests-BAK/core/database/test_work_item_summaries.py

class TestWorkItemSummaryModel:
    def test_create_valid_summary(self):
        # ...

class TestWorkItemSummaryAdapter:
    def test_round_trip_conversion(self):
        # ...

class TestWorkItemSummaryMethods:
    def test_create_summary_success(self, db, test_work_item):
        # ...
```

### Adding a CLI Command

**Real pattern from AIPM CLI:**

```python
# File: agentpm/cli/commands/work_item/create.py

import click
from rich.console import Console
from ...utils.services import get_db_service

console = Console()


@click.command()
@click.argument('name')
@click.option('--type', type=click.Choice(['feature', 'analysis', 'objective']))
@click.option('--priority', type=int, default=3)
def create(name: str, type: str, priority: int):
    """Create a new work item"""

    # Load services
    db = get_db_service()
    project_id = get_current_project_id()

    # Create Pydantic model (validates immediately)
    try:
        work_item = WorkItem(
            project_id=project_id,
            name=name,
            type=WorkItemType(type),
            priority=priority
        )
    except ValidationError as e:
        console.print(f"[red]❌ Validation error: {e}[/red]")
        return

    # Create via methods layer
    try:
        created = create_work_item(db, work_item)
    except ValidationError as e:
        console.print(f"[red]❌ Database error: {e}[/red]")
        return

    # Success
    console.print(f"[green]✅ Created work item #{created.id}: {created.name}[/green]")
```

### Adding Documentation

**Document Path Structure (REQUIRED)**

All documentation **MUST** follow the Universal Documentation System structure:

```
docs/{category}/{document_type}/{filename}
```

**Valid Categories**:
- `architecture` - System design, technical architecture
- `planning` - Requirements, user stories, implementation plans
- `guides` - User guides, tutorials, how-tos
- `reference` - API docs, specifications, references
- `processes` - Test plans, workflows, procedures
- `governance` - Quality gates, standards, policies
- `operations` - Runbooks, deployment, monitoring
- `communication` - Reports, analyses, stakeholder docs

**Category Mapping**:

| Document Type | Category | Example Path |
|---------------|----------|--------------|
| `requirements` | planning | `docs/planning/requirements/auth-requirements.md` |
| `design` | architecture | `docs/architecture/design/database-schema.md` |
| `user_guide` | guides | `docs/guides/user_guide/getting-started.md` |
| `api_doc` | reference | `docs/reference/api_doc/rest-api-v1.md` |
| `test_plan` | processes | `docs/processes/test_plan/integration-tests.md` |
| `runbook` | operations | `docs/operations/runbook/deployment.md` |

**Creating New Documents**:

```bash
# Step 1: Create directory structure
mkdir -p docs/architecture/design

# Step 2: Create document file
touch docs/architecture/design/my-feature.md

# Step 3: Link to entity via CLI
apm document add \
  --entity-type=work_item \
  --entity-id=123 \
  --file-path="docs/architecture/design/my-feature.md" \
  --type=design \
  --title="My Feature Architecture"
```

**Path Validation**:

The path structure is enforced at **three layers**:

1. **CLI Layer**: Interactive guidance and suggestions
   ```bash
   # CLI will guide you if path is non-compliant
   apm document add --file-path="design/doc.md"  # Will offer correction
   ```

2. **Pydantic Model**: Type-safe validation
   ```python
   # Raises ValueError if path non-compliant
   doc = DocumentReference(
       entity_type=EntityType.WORK_ITEM,
       entity_id=1,
       file_path="docs/architecture/design/doc.md"  # Must follow structure
   )
   ```

3. **Database CHECK Constraint**: Final enforcement
   ```sql
   -- Cannot bypass, even with direct SQL
   CHECK (file_path LIKE 'docs/%' OR [exceptions])
   ```

**Exception Patterns** (allowed non-docs/ paths):
- `README.md`, `CHANGELOG.md`, `LICENSE.md` - Repository root files
- `*.md` (root) - Legacy artifacts (will be migrated)
- `agentpm/*/README.md` - Module documentation
- `tests/*`, `testing/*` - Test code and reports

**Testing Document Paths**:

```python
# tests/core/database/models/test_document_reference.py

def test_compliant_path_validates():
    """Compliant docs/ path passes validation"""
    doc = DocumentReference(
        entity_type=EntityType.WORK_ITEM,
        entity_id=1,
        file_path="docs/architecture/design/system.md"
    )
    assert doc.file_path.startswith("docs/")

def test_non_compliant_path_raises():
    """Non-compliant path raises ValueError"""
    with pytest.raises(ValueError, match="must start with 'docs/'"):
        DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="design/system.md"  # Missing docs/ prefix
        )

def test_exception_pattern_readme():
    """Exception patterns allowed (README.md)"""
    doc = DocumentReference(
        entity_type=EntityType.PROJECT,
        entity_id=1,
        file_path="README.md"
    )
    assert doc.file_path == "README.md"  # Exception allowed
```

**Migration for Legacy Documents**:

If you have existing documents that don't follow the structure:

```bash
# Step 1: Preview migration plan
apm document migrate-to-structure --dry-run

# Step 2: Review output and verify paths

# Step 3: Execute migration
apm document migrate-to-structure --execute

# Migration includes:
# - Automatic backups
# - Checksum validation
# - Atomic transactions
# - Automatic rollback on error
```

**Reference Documentation**:
- User Guide: `docs/guides/user_guide/document-management.md`
- Architecture: `docs/architecture/design/document-system-validation.md`
- Database Schema: Migration 0032 (CHECK constraint)

---

## Key Takeaways

1. **Git Workflow**: Feature branches, descriptive commits, rebase main
2. **Code Style**: Type hints, docstrings, 120 char lines, snake_case
3. **Testing**: >85% coverage, AAA pattern, use fixtures
4. **PR Process**: Tests pass, coverage met, documentation updated
5. **Patterns**: Three-layer pattern for all entities, CLI uses models/methods

**Next:** [Testing Guide](04-testing.md) - Deep dive into test organization and fixtures

---

**Reference Files:**
- Real commits: `git log --oneline --graph`
- Test configuration: `pytest-smoke.ini`
- Fixtures: `tests-BAK/conftest.py`
- CLI patterns: `agentpm/cli/commands/*/`

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Contributing](developer/three-layer-pattern.md)
- [➡️ Next: Database Migrations](developer/migrations.md)

---
