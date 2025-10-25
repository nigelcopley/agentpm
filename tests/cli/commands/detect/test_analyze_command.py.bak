"""
Integration tests for 'apm detect analyze' CLI command.

Tests comprehensive static analysis CLI integration including:
- Basic analysis execution
- Multiple output formats (table, JSON, YAML, markdown)
- File export functionality
- Threshold configuration
- Verbose and summary modes
- Error handling
"""

import json
import yaml
from pathlib import Path
import pytest
from click.testing import CliRunner
from rich.console import Console
from io import StringIO

from agentpm.cli.main import cli


@pytest.fixture
def cli_runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_console():
    """Mock Rich console for testing."""
    output = StringIO()
    return Console(file=output, force_terminal=True, width=120)


@pytest.fixture
def sample_project(tmp_path):
    """
    Create sample Python project for analysis.

    Creates realistic project structure with varying complexity:
    - Simple module (low complexity)
    - Complex module (high complexity)
    - Medium module (acceptable complexity)
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Simple module (low complexity)
    simple_file = project_dir / "simple.py"
    simple_file.write_text('''
"""Simple module with low complexity."""

def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract two numbers."""
    return a - b


class Calculator:
    """Basic calculator."""

    def multiply(self, a, b):
        """Multiply numbers."""
        return a * b
''')

    # Complex module (high complexity)
    complex_file = project_dir / "complex.py"
    complex_file.write_text('''
"""Complex module with high cyclomatic complexity."""

def complex_function(x, y, z, w):
    """Function with high complexity."""
    if x > 0:
        if y > 0:
            if z > 0:
                if w > 0:
                    return x + y + z + w
                else:
                    return x + y + z
            else:
                if w > 0:
                    return x + y + w
                else:
                    return x + y
        else:
            if z > 0:
                if w > 0:
                    return x + z + w
                else:
                    return x + z
            else:
                return x
    else:
        if y > 0:
            if z > 0:
                return y + z
            else:
                return y
        else:
            return 0


class ComplexClass:
    """Class with multiple complex methods."""

    def method1(self, a, b, c):
        """Complex method 1."""
        if a:
            if b:
                if c:
                    return a + b + c
                return a + b
            return a
        return 0

    def method2(self, x):
        """Complex method 2."""
        result = 0
        for i in range(x):
            if i % 2 == 0:
                if i % 3 == 0:
                    result += i
                else:
                    result -= i
            else:
                result += i * 2
        return result
''')

    # Medium complexity module
    medium_file = project_dir / "medium.py"
    medium_file.write_text('''
"""Medium complexity module."""

def process_data(data):
    """Process input data."""
    if not data:
        return None

    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(item)

    return result


class DataProcessor:
    """Data processing class."""

    def __init__(self):
        self.data = []

    def add(self, item):
        """Add item to data."""
        if item:
            self.data.append(item)

    def process(self):
        """Process stored data."""
        return [x * 2 for x in self.data if x > 0]
