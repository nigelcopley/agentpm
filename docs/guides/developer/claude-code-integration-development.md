# Claude Code Integration - Developer Guide

## Overview

This guide covers the architecture, design patterns, and extension points for the APM (Agent Project Manager) Claude Code integration. It's intended for developers who want to extend, customize, or contribute to the integration.

---

## Architecture

The Claude Code integration follows a **three-layer architecture** with four major components:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Commands Layer                       │
│  (agentpm/cli/commands/claude_code.py)                      │
│  • Integration management commands                           │
│  • Settings management commands                              │
│  • User-facing CLI interface                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Layer                          │
│  (agentpm/providers/anthropic/claude_code.py)               │
│  • ClaudeCodeOrchestrator                                    │
│  • Integration generation logic                              │
│  • Component coordination                                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ Plugin Layer │  │  Hooks Engine    │  │ Settings Layer  │
│              │  │                  │  │                 │
│ • Capability │  │ • Event dispatch │  │ • Multi-layer   │
│   routing    │  │ • Handler reg.   │  │   precedence    │
│ • Event      │  │ • Session track  │  │ • Validation    │
│   handling   │  │                  │  │                 │
└──────────────┘  └──────────────────┘  └─────────────────┘
```

### Component Interaction Flow

```
User Command
    │
    ▼
CLI Command Handler
    │
    ▼
ClaudeCodeOrchestrator
    │
    ├──> Plugin System ──> Event Handlers
    │
    ├──> Hooks Engine ──> Database (sessions table)
    │
    ├──> Settings Manager ──> Multi-layer settings
    │
    └──> Generator ──> Claude Code files (.md)
```

---

## Core Components

### 1. ClaudeCodeOrchestrator

**Location**: `agentpm/providers/anthropic/claude_code.py` (to be implemented)

**Responsibility**: Coordinate integration generation, validation, and management.

**Key Methods**:
```python
class ClaudeCodeOrchestrator:
    def create_comprehensive_integration(
        self,
        output_dir: Path,
        project_id: Optional[int] = None,
        integration_name: str = "APM (Agent Project Manager) Claude Code Integration"
    ) -> Integration:
        """Generate complete Claude Code integration."""

    def generate_project_integration(
        self,
        project_id: int,
        output_dir: Path
    ) -> Integration:
        """Generate project-specific integration."""

    def generate_agent_integration(
        self,
        agent_role: str,
        output_dir: Path
    ) -> Integration:
        """Generate agent-specific integration."""

    def validate_integration(
        self,
        integration: Integration
    ) -> ValidationResult:
        """Validate integration completeness."""
```

**Design Pattern**: Facade pattern - provides unified interface to complex subsystems.

### 2. Plugin System

**Location**: `agentpm/services/claude_integration/plugins/claude_code.py`

**Responsibility**: Handle Claude Code events and capabilities.

**Architecture**:
```python
class ClaudeCodePlugin(BaseClaudePlugin):
    """
    Capability-based plugin with routing.

    Capabilities:
    - HOOKS: Lifecycle event handling
    - MEMORY: Context persistence
    - COMMANDS: Slash command execution
    - CHECKPOINTING: State snapshots
    - SUBAGENTS: Subagent orchestration
    """

    def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route input to appropriate capability handler.

        Routing strategy:
        - "type" field → hooks handler
        - "command" field → commands handler
        - "scope" field → memory handler
        - "checkpoint_id" field → checkpointing handler
        - "subagent" field → subagents handler
        """
```

**Design Pattern**: Strategy pattern - capability-based routing with pluggable handlers.

### 3. Hooks Engine

**Location**: `agentpm/services/claude_integration/hooks/claude_code_handlers.py`

**Responsibility**: Track session lifecycle and dispatch events.

**Event Flow**:
```
SESSION_START
    └──> Create session record
    └──> Load previous context
    └──> Return handover data

PROMPT_SUBMIT
    └──> Track prompt in session metadata
    └──> Update prompt count

TOOL_RESULT
    └──> Track tool usage statistics
    └──> Update failure counts

SESSION_END
    └──> Calculate session duration
    └──> Generate session summary
    └──> Create handover document
```

**Design Pattern**: Observer pattern - event-driven architecture with registered handlers.

### 4. Settings Manager

**Location**: `agentpm/services/claude_integration/settings/manager.py`

**Responsibility**: Multi-layer settings management with precedence.

**Settings Hierarchy**:
```
Session Overrides (in-memory, temporary)
    ↓ (overrides)
User Config (~/.aipm/config/claude_code_settings.json)
    ↓ (overrides)
Project Settings (database)
    ↓ (overrides)
System Defaults (Pydantic model defaults)
```

**Design Pattern**: Chain of Responsibility - settings precedence with fallback.

---

## Extending the Integration

### Adding a New Slash Command

**1. Register Command Handler in Plugin**

```python
# agentpm/services/claude_integration/plugins/claude_code.py

def _initialize(self) -> None:
    """Initialize plugin on first use."""
    self._command_handlers = {
        "checkpoint": self._cmd_checkpoint,
        "restore": self._cmd_restore,
        "context": self._cmd_context,
        "subagent": self._cmd_subagent,
        # Add your new command
        "my_command": self._cmd_my_command,
    }
```

**2. Implement Command Handler**

```python
def _cmd_my_command(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle /my_command slash command."""
    # Extract arguments
    param1 = args.get("param1", "default")

    # Perform command logic
    result = do_something(param1)

    # Return result
    return {
        "status": "success",
        "message": f"Command executed with {param1}",
        "data": {"result": result}
    }
