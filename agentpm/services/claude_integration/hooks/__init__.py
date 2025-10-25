"""
Claude Hooks Engine

Event-driven lifecycle management for Claude integrations.
Supports session lifecycle, tool usage, and custom events.

Pattern: Event bus with plugin dispatch
"""

from .models import HookEvent, EventType, EventResult
from .engine import HooksEngine, get_hooks_engine, reset_hooks_engine
from .claude_code_handlers import ClaudeCodeHookHandlers

__all__ = [
    "HookEvent",
    "EventType",
    "EventResult",
    "HooksEngine",
    "get_hooks_engine",
    "reset_hooks_engine",
    "ClaudeCodeHookHandlers",
]
