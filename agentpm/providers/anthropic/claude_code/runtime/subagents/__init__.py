"""
Claude Code Subagents Module

Subagent orchestration for Claude Code integration.
Provides registry, invocation handler, and models for AIPM subagent execution.

Example:
    from agentpm.providers.anthropic.claude_code.runtime.subagents import (
        get_subagent_registry,
        get_invocation_handler,
        SubagentSpec,
        SubagentCapability
    )

    # Register subagents
    registry = get_subagent_registry()
    spec = SubagentSpec(
        name="test-implementer",
        description="Creates comprehensive unit tests",
        capabilities=[SubagentCapability.TESTING],
        tier=1,
        invocation_template="Create tests for [component]"
    )
    registry.register_subagent(spec)

    # Invoke subagent
    handler = get_invocation_handler()
    result = await handler.invoke_subagent(
        subagent_name="test-implementer",
        task_description="Create tests for UserService",
        context={"service": "UserService"},
        session_id="session-123",
        correlation_id="req-456"
    )
"""

from .models import (
    SubagentCapability,
    SubagentSpec,
    SubagentInvocationRequest,
    SubagentInvocationResult,
)
from .registry import (
    SubagentRegistry,
    get_subagent_registry,
    reset_subagent_registry,
)
from .handler import (
    SubagentInvocationHandler,
    get_invocation_handler,
    reset_invocation_handler,
)


__all__ = [
    # Models
    "SubagentCapability",
    "SubagentSpec",
    "SubagentInvocationRequest",
    "SubagentInvocationResult",
    # Registry
    "SubagentRegistry",
    "get_subagent_registry",
    "reset_subagent_registry",
    # Handler
    "SubagentInvocationHandler",
    "get_invocation_handler",
    "reset_invocation_handler",
]
