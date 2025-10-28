"""
Claude Code Runtime Module

Runtime orchestration for Claude Code integration in APM (Agent Project Manager).
Provides comprehensive capabilities for Claude-based development workflows.

Organized under providers/anthropic/claude_code/runtime/ for cohesive architecture.
Complementary to generation/ (templates) - provides runtime orchestration.

Main Components:
- ClaudeCodeOrchestrator: Main coordinator for all subsystems
- ClaudeIntegrationService: Service-level coordinator
- ClaudeCodePlugin: Comprehensive plugin with all capabilities
- HooksEngine: Event-driven lifecycle management
- SubagentInvocationHandler: Subagent execution
- SettingsManager: Configuration management
- SlashCommandRegistry: Command handling

Example:
    from agentpm.providers.anthropic.claude_code.runtime import (
        ClaudeCodeOrchestrator,
        get_orchestrator
    )
    from agentpm.core.database import get_database

    db = get_database()
    orchestrator = get_orchestrator(db, project_id=1)

    await orchestrator.initialize()
    await orchestrator.handle_session_start("session-123", {})
    # ... work ...
    await orchestrator.handle_session_end("session-123", {})
    await orchestrator.shutdown()
"""

from .service import ClaudeIntegrationService
from .orchestrator import ClaudeCodeOrchestrator, get_orchestrator, reset_orchestrator

__all__ = [
    "ClaudeIntegrationService",
    "ClaudeCodeOrchestrator",
    "get_orchestrator",
    "reset_orchestrator",
]
