"""
Tests for Claude Code Memory Tool

Tests WI-116 Task #623: Create Claude Code Memory Tool System

Test Coverage:
- Read operations (memory files)
- Write operations (database updates + staleness triggers)
- Search functionality (full-text search)
- List operations (memory types)
- Stats operations (memory statistics)
- Error handling
- Integration with memory system
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from agentpm.providers.anthropic.claude_code.runtime.tools.memory_tool import (
    MemoryTool,
    MemoryToolError
)
from agentpm.core.database.models.memory import (
    MemoryFile,
    MemoryFileType,
    ValidationStatus
)


class TestMemoryToolRead:
    """Test read_memory operations."""

    def test_read_memory_success(self, db_service, sample_memory_file):
        """Test reading memory file successfully."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                mock_get.return_value = sample_memory_file
                mock_is_current.return_value = True

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                content = tool.read_memory("RULES")

                # Assert
                assert content == sample_memory_file.content
                mock_get.assert_called_once_with(db_service, 1, MemoryFileType.RULES)
                mock_is_current.assert_called_once()

    def test_read_memory_with_query_filter(self, db_service):
        """Test reading memory with query filter."""
        # Setup - use longer content to ensure filtering makes a difference
        memory_file = MemoryFile(
            id=1,
            project_id=1,
            file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="""Line 1: Introduction
Line 2: Testing guidelines
Line 3: More content
Line 4: Even more content
Line 5: Quality gates are here
Line 6: Additional stuff
Line 7: Final line""",
            source_tables=["rules"],
            template_version="1.0.0",
            confidence_score=0.95,
            completeness_score=0.90,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="memory-generator",
            generated_at="2025-10-21T10:00:00"
        )
        original_content = memory_file.content

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                mock_get.return_value = memory_file
                mock_is_current.return_value = True

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                content = tool.read_memory("RULES", query="quality")

                # Assert
                assert "Quality gates" in content
                # Should not include line 1 or line 7 due to context filtering
                assert "Introduction" not in content or "Final line" not in content

    def test_read_memory_invalid_type(self, db_service):
        """Test reading with invalid memory type."""
        # Execute & Assert
        tool = MemoryTool(db_service, project_id=1)
        with pytest.raises(MemoryToolError) as exc_info:
            tool.read_memory("INVALID_TYPE")

        assert "Invalid memory type" in str(exc_info.value)

    def test_read_memory_not_found(self, db_service):
        """Test reading memory file that doesn't exist."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                mock_get.return_value = None
                mock_is_current.return_value = False

                # Execute & Assert
                tool = MemoryTool(db_service, project_id=1)
                with pytest.raises(MemoryToolError) as exc_info:
                    tool.read_memory("RULES")

                assert "not found" in str(exc_info.value)

    def test_read_memory_stale_warning(self, db_service, sample_memory_file, caplog):
        """Test warning when memory file is stale."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                mock_get.return_value = sample_memory_file
                mock_is_current.return_value = False  # Stale

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                content = tool.read_memory("RULES")

                # Assert
                assert "stale" in caplog.text.lower()
                assert content == sample_memory_file.content

    def test_read_memory_all_types(self, db_service, sample_memory_file):
        """Test reading all memory types."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                mock_get.return_value = sample_memory_file
                mock_is_current.return_value = True

                # Execute
                tool = MemoryTool(db_service, project_id=1)

                for memory_type in ["RULES", "AGENTS", "WORKFLOW", "CONTEXT", "PROJECT", "PRINCIPLES", "IDEAS"]:
                    content = tool.read_memory(memory_type)
                    assert content is not None


class TestMemoryToolWrite:
    """Test write_memory operations."""

    def test_write_memory_success(self, db_service, sample_memory_file):
        """Test writing to memory successfully."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.mark_stale') as mock_mark_stale:
                mock_get.return_value = sample_memory_file

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                result = tool.write_memory("PROJECT", key="status", value="active")

                # Assert
                assert result is True
                mock_mark_stale.assert_called_once_with(db_service, sample_memory_file.id)

    def test_write_memory_no_regeneration(self, db_service, sample_memory_file):
        """Test writing without triggering regeneration."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.mark_stale') as mock_mark_stale:
                mock_get.return_value = sample_memory_file

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                result = tool.write_memory(
                    "PROJECT",
                    key="status",
                    value="active",
                    trigger_regeneration=False
                )

                # Assert
                assert result is True
                mock_mark_stale.assert_not_called()

    def test_write_memory_invalid_type(self, db_service):
        """Test writing with invalid memory type."""
        # Execute & Assert
        tool = MemoryTool(db_service, project_id=1)
        with pytest.raises(MemoryToolError) as exc_info:
            tool.write_memory("INVALID_TYPE", key="test", value="value")

        assert "Invalid memory type" in str(exc_info.value)

    def test_write_memory_not_found(self, db_service):
        """Test writing to non-existent memory file."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.return_value = None

            # Execute & Assert
            tool = MemoryTool(db_service, project_id=1)
            with pytest.raises(MemoryToolError) as exc_info:
                tool.write_memory("RULES", key="test", value="value")

            assert "not found" in str(exc_info.value)


