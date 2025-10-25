# Cursor Integration Reference Documentation

**Version**: 1.0.0
**Last Updated**: 2025-10-20
**Related Work Item**: WI-118 "Full Cursor Integration"

---

## Quick Reference

**Active Rules**: 5 files
**Archived Rules**: 22 files
**Space Savings**: 65% reduction
**Load Time**: < 200ms for all rules

**File Locations**:
- Active: `.cursor/rules/*.mdc`
- Archive: `.cursor/rules/_archive/*.mdc`
- Design: `docs/architecture/cursor-integration-consolidation-design.md`

---

## Complete Rule Specifications

### 1. aipm-master.mdc

**Always Active Master Orchestrator**

**Configuration**:
```yaml
---
alwaysApply: true
description: APM (Agent Project Manager) master orchestrator - workflow, commands, quality gates
priority: 100
---
```

**Purpose**: Single source of truth for:
- Workflow orchestration and phase progression
- Database-first command patterns
- Quality gate enforcement
- Agent delegation strategies
- Error handling and escalation

**File Size**: ~13KB

**Core Content Sections**:

1. **Database-First Architecture** (CRITICAL)
   - All state from database via `apm` commands
   - No file-based state reading
   - `_RULES/` directory is documentation only
   - Runtime queries only

2. **Workflow Phases** (D1 → P1 → I1 → R1 → O1 → E1)
   ```
   D1_DISCOVERY     → Requirements gathering, 6W analysis
   P1_PLAN          → Task decomposition, estimation
   I1_IMPLEMENTATION → Build and test
   R1_REVIEW        → Quality validation
   O1_OPERATIONS    → Deploy and monitor
   E1_EVOLUTION     → Continuous improvement
   ```

3. **Command Usage Matrix**
   - Phase-specific commands
   - Common operations across phases
   - Error recovery patterns

4. **Quality Gates**
   - CI-001: Agent validation
   - CI-002: Context quality (≥ 0.70 confidence)
   - CI-004: Testing coverage (≥ 90%)
   - CI-006: Documentation standards

5. **Agent Delegation**
   - When to delegate
   - Agent selection patterns
   - Escalation protocols

6. **Error Patterns & Recovery**
   - Common error signatures
   - Diagnostic commands
   - Recovery steps

**When to Reference**:
- Every session (always active)
- Workflow phase transitions
- Gate validation
- Command guidance
- Error recovery

---

### 2. cli-development.mdc

**Auto-Attach for CLI Code**

**Configuration**:
```yaml
---
globs:
  - "agentpm/cli/**/*.py"
  - "agentpm/commands/**/*.py"
description: CLI development patterns with Click and Rich
priority: 85
---
```

**Purpose**: CLI-specific patterns and standards
- Click command structure
- Rich output formatting
- LazyGroup for fast startup
- Input validation
- Performance requirements

**File Size**: ~12KB

**Core Content Sections**:

1. **Click + Rich Architecture**
   ```python
   import click
   from rich.console import Console

   @click.command()
   def command_name():
       """Command description."""
       console = Console()
       # Use Rich for all output
   ```

2. **Command Patterns**
   - LazyGroup for startup < 100ms
   - Consistent option naming (`--option-name`)
   - Comprehensive help text
   - Type hints with click.Path, click.IntRange

3. **Input Validation**
   - Validate at boundaries (Click layer)
   - Clear error messages with guidance
   - Type safety with Pydantic models

4. **Output Formatting**
   - Rich tables for lists
   - Rich panels for status
   - Color coding:
     - Green (✓): Success, completed
     - Yellow (⚠): Warning, in progress
     - Red (✗): Error, blocked

5. **Performance Requirements**
   - Startup: < 100ms
   - Command execution: < 2s
   - Context generation: < 5s

**Trigger Examples**:
- `agentpm/cli/status.py`
- `agentpm/cli/task_commands.py`
- `agentpm/commands/work_item_commands.py`

