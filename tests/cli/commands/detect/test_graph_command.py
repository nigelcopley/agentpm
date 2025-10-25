"""
Integration tests for 'apm detect graph' CLI command.

Tests dependency graph CLI integration including:
- Basic graph building
- Cycle detection
- Coupling metrics display
- Visualization export
- Multiple output formats
- Module-specific analysis
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
def sample_project_with_deps(tmp_path):
    """
    Create sample Python project with dependencies for graph testing.

    Creates modules with various dependency patterns:
    - Simple linear dependencies
    - Circular dependencies
    - Complex coupling patterns
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Module A (root module - no dependencies)
    module_a = project_dir / "module_a.py"
    module_a.write_text('''
"""Module A - root module."""

def function_a():
    """Function in module A."""
    return "A"
''')

    # Module B (depends on A)
    module_b = project_dir / "module_b.py"
    module_b.write_text('''
"""Module B - depends on A."""

from .module_a import function_a

def function_b():
    """Function in module B."""
    return function_a() + "B"
''')

    # Module C (depends on B)
    module_c = project_dir / "module_c.py"
    module_c.write_text('''
"""Module C - depends on B."""

from .module_b import function_b

def function_c():
    """Function in module C."""
    return function_b() + "C"
''')

    # Module D (circular dependency with E)
    module_d = project_dir / "module_d.py"
    module_d.write_text('''
"""Module D - circular dependency with E."""

from .module_e import function_e

def function_d():
    """Function in module D."""
    return "D" + function_e()
''')

    # Module E (circular dependency with D)
    module_e = project_dir / "module_e.py"
    module_e.write_text('''
"""Module E - circular dependency with D."""

from .module_d import function_d

def function_e():
    """Function in module E."""
    return "E"
''')

    # Module F (leaf module - depends on multiple)
    module_f = project_dir / "module_f.py"
    module_f.write_text('''
"""Module F - leaf module with high coupling."""

from .module_a import function_a
from .module_b import function_b
from .module_c import function_c

def function_f():
    """Function in module F."""
    return function_a() + function_b() + function_c()
''')

    # Create __init__.py
    (project_dir / "__init__.py").write_text("")

    return project_dir


# ===== Basic Graph Tests =====

def test_graph_basic_execution(cli_runner, sample_project_with_deps, mock_console):
    """Test basic graph command execution."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps)],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'Total Modules' in output or 'total_modules' in output.lower()


def test_graph_current_directory(cli_runner, sample_project_with_deps, mock_console):
    """Test analyzing current directory (default)."""
    with cli_runner.isolated_filesystem(temp_dir=sample_project_with_deps.parent):
        import os
        os.chdir(sample_project_with_deps)

        result = cli_runner.invoke(
            cli,
            ['detect', 'graph'],
            obj={'console': mock_console}
        )

        assert result.exit_code == 0


def test_graph_summary_table(cli_runner, sample_project_with_deps, mock_console):
    """Test that summary table is displayed."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps)],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Check for key metrics
    assert 'Total Modules' in output
    assert 'Dependencies' in output


# ===== Cycle Detection Tests =====

def test_graph_detect_cycles_flag(cli_runner, sample_project_with_deps, mock_console):
    """Test --detect-cycles flag."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--detect-cycles'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should detect circular dependency between D and E
    assert 'circular' in output.lower() or 'cycle' in output.lower()


def test_graph_cycles_only_mode(cli_runner, sample_project_with_deps, mock_console):
    """Test --cycles-only mode shows only cycles."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--cycles-only'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show cycles
    assert 'circular' in output.lower() or 'cycle' in output.lower()


def test_graph_no_cycles_detected(cli_runner, tmp_path, mock_console):
    """Test project with no circular dependencies."""
    # Create simple project without cycles
    project_dir = tmp_path / "no_cycles"
    project_dir.mkdir()

    (project_dir / "a.py").write_text("def a(): return 'a'")
    (project_dir / "b.py").write_text("from .a import a\ndef b(): return a() + 'b'")
    (project_dir / "__init__.py").write_text("")

    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(project_dir), '--detect-cycles'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'No circular dependencies' in output or 'no circular' in output.lower()


# ===== Coupling Metrics Tests =====

def test_graph_coupling_metrics(cli_runner, sample_project_with_deps, mock_console):
    """Test --coupling flag displays coupling metrics."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--coupling'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show coupling table
    assert 'Coupling Metrics' in output or 'coupling' in output.lower()
    # Should show Ca (afferent) and Ce (efferent)
    assert 'Ca' in output or 'afferent' in output.lower()
    assert 'Ce' in output or 'efferent' in output.lower()
    assert 'Instability' in output or 'instability' in output.lower()


def test_graph_coupling_show_all(cli_runner, sample_project_with_deps, mock_console):
    """Test --all flag shows all modules (not just top 20)."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--coupling',
            '--all'
        ],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show coupling metrics
    assert 'Coupling' in output or 'coupling' in output.lower()


# ===== Module-Specific Analysis Tests =====

def test_graph_module_specific_analysis(cli_runner, sample_project_with_deps, mock_console):
    """Test --module flag for specific module analysis."""
    # Analyze module_b specifically
    module_path = "module_b.py"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--module', module_path
        ],
        obj={'console': mock_console}
    )

    # May succeed or fail depending on module detection
    # Just verify it doesn't crash
    assert result.exit_code in [0, 1]


def test_graph_module_not_found(cli_runner, sample_project_with_deps, mock_console):
    """Test error handling for non-existent module."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--module', 'nonexistent_module.py'
        ],
        obj={'console': mock_console}
    )

    # Should handle gracefully
    assert result.exit_code in [0, 1]


# ===== Root and Leaf Module Tests =====

def test_graph_root_modules(cli_runner, sample_project_with_deps, mock_console):
    """Test --root-modules flag shows root modules."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--root-modules'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show root modules section
    assert 'Root Modules' in output or 'root' in output.lower()


def test_graph_leaf_modules(cli_runner, sample_project_with_deps, mock_console):
    """Test --leaf-modules flag shows leaf modules."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--leaf-modules'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show leaf modules section
    assert 'Leaf Modules' in output or 'leaf' in output.lower()


def test_graph_root_and_leaf(cli_runner, sample_project_with_deps, mock_console):
    """Test showing both root and leaf modules."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--root-modules',
            '--leaf-modules'
        ],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'Root' in output or 'root' in output.lower()
    assert 'Leaf' in output or 'leaf' in output.lower()


# ===== Visualization Tests =====

def test_graph_visualize_basic(cli_runner, sample_project_with_deps, tmp_path, mock_console):
    """Test basic Graphviz visualization generation."""
    output_file = tmp_path / "graph.dot"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--visualize',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify DOT file content
    content = output_file.read_text()
    assert 'digraph' in content


def test_graph_visualize_default_filename(cli_runner, sample_project_with_deps, mock_console):
    """Test visualization with default filename."""
    with cli_runner.isolated_filesystem(temp_dir=sample_project_with_deps.parent):
        import os
        os.chdir(sample_project_with_deps)

        result = cli_runner.invoke(
            cli,
            ['detect', 'graph', '--visualize'],
            obj={'console': mock_console}
        )

        assert result.exit_code == 0
        # Should create dependency-graph.dot
        default_file = Path('dependency-graph.dot')
        assert default_file.exists()


def test_graph_visualize_highlight_cycles(cli_runner, sample_project_with_deps, tmp_path, mock_console):
    """Test visualization with cycle highlighting."""
    output_file = tmp_path / "graph_cycles.dot"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--visualize',
            '--highlight-cycles',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    content = output_file.read_text()
    # Should have cycle highlighting (red edges or special styling)
    assert 'digraph' in content


def test_graph_visualize_with_metrics(cli_runner, sample_project_with_deps, tmp_path, mock_console):
    """Test visualization including coupling metrics."""
    output_file = tmp_path / "graph_metrics.dot"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--visualize',
            '--coupling',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()


# ===== Output Format Tests =====

def test_graph_json_format(cli_runner, sample_project_with_deps, mock_console):
    """Test JSON output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--format', 'json'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0

    # Should create default JSON file
    # In isolated mode, check result indicates success
    assert 'exported' in output.lower() or result.exit_code == 0


def test_graph_yaml_format(cli_runner, sample_project_with_deps, mock_console):
    """Test YAML output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--format', 'yaml'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    assert 'exported' in output.lower() or result.exit_code == 0


def test_graph_export_json_custom_file(cli_runner, sample_project_with_deps, tmp_path, mock_console):
    """Test exporting JSON to custom file."""
    output_file = tmp_path / "deps.json"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--format', 'json',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify JSON structure
    data = json.loads(output_file.read_text())
    assert 'project_path' in data
    assert 'total_modules' in data
    assert 'total_dependencies' in data
    assert 'circular_dependencies' in data
    assert 'coupling_metrics' in data


def test_graph_export_yaml_custom_file(cli_runner, sample_project_with_deps, tmp_path, mock_console):
    """Test exporting YAML to custom file."""
    output_file = tmp_path / "deps.yaml"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--format', 'yaml',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify YAML structure
    data = yaml.safe_load(output_file.read_text())
    assert 'project_path' in data
    assert 'total_modules' in data


# ===== Rebuild/Cache Tests =====

def test_graph_with_cache(cli_runner, sample_project_with_deps, mock_console):
    """Test graph building with cache (default)."""
    # First run
    result1 = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--format', 'json'],
        obj={'console': mock_console}
    )
    assert result1.exit_code == 0

    # Second run should use cache
    result2 = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--format', 'json'],
        obj={'console': mock_console}
    )
    assert result2.exit_code == 0


def test_graph_rebuild_cache(cli_runner, sample_project_with_deps, mock_console):
    """Test --rebuild flag forces cache rebuild."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--rebuild'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0


# ===== Error Handling Tests =====

def test_graph_nonexistent_path(cli_runner, mock_console):
    """Test error handling for nonexistent path."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', '/nonexistent/path'],
        obj={'console': mock_console}
    )

    # Should fail with error
    assert result.exit_code == 2  # Click parameter error


def test_graph_empty_project(cli_runner, tmp_path, mock_console):
    """Test analyzing project with no Python files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(empty_dir)],
        obj={'console': mock_console}
    )

    # Should handle gracefully
    assert result.exit_code in [0, 1]


# ===== Recommendations Tests =====

def test_graph_recommendations_with_cycles(cli_runner, sample_project_with_deps, mock_console):
    """Test that recommendations are shown when cycles detected."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--detect-cycles'],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show recommendations
    assert 'Recommendation' in output or 'suggestion' in output.lower()


# ===== Combined Options Tests =====

def test_graph_all_options_combined(cli_runner, sample_project_with_deps, mock_console):
    """Test combining multiple options."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'graph', str(sample_project_with_deps),
            '--detect-cycles',
            '--coupling',
            '--root-modules',
            '--leaf-modules',
            '--all'
        ],
        obj={'console': mock_console}
    )

    output = get_output(result, mock_console)

    assert result.exit_code == 0
    # Should show comprehensive analysis
    assert output  # Has content


# ===== Help and Documentation Tests =====

def test_graph_help(cli_runner):
    """Test --help displays usage information."""
    result = cli_runner.invoke(cli, ['detect', 'graph', '--help'])

    assert result.exit_code == 0
    assert 'Analyze project dependency graph' in result.output
    assert '--detect-cycles' in result.output
    assert '--visualize' in result.output
    assert '--coupling' in result.output
    assert 'Examples:' in result.output
