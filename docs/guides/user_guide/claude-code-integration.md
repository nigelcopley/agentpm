# Claude Code Integration - User Guide

## Overview

The Claude Code Integration provides comprehensive programmatic integration between APM (Agent Project Manager) and Claude Code, enabling automated generation of Claude Code plugins, hooks, subagents, settings, slash commands, checkpoints, and memory tools.

### Benefits

- **Automated Integration Generation**: Generate complete Claude Code integrations with a single command
- **Project-Specific Customization**: Create integrations tailored to specific APM projects
- **Agent-Specific Integration**: Generate integrations for individual agents
- **Flexible Settings Management**: Multi-layer settings with session, user, and project scopes
- **Session Lifecycle Tracking**: Automatic tracking of sessions, prompts, and tool usage
- **Context Handover**: Seamless handover between sessions with previous context
- **Quality Validation**: Built-in validation for integration completeness and correctness

### Key Features

1. **Integration Generation**: Create comprehensive Claude Code integrations from AIPM data
2. **Settings Management**: Configure hooks, memory, subagents, and performance settings
3. **Session Tracking**: Automatic session lifecycle tracking with handover support
4. **Plugin System**: Capability-based plugin architecture with hooks, memory, commands, checkpointing, and subagents
5. **Validation**: Validate integrations for completeness and compliance
6. **Import/Export**: Share and version integrations using JSON/YAML format

---

## Installation

The Claude Code integration is included with APM (Agent Project Manager). No separate installation required.

### Prerequisites

- APM (Agent Project Manager) installed and initialized (`apm init`)
- Active APM project
- Claude Code CLI tool (optional, for testing generated integrations)

### Verification

Verify the integration is available:

```bash
apm claude-code --help
```

You should see available commands for Claude Code integration management.

---

## Quick Start

### 1. Generate Your First Integration

Generate a comprehensive Claude Code integration for your project:

```bash
# Generate integration in current directory
apm claude-code generate

# Generate with custom output directory
apm claude-code generate -o .claude/integrations/

# Generate with custom integration name
apm claude-code generate -n "My AIPM Integration"

# Generate in JSON format (default is JSON)
apm claude-code generate -f json

# Generate in YAML format
apm claude-code generate -f yaml
```

**Output**:
```
✓ Claude Code integration generated successfully!

Integration: APM (Agent Project Manager) Claude Code Integration
Version: 1.0.0
Components: 5 plugins, 8 hooks, 12 subagents, 1 settings, 4 slash commands,
           3 checkpoints, 5 memory tools
Output: /Users/you/project/.claude/integrations/
```

### 2. Generate Project-Specific Integration

Generate integration tailored to a specific APM project:

```bash
# First, find your project ID
apm project list

# Generate integration for project
apm claude-code generate-project -p 1

# Custom output directory
apm claude-code generate-project -p 1 -o .claude/project1/
```

### 3. Generate Agent-Specific Integration

Generate integration for a specific agent:

```bash
# List available agents
apm agents list

# Generate integration for agent
apm claude-code generate-agent -a "context-delivery"

# Custom output directory
apm claude-code generate-agent -a "test-implementer" -o .claude/agents/
```

### 4. Validate Integration

Validate generated integration:

```bash
# Validate from cache
apm claude-code validate -n "APM (Agent Project Manager) Claude Code Integration"

# Validate from file
apm claude-code validate -f integration.json
```

**Output**:
```
✓ Integration 'APM (Agent Project Manager) Claude Code Integration' is valid!

Components: {'plugins': 5, 'hooks': 8, 'subagents': 12}
Warnings: 0
```

---

## Command Reference

### Integration Management

#### `generate`

Generate comprehensive Claude Code integration.

```bash
apm claude-code generate [OPTIONS]
```

**Options**:
- `-o, --output-dir PATH`: Output directory (default: current directory)
- `-p, --project-id INT`: Project ID for project-specific integration
- `-n, --name TEXT`: Integration name (default: "APM (Agent Project Manager) Claude Code Integration")
- `-f, --format [json|yaml]`: Export format (default: json)

**Examples**:
```bash
# Basic generation
apm claude-code generate

# With all options
apm claude-code generate \
  -o .claude/integrations/ \
  -p 1 \
  -n "Production Integration" \
  -f yaml
```

#### `generate-project`

Generate integration for specific project.

```bash
apm claude-code generate-project -p PROJECT_ID [OPTIONS]
```

