"""
Base Plugin Interface for Claude Integration

Defines the plugin protocol that all Claude integration plugins must implement.
Extends the Protocol pattern from service.py with Claude-specific capabilities.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Protocol, runtime_checkable


class PluginCapability(Enum):
    """
    Capabilities that Claude plugins can provide.

    Used for plugin discovery and routing.
    """

    HOOKS = "hooks"                  # Lifecycle event handling
    MEMORY = "memory"                # Persistent context management
    COMMANDS = "commands"            # Slash command execution
    CHECKPOINTING = "checkpointing"  # State snapshot creation
    SUBAGENTS = "subagents"          # Subagent orchestration


@runtime_checkable
class ClaudePlugin(Protocol):
    """
    Protocol for Claude integration plugins.

    All plugins must implement this interface for registration and execution.
    Follows the plugin pattern from agentpm/core/plugins/registry.py.

    Example:
        class HooksPlugin:
            name: str = "hooks"

            def supports(self, capability: PluginCapability) -> bool:
                return capability == PluginCapability.HOOKS

            def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                # Process hook event
                return {"status": "success"}
    """

    name: str
    """Unique plugin identifier (e.g., 'hooks', 'memory')"""

    def supports(self, capability: PluginCapability | str) -> bool:
        """
        Check if plugin supports a given capability.

        Args:
            capability: PluginCapability enum or capability string

        Returns:
            True if plugin can handle this capability

        Example:
            if plugin.supports(PluginCapability.HOOKS):
                result = plugin.handle(event_data)
        """
        ...

    def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle plugin-specific input and produce output.

        Args:
            input_data: Plugin-specific input dictionary
                For hooks: {"type": str, "payload": dict, "session_id": str, ...}
                For memory: {"scope": str, "action": str, ...}
                For commands: {"command": str, "args": dict, ...}

        Returns:
            Plugin-specific output dictionary
            Should include "status": "success" | "error"

        Raises:
            ValueError: If input_data is invalid
            RuntimeError: If processing fails

        Example:
            result = plugin.handle({
                "type": "session-start",
                "payload": {...},
                "session_id": "abc123"
            })
            assert result["status"] == "success"
        """
        ...


class BaseClaudePlugin:
    """
    Base implementation class for Claude plugins.

    Provides common functionality for plugins that don't need
    to be pure Protocols. Subclass this for concrete plugins.

    Example:
        class MyPlugin(BaseClaudePlugin):
            def __init__(self):
                super().__init__(name="my-plugin")

            def supports(self, capability):
                return capability == PluginCapability.HOOKS

            def handle(self, input_data):
                return {"status": "success", "data": {...}}
    """

    def __init__(self, name: str):
        """
        Initialize base plugin.

        Args:
            name: Unique plugin identifier
        """
        self.name = name
        self._capabilities: set[PluginCapability] = set()

    def register_capability(self, capability: PluginCapability) -> None:
        """
        Register a capability this plugin provides.

        Args:
            capability: Capability to register
        """
        self._capabilities.add(capability)

    def supports(self, capability: PluginCapability | str) -> bool:
        """
        Check if plugin supports capability.

        Args:
            capability: PluginCapability or capability string

        Returns:
            True if supported
        """
        if isinstance(capability, str):
            try:
                capability = PluginCapability(capability)
            except ValueError:
                return False

        return capability in self._capabilities

    def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Base handler - override in subclasses.

        Args:
            input_data: Plugin input

        Returns:
            Plugin output
        """
        raise NotImplementedError(
            f"Plugin {self.name} must implement handle() method"
        )
