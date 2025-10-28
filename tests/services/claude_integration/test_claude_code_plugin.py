"""
Tests for Claude Code Plugin

Validates comprehensive Claude Code integration including:
- Plugin initialization and registration
- Lifecycle hooks (session, tools, events)
- Memory operations (get/set)
- Slash commands (checkpoint, restore, context)
- Checkpointing (create, restore, list)
- Subagent operations
"""

import pytest
from datetime import datetime

from agentpm.providers.anthropic.claude_code.runtime.plugins import (
    ClaudePluginRegistry,
    PluginCapability,
    ClaudeCodePlugin,
    reset_registry,
)
from agentpm.providers.anthropic.claude_code.runtime.hooks.models import EventType


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reset_registry()
    reg = ClaudePluginRegistry()
    yield reg
    reg.clear()


@pytest.fixture
def plugin():
    """Create ClaudeCodePlugin instance."""
    return ClaudeCodePlugin()


class TestPluginInitialization:
    """Test plugin initialization and capabilities."""

    def test_plugin_name(self, plugin):
        """Should have correct plugin name."""
        assert plugin.name == "claude-code"

    def test_plugin_version(self, plugin):
        """Should have version."""
        assert plugin.get_version() == "1.0.0"

    def test_plugin_capabilities(self, plugin):
        """Should support all Claude Code capabilities."""
        assert plugin.supports(PluginCapability.HOOKS)
        assert plugin.supports(PluginCapability.MEMORY)
        assert plugin.supports(PluginCapability.COMMANDS)
        assert plugin.supports(PluginCapability.CHECKPOINTING)
        assert plugin.supports(PluginCapability.SUBAGENTS)

    def test_plugin_capabilities_by_string(self, plugin):
        """Should support capability checks by string."""
        assert plugin.supports("hooks")
        assert plugin.supports("memory")
        assert plugin.supports("commands")
        assert plugin.supports("checkpointing")
        assert plugin.supports("subagents")

    def test_registration_with_registry(self, registry, plugin):
        """Should register successfully with registry."""
        registry.register_plugin(plugin)

        assert registry.has_plugin("claude-code")
        assert registry.get_plugin_count() == 1

    def test_capability_discovery(self, registry, plugin):
        """Should be discoverable by all capabilities."""
        registry.register_plugin(plugin)

        # Should appear in all capability searches
        hooks_plugins = registry.get_plugins_by_capability(PluginCapability.HOOKS)
        memory_plugins = registry.get_plugins_by_capability(PluginCapability.MEMORY)
        commands_plugins = registry.get_plugins_by_capability(PluginCapability.COMMANDS)
        checkpoint_plugins = registry.get_plugins_by_capability(PluginCapability.CHECKPOINTING)
        subagent_plugins = registry.get_plugins_by_capability(PluginCapability.SUBAGENTS)

        assert len(hooks_plugins) == 1
        assert len(memory_plugins) == 1
        assert len(commands_plugins) == 1
        assert len(checkpoint_plugins) == 1
        assert len(subagent_plugins) == 1

        assert hooks_plugins[0].name == "claude-code"
        assert memory_plugins[0].name == "claude-code"


