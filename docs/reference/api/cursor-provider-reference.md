---
title: Cursor Provider API Reference
category: api_reference
version: 1.0.0
status: active
author: AIPM Documentation
date: 2025-10-20
related:
  - docs/guides/setup_guide/cursor-provider-setup.md
  - docs/guides/user_guide/cursor-provider-usage.md
  - docs/operations/troubleshooting/cursor-provider-issues.md
tags:
  - cursor
  - provider
  - api
  - reference
  - cli
---

# Cursor Provider API Reference

## Overview

Complete reference for the Cursor Provider CLI commands, configuration files, Python API, database schema, hooks, and template variables.

---

## CLI Commands

### apm provider install

Install Cursor provider to current project.

**Syntax**:
```bash
apm provider install cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config PATH` | File path | None | Path to configuration YAML file |
| `--interactive` | Flag | False | Interactive installation with prompts |
| `--skip-rules` | Flag | False | Skip rule installation |
| `--skip-modes` | Flag | False | Skip custom mode installation |
| `--skip-hooks` | Flag | False | Skip hook installation |
| `--skip-memories` | Flag | False | Skip initial memory sync |
| `--force` | Flag | False | Overwrite existing installation |

**Examples**:

```bash
# Default installation
apm provider install cursor

# Interactive installation
apm provider install cursor --interactive

# Custom config
apm provider install cursor --config=.aipm/cursor-config.yml

# Skip memories (for new projects)
apm provider install cursor --skip-memories

# Force reinstall
apm provider install cursor --force
```

**Exit Codes**:
- `0`: Success
- `1`: Installation failed (check logs)
- `2`: Validation failed (prerequisites not met)
- `3`: Configuration error (invalid config file)

**Output**:

Returns installation summary with:
- Installation ID
- Installed rules count
- Installed modes count
- Installed hooks count
- Synced memories count
- Verification status

---

### apm provider uninstall

Uninstall Cursor provider from current project.

**Syntax**:
```bash
apm provider uninstall cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--keep-config` | Flag | False | Keep configuration file |
| `--keep-memories` | Flag | True | Keep memory files |
| `--purge` | Flag | False | Remove all provider data including memories |

**Examples**:

```bash
# Standard uninstall (keeps memories)
apm provider uninstall cursor

# Complete removal
apm provider uninstall cursor --purge

# Keep config for reinstall
apm provider uninstall cursor --keep-config
```

**Exit Codes**:
- `0`: Success
- `1`: Uninstall failed
- `4`: Provider not installed

---

### apm provider verify

Verify Cursor provider installation.

**Syntax**:
```bash
apm provider verify cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose` | Flag | False | Show detailed verification output |
| `--fix` | Flag | False | Auto-fix issues if possible |

**Examples**:

```bash
# Basic verification
apm provider verify cursor

# Detailed verification
apm provider verify cursor --verbose

# Verify and fix issues
apm provider verify cursor --fix
```

**Exit Codes**:
- `0`: All checks passed
- `1`: Verification failed (issues found)
- `5`: Warnings only (not critical)

**Checks Performed**:
1. Installation record exists in database
2. Rule files exist and are valid
3. Hook files exist and are executable
4. Custom modes configured in Cursor settings
5. Cursor IDE detected on system
6. Configuration file valid

---

### apm provider sync-memories

Sync memories between AIPM and Cursor.

**Syntax**:
```bash
apm provider sync-memories cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--direction` | Choice | bidirectional | Sync direction: `to-cursor`, `from-cursor`, `bidirectional` |
| `--type` | Choice | all | Memory type filter: `all`, `decision`, `learning`, `pattern`, `context` |
| `--min-confidence` | Float | 0.70 | Minimum confidence for synced memories |
| `--force` | Flag | False | Force sync even if unchanged |

**Examples**:

