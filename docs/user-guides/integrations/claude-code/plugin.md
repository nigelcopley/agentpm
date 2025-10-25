# Claude Code Plugin

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](integrations/claude-code/hooks.md) | [Next →](integrations/cursor/overview.md)

## Overview

The Claude Code Plugin provides comprehensive integration with Claude Code, supporting all major capabilities through a unified plugin architecture.

## Features

The Claude Code Plugin supports five key capabilities:

1. **Hooks** - Lifecycle event handling (session start/end, tool use, etc.)
2. **Memory** - Persistent context management
3. **Commands** - Slash command execution
4. **Checkpointing** - State snapshot creation and restoration
5. **Subagents** - Subagent orchestration

## Installation

The plugin is automatically registered when you use the Claude Integration Service:

```python
from agentpm.services.claude_integration import ClaudeIntegrationService
from agentpm.services.claude_integration.plugins import ClaudeCodePlugin

# Initialize service
service = ClaudeIntegrationService()

# Register Claude Code plugin
plugin = ClaudeCodePlugin()
service.register_plugin(plugin)
```

## Usage Examples

### 1. Lifecycle Hooks

Handle Claude Code lifecycle events:

```python
# Session start event
result = plugin.handle({
    "type": "session-start",
    "payload": {"user": "developer"},
    "session_id": "session-123",
    "correlation_id": "req-001"
})

# Prompt submission
result = plugin.handle({
    "type": "prompt-submit",
    "payload": {"prompt": "Implement feature X"},
    "session_id": "session-123",
    "correlation_id": "req-002"
})

# Tool usage tracking
result = plugin.handle({
    "type": "post-tool-use",
    "payload": {"tool": "bash", "command": "pytest"},
    "session_id": "session-123",
    "correlation_id": "req-003"
})

# Session end
result = plugin.handle({
    "type": "session-end",
    "payload": {},
    "session_id": "session-123",
    "correlation_id": "req-004"
})
```

**Supported Event Types:**
- `session-start` - New session begins
- `session-end` - Session ends
- `prompt-submit` - User submits prompt
- `pre-tool-use` - Before tool execution
- `post-tool-use` - After tool execution
- `tool-result` - Tool execution complete
- `stop` - Session stopped
- `subagent-stop` - Subagent completed
- `pre-compact` - Before message compaction
- `notification` - User notification

### 2. Memory Operations

Manage persistent context:

```python
# Set value in memory
result = plugin.handle({
    "scope": "session",
    "action": "set",
    "key": "current_feature",
    "value": "authentication",
    "session_id": "session-123"
})

# Get value from memory
result = plugin.handle({
    "scope": "session",
    "action": "get",
    "key": "current_feature",
    "session_id": "session-123"
})

# Returns: {"status": "success", "data": {"key": "current_feature", "value": "authentication"}}
```

### 3. Slash Commands

Execute custom commands:

```python
# Checkpoint command
result = plugin.handle({
    "command": "checkpoint",
    "args": {"name": "before-refactor"},
    "session_id": "session-123"
})

# Restore checkpoint
result = plugin.handle({
    "command": "restore",
    "args": {"checkpoint_id": "session-123-before-refactor"},
    "session_id": "session-123"
})

# Get context
result = plugin.handle({
    "command": "context",
    "args": {},
    "session_id": "session-123"
})

# Subagent command
result = plugin.handle({
    "command": "subagent",
    "args": {"name": "test-runner"},
    "session_id": "session-123"
})
```

**Available Commands:**
- `/checkpoint [name]` - Create state snapshot
- `/restore <checkpoint_id>` - Restore from snapshot
- `/context` - Get current session context
- `/subagent <name>` - Subagent operations

### 4. Checkpointing

Create and restore state snapshots:

```python
# Create checkpoint
result = plugin.handle({
    "action": "checkpoint",
    "session_id": "session-123"
})

checkpoint_id = result["data"]["checkpoint_id"]

# List checkpoints
result = plugin.handle({
    "action": "list",
    "session_id": "session-123"
})

# Restore checkpoint
result = plugin.handle({
    "action": "restore",
    "checkpoint_id": checkpoint_id,
    "session_id": "session-123"
})
```

