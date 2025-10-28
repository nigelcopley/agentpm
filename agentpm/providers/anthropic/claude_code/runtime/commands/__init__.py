"""
Claude Code Slash Commands

AIPM-specific slash commands for Claude Code integration.

Provides:
- /aipm:context - Load AIPM context for current session
- /aipm:status - Show APM project status
- /aipm:memory - Generate or show memory files
- /aipm:checkpoint - Create session checkpoint

Example:
    from agentpm.providers.anthropic.claude_code.runtime.commands import get_registry

    registry = get_registry()
    result = registry.execute("aipm:context", args=["--work-item=123"])
"""

from .registry import SlashCommandRegistry, get_registry, reset_registry
from .models import SlashCommand, CommandResult, CommandError, CommandStatus
from .handlers import CommandHandlers
from .init_commands import init_commands, list_available_commands

__all__ = [
    "SlashCommandRegistry",
    "get_registry",
    "reset_registry",
    "SlashCommand",
    "CommandResult",
    "CommandError",
    "CommandStatus",
    "CommandHandlers",
    "init_commands",
    "list_available_commands",
]
