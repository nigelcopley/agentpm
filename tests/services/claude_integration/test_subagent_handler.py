"""
Tests for Subagent Invocation Handler

Tests subagent invocation, request normalization, and result handling.
"""

import pytest
import asyncio
from agentpm.providers.anthropic.claude_code.runtime.subagents import (
    SubagentInvocationHandler,
    SubagentRegistry,
    SubagentSpec,
    SubagentCapability,
    SubagentInvocationRequest,
    SubagentInvocationResult,
    get_invocation_handler,
    reset_invocation_handler,
    get_subagent_registry,
    reset_subagent_registry,
)


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reset_subagent_registry()
    reg = get_subagent_registry()
    yield reg
    reg.clear()


@pytest.fixture
def handler(registry):
    """Create fresh handler for each test."""
    reset_invocation_handler()
    h = get_invocation_handler()
    yield h


@pytest.fixture
def sample_spec():
    """Create sample subagent spec."""
    return SubagentSpec(
        name="test-implementer",
        description="Creates comprehensive unit tests",
        capabilities=[SubagentCapability.TESTING],
        tier=1,
        invocation_template="Create tests for [component]"
    )


class TestHandlerBasics:
    """Test basic handler operations."""

    def test_handler_singleton(self):
        """Handler should be singleton."""
        reset_invocation_handler()
        h1 = get_invocation_handler()
        h2 = get_invocation_handler()
        assert h1 is h2

    def test_handler_initialization(self, handler):
        """Handler should initialize successfully."""
        assert handler is not None


