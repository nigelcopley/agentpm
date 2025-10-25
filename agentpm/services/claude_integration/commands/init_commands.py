"""
Command Initialization

Registers all AIPM slash commands with the registry.

Usage:
    from agentpm.services.claude_integration.commands import init_commands

    # Initialize all commands
    init_commands()

    # Use commands
    registry = get_registry()
    result = registry.execute("aipm:status")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .registry import get_registry
from .handlers import CommandHandlers

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


def init_commands(db: DatabaseService) -> None:
    """
    Initialize and register all AIPM slash commands.

    Args:
        db: Database service instance (required)

    Example:
        from agentpm.services.claude_integration.commands import init_commands
        from agentpm.core.database import DatabaseService

        # Initialize all commands with database
        db = DatabaseService("/path/to/db")
        init_commands(db)

        # Commands are now available
        registry = get_registry()
        result = registry.execute("aipm:context")
    """
    registry = get_registry()
    handlers = CommandHandlers(db)

    # Register /aipm:context command
    registry.register(
        name="aipm:context",
        description="Load AIPM context for current session",
        usage=(
            "/aipm:context [options]\n"
            "  Options:\n"
            "    --work-item=ID  : Load specific work item context\n"
            "    --task=ID       : Load specific task context\n"
            "    --full          : Load full hierarchical context"
        ),
        handler=handlers.context
    )

    # Register /aipm:status command
    registry.register(
        name="aipm:status",
        description="Show AIPM project status",
        usage=(
            "/aipm:status [options]\n"
            "  Options:\n"
            "    --detailed       : Show detailed status\n"
            "    --work-items-only: Show only work items\n"
            "    --tasks-only     : Show only tasks"
        ),
        handler=handlers.status
    )

    # Register /aipm:memory command
    registry.register(
        name="aipm:memory",
        description="Generate or show memory files",
        usage=(
            "/aipm:memory <action> [options]\n"
            "  Actions:\n"
            "    status          : Show memory file status (default)\n"
            "    generate        : Generate memory files\n"
            "  Options:\n"
            "    --all           : Generate all memory files"
        ),
        handler=handlers.memory
    )

    # Register /aipm:checkpoint command
    registry.register(
        name="aipm:checkpoint",
        description="Create, list, and restore session checkpoints",
        usage=(
            "/aipm:checkpoint [options]\n"
            "  Options:\n"
            "    --name=NAME     : Checkpoint name (default: auto-generated)\n"
            "    --message=MSG   : Checkpoint message\n"
            "    --list          : List all checkpoints for session\n"
            "    --restore=ID    : Restore checkpoint by ID"
        ),
        handler=handlers.checkpoint
    )

    logger.info("All AIPM slash commands registered")


def list_available_commands() -> str:
    """
    Get formatted list of available slash commands.

    Returns:
        Formatted string with command list

    Example:
        print(list_available_commands())
    """
    registry = get_registry()
    commands = registry.list_commands()

    if not commands:
        return "No commands registered. Call init_commands() first."

    lines = ["Available AIPM Slash Commands:", ""]

    for cmd in sorted(commands, key=lambda c: c.name):
        lines.append(f"/{cmd.name}")
        lines.append(f"  {cmd.description}")
        lines.append(f"  Enabled: {'Yes' if cmd.enabled else 'No'}")
        lines.append("")
        lines.append(f"  Usage:")
        for usage_line in cmd.usage.split("\n"):
            lines.append(f"    {usage_line}")
        lines.append("")

    return "\n".join(lines)
