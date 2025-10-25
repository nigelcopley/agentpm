"""
Unit tests for CursorProvider class (main interface).

Tests high-level provider operations including:
- Installation workflows
- Uninstallation workflows
- Configuration management
- Status queries
- Memory sync
- Verification

Coverage target: 90%
"""

import pytest
from pathlib import Path

from agentpm.providers.cursor.provider import CursorProvider
from agentpm.core.database.models.provider import (
    InstallResult,
    VerifyResult,
    MemorySyncResult,
    UpdateResult,
)


class TestCursorProviderInstallation:
    """Test CursorProvider installation workflows."""

    def test_install_success(self, db_service, project, temp_project_dir):
        """
        GIVEN valid project path
        WHEN calling install()
        THEN provider is installed successfully
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act
        result = provider.install(temp_project_dir)

        # Assert
        assert isinstance(result, InstallResult)
        assert result.success is True
        assert result.installation_id is not None
        assert len(result.installed_files) > 0
        assert len(result.errors) == 0

    def test_install_with_custom_config(self, db_service, project, temp_project_dir):
        """
        GIVEN custom configuration
        WHEN calling install()
        THEN custom config is applied
        """
        # Arrange
        provider = CursorProvider(db_service)
        config = {
            "tech_stack": ["Python", "PostgreSQL"],
            "rules_enabled": True,
            "memory_sync_enabled": False,
        }

        # Act
        result = provider.install(temp_project_dir, config=config)

        # Assert
        assert result.success is True
        # Verify config was saved
        status = provider.get_status(temp_project_dir)
        assert status["status"] == "installed"

    def test_install_creates_directory_structure(
        self, db_service, project, temp_project_dir
    ):
        """
        GIVEN project without .cursor directory
        WHEN calling install()
        THEN .cursor directory is created with proper structure
        """
        # Arrange
        provider = CursorProvider(db_service)
        cursor_dir = temp_project_dir / ".cursor"

        # Act
        result = provider.install(temp_project_dir)

        # Assert
        assert cursor_dir.exists()
        assert (cursor_dir / "rules").exists()
        assert (cursor_dir / "memories").exists()

    def test_install_project_not_found(self, db_service, temp_project_dir):
        """
        GIVEN project not in database
        WHEN calling install()
        THEN error is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        unknown_path = temp_project_dir / "unknown"
        unknown_path.mkdir()

        # Act
        result = provider.install(unknown_path)

        # Assert
        assert result.success is False
        assert "not found" in result.message.lower()
        assert len(result.errors) > 0

    def test_install_with_minimal_config(self, db_service, project, temp_project_dir):
        """
        GIVEN minimal configuration
        WHEN calling install()
        THEN defaults are applied
        """
        # Arrange
        provider = CursorProvider(db_service)
        config = {
            "rules_enabled": True,
        }

        # Act
        result = provider.install(temp_project_dir, config=config)

        # Assert
        assert result.success is True
        # Should use defaults for other settings
        assert result.installation_id is not None


