"""
Anthropic Claude Code Skills Integration

Provides integration between APM (Agent Project Manager) agents and Claude Code Skills.
Converts APM (Agent Project Manager) agents, workflows, and capabilities into Claude Code Skills
for seamless project management within Claude Code.

Pattern: Provider-specific skills generation and management
"""

from .generator import ClaudeCodeSkillGenerator
from .models import SkillDefinition, SkillTemplate, SkillCategory, SkillType
from .registry import SkillRegistry
from .templates import get_skill_template

__all__ = [
    "ClaudeCodeSkillGenerator",
    "SkillDefinition", 
    "SkillTemplate",
    "SkillCategory",
    "SkillType",
    "SkillRegistry",
    "get_skill_template"
]
