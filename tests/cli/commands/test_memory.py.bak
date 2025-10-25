"""
Tests for Memory CLI Commands

Tests the CLI interface in agentpm/cli/commands/memory.py

Pattern: Click testing with CliRunner
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from agentpm.cli.commands.memory import memory, generate, status, validate
from agentpm.core.database.models.memory import MemoryFile, MemoryFileType, ValidationStatus


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_console():
    """Create mock Rich console."""
    console = Mock()
    console.print = Mock()
    return console


@pytest.fixture
def mock_context(tmp_path, mock_console):
    """Create mock Click context with required objects."""
    ctx = Mock()
    ctx.obj = {
        'console': mock_console,
        'project_root': tmp_path,
        'project_id': 1,
        'db_service': Mock()
    }
    return ctx


@pytest.fixture
def sample_memory_file():
    """Create sample MemoryFile for testing."""
    return MemoryFile(
        id=1,
        project_id=1,
        session_id=100,
        file_type=MemoryFileType.RULES,
        file_path=".claude/RULES.md",
        file_hash="abc123",
        content="# RULES\n\nTest content",
        source_tables=["rules"],
        template_version="1.0.0",
        confidence_score=0.95,
        completeness_score=0.90,
        validation_status=ValidationStatus.VALIDATED,
        generated_by="memory-generator",
        generation_duration_ms=150,
        generated_at=datetime.now().isoformat(),
        validated_at=datetime.now().isoformat(),
        expires_at=(datetime.now() + timedelta(hours=24)).isoformat()
    )


class TestMemoryGroupCommand:
    """Test the memory command group."""

    def test_memory_help(self, runner):
        """Test memory --help shows available commands."""
        result = runner.invoke(memory, ['--help'])
        assert result.exit_code == 0
        assert "Manage Claude's persistent memory files" in result.output
        assert "generate" in result.output
        assert "status" in result.output
        assert "validate" in result.output


class TestGenerateCommand:
    """Test the 'apm memory generate' command."""

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.MemoryGenerator')
    def test_generate_all_success(
        self,
        mock_generator_class,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test generating all memory files successfully."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_all_memory_files.return_value = [sample_memory_file]
        mock_generator_class.return_value = mock_generator

        # Run command
        result = runner.invoke(memory, ['generate', '--all'])

        # Assertions
        assert result.exit_code == 0
        mock_generator.generate_all_memory_files.assert_called_once_with(1)
        assert "Generated Memory Files" in result.output
        assert "Memory files generated successfully" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.MemoryGenerator')
    def test_generate_specific_type_success(
        self,
        mock_generator_class,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test generating specific memory file type."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_memory_file.return_value = sample_memory_file
        mock_generator_class.return_value = mock_generator

        # Run command
        result = runner.invoke(memory, ['generate', '--type', 'rules'])

        # Assertions
        assert result.exit_code == 0
        mock_generator.generate_memory_file.assert_called_once_with(
            1,
            MemoryFileType.RULES,
            force_regenerate=False
        )
        assert "Memory File Generated" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.MemoryGenerator')
    def test_generate_with_force_flag(
        self,
        mock_generator_class,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test generating with force flag."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock generator
        mock_generator = Mock()
        mock_generator.generate_memory_file.return_value = sample_memory_file
        mock_generator_class.return_value = mock_generator

        # Run command
        result = runner.invoke(memory, ['generate', '--type', 'rules', '--force'])

        # Assertions
        assert result.exit_code == 0
        mock_generator.generate_memory_file.assert_called_once_with(
            1,
            MemoryFileType.RULES,
            force_regenerate=True
        )

    def test_generate_requires_type_or_all(self, runner):
        """Test generate command requires --type or --all."""
        with patch('agentpm.cli.commands.memory.ensure_project_root'):
            with patch('agentpm.cli.commands.memory.get_current_project_id'):
                with patch('agentpm.cli.commands.memory.get_database_service'):
                    result = runner.invoke(memory, ['generate'])

                    # Should show usage message
                    assert "Please specify --type or --all" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.MemoryGenerator')
    def test_generate_handles_errors(
        self,
        mock_generator_class,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path
    ):
        """Test generate command handles errors gracefully."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mock generator to raise error
        mock_generator = Mock()
        mock_generator.generate_all_memory_files.side_effect = Exception("Database error")
        mock_generator_class.return_value = mock_generator

        # Run command
        result = runner.invoke(memory, ['generate', '--all'])

        # Should fail with error message
        assert result.exit_code == 1
        assert "Error generating memory files" in result.output


class TestStatusCommand:
    """Test the 'apm memory status' command."""

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_status_shows_memory_files(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test status command displays memory files."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = [sample_memory_file]

        # Run command
        result = runner.invoke(memory, ['status'])

        # Assertions
        assert result.exit_code == 0
        mock_memory_methods.list_memory_files.assert_called_once_with(mock_db, project_id=1)
        assert "Memory Files Status" in result.output
        assert "rules" in result.output
        assert ".claude/RULES.md" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_status_shows_stale_warning(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test status command shows warning for stale files."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Mark file as stale
        sample_memory_file.validation_status = ValidationStatus.STALE
        mock_memory_methods.list_memory_files.return_value = [sample_memory_file]

        # Run command
        result = runner.invoke(memory, ['status'])

        # Assertions
        assert result.exit_code == 0
        assert "file(s) need regeneration" in result.output
        assert "stale" in result.output.lower()

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_status_no_files_message(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path
    ):
        """Test status command shows message when no files exist."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = []

        # Run command
        result = runner.invoke(memory, ['status'])

        # Assertions
        assert result.exit_code == 0
        assert "No memory files generated yet" in result.output
        assert "apm memory generate --all" in result.output


class TestValidateCommand:
    """Test the 'apm memory validate' command."""

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_validate_all_files(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test validating all memory files."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = [sample_memory_file]

        # Create actual file
        file_path = tmp_path / sample_memory_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_memory_file.content, encoding='utf-8')

        # Update hash to match
        import hashlib
        sample_memory_file.file_hash = hashlib.sha256(
            sample_memory_file.content.encode()
        ).hexdigest()

        # Run command
        result = runner.invoke(memory, ['validate'])

        # Assertions
        assert result.exit_code == 0
        assert "Validation Results" in result.output
        assert "All memory files are valid" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_validate_specific_type(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test validating specific memory file type."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.get_memory_file_by_type.return_value = sample_memory_file

        # Create actual file
        file_path = tmp_path / sample_memory_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_memory_file.content, encoding='utf-8')

        # Update hash to match
        import hashlib
        sample_memory_file.file_hash = hashlib.sha256(
            sample_memory_file.content.encode()
        ).hexdigest()

        # Run command
        result = runner.invoke(memory, ['validate', '--type', 'rules'])

        # Assertions
        assert result.exit_code == 0
        mock_memory_methods.get_memory_file_by_type.assert_called_once_with(
            mock_db,
            1,
            MemoryFileType.RULES
        )

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_validate_detects_missing_file(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test validate detects missing file on disk."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = [sample_memory_file]

        # Don't create file (should fail validation)

        # Run command
        result = runner.invoke(memory, ['validate'])

        # Assertions
        assert result.exit_code == 0
        assert "File missing on disk" in result.output
        assert "validation issues" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_validate_detects_hash_mismatch(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path,
        sample_memory_file
    ):
        """Test validate detects file content mismatch."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = [sample_memory_file]

        # Create file with different content
        file_path = tmp_path / sample_memory_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("Different content", encoding='utf-8')

        # Run command
        result = runner.invoke(memory, ['validate'])

        # Assertions
        assert result.exit_code == 0
        assert "Hash mismatch" in result.output
        assert "validation issues" in result.output

    @patch('agentpm.cli.commands.memory.ensure_project_root')
    @patch('agentpm.cli.commands.memory.get_current_project_id')
    @patch('agentpm.cli.commands.memory.get_database_service')
    @patch('agentpm.cli.commands.memory.memory_methods')
    def test_validate_no_files_message(
        self,
        mock_memory_methods,
        mock_get_db,
        mock_get_project_id,
        mock_ensure_root,
        runner,
        tmp_path
    ):
        """Test validate shows message when no files to validate."""
        # Setup mocks
        mock_ensure_root.return_value = tmp_path
        mock_get_project_id.return_value = 1
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_memory_methods.list_memory_files.return_value = []

        # Run command
        result = runner.invoke(memory, ['validate'])

        # Assertions
        assert result.exit_code == 0
        assert "No memory files to validate" in result.output


class TestHelperFunctions:
    """Test helper functions."""

    def test_format_file_size(self):
        """Test file size formatting."""
        from agentpm.cli.commands.memory import _format_file_size

        assert _format_file_size(100) == "100.0 B"
        assert _format_file_size(1024) == "1.0 KB"
        assert _format_file_size(1024 * 1024) == "1.0 MB"
        assert _format_file_size(1536) == "1.5 KB"

    def test_validate_memory_file_success(self, tmp_path, sample_memory_file):
        """Test validating a memory file successfully."""
        from agentpm.cli.commands.memory import _validate_memory_file
        import hashlib

        # Create file
        file_path = tmp_path / sample_memory_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_memory_file.content, encoding='utf-8')

        # Update hash to match
        sample_memory_file.file_hash = hashlib.sha256(
            sample_memory_file.content.encode()
        ).hexdigest()

        # Validate
        result = _validate_memory_file(sample_memory_file, tmp_path)

        assert result['type'] == 'rules'
        assert result['file_exists'] is True
        assert result['hash_match'] is True
        assert result['is_current'] is True
        assert len(result['issues']) == 0

    def test_validate_memory_file_missing(self, tmp_path, sample_memory_file):
        """Test validating a missing memory file."""
        from agentpm.cli.commands.memory import _validate_memory_file

        # Don't create file

        # Validate
        result = _validate_memory_file(sample_memory_file, tmp_path)

        assert result['file_exists'] is False
        assert "File missing on disk" in result['issues']

    def test_validate_memory_file_stale(self, tmp_path, sample_memory_file):
        """Test validating a stale memory file."""
        from agentpm.cli.commands.memory import _validate_memory_file
        import hashlib

        # Create file
        file_path = tmp_path / sample_memory_file.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_memory_file.content, encoding='utf-8')

        # Update hash to match
        sample_memory_file.file_hash = hashlib.sha256(
            sample_memory_file.content.encode()
        ).hexdigest()

        # Mark as stale
        sample_memory_file.validation_status = ValidationStatus.STALE

        # Validate
        result = _validate_memory_file(sample_memory_file, tmp_path)

        assert result['is_current'] is False
        assert "Marked as stale" in result['issues']
