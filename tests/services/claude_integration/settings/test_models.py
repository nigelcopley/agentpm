"""
Tests for Claude Code Settings Models

Tests Pydantic models for settings validation and serialization.
"""

import pytest
from pydantic import ValidationError

from agentpm.services.claude_integration.settings.models import (
    ClaudeCodeSettings,
    HooksSettings,
    MemorySettings,
    SubagentSettings,
    PerformanceSettings,
    MemoryGenerationFrequency,
)


class TestHooksSettings:
    """Test HooksSettings model."""

    def test_default_hooks_settings(self):
        """Test default hooks settings initialization."""
        # Arrange & Act
        settings = HooksSettings()

        # Assert
        assert settings.enabled["session_start"] is True
        assert settings.enabled["session_end"] is True
        assert settings.enabled["prompt_submit"] is True
        assert settings.enabled["tool_result"] is False
        assert settings.timeout_seconds == 30
        assert settings.retry_on_failure is False
        assert settings.max_retries == 3

    def test_custom_hooks_settings(self):
        """Test custom hooks settings."""
        # Arrange & Act
        settings = HooksSettings(
            enabled={"session_start": False, "custom_hook": True},
            timeout_seconds=60,
            retry_on_failure=True,
            max_retries=5
        )

        # Assert
        assert settings.enabled["session_start"] is False
        assert settings.enabled["custom_hook"] is True
        assert settings.timeout_seconds == 60
        assert settings.retry_on_failure is True
        assert settings.max_retries == 5

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Arrange & Act & Assert - valid
        settings = HooksSettings(timeout_seconds=1)
        assert settings.timeout_seconds == 1

        settings = HooksSettings(timeout_seconds=300)
        assert settings.timeout_seconds == 300

        # Invalid - too low
        with pytest.raises(ValidationError):
            HooksSettings(timeout_seconds=0)

        # Invalid - too high
        with pytest.raises(ValidationError):
            HooksSettings(timeout_seconds=301)

    def test_max_retries_validation(self):
        """Test max_retries validation."""
        # Arrange & Act & Assert - valid
        settings = HooksSettings(max_retries=0)
        assert settings.max_retries == 0

        settings = HooksSettings(max_retries=10)
        assert settings.max_retries == 10

        # Invalid - negative
        with pytest.raises(ValidationError):
            HooksSettings(max_retries=-1)

        # Invalid - too high
        with pytest.raises(ValidationError):
            HooksSettings(max_retries=11)


class TestMemorySettings:
    """Test MemorySettings model."""

    def test_default_memory_settings(self):
        """Test default memory settings initialization."""
        # Arrange & Act
        settings = MemorySettings()

        # Assert
        assert settings.auto_load_memory is True
        assert settings.auto_generate_memory is True
        assert settings.generation_frequency == MemoryGenerationFrequency.SESSION_END
        assert settings.retention_days == 90
        assert settings.max_file_size_kb == 500
        assert settings.cache_duration_minutes == 60

    def test_custom_memory_settings(self):
        """Test custom memory settings."""
        # Arrange & Act
        settings = MemorySettings(
            auto_load_memory=False,
            generation_frequency=MemoryGenerationFrequency.MANUAL,
            retention_days=30,
            max_file_size_kb=1000
        )

        # Assert
        assert settings.auto_load_memory is False
        assert settings.generation_frequency == MemoryGenerationFrequency.MANUAL
        assert settings.retention_days == 30
        assert settings.max_file_size_kb == 1000

    def test_retention_days_validation(self):
        """Test retention_days validation."""
        # Arrange & Act & Assert - valid
        settings = MemorySettings(retention_days=1)
        assert settings.retention_days == 1

        settings = MemorySettings(retention_days=365)
        assert settings.retention_days == 365

        # Invalid - too low
        with pytest.raises(ValidationError):
            MemorySettings(retention_days=0)

        # Invalid - too high
        with pytest.raises(ValidationError):
            MemorySettings(retention_days=366)

    def test_max_file_size_validation(self):
        """Test max_file_size_kb validation."""
        # Arrange & Act & Assert - valid
        settings = MemorySettings(max_file_size_kb=100)
        assert settings.max_file_size_kb == 100

        settings = MemorySettings(max_file_size_kb=5000)
        assert settings.max_file_size_kb == 5000

        # Invalid - too low
        with pytest.raises(ValidationError):
            MemorySettings(max_file_size_kb=99)

        # Invalid - too high
        with pytest.raises(ValidationError):
            MemorySettings(max_file_size_kb=5001)


class TestSubagentSettings:
    """Test SubagentSettings model."""

    def test_default_subagent_settings(self):
        """Test default subagent settings initialization."""
        # Arrange & Act
        settings = SubagentSettings()

        # Assert
        assert settings.enabled is True
        assert settings.max_parallel == 3
        assert settings.timeout_seconds == 300
        assert settings.auto_cleanup is True
        assert settings.max_depth == 3

    def test_custom_subagent_settings(self):
        """Test custom subagent settings."""
        # Arrange & Act
        settings = SubagentSettings(
            enabled=False,
            max_parallel=5,
            timeout_seconds=600,
            auto_cleanup=False,
            max_depth=2
        )

        # Assert
        assert settings.enabled is False
        assert settings.max_parallel == 5
        assert settings.timeout_seconds == 600
        assert settings.auto_cleanup is False
        assert settings.max_depth == 2

    def test_max_parallel_validation(self):
        """Test max_parallel validation."""
        # Arrange & Act & Assert - valid
        settings = SubagentSettings(max_parallel=1)
        assert settings.max_parallel == 1

        settings = SubagentSettings(max_parallel=10)
        assert settings.max_parallel == 10

        # Invalid - too low
        with pytest.raises(ValidationError):
            SubagentSettings(max_parallel=0)

        # Invalid - too high
        with pytest.raises(ValidationError):
            SubagentSettings(max_parallel=11)


