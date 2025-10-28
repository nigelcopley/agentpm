"""
Tests for Hooks Engine

Validates event normalization, dispatch, and aggregation.
"""

import pytest
from datetime import datetime

from agentpm.providers.anthropic.claude_code.runtime.hooks import (
    HooksEngine,
    HookEvent,
    EventResult,
    EventType,
    reset_hooks_engine,
)
from agentpm.providers.anthropic.claude_code.runtime.plugins import (
    BaseClaudePlugin,
    PluginCapability,
    get_registry,
    reset_registry,
)


class MockHooksPlugin(BaseClaudePlugin):
    """Mock plugin that handles hooks."""

    def __init__(self, name="test-hooks", should_fail=False):
        super().__init__(name=name)
        self.register_capability(PluginCapability.HOOKS)
        self.events_received = []
        self.should_fail = should_fail

    def handle(self, input_data):
        self.events_received.append(input_data)

        if self.should_fail:
            raise RuntimeError("Plugin intentionally failed")

        return {
            "status": "success",
            "event_type": input_data.get("type"),
            "processed_at": datetime.now().isoformat()
        }


@pytest.fixture
def engine():
    """Create fresh hooks engine for each test."""
    reset_hooks_engine()
    reset_registry()
    eng = HooksEngine()
    yield eng
    eng.clear_handlers()


@pytest.fixture
def hooks_plugin():
    """Create mock hooks plugin."""
    return MockHooksPlugin()


@pytest.fixture
def failing_plugin():
    """Create mock plugin that fails."""
    return MockHooksPlugin(name="failing-hooks", should_fail=True)


class TestEventNormalization:
    """Test event normalization and validation."""

    def test_normalize_event_with_enum(self, engine):
        """Should normalize event with EventType enum."""
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={"user": "claude"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        event_dict = result.data["event"]
        assert event_dict["type"] == "session-start"
        assert event_dict["session_id"] == "session-123"

    def test_normalize_event_with_string(self, engine):
        """Should normalize event with string type."""
        result = engine.dispatch_event(
            event_type="custom-event",
            payload={"custom": "data"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        event_dict = result.data["event"]
        assert event_dict["type"] == "custom-event"

    def test_normalize_event_with_metadata(self, engine):
        """Should include metadata in normalized event."""
        result = engine.dispatch_event(
            event_type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "Hello"},
            session_id="session-123",
            correlation_id="req-456",
            metadata={"source": "test", "priority": "high"}
        )

        assert result.success
        event_dict = result.data["event"]
        assert event_dict["metadata"]["source"] == "test"
        assert event_dict["metadata"]["priority"] == "high"

    def test_missing_session_id(self, engine):
        """Should handle missing session_id."""
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="",  # Empty session ID
            correlation_id="req-456"
        )

        assert not result.success
        assert "session_id is required" in result.message


class TestEventDispatching:
    """Test event dispatch to plugins."""

    def test_dispatch_to_registered_plugin(self, engine, hooks_plugin):
        """Should dispatch event to registered plugin."""
        # Register plugin
        registry = get_registry()
        registry.register_plugin(hooks_plugin)

        # Dispatch event
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={"session_id": "session-123"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert len(hooks_plugin.events_received) == 1
        assert hooks_plugin.events_received[0]["type"] == "session-start"

    def test_dispatch_to_multiple_plugins(self, engine):
        """Should dispatch to all registered hook plugins."""
        # Register multiple plugins
        registry = get_registry()
        plugin1 = MockHooksPlugin(name="plugin-1")
        plugin2 = MockHooksPlugin(name="plugin-2")
        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)

        # Dispatch event
        result = engine.dispatch_event(
            event_type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "test"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert len(plugin1.events_received) == 1
        assert len(plugin2.events_received) == 1

    def test_dispatch_with_no_plugins(self, engine):
        """Should handle dispatch when no plugins registered."""
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert "No hook plugins or handlers registered" in result.message

    def test_dispatch_when_disabled(self, engine, hooks_plugin):
        """Should skip dispatch when engine disabled."""
        registry = get_registry()
        registry.register_plugin(hooks_plugin)

        # Disable engine
        engine.disable()

        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert "disabled" in result.message.lower()
        assert len(hooks_plugin.events_received) == 0


class TestCustomHandlers:
    """Test custom event handler registration."""

    def test_register_custom_handler(self, engine):
        """Should register and call custom handler."""
        events = []

        def on_session_start(event: HookEvent):
            events.append(event)
            return {"handled": True}

        engine.register_handler(EventType.SESSION_START, on_session_start)

        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert len(events) == 1
        assert events[0].session_id == "session-123"

    def test_register_multiple_handlers(self, engine):
        """Should call all registered handlers for event type."""
        calls = []

        def handler1(event):
            calls.append("handler1")
            return {}

        def handler2(event):
            calls.append("handler2")
            return {}

        engine.register_handler(EventType.SESSION_START, handler1)
        engine.register_handler(EventType.SESSION_START, handler2)

        engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert "handler1" in calls
        assert "handler2" in calls

    def test_unregister_handler(self, engine):
        """Should unregister custom handler."""
        calls = []

        def handler(event):
            calls.append("called")
            return {}

        # Register and call
        engine.register_handler(EventType.SESSION_START, handler)
        engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )
        assert len(calls) == 1

        # Unregister and call again
        engine.unregister_handler(EventType.SESSION_START, handler)
        engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-456",
            correlation_id="req-789"
        )
        assert len(calls) == 1  # Should not increase

    def test_clear_handlers(self, engine):
        """Should clear all custom handlers."""
        def handler(event):
            return {}

        engine.register_handler(EventType.SESSION_START, handler)
        engine.register_handler(EventType.PROMPT_SUBMIT, handler)

        engine.clear_handlers()

        # Handlers should not be called
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        # No custom handlers, only plugin system response
        assert result.success


