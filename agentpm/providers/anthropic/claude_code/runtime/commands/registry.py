"""
Slash Command Registry

Central registry for managing and executing slash commands.

Pattern: Singleton registry with command routing
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from .models import SlashCommand, CommandResult, CommandError, CommandStatus

logger = logging.getLogger(__name__)


class SlashCommandRegistry:
    """
    Registry for AIPM slash commands.

    Manages command registration, lookup, and execution.
    Follows singleton pattern for global command access.

    Example:
        registry = get_registry()

        # Register command
        registry.register(
            name="aipm:context",
            description="Load AIPM context",
            usage="/aipm:context [--work-item=ID]",
            handler=context_handler
        )

        # Execute command
        result = registry.execute("aipm:context", args=["--work-item=123"])
    """

    def __init__(self):
        """Initialize empty registry."""
        self._commands: Dict[str, SlashCommand] = {}
        logger.info("SlashCommandRegistry initialized")

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        handler: Callable[[List[str]], CommandResult],
        enabled: bool = True
    ) -> None:
        """
        Register a slash command.

        Args:
            name: Command name (without leading slash, e.g., "aipm:context")
            description: Human-readable description
            usage: Usage string with examples
            handler: Command handler function taking args and returning CommandResult
            enabled: Whether command is enabled (default: True)

        Raises:
            ValueError: If command already registered

        Example:
            def my_handler(args: List[str]) -> CommandResult:
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message="Command executed"
                )

            registry.register(
                name="aipm:test",
                description="Test command",
                usage="/aipm:test [options]",
                handler=my_handler
            )
        """
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")

        command = SlashCommand(
            name=name,
            description=description,
            usage=usage,
            handler=handler,
            enabled=enabled
        )

        self._commands[name] = command
        logger.info(f"Registered command: /{name}")

    def unregister(self, name: str) -> None:
        """
        Unregister a slash command.

        Args:
            name: Command name to unregister

        Raises:
            KeyError: If command not found

        Example:
            registry.unregister("aipm:test")
        """
        if name not in self._commands:
            raise KeyError(f"Command '{name}' not registered")

        del self._commands[name]
        logger.info(f"Unregistered command: /{name}")

    def get(self, name: str) -> Optional[SlashCommand]:
        """
        Get command by name.

        Args:
            name: Command name

        Returns:
            SlashCommand instance or None if not found

        Example:
            command = registry.get("aipm:context")
            if command:
                print(command.description)
        """
        return self._commands.get(name)

    def list_commands(self) -> List[SlashCommand]:
        """
        List all registered commands.

        Returns:
            List of SlashCommand instances (handler excluded)

        Example:
            for cmd in registry.list_commands():
                print(f"/{cmd.name}: {cmd.description}")
        """
        return [
            SlashCommand(
                name=cmd.name,
                description=cmd.description,
                usage=cmd.usage,
                enabled=cmd.enabled
            )
            for cmd in self._commands.values()
        ]

    def execute(
        self,
        name: str,
        args: Optional[List[str]] = None
    ) -> CommandResult:
        """
        Execute a slash command.

        Args:
            name: Command name (with or without leading slash)
            args: Optional command arguments

        Returns:
            CommandResult with execution status and data

        Raises:
            CommandError: If command not found or execution fails

        Example:
            # Execute with arguments
            result = registry.execute(
                "aipm:context",
                args=["--work-item=123"]
            )

            if result.status == CommandStatus.SUCCESS:
                print(result.message)
                print(result.data)
        """
        # Normalize command name (remove leading slash if present)
        if name.startswith("/"):
            name = name[1:]

        args = args or []

        # Check if command exists
        command = self._commands.get(name)
        if not command:
            raise CommandError(
                command=name,
                message=f"Command '/{name}' not found",
                details={"available_commands": list(self._commands.keys())}
            )

        # Check if command is enabled
        if not command.enabled:
            raise CommandError(
                command=name,
                message=f"Command '/{name}' is disabled"
            )

        # Execute handler
        try:
            logger.debug(f"Executing command: /{name} with args: {args}")
            result = command.handler(args)

            if not isinstance(result, CommandResult):
                # Handler returned wrong type - wrap it
                logger.warning(
                    f"Handler for /{name} returned non-CommandResult: {type(result)}"
                )
                result = CommandResult(
                    status=CommandStatus.SUCCESS,
                    message="Command executed",
                    data={"result": result}
                )

            logger.info(f"Command /{name} executed: {result.status}")
            return result

        except CommandError:
            # Re-raise CommandErrors
            raise
        except Exception as e:
            # Wrap other exceptions
            logger.error(f"Error executing /{name}: {e}", exc_info=True)
            raise CommandError(
                command=name,
                message=f"Execution failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )

    def clear(self) -> None:
        """
        Clear all registered commands.

        Useful for testing and cleanup.

        Example:
            registry.clear()
        """
        self._commands.clear()
        logger.info("All commands cleared from registry")


# Global singleton instance
_registry: Optional[SlashCommandRegistry] = None


def get_registry() -> SlashCommandRegistry:
    """
    Get global slash command registry.

    Returns singleton instance, creating it if needed.

    Returns:
        SlashCommandRegistry instance

    Example:
        registry = get_registry()
        result = registry.execute("aipm:status")
    """
    global _registry
    if _registry is None:
        _registry = SlashCommandRegistry()
    return _registry


def reset_registry() -> None:
    """
    Reset global registry (for testing).

    Creates new registry instance, discarding old one.

    Example:
        # In tests
        reset_registry()
        registry = get_registry()
        # Fresh registry with no commands
    """
    global _registry
    _registry = None
    logger.info("Registry reset")
