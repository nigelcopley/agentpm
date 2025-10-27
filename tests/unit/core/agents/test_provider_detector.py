"""
Tests for Provider Detection Utility

Tests multi-provider detection and path resolution.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentpm.core.agents.provider_detector import (
    Provider,
    detect_provider,
    get_project_root,
    get_provider_base_path,
    get_agents_directory,
    get_agent_paths,
    get_agent_names,
    get_provider_info,
)


class TestProviderDetection:
    """Test provider detection logic."""

    def test_detect_claude_code(self, tmp_path):
        """Test Claude Code detection."""
        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        provider = detect_provider(tmp_path)
        assert provider == Provider.CLAUDE_CODE

    def test_detect_codex(self, tmp_path):
        """Test Codex detection."""
        # Create .codex directory (no .claude)
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()

        provider = detect_provider(tmp_path)
        assert provider == Provider.CODEX

    def test_detect_cursor_fallback(self, tmp_path):
        """Test Cursor detection as fallback."""
        # Create .cursor directory (no .claude or .codex)
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        provider = detect_provider(tmp_path)
        assert provider == Provider.CURSOR

    def test_detect_unknown(self, tmp_path):
        """Test unknown provider when no directories exist."""
        provider = detect_provider(tmp_path)
        assert provider == Provider.UNKNOWN

    def test_detect_precedence(self, tmp_path):
        """Test provider detection precedence (.claude > .codex > .cursor)."""
        # Create all three directories
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".codex").mkdir()
        (tmp_path / ".cursor").mkdir()

        # Should detect Claude Code (highest precedence)
        provider = detect_provider(tmp_path)
        assert provider == Provider.CLAUDE_CODE


class TestProviderPaths:
    """Test provider path resolution."""

    def test_get_provider_base_path_claude(self, tmp_path):
        """Test base path for Claude Code."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        base_path = get_provider_base_path(Provider.CLAUDE_CODE, tmp_path)
        assert base_path == claude_dir
        assert base_path.exists()

    def test_get_provider_base_path_codex(self, tmp_path):
        """Test base path for Codex."""
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()

        base_path = get_provider_base_path(Provider.CODEX, tmp_path)
        assert base_path == codex_dir

    def test_get_provider_base_path_cursor(self, tmp_path):
        """Test base path for Cursor."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        base_path = get_provider_base_path(Provider.CURSOR, tmp_path)
        assert base_path == cursor_dir

    def test_get_provider_base_path_not_found(self, tmp_path):
        """Test base path returns None when directory doesn't exist."""
        base_path = get_provider_base_path(Provider.CLAUDE_CODE, tmp_path)
        assert base_path is None

    def test_get_provider_base_path_auto_detect(self, tmp_path):
        """Test auto-detection of provider base path."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Don't specify provider, should auto-detect
        base_path = get_provider_base_path(project_root=tmp_path)
        assert base_path == claude_dir


class TestAgentsDirectory:
    """Test agents directory resolution."""

    def test_get_agents_directory_claude(self, tmp_path):
        """Test agents directory for Claude Code."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        result = get_agents_directory(Provider.CLAUDE_CODE, tmp_path)
        assert result == agents_dir

    def test_get_agents_directory_codex(self, tmp_path):
        """Test agents directory for Codex."""
        agents_dir = tmp_path / ".codex" / "agents"
        agents_dir.mkdir(parents=True)

        result = get_agents_directory(Provider.CODEX, tmp_path)
        assert result == agents_dir

    def test_get_agents_directory_cursor_none(self, tmp_path):
        """Test Cursor returns None (no agents)."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        result = get_agents_directory(Provider.CURSOR, tmp_path)
        assert result is None

    def test_get_agents_directory_not_found(self, tmp_path):
        """Test returns None when agents directory doesn't exist."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        # No agents subdirectory

        result = get_agents_directory(Provider.CLAUDE_CODE, tmp_path)
        assert result is None


