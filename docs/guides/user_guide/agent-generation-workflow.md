# Agent Generation Workflow

**Document Type**: User Guide
**Audience**: Users, AI coding agents
**Purpose**: Complete guide to agent generation system
**Last Updated**: 2025-10-18

---

## Overview

APM uses a **three-stage agent generation system** that separates agent definitions, database storage, and provider-specific file generation.

### Key Benefits

- **Single Source of Truth**: Agent metadata lives in database, files are generated on-demand
- **Multi-Provider Support**: Same agent definitions work across different LLM providers
- **Version Control**: Agent evolution tracked in database with migrations
- **Consistency**: Generated files automatically follow provider conventions

---

## Three-Stage Workflow

### Stage 1: YAML Catalog (Development Time)

**Purpose**: Define agent specifications in human-readable format

**Location**: `_RULES/agents/` directory (documentation only)

**Contents**:
- Agent role and persona
- Description and responsibilities
- Behavioral rules
- Success metrics
- Metadata

**Example**:
```yaml
# _RULES/agents/context-generator.yaml
role: context-generator
persona: Context Assembly Specialist
description: |
  Assembles comprehensive session context from database records,
  project files, and plugin intelligence.
behavioral_rules:
  - Load context hierarchically: project → work item → task
  - Calculate confidence scores for all elements
  - Identify missing context and recommend research
success_metrics: |
  Context confidence >70%, load time <2s, cache hit rate >60%
```

**Important**: These YAML files are **documentation and initial catalog only**. They are NOT used at runtime.

---

### Stage 2: Database Population (Init Time)

**Purpose**: Populate agents table with initial agent definitions

**When**: During `apm init` or when migrations run

**How**: Migration 0029 populates database with 5 utility agents

**Migration**: `migration_0029.py` - Add five new default utility agents

**Agents Created**:
1. `context-generator` - Assembles session context
2. `agent-builder` - Creates new agents from specifications
3. `database-query-agent` - SQL query generation and execution
4. `file-operations-agent` - CRUD operations for files
5. `workflow-coordinator` - State machine transitions

**Database Schema**:
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL UNIQUE,
    display_name TEXT,
    description TEXT,
    sop_content TEXT,
    metadata TEXT,  -- JSON: behavioral_rules, etc.
    is_active INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

**Verification**:
```bash
# Check agents in database
apm agents list

# Or query directly
sqlite3 .agentpm/data/agentpm.db "SELECT role, display_name FROM agents"
```

**Important**: Agents require a project to exist. If `apm init` hasn't run yet, migration 0029 will skip agent creation with a warning.

---

### Stage 3: File Generation (Post-Init)

**Purpose**: Generate provider-specific agent files for LLM consumption

**When**: On-demand via CLI command

**How**: Provider generator system reads from database and generates files

**Command**:
```bash
apm agents generate --all
```

**What It Does**:
1. **Detects Provider**: Auto-detects LLM provider from environment
2. **Loads from Database**: Queries agents table for agent definitions
3. **Applies Template**: Uses provider-specific Jinja2 templates
4. **Generates Files**: Creates `.claude/agents/*.md` (or other provider formats)
5. **Validates Output**: Ensures generated files are valid

**Provider Detection Order**:
1. `AIPM_LLM_PROVIDER` environment variable
2. `.claude/` directory exists → `claude-code`
3. `.cursor/` directory exists → `cursor`
4. Default to `claude-code`

**Output Locations** (by provider):
- **claude-code**: `.claude/agents/*.md`
- **cursor**: `.cursor/agents/*.md` (future)
- **gemini**: `.gemini/agents/*.md` (future)

---

## Complete Workflow Example

### 1. Initialize Project

```bash
cd /path/to/your/project
apm init "My Project"
```

**What Happens**:
- Creates `.agentpm/` directory structure
- Runs database migrations (including migration 0029)
- Populates agents table with 5 utility agents
- ⚠️ **Does NOT generate agent files yet**

