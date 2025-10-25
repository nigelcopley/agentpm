"""
Tests for Google Gemini Formatter

Tests the GoogleFormatter class for context payload formatting optimized for
Gemini's 32K token context window.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from agentpm.providers.google.formatter import GoogleFormatter
from agentpm.core.context.models import ContextPayload
from agentpm.core.database.models.context import UnifiedSixW
from agentpm.core.database.enums import ConfidenceBand


class TestGoogleFormatterBasics:
    """Test basic GoogleFormatter functionality."""

    def test_formatter_initialization(self):
        """Test GoogleFormatter can be instantiated."""
        formatter = GoogleFormatter()
        assert formatter.provider == "google"
        assert formatter._SOP_MAX_CHARS == 400
        assert formatter._MAX_TEMPORAL_SESSIONS == 5

    def test_provider_attribute(self):
        """Test provider attribute is correctly set."""
        formatter = GoogleFormatter()
        assert formatter.provider == "google"


class TestFormatTask:
    """Test format_task method."""

    @pytest.fixture
    def minimal_payload(self):
        """Create minimal ContextPayload for testing."""
        return ContextPayload(
            project={"id": 1, "name": "Test Project"},
            merged_6w=UnifiedSixW(),
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime(2025, 1, 15, 10, 30, 0),
            assembly_duration_ms=45.0,
        )

    @pytest.fixture
    def full_payload(self):
        """Create complete ContextPayload for testing."""
        return ContextPayload(
            project={"id": 1, "name": "Test Project"},
            work_item={"id": 42, "name": "Feature Implementation"},
            task={
                "id": 123,
                "name": "Implement GoogleFormatter",
                "type": "IMPLEMENTATION",
                "effort_hours": 2.5,
                "work_item_id": 42,
            },
            merged_6w=UnifiedSixW(
                implementers=["Python developer"],
                functional_requirements=["Implement Google Gemini formatter"],
                dependencies_timeline=["Sprint 3"],
                affected_services=["agentpm/providers/google/"],
                business_value="Enable Gemini integration",
                suggested_approach="Follow Anthropic pattern with 32K token optimization",
            ),
            plugin_facts={
                "pytest": {"version": "7.4.0"},
                "python": {"version": "3.11"},
            },
            agent_sop="Agent Standard Operating Procedure for testing. This is a longer SOP that should be truncated.",
            assigned_agent="google-formatter-developer",
            temporal_context=[
                {
                    "summary_type": "task_completion",
                    "session_date": "2025-01-14",
                    "summary_text": "Completed formatter stub analysis",
                    "metadata": {
                        "key_decisions": ["Use Anthropic pattern", "Optimize for 32K tokens"],
                        "tasks_completed": [121, 122],
                        "next_steps": ["Implement format_task", "Create unit tests"],
                    },
                }
            ],
            confidence_score=0.85,
            confidence_band=ConfidenceBand.GREEN,
            warnings=["Temporal context older than 7 days"],
            assembled_at=datetime(2025, 1, 15, 10, 30, 0),
            assembly_duration_ms=125.5,
        )

    def test_format_task_minimal(self, minimal_payload):
        """Test formatting minimal payload."""
        formatter = GoogleFormatter()
        result = formatter.format_task(minimal_payload, assembly_duration_ms=45.0)

        assert "## Task Context (Gemini Context Assembly)" in result
        assert "**Task**: Unknown" in result
        assert "**Context Confidence**: 75% (GREEN)" in result
        assert "**Assembly Time**: 45ms" in result

    def test_format_task_full(self, full_payload):
        """Test formatting complete payload."""
        formatter = GoogleFormatter()
        result = formatter.format_task(full_payload)

        # Task header
        assert "## Task Context (Gemini Context Assembly)" in result
        assert "**Task #123**: Implement GoogleFormatter" in result
        assert "(implementation, 2.5h)" in result
        assert "**Work Item**: WI-42" in result
        assert "**Agent**: google-formatter-developer" in result

        # 6W context
        assert "### Merged Context (Task → Work Item → Project)" in result
        assert "**WHO**: Implementers: Python developer" in result
        assert "**WHAT**: Implement Google Gemini formatter" in result
        assert "**WHY**: Enable Gemini integration" in result

        # Plugin facts
        assert "### Tech Stack" in result
        assert "- pytest: 7.4.0" in result
        assert "- python: 3.11" in result

        # Agent SOP
        assert "### Agent SOP" in result

        # Temporal context
        assert "### Recent Sessions" in result
        assert "Task_Completion (2025-01-14)" in result

        # Quality metrics
        assert "**Context Confidence**: 85% (GREEN)" in result
        assert "**Assembly Time**: 126ms" in result

        # Warnings
        assert "**Warnings**:" in result
        assert "- Temporal context older than 7 days" in result

    def test_format_task_with_metadata(self, full_payload):
        """Test formatting with additional metadata."""
        formatter = GoogleFormatter()
        result = formatter.format_task(
            full_payload,
            assembly_duration_ms=200.0,
            warnings=["Warning 1", "Warning 2", "Warning 3", "Warning 4"],
        )

        assert "**Assembly Time**: 200ms" in result
        # Should limit to 3 warnings
        assert "- Warning 1" in result
        assert "- Warning 2" in result
        assert "- Warning 3" in result
        assert "Warning 4" not in result

    def test_sop_truncation(self, full_payload):
        """Test SOP is truncated to 400 chars."""
        # Create very long SOP
        long_sop = "A" * 1000
        full_payload.agent_sop = long_sop

        formatter = GoogleFormatter()
        result = formatter.format_task(full_payload)

        # Should be truncated to 400 chars + "..."
        assert "### Agent SOP" in result
        # Count actual SOP content (not including markdown headers)
        sop_section = result.split("### Agent SOP")[1].split("###")[0]
        # Should be ~400 chars, not 1000
        assert len(sop_section.strip()) < 450

    def test_temporal_context_limit(self):
        """Test temporal context limited to 5 sessions."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test Project"},
            merged_6w=UnifiedSixW(),
            temporal_context=[
                {"summary_type": f"session_{i}", "session_date": f"2025-01-{10+i}"}
                for i in range(10)
            ],
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime(2025, 1, 15, 10, 30, 0),
            assembly_duration_ms=45.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        # Should only include first 5 sessions
        for i in range(5):
            assert f"2025-01-{10+i}" in result
        # Should not include sessions 6-10
        for i in range(5, 10):
            assert f"2025-01-{10+i}" not in result


