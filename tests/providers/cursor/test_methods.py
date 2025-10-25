"""
Unit tests for Cursor provider methods (Layer 3).

Tests business logic including:
- InstallationMethods
- VerificationMethods
- MemoryMethods
- TemplateMethods

Coverage target: 90%
"""

import pytest
import hashlib
from pathlib import Path
from datetime import datetime

from agentpm.core.database.methods.provider_methods import (
    InstallationMethods,
    VerificationMethods,
    MemoryMethods,
    TemplateMethods,
)
from agentpm.core.database.models.provider import (
    CursorConfig,
    ProviderType,
    InstallationStatus,
)


class TestInstallationMethods:
    """Test InstallationMethods business logic."""

    def test_install_success(self, db_service, project, sample_config, aipm_root):
        """
        GIVEN valid project and config
        WHEN calling install()
        THEN provider is installed successfully
        """
        # Arrange
        methods = InstallationMethods(db_service)

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        assert result.success is True
        assert result.installation_id is not None
        assert len(result.installed_files) > 0
        assert len(result.errors) == 0
        assert "successfully" in result.message.lower()

    def test_install_creates_directory_structure(
        self, db_service, project, sample_config
    ):
        """
        GIVEN project without .cursor directory
        WHEN calling install()
        THEN .cursor directory structure is created
        """
        # Arrange
        methods = InstallationMethods(db_service)
        project_path = Path(sample_config.project_path)
        cursor_dir = project_path / ".cursor"

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        assert cursor_dir.exists()
        assert (cursor_dir / "rules").exists()
        assert (cursor_dir / "memories").exists()

    def test_install_creates_modes_dir_when_enabled(
        self, db_service, project, sample_config
    ):
        """
        GIVEN config with modes_enabled=True
        WHEN calling install()
        THEN modes directory is created
        """
        # Arrange
        methods = InstallationMethods(db_service)
        sample_config.modes_enabled = True
        cursor_dir = Path(sample_config.project_path) / ".cursor"

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        assert (cursor_dir / "modes").exists()

    def test_install_skips_modes_dir_when_disabled(
        self, db_service, project, minimal_config
    ):
        """
        GIVEN config with modes_enabled=False
        WHEN calling install()
        THEN modes directory is not created
        """
        # Arrange
        methods = InstallationMethods(db_service)
        minimal_config.modes_enabled = False
        cursor_dir = Path(minimal_config.project_path) / ".cursor"

        # Act
        result = methods.install(project.id, minimal_config)

        # Assert
        assert not (cursor_dir / "modes").exists()

    def test_install_creates_cursorignore(self, db_service, project, sample_config):
        """
        GIVEN config with indexing_enabled=True
        WHEN calling install()
        THEN .cursorignore file is created with exclude patterns
        """
        # Arrange
        methods = InstallationMethods(db_service)
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        sample_config.exclude_patterns = [".aipm/", "*.pyc"]

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        cursorignore = cursor_dir / ".cursorignore"
        assert cursorignore.exists()
        content = cursorignore.read_text()
        assert ".aipm/" in content
        assert "*.pyc" in content

    def test_install_saves_to_database(self, db_service, project, sample_config):
        """
        GIVEN successful installation
        WHEN calling install()
        THEN installation record is saved to database
        """
        # Arrange
        methods = InstallationMethods(db_service)

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM provider_installations WHERE id = ?",
                (result.installation_id,),
            )
            row = cursor.fetchone()
        assert row is not None
        assert row["project_id"] == project.id
        assert row["provider_type"] == "cursor"
        assert row["status"] == "installed"

    def test_install_tracks_file_hashes(self, db_service, project, sample_config):
        """
        GIVEN successful installation
        WHEN calling install()
        THEN file hashes are tracked
        """
        # Arrange
        methods = InstallationMethods(db_service)

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM provider_files WHERE installation_id = ?",
                (result.installation_id,),
            )
            rows = cursor.fetchall()
        assert len(rows) > 0
        for row in rows:
            assert row["file_hash"] is not None
            assert len(row["file_hash"]) == 64  # SHA-256 hex length

    def test_install_handles_partial_failure(
        self, db_service, project, sample_config
    ):
        """
        GIVEN config with invalid rule
        WHEN calling install()
        THEN status is PARTIAL and errors are reported
        """
        # Arrange
        methods = InstallationMethods(db_service)
        sample_config.rules_to_install.append("non-existent-rule")

        # Act
        result = methods.install(project.id, sample_config)

        # Assert
        # Should still succeed for valid rules
        assert result.installation_id is not None
        # But errors should be reported
        assert len(result.errors) > 0

    def test_uninstall_success(self, db_service, project, sample_config):
        """
        GIVEN installed provider
        WHEN calling uninstall()
        THEN provider is uninstalled successfully
        """
        # Arrange
        methods = InstallationMethods(db_service)
        install_result = methods.install(project.id, sample_config)
        cursor_dir = Path(sample_config.project_path) / ".cursor"

        # Act
        success = methods.uninstall(project.id)

        # Assert
        assert success is True
        assert not cursor_dir.exists()

    def test_uninstall_removes_database_records(
        self, db_service, project, sample_config
    ):
        """
        GIVEN installed provider
        WHEN calling uninstall()
        THEN database records are deleted
        """
        # Arrange
        methods = InstallationMethods(db_service)
        install_result = methods.install(project.id, sample_config)

        # Act
        success = methods.uninstall(project.id)

        # Assert
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM provider_installations WHERE id = ?",
                (install_result.installation_id,),
            )
            install_row = cursor.fetchone()
        assert install_row is None

        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM provider_files WHERE installation_id = ?",
                (install_result.installation_id,),
            )
            file_rows = cursor.fetchall()
        assert len(file_rows) == 0

    def test_uninstall_not_installed(self, db_service, project):
        """
        GIVEN project without Cursor provider
        WHEN calling uninstall()
        THEN returns False
        """
        # Arrange
        methods = InstallationMethods(db_service)

        # Act
        success = methods.uninstall(project.id)

        # Assert
        assert success is False

    def test_uninstall_creates_backup(self, db_service, project, sample_config):
        """
        GIVEN installed provider with backup=True
        WHEN calling uninstall()
        THEN backup is created before deletion
        """
        # Arrange
        methods = InstallationMethods(db_service)
        install_result = methods.install(project.id, sample_config)
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        project_path = Path(sample_config.project_path)

        # Act
        success = methods.uninstall(project.id, backup=True)

        # Assert
        assert success is True
        assert not cursor_dir.exists()

        # Check backup directory exists (if files were installed)
        backup_dirs = list(project_path.glob(".cursor-backup-*"))
        if install_result.installed_files:
            assert len(backup_dirs) > 0
            # Check backup contains files
            backup_dir = backup_dirs[0]
            backup_files = list(backup_dir.rglob("*.mdc"))  # Check for rule files
            # Backup should have at least rule files if they were installed
            assert len(backup_files) > 0 or len(install_result.installed_files) == 0

    def test_uninstall_without_backup(self, db_service, project, sample_config):
        """
        GIVEN installed provider with backup=False
        WHEN calling uninstall()
        THEN no backup is created
        """
        # Arrange
        methods = InstallationMethods(db_service)
        install_result = methods.install(project.id, sample_config)
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        project_path = Path(sample_config.project_path)

        # Act
        success = methods.uninstall(project.id, backup=False)

        # Assert
        assert success is True
        assert not cursor_dir.exists()

        # Check no backup directory created
        backup_dirs = list(project_path.glob(".cursor-backup-*"))
        assert len(backup_dirs) == 0

    def test_uninstall_removes_cursor_memories(
        self, db_service, project, sample_config
    ):
        """
        GIVEN installed provider with cursor memories
        WHEN calling uninstall()
        THEN cursor memories are deleted from database
        """
        # Arrange
        methods = InstallationMethods(db_service)
        install_result = methods.install(project.id, sample_config)

        # Create cursor memory record (disable FK checks temporarily)
        with db_service.connect() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                INSERT INTO cursor_memories (
                    project_id, name, description, category, content,
                    tags, file_path, file_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    "test-memory",
                    "Test memory",
                    "general",
                    "Test content",
                    "[]",
                    "test.md",
                    "abc123",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.execute("PRAGMA foreign_keys = ON")

        # Act
        success = methods.uninstall(project.id)

        # Assert
        assert success is True

        # Verify cursor memories deleted
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            memories = conn.execute(
                "SELECT * FROM cursor_memories WHERE project_id = ?",
                (project.id,)
            ).fetchall()

        assert len(memories) == 0

    def test_determine_file_type(self, db_service):
        """
        GIVEN different file paths
        WHEN calling _determine_file_type()
        THEN correct file type is returned
        """
        # Arrange
        methods = InstallationMethods(db_service)

        # Act & Assert
        assert methods._determine_file_type("rules/test.mdc") == "rule"
        assert methods._determine_file_type("modes/test.json") == "mode"
        assert methods._determine_file_type(".cursorignore") == "config"
        assert methods._determine_file_type("memories/test.md") == "memory"
        assert methods._determine_file_type("other.txt") == "config"


class TestVerificationMethods:
    """Test VerificationMethods business logic."""

    def test_verify_success(self, db_service, project, sample_config):
        """
        GIVEN installed provider with unmodified files
        WHEN calling verify()
        THEN verification passes
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        verify_methods = VerificationMethods(db_service)
        install_methods.install(project.id, sample_config)

        # Act
        result = verify_methods.verify(project.id)

        # Assert
        assert result.success is True
        assert result.verified_files > 0
        assert len(result.missing_files) == 0
        assert len(result.modified_files) == 0

    def test_verify_detects_missing_files(self, db_service, project, sample_config):
        """
        GIVEN installed provider with deleted file
        WHEN calling verify()
        THEN missing file is detected
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        verify_methods = VerificationMethods(db_service)
        install_result = install_methods.install(project.id, sample_config)

        # Delete a file
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        cursorignore = cursor_dir / ".cursorignore"
        if cursorignore.exists():
            cursorignore.unlink()

        # Act
        result = verify_methods.verify(project.id)

        # Assert
        assert result.success is False
        assert len(result.missing_files) > 0
        assert ".cursorignore" in result.missing_files

    def test_verify_detects_modified_files(self, db_service, project, sample_config):
        """
        GIVEN installed provider with modified file
        WHEN calling verify()
        THEN modified file is detected
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        verify_methods = VerificationMethods(db_service)
        install_result = install_methods.install(project.id, sample_config)

        # Modify a file
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        cursorignore = cursor_dir / ".cursorignore"
        if cursorignore.exists():
            cursorignore.write_text("# Modified content\n")

        # Act
        result = verify_methods.verify(project.id)

        # Assert
        assert result.success is False
        assert len(result.modified_files) > 0
        assert ".cursorignore" in result.modified_files

    def test_verify_updates_last_verified_at(self, db_service, project, sample_config):
        """
        GIVEN installed provider
        WHEN calling verify()
        THEN last_verified_at timestamp is updated
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        verify_methods = VerificationMethods(db_service)
        install_result = install_methods.install(project.id, sample_config)

        # Act
        result = verify_methods.verify(project.id)

        # Assert
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT last_verified_at FROM provider_installations WHERE id = ?",
                (install_result.installation_id,),
            )
            row = cursor.fetchone()
        assert row["last_verified_at"] is not None

    def test_verify_not_installed(self, db_service, project):
        """
        GIVEN project without Cursor provider
        WHEN calling verify()
        THEN verification fails with message
        """
        # Arrange
        methods = VerificationMethods(db_service)

        # Act
        result = methods.verify(project.id)

        # Assert
        assert result.success is False
        assert "not installed" in result.message.lower()


