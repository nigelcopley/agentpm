"""
Tests for Claude Code Settings Manager

Tests multi-layer settings management with precedence.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from agentpm.providers.anthropic.claude_code.runtime.settings.manager import SettingsManager
from agentpm.providers.anthropic.claude_code.runtime.settings.models import (
    ClaudeCodeSettings,
    HooksSettings,
    MemorySettings,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_db():
    """Create mock database service."""
    return Mock()


@pytest.fixture
def settings_manager(mock_db, temp_config_dir):
    """Create settings manager with mocked dependencies."""
    return SettingsManager(db_service=mock_db, config_dir=temp_config_dir)


class TestSettingsManagerInit:
    """Test SettingsManager initialization."""

    def test_init_with_defaults(self, mock_db):
        """Test initialization with default config dir."""
        # Arrange & Act
        manager = SettingsManager(db_service=mock_db)

        # Assert
        assert manager.db == mock_db
        assert manager.config_dir == Path.home() / ".agentpm" / "config"
        assert manager._session_overrides == {}
        assert manager._cache == {}

    def test_init_with_custom_config_dir(self, mock_db, temp_config_dir):
        """Test initialization with custom config dir."""
        # Arrange & Act
        manager = SettingsManager(db_service=mock_db, config_dir=temp_config_dir)

        # Assert
        assert manager.config_dir == temp_config_dir


class TestLoadSettings:
    """Test settings loading with multi-layer precedence."""

    def test_load_default_settings(self, settings_manager):
        """Test loading default settings (no overrides)."""
        # Arrange & Act
        settings = settings_manager.load_settings()

        # Assert
        assert isinstance(settings, ClaudeCodeSettings)
        assert settings.plugin_enabled is True
        assert settings.hooks.timeout_seconds == 30
        assert settings.memory.retention_days == 90

    def test_load_with_project_id(self, settings_manager):
        """Test loading settings with project ID."""
        # Arrange & Act
        settings = settings_manager.load_settings(project_id=1)

        # Assert
        assert settings.project_id == 1

    def test_load_with_user_config(self, settings_manager, temp_config_dir):
        """Test loading settings with user config file override."""
        # Arrange - create user config
        config_file = temp_config_dir / "claude_code_settings.json"
        user_config = {
            "plugin_enabled": False,
            "hooks": {"timeout_seconds": 60},
        }
        config_file.write_text(json.dumps(user_config))

        # Act
        settings = settings_manager.load_settings()

        # Assert
        assert settings.plugin_enabled is False
        assert settings.hooks.timeout_seconds == 60
        assert settings.memory.retention_days == 90  # Default preserved

    def test_load_with_session_override(self, settings_manager):
        """Test loading settings with session overrides."""
        # Arrange - set session override
        settings_manager._session_overrides[1] = {
            "verbose_logging": True,
            "hooks": {"timeout_seconds": 100},
        }

        # Act
        settings = settings_manager.load_settings(project_id=1)

        # Assert
        assert settings.verbose_logging is True
        assert settings.hooks.timeout_seconds == 100

    def test_load_uses_cache(self, settings_manager):
        """Test that loading uses cache when available."""
        # Arrange - populate cache
        cached_settings = ClaudeCodeSettings(project_id=1, verbose_logging=True)
        settings_manager._cache[1] = cached_settings

        # Act
        settings = settings_manager.load_settings(project_id=1, use_cache=True)

        # Assert
        assert settings == cached_settings
        assert settings.verbose_logging is True

    def test_load_bypasses_cache(self, settings_manager):
        """Test that loading can bypass cache."""
        # Arrange - populate cache with different settings
        cached_settings = ClaudeCodeSettings(project_id=1, verbose_logging=True)
        settings_manager._cache[1] = cached_settings

        # Act
        settings = settings_manager.load_settings(project_id=1, use_cache=False)

        # Assert
        assert settings.verbose_logging is False  # Default, not cached value


class TestSaveSettings:
    """Test settings saving to different scopes."""

    def test_save_session_scope(self, settings_manager):
        """Test saving settings to session scope."""
        # Arrange
        settings = ClaudeCodeSettings(project_id=1, verbose_logging=True)

        # Act
        success = settings_manager.save_settings(
            project_id=1,
            settings=settings,
            scope="session"
        )

        # Assert
        assert success is True
        assert 1 in settings_manager._session_overrides
        assert settings_manager._session_overrides[1]["verbose_logging"] is True

    def test_save_user_scope(self, settings_manager, temp_config_dir):
        """Test saving settings to user scope."""
        # Arrange
        settings = ClaudeCodeSettings(plugin_enabled=False)

        # Act
        success = settings_manager.save_settings(
            project_id=None,
            settings=settings,
            scope="user"
        )

        # Assert
        assert success is True
        config_file = temp_config_dir / "claude_code_settings.json"
        assert config_file.exists()

        # Verify content
        saved_data = json.loads(config_file.read_text())
        assert saved_data["plugin_enabled"] is False

    def test_save_invalidates_cache(self, settings_manager):
        """Test that saving to session invalidates cache."""
        # Arrange
        settings_manager._cache[1] = ClaudeCodeSettings(project_id=1)
        new_settings = ClaudeCodeSettings(project_id=1, verbose_logging=True)

        # Act
        settings_manager.save_settings(
            project_id=1,
            settings=new_settings,
            scope="session"
        )

        # Assert
        assert 1 not in settings_manager._cache

    def test_save_project_scope_requires_project_id(self, settings_manager):
        """Test that project scope requires project_id."""
        # Arrange
        settings = ClaudeCodeSettings()

        # Act & Assert
        with pytest.raises(ValueError, match="project_id required"):
            settings_manager.save_settings(
                project_id=None,
                settings=settings,
                scope="project"
            )

    def test_save_invalid_scope(self, settings_manager):
        """Test that invalid scope raises error."""
        # Arrange
        settings = ClaudeCodeSettings()

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid scope"):
            settings_manager.save_settings(
                project_id=1,
                settings=settings,
                scope="invalid"
            )


class TestValidateSettings:
    """Test settings validation."""

    def test_validate_good_settings(self, settings_manager):
        """Test validation of good settings returns no warnings."""
        # Arrange
        settings = ClaudeCodeSettings()

        # Act
        warnings = settings_manager.validate_settings(settings)

        # Assert
        assert warnings == []

    def test_validate_low_hook_timeout(self, settings_manager):
        """Test validation warns about low hook timeout."""
        # Arrange
        settings = ClaudeCodeSettings(
            hooks=HooksSettings(timeout_seconds=3)
        )

        # Act
        warnings = settings_manager.validate_settings(settings)

        # Assert
        assert len(warnings) > 0
        assert any("timeout is very low" in w.lower() for w in warnings)

    def test_validate_low_memory_retention(self, settings_manager):
        """Test validation warns about low memory retention."""
        # Arrange
        settings = ClaudeCodeSettings(
            memory=MemorySettings(retention_days=5)
        )

        # Act
        warnings = settings_manager.validate_settings(settings)

        # Assert
        assert len(warnings) > 0
        assert any("retention is low" in w.lower() for w in warnings)

    def test_validate_high_parallel_subagents(self, settings_manager):
        """Test validation warns about high parallel subagents."""
        # Arrange
        settings = ClaudeCodeSettings()
        settings.subagents.max_parallel = 8

        # Act
        warnings = settings_manager.validate_settings(settings)

        # Assert
        assert len(warnings) > 0
        assert any("parallel subagents" in w.lower() for w in warnings)


class TestGetSetting:
    """Test getting specific setting values."""

    def test_get_top_level_setting(self, settings_manager):
        """Test getting top-level setting."""
        # Arrange & Act
        value = settings_manager.get_setting("plugin_enabled")

        # Assert
        assert value is True

    def test_get_nested_setting(self, settings_manager):
        """Test getting nested setting."""
        # Arrange & Act
        value = settings_manager.get_setting("hooks.timeout_seconds")

        # Assert
        assert value == 30

    def test_get_deep_nested_setting(self, settings_manager):
        """Test getting deeply nested setting."""
        # Arrange & Act
        value = settings_manager.get_setting("hooks.enabled.session_start")

        # Assert
        assert value is True

    def test_get_nonexistent_setting(self, settings_manager):
        """Test getting nonexistent setting returns default."""
        # Arrange & Act
        value = settings_manager.get_setting("nonexistent.key", default="default_value")

        # Assert
        assert value == "default_value"


class TestSetSetting:
    """Test setting specific setting values."""

    def test_set_top_level_setting(self, settings_manager):
        """Test setting top-level setting."""
        # Arrange & Act
        success = settings_manager.set_setting(
            "plugin_enabled",
            False,
            project_id=1,
            scope="session"
        )

        # Assert
        assert success is True
        assert settings_manager.get_setting("plugin_enabled", project_id=1) is False

    def test_set_nested_setting(self, settings_manager):
        """Test setting nested setting."""
        # Arrange & Act
        success = settings_manager.set_setting(
            "hooks.timeout_seconds",
            60,
            project_id=1,
            scope="session"
        )

        # Assert
        assert success is True
        assert settings_manager.get_setting("hooks.timeout_seconds", project_id=1) == 60

    def test_set_deep_nested_setting(self, settings_manager):
        """Test setting deeply nested setting."""
        # Arrange & Act
        success = settings_manager.set_setting(
            "hooks.enabled.session_start",
            False,
            project_id=1,
            scope="session"
        )

        # Assert
        assert success is True
        assert settings_manager.get_setting("hooks.enabled.session_start", project_id=1) is False


class TestResetSettings:
    """Test resetting settings to defaults."""

    def test_reset_session_scope(self, settings_manager):
        """Test resetting session scope."""
        # Arrange - set some session overrides
        settings_manager._session_overrides[1] = {"verbose_logging": True}
        settings_manager._cache[1] = ClaudeCodeSettings(project_id=1)

        # Act
        success = settings_manager.reset_settings(project_id=1, scope="session")

        # Assert
        assert success is True
        assert 1 not in settings_manager._session_overrides
        assert 1 not in settings_manager._cache

    def test_reset_user_scope(self, settings_manager, temp_config_dir):
        """Test resetting user scope."""
        # Arrange - create user config file
        config_file = temp_config_dir / "claude_code_settings.json"
        config_file.write_text(json.dumps({"plugin_enabled": False}))

        # Act
        success = settings_manager.reset_settings(scope="user")

        # Assert
        assert success is True
        assert not config_file.exists()

    def test_reset_project_scope_requires_project_id(self, settings_manager):
        """Test that resetting project scope requires project_id."""
        # Act & Assert
        with pytest.raises(ValueError, match="project_id required"):
            settings_manager.reset_settings(project_id=None, scope="project")


class TestMergeSettings:
    """Test settings merging."""

    def test_merge_flat_settings(self, settings_manager):
        """Test merging flat settings."""
        # Arrange
        base = ClaudeCodeSettings(plugin_enabled=True, verbose_logging=False)
        override = ClaudeCodeSettings(verbose_logging=True)

        # Act
        merged = settings_manager._merge_settings(base, override)

        # Assert
        assert merged.plugin_enabled is True  # From base
        assert merged.verbose_logging is True  # From override

    def test_merge_nested_settings(self, settings_manager):
        """Test merging nested settings."""
        # Arrange
        base = ClaudeCodeSettings(
            hooks=HooksSettings(timeout_seconds=30, retry_on_failure=False)
        )
        override = ClaudeCodeSettings(
            hooks=HooksSettings(timeout_seconds=60)
        )

        # Act
        merged = settings_manager._merge_settings(base, override)

        # Assert
        assert merged.hooks.timeout_seconds == 60  # From override
        assert merged.hooks.retry_on_failure is False  # From base (preserved)


class TestNestedValueHelpers:
    """Test nested value getter/setter helpers."""

    def test_get_nested_value(self, settings_manager):
        """Test getting nested value from dict."""
        # Arrange
        data = {
            "a": {
                "b": {
                    "c": "value"
                }
            }
        }

        # Act
        value = settings_manager._get_nested_value(data, "a.b.c")

        # Assert
        assert value == "value"

    def test_get_nested_value_nonexistent(self, settings_manager):
        """Test getting nonexistent nested value returns default."""
        # Arrange
        data = {"a": {"b": "value"}}

        # Act
        value = settings_manager._get_nested_value(data, "a.x.y", default="default")

        # Assert
        assert value == "default"

    def test_set_nested_value(self, settings_manager):
        """Test setting nested value in dict."""
        # Arrange
        data = {"a": {"b": "old"}}

        # Act
        settings_manager._set_nested_value(data, "a.b", "new")

        # Assert
        assert data["a"]["b"] == "new"

    def test_set_nested_value_creates_structure(self, settings_manager):
        """Test setting nested value creates intermediate dicts."""
        # Arrange
        data = {}

        # Act
        settings_manager._set_nested_value(data, "a.b.c", "value")

        # Assert
        assert data == {"a": {"b": {"c": "value"}}}