```

**3. Test Command**

```python
# tests/services/claude_integration/test_claude_code_plugin.py

def test_my_command(plugin: ClaudeCodePlugin):
    """Test /my_command slash command."""
    result = plugin.handle({
        "command": "my_command",
        "args": {"param1": "test_value"},
        "session_id": "test-session"
    })

    assert result["status"] == "success"
    assert "result" in result["data"]
```

### Adding a New Hook Event Type

**1. Add Event Type to Models**

```python
# agentpm/services/claude_integration/hooks/models.py

class EventType(str, Enum):
    """Claude Code lifecycle event types."""
    SESSION_START = "session-start"
    SESSION_END = "session-end"
    # ... existing events ...
    MY_EVENT = "my-event"  # Add new event
```

**2. Implement Event Handler**

```python
# agentpm/services/claude_integration/hooks/claude_code_handlers.py

class ClaudeCodeHookHandlers:
    def register_all(self) -> None:
        """Register all hook handlers."""
        self.engine.register_handler(EventType.SESSION_START, self.on_session_start)
        # ... existing handlers ...
        self.engine.register_handler(EventType.MY_EVENT, self.on_my_event)

    def on_my_event(self, event: HookEvent) -> EventResult:
        """Handle MY_EVENT event."""
        # Extract payload
        data = event.payload.get("data")

        # Process event
        result = process_event(data)

        # Return result
        return EventResult(
            success=True,
            message=f"MY_EVENT handled",
            data={"result": result}
        )
```

**3. Add Plugin Routing**

```python
# agentpm/services/claude_integration/plugins/claude_code.py