class TestMemoryMethods:
    """Test MemoryMethods business logic."""

    def test_sync_to_cursor_success(
        self, db_service, project, sample_config, mock_database_with_learnings
    ):
        """
        GIVEN installed provider and learnings
        WHEN calling sync_to_cursor()
        THEN learnings are synced to Cursor memories
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)
        install_methods.install(project.id, sample_config)

        # Act
        result = memory_methods.sync_to_cursor(project.id)

        # Assert
        assert result.success is True
        assert result.synced_to_cursor == 3  # 3 learnings from fixture
        assert len(result.errors) == 0

    def test_sync_to_cursor_creates_memory_files(
        self, db_service, project, sample_config, mock_database_with_learnings
    ):
        """
        GIVEN installed provider and learnings
        WHEN calling sync_to_cursor()
        THEN memory files are created
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)
        install_methods.install(project.id, sample_config)
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        memories_dir = cursor_dir / "memories"

        # Act
        result = memory_methods.sync_to_cursor(project.id)

        # Assert
        memory_files = list(memories_dir.glob("*.md"))
        assert len(memory_files) == 3

    def test_sync_to_cursor_saves_to_database(
        self, db_service, project, sample_config, mock_database_with_learnings
    ):
        """
        GIVEN installed provider and learnings
        WHEN calling sync_to_cursor()
        THEN cursor_memories records are created
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)
        install_methods.install(project.id, sample_config)

        # Act
        result = memory_methods.sync_to_cursor(project.id)

        # Assert
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM cursor_memories WHERE project_id = ?",
                (project.id,),
            )
            rows = cursor.fetchall()
        assert len(rows) == 3
        for row in rows:
            assert row["source_learning_id"] is not None
            assert row["file_hash"] is not None

    def test_sync_to_cursor_skips_already_synced(
        self, db_service, project, sample_config, mock_database_with_learnings
    ):
        """
        GIVEN learnings already synced
        WHEN calling sync_to_cursor() again
        THEN already synced learnings are skipped
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)
        install_methods.install(project.id, sample_config)

        # Act - first sync
        result1 = memory_methods.sync_to_cursor(project.id)
        # Act - second sync (should skip)
        result2 = memory_methods.sync_to_cursor(project.id)

        # Assert
        assert result1.synced_to_cursor == 3
        assert result2.synced_to_cursor == 0  # All already synced

    def test_sync_to_cursor_not_installed(self, db_service, project):
        """
        GIVEN project without Cursor provider
        WHEN calling sync_to_cursor()
        THEN returns error
        """
        # Arrange
        methods = MemoryMethods(db_service)

        # Act
        result = methods.sync_to_cursor(project.id)

        # Assert
        assert result.success is False
        assert "not installed" in result.message.lower()

    def test_sync_to_cursor_limits_to_20(
        self, db_service, project, sample_config
    ):
        """
        GIVEN more than 20 unsynced learnings
        WHEN calling sync_to_cursor()
        THEN only 20 most recent are synced
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)
        install_methods.install(project.id, sample_config)

        # Create 25 learnings
        with db_service.connect() as conn:
            for i in range(25):
                conn.execute(
                    """
                    INSERT INTO learnings (
                        project_id, title, content, type, confidence,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project.id,
                        f"Learning {i}",
                        f"Content {i}",
                        "technical",
                        0.8,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                    ),
                )
            conn.commit()

        # Act
        result = memory_methods.sync_to_cursor(project.id)

        # Assert
        assert result.success is True
        assert result.synced_to_cursor <= 20


