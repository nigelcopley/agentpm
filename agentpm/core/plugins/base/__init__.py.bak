"""
Plugin Base Module

Base classes and types for plugin system.

Usage:
    from agentpm.core.plugins.base import BasePlugin, PluginCategory

    class MyPlugin(BasePlugin):
        def extract_project_facts(self, project_path):
            return {'python_version': '3.11', ...}

        def generate_code_amalgamations(self, project_path):
            return {'classes': '# All classes...', ...}
"""

from .plugin_interface import BasePlugin
from .types import (
    PluginCategory,
    ProjectFacts,
    CodeAmalgamation,
)

__all__ = [
    "BasePlugin",
    "PluginCategory",
    "ProjectFacts",
    "CodeAmalgamation",
]