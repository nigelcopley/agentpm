"""
pytest Plugin - Testing Framework Context Extraction

Extracts pytest configuration, fixtures, and test organization facts.

Provides:
1. Project facts (pytest version, config, fixtures, test patterns)
2. Code amalgamations (test functions, fixtures, conftest files)

Pattern: BasePlugin implementation using plugin utilities
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory
from ...utils import (
    find_config_files,
    extract_python_functions,
    filter_project_files,
)


class PytestPlugin(BasePlugin):
    """
    pytest testing framework plugin for context extraction.

    Provides:
    1. Test framework facts (version, config, fixtures, patterns)
    2. Test code amalgamations (tests, fixtures, conftest)
    """

    @property
    def plugin_id(self) -> str:
        return "testing:pytest"

    @property
    def enriches(self) -> str:
        return "pytest"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.TESTING

    def detect(self, project_path: Path) -> float:
        """
        Detect pytest with 3-phase approach.

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        # Phase 1: Files (0.3 max)
        if (project_path / "pytest.ini").exists():
            confidence += 0.15
        if (project_path / "conftest.py").exists():
            confidence += 0.15

        # Phase 2: Imports (0.4 max)
        py_files = list(project_path.glob("**/*.py"))[:10]
        for py_file in py_files:
            try:
                content = py_file.read_text()
                if "import pytest" in content or "from pytest" in content:
                    confidence += 0.40
                    break
            except Exception:
                continue

        # Phase 3: Structure (0.3 max)
        if (project_path / "tests").exists() or (project_path / "test").exists():
            confidence += 0.15
        # Check for test_*.py pattern
        if list(project_path.glob("**/test_*.py")):
            confidence += 0.15

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract pytest project facts.

        Returns testing framework configuration and organization.
        """
        facts = {}

        # Framework info
        facts['test_framework'] = 'pytest'
        facts['pytest_version'] = self._get_pytest_version(project_path)

        # Configuration
        facts['config'] = self._extract_config(project_path)

        # Test organization
        facts['test_organization'] = self._analyze_test_structure(project_path)

        # Fixtures
        facts['fixtures'] = self._discover_fixtures(project_path)

        # Pytest plugins
        facts['pytest_plugins'] = self._detect_pytest_plugins(project_path)

        # Coverage configuration
        facts['coverage'] = self._extract_coverage_config(project_path)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate pytest code amalgamations.

        Returns test code groupings for agent reference.
        """
        amalgamations = {}

        # Collect all test functions
        amalgamations['tests'] = self._collect_tests(project_path)

        # Collect all fixtures
        amalgamations['fixtures'] = self._collect_fixtures(project_path)

        # Collect conftest files
        amalgamations['conftest'] = self._collect_conftest_files(project_path)

        return amalgamations

    # ========== Fact Extraction Helpers ==========

    def _get_pytest_version(self, project_path: Path) -> Optional[str]:
        """Extract pytest version from dependencies"""
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text()
            match = re.search(r'pytest[>=<]+(\d+\.\d+\.\d+)', content)
            if match:
                return match.group(1)

        # Check pyproject.toml
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            match = re.search(r'pytest\s*=\s*["\'][\^>=]*(\d+\.\d+)', content)
            if match:
                return match.group(1)

        return None

    def _extract_config(self, project_path: Path) -> Dict[str, Any]:
        """Extract pytest configuration"""
        config = {}

        # Find config file
        config_files = find_config_files(project_path, [
            'pytest.ini', 'pyproject.toml', 'setup.cfg', 'tox.ini'
        ])

        if config_files:
            config['config_file'] = config_files[0]

            # Parse pytest.ini if exists
            if 'pytest.ini' in config_files[0]:
                pytest_ini = project_path / 'pytest.ini'
                content = pytest_ini.read_text()

                # Extract test paths
                match = re.search(r'testpaths\s*=\s*(.+)', content)
                if match:
                    config['test_paths'] = [p.strip() for p in match.group(1).split()]

                # Extract python files pattern
                match = re.search(r'python_files\s*=\s*(.+)', content)
                if match:
                    config['test_file_pattern'] = match.group(1).strip()

                # Extract markers
                markers = re.findall(r'markers\s*=\s*(.+)', content)
                if markers:
                    config['custom_markers'] = markers
        else:
            config['config_file'] = None
            config['using_defaults'] = True

        return config

    def _analyze_test_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze test directory structure"""
        structure = {}

        # Find test directory
        test_dir = None
        for td in ['tests', 'test', 'testing']:
            if (project_path / td).is_dir():
                test_dir = td
                break

        if test_dir:
            structure['test_directory'] = f'{test_dir}/'

            # Analyze structure
            test_path = project_path / test_dir
            test_files = list(test_path.glob('**/test_*.py'))
            conftest_files = list(test_path.glob('**/conftest.py'))

            structure['test_files_count'] = len(test_files)
            structure['conftest_count'] = len(conftest_files)
            structure['conftest_locations'] = [str(f.relative_to(project_path)) for f in conftest_files]

            # Check if mirrors source structure
            source_dirs = ['src', 'lib', project_path.name]
            for src in source_dirs:
                if (project_path / src).is_dir():
                    structure['mirrors_source'] = f'tests/ mirrors {src}/ structure'
                    break
        else:
            structure['test_directory'] = None

        return structure

    def _discover_fixtures(self, project_path: Path) -> Dict[str, Any]:
        """Discover pytest fixtures from conftest files"""
        fixtures = {
            'conftest_files': [],
            'fixture_names': [],
            'fixture_count': 0
        }

        # Find all conftest.py files
        conftest_files = list(project_path.glob('**/conftest.py'))
        conftest_files = [f for f in conftest_files if 'venv' not in str(f) and '__pycache__' not in str(f)]

        for conftest in conftest_files:
            fixtures['conftest_files'].append(str(conftest.relative_to(project_path)))

            # Parse for @pytest.fixture
            try:
                content = conftest.read_text()
                fixture_matches = re.findall(r'@pytest\.fixture[^\n]*\ndef\s+(\w+)', content)
                fixtures['fixture_names'].extend(fixture_matches)
            except Exception:
                continue

        fixtures['fixture_count'] = len(fixtures['fixture_names'])
        fixtures['fixture_names'] = sorted(set(fixtures['fixture_names']))  # Unique, sorted

        return fixtures

    def _detect_pytest_plugins(self, project_path: Path) -> List[str]:
        """Detect pytest plugins in use"""
        plugins = []

        # Check dependencies
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text()
            pytest_plugins = [
                'pytest-cov', 'pytest-django', 'pytest-asyncio',
                'pytest-mock', 'pytest-xdist', 'pytest-timeout'
            ]
            for plugin in pytest_plugins:
                if plugin in content:
                    plugins.append(plugin)

        # Check pyproject.toml
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            pytest_plugins = [
                'pytest-cov', 'pytest-django', 'pytest-asyncio',
                'pytest-mock', 'pytest-xdist', 'pytest-timeout'
            ]
            for plugin in pytest_plugins:
                if plugin in content:
                    if plugin not in plugins:
                        plugins.append(plugin)

        return sorted(plugins)

    def _extract_coverage_config(self, project_path: Path) -> Dict[str, Any]:
        """Extract coverage configuration"""
        coverage = {
            'tool': None,
            'target': None,
            'config_file': None
        }

        # Check if pytest-cov is used
        if 'pytest-cov' in self._detect_pytest_plugins(project_path):
            coverage['tool'] = 'pytest-cov'

            # Find coverage target
            pytest_ini = project_path / 'pytest.ini'
            if pytest_ini.exists():
                content = pytest_ini.read_text()
                match = re.search(r'--cov-fail-under[=\s]+(\d+)', content)
                if match:
                    coverage['target'] = f'{match.group(1)}%'
                    coverage['config_file'] = 'pytest.ini'

            # Check pyproject.toml
            if not coverage['target']:
                pyproject = project_path / 'pyproject.toml'
                if pyproject.exists():
                    content = pyproject.read_text()
                    match = re.search(r'fail_under\s*=\s*(\d+)', content)
                    if match:
                        coverage['target'] = f'{match.group(1)}%'
                        coverage['config_file'] = 'pyproject.toml'

        return coverage

    # ========== Code Amalgamation Helpers ==========

    def _collect_tests(self, project_path: Path) -> str:
        """Collect all pytest test functions"""
        content = "# All pytest Test Functions\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Find test files
        test_files = list(project_path.glob('**/test_*.py'))
        test_files = filter_project_files(test_files)

        for test_file in sorted(test_files)[:100]:
            try:
                file_content = test_file.read_text(errors='ignore')
                relative_path = test_file.relative_to(project_path)
                content += f"\n# File: {relative_path}\n"

                # Extract test functions (def test_*)
                for match in re.finditer(r'^def (test_\w+)\(.*?\):', file_content, re.MULTILINE):
                    content += f"def {match.group(1)}(...)\n"

                # Extract test classes (class Test*)
                for match in re.finditer(r'^class (Test\w+)', file_content, re.MULTILINE):
                    content += f"class {match.group(1)}\n"

            except Exception:
                continue

        return content

    def _collect_fixtures(self, project_path: Path) -> str:
        """Collect all pytest fixtures"""
        content = "# All pytest Fixtures\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        conftest_files = list(project_path.glob('**/conftest.py'))
        conftest_files = filter_project_files(conftest_files)

        for conftest in sorted(conftest_files):
            try:
                file_content = conftest.read_text(errors='ignore')
                relative_path = conftest.relative_to(project_path)

                # Find fixtures
                fixtures = re.findall(
                    r'@pytest\.fixture[^\n]*\ndef\s+(\w+)\([^)]*\):\s*\n\s*"""([^"]+)"""',
                    file_content,
                    re.MULTILINE
                )

                if fixtures:
                    content += f"\n# File: {relative_path}\n"
                    for fixture_name, docstring in fixtures:
                        content += f"@pytest.fixture\ndef {fixture_name}():\n"
                        content += f'    """{docstring.strip()}"""\n\n'

            except Exception:
                continue

        return content

    def _collect_conftest_files(self, project_path: Path) -> str:
        """Collect all conftest.py file contents"""
        content = "# All conftest.py Files\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        conftest_files = list(project_path.glob('**/conftest.py'))
        conftest_files = filter_project_files(conftest_files)

        for conftest in sorted(conftest_files):
            try:
                relative_path = conftest.relative_to(project_path)
                content += f"\n{'='*60}\n"
                content += f"# File: {relative_path}\n"
                content += f"{'='*60}\n\n"
                content += conftest.read_text(errors='ignore')
                content += "\n\n"
            except Exception:
                continue

        return content


# Import datetime for timestamps
from datetime import datetime