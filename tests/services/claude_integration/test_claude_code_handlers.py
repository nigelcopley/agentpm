"""
Tests for Claude Code Hook Handlers

Validates Claude Code event handling and session integration.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from agentpm.providers.anthropic.claude_code.runtime.hooks import (
    ClaudeCodeHookHandlers,
    HookEvent,
    EventType,
    get_hooks_engine,
    reset_hooks_engine,
)
from agentpm.core.database.models.session import (
    Session, SessionTool, SessionType, SessionMetadata, SessionStatus
)


@pytest.fixture
def mock_db():
    """Mock database service."""
    db = MagicMock()
    db.db_path = "/tmp/test.db"
    return db


@pytest.fixture
def handlers(mock_db):
    """Create handlers with mock database."""
    reset_hooks_engine()
    return ClaudeCodeHookHandlers(mock_db)


def make_mock_metadata(**kwargs):
    """Helper to create mock metadata with model_dump."""
    metadata = MagicMock()
    metadata.model_dump.return_value = kwargs
    # Also set attributes for direct access
    for key, value in kwargs.items():
        setattr(metadata, key, value)
    return metadata


@pytest.fixture
def sample_session():
    """Sample session for testing."""
    return Session(
        id=1,
        session_id="session-test-123",
        project_id=1,
        tool=SessionTool.CLAUDE_CODE,
        tool_version="1.5.0",
        session_type=SessionType.DEVELOPMENT,
        metadata=SessionMetadata(
            work_item_count=2,
            task_count=5,
        ),
        started_at=datetime.now().isoformat(),
        duration_minutes=None,
    )


class TestHandlerRegistration:
    """Test handler registration with hooks engine."""

    def test_register_all_handlers(self, handlers):
        """Should register all event handlers."""
        handlers.register_all()

        engine = get_hooks_engine()

        # Verify handlers registered
        assert EventType.SESSION_START.value in engine._event_handlers
        assert EventType.SESSION_END.value in engine._event_handlers
        assert EventType.PROMPT_SUBMIT.value in engine._event_handlers
        assert EventType.TOOL_RESULT.value in engine._event_handlers

    def test_unregister_all_handlers(self, handlers):
        """Should unregister all handlers."""
        handlers.register_all()
        handlers.unregister_all()

        engine = get_hooks_engine()

        # Verify handlers unregistered
        assert len(engine._event_handlers.get(EventType.SESSION_START.value, [])) == 0
        assert len(engine._event_handlers.get(EventType.SESSION_END.value, [])) == 0

    def test_register_with_engine(self, handlers):
        """Should work with engine dispatch after registration."""
        handlers.register_all()

        engine = get_hooks_engine()

        # Mock the session creation
        with patch('agentpm.core.database.methods.sessions.create_session') as mock_create:
            mock_session = Session(
                id=1,
                session_id="test-123",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=SessionMetadata(),
            )
            mock_create.return_value = mock_session

            result = engine.dispatch_event(
                event_type=EventType.SESSION_START,
                payload={"project_id": 1},
                session_id="test-123",
                correlation_id="req-001"
            )

            assert result.success


class TestSessionStartHandler:
    """Test SESSION_START event handling."""

    def test_session_start_creates_session(self, handlers, mock_db):
        """Should create new session in database."""
        with patch('agentpm.core.database.methods.sessions.create_session') as mock_create, \
             patch('agentpm.core.database.methods.sessions.set_current_session') as mock_set:

            mock_session = Session(
                id=1,
                session_id="test-123",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=SessionMetadata(),
            )
            mock_create.return_value = mock_session

            event = HookEvent(
                type=EventType.SESSION_START,
                payload={"project_id": 1, "tool_version": "1.5.0"},
                session_id="test-123",
                correlation_id="req-001",
            )

            result = handlers.on_session_start(event)

            # Verify session created
            assert mock_create.called
            assert mock_set.called
            assert result["status"] == "success"
            assert result["session"]["session_id"] == "test-123"

    def test_session_start_loads_previous_context(self, handlers, mock_db):
        """Should load context from previous session."""
        with patch('agentpm.core.database.methods.sessions.create_session') as mock_create, \
             patch('agentpm.core.database.methods.sessions.set_current_session'), \
             patch('agentpm.core.database.methods.sessions.list_sessions') as mock_list:

            mock_create.return_value = Session(
                id=1,
                session_id="test-123",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=SessionMetadata(),
            )

            # Mock previous session with metadata dict
            prev_metadata = make_mock_metadata(
                work_items_touched=[35, 42],
                tasks_completed=[100, 101],
                tool_specific={'session_summary': 'Previous work done'}
            )

            mock_list.return_value = [Session(
                id=0,
                session_id="prev-session",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=prev_metadata,
                ended_at=datetime.now().isoformat(),
                duration_minutes=120,
            )]

            event = HookEvent(
                type=EventType.SESSION_START,
                payload={"project_id": 1},
                session_id="test-123",
                correlation_id="req-001",
            )

            result = handlers.on_session_start(event)

            assert result["status"] == "success"
            assert result["previous_context"]["available"] is True
            assert result["previous_context"]["work_items"] == [35, 42]

    def test_session_start_missing_project_id(self, handlers):
        """Should error if project_id missing."""
        event = HookEvent(
            type=EventType.SESSION_START,
            payload={},  # Missing project_id
            session_id="test-123",
            correlation_id="req-001",
        )

        result = handlers.on_session_start(event)

        assert result["status"] == "error"
        assert "project_id required" in result["message"]

    def test_session_start_with_developer_info(self, handlers):
        """Should capture developer info in session."""
        with patch('agentpm.core.database.methods.sessions.create_session') as mock_create, \
             patch('agentpm.core.database.methods.sessions.set_current_session'):

            mock_create.return_value = Session(
                id=1,
                session_id="test-123",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=SessionMetadata(),
                developer_name="Jane Doe",
                developer_email="jane@example.com",
            )

            event = HookEvent(
                type=EventType.SESSION_START,
                payload={
                    "project_id": 1,
                    "developer_name": "Jane Doe",
                    "developer_email": "jane@example.com",
                },
                session_id="test-123",
                correlation_id="req-001",
            )

            result = handlers.on_session_start(event)

            # Verify developer info passed to create
            call_args = mock_create.call_args[0][1]
            assert call_args.developer_name == "Jane Doe"
            assert call_args.developer_email == "jane@example.com"


class TestSessionEndHandler:
    """Test SESSION_END event handling."""

    def test_session_end_finalizes_session(self, handlers, sample_session):
        """Should finalize session with end time and duration."""
        with patch('agentpm.core.database.methods.sessions.get_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.end_session') as mock_end, \
             patch('agentpm.core.database.methods.sessions.clear_current_session') as mock_clear:

            # Setup active session
            sample_session.status = SessionStatus.ACTIVE
            mock_get.return_value = sample_session

            # Mock ended session
            ended_session = Session(**sample_session.model_dump())
            ended_session.ended_at = datetime.now().isoformat()
            ended_session.duration_minutes = 45
            ended_session.status = SessionStatus.COMPLETED
            mock_end.return_value = ended_session

            event = HookEvent(
                type=EventType.SESSION_END,
                payload={"exit_reason": "User closed app"},
                session_id="session-test-123",
                correlation_id="req-002",
            )

            result = handlers.on_session_end(event)

            # Verify session ended
            assert mock_end.called
            assert mock_clear.called
            assert result["status"] == "success"
            assert result["session"]["duration_minutes"] == 45

    def test_session_end_generates_summary(self, handlers, sample_session):
        """Should generate session summary."""
        with patch('agentpm.core.database.methods.sessions.get_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.end_session') as mock_end, \
             patch('agentpm.core.database.methods.sessions.clear_current_session'):

            sample_session.status = SessionStatus.ACTIVE
            sample_session.metadata = make_mock_metadata(
                work_items_touched=[35, 42],
                tasks_completed=[100, 101, 102]
            )
            mock_get.return_value = sample_session

            ended_session = Session(**sample_session.model_dump())
            ended_session.metadata = sample_session.metadata
            ended_session.duration_minutes = 45
            mock_end.return_value = ended_session

            event = HookEvent(
                type=EventType.SESSION_END,
                payload={"summary": "Implemented feature X"},
                session_id="session-test-123",
                correlation_id="req-002",
            )

            result = handlers.on_session_end(event)

            assert result["status"] == "success"
            assert "Implemented feature X" in result["summary"]
            assert "Work items: 2" in result["summary"]
            assert "Tasks completed: 3" in result["summary"]

    def test_session_end_creates_handover(self, handlers, sample_session):
        """Should create handover document for next session."""
        with patch('agentpm.core.database.methods.sessions.get_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.end_session') as mock_end, \
             patch('agentpm.core.database.methods.sessions.clear_current_session'):

            sample_session.status = SessionStatus.ACTIVE
            sample_session.metadata = make_mock_metadata(
                work_items_touched=[35],
                tasks_completed=[100, 101],
                decisions_made=[
                    {"decision": "Use Pydantic", "rationale": "Type safety"}
                ]
            )
            mock_get.return_value = sample_session

            ended_session = Session(**sample_session.model_dump())
            ended_session.metadata = sample_session.metadata
            ended_session.duration_minutes = 45
            mock_end.return_value = ended_session

            event = HookEvent(
                type=EventType.SESSION_END,
                payload={},
                session_id="session-test-123",
                correlation_id="req-002",
            )

            result = handlers.on_session_end(event)

            handover = result["handover"]
            assert handover["session_id"] == "session-test-123"
            assert handover["work_completed"]["work_items"] == [35]
            assert handover["work_completed"]["tasks"] == [100, 101]
            assert len(handover["decisions"]) == 1

    def test_session_end_session_not_found(self, handlers):
        """Should error if session not found."""
        with patch('agentpm.core.database.methods.sessions.get_session') as mock_get:
            mock_get.return_value = None

            event = HookEvent(
                type=EventType.SESSION_END,
                payload={},
                session_id="nonexistent",
                correlation_id="req-002",
            )

            result = handlers.on_session_end(event)

            assert result["status"] == "error"
            assert "not found" in result["message"]


class TestPromptSubmitHandler:
    """Test PROMPT_SUBMIT event handling."""

    def test_prompt_submit_tracks_prompt(self, handlers, sample_session):
        """Should track prompt in session metadata."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update:

            sample_session.metadata = make_mock_metadata(tool_specific={})
            mock_get.return_value = sample_session
            mock_update.return_value = sample_session

            event = HookEvent(
                type=EventType.PROMPT_SUBMIT,
                payload={
                    "prompt": "Implement user authentication",
                    "prompt_number": 5
                },
                session_id="session-test-123",
                correlation_id="req-003",
            )

            result = handlers.on_prompt_submit(event)

            assert result["status"] == "success"
            assert result["prompt_count"] == 1
            assert mock_update.called

            # Verify prompt stored
            call_args = mock_update.call_args[0][1]
            tool_specific = call_args.metadata.tool_specific
            assert 'prompts' in tool_specific
            prompts = tool_specific['prompts']
            assert len(prompts) == 1
            assert prompts[0]['text'] == "Implement user authentication"
            assert prompts[0]['prompt_number'] == 5

    def test_prompt_submit_truncates_long_prompts(self, handlers, sample_session):
        """Should truncate very long prompts for storage."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update:

            sample_session.metadata = make_mock_metadata(tool_specific={})
            mock_get.return_value = sample_session

            long_prompt = "A" * 500  # 500 chars

            event = HookEvent(
                type=EventType.PROMPT_SUBMIT,
                payload={"prompt": long_prompt},
                session_id="session-test-123",
                correlation_id="req-003",
            )

            result = handlers.on_prompt_submit(event)

            # Verify truncated to 200 chars
            call_args = mock_update.call_args[0][1]
            stored_prompt = call_args.metadata.tool_specific['prompts'][0]['text']
            assert len(stored_prompt) == 200

    def test_prompt_submit_no_active_session(self, handlers):
        """Should warn if no active session."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get:
            mock_get.return_value = None

            event = HookEvent(
                type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Test"},
                session_id="session-test-123",
                correlation_id="req-003",
            )

            result = handlers.on_prompt_submit(event)

            assert result["status"] == "warning"
            assert "No active session" in result["message"]

    def test_prompt_submit_missing_prompt(self, handlers):
        """Should skip if no prompt in payload."""
        event = HookEvent(
            type=EventType.PROMPT_SUBMIT,
            payload={},  # No prompt
            session_id="session-test-123",
            correlation_id="req-003",
        )

        result = handlers.on_prompt_submit(event)

        assert result["status"] == "skipped"