class TestAgentPaths:
    """Test agent file path scanning."""

    def test_get_agent_paths_flat(self, tmp_path):
        """Test scanning flat agent directory."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create agent files
        (agents_dir / "agent1.md").write_text("# Agent 1")
        (agents_dir / "agent2.md").write_text("# Agent 2")
        (agents_dir / "not-agent.txt").write_text("Not an agent")

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path, include_subdirs=False)

        assert len(paths) == 2
        assert all(p.suffix == ".md" for p in paths)
        assert any(p.name == "agent1.md" for p in paths)
        assert any(p.name == "agent2.md" for p in paths)

    def test_get_agent_paths_tiered(self, tmp_path):
        """Test scanning tiered agent directory (with subdirectories)."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        sub_agents_dir = agents_dir / "sub-agents"
        sub_agents_dir.mkdir()

        # Create agents in both levels
        (agents_dir / "top-level.md").write_text("# Top Level")
        (sub_agents_dir / "sub-agent1.md").write_text("# Sub Agent 1")
        (sub_agents_dir / "sub-agent2.md").write_text("# Sub Agent 2")

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path, include_subdirs=True)

        assert len(paths) == 3
        assert any(p.name == "top-level.md" for p in paths)
        assert any(p.name == "sub-agent1.md" for p in paths)
        assert any(p.name == "sub-agent2.md" for p in paths)

    def test_get_agent_paths_exclude_subdirs(self, tmp_path):
        """Test excluding subdirectories from scan."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        sub_agents_dir = agents_dir / "sub-agents"
        sub_agents_dir.mkdir()

        (agents_dir / "top-level.md").write_text("# Top Level")
        (sub_agents_dir / "sub-agent1.md").write_text("# Sub Agent 1")

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path, include_subdirs=False)

        assert len(paths) == 1
        assert paths[0].name == "top-level.md"

    def test_get_agent_paths_empty(self, tmp_path):
        """Test empty agent directory."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path)
        assert len(paths) == 0

    def test_get_agent_paths_cursor(self, tmp_path):
        """Test Cursor returns empty list (no agents)."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        paths = get_agent_paths(Provider.CURSOR, tmp_path)
        assert len(paths) == 0


class TestAgentNames:
    """Test agent name extraction."""

    def test_get_agent_names(self, tmp_path):
        """Test extracting agent names from files."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "code-implementer.md").write_text("# Code Implementer")
        (agents_dir / "test-runner.md").write_text("# Test Runner")

        names = get_agent_names(Provider.CLAUDE_CODE, tmp_path)

        assert len(names) == 2
        assert "code-implementer" in names
        assert "test-runner" in names

    def test_get_agent_names_tiered(self, tmp_path):
        """Test extracting names from tiered structure."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        sub_agents_dir = agents_dir / "sub-agents"
        sub_agents_dir.mkdir()

        (agents_dir / "orchestrator.md").write_text("# Orchestrator")
        (sub_agents_dir / "sub-agent.md").write_text("# Sub Agent")

        names = get_agent_names(Provider.CLAUDE_CODE, tmp_path, include_subdirs=True)

        assert len(names) == 2
        assert "orchestrator" in names
        assert "sub-agent" in names


class TestProviderInfo:
    """Test comprehensive provider info."""

    def test_get_provider_info_claude(self, tmp_path):
        """Test provider info for Claude Code."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "agent1.md").write_text("# Agent 1")
        (agents_dir / "agent2.md").write_text("# Agent 2")

        info = get_provider_info(Provider.CLAUDE_CODE, tmp_path)

        assert info["provider"] == Provider.CLAUDE_CODE
        assert info["base_path"] == str(tmp_path / ".claude")
        assert info["agents_dir"] == str(agents_dir)
        assert info["agent_count"] == 2
        assert info["supports_agents"] is True

    def test_get_provider_info_cursor(self, tmp_path):
        """Test provider info for Cursor (no agents)."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        info = get_provider_info(Provider.CURSOR, tmp_path)

        assert info["provider"] == Provider.CURSOR
        assert info["base_path"] == str(cursor_dir)
        assert info["agents_dir"] is None
        assert info["agent_count"] == 0
        assert info["supports_agents"] is False

    def test_get_provider_info_auto_detect(self, tmp_path):
        """Test auto-detection in provider info."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        info = get_provider_info(project_root=tmp_path)

        assert info["provider"] == Provider.CLAUDE_CODE
        assert info["supports_agents"] is True


class TestIntegration:
    """Integration tests with actual project structure."""

    def test_real_project_detection(self):
        """Test detection on actual APM project."""
        # This test runs against the real project structure
        provider = detect_provider()
        assert provider == Provider.CLAUDE_CODE

    def test_real_agents_directory(self):
        """Test agents directory on actual project."""
        agents_dir = get_agents_directory()
        assert agents_dir is not None
        assert agents_dir.exists()
        assert agents_dir.name == "agents"

    def test_real_agent_paths(self):
        """Test agent paths on actual project."""
        paths = get_agent_paths()
        assert len(paths) > 0
        assert all(p.suffix == ".md" for p in paths)
        # Should include both flat and sub-agents
        assert any("sub-agents" in str(p) for p in paths)

    def test_real_agent_names(self):
        """Test agent names on actual project."""
        names = get_agent_names()
        assert len(names) > 0
        # Should include known agents
        assert any("code-implementer" in name for name in names)

    def test_real_provider_info(self):
        """Test provider info on actual project."""
        info = get_provider_info()
        assert info["provider"] == Provider.CLAUDE_CODE
        assert info["agent_count"] > 0
        assert info["supports_agents"] is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_nonexistent_project_root(self, tmp_path):
        """Test with nonexistent project root."""
        fake_path = tmp_path / "nonexistent"
        provider = detect_provider(fake_path)
        assert provider == Provider.UNKNOWN

    def test_file_instead_of_directory(self, tmp_path):
        """Test when .claude is a file instead of directory."""
        claude_file = tmp_path / ".claude"
        claude_file.write_text("not a directory")

        provider = detect_provider(tmp_path)
        # Should not detect Claude Code since .claude is not a directory
        assert provider != Provider.CLAUDE_CODE

    def test_empty_agents_directory(self, tmp_path):
        """Test empty agents directory."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path)
        assert len(paths) == 0

        names = get_agent_names(Provider.CLAUDE_CODE, tmp_path)
        assert len(names) == 0

    def test_mixed_file_types(self, tmp_path):
        """Test directory with mixed file types."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "agent.md").write_text("# Agent")
        (agents_dir / "readme.txt").write_text("Readme")
        (agents_dir / "config.json").write_text("{}")
        (agents_dir / ".hidden.md").write_text("# Hidden")

        paths = get_agent_paths(Provider.CLAUDE_CODE, tmp_path)
        # Should only include .md files
        assert len(paths) == 2  # agent.md and .hidden.md
        assert all(p.suffix == ".md" for p in paths)
