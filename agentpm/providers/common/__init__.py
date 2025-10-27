"""
Common Patterns for Provider Generators

Shared patterns, dataclasses, and utilities used across all provider generators
(Claude Code, Cursor, OpenAI Codex, Google Gemini).
"""

from .patterns import (
    UniversalContext,
    ProjectContext,
    WorkItemContext,
    TaskContext,
    CommonExclusions,
    CommonRuleCategories,
)
from .integrity import SHA256HashVerifier

__all__ = [
    "UniversalContext",
    "ProjectContext",
    "WorkItemContext",
    "TaskContext",
    "CommonExclusions",
    "CommonRuleCategories",
    "SHA256HashVerifier",
]
