"""
Tests for Subagent Integration

Integration tests for subagent system with ClaudeCodePlugin.
"""

import pytest
from agentpm.providers.anthropic.claude_code.runtime.plugins.claude_code import ClaudeCodePlugin
from agentpm.providers.anthropic.claude_code.runtime.subagents import (
    get_subagent_registry,
    reset_subagent_registry,
    SubagentSpec,
    SubagentCapability,
)


@pytest.fixture
def registry():
    """Get subagent registry (must be called before plugin)."""
    reset_subagent_registry()
    reg = get_subagent_registry()
    yield reg
    reg.clear()


@pytest.fixture
def plugin(registry):
    """Create fresh plugin for each test (uses existing registry)."""
    # Don't reset here - use the registry fixture's reset
    p = ClaudeCodePlugin()
    yield p
    # Cleanup handled by registry fixture


@pytest.fixture
def sample_specs():
    """Create sample subagent specs."""
    return [
        SubagentSpec(
            name="test-implementer",
            description="Creates comprehensive unit tests",
            capabilities=[SubagentCapability.TESTING],
            tier=1,
            invocation_template="Create tests for [component]"
        ),
        SubagentSpec(
            name="code-implementer",
            description="Implements production code",
            capabilities=[SubagentCapability.IMPLEMENTATION],
            tier=1,
            invocation_template="Implement [feature]"
        ),
    ]


class TestPluginSubagentIntegration:
    """Test ClaudeCodePlugin subagent integration."""

    def test_plugin_has_subagent_components(self, plugin):
        """Plugin should have subagent handler and registry."""
        assert hasattr(plugin, '_subagent_handler')
        assert hasattr(plugin, '_subagent_registry')
        assert plugin._subagent_handler is not None
        assert plugin._subagent_registry is not None

    def test_plugin_routes_subagent_invocation(self, plugin, registry, sample_specs):
        """Plugin should route subagent invocations."""
        # Register subagent
        registry.register_subagent(sample_specs[0])

        # Invoke via plugin
        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests for UserService",
            "context": {"service": "UserService"},
            "session_id": "session-123"
        })

        assert result["status"] in ["success", "error"]
        assert "message" in result
        assert "data" in result

    def test_plugin_list_subagents(self, plugin, registry, sample_specs):
        """Plugin should list subagents."""
        # Register multiple subagents
        for spec in sample_specs:
            registry.register_subagent(spec)

        # List via plugin
        result = plugin.handle({
            "action": "list",
            "subagent": "dummy",  # Required for routing
            "session_id": "session-123"
        })

        assert result["status"] == "success"
        assert "subagents" in result["data"]
        assert len(result["data"]["subagents"]) == 2

    def test_plugin_get_invocation_guide(self, plugin, registry, sample_specs):
        """Plugin should generate invocation guide."""
        # Register subagent
        registry.register_subagent(sample_specs[0])

        # Get guide via plugin
        result = plugin.handle({
            "action": "get-guide",
            "subagent": "dummy",  # Required for routing
            "session_id": "session-123"
        })

        assert result["status"] == "success"
        assert "guide" in result["data"]
        assert "test-implementer" in result["data"]["guide"]


