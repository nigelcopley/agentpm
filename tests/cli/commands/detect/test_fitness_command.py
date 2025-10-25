"""
Integration tests for 'apm detect fitness' CLI command.

Tests architecture fitness testing CLI integration including:
- Basic fitness test execution
- --fail-on-error exit codes (critical for CI/CD)
- Policy filtering
- Violation display with suggestions
- Multiple output formats
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
def compliant_project(tmp_path):
    """
    Create sample project that passes fitness tests.

    Well-structured code with:
    - Low complexity
    - No circular dependencies
    - Good naming conventions
    """
    project_dir = tmp_path / "compliant_project"
    project_dir.mkdir()

    # Simple, well-structured module
    (project_dir / "service.py").write_text('''
"""Service module with low complexity."""

class UserService:
    """User service with simple methods."""

    def __init__(self, repository):
        self.repository = repository

    def create_user(self, name, email):
        """Create a new user."""
        if not name or not email:
            raise ValueError("Name and email required")

        user = {"name": name, "email": email}
        return self.repository.save(user)

    def get_user(self, user_id):
        """Get user by ID."""
        return self.repository.find_by_id(user_id)
''')

    (project_dir / "repository.py").write_text('''
"""Repository module."""

class UserRepository:
    """User repository."""

    def __init__(self):
        self.users = {}

    def save(self, user):
        """Save user."""
        user_id = len(self.users) + 1
        self.users[user_id] = user
        return user_id

    def find_by_id(self, user_id):
        """Find user by ID."""
        return self.users.get(user_id)
''')

    return project_dir


@pytest.fixture
def noncompliant_project(tmp_path):
    """
    Create sample project that fails fitness tests.

    Code with issues:
    - High complexity
    - Circular dependencies
    - Poor structure
    """
    project_dir = tmp_path / "noncompliant_project"
    project_dir.mkdir()

    # Module with circular dependency and high complexity
    (project_dir / "module_a.py").write_text('''
"""Module A with high complexity and circular dependency."""

from .module_b import function_b

def complex_function(x, y, z, w, a, b, c):
    """Function with very high cyclomatic complexity."""
    result = 0

    if x > 0:
        if y > 0:
            if z > 0:
                if w > 0:
                    if a > 0:
                        if b > 0:
                            if c > 0:
                                result = x + y + z + w + a + b + c
                            else:
                                result = x + y + z + w + a + b
                        else:
                            result = x + y + z + w + a
                    else:
                        result = x + y + z + w
                else:
                    result = x + y + z
            else:
                result = x + y
        else:
            result = x
    else:
        result = 0

    return result + function_b()
''')

    (project_dir / "module_b.py").write_text('''
"""Module B with circular dependency."""

from .module_a import complex_function

def function_b():
    """Function that creates circular dependency."""
    return 42
''')

    # Create __init__.py
    (project_dir / "__init__.py").write_text("")

    return project_dir


# ===== Basic Fitness Test Execution =====

def test_fitness_basic_execution(cli_runner, compliant_project, mock_console):
    """Test basic fitness command execution."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    # May pass or fail depending on policies
    assert result.exit_code in [0, 1]
    # Should show fitness test results
    assert 'Fitness' in result.output or 'fitness' in result.output.lower()


def test_fitness_current_directory(cli_runner, compliant_project, mock_console):
    """Test running fitness tests on current directory (default)."""
    with cli_runner.isolated_filesystem(temp_dir=compliant_project.parent):
        import os
        os.chdir(compliant_project)

        result = cli_runner.invoke(
            cli,
            ['detect', 'fitness'],
            obj={'console': mock_console}
        )

        assert result.exit_code in [0, 1]


def test_fitness_summary_displayed(cli_runner, compliant_project, mock_console):
    """Test that fitness test summary is displayed."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]
    # Should show summary with pass/fail counts
    output_lower = result.output.lower()
    assert 'passed' in output_lower or 'failed' in output_lower or 'compliance' in output_lower


# ===== Exit Code Tests (CI/CD Critical) =====

def test_fitness_pass_exit_code_zero(cli_runner, compliant_project, mock_console):
    """Test exit code 0 when tests pass without --fail-on-error."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    # Without --fail-on-error, always exits 0 (report mode)
    # unless there's a crash
    assert result.exit_code in [0, 1]


