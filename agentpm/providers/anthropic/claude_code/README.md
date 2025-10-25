# Claude Code Comprehensive Integration

This module provides comprehensive integration between APM (Agent Project Manager) and Claude Code, enabling seamless interaction with all Claude Code features including plugins, hooks, subagents, settings, slash commands, checkpointing, and memory tools.

## Overview

The Claude Code integration transforms APM (Agent Project Manager) into a powerful Claude Code extension that provides:

- **Plugin System**: Create and manage Claude Code plugins for APM (Agent Project Manager) workflows
- **Hooks System**: Define custom event handlers for Claude Code operations
- **Subagents**: Represent APM (Agent Project Manager) agents as Claude Code subagents
- **Settings Management**: Configure Claude Code behavior through APM (Agent Project Manager) settings
- **Slash Commands**: Add custom CLI commands to Claude Code
- **Checkpointing**: Save and restore Claude Code state at key milestones
- **Memory Tools**: Persistent memory storage for APM (Agent Project Manager) data
- **Orchestration**: Unified management of all Claude Code components

## Architecture

### Core Components

```
claude_code/
├── models.py              # Pydantic models for all Claude Code components
├── orchestrator.py        # Unified orchestrator for all integrations
├── plugins.py            # Plugin system management
├── hooks.py              # Hooks system management
├── subagents.py          # Subagents system management
├── settings.py           # Settings system management
├── slash_commands.py     # Slash commands management
├── checkpointing.py      # Checkpointing system management
├── memory_tool.py        # Memory tool management
└── README.md            # This documentation
```

### Integration Flow

1. **APM (Agent Project Manager) Data** → **Claude Code Components** → **Claude Code Configuration**
2. **Claude Code Events** → **APM (Agent Project Manager) Hooks** → **APM (Agent Project Manager) Actions**
3. **APM (Agent Project Manager) Agents** → **Claude Code Subagents** → **Claude Code Execution**

## Features

### 1. Plugin System

Create Claude Code plugins that extend APM (Agent Project Manager) functionality:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodePluginManager

# Create plugin manager
plugin_manager = ClaudeCodePluginManager(db_service)

# Generate APM (Agent Project Manager) plugins
plugins = plugin_manager.create_aipm_plugins(output_dir, project_id=1)

# Create specific plugin types
core_plugins = plugin_manager.create_core_plugins(output_dir)
workflow_plugins = plugin_manager.create_workflow_plugins(output_dir, project_id=1)
agent_plugins = plugin_manager.create_agent_plugins(output_dir, agent_role="senior-agent")
```

**Plugin Types:**
- **Core Plugins**: Essential APM (Agent Project Manager) functionality
- **Workflow Plugins**: Work item and task management
- **Agent Plugins**: Agent-specific capabilities
- **Framework Plugins**: Technology-specific integrations

### 2. Hooks System

Define custom event handlers for Claude Code operations:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeHookManager

# Create hook manager
hook_manager = ClaudeCodeHookManager(db_service)

# Generate APM (Agent Project Manager) hooks
hooks = hook_manager.create_aipm_hooks(output_dir, project_id=1)

# Create specific hook types
workflow_hooks = hook_manager.create_workflow_hooks(output_dir, project_id=1)
quality_hooks = hook_manager.create_quality_hooks(output_dir)
context_hooks = hook_manager.create_context_hooks(output_dir)
```

**Hook Events:**
- **PreToolUse**: Before tool execution
- **PostToolUse**: After tool execution
- **SessionStart**: Session initialization
- **SessionEnd**: Session cleanup
- **FileOpen**: File access events
- **FileSave**: File modification events

### 3. Subagents System

Represent APM (Agent Project Manager) agents as Claude Code subagents:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeSubagentManager

# Create subagent manager
subagent_manager = ClaudeCodeSubagentManager(db_service)

# Generate APM (Agent Project Manager) subagents
subagents = subagent_manager.create_aipm_subagents(output_dir, project_id=1)

