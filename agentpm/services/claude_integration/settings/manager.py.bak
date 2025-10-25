"""
Claude Code Settings Manager

Multi-layer settings management with precedence:
1. System defaults (hardcoded in models)
2. Project settings (database)
3. User overrides (config file)
4. Session overrides (temporary)

Follows APM (Agent Project Manager) three-layer architecture (Methods layer).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ClaudeCodeSettings

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Manage Claude Code integration settings with multi-layer precedence.

    Settings are loaded in order of precedence:
    1. System defaults (from Pydantic models)
    2. Project settings (from database)
    3. User overrides (from config file)
    4. Session overrides (temporary, in-memory)

    Example:
        manager = SettingsManager(db_service)
        settings = manager.load_settings(project_id=1)
        manager.save_settings(project_id=1, settings)
    """

    def __init__(self, db_service: Optional[Any] = None, config_dir: Optional[Path] = None):
        """
        Initialize settings manager.

        Args:
            db_service: Database service for project settings
            config_dir: Directory for user config files
        """
        self.db = db_service
        self.config_dir = config_dir or Path.home() / ".agentpm" / "config"
        self._session_overrides: Dict[int, Dict[str, Any]] = {}
        self._cache: Dict[int, ClaudeCodeSettings] = {}

    def load_settings(
        self,
        project_id: Optional[int] = None,
        use_cache: bool = True
    ) -> ClaudeCodeSettings:
        """
        Load settings with multi-layer precedence.

        Precedence order (highest to lowest):
        1. Session overrides (temporary)
        2. User config file
        3. Project database settings
        4. System defaults

        Args:
            project_id: Optional project ID for project-specific settings
            use_cache: Whether to use cached settings

        Returns:
            ClaudeCodeSettings instance

        Example:
            settings = manager.load_settings(project_id=1)
        """
        # Check cache first
        if use_cache and project_id and project_id in self._cache:
            logger.debug(f"Using cached settings for project {project_id}")
            return self._cache[project_id]

        # Layer 1: System defaults (from Pydantic model defaults)
        settings = ClaudeCodeSettings(project_id=project_id)
        logger.debug("Loaded system default settings")

        # Layer 2: Project settings from database
        if project_id and self.db:
            project_settings = self._load_project_settings(project_id)
            if project_settings:
                settings = self._merge_settings(settings, project_settings)
                logger.debug(f"Merged project settings for project {project_id}")

        # Layer 3: User overrides from config file
        user_settings = self._load_user_config()
        if user_settings:
            settings = self._merge_settings(settings, user_settings)
            logger.debug("Merged user config settings")

        # Layer 4: Session overrides (temporary)
        if project_id and project_id in self._session_overrides:
            session_settings = ClaudeCodeSettings(**self._session_overrides[project_id])
            settings = self._merge_settings(settings, session_settings)
            logger.debug(f"Merged session overrides for project {project_id}")

        # Cache the result
        if project_id:
            self._cache[project_id] = settings

        return settings

    def save_settings(
        self,
        project_id: Optional[int],
        settings: ClaudeCodeSettings,
        scope: str = "project"
    ) -> bool:
        """
        Save settings to appropriate storage.

        Args:
            project_id: Optional project ID
            settings: Settings to save
            scope: Storage scope ("project", "user", or "session")

        Returns:
            True if saved successfully

        Raises:
            ValueError: If scope is invalid or requirements not met

        Example:
            success = manager.save_settings(
                project_id=1,
                settings=settings,
                scope="project"
            )
        """
        if scope == "project":
            if not project_id:
                raise ValueError("project_id required for project scope")
            if not self.db:
                raise ValueError("Database service required for project scope")
            return self._save_project_settings(project_id, settings)

        elif scope == "user":
            return self._save_user_config(settings)

        elif scope == "session":
            if not project_id:
                raise ValueError("project_id required for session scope")
            self._session_overrides[project_id] = settings.model_dump()
            # Invalidate cache
            if project_id in self._cache:
                del self._cache[project_id]
            logger.debug(f"Saved session overrides for project {project_id}")
            return True

        else:
            raise ValueError(f"Invalid scope: {scope}. Must be 'project', 'user', or 'session'")

    def validate_settings(self, settings: ClaudeCodeSettings) -> List[str]:
        """
        Validate settings and return warnings.

        Args:
            settings: Settings to validate

        Returns:
            List of validation warning messages (empty if all valid)

        Example:
            warnings = manager.validate_settings(settings)
            if warnings:
                print("Warnings:", warnings)
        """
        warnings: List[str] = []

        # Validate hooks timeout
        if settings.hooks.timeout_seconds < 5:
            warnings.append("Hook timeout is very low (<5s), may cause premature failures")

        # Validate memory retention
        if settings.memory.retention_days < 7:
            warnings.append("Memory retention is low (<7 days), may lose important context")

        # Validate subagent settings
        if settings.subagents.max_parallel > 5:
            warnings.append("High parallel subagents (>5) may impact performance")

        if settings.subagents.timeout_seconds < 60:
            warnings.append("Subagent timeout is low (<60s), complex tasks may fail")

        # Validate performance settings
        if settings.performance.max_concurrent_requests > 10:
            warnings.append("High concurrent requests (>10) may hit rate limits")

        # Validate memory file size
        if settings.memory.max_file_size_kb > 2000:
            warnings.append("Large memory files (>2MB) may slow down loading")

        return warnings

    def get_setting(self, key: str, project_id: Optional[int] = None, default: Any = None) -> Any:
        """
        Get a specific setting value by dotted key path.

        Args:
            key: Dotted key path (e.g., "hooks.enabled.session_start")
            project_id: Optional project ID
            default: Default value if not found

        Returns:
            Setting value or default

        Example:
            enabled = manager.get_setting("hooks.enabled.session_start", project_id=1)
        """
        settings = self.load_settings(project_id)
        return self._get_nested_value(settings.model_dump(), key, default)

    def set_setting(
        self,
        key: str,
        value: Any,
        project_id: Optional[int] = None,
        scope: str = "session"
    ) -> bool:
        """
        Set a specific setting value by dotted key path.

        Args:
            key: Dotted key path (e.g., "hooks.enabled.session_start")
            value: Value to set
            project_id: Optional project ID
            scope: Storage scope ("project", "user", or "session")

        Returns:
            True if set successfully

        Example:
            manager.set_setting(
                "hooks.enabled.session_start",
                True,
                project_id=1,
                scope="session"
            )
        """
        settings = self.load_settings(project_id, use_cache=False)
        settings_dict = settings.model_dump()

        # Set the nested value
        self._set_nested_value(settings_dict, key, value)

        # Recreate settings object
        updated_settings = ClaudeCodeSettings(**settings_dict)

        # Save to appropriate scope
        return self.save_settings(project_id, updated_settings, scope)

    def reset_settings(self, project_id: Optional[int] = None, scope: str = "session") -> bool:
        """
        Reset settings to defaults.

        Args:
            project_id: Optional project ID
            scope: Scope to reset ("project", "user", or "session")

        Returns:
            True if reset successfully

        Example:
            manager.reset_settings(project_id=1, scope="session")
        """
        if scope == "session" and project_id:
            if project_id in self._session_overrides:
                del self._session_overrides[project_id]
            if project_id in self._cache:
                del self._cache[project_id]
            logger.info(f"Reset session settings for project {project_id}")
            return True

        elif scope == "user":
            config_file = self.config_dir / "claude_code_settings.json"
            if config_file.exists():
                config_file.unlink()
                logger.info("Deleted user config file")
            return True

        elif scope == "project":
            if not project_id:
                raise ValueError("project_id required for project scope")
            # Would delete from database here
            # For now, just clear cache
            if project_id in self._cache:
                del self._cache[project_id]
            logger.info(f"Reset project settings for project {project_id}")
            return True

        return False

    def _load_project_settings(self, project_id: int) -> Optional[ClaudeCodeSettings]:
        """Load settings from database for project."""
        if not self.db:
            return None

        try:
            # Query database for project settings
            # This would use the database service to fetch settings
            # For now, return None (would be implemented with db access)
            logger.debug(f"Database query for project {project_id} settings not yet implemented")
            return None
        except Exception as e:
            logger.error(f"Error loading project settings: {e}")
            return None

    def _save_project_settings(self, project_id: int, settings: ClaudeCodeSettings) -> bool:
        """Save settings to database for project."""
        if not self.db:
            return False

        try:
            # Save to database
            # This would use the database service to persist settings
            # For now, return False (would be implemented with db access)
            logger.debug(f"Database save for project {project_id} settings not yet implemented")
            return False
        except Exception as e:
            logger.error(f"Error saving project settings: {e}")
            return False

    def _load_user_config(self) -> Optional[ClaudeCodeSettings]:
        """Load user config from filesystem."""
        config_file = self.config_dir / "claude_code_settings.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
            return ClaudeCodeSettings(**config_data)
        except Exception as e:
            logger.error(f"Error loading user config: {e}")
            return None

    def _save_user_config(self, settings: ClaudeCodeSettings) -> bool:
        """Save user config to filesystem."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "claude_code_settings.json"

        try:
            with open(config_file, "w") as f:
                json.dump(settings.model_dump(), f, indent=2)
            logger.info(f"Saved user config to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving user config: {e}")
            return False

    def _merge_settings(
        self,
        base: ClaudeCodeSettings,
        override: ClaudeCodeSettings
    ) -> ClaudeCodeSettings:
        """
        Merge two settings objects, with override taking precedence.

        Args:
            base: Base settings
            override: Override settings

        Returns:
            Merged settings
        """
        # Convert to dicts
        base_dict = base.model_dump()
        override_dict = override.model_dump()

        # Deep merge
        merged = self._deep_merge(base_dict, override_dict)

        # Return new settings object
        return ClaudeCodeSettings(**merged)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _get_nested_value(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get value from nested dict using dotted key path."""
        keys = key.split(".")
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any) -> None:
        """Set value in nested dict using dotted key path."""
        keys = key.split(".")
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