```bash
# Bi-directional sync
apm provider sync-memories cursor

# Export to Cursor only
apm provider sync-memories cursor --direction=to-cursor

# Import from Cursor only
apm provider sync-memories cursor --direction=from-cursor

# Sync only decisions
apm provider sync-memories cursor --type=decision

# Include low-confidence memories
apm provider sync-memories cursor --min-confidence=0.50

# Force full re-sync
apm provider sync-memories cursor --force
```

**Exit Codes**:
- `0`: Sync successful
- `1`: Sync failed
- `6`: No changes to sync

**Output**:

Returns sync summary:
- Memories created count
- Memories updated count
- Memories skipped count (unchanged)
- Total memories count

---

### apm provider generate-memory

Generate Cursor memory from work item context.

**Syntax**:
```bash
apm provider generate-memory cursor [OPTIONS]
```

**Options**:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--work-item-id` | Integer | Yes | Work item ID to generate memory from |
| `--type` | Choice | No | Memory type: `project_context`, `decision`, `learning`, `pattern` |
| `--title` | String | No | Custom memory title (auto-generated if omitted) |

**Examples**:

```bash
# Generate from work item
apm provider generate-memory cursor --work-item-id=125

# Specify type
apm provider generate-memory cursor --work-item-id=125 --type=decision

# Custom title
apm provider generate-memory cursor --work-item-id=125 --title="Priority Field Implementation"
```

**Exit Codes**:
- `0`: Memory generated
- `1`: Generation failed
- `7`: Work item not found

**Output**:

Returns:
- Memory ID
- Memory file path
- Confidence score

---

### apm provider list-memories

List Cursor memories.

**Syntax**:
```bash
apm provider list-memories cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type` | Choice | all | Filter by type: `all`, `decision`, `learning`, `pattern`, `context`, `constraint`, `architecture` |
| `--tag` | String | None | Filter by tag |
| `--work-item-id` | Integer | None | Filter by work item ID |
| `--min-confidence` | Float | 0.0 | Minimum confidence threshold |
| `--limit` | Integer | 50 | Maximum results to return |
| `--format` | Choice | table | Output format: `table`, `json`, `csv` |

**Examples**:

```bash
# List all memories
apm provider list-memories cursor

# Filter by type
apm provider list-memories cursor --type=decision

# Filter by tag
apm provider list-memories cursor --tag=migration

# Filter by work item
apm provider list-memories cursor --work-item-id=125

# High-confidence only
apm provider list-memories cursor --min-confidence=0.85

# JSON output
apm provider list-memories cursor --format=json
```

**Exit Codes**:
- `0`: Success
- `1`: Query failed

**Output Formats**:

**Table** (default):
```
ID  Type            Title                           Confidence  Created     Tags
--  --------------  ------------------------------  ----------  ----------  ------------------
1   project_context Add task priority field         0.85        2025-10-20  feature, tasks
2   decision        Default priority to medium      0.90        2025-10-20  decision, tasks
3   learning        Migration pattern successful    0.80        2025-10-20  learning, database
```

**JSON**:
```json
[
  {
    "id": 1,
    "type": "project_context",
    "title": "Add task priority field",
    "confidence": 0.85,
    "created_at": "2025-10-20T10:30:00Z",
    "tags": ["feature", "tasks"],
    "file_path": ".cursor/memories/project_context-1.md"
  }
]
```

---

### apm provider configure

Configure Cursor provider settings.

**Syntax**:
```bash
apm provider configure cursor [OPTIONS]
```

**Options**:

| Option | Type | Description |
|--------|------|-------------|
| `--set KEY=VALUE` | String | Set configuration value |
| `--get KEY` | String | Get configuration value |
| `--edit` | Flag | Open config file in editor |
| `--reload` | Flag | Reload configuration from file |
| `--hooks ENABLED` | Choice | Enable/disable hooks: `enabled`, `disabled` |

**Examples**:

```bash
# Set configuration value
apm provider configure cursor --set guardrails.auto_run_safe_commands=true

# Get configuration value
apm provider configure cursor --get guardrails.auto_run_safe_commands

# Edit config file
apm provider configure cursor --edit

# Reload after manual edits
apm provider configure cursor --reload

