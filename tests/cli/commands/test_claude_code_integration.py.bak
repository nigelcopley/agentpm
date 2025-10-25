"""
Tests for Claude Code Integration CLI Commands

Tests the user-facing integration management commands in
agentpm/cli/commands/claude_code.py (init, status, sync, hooks, checkpoint)

Pattern: Click testing with CliRunner
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from agentpm.cli.commands.claude_code import (
    claude_code,
    init,
    status,
    sync,
    hooks,
    checkpoint
)


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_console():
    """Create mock Rich console that works with CLI commands."""
    from rich.console import Console
    # Use a real Console but capture output
    console = Console(file=None, force_terminal=False)
    return console


@pytest.fixture
def ctx_obj(tmp_path, mock_console):
    """Create mock Click context object with required fields."""
    return {
        'console': mock_console,
        'project_root': tmp_path,
        'project_id': 1,
        'db_service': Mock()
    }


@pytest.fixture
def initialized_claude_dir(tmp_path):
    """Create initialized .claude directory structure."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Create subdirectories
    (claude_dir / "plugins").mkdir()
    (claude_dir / "memory").mkdir()
    (claude_dir / "checkpoints").mkdir()
    (claude_dir / "settings").mkdir()

    # Create sample memory files
    (claude_dir / "memory" / "project_context.md").write_text("# Project Context\n\nTest project")
    (claude_dir / "memory" / "recent_work.md").write_text("# Recent Work\n\nNo work yet")

    # Create sample settings
    settings = {
        "plugin_enabled": True,
        "verbose_logging": False,
        "hooks": {
            "enabled": {
                "session_start": True,
                "session_end": True,
                "prompt_submit": False
            }
        }
    }
    (claude_dir / "settings" / "integration.json").write_text(json.dumps(settings, indent=2))

    return claude_dir


class TestClaudeCodeGroupCommand:
    """Test the claude-code command group."""

    def test_claude_code_help(self, runner):
        """Test claude-code --help shows available commands."""
        result = runner.invoke(claude_code, ['--help'])
        assert result.exit_code == 0
        assert "Claude Code integration management commands" in result.output


class TestInitCommand:
    """Test the 'apm claude-code init' command."""

    def test_init_creates_directory_structure(self, runner, tmp_path, mock_console):
        """Test init creates .claude directory and subdirectories."""
        result = runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0, f"Command failed: {result.output}\n{result.exception}"

        claude_dir = tmp_path / ".claude"
        assert claude_dir.exists()
        assert (claude_dir / "plugins").exists()
        assert (claude_dir / "memory").exists()
        assert (claude_dir / "checkpoints").exists()
        assert (claude_dir / "settings").exists()

        assert "Initialization Complete" in result.output

    def test_init_creates_memory_files(self, runner, tmp_path, mock_console):
        """Test init creates initial memory files."""
        result = runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0, f"Command failed: {result.output}\n{result.exception}"

        memory_dir = tmp_path / ".claude" / "memory"
        assert (memory_dir / "project_context.md").exists()
        assert (memory_dir / "recent_work.md").exists()

        context_content = (memory_dir / "project_context.md").read_text()
        assert "Project Context" in context_content

    def test_init_creates_default_settings(self, runner, tmp_path, mock_console):
        """Test init creates default settings file."""
        result = runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0, f"Command failed: {result.output}\n{result.exception}"

        settings_file = tmp_path / ".claude" / "settings" / "integration.json"
        assert settings_file.exists()

        settings = json.loads(settings_file.read_text())
        assert settings["plugin_enabled"] is True
        assert "hooks" in settings
        assert "memory" in settings

    def test_init_creates_readme(self, runner, tmp_path, mock_console):
        """Test init creates README.md."""
        result = runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0, f"Command failed: {result.output}\n{result.exception}"

        readme = tmp_path / ".claude" / "README.md"
        assert readme.exists()

        readme_content = readme.read_text()
        assert "Claude Code Integration" in readme_content
        assert "Directory Structure" in readme_content
        assert "Next Steps" in readme_content

    def test_init_warns_if_already_initialized(self, runner, tmp_path, mock_console):
        """Test init warns when .claude already exists."""
        # First init
        runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        # Second init without --force
        result = runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0
        assert "already initialized" in result.output

    def test_init_force_reinitializes(self, runner, tmp_path, mock_console):
        """Test init --force reinitializes existing integration."""
        # First init
        runner.invoke(
            claude_code,
            ['init'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        # Modify a file
        memory_file = tmp_path / ".claude" / "memory" / "project_context.md"
        memory_file.write_text("Modified content")

        # Reinitialize with --force
        result = runner.invoke(
            claude_code,
            ['init', '--force'],
            obj={'console': mock_console, 'project_root': tmp_path}
        )

        assert result.exit_code == 0
        assert "Initialization Complete" in result.output

        # Check file was recreated with default content
        new_content = memory_file.read_text()
        assert "APM (Agent Project Manager) Project" in new_content


class TestStatusCommand:
    """Test the 'apm claude-code status' command."""

    def test_status_not_initialized(self, runner, tmp_path, mock_console):
        """Test status when integration not initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            result = runner.invoke(claude_code, ['status'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "not initialized" in result.output

    def test_status_shows_component_status(self, runner, tmp_path, initialized_claude_dir):
        """Test status displays component status."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            # Move initialized dir to current location
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(claude_code, ['status'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "Components" in result.output
            assert "Plugins" in result.output
            assert "Memory" in result.output
            assert "Checkpoints" in result.output
            assert "Settings" in result.output

    def test_status_shows_active_hooks(self, runner, tmp_path, initialized_claude_dir):
        """Test status displays active hooks."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(claude_code, ['status'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "Active Hooks" in result.output
            assert "session_start" in result.output
            assert "session_end" in result.output

    def test_status_shows_checkpoints(self, runner, tmp_path, initialized_claude_dir):
        """Test status displays recent checkpoints."""
        # Create sample checkpoints
        checkpoints_dir = initialized_claude_dir / "checkpoints"

        for i in range(3):
            checkpoint_data = {
                "name": f"checkpoint_{i}",
                "timestamp": datetime.now().isoformat(),
                "type": "manual"
            }
            (checkpoints_dir / f"checkpoint_{i}.json").write_text(json.dumps(checkpoint_data))

        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(claude_code, ['status'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "Recent Checkpoints" in result.output
            assert "checkpoint_0" in result.output


class TestSyncCommand:
    """Test the 'apm claude-code sync' command."""

    def test_sync_not_initialized(self, runner, tmp_path, mock_console):
        """Test sync when integration not initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            result = runner.invoke(claude_code, ['sync'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "not initialized" in result.output

    @patch('agentpm.cli.commands.claude_code.get_current_project_id')
    @patch('agentpm.cli.commands.claude_code.wi_methods')
    @patch('agentpm.cli.commands.claude_code.task_methods')
    def test_sync_generates_memory_files(
        self,
        mock_task_methods,
        mock_wi_methods,
        mock_get_project_id,
        runner,
        tmp_path,
        initialized_claude_dir
    ):
        """Test sync generates memory files from database."""
        # Setup mocks
        mock_get_project_id.return_value = 1

        mock_wi = Mock()
        mock_wi.id = 1
        mock_wi.name = "Test Work Item"
        mock_wi.type.value = "feature"
        mock_wi.status.value = "active"
        mock_wi.phase.value = "D1_discovery"
        mock_wi.business_context = "Test business context"

        mock_wi_methods.list_work_items.return_value = [mock_wi]

        mock_task = Mock()
        mock_task.id = 1
        mock_task.name = "Test Task"
        mock_task.status.value = "ready"
        mock_task.created_at = datetime.now()
        mock_task.updated_at = datetime.now()

        mock_task_methods.list_tasks.return_value = [mock_task]

        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            mock_db = Mock()
            result = runner.invoke(
                claude_code,
                ['sync'],
                obj={'console': mock_console, 'db_service': mock_db}
            )

            assert result.exit_code == 0
            assert "Sync Complete" in result.output

            # Check memory files were updated
            memory_dir = Path(fs_path) / ".claude" / "memory"
            context_file = memory_dir / "project_context.md"
            assert context_file.exists()

            context_content = context_file.read_text()
            assert "Test Work Item" in context_content
            assert "feature" in context_content

    def test_sync_without_database(self, runner, tmp_path, initialized_claude_dir):
        """Test sync updates timestamps when no database."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(
                claude_code,
                ['sync'],
                obj={'console': mock_console, 'db_service': None}
            )

            assert result.exit_code == 0
            assert "Sync Complete" in result.output


class TestHooksCommand:
    """Test the 'apm claude-code hooks' command."""

    def test_hooks_not_initialized(self, runner, tmp_path, mock_console):
        """Test hooks when integration not initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            result = runner.invoke(
                claude_code,
                ['hooks', '--enable', 'test_hook'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Settings file not found" in result.output

    def test_hooks_enable(self, runner, tmp_path, initialized_claude_dir):
        """Test enabling a hook."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(
                claude_code,
                ['hooks', '--enable', 'new_hook'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Enabled: new_hook" in result.output

            # Verify settings file updated
            settings_file = Path(fs_path) / ".claude" / "settings" / "integration.json"
            settings = json.loads(settings_file.read_text())
            assert settings["hooks"]["enabled"]["new_hook"] is True

    def test_hooks_disable(self, runner, tmp_path, initialized_claude_dir):
        """Test disabling a hook."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(
                claude_code,
                ['hooks', '--disable', 'session_start'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Disabled: session_start" in result.output

            # Verify settings file updated
            settings_file = Path(fs_path) / ".claude" / "settings" / "integration.json"
            settings = json.loads(settings_file.read_text())
            assert settings["hooks"]["enabled"]["session_start"] is False

    def test_hooks_multiple_changes(self, runner, tmp_path, initialized_claude_dir):
        """Test enabling and disabling multiple hooks."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(
                claude_code,
                [
                    'hooks',
                    '--enable', 'hook_a',
                    '--enable', 'hook_b',
                    '--disable', 'session_end'
                ],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Enabled: hook_a" in result.output
            assert "Enabled: hook_b" in result.output
            assert "Disabled: session_end" in result.output

    def test_hooks_shows_current_status(self, runner, tmp_path, initialized_claude_dir):
        """Test hooks displays current hook status."""
        with runner.isolated_filesystem(temp_dir=tmp_path.parent) as fs_path:
            import shutil
            shutil.move(str(initialized_claude_dir), str(Path(fs_path) / ".claude"))

            result = runner.invoke(claude_code, ['hooks'], obj={'console': mock_console})

            assert result.exit_code == 0
            assert "Current Hook Status" in result.output


class TestCheckpointCommand:
    """Test the 'apm claude-code checkpoint' command."""

    def test_checkpoint_create_requires_name(self, runner, tmp_path, mock_console):
        """Test checkpoint create requires --name option."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            result = runner.invoke(
                claude_code,
                ['checkpoint', 'create'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 1
            assert "Checkpoint name required" in result.output

    def test_checkpoint_create_success(self, runner, tmp_path, mock_console):
        """Test creating a checkpoint."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            result = runner.invoke(
                claude_code,
                ['checkpoint', 'create', '--name', 'test_checkpoint'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Checkpoint 'test_checkpoint' created" in result.output

            # Verify checkpoint file created
            checkpoint_file = Path(fs_path) / ".claude" / "checkpoints" / "test_checkpoint.json"
            assert checkpoint_file.exists()

            checkpoint_data = json.loads(checkpoint_file.read_text())
            assert checkpoint_data["name"] == "test_checkpoint"
            assert checkpoint_data["type"] == "manual"
            assert "timestamp" in checkpoint_data

    def test_checkpoint_list_empty(self, runner, tmp_path, mock_console):
        """Test listing checkpoints when none exist."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            # Create empty checkpoints dir
            (Path(fs_path) / ".claude" / "checkpoints").mkdir(parents=True)

            result = runner.invoke(
                claude_code,
                ['checkpoint', 'list'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "No checkpoints found" in result.output

    def test_checkpoint_list_displays_checkpoints(self, runner, tmp_path, mock_console):
        """Test listing checkpoints displays all checkpoints."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            checkpoints_dir = Path(fs_path) / ".claude" / "checkpoints"
            checkpoints_dir.mkdir(parents=True)

            # Create sample checkpoints
            for i in range(3):
                checkpoint_data = {
                    "name": f"checkpoint_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "type": "manual"
                }
                (checkpoints_dir / f"checkpoint_{i}.json").write_text(
                    json.dumps(checkpoint_data)
                )

            result = runner.invoke(
                claude_code,
                ['checkpoint', 'list'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Session Checkpoints" in result.output
            assert "checkpoint_0" in result.output
            assert "checkpoint_1" in result.output
            assert "checkpoint_2" in result.output

    def test_checkpoint_delete_success(self, runner, tmp_path, mock_console):
        """Test deleting a checkpoint."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            checkpoints_dir = Path(fs_path) / ".claude" / "checkpoints"
            checkpoints_dir.mkdir(parents=True)

            # Create checkpoint to delete
            checkpoint_data = {
                "name": "to_delete",
                "timestamp": datetime.now().isoformat(),
                "type": "manual"
            }
            checkpoint_file = checkpoints_dir / "to_delete.json"
            checkpoint_file.write_text(json.dumps(checkpoint_data))

            result = runner.invoke(
                claude_code,
                ['checkpoint', 'delete', '--name', 'to_delete'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Checkpoint 'to_delete' deleted" in result.output
            assert not checkpoint_file.exists()

    def test_checkpoint_delete_not_found(self, runner, tmp_path, mock_console):
        """Test deleting non-existent checkpoint."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            checkpoints_dir = Path(fs_path) / ".claude" / "checkpoints"
            checkpoints_dir.mkdir(parents=True)

            result = runner.invoke(
                claude_code,
                ['checkpoint', 'delete', '--name', 'nonexistent'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 1
            assert "not found" in result.output

    def test_checkpoint_restore_shows_details(self, runner, tmp_path, mock_console):
        """Test restoring a checkpoint shows details."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            checkpoints_dir = Path(fs_path) / ".claude" / "checkpoints"
            checkpoints_dir.mkdir(parents=True)

            # Create checkpoint
            checkpoint_data = {
                "name": "to_restore",
                "timestamp": datetime.now().isoformat(),
                "type": "manual"
            }
            (checkpoints_dir / "to_restore.json").write_text(json.dumps(checkpoint_data))

            result = runner.invoke(
                claude_code,
                ['checkpoint', 'restore', '--name', 'to_restore'],
                obj={'console': mock_console}
            )

            assert result.exit_code == 0
            assert "Checkpoint Details" in result.output
            assert "to_restore" in result.output
            assert "Restore functionality not yet implemented" in result.output


# Integration Tests

class TestClaudeCodeIntegrationFlow:
    """Test complete Claude Code integration workflow."""

    def test_full_initialization_workflow(self, runner, tmp_path, mock_console):
        """Test full init -> status -> sync -> hooks -> checkpoint workflow."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            console = Mock()

            # Step 1: Initialize
            result = runner.invoke(claude_code, ['init'], obj={'console': console})
            assert result.exit_code == 0
            assert (Path(fs_path) / ".claude").exists()

            # Step 2: Check status
            result = runner.invoke(claude_code, ['status'], obj={'console': console})
            assert result.exit_code == 0
            assert "Initialized" in result.output

            # Step 3: Sync (without database)
            result = runner.invoke(
                claude_code,
                ['sync'],
                obj={'console': console, 'db_service': None}
            )
            assert result.exit_code == 0

            # Step 4: Enable hooks
            result = runner.invoke(
                claude_code,
                ['hooks', '--enable', 'custom_hook'],
                obj={'console': console}
            )
            assert result.exit_code == 0

            # Step 5: Create checkpoint
            result = runner.invoke(
                claude_code,
                ['checkpoint', 'create', '--name', 'initial'],
                obj={'console': console}
            )
            assert result.exit_code == 0

            # Verify all components exist
            claude_dir = Path(fs_path) / ".claude"
            assert (claude_dir / "memory").exists()
            assert (claude_dir / "checkpoints" / "initial.json").exists()

            settings_file = claude_dir / "settings" / "integration.json"
            settings = json.loads(settings_file.read_text())
            assert settings["hooks"]["enabled"]["custom_hook"] is True

    def test_error_handling_without_init(self, runner, tmp_path, mock_console):
        """Test commands handle gracefully when not initialized."""
        with runner.isolated_filesystem(temp_dir=tmp_path) as fs_path:
            console = Mock()

            # Status without init
            result = runner.invoke(claude_code, ['status'], obj={'console': console})
            assert result.exit_code == 0
            assert "not initialized" in result.output

            # Sync without init
            result = runner.invoke(claude_code, ['sync'], obj={'console': console})
            assert result.exit_code == 0
            assert "not initialized" in result.output

            # Hooks without init
            result = runner.invoke(
                claude_code,
                ['hooks', '--enable', 'test'],
                obj={'console': console}
            )
            assert result.exit_code == 0
            assert "Settings file not found" in result.output