**Common Questions This Answers**:
- "How do I structure a Click command?"
- "How do I format output with Rich?"
- "What performance targets should I meet?"
- "How do I validate CLI input?"

---

### 3. database-patterns.mdc

**Auto-Attach for Database Layer**

**Configuration**:
```yaml
---
globs:
  - "**/adapters/**/*.py"
  - "**/methods/**/*.py"
  - "**/database/**/*.py"
  - "**/models/**/*.py"
description: Database three-layer architecture patterns
priority: 90
---
```

**Purpose**: Database patterns and architecture
- Three-layer pattern (Models → Adapters → Methods)
- Pydantic model validation
- ServiceResult pattern
- SQLite best practices
- Transaction handling

**File Size**: ~14KB

**Core Content Sections**:

1. **Three-Layer Pattern (MANDATORY)**

   **Layer 1: Models (Pydantic)**
   ```python
   from pydantic import BaseModel

   class WorkItem(BaseModel):
       id: int
       name: str
       status: WorkItemStatus
       # Type-safe data models
   ```

   **Layer 2: Adapters (DB Conversion)**
   ```python
   class WorkItemAdapter:
       @classmethod
       def from_row(cls, row: sqlite3.Row) -> WorkItem:
           """Convert DB row to Pydantic model"""
           return WorkItem(
               id=row["id"],
               name=row["name"],
               status=WorkItemStatus(row["status"])
           )

       @staticmethod
       def to_dict(model: WorkItem) -> dict:
           """Convert Pydantic model to DB dict"""
           return {
               "id": model.id,
               "name": model.name,
               "status": model.status.value
           }
   ```

   **Layer 3: Methods (Business Logic)**
   ```python
   class WorkItemMethods:
       def create(self, model: WorkItem) -> ServiceResult[WorkItem]:
           """Business logic with validation"""
           # Validate
           # Transform
           # Persist
           # Return ServiceResult
   ```

2. **ServiceResult Pattern**
   ```python
   from typing import Generic, TypeVar, Optional

   T = TypeVar('T')

   class ServiceResult(Generic[T]):
       success: bool
       data: Optional[T]
       error: Optional[str]
   ```

3. **Schema Patterns**
   - snake_case naming
   - JSON columns for complex data
   - ISO format timestamps
   - Indexes for performance

4. **Migration Patterns**
   - Version-based migrations
   - Backward compatibility
   - Data migration scripts

5. **Testing Database Code**
   - Temporary databases for tests
   - Fixture patterns
   - Transaction rollback

**Trigger Examples**:
- `agentpm/database/adapters/work_item_adapter.py`
- `agentpm/database/methods/task_methods.py`
- `agentpm/services/adapters/context_adapter.py`

**Common Questions This Answers**:
- "How do I structure database code?"
- "How do I convert between DB rows and models?"
- "What's the ServiceResult pattern?"
- "How do I test database code?"

---

### 4. testing-standards.mdc

**Auto-Attach for Test Files**

**Configuration**:
```yaml
---
globs:
  - "tests/**/*.py"
  - "**/*_test.py"
  - "**/test_*.py"
description: Testing patterns and coverage requirements
priority: 85
---
```

**Purpose**: Test patterns and quality standards
- AAA pattern (Arrange-Act-Assert)
- Coverage requirements
- Pytest fixtures
- Test organization
- Descriptive naming

**File Size**: ~11KB

**Core Content Sections**:

1. **Test Organization**
   ```python
   class TestWorkItemService:
       """Class-based test suite"""

       def test_create_work_item_success(self):
           """test_<operation>_<condition> naming"""
           # Arrange: Setup test data
           work_item_data = {"name": "Test WI"}

           # Act: Execute operation
           result = service.create_work_item(work_item_data)

           # Assert: Verify outcome
           assert result.success
           assert result.data.name == "Test WI"
   ```