class TestFormatSession:
    """Test format_session method."""

    def test_format_session_no_structured_data(self):
        """Test session formatting with no structured data."""
        formatter = GoogleFormatter()
        result = formatter.format_session("Raw history text")

        assert result == "Raw history text"

    def test_format_session_empty_history(self):
        """Test session formatting with empty history."""
        formatter = GoogleFormatter()
        result = formatter.format_session("")

        assert result == "_No recent session history available._"

    def test_format_session_with_project(self):
        """Test session formatting with project data."""
        formatter = GoogleFormatter()
        result = formatter.format_session(
            "",
            project={"name": "APM (Agent Project Manager)", "status": "active"},
            tech_stack="Python 3.11, SQLite, Pydantic",
        )

        assert "## Project Context (Gemini Context Assembly)" in result
        assert "**Project**: APM (Agent Project Manager)" in result
        assert "**Status**: active" in result
        assert "**Tech Stack**: Python 3.11, SQLite, Pydantic" in result
        assert "Use `apm status` for complete dashboard" in result

    def test_format_session_with_active_work(self):
        """Test session formatting with active work items."""
        formatter = GoogleFormatter()
        result = formatter.format_session(
            "",
            project={"name": "APM (Agent Project Manager)"},
            active_work=[
                {
                    "id": 125,
                    "name": "Provider System Readiness",
                    "status": "in_progress",
                    "priority": 1,
                    "summary_count": 5,
                },
                {
                    "id": 126,
                    "name": "Documentation Updates",
                    "status": "planned",
                    "priority": 2,
                },
            ],
        )

        assert "### Active Work" in result
        assert "- **WI-125**: Provider System Readiness" in result
        assert "Status: in_progress" in result
        assert "Priority: 1" in result
        assert "History: 5 sessions" in result
        assert "- **WI-126**: Documentation Updates" in result

    def test_format_session_active_work_limit(self):
        """Test active work limited to 10 items."""
        formatter = GoogleFormatter()
        active_work = [
            {"id": i, "name": f"Work Item {i}"} for i in range(1, 16)
        ]

        result = formatter.format_session(
            "",
            project={"name": "Test"},
            active_work=active_work,
        )

        # Should include first 10
        for i in range(1, 11):
            assert f"Work Item {i}" in result
        # Should not include 11-15
        for i in range(11, 16):
            assert f"Work Item {i}" not in result

    def test_format_session_with_contexts(self):
        """Test session formatting with task/static contexts."""
        formatter = GoogleFormatter()
        result = formatter.format_session(
            "",
            project={"name": "Test"},
            active_task_contexts=["## Active Task 1", "Details here"],
            static_context=["## Static Info", "Configuration data"],
            handover=["## Handover Notes", "Next steps from previous session"],
        )

        assert "## Active Task 1" in result
        assert "## Static Info" in result
        assert "## Handover Notes" in result