# Create specific subagent types
workflow_subagents = subagent_manager.create_workflow_subagents(output_dir, project_id=1)
specialized_subagents = subagent_manager.create_specialized_subagents(output_dir)
quality_subagents = subagent_manager.create_quality_subagents(output_dir)
```

**Subagent Capabilities:**
- **Code Generation**: Generate code following APM (Agent Project Manager) patterns
- **Code Review**: Review code against APM (Agent Project Manager) standards
- **Testing**: Create and run tests
- **Documentation**: Generate documentation
- **Debugging**: Debug issues with APM (Agent Project Manager) context
- **Refactoring**: Refactor code following APM (Agent Project Manager) patterns

### 4. Settings Management

Configure Claude Code behavior through APM (Agent Project Manager) settings:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeSettingsManager

# Create settings manager
settings_manager = ClaudeCodeSettingsManager(db_service)

# Generate APM (Agent Project Manager) settings
settings = settings_manager.create_aipm_settings(output_dir, project_id=1)

# Create specific setting types
workflow_settings = settings_manager.create_workflow_settings(output_dir, project_id=1)
quality_settings = settings_manager.create_quality_settings(output_dir)
context_settings = settings_manager.create_context_settings(output_dir)
```

**Setting Types:**
- **Workflow Settings**: Work item and task configuration
- **Quality Settings**: Quality gates and standards
- **Context Settings**: Context assembly configuration
- **Agent Settings**: Agent behavior configuration

### 5. Slash Commands

Add custom CLI commands to Claude Code:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeSlashCommandManager

# Create slash command manager
slash_command_manager = ClaudeCodeSlashCommandManager(db_service)

# Generate APM (Agent Project Manager) slash commands
commands = slash_command_manager.create_aipm_slash_commands(output_dir, project_id=1)

# Create specific command types
workflow_commands = slash_command_manager.create_workflow_commands(output_dir, project_id=1)
quality_commands = slash_command_manager.create_quality_commands(output_dir)
context_commands = slash_command_manager.create_context_commands(output_dir)
```

**Command Examples:**
- `/aipm-status`: Show APM (Agent Project Manager) project status
- `/aipm-context`: Get current context
- `/aipm-work-item`: Create or manage work items
- `/aipm-task`: Create or manage tasks
- `/aipm-learnings`: Record or retrieve learnings

### 6. Checkpointing

Save and restore Claude Code state at key milestones:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeCheckpointingManager

# Create checkpointing manager
checkpointing_manager = ClaudeCodeCheckpointingManager(db_service)

# Generate APM (Agent Project Manager) checkpoints
checkpoints = checkpointing_manager.create_aipm_checkpoints(output_dir, project_id=1)

# Create specific checkpoint types
session_checkpoints = checkpointing_manager.create_session_checkpoints(output_dir)
workflow_checkpoints = checkpointing_manager.create_workflow_checkpoints(output_dir, project_id=1)
milestone_checkpoints = checkpointing_manager.create_milestone_checkpoints(output_dir)
```

**Checkpoint Types:**
- **Session Checkpoints**: Save session state
- **Workflow Checkpoints**: Save workflow progress
- **Milestone Checkpoints**: Save key achievements
- **Quality Checkpoints**: Save quality gate states

### 7. Memory Tools

Persistent memory storage for APM (Agent Project Manager) data:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeMemoryToolManager

# Create memory tool manager
memory_tool_manager = ClaudeCodeMemoryToolManager(db_service)

# Generate APM (Agent Project Manager) memory configurations
memory_configs = memory_tool_manager.create_aipm_memory_configs(output_dir, project_id=1)

# Store and retrieve memory
memory_tool_manager.store_memory("key", {"data": "value"}, MemoryType.PERSISTENT, "category")
data = memory_tool_manager.retrieve_memory("key")