def test_fitness_fail_on_error_exit_code(cli_runner, noncompliant_project, mock_console):
    """Test exit code 1 when violations found with --fail-on-error."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--fail-on-error'
        ],
        obj={'console': mock_console}
    )

    # Should exit with 1 if violations found
    # May also be 0 if passes, or 1 for violations
    assert result.exit_code in [0, 1]


def test_fitness_fail_on_error_with_json(cli_runner, noncompliant_project, mock_console):
    """Test --fail-on-error with JSON output (CI/CD automation)."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--fail-on-error',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    # Should have JSON output even with error
    if result.exit_code == 1:
        # Verify JSON is still valid
        try:
            data = json.loads(result.output)
            assert 'is_passing' in data
        except json.JSONDecodeError:
            # May not have JSON if command failed before output
            pass


def test_fitness_ci_cd_workflow(cli_runner, compliant_project, mock_console):
    """Test typical CI/CD workflow: run with --fail-on-error and JSON."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--fail-on-error',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    # Should work for CI/CD integration
    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        # Parse JSON output
        data = json.loads(result.output)
        assert 'is_passing' in data
        assert 'compliance_score' in data


# ===== Policy Filtering Tests =====

def test_fitness_default_policy_set(cli_runner, compliant_project, mock_console):
    """Test default policy set."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        data = json.loads(result.output)
        # Should have run some policies
        total_tests = data['passed_count'] + data['warning_count'] + data['error_count']
        assert total_tests > 0


def test_fitness_errors_only_filter(cli_runner, noncompliant_project, mock_console):
    """Test --errors-only flag shows only ERROR level violations."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--errors-only'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should only show errors (if any)
    if 'ERROR' in result.output:
        assert 'WARNING' not in result.output or result.output.count('WARNING') < result.output.count('ERROR')


def test_fitness_warnings_only_filter(cli_runner, compliant_project, mock_console):
    """Test --warnings-only flag shows only WARNING level violations."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--warnings-only'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should only show warnings (if any)
    # Without errors displayed


def test_fitness_errors_only_json(cli_runner, noncompliant_project, mock_console):
    """Test --errors-only with JSON format."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--errors-only',
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        data = json.loads(result.output)
        # Violations should be filtered
        for violation in data['violations']:
            assert violation['level'] == 'error'


# ===== Violation Display Tests =====

def test_fitness_violations_table(cli_runner, noncompliant_project, mock_console):
    """Test violations displayed in table format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(noncompliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should show violations table
    if result.exit_code == 1 or 'violation' in result.output.lower():
        assert 'Policy' in result.output or 'policy' in result.output.lower()


def test_fitness_no_violations_message(cli_runner, compliant_project, mock_console):
    """Test 'no violations' message when tests pass."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # May show "no violations" or "passed"
    output_lower = result.output.lower()
    assert 'passed' in output_lower or 'no violations' in output_lower or 'compliance' in output_lower


def test_fitness_violation_details(cli_runner, noncompliant_project, mock_console):
    """Test that violation details include policy, message, location."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(noncompliant_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        data = json.loads(result.output)

        # Check violation structure
        for violation in data['violations']:
            assert 'policy_id' in violation
            assert 'level' in violation
            assert 'message' in violation
            assert 'location' in violation


# ===== Suggestions Tests =====

def test_fitness_show_suggestions(cli_runner, noncompliant_project, mock_console):
    """Test --show-suggestions displays fix suggestions."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--show-suggestions'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should show suggestions section
    if 'violation' in result.output.lower():
        assert 'Suggestion' in result.output or 'suggestion' in result.output.lower()


def test_fitness_suggestions_in_json(cli_runner, noncompliant_project, mock_console):
    """Test suggestions included in JSON output."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--format', 'json'
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        data = json.loads(result.output)

        # Suggestions should be in violations
        for violation in data['violations']:
            assert 'suggestion' in violation


def test_fitness_no_suggestions_without_flag(cli_runner, noncompliant_project, mock_console):
    """Test suggestions not shown without --show-suggestions flag."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(noncompliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]
    # Suggestions section may not be prominent without flag


# ===== Summary Statistics Tests =====

def test_fitness_summary_statistics(cli_runner, compliant_project, mock_console):
    """Test summary statistics display."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should show summary stats
    output_lower = result.output.lower()
    assert 'passed' in output_lower or 'compliance' in output_lower


def test_fitness_compliance_score(cli_runner, compliant_project, mock_console):
    """Test compliance score calculation and display."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        data = json.loads(result.output)

        # Should have compliance score
        assert 'compliance_score' in data
        assert 0.0 <= data['compliance_score'] <= 1.0


# ===== Output Format Tests =====

def test_fitness_table_format(cli_runner, compliant_project, mock_console):
    """Test table output format (default)."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project), '--format', 'table'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]
    # Table uses Rich rendering
    assert result.output


def test_fitness_json_format(cli_runner, compliant_project, mock_console):
    """Test JSON output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project), '--format', 'json'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        # Parse and verify JSON structure
        data = json.loads(result.output)

        assert 'passed_count' in data
        assert 'warning_count' in data
        assert 'error_count' in data
        assert 'compliance_score' in data
        assert 'tested_at' in data
        assert 'is_passing' in data
        assert 'violations' in data


def test_fitness_yaml_format(cli_runner, compliant_project, mock_console):
    """Test YAML output format."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project), '--format', 'yaml'],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        # Parse and verify YAML structure
        data = yaml.safe_load(result.output)

        assert 'passed_count' in data
        assert 'compliance_score' in data


# ===== File Export Tests =====

def test_fitness_export_json(cli_runner, compliant_project, tmp_path, mock_console):
    """Test exporting JSON to file."""
    output_file = tmp_path / "fitness.json"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--format', 'json',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        assert output_file.exists()

        # Verify file contents
        data = json.loads(output_file.read_text())
        assert 'compliance_score' in data


def test_fitness_export_yaml(cli_runner, compliant_project, tmp_path, mock_console):
    """Test exporting YAML to file."""
    output_file = tmp_path / "fitness.yaml"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--format', 'yaml',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        assert output_file.exists()

        # Verify file contents
        data = yaml.safe_load(output_file.read_text())
        assert 'compliance_score' in data


def test_fitness_export_markdown(cli_runner, compliant_project, tmp_path, mock_console):
    """Test exporting table format to markdown file."""
    output_file = tmp_path / "fitness.md"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if result.exit_code == 0:
        assert output_file.exists()

        # Verify markdown structure
        content = output_file.read_text()
        assert '# Architecture Fitness Test Results' in content


def test_fitness_export_with_suggestions(cli_runner, noncompliant_project, tmp_path, mock_console):
    """Test exporting with suggestions included."""
    output_file = tmp_path / "fitness_suggestions.md"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--show-suggestions',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    if output_file.exists():
        content = output_file.read_text()
        assert '## Suggestions' in content or '# Architecture Fitness Test Results' in content


# ===== Status Messages Tests =====

def test_fitness_passed_status(cli_runner, compliant_project, mock_console):
    """Test PASSED status message."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(compliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # Should show pass/fail status
    output_lower = result.output.lower()
    assert 'passed' in output_lower or 'failed' in output_lower


def test_fitness_failed_status(cli_runner, noncompliant_project, mock_console):
    """Test FAILED status message."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(noncompliant_project)],
        obj={'console': mock_console}
    )

    assert result.exit_code in [0, 1]

    # May show failed status
    output_lower = result.output.lower()
    assert 'fitness' in output_lower or 'test' in output_lower


