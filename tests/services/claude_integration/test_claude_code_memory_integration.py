"""
Tests for Claude Code Plugin Memory Integration

Tests integration between ClaudeCodePlugin and MemoryTool.
Part of WI-116 Task #623: Create Claude Code Memory Tool System
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from agentpm.providers.anthropic.claude_code.runtime.plugins.claude_code import ClaudeCodePlugin
from agentpm.core.database.models.memory import MemoryFile, MemoryFileType, ValidationStatus


class TestClaudeCodeMemoryIntegration:
    """Test memory operations through Claude Code plugin."""

    def test_aipm_memory_read_success(self):
        """Test AIPM memory read through plugin."""
        # Setup
        plugin = ClaudeCodePlugin()
        sample_content = "# AIPM Rules\n\nContent here"

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.read_memory.return_value = sample_content

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "read",
                "memory_type": "RULES",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            assert result["data"]["content"] == sample_content
            assert result["data"]["memory_type"] == "RULES"
            mock_tool.read_memory.assert_called_once_with("RULES", query=None)

    def test_aipm_memory_read_with_query(self):
        """Test AIPM memory read with query filter."""
        # Setup
        plugin = ClaudeCodePlugin()
        filtered_content = "Quality gates content"

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.read_memory.return_value = filtered_content

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "read",
                "memory_type": "RULES",
                "query": "quality gates",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            assert result["data"]["content"] == filtered_content
            mock_tool.read_memory.assert_called_once_with("RULES", query="quality gates")

    def test_aipm_memory_search_success(self):
        """Test AIPM memory search through plugin."""
        # Setup
        plugin = ClaudeCodePlugin()
        search_results = [
            {
                "memory_type": "RULES",
                "excerpt": "Quality gates ensure...",
                "line_number": 10,
                "confidence": 0.95
            },
            {
                "memory_type": "WORKFLOW",
                "excerpt": "Quality gates must pass...",
                "line_number": 25,
                "confidence": 0.90
            }
        ]

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.search_memory.return_value = search_results

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "search",
                "query": "quality gates",
                "limit": 10,
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            assert result["data"]["result_count"] == 2
            assert len(result["data"]["results"]) == 2
            mock_tool.search_memory.assert_called_once_with(
                query="quality gates",
                memory_types=None,
                limit=10
            )

    def test_aipm_memory_search_specific_types(self):
        """Test AIPM memory search with specific types."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.search_memory.return_value = []

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "search",
                "query": "testing",
                "memory_types": ["RULES", "AGENTS"],
                "limit": 5,
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            mock_tool.search_memory.assert_called_once_with(
                query="testing",
                memory_types=["RULES", "AGENTS"],
                limit=5
            )

    def test_aipm_memory_list_success(self):
        """Test listing AIPM memory types."""
        # Setup
        plugin = ClaudeCodePlugin()
        memory_types = [
            {
                "name": "RULES",
                "description": "Governance rules",
                "available": True,
                "confidence": 0.95
            },
            {
                "name": "AGENTS",
                "description": "Agent system",
                "available": True,
                "confidence": 0.90
            }
        ]

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.list_memory_types.return_value = memory_types

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "list",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            assert len(result["data"]["memory_types"]) == 2
            mock_tool.list_memory_types.assert_called_once()

    def test_aipm_memory_stats_success(self):
        """Test getting AIPM memory statistics."""
        # Setup
        plugin = ClaudeCodePlugin()
        stats = {
            "project_id": 1,
            "total_files": 5,
            "stale_files": 1,
            "avg_confidence": 0.92
        }

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.get_memory_stats.return_value = stats

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "stats",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "success"
            assert result["data"]["total_files"] == 5
            assert result["data"]["stale_files"] == 1
            mock_tool.get_memory_stats.assert_called_once()

    def test_aipm_memory_read_missing_type(self):
        """Test AIPM memory read without memory_type."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db'):
            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "read",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "error"
            assert "memory_type required" in result["message"]

    def test_aipm_memory_search_missing_query(self):
        """Test AIPM memory search without query."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db'):
            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "search",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "error"
            assert "query required" in result["message"]

    def test_aipm_memory_unknown_action(self):
        """Test AIPM memory with unknown action."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db'):
            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "unknown_action",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "error"
            assert "Unknown AIPM memory action" in result["message"]

    def test_aipm_memory_tool_initialization(self):
        """Test MemoryTool is initialized on first use."""
        # Setup
        plugin = ClaudeCodePlugin()
        assert plugin._memory_tool is None

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            with patch.object(plugin, '_memory_tool', None):
                # First call should initialize
                with patch('agentpm.services.claude_integration.tools.memory_tool.MemoryTool') as MockMemoryTool:
                    mock_tool_instance = Mock()
                    MockMemoryTool.return_value = mock_tool_instance
                    mock_tool_instance.list_memory_types.return_value = []

                    # Execute
                    result = plugin.handle({
                        "scope": "aipm",
                        "action": "list",
                        "session_id": "test-session"
                    })

                    # Assert - tool was initialized
                    assert result["status"] == "success"
                    MockMemoryTool.assert_called_once_with(mock_db)

    def test_session_memory_vs_aipm_memory(self):
        """Test distinction between session and AIPM memory."""
        # Setup
        plugin = ClaudeCodePlugin()

        # Session memory
        result1 = plugin.handle({
            "scope": "session",
            "action": "set",
            "key": "test_key",
            "value": "test_value",
            "session_id": "test-session"
        })
        assert result1["status"] == "success"

        result2 = plugin.handle({
            "scope": "session",
            "action": "get",
            "key": "test_key",
            "session_id": "test-session"
        })
        assert result2["status"] == "success"
        assert result2["data"]["value"] == "test_value"

        # AIPM memory (different behavior)
        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.read_memory.return_value = "AIPM content"

            result3 = plugin.handle({
                "scope": "aipm",
                "action": "read",
                "memory_type": "RULES",
                "session_id": "test-session"
            })
            assert result3["status"] == "success"
            assert result3["data"]["content"] == "AIPM content"


class TestClaudeCodeMemoryErrors:
    """Test error handling in memory integration."""

    def test_aipm_memory_tool_error(self):
        """Test handling of MemoryTool errors."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db'):
            with patch('agentpm.services.claude_integration.tools.memory_tool.MemoryTool') as MockTool:
                mock_tool = Mock()
                MockTool.return_value = mock_tool
                mock_tool.read_memory.side_effect = Exception("Database error")

                # Execute
                result = plugin.handle({
                    "scope": "aipm",
                    "action": "read",
                    "memory_type": "RULES",
                    "session_id": "test-session"
                })

                # Assert
                assert result["status"] == "error"
                assert "Database error" in result["error"]

    def test_aipm_memory_initialization_error(self):
        """Test handling of MemoryTool initialization errors."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("DB connection failed")

            # Execute
            result = plugin.handle({
                "scope": "aipm",
                "action": "list",
                "session_id": "test-session"
            })

            # Assert
            assert result["status"] == "error"


class TestClaudeCodeMemoryPerformance:
    """Test performance aspects of memory integration."""

    def test_memory_tool_reuse(self):
        """Test MemoryTool instance is reused across calls."""
        # Setup
        plugin = ClaudeCodePlugin()

        with patch('agentpm.services.claude_integration.plugins.claude_code.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            with patch('agentpm.services.claude_integration.tools.memory_tool.MemoryTool') as MockMemoryTool:
                mock_tool = Mock()
                MockMemoryTool.return_value = mock_tool
                mock_tool.list_memory_types.return_value = []

                # Execute multiple calls
                for _ in range(3):
                    plugin.handle({
                        "scope": "aipm",
                        "action": "list",
                        "session_id": "test-session"
                    })

                # Assert - MemoryTool created only once (reused)
                assert MockMemoryTool.call_count == 1

    def test_large_search_results(self):
        """Test handling of large search result sets."""
        # Setup
        plugin = ClaudeCodePlugin()
        large_results = [
            {
                "memory_type": "RULES",
                "excerpt": f"Content {i}",
                "line_number": i
            }
            for i in range(100)
        ]

        with patch.object(plugin, '_memory_tool') as mock_tool:
            mock_tool.search_memory.return_value = large_results

            # Execute with limit
            result = plugin.handle({
                "scope": "aipm",
                "action": "search",
                "query": "test",
                "limit": 10,
                "session_id": "test-session"
            })

            # Assert - limit was applied
            assert result["status"] == "success"
            # MemoryTool should have been called with limit=10
            mock_tool.search_memory.assert_called_once()
            call_args = mock_tool.search_memory.call_args
            assert call_args[1]["limit"] == 10