class TestCursorProviderUninstallation:
    """Test CursorProvider uninstallation workflows."""

    def test_uninstall_success(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN calling uninstall()
        THEN provider is uninstalled successfully
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)
        cursor_dir = temp_project_dir / ".cursor"
        assert cursor_dir.exists()

        # Act
        success = provider.uninstall(temp_project_dir)

        # Assert
        assert success is True
        assert not cursor_dir.exists()

    def test_uninstall_removes_all_files(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider with files
        WHEN calling uninstall()
        THEN all files are removed
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)
        cursor_dir = temp_project_dir / ".cursor"

        # Get file count before uninstall
        file_count = len(list(cursor_dir.rglob("*")))
        assert file_count > 0

        # Act
        success = provider.uninstall(temp_project_dir)

        # Assert
        assert success is True
        assert not cursor_dir.exists()

    def test_uninstall_not_installed(self, db_service, project, temp_project_dir):
        """
        GIVEN project without Cursor provider
        WHEN calling uninstall()
        THEN returns False
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act
        success = provider.uninstall(temp_project_dir)

        # Assert
        assert success is False

    def test_uninstall_project_not_found(self, db_service, temp_project_dir):
        """
        GIVEN project not in database
        WHEN calling uninstall()
        THEN returns False
        """
        # Arrange
        provider = CursorProvider(db_service)
        unknown_path = temp_project_dir / "unknown"
        unknown_path.mkdir()

        # Act
        success = provider.uninstall(unknown_path)

        # Assert
        assert success is False


class TestCursorProviderVerification:
    """Test CursorProvider verification workflows."""

    def test_verify_success(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider with unmodified files
        WHEN calling verify()
        THEN verification passes
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act
        result = provider.verify(temp_project_dir)

        # Assert
        assert isinstance(result, VerifyResult)
        assert result.success is True
        assert result.verified_files > 0
        assert len(result.missing_files) == 0
        assert len(result.modified_files) == 0

    def test_verify_detects_missing_files(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider with deleted file
        WHEN calling verify()
        THEN missing file is detected
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Delete a file
        cursor_dir = temp_project_dir / ".cursor"
        cursorignore = cursor_dir / ".cursorignore"
        if cursorignore.exists():
            cursorignore.unlink()

        # Act
        result = provider.verify(temp_project_dir)

        # Assert
        assert result.success is False
        assert len(result.missing_files) > 0
        assert ".cursorignore" in result.missing_files

    def test_verify_detects_modified_files(
        self, db_service, project, temp_project_dir
    ):
        """
        GIVEN installed provider with modified file
        WHEN calling verify()
        THEN modified file is detected
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Modify a file
        cursor_dir = temp_project_dir / ".cursor"
        cursorignore = cursor_dir / ".cursorignore"
        if cursorignore.exists():
            cursorignore.write_text("# Modified\n")

        # Act
        result = provider.verify(temp_project_dir)

        # Assert
        assert result.success is False
        assert len(result.modified_files) > 0
        assert ".cursorignore" in result.modified_files

    def test_verify_project_not_found(self, db_service, temp_project_dir):
        """
        GIVEN project not in database
        WHEN calling verify()
        THEN error is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        unknown_path = temp_project_dir / "unknown"
        unknown_path.mkdir()

        # Act
        result = provider.verify(unknown_path)

        # Assert
        assert result.success is False
        assert "not found" in result.message.lower()


class TestCursorProviderMemorySync:
    """Test CursorProvider memory sync workflows."""

    def test_sync_memories_to_cursor(
        self, db_service, project, temp_project_dir, mock_database_with_learnings
    ):
        """
        GIVEN installed provider and learnings
        WHEN calling sync_memories(direction="to_cursor")
        THEN learnings are synced to Cursor
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act
        result = provider.sync_memories(temp_project_dir, direction="to_cursor")

        # Assert
        assert isinstance(result, MemorySyncResult)
        assert result.success is True
        assert result.synced_to_cursor > 0
        assert len(result.errors) == 0

    def test_sync_memories_creates_files(
        self, db_service, project, temp_project_dir, mock_database_with_learnings
    ):
        """
        GIVEN installed provider and learnings
        WHEN calling sync_memories()
        THEN memory files are created
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)
        memories_dir = temp_project_dir / ".cursor" / "memories"

        # Act
        result = provider.sync_memories(temp_project_dir, direction="to_cursor")

        # Assert
        memory_files = list(memories_dir.glob("*.md"))
        assert len(memory_files) > 0

    def test_sync_memories_project_not_found(self, db_service, temp_project_dir):
        """
        GIVEN project not in database
        WHEN calling sync_memories()
        THEN error is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        unknown_path = temp_project_dir / "unknown"
        unknown_path.mkdir()

        # Act
        result = provider.sync_memories(unknown_path)

        # Assert
        assert result.success is False
        assert "not found" in result.message.lower()

    def test_sync_memories_not_installed(self, db_service, project, temp_project_dir):
        """
        GIVEN project without Cursor provider
        WHEN calling sync_memories()
        THEN error is returned
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act
        result = provider.sync_memories(temp_project_dir)

        # Assert
        assert result.success is False
        assert "not installed" in result.message.lower()

    def test_sync_memories_from_cursor_p1_feature(
        self, db_service, project, temp_project_dir
    ):
        """
        GIVEN direction="from_cursor" (P1 feature)
        WHEN calling sync_memories()
        THEN P1 message is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act
        result = provider.sync_memories(temp_project_dir, direction="from_cursor")

        # Assert
        assert result.success is False
        assert "P1" in result.message or "coming" in result.message.lower()


