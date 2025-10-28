"""
Claude Plugin Registry

Manages registration and discovery of Claude integration plugins.
Follows the pattern from agentpm/core/plugins/registry.py with
Claude-specific enhancements for capability-based routing.

Pattern: Singleton registry with lazy loading
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import ClaudePlugin, PluginCapability


class ClaudePluginRegistry:
    """
    Registry for Claude integration plugins.

    Provides:
    - Plugin registration by name
    - Capability-based discovery
    - Lazy loading for performance
    - Singleton pattern for global access

    Example:
        registry = get_registry()

        # Register plugin
        registry.register_plugin(hooks_plugin)

        # Find plugins by capability
        hook_plugins = registry.get_plugins_by_capability(PluginCapability.HOOKS)

        # Get specific plugin
        memory_plugin = registry.get_plugin("memory")
    """

    def __init__(self):
        """Initialize registry with empty plugin cache."""
        self._plugins: Dict[str, ClaudePlugin] = {}
        self._capability_index: Dict[PluginCapability, List[str]] = {
            cap: [] for cap in PluginCapability
        }

    def register_plugin(self, plugin: ClaudePlugin) -> None:
        """
        Register a Claude plugin.

        Indexes plugin by name and capabilities for efficient lookup.

        Args:
            plugin: Plugin instance implementing ClaudePlugin protocol

        Raises:
            ValueError: If plugin with same name already registered
            TypeError: If plugin doesn't implement ClaudePlugin protocol

        Example:
            registry = get_registry()
            registry.register_plugin(MyHooksPlugin())
        """
        # Validate plugin implements protocol
        if not isinstance(plugin, ClaudePlugin):
            raise TypeError(
                f"Plugin {plugin} must implement ClaudePlugin protocol "
                "(must have 'name' attribute and 'supports'/'handle' methods)"
            )

        # Check for duplicate registration
        if plugin.name in self._plugins:
            raise ValueError(
                f"Plugin '{plugin.name}' already registered. "
                "Unregister existing plugin first."
            )

        # Register plugin
        self._plugins[plugin.name] = plugin

        # Build capability index
        for capability in PluginCapability:
            if plugin.supports(capability):
                self._capability_index[capability].append(plugin.name)

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin by name.

        Args:
            plugin_name: Name of plugin to unregister

        Raises:
            KeyError: If plugin not found
        """
        if plugin_name not in self._plugins:
            raise KeyError(f"Plugin '{plugin_name}' not registered")

        # Remove from capability index
        for capability, plugin_names in self._capability_index.items():
            if plugin_name in plugin_names:
                plugin_names.remove(plugin_name)

        # Remove plugin
        del self._plugins[plugin_name]

    def get_plugin(self, plugin_name: str) -> Optional[ClaudePlugin]:
        """
        Get plugin by name.

        Args:
            plugin_name: Name of plugin to retrieve

        Returns:
            Plugin instance or None if not found

        Example:
            plugin = registry.get_plugin("hooks")
            if plugin:
                result = plugin.handle(event_data)
        """
        return self._plugins.get(plugin_name)

    def get_plugins_by_capability(
        self, capability: PluginCapability
    ) -> List[ClaudePlugin]:
        """
        Get all plugins supporting a capability.

        Args:
            capability: PluginCapability to search for

        Returns:
            List of plugin instances (may be empty)

        Example:
            # Get all plugins that handle hooks
            hook_plugins = registry.get_plugins_by_capability(
                PluginCapability.HOOKS
            )

            for plugin in hook_plugins:
                result = plugin.handle(event_data)
        """
        plugin_names = self._capability_index.get(capability, [])
        return [self._plugins[name] for name in plugin_names]

    def list_plugins(self) -> List[Dict[str, any]]:
        """
        List all registered plugins with metadata.

        Returns:
            List of plugin info dictionaries

        Example:
            [
                {
                    'name': 'hooks',
                    'capabilities': ['hooks'],
                },
                {
                    'name': 'memory',
                    'capabilities': ['memory', 'checkpointing'],
                },
            ]
        """
        plugin_list = []

        for name, plugin in self._plugins.items():
            capabilities = [
                cap.value
                for cap in PluginCapability
                if plugin.supports(cap)
            ]

            plugin_list.append({
                "name": name,
                "capabilities": capabilities,
            })

        return plugin_list

    def get_plugin_count(self) -> int:
        """Get total number of registered plugins."""
        return len(self._plugins)

    def has_plugin(self, plugin_name: str) -> bool:
        """Check if plugin is registered."""
        return plugin_name in self._plugins

    def clear(self) -> None:
        """
        Clear all registered plugins.

        Useful for testing or reinitialization.
        """
        self._plugins.clear()
        for capability in PluginCapability:
            self._capability_index[capability].clear()


# Global registry instance (singleton pattern)
_registry: Optional[ClaudePluginRegistry] = None


def get_registry() -> ClaudePluginRegistry:
    """
    Get global Claude plugin registry instance.

    Returns:
        Singleton ClaudePluginRegistry instance

    Example:
        from agentpm.providers.anthropic.claude_code.runtime.plugins import get_registry

        registry = get_registry()
        registry.register_plugin(my_plugin)
    """
    global _registry
    if _registry is None:
        _registry = ClaudePluginRegistry()
    return _registry


def reset_registry() -> None:
    """
    Reset global registry to None.

    Useful for testing to ensure clean state.

    Example:
        # In test teardown
        reset_registry()
    """
    global _registry
    _registry = None
