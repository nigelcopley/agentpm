"""
Agent File Generator Plugins

Generates provider-specific agent files from database agent records.
Supports extensible provider architecture for Claude Code, Cursor, Gemini, etc.
"""

from .base import ProviderGenerator
from .registry import (
    get_provider_generator,
    register_provider_generator,
    detect_current_provider,
    list_available_providers,
)

__all__ = [
    "ProviderGenerator",
    "get_provider_generator",
    "register_provider_generator",
    "detect_current_provider",
    "list_available_providers",
]