class TestHelperMethods:
    """Test helper methods."""

    def test_format_6w_context_complete(self):
        """Test 6W context formatting with all fields."""
        formatter = GoogleFormatter()
        six_w = UnifiedSixW(
            implementers=["Developer"],
            functional_requirements=["Implement feature"],
            dependencies_timeline=["Sprint 3"],
            affected_services=["Backend module"],
            business_value="User requirement",
            suggested_approach="Follow TDD approach",
        )

        result = formatter._format_6w_context(six_w)

        assert "### Merged Context (Task → Work Item → Project)" in result
        assert "**WHO**: Implementers: Developer" in result
        assert "**WHAT**: Implement feature" in result
        assert "**WHEN**: Dependencies: Sprint 3" in result
        assert "**WHERE**: Services: Backend module" in result
        assert "**WHY**: User requirement" in result
        assert "**HOW**: Follow TDD approach" in result

    def test_format_6w_context_partial(self):
        """Test 6W context formatting with some fields."""
        formatter = GoogleFormatter()
        six_w = UnifiedSixW(
            implementers=["Developer"],
            functional_requirements=["Implement feature"],
            # Other fields None/empty
        )

        result = formatter._format_6w_context(six_w)

        assert "**WHO**: Implementers: Developer" in result
        assert "**WHAT**: Implement feature" in result
        assert "**WHEN**:" not in result
        assert "**WHERE**:" not in result

    def test_format_plugin_facts(self):
        """Test plugin facts formatting."""
        formatter = GoogleFormatter()
        facts = {
            "pytest": {"version": "7.4.0"},
            "python": {"version": "3.11"},
            "mypy": {},  # No version
        }

        result = formatter._format_plugin_facts(facts)

        assert "### Tech Stack" in result
        assert "- pytest: 7.4.0" in result
        assert "- python: 3.11" in result
        assert "- mypy" in result

    def test_format_temporal_context_complete(self):
        """Test temporal context formatting with complete metadata."""
        formatter = GoogleFormatter()
        summaries = [
            {
                "summary_type": "task_completion",
                "session_date": "2025-01-14",
                "summary_text": "Completed implementation of formatter",
                "metadata": {
                    "key_decisions": ["Decision 1", "Decision 2", "Decision 3"],
                    "tasks_completed": [1, 2, 3],
                    "blockers_resolved": [10, 11],
                    "next_steps": ["Step 1", "Step 2", "Step 3"],
                },
            }
        ]

        result = formatter._format_temporal_context(summaries)
        result_str = '\n'.join(result)

        assert "### Recent Sessions" in result_str
        assert "- Task_Completion (2025-01-14)" in result_str
        assert "Completed implementation of formatter" in result_str
        assert "Key Decisions:" in result_str
        # Should limit to 2 decisions
        assert "• Decision 1" in result_str
        assert "• Decision 2" in result_str
        assert "Decision 3" not in result_str
        assert "Tasks Completed: 3" in result_str
        assert "Blockers Resolved: 2" in result_str
        # Should limit to 2 next steps
        assert "• Step 1" in result_str
        assert "• Step 2" in result_str
        assert "Step 3" not in result_str

    def test_format_temporal_context_long_summary(self):
        """Test temporal context truncates long summaries."""
        formatter = GoogleFormatter()
        long_text = "A" * 500  # 500 chars
        summaries = [
            {
                "summary_type": "session",
                "session_date": "2025-01-14",
                "summary_text": long_text,
            }
        ]

        result = formatter._format_temporal_context(summaries)
        result_str = '\n'.join(result)

        # Should be truncated to ~200 chars
        assert "### Recent Sessions" in result_str
        # Should contain truncation indicator
        assert "..." in result_str
        # Should not contain full 500 chars
        assert long_text not in result_str

    def test_format_temporal_context_empty(self):
        """Test temporal context with empty list."""
        formatter = GoogleFormatter()
        result = formatter._format_temporal_context([])

        # Should return empty list
        assert result == []


