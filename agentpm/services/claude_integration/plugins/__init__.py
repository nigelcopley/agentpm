"""
Claude Integration Plugin System

Modular plugin architecture for Claude-related capabilities:
- Hooks (lifecycle events)
- Memory (persistent context)
- Commands (slash commands)
- Checkpointing (state snapshots)

Pattern: Registry pattern with capability-based discovery
"""

from .base import ClaudePlugin, PluginCapability, BaseClaudePlugin
from .registry import ClaudePluginRegistry, get_registry, reset_registry
from .claude_code import ClaudeCodePlugin

__all__ = [
    "ClaudePlugin",
    "PluginCapability",
    "BaseClaudePlugin",
    "ClaudePluginRegistry",
    "get_registry",
    "reset_registry",
    "ClaudeCodePlugin",
]