**Verify**:
```bash
# Check database has agents
apm agents list

# Expected output:
# 📋 Agents (5)
# ┌────────────────────────────┬────────────────────────────┐
# │ Role                       │ Display Name               │
# ├────────────────────────────┼────────────────────────────┤
# │ context-generator          │ Context Assembly Specialist│
# │ agent-builder              │ Agent System Architect     │
# │ database-query-agent       │ Database Operations...     │
# │ file-operations-agent      │ File System Operations...  │
# │ workflow-coordinator       │ State Machine Orchestrator │
# └────────────────────────────┴────────────────────────────┘
```

---

### 2. Generate Agent Files

```bash
apm agents generate --all
```

**What Happens**:
- Auto-detects provider (e.g., `claude-code`)
- Loads agents from database
- Generates 5 agent markdown files
- Creates `.claude/agents/` directory structure

**Output**:
```
🔍 Using provider: claude-code

🔍 Generating 5 agent(s)...
████████████████████████████████████████ 100%

✅ Generated 5 agent file(s)
📁 Location: .claude/agents/

💡 Agents are ready to use via Task tool delegation
```

**Verify**:
```bash
# Check generated files
ls .claude/agents/

# Expected output:
# context-generator.md
# agent-builder.md
# database-query-agent.md
# file-operations-agent.md
# workflow-coordinator.md
```

---

### 3. View Generated Agent

```bash
cat .claude/agents/context-generator.md
```

**File Format**:
```markdown
# Context Generator

**Role**: context-generator
**Persona**: Context Assembly Specialist

## Description

Assembles comprehensive session context from database records,
project files, and plugin intelligence. Calculates context confidence
and identifies gaps requiring additional research.

## Behavioral Rules

- Load context hierarchically: project → work item → task → dependencies
- Calculate confidence scores for all context elements
- Identify missing context and recommend research agents
- Compress context using token-efficient formatting
- Cache frequently accessed context elements

## Success Metrics

Context confidence >70%, load time <2s, cache hit rate >60%

## Project Rules

[Rules loaded from database...]

---

Generated: 2025-10-18
Provider: claude-code
```

---

## Command Reference

### `apm agents list`

**Purpose**: Show agents in database

**Syntax**:
```bash
apm agents list [OPTIONS]
```

**Options**:
- `--active-only`: Show only active agents
- `--format=json`: JSON output

**Example**:
```bash
# List all agents
apm agents list

# Active agents only
apm agents list --active-only

# JSON output
apm agents list --format=json
```

---

### `apm agents generate`

**Purpose**: Generate provider-specific agent files from database

**Syntax**:
```bash
apm agents generate [OPTIONS]
```

**Options**:
- `--all`: Generate all agents
- `--role <name>`: Generate specific agent
- `--provider <name>`: Specify provider (claude-code, cursor, gemini)
- `--force`: Regenerate even if files exist
- `--dry-run`: Show what would be generated without writing
- `--output-dir <path>`: Override default output directory

**Examples**:
```bash
# Generate all agents (auto-detect provider)
apm agents generate --all

# Generate for specific provider
apm agents generate --all --provider=claude-code

# Generate single agent
apm agents generate --role context-generator

# Dry run (preview)
apm agents generate --all --dry-run

# Force regeneration
apm agents generate --all --force

# Custom output directory
apm agents generate --all --output-dir=/tmp/agents
```

---

### `apm agents show`

**Purpose**: Show agent details from database

**Syntax**:
```bash
apm agents show <role>
```

**Example**:
```bash
apm agents show context-generator
```

---

## Troubleshooting

### No Agents in Database

**Problem**: `apm agents list` shows no agents

**Cause**: Migrations haven't run or no project exists

**Solution**:
```bash
# Check if project exists
apm status

# If no project, initialize
apm init "My Project"

# If project exists but no agents, run migrations manually
apm db migrate
```

---

### Provider Not Detected