class TestPerformanceSettings:
    """Test PerformanceSettings model."""

    def test_default_performance_settings(self):
        """Test default performance settings initialization."""
        # Arrange & Act
        settings = PerformanceSettings()

        # Assert
        assert settings.enable_caching is True
        assert settings.cache_ttl_seconds == 300
        assert settings.max_concurrent_requests == 5
        assert settings.request_timeout_seconds == 120
        assert settings.enable_metrics is True
        assert settings.metrics_interval_seconds == 60

    def test_custom_performance_settings(self):
        """Test custom performance settings."""
        # Arrange & Act
        settings = PerformanceSettings(
            enable_caching=False,
            cache_ttl_seconds=600,
            max_concurrent_requests=10,
            request_timeout_seconds=240
        )

        # Assert
        assert settings.enable_caching is False
        assert settings.cache_ttl_seconds == 600
        assert settings.max_concurrent_requests == 10
        assert settings.request_timeout_seconds == 240


class TestClaudeCodeSettings:
    """Test ClaudeCodeSettings main model."""

    def test_default_settings(self):
        """Test default Claude Code settings initialization."""
        # Arrange & Act
        settings = ClaudeCodeSettings()

        # Assert
        assert settings.plugin_enabled is True
        assert settings.verbose_logging is False
        assert settings.project_id is None
        assert isinstance(settings.hooks, HooksSettings)
        assert isinstance(settings.memory, MemorySettings)
        assert isinstance(settings.subagents, SubagentSettings)
        assert isinstance(settings.performance, PerformanceSettings)
        assert settings.custom_settings == {}

    def test_custom_settings(self):
        """Test custom Claude Code settings."""
        # Arrange & Act
        settings = ClaudeCodeSettings(
            plugin_enabled=False,
            verbose_logging=True,
            project_id=42,
            hooks=HooksSettings(timeout_seconds=60),
            custom_settings={"foo": "bar"}
        )

        # Assert
        assert settings.plugin_enabled is False
        assert settings.verbose_logging is True
        assert settings.project_id == 42
        assert settings.hooks.timeout_seconds == 60
        assert settings.custom_settings == {"foo": "bar"}

    def test_project_id_validation(self):
        """Test project_id validation."""
        # Arrange & Act & Assert - valid
        settings = ClaudeCodeSettings(project_id=1)
        assert settings.project_id == 1

        settings = ClaudeCodeSettings(project_id=None)
        assert settings.project_id is None

        # Invalid - negative
        with pytest.raises(ValidationError):
            ClaudeCodeSettings(project_id=-1)

        # Invalid - zero
        with pytest.raises(ValidationError):
            ClaudeCodeSettings(project_id=0)

    def test_get_hook_enabled(self):
        """Test get_hook_enabled method."""
        # Arrange
        settings = ClaudeCodeSettings()

        # Act & Assert
        assert settings.get_hook_enabled("session_start") is True
        assert settings.get_hook_enabled("tool_result") is False
        assert settings.get_hook_enabled("nonexistent_hook") is False

    def test_set_hook_enabled(self):
        """Test set_hook_enabled method."""
        # Arrange
        settings = ClaudeCodeSettings()

        # Act
        settings.set_hook_enabled("session_start", False)
        settings.set_hook_enabled("custom_hook", True)

        # Assert
        assert settings.get_hook_enabled("session_start") is False
        assert settings.get_hook_enabled("custom_hook") is True

    def test_model_serialization(self):
        """Test settings model serialization."""
        # Arrange
        settings = ClaudeCodeSettings(
            project_id=1,
            plugin_enabled=True,
            hooks=HooksSettings(timeout_seconds=45)
        )

        # Act
        settings_dict = settings.model_dump()

        # Assert
        assert isinstance(settings_dict, dict)
        assert settings_dict["project_id"] == 1
        assert settings_dict["plugin_enabled"] is True
        assert settings_dict["hooks"]["timeout_seconds"] == 45

    def test_model_deserialization(self):
        """Test settings model deserialization."""
        # Arrange
        settings_data = {
            "plugin_enabled": False,
            "project_id": 5,
            "hooks": {"timeout_seconds": 50},
            "memory": {"retention_days": 30},
        }

        # Act
        settings = ClaudeCodeSettings(**settings_data)

        # Assert
        assert settings.plugin_enabled is False
        assert settings.project_id == 5
        assert settings.hooks.timeout_seconds == 50
        assert settings.memory.retention_days == 30

    def test_nested_model_defaults(self):
        """Test that nested models use their defaults when not specified."""
        # Arrange
        settings_data = {
            "project_id": 1,
            "hooks": {"timeout_seconds": 100}  # Only override one field
        }

        # Act
        settings = ClaudeCodeSettings(**settings_data)

        # Assert
        assert settings.hooks.timeout_seconds == 100
        assert settings.hooks.retry_on_failure is False  # Default preserved
        assert settings.memory.retention_days == 90  # Memory uses all defaults
