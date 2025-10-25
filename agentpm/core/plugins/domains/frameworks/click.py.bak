"""
Click Plugin - CLI Framework Context Extraction

Extracts Click CLI framework configuration and command structure.

Provides:
1. Project facts (Click version, command structure, option patterns)
2. Code amalgamations (commands, groups, decorators)

Pattern: BasePlugin implementation
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory
from ...utils import find_config_files, filter_project_files


class ClickPlugin(BasePlugin):
    """
    Click CLI framework plugin for context extraction.

    Provides:
    1. CLI framework facts (version, structure, commands)
    2. Command code amalgamations (all commands and groups)
    """

    @property
    def plugin_id(self) -> str:
        return "framework:click"

    @property
    def enriches(self) -> str:
        return "click"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.FRAMEWORK

    def detect(self, project_path: Path) -> float:
        """Detect Click CLI framework presence."""
        confidence = 0.0

        # Phase 1: Files - Check dependencies
        for req_file in ['requirements.txt', 'pyproject.toml', 'setup.py']:
            try:
                file_path = project_path / req_file
                if file_path.exists():
                    content = file_path.read_text()
                    if 'click' in content.lower():
                        confidence += 0.15
                        break
            except Exception:
                continue

        # Phase 2: Imports (strongest signal)
        # Look in common CLI directory patterns (including nested packages)
        cli_patterns = ['**/cli/**/*.py', '**/commands/**/*.py', '**/cmd/**/*.py', 'cli.py', 'main.py']
        cli_files = []
        for pattern in cli_patterns:
            cli_files.extend(project_path.glob(pattern))

        # Sample CLI files first (more likely to have Click), then other Python files
        py_files = list(cli_files[:30]) + list(project_path.glob("**/*.py"))[:20]

        for py_file in py_files:
            try:
                content = py_file.read_text()
                if "import click" in content or "from click" in content:
                    confidence += 0.40
                    break
            except Exception:
                continue

        # Phase 3: Structure - Click decorators (stronger check with more samples)
        for py_file in py_files[:20]:  # Increased from 5 to 20
            try:
                content = py_file.read_text()
                if "@click.command" in content or "@click.group" in content:
                    confidence += 0.30
                    break
            except Exception:
                continue

        return min(confidence, 1.0)

    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        """
        Extract Click framework facts.

        Returns CLI framework configuration and command structure.
        """
        facts = {}

        # Framework info
        facts['framework'] = 'Click'
        facts['click_version'] = self._get_click_version(project_path)

        # Command structure
        facts['command_structure'] = self._analyze_command_structure(project_path)

        # CLI patterns
        facts['cli_patterns'] = self._detect_cli_patterns(project_path)

        # Entry point
        facts['cli_entry_point'] = self._find_cli_entry_point(project_path)

        return facts

    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        """
        Generate Click code amalgamations.

        Returns CLI command and group definitions.
        """
        amalgamations = {}

        # Collect all Click commands
        amalgamations['commands'] = self._collect_commands(project_path)

        # Collect command groups
        amalgamations['groups'] = self._collect_groups(project_path)

        # Collect Click decorators usage
        amalgamations['decorators'] = self._collect_decorators(project_path)

        return amalgamations

    # ========== Fact Extraction Helpers ==========

    def _get_click_version(self, project_path: Path) -> Optional[str]:
        """Extract Click version from dependencies"""
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            content = req_file.read_text()
            match = re.search(r'click[>=<]+(\d+\.\d+)', content)
            if match:
                return match.group(1)

        # Check pyproject.toml
        pyproject = project_path / 'pyproject.toml'
        if pyproject.exists():
            content = pyproject.read_text()
            match = re.search(r'click\s*=\s*["\'][\^>=]*(\d+\.\d+)', content)
            if match:
                return match.group(1)

        return None

    def _find_cli_entry_point(self, project_path: Path) -> Optional[str]:
        """Find main CLI entry point file"""
        cli_files = ['cli.py', 'main.py', '__main__.py', 'app.py']

        for cli_file in cli_files:
            if (project_path / cli_file).exists():
                return cli_file

        # Check in package directory
        for subdir in project_path.iterdir():
            if subdir.is_dir() and (subdir / '__init__.py').exists():
                for cli_file in cli_files:
                    if (subdir / cli_file).exists():
                        return f'{subdir.name}/{cli_file}'

        return None

    def _analyze_command_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Click command structure"""
        structure = {
            'type': None,
            'commands': [],
            'groups': []
        }

        # Find Python files with Click usage
        py_files = list(project_path.glob('**/*.py'))
        py_files = filter_project_files(py_files)

        has_groups = False
        commands_found = []
        groups_found = []

        for py_file in py_files:
            try:
                content = py_file.read_text(errors='ignore')

                # Check for @click.group
                if '@click.group' in content:
                    has_groups = True
                    # Find group names
                    group_matches = re.findall(r'@click\.group[^\n]*\ndef\s+(\w+)', content)
                    groups_found.extend(group_matches)

                # Find commands
                command_matches = re.findall(r'@click\.command[^\n]*\ndef\s+(\w+)', content)
                commands_found.extend(command_matches)

            except Exception:
                continue

        structure['type'] = 'group-based' if has_groups else 'flat'
        structure['commands'] = sorted(set(commands_found))
        structure['groups'] = sorted(set(groups_found))
        structure['total_commands'] = len(set(commands_found))

        return structure

    def _detect_cli_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Detect Click usage patterns"""
        patterns = {
            'uses_context': False,
            'uses_options': False,
            'uses_arguments': False,
            'uses_pass_decorator': False
        }

        py_files = list(project_path.glob('**/*.py'))
        py_files = filter_project_files(py_files)

        for py_file in py_files[:20]:  # Sample first 20 files
            try:
                content = py_file.read_text(errors='ignore')

                if '@click.pass_context' in content or '@click.pass_obj' in content:
                    patterns['uses_context'] = True

                if '@click.option' in content:
                    patterns['uses_options'] = True

                if '@click.argument' in content:
                    patterns['uses_arguments'] = True

                if 'pass_' in content and 'click' in content:
                    patterns['uses_pass_decorator'] = True

            except Exception:
                continue

        return patterns

    # ========== Code Amalgamation Helpers ==========

    def _collect_commands(self, project_path: Path) -> str:
        """Collect all Click command definitions"""
        content = "# All Click Commands\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        py_files = list(project_path.glob('**/*.py'))
        py_files = filter_project_files(py_files)

        for py_file in sorted(py_files):
            try:
                file_content = py_file.read_text(errors='ignore')

                # Find @click.command decorated functions
                if '@click.command' in file_content:
                    relative_path = py_file.relative_to(project_path)
                    content += f"\n# File: {relative_path}\n"

                    # Extract command definitions with decorators
                    lines = file_content.split('\n')
                    for i, line in enumerate(lines):
                        if '@click.command' in line or '@click.option' in line or '@click.argument' in line:
                            content += line + '\n'
                        elif line.strip().startswith('def ') and i > 0 and '@click' in lines[i-1]:
                            content += line + '\n'
                            # Get docstring
                            if i + 1 < len(lines) and '"""' in lines[i+1]:
                                for j in range(i+1, min(i+10, len(lines))):
                                    content += lines[j] + '\n'
                                    if j > i+1 and '"""' in lines[j]:
                                        break
                            content += '\n'

            except Exception:
                continue

        return content

    def _collect_groups(self, project_path: Path) -> str:
        """Collect all Click group definitions"""
        content = "# All Click Groups\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        py_files = list(project_path.glob('**/*.py'))
        py_files = filter_project_files(py_files)

        for py_file in sorted(py_files):
            try:
                file_content = py_file.read_text(errors='ignore')

                if '@click.group' in file_content:
                    relative_path = py_file.relative_to(project_path)
                    content += f"\n# File: {relative_path}\n"

                    # Extract group definitions
                    lines = file_content.split('\n')
                    for i, line in enumerate(lines):
                        if '@click.group' in line:
                            content += line + '\n'
                            if i + 1 < len(lines) and line.strip().startswith('def '):
                                content += lines[i+1] + '\n\n'

            except Exception:
                continue

        return content

    def _collect_decorators(self, project_path: Path) -> str:
        """Collect Click decorator usage patterns"""
        content = "# Click Decorator Patterns\n"
        content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        decorators = set()
        py_files = list(project_path.glob('**/*.py'))
        py_files = filter_project_files(py_files)

        for py_file in py_files:
            try:
                file_content = py_file.read_text(errors='ignore')
                # Find all @click.* decorators
                click_decorators = re.findall(r'@click\.\w+[^\n]*', file_content)
                decorators.update(click_decorators)
            except Exception:
                continue

        for dec in sorted(decorators):
            content += dec + '\n'

        return content


# Import datetime for timestamps
from datetime import datetime