class TestMemoryToolSearch:
    """Test search_memory operations."""

    def test_search_memory_success(self, db_service, sample_memory_files):
        """Test searching across memory files."""
        # Setup
        def get_file_by_type(db, project_id, file_type):
            for f in sample_memory_files:
                if f.file_type == file_type:
                    return f
            return None

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = get_file_by_type

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            results = tool.search_memory("quality gates", limit=5)

            # Assert
            assert isinstance(results, list)
            assert len(results) <= 5
            # Check that results have expected structure
            for result in results:
                assert "memory_type" in result
                assert "excerpt" in result
                # Each sample file has "quality gates" in content
                if result:
                    assert "quality gates" in result["excerpt"].lower()

    def test_search_memory_specific_types(self, db_service, sample_memory_file):
        """Test searching specific memory types."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.return_value = sample_memory_file

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            results = tool.search_memory(
                "test",
                memory_types=["RULES", "AGENTS"],
                limit=10
            )

            # Assert
            assert isinstance(results, list)
            # Called for RULES and AGENTS
            assert mock_get.call_count == 2

    def test_search_memory_min_confidence(self, db_service):
        """Test searching with minimum confidence threshold."""
        # Setup
        low_confidence_file = MemoryFile(
            id=1, project_id=1, file_type=MemoryFileType.RULES,
            file_path=".claude/RULES.md",
            content="Content with test keyword",
            source_tables=["rules"], generated_by="test",
            generated_at="2025-10-21T10:00:00",
            confidence_score=0.3  # Below threshold
        )

        def get_file_by_type(db, project_id, file_type):
            if file_type == MemoryFileType.RULES:
                return low_confidence_file
            return None

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = get_file_by_type

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            results = tool.search_memory("test", min_confidence=0.5, memory_types=["RULES"])

            # Assert - low confidence file should be skipped
            assert isinstance(results, list)
            # Should be empty because RULES file has confidence 0.3 < 0.5
            assert len(results) == 0

    def test_search_memory_invalid_types(self, db_service):
        """Test searching with invalid memory types."""
        # Execute & Assert
        tool = MemoryTool(db_service, project_id=1)
        with pytest.raises(MemoryToolError) as exc_info:
            tool.search_memory("test", memory_types=["INVALID", "RULES"])

        assert "Invalid memory types" in str(exc_info.value)

    def test_search_memory_no_results(self, db_service, sample_memory_file):
        """Test search with no matches."""
        # Setup
        sample_memory_file.content = "No matches here"

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.return_value = sample_memory_file

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            results = tool.search_memory("NONEXISTENT_QUERY_STRING_12345")

            # Assert
            assert results == []


class TestMemoryToolList:
    """Test list_memory_types operations."""

    def test_list_memory_types_success(self, db_service, sample_memory_files):
        """Test listing all memory types."""
        # Setup
        def get_file_by_type(db, project_id, file_type):
            for f in sample_memory_files:
                if f.file_type == file_type:
                    return f
            return None

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = get_file_by_type

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            memory_types = tool.list_memory_types()

            # Assert
            assert isinstance(memory_types, list)
            assert len(memory_types) == 7  # All memory types (RULES, AGENTS, WORKFLOW, CONTEXT, PROJECT, PRINCIPLES, IDEAS)

            for mt in memory_types:
                assert "name" in mt
                assert "description" in mt
                assert "available" in mt

    def test_list_memory_types_with_metadata(self, db_service, sample_memory_file):
        """Test list includes full metadata for available files."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            def get_file(db, project_id, file_type):
                if file_type == MemoryFileType.RULES:
                    return sample_memory_file
                return None

            mock_get.side_effect = get_file

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            memory_types = tool.list_memory_types()

            # Assert
            rules_info = next(mt for mt in memory_types if mt["name"] == "RULES")
            assert rules_info["available"] is True
            assert "file_path" in rules_info
            assert "confidence" in rules_info
            assert "completeness" in rules_info

    def test_list_memory_types_unavailable(self, db_service):
        """Test list shows unavailable memory types."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.return_value = None  # All unavailable

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            memory_types = tool.list_memory_types()

            # Assert
            assert all(not mt["available"] for mt in memory_types)


class TestMemoryToolStats:
    """Test get_memory_stats operations."""

    def test_get_memory_stats_success(self, db_service, sample_memory_files):
        """Test getting memory statistics."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.list_memory_files') as mock_list:
            with patch('agentpm.core.database.methods.memory_methods.get_stale_memory_files') as mock_stale:
                mock_list.return_value = sample_memory_files
                mock_stale.return_value = [sample_memory_files[0]]  # 1 stale

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                stats = tool.get_memory_stats()

                # Assert
                assert stats["project_id"] == 1
                assert stats["total_files"] == len(sample_memory_files)
                assert stats["stale_files"] == 1
                assert "total_size_bytes" in stats
                assert "avg_confidence" in stats
                assert "status_counts" in stats

    def test_get_memory_stats_empty(self, db_service):
        """Test stats with no memory files."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.list_memory_files') as mock_list:
            with patch('agentpm.core.database.methods.memory_methods.get_stale_memory_files') as mock_stale:
                mock_list.return_value = []
                mock_stale.return_value = []

                # Execute
                tool = MemoryTool(db_service, project_id=1)
                stats = tool.get_memory_stats()

                # Assert
                assert stats["total_files"] == 0
                assert stats["stale_files"] == 0
                assert stats["avg_confidence"] == 0.0


class TestMemoryToolHelpers:
    """Test helper methods."""

    def test_filter_content(self, db_service):
        """Test content filtering."""
        # Setup
        tool = MemoryTool(db_service, project_id=1)
        content = """Line 1
