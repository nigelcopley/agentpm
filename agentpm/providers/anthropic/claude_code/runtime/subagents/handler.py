"""
Subagent Invocation Handler

Handles subagent invocations from Claude Code.
Translates natural language requests to AIPM task execution.

Pattern: Async handler with request normalization and result transformation
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .models import (
    SubagentInvocationRequest,
    SubagentInvocationResult,
)
from .registry import get_subagent_registry


logger = logging.getLogger(__name__)


class SubagentInvocationHandler:
    """
    Handler for Claude Code subagent invocations.

    Processes invocation requests, validates subagent availability,
    and executes subagent tasks (placeholder for future Task tool integration).

    Example:
        handler = SubagentInvocationHandler()

        # Invoke subagent
        result = await handler.invoke_subagent(
            subagent_name="test-implementer",
            task_description="Create unit tests for UserService",
            context={"service": "UserService"},
            session_id="session-123",
            correlation_id="req-456"
        )

        if result.success:
            print(f"Tests created: {result.artifacts}")
    """

    def __init__(self, registry: Optional[Any] = None):
        """
        Initialize invocation handler.

        Args:
            registry: Optional subagent registry (uses global if None)
        """
        self._registry = registry or get_subagent_registry()
        logger.info("SubagentInvocationHandler initialized")

    async def invoke_subagent(
        self,
        subagent_name: str,
        task_description: str,
        context: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubagentInvocationResult:
        """
        Invoke an AIPM subagent.

        Validates subagent existence, normalizes request, executes task
        (placeholder), and returns result.

        Args:
            subagent_name: Name of subagent to invoke
            task_description: Natural language task description
            context: Contextual data for subagent
            session_id: Claude session identifier
            correlation_id: Request correlation ID
            metadata: Additional metadata

        Returns:
            Invocation result

        Example:
            result = await handler.invoke_subagent(
                subagent_name="code-implementer",
                task_description="Implement UserService CRUD operations",
                context={"entity": "User", "operations": ["create", "read"]},
                session_id="session-123",
                correlation_id="req-456"
            )
        """
        try:
            # Validate subagent exists
            spec = self._registry.get_subagent(subagent_name)
            if not spec:
                return SubagentInvocationResult.error_result(
                    subagent_name=subagent_name,
                    message=f"Subagent '{subagent_name}' not found",
                    errors=[f"Subagent '{subagent_name}' is not registered"]
                )

            # Normalize request
            request = SubagentInvocationRequest(
                subagent_name=subagent_name,
                task_description=task_description,
                context=context,
                session_id=session_id,
                correlation_id=correlation_id,
                metadata=metadata or {}
            )

            # Execute subagent task
            result = await self._execute_subagent(request, spec)

            return result

        except Exception as e:
            logger.error(
                f"Error invoking subagent {subagent_name}: {e}",
                exc_info=True
            )
            return SubagentInvocationResult.error_result(
                subagent_name=subagent_name,
                message=f"Invocation failed: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_subagent(
        self,
        request: SubagentInvocationRequest,
        spec: Any,
    ) -> SubagentInvocationResult:
        """
        Execute subagent task.

        Placeholder for future Task tool integration.
        Currently returns mock success result.

        Args:
            request: Normalized invocation request
            spec: Subagent specification

        Returns:
            Invocation result

        Future Implementation:
            # from agentpm.core.orchestration import TaskTool
            # task_tool = TaskTool()
            # result = await task_tool.invoke(
            #     subagent_type=request.subagent_name,
            #     description=request.task_description,
            #     context=request.context
            # )
        """
        logger.info(
            f"Executing subagent '{request.subagent_name}': {request.task_description}"
        )

        # TODO: Integrate with AIPM Task tool for actual execution
        # For now, return success with placeholder data
        return SubagentInvocationResult.success_result(
            subagent_name=request.subagent_name,
            message=f"Subagent '{request.subagent_name}' invocation placeholder",
            data={
                "task_description": request.task_description,
                "context": request.context,
                "status": "simulated",
                "note": "Task tool integration pending"
            },
            artifacts=[]
        )

    def invoke_subagent_sync(
        self,
        subagent_name: str,
        task_description: str,
        context: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubagentInvocationResult:
        """
        Synchronous version of invoke_subagent.

        Convenience method for non-async contexts.

        Args:
            subagent_name: Name of subagent to invoke
            task_description: Natural language task description
            context: Contextual data for subagent
            session_id: Claude session identifier
            correlation_id: Request correlation ID
            metadata: Additional metadata

        Returns:
            Invocation result

        Example:
            result = handler.invoke_subagent_sync(
                subagent_name="doc-toucher",
                task_description="Update API documentation",
                context={"files": ["api.md"]},
                session_id="session-123",
                correlation_id="req-456"
            )
        """
        import asyncio

        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create task and wait
                # (useful in async contexts calling sync method)
                task = loop.create_task(
                    self.invoke_subagent(
                        subagent_name=subagent_name,
                        task_description=task_description,
                        context=context,
                        session_id=session_id,
                        correlation_id=correlation_id,
                        metadata=metadata
                    )
                )
                # Note: This won't actually work in sync context
                # Better to use asyncio.run() in new loop
                logger.warning("Called sync method in async context - use await instead")
                return SubagentInvocationResult.error_result(
                    subagent_name=subagent_name,
                    message="Sync invocation called in async context",
                    errors=["Use invoke_subagent() with await instead"]
                )
        except RuntimeError:
            # No event loop, create new one
            pass

        # Run in new event loop
        return asyncio.run(
            self.invoke_subagent(
                subagent_name=subagent_name,
                task_description=task_description,
                context=context,
                session_id=session_id,
                correlation_id=correlation_id,
                metadata=metadata
            )
        )


# Singleton handler instance
_handler: Optional[SubagentInvocationHandler] = None


def get_invocation_handler() -> SubagentInvocationHandler:
    """
    Get global invocation handler instance.

    Returns:
        Singleton SubagentInvocationHandler instance

    Example:
        from agentpm.providers.anthropic.claude_code.runtime.subagents import get_invocation_handler

        handler = get_invocation_handler()
        result = await handler.invoke_subagent(...)
    """
    global _handler
    if _handler is None:
        _handler = SubagentInvocationHandler()
    return _handler


def reset_invocation_handler() -> None:
    """
    Reset global handler to None.

    Useful for testing to ensure clean state.

    Example:
        # In test teardown
        reset_invocation_handler()
    """
    global _handler
    _handler = None
