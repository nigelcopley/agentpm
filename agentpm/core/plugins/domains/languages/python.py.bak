"""
Python Plugin - Framework-Specific Context Extraction

Extracts Python project facts and generates code amalgamations.

Uses shared utilities for common operations (dependency parsing, code extraction).

Pattern: BasePlugin implementation using plugin utilities
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory
from ...utils import (
    TomlDependencyParser,
    TextDependencyParser,
    extract_python_classes,
    extract_python_functions,
    extract_python_imports,
    detect_project_pattern,
    find_entry_points,
    discover_test_directory,
    discover_key_modules,
    find_config_files,
)


class PythonPlugin(BasePlugin):
    """
    Python language plugin for context extraction.

    Provides:
    1. Project facts (versions, dependencies, structure, standards)
    2. Code amalgamations (classes, functions, imports)
    """

    @property
    def plugin_id(self) -> str:
        return "lang:python"

    @property
    def enriches(self) -> str:
        return "python"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.LANGUAGE

    def detect(self, project_path: Path) -> float:
        """
        Detect Python presence with 3-phase approach.

        Phase 1: Files (30%) - Config files and package managers
        Phase 2: Extensions (40%) - Python file count
        Phase 3: Structure (30%) - Project organization

        Returns:
            Confidence score 0.0-1.0 (graceful degradation on errors)
        """
        confidence = 0.0

        try:
            # Phase 1: Files (0.3 max)
            # Modern Python projects use pyproject.toml (PEP 518/621)
            if (project_path / "pyproject.toml").exists():
                confidence += 0.20  # Increased - strong modern Python signal
            # Legacy package files
            if (project_path / "setup.py").exists():
                confidence += 0.10
            # Requirements files (pip, poetry, pipenv)
            if any((project_path / f).exists() for f in ["requirements.txt", "Pipfile", "poetry.lock"]):
                confidence += 0.10  # Increased - any package manager is strong signal

        except Exception:
            # If Phase 1 fails, continue with Phase 2
            pass

        try:
            # Phase 2: Extensions (0.4 max) - Count .py files for signal strength
            py_files = list(project_path.glob("**/*.py"))
            py_file_count = len(py_files)

            if py_file_count > 0:
                # Scale confidence by file count (stronger signal with more files)
                if py_file_count >= 50:
                    confidence += 0.40  # Definitely a Python project
                elif py_file_count >= 20:
                    confidence += 0.35  # Likely a Python project
                elif py_file_count >= 10:
                    confidence += 0.30  # Probably a Python project
                else:
                    confidence += 0.20  # May be a Python project

        except Exception:
            # If Phase 2 fails, continue with Phase 3
            pass

        try:
            # Phase 3: Structure (0.3 max)
            if (project_path / "tests").exists() or (project_path / "test").exists():
                confidence += 0.10
            # Virtual environments (may be filtered by gitignore)
            if any((project_path / venv).exists() for venv in ["venv", ".venv", "env"]):
                confidence += 0.10
            # Package directories (src/ or named packages like agentpm/, django/, etc.)
            if (project_path / "src").exists():
                confidence += 0.10
            else:
                # Check for package directories with __init__.py
                try:
                    for p in project_path.iterdir():
                        if not p.name.startswith('.') and p.is_dir() and (p / "__init__.py").exists():
                            confidence += 0.10
                            break
                except Exception:
                    # Directory iteration failed, skip package dir detection
                    pass

        except Exception:
            # If Phase 3 fails, return current confidence
            pass

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract Python project facts using shared utilities.

        Returns technical facts about Python project configuration,
        dependencies, structure, and standards.
        """
        facts = {}

        # Technical Foundation
        facts['language'] = 'Python'
        facts['python_version'] = self._get_python_version(project_path)
        facts['package_manager'] = self._detect_package_manager(project_path)
        facts['package_files'] = self._get_package_files(project_path)

        # Dependencies (using shared parser)
        facts['dependencies'] = self._extract_dependencies(project_path)

        # Project Structure (using shared analyzer)
        facts['project_structure'] = self._analyze_structure(project_path)

        # Code Standards
        facts['code_standards'] = self._detect_code_standards(project_path)

        # Environment
        facts['virtual_env'] = self._detect_virtual_env(project_path)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate Python code amalgamations using shared utilities.

        Returns code groupings for agent reference.
        """
        # Use shared extraction utilities
        return {
            'classes': extract_python_classes(project_path, max_files=100),
            'functions': extract_python_functions(project_path, max_files=100),
            'imports': extract_python_imports(project_path)
        }

    # ========== Python-Specific Helpers ==========

    def _get_python_version(self, project_path: Path) -> Optional[str]:
        """Extract Python version from pyproject.toml"""
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            match = re.search(r'python\s*=\s*["\'][\^>=]*(\d+\.\d+)', content)
            if match:
                return match.group(1)
        return None

    def _detect_package_manager(self, project_path: Path) -> str:
        """Detect Python package manager"""
        if (project_path / 'poetry.lock').exists():
            return 'poetry'
        elif (project_path / 'Pipfile').exists() or (project_path / 'Pipfile.lock').exists():
            return 'pipenv'
        elif (project_path / 'conda.yaml').exists() or (project_path / 'environment.yml').exists():
            return 'conda'
        elif (project_path / 'requirements.txt').exists():
            return 'pip'
        return 'unknown'

    def _get_package_files(self, project_path: Path) -> List[str]:
        """Get list of Python package management files"""
        return find_config_files(project_path, [
            'pyproject.toml', 'poetry.lock',
            'requirements.txt', 'requirements-dev.txt',
            'Pipfile', 'Pipfile.lock',
            'setup.py', 'setup.cfg'
        ])

    def _extract_dependencies(self, project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """Extract dependencies using shared parsers"""
        # Try Poetry format first
        deps = TomlDependencyParser.parse_poetry_deps(project_path)

        # Fallback to requirements.txt
        if not deps['runtime']:
            deps = TextDependencyParser.parse_requirements_txt(project_path)

        return deps

    def _analyze_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Python project structure using shared utilities"""
        # Use shared detector
        structure = detect_project_pattern(
            project_path,
            package_indicator_file='__init__.py',
            source_dir_names=['src', 'lib']
        )

        # Add test directory
        test_dir = discover_test_directory(project_path)
        if test_dir:
            structure['test_directory'] = test_dir

        # Find Python entry points
        entry_points = find_entry_points(project_path, [
            'cli.py', 'main.py', '__main__.py', 'app.py'
        ])
        structure['entry_points'] = entry_points

        # Discover key modules
        if 'source_directory' in structure:
            source_dir = project_path / structure['source_directory']
            key_modules = discover_key_modules(
                source_dir,
                max_depth=2,
                min_files=1,
                file_extension='.py'
            )
            structure['key_modules'] = [str(Path(m).relative_to(project_path)) for m in key_modules]

        return structure

    def _detect_code_standards(self, project_path: Path) -> Dict[str, Optional[str]]:
        """Detect Python code quality tools"""
        standards = {}

        # Formatter
        if (project_path / '.black').exists():
            standards['formatter'] = 'black'
            standards['formatter_config'] = '.black'
        elif (project_path / 'pyproject.toml').exists():
            content = (project_path / 'pyproject.toml').read_text()
            if '[tool.black]' in content:
                standards['formatter'] = 'black'
                standards['formatter_config'] = 'pyproject.toml'
            elif '[tool.yapf]' in content:
                standards['formatter'] = 'yapf'
                standards['formatter_config'] = 'pyproject.toml'
        else:
            standards['formatter'] = None

        # Linter
        linter_configs = find_config_files(project_path, [
            'ruff.toml', '.ruff.toml', '.flake8', 'pylintrc'
        ])
        if linter_configs:
            if 'ruff' in linter_configs[0]:
                standards['linter'] = 'ruff'
            elif 'flake8' in linter_configs[0]:
                standards['linter'] = 'flake8'
            elif 'pylint' in linter_configs[0]:
                standards['linter'] = 'pylint'
            standards['linter_config'] = linter_configs[0]
        else:
            standards['linter'] = None

        # Type checker
        type_configs = find_config_files(project_path, ['mypy.ini', '.mypy.ini'])
        if type_configs:
            standards['type_checker'] = 'mypy'
            standards['type_checker_config'] = type_configs[0]
        else:
            standards['type_checker'] = None

        # Test framework
        test_configs = find_config_files(project_path, [
            'pytest.ini', 'setup.cfg', 'tox.ini'
        ])
        if test_configs or self._has_pytest_in_deps(project_path):
            standards['test_framework'] = 'pytest'
            standards['test_config'] = test_configs[0] if test_configs else 'pyproject.toml'

            # Extract coverage target if configured
            standards['coverage_target'] = self._extract_coverage_target(project_path)
        else:
            standards['test_framework'] = 'unittest'

        return standards

    def _has_pytest_in_deps(self, project_path: Path) -> bool:
        """Check if pytest in dependencies"""
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists() and 'pytest' in req_file.read_text().lower():
            return True

        # Check pyproject.toml
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists() and 'pytest' in pyproject.read_text().lower():
            return True

        return False

    def _extract_coverage_target(self, project_path: Path) -> Optional[str]:
        """Extract coverage target from pytest config"""
        # Check pytest.ini
        pytest_ini = project_path / 'pytest.ini'
        if pytest_ini.exists():
            content = pytest_ini.read_text()
            match = re.search(r'--cov-fail-under[=\s]+(\d+)', content)
            if match:
                return f'{match.group(1)}%'

        # Check pyproject.toml
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            match = re.search(r'fail_under\s*=\s*(\d+)', content)
            if match:
                return f'{match.group(1)}%'

        return None

    def _detect_virtual_env(self, project_path: Path) -> Dict[str, Any]:
        """Detect Python virtual environment"""
        venv_names = ['venv', '.venv', 'env', '.env', 'virtualenv']

        for venv_name in venv_names:
            venv_path = project_path / venv_name
            if venv_path.is_dir():
                # Check for Python binary (Unix or Windows)
                if (venv_path / 'bin' / 'python').exists():
                    return {'detected': True, 'path': str(venv_path), 'type': 'venv'}
                elif (venv_path / 'Scripts' / 'python.exe').exists():
                    return {'detected': True, 'path': str(venv_path), 'type': 'venv'}

        return {'detected': False, 'path': None, 'type': None}