**Options**:
- `-p, --project-id INT` (required): Project ID
- `-o, --output-dir PATH`: Output directory (default: current directory)

**Examples**:
```bash
# Generate for project 1
apm claude-code generate-project -p 1

# Custom output
apm claude-code generate-project -p 1 -o .claude/project1/
```

#### `generate-agent`

Generate integration for specific agent.

```bash
apm claude-code generate-agent -a AGENT_ROLE [OPTIONS]
```

**Options**:
- `-a, --agent-role TEXT` (required): Agent role name
- `-o, --output-dir PATH`: Output directory (default: current directory)

**Examples**:
```bash
# Generate for context-delivery agent
apm claude-code generate-agent -a "context-delivery"

# Generate for test-implementer
apm claude-code generate-agent -a "test-implementer" -o .claude/agents/
```

#### `validate`

Validate integration configuration.

```bash
apm claude-code validate [OPTIONS]
```

**Options**:
- `-n, --integration-name TEXT`: Integration name to validate
- `-f, --file PATH`: Integration file to validate

**Examples**:
```bash
# Validate from cache
apm claude-code validate -n "APM (Agent Project Manager) Claude Code Integration"

# Validate from file
apm claude-code validate -f integration.json
```

#### `list-integrations`

List all cached integrations.

```bash
apm claude-code list-integrations
```

**Output**:
```
Claude Code Integrations
┌─────────────────────────────────┬─────────┬────────────┬──────────────────┐
│ Name                            │ Version │ Components │ Created          │
├─────────────────────────────────┼─────────┼────────────┼──────────────────┤
│ APM (Agent Project Manager) Claude Code Integration │ 1.0.0   │ 37         │ 2025-10-21 09:00 │
└─────────────────────────────────┴─────────┴────────────┴──────────────────┘
```

#### `show`

Show detailed integration information.

```bash
apm claude-code show -n INTEGRATION_NAME
```

**Example**:
```bash
apm claude-code show -n "APM (Agent Project Manager) Claude Code Integration"
```

**Output**:
```
Integration Details
Name: APM (Agent Project Manager) Claude Code Integration
Description: Comprehensive Claude Code integration for APM (Agent Project Manager)
Version: 1.0.0
Created: 2025-10-21 09:00
Updated: 2025-10-21 09:15

Component Counts
┌──────────────────┬───────┐
│ Component Type   │ Count │
├──────────────────┼───────┤
│ Plugins          │ 5     │
│ Hooks            │ 8     │
│ Subagents        │ 12    │
│ Settings         │ 1     │
│ Slash Commands   │ 4     │
│ Checkpoints      │ 3     │
│ Memory Tools     │ 5     │
└──────────────────┴───────┘
```

#### `export`

Export integration to file.

```bash
apm claude-code export -n INTEGRATION_NAME [OPTIONS]
```

**Options**:
- `-n, --integration-name TEXT` (required): Integration name
- `-o, --output-file PATH`: Output file path
- `-f, --format [json|yaml]`: Export format (default: json)

**Examples**:
```bash
# Export to default file
apm claude-code export -n "APM (Agent Project Manager) Claude Code Integration"

# Export to custom file
apm claude-code export \
  -n "APM (Agent Project Manager) Claude Code Integration" \
  -o integrations/production.json \
  -f json

# Export as YAML
apm claude-code export \
  -n "APM (Agent Project Manager) Claude Code Integration" \
  -o integrations/production.yaml \
  -f yaml
```

#### `import-integration`

Import integration from file.

```bash
apm claude-code import-integration -i INPUT_FILE
```

**Options**:
- `-i, --input-file PATH` (required): Input file path

**Example**:
```bash
# Import from JSON
apm claude-code import-integration -i integration.json

# Import from YAML
apm claude-code import-integration -i integration.yaml
```

#### `stats`

Show integration statistics.

```bash
apm claude-code stats
```

**Output**:
```
Integration Statistics
Total Integrations: 3
Total Components: 112
Cache Size: 3

Component Breakdown by Integration
┌─────────────────────┬─────────┬───────┬───────────┬──────────┬───────────────┬─────────────┬──────────────┐
│ Integration         │ Plugins │ Hooks │ Subagents │ Settings │ Slash Commands│ Checkpoints │ Memory Tools │
├─────────────────────┼─────────┼───────┼───────────┼──────────┼───────────────┼─────────────┼──────────────┤
│ APM (Agent Project Manager) Integration │ 5       │ 8     │ 12        │ 1        │ 4             │ 3           │ 5            │
│ Project 1           │ 3       │ 6     │ 8         │ 1        │ 2             │ 2           │ 3            │
│ Test Agent          │ 1       │ 2     │ 1         │ 1        │ 1             │ 1           │ 1            │
└─────────────────────┴─────────┴───────┴───────────┴──────────┴───────────────┴─────────────┴──────────────┘
```

