"""
Plugin System Module

Plugin system for framework-specific fact extraction and code amalgamations.

Usage:
    from agentpm.core.plugins.domains.languages.python import PythonPlugin

    plugin = PythonPlugin()

    # Extract project facts
    facts = plugin.extract_project_facts(project_path)

    # Generate code amalgamations
    amalgamations = plugin.generate_code_amalgamations(project_path)
"""

from .base import (
    BasePlugin,
    PluginCategory,
    ProjectFacts,
    CodeAmalgamation,
)
from .base.types import EnrichmentResult, ContextDelta
from .orchestrator import PluginOrchestrator

__all__ = [
    "BasePlugin",
    "PluginCategory",
    "ProjectFacts",
    "CodeAmalgamation",
    "EnrichmentResult",
    "ContextDelta",
    "PluginOrchestrator",
]