''')

    return project_dir


# ===== Basic Analysis Tests =====

def test_analyze_basic_execution(cli_runner, sample_project, mock_console):
    """Test basic analyze command execution."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert 'Files Analyzed' in result.output or 'files_analyzed' in result.output.lower()


def test_analyze_current_directory(cli_runner, sample_project, mock_console):
    """Test analyzing current directory (default)."""
    # Use isolated filesystem
    with cli_runner.isolated_filesystem(temp_dir=sample_project.parent):
        # Change to sample project directory
        import os
        os.chdir(sample_project)

        result = cli_runner.invoke(
            cli,
            ['detect', 'analyze'],
            obj={'console': mock_console}
        )

        assert result.exit_code == 0


def test_analyze_summary_displayed(cli_runner, sample_project, mock_console):
    """Test that analysis summary is displayed."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Check for key metrics in output
    output_lower = result.output.lower()
    assert any(x in output_lower for x in ['files analyzed', 'total lines', 'quality'])


# ===== Output Format Tests =====

def test_analyze_json_format(cli_runner, sample_project, mock_console):
    """Test JSON output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)

    # Verify JSON structure
    assert 'summary' in data
    assert 'files' in data
    assert 'quality_issues' in data

    # Verify summary fields
    assert 'files_analyzed' in data['summary']
    assert 'total_lines' in data['summary']
    assert 'quality_score' in data['summary']

    # Should have analyzed our 3 files
    assert data['summary']['files_analyzed'] >= 3


def test_analyze_yaml_format(cli_runner, sample_project, mock_console):
    """Test YAML output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'yaml'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0

    # Parse YAML output
    data = yaml.safe_load(result.output)

    # Verify YAML structure
    assert 'summary' in data
    assert 'files' in data
    assert 'quality_issues' in data


def test_analyze_markdown_format(cli_runner, sample_project, mock_console):
    """Test markdown output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'markdown'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0

    # Check for markdown headers
    assert '# Static Analysis Report' in result.output
    assert '## Summary' in result.output
    assert '## Metrics' in result.output


def test_analyze_table_format(cli_runner, sample_project, mock_console):
    """Test table output format (default)."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'table'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Table format uses Rich rendering, just check it doesn't error


# ===== File Export Tests =====

def test_analyze_export_json(cli_runner, sample_project, tmp_path, mock_console):
    """Test exporting JSON to file."""
    output_file = tmp_path / "analysis.json"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--format', 'json',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file contents
    data = json.loads(output_file.read_text())
    assert 'summary' in data
    assert 'files' in data


def test_analyze_export_yaml(cli_runner, sample_project, tmp_path, mock_console):
    """Test exporting YAML to file."""
    output_file = tmp_path / "analysis.yaml"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--format', 'yaml',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file contents
    data = yaml.safe_load(output_file.read_text())
    assert 'summary' in data


def test_analyze_export_markdown(cli_runner, sample_project, tmp_path, mock_console):
    """Test exporting markdown to file."""
    output_file = tmp_path / "analysis.md"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--format', 'markdown',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    content = output_file.read_text()
    assert '# Static Analysis Report' in content


def test_analyze_export_table_as_markdown(cli_runner, sample_project, tmp_path, mock_console):
    """Test exporting table format to file saves as markdown."""
    output_file = tmp_path / "analysis.md"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--format', 'table',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert 'markdown' in result.output.lower()


# ===== Threshold Configuration Tests =====

def test_analyze_custom_complexity_threshold(cli_runner, sample_project, mock_console):
    """Test custom complexity threshold."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--complexity-threshold', '5',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    data = json.loads(result.output)

    # With lower threshold, should detect more high complexity files
    # Our complex.py file should be flagged
    high_complexity_files = data['quality_issues']['high_complexity_files']
    assert len(high_complexity_files) >= 1


def test_analyze_custom_maintainability_threshold(cli_runner, sample_project, mock_console):
    """Test custom maintainability threshold."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--maintainability-threshold', '80.0',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    data = json.loads(result.output)

    # Verify threshold was applied
    assert 'quality_issues' in data


def test_analyze_invalid_complexity_threshold(cli_runner, sample_project, mock_console):
    """Test invalid complexity threshold (< 1)."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--complexity-threshold', '0'
        ],
        obj={'console': mock_console}
    )

    # Should fail with error
    assert result.exit_code != 0
    assert 'error' in result.output.lower()


def test_analyze_invalid_maintainability_threshold(cli_runner, sample_project, mock_console):
    """Test invalid maintainability threshold (> 100)."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--maintainability-threshold', '150.0'
        ],
        obj={'console': mock_console}
    )

    # Should fail with error
    assert result.exit_code != 0
    assert 'error' in result.output.lower()


# ===== Display Mode Tests =====

def test_analyze_verbose_mode(cli_runner, sample_project, mock_console):
    """Test verbose mode shows per-file details."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--verbose'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Verbose mode should show file-level details
    assert 'simple.py' in result.output or 'complex.py' in result.output


def test_analyze_summary_only_mode(cli_runner, sample_project, mock_console):
    """Test summary-only mode shows only summary."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--summary-only'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Should show summary but less detail
    assert 'Files Analyzed' in result.output or 'files_analyzed' in result.output.lower()


def test_analyze_top_n_files(cli_runner, sample_project, mock_console):
    """Test --top option limits displayed files."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--top', '2',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    data = json.loads(result.output)

    # Should have all files in data, but UI limits display
    # (the --top flag affects display, not data collection)
    assert len(data['files']) >= 3


# ===== Cache Tests =====

def test_analyze_with_cache(cli_runner, sample_project, mock_console):
    """Test analysis with cache enabled (default)."""
    # First run
    result1 = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': mock_console}
    )
    assert result1.exit_code == 0

    # Second run should use cache
    result2 = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': mock_console}
    )
    assert result2.exit_code == 0

    # Results should be consistent
    data1 = json.loads(result1.output)
    data2 = json.loads(result2.output)
    assert data1['summary']['files_analyzed'] == data2['summary']['files_analyzed']


def test_analyze_no_cache(cli_runner, sample_project, mock_console):
    """Test analysis with cache disabled."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--no-cache'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert 'disabled' in result.output.lower()


# ===== Pattern and File Filtering Tests =====

def test_analyze_custom_pattern(cli_runner, tmp_path, mock_console):
    """Test custom file pattern."""
    # Create test files
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "test_file.py").write_text("def test(): pass")
    (project_dir / "main.py").write_text("def main(): pass")

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(project_dir),
            '--pattern', 'test_*.py',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    data = json.loads(result.output)

    # Should only analyze test_file.py
    assert data['summary']['files_analyzed'] == 1


# ===== Error Handling Tests =====

def test_analyze_nonexistent_path(cli_runner, mock_console):
    """Test error handling for nonexistent path."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', '/nonexistent/path'],
        obj={'console': mock_console}
    )

    # Should fail with error
    assert result.exit_code == 2  # Click parameter error


def test_analyze_empty_project(cli_runner, tmp_path, mock_console):
    """Test analyzing project with no Python files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(empty_dir)],
        obj={'console': mock_console}
    )

    # Should succeed but show warning
    assert result.exit_code == 0
    assert 'warning' in result.output.lower() or 'no' in result.output.lower()


def test_analyze_quality_issues_detected(cli_runner, sample_project, mock_console):
    """Test that quality issues are properly detected and displayed."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'analyze', str(sample_project),
            '--complexity-threshold', '5',  # Lower threshold to catch issues
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    data = json.loads(result.output)

    # Our complex.py should trigger quality issues
    quality_issues = data['quality_issues']
    assert 'high_complexity_files' in quality_issues
    assert 'low_maintainability_files' in quality_issues


# ===== Help and Documentation Tests =====

def test_analyze_help(cli_runner):
    """Test --help displays usage information."""
    result = cli_runner.invoke(cli, ['detect', 'analyze', '--help'])

    assert result.exit_code == 0
    assert 'Perform comprehensive static code analysis' in result.output
    assert '--format' in result.output
    assert '--complexity-threshold' in result.output
    assert 'Examples:' in result.output