# Search memory
results = memory_tool_manager.search_memory("query", category="category")
```

**Memory Types:**
- **Decision Memory**: Store decisions with evidence
- **Learning Memory**: Store learnings and insights
- **Pattern Memory**: Store reusable patterns
- **Context Memory**: Store context information
- **Workflow Memory**: Store workflow execution data

### 8. Orchestration

Unified management of all Claude Code components:

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator

# Create orchestrator
orchestrator = ClaudeCodeOrchestrator(db_service)

# Generate comprehensive integration
integration = orchestrator.create_comprehensive_integration(
    output_dir=output_dir,
    project_id=1,
    integration_name="APM (Agent Project Manager) Integration"
)

# Generate project-specific integration
project_integration = orchestrator.generate_project_integration(project_id=1, output_dir=output_dir)

# Generate agent-specific integration
agent_integration = orchestrator.generate_agent_integration(agent_role="senior-agent", output_dir=output_dir)

# Validate integration
validation_results = orchestrator.validate_integration(integration)

# Export/import integration
orchestrator.export_integration(integration, output_path, "json")
imported_integration = orchestrator.import_integration(input_path)
```

## CLI Commands

The integration provides comprehensive CLI commands for management:

```bash
# Generate comprehensive integration
apm claude-code generate --output-dir ./claude --project-id 1

# Generate project-specific integration
apm claude-code generate-project --project-id 1 --output-dir ./claude

# Generate agent-specific integration
apm claude-code generate-agent --agent-role senior-agent --output-dir ./claude

# Validate integration
apm claude-code validate --integration-name "APM (Agent Project Manager) Integration"

# List integrations
apm claude-code list-integrations

# Show integration details
apm claude-code show --integration-name "APM (Agent Project Manager) Integration"

# Export integration
apm claude-code export --integration-name "APM (Agent Project Manager) Integration" --output-file integration.json

# Import integration
apm claude-code import-integration --input-file integration.json

# Show integration statistics
apm claude-code stats

# Clear integration cache
apm claude-code clear-cache
```

## Configuration

### Integration Configuration

The integration can be configured through various settings:

```python
# Integration settings
integration_config = {
    "name": "APM (Agent Project Manager) Claude Code Integration",
    "version": "1.0.0",
    "dependencies": ["agentpm", "claude-code", "anthropic"],
    "requirements": ["python>=3.8", "pydantic>=2.0.0"],
    "permissions": ["read_project_files", "write_claude_config"]
}
```

### Component Configuration

Each component type can be configured independently:

```python
# Plugin configuration
plugin_config = {
    "enabled": True,
    "auto_load": True,
    "dependencies": ["agentpm.core"],
    "permissions": ["read_files", "write_files"]
}

# Hook configuration
hook_config = {
    "enabled": True,
    "priority": 100,
    "async_execution": False,
    "timeout": 30
}

# Subagent configuration
subagent_config = {
    "enabled": True,
    "auto_invoke": False,
    "max_concurrent": 1,
    "capabilities": ["code_generation", "code_review"]
}
```

## Usage Examples

### Basic Integration

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator
from agentpm.core.database.service import DatabaseService

# Initialize
db_service = DatabaseService("/path/to/database")
orchestrator = ClaudeCodeOrchestrator(db_service)

# Generate integration
integration = orchestrator.create_comprehensive_integration(
    output_dir=Path("./claude"),
    project_id=1
)

print(f"Generated {len(integration.plugins)} plugins")
print(f"Generated {len(integration.hooks)} hooks")
print(f"Generated {len(integration.subagents)} subagents")
```

### Project-Specific Integration

```python
# Generate integration for specific project
project_integration = orchestrator.generate_project_integration(
    project_id=123,
    output_dir=Path("./claude/project-123")
)

# Validate integration
validation_results = orchestrator.validate_integration(project_integration)
if validation_results["valid"]:
    print("Integration is valid!")
else:
    print(f"Validation errors: {validation_results['errors']}")
```

### Agent-Specific Integration

```python
# Generate integration for specific agent
agent_integration = orchestrator.generate_agent_integration(
    agent_role="senior-agent",
    output_dir=Path("./claude/senior-agent")
)