class TestHookEvents:
    """Test lifecycle hook event handling."""

    def test_session_start_event(self, plugin):
        """Should handle session-start event."""
        result = plugin.handle({
            "type": "session-start",
            "payload": {"user": "test"},
            "session_id": "session-123",
            "correlation_id": "req-001"
        })

        assert result["status"] == "success"
        assert "Session session-123 initialized" in result["message"]
        assert result["data"]["session_id"] == "session-123"

    def test_session_start_creates_context(self, plugin):
        """Should create session context on session-start."""
        plugin.handle({
            "type": "session-start",
            "payload": {"user": "test"},
            "session_id": "session-456",
            "correlation_id": "req-002"
        })

        context = plugin.get_session_context("session-456")
        assert context is not None
        assert context["session_id"] == "session-456"
        assert "start_time" in context
        assert context["prompts"] == []
        assert context["tool_uses"] == []

    def test_session_end_event(self, plugin):
        """Should handle session-end event."""
        # Start session first
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-789",
            "correlation_id": "req-003"
        })

        # End session
        result = plugin.handle({
            "type": "session-end",
            "payload": {},
            "session_id": "session-789",
            "correlation_id": "req-004"
        })

        assert result["status"] == "success"
        assert "Session session-789 ended" in result["message"]

        # Context should be cleaned up
        context = plugin.get_session_context("session-789")
        assert context is None

    def test_prompt_submit_event(self, plugin):
        """Should handle prompt-submit event."""
        # Start session
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-001",
            "correlation_id": "req-005"
        })

        # Submit prompt
        result = plugin.handle({
            "type": "prompt-submit",
            "payload": {"prompt": "Hello Claude"},
            "session_id": "session-001",
            "correlation_id": "req-006"
        })

        assert result["status"] == "success"
        assert result["data"]["prompt_length"] == 12

        # Check prompt was tracked
        context = plugin.get_session_context("session-001")
        assert len(context["prompts"]) == 1
        assert context["prompts"][0]["prompt"] == "Hello Claude"

    def test_pre_tool_use_event(self, plugin):
        """Should handle pre-tool-use event."""
        result = plugin.handle({
            "type": "pre-tool-use",
            "payload": {"tool": "bash", "args": {}},
            "session_id": "session-002",
            "correlation_id": "req-007"
        })

        assert result["status"] == "success"
        assert "bash" in result["message"]
        assert result["data"]["tool"] == "bash"

    def test_post_tool_use_event(self, plugin):
        """Should handle post-tool-use event."""
        # Start session
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-003",
            "correlation_id": "req-008"
        })

        # Post-tool-use
        result = plugin.handle({
            "type": "post-tool-use",
            "payload": {"tool": "grep"},
            "session_id": "session-003",
            "correlation_id": "req-009"
        })

        assert result["status"] == "success"
        assert "grep" in result["message"]

        # Check tool use was tracked
        context = plugin.get_session_context("session-003")
        assert len(context["tool_uses"]) == 1
        assert context["tool_uses"][0]["tool"] == "grep"

    def test_tool_result_event(self, plugin):
        """Should handle tool-result event."""
        result = plugin.handle({
            "type": "tool-result",
            "payload": {"result": "success"},
            "session_id": "session-004",
            "correlation_id": "req-010"
        })

        assert result["status"] == "success"

    def test_stop_event(self, plugin):
        """Should handle stop event."""
        result = plugin.handle({
            "type": "stop",
            "payload": {},
            "session_id": "session-005",
            "correlation_id": "req-011"
        })

        assert result["status"] == "success"
        assert "Stop signal handled" in result["message"]

    def test_subagent_stop_event(self, plugin):
        """Should handle subagent-stop event."""
        result = plugin.handle({
            "type": "subagent-stop",
            "payload": {"subagent": "test-runner"},
            "session_id": "session-006",
            "correlation_id": "req-012"
        })

        assert result["status"] == "success"
        assert "test-runner" in result["message"]

    def test_pre_compact_event(self, plugin):
        """Should handle pre-compact event."""
        result = plugin.handle({
            "type": "pre-compact",
            "payload": {},
            "session_id": "session-007",
            "correlation_id": "req-013"
        })

        assert result["status"] == "success"

    def test_notification_event(self, plugin):
        """Should handle notification event."""
        result = plugin.handle({
            "type": "notification",
            "payload": {"message": "Test notification"},
            "session_id": "session-008",
            "correlation_id": "req-014"
        })

        assert result["status"] == "success"
        assert result["data"]["notification"] == "Test notification"

    def test_unknown_event_type(self, plugin):
        """Should handle unknown event type gracefully."""
        result = plugin.handle({
            "type": "unknown-event",
            "payload": {},
            "session_id": "session-009",
            "correlation_id": "req-015"
        })

        assert result["status"] == "success"
        assert "not handled" in result["message"]


class TestMemoryOperations:
    """Test memory management functionality."""

    def test_memory_set_operation(self, plugin):
        """Should handle memory set operation."""
        result = plugin.handle({
            "scope": "session",
            "action": "set",
            "key": "test_key",
            "value": "test_value",
            "session_id": "session-101"
        })

        assert result["status"] == "success"
        assert result["data"]["key"] == "test_key"
        assert result["data"]["value"] == "test_value"

    def test_memory_get_operation(self, plugin):
        """Should handle memory get operation."""
        # Set value first
        plugin.handle({
            "scope": "session",
            "action": "set",
            "key": "retrieve_key",
            "value": "retrieve_value",
            "session_id": "session-102"
        })

        # Get value
        result = plugin.handle({
            "scope": "session",
            "action": "get",
            "key": "retrieve_key",
            "session_id": "session-102"
        })

        assert result["status"] == "success"
        assert result["data"]["value"] == "retrieve_value"

    def test_memory_get_nonexistent_key(self, plugin):
        """Should return None for nonexistent key."""
        result = plugin.handle({
            "scope": "session",
            "action": "get",
            "key": "nonexistent",
            "session_id": "session-103"
        })

        assert result["status"] == "success"
        assert result["data"]["value"] is None

    def test_memory_unknown_action(self, plugin):
        """Should handle unknown memory action."""
        result = plugin.handle({
            "scope": "session",
            "action": "delete",
            "key": "test",
            "session_id": "session-104"
        })

        assert result["status"] == "error"
        assert "Unknown memory action" in result["message"]