**Problem**: `❌ Could not detect LLM provider`

**Cause**: No provider-specific directory exists

**Solutions**:
1. **Set environment variable**:
   ```bash
   export AIPM_LLM_PROVIDER=claude-code
   apm agents generate --all
   ```

2. **Create provider directory**:
   ```bash
   mkdir .claude
   apm agents generate --all
   ```

3. **Specify explicitly**:
   ```bash
   apm agents generate --all --provider=claude-code
   ```

---

### Agent Files Already Exist

**Problem**: `✅ Agent 'context-generator' already exists`

**Cause**: Files were previously generated

**Solution**: Use `--force` to regenerate
```bash
apm agents generate --all --force
```

---

### Migration 0029 Skipped Agent Creation

**Problem**: Migration runs but says "No project found - skipping agent creation"

**Cause**: Project record doesn't exist in database yet

**Solution**:
```bash
# Run apm init first
apm init "My Project"

# Now agents will be created automatically
```

**Technical Details**: Migration 0029 requires a project_id to create agents. It queries the projects table and skips agent creation if no project exists.

---

## Advanced Topics

### Adding Custom Agents

To add custom agents to your project:

**Option 1: Direct Database Insert**
```bash
sqlite3 .agentpm/data/agentpm.db
```

```sql
INSERT INTO agents (
    project_id,
    role,
    display_name,
    description,
    sop_content,
    metadata,
    is_active,
    created_at,
    updated_at
)
VALUES (
    1,
    'my-custom-agent',
    'My Custom Agent',
    'Description of what agent does',
    'Success metrics',
    '{"behavioral_rules": ["Rule 1", "Rule 2"]}',
    1,
    datetime('now'),
    datetime('now')
);
```

**Option 2: Create Migration**

Create a new migration file (e.g., `migration_0030.py`) following the pattern in `migration_0029.py`.

**Then Generate**:
```bash
apm agents generate --role my-custom-agent
```

---

### Provider-Specific Customization

Each provider generator uses Jinja2 templates located in:
```
agentpm/providers/generators/<provider>/templates/
```

**Claude Code Template**: `agent.md.j2`

**Available Template Variables**:
- `agent` - Agent model from database
- `project_rules` - List of project rules
- `universal_rules` - List of universal rules
- `additional_context` - Provider-specific data

**Customization**:
1. Copy template to project: `.agentpm/templates/agents/`
2. Modify as needed
3. Regenerate: `apm agents generate --all --force`

---

### Multi-Provider Workflow

Generate agents for multiple providers:

```bash
# Claude Code
apm agents generate --all --provider=claude-code

# Cursor (when implemented)
apm agents generate --all --provider=cursor

# Gemini (when implemented)
apm agents generate --all --provider=gemini
```

This creates provider-specific directories:
```
project/
├── .claude/
│   └── agents/
│       ├── context-generator.md
│       └── ...
├── .cursor/
│   └── agents/
│       ├── context-generator.md
│       └── ...
└── .gemini/
    └── agents/
        ├── context-generator.yaml
        └── ...
```

---

## Key Takeaways

1. **YAML files are documentation only** - Not used at runtime
2. **Database is source of truth** - All agent metadata stored in DB
3. **Files are generated on-demand** - Via `apm agents generate`
4. **Migration 0029 populates agents** - Runs during `apm init`
5. **Project must exist first** - Agents require project_id
6. **Provider detection is automatic** - Or specify with `--provider`
7. **Regeneration is safe** - Use `--force` to update existing files

---

## See Also

- [Provider Generator System](../developer-guide/provider-generator-system.md) - Architecture details
- [Database Schema](../components/database/schema.md) - Agents table structure
- [CLI Commands Reference](03-cli-commands.md) - All CLI commands
- [Agent Architecture](../components/agents/README.md) - Agent system overview

---

**Last Updated**: 2025-10-18
**Version**: 1.0.0
**Pattern**: YAML → DB → Generate (Three-Stage Workflow)