#### `clear-cache`

Clear integration cache.

```bash
apm claude-code clear-cache
```

**Confirmation Required**: You will be prompted to confirm before clearing.

---

### Settings Management

#### `settings show`

Show current settings.

```bash
apm claude-code settings show [OPTIONS]
```

**Options**:
- `-p, --project-id INT`: Project ID for project-specific settings
- `-f, --format [text|json|yaml]`: Output format (default: text)

**Examples**:
```bash
# Show default settings
apm claude-code settings show

# Show project-specific settings
apm claude-code settings show -p 1

# Show as JSON
apm claude-code settings show -f json

# Show as YAML
apm claude-code settings show -f yaml
```

**Output (text format)**:
```
Core Settings
Plugin Enabled: True
Verbose Logging: False
Project ID: None

Hooks Settings
Enabled Hooks: session_start, session_end, prompt_submit, stop, subagent_stop
Timeout: 30s
Retry on Failure: False
Max Retries: 3

Memory Settings
Auto Load: True
Auto Generate: True
Generation Frequency: session_end
Retention: 90 days
Max File Size: 500 KB
Cache Duration: 60 min

Subagent Settings
Enabled: True
Max Parallel: 3
Timeout: 300s
Auto Cleanup: True
Max Depth: 3

Performance Settings
Caching: True
Cache TTL: 300s
Max Concurrent Requests: 5
Request Timeout: 120s
Metrics: True
Metrics Interval: 60s
```

#### `settings set`

Set a specific setting.

```bash
apm claude-code settings set -k KEY -v VALUE [OPTIONS]
```

**Options**:
- `-k, --key TEXT` (required): Setting key (dotted path)
- `-v, --value TEXT` (required): Setting value
- `-p, --project-id INT`: Project ID for project-specific settings
- `-s, --scope [session|user|project]`: Setting scope (default: session)
- `-t, --type [bool|int|float|str]`: Value type (default: str)

**Examples**:
```bash
# Enable verbose logging (session scope)
apm claude-code settings set \
  -k verbose_logging \
  -v true \
  -t bool

# Set hook timeout (project scope)
apm claude-code settings set \
  -k hooks.timeout_seconds \
  -v 60 \
  -p 1 \
  -s project \
  -t int

# Enable specific hook
apm claude-code settings set \
  -k hooks.enabled.tool_result \
  -v true \
  -t bool

# Set memory retention
apm claude-code settings set \
  -k memory.retention_days \
  -v 180 \
  -t int
```

#### `settings reset`

Reset settings to defaults.

```bash
apm claude-code settings reset [OPTIONS]
```

**Options**:
- `-p, --project-id INT`: Project ID
- `-s, --scope [session|user|project]`: Scope to reset (default: session)

**Examples**:
```bash
# Reset session settings
apm claude-code settings reset

# Reset user settings
apm claude-code settings reset -s user

# Reset project settings
apm claude-code settings reset -p 1 -s project
```

**Confirmation Required**: You will be prompted to confirm before resetting.

#### `settings validate`

Validate current settings.

```bash
apm claude-code settings validate [OPTIONS]
```

**Options**:
- `-p, --project-id INT`: Project ID

**Example**:
```bash
# Validate default settings
apm claude-code settings validate

# Validate project settings
apm claude-code settings validate -p 1
```

**Output (no warnings)**:
```
✓ All settings are valid!

No warnings detected.
```

**Output (with warnings)**:
```
⚠ Settings are valid but have 2 warning(s):

• Hook timeout is very low (<5s), may cause premature failures
• Memory retention is low (<7 days), may lose important context
```

#### `settings export`

Export settings to file.

```bash
apm claude-code settings export -o OUTPUT_FILE [OPTIONS]
```

**Options**:
- `-o, --output-file PATH` (required): Output file path
- `-p, --project-id INT`: Project ID
- `-f, --format [json|yaml]`: Export format (default: json)

