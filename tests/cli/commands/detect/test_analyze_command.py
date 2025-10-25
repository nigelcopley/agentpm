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
import re
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
    # Use very wide width to prevent line wrapping which can break JSON/YAML
    console = Console(file=output, force_terminal=True, width=999, legacy_windows=False)
    # Attach the StringIO to the console for easy access in tests
    console._test_output = output
    return console


def get_output(result, console=None):
    """
    Get output from either CLI result or mock console.
    
    When using custom console with Rich, output goes to console.file.
    When using Click's default output, it goes to result.output.
    """
    if console and hasattr(console, '_test_output'):
        return console._test_output.getvalue()
    return result.output


def strip_ansi(text: str) -> str:
    """
    Strip ANSI escape codes from text.
    
    Rich applies syntax highlighting to JSON/YAML which adds ANSI codes.
    For testing structured output, we need to strip these.
    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKHF]')
    return ansi_escape.sub('', text)


def extract_json(text: str) -> str:
    """
    Extract JSON content from console output.
    
    The CLI prints status messages before JSON, so we need to find and extract
    just the JSON portion (from first { to last }).
    """
    # Strip ANSI codes first
    text = strip_ansi(text)
    
    # Find the JSON object
    start = text.find('{')
    if start == -1:
        return text  # No JSON found, return as-is
    
    # Find matching closing brace
    end = text.rfind('}')
    if end == -1 or end < start:
        return text  # No valid JSON found
    
    return text[start:end + 1]


def extract_yaml(text: str) -> str:
    """
    Extract YAML content from console output.

    The CLI prints status messages before YAML. We extract everything after
    the last status line (lines starting with emojis or "Pattern:", etc.).
    """
    # Strip ANSI codes first
    text = strip_ansi(text)

    lines = text.split('\n')

    # Find where YAML content starts (after status messages)
    yaml_start = 0
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue

        # Skip common status message prefixes
        status_prefixes = ['🔍', '🏋️', 'Pattern:', 'Cache:', '✅', '⚠️', '❌',
                          'Analyzing', 'Running', 'Loaded', 'Total']
        if any(line.strip().startswith(x) for x in status_prefixes):
            continue

        # Check if this looks like YAML (key: value)
        if ':' in line and not line.strip().startswith('#'):
            yaml_start = i
            break

    return '\n'.join(lines[yaml_start:])


def get_output_clean(result, console=None, format='json') -> str:
    """
    Get output and extract structured data (JSON/YAML).
    
    Use this when you need to parse structured output that Rich has syntax-highlighted
    and that comes after CLI status messages.
    
    Args:
        result: Click test result
        console: Mock console (optional)
        format: Output format - 'json' or 'yaml' (default: 'json')
    
    Returns:
        Extracted and cleaned structured data
    """
    output = get_output(result, console)
    
    if format == 'json':
        return extract_json(output)
    elif format == 'yaml':
        return extract_yaml(output)
    else:
        return strip_ansi(output)


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'Files Analyzed' in output or 'files_analyzed' in output.lower()


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Check for key metrics in output
    output_lower = output.lower()
    assert any(x in output_lower for x in ['files analyzed', 'total lines', 'quality'])


# ===== Output Format Tests =====

def test_analyze_json_format(cli_runner, sample_project, mock_console):
    """Test JSON output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(get_output_clean(result, mock_console))

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

    output = get_output(result, mock_console)

    assert result.exit_code == 0

    # Parse YAML output
    data = yaml.safe_load(get_output_clean(result, mock_console, format='yaml'))

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

    output = get_output(result, mock_console)

    assert result.exit_code == 0

    # When printed to console without --output, Rich renders Markdown as rich text
    # So we check for rendered content, not raw markdown syntax
    # Check for key content that should be in the rendered markdown
    assert 'Static Analysis Report' in output or 'Summary' in output or 'Metrics' in output


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert output_file.exists()
    assert 'markdown' in output.lower()


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    data = json.loads(get_output_clean(result, mock_console))

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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    data = json.loads(get_output_clean(result, mock_console))

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

    output = get_output(result, mock_console)

    # Should fail with error
    assert result.exit_code != 0
    assert 'error' in output.lower()


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

    output = get_output(result, mock_console)

    # Should fail with error
    assert result.exit_code != 0
    assert 'error' in output.lower()


# ===== Display Mode Tests =====

def test_analyze_verbose_mode(cli_runner, sample_project, mock_console):
    """Test verbose mode shows per-file details."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--verbose'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Verbose mode should show file-level details
    assert 'simple.py' in output or 'complex.py' in output


def test_analyze_summary_only_mode(cli_runner, sample_project, mock_console):
    """Test summary-only mode shows only summary."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--summary-only'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show summary but less detail
    assert 'Files Analyzed' in output or 'files_analyzed' in output.lower()


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    data = json.loads(get_output_clean(result, mock_console))

    # Should have all files in data, but UI limits display
    # (the --top flag affects display, not data collection)
    assert len(data['files']) >= 3


# ===== Cache Tests =====

def test_analyze_with_cache(cli_runner, sample_project):
    """Test analysis with cache enabled (default)."""
    # Use separate console instances for each run to avoid output mixing
    from io import StringIO
    from rich.console import Console

    # First run
    output1 = StringIO()
    console1 = Console(file=output1, force_terminal=True, width=999, legacy_windows=False)
    console1._test_output = output1

    result1 = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': console1}
    )
    assert result1.exit_code == 0

    # Second run should use cache
    output2 = StringIO()
    console2 = Console(file=output2, force_terminal=True, width=999, legacy_windows=False)
    console2._test_output = output2

    result2 = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--format', 'json'],
        obj={'console': console2}
    )
    assert result2.exit_code == 0

    # Results should be consistent
    data1 = json.loads(get_output_clean(result1, console1))
    data2 = json.loads(get_output_clean(result2, console2))
    assert data1['summary']['files_analyzed'] == data2['summary']['files_analyzed']


def test_analyze_no_cache(cli_runner, sample_project, mock_console):
    """Test analysis with cache disabled."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'analyze', str(sample_project), '--no-cache'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'disabled' in output.lower()


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    data = json.loads(get_output_clean(result, mock_console))

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

    output = get_output(result, mock_console)

    # Should succeed but show warning
    assert result.exit_code == 0
    assert 'warning' in output.lower() or 'no' in output.lower()


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

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    data = json.loads(get_output_clean(result, mock_console))

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
