"""
Claude Code Generation Module

This module provides template generation capabilities for Claude Code:
- Skill template generation
- Memory template generation
- Configuration generation

Organized under providers/anthropic/claude_code/generation/ for cohesive architecture.
"""

from .generator import ClaudeCodeGenerator
from .skill_generator import SkillGenerator
from .memory_generator import MemoryGenerator

__all__ = [
    "ClaudeCodeGenerator",
    "SkillGenerator",
    "MemoryGenerator",
]