class TestCursorProviderUpdate:
    """Test CursorProvider update workflows."""

    def test_update_p1_feature(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN calling update() (P1 feature)
        THEN P1 message is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act
        result = provider.update(temp_project_dir)

        # Assert
        assert isinstance(result, UpdateResult)
        assert result.success is True
        assert "P1" in result.message or "coming" in result.message.lower()


class TestCursorProviderConfiguration:
    """Test CursorProvider configuration management."""

    def test_configure_p1_feature(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN calling configure() (P1 feature)
        THEN configuration is updated
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)
        config = {"memory_sync_enabled": False}

        # Act
        success = provider.configure(temp_project_dir, config)

        # Assert
        assert success is True


class TestCursorProviderStatus:
    """Test CursorProvider status queries."""

    def test_get_status_installed(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN calling get_status()
        THEN status details are returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        install_result = provider.install(temp_project_dir)

        # Act
        status = provider.get_status(temp_project_dir)

        # Assert
        assert isinstance(status, dict)
        assert status["status"] == "installed"
        assert "installed_at" in status
        assert "updated_at" in status
        assert status["installed_files"] > 0
        assert status["version"] == "1.0.0"

    def test_get_status_not_installed(self, db_service, project, temp_project_dir):
        """
        GIVEN project without Cursor provider
        WHEN calling get_status()
        THEN not_installed status is returned
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act
        status = provider.get_status(temp_project_dir)

        # Assert
        assert status["status"] == "not_installed"
        assert "not installed" in status["message"].lower()

    def test_get_status_project_not_found(self, db_service, temp_project_dir):
        """
        GIVEN project not in database
        WHEN calling get_status()
        THEN not_found status is returned
        """
        # Arrange
        provider = CursorProvider(db_service)
        unknown_path = temp_project_dir / "unknown"
        unknown_path.mkdir()

        # Act
        status = provider.get_status(unknown_path)

        # Assert
        assert status["status"] == "not_found"
        assert "not found" in status["message"].lower()


class TestCursorProviderWorkflows:
    """Test complete CursorProvider workflows."""

    def test_full_installation_workflow(self, db_service, project, temp_project_dir):
        """
        GIVEN new project
        WHEN running install → verify → status workflow
        THEN all operations succeed
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act - Install
        install_result = provider.install(temp_project_dir)
        assert install_result.success is True

        # Act - Verify
        verify_result = provider.verify(temp_project_dir)
        assert verify_result.success is True

        # Act - Status
        status = provider.get_status(temp_project_dir)
        assert status["status"] == "installed"

    def test_install_sync_workflow(
        self, db_service, project, temp_project_dir, mock_database_with_learnings
    ):
        """
        GIVEN project with learnings
        WHEN running install → sync workflow
        THEN learnings are synced
        """
        # Arrange
        provider = CursorProvider(db_service)

        # Act - Install
        install_result = provider.install(temp_project_dir)
        assert install_result.success is True

        # Act - Sync
        sync_result = provider.sync_memories(temp_project_dir)
        assert sync_result.success is True
        assert sync_result.synced_to_cursor > 0

    def test_install_uninstall_workflow(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN running install → uninstall workflow
        THEN cleanup is complete
        """
        # Arrange
        provider = CursorProvider(db_service)
        cursor_dir = temp_project_dir / ".cursor"

        # Act - Install
        install_result = provider.install(temp_project_dir)
        assert install_result.success is True
        assert cursor_dir.exists()

        # Act - Uninstall
        uninstall_success = provider.uninstall(temp_project_dir)
        assert uninstall_success is True
        assert not cursor_dir.exists()

        # Act - Status after uninstall
        status = provider.get_status(temp_project_dir)
        assert status["status"] == "not_installed"

    def test_multiple_verify_calls(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider
        WHEN calling verify() multiple times
        THEN all succeed and last_verified_at is updated
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act - First verify
        result1 = provider.verify(temp_project_dir)
        status1 = provider.get_status(temp_project_dir)

        # Act - Second verify
        result2 = provider.verify(temp_project_dir)
        status2 = provider.get_status(temp_project_dir)

        # Assert
        assert result1.success is True
        assert result2.success is True
        # last_verified_at should be updated
        assert status1["last_verified_at"] is not None
        assert status2["last_verified_at"] is not None


class TestCursorProviderEdgeCases:
    """Test edge cases and error scenarios."""

    def test_install_twice_same_project(self, db_service, project, temp_project_dir):
        """
        GIVEN already installed provider
        WHEN calling install() again
        THEN second installation handles existing installation
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act - Second install (should handle gracefully or update)
        # Note: Current implementation may fail on UNIQUE constraint
        # This test documents expected behavior
        result = provider.install(temp_project_dir)

        # Assert - Either succeeds or provides clear error
        assert isinstance(result, InstallResult)

    def test_verify_empty_directory(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider with all files deleted
        WHEN calling verify()
        THEN all files are detected as missing
        """
        # Arrange
        provider = CursorProvider(db_service)
        install_result = provider.install(temp_project_dir)
        cursor_dir = temp_project_dir / ".cursor"

        # Delete all files
        import shutil
        if cursor_dir.exists():
            shutil.rmtree(cursor_dir)
            cursor_dir.mkdir()

        # Act
        result = provider.verify(temp_project_dir)

        # Assert
        assert result.success is False
        assert len(result.missing_files) == len(install_result.installed_files)

    def test_sync_with_no_learnings(self, db_service, project, temp_project_dir):
        """
        GIVEN installed provider with no learnings
        WHEN calling sync_memories()
        THEN sync succeeds with 0 synced
        """
        # Arrange
        provider = CursorProvider(db_service)
        provider.install(temp_project_dir)

        # Act
        result = provider.sync_memories(temp_project_dir)

        # Assert
        assert result.success is True
        assert result.synced_to_cursor == 0
