"""
OpenAI Codex Provider Module

Provides configuration generation for OpenAI Codex from APM database.

Key Features:
- Native AGENTS.md support (Codex reads it directly!)
- config.toml generation with profiles
- Sandbox and approval policies
- APM-specific profiles (planning, implementation, testing)

Usage:
    >>> from agentpm.providers.openai.codex import CodexGenerator
    >>> generator = CodexGenerator(db_service)
    >>> result = generator.generate_from_agents(agents, rules, project, output_dir)
"""

from .generator import CodexGenerator

__all__ = ["CodexGenerator"]
