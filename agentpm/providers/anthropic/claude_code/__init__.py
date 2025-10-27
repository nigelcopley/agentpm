"""
Claude Code Integration (Simplified)

DEPRECATED ARCHITECTURE:
The old manager-based integration system (plugins, hooks, subagents, settings,
slash commands, checkpointing, memory tools) has been replaced with a simpler
template-based generator system.

RECOMMENDED APPROACH:
Use the new template-based generator:

```python
from agentpm.providers.anthropic.claude_code.generator import ClaudeCodeGenerator
generator = ClaudeCodeGenerator(db_service)
result = generator.generate_from_agents(agents, rules, project, output_dir)
```

Or use the high-level service:

```python
from agentpm.core.services.agent_generator import AgentGeneratorService
generator = AgentGeneratorService(db_service, project_path)
summary = generator.generate_all()
```

BACKWARD COMPATIBILITY:
This module still exports the deprecated managers for backward compatibility.
They are located in the `deprecated/` directory.

See deprecated/README.md for migration guide.
"""

import warnings

# New template-based generator (recommended)
from .generator import ClaudeCodeGenerator

# Deprecated: Legacy orchestrator (now a thin compatibility wrapper)
from .orchestrator import ClaudeCodeOrchestrator

# Models (still useful for data structures)
from .models import ClaudeCodeIntegration

# Deprecated: Old manager classes (moved to deprecated/)
# These imports are kept for backward compatibility but will emit warnings
try:
    from .deprecated.plugins import ClaudeCodePluginManager, PluginDefinition, MarketplaceDefinition
    from .deprecated.hooks import ClaudeCodeHooksManager, HookDefinition, HookEvent
    from .deprecated.subagents import ClaudeCodeSubagentsManager, SubagentDefinition
    from .deprecated.settings import ClaudeCodeSettingsManager, SettingsDefinition
    from .deprecated.slash_commands import ClaudeCodeSlashCommandsManager, SlashCommandDefinition
    from .deprecated.checkpointing import ClaudeCodeCheckpointingManager, CheckpointDefinition
    from .deprecated.memory_tool import ClaudeCodeMemoryToolManager, MemoryToolDefinition

    # Emit deprecation warning when importing deprecated managers
    warnings.warn(
        "Claude Code manager classes (PluginManager, HooksManager, etc.) are deprecated. "
        "Use AgentGeneratorService from agentpm.core.services.agent_generator instead. "
        "See deprecated/README.md for migration guide.",
        DeprecationWarning,
        stacklevel=2
    )
except ImportError as e:
    # If deprecated modules can't be imported, provide stub classes
    warnings.warn(
        f"Deprecated Claude Code managers could not be imported: {e}. "
        "Use AgentGeneratorService instead.",
        DeprecationWarning
    )

__all__ = [
    # New template-based generator (recommended)
    "ClaudeCodeGenerator",

    # Core (deprecated but maintained for compatibility)
    "ClaudeCodeOrchestrator",
    "ClaudeCodeIntegration",

    # Deprecated managers (use AgentGeneratorService instead)
    "ClaudeCodePluginManager",
    "PluginDefinition",
    "MarketplaceDefinition",
    "ClaudeCodeHooksManager",
    "HookDefinition",
    "HookEvent",
    "ClaudeCodeSubagentsManager",
    "SubagentDefinition",
    "ClaudeCodeSettingsManager",
    "SettingsDefinition",
    "ClaudeCodeSlashCommandsManager",
    "SlashCommandDefinition",
    "ClaudeCodeCheckpointingManager",
    "CheckpointDefinition",
    "ClaudeCodeMemoryToolManager",
    "MemoryToolDefinition",
]
