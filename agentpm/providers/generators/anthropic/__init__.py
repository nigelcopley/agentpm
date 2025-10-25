"""
Anthropic (Claude Code) Provider Generator

Generates .claude/agents/*.md files from database agent records.
"""

from .claude_code_generator import ClaudeCodeGenerator

__all__ = ["ClaudeCodeGenerator"]
