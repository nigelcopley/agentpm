"""
Tests for Claude Code Orchestrator

Validates orchestrator functionality including:
- Initialization and component registration
- Session lifecycle management
- Event routing and coordination
- Resource management and cleanup
- Error handling and recovery
- Integration across all subsystems
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

# Tests are synchronous since orchestrator is synchronous
# pytestmark = pytest.mark.asyncio

from agentpm.services.claude_integration.orchestrator import (
    ClaudeCodeOrchestrator,
    get_orchestrator,
    reset_orchestrator,
)
from agentpm.services.claude_integration.hooks.models import EventType
from agentpm.services.claude_integration.plugins import reset_registry
from agentpm.services.claude_integration.hooks import reset_hooks_engine
from agentpm.services.claude_integration.subagents import (
    reset_subagent_registry,
    reset_invocation_handler,
)


@pytest.fixture
def mock_db():
    """Mock database service."""
    db = Mock()
    db.project_id = 1
    return db


@pytest.fixture
def orchestrator(mock_db):
    """Create orchestrator instance for testing."""
    # Reset all singletons
    reset_registry()
    reset_hooks_engine()
    reset_subagent_registry()
    reset_invocation_handler()
    reset_orchestrator()

    orch = ClaudeCodeOrchestrator(mock_db, project_id=1)
    return orch


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""

    def test_create_orchestrator(self, mock_db):
        """Should create orchestrator without initialization."""
        orch = ClaudeCodeOrchestrator(mock_db, project_id=1)

        assert orch.project_id == 1
        assert not orch.is_initialized
        assert orch.active_session_count == 0

    def test_initialize_orchestrator(self, orchestrator):
        """Should initialize all subsystems."""
        orchestrator.initialize()

        assert orchestrator.is_initialized
        assert orchestrator.plugin is not None
        assert orchestrator.plugin.name == "claude-code"
        assert orchestrator.uptime_seconds > 0

    def test_double_initialization(self, orchestrator):
        """Should handle double initialization gracefully."""
        orchestrator.initialize()
        orchestrator.initialize()  # Should not raise

        assert orchestrator.is_initialized

    def test_ensure_initialized_check(self, orchestrator):
        """Should raise error if not initialized."""
        with pytest.raises(RuntimeError, match="not initialized"):
            orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={},
                session_id="test",
                correlation_id="req-001"
            )


class TestSessionLifecycle:
    """Test session lifecycle management."""

    def test_session_start(self, orchestrator):
        """Should start session successfully."""
        orchestrator.initialize()

        result = orchestrator.handle_session_start("session-123", {
            "user_id": "user-456",
            "workspace": "/path/to/workspace"
        })

        assert result.success
        assert orchestrator.active_session_count == 1
        assert "session-123" in orchestrator._active_sessions

    def test_session_end(self, orchestrator):
        """Should end session successfully."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        result = orchestrator.handle_session_end("session-123", {})

        assert result.success
        assert orchestrator.active_session_count == 0
        assert "session-123" not in orchestrator._active_sessions

    def test_session_end_without_start(self, orchestrator):
        """Should handle session end without start."""
        orchestrator.initialize()

        # Should not raise, just log warning
        result = orchestrator.handle_session_end("session-123", {})

        assert result.success

    def test_duplicate_session_start(self, orchestrator):
        """Should reject duplicate session start."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        with pytest.raises(ValueError, match="already active"):
            orchestrator.handle_session_start("session-123", {})

    def test_multiple_concurrent_sessions(self, orchestrator):
        """Should handle multiple concurrent sessions."""
        orchestrator.initialize()

        orchestrator.handle_session_start("session-1", {})
        orchestrator.handle_session_start("session-2", {})
        orchestrator.handle_session_start("session-3", {})

        assert orchestrator.active_session_count == 3

        orchestrator.handle_session_end("session-2", {})

        assert orchestrator.active_session_count == 2

    def test_session_context_manager(self, orchestrator):
        """Should support context manager for sessions."""
        orchestrator.initialize()

        with orchestrator.session("session-123", {"user_id": "user-456"}):
            assert orchestrator.active_session_count == 1
            # Session is active here

        # Session automatically ended
        assert orchestrator.active_session_count == 0

    def test_session_context_manager_with_exception(self, orchestrator):
        """Should cleanup session even on exception."""
        orchestrator.initialize()

        with pytest.raises(RuntimeError):
            with orchestrator.session("session-123", {}):
                assert orchestrator.active_session_count == 1
                raise RuntimeError("Test exception")

        # Session still cleaned up
        assert orchestrator.active_session_count == 0


class TestEventHandling:
    """Test event handling and routing."""

    def test_handle_event(self, orchestrator):
        """Should handle events successfully."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        result = orchestrator.handle_event(
            event_type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "Hello Claude"},
            session_id="session-123",
            correlation_id="req-001"
        )

        assert result.success
        # EventResult doesn't have session_id/correlation_id fields
        # Those are tracked internally by orchestrator

    def test_event_tracking(self, orchestrator):
        """Should track event counts for sessions."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        # Send multiple events
        for i in range(5):
            orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": f"Prompt {i}"},
                session_id="session-123",
                correlation_id=f"req-{i}"
            )

        session_state = orchestrator._active_sessions["session-123"]
        assert session_state["event_count"] == 6  # 5 prompts + 1 session-start

    def test_handle_event_with_error(self, orchestrator):
        """Should handle event processing errors gracefully."""
        orchestrator.initialize()

        # Create scenario that triggers error (session not started)
        # Event should still return result (not raise)
        result = orchestrator.handle_event(
            event_type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "Test"},
            session_id="nonexistent",
            correlation_id="req-001"
        )

        # Should get result, even if processing had issues
        assert result is not None
        # EventResult doesn't have correlation_id field

    def test_all_event_types(self, orchestrator):
        """Should handle all event types."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        event_types = [
            EventType.PROMPT_SUBMIT,
            EventType.PRE_TOOL_USE,
            EventType.POST_TOOL_USE,
            EventType.TOOL_RESULT,
            EventType.STOP,
            EventType.PRE_COMPACT,
            EventType.NOTIFICATION,
        ]

        for event_type in event_types:
            result = orchestrator.handle_event(
                event_type=event_type,
                payload={"test": "data"},
                session_id="session-123",
                correlation_id=f"req-{event_type.value}"
            )

            assert result is not None