2. **Coverage Requirements**
   | Code Type | Minimum Coverage |
   |-----------|-----------------|
   | Overall | ≥ 90% |
   | Critical paths | 100% |
   | User-facing code | ≥ 95% |
   | Data layer | ≥ 90% |
   | Security code | 100% |
   | Utilities | ≥ 85% |

3. **Fixture Patterns**
   ```python
   @pytest.fixture
   def temp_db(tmp_path):
       """Temporary database for tests"""
       db_path = tmp_path / "test.db"
       # Setup database
       yield db_path
       # Cleanup automatically
   ```

4. **Test Categories**
   - **Unit tests**: Individual methods, no external dependencies
   - **Integration tests**: Component interaction, database operations
   - **E2E tests**: Full workflow validation

5. **Quality Checks**
   ```bash
   # Run tests with coverage
   pytest tests/ -v --cov=agentpm --cov-report=html

   # Check coverage threshold
   pytest tests/ --cov=agentpm --cov-fail-under=90
   ```

**Trigger Examples**:
- `tests/test_workflow.py`
- `tests/database/test_adapters.py`
- `tests/cli/test_commands.py`

**Common Questions This Answers**:
- "How should I structure tests?"
- "What coverage is required?"
- "How do I use pytest fixtures?"
- "What naming convention for tests?"

---

### 5. documentation-quality.mdc

**Auto-Attach for Documentation Files**

**Configuration**:
```yaml
---
globs:
  - "docs/**/*.md"
  - "*.md"
description: Documentation quality and structure standards
priority: 75
---
```

**Purpose**: Documentation standards and quality gates
- Document path structure
- Content standards
- Style guidelines
- Quality requirements
- Metadata requirements

**File Size**: ~11KB

**Core Content Sections**:

1. **Document Structure (REQUIRED)**

   **Path Pattern**:
   ```
   docs/{category}/{document_type}/{filename}
   ```

   **Categories**:
   - `architecture`: System design, ADRs
   - `planning`: Requirements, task breakdown
   - `guides`: User guides, tutorials
   - `reference`: API docs, command reference
   - `processes`: Workflows, procedures
   - `governance`: Policies, standards
   - `operations`: Runbooks, deployment
   - `communication`: Status reports, retrospectives
   - `testing`: Test plans, results

   **Examples**:
   ```
   docs/planning/requirements/wi-119-requirements.md
   docs/architecture/design/database-schema-design.md
   docs/guides/user_guide/getting-started.md
   docs/operations/runbook/deployment-checklist.md
   ```

2. **Content Standards**
   - Clear headings (H1, H2, H3 hierarchy)
   - Code examples with syntax highlighting
   - Tables for comparisons
   - Decision rationale included
   - Links to related documents

   **Template Structure**:
   ```markdown
   # Document Title

   **Version**: 1.0.0
   **Last Updated**: YYYY-MM-DD

   ## Quick Start
   [Immediate actions]

   ## Overview
   [What and why]

   ## Detailed Content
   [Main sections]

   ## References
   [Related documents]
   ```

3. **Style Guide**
   - Active voice preferred
   - Present tense for current state
   - Avoid jargon without explanation
   - Include examples for complex concepts
   - Use "you" to address reader

4. **Quality Gates**
   - Description ≥ 50 chars
   - No placeholder text (TODO, TBD, FIXME)
   - Business context required
   - Links must be valid
   - Code examples must be working

5. **Metadata Requirements (YAML Frontmatter)**
   ```yaml
   ---
   title: Document Title
   version: 1.0.0
   date: 2025-10-20
   author: Team Name
   status: Published
   ---
   ```

**Trigger Examples**:
- `docs/architecture/design.md`
- `docs/planning/requirements/wi-119-requirements.md`
- `docs/guides/user_guide/getting-started.md`
- `README.md`

**Common Questions This Answers**:
- "Where should this document go?"
- "How should I structure documentation?"
- "What style should I use?"
- "What quality gates must I meet?"

---

## Auto-Attach Pattern Reference

### Glob Pattern Syntax