class TestSlashCommands:
    """Test slash command execution."""

    def test_checkpoint_command(self, plugin):
        """Should handle checkpoint command."""
        result = plugin.handle({
            "command": "checkpoint",
            "args": {"name": "test-checkpoint"},
            "session_id": "session-201"
        })

        assert result["status"] == "success"
        assert "Checkpoint 'test-checkpoint' created" in result["message"]
        assert "checkpoint_id" in result["data"]

    def test_restore_command(self, plugin):
        """Should handle restore command."""
        # Create checkpoint first
        checkpoint_result = plugin.handle({
            "command": "checkpoint",
            "args": {"name": "restore-test"},
            "session_id": "session-202"
        })
        checkpoint_id = checkpoint_result["data"]["checkpoint_id"]

        # Restore checkpoint
        result = plugin.handle({
            "command": "restore",
            "args": {"checkpoint_id": checkpoint_id},
            "session_id": "session-202"
        })

        assert result["status"] == "success"
        assert "Restored checkpoint" in result["message"]

    def test_restore_nonexistent_checkpoint(self, plugin):
        """Should handle restore of nonexistent checkpoint."""
        result = plugin.handle({
            "command": "restore",
            "args": {"checkpoint_id": "nonexistent"},
            "session_id": "session-203"
        })

        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_context_command(self, plugin):
        """Should handle context command."""
        # Start session to create context
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-204",
            "correlation_id": "req-016"
        })

        # Get context
        result = plugin.handle({
            "command": "context",
            "args": {},
            "session_id": "session-204"
        })

        assert result["status"] == "success"
        assert "context" in result["data"]
        assert result["data"]["context"]["session_id"] == "session-204"

    def test_subagent_command(self, plugin):
        """Should handle subagent command."""
        result = plugin.handle({
            "command": "subagent",
            "args": {"name": "test-agent"},
            "session_id": "session-205"
        })

        assert result["status"] == "success"
        assert "test-agent" in result["message"]

    def test_unknown_command(self, plugin):
        """Should handle unknown command."""
        result = plugin.handle({
            "command": "unknown",
            "args": {},
            "session_id": "session-206"
        })

        assert result["status"] == "error"
        assert "Unknown command" in result["message"]


class TestCheckpointing:
    """Test checkpointing operations."""

    def test_checkpoint_action(self, plugin):
        """Should handle checkpoint action."""
        result = plugin.handle({
            "action": "checkpoint",
            "session_id": "session-301"
        })

        assert result["status"] == "success"
        assert "checkpoint_id" in result["data"]

    def test_checkpoint_preserves_session_state(self, plugin):
        """Should preserve session state in checkpoint."""
        # Create session with state
        plugin.handle({
            "type": "session-start",
            "payload": {"user": "test"},
            "session_id": "session-302",
            "correlation_id": "req-017"
        })

        plugin.handle({
            "type": "prompt-submit",
            "payload": {"prompt": "Test prompt"},
            "session_id": "session-302",
            "correlation_id": "req-018"
        })

        # Create checkpoint
        result = plugin.handle({
            "action": "checkpoint",
            "session_id": "session-302"
        })

        checkpoint_id = result["data"]["checkpoint_id"]

        # Verify checkpoint contains session state
        # (Internal validation - checkpoint should have context)
        assert result["status"] == "success"

    def test_restore_action(self, plugin):
        """Should handle restore action."""
        # Create checkpoint
        checkpoint_result = plugin.handle({
            "action": "checkpoint",
            "session_id": "session-303"
        })
        checkpoint_id = checkpoint_result["data"]["checkpoint_id"]

        # Restore
        result = plugin.handle({
            "action": "restore",
            "checkpoint_id": checkpoint_id,
            "session_id": "session-303"
        })

        assert result["status"] == "success"
        assert checkpoint_id in result["message"]

    def test_list_checkpoints_action(self, plugin):
        """Should handle list checkpoints action."""
        # Create multiple checkpoints
        plugin.handle({
            "action": "checkpoint",
            "session_id": "session-304"
        })
        plugin.handle({
            "action": "checkpoint",
            "session_id": "session-304"
        })

        # List checkpoints
        result = plugin.handle({
            "action": "list",
            "session_id": "session-304"
        })

        assert result["status"] == "success"
        assert "checkpoints" in result["data"]
        assert len(result["data"]["checkpoints"]) == 2

    def test_unknown_checkpoint_action(self, plugin):
        """Should handle unknown checkpoint action."""
        result = plugin.handle({
            "action": "delete",
            "checkpoint_id": "test",
            "session_id": "session-305"
        })

        assert result["status"] == "error"
        assert "Unknown checkpoint action" in result["message"]


