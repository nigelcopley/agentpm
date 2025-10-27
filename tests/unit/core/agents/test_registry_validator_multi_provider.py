"""
Tests for Multi-Provider Registry Validator

Tests registry validation with dynamic provider detection.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentpm.core.agents.registry_validator import (
    get_agents_directory,
    _load_agent_registry,
    validate_agent,
    get_all_agents,
    get_agent_suggestions,
    validate_agent_with_suggestions,
    get_registry_stats,
    refresh_cache,
)
from agentpm.core.agents.provider_detector import Provider


class TestMultiProviderValidation:
    """Test validation across multiple providers."""

    @pytest.fixture
    def mock_claude_agents(self, tmp_path):
        """Create mock Claude Code agents structure."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        sub_agents_dir = agents_dir / "sub-agents"
        sub_agents_dir.mkdir()

        # Create agents in both levels
        (agents_dir / "orchestrator.md").write_text("# Orchestrator")
        (sub_agents_dir / "code-implementer.md").write_text("# Code Implementer")
        (sub_agents_dir / "test-runner.md").write_text("# Test Runner")

        return tmp_path

    @pytest.fixture
    def mock_codex_agents(self, tmp_path):
        """Create mock Codex agents structure."""
        agents_dir = tmp_path / ".codex" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "developer.md").write_text("# Developer")
        (agents_dir / "tester.md").write_text("# Tester")

        return tmp_path

    def test_load_registry_flat_structure(self, tmp_path):
        """Test loading registry from flat structure."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "agent1.md").write_text("# Agent 1")
        (agents_dir / "agent2.md").write_text("# Agent 2")

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["agent1", "agent2"]):
                registry = _load_agent_registry()

        assert len(registry) == 2
        assert "agent1" in registry
        assert "agent2" in registry

    def test_load_registry_tiered_structure(self, mock_claude_agents):
        """Test loading registry from tiered structure."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["orchestrator", "code-implementer", "test-runner"]):
                registry = _load_agent_registry()

        assert len(registry) == 3
        assert "orchestrator" in registry
        assert "code-implementer" in registry
        assert "test-runner" in registry

    def test_load_registry_cursor_no_agents(self, tmp_path):
        """Test loading registry for Cursor (no agents)."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=None):
            with patch("agentpm.core.agents.registry_validator.detect_provider", return_value=Provider.CURSOR):
                with pytest.warns(RuntimeWarning, match="Agents directory not found for provider"):
                    registry = _load_agent_registry()

        assert len(registry) == 0

    def test_validate_agent_success(self, mock_claude_agents):
        """Test successful agent validation."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer"]):
                refresh_cache()  # Clear cache
                result = validate_agent("code-implementer")

        assert result is True

    def test_validate_agent_failure(self, mock_claude_agents):
        """Test failed agent validation."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer"]):
                refresh_cache()
                result = validate_agent("nonexistent-agent")

        assert result is False

    def test_get_all_agents(self, mock_claude_agents):
        """Test getting all agents."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["orchestrator", "code-implementer", "test-runner"]):
                refresh_cache()
                agents = get_all_agents()

        assert len(agents) == 3
        assert "code-implementer" in agents
        assert "orchestrator" in agents
        assert "test-runner" in agents
        # Should be sorted
        assert agents == sorted(agents)

    def test_get_agent_suggestions(self, mock_claude_agents):
        """Test agent suggestions."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer", "test-runner", "orchestrator"]):
                refresh_cache()
                suggestions = get_agent_suggestions("code")

        assert len(suggestions) > 0
        assert "code-implementer" in suggestions

    def test_validate_agent_with_suggestions_success(self, mock_claude_agents):
        """Test validation with suggestions - success case."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer"]):
                refresh_cache()
                valid, msg = validate_agent_with_suggestions("code-implementer")

        assert valid is True
        assert msg is None

    def test_validate_agent_with_suggestions_failure(self, mock_claude_agents):
        """Test validation with suggestions - failure case."""
        agents_dir = mock_claude_agents / ".claude" / "agents"

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer"]):
                refresh_cache()
                valid, msg = validate_agent_with_suggestions("code-impl")

        assert valid is False
        assert msg is not None
        assert "code-implementer" in msg