**Basic Patterns**:
```yaml
"*.py"              # Any .py file in current directory
"**/*.py"           # Any .py file in any subdirectory
"tests/*.py"        # .py files directly in tests/
"tests/**/*.py"     # .py files anywhere under tests/
```

**Negation Patterns**:
```yaml
"**/*.py"           # All Python files
"!tests/**/*.py"    # Except test files
```

**Multiple Extensions**:
```yaml
"**/*.{py,pyi}"     # .py or .pyi files
"**/*.{md,rst}"     # .md or .rst files
```

### Complete Pattern Matrix

| Pattern | Rule Loaded | Priority |
|---------|-------------|----------|
| `agentpm/cli/**/*.py` | cli-development.mdc | 85 |
| `agentpm/commands/**/*.py` | cli-development.mdc | 85 |
| `**/adapters/**/*.py` | database-patterns.mdc | 90 |
| `**/methods/**/*.py` | database-patterns.mdc | 90 |
| `**/database/**/*.py` | database-patterns.mdc | 90 |
| `**/models/**/*.py` | database-patterns.mdc | 90 |
| `tests/**/*.py` | testing-standards.mdc | 85 |
| `**/*_test.py` | testing-standards.mdc | 85 |
| `**/test_*.py` | testing-standards.mdc | 85 |
| `docs/**/*.md` | documentation-quality.mdc | 75 |
| `*.md` | documentation-quality.mdc | 75 |
| **ALL FILES** | aipm-master.mdc | 100 |

### Priority System

Rules load in priority order (highest first):

1. **Priority 100**: aipm-master.mdc (always)
2. **Priority 90**: database-patterns.mdc
3. **Priority 85**: cli-development.mdc, testing-standards.mdc
4. **Priority 75**: documentation-quality.mdc

**Multiple Rules**: If a file matches multiple patterns, all matching rules load (they stack).

**Example**:
```python
# File: agentpm/database/adapters/task_adapter.py
# Matches: **/adapters/**/*.py
# Loads:
#   1. aipm-master.mdc (priority 100, always)
#   2. database-patterns.mdc (priority 90, matched pattern)
```

---

## apm Command Quick Reference

### Session Management

```bash
# Project overview
apm status

# List work items
apm work-item list
apm work-item list --status=in_progress
apm work-item list --phase=I1_IMPLEMENTATION

# Show work item details
apm work-item show <id>

# Get context
apm context show
apm context show --work-item-id=<id>
apm context show --task-id=<id>
```

### Work Item Lifecycle

```bash
# Create work item
apm work-item create "Feature Name" --type=feature

# Progress work item (automatic state machine)
apm work-item next <id>          # Auto-advance to next logical state

# Explicit state control (when needed)
apm work-item validate <id>      # PROPOSED → VALIDATED
apm work-item accept <id> --agent <role>  # VALIDATED → ACCEPTED
apm work-item start <id>         # ACCEPTED → IN_PROGRESS
apm work-item submit-review <id> # IN_PROGRESS → REVIEW
apm work-item approve <id>       # REVIEW → COMPLETED
apm work-item request-changes <id> --reason "..."  # REVIEW → IN_PROGRESS

# Dependencies
apm work-item add-dependency <id> --depends-on=<other-id>
apm work-item list-dependencies <id>
```

### Task Management

```bash
# Create task
apm task create "Task Name" --type=implementation --effort=4

# List tasks
apm task list
apm task list --work-item-id=<id>
apm task list --status=in_progress

# Show task details
apm task show <id>

# Progress task (automatic)
apm task next <id>               # Auto-advance to next logical state

# Explicit state control
apm task validate <id>           # PROPOSED → VALIDATED
apm task accept <id> --agent <role>  # VALIDATED → ACCEPTED
apm task start <id>              # ACCEPTED → IN_PROGRESS
apm task submit-review <id>      # IN_PROGRESS → REVIEW
apm task approve <id>            # REVIEW → COMPLETED
apm task request-changes <id> --reason "..."  # REVIEW → IN_PROGRESS

# Complete with evidence
apm task complete <id> --evidence="Implementation details"
```