**Checkpoint Actions:**
- `checkpoint` - Create new checkpoint
- `restore` - Restore from checkpoint
- `list` - List all checkpoints for session

### 5. Subagent Operations

Orchestrate subagents:

```python
# Start subagent
result = plugin.handle({
    "subagent": "code-implementer",
    "action": "start",
    "session_id": "session-123"
})

# Stop subagent
result = plugin.handle({
    "subagent": "code-implementer",
    "action": "stop",
    "session_id": "session-123"
})
```

## Integration with Hooks Engine

The plugin integrates seamlessly with the hooks engine for automatic event dispatch:

```python
from agentpm.services.claude_integration import ClaudeIntegrationService
from agentpm.services.claude_integration.plugins import ClaudeCodePlugin
from agentpm.services.claude_integration.hooks.models import EventType

# Initialize service with plugin
service = ClaudeIntegrationService()
plugin = ClaudeCodePlugin()
service.register_plugin(plugin)

# Events are automatically dispatched to plugin
result = service.handle_event(
    event_type=EventType.SESSION_START,
    payload={"user": "developer"},
    session_id="session-123",
    correlation_id="req-001"
)

# Check result
if result.success:
    print(f"Event handled: {result.message}")
else:
    print(f"Error: {result.errors}")
```

## Session Context Tracking

The plugin automatically tracks session state:

```python
# After session starts and prompts are submitted
context = plugin.get_session_context("session-123")

# Context contains:
# {
#     "session_id": "session-123",
#     "start_time": "2025-10-21T10:00:00",
#     "metadata": {...},
#     "prompts": [
#         {"prompt": "...", "timestamp": "..."},
#         ...
#     ],
#     "tool_uses": [
#         {"tool": "bash", "timestamp": "..."},
#         ...
#     ]
# }
```

## Error Handling

All plugin operations return a status indicator:

```python
result = plugin.handle({...})

if result["status"] == "success":
    # Handle success
    data = result.get("data", {})
    print(f"Success: {result.get('message')}")
else:
    # Handle error
    error = result.get("error", "Unknown error")
    print(f"Error: {result.get('message')} - {error}")
```

## Advanced Usage

### Capability Discovery

```python
from agentpm.services.claude_integration.plugins import get_registry, PluginCapability

registry = get_registry()
registry.register_plugin(plugin)

# Find all plugins supporting hooks
hook_plugins = registry.get_plugins_by_capability(PluginCapability.HOOKS)

# Check if plugin supports capability
if plugin.supports(PluginCapability.CHECKPOINTING):
    print("Checkpointing is supported")
```

### Plugin Metadata

```python
# Get plugin information
print(f"Plugin: {plugin.name}")
print(f"Version: {plugin.get_version()}")

# List all capabilities
capabilities = [
    PluginCapability.HOOKS,
    PluginCapability.MEMORY,
    PluginCapability.COMMANDS,
    PluginCapability.CHECKPOINTING,
    PluginCapability.SUBAGENTS,
]

for cap in capabilities:
    if plugin.supports(cap):
        print(f"  - {cap.value}")
```

## Testing

The plugin includes comprehensive tests (42 tests, 100% coverage):

```bash
# Run plugin tests
pytest tests/services/claude_integration/test_claude_code_plugin.py -v

# Check coverage
pytest tests/services/claude_integration/test_claude_code_plugin.py \
  --cov=agentpm.services.claude_integration.plugins.claude_code \
  --cov-report=term-missing
```

## Architecture

The plugin follows the APM (Agent Project Manager) plugin pattern:

1. **Protocol-based design** - Implements `ClaudePlugin` protocol
2. **Capability-based routing** - Routes by capability type
3. **Event normalization** - Consistent event handling
4. **State management** - Session context tracking
5. **Error handling** - Graceful error recovery

## See Also

- [Plugin System Architecture](../../architecture/design/cursor-provider-architecture.md)
- [Hooks Engine Documentation](../../architecture/design/claude-integration-consolidation-design.md)
- [API Reference](../../reference/api/)

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Claude Code Plugin](integrations/claude-code/hooks.md)
- [➡️ Next: Cursor Overview](integrations/cursor/overview.md)

---