class TestErrorHandling:
    """Test error handling in event dispatch."""

    def test_plugin_failure(self, engine, failing_plugin):
        """Should handle plugin failures gracefully."""
        registry = get_registry()
        registry.register_plugin(failing_plugin)

        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert not result.success
        assert len(result.errors) > 0
        assert "intentionally failed" in result.errors[0]

    def test_partial_plugin_failure(self, engine, hooks_plugin, failing_plugin):
        """Should continue with other plugins when one fails."""
        registry = get_registry()
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(failing_plugin)

        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        # Result should indicate errors but show partial success
        assert not result.success
        assert result.data["success_count"] == 1
        assert result.data["error_count"] == 1
        assert len(hooks_plugin.events_received) == 1  # Successful plugin was called

    def test_custom_handler_failure(self, engine):
        """Should handle custom handler failures gracefully."""
        def failing_handler(event):
            raise ValueError("Handler failed")

        engine.register_handler(EventType.SESSION_START, failing_handler)

        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={},
            session_id="session-123",
            correlation_id="req-456"
        )

        # Should complete despite handler failure
        assert not result.success


class TestEngineLifecycle:
    """Test engine enable/disable lifecycle."""

    def test_engine_enabled_by_default(self, engine):
        """Should be enabled by default."""
        assert engine.is_enabled()

    def test_disable_engine(self, engine):
        """Should disable event processing."""
        engine.disable()
        assert not engine.is_enabled()

    def test_enable_engine(self, engine):
        """Should enable event processing."""
        engine.disable()
        engine.enable()
        assert engine.is_enabled()


class TestEventTypes:
    """Test all supported event types."""

    @pytest.mark.parametrize("event_type", [
        EventType.SESSION_START,
        EventType.SESSION_END,
        EventType.PROMPT_SUBMIT,
        EventType.TOOL_RESULT,
        EventType.PRE_TOOL_USE,
        EventType.POST_TOOL_USE,
        EventType.STOP,
        EventType.SUBAGENT_STOP,
        EventType.PRE_COMPACT,
        EventType.NOTIFICATION,
    ])
    def test_all_event_types(self, engine, hooks_plugin, event_type):
        """Should handle all documented event types."""
        registry = get_registry()
        registry.register_plugin(hooks_plugin)

        result = engine.dispatch_event(
            event_type=event_type,
            payload={"test": "data"},
            session_id="session-123",
            correlation_id="req-456"
        )

        assert result.success
        assert len(hooks_plugin.events_received) == 1
        assert hooks_plugin.events_received[0]["type"] == event_type.value


class TestHookEventModel:
    """Test HookEvent model functionality."""

    def test_hook_event_creation(self):
        """Should create HookEvent with all fields."""
        event = HookEvent(
            type=EventType.SESSION_START,
            payload={"user": "claude"},
            session_id="session-123",
            correlation_id="req-456",
            metadata={"source": "test"}
        )

        assert event.type == EventType.SESSION_START
        assert event.payload["user"] == "claude"
        assert event.session_id == "session-123"
        assert event.correlation_id == "req-456"
        assert event.metadata["source"] == "test"

    def test_hook_event_to_dict(self):
        """Should convert event to dictionary."""
        event = HookEvent(
            type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "test"},
            session_id="session-123",
            correlation_id="req-456"
        )

        event_dict = event.to_dict()
        assert event_dict["type"] == "prompt-submit"
        assert event_dict["payload"]["prompt"] == "test"
        assert event_dict["session_id"] == "session-123"

    def test_hook_event_from_dict(self):
        """Should create event from dictionary."""
        event = HookEvent.from_dict({
            "type": "session-start",
            "payload": {"user": "claude"},
            "session_id": "session-123",
            "correlation_id": "req-456"
        })

        assert event.type == EventType.SESSION_START
        assert event.payload["user"] == "claude"


class TestEventResult:
    """Test EventResult model functionality."""

    def test_success_result(self):
        """Should create success result."""
        result = EventResult.success_result(
            message="Operation successful",
            data={"count": 5}
        )

        assert result.success
        assert result.message == "Operation successful"
        assert result.data["count"] == 5

    def test_error_result(self):
        """Should create error result."""
        result = EventResult.error_result(
            message="Operation failed",
            errors=["Error 1", "Error 2"]
        )

        assert not result.success
        assert result.message == "Operation failed"
        assert len(result.errors) == 2

    def test_result_to_dict(self):
        """Should convert result to dictionary."""
        result = EventResult(
            success=True,
            message="Success",
            data={"key": "value"}
        )

        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["message"] == "Success"
        assert result_dict["data"]["key"] == "value"
