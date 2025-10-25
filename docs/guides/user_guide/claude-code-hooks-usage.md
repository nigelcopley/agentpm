# Claude Code Hooks Usage Guide

## Overview

The Claude Code Hooks System provides event-driven session tracking for Claude Code integrations with APM (Agent Project Manager). It automatically captures session lifecycle events, tool usage, and context for seamless handover between sessions.

## Features

- **Session Lifecycle Tracking**: Automatic start/end tracking with duration calculation
- **Context Handover**: Load previous session context on startup
- **Prompt History**: Track user prompts for session analysis
- **Tool Analytics**: Monitor tool usage patterns and failures
- **Session Summaries**: Auto-generate summaries for documentation

## Quick Start

### 1. Initialize Handlers

```python
from agentpm.core.database.service import DatabaseService
from agentpm.services.claude_integration.hooks import ClaudeCodeHookHandlers

# Initialize database and handlers
db = DatabaseService("path/to/aipm.db")
handlers = ClaudeCodeHookHandlers(db)

# Register all handlers (do this once at app startup)
handlers.register_all()
```

### 2. Dispatch Events

Events are automatically dispatched by the hooks engine:

```python
from agentpm.services.claude_integration.hooks import get_hooks_engine, EventType

engine = get_hooks_engine()

# Session start
result = engine.dispatch_event(
    event_type=EventType.SESSION_START,
    payload={"project_id": 1, "tool_version": "1.5.0"},
    session_id="session-abc-123",
    correlation_id="req-001"
)

# Session end
result = engine.dispatch_event(
    event_type=EventType.SESSION_END,
    payload={"exit_reason": "User closed app"},
    session_id="session-abc-123",
    correlation_id="req-002"
)
```

## Event Types

### SESSION_START

**When**: New Claude Code session begins
**Payload**:
- `project_id` (required): Project ID
- `tool_version` (optional): Claude Code version
- `developer_name` (optional): Developer name
- `developer_email` (optional): Developer email

**Returns**:
- `session`: Created session details
- `previous_context`: Handover data from last session
  - `work_items`: Work items from previous session
  - `tasks`: Completed tasks
  - `summary`: Previous session summary

**Example**:
```python
result = engine.dispatch_event(
    event_type=EventType.SESSION_START,
    payload={
        "project_id": 1,
        "tool_version": "1.5.0",
        "developer_name": "Jane Doe",
        "developer_email": "jane@example.com"
    },
    session_id="session-123",
    correlation_id="req-001"
)

# Access previous context
if result.data["previous_context"]["available"]:
    work_items = result.data["previous_context"]["work_items"]
    print(f"Continue from work items: {work_items}")
```

### SESSION_END

**When**: Session terminates
**Payload**:
- `exit_reason` (optional): Why session ended
- `summary` (optional): User-provided summary

**Returns**:
- `session`: Updated session with duration
- `summary`: Generated session summary
- `handover`: Handover document for next session
  - `work_completed`: Work items and tasks completed
  - `decisions`: Decisions made during session
  - `tool_usage`: Tool usage statistics

**Example**:
```python
result = engine.dispatch_event(
    event_type=EventType.SESSION_END,
    payload={
        "exit_reason": "Complete",
        "summary": "Implemented authentication feature"
    },
    session_id="session-123",
    correlation_id="req-002"
)

# Access handover for documentation
handover = result.data["handover"]
print(f"Session duration: {handover['duration_minutes']} min")
print(f"Work completed: {handover['work_completed']}")
```

### PROMPT_SUBMIT

**When**: User submits a prompt
**Payload**:
- `prompt` (required): User prompt text
- `prompt_number` (optional): Sequence number

**Returns**:
- `prompt_count`: Total prompts in session

**Example**:
```python
result = engine.dispatch_event(
    event_type=EventType.PROMPT_SUBMIT,
    payload={
        "prompt": "Implement user authentication",
        "prompt_number": 5
    },
    session_id="session-123",
    correlation_id="req-003"
)

print(f"Prompts so far: {result.data['prompt_count']}")
```

**Note**: Prompts are truncated to 200 characters for storage efficiency.

### TOOL_RESULT

**When**: Tool execution completes
**Payload**:
- `tool_name` (required): Name of tool (e.g., "Bash", "Read", "Write")
- `success` (required): Boolean indicating success/failure
- `duration_ms` (optional): Execution duration
- `error` (optional): Error message if failed

**Returns**:
- `tool_usage`: Updated tool usage statistics
  - `count`: Total executions
  - `failures`: Failed executions

**Example**:
```python
result = engine.dispatch_event(
    event_type=EventType.TOOL_RESULT,
    payload={
        "tool_name": "Bash",
        "success": True,
        "duration_ms": 234
    },
    session_id="session-123",
    correlation_id="req-004"
)

# Check tool usage
usage = result.data["tool_usage"]["Bash"]
print(f"Bash: {usage['count']} calls, {usage['failures']} failures")
```

### PRE_TOOL_USE / POST_TOOL_USE

**When**: Before/after tool execution
**Payload**:
- `tool_name` (required): Tool name
- `tool_input` (optional): Tool input parameters
- `result` (optional): Tool result (POST only)

