"""
pytest configuration for documentation tests.

This module configures pytest for testing markdown documentation:
- Code examples validation
- Command syntax verification
- State machine consistency checks
"""

import subprocess
from pathlib import Path
from typing import Generator, List

import pytest


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ENUM_FILE = PROJECT_ROOT / "agentpm" / "core" / "database" / "enums" / "status.py"


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Provide project root path.

    Returns:
        Path to project root directory
    """
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def docs_dir() -> Path:
    """
    Provide docs directory path.

    Returns:
        Path to documentation directory
    """
    return DOCS_DIR


@pytest.fixture(scope="session")
def enum_file() -> Path:
    """
    Provide enum file path.

    Returns:
        Path to status.py enum definitions
    """
    return ENUM_FILE


@pytest.fixture
def markdown_files(docs_dir: Path) -> Generator[List[Path], None, None]:
    """
    Collect all markdown files in docs directory.

    Args:
        docs_dir: Documentation directory path

    Yields:
        List of markdown file paths
    """
    files = list(docs_dir.rglob("*.md"))
    yield files


@pytest.fixture
def valid_apm_commands() -> List[str]:
    """
    Provide list of valid apm CLI commands.

    Returns:
        List of valid command names
    """
    # This would ideally be generated from the CLI itself
    # For now, we'll maintain a curated list
    return [
        "status",
        "init",
        "work-item",
        "task",
        "rules",
        "agents",
        "context",
        "session",
        "document",
        "summary",
        "hooks",
    ]


@pytest.fixture
def valid_work_item_commands() -> List[str]:
    """
    Provide list of valid work-item subcommands.

    Returns:
        List of valid subcommand names
    """
    return [
        "create",
        "show",
        "list",
        "update",
        "next",
        "validate",
        "accept",
        "start",
        "submit-review",
        "approve",
        "phase-status",
        "phase-validate",
    ]


@pytest.fixture
def valid_task_commands() -> List[str]:
    """
    Provide list of valid task subcommands.

    Returns:
        List of valid subcommand names
    """
    return [
        "create",
        "show",
        "list",
        "update",
        "next",
        "validate",
        "accept",
        "start",
        "submit-review",
        "approve",
    ]


def extract_bash_commands(markdown_content: str) -> List[str]:
    """
    Extract bash commands from markdown code blocks.

    Args:
        markdown_content: Raw markdown text

    Returns:
        List of bash commands
    """
    commands = []
    in_bash_block = False
    current_block = []

    for line in markdown_content.split('\n'):
        if line.strip().startswith('```bash'):
            in_bash_block = True
            current_block = []
        elif line.strip().startswith('```') and in_bash_block:
            in_bash_block = False
            if current_block:
                commands.extend(current_block)
        elif in_bash_block:
            # Skip comments and empty lines
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                commands.append(stripped)

    return commands


def is_apm_command(command: str) -> bool:
    """
    Check if command is an apm CLI command.

    Args:
        command: Command string

    Returns:
        True if command starts with 'apm'
    """
    return command.strip().startswith('apm ')


@pytest.fixture
def extract_bash_commands_func():
    """Provide bash command extraction function as fixture."""
    return extract_bash_commands


@pytest.fixture
def is_apm_command_func():
    """Provide apm command detection function as fixture."""
    return is_apm_command


def pytest_configure(config):
    """
    Configure pytest with custom markers.

    Args:
        config: pytest configuration object
    """
    config.addinivalue_line(
        "markers", "docs: mark test as documentation test"
    )
    config.addinivalue_line(
        "markers", "state_machine: mark test as state machine validation test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.

    Args:
        config: pytest configuration
        items: collected test items
    """
    for item in items:
        # Add 'docs' marker to all tests in tests/docs/
        if "tests/docs" in str(item.fspath):
            item.add_marker(pytest.mark.docs)

        # Add 'state_machine' marker to state machine tests
        if "state_machine" in item.nodeid:
            item.add_marker(pytest.mark.state_machine)