class TestToolResultHandler:
    """Test TOOL_RESULT event handling."""

    def test_tool_result_tracks_usage(self, handlers, sample_session):
        """Should track tool usage in session metadata."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update:

            sample_session.metadata = make_mock_metadata(tool_specific={})
            mock_get.return_value = sample_session
            mock_update.return_value = sample_session

            event = HookEvent(
                type=EventType.TOOL_RESULT,
                payload={
                    "tool_name": "Bash",
                    "success": True,
                    "duration_ms": 234
                },
                session_id="session-test-123",
                correlation_id="req-004",
            )

            result = handlers.on_tool_result(event)

            assert result["status"] == "success"
            assert "Bash" in result["tool_usage"]
            assert result["tool_usage"]["Bash"]["count"] == 1
            assert result["tool_usage"]["Bash"]["failures"] == 0

    def test_tool_result_tracks_failures(self, handlers, sample_session):
        """Should track tool failures separately."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update:

            sample_session.metadata = make_mock_metadata(
                tool_specific={
                    'tool_usage': {
                        'Bash': {'count': 2, 'failures': 0}
                    }
                }
            )
            mock_get.return_value = sample_session
            mock_update.return_value = sample_session

            event = HookEvent(
                type=EventType.TOOL_RESULT,
                payload={
                    "tool_name": "Bash",
                    "success": False,
                    "error": "Command not found"
                },
                session_id="session-test-123",
                correlation_id="req-004",
            )

            result = handlers.on_tool_result(event)

            # Should increment both count and failures
            assert result["tool_usage"]["Bash"]["count"] == 3
            assert result["tool_usage"]["Bash"]["failures"] == 1

    def test_tool_result_multiple_tools(self, handlers, sample_session):
        """Should track multiple different tools."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update:

            sample_session.metadata = make_mock_metadata(tool_specific={})
            mock_get.return_value = sample_session
            mock_update.return_value = sample_session

            # Execute multiple tools
            for tool in ["Bash", "Read", "Write", "Bash", "Read"]:
                event = HookEvent(
                    type=EventType.TOOL_RESULT,
                    payload={"tool_name": tool, "success": True},
                    session_id="session-test-123",
                    correlation_id="req-004",
                )
                handlers.on_tool_result(event)

            # Verify counts
            final_call = mock_update.call_args[0][1]
            tool_usage = final_call.metadata.tool_specific['tool_usage']
            assert tool_usage["Bash"]["count"] == 2
            assert tool_usage["Read"]["count"] == 2
            assert tool_usage["Write"]["count"] == 1

    def test_tool_result_no_active_session(self, handlers):
        """Should warn if no active session."""
        with patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get:
            mock_get.return_value = None

            event = HookEvent(
                type=EventType.TOOL_RESULT,
                payload={"tool_name": "Bash", "success": True},
                session_id="session-test-123",
                correlation_id="req-004",
            )

            result = handlers.on_tool_result(event)

            assert result["status"] == "warning"


class TestPrePostToolHandlers:
    """Test PRE_TOOL_USE and POST_TOOL_USE handlers."""

    def test_pre_tool_use_acknowledges(self, handlers):
        """Should acknowledge pre-tool event."""
        event = HookEvent(
            type=EventType.PRE_TOOL_USE,
            payload={"tool_name": "Bash"},
            session_id="session-test-123",
            correlation_id="req-005",
        )

        result = handlers.on_pre_tool_use(event)

        assert result["status"] == "success"
        assert "Bash" in result["message"]

    def test_post_tool_use_acknowledges(self, handlers):
        """Should acknowledge post-tool event."""
        event = HookEvent(
            type=EventType.POST_TOOL_USE,
            payload={"tool_name": "Read"},
            session_id="session-test-123",
            correlation_id="req-006",
        )

        result = handlers.on_post_tool_use(event)

        assert result["status"] == "success"
        assert "Read" in result["message"]


class TestHelperMethods:
    """Test private helper methods."""

    def test_load_previous_session_context_available(self, handlers):
        """Should load context when previous session exists."""
        with patch('agentpm.core.database.methods.sessions.list_sessions') as mock_list:
            prev_metadata = make_mock_metadata(
                work_items_touched=[35, 42],
                tasks_completed=[100, 101],
                tool_specific={'session_summary': 'Previous work completed'}
            )

            mock_list.return_value = [Session(
                id=1,
                session_id="prev-session",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=prev_metadata,
                ended_at=datetime.now().isoformat(),
                duration_minutes=90,
            )]

            context = handlers._load_previous_session_context(project_id=1)

            assert context["available"] is True
            assert context["work_items"] == [35, 42]
            assert context["tasks"] == [100, 101]
            assert context["summary"] == 'Previous work completed'

    def test_load_previous_session_context_none_available(self, handlers):
        """Should handle no previous sessions gracefully."""
        with patch('agentpm.core.database.methods.sessions.list_sessions') as mock_list:
            mock_list.return_value = []

            context = handlers._load_previous_session_context(project_id=1)

            assert context["available"] is False
            assert "No previous sessions" in context["message"]

    def test_generate_session_summary_with_user_input(self, handlers, sample_session):
        """Should combine user summary with metrics."""
        payload = {"summary": "Implemented authentication"}
        sample_session.metadata = make_mock_metadata(
            work_items_touched=[35],
            tasks_completed=[100, 101]
        )

        summary = handlers._generate_session_summary(sample_session, payload)

        assert "Implemented authentication" in summary
        assert "Work items: 1" in summary
        assert "Tasks completed: 2" in summary

    def test_generate_session_summary_metrics_only(self, handlers, sample_session):
        """Should generate summary from metrics alone."""
        payload = {}
        sample_session.metadata = make_mock_metadata(
            work_items_touched=[35, 42],
            decisions_made=[{"decision": "Use Pydantic"}]
        )

        summary = handlers._generate_session_summary(sample_session, payload)

        assert "Work items: 2" in summary
        assert "Decisions made: 1" in summary

    def test_create_handover_document_complete(self, handlers, sample_session):
        """Should create complete handover document."""
        sample_session.ended_at = datetime.now().isoformat()
        sample_session.duration_minutes = 60
        sample_session.metadata = make_mock_metadata(
            work_items_touched=[35, 42],
            tasks_completed=[100, 101, 102],
            decisions_made=[
                {"decision": "Use Pydantic", "rationale": "Type safety"}
            ],
            tool_specific={
                'tool_usage': {
                    'Bash': {'count': 10, 'failures': 1}
                }
            }
        )

        handover = handlers._create_handover_document(sample_session)

        assert handover["session_id"] == "session-test-123"
        assert handover["duration_minutes"] == 60
        assert handover["work_completed"]["work_items"] == [35, 42]
        assert handover["work_completed"]["tasks"] == [100, 101, 102]
        assert len(handover["decisions"]) == 1
        assert handover["tool_usage"]["Bash"]["count"] == 10


class TestEndToEndWorkflow:
    """Test complete session workflow."""

    def test_complete_session_lifecycle(self, handlers):
        """Should handle complete session start to end."""
        with patch('agentpm.core.database.methods.sessions.create_session') as mock_create, \
             patch('agentpm.core.database.methods.sessions.set_current_session'), \
             patch('agentpm.core.database.methods.sessions.get_current_session') as mock_get_current, \
             patch('agentpm.core.database.methods.sessions.update_session') as mock_update, \
             patch('agentpm.core.database.methods.sessions.get_session') as mock_get, \
             patch('agentpm.core.database.methods.sessions.end_session') as mock_end, \
             patch('agentpm.core.database.methods.sessions.clear_current_session'):

            # Create session
            session = Session(
                id=1,
                session_id="test-123",
                project_id=1,
                tool=SessionTool.CLAUDE_CODE,
                metadata=SessionMetadata(),
                started_at=datetime.now().isoformat(),
            )
            mock_create.return_value = session
            mock_get_current.return_value = session
            mock_get.return_value = session

            # Start session
            start_event = HookEvent(
                type=EventType.SESSION_START,
                payload={"project_id": 1},
                session_id="test-123",
                correlation_id="req-001",
            )
            start_result = handlers.on_session_start(start_event)
            assert start_result["status"] == "success"

            # Submit prompts
            session.metadata = make_mock_metadata(tool_specific={})
            mock_get_current.return_value = session
            prompt_event = HookEvent(
                type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Test prompt"},
                session_id="test-123",
                correlation_id="req-002",
            )
            prompt_result = handlers.on_prompt_submit(prompt_event)
            assert prompt_result["status"] == "success"

            # Tool usage
            tool_event = HookEvent(
                type=EventType.TOOL_RESULT,
                payload={"tool_name": "Bash", "success": True},
                session_id="test-123",
                correlation_id="req-003",
            )
            tool_result = handlers.on_tool_result(tool_event)
            assert tool_result["status"] == "success"

            # End session
            ended_session = Session(**session.model_dump())
            ended_session.duration_minutes = 30
            ended_session.ended_at = datetime.now().isoformat()
            mock_end.return_value = ended_session

            end_event = HookEvent(
                type=EventType.SESSION_END,
                payload={"exit_reason": "Complete"},
                session_id="test-123",
                correlation_id="req-004",
            )
            end_result = handlers.on_session_end(end_event)
            assert end_result["status"] == "success"
            assert "handover" in end_result