**Returns**: Acknowledgment message

**Example**:
```python
# Before tool execution
engine.dispatch_event(
    event_type=EventType.PRE_TOOL_USE,
    payload={"tool_name": "Bash"},
    session_id="session-123",
    correlation_id="req-005"
)

# After tool execution
engine.dispatch_event(
    event_type=EventType.POST_TOOL_USE,
    payload={"tool_name": "Bash", "result": {...}},
    session_id="session-123",
    correlation_id="req-006"
)
```

## Integration Patterns

### Pattern 1: Automatic Session Tracking

Let hooks handle session lifecycle automatically:

```python
# At app startup
handlers = ClaudeCodeHookHandlers(db)
handlers.register_all()

# Events auto-dispatched by Claude Code
# Session data automatically persisted to database
```

### Pattern 2: Manual Context Loading

Explicitly load and use previous context:

```python
# On session start
result = engine.dispatch_event(
    event_type=EventType.SESSION_START,
    payload={"project_id": 1},
    session_id=new_session_id,
    correlation_id=correlation_id
)

# Use previous context
prev_context = result.data["previous_context"]
if prev_context["available"]:
    display_handover_info(prev_context)
    recommend_next_actions(prev_context["work_items"])
```

### Pattern 3: Session Analytics

Analyze tool usage and session patterns:

```python
# On session end
result = engine.dispatch_event(
    event_type=EventType.SESSION_END,
    payload={},
    session_id=session_id,
    correlation_id=correlation_id
)

# Analyze tool usage
handover = result.data["handover"]
for tool, stats in handover["tool_usage"].items():
    if stats["failures"] > 0:
        failure_rate = stats["failures"] / stats["count"]
        print(f"⚠️ {tool}: {failure_rate:.1%} failure rate")
```

## Database Schema

Session data is stored in the `sessions` table:

```sql
-- Session record
SELECT
    session_id,
    project_id,
    start_time,
    end_time,
    duration_minutes,
    metadata  -- JSON with prompts, tool_usage, etc.
FROM sessions
WHERE session_id = 'session-123';

-- Query metadata
SELECT
    json_extract(metadata, '$.tool_specific.prompts') as prompts,
    json_extract(metadata, '$.tool_specific.tool_usage') as tool_usage
FROM sessions;
```

## Advanced Usage

### Custom Event Handlers

Add custom logic to existing handlers:

```python
class CustomHandlers(ClaudeCodeHookHandlers):
    def on_session_start(self, event):
        result = super().on_session_start(event)

        # Custom logic
        notify_team(f"Session started: {event.session_id}")

        return result
```

### Conditional Event Dispatch

Only dispatch events when needed:

```python
engine = get_hooks_engine()

# Disable during tests
engine.disable()

# Enable for production
engine.enable()

# Check if enabled
if engine.is_enabled():
    engine.dispatch_event(...)
```

### Error Handling

Handle event dispatch errors gracefully:

```python
result = engine.dispatch_event(
    event_type=EventType.SESSION_START,
    payload={"project_id": 1},
    session_id=session_id,
    correlation_id=correlation_id
)

if not result.success:
    logger.error(f"Event failed: {result.message}")
    for error in result.errors:
        logger.error(f"  - {error}")
```

## Troubleshooting

### Issue: No previous context available

**Cause**: No previous sessions exist or sessions table empty

**Solution**:
```python
result = engine.dispatch_event(...)

if not result.data["previous_context"]["available"]:
    logger.info("First session for this project")
    # Show onboarding info
```

### Issue: Tool usage not tracked

**Cause**: TOOL_RESULT events not dispatched or no active session

**Solution**:
1. Ensure session started with SESSION_START
2. Verify TOOL_RESULT payloads include `tool_name` and `success`
3. Check session is active: `apm sessions list --active`

### Issue: Prompts truncated

**Expected Behavior**: Prompts > 200 chars truncated for storage

**Workaround**:
- Truncation is intentional (database optimization)
- Full prompts available in Claude Code UI
- Summaries capture intent, not full text

## Best Practices

1. **Always register handlers at app startup**
   ```python
   handlers.register_all()  # Once per app lifecycle
   ```

2. **Use correlation IDs for tracing**
   ```python
   correlation_id = f"req-{uuid.uuid4()}"
   # Use same ID across related events
   ```

3. **Provide exit reasons on session end**
   ```python
   engine.dispatch_event(
       event_type=EventType.SESSION_END,
       payload={"exit_reason": "User completed work"},
       ...
   )
   ```

4. **Check previous context availability**
   ```python
   if prev_context["available"]:
       # Use handover data
   else:
       # First session - show onboarding
   ```

5. **Monitor tool failure rates**
   ```python
   tool_usage = handover["tool_usage"]
   for tool, stats in tool_usage.items():
       if stats["failures"] / stats["count"] > 0.1:
           alert_team(f"{tool} failing frequently")
   ```

## Related Documentation

- [Hooks Engine API Reference](../../reference/api/hooks-engine.md)
- [Session Tracking Guide](./session-tracking.md)
- [Claude Code Integration](./claude-code-integration.md)
- [Event Models Reference](../../reference/api/event-models.md)

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-10-21
- **Author**: AIPM Development Team