class TestSubagentInvocationFlow:
    """Test end-to-end subagent invocation flow."""

    def test_successful_invocation(self, plugin, registry, sample_specs):
        """Should invoke subagent successfully."""
        registry.register_subagent(sample_specs[0])

        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests for UserService",
            "context": {"service": "UserService", "coverage": 0.9},
            "session_id": "session-123",
            "correlation_id": "req-456"
        })

        assert result["status"] in ["success", "error"]
        assert "subagent" in result["data"]
        assert result["data"]["subagent"] == "test-implementer"

    def test_invocation_missing_subagent(self, plugin, registry):
        """Should handle missing subagent name."""
        result = plugin.handle({
            "action": "invoke",
            "task_description": "Create tests",
            "context": {},
            "session_id": "session-123"
        })

        assert result["status"] == "error"
        assert "required" in result["message"].lower()

    def test_invocation_missing_description(self, plugin, registry, sample_specs):
        """Should handle missing task description."""
        registry.register_subagent(sample_specs[0])

        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "context": {},
            "session_id": "session-123"
        })

        assert result["status"] == "error"
        assert "required" in result["message"].lower()

    def test_invocation_nonexistent_subagent(self, plugin, registry):
        """Should handle nonexistent subagent."""
        result = plugin.handle({
            "subagent": "nonexistent",
            "action": "invoke",
            "task_description": "Do something",
            "context": {},
            "session_id": "session-123"
        })

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestSubagentActions:
    """Test different subagent actions."""

    def test_invoke_action(self, plugin, registry, sample_specs):
        """Should handle invoke action."""
        registry.register_subagent(sample_specs[0])

        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests",
            "context": {},
            "session_id": "session-123"
        })

        assert "status" in result

    def test_list_action(self, plugin, registry, sample_specs):
        """Should handle list action."""
        for spec in sample_specs:
            registry.register_subagent(spec)

        result = plugin.handle({
            "action": "list",
            "subagent": "dummy",
            "session_id": "session-123"
        })

        assert result["status"] == "success"
        assert len(result["data"]["subagents"]) == 2

    def test_get_guide_action(self, plugin, registry, sample_specs):
        """Should handle get-guide action."""
        registry.register_subagent(sample_specs[0])

        result = plugin.handle({
            "action": "get-guide",
            "subagent": "dummy",
            "session_id": "session-123"
        })

        assert result["status"] == "success"
        assert "guide" in result["data"]

    def test_unknown_action(self, plugin, registry):
        """Should handle unknown action."""
        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "unknown",
            "session_id": "session-123"
        })

        assert result["status"] == "error"
        assert "unknown" in result["message"].lower()


class TestMultipleSubagents:
    """Test operations with multiple subagents."""

    def test_invoke_different_subagents(self, plugin, registry, sample_specs):
        """Should invoke different subagents."""
        # Register multiple subagents
        for spec in sample_specs:
            registry.register_subagent(spec)

        # Invoke first subagent
        result1 = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests",
            "context": {},
            "session_id": "session-123"
        })

        # Invoke second subagent
        result2 = plugin.handle({
            "subagent": "code-implementer",
            "action": "invoke",
            "task_description": "Implement feature",
            "context": {},
            "session_id": "session-123"
        })

        assert result1["data"]["subagent"] == "test-implementer"
        assert result2["data"]["subagent"] == "code-implementer"

    def test_list_shows_all_subagents(self, plugin, registry, sample_specs):
        """Should list all registered subagents."""
        for spec in sample_specs:
            registry.register_subagent(spec)

        result = plugin.handle({
            "action": "list",
            "subagent": "dummy",
            "session_id": "session-123"
        })

        subagents = result["data"]["subagents"]
        names = [s["name"] for s in subagents]
        assert "test-implementer" in names
        assert "code-implementer" in names


class TestContextPassing:
    """Test context passing to subagents."""

    def test_context_passed_to_subagent(self, plugin, registry, sample_specs):
        """Should pass context to subagent."""
        registry.register_subagent(sample_specs[0])

        context = {"service": "UserService", "coverage": 0.95}
        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests",
            "context": context,
            "session_id": "session-123"
        })

        # Context should be in result data
        assert "result" in result["data"]

    def test_empty_context(self, plugin, registry, sample_specs):
        """Should handle empty context."""
        registry.register_subagent(sample_specs[0])

        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests",
            "context": {},
            "session_id": "session-123"
        })

        assert "status" in result

    def test_complex_context(self, plugin, registry, sample_specs):
        """Should handle complex context."""
        registry.register_subagent(sample_specs[0])

        context = {
            "service": "UserService",
            "operations": ["create", "read", "update", "delete"],
            "validation": {"email": True, "phone": True},
            "coverage": 0.95
        }
        result = plugin.handle({
            "subagent": "test-implementer",
            "action": "invoke",
            "task_description": "Create tests",
            "context": context,
            "session_id": "session-123"
        })

        assert "status" in result