class TestTemplateMethods:
    """Test TemplateMethods business logic."""

    def test_render_rule_success(self, db_service, project, sample_config, aipm_root):
        """
        GIVEN valid rule ID
        WHEN calling render_rule()
        THEN rendered rule content is returned
        """
        # Arrange
        methods = TemplateMethods(db_service)

        # Act
        content = methods.render_rule("aipm-master", sample_config, project.id)

        # Assert
        assert isinstance(content, str)
        assert len(content) > 0

    def test_render_rule_substitutes_variables(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN rule template with variables
        WHEN calling render_rule()
        THEN variables are substituted
        """
        # Arrange
        methods = TemplateMethods(db_service)

        # Act
        content = methods.render_rule("aipm-master", sample_config, project.id)

        # Assert
        # Variables should be substituted
        assert sample_config.project_name in content or "{{ project_name }}" not in content
        assert sample_config.project_path in content or "{{ project_path }}" not in content

    def test_render_rule_not_found(self, db_service, project, sample_config):
        """
        GIVEN non-existent rule ID
        WHEN calling render_rule()
        THEN FileNotFoundError is raised
        """
        # Arrange
        methods = TemplateMethods(db_service)

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            methods.render_rule("non-existent-rule", sample_config, project.id)
        assert "not found" in str(exc_info.value).lower()


class TestMethodsIntegration:
    """Test integration between different methods classes."""

    def test_install_verify_workflow(self, db_service, project, sample_config):
        """
        GIVEN installation then verification
        WHEN workflow completes
        THEN both succeed
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        verify_methods = VerificationMethods(db_service)

        # Act
        install_result = install_methods.install(project.id, sample_config)
        verify_result = verify_methods.verify(project.id)

        # Assert
        assert install_result.success is True
        assert verify_result.success is True

    def test_install_sync_workflow(
        self, db_service, project, sample_config, mock_database_with_learnings
    ):
        """
        GIVEN installation then memory sync
        WHEN workflow completes
        THEN both succeed
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        memory_methods = MemoryMethods(db_service)

        # Act
        install_result = install_methods.install(project.id, sample_config)
        sync_result = memory_methods.sync_to_cursor(project.id)

        # Assert
        assert install_result.success is True
        assert sync_result.success is True
        assert sync_result.synced_to_cursor > 0

    def test_install_uninstall_cleanup(self, db_service, project, sample_config):
        """
        GIVEN installation then uninstallation
        WHEN workflow completes
        THEN all resources are cleaned up
        """
        # Arrange
        install_methods = InstallationMethods(db_service)
        cursor_dir = Path(sample_config.project_path) / ".cursor"

        # Act
        install_result = install_methods.install(project.id, sample_config)
        assert cursor_dir.exists()

        uninstall_success = install_methods.uninstall(project.id)

        # Assert
        assert uninstall_success is True
        assert not cursor_dir.exists()

        # Verify database cleanup
        with db_service.connect() as conn:
            conn.row_factory = lambda cursor, row: dict(
                zip([col[0] for col in cursor.description], row)
            )
            cursor = conn.execute(
                "SELECT * FROM provider_installations WHERE id = ?",
                (install_result.installation_id,),
            )
            install_row = cursor.fetchone()
        assert install_row is None
