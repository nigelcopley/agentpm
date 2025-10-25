# Contributing to APM (Agent Project Manager)

Thank you for your interest in contributing to APM! This guide will help you get started with development and ensure your contributions meet our quality standards.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Project Architecture](#project-architecture)
- [Quality Gates](#quality-gates)
- [Documentation](#documentation)
- [Getting Help](#getting-help)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and professional
- Provide constructive feedback
- Focus on what is best for the project
- Show empathy towards other contributors

---

## Getting Started

### Types of Contributions

We welcome:

- 🐛 **Bug Fixes** - Fix issues in existing code
- ✨ **Features** - Add new capabilities (discuss first via issue)
- 📚 **Documentation** - Improve guides, fix typos, add examples
- 🧪 **Tests** - Increase coverage, add edge cases
- 🔌 **Plugins** - Add new framework detection plugins
- 🤖 **Agents** - Improve agent SOPs and capabilities
- ⚡ **Performance** - Optimize slow operations
- 🎨 **UI/UX** - Improve CLI output and web interface

### Before You Start

1. **Search existing issues** - Someone may already be working on it
2. **Create an issue** - Discuss features before implementing
3. **Read this guide** - Understand our standards
4. **Review architecture docs** - Understand the system

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- SQLite 3.35+
- Text editor or IDE

### Clone and Install

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/agentpm.git
cd agentpm

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
apm --version
```

### Initialize APM in Development Project

```bash
# Initialize APM to track its own development
apm init "APM Development" .

# Verify database created
ls .agentpm/data/agentpm.db

# Check status
apm status
```

### Development Tools

```bash
# Install development tools
pip install -e ".[dev]"

# This includes:
# - pytest, pytest-cov (testing)
# - black, ruff (formatting and linting)
# - mypy (type checking)
# - flask, playwright (web testing)
```

---

## Code Standards

### Three-Layer Architecture (MANDATORY)

**All database operations MUST follow this pattern:**

```python
# Layer 1: Pydantic Models (agentpm/core/database/models/)
from agentpm.core.database.models import WorkItem, WorkItemStatus

work_item = WorkItem(
    id=None,
    project_id=1,
    name="Add OAuth2 Support",
    status=WorkItemStatus.PROPOSED,
    work_item_type=WorkItemType.FEATURE
)

# Layer 2: Adapters (agentpm/core/database/adapters/)
from agentpm.core.database.adapters import WorkItemAdapter

# Convert Pydantic model to SQLite row
row_data = WorkItemAdapter.to_row(work_item)

# Convert SQLite row back to Pydantic model
work_item = WorkItemAdapter.from_row(row)

# Layer 3: Methods (agentpm/core/database/methods/)
from agentpm.core.database.methods import work_items

# Business logic with transaction handling
created = work_items.create_work_item(db, work_item)
```

**Why**: Type safety, testability, database portability, maintainability.

**Violations of this pattern will not be accepted.**

### Type Safety

```python
# ✅ Good - Type-safe with Pydantic
def create_work_item(db: DatabaseService, work_item: WorkItem) -> WorkItem:
    """Create a new work item with validation."""
    # Implementation...

# ❌ Bad - Untyped dictionary
def create_work_item(db, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new work item."""
    # Don't do this!
```

**Rules**:
- Use Pydantic models for all data structures
- Add type hints to all functions
- No `Dict[str, Any]` in public APIs
- Run `mypy` before committing

### Code Formatting

```bash
# Format code with black
black agentpm/ tests/

# Lint with ruff
ruff check agentpm/ tests/

# Type check with mypy
mypy agentpm/
```

**Standards**:
- Black formatting (88 character line length)
- Ruff linting (enforces Python best practices)
- Type hints required (mypy strict mode)
- Docstrings for all public functions

### File Organization

```
agentpm/
├── cli/                    # CLI commands
│   ├── commands/          # Command implementations
│   │   ├── task/         # Task commands (create, start, etc.)
│   │   ├── work_item/    # Work item commands
│   │   └── agents/       # Agent commands
│   └── utils/            # CLI utilities
├── core/                  # Core business logic
│   ├── database/         # Three-layer database pattern
│   │   ├── models/      # Pydantic models (Layer 1)
│   │   ├── adapters/    # DB conversion (Layer 2)
│   │   └── methods/     # Business logic (Layer 3)
│   ├── workflow/        # Workflow state machine
│   ├── context/         # Context assembly
│   └── plugins/         # Framework detection
└── providers/            # Provider integrations
```

---

## Testing Requirements

### Coverage Requirements

**MANDATORY**: All contributions must maintain ≥90% test coverage.

```bash
# Run tests with coverage
python -m pytest tests/ --cov=agentpm --cov-report=term-missing

# Generate HTML coverage report
python -m pytest tests/ --cov=agentpm --cov-report=html
# Then open: htmlcov/index.html

# Coverage must be ≥90% on:
# - agentpm/core/database/ (database layer)
# - agentpm/core/workflow/ (workflow logic)
# - agentpm/cli/ (CLI commands)
```

### Test Structure

**Follow AAA Pattern** (Arrange, Act, Assert):

```python
def test_create_work_item():
    """Test work item creation with validation."""
    # Arrange - Set up test data
    db = get_test_database()
    work_item = WorkItem(
        project_id=1,
        name="Test Feature",
        status=WorkItemStatus.PROPOSED
    )

    # Act - Execute the operation
    created = work_items.create_work_item(db, work_item)

    # Assert - Verify results
    assert created.id is not None
    assert created.name == "Test Feature"
    assert created.status == WorkItemStatus.PROPOSED
```

### Test Organization

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── core/         # Core module tests
│   ├── cli/          # CLI tests
│   └── utils/        # Utility tests
├── integration/       # Integration tests (slower)
│   ├── database/     # Database integration
│   └── workflow/     # Workflow integration
└── e2e/              # End-to-end tests (slowest)
    └── cli/          # Full CLI workflows
```

### Running Tests

```bash
# Run all tests (2,230 tests, ~30 seconds)
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/core/database/test_work_items.py -v

# Run specific test
python -m pytest tests/core/database/test_work_items.py::test_create_work_item -v

# Run tests matching pattern
python -m pytest tests/ -k "work_item" -v

# Run with detailed output
python -m pytest tests/ -vv

# Stop on first failure
python -m pytest tests/ -x
```

---

## Commit Conventions

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **test**: Test additions or changes
- **refactor**: Code refactoring (no behavior change)
- **perf**: Performance improvements
- **chore**: Maintenance tasks (dependencies, build, etc.)
- **ci**: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(cli): Add 'apm agents generate-intelligent' command"

# Bug fix
git commit -m "fix(database): Handle empty tech_stack list in context builder"

# Documentation
git commit -m "docs: Add comprehensive CLI command reference"

# Test
git commit -m "test(workflow): Add tests for quality gate validation"

# Refactoring
git commit -m "refactor(database): Extract common adapter patterns"
```

### Scope Guidelines

Common scopes:
- `cli` - CLI commands
- `database` - Database models/adapters/methods
- `workflow` - Workflow state machine
- `context` - Context assembly
- `plugins` - Plugin system
- `agents` - Agent system
- `web` - Web interface
- `docs` - Documentation

---

## Pull Request Process

### Before Creating PR

1. **Create feature branch**
   ```bash
   git checkout -b feat/add-oauth2-support
   ```

2. **Write code following standards**
   - Three-layer pattern
   - Type hints
   - Docstrings

3. **Add/update tests**
   - ≥90% coverage required
   - AAA pattern
   - All tests passing

4. **Update documentation**
   - Update relevant guides
   - Add/update docstrings
   - Update CLI help text

5. **Run quality checks**
   ```bash
   # Format code
   black agentpm/ tests/

   # Lint
   ruff check agentpm/ tests/

   # Type check
   mypy agentpm/

   # Run tests
   python -m pytest tests/ --cov=agentpm

   # Verify coverage ≥90%
   ```

6. **Commit with conventional format**
   ```bash
   git add .
   git commit -m "feat(cli): Add OAuth2 authentication support"
   ```

### Creating the PR

1. **Push to your fork**
   ```bash
   git push origin feat/add-oauth2-support
   ```

2. **Open PR on GitHub**
   - Use descriptive title (same as commit message)
   - Fill out PR template
   - Reference related issues

3. **PR Description Should Include**:
   - **What**: What does this PR do?
   - **Why**: Why is this change needed?
   - **How**: How does it work?
   - **Testing**: How was it tested?
   - **Screenshots**: If UI changes

### PR Requirements Checklist

Your PR must:

- [ ] Follow three-layer architecture pattern
- [ ] Include comprehensive tests (≥90% coverage)
- [ ] Pass all 2,230+ existing tests
- [ ] Include type hints and docstrings
- [ ] Follow conventional commit format
- [ ] Update relevant documentation
- [ ] Pass `black`, `ruff`, `mypy` checks
- [ ] Include examples in docstrings
- [ ] Add entry to CHANGELOG.md (if user-facing)

### Review Process

1. **Automated Checks** (CI/CD):
   - All tests must pass
   - Coverage must be ≥90%
   - Linting must pass
   - Type checking must pass

2. **Code Review**:
   - Maintainer reviews code
   - May request changes
   - Discussion and iteration

3. **Approval and Merge**:
   - Once approved, maintainer merges
   - PR is squashed into single commit
   - Automatically deployed to main

---

## Project Architecture

### Understanding the System

Before contributing, understand these core patterns:

#### 1. Three-Layer Database Pattern (MANDATORY)

**Every database operation follows this pattern:**

```python
# LAYER 1: Models (agentpm/core/database/models/)
# - Pydantic models with validation
# - Type-safe business objects
# - No database logic

from pydantic import BaseModel, Field

class Task(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=1)
    status: TaskStatus
    effort_hours: float = Field(gt=0, le=4)  # Implementation ≤4h

# LAYER 2: Adapters (agentpm/core/database/adapters/)
# - Convert between Pydantic models and SQLite rows
# - Handle JSON serialization
# - No business logic

class TaskAdapter:
    @staticmethod
    def to_row(task: Task) -> Dict[str, Any]:
        """Convert Task model to SQLite row."""
        return {
            'id': task.id,
            'name': task.name,
            'status': task.status.value,
            'effort_hours': task.effort_hours
        }

    @staticmethod
    def from_row(row: sqlite3.Row) -> Task:
        """Convert SQLite row to Task model."""
        return Task(
            id=row['id'],
            name=row['name'],
            status=TaskStatus(row['status']),
            effort_hours=row['effort_hours']
        )

# LAYER 3: Methods (agentpm/core/database/methods/)
# - Business logic and validation
# - CRUD operations
# - Transaction handling

def create_task(db: DatabaseService, task: Task) -> Task:
    """Create task with validation and state machine checks."""
    # Validate
    if task.effort_hours > 4 and task.task_type == TaskType.IMPLEMENTATION:
        raise ValueError("Implementation tasks limited to 4 hours")

    # Create
    with db.transaction() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (name, status, effort_hours) VALUES (?, ?, ?)",
            (task.name, task.status.value, task.effort_hours)
        )
        task.id = cursor.lastrowid

    return task
```

**Benefits**:
- Type-safe at every layer
- Testable in isolation
- Database-agnostic (can swap SQLite for PostgreSQL)
- Clear separation of concerns

#### 2. Time-Boxing Philosophy

**All contributions must respect time-boxing:**

```python
# Task types have maximum effort limits
TaskType.IMPLEMENTATION: 4 hours   # STRICT - forces decomposition
TaskType.TESTING: 6 hours
TaskType.DESIGN: 8 hours
TaskType.DOCUMENTATION: 4 hours
TaskType.REVIEW: 2 hours
TaskType.SIMPLE: 1 hour
```

**If your task takes longer, break it into smaller tasks.**

#### 3. Quality Gates

**Contributions must pass quality gates:**

- **CI-004**: Test coverage ≥90%
- **DP-001**: Implementation tasks ≤4 hours
- **DP-002**: Three-layer pattern mandatory
- **SEC-001**: Input validation required
- **TES-001**: AAA test pattern required

See: `apm rules list` for complete rule set.

---

## Code Standards

### Python Style

```python
# ✅ Good Example
from typing import Optional
from pydantic import BaseModel, Field

class WorkItem(BaseModel):
    """Work item represents a feature, bug, or research effort.

    Work items are strategic-level entities that contain multiple tasks.
    They progress through a quality-gated state machine.

    Attributes:
        id: Unique identifier (None until persisted)
        project_id: Parent project reference
        name: Work item name (1-200 characters)
        status: Current workflow status
        work_item_type: Type (FEATURE, BUGFIX, etc.)

    Example:
        >>> work_item = WorkItem(
        ...     project_id=1,
        ...     name="Add OAuth2 Support",
        ...     status=WorkItemStatus.PROPOSED,
        ...     work_item_type=WorkItemType.FEATURE
        ... )
    """
    id: Optional[int] = None
    project_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    status: WorkItemStatus
    work_item_type: WorkItemType

# ❌ Bad Example
class WorkItem:  # No type hints, no validation
    def __init__(self, data):
        self.id = data.get('id')  # Unsafe
        self.name = data['name']  # No validation
```

### Naming Conventions

```python
# Classes: PascalCase
class WorkItemAdapter:
    pass

# Functions/methods: snake_case
def create_work_item(db, work_item):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_IMPLEMENTATION_HOURS = 4

# Private: Leading underscore
def _internal_helper():
    pass

# Pydantic models: PascalCase (no 'Model' suffix)
class WorkItem(BaseModel):  # ✅ Good
    pass

class WorkItemModel(BaseModel):  # ❌ Redundant
    pass
```

### Import Organization

```python
# Standard library imports (alphabetical)
from pathlib import Path
from typing import Dict, List, Optional
import json
import sqlite3

# Third-party imports (alphabetical)
import click
from pydantic import BaseModel, Field
from rich.console import Console

# Local imports (relative)
from ..models import WorkItem, WorkItemStatus
from ..adapters import WorkItemAdapter
from ...utils import validate_id
```

### Docstring Style

Use Google-style docstrings:

```python
def create_work_item(
    db: DatabaseService,
    work_item: WorkItem
) -> WorkItem:
    """Create a new work item with validation.

    Creates work item in database after validating against quality gates.
    Enforces type-specific requirements (e.g., FEATURE needs specific tasks).

    Args:
        db: Database service instance
        work_item: Work item to create (id should be None)

    Returns:
        Created work item with id populated

    Raises:
        ValueError: If work item validation fails
        TransactionError: If database operation fails

    Example:
        >>> from agentpm.core.database import get_database
        >>> db = get_database()
        >>> work_item = WorkItem(
        ...     project_id=1,
        ...     name="Add OAuth2",
        ...     status=WorkItemStatus.PROPOSED,
        ...     work_item_type=WorkItemType.FEATURE
        ... )
        >>> created = create_work_item(db, work_item)
        >>> created.id
        42
    """
    # Implementation...
```

---

## Testing Requirements

### Test Coverage

**MANDATORY**: ≥90% coverage on all new code.

```bash
# Check coverage
python -m pytest tests/ --cov=agentpm --cov-report=term-missing

# Must show ≥90% for changed modules
```

### Writing Tests

**Use AAA Pattern** (Arrange, Act, Assert):

```python
import pytest
from agentpm.core.database import get_test_database
from agentpm.core.database.models import Task, TaskStatus
from agentpm.core.database.methods import tasks

def test_create_task_with_time_boxing():
    """Test that implementation tasks are limited to 4 hours."""
    # Arrange
    db = get_test_database()
    task = Task(
        project_id=1,
        work_item_id=1,
        name="Implement OAuth2",
        task_type=TaskType.IMPLEMENTATION,
        effort_hours=5.0  # Exceeds 4h limit
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Implementation tasks limited to 4 hours"):
        tasks.create_task(db, task)
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def test_db():
    """Provide isolated test database."""
    db = get_test_database()
    yield db
    db.close()

@pytest.fixture
def sample_work_item():
    """Provide sample work item for testing."""
    return WorkItem(
        project_id=1,
        name="Test Feature",
        status=WorkItemStatus.PROPOSED,
        work_item_type=WorkItemType.FEATURE
    )

def test_with_fixtures(test_db, sample_work_item):
    """Test using fixtures."""
    created = work_items.create_work_item(test_db, sample_work_item)
    assert created.id is not None
```

### Test Categories

```bash
# Unit tests - Test single function/class in isolation
pytest tests/unit/ -v

# Integration tests - Test module interactions
pytest tests/integration/ -v

# E2E tests - Test complete workflows
pytest tests/e2e/ -v

# Specific module
pytest tests/core/database/ -v
pytest tests/core/workflow/ -v
pytest tests/cli/ -v
```

---

## Commit Conventions

### Work Item Tracking

**If working on a tracked work item, reference it:**

```bash
git commit -m "feat(cli): Add OAuth2 support

Implements WI-152 (Add OAuth2 Authentication).

- Added OAuth2Provider class
- Integrated with authentication flow
- Added tests for OAuth2 flow
- Updated documentation

Closes #152"
```

### Atomic Commits

**Make small, focused commits:**

```bash
# ✅ Good - Each commit is atomic
git commit -m "feat(database): Add OAuth2 provider model"
git commit -m "feat(database): Add OAuth2 provider adapter"
git commit -m "feat(database): Add OAuth2 provider methods"
git commit -m "test(database): Add OAuth2 provider tests"
git commit -m "docs: Add OAuth2 provider documentation"

# ❌ Bad - One massive commit
git commit -m "feat: Add complete OAuth2 system with everything"
```

### Commit Message Body

For complex changes, add details:

```
feat(workflow): Add automatic blocker resolution

Implements automatic blocker resolution when blocking tasks complete.
Uses SQLite trigger to update blocker status in real-time.

Changes:
- Added blocker_resolution trigger
- Updated WorkflowService.complete_task()
- Added tests for auto-resolution
- Updated workflow documentation

Technical Details:
- Trigger fires on task status UPDATE
- Checks if task is blocking other tasks
- Marks blockers as resolved automatically
- Maintains audit trail of resolution

Closes #142
```

---

## Pull Request Process

### 1. Prepare Your Branch

```bash
# Update from main
git checkout main
git pull upstream main

# Rebase your feature branch
git checkout feat/your-feature
git rebase main

# Run all checks
black agentpm/ tests/
ruff check agentpm/ tests/
mypy agentpm/
python -m pytest tests/ --cov=agentpm

# All must pass before creating PR
```

### 2. Create Pull Request

**Title**: Use conventional commit format
```
feat(cli): Add OAuth2 authentication support
```

**Description Template**:
```markdown
## Summary
[Brief description of what this PR does]

## Motivation
[Why is this change needed?]

## Changes
- Added OAuth2Provider class
- Integrated with authentication flow
- Added 25 tests with 95% coverage
- Updated CLI commands for OAuth2

## Testing
- [x] All existing tests pass (2,230 tests)
- [x] New tests added with ≥90% coverage
- [x] Manual testing completed
- [x] Edge cases covered

## Documentation
- [x] Docstrings added/updated
- [x] User guide updated
- [x] CLI help text updated
- [x] CHANGELOG.md updated

## Screenshots
[If applicable - CLI output, web UI, etc.]

## Checklist
- [x] Follows three-layer architecture
- [x] Type hints on all functions
- [x] Tests pass with ≥90% coverage
- [x] Code formatted with black
- [x] Linting passes (ruff)
- [x] Type checking passes (mypy)
- [x] Documentation updated
- [x] Conventional commit format

## Related Issues
Closes #142
Related to #135, #148
```

### 3. Code Review

**Expect feedback on:**
- Architecture compliance (three-layer pattern)
- Test coverage and quality
- Type safety
- Documentation completeness
- Code clarity and maintainability

**Respond to feedback:**
- Make requested changes
- Commit with clear messages
- Push updates to PR branch
- Request re-review when ready

### 4. Merge

Once approved:
- Maintainer will merge (usually squash merge)
- Your contribution becomes part of APM!
- Thanks for contributing!

---

## Quality Gates

### What Are Quality Gates?

APM enforces quality through database-level gates that prevent shortcuts.

**Example**: You cannot move a work item from `proposed` to `completed` without going through validation, acceptance, implementation, and review.

### Gates That Affect Contributions

**Your code contributions must pass:**

1. **CI-004: Testing Quality** (BLOCK)
   - ≥90% test coverage required
   - All tests must pass
   - No skipped tests without justification

2. **DP-001: Time-Boxing** (LIMIT)
   - Implementation tasks ≤4 hours
   - If longer, break into smaller tasks

3. **DP-002: Three-Layer Pattern** (BLOCK)
   - All database code must follow Models → Adapters → Methods
   - No direct SQL in business logic

4. **SEC-001: Input Validation** (BLOCK)
   - All user input must be validated
   - Use Pydantic models for validation
   - Check for injection, path traversal, etc.

5. **TES-001: Test Pattern** (WARN)
   - Use AAA pattern (Arrange, Act, Assert)
   - Clear test names
   - One assertion concept per test

### Checking Gate Compliance

```bash
# View all rules
apm rules list

# View blocking rules only
apm rules list --enforcement BLOCK

# Check specific rule
apm rules show CI-004
```

---

## Documentation

### When to Update Documentation

**Update docs when you:**
- Add new CLI command
- Add new feature
- Change existing behavior
- Add new plugin
- Modify database schema
- Change API

### Documentation Locations

```
docs/
├── user-guides/           # User-facing documentation
│   ├── INDEX.md          # Start here for navigation
│   ├── cli-reference/    # CLI command docs
│   ├── workflows/        # Workflow guides
│   └── advanced/         # Advanced features
├── developer-guide/       # Developer documentation
│   ├── database-schema.md # Database reference
│   └── architecture.md   # Architecture guide
└── components/           # Component-specific docs
```

### Documentation Standards

**Code Examples**:
```markdown
# ✅ Good - Tested, complete example
```bash
# Create a feature work item
apm work-item create "Add OAuth2" --type feature

# Shows output:
# ✓ Created work item #42
# Required tasks: DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION
```
\```

# ❌ Bad - Incomplete, untested
```bash
apm work-item create ...
```
\```

**Links**:
```markdown
# ✅ Good - Relative link, works in GitHub
See [Architecture Guide](docs/user-guides/developer/architecture.md)

# ❌ Bad - Absolute path, breaks in GitHub
See [Architecture Guide](/Users/nigelcopley/Projects/AgentPM/docs/...)
```

---

## Common Contribution Scenarios

### Adding a New CLI Command

1. **Create command file**
   ```bash
   # Create: agentpm/cli/commands/mycommand.py
   ```

2. **Implement command**
   ```python
   import click
   from rich.console import Console

   console = Console()

   @click.command()
   @click.option('--example', help='Example option')
   def mycommand(example: str):
       """Brief description of command."""
       console.print(f"Example: {example}")
   ```

3. **Register in main.py**
   ```python
   # agentpm/cli/main.py
   from agentpm.cli.commands.mycommand import mycommand
   cli.add_command(mycommand)
   ```

4. **Add tests**
   ```python
   # tests/cli/commands/test_mycommand.py
   def test_mycommand(cli_runner):
       result = cli_runner.invoke(['mycommand', '--example', 'test'])
       assert result.exit_code == 0
   ```

5. **Update documentation**
   - Add to `docs/user-guides/cli-reference/commands.md`
   - Update CLI command count in README.md

### Adding a New Plugin

1. **Create plugin file**
   ```bash
   # Create: agentpm/core/plugins/domains/frameworks/myframework.py
   ```

2. **Implement plugin**
   ```python
   from agentpm.core.plugins.base import Plugin, DetectionResult

   class MyFrameworkPlugin(Plugin):
       name = "myframework"

       def detect(self, project_path: Path) -> DetectionResult:
           # Detection logic
           pass
   ```

3. **Register plugin**
   ```python
   # agentpm/core/plugins/registry.py
   from .domains.frameworks.myframework import MyFrameworkPlugin

   PLUGINS = {
       'myframework': MyFrameworkPlugin,
       # ...
   }
   ```

4. **Add tests**
   ```python
   # tests/core/plugins/test_myframework.py
   def test_myframework_detection():
       # Test detection logic
       pass
   ```

5. **Update documentation**
   - Add to plugin list in README.md
   - Document in `docs/user-guides/advanced/detection-packs.md`

### Fixing a Bug

1. **Reproduce the bug**
   - Write failing test
   - Document reproduction steps

2. **Fix the bug**
   - Minimal change to fix issue
   - Follow existing patterns

3. **Verify fix**
   - Test passes
   - No regressions
   - Coverage maintained

4. **Document**
   - Add test documenting the bug
   - Update relevant docs if behavior changed
   - Add entry to CHANGELOG.md

---

## Development Workflow

### Typical Development Flow

```bash
# 1. Create feature branch
git checkout -b feat/add-oauth2

# 2. Write failing test (TDD)
# tests/core/auth/test_oauth2.py
python -m pytest tests/core/auth/test_oauth2.py -v
# Should fail - feature not implemented yet

# 3. Implement feature (three-layer pattern)
# - Create model in models/
# - Create adapter in adapters/
# - Create methods in methods/

# 4. Run test - should pass now
python -m pytest tests/core/auth/test_oauth2.py -v

# 5. Check coverage
python -m pytest tests/core/auth/ --cov=agentpm.core.auth --cov-report=term-missing

# 6. Format and lint
black agentpm/ tests/
ruff check agentpm/ tests/
mypy agentpm/

# 7. Run full test suite
python -m pytest tests/ -v

# 8. Update documentation
# - Add docstrings
# - Update user guides
# - Update CLI help text

# 9. Commit
git add .
git commit -m "feat(auth): Add OAuth2 authentication support"

# 10. Push and create PR
git push origin feat/add-oauth2
# Then create PR on GitHub
```

---

## Getting Help

### Resources

- **Documentation**: [docs/user-guides/INDEX.md](docs/user-guides/INDEX.md)
- **Architecture Guide**: [docs/user-guides/developer/architecture.md](docs/user-guides/developer/architecture.md)
- **Database Schema**: [docs/developer-guide/database-schema.md](docs/developer-guide/database-schema.md)
- **CLI Reference**: [docs/user-guides/cli-reference/commands.md](docs/user-guides/cli-reference/commands.md)

### Communication

- **GitHub Issues**: [Report bugs, request features](https://github.com/nigelcopley/agentpm/issues)
- **GitHub Discussions**: [Ask questions, share ideas](https://github.com/nigelcopley/agentpm/discussions)
- **Pull Requests**: [Code review and collaboration](https://github.com/nigelcopley/agentpm/pulls)

### Finding Good First Issues

Look for issues labeled:
- `good first issue` - Great for newcomers
- `help wanted` - Community contributions welcome
- `documentation` - Documentation improvements
- `testing` - Test coverage improvements

---

## Recognition

Contributors are recognized in:
- CHANGELOG.md (for significant contributions)
- GitHub Contributors page
- Release notes

Thank you for contributing to APM! Your efforts help make AI-assisted development more reliable and professional.

---

**Questions?** Open an issue or discussion on GitHub.

**Ready to contribute?** Fork, code, test, submit PR!

---

**APM: Built by developers, for AI agents, with quality gates.**
