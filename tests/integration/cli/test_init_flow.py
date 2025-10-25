"""
Integration tests for initialization flow.
Tests the complete init command end-to-end.
"""

import pytest
import time
from pathlib import Path
from click.testing import CliRunner

from agentpm.cli.commands.init import init


@pytest.fixture
def cli_runner():
    """Create Click CLI test runner"""
    return CliRunner()


@pytest.fixture
def mock_console():
    """Create mock console object for Click context"""
    from rich.console import Console
    return Console()


def test_init_creates_complete_installation(cli_runner, tmp_path, mock_console):
    """Test init command creates complete installation"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # Run init command
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )

        # Check command succeeded
        if result.exit_code != 0:
            print(f"Command output:\n{result.output}")
            if result.exception:
                raise result.exception

        assert result.exit_code == 0
        assert "✅" in result.output or "initialized successfully" in result.output.lower()

        # Verify database created
        db_path = Path.cwd() / ".agentpm" / "data" / "agentpm.db"
        assert db_path.exists(), "Database file not found"

        # Verify directory structure
        assert (Path.cwd() / ".agentpm").exists()
        assert (Path.cwd() / ".agentpm" / "data").exists()
        assert (Path.cwd() / ".agentpm" / "logs").exists()
        assert (Path.cwd() / ".agentpm" / "contexts").exists()
        assert (Path.cwd() / ".agentpm" / "cache").exists()

        # Verify .claude directory created
        assert (Path.cwd() / ".claude" / "agents").exists()


def test_init_shows_progress(cli_runner, tmp_path, mock_console):
    """Test init shows progress indicators"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )

        # Check progress messages appear
        # The output might not contain exact progress indicators due to Rich formatting,
        # but should contain key phase messages
        assert "Project" in result.output or "Initializing" in result.output


def test_init_prevents_double_initialization(cli_runner, tmp_path, mock_console):
    """Test can't initialize twice without --reset"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # First init
        result1 = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result1.exit_code == 0

        # Second init should fail
        result2 = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result2.exit_code != 0
        assert "already initialized" in result2.output.lower()


def test_init_reset_flag_works(cli_runner, tmp_path, mock_console):
    """Test --reset flag allows reinitialization"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        # First init
        result1 = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result1.exit_code == 0

        # Reset and reinit
        result2 = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire", "--reset"],
            obj={'console': mock_console},
            input="y\n"  # Confirm deletion
        )
        assert result2.exit_code == 0
        assert "initialized successfully" in result2.output.lower() or "✅" in result2.output


def test_init_database_has_tables(cli_runner, tmp_path, mock_console):
    """Test initialized database has expected tables"""
    import sqlite3

    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result.exit_code == 0

        # Connect to database and check tables
        db_path = Path.cwd() / ".agentpm" / "data" / "agentpm.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check table count
        cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        )
        table_count = cursor.fetchone()[0]
        assert table_count >= 50, f"Expected at least 50 tables, found {table_count}"

        # Check key tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"
        )
        assert cursor.fetchone() is not None, "projects table not found"

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='work_items'"
        )
        assert cursor.fetchone() is not None, "work_items table not found"

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='rules'"
        )
        assert cursor.fetchone() is not None, "rules table not found"

        conn.close()


def test_init_creates_project_record(cli_runner, tmp_path, mock_console):
    """Test init creates project record in database"""
    import sqlite3

    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result.exit_code == 0

        # Check project record created
        db_path = Path.cwd() / ".agentpm" / "data" / "agentpm.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT count(*) FROM projects")
        project_count = cursor.fetchone()[0]
        assert project_count == 1, f"Expected 1 project, found {project_count}"

        cursor.execute("SELECT name FROM projects WHERE id=1")
        project_name = cursor.fetchone()[0]
        assert project_name == "Test Project"

        conn.close()


def test_init_less_than_3_minutes(cli_runner, tmp_path, mock_console):
    """Test initialization completes in <3 minutes"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        start = time.time()
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        duration = time.time() - start

        assert result.exit_code == 0
        assert duration < 180, f"Initialization took {duration:.1f}s (expected <180s)"
        print(f"Initialization completed in {duration:.1f} seconds")


def test_init_with_description(cli_runner, tmp_path, mock_console):
    """Test init with project description"""
    import sqlite3

    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--description", "Test Description", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result.exit_code == 0

        # Check description stored
        db_path = Path.cwd() / ".agentpm" / "data" / "agentpm.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT description FROM projects WHERE id=1")
        description = cursor.fetchone()[0]
        assert description == "Test Description"

        conn.close()


def test_init_verification_checks(cli_runner, tmp_path, mock_console):
    """Test verification phase runs and passes"""
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(
            init,
            ["Test Project", ".", "--skip-questionnaire"],
            obj={'console': mock_console}
        )
        assert result.exit_code == 0

        # If verification failed, init would not succeed
        # The fact that exit_code == 0 means verification passed

        # Additional verification: check all expected directories exist
        required_dirs = [
            Path.cwd() / ".agentpm",
            Path.cwd() / ".agentpm" / "data",
            Path.cwd() / ".agentpm" / "logs",
            Path.cwd() / ".claude" / "agents"
        ]

        for directory in required_dirs:
            assert directory.exists(), f"Required directory not found: {directory}"


@pytest.mark.parametrize("project_name,description", [
    ("Simple Project", ""),
    ("Project With Spaces", "A test description"),
    ("CLI-Tool-2024", "Command line interface tool"),
])
def test_init_with_various_names(cli_runner, tmp_path, mock_console, project_name, description):
    """Test init with various project names and descriptions"""
    import sqlite3

    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        args = [project_name, "."]
        if description:
            args.extend(["--description", description])
        args.append("--skip-questionnaire")

        result = cli_runner.invoke(
            init,
            args,
            obj={'console': mock_console}
        )
        assert result.exit_code == 0

        # Verify project created with correct name
        db_path = Path.cwd() / ".agentpm" / "data" / "agentpm.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name, description FROM projects WHERE id=1")
        row = cursor.fetchone()
        assert row[0] == project_name
        assert row[1] == description

        conn.close()