# Export integration
orchestrator.export_integration(
    agent_integration,
    Path("./senior-agent-integration.json"),
    "json"
)
```

### Memory Management

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeMemoryToolManager

# Initialize memory manager
memory_manager = ClaudeCodeMemoryToolManager(db_service)

# Store decision
memory_manager.store_memory(
    "decision-001",
    {
        "decision": "Use Django for web framework",
        "evidence": "Team expertise, rapid development",
        "business_value": "Faster time to market",
        "confidence_score": 0.85
    },
    MemoryType.PERSISTENT,
    "decision"
)

# Retrieve decision
decision = memory_manager.retrieve_memory("decision-001")
print(f"Decision: {decision['decision']}")

# Search decisions
results = memory_manager.search_memory("Django", category="decision")
print(f"Found {len(results)} related decisions")
```

### Checkpointing

```python
from agentpm.providers.anthropic.claude_code import ClaudeCodeCheckpointingManager

# Initialize checkpointing manager
checkpointing_manager = ClaudeCodeCheckpointingManager(db_service)

# Create checkpoint
checkpointing_manager.create_checkpoint(
    "workflow-milestone-1",
    {
        "work_item_id": 123,
        "status": "in_progress",
        "tasks_completed": 3,
        "quality_gates_passed": 2
    },
    CheckpointType.MILESTONE
)

# Restore checkpoint
checkpoint_data = checkpointing_manager.restore_checkpoint("workflow-milestone-1")
if checkpoint_data:
    print(f"Restored workflow state: {checkpoint_data['status']}")
```

## Testing

The integration includes comprehensive test coverage:

```bash
# Run all Claude Code integration tests
python -m pytest tests/providers/test_claude_code_integration.py -v

# Run specific component tests
python -m pytest tests/providers/test_claude_code_integration.py::TestClaudeCodeOrchestrator -v
python -m pytest tests/providers/test_claude_code_integration.py::TestClaudeCodePluginManager -v
python -m pytest tests/providers/test_claude_code_integration.py::TestClaudeCodeHookManager -v
```

## Best Practices

### 1. Integration Design

- **Modular Components**: Design components to be independent and reusable
- **Clear Interfaces**: Define clear interfaces between APM (Agent Project Manager) and Claude Code
- **Error Handling**: Implement comprehensive error handling and recovery
- **Validation**: Validate all configurations before deployment

### 2. Performance

- **Lazy Loading**: Load components only when needed
- **Caching**: Cache frequently accessed data
- **Async Operations**: Use async operations for long-running tasks
- **Resource Management**: Properly manage resources and cleanup

### 3. Security

- **Input Validation**: Validate all inputs from Claude Code
- **Output Sanitization**: Sanitize all outputs to APM (Agent Project Manager)
- **Access Control**: Implement proper access control for components
- **Audit Logging**: Log all operations for audit purposes

### 4. Maintenance

- **Versioning**: Use semantic versioning for all components
- **Documentation**: Keep documentation up to date
- **Testing**: Maintain comprehensive test coverage
- **Monitoring**: Monitor component health and performance

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Configuration Errors**: Validate configuration files
3. **Permission Errors**: Check file and directory permissions
4. **Memory Issues**: Monitor memory usage and cleanup

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode for orchestrator
orchestrator = ClaudeCodeOrchestrator(db_service, debug=True)
```

### Support

For issues and questions:

1. Check the test suite for examples
2. Review the documentation
3. Check the APM (Agent Project Manager) logs
4. Create an issue with detailed information

## Future Enhancements

### Planned Features

1. **Real-time Sync**: Real-time synchronization between APM (Agent Project Manager) and Claude Code
2. **Advanced Analytics**: Analytics and reporting for Claude Code usage
3. **Custom Templates**: Custom templates for component generation
4. **Plugin Marketplace**: Marketplace for sharing Claude Code plugins
5. **AI-Powered Optimization**: AI-powered optimization of Claude Code configurations

### Contributing

Contributions are welcome! Please:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Submit pull requests with clear descriptions

## License

This integration is part of APM (Agent Project Manager) and follows the same license terms.
