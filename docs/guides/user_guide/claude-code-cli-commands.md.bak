# Claude Code CLI Commands - User Guide

User-facing commands for managing Claude Code integration in APM (Agent Project Manager) projects.

## Overview

The `apm claude-code` command group provides tools for initializing, configuring, and managing Claude Code integration within your APM (Agent Project Manager) project.

## Quick Start

```bash
# 1. Initialize Claude Code integration
apm claude-code init

# 2. Check integration status
apm claude-code status

# 3. Sync AIPM context to Claude memory
apm claude-code sync

# 4. Manage hooks
apm claude-code hooks --enable session_start --enable prompt_submit

# 5. Create session checkpoint
apm claude-code checkpoint create --name milestone-1
```

## Commands

### `apm claude-code init`

Initialize Claude Code integration for your project.

**What it does**:
- Creates `.claude/` directory structure
- Generates initial memory files
- Creates default settings
- Sets up hooks configuration
- Adds README with next steps

**Options**:
- `--force` - Force reinitialization if already initialized

**Example**:
```bash
# First-time initialization
apm claude-code init

# Reinitialize (overwrites existing files)
apm claude-code init --force
```

**Directory Structure Created**:
```
.claude/
├── plugins/          # Claude Code plugins
├── memory/           # Memory files for context
│   ├── project_context.md
│   └── recent_work.md
├── checkpoints/      # Session checkpoints
├── settings/         # Integration settings
│   └── integration.json
└── README.md         # Integration documentation
```

---

### `apm claude-code status`

Show current Claude Code integration status.

**What it displays**:
- Integration location and status
- Component status (Plugins, Memory, Checkpoints, Settings)
- Active hooks
- Recent checkpoints

**Example**:
```bash
apm claude-code status
```

**Sample Output**:
```
╭─ Claude Code Integration Status ─╮
│ Location: /path/to/project/.claude │
│ Status: Initialized                 │
╰─────────────────────────────────────╯

Components:
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Component  ┃ Status ┃ Details        ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Plugins    │ ✓      │ 0 plugins      │
│ Memory     │ ✓      │ 2 files        │
│ Checkpoints│ ✓      │ 3 checkpoints  │
│ Settings   │ ✓      │ Configured     │
└────────────┴────────┴────────────────┘

Active Hooks:
• session_start
• session_end
• prompt_submit
```

---

### `apm claude-code sync`

Sync AIPM state to Claude Code memory files.

**What it does**:
- Generates `project_context.md` from active work items
- Generates `recent_work.md` from recent tasks
- Updates memory file timestamps
- Pulls data from AIPM database

**Options**:
- `--force` - Force regeneration of all memory files

**Example**:
```bash
# Sync with database
apm claude-code sync

# Force full regeneration
apm claude-code sync --force
```

**Generated Files**:
- `.claude/memory/project_context.md` - Active work items with context
- `.claude/memory/recent_work.md` - Recent tasks and progress

---

### `apm claude-code hooks`

Enable or disable Claude Code hooks.

**What it does**:
- Updates hook configuration in settings
- Displays current hook status
- Supports multiple enable/disable operations

**Options**:
- `--enable HOOK` - Enable a hook (can be used multiple times)
- `--disable HOOK` - Disable a hook (can be used multiple times)

**Available Hooks**:
- `session_start` - Runs when Claude session starts
- `session_end` - Runs when Claude session ends
- `prompt_submit` - Runs before prompt submission
- `response_complete` - Runs after Claude responds
- `tool_call` - Runs when tool is called
- `context_load` - Runs when context loads

**Examples**:
```bash
# Enable a single hook
apm claude-code hooks --enable session_start

# Disable a hook
apm claude-code hooks --disable prompt_submit

# Enable multiple hooks at once
apm claude-code hooks --enable session_start --enable session_end --enable tool_call

# Mixed enable/disable
apm claude-code hooks --enable session_start --disable prompt_submit

# Show current hook status (no options)
apm claude-code hooks
```

**Sample Output**:
```
╭─ Hook Configuration Updated ─╮
│ ✓ Enabled: session_start      │
│ ✓ Enabled: session_end         │
│ ✗ Disabled: prompt_submit      │
╰────────────────────────────────╯

Current Hook Status:
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Hook           ┃ Status  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ session_start  │ Enabled │
│ session_end    │ Enabled │
│ prompt_submit  │ Disabled│
└────────────────┴─────────┘
```

---

### `apm claude-code checkpoint`

Manage session checkpoints.

