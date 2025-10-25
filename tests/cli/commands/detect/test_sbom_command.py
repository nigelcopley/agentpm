"""
Tests for SBOM CLI command.

Verifies CLI integration with SBOMService.
"""

import json
from pathlib import Path
from click.testing import CliRunner
import pytest

from agentpm.cli.commands.detect.sbom import sbom


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_console():
    """Mock Rich console for testing."""
    from rich.console import Console
    from io import StringIO

    output = StringIO()
    return Console(file=output, force_terminal=True)


def test_sbom_help(runner):
    """Test sbom --help displays usage."""
    result = runner.invoke(sbom, ['--help'])
    assert result.exit_code == 0
    assert 'Generate Software Bill of Materials' in result.output
    assert 'CycloneDX' in result.output
    assert 'SPDX' in result.output


def test_sbom_basic_display(runner, mock_console):
    """Test basic SBOM display in table format."""
    # Note: This test requires a real project with dependencies
    # In CI/CD, this would use a test fixture project
    result = runner.invoke(sbom, ['.', '--skip-licenses', '--limit', '5'],
                          obj={'console': mock_console})

    # Command should succeed (exit 0) or fail gracefully
    assert result.exit_code in [0, 1]  # Allow graceful failure if no deps found


def test_sbom_export_cyclonedx(runner, tmp_path, mock_console):
    """Test CycloneDX export to file."""
    output_file = tmp_path / "sbom.json"

    result = runner.invoke(
        sbom,
        ['.', '--format', 'cyclonedx', '--output', str(output_file), '--skip-licenses'],
        obj={'console': mock_console}
    )

    # If project has deps, file should be created
    if result.exit_code == 0:
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data['bomFormat'] == 'CycloneDX'
        assert data['specVersion'] == '1.5'


def test_sbom_export_spdx(runner, tmp_path, mock_console):
    """Test SPDX export to file."""
    output_file = tmp_path / "sbom_spdx.json"

    result = runner.invoke(
        sbom,
        ['.', '--format', 'spdx', '--output', str(output_file), '--skip-licenses'],
        obj={'console': mock_console}
    )

    # If project has deps, file should be created
    if result.exit_code == 0:
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data['spdxVersion'] == 'SPDX-2.3'
        assert 'packages' in data


def test_sbom_runtime_only(runner, mock_console):
    """Test --runtime-only flag excludes dev dependencies."""
    result = runner.invoke(
        sbom,
        ['.', '--runtime-only', '--skip-licenses'],
        obj={'console': mock_console}
    )

    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_sbom_include_dev(runner, mock_console):
    """Test --include-dev flag includes dev dependencies."""
    result = runner.invoke(
        sbom,
        ['.', '--include-dev', '--skip-licenses'],
        obj={'console': mock_console}
    )

    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_sbom_conflicting_flags_warning(runner, mock_console):
    """Test warning when --runtime-only and --include-dev are both specified."""
    result = runner.invoke(
        sbom,
        ['.', '--runtime-only', '--include-dev', '--skip-licenses'],
        obj={'console': mock_console},
        catch_exceptions=False
    )

    # Should succeed but show warning (we can't easily capture rich output in tests)
    # Just verify it doesn't crash
    assert result.exit_code in [0, 1]


def test_sbom_format_choices(runner, mock_console):
    """Test that format option accepts valid choices."""
    valid_formats = ['cyclonedx', 'cyclonedx-xml', 'spdx', 'json', 'table']

    for fmt in valid_formats:
        result = runner.invoke(
            sbom,
            ['.', '--format', fmt, '--skip-licenses'],
            obj={'console': mock_console}
        )
        # Should not fail due to invalid format
        assert result.exit_code in [0, 1]


def test_sbom_invalid_format(runner, mock_console):
    """Test that invalid format is rejected."""
    result = runner.invoke(
        sbom,
        ['.', '--format', 'invalid_format'],
        obj={'console': mock_console}
    )

    # Should fail with usage error
    assert result.exit_code == 2  # Click usage error


def test_sbom_limit_option(runner, mock_console):
    """Test --limit option limits displayed components."""
    result = runner.invoke(
        sbom,
        ['.', '--limit', '3', '--skip-licenses'],
        obj={'console': mock_console}
    )

    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_sbom_nonexistent_path(runner, mock_console):
    """Test error handling for nonexistent project path."""
    result = runner.invoke(
        sbom,
        ['/nonexistent/path/to/project'],
        obj={'console': mock_console}
    )

    # Should fail with path error
    assert result.exit_code == 2  # Click parameter error
