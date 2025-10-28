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
    ClaudeCodeGenerator,
    SkillGenerator,
    MemoryGenerator,
    ClaudeCodeOrchestrator,
    get_orchestrator,
    reset_orchestrator,
    ClaudeCodeIntegration,
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

    # Claude Code generation (templates)
    "ClaudeCodeGenerator",
    "SkillGenerator",
    "MemoryGenerator",

    # Claude Code runtime (orchestration)
    "ClaudeCodeOrchestrator",
    "get_orchestrator",
    "reset_orchestrator",

    # Models
    "ClaudeCodeIntegration",
]
