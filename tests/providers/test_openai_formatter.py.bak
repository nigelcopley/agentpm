"""
Tests for OpenAI Formatter Module

Tests OpenAI GPT formatter functionality for context payloads.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from agentpm.providers.openai.formatter import OpenAIFormatter
from agentpm.providers.base import TokenAllocation
from agentpm.core.context.models import ContextPayload
from agentpm.core.database.models.context import UnifiedSixW
from agentpm.core.database.enums import ConfidenceBand


class TestOpenAIFormatter:
    """Test OpenAIFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return OpenAIFormatter()

    @pytest.fixture
    def minimal_payload(self) -> ContextPayload:
        """Create minimal context payload for testing."""
        return ContextPayload(
            project={"id": 1, "name": "Test Project"},
            task=None,
            work_item=None,
            merged_6w=UnifiedSixW(),
            confidence_score=0.8,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

    @pytest.fixture
    def full_payload(self) -> ContextPayload:
        """Create full context payload for testing."""
        # Create UnifiedSixW with proper dataclass structure
        six_w = UnifiedSixW()
        six_w.implementers = ["Development Team"]
        six_w.end_users = ["System Users"]
        six_w.functional_requirements = ["OAuth2 authentication"]
        six_w.acceptance_criteria = ["Secure token validation"]
        six_w.affected_services = ["Auth module"]
        six_w.business_value = "Security requirement"
        six_w.suggested_approach = "OpenID Connect"
        six_w.dependencies_timeline = ["Sprint 3"]

        return ContextPayload(
            project={"id": 1, "name": "Test Project", "status": "active"},
            work_item={"id": 10, "name": "Feature Implementation", "priority": 1},
            task={
                "id": 100,
                "name": "Implement OAuth2",
                "type": "implementation",
                "effort_hours": 4.0,
                "work_item_id": 10,
            },
            merged_6w=six_w,
            plugin_facts={
                "Python": {"version": "3.11"},
                "FastAPI": {"version": "0.104.0"},
            },
            agent_sop="Follow OAuth2 best practices. Validate all tokens.",
            assigned_agent="implementation-orch",
            temporal_context=[
                {
                    "summary_type": "task_completion",
                    "session_date": "2025-10-20",
                    "summary_text": "Completed database schema design",
                    "metadata": {
                        "key_decisions": ["Use PostgreSQL", "Add UUID support"],
                        "tasks_completed": [1, 2, 3],
                        "blockers_resolved": [4],
                        "next_steps": ["Implement migrations", "Add tests"],
                    },
                }
            ],
            confidence_score=0.85,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=125.5,
        )

    def test_provider_name(self, formatter):
        """Test provider name is set correctly."""
        assert formatter.provider == "openai"

    def test_sop_max_chars(self, formatter):
        """Test SOP max chars constant."""
        assert formatter._SOP_MAX_CHARS == 500

    def test_format_task_minimal(self, formatter, minimal_payload):
        """Test formatting minimal task context."""
        result = formatter.format_task(minimal_payload)

        assert isinstance(result, str)
        assert "Task Context Assembled" in result
        assert "Context Delivery Agent" in result
        assert "**Task**: Unknown" in result
        assert "**Context Confidence**: 80% (GREEN)" in result

    def test_format_task_full(self, formatter, full_payload):
        """Test formatting full task context."""
        result = formatter.format_task(
            full_payload, assembly_duration_ms=125.5, warnings=["Test warning"]
        )

        # Basic structure
        assert "Task Context Assembled" in result
        assert "Context Delivery Agent" in result

        # Task details
        assert "Task #100" in result
        assert "Implement OAuth2" in result
        assert "implementation" in result
        assert "4.0h" in result
        assert "Work Item**: WI-10" in result

        # Agent assignment
        assert "Agent**: implementation-orch" in result

        # 6W Context (properties combine multiple fields)
        assert "Merged Context" in result
        assert "WHO**:" in result
        assert "Development Team" in result
        assert "WHAT**:" in result
        assert "OAuth2 authentication" in result
        assert "WHEN**:" in result
        assert "Sprint 3" in result
        assert "WHERE**:" in result
        assert "Auth module" in result
        assert "WHY**:" in result
        assert "Security requirement" in result
        assert "HOW**:" in result
        assert "OpenID Connect" in result

        # Tech stack
        assert "Tech Stack" in result
        assert "Python: 3.11" in result
        assert "FastAPI: 0.104.0" in result

        # Agent SOP
        assert "Agent SOP" in result
        assert "Follow OAuth2 best practices" in result

        # Temporal context
        assert "Recent Sessions" in result
        assert "task_completion" in result.lower()
        assert "2025-10-20" in result
        assert "Completed database schema design" in result
        assert "Key Decisions:" in result
        assert "Use PostgreSQL" in result
        assert "Tasks Completed: 3" in result
        assert "Blockers Resolved: 1" in result
        assert "Next Steps:" in result
        assert "Implement migrations" in result

        # Metadata
        assert "**Context Confidence**: 85% (GREEN)" in result
        assert "**Assembly Time**: 125ms" in result or "**Assembly Time**: 126ms" in result

        # Warnings
        assert "Warnings" in result
        assert "Test warning" in result

    def test_format_task_with_token_allocation(self, formatter, full_payload):
        """Test formatting with token allocation."""
        allocation = TokenAllocation(
            total_tokens=128_000,
            context_tokens=64_000,
            response_tokens=51_200,
            safety_buffer=12_800,
        )

        result = formatter.format_task(full_payload, token_allocation=allocation)

        # Token allocation should be accepted but doesn't affect output currently
        assert isinstance(result, str)
        assert "Task Context Assembled" in result

    def test_format_task_no_task_data(self, formatter, minimal_payload):
        """Test formatting when task data is None."""
        result = formatter.format_task(minimal_payload)

        assert "**Task**: Unknown" in result

    def test_format_task_truncates_long_sop(self, formatter, full_payload):
        """Test that long SOPs are truncated to 500 chars."""
        long_sop = "A" * 600
        full_payload.agent_sop = long_sop

        result = formatter.format_task(full_payload)

        assert "Agent SOP" in result
        # Should be truncated with ellipsis
        assert "A" * 500 + "..." in result
        assert "A" * 600 not in result

    def test_format_task_no_warnings(self, formatter, full_payload):
        """Test formatting without warnings."""
        result = formatter.format_task(full_payload)

        # Should not contain warnings section when no warnings provided
        assert "Warnings" not in result

    def test_format_task_multiple_warnings(self, formatter, full_payload):
        """Test formatting with multiple warnings (max 3 shown)."""
        warnings = ["Warning 1", "Warning 2", "Warning 3", "Warning 4"]
        result = formatter.format_task(full_payload, warnings=warnings)

        assert "Warnings" in result
        assert "Warning 1" in result
        assert "Warning 2" in result
        assert "Warning 3" in result
        # 4th warning should not appear (max 3)
        assert "Warning 4" not in result

    def test_format_session_minimal(self, formatter):
        """Test formatting minimal session context."""
        result = formatter.format_session("")

        assert result == "_No recent session history available._"

    def test_format_session_with_history_only(self, formatter):
        """Test formatting with only history text."""
        history = "Previous session history text"
        result = formatter.format_session(history)

        assert result == history

    def test_format_session_with_structured_data(self, formatter):
        """Test formatting with structured session data."""
        result = formatter.format_session(
            "",
            project={"name": "Test Project", "status": "active"},
            tech_stack="Python 3.11, FastAPI, PostgreSQL",
            active_work=[
                {
                    "id": 10,
                    "name": "Feature Implementation",
                    "status": "in_progress",
                    "priority": 1,
                    "summary_count": 5,
                },
                {
                    "id": 11,
                    "name": "Bug Fix",
                    "status": "review",
                    "priority": 2,
                },
            ],
        )

        # Project info
        assert "Project Context Loaded" in result
        assert "Context Delivery Agent" in result
        assert "**Project**: Test Project" in result
        assert "**Status**: active" in result
        assert "**Tech Stack**: Python 3.11, FastAPI, PostgreSQL" in result

        # Active work
        assert "### Active Work" in result
        assert "**WI-10**: Feature Implementation" in result
        assert "Status: in_progress" in result
        assert "Priority: 1" in result
        assert "History: 5 sessions" in result
        assert "**WI-11**: Bug Fix" in result
        assert "Status: review" in result
        assert "Priority: 2" in result

        # Dashboard hint
        assert "Use `apm status` for complete dashboard" in result

    def test_format_session_with_all_metadata(self, formatter):
        """Test formatting with all metadata fields."""
        result = formatter.format_session(
            "",
            project={"name": "APM (Agent Project Manager)"},
            tech_stack="Python, SQLite",
            active_work=[{"id": 1, "name": "Feature A"}],
            active_task_contexts=["- Active task context line"],
            static_context=["- Static context line"],
            handover=["- Handover note"],
        )

        assert "Project Context Loaded" in result
        assert "APM (Agent Project Manager)" in result
        assert "Active task context line" in result
        assert "Static context line" in result
        assert "Handover note" in result

    def test_format_session_work_item_without_id(self, formatter):
        """Test formatting work item without ID."""
        result = formatter.format_session(
            "",
            project={"name": "Test"},
            active_work=[{"name": "No ID Work Item", "status": "draft"}],
        )

        assert "- No ID Work Item" in result
        assert "Status: draft" in result

    def test_format_6w_context_empty(self, formatter):
        """Test formatting empty 6W context."""
        empty_6w = UnifiedSixW()
        lines = formatter._format_6w_context(empty_6w)

        assert "### Merged Context (Task → Work Item → Project)" in lines
        # Only header and empty line
        assert len(lines) == 3

    def test_format_6w_context_partial(self, formatter):
        """Test formatting partial 6W context."""
        partial_6w = UnifiedSixW()
        partial_6w.implementers = ["Developer"]
        partial_6w.functional_requirements = ["Implementation"]
        # Others remain empty

        lines = formatter._format_6w_context(partial_6w)

        formatted = "\n".join(lines)
        assert "WHO**:" in formatted
        assert "Developer" in formatted
        assert "WHAT**:" in formatted
        assert "Implementation" in formatted
        # These should not appear since they're empty
        assert "WHEN**:" not in formatted
        assert "WHERE**:" not in formatted
        assert "WHY**:" not in formatted
        assert "HOW**:" not in formatted

    def test_format_plugin_facts_empty(self, formatter):
        """Test formatting empty plugin facts."""
        lines = formatter._format_plugin_facts({})

        # Should still have header and empty line
        assert "### Tech Stack" in lines
        assert len(lines) == 3

    def test_format_plugin_facts_with_versions(self, formatter):
        """Test formatting plugin facts with versions."""
        facts = {
            "Python": {"version": "3.11"},
            "FastAPI": {"version": "0.104.0"},
        }
        lines = formatter._format_plugin_facts(facts)

        formatted = "\n".join(lines)
        assert "Python: 3.11" in formatted
        assert "FastAPI: 0.104.0" in formatted

    def test_format_plugin_facts_without_versions(self, formatter):
        """Test formatting plugin facts without version info."""
        facts = {
            "Python": {},
            "Framework": "some_value",
        }
        lines = formatter._format_plugin_facts(facts)

        formatted = "\n".join(lines)
        assert "- Python" in formatted
        assert "- Framework" in formatted

    def test_format_temporal_context_empty(self, formatter):
        """Test formatting empty temporal context."""
        lines = formatter._format_temporal_context([])

        # Should return empty list when no sessions
        assert lines == []

    def test_format_temporal_context_minimal(self, formatter):
        """Test formatting minimal temporal context."""
        summaries = [
            {
                "summary_type": "session",
                "session_date": "2025-10-20",
                "summary_text": "Basic session",
            }
        ]
        lines = formatter._format_temporal_context(summaries)

        formatted = "\n".join(lines)
        assert "Recent Sessions" in formatted
        assert "Session (2025-10-20)" in formatted
        assert "Basic session" in formatted

    def test_format_temporal_context_full(self, formatter):
        """Test formatting full temporal context with all metadata."""
        summaries = [
            {
                "summary_type": "task_completion",
                "session_date": "2025-10-20",
                "summary_text": "Completed feature implementation",
                "metadata": {
                    "key_decisions": ["Decision 1", "Decision 2", "Decision 3", "Decision 4"],
                    "tasks_completed": [1, 2, 3],
                    "blockers_resolved": [4, 5],
                    "next_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
                },
            }
        ]
        lines = formatter._format_temporal_context(summaries)

        formatted = "\n".join(lines)
        assert "Task_Completion (2025-10-20)" in formatted
        assert "Completed feature implementation" in formatted
        assert "Key Decisions:" in formatted
        assert "Decision 1" in formatted
        assert "Decision 2" in formatted
        assert "Decision 3" in formatted
        # 4th decision should not appear (max 3)
        assert "Decision 4" not in formatted
        assert "Tasks Completed: 3" in formatted
        assert "Blockers Resolved: 2" in formatted
        assert "Next Steps:" in formatted
        assert "Step 1" in formatted
        assert "Step 3" in formatted
        # 4th step should not appear (max 3)
        assert "Step 4" not in formatted

    def test_format_temporal_context_no_metadata(self, formatter):
        """Test formatting temporal context without metadata."""
        summaries = [
            {
                "summary_type": "session",
                "summary_text": "Session without metadata",
            }
        ]
        lines = formatter._format_temporal_context(summaries)

        formatted = "\n".join(lines)
        assert "Session without metadata" in formatted
        assert "Key Decisions:" not in formatted
        assert "Tasks Completed:" not in formatted

    def test_format_temporal_context_multiple_sessions(self, formatter):
        """Test formatting multiple temporal contexts."""
        summaries = [
            {
                "summary_type": "session",
                "session_date": "2025-10-20",
                "summary_text": "Session 1",
            },
            {
                "summary_type": "task_completion",
                "session_date": "2025-10-21",
                "summary_text": "Session 2",
            },
        ]
        lines = formatter._format_temporal_context(summaries)

        formatted = "\n".join(lines)
        assert "Session (2025-10-20)" in formatted
        assert "Session 1" in formatted
        assert "Task_Completion (2025-10-21)" in formatted
        assert "Session 2" in formatted

    def test_confidence_band_formatting(self, formatter, minimal_payload):
        """Test confidence band formatting for different levels."""
        # Test GREEN
        minimal_payload.confidence_score = 0.9
        minimal_payload.confidence_band = ConfidenceBand.GREEN
        result = formatter.format_task(minimal_payload)
        assert "90% (GREEN)" in result

        # Test YELLOW
        minimal_payload.confidence_score = 0.6
        minimal_payload.confidence_band = ConfidenceBand.YELLOW
        result = formatter.format_task(minimal_payload)
        assert "60% (YELLOW)" in result

        # Test RED
        minimal_payload.confidence_score = 0.3
        minimal_payload.confidence_band = ConfidenceBand.RED
        result = formatter.format_task(minimal_payload)
        assert "30% (RED)" in result

    def test_effort_hours_none(self, formatter, full_payload):
        """Test formatting when effort_hours is None."""
        full_payload.task["effort_hours"] = None
        result = formatter.format_task(full_payload)

        assert "n/a)" in result

    def test_markdown_structure(self, formatter, full_payload):
        """Test that output maintains proper markdown structure."""
        result = formatter.format_task(full_payload)

        # Should have proper markdown headers
        assert "## Task Context" in result
        assert "### Merged Context" in result
        assert "### Tech Stack" in result
        assert "### Agent SOP" in result
        assert "### Recent Sessions" in result

        # Should use bold for key-value pairs
        assert "**Task #" in result
        assert "**Work Item**:" in result
        assert "**Agent**:" in result
        assert "**WHO**:" in result
        assert "**Context Confidence**:" in result

    def test_empty_strings_handling(self, formatter, full_payload):
        """Test handling of empty strings in various fields."""
        full_payload.task["name"] = ""
        full_payload.agent_sop = ""
        # Empty UnifiedSixW
        full_payload.merged_6w = UnifiedSixW()

        result = formatter.format_task(full_payload)

        # Should not crash and should handle empty gracefully
        assert isinstance(result, str)
        assert "Task Context Assembled" in result
