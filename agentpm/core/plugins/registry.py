"""
Plugin Registry - Tool Registration and Discovery

Maps detected technologies to available plugins.
Enables dynamic plugin loading and tool invocation.

Inspired by Claude Agent SDK tool pattern.

Pattern: Registry pattern with lazy loading
"""

from pathlib import Path
from typing import Dict, Type, List, Optional

from .base.plugin_interface import BasePlugin
from .domains.languages.python import PythonPlugin
from .domains.testing.pytest import PytestPlugin
from .domains.frameworks.click import ClickPlugin
from .domains.data.sqlite import SQLitePlugin


class PluginRegistry:
    """
    Registry of all available plugins.

    Provides:
    - Plugin discovery by technology name
    - Plugin metadata
    - Lazy loading for performance
    """

    # Technology name → Plugin class mapping
    PLUGIN_MAP: Dict[str, Type[BasePlugin]] = {
        'python': PythonPlugin,
        'pytest': PytestPlugin,
        'click': ClickPlugin,
        'sqlite': SQLitePlugin,
        # Future plugins added here:
        # 'django': DjangoPlugin,
        # 'html': HTMLPlugin,
        # 'javascript': JavaScriptPlugin,
        # 'nextjs': NextJsPlugin,
    }

    def __init__(self):
        """Initialize registry with empty cache"""
        self._plugin_cache: Dict[str, BasePlugin] = {}

    def get_plugin(self, technology: str) -> Optional[BasePlugin]:
        """
        Get plugin instance for technology.

        Lazy loads and caches plugins for performance.

        Args:
            technology: Technology name (e.g., 'python', 'django')

        Returns:
            Plugin instance or None if not available

        Example:
            registry = PluginRegistry()
            python_plugin = registry.get_plugin('python')
            facts = python_plugin.extract_project_facts(project_path)
        """
        # Check cache
        if technology in self._plugin_cache:
            return self._plugin_cache[technology]

        # Check if plugin exists
        if technology not in self.PLUGIN_MAP:
            return None

        # Instantiate and cache
        plugin_class = self.PLUGIN_MAP[technology]
        plugin_instance = plugin_class()
        self._plugin_cache[technology] = plugin_instance

        return plugin_instance

    def get_plugins_for_technologies(
        self,
        technologies: List[str]
    ) -> Dict[str, BasePlugin]:
        """
        Get plugins for multiple technologies.

        Args:
            technologies: List of technology names

        Returns:
            Dictionary mapping technology → plugin instance

        Example:
            detected = ['python', 'django', 'pytest']
            plugins = registry.get_plugins_for_technologies(detected)
            # Returns: {'python': PythonPlugin(), 'django': DjangoPlugin(), ...}
        """
        plugins = {}

        for tech in technologies:
            plugin = self.get_plugin(tech)
            if plugin:
                plugins[tech] = plugin

        return plugins

    def list_available_plugins(self) -> List[Dict[str, str]]:
        """
        List all available plugins with metadata.

        Returns:
            List of plugin info dictionaries

        Example:
            [
                {'id': 'lang:python', 'technology': 'python', 'category': 'language'},
                {'id': 'testing:pytest', 'technology': 'pytest', 'category': 'testing'},
                ...
            ]
        """
        plugin_list = []

        for tech_name, plugin_class in self.PLUGIN_MAP.items():
            # Instantiate to get metadata
            plugin = self.get_plugin(tech_name)
            if plugin:
                plugin_list.append({
                    'id': plugin.plugin_id,
                    'technology': plugin.enriches,
                    'category': plugin.category.value
                })

        return plugin_list

    def get_plugin_count(self) -> int:
        """Get total number of available plugins"""
        return len(self.PLUGIN_MAP)

    def has_plugin(self, technology: str) -> bool:
        """Check if plugin exists for technology"""
        return technology in self.PLUGIN_MAP


# Global registry instance (singleton pattern)
_registry = None


def get_registry() -> PluginRegistry:
    """
    Get global plugin registry instance.

    Returns:
        Singleton PluginRegistry instance

    Example:
        from agentpm.core.plugins.registry import get_registry

        registry = get_registry()
        python_plugin = registry.get_plugin('python')
    """
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry