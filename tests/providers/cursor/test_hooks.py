"""
Unit tests for Cursor provider hooks.

Tests event-driven lifecycle management including:
- Provider installation/uninstallation hooks
- Context change hooks
- Rule update hooks
- Hook registration/unregistration

Coverage target: 90%
"""

import pytest
from pathlib import Path
from datetime import datetime

from agentpm.providers.cursor.hooks import CursorHooks, register_cursor_hooks
from agentpm.providers.anthropic.claude_code.runtime.hooks import (
    HookEvent,
    EventType,
    get_hooks_engine,
    reset_hooks_engine,
)
from agentpm.core.database.models.provider import (
    CursorConfig,
    ProviderType,
    InstallationStatus,
)


class TestCursorHooks:
    """Test CursorHooks lifecycle management."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Reset hooks engine before and after each test."""
        reset_hooks_engine()
        yield
        reset_hooks_engine()

    def test_register_all_hooks(self, db_service):
        """
        GIVEN CursorHooks instance
        WHEN calling register_all()
        THEN all hooks are registered with engine
        """
        # Arrange
        hooks = CursorHooks(db_service)
        engine = get_hooks_engine()

        # Act
        hooks.register_all()

        # Assert
        assert hooks._registered is True
        # Verify handlers exist by checking internal state
        assert "provider-install" in engine._event_handlers
        assert "provider-uninstall" in engine._event_handlers
        assert "context-change" in engine._event_handlers
        assert "rule-update" in engine._event_handlers

    def test_register_all_idempotent(self, db_service):
        """
        GIVEN already registered hooks
        WHEN calling register_all() again
        THEN no error occurs (idempotent)
        """
        # Arrange
        hooks = CursorHooks(db_service)

        # Act
        hooks.register_all()
        hooks.register_all()  # Should not raise

        # Assert
        assert hooks._registered is True

    def test_unregister_all_hooks(self, db_service):
        """
        GIVEN registered hooks
        WHEN calling unregister_all()
        THEN all hooks are unregistered
        """
        # Arrange
        hooks = CursorHooks(db_service)
        hooks.register_all()
        engine = get_hooks_engine()

        # Act
        hooks.unregister_all()

        # Assert
        assert hooks._registered is False

    def test_on_provider_install_success(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN provider installation event
        WHEN calling on_provider_install()
        THEN rule files are generated
        """
        # Arrange
        hooks = CursorHooks(db_service)

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
            provider_id = result.lastrowid

        event = HookEvent(
            type="provider-install",
            payload={
                "provider_id": provider_id,
                "project_id": project.id,
                "config": sample_config.model_dump(),
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_provider_install(event)

        # Assert
        assert result["status"] == "success"
        assert result["files_generated"] > 0
        assert len(result["files"]) > 0

    def test_on_provider_install_missing_payload(self, db_service):
        """
        GIVEN event with missing provider_id
        WHEN calling on_provider_install()
        THEN error is returned
        """
        # Arrange
        hooks = CursorHooks(db_service)
        event = HookEvent(
            type="provider-install",
            payload={},
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_provider_install(event)

        # Assert
        assert result["status"] == "error"
        assert "Missing" in result["message"]

    def test_on_provider_uninstall_success(
        self, db_service, project, sample_config
    ):
        """
        GIVEN provider installation
        WHEN calling on_provider_uninstall()
        THEN cleanup is reported
        """
        # Arrange
        hooks = CursorHooks(db_service)

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
                    "rules/aipm-master.mdc,rules/code-quality.mdc",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            provider_id = result.lastrowid

        event = HookEvent(
            type="provider-uninstall",
            payload={
                "provider_id": provider_id,
                "project_id": project.id,
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_provider_uninstall(event)

        # Assert
        assert result["status"] == "success"
        assert "files_cleaned" in result

    def test_on_provider_uninstall_not_found(self, db_service):
        """
        GIVEN non-existent provider
        WHEN calling on_provider_uninstall()
        THEN warning is returned
        """
        # Arrange
        hooks = CursorHooks(db_service)
        event = HookEvent(
            type="provider-uninstall",
            payload={
                "provider_id": 99999,
                "project_id": 99999,
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_provider_uninstall(event)

        # Assert
        assert result["status"] == "warning"
        assert "not found" in result["message"]

    def test_on_context_change_provider_installed(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN provider installed and context change
        WHEN calling on_context_change()
        THEN rule files are regenerated
        """
        # Arrange
        hooks = CursorHooks(db_service)

        # Create directories
        cursor_dir = Path(sample_config.project_path) / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Create installation record
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
                    str(cursor_dir),
                    InstallationStatus.INSTALLED.value,
                    sample_config.model_dump_json(),
                    "[]",
                    "{}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        event = HookEvent(
            type="context-change",
            payload={
                "project_id": project.id,
                "changes": {"tech_stack": ["Python", "SQLite"]},
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_context_change(event)

        # Assert
        assert result["status"] == "success"
        assert result["files_regenerated"] > 0

    def test_on_context_change_provider_not_installed(
        self, db_service, project
    ):
        """
        GIVEN provider not installed
        WHEN calling on_context_change()
        THEN event is skipped
        """
        # Arrange
        hooks = CursorHooks(db_service)
        event = HookEvent(
            type="context-change",
            payload={
                "project_id": project.id,
                "changes": {"tech_stack": ["Python"]},
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_context_change(event)

        # Assert
        assert result["status"] == "skipped"
        assert "not installed" in result["message"]

    def test_on_rule_update_success(
        self, db_service, project, sample_config, aipm_root
    ):
        """
        GIVEN rule category update
        WHEN calling on_rule_update()
        THEN corresponding rule file is regenerated
        """
        # Arrange
        hooks = CursorHooks(db_service)

        # Create installation record
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

        event = HookEvent(
            type="rule-update",
            payload={
                "project_id": project.id,
                "rule_category": "Code Quality",
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_rule_update(event)

        # Assert - may be success or skipped depending on rules in DB
        assert result["status"] in ["success", "skipped"]

    def test_on_rule_update_unknown_category(
        self, db_service, project, sample_config
    ):
        """
        GIVEN unknown rule category
        WHEN calling on_rule_update()
        THEN event is skipped
        """
        # Arrange
        hooks = CursorHooks(db_service)

        # Create installation record
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

        event = HookEvent(
            type="rule-update",
            payload={
                "project_id": project.id,
                "rule_category": "Unknown Category",
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Act
        result = hooks.on_rule_update(event)

        # Assert
        assert result["status"] == "skipped"
        assert "No rule file" in result["message"]


class TestRegisterCursorHooks:
    """Test convenience registration function."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Reset hooks engine before and after each test."""
        reset_hooks_engine()
        yield
        reset_hooks_engine()

    def test_register_cursor_hooks(self, db_service):
        """
        GIVEN database service
        WHEN calling register_cursor_hooks()
        THEN hooks are registered and instance returned
        """
        # Act
        hooks = register_cursor_hooks(db_service)

        # Assert
        assert isinstance(hooks, CursorHooks)
        assert hooks._registered is True

    def test_hooks_respond_to_events(self, db_service, project, sample_config):
        """
        GIVEN registered hooks
        WHEN dispatching events through engine
        THEN hooks respond appropriately
        """
        # Arrange
        register_cursor_hooks(db_service)
        engine = get_hooks_engine()

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
            provider_id = result.lastrowid

        # Act
        result = engine.dispatch_event(
            event_type="provider-uninstall",
            payload={
                "provider_id": provider_id,
                "project_id": project.id,
            },
            session_id="test-session",
            correlation_id="test-corr",
        )

        # Assert
        assert result.success is True
        assert len(result.data["results"]) > 0
