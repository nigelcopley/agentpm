# Claude Code Integration - API Reference

## Overview

This document provides complete API reference for the APM (Agent Project Manager) Claude Code integration, including all classes, methods, data models, and interfaces.

---

## Table of Contents

- [ClaudeCodeOrchestrator API](#claudecodeorchestrator-api)
- [Plugin System API](#plugin-system-api)
- [Hooks System API](#hooks-system-api)
- [Settings System API](#settings-system-api)
- [Subagent System API](#subagent-system-api)
- [Checkpointing API](#checkpointing-api)
- [Memory Tools API](#memory-tools-api)
- [Data Models](#data-models)

---

## ClaudeCodeOrchestrator API

**Module**: `agentpm.providers.anthropic.claude_code`

### Class: `ClaudeCodeOrchestrator`

Orchestrates Claude Code integration generation, validation, and management.

#### Constructor

```python
ClaudeCodeOrchestrator(db_service: DatabaseService)
```

**Parameters**:
- `db_service` (`DatabaseService`): Database service for accessing AIPM data

**Example**:

```python
from agentpm.core.database.service import DatabaseService
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator

db = DatabaseService("path/to/aipm.db")
orchestrator = ClaudeCodeOrchestrator(db)
```

---

#### Method: `create_comprehensive_integration`

Generate comprehensive Claude Code integration with all components.

```python
def create_comprehensive_integration(
    self,
    output_dir: Path,
    project_id: Optional[int] = None,
    integration_name: str = "APM (Agent Project Manager) Claude Code Integration"
) -> Integration
```

**Parameters**:
- `output_dir` (`Path`): Directory for generated integration files
- `project_id` (`Optional[int]`): Optional project ID for project-specific integration
- `integration_name` (`str`): Name for the integration

**Returns**:
- `Integration`: Generated integration object with all components

**Raises**:
- `ValueError`: If output_dir is invalid or project_id doesn't exist
- `RuntimeError`: If generation fails

**Example**:
```python
from pathlib import Path

integration = orchestrator.create_comprehensive_integration(
    output_dir=Path(".claude/integrations"),
    project_id=1,
    integration_name="Production Integration"
)

print(f"Generated: {integration.name}")
print(f"Plugins: {len(integration.plugins)}")
print(f"Hooks: {len(integration.hooks)}")
```

---

#### Method: `generate_project_integration`

Generate integration for specific AIPM project.

```python
def generate_project_integration(
    self,
    project_id: int,
    output_dir: Path
) -> Integration
```

**Parameters**:
- `project_id` (`int`): AIPM project ID
- `output_dir` (`Path`): Directory for generated files

**Returns**:
- `Integration`: Project-specific integration

**Raises**:
- `ValueError`: If project_id doesn't exist
- `RuntimeError`: If generation fails

**Example**:
```python
integration = orchestrator.generate_project_integration(
    project_id=1,
    output_dir=Path(".claude/project1")
)
```

---

#### Method: `generate_agent_integration`

Generate integration for specific agent.

```python
def generate_agent_integration(
    self,
    agent_role: str,
    output_dir: Path
) -> Integration
```

**Parameters**:
- `agent_role` (`str`): Agent role identifier (e.g., "context-delivery")
- `output_dir` (`Path`): Directory for generated files

**Returns**:
- `Integration`: Agent-specific integration

**Raises**:
- `ValueError`: If agent_role doesn't exist
- `RuntimeError`: If generation fails

**Example**:
```python
integration = orchestrator.generate_agent_integration(
    agent_role="test-implementer",
    output_dir=Path(".claude/agents")
)
```

---

#### Method: `validate_integration`

Validate integration for completeness and correctness.

```python
def validate_integration(
    self,
    integration: Integration
) -> Dict[str, Any]
```

**Parameters**:
- `integration` (`Integration`): Integration to validate

**Returns**:
- `Dict[str, Any]`: Validation result with structure:
  ```python
  {
      "valid": bool,              # Overall validation status
      "errors": List[str],        # Validation errors (empty if valid)
      "warnings": List[str],      # Validation warnings
      "component_counts": {       # Component counts
          "plugins": int,
          "hooks": int,
          "subagents": int,
          ...
      }
  }
  ```

**Example**:
```python
validation = orchestrator.validate_integration(integration)

if validation["valid"]:
    print("✓ Integration is valid")
else:
    print("✗ Validation failed:")
    for error in validation["errors"]:
        print(f"  - {error}")
```

---

#### Method: `export_integration`

Export integration to file (JSON or YAML).

```python
def export_integration(
    self,
    integration: Integration,
    output_path: Path,
    format: str = "json"
) -> bool
```

**Parameters**:
- `integration` (`Integration`): Integration to export
- `output_path` (`Path`): Output file path
- `format` (`str`): Export format ("json" or "yaml")

**Returns**:
- `bool`: True if export succeeded

**Raises**:
- `ValueError`: If format is invalid
- `IOError`: If file cannot be written

**Example**:
```python
success = orchestrator.export_integration(
    integration=integration,
    output_path=Path("integration.json"),
    format="json"
)

if success:
    print("Export successful")
```

---

#### Method: `import_integration`

Import integration from file.

```python
def import_integration(
    self,
    input_path: Path
) -> Optional[Integration]
```

**Parameters**:
- `input_path` (`Path`): Input file path (JSON or YAML)

**Returns**:
- `Optional[Integration]`: Imported integration or None if import failed

**Raises**:
- `FileNotFoundError`: If input file doesn't exist
- `ValueError`: If file format is invalid

**Example**:
```python
integration = orchestrator.import_integration(
    input_path=Path("integration.json")
)

if integration:
    print(f"Imported: {integration.name}")
```

---

#### Method: `list_integrations`

List all cached integrations.

```python
def list_integrations(self) -> List[str]
```

**Returns**:
- `List[str]`: List of integration names in cache

**Example**:
```python
integrations = orchestrator.list_integrations()
for name in integrations:
    print(f"- {name}")
```

---

#### Method: `get_integration`

Get integration from cache by name.

```python
def get_integration(
    self,
    integration_name: str
) -> Optional[Integration]
```

**Parameters**:
- `integration_name` (`str`): Name of integration

**Returns**:
- `Optional[Integration]`: Integration or None if not found

**Example**:
```python
integration = orchestrator.get_integration("APM (Agent Project Manager) Integration")
if integration:
    print(f"Version: {integration.version}")
```

---

#### Method: `get_integration_stats`

Get statistics about cached integrations.

```python
def get_integration_stats(self) -> Dict[str, Any]
```

**Returns**:
- `Dict[str, Any]`: Statistics with structure:
  ```python
  {
      "total_integrations": int,
      "total_components": int,
      "cache_size": int,
      "component_breakdown": {
          "integration_name": {
              "plugins": int,
              "hooks": int,
              "subagents": int,
              ...
          },
          ...
      }
  }
  ```

**Example**:
```python
stats = orchestrator.get_integration_stats()
print(f"Total integrations: {stats['total_integrations']}")
print(f"Total components: {stats['total_components']}")
```

---

#### Method: `cleanup_integration_cache`

Clear integration cache.

```python
def cleanup_integration_cache(self) -> int
```

**Returns**:
- `int`: Number of integrations removed from cache

**Example**:
```python
count = orchestrator.cleanup_integration_cache()
print(f"Removed {count} integrations from cache")
```

---

## Plugin System API

**Module**: `agentpm.services.claude_integration.plugins.claude_code`

### Class: `ClaudeCodePlugin`

Claude Code integration plugin with capability-based routing.

#### Constructor

```python
ClaudeCodePlugin()
```

**Example**:

```python
from agentpm.services.claude_integration.plugins.claude_code import ClaudeCodePlugin

plugin = ClaudeCodePlugin()
```

---

#### Method: `handle`

Handle plugin input and route to appropriate capability handler.

```python
def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters**:
- `input_data` (`Dict[str, Any]`): Plugin input with routing hints

**Routing Strategy**:
- `"type"` field → Hooks handler
- `"command"` field → Commands handler
- `"scope"` field → Memory handler
- `"checkpoint_id"` field → Checkpointing handler
- `"subagent"` field → Subagents handler

**Returns**:
- `Dict[str, Any]`: Plugin output with structure:
  ```python
  {
      "status": str,        # "success" or "error"
      "message": str,       # Human-readable message
      "data": Dict[str, Any],  # Result data (optional)
      "error": str          # Error message (if status="error")
  }
  ```

**Raises**:
- `ValueError`: If input_data is invalid or missing required fields

**Examples**:

**Hook Event**:
```python
result = plugin.handle({
    "type": "session-start",
    "payload": {"user": "developer"},
    "session_id": "session-123",
    "correlation_id": "req-001"
})

if result["status"] == "success":
    print(f"Session started: {result['data']['session_id']}")
```

**Slash Command**:
```python
result = plugin.handle({
    "command": "checkpoint",
    "args": {"name": "before-refactor"},
    "session_id": "session-123"
})

checkpoint_id = result["data"]["checkpoint_id"]
```

**Memory Operation**:
```python
# Set value
result = plugin.handle({
    "scope": "session",
    "action": "set",
    "key": "current_feature",
    "value": "authentication",
    "session_id": "session-123"
})

# Get value
result = plugin.handle({
    "scope": "session",
    "action": "get",
    "key": "current_feature",
    "session_id": "session-123"
})

value = result["data"]["value"]
```

**Checkpointing**:
```python
# Create checkpoint
result = plugin.handle({
    "action": "checkpoint",
    "session_id": "session-123"
})

# List checkpoints
result = plugin.handle({
    "action": "list",
    "session_id": "session-123"
})

checkpoints = result["data"]["checkpoints"]
```

**Subagent Invocation**:
```python
result = plugin.handle({
    "subagent": "test-implementer",
    "action": "invoke",
    "task_description": "Create tests for UserService",
    "context": {"service": "UserService"},
    "session_id": "session-123",
    "correlation_id": "req-001"
})

if result["status"] == "success":
    artifacts = result["data"]["artifacts"]
```

---

#### Method: `get_version`

Get plugin version.

```python
def get_version(self) -> str
```

**Returns**:
- `str`: Plugin version

**Example**:
```python
version = plugin.get_version()
print(f"Plugin version: {version}")
```

---

#### Method: `get_session_context`

Get session context for debugging/testing.

```python
def get_session_context(
    self,
    session_id: str
) -> Optional[Dict[str, Any]]
```

**Parameters**:
- `session_id` (`str`): Session identifier

**Returns**:
- `Optional[Dict[str, Any]]`: Session context or None if not found

**Example**:
```python
context = plugin.get_session_context("session-123")
if context:
    print(f"Prompts: {len(context['prompts'])}")
    print(f"Tool uses: {len(context['tool_uses'])}")
```

---

#### Method: `clear_session_context`

Clear session context (useful for testing).

```python
def clear_session_context(self, session_id: str) -> None
```

**Parameters**:
- `session_id` (`str`): Session identifier

**Example**:
```python
plugin.clear_session_context("session-123")
```

---

## Hooks System API

**Module**: `agentpm.services.claude_integration.hooks`

### Class: `HooksEngine`

Event dispatch and handler registration engine.

#### Method: `dispatch_event`

Dispatch event to registered handlers.

```python
def dispatch_event(
    self,
    event_type: EventType,
    payload: Dict[str, Any],
    session_id: str,
    correlation_id: str
) -> EventResult
```

**Parameters**:
- `event_type` (`EventType`): Type of event
- `payload` (`Dict[str, Any]`): Event payload data
- `session_id` (`str`): Session identifier
- `correlation_id` (`str`): Request correlation ID

**Returns**:
- `EventResult`: Event handling result

**Example**:

```python
from agentpm.services.claude_integration.hooks import get_hooks_engine, EventType

engine = get_hooks_engine()

result = engine.dispatch_event(
    event_type=EventType.SESSION_START,
    payload={"project_id": 1},
    session_id="session-123",
    correlation_id="req-001"
)

if result.success:
    print(f"Event handled: {result.message}")
```

---

#### Method: `register_handler`

Register event handler.

```python
def register_handler(
    self,
    event_type: EventType,
    handler: Callable[[HookEvent], EventResult]
) -> None
```

**Parameters**:
- `event_type` (`EventType`): Event type to handle
- `handler` (`Callable`): Handler function

**Example**:
```python
def my_handler(event: HookEvent) -> EventResult:
    print(f"Handling: {event.event_type}")
    return EventResult(success=True, message="Handled")

engine.register_handler(EventType.SESSION_START, my_handler)
```

---

### Class: `ClaudeCodeHookHandlers`

Claude Code event handlers for session tracking.

#### Constructor

```python
ClaudeCodeHookHandlers(db_service: DatabaseService)
```

**Parameters**:
- `db_service` (`DatabaseService`): Database service

**Example**:

```python
from agentpm.services.claude_integration.hooks import ClaudeCodeHookHandlers

handlers = ClaudeCodeHookHandlers(db_service)
handlers.register_all()
```

---

#### Method: `register_all`

Register all hook handlers with engine.

```python
def register_all(self) -> None
```

**Example**:
```python
handlers.register_all()
```

---

#### Method: `on_session_start`

Handle SESSION_START event.

```python
def on_session_start(self, event: HookEvent) -> EventResult
```

**Parameters**:
- `event` (`HookEvent`): Session start event

**Expected Payload**:
```python
{
    "project_id": int,           # Required
    "tool_version": str,         # Optional
    "developer_name": str,       # Optional
    "developer_email": str       # Optional
}
```

**Returns**:
- `EventResult`: Result with session data and previous context

**Result Data Structure**:
```python
{
    "session": {
        "session_id": str,
        "project_id": int,
        "start_time": str,
        ...
    },
    "previous_context": {
        "available": bool,
        "work_items": List[...],
        "tasks": List[...],
        "summary": str
    }
}
```

---

#### Method: `on_session_end`

Handle SESSION_END event.

```python
def on_session_end(self, event: HookEvent) -> EventResult
```

**Parameters**:
- `event` (`HookEvent`): Session end event

**Expected Payload**:
```python
{
    "exit_reason": str,    # Optional
    "summary": str         # Optional
}
```

**Returns**:
- `EventResult`: Result with session summary and handover

**Result Data Structure**:
```python
{
    "session": {
        "session_id": str,
        "duration_minutes": float,
        ...
    },
    "summary": str,
    "handover": {
        "work_completed": List[...],
        "decisions": List[...],
        "tool_usage": Dict[str, Dict[str, int]]
    }
}
```

---

#### Method: `on_prompt_submit`

Handle PROMPT_SUBMIT event.

```python
def on_prompt_submit(self, event: HookEvent) -> EventResult
```

**Parameters**:
- `event` (`HookEvent`): Prompt submit event

**Expected Payload**:
```python
{
    "prompt": str,          # Required
    "prompt_number": int    # Optional
}
```

**Returns**:
- `EventResult`: Result with prompt count

---

#### Method: `on_tool_result`

Handle TOOL_RESULT event.

```python
def on_tool_result(self, event: HookEvent) -> EventResult
```

**Parameters**:
- `event` (`HookEvent`): Tool result event

**Expected Payload**:
```python
{
    "tool_name": str,       # Required
    "success": bool,        # Required
    "duration_ms": int,     # Optional
    "error": str            # Optional (if success=False)
}
```

**Returns**:
- `EventResult`: Result with tool usage statistics

---

### Enum: `EventType`

Claude Code lifecycle event types.

```python
class EventType(str, Enum):
    SESSION_START = "session-start"
    SESSION_END = "session-end"
    PROMPT_SUBMIT = "prompt-submit"
    PRE_TOOL_USE = "pre-tool-use"
    POST_TOOL_USE = "post-tool-use"
    TOOL_RESULT = "tool-result"
    STOP = "stop"
    SUBAGENT_STOP = "subagent-stop"
    PRE_COMPACT = "pre-compact"
    NOTIFICATION = "notification"
```

---

## Settings System API

**Module**: `agentpm.services.claude_integration.settings`

### Class: `SettingsManager`

Multi-layer settings management with precedence.

#### Constructor

```python
SettingsManager(
    db_service: Optional[DatabaseService] = None,
    config_dir: Optional[Path] = None
)
```

**Parameters**:
- `db_service` (`Optional[DatabaseService]`): Database service for project settings
- `config_dir` (`Optional[Path]`): Directory for user config files (default: `~/.aipm/config`)

**Example**:

```python
from agentpm.services.claude_integration.settings import SettingsManager

manager = SettingsManager(db_service=db)
```

---

#### Method: `load_settings`

Load settings with multi-layer precedence.

```python
def load_settings(
    self,
    project_id: Optional[int] = None,
    use_cache: bool = True
) -> ClaudeCodeSettings
```

**Parameters**:
- `project_id` (`Optional[int]`): Project ID for project-specific settings
- `use_cache` (`bool`): Whether to use cached settings

**Returns**:
- `ClaudeCodeSettings`: Loaded settings

**Precedence** (highest to lowest):
1. Session overrides (in-memory)
2. User config file
3. Project database settings
4. System defaults

**Example**:
```python
# Load default settings
settings = manager.load_settings()

# Load project-specific settings
settings = manager.load_settings(project_id=1)

# Force reload (bypass cache)
settings = manager.load_settings(project_id=1, use_cache=False)
```

---

#### Method: `save_settings`

Save settings to appropriate storage.

```python
def save_settings(
    self,
    project_id: Optional[int],
    settings: ClaudeCodeSettings,
    scope: str = "project"
) -> bool
```

**Parameters**:
- `project_id` (`Optional[int]`): Project ID (required for project/session scope)
- `settings` (`ClaudeCodeSettings`): Settings to save
- `scope` (`str`): Storage scope ("project", "user", or "session")

**Returns**:
- `bool`: True if saved successfully

**Raises**:
- `ValueError`: If scope is invalid or requirements not met

**Example**:
```python
# Save to project scope (database)
success = manager.save_settings(
    project_id=1,
    settings=settings,
    scope="project"
)

# Save to user scope (config file)
success = manager.save_settings(
    project_id=None,
    settings=settings,
    scope="user"
)

# Save to session scope (in-memory)
success = manager.save_settings(
    project_id=1,
    settings=settings,
    scope="session"
)
```

---

#### Method: `validate_settings`

Validate settings and return warnings.

```python
def validate_settings(
    self,
    settings: ClaudeCodeSettings
) -> List[str]
```

**Parameters**:
- `settings` (`ClaudeCodeSettings`): Settings to validate

**Returns**:
- `List[str]`: Validation warning messages (empty if all valid)

**Example**:
```python
warnings = manager.validate_settings(settings)

if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"  - {warning}")
```

---

#### Method: `get_setting`

Get specific setting value by dotted key path.

```python
def get_setting(
    self,
    key: str,
    project_id: Optional[int] = None,
    default: Any = None
) -> Any
```

**Parameters**:
- `key` (`str`): Dotted key path (e.g., "hooks.enabled.session_start")
- `project_id` (`Optional[int]`): Project ID
- `default` (`Any`): Default value if not found

**Returns**:
- `Any`: Setting value or default

**Example**:
```python
# Get simple value
enabled = manager.get_setting("plugin_enabled", default=True)

# Get nested value
timeout = manager.get_setting("hooks.timeout_seconds", default=30)

# Get from specific project
timeout = manager.get_setting(
    "hooks.timeout_seconds",
    project_id=1,
    default=30
)
```

---

#### Method: `set_setting`

Set specific setting value by dotted key path.

```python
def set_setting(
    self,
    key: str,
    value: Any,
    project_id: Optional[int] = None,
    scope: str = "session"
) -> bool
```

**Parameters**:
- `key` (`str`): Dotted key path
- `value` (`Any`): Value to set
- `project_id` (`Optional[int]`): Project ID
- `scope` (`str`): Storage scope

**Returns**:
- `bool`: True if set successfully

**Example**:
```python
# Set simple value
manager.set_setting("verbose_logging", True)

# Set nested value
manager.set_setting("hooks.timeout_seconds", 60)

# Set in project scope
manager.set_setting(
    "hooks.enabled.session_start",
    True,
    project_id=1,
    scope="project"
)
```

---

#### Method: `reset_settings`

Reset settings to defaults.

```python
def reset_settings(
    self,
    project_id: Optional[int] = None,
    scope: str = "session"
) -> bool
```

**Parameters**:
- `project_id` (`Optional[int]`): Project ID
- `scope` (`str`): Scope to reset

**Returns**:
- `bool`: True if reset successfully

**Example**:
```python
# Reset session settings
manager.reset_settings(project_id=1, scope="session")

# Reset user settings
manager.reset_settings(scope="user")
```

---

### Class: `ClaudeCodeSettings`

Comprehensive Claude Code integration settings.

#### Constructor

```python
ClaudeCodeSettings(
    plugin_enabled: bool = True,
    verbose_logging: bool = False,
    hooks: HooksSettings = HooksSettings(),
    memory: MemorySettings = MemorySettings(),
    subagents: SubagentSettings = SubagentSettings(),
    performance: PerformanceSettings = PerformanceSettings(),
    project_id: Optional[int] = None,
    custom_settings: Dict[str, Any] = {}
)
```

**Example**:

```python
from agentpm.services.claude_integration.settings import ClaudeCodeSettings

# Use defaults
settings = ClaudeCodeSettings()

# Customize
settings = ClaudeCodeSettings(
    verbose_logging=True,
    project_id=1
)
```

---

#### Method: `get_hook_enabled`

Check if specific hook is enabled.

```python
def get_hook_enabled(self, hook_name: str) -> bool
```

**Parameters**:
- `hook_name` (`str`): Hook event type name

**Returns**:
- `bool`: True if hook is enabled

**Example**:
```python
if settings.get_hook_enabled("session_start"):
    # Execute hook
    pass
```

---

#### Method: `set_hook_enabled`

Enable or disable specific hook.

```python
def set_hook_enabled(self, hook_name: str, enabled: bool) -> None
```

**Parameters**:
- `hook_name` (`str`): Hook event type name
- `enabled` (`bool`): Enable flag

**Example**:
```python
settings.set_hook_enabled("tool_result", True)
```

---

## Subagent System API

**Module**: `agentpm.services.claude_integration.subagents`

### Class: `SubagentInvocationHandler`

Handle subagent invocations from Claude Code.

#### Method: `invoke_subagent_sync`

Invoke subagent synchronously.

```python
def invoke_subagent_sync(
    self,
    subagent_name: str,
    task_description: str,
    context: Dict[str, Any],
    session_id: str,
    correlation_id: str
) -> InvocationResult
```

**Parameters**:
- `subagent_name` (`str`): Subagent name
- `task_description` (`str`): Task description
- `context` (`Dict[str, Any]`): Context data
- `session_id` (`str`): Session identifier
- `correlation_id` (`str`): Request correlation ID

**Returns**:
- `InvocationResult`: Invocation result

**Example**:

```python
from agentpm.services.claude_integration.subagents import get_invocation_handler

handler = get_invocation_handler()

result = handler.invoke_subagent_sync(
    subagent_name="test-implementer",
    task_description="Create tests for UserService",
    context={"service": "UserService"},
    session_id="session-123",
    correlation_id="req-001"
)

if result.success:
    for artifact in result.artifacts:
        print(f"Created: {artifact}")
```

---

### Class: `SubagentRegistry`

Registry of available subagents.

#### Method: `list_subagents`

List all registered subagents.

```python
def list_subagents(self) -> List[SubagentSpec]
```

**Returns**:
- `List[SubagentSpec]`: List of subagent specifications

**Example**:

```python
from agentpm.services.claude_integration.subagents import get_subagent_registry

registry = get_subagent_registry()
subagents = registry.list_subagents()

for spec in subagents:
    print(f"- {spec.name}: {spec.description}")
```

---

#### Method: `get_invocation_guide`

Get invocation guide for all subagents.

```python
def get_invocation_guide(self) -> str
```

**Returns**:
- `str`: Markdown-formatted invocation guide

**Example**:
```python
guide = registry.get_invocation_guide()
print(guide)
```

---

## Checkpointing API

Checkpointing is handled through the plugin `handle()` method with checkpoint-specific inputs.

### Create Checkpoint

```python
result = plugin.handle({
    "action": "checkpoint",
    "session_id": "session-123"
})

checkpoint_id = result["data"]["checkpoint_id"]
```

### Restore Checkpoint

```python
result = plugin.handle({
    "action": "restore",
    "checkpoint_id": "session-123-checkpoint-001",
    "session_id": "session-123"
})
```

### List Checkpoints

```python
result = plugin.handle({
    "action": "list",
    "session_id": "session-123"
})

checkpoints = result["data"]["checkpoints"]
for cp in checkpoints:
    print(f"- {cp['name']}: {cp['timestamp']}")
```

---

## Memory Tools API

Memory operations are handled through the plugin `handle()` method with memory-specific inputs.

### Set Memory Value

```python
result = plugin.handle({
    "scope": "session",
    "action": "set",
    "key": "current_feature",
    "value": "authentication",
    "session_id": "session-123"
})
```

### Get Memory Value

```python
result = plugin.handle({
    "scope": "session",
    "action": "get",
    "key": "current_feature",
    "session_id": "session-123"
})

value = result["data"]["value"]
```

---

## Data Models

### `Integration`

Complete integration data structure.

```python
@dataclass
class Integration:
    name: str
    version: str
    description: str
    created_at: datetime
    updated_at: datetime
    plugins: List[PluginSpec]
    hooks: List[HookSpec]
    subagents: List[SubagentSpec]
    settings: List[SettingSpec]
    slash_commands: List[CommandSpec]
    checkpoints: List[CheckpointSpec]
    memory_tools: List[MemoryToolSpec]
    dependencies: List[str]
    requirements: List[str]
    project_id: Optional[int] = None
```

### `HookEvent`

Event data passed to hook handlers.

```python
@dataclass
class HookEvent:
    event_type: EventType
    payload: Dict[str, Any]
    session_id: str
    correlation_id: str
    timestamp: datetime
```

### `EventResult`

Result from event handler.

```python
@dataclass
class EventResult:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

### `InvocationResult`

Result from subagent invocation.

```python
@dataclass
class InvocationResult:
    success: bool
    message: str
    subagent_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

---

## Error Handling

All API methods follow consistent error handling patterns:

**Success Response**:
```python
{
    "status": "success",
    "message": "Operation completed",
    "data": {...}
}
```

**Error Response**:
```python
{
    "status": "error",
    "message": "Operation failed",
    "error": "Detailed error message"
}
```

**Exceptions**:
- `ValueError`: Invalid parameters or data
- `RuntimeError`: Operation failed at runtime
- `FileNotFoundError`: Required file not found
- `IOError`: File I/O operation failed

**Example Error Handling**:
```python
try:
    integration = orchestrator.create_comprehensive_integration(
        output_dir=Path(".claude"),
        project_id=999  # Non-existent project
    )
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Generation failed: {e}")
```

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-10-21
- **Author**: AIPM Development Team

---

## Related Documentation

- [User Guide](../../guides/user_guide/claude-code-integration.md)
- [Developer Guide](../../guides/developer/claude-code-integration-development.md)
- [Plugin Usage Guide](../../guides/user_guide/claude-code-plugin-usage.md)
- [Hooks Usage Guide](../../guides/user_guide/claude-code-hooks-usage.md)
