"""
Unit tests for Cursor provider modes.

Tests custom mode management including:
- Mode activation/deactivation
- Mode configuration
- Available modes listing
- Phase-specific modes

Coverage target: 90%
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from agentpm.providers.cursor.modes import (
    CursorModeManager,
    CursorModeType,
    get_mode_manager,
)
from agentpm.core.database.models.provider import (
    CursorConfig,
    ProviderType,
    InstallationStatus,
)


class TestCursorModeManager:
    """Test CursorModeManager functionality."""

    def test_activate_mode_success(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN provider installed and valid mode
        WHEN calling activate_mode()
        THEN mode is activated and config updated
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation record
        with db_service.transaction() as conn:
            result = conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    sample_config.model_dump_json(),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            installation_id = result.lastrowid

        # Create modes directory
        modes_dir = Path(sample_config.project_path) / ".cursor" / "modes"
        modes_dir.mkdir(parents=True, exist_ok=True)

        # Act
        result = manager.activate_mode(
            project_id=project.id,
            mode=CursorModeType.IMPLEMENTATION
        )

        # Assert
        assert result["success"] is True
        assert result["mode"] == CursorModeType.IMPLEMENTATION.value
        assert "mode_file" in result

        # Verify mode file created
        mode_file = Path(result["mode_file"])
        assert mode_file.exists()
        mode_config = json.loads(mode_file.read_text())
        assert mode_config["display_name"] == "Implementation Mode"

    def test_activate_mode_provider_not_installed(self, db_service, project):
        """
        GIVEN provider not installed
        WHEN calling activate_mode()
        THEN error is returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Act
        result = manager.activate_mode(
            project_id=project.id,
            mode=CursorModeType.DISCOVERY
        )

        # Assert
        assert result["success"] is False
        assert "not installed" in result["message"]

    def test_activate_mode_with_overrides(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN config overrides
        WHEN calling activate_mode()
        THEN overrides are applied
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation
        with db_service.transaction() as conn:
            conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    sample_config.model_dump_json(),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        modes_dir = Path(sample_config.project_path) / ".cursor" / "modes"
        modes_dir.mkdir(parents=True, exist_ok=True)

        overrides = {
            "tools_enabled": ["pytest", "git"],
            "custom_field": "custom_value"
        }

        # Act
        result = manager.activate_mode(
            project_id=project.id,
            mode=CursorModeType.TESTING,
            config_overrides=overrides
        )

        # Assert
        assert result["success"] is True

        # Verify overrides in mode file
        mode_file = Path(result["mode_file"])
        mode_config = json.loads(mode_file.read_text())
        assert mode_config["tools_enabled"] == ["pytest", "git"]
        assert mode_config["custom_field"] == "custom_value"

    def test_deactivate_mode_success(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN activated mode
        WHEN calling deactivate_mode()
        THEN mode is deactivated
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation with active mode
        config_data = sample_config.model_dump()
        config_data["active_mode"] = CursorModeType.DEBUG.value
        config_data["active_mode_config"] = {"test": "config"}

        with db_service.transaction() as conn:
            conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    json.dumps(config_data),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        # Act
        result = manager.deactivate_mode(project_id=project.id)

        # Assert
        assert result["success"] is True
        assert result["previous_mode"] == CursorModeType.DEBUG.value

        # Verify mode removed from config
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            row = conn.execute(
                "SELECT config FROM provider_installations WHERE project_id = ?",
                (project.id,)
            ).fetchone()

        updated_config = json.loads(row["config"])
        assert "active_mode" not in updated_config
        assert "active_mode_config" not in updated_config

    def test_deactivate_mode_provider_not_installed(self, db_service, project):
        """
        GIVEN provider not installed
        WHEN calling deactivate_mode()
        THEN error is returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Act
        result = manager.deactivate_mode(project_id=project.id)

        # Assert
        assert result["success"] is False
        assert "not installed" in result["message"]

    def test_get_active_mode_with_mode(
        self, db_service, project, sample_config
    ):
        """
        GIVEN active mode
        WHEN calling get_active_mode()
        THEN mode name is returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation with active mode
        config_data = sample_config.model_dump()
        config_data["active_mode"] = CursorModeType.REVIEW.value

        with db_service.transaction() as conn:
            conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    json.dumps(config_data),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        # Act
        mode = manager.get_active_mode(project_id=project.id)

        # Assert
        assert mode == CursorModeType.REVIEW.value

    def test_get_active_mode_no_mode(
        self, db_service, project, sample_config
    ):
        """
        GIVEN no active mode
        WHEN calling get_active_mode()
        THEN None is returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation without active mode
        with db_service.transaction() as conn:
            conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    sample_config.model_dump_json(),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        # Act
        mode = manager.get_active_mode(project_id=project.id)

        # Assert
        assert mode is None

    def test_get_active_mode_provider_not_installed(self, db_service, project):
        """
        GIVEN provider not installed
        WHEN calling get_active_mode()
        THEN None is returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Act
        mode = manager.get_active_mode(project_id=project.id)

        # Assert
        assert mode is None

    def test_list_available_modes(self, db_service):
        """
        GIVEN mode manager
        WHEN calling list_available_modes()
        THEN all modes are returned
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Act
        modes = manager.list_available_modes()

        # Assert
        assert len(modes) == 8  # 6 phase modes + 2 ad-hoc modes
        mode_ids = [m["mode_id"] for m in modes]
        assert CursorModeType.DISCOVERY.value in mode_ids
        assert CursorModeType.PLANNING.value in mode_ids
        assert CursorModeType.IMPLEMENTATION.value in mode_ids
        assert CursorModeType.REVIEW.value in mode_ids
        assert CursorModeType.OPERATIONS.value in mode_ids
        assert CursorModeType.EVOLUTION.value in mode_ids
        assert CursorModeType.DEBUG.value in mode_ids
        assert CursorModeType.TESTING.value in mode_ids

    def test_mode_definitions_structure(self, db_service):
        """
        GIVEN mode manager
        WHEN checking mode definitions
        THEN all required fields are present
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Act
        modes = manager.list_available_modes()

        # Assert
        for mode in modes:
            assert "mode_id" in mode
            assert "display_name" in mode
            assert "description" in mode
            assert "phase" in mode
            assert "system_prompt" in mode
            assert "tools_enabled" in mode
            assert "rules_active" in mode
            assert "icon" in mode
            assert "color" in mode
            assert "auto_activate" in mode
            assert "default_for_phase" in mode

    def test_phase_modes_have_correct_phase(self, db_service):
        """
        GIVEN phase-specific modes
        WHEN checking phase field
        THEN phase matches mode purpose
        """
        # Arrange
        manager = CursorModeManager(db_service)
        modes = manager.list_available_modes()

        # Assert phase mapping
        phase_map = {
            CursorModeType.DISCOVERY.value: "D1",
            CursorModeType.PLANNING.value: "P1",
            CursorModeType.IMPLEMENTATION.value: "I1",
            CursorModeType.REVIEW.value: "R1",
            CursorModeType.OPERATIONS.value: "O1",
            CursorModeType.EVOLUTION.value: "E1",
            CursorModeType.DEBUG.value: "ad-hoc",
            CursorModeType.TESTING.value: "ad-hoc",
        }

        for mode in modes:
            mode_id = mode["mode_id"]
            expected_phase = phase_map[mode_id]
            assert mode["phase"] == expected_phase


class TestGetModeManager:
    """Test convenience function."""

    def test_get_mode_manager(self, db_service):
        """
        GIVEN database service
        WHEN calling get_mode_manager()
        THEN manager instance is returned
        """
        # Act
        manager = get_mode_manager(db_service)

        # Assert
        assert isinstance(manager, CursorModeManager)
        assert manager.db == db_service


class TestModeActivationDeactivationCycle:
    """Test complete activation/deactivation cycle."""

    def test_activate_deactivate_cycle(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN provider installed
        WHEN activating and deactivating modes
        THEN state changes correctly
        """
        # Arrange
        manager = CursorModeManager(db_service)

        # Create installation
        with db_service.transaction() as conn:
            conn.execute(
                """
                INSERT INTO provider_installations (
                    project_id, provider_type, provider_version,
                    install_path, status, config,
                    installed_files, file_hashes,
                    installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    ProviderType.CURSOR.value,
                    "1.0.0",
                    str(Path(sample_config.project_path) / ".cursor"),
                    InstallationStatus.INSTALLED.value,
                    sample_config.model_dump_json(),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        modes_dir = Path(sample_config.project_path) / ".cursor" / "modes"
        modes_dir.mkdir(parents=True, exist_ok=True)

        # Assert initial state
        assert manager.get_active_mode(project.id) is None

        # Activate mode
        result = manager.activate_mode(project.id, CursorModeType.PLANNING)
        assert result["success"] is True
        assert manager.get_active_mode(project.id) == CursorModeType.PLANNING.value

        # Switch mode
        result = manager.activate_mode(project.id, CursorModeType.IMPLEMENTATION)
        assert result["success"] is True
        assert manager.get_active_mode(project.id) == CursorModeType.IMPLEMENTATION.value

        # Deactivate
        result = manager.deactivate_mode(project.id)
        assert result["success"] is True
        assert manager.get_active_mode(project.id) is None