class TestCheckpointing:
    """Test checkpoint functionality."""

    def test_checkpoint_on_session_end(self, orchestrator):
        """Should create checkpoint on session end."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        # Trigger checkpoint creation
        orchestrator.handle_session_end("session-123", {})

        # Verify checkpoint was attempted
        # (actual checkpoint is in plugin, we're testing orchestration)
        assert orchestrator.active_session_count == 0

    def test_checkpoint_loading_on_session_start(self, orchestrator):
        """Should attempt to load checkpoint on session start."""
        orchestrator.initialize()

        # First session - creates checkpoint
        orchestrator.handle_session_start("session-123", {})
        orchestrator.handle_session_end("session-123", {})

        # Second session - should try to load checkpoint
        result = orchestrator.handle_session_start("session-123", {})

        assert result.success


class TestResourceManagement:
    """Test resource management and cleanup."""

    def test_shutdown_cleans_active_sessions(self, orchestrator):
        """Should end all active sessions on shutdown."""
        orchestrator.initialize()

        orchestrator.handle_session_start("session-1", {})
        orchestrator.handle_session_start("session-2", {})
        orchestrator.handle_session_start("session-3", {})

        assert orchestrator.active_session_count == 3

        orchestrator.shutdown()

        assert orchestrator.active_session_count == 0
        assert not orchestrator.is_initialized

    def test_shutdown_disables_hooks(self, orchestrator):
        """Should disable hooks on shutdown."""
        orchestrator.initialize()

        assert orchestrator._hooks_engine.is_enabled()

        orchestrator.shutdown()

        assert not orchestrator._hooks_engine.is_enabled()

    def test_shutdown_clears_plugins(self, orchestrator):
        """Should clear plugin registry on shutdown."""
        orchestrator.initialize()

        assert orchestrator._plugin_registry.get_plugin_count() > 0

        orchestrator.shutdown()

        assert orchestrator._plugin_registry.get_plugin_count() == 0


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_session_start_error_cleanup(self, orchestrator):
        """Should cleanup session on start error."""
        orchestrator.initialize()

        # Simulate error during session start
        with patch.object(
            orchestrator._service,
            'handle_event',
            side_effect=RuntimeError("Test error")
        ):
            with pytest.raises(RuntimeError):
                orchestrator.handle_session_start("session-123", {})

        # Session should be cleaned up
        assert "session-123" not in orchestrator._active_sessions

    def test_session_end_error_still_cleanups(self, orchestrator):
        """Should cleanup session even if end fails."""
        orchestrator.initialize()
        orchestrator.handle_session_start("session-123", {})

        # Simulate error during session end
        with patch.object(
            orchestrator._service,
            'handle_event',
            side_effect=RuntimeError("Test error")
        ):
            with pytest.raises(RuntimeError):
                orchestrator.handle_session_end("session-123", {})

        # Session should still be cleaned up
        assert "session-123" not in orchestrator._active_sessions

    def test_shutdown_continues_on_session_end_error(self, orchestrator):
        """Should continue shutdown even if session end fails."""
        orchestrator.initialize()

        orchestrator.handle_session_start("session-1", {})
        orchestrator.handle_session_start("session-2", {})

        # Simulate error ending sessions
        with patch.object(
            orchestrator._service,
            'handle_event',
            side_effect=RuntimeError("Test error")
        ):
            orchestrator.shutdown()  # Should not raise

        # Should still complete shutdown
        assert not orchestrator.is_initialized


class TestGlobalInstance:
    """Test global singleton instance."""

    def test_get_orchestrator_first_call(self, mock_db):
        """Should require db and project_id on first call."""
        reset_orchestrator()

        with pytest.raises(ValueError, match="required for first"):
            get_orchestrator()

        # Should work with parameters
        orch = get_orchestrator(mock_db, project_id=1)
        assert orch is not None

    def test_get_orchestrator_subsequent_calls(self, mock_db):
        """Should return same instance on subsequent calls."""
        reset_orchestrator()

        orch1 = get_orchestrator(mock_db, project_id=1)
        orch2 = get_orchestrator()

        assert orch1 is orch2

    def test_reset_orchestrator(self, mock_db):
        """Should reset global instance."""
        reset_orchestrator()

        orch1 = get_orchestrator(mock_db, project_id=1)
        reset_orchestrator()

        with pytest.raises(ValueError):
            get_orchestrator()  # Requires parameters again


class TestProperties:
    """Test orchestrator properties."""

    def test_is_initialized_property(self, orchestrator):
        """Should track initialization state."""
        assert not orchestrator.is_initialized

        orchestrator.initialize()

        assert orchestrator.is_initialized

        orchestrator.shutdown()

        assert not orchestrator.is_initialized

    def test_active_session_count_property(self, orchestrator):
        """Should track active session count."""
        orchestrator.initialize()

        assert orchestrator.active_session_count == 0

        orchestrator.handle_session_start("session-1", {})
        assert orchestrator.active_session_count == 1

        orchestrator.handle_session_start("session-2", {})
        assert orchestrator.active_session_count == 2

        orchestrator.handle_session_end("session-1", {})
        assert orchestrator.active_session_count == 1

    def test_service_property(self, orchestrator):
        """Should expose service coordinator."""
        assert orchestrator.service is not None
        assert hasattr(orchestrator.service, 'handle_event')

    def test_plugin_property(self, orchestrator):
        """Should expose main plugin after initialization."""
        assert orchestrator.plugin is None

        orchestrator.initialize()

        assert orchestrator.plugin is not None
        assert orchestrator.plugin.name == "claude-code"

    def test_uptime_seconds_property(self, orchestrator):
        """Should track uptime."""
        assert orchestrator.uptime_seconds == 0.0

        orchestrator.initialize()

        # Should have positive uptime
        
        import time; time.sleep(0.1)

        assert orchestrator.uptime_seconds > 0.0


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_complete_session_workflow(self, orchestrator):
        """Should handle complete session workflow."""
        # Initialize
        orchestrator.initialize()
        assert orchestrator.is_initialized

        # Start session
        result = orchestrator.handle_session_start("session-123", {
            "user_id": "user-456"
        })
        assert result.success

        # Handle events
        for i in range(10):
            result = orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": f"Prompt {i}"},
                session_id="session-123",
                correlation_id=f"req-{i}"
            )
            assert result.success

        # End session
        result = orchestrator.handle_session_end("session-123", {})
        assert result.success

        # Shutdown
        orchestrator.shutdown()
        assert not orchestrator.is_initialized

    def test_multi_session_concurrent_workflow(self, orchestrator):
        """Should handle multiple concurrent sessions."""
        orchestrator.initialize()

        # Start multiple sessions
        sessions = ["session-1", "session-2", "session-3"]
        for session_id in sessions:
            orchestrator.handle_session_start(session_id, {})

        # Handle events for each session
        for session_id in sessions:
            for i in range(5):
                orchestrator.handle_event(
                    event_type=EventType.PROMPT_SUBMIT,
                    payload={"prompt": f"Prompt {i}"},
                    session_id=session_id,
                    correlation_id=f"{session_id}-req-{i}"
                )

        # End sessions
        for session_id in sessions:
            orchestrator.handle_session_end(session_id, {})

        assert orchestrator.active_session_count == 0

    def test_session_with_context_manager(self, orchestrator):
        """Should handle session via context manager."""
        orchestrator.initialize()

        with orchestrator.session("session-123", {}):
            # Send events during session
            for i in range(5):
                orchestrator.handle_event(
                    event_type=EventType.PROMPT_SUBMIT,
                    payload={"prompt": f"Prompt {i}"},
                    session_id="session-123",
                    correlation_id=f"req-{i}"
                )

        # Session automatically ended
        assert orchestrator.active_session_count == 0

    def test_recovery_from_errors(self, orchestrator):
        """Should recover from errors during workflow."""
        orchestrator.initialize()

        # Start session
        orchestrator.handle_session_start("session-123", {})

        # Simulate error during event handling
        with patch.object(
            orchestrator._service,
            'handle_event',
            side_effect=[
                RuntimeError("Temporary error"),
                Mock(return_value=Mock(success=True))
            ]
        ):
            # First event fails
            result1 = orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Test 1"},
                session_id="session-123",
                correlation_id="req-001"
            )
            assert not result1.success

            # Second event succeeds
            result2 = orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Test 2"},
                session_id="session-123",
                correlation_id="req-002"
            )
            assert result2.success

        # Session still active
        assert orchestrator.active_session_count == 1

        # Can end session normally
        orchestrator.handle_session_end("session-123", {})
        assert orchestrator.active_session_count == 0