### Rules & Quality

```bash
# List all rules
apm rules list

# Filter by enforcement level
apm rules list -e BLOCK          # Blocking rules
apm rules list -e GUIDE          # Guideline rules

# Filter by category
apm rules list -c code_quality
apm rules list -c testing
apm rules list -c documentation

# Show rule details
apm rules show DP-001
```

### Learnings & Evidence

```bash
# List learnings
apm learnings list
apm learnings list --recent
apm learnings list --search="keywords"

# Record learning
apm learnings record --type=decision \
  --content="Why we chose approach X"

apm learnings record --type=pattern \
  --content="Pattern observed in implementation"

apm learnings record --type=deployment \
  --content="Deployment went smoothly, no issues"
```

### Ideas & Analysis

```bash
# Create idea
apm idea create "Feature idea" --type=enhancement

# Analyze idea
apm idea analyze <id>
apm idea analyze <id> --comprehensive

# List ideas
apm idea list
```

### Documentation

```bash
# Add document to work item
apm document add \
  --entity-type=work_item \
  --entity-id=<id> \
  --file-path="docs/planning/requirements/wi-X-requirements.md" \
  --document-type=requirements

# List documents
apm document list --entity-type=work_item --entity-id=<id>
```

---

## Migration Guide from 22-Rule Setup

### What Changed

**Old Structure** (22 files):
```
.cursor/rules/
├── Infrastructure (5 files): architecture, plugins, context, etc.
├── Implementation (6 files): coding, CLI, database, testing, etc.
├── Documentation (3 files): style, quality gates, etc.
├── Cursor-specific (7 files): workflow, patterns, checklists, etc.
└── Agent (1 file): enablement
```

**New Structure** (5 files):
```
.cursor/rules/
├── aipm-master.mdc              # Core orchestration (was 7 Cursor files)
├── cli-development.mdc          # CLI patterns (was 1 file)
├── database-patterns.mdc        # DB patterns (was 1 file + architecture)
├── documentation-quality.mdc    # Doc standards (was 3 files)
└── testing-standards.mdc        # Test patterns (was 1 file)
```

### Content Mapping

| Old Files | New Location | Notes |
|-----------|-------------|--------|
| **Cursor-specific (7 files)** | `aipm-master.mdc` | Workflow orchestration consolidated |
| `coding-standards.mdc` | Removed | Now in Python/DB rules |
| `cli-development.mdc` | `cli-development.mdc` | Enhanced, auto-attach |
| `database-patterns.mdc` | `database-patterns.mdc` | Enhanced, auto-attach |
| `testing-standards.mdc` | `testing-standards.mdc` | Enhanced, auto-attach |
| `documentation-*.mdc` (3) | `documentation-quality.mdc` | Consolidated |
| `project-architecture.mdc` | `aipm-master.mdc` | Workflow sections |
| `plugin-architecture.mdc` | Archived | Reference only |
| `context-system.mdc` | `aipm-master.mdc` | Context commands |
| `security-patterns.mdc` | Archived | Enforced by rules system |
| `workflow-quality-gates.mdc` | `aipm-master.mdc` | Gate validation |
| `agent-enablement.mdc` | Archived | Agents in database |

### Benefits of Consolidation

**Cognitive Load**:
- **Before**: 22 files, unclear which applies when
- **After**: 5 files, clear auto-attach triggers

**Maintenance**:
- **Before**: Update multiple files for workflow changes
- **After**: Update master rule only

**File Size**:
- **Before**: 154 KB total
- **After**: 60 KB total (65% reduction)

**Loading**:
- **Before**: All 22 files loaded always
- **After**: 1 master + context-aware auto-attach

**Clarity**:
- **Before**: Overlapping content, unclear precedence
- **After**: Clear hierarchy, single source of truth

### Rollback Instructions