**Actions**:
- `create` - Create a new checkpoint
- `list` - List all checkpoints
- `restore` - Restore from a checkpoint (planned)
- `delete` - Delete a checkpoint

**Options**:
- `--name NAME` - Checkpoint name (required for create/restore/delete)

**Examples**:

#### Create Checkpoint
```bash
# Create named checkpoint
apm claude-code checkpoint create --name milestone-1

# Create checkpoint for specific session phase
apm claude-code checkpoint create --name before-refactor
```

#### List Checkpoints
```bash
apm claude-code checkpoint list
```

**Sample Output**:
```
Session Checkpoints:
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Name             ┃ Created            ┃ Type   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ milestone-1      │ 2025-10-21 10:30   │ manual │
│ before-refactor  │ 2025-10-21 09:15   │ manual │
│ initial          │ 2025-10-21 08:00   │ manual │
└──────────────────┴────────────────────┴────────┘
```

#### Restore Checkpoint
```bash
apm claude-code checkpoint restore --name milestone-1
```

**Note**: Restore functionality is planned but not yet implemented.

#### Delete Checkpoint
```bash
apm claude-code checkpoint delete --name old-checkpoint
```

---

## Common Workflows

### Initial Setup
```bash
# 1. Initialize integration
apm claude-code init

# 2. Check everything is set up correctly
apm claude-code status

# 3. Enable recommended hooks
apm claude-code hooks --enable session_start --enable session_end

# 4. Create initial checkpoint
apm claude-code checkpoint create --name initial-setup
```

### During Development
```bash
# Before starting work session
apm claude-code sync                           # Update context
apm claude-code checkpoint create --name pre-session

# Check integration health
apm claude-code status

# After completing milestone
apm claude-code sync                           # Update context
apm claude-code checkpoint create --name milestone-complete
```

### Debugging Integration
```bash
# Check status
apm claude-code status

# Disable all hooks temporarily
apm claude-code hooks --disable session_start --disable session_end --disable prompt_submit

# Reinitialize if needed
apm claude-code init --force

# Re-enable hooks
apm claude-code hooks --enable session_start --enable session_end
```

---

## Integration with AIPM Workflow

### Work Item Context
When you run `apm claude-code sync`, memory files are generated from your active work items:

```markdown
# Project Context

## Active Work Items (5)

### WI-123: Add Authentication System
- Type: feature
- Status: active
- Phase: I1_implementation
- Context: Implement JWT-based authentication for API endpoints...

### WI-124: Fix Database Migration
- Type: fix
- Status: in_progress
- Phase: I1_implementation
- Context: Resolve foreign key constraint issues in migration_0025...
```

### Task Progress
Recent tasks are tracked in memory:

```markdown
# Recent Work

## Recent Tasks (20)

- **Task #456**: Implement JWT token generation (completed)
- **Task #457**: Add auth middleware (in_progress)
- **Task #458**: Create user login endpoint (ready)
```

---

## Settings File Format

The integration settings are stored in `.claude/settings/integration.json`:

```json
{
  "plugin_enabled": true,
  "verbose_logging": false,
  "hooks": {
    "enabled": {
      "session_start": true,
      "session_end": true,
      "prompt_submit": true
    }
  },
  "memory": {
    "auto_load_memory": true,
    "auto_generate_memory": true,
    "generation_frequency": "on_change"
  }
}
```

You can manually edit this file, or use `apm claude-code hooks` to update hook settings.

---

## Troubleshooting

### Integration Not Found
```
⚠ Claude Code integration not initialized
Run: apm claude-code init
```

**Solution**: Run `apm claude-code init` to create the integration.

### Settings File Not Found
```
⚠ Settings file not found
Run: apm claude-code init
```

**Solution**: Reinitialize the integration:
```bash
apm claude-code init --force
```

### Memory Files Not Updating
If `apm claude-code sync` doesn't update memory files:

1. Check database connection:
   ```bash
   apm status
   ```

2. Force regeneration:
   ```bash
   apm claude-code sync --force
   ```

3. Check for active work items:
   ```bash
   apm work-item list --status=active
   ```

---

## Related Commands

- `apm status` - View project status (complements `claude-code status`)
- `apm work-item list` - List work items (source for `sync`)
- `apm task list` - List tasks (source for `sync`)
- `apm memory generate` - Generate memory files (alternative to `sync`)

---

## See Also

- [Claude Code Integration Guide](./claude-integration-readme.md)
- [AIPM CLI Reference](../../reference/cli/)
- [Memory System Documentation](../../architecture/memory-system.md)