class TestSubagentInvocation:
    """Test subagent invocation (async)."""

    @pytest.mark.asyncio
    async def test_invoke_existing_subagent(self, handler, registry, sample_spec):
        """Should invoke registered subagent."""
        registry.register_subagent(sample_spec)

        result = await handler.invoke_subagent(
            subagent_name="test-implementer",
            task_description="Create tests for UserService",
            context={"service": "UserService"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is True
        assert result.subagent_name == "test-implementer"
        assert "test-implementer" in result.message.lower()

    @pytest.mark.asyncio
    async def test_invoke_nonexistent_subagent(self, handler, registry):
        """Should return error for nonexistent subagent."""
        result = await handler.invoke_subagent(
            subagent_name="nonexistent",
            task_description="Do something",
            context={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is False
        assert "not found" in result.message.lower()
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_invoke_with_context(self, handler, registry, sample_spec):
        """Should pass context to subagent."""
        registry.register_subagent(sample_spec)

        context = {"service": "UserService", "coverage": 0.9}
        result = await handler.invoke_subagent(
            subagent_name="test-implementer",
            task_description="Create tests",
            context=context,
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is True
        assert "context" in result.data
        assert result.data["context"] == context

    @pytest.mark.asyncio
    async def test_invoke_with_metadata(self, handler, registry, sample_spec):
        """Should handle metadata."""
        registry.register_subagent(sample_spec)

        metadata = {"priority": "high", "requester": "user-123"}
        result = await handler.invoke_subagent(
            subagent_name="test-implementer",
            task_description="Create tests",
            context={},
            session_id="session-123",
            correlation_id="req-456",
            metadata=metadata
        )

        assert result.success is True


class TestSyncInvocation:
    """Test synchronous invocation wrapper."""

    def test_invoke_sync(self, handler, registry, sample_spec):
        """Should invoke subagent synchronously."""
        registry.register_subagent(sample_spec)

        result = handler.invoke_subagent_sync(
            subagent_name="test-implementer",
            task_description="Create tests for UserService",
            context={"service": "UserService"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is True
        assert result.subagent_name == "test-implementer"

    def test_invoke_sync_nonexistent(self, handler, registry):
        """Should handle nonexistent subagent synchronously."""
        result = handler.invoke_subagent_sync(
            subagent_name="nonexistent",
            task_description="Do something",
            context={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is False
        assert "not found" in result.message.lower()


class TestInvocationRequest:
    """Test SubagentInvocationRequest model."""

    def test_request_creation(self):
        """Should create request with valid data."""
        request = SubagentInvocationRequest(
            subagent_name="test-implementer",
            task_description="Create tests",
            context={"service": "UserService"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert request.subagent_name == "test-implementer"
        assert request.task_description == "Create tests"
        assert request.context == {"service": "UserService"}

    def test_request_default_context(self):
        """Should handle empty context."""
        request = SubagentInvocationRequest(
            subagent_name="test-implementer",
            task_description="Create tests",
            session_id="session-123",
            correlation_id="req-456"
        )

        assert request.context == {}

    def test_request_default_metadata(self):
        """Should handle empty metadata."""
        request = SubagentInvocationRequest(
            subagent_name="test-implementer",
            task_description="Create tests",
            session_id="session-123",
            correlation_id="req-456"
        )

        assert request.metadata == {}


class TestInvocationResult:
    """Test SubagentInvocationResult model."""

    def test_result_creation(self):
        """Should create result with valid data."""
        result = SubagentInvocationResult(
            success=True,
            subagent_name="test-implementer",
            message="Tests created",
            data={"tests": 15},
            artifacts=["tests/test_user.py"],
            errors=[]
        )

        assert result.success is True
        assert result.subagent_name == "test-implementer"
        assert result.data == {"tests": 15}
        assert result.artifacts == ["tests/test_user.py"]

    def test_result_success_helper(self):
        """Should create success result via helper."""
        result = SubagentInvocationResult.success_result(
            subagent_name="test-implementer",
            message="Tests created",
            data={"tests": 15},
            artifacts=["tests/test_user.py"]
        )

        assert result.success is True
        assert result.subagent_name == "test-implementer"
        assert len(result.errors) == 0

    def test_result_error_helper(self):
        """Should create error result via helper."""
        result = SubagentInvocationResult.error_result(
            subagent_name="test-implementer",
            message="Failed to create tests",
            errors=["Import error", "Syntax error"]
        )

        assert result.success is False
        assert result.subagent_name == "test-implementer"
        assert len(result.errors) == 2

    def test_result_default_data(self):
        """Should handle empty data."""
        result = SubagentInvocationResult(
            success=True,
            subagent_name="test-implementer",
            message="Success"
        )

        assert result.data == {}

    def test_result_default_artifacts(self):
        """Should handle empty artifacts."""
        result = SubagentInvocationResult(
            success=True,
            subagent_name="test-implementer",
            message="Success"
        )

        assert result.artifacts == []

    def test_result_default_errors(self):
        """Should handle empty errors."""
        result = SubagentInvocationResult(
            success=True,
            subagent_name="test-implementer",
            message="Success"
        )

        assert result.errors == []


class TestErrorHandling:
    """Test error handling in invocation."""

    @pytest.mark.asyncio
    async def test_exception_handling(self, handler, registry):
        """Should handle exceptions gracefully."""
        # Force an error by not registering subagent
        result = await handler.invoke_subagent(
            subagent_name="nonexistent",
            task_description="Test",
            context={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success is False
        assert len(result.errors) > 0


class TestSubagentCapability:
    """Test SubagentCapability enum."""

    def test_capability_values(self):
        """Should have expected capability values."""
        assert SubagentCapability.DISCOVERY.value == "discovery"
        assert SubagentCapability.PLANNING.value == "planning"
        assert SubagentCapability.IMPLEMENTATION.value == "implementation"
        assert SubagentCapability.TESTING.value == "testing"
        assert SubagentCapability.REVIEW.value == "review"

    def test_capability_in_list(self):
        """Should work in lists."""
        caps = [
            SubagentCapability.IMPLEMENTATION,
            SubagentCapability.TESTING
        ]
        assert SubagentCapability.IMPLEMENTATION in caps
        assert SubagentCapability.DOCUMENTATION not in caps
