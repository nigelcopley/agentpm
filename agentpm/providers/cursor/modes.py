"""
Cursor Provider Modes - Phase-Specific Workflows

Custom Cursor modes tailored to AIPM workflow phases.
Each mode optimizes Cursor behavior for specific phase requirements.

Pattern: Mode manager with JSON configuration
Database-first: Mode state tracked in provider config
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.provider import (
    CustomMode,
    CursorConfig,
    ProviderType,
)


logger = logging.getLogger(__name__)


class CursorModeType(str, Enum):
    """
    Cursor mode types aligned with AIPM phases.

    Each mode provides phase-specific configuration.
    """

    DISCOVERY = "aipm-discovery"      # D1: Requirements and 6W analysis
    PLANNING = "aipm-planning"        # P1: Task breakdown and estimation
    IMPLEMENTATION = "aipm-implementation"  # I1: Code implementation
    REVIEW = "aipm-review"            # R1: Quality validation
    OPERATIONS = "aipm-operations"    # O1: Deployment and monitoring
    EVOLUTION = "aipm-evolution"      # E1: Continuous improvement
    DEBUG = "aipm-debug"              # Ad-hoc: Debugging mode
    TESTING = "aipm-testing"          # Ad-hoc: Testing focus


class CursorModeManager:
    """
    Manage Cursor-specific modes.

    Provides phase-optimized Cursor configurations including:
    - Custom system prompts
    - Enabled tools
    - Active rules
    - UI customization

    Example:
        db = DatabaseService()
        manager = CursorModeManager(db)

        # Activate discovery mode
        result = manager.activate_mode(
            project_id=123,
            mode=CursorModeType.DISCOVERY
        )

        # Deactivate mode
        manager.deactivate_mode(project_id=123)
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize mode manager.

        Args:
            db: Database service instance
        """
        self.db = db
        self._mode_definitions = self._load_mode_definitions()

    def activate_mode(
        self,
        project_id: int,
        mode: CursorModeType,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Activate a Cursor mode with specific configuration.

        Updates provider configuration and generates mode-specific files.

        Args:
            project_id: Project ID
            mode: Mode to activate
            config_overrides: Optional configuration overrides

        Returns:
            Dict with activation status

        Example:
            result = manager.activate_mode(
                project_id=123,
                mode=CursorModeType.IMPLEMENTATION,
                config_overrides={"tools_enabled": ["git", "pytest"]}
            )
        """
        try:
            # Get provider installation
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    """
                    SELECT * FROM provider_installations
                    WHERE project_id = ? AND provider_type = ?
                    """,
                    (project_id, ProviderType.CURSOR.value)
                ).fetchone()

            if not row:
                return {
                    "success": False,
                    "message": "Cursor provider not installed"
                }

            # Get mode definition
            mode_def = self._mode_definitions.get(mode.value)
            if not mode_def:
                return {
                    "success": False,
                    "message": f"Mode definition not found: {mode.value}"
                }

            # Apply config overrides
            if config_overrides:
                mode_def = {**mode_def, **config_overrides}

            # Get config
            config_data = row.get("config", {})
            if isinstance(config_data, str):
                config_data = json.loads(config_data)

            config = CursorConfig(**config_data)
            cursor_dir = Path(config.project_path) / ".cursor"
            modes_dir = cursor_dir / "modes"
            modes_dir.mkdir(parents=True, exist_ok=True)

            # Generate mode configuration file
            mode_file = modes_dir / f"{mode.value}.json"
            mode_file.write_text(json.dumps(mode_def, indent=2))

            # Update active mode in provider config
            config_data["active_mode"] = mode.value
            config_data["active_mode_config"] = mode_def

            with self.db.transaction() as conn:
                conn.execute(
                    """
                    UPDATE provider_installations
                    SET config = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (json.dumps(config_data), json.dumps(datetime.now().isoformat()), row["id"])
                )

            logger.info(f"Activated mode {mode.value} for project {project_id}")

            return {
                "success": True,
                "mode": mode.value,
                "mode_file": str(mode_file),
                "message": f"Activated mode: {mode.value}"
            }

        except Exception as e:
            logger.error(f"Error activating mode: {e}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }

    def deactivate_mode(self, project_id: int) -> Dict[str, Any]:
        """
        Deactivate current mode and restore default.

        Args:
            project_id: Project ID

        Returns:
            Dict with deactivation status

        Example:
            result = manager.deactivate_mode(project_id=123)
        """
        try:
            # Get provider installation
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    """
                    SELECT * FROM provider_installations
                    WHERE project_id = ? AND provider_type = ?
                    """,
                    (project_id, ProviderType.CURSOR.value)
                ).fetchone()

            if not row:
                return {
                    "success": False,
                    "message": "Cursor provider not installed"
                }

            # Remove active mode from config
            config_data = row.get("config", {})
            if isinstance(config_data, str):
                config_data = json.loads(config_data)

            active_mode = config_data.pop("active_mode", None)
            config_data.pop("active_mode_config", None)

            with self.db.transaction() as conn:
                conn.execute(
                    """
                    UPDATE provider_installations
                    SET config = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (json.dumps(config_data), json.dumps(datetime.now().isoformat()), row["id"])
                )

            logger.info(f"Deactivated mode for project {project_id}")

            return {
                "success": True,
                "previous_mode": active_mode,
                "message": "Mode deactivated, restored to default"
            }

        except Exception as e:
            logger.error(f"Error deactivating mode: {e}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }

    def get_active_mode(self, project_id: int) -> Optional[str]:
        """
        Get currently active mode for project.

        Args:
            project_id: Project ID

        Returns:
            Mode name or None if no mode active

        Example:
            mode = manager.get_active_mode(project_id=123)
            if mode:
                print(f"Active mode: {mode}")
        """
        try:
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    """
                    SELECT config FROM provider_installations
                    WHERE project_id = ? AND provider_type = ?
                    """,
                    (project_id, ProviderType.CURSOR.value)
                ).fetchone()

            if not row:
                return None

            config_data = row.get("config", {})
            if isinstance(config_data, str):
                config_data = json.loads(config_data)

            return config_data.get("active_mode")

        except Exception as e:
            logger.error(f"Error getting active mode: {e}", exc_info=True)
            return None

    def list_available_modes(self) -> List[Dict[str, Any]]:
        """
        List all available modes.

        Returns:
            List of mode definitions

        Example:
            modes = manager.list_available_modes()
            for mode in modes:
                print(f"{mode['mode_id']}: {mode['description']}")
        """
        return [
            {
                "mode_id": mode_id,
                **config
            }
            for mode_id, config in self._mode_definitions.items()
        ]

    def _load_mode_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Load mode definitions.

        Returns:
            Dict mapping mode_id to configuration

        Note: In production, these could be loaded from database or config files.
        For now, hardcoded definitions aligned with AIPM phases.
        """
        return {
            CursorModeType.DISCOVERY.value: {
                "display_name": "Discovery Mode",
                "description": "Optimized for requirements gathering and 6W analysis",
                "phase": "D1",
                "system_prompt": """You are in Discovery mode. Focus on:
- Understanding requirements
- Asking clarifying questions
- Identifying use cases
- Analyzing stakeholder needs
- Documenting 6W context (Who, What, When, Where, Why, How)

Use `apm work-item` commands to document findings.""",
                "tools_enabled": [
                    "apm work-item create",
                    "apm work-item update",
                    "apm context show",
                    "web-search"
                ],
                "rules_active": [
                    "aipm-master",
                    "workflow-rules",
                    "documentation-standards"
                ],
                "icon": "🔍",
                "color": "#4A90E2",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.PLANNING.value: {
                "display_name": "Planning Mode",
                "description": "Optimized for task breakdown and estimation",
                "phase": "P1",
                "system_prompt": """You are in Planning mode. Focus on:
- Breaking work into tasks
- Estimating effort
- Identifying dependencies
- Planning risk mitigations
- Creating implementation roadmap

Use `apm task` commands to create plan.""",
                "tools_enabled": [
                    "apm task create",
                    "apm task update",
                    "apm work-item show",
                    "file-tree-view"
                ],
                "rules_active": [
                    "aipm-master",
                    "workflow-rules",
                    "development-principles"
                ],
                "icon": "📋",
                "color": "#7B68EE",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.IMPLEMENTATION.value: {
                "display_name": "Implementation Mode",
                "description": "Optimized for coding and implementation",
                "phase": "I1",
                "system_prompt": """You are in Implementation mode. Focus on:
- Writing production code
- Following project patterns
- Adding type hints
- Including error handling
- Writing docstrings

Follow three-tier architecture: Models → Adapters → Methods.""",
                "tools_enabled": [
                    "file-edit",
                    "pytest",
                    "git",
                    "apm task update"
                ],
                "rules_active": [
                    "aipm-master",
                    "code-quality",
                    "testing-standards",
                    "development-principles"
                ],
                "icon": "⚙️",
                "color": "#50C878",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.REVIEW.value: {
                "display_name": "Review Mode",
                "description": "Optimized for quality validation and testing",
                "phase": "R1",
                "system_prompt": """You are in Review mode. Focus on:
- Validating acceptance criteria
- Running comprehensive tests
- Checking code quality
- Verifying documentation
- Ensuring compliance

Use quality gates to validate work.""",
                "tools_enabled": [
                    "pytest",
                    "ruff",
                    "black",
                    "mypy",
                    "apm quality validate"
                ],
                "rules_active": [
                    "aipm-master",
                    "code-quality",
                    "testing-standards"
                ],
                "icon": "✅",
                "color": "#FF6B6B",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.OPERATIONS.value: {
                "display_name": "Operations Mode",
                "description": "Optimized for deployment and monitoring",
                "phase": "O1",
                "system_prompt": """You are in Operations mode. Focus on:
- Version management
- Deployment procedures
- Health checks
- Monitoring setup
- Production validation

Ensure safe deployment practices.""",
                "tools_enabled": [
                    "git",
                    "docker",
                    "apm version bump",
                    "health-check"
                ],
                "rules_active": [
                    "aipm-master",
                    "workflow-rules"
                ],
                "icon": "🚀",
                "color": "#FFA500",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.EVOLUTION.value: {
                "display_name": "Evolution Mode",
                "description": "Optimized for continuous improvement",
                "phase": "E1",
                "system_prompt": """You are in Evolution mode. Focus on:
- Analyzing telemetry
- Identifying improvements
- Capturing learnings
- Updating documentation
- Planning next iterations

Learn from production feedback.""",
                "tools_enabled": [
                    "apm learnings create",
                    "apm telemetry show",
                    "analytics"
                ],
                "rules_active": [
                    "aipm-master",
                    "documentation-standards"
                ],
                "icon": "🔄",
                "color": "#9370DB",
                "auto_activate": False,
                "default_for_phase": True
            },
            CursorModeType.DEBUG.value: {
                "display_name": "Debug Mode",
                "description": "Optimized for debugging and troubleshooting",
                "phase": "ad-hoc",
                "system_prompt": """You are in Debug mode. Focus on:
- Analyzing error messages
- Reproducing issues
- Identifying root causes
- Testing fixes
- Validating solutions

Use systematic debugging approach.""",
                "tools_enabled": [
                    "pytest",
                    "debugger",
                    "logs-viewer",
                    "git-bisect"
                ],
                "rules_active": [
                    "aipm-master",
                    "testing-standards"
                ],
                "icon": "🐛",
                "color": "#DC143C",
                "auto_activate": False,
                "default_for_phase": False
            },
            CursorModeType.TESTING.value: {
                "display_name": "Testing Mode",
                "description": "Optimized for test development",
                "phase": "ad-hoc",
                "system_prompt": """You are in Testing mode. Focus on:
- Writing comprehensive tests
- Following AAA pattern (Arrange, Act, Assert)
- Achieving high coverage
- Testing edge cases
- Creating fixtures

Aim for >90% coverage.""",
                "tools_enabled": [
                    "pytest",
                    "pytest-cov",
                    "file-edit"
                ],
                "rules_active": [
                    "aipm-master",
                    "testing-standards"
                ],
                "icon": "🧪",
                "color": "#20B2AA",
                "auto_activate": False,
                "default_for_phase": False
            }
        }


# Import datetime for mode activation
from datetime import datetime


# Convenience function
def get_mode_manager(db: DatabaseService) -> CursorModeManager:
    """
    Get mode manager instance.

    Args:
        db: Database service instance

    Returns:
        CursorModeManager instance

    Example:
        from agentpm.providers.cursor.modes import get_mode_manager
        from agentpm.core.database.service import DatabaseService

        db = DatabaseService()
        manager = get_mode_manager(db)
    """
    return CursorModeManager(db)