Line 2: quality gates are important
Line 3
Line 4: another quality mention
Line 5"""

        # Execute
        filtered = tool._filter_content(content, "quality")

        # Assert
        assert "quality gates" in filtered
        assert "another quality" in filtered

    def test_search_content(self, db_service):
        """Test content search."""
        # Setup
        tool = MemoryTool(db_service, project_id=1)
        content = """Line 1
Line 2: testing is important
Line 3
Line 4: more testing content
Line 5"""

        # Execute
        matches = tool._search_content(content, "testing")

        # Assert
        assert len(matches) == 2
        assert all("testing" in m["excerpt"].lower() for m in matches)
        assert all("line_number" in m for m in matches)

    def test_get_memory_description(self, db_service):
        """Test memory type descriptions."""
        # Setup
        tool = MemoryTool(db_service, project_id=1)

        # Execute & Assert
        for memory_type in ["RULES", "AGENTS", "WORKFLOW", "CONTEXT", "PROJECT", "PRINCIPLES", "IDEAS"]:
            desc = tool._get_memory_description(memory_type)
            assert desc is not None
            assert len(desc) > 0


class TestMemoryToolIntegration:
    """Integration tests with memory system."""

    def test_read_write_flow(self, db_service, sample_memory_file):
        """Test complete read-write-regenerate flow."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            with patch('agentpm.core.database.methods.memory_methods.mark_stale') as mock_mark_stale:
                with patch('agentpm.core.database.methods.memory_methods.is_memory_file_current') as mock_is_current:
                    mock_get.return_value = sample_memory_file
                    mock_is_current.return_value = True

                    # Execute
                    tool = MemoryTool(db_service, project_id=1)

                    # Read
                    content = tool.read_memory("RULES")
                    assert content is not None

                    # Write (marks as stale)
                    result = tool.write_memory("RULES", key="test", value="value")
                    assert result is True
                    mock_mark_stale.assert_called_once()

    def test_search_across_types(self, db_service):
        """Test searching across multiple memory types."""
        # Setup
        files = {
            MemoryFileType.RULES: MemoryFile(
                id=1, project_id=1, file_type=MemoryFileType.RULES,
                file_path=".claude/RULES.md",
                content="Quality gates and testing requirements",
                source_tables=["rules"], generated_by="test",
                generated_at="2025-10-21T10:00:00"
            ),
            MemoryFileType.AGENTS: MemoryFile(
                id=2, project_id=1, file_type=MemoryFileType.AGENTS,
                file_path=".claude/AGENTS.md",
                content="Agent testing and quality validation",
                source_tables=["agents"], generated_by="test",
                generated_at="2025-10-21T10:00:00"
            ),
        }

        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = lambda db, pid, ftype: files.get(ftype)

            # Execute
            tool = MemoryTool(db_service, project_id=1)
            results = tool.search_memory("testing")

            # Assert
            assert len(results) >= 2
            memory_types = {r["memory_type"] for r in results}
            assert "rules" in memory_types or "RULES" in memory_types