def _handle_hook_event(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle lifecycle hook events."""
    event_type = input_data.get("type")

    # ... existing routing ...

    elif event_type == EventType.MY_EVENT or event_type == "my-event":
        return self._on_my_event(session_id, payload)

def _on_my_event(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle my-event hook."""
    # Process event
    return {
        "status": "success",
        "message": "MY_EVENT handled",
        "data": {}
    }
```

### Creating Custom Memory Generators

**1. Create Memory Generator Class**

```python
# agentpm/services/claude_integration/memory/my_generator.py

from .base import MemoryGenerator

class MyMemoryGenerator(MemoryGenerator):
    """Custom memory generator for specific context."""

    def generate(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate custom memory content.

        Args:
            session_id: Session identifier
            context: Session context data

        Returns:
            Memory content as markdown string
        """
        # Extract relevant data
        work_items = context.get("work_items", [])
        tasks = context.get("tasks", [])

        # Generate memory content
        memory = "# Custom Memory\n\n"
        memory += f"Session: {session_id}\n\n"

        memory += "## Work Items\n"
        for item in work_items:
            memory += f"- {item['name']}\n"

        memory += "\n## Tasks\n"
        for task in tasks:
            memory += f"- {task['objective']}\n"

        return memory
```

**2. Register Generator**

```python
# agentpm/services/claude_integration/memory/__init__.py

from .my_generator import MyMemoryGenerator

def get_memory_generators():
    """Get all registered memory generators."""
    return {
        "default": DefaultMemoryGenerator(),
        "my_generator": MyMemoryGenerator(),
    }
```

**3. Use Custom Generator**

```python
# In your code
generators = get_memory_generators()
my_gen = generators["my_generator"]
memory_content = my_gen.generate(session_id, context)
```

### Extending Settings

**1. Add New Settings Model**

```python
# agentpm/services/claude_integration/settings/models.py

class MyCustomSettings(BaseModel):
    """Custom settings for new feature."""

    feature_enabled: bool = Field(
        default=True,
        description="Enable custom feature"
    )

    feature_timeout: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Feature timeout in seconds"
    )
```

**2. Add to ClaudeCodeSettings**

```python
class ClaudeCodeSettings(BaseModel):
    """Comprehensive Claude Code integration settings."""

    # ... existing settings ...

    my_custom: MyCustomSettings = Field(
        default_factory=MyCustomSettings,
        description="Custom feature configuration"
    )
```

**3. Add CLI Command for Setting**

```python
# agentpm/cli/commands/claude_code.py

@settings.command(name='set-custom')
@click.option('--feature-enabled/--no-feature-enabled', default=True)
@click.option('--feature-timeout', type=int, default=60)
@click.pass_context
def settings_set_custom(ctx, feature_enabled: bool, feature_timeout: int):
    """Set custom feature settings."""
    manager = SettingsManager(db_service)

    # Load current settings
    settings = manager.load_settings()

    # Update custom settings
    settings.my_custom.feature_enabled = feature_enabled
    settings.my_custom.feature_timeout = feature_timeout

    # Save settings
    manager.save_settings(settings=settings, scope="session")
```

---

## Testing Guide

### Unit Testing

**Test Plugin Event Handling**:

```python
# tests/services/claude_integration/test_claude_code_plugin.py

import pytest
from agentpm.services.claude_integration.plugins.claude_code import ClaudeCodePlugin


@pytest.fixture
def plugin():
    """Create plugin instance for testing."""
    return ClaudeCodePlugin()


def test_session_start_event(plugin):
    """Test session-start event handling."""
    result = plugin.handle({
        "type": "session-start",
        "payload": {"user": "test_user"},
        "session_id": "test-session-123",
        "correlation_id": "req-001"
    })

    assert result["status"] == "success"
    assert "session_id" in result["data"]

    # Verify session context created
    context = plugin.get_session_context("test-session-123")
    assert context is not None
    assert context["session_id"] == "test-session-123"


def test_command_execution(plugin):
    """Test slash command execution."""
    result = plugin.handle({
        "command": "checkpoint",
        "args": {"name": "test-checkpoint"},
        "session_id": "test-session"
    })

    assert result["status"] == "success"
    assert "checkpoint_id" in result["data"]


def test_memory_operations(plugin):
    """Test memory set/get operations."""
    # Set value
    set_result = plugin.handle({
        "scope": "session",
        "action": "set",
        "key": "test_key",
        "value": "test_value",
        "session_id": "test-session"
    })

    assert set_result["status"] == "success"

    # Get value
    get_result = plugin.handle({
        "scope": "session",
        "action": "get",
        "key": "test_key",
        "session_id": "test-session"
    })

    assert get_result["status"] == "success"
    assert get_result["data"]["value"] == "test_value"
```

**Test Settings Manager**:

```python
# tests/services/claude_integration/test_settings_manager.py

import pytest
from agentpm.services.claude_integration.settings import SettingsManager, ClaudeCodeSettings


@pytest.fixture
def manager(tmp_path):
    """Create settings manager with temp config dir."""
    return SettingsManager(config_dir=tmp_path / "config")


def test_load_defaults(manager):
    """Test loading default settings."""
    settings = manager.load_settings()

    assert settings.plugin_enabled is True
    assert settings.hooks.timeout_seconds == 30
    assert settings.memory.retention_days == 90


def test_settings_precedence(manager, tmp_path):
    """Test settings precedence layers."""
    # Save user config
    user_settings = ClaudeCodeSettings(verbose_logging=True)
    manager.save_settings(settings=user_settings, scope="user")

    # Save session override
    session_settings = ClaudeCodeSettings(
        verbose_logging=False,
        project_id=1
    )
    manager.save_settings(
        project_id=1,
        settings=session_settings,
        scope="session"
    )

    # Load settings - session should override user
    loaded = manager.load_settings(project_id=1)
    assert loaded.verbose_logging is False  # Session override
    assert loaded.project_id == 1


def test_settings_validation(manager):
    """Test settings validation."""
    # Create settings with warnings
    settings = ClaudeCodeSettings(
        hooks=HooksSettings(timeout_seconds=3),  # Too low
        memory=MemorySettings(retention_days=5)  # Too low
    )

    warnings = manager.validate_settings(settings)

    assert len(warnings) >= 2
    assert any("timeout" in w.lower() for w in warnings)
    assert any("retention" in w.lower() for w in warnings)
```

### Integration Testing

**Test Complete Integration Generation**:

```python
# tests/integration/test_claude_code_integration.py

import pytest
from pathlib import Path
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator


@pytest.fixture
def orchestrator(db_service):
    """Create orchestrator instance."""
    return ClaudeCodeOrchestrator(db_service)


def test_generate_comprehensive_integration(orchestrator, tmp_path):
    """Test comprehensive integration generation."""
    integration = orchestrator.create_comprehensive_integration(
        output_dir=tmp_path,
        integration_name="Test Integration"
    )

    # Verify integration structure
    assert integration.name == "Test Integration"
    assert len(integration.plugins) > 0
    assert len(integration.hooks) > 0
    assert len(integration.subagents) > 0

    # Verify files created
    assert (tmp_path / "integration.json").exists()


def test_generate_project_integration(orchestrator, tmp_path, db_service):
    """Test project-specific integration generation."""
    # Create test project
    project = create_test_project(db_service)

    integration = orchestrator.generate_project_integration(
        project_id=project.id,
        output_dir=tmp_path
    )

    # Verify project-specific integration
    assert integration.project_id == project.id
    assert len(integration.plugins) > 0


def test_validate_integration(orchestrator):
    """Test integration validation."""
    # Generate integration
    integration = orchestrator.create_comprehensive_integration(
        output_dir=Path("/tmp"),
        integration_name="Test"
    )

    # Validate
    validation = orchestrator.validate_integration(integration)

    assert validation["valid"] is True
    assert "component_counts" in validation
```

### End-to-End Testing

**Test CLI Commands**:

```python
# tests/e2e/test_claude_code_cli.py

from click.testing import CliRunner
from agentpm.cli.main import cli


def test_generate_command(tmp_path):
    """Test apm claude-code generate command."""
    runner = CliRunner()

    result = runner.invoke(cli, [
        'claude-code',
        'generate',
        '-o', str(tmp_path),
        '-n', 'Test Integration'
    ])

    assert result.exit_code == 0
    assert "Integration generated successfully" in result.output
    assert (tmp_path / "integration.json").exists()


def test_settings_commands():
    """Test settings management commands."""
    runner = CliRunner()

    # Show settings
    result = runner.invoke(cli, ['claude-code', 'settings', 'show'])
    assert result.exit_code == 0
    assert "Plugin Enabled" in result.output

    # Set setting
    result = runner.invoke(cli, [
        'claude-code', 'settings', 'set',
        '-k', 'verbose_logging',
        '-v', 'true',
        '-t', 'bool'
    ])
    assert result.exit_code == 0
    assert "Setting 'verbose_logging' set to 'True'" in result.output
```

---

## Contributing

### Development Setup

**1. Clone Repository**:
```bash
git clone https://github.com/yourusername/aipm-v2.git
cd aipm-v2
```

**2. Install Dependencies**:
```bash
pip install -e ".[dev]"
```

**3. Run Tests**:
```bash
# All tests
pytest

# Specific test file
pytest tests/services/claude_integration/test_claude_code_plugin.py

# With coverage
pytest --cov=agentpm.services.claude_integration \
       --cov-report=term-missing \
       --cov-report=html
```

**4. Code Quality**:
```bash
# Format code
black agentpm/

# Lint
pylint agentpm/services/claude_integration/

# Type check
mypy agentpm/services/claude_integration/
```

### Contribution Guidelines

**1. Code Style**:
- Follow PEP 8
- Use Black for formatting
- Add type hints
- Write docstrings (Google style)

**2. Testing**:
- Unit test coverage ≥90%
- Integration tests for major features
- E2E tests for CLI commands

**3. Documentation**:
- Update user guide for user-facing changes
- Update developer guide for API changes
- Add inline comments for complex logic

**4. Pull Request Process**:
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with tests
3. Run tests and linters
4. Update documentation
5. Create pull request with description

### Common Development Tasks

**Add New CLI Command**:
```python
# agentpm/cli/commands/claude_code.py

@claude_code.command()
@click.option('--param', '-p', required=True, help='Parameter description')
@click.pass_context
def my_command(ctx, param: str):
    """Command description."""
    console = ctx.obj['console']
    db_service = ctx.obj['db_service']

    try:
        # Command logic
        result = do_something(param)

        console.print(f"[green]✓[/green] Success: {result}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise click.Abort()
```

**Add New Setting**:
```python
# agentpm/services/claude_integration/settings/models.py

class MySettings(BaseModel):
    """My custom settings."""
    my_param: bool = Field(default=True, description="My parameter")

class ClaudeCodeSettings(BaseModel):
    # ... existing ...
    my_settings: MySettings = Field(default_factory=MySettings)
```

**Add New Event Type**:
```python
# 1. Add to EventType enum
class EventType(str, Enum):
    MY_EVENT = "my-event"

# 2. Add handler in ClaudeCodeHookHandlers
def on_my_event(self, event: HookEvent) -> EventResult:
    """Handle my-event."""
    # Process event
    return EventResult(success=True, message="Handled")

# 3. Register handler
self.engine.register_handler(EventType.MY_EVENT, self.on_my_event)
```

---

## Architecture Decisions

### Why Capability-Based Plugin Routing?

**Decision**: Use capability-based routing instead of event-type-only routing.

**Rationale**:
- **Flexibility**: Easy to add new capabilities without changing core plugin
- **Separation of Concerns**: Each capability has isolated handler
- **Extensibility**: Third-party developers can add custom capabilities
- **Testability**: Each capability handler can be tested independently

**Trade-offs**:
- More complex routing logic
- Slightly higher overhead for routing decision

### Why Multi-Layer Settings?

**Decision**: Implement four-layer settings hierarchy (session → user → project → defaults).

**Rationale**:
- **Flexibility**: Different scopes for different use cases
- **Precedence**: Clear precedence rules for conflict resolution
- **Persistence**: User and project settings persist across sessions
- **Testing**: Session scope allows temporary testing without affecting persistent settings

**Trade-offs**:
- More complex settings management
- Potential confusion about which setting takes precedence

### Why Hooks Engine as Separate Component?

**Decision**: Separate hooks engine from plugin system.

**Rationale**:
- **Reusability**: Hooks engine can be used by other components
- **Separation of Concerns**: Event dispatch separate from event handling
- **Testability**: Hooks engine can be tested independently
- **Future-Proofing**: Easier to add new event sources (beyond Claude Code)

**Trade-offs**:
- Additional layer of abstraction
- More files to maintain

---

## Related Documentation

- [User Guide](../user_guide/claude-code-integration.md) - User-facing documentation
- [API Reference](../../reference/api/claude-code-integration-api.md) - Complete API documentation
- [Plugin Architecture](../../architecture/design/cursor-provider-architecture.md) - Plugin system design
- [Hooks Design](../../architecture/design/claude-integration-consolidation-design.md) - Hooks engine design

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-10-21
- **Author**: AIPM Development Team