# Disable hooks temporarily
apm provider configure cursor --hooks=disabled
```

**Exit Codes**:
- `0`: Success
- `1`: Configuration failed
- `8`: Invalid configuration key/value

---

### apm provider status

Show Cursor provider status.

**Syntax**:
```bash
apm provider status cursor [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose` | Flag | False | Show detailed status |
| `--format` | Choice | table | Output format: `table`, `json` |

**Examples**:

```bash
# Basic status
apm provider status cursor

# Detailed status
apm provider status cursor --verbose

# JSON output
apm provider status cursor --format=json
```

**Output**:

```
Cursor Provider Status

Installation ID: 42
Installed: 2025-10-20 10:30:00
Version: 1.0.0

Rules:          6 installed, 6 active
Custom Modes:   6 installed
Hooks:          3 installed, 3 enabled
Memories:       12 synced

Last Sync:      2025-10-20 14:15:00
Cursor Version: 0.42.0

Status: ✓ Active and healthy
```

---

## Configuration File Format

### Complete YAML Specification

**File**: `.aipm/providers/cursor.yml`

```yaml
# Cursor Provider Configuration
# Version: 1.0.0

# ============================================================================
# RULE CONFIGURATION
# ============================================================================
rules:
  # Which rules to install
  enabled_rules:
    - aipm-master           # Required: Core orchestration
    - python-implementation # Optional: Python patterns
    - testing-standards     # Optional: Test requirements
    - cli-development       # Optional: Click CLI patterns
    - database-patterns     # Optional: Three-layer architecture
    - documentation-quality # Optional: Doc standards

  # Auto-attach rules to all Cursor sessions
  auto_attach: true

  # Update rules when AIPM rules database changes
  update_on_sync: true

  # Custom rule templates directory (optional)
  custom_templates_dir: null

  # Rule-specific overrides (optional)
  overrides:
    aipm-master:
      priority: 1  # Load order
    python-implementation:
      enabled: true

# ============================================================================
# MEMORY CONFIGURATION
# ============================================================================
memories:
  # Enable memory sync
  sync_enabled: true

  # Sync direction: to-cursor, from-cursor, bidirectional
  sync_direction: bidirectional

  # What to include in sync
  include_completed_work_items: true
  include_decisions: true
  include_learnings: true
  include_patterns: true
  include_architectural_decisions: true
  include_constraints: true

  # Quality threshold (0.0-1.0)
  min_confidence: 0.70

  # Automatic sync triggers
  auto_sync_on_work_item_complete: true
  auto_sync_on_phase_change: true
  auto_sync_on_evolution_phase: true

  # Memory retention
  max_memories: 100
  auto_archive_old_memories: true
  archive_after_days: 90

# ============================================================================
# CUSTOM MODES CONFIGURATION
# ============================================================================
custom_modes:
  # Enable custom modes
  enabled: true

  # Install all 6 AIPM modes
  install_all: true

  # Or select specific modes
  modes:
    - discovery        # D1 phase
    - planning         # P1 phase
    - implementation   # I1 phase
    - review           # R1 phase
    - operations       # O1 phase
    - evolution        # E1 phase

  # Mode-specific overrides
  overrides:
    implementation:
      auto_apply_edits: true
      auto_run_commands: true
    review:
      auto_apply_edits: false
      auto_run_commands: true
    operations:
      auto_apply_edits: false
      auto_run_commands: false

# ============================================================================
# GUARDRAILS CONFIGURATION
# ============================================================================
guardrails:
  # Enable guardrails
  enabled: true

  # Auto-run safe commands without confirmation
  auto_run_safe_commands: true

  # Auto-apply edits in Implementation mode
  auto_apply_edits_in_implementation: true

  # Commands that can run without confirmation
  safe_commands:
    # Testing
    - pytest
    - pytest *
    - python -m pytest
    # Static analysis
    - mypy
    - mypy *
    - pylint
    - pylint *
    - bandit
    - bandit -r *
    # Formatting (check mode)
    - black --check
    - ruff check
    # AIPM read-only
    - apm status
    - apm work-item show *
    - apm task show *
    - apm context show *
    - apm rules list *
    # Git read-only
    - git status
    - git diff
    - git log

  # Commands that always require confirmation
  require_confirmation:
    # Git destructive
    - git push
    - git push *
    - git tag
    - git reset --hard
    - git rebase
    - git merge
    # File operations
    - rm -rf
    - rm -rf *
    - mv * /dev/null
    # AIPM state changes
    - apm work-item approve *
    - apm task approve *
    - apm work-item complete *
    # Database operations
    - sqlite3 *
    - psql *
    - mysql *
    # Deployment
    - kubectl *
    - docker push *
    - terraform apply

  # File patterns to protect from auto-edit
  protected_files:
    - "*.db"
    - "*.sqlite"
    - "*.sqlite3"
    - ".env"
    - ".env.*"
    - "credentials.json"
    - "secrets.yml"
    - "secrets.yaml"
    - "setup.py"
    - "pyproject.toml"

  # Directory patterns to protect
  protected_directories:
    - .git/
    - .aipm/
    - node_modules/
    - venv/
    - .venv/

# ============================================================================
# HOOKS CONFIGURATION
# ============================================================================
hooks:
  # Enable hooks system
  enabled: true

  # Individual hook toggles
  beforeAgentRequest: true
  afterAgentRequest: true
  onFileSave: false  # Can be slow on large projects

  # Debug logging
  debug_logging: false
  log_file: .aipm/logs/hooks.log

  # beforeAgentRequest settings
  beforeAgentRequest_settings:
    inject_work_item_context: true
    inject_active_rules: true
    inject_phase_requirements: true
    inject_task_context: true
    detect_branch_work_item: true  # Parse WI-XXX from branch name

  # afterAgentRequest settings
  afterAgentRequest_settings:
    update_task_status: true
    log_ai_interactions: true
    auto_sync_memories: false  # Manual sync preferred
    detect_completed_work: true

  # onFileSave settings
  onFileSave_settings:
    run_linters: true
    check_coverage: false  # Too slow for every save
    validate_rules: true
    linters:
      - mypy
      - pylint

# ============================================================================
# INDEXING CONFIGURATION
# ============================================================================
indexing:
  # Exclude AIPM metadata from Cursor indexing
  exclude_aipm_metadata: true

  # Additional exclusion patterns
  exclude_patterns:
    # AIPM
    - .aipm/**
    - .cursor/**
    # Python
    - __pycache__/**
    - "*.pyc"
    - "*.pyo"
    - "*.pyd"
    - .Python
    - build/**
    - dist/**
    - "*.egg-info/**"
    # Virtual environments
    - venv/**
    - .venv/**
    - env/**
    - .env/**
    # Node
    - node_modules/**
    - .npm/**
    # IDE
    - .vscode/**
    - .idea/**
    - "*.swp"
    - "*.swo"
    # Test coverage
    - .coverage
    - htmlcov/**
    - .pytest_cache/**
    # Logs
    - "*.log"
    - logs/**

  # Include patterns (override exclusions)
  include_patterns:
    - docs/**
    - agentpm/**
    - tests/**
    - README.md
    - CHANGELOG.md

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
advanced:
  # Template rendering
  template_engine: jinja2
  template_variables:
    project_name: "{{ project.name }}"
    python_version: "{{ project.python_version }}"

  # Performance
  cache_enabled: true
  cache_duration: 300  # seconds

  # Error handling
  fail_on_hook_error: false
  retry_on_sync_failure: true
  max_retries: 3

  # Feature flags
  experimental_features:
    background_agents: false
    context_symbols_api: false
```

### Configuration Sections Reference

#### rules

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled_rules` | List[str] | All 6 rules | Which rules to install |
| `auto_attach` | bool | true | Auto-attach rules to sessions |
| `update_on_sync` | bool | true | Update rules when AIPM rules change |
| `custom_templates_dir` | str\|null | null | Custom rule templates directory |

#### memories

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `sync_enabled` | bool | true | Enable memory sync |
| `sync_direction` | str | bidirectional | Sync direction |
| `include_*` | bool | true | What to sync |
| `min_confidence` | float | 0.70 | Quality threshold |
| `auto_sync_on_*` | bool | varies | Auto-sync triggers |

#### custom_modes

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | true | Enable custom modes |
| `install_all` | bool | true | Install all 6 modes |
| `modes` | List[str] | All 6 | Specific modes to install |
| `overrides` | Dict | {} | Mode-specific settings |

#### guardrails

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | true | Enable guardrails |
| `auto_run_safe_commands` | bool | true | Auto-run safe commands |
| `auto_apply_edits_in_implementation` | bool | true | Auto-edit in I1 mode |
| `safe_commands` | List[str] | See spec | Commands that can auto-run |
| `require_confirmation` | List[str] | See spec | Commands requiring confirmation |
| `protected_files` | List[str] | See spec | Files protected from auto-edit |

#### hooks

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | true | Enable hooks |
| `beforeAgentRequest` | bool | true | Enable before-request hook |
| `afterAgentRequest` | bool | true | Enable after-request hook |
| `onFileSave` | bool | false | Enable file-save hook |
| `debug_logging` | bool | false | Enable debug logs |
| `*_settings` | Dict | See spec | Hook-specific settings |

#### indexing

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `exclude_aipm_metadata` | bool | true | Exclude .aipm/ from indexing |
| `exclude_patterns` | List[str] | See spec | Additional exclusions |
| `include_patterns` | List[str] | See spec | Explicit inclusions |

---

## Hook Scripts Reference

### beforeAgentRequest.sh

**Location**: `.cursor/hooks/beforeAgentRequest.sh`

**Trigger**: Before every AI request in Cursor chat

**Environment Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `CURSOR_REQUEST` | string | User's request text |
| `CURSOR_SESSION_ID` | string | Unique session ID |
| `CURSOR_PROJECT_PATH` | string | Project root path |
| `AIPM_DB_PATH` | string | Path to AIPM database |

**Exit Codes**:
- `0`: Success (continue with request)
- `1`: Failure (abort request)
- `2`: Warning (continue but log)

**Injected Context Format**:

```markdown
<!-- AIPM Context (injected by beforeAgentRequest hook) -->

## Current Work Item
WI-125: Add task priority field
Phase: I1_IMPLEMENTATION
Status: in_progress

## Active Task
Task 652: Add priority field to model
Type: implementation
Effort: 2.0h / 4.0h max

## Phase Requirements
- All implementation tasks complete
- Tests written (≥90% coverage)
- Documentation updated

## Active Rules
- DP-003: Three-layer architecture
- TES-004: Test coverage ≥90%
- CQ-013: Type hints required

<!-- End AIPM Context -->
```

**Customization**:

Edit `.cursor/hooks/beforeAgentRequest.sh` to modify injection logic.

---

### afterAgentRequest.sh

**Location**: `.cursor/hooks/afterAgentRequest.sh`

**Trigger**: After AI response in Cursor chat

**Environment Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `CURSOR_RESPONSE` | string | AI's response text |
| `CURSOR_SESSION_ID` | string | Unique session ID |
| `CURSOR_PROJECT_PATH` | string | Project root path |
| `AIPM_DB_PATH` | string | Path to AIPM database |
| `CURSOR_FILES_CHANGED` | string | Comma-separated changed files |

**Actions Performed**:

1. Parse response for completed actions
2. Update task status if applicable
3. Log interaction to audit trail
4. Detect work item completion

**Exit Codes**:
- `0`: Success
- `1`: Failure (logged but not blocking)

**Database Updates**:

```sql
-- Task status update (if detected)
UPDATE tasks
SET status = 'in_progress', updated_at = datetime('now')
WHERE id = ?;

-- Audit log entry
INSERT INTO audit_log (entity_type, entity_id, action, metadata, created_at)
VALUES ('task', 652, 'ai_interaction', '{"response_length": 1234}', datetime('now'));
```

---

### onFileSave.sh

**Location**: `.cursor/hooks/onFileSave.sh`

**Trigger**: When any file is saved in Cursor

**Environment Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `CURSOR_FILE_PATH` | string | Saved file path (relative) |
| `CURSOR_PROJECT_PATH` | string | Project root path |
| `AIPM_DB_PATH` | string | Path to AIPM database |

**Validations Performed**:

1. Run configured linters (mypy, pylint)
2. Check rule compliance
3. Validate file patterns

**Exit Codes**:
- `0`: All validations passed
- `1`: Validation failed (shows warning)

**Performance Note**:

This hook can be slow on large projects. Disable if needed:

```yaml
hooks:
  onFileSave: false
```

---

## Database Schema

### cursor_memories Table

```sql
CREATE TABLE cursor_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id INTEGER NOT NULL,

    -- Memory metadata
    memory_type TEXT NOT NULL CHECK(memory_type IN (
        'project_context',
        'decision',
        'learning',
        'pattern',
        'constraint',
        'architecture'
    )),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN (
        'aipm_decision',
        'aipm_learning',
        'aipm_context',
        'manual',
        'generated'
    )),
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),

    -- AIPM linkage
    work_item_id INTEGER,
    task_id INTEGER,
    evidence_id INTEGER,

    -- Additional metadata
    tags TEXT,  -- JSON array: ["tag1", "tag2"]
    file_path TEXT,
    file_hash TEXT,

    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    last_synced_at TEXT,

    -- Foreign keys
    FOREIGN KEY (installation_id) REFERENCES provider_installations(id) ON DELETE CASCADE,
    FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE SET NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

CREATE INDEX idx_cursor_memories_installation ON cursor_memories(installation_id);
CREATE INDEX idx_cursor_memories_type ON cursor_memories(memory_type);
CREATE INDEX idx_cursor_memories_work_item ON cursor_memories(work_item_id);
CREATE INDEX idx_cursor_memories_hash ON cursor_memories(file_hash);
```

### provider_installations Table

```sql
CREATE TABLE provider_installations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL,
    project_id INTEGER NOT NULL,

    -- Installation metadata
    version TEXT NOT NULL,
    config TEXT,  -- JSON configuration
    installed_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,

    -- Status
    status TEXT CHECK(status IN ('active', 'disabled', 'error')),
    error_message TEXT,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_provider_installations_project ON provider_installations(project_id);
CREATE INDEX idx_provider_installations_provider ON provider_installations(provider_name);
```

---

## Template Variables Reference

### Available in Rule Templates

All `.mdc.j2` templates have access to these variables:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `project.name` | str | Project name | "APM (Agent Project Manager)" |
| `project.description` | str | Project description | "AI-powered project management" |
| `project.python_version` | str | Python version | "3.10" |
| `project.database_path` | str | Database path | ".aipm/data/aipm.db" |
| `project.tech_stack` | List[str] | Technologies | ["Python", "SQLite", "Click"] |
| `config.rules.*` | Any | Rule configuration | `config.rules.auto_attach` |
| `config.guardrails.*` | Any | Guardrail settings | `config.guardrails.safe_commands` |

### Available in Mode Templates

All `aipm-*.json.j2` templates have access to:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `mode.name` | str | Mode name | "AIPM Implementation" |
| `mode.phase` | str | AIPM phase | "I1_IMPLEMENTATION" |
| `guardrails.*` | Any | Guardrail settings | `guardrails.allow_auto_edits` |
| `tools.*` | List[str] | Enabled tools | `tools.implementation` |

### Available in Memory Templates

All memory `.md.j2` templates have access to:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `work_item.*` | Any | Work item data | `work_item.name` |
| `context.*` | Any | 6W context | `context.confidence` |
| `decisions` | List[Dict] | Recent decisions | `decisions[0].title` |
| `learnings` | List[Dict] | Captured learnings | `learnings[0].content` |
| `patterns` | List[Dict] | Architectural patterns | `patterns[0].description` |

### Template Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `now()` | None | datetime | Current timestamp |
| `format_date(dt)` | datetime | str | Format date as YYYY-MM-DD |
| `format_datetime(dt)` | datetime | str | Format datetime as ISO 8601 |
| `slugify(text)` | str | str | Create URL-safe slug |
| `truncate(text, length)` | str, int | str | Truncate text to length |

---

## Python API

### CursorProvider Class

**Import**:

```python
from agentpm.providers.cursor.provider import CursorProvider
```

**Methods**:

#### install()

Install Cursor provider.

```python
def install(
    self,
    project_path: Path,
    config: Optional[CursorConfig] = None,
    skip_rules: bool = False,
    skip_modes: bool = False,
    skip_hooks: bool = False,
    skip_memories: bool = False,
    force: bool = False
) -> ProviderInstallation:
    """
    Install Cursor provider to project.

    Args:
        project_path: Project root directory
        config: Configuration (uses defaults if None)
        skip_rules: Skip rule installation
        skip_modes: Skip custom mode installation
        skip_hooks: Skip hook installation
        skip_memories: Skip initial memory sync
        force: Overwrite existing installation

    Returns:
        ProviderInstallation object

    Raises:
        ProviderInstallationError: If installation fails
        ValidationError: If config invalid
    """
```

**Example**:

```python
from pathlib import Path
from agentpm.providers.cursor.provider import CursorProvider

provider = CursorProvider()
installation = provider.install(
    project_path=Path.cwd(),
    force=True
)
print(f"Installed: {installation.id}")
```

#### uninstall()

Uninstall Cursor provider.

```python
def uninstall(
    self,
    project_path: Path,
    keep_config: bool = False,
    keep_memories: bool = True,
    purge: bool = False
) -> bool:
    """
    Uninstall Cursor provider from project.

    Args:
        project_path: Project root directory
        keep_config: Keep configuration file
        keep_memories: Keep memory files
        purge: Remove all data including memories

    Returns:
        True if successful

    Raises:
        ProviderNotInstalledError: If provider not installed
    """
```

#### verify()

Verify installation.

```python
def verify(
    self,
    project_path: Path,
    fix: bool = False
) -> Dict[str, Any]:
    """
    Verify Cursor provider installation.

    Args:
        project_path: Project root directory
        fix: Auto-fix issues if possible

    Returns:
        Verification result dict with:
        - checks: List of check results
        - passed: bool (all checks passed)
        - warnings: List of warnings
        - errors: List of errors

    Raises:
        ProviderNotInstalledError: If provider not installed
    """
```

#### sync_memories()

Sync memories.

```python
def sync_memories(
    self,
    project_path: Path,
    direction: str = "bidirectional",
    memory_type: Optional[str] = None,
    min_confidence: float = 0.70,
    force: bool = False
) -> Dict[str, int]:
    """
    Sync memories between AIPM and Cursor.

    Args:
        project_path: Project root directory
        direction: Sync direction (to-cursor, from-cursor, bidirectional)
        memory_type: Filter by type (None for all)
        min_confidence: Minimum confidence threshold
        force: Force sync even if unchanged

    Returns:
        Sync statistics dict:
        - created: int
        - updated: int
        - skipped: int
        - total: int

    Raises:
        ProviderNotInstalledError: If provider not installed
        MemorySyncError: If sync fails
    """
```

---

## Related Documentation

- **Setup Guide**: [cursor-provider-setup.md](../../guides/setup_guide/cursor-provider-setup.md)
- **User Guide**: [cursor-provider-usage.md](../../guides/user_guide/cursor-provider-usage.md)
- **Troubleshooting**: [cursor-provider-issues.md](../../operations/troubleshooting/cursor-provider-issues.md)
- **Architecture**: [cursor-provider-architecture.md](../../architecture/design/cursor-provider-architecture.md)

---

**Last Updated**: 2025-10-20
**Version**: 1.0.0
**Status**: Active
