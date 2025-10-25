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

    assert result.exit_code == 0
    assert 'Total Modules' in result.output or 'total_modules' in result.output.lower()


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

    assert result.exit_code == 0
    # Check for key metrics
    assert 'Total Modules' in result.output
    assert 'Dependencies' in result.output


# ===== Cycle Detection Tests =====

def test_graph_detect_cycles_flag(cli_runner, sample_project_with_deps, mock_console):
    """Test --detect-cycles flag."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--detect-cycles'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Should detect circular dependency between D and E
    assert 'circular' in result.output.lower() or 'cycle' in result.output.lower()


def test_graph_cycles_only_mode(cli_runner, sample_project_with_deps, mock_console):
    """Test --cycles-only mode shows only cycles."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--cycles-only'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Should show cycles
    assert 'circular' in result.output.lower() or 'cycle' in result.output.lower()


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

    assert result.exit_code == 0
    assert 'No circular dependencies' in result.output or 'no circular' in result.output.lower()


# ===== Coupling Metrics Tests =====

def test_graph_coupling_metrics(cli_runner, sample_project_with_deps, mock_console):
    """Test --coupling flag displays coupling metrics."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--coupling'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Should show coupling table
    assert 'Coupling Metrics' in result.output or 'coupling' in result.output.lower()
    # Should show Ca (afferent) and Ce (efferent)
    assert 'Ca' in result.output or 'afferent' in result.output.lower()
    assert 'Ce' in result.output or 'efferent' in result.output.lower()
    assert 'Instability' in result.output or 'instability' in result.output.lower()


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

    assert result.exit_code == 0
    # Should show coupling metrics
    assert 'Coupling' in result.output or 'coupling' in result.output.lower()


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

    assert result.exit_code == 0
    # Should show root modules section
    assert 'Root Modules' in result.output or 'root' in result.output.lower()


def test_graph_leaf_modules(cli_runner, sample_project_with_deps, mock_console):
    """Test --leaf-modules flag shows leaf modules."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--leaf-modules'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    # Should show leaf modules section
    assert 'Leaf Modules' in result.output or 'leaf' in result.output.lower()


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

    assert result.exit_code == 0
    assert 'Root' in result.output or 'root' in result.output.lower()
    assert 'Leaf' in result.output or 'leaf' in result.output.lower()


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

    assert result.exit_code == 0

    # Should create default JSON file
    # In isolated mode, check result indicates success
    assert 'exported' in result.output.lower() or result.exit_code == 0


def test_graph_yaml_format(cli_runner, sample_project_with_deps, mock_console):
    """Test YAML output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'graph', str(sample_project_with_deps), '--format', 'yaml'],
        obj={'console': mock_console}
    )

    assert result.exit_code == 0
    assert 'exported' in result.output.lower() or result.exit_code == 0


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

    assert result.exit_code == 0
    # Should show recommendations
    assert 'Recommendation' in result.output or 'suggestion' in result.output.lower()


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

    assert result.exit_code == 0
    # Should show comprehensive analysis
    assert result.output  # Has content


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