class TestTokenOptimization:
    """Test token budget optimization features."""

    def test_sop_limit_smaller_than_anthropic(self):
        """Verify SOP limit is smaller than Anthropic's 500."""
        formatter = GoogleFormatter()
        assert formatter._SOP_MAX_CHARS == 400
        assert formatter._SOP_MAX_CHARS < 500

    def test_temporal_session_limit(self):
        """Verify temporal sessions limited to 5."""
        formatter = GoogleFormatter()
        assert formatter._MAX_TEMPORAL_SESSIONS == 5

    def test_compact_formatting(self):
        """Test compact formatting compared to verbose alternatives."""
        formatter = GoogleFormatter()
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            task={
                "id": 1,
                "name": "Test Task",
                "type": "IMPLEMENTATION",
                "effort_hours": 2,
            },
            merged_6w=UnifiedSixW(
                implementers=["Dev"],
                functional_requirements=["Task"]
            ),
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        result = formatter.format_task(payload)

        # Should use compact bullet format, not verbose paragraphs
        assert "**Task #1**:" in result  # Compact header
        assert "(implementation, 2h)" in result  # Inline metadata

    def test_active_work_item_limit(self):
        """Test active work items limited to 10 for session context."""
        formatter = GoogleFormatter()
        active_work = [{"id": i, "name": f"Item {i}"} for i in range(15)]

        result = formatter.format_session(
            "",
            project={"name": "Test"},
            active_work=active_work,
        )

        # Count work items in result
        work_item_count = result.count("- **WI-")
        assert work_item_count == 10


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_none_task_in_payload(self):
        """Test handling when task is None."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            task=None,
            merged_6w=UnifiedSixW(),
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        assert "**Task**: Unknown" in result

    def test_empty_plugin_facts(self):
        """Test handling empty plugin facts."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            merged_6w=UnifiedSixW(),
            plugin_facts={},
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        # Should not include Tech Stack section
        assert "### Tech Stack" not in result

    def test_no_warnings(self):
        """Test handling when no warnings present."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            merged_6w=UnifiedSixW(),
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            warnings=[],
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        assert "**Warnings**:" not in result

    def test_no_agent_sop(self):
        """Test handling when agent SOP is None."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            merged_6w=UnifiedSixW(),
            agent_sop=None,
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        assert "### Agent SOP" not in result

    def test_no_temporal_context(self):
        """Test handling when temporal context is empty."""
        payload = ContextPayload(
            project={"id": 1, "name": "Test"},
            merged_6w=UnifiedSixW(),
            temporal_context=[],
            confidence_score=0.75,
            confidence_band=ConfidenceBand.GREEN,
            assembled_at=datetime.now(),
            assembly_duration_ms=50.0,
        )

        formatter = GoogleFormatter()
        result = formatter.format_task(payload)

        assert "### Recent Sessions" not in result