See Setup Guide section "Rollback Procedure" for detailed steps.

**Quick Rollback**:
```bash
# Restore archived rules
cp .cursor/rules/_archive/*.mdc .cursor/rules/

# Remove consolidated rules
rm .cursor/rules/aipm-master.mdc
rm .cursor/rules/cli-development.mdc
rm .cursor/rules/database-patterns.mdc
rm .cursor/rules/documentation-quality.mdc
rm .cursor/rules/testing-standards.mdc

# Restart Cursor
```

---

## Related Documentation

### Core Documentation

- **Setup Guide**: `docs/cursor-integration/setup.md`
  - Installation and verification
  - Troubleshooting
  - Rollback procedures

- **Usage Guide**: `docs/cursor-integration/usage.md`
  - How consolidated rules work
  - Common workflows with examples
  - Best practices
  - Command patterns by phase

- **Architecture Design**: `docs/architecture/cursor-integration-consolidation-design.md`
  - Complete design specification
  - Rationale for consolidation
  - Technical architecture
  - Future enhancements

### Developer Documentation

- **Developer Guide**: `docs/developer-guide/`
  - Contributing to APM (Agent Project Manager)
  - Code patterns
  - Testing guidelines

- **Workflow Guide**: `docs/components/workflow/`
  - Phase progression details
  - Quality gates
  - State machines

- **Context System**: `docs/components/context/`
  - Context assembly
  - 6W analysis
  - Confidence scoring

### Command Documentation

```bash
# Built-in help for all commands
apm --help
apm work-item --help
apm task --help
apm context --help
apm rules --help
apm learnings --help
```

---

## Appendix: File Size Analysis

### Active Rules Breakdown

| File | Size | Purpose | Auto-Attach Pattern |
|------|------|---------|-------------------|
| aipm-master.mdc | 13 KB | Core orchestration | Always active |
| database-patterns.mdc | 14 KB | DB layer patterns | **/adapters/**/*.py, **/methods/**/*.py |
| cli-development.mdc | 12 KB | CLI patterns | agentpm/cli/**/*.py |
| testing-standards.mdc | 11 KB | Test patterns | tests/**/*.py |
| documentation-quality.mdc | 11 KB | Doc standards | docs/**/*.md |
| **Total Active** | **60 KB** | | |

### Archived Rules (Reference Only)

| Category | File Count | Total Size |
|----------|-----------|-----------|
| Infrastructure | 5 | 35 KB |
| Implementation | 6 | 42 KB |
| Documentation | 3 | 21 KB |
| Cursor-specific | 7 | 49 KB |
| Agent | 1 | 7 KB |
| **Total Archive** | **22** | **154 KB** |

### Space Savings

- **Active Content**: 60 KB (current)
- **Old Total**: 154 KB (archived)
- **Reduction**: 94 KB saved (65% reduction)
- **Benefit**: Faster loading, clearer structure, easier maintenance

---

## Glossary

**Terms Used in Rules**:

- **AAA Pattern**: Arrange-Act-Assert test structure
- **Auto-Attach**: Automatic rule loading based on file patterns
- **Database-First**: All runtime state from database, not files
- **Gate**: Quality checkpoint that must pass before phase progression
- **Glob Pattern**: File path matching pattern (e.g., `**/*.py`)
- **Phase**: Workflow stage (D1, P1, I1, R1, O1, E1)
- **Priority**: Rule loading order (higher loads first)
- **Service Result**: Pattern for operation outcomes (success/error/data)
- **Three-Layer**: Models → Adapters → Methods architecture
- **6W**: WHO, WHAT, WHEN, WHERE, WHY, HOW analysis

---

**Version**: 1.0.0
**Document Status**: Published
**Last Review**: 2025-10-20
**Next Review**: 2025-11-20 (or when rules updated)

**Feedback**: Submit issues or improvements via work item system
**Maintenance**: Update when rules change or patterns evolve

---

**End of Reference Documentation**