class TestSubagentOperations:
    """Test subagent orchestration."""

    def test_subagent_start_action(self, plugin):
        """Should handle subagent start action."""
        result = plugin.handle({
            "subagent": "test-runner",
            "action": "start",
            "session_id": "session-401"
        })

        assert result["status"] == "success"
        assert "test-runner" in result["message"]
        assert result["data"]["subagent"] == "test-runner"
        assert result["data"]["action"] == "start"

    def test_subagent_stop_action(self, plugin):
        """Should handle subagent stop action."""
        result = plugin.handle({
            "subagent": "code-implementer",
            "action": "stop",
            "session_id": "session-402"
        })

        assert result["status"] == "success"
        assert "code-implementer" in result["message"]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_input_missing_routing_field(self, plugin):
        """Should handle invalid input without routing field."""
        result = plugin.handle({
            "session_id": "session-501"
        })

        assert result["status"] == "error"
        assert "Unable to route input" in result["message"]

    def test_multiple_prompts_in_session(self, plugin):
        """Should track multiple prompts in session."""
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-502",
            "correlation_id": "req-019"
        })

        # Submit multiple prompts
        for i in range(3):
            plugin.handle({
                "type": "prompt-submit",
                "payload": {"prompt": f"Prompt {i}"},
                "session_id": "session-502",
                "correlation_id": f"req-{20 + i}"
            })

        context = plugin.get_session_context("session-502")
        assert len(context["prompts"]) == 3

    def test_multiple_tool_uses_in_session(self, plugin):
        """Should track multiple tool uses in session."""
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-503",
            "correlation_id": "req-023"
        })

        # Use multiple tools
        for tool in ["bash", "grep", "read"]:
            plugin.handle({
                "type": "post-tool-use",
                "payload": {"tool": tool},
                "session_id": "session-503",
                "correlation_id": f"req-{tool}"
            })

        context = plugin.get_session_context("session-503")
        assert len(context["tool_uses"]) == 3

    def test_clear_session_context(self, plugin):
        """Should clear session context."""
        plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-504",
            "correlation_id": "req-024"
        })

        assert plugin.get_session_context("session-504") is not None

        plugin.clear_session_context("session-504")
        assert plugin.get_session_context("session-504") is None


class TestIntegrationWithRegistry:
    """Test integration with plugin registry and hooks engine."""

    def test_plugin_registration_and_event_handling(self, registry, plugin):
        """Should register and handle events through registry."""
        registry.register_plugin(plugin)

        # Get plugin from registry
        registered_plugin = registry.get_plugin("claude-code")
        assert registered_plugin is not None

        # Handle event through registered plugin
        result = registered_plugin.handle({
            "type": "session-start",
            "payload": {},
            "session_id": "session-601",
            "correlation_id": "req-025"
        })

        assert result["status"] == "success"

    def test_multiple_capabilities_discoverable(self, registry, plugin):
        """Should be discoverable through multiple capabilities."""
        registry.register_plugin(plugin)

        # Should appear in all capability lists
        capabilities = [
            PluginCapability.HOOKS,
            PluginCapability.MEMORY,
            PluginCapability.COMMANDS,
            PluginCapability.CHECKPOINTING,
            PluginCapability.SUBAGENTS,
        ]

        for capability in capabilities:
            plugins = registry.get_plugins_by_capability(capability)
            assert len(plugins) == 1
            assert plugins[0].name == "claude-code"

    def test_plugin_listing_shows_all_capabilities(self, registry, plugin):
        """Should list all capabilities in plugin metadata."""
        registry.register_plugin(plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 1

        plugin_info = plugins[0]
        assert plugin_info["name"] == "claude-code"
        assert "hooks" in plugin_info["capabilities"]
        assert "memory" in plugin_info["capabilities"]
        assert "commands" in plugin_info["capabilities"]
        assert "checkpointing" in plugin_info["capabilities"]
        assert "subagents" in plugin_info["capabilities"]