**Examples**:
```bash
# Export to JSON
apm claude-code settings export -o settings.json

# Export project settings as YAML
apm claude-code settings export \
  -p 1 \
  -o project1-settings.yaml \
  -f yaml
```

#### `settings import`

Import settings from file.

```bash
apm claude-code settings import -i INPUT_FILE [OPTIONS]
```

**Options**:
- `-i, --input-file PATH` (required): Input file path
- `-p, --project-id INT`: Project ID
- `-s, --scope [session|user|project]`: Import scope (default: session)

**Examples**:
```bash
# Import from JSON
apm claude-code settings import -i settings.json

# Import to project scope
apm claude-code settings import \
  -i project-settings.json \
  -p 1 \
  -s project
```

---

## Settings Reference

### Settings Hierarchy

Settings are loaded with the following precedence (highest to lowest):

1. **Session Overrides** (temporary, in-memory)
2. **User Config** (`~/.agentpm/config/claude_code_settings.json`)
3. **Project Settings** (database)
4. **System Defaults** (hardcoded)

### Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `plugin_enabled` | bool | `true` | Enable Claude Code plugin system |
| `verbose_logging` | bool | `false` | Enable verbose debug logging |
| `project_id` | int | `null` | APM project ID for context |

### Hooks Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `hooks.enabled.session_start` | bool | `true` | Enable session-start hook |
| `hooks.enabled.session_end` | bool | `true` | Enable session-end hook |
| `hooks.enabled.prompt_submit` | bool | `true` | Enable prompt-submit hook |
| `hooks.enabled.tool_result` | bool | `false` | Enable tool-result hook |
| `hooks.enabled.pre_tool_use` | bool | `false` | Enable pre-tool-use hook |
| `hooks.enabled.post_tool_use` | bool | `false` | Enable post-tool-use hook |
| `hooks.enabled.stop` | bool | `true` | Enable stop hook |
| `hooks.enabled.subagent_stop` | bool | `true` | Enable subagent-stop hook |
| `hooks.timeout_seconds` | int | `30` | Maximum hook execution time (1-300s) |
| `hooks.retry_on_failure` | bool | `false` | Retry failed hooks |
| `hooks.max_retries` | int | `3` | Maximum retry attempts (0-10) |

### Memory Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `memory.auto_load_memory` | bool | `true` | Automatically load memory at session start |
| `memory.auto_generate_memory` | bool | `true` | Automatically generate memory snapshots |
| `memory.generation_frequency` | enum | `session_end` | When to generate memory (`session_end`, `manual`, `scheduled`) |
| `memory.retention_days` | int | `90` | Days to retain memory snapshots (1-365) |
| `memory.max_file_size_kb` | int | `500` | Maximum memory file size (100-5000 KB) |
| `memory.cache_duration_minutes` | int | `60` | Cache duration for memory data (5-1440 min) |

### Subagent Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `subagents.enabled` | bool | `true` | Enable subagent system |
| `subagents.max_parallel` | int | `3` | Maximum parallel executions (1-10) |
| `subagents.timeout_seconds` | int | `300` | Subagent execution timeout (30-3600s) |
| `subagents.auto_cleanup` | bool | `true` | Automatically cleanup completed subagents |
| `subagents.max_depth` | int | `3` | Maximum subagent nesting depth (1-5) |

### Performance Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `performance.enable_caching` | bool | `true` | Enable response caching |
| `performance.cache_ttl_seconds` | int | `300` | Cache time-to-live (60-3600s) |
| `performance.max_concurrent_requests` | int | `5` | Maximum concurrent API requests (1-20) |
| `performance.request_timeout_seconds` | int | `120` | API request timeout (30-600s) |
| `performance.enable_metrics` | bool | `true` | Enable performance metrics collection |
| `performance.metrics_interval_seconds` | int | `60` | Metrics collection interval (10-300s) |

---

## Workflows

### Workflow 1: Initial Setup

Set up Claude Code integration for a new project:

```bash
# 1. Initialize APM project (if not already done)
apm init

# 2. Generate Claude Code integration
apm claude-code generate -o .claude/

# 3. Configure settings
apm claude-code settings set -k verbose_logging -v true -t bool
apm claude-code settings set -k memory.retention_days -v 180 -t int

# 4. Validate integration
apm claude-code validate -n "APM (Agent Project Manager) Claude Code Integration"

# 5. Export for version control
apm claude-code export \
  -n "APM (Agent Project Manager) Claude Code Integration" \
  -o .claude/integration.json
```

