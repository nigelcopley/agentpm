"""
Context Assembly Plugin - Platform Agnostic Context Management

This plugin provides universal context assembly capabilities that can be used
across different AI platforms and interfaces.

Architecture:
- Core assembly logic (platform agnostic)
- Universal formatters (markdown, JSON, XML)
- Platform adapters (Claude, OpenAI, Anthropic, etc.)
- Hook integration (Claude Code, Web, CLI)

Usage:
    from agentpm.core.plugins.context_assembly import ContextAssemblyPlugin
    from agentpm.core.plugins.context_assembly.formatters import MarkdownFormatter
    from agentpm.core.plugins.context_assembly.adapters import ClaudeAdapter
    
    plugin = ContextAssemblyPlugin()
    formatter = MarkdownFormatter()
    adapter = ClaudeAdapter()
    
    context = plugin.assemble_context(task_id=123)
    formatted = formatter.format(context)
    platform_optimized = adapter.optimize(formatted)
"""

from .assembly_plugin import ContextAssemblyPlugin
from .formatters.markdown_formatter import MarkdownFormatter
from .formatters.json_formatter import JSONFormatter
from .adapters.claude_adapter import ClaudeAdapter
from agentpm.providers import get_provider

__all__ = [
    "ContextAssemblyPlugin",
    "MarkdownFormatter",
    "JSONFormatter",
    "ClaudeAdapter",
    "get_provider",
]

