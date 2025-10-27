"""
Agent Generation System

Provides agent file generation with Claude Code headless integration.

Components:
- claude_integration: Wrapper for Claude Code headless invocation
- generator: Agent file generation orchestration
- templates: Base template management
- provider_detector: Multi-provider detection and path resolution
- registry_validator: Agent registry validation

Pattern: Generate project-specific agents from base templates
"""

from .claude_integration import invoke_claude_code_headless, MockClaudeIntegration
from .provider_detector import (
    Provider,
    detect_provider,
    get_provider_base_path,
    get_agents_directory,
    get_agent_paths,
    get_agent_names,
    get_provider_info,
)

__all__ = [
    'invoke_claude_code_headless',
    'MockClaudeIntegration',
    'Provider',
    'detect_provider',
    'get_provider_base_path',
    'get_agents_directory',
    'get_agent_paths',
    'get_agent_names',
    'get_provider_info',
]
