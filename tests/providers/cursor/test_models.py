"""
Unit tests for Cursor provider models (Layer 1).

Tests all Pydantic models including:
- ProviderInstallation
- CursorConfig
- CursorMemory
- CustomMode
- Guardrails
- Result types

Coverage target: 95%
"""

import pytest
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError

from agentpm.core.database.models.provider import (
    ProviderType,
    InstallationStatus,
    MemorySyncDirection,
    SafetyLevel,
    ProviderInstallation,
    CursorConfig,
    CursorMemory,
    CustomMode,
    AllowlistEntry,
    Guardrails,
    RuleTemplate,
    InstallResult,
    VerifyResult,
    MemorySyncResult,
    UpdateResult,
)


class TestEnums:
    """Test enum definitions."""

    def test_provider_type_enum(self):
        """
        GIVEN ProviderType enum
        WHEN accessing valid values
        THEN correct values are returned
        """
        # Act & Assert
        assert ProviderType.CURSOR == "cursor"
        assert ProviderType.VSCODE == "vscode"
        assert ProviderType.ZED == "zed"
        assert ProviderType.CLAUDE_CODE == "claude_code"

    def test_installation_status_enum(self):
        """
        GIVEN InstallationStatus enum
        WHEN accessing valid values
        THEN correct values are returned
        """
        # Act & Assert
        assert InstallationStatus.INSTALLED == "installed"
        assert InstallationStatus.PARTIAL == "partial"
        assert InstallationStatus.FAILED == "failed"
        assert InstallationStatus.UNINSTALLED == "uninstalled"

    def test_memory_sync_direction_enum(self):
        """
        GIVEN MemorySyncDirection enum
        WHEN accessing valid values
        THEN correct values are returned
        """
        # Act & Assert
        assert MemorySyncDirection.TO_CURSOR == "to_cursor"
        assert MemorySyncDirection.FROM_CURSOR == "from_cursor"
        assert MemorySyncDirection.BI_DIRECTIONAL == "bi_directional"

    def test_safety_level_enum(self):
        """
        GIVEN SafetyLevel enum
        WHEN accessing valid values
        THEN correct values are returned
        """
        # Act & Assert
        assert SafetyLevel.SAFE_AUTO == "safe_auto"
        assert SafetyLevel.SAFE_CONFIRM == "safe_confirm"
        assert SafetyLevel.UNSAFE == "unsafe"


class TestProviderInstallation:
    """Test ProviderInstallation model."""

    def test_create_provider_installation_valid(self):
        """
        GIVEN valid ProviderInstallation data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            provider_version="1.0.0",
            install_path="/path/to/project/.cursor",
            status=InstallationStatus.INSTALLED,
            config={"test": "value"},
            installed_files=["rules/test.mdc"],
            file_hashes={"rules/test.mdc": "abc123"},
        )

        # Assert
        assert installation.project_id == 1
        assert installation.provider_type == ProviderType.CURSOR
        assert installation.status == InstallationStatus.INSTALLED
        assert installation.installed_files == ["rules/test.mdc"]
        assert installation.file_hashes == {"rules/test.mdc": "abc123"}
        assert installation.installed_at is not None
        assert installation.updated_at is not None

    def test_provider_installation_defaults(self):
        """
        GIVEN minimal ProviderInstallation data
        WHEN creating model
        THEN default values are applied
        """
        # Arrange & Act
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
        )

        # Assert
        assert installation.provider_version == "1.0.0"
        assert installation.status == InstallationStatus.INSTALLED
        assert installation.config == {}
        assert installation.installed_files == []
        assert installation.file_hashes == {}
        assert installation.last_verified_at is None

    def test_provider_installation_whitespace_stripping(self):
        """
        GIVEN ProviderInstallation with whitespace
        WHEN creating model
        THEN whitespace is stripped
        """
        # Arrange & Act
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            provider_version=" 1.0.0 ",
            install_path=" /path/.cursor ",
        )

        # Assert
        assert installation.provider_version == "1.0.0"
        assert installation.install_path == "/path/.cursor"


class TestCursorConfig:
    """Test CursorConfig model."""

    def test_create_cursor_config_valid(self, temp_project_dir):
        """
        GIVEN valid CursorConfig data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        config = CursorConfig(
            project_name="Test Project",
            project_path=str(temp_project_dir),
            tech_stack=["Python", "SQLite"],
            rules_enabled=True,
            memory_sync_enabled=True,
        )

        # Assert
        assert config.project_name == "Test Project"
        assert config.project_path == str(temp_project_dir)
        assert config.tech_stack == ["Python", "SQLite"]
        assert config.rules_enabled is True
        assert config.memory_sync_enabled is True

    def test_cursor_config_default_rules(self, temp_project_dir):
        """
        GIVEN CursorConfig without rules_to_install
        WHEN creating model
        THEN default rules are set
        """
        # Arrange & Act
        config = CursorConfig(
            project_name="Test",
            project_path=str(temp_project_dir),
        )

        # Assert
        assert len(config.rules_to_install) == 6
        assert "aipm-master" in config.rules_to_install
        assert "python-implementation" in config.rules_to_install
        assert "testing-standards" in config.rules_to_install
        assert "cli-development" in config.rules_to_install
        assert "database-patterns" in config.rules_to_install
        assert "documentation-quality" in config.rules_to_install

    def test_cursor_config_default_modes(self, temp_project_dir):
        """
        GIVEN CursorConfig without modes_to_install
        WHEN creating model
        THEN default modes are set
        """
        # Arrange & Act
        config = CursorConfig(
            project_name="Test",
            project_path=str(temp_project_dir),
        )

        # Assert
        assert len(config.modes_to_install) == 6
        assert "aipm-discovery" in config.modes_to_install
        assert "aipm-planning" in config.modes_to_install
        assert "aipm-implementation" in config.modes_to_install
        assert "aipm-review" in config.modes_to_install
        assert "aipm-operations" in config.modes_to_install
        assert "aipm-evolution" in config.modes_to_install

    def test_cursor_config_default_exclude_patterns(self, temp_project_dir):
        """
        GIVEN CursorConfig without exclude_patterns
        WHEN creating model
        THEN default patterns are set
        """
        # Arrange & Act
        config = CursorConfig(
            project_name="Test",
            project_path=str(temp_project_dir),
        )

        # Assert
        assert ".aipm/" in config.exclude_patterns
        assert "htmlcov/" in config.exclude_patterns
        assert ".pytest_cache/" in config.exclude_patterns
        assert "**/__pycache__/" in config.exclude_patterns
        assert "*.pyc" in config.exclude_patterns

    def test_cursor_config_memory_sync_interval_validation(self, temp_project_dir):
        """
        GIVEN CursorConfig with invalid memory_sync_interval_hours
        WHEN creating model
        THEN validation error is raised
        """
        # Act & Assert - too small
        with pytest.raises(ValidationError) as exc_info:
            CursorConfig(
                project_name="Test",
                project_path=str(temp_project_dir),
                memory_sync_interval_hours=0,
            )
        assert "greater than or equal to 1" in str(exc_info.value)

        # Act & Assert - too large
        with pytest.raises(ValidationError) as exc_info:
            CursorConfig(
                project_name="Test",
                project_path=str(temp_project_dir),
                memory_sync_interval_hours=25,
            )
        assert "less than or equal to 24" in str(exc_info.value)

    def test_cursor_config_project_path_must_be_absolute(self):
        """
        GIVEN CursorConfig with relative project_path
        WHEN creating model
        THEN validation error is raised
        """
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            CursorConfig(
                project_name="Test",
                project_path="relative/path",
            )
        assert "must be an absolute path" in str(exc_info.value)


class TestCursorMemory:
    """Test CursorMemory model."""

    def test_create_cursor_memory_valid(self):
        """
        GIVEN valid CursorMemory data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        memory = CursorMemory(
            project_id=1,
            name="test-memory",
            description="Test memory",
            category="testing",
            content="# Test\n\nContent here.",
            tags=["test", "demo"],
            file_path="test-memory.md",
        )

        # Assert
        assert memory.project_id == 1
        assert memory.name == "test-memory"
        assert memory.description == "Test memory"
        assert memory.category == "testing"
        assert memory.content == "# Test\n\nContent here."
        assert memory.tags == ["test", "demo"]
        assert memory.file_path == "test-memory.md"
        assert memory.created_at is not None
        assert memory.updated_at is not None

    def test_cursor_memory_defaults(self):
        """
        GIVEN minimal CursorMemory data
        WHEN creating model
        THEN default values are applied
        """
        # Arrange & Act
        memory = CursorMemory(
            project_id=1,
            name="test",
            description="Test",
            content="Content",
            file_path="test.md",
        )

        # Assert
        assert memory.category == "general"
        assert memory.tags == []
        assert memory.file_hash is None
        assert memory.source_learning_id is None
        assert memory.last_synced_at is None

    def test_cursor_memory_field_validation(self):
        """
        GIVEN CursorMemory with invalid field lengths
        WHEN creating model
        THEN validation error is raised
        """
        # Act & Assert - name too long
        with pytest.raises(ValidationError):
            CursorMemory(
                project_id=1,
                name="x" * 101,  # max_length=100
                description="Test",
                content="Content",
                file_path="test.md",
            )

        # Act & Assert - description too long
        with pytest.raises(ValidationError):
            CursorMemory(
                project_id=1,
                name="test",
                description="x" * 501,  # max_length=500
                content="Content",
                file_path="test.md",
            )

        # Act & Assert - empty name
        with pytest.raises(ValidationError):
            CursorMemory(
                project_id=1,
                name="",  # min_length=1
                description="Test",
                content="Content",
                file_path="test.md",
            )


class TestCustomMode:
    """Test CustomMode model."""

    def test_create_custom_mode_valid(self):
        """
        GIVEN valid CustomMode data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        mode = CustomMode(
            mode_id="aipm-discovery",
            display_name="AIPM Discovery",
            description="Discovery phase mode",
            system_prompt="You are in discovery mode.",
            phase="D1",
            tools_enabled=["search", "analyze"],
            rules_active=["aipm-master"],
        )

        # Assert
        assert mode.mode_id == "aipm-discovery"
        assert mode.display_name == "AIPM Discovery"
        assert mode.phase == "D1"
        assert mode.tools_enabled == ["search", "analyze"]
        assert mode.rules_active == ["aipm-master"]

    def test_custom_mode_defaults(self):
        """
        GIVEN minimal CustomMode data
        WHEN creating model
        THEN default values are applied
        """
        # Arrange & Act
        mode = CustomMode(
            mode_id="test-mode",
            display_name="Test",
            description="Test mode",
            system_prompt="Test prompt",
            phase="I1",
        )

        # Assert
        assert mode.tools_enabled == []
        assert mode.rules_active == []
        assert mode.icon == "🔧"
        assert mode.color == "#1e90ff"
        assert mode.auto_activate is False
        assert mode.default_for_phase is True


class TestGuardrails:
    """Test Guardrails and AllowlistEntry models."""

    def test_create_allowlist_entry_valid(self):
        """
        GIVEN valid AllowlistEntry data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        entry = AllowlistEntry(
            pattern="^apm status$",
            safety=SafetyLevel.SAFE_AUTO,
            auto_run=True,
            description="Safe command",
        )

        # Assert
        assert entry.pattern == "^apm status$"
        assert entry.safety == SafetyLevel.SAFE_AUTO
        assert entry.auto_run is True
        assert entry.description == "Safe command"

    def test_allowlist_entry_defaults(self):
        """
        GIVEN minimal AllowlistEntry data
        WHEN creating model
        THEN default values are applied
        """
        # Arrange & Act
        entry = AllowlistEntry(
            pattern="^test$",
        )

        # Assert
        assert entry.safety == SafetyLevel.SAFE_CONFIRM
        assert entry.auto_run is False
        assert entry.description == ""

    def test_create_guardrails_with_defaults(self):
        """
        GIVEN Guardrails without allowlists
        WHEN creating model
        THEN default allowlists are set
        """
        # Arrange & Act
        guardrails = Guardrails()

        # Assert
        assert "apm_commands" in guardrails.allowlists
        assert "testing" in guardrails.allowlists
        assert "linting" in guardrails.allowlists
        assert len(guardrails.allowlists["apm_commands"]) >= 3
        assert guardrails.require_confirmation_by_default is True
        assert guardrails.allow_destructive_operations is False
        assert guardrails.max_auto_runs_per_session == 10

    def test_guardrails_custom_allowlists(self):
        """
        GIVEN Guardrails with custom allowlists
        WHEN creating model
        THEN custom allowlists are used
        """
        # Arrange
        custom_allowlists = {
            "custom": [
                AllowlistEntry(
                    pattern="^custom command$",
                    safety=SafetyLevel.SAFE_AUTO,
                )
            ]
        }

        # Act
        guardrails = Guardrails(allowlists=custom_allowlists)

        # Assert
        assert "custom" in guardrails.allowlists
        assert len(guardrails.allowlists["custom"]) == 1
        assert guardrails.allowlists["custom"][0].pattern == "^custom command$"


class TestRuleTemplate:
    """Test RuleTemplate model."""

    def test_create_rule_template_valid(self):
        """
        GIVEN valid RuleTemplate data
        WHEN creating model
        THEN model is created successfully
        """
        # Arrange & Act
        template = RuleTemplate(
            rule_id="aipm-master",
            template_path="templates/rules/aipm-master.j2",
            output_filename="aipm-master.mdc",
            required_vars=["project_name", "project_path"],
            optional_vars=["tech_stack"],
            priority=100,
            always_apply=True,
            description="Master AIPM rule",
        )

        # Assert
        assert template.rule_id == "aipm-master"
        assert template.template_path == "templates/rules/aipm-master.j2"
        assert template.output_filename == "aipm-master.mdc"
        assert template.required_vars == ["project_name", "project_path"]
        assert template.priority == 100
        assert template.always_apply is True

    def test_rule_template_defaults(self):
        """
        GIVEN minimal RuleTemplate data
        WHEN creating model
        THEN default values are applied
        """
        # Arrange & Act
        template = RuleTemplate(
            rule_id="test",
            template_path="test.j2",
            output_filename="test.mdc",
        )

        # Assert
        assert template.required_vars == []
        assert template.optional_vars == []
        assert template.priority == 100
        assert template.always_apply is True
        assert template.description == ""


class TestResultModels:
    """Test result models (InstallResult, VerifyResult, etc.)."""

    def test_install_result_success(self):
        """
        GIVEN successful installation
        WHEN creating InstallResult
        THEN success is True with files listed
        """
        # Arrange & Act
        result = InstallResult(
            success=True,
            installation_id=1,
            installed_files=["rules/test.mdc", ".cursorignore"],
            errors=[],
            warnings=[],
            message="Installation successful",
        )

        # Assert
        assert result.success is True
        assert result.installation_id == 1
        assert len(result.installed_files) == 2
        assert result.errors == []
        assert result.message == "Installation successful"

    def test_install_result_failure(self):
        """
        GIVEN failed installation
        WHEN creating InstallResult
        THEN success is False with errors listed
        """
        # Arrange & Act
        result = InstallResult(
            success=False,
            errors=["File not found", "Permission denied"],
            warnings=["Low disk space"],
            message="Installation failed",
        )

        # Assert
        assert result.success is False
        assert result.installation_id is None
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert result.installed_files == []

    def test_verify_result_success(self):
        """
        GIVEN successful verification
        WHEN creating VerifyResult
        THEN success is True with verified count
        """
        # Arrange & Act
        result = VerifyResult(
            success=True,
            verified_files=5,
            missing_files=[],
            modified_files=[],
            errors=[],
            message="Verification passed",
        )

        # Assert
        assert result.success is True
        assert result.verified_files == 5
        assert result.missing_files == []
        assert result.modified_files == []

    def test_verify_result_with_issues(self):
        """
        GIVEN verification with missing/modified files
        WHEN creating VerifyResult
        THEN success is False with issues listed
        """
        # Arrange & Act
        result = VerifyResult(
            success=False,
            verified_files=3,
            missing_files=["rules/deleted.mdc"],
            modified_files=["rules/edited.mdc"],
            message="Verification failed",
        )

        # Assert
        assert result.success is False
        assert len(result.missing_files) == 1
        assert len(result.modified_files) == 1

    def test_memory_sync_result(self):
        """
        GIVEN memory sync operation
        WHEN creating MemorySyncResult
        THEN sync counts are tracked
        """
        # Arrange & Act
        result = MemorySyncResult(
            success=True,
            synced_to_cursor=5,
            synced_from_cursor=0,
            skipped=2,
            errors=[],
            message="Synced 5 memories",
        )

        # Assert
        assert result.success is True
        assert result.synced_to_cursor == 5
        assert result.synced_from_cursor == 0
        assert result.skipped == 2

    def test_update_result(self):
        """
        GIVEN update operation
        WHEN creating UpdateResult
        THEN changes are tracked
        """
        # Arrange & Act
        result = UpdateResult(
            success=True,
            updated_files=["rules/test.mdc"],
            added_files=["rules/new.mdc"],
            removed_files=["rules/old.mdc"],
            errors=[],
            message="Update complete",
        )

        # Assert
        assert result.success is True
        assert len(result.updated_files) == 1
        assert len(result.added_files) == 1
        assert len(result.removed_files) == 1


class TestModelSerialization:
    """Test model serialization/deserialization."""

    def test_cursor_config_model_dump(self, temp_project_dir):
        """
        GIVEN CursorConfig model
        WHEN calling model_dump()
        THEN dict representation is returned
        """
        # Arrange
        config = CursorConfig(
            project_name="Test",
            project_path=str(temp_project_dir),
            tech_stack=["Python"],
        )

        # Act
        data = config.model_dump()

        # Assert
        assert isinstance(data, dict)
        assert data["project_name"] == "Test"
        assert data["project_path"] == str(temp_project_dir)
        assert data["tech_stack"] == ["Python"]
        assert data["rules_enabled"] is True

    def test_provider_installation_model_dump_json(self):
        """
        GIVEN ProviderInstallation model
        WHEN calling model_dump_json()
        THEN JSON string is returned
        """
        # Arrange
        installation = ProviderInstallation(
            project_id=1,
            provider_type=ProviderType.CURSOR,
            install_path="/path/.cursor",
        )

        # Act
        json_str = installation.model_dump_json()

        # Assert
        assert isinstance(json_str, str)
        assert '"project_id":1' in json_str or '"project_id": 1' in json_str
        assert '"provider_type":"cursor"' in json_str or '"provider_type": "cursor"' in json_str

    def test_cursor_memory_round_trip(self):
        """
        GIVEN CursorMemory model
        WHEN dumping to dict and reconstructing
        THEN data is preserved
        """
        # Arrange
        original = CursorMemory(
            project_id=1,
            name="test",
            description="Test memory",
            content="Content",
            file_path="test.md",
            tags=["test"],
        )

        # Act
        data = original.model_dump()
        reconstructed = CursorMemory(**data)

        # Assert
        assert reconstructed.project_id == original.project_id
        assert reconstructed.name == original.name
        assert reconstructed.description == original.description
        assert reconstructed.content == original.content
        assert reconstructed.tags == original.tags
