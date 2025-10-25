"""
Claude Code Comprehensive Integration

Provides complete integration with Claude Code including:
- Plugins system
- Hooks system  
- Subagents
- Settings management
- Slash commands
- Checkpointing
- Memory tools
- Skills (already implemented)

Based on Claude Code documentation:
- https://docs.claude.com/en/docs/claude-code/plugins
- https://docs.claude.com/en/docs/claude-code/hooks-guide
- https://docs.claude.com/en/docs/claude-code/sub-agents
- https://docs.claude.com/en/docs/claude-code/settings
- https://docs.claude.com/en/docs/claude-code/slash-commands
- https://docs.claude.com/en/docs/claude-code/checkpointing
- https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool
"""

from .plugins import ClaudeCodePluginManager, PluginDefinition, MarketplaceDefinition
from .hooks import ClaudeCodeHooksManager, HookDefinition, HookEvent
from .subagents import ClaudeCodeSubagentsManager, SubagentDefinition
from .settings import ClaudeCodeSettingsManager, SettingsDefinition
from .slash_commands import ClaudeCodeSlashCommandsManager, SlashCommandDefinition
from .checkpointing import ClaudeCodeCheckpointingManager, CheckpointDefinition
from .memory_tool import ClaudeCodeMemoryToolManager, MemoryToolDefinition
from .orchestrator import ClaudeCodeOrchestrator

__all__ = [
    # Core managers
    "ClaudeCodeOrchestrator",
    
    # Plugin system
    "ClaudeCodePluginManager",
    "PluginDefinition", 
    "MarketplaceDefinition",
    
    # Hooks system
    "ClaudeCodeHooksManager",
    "HookDefinition",
    "HookEvent",
    
    # Subagents system
    "ClaudeCodeSubagentsManager",
    "SubagentDefinition",
    
    # Settings system
    "ClaudeCodeSettingsManager",
    "SettingsDefinition",
    
    # Slash commands
    "ClaudeCodeSlashCommandsManager",
    "SlashCommandDefinition",
    
    # Checkpointing
    "ClaudeCodeCheckpointingManager",
    "CheckpointDefinition",
    
    # Memory tools
    "ClaudeCodeMemoryToolManager",
    "MemoryToolDefinition",
]