### Workflow 2: Project-Specific Integration

Create integration for a specific project:

```bash
# 1. List projects to find ID
apm project list

# 2. Generate project integration
apm claude-code generate-project -p 1 -o .claude/project1/

# 3. Configure project-specific settings
apm claude-code settings set \
  -k hooks.enabled.tool_result \
  -v true \
  -p 1 \
  -s project \
  -t bool

# 4. Export project settings
apm claude-code settings export \
  -p 1 \
  -o .claude/project1/settings.json
```

### Workflow 3: Agent Development

Generate integration for a specific agent during development:

```bash
# 1. Generate agent integration
apm claude-code generate-agent -a "test-implementer" -o .claude/agents/

# 2. Configure agent-specific settings (session scope for testing)
apm claude-code settings set -k subagents.timeout_seconds -v 600 -t int

# 3. Test and iterate
# (make changes to agent in database)

# 4. Regenerate integration
apm claude-code generate-agent -a "test-implementer" -o .claude/agents/

# 5. Reset session settings when done
apm claude-code settings reset
```

---

## Troubleshooting

### Integration Generation Issues

**Issue**: Integration generation fails with "No agents found"

**Solution**:
1. Verify APM is initialized: `apm status`
2. Check agents are registered: `apm agents list`
3. Initialize database if needed: `apm init`

**Issue**: Integration generation fails with "Permission denied"

**Solution**:
1. Check directory permissions: `ls -la .claude/`
2. Create directory manually: `mkdir -p .claude/integrations/`
3. Specify different output directory: `apm claude-code generate -o /tmp/integration/`

### Settings Issues

**Issue**: Settings changes not persisting

**Solution**:
1. Check scope - session scope is temporary: Use `-s user` or `-s project`
2. Verify permissions on config directory: `ls -la ~/.agentpm/config/`
3. Create config directory: `mkdir -p ~/.agentpm/config/`

**Issue**: Settings validation warnings

**Solution**:
1. Review warnings: `apm claude-code settings validate`
2. Adjust settings based on recommendations
3. Re-validate: `apm claude-code settings validate`

### Validation Issues

**Issue**: Integration validation fails

**Solution**:
1. Check validation errors: `apm claude-code validate -n "Integration Name"`
2. Regenerate integration: `apm claude-code generate`
3. Verify all required components present

---

## Best Practices

### Integration Management

1. **Version Control**: Export integrations to JSON/YAML and commit to version control
   ```bash
   apm claude-code export -n "Integration" -o .claude/integration.json
   git add .claude/integration.json
   git commit -m "Add Claude Code integration"
   ```

2. **Validation**: Always validate before deployment
   ```bash
   apm claude-code validate -f integration.json
   ```

3. **Documentation**: Document integration purpose and customizations in README

### Settings Management

1. **Use Appropriate Scope**:
   - **Session**: Temporary testing (cleared on session end)
   - **User**: Personal preferences (all projects)
   - **Project**: Project-specific configurations (persistent)

2. **Export Settings**: Export settings for team sharing
   ```bash
   apm claude-code settings export -o team-settings.json
   ```

3. **Validate After Changes**: Validate settings after modifications
   ```bash
   apm claude-code settings set -k some.setting -v value
   apm claude-code settings validate
   ```

### Performance Optimization

1. **Enable Caching**: Keep caching enabled for better performance
   ```bash
   apm claude-code settings set -k performance.enable_caching -v true -t bool
   ```

2. **Tune Concurrency**: Adjust based on your system
   ```bash
   # Lower for resource-constrained systems
   apm claude-code settings set -k performance.max_concurrent_requests -v 3 -t int

   # Higher for powerful systems
   apm claude-code settings set -k performance.max_concurrent_requests -v 10 -t int
   ```

3. **Adjust Timeouts**: Set appropriate timeouts for your workflow
   ```bash
   # Longer for complex operations
   apm claude-code settings set -k subagents.timeout_seconds -v 600 -t int
   ```

---

## Related Documentation

- [Developer Guide](../developer/claude-code-integration-development.md) - Extending and developing integrations
- [API Reference](../../reference/api/claude-code-integration-api.md) - Complete API documentation
- [Plugin Usage Guide](./claude-code-plugin-usage.md) - Plugin system details
- [Hooks Usage Guide](./claude-code-hooks-usage.md) - Hooks system details

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-10-21
- **Author**: AIPM Development Team
