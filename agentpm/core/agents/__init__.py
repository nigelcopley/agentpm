"""
Agent Generation System

Provides agent file generation with Claude Code headless integration.

Components:
- claude_integration: Wrapper for Claude Code headless invocation
- generator: Agent file generation orchestration
- templates: Base template management

Pattern: Generate project-specific agents from base templates
"""

from .claude_integration import invoke_claude_code_headless, MockClaudeIntegration

__all__ = [
    'invoke_claude_code_headless',
    'MockClaudeIntegration',
]
