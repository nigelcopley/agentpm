"""
Anthropic / Claude provider comprehensive integration.

Provides formatter and adapter skeletons that will later be populated with
real formatting logic migrated from hooks/context_integration.py.

Also provides comprehensive Claude Code integration for APM (Agent Project Manager) including:
- Skills system
- Plugins system
- Hooks system
- Subagents
- Settings management
- Slash commands
- Checkpointing
- Memory tools
- Orchestration
"""

from .formatter import AnthropicFormatter
from .adapter import AnthropicAdapter
from .skills import ClaudeCodeSkillGenerator, SkillDefinition, SkillRegistry
from .claude_code import (
    ClaudeCodeOrchestrator,
    ClaudeCodePluginManager,
    ClaudeCodeHooksManager,
    ClaudeCodeSubagentsManager,
    ClaudeCodeSettingsManager,
    ClaudeCodeSlashCommandsManager,
    ClaudeCodeCheckpointingManager,
    ClaudeCodeMemoryToolManager,
)
from ..base import register_formatter

register_formatter("anthropic", AnthropicFormatter)

__all__ = [
    # Core formatter and adapter
    "AnthropicFormatter",
    "AnthropicAdapter",
    
    # Skills system
    "ClaudeCodeSkillGenerator",
    "SkillDefinition",
    "SkillRegistry",
    
    # Claude Code comprehensive integration
    "ClaudeCodeOrchestrator",
    "ClaudeCodePluginManager",
    "ClaudeCodeHooksManager",
    "ClaudeCodeSubagentsManager",
    "ClaudeCodeSettingsManager",
    "ClaudeCodeSlashCommandsManager",
    "ClaudeCodeCheckpointingManager",
    "ClaudeCodeMemoryToolManager",
]