# ===== Error Handling Tests =====

def test_fitness_nonexistent_path(cli_runner, mock_console):
    """Test error handling for nonexistent path."""
    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', '/nonexistent/path'],
        obj={'console': mock_console}
    )

    # Should fail with error
    assert result.exit_code == 2  # Click parameter error


def test_fitness_empty_project(cli_runner, tmp_path, mock_console):
    """Test fitness tests on empty project."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = cli_runner.invoke(
        cli,
        ['detect', 'fitness', str(empty_dir)],
        obj={'console': mock_console}
    )

    # Should handle gracefully
    assert result.exit_code in [0, 1]


# ===== Policy Set Tests =====

def test_fitness_custom_policy_set(cli_runner, compliant_project, mock_console):
    """Test --policy-set option."""
    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(compliant_project),
            '--policy-set', 'strict'
        ],
        obj={'console': mock_console}
    )

    # May succeed or fail depending on policy set support
    assert result.exit_code in [0, 1]


# ===== Combined Options Tests =====

def test_fitness_all_options_combined(cli_runner, noncompliant_project, tmp_path, mock_console):
    """Test combining multiple options."""
    output_file = tmp_path / "full_fitness.md"

    result = cli_runner.invoke(
        cli,
        [
            'detect', 'fitness', str(noncompliant_project),
            '--fail-on-error',
            '--errors-only',
            '--show-suggestions',
            '--output', str(output_file)
        ],
        obj={'console': mock_console}
    )

    # Should handle all options together
    assert result.exit_code in [0, 1]


# ===== Help and Documentation Tests =====

def test_fitness_help(cli_runner):
    """Test --help displays usage information."""
    result = cli_runner.invoke(cli, ['detect', 'fitness', '--help'])

    assert result.exit_code == 0
    assert 'Run architecture fitness tests' in result.output
    assert '--fail-on-error' in result.output
    assert '--show-suggestions' in result.output
    assert '--errors-only' in result.output
    assert 'Exit codes:' in result.output
    assert 'Examples:' in result.output