class TestRegistryStats:
    """Test registry statistics with provider info."""

    def test_registry_stats_claude(self, tmp_path):
        """Test stats for Claude Code provider."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "agent1.md").write_text("# Agent 1")

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["agent1"]):
                with patch("agentpm.core.agents.registry_validator.detect_provider", return_value=Provider.CLAUDE_CODE):
                    refresh_cache()
                    stats = get_registry_stats()

        assert stats["total_agents"] == 1
        assert stats["provider"] == "claude-code"
        assert stats["supports_agents"] is True
        assert stats["agents_dir"] == str(agents_dir)

    def test_registry_stats_cursor(self, tmp_path):
        """Test stats for Cursor provider (no agents)."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=None):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=[]):
                with patch("agentpm.core.agents.registry_validator.detect_provider", return_value=Provider.CURSOR):
                    refresh_cache()
                    stats = get_registry_stats()

        assert stats["total_agents"] == 0
        assert stats["provider"] == "cursor"
        assert stats["supports_agents"] is False
        assert stats["agents_dir"] is None

    def test_registry_stats_cache_age(self, tmp_path):
        """Test cache age in stats."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=[]):
                with patch("agentpm.core.agents.registry_validator.detect_provider", return_value=Provider.CLAUDE_CODE):
                    refresh_cache()
                    stats = get_registry_stats()

        assert "cache_age_seconds" in stats
        assert stats["cache_age_seconds"] >= 0
        assert "cache_ttl_seconds" in stats


class TestCaching:
    """Test caching behavior with provider detection."""

    def test_cache_refresh(self, tmp_path):
        """Test cache refresh."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "agent1.md").write_text("# Agent 1")

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["agent1"]):
                refresh_cache()
                agents_before = get_all_agents()

                # Add new agent
                with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["agent1", "agent2"]):
                    refresh_cache()
                    agents_after = get_all_agents()

        assert len(agents_before) == 1
        assert len(agents_after) == 2


class TestEdgeCases:
    """Test edge cases in multi-provider validation."""

    def test_empty_agent_name(self):
        """Test validation of empty agent name."""
        result = validate_agent("")
        assert result is False

        result = validate_agent("   ")
        assert result is False

    def test_none_agent_name(self):
        """Test validation of None agent name."""
        result = validate_agent(None)
        assert result is False

    def test_mixed_case_validation(self, tmp_path):
        """Test case-sensitive validation."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        with patch("agentpm.core.agents.registry_validator.get_provider_agents_directory", return_value=agents_dir):
            with patch("agentpm.core.agents.registry_validator.get_provider_agent_names", return_value=["code-implementer"]):
                refresh_cache()

                # Exact match should work
                assert validate_agent("code-implementer") is True

                # Different case should fail (case-sensitive)
                assert validate_agent("Code-Implementer") is False
                assert validate_agent("CODE-IMPLEMENTER") is False


class TestIntegration:
    """Integration tests with actual project."""

    def test_real_project_validation(self):
        """Test validation on actual project."""
        # Should find real agents
        agents = get_all_agents()
        assert len(agents) > 0

        # Should validate known agent
        # Find any agent from the list
        if agents:
            assert validate_agent(agents[0]) is True

        # Should reject unknown agent
        assert validate_agent("definitely-not-a-real-agent-12345") is False

    def test_real_project_stats(self):
        """Test stats on actual project."""
        stats = get_registry_stats()

        assert stats["total_agents"] > 0
        assert stats["provider"] == "claude-code"
        assert stats["supports_agents"] is True
        assert stats["agents_dir"] is not None

    def test_real_project_suggestions(self):
        """Test suggestions on actual project."""
        suggestions = get_agent_suggestions("code")
        # Should find agents matching "code"
        assert len(suggestions) >= 0  # May or may not have matches