class TestMemoryToolErrors:
    """Test error handling."""

    def test_read_error_handling(self, db_service):
        """Test error handling in read operations."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = Exception("Database error")

            # Execute & Assert
            tool = MemoryTool(db_service, project_id=1)
            with pytest.raises(MemoryToolError):
                tool.read_memory("RULES")

    def test_write_error_handling(self, db_service):
        """Test error handling in write operations."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = Exception("Database error")

            # Execute & Assert
            tool = MemoryTool(db_service, project_id=1)
            with pytest.raises(MemoryToolError):
                tool.write_memory("RULES", key="test", value="value")

    def test_search_error_handling(self, db_service):
        """Test error handling in search operations."""
        # Setup
        with patch('agentpm.core.database.methods.memory_methods.get_memory_file_by_type') as mock_get:
            mock_get.side_effect = Exception("Database error")

            # Execute & Assert
            tool = MemoryTool(db_service, project_id=1)
            with pytest.raises(MemoryToolError):
                tool.search_memory("test")


# Fixtures

@pytest.fixture
def db_service():
    """Mock database service."""
    return Mock()


@pytest.fixture
def sample_memory_file():
    """Sample memory file for testing."""
    return MemoryFile(
        id=1,
        project_id=1,
        file_type=MemoryFileType.RULES,
        file_path=".claude/RULES.md",
        content="# APM (Agent Project Manager) Governance Rules\n\nQuality gates ensure work meets standards.",
        source_tables=["rules"],
        template_version="1.0.0",
        confidence_score=0.95,
        completeness_score=0.90,
        validation_status=ValidationStatus.VALIDATED,
        generated_by="memory-generator",
        generated_at="2025-10-21T10:00:00"
    )


@pytest.fixture
def sample_memory_files():
    """Multiple sample memory files."""
    return [
        MemoryFile(
            id=i,
            project_id=1,
            file_type=file_type,
            file_path=f".claude/{file_type.value.upper()}.md",
            content=f"Content for {file_type.value} with quality gates and testing",
            source_tables=[file_type.value],
            template_version="1.0.0",
            confidence_score=0.95,
            completeness_score=0.90,
            validation_status=ValidationStatus.VALIDATED,
            generated_by="memory-generator",
            generated_at="2025-10-21T10:00:00"
        )
        for i, file_type in enumerate([
            MemoryFileType.RULES,
            MemoryFileType.AGENTS,
            MemoryFileType.WORKFLOW,
        ], start=1)
    ]
