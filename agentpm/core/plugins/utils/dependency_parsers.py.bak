"""
Dependency Parsing Utilities

Reusable parsers for dependency files across different formats and languages.

Supports:
- TOML (pyproject.toml, Cargo.toml)
- JSON (package.json, composer.json)
- Text (requirements.txt, Gemfile)

Pattern: Format-specific parsers with consistent output structure
"""

from pathlib import Path
from typing import Dict, List, Optional
import re
import json


class TomlDependencyParser:
    """Parse TOML-based dependency files"""

    @staticmethod
    def parse_poetry_deps(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Python Poetry dependencies from pyproject.toml.

        Returns:
            {'runtime': [...], 'dev': [...]}
        """
        pyproject = project_path / 'pyproject.toml'
        if not pyproject.exists():
            return {'runtime': [], 'dev': []}

        content = pyproject.read_text()
        deps = {'runtime': [], 'dev': []}

        in_deps = False
        in_dev_deps = False

        for line in content.split('\n'):
            if '[tool.poetry.dependencies]' in line:
                in_deps = True
                in_dev_deps = False
            elif '[tool.poetry.dev-dependencies]' in line or '[tool.poetry.group.dev.dependencies]' in line:
                in_deps = False
                in_dev_deps = True
            elif line.startswith('['):
                in_deps = False
                in_dev_deps = False
            elif in_deps and '=' in line:
                match = re.match(r'(\S+)\s*=\s*["\']([^"\']+)', line)
                if match and match.group(1) != 'python':
                    deps['runtime'].append({
                        'name': match.group(1),
                        'version': match.group(2),
                        'source': 'pyproject.toml'
                    })
            elif in_dev_deps and '=' in line:
                match = re.match(r'(\S+)\s*=\s*["\']([^"\']+)', line)
                if match:
                    deps['dev'].append({
                        'name': match.group(1),
                        'version': match.group(2),
                        'source': 'pyproject.toml'
                    })

        return deps

    @staticmethod
    def parse_cargo_deps(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Rust Cargo dependencies from Cargo.toml.

        Returns:
            {'runtime': [...], 'dev': [...]}
        """
        cargo_toml = project_path / 'Cargo.toml'
        if not cargo_toml.exists():
            return {'runtime': [], 'dev': []}

        content = cargo_toml.read_text()
        deps = {'runtime': [], 'dev': []}

        in_deps = False
        in_dev_deps = False

        for line in content.split('\n'):
            if '[dependencies]' in line:
                in_deps = True
                in_dev_deps = False
            elif '[dev-dependencies]' in line:
                in_deps = False
                in_dev_deps = True
            elif line.startswith('['):
                in_deps = False
                in_dev_deps = False
            elif in_deps and '=' in line:
                match = re.match(r'(\S+)\s*=\s*["\']([^"\']+)', line)
                if match:
                    deps['runtime'].append({
                        'name': match.group(1),
                        'version': match.group(2),
                        'source': 'Cargo.toml'
                    })
            elif in_dev_deps and '=' in line:
                match = re.match(r'(\S+)\s*=\s*["\']([^"\']+)', line)
                if match:
                    deps['dev'].append({
                        'name': match.group(1),
                        'version': match.group(2),
                        'source': 'Cargo.toml'
                    })

        return deps


class JsonDependencyParser:
    """Parse JSON-based dependency files"""

    @staticmethod
    def parse_npm_deps(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Node.js dependencies from package.json.

        Returns:
            {'runtime': [...], 'dev': [...]}
        """
        package_json = project_path / 'package.json'
        if not package_json.exists():
            return {'runtime': [], 'dev': []}

        try:
            data = json.loads(package_json.read_text())
            deps = {'runtime': [], 'dev': []}

            # Runtime dependencies
            if 'dependencies' in data:
                for name, version in data['dependencies'].items():
                    deps['runtime'].append({
                        'name': name,
                        'version': version,
                        'source': 'package.json'
                    })

            # Dev dependencies
            if 'devDependencies' in data:
                for name, version in data['devDependencies'].items():
                    deps['dev'].append({
                        'name': name,
                        'version': version,
                        'source': 'package.json'
                    })

            return deps

        except (json.JSONDecodeError, KeyError):
            return {'runtime': [], 'dev': []}

    @staticmethod
    def parse_composer_deps(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse PHP Composer dependencies from composer.json.

        Returns:
            {'runtime': [...], 'dev': [...]}
        """
        composer_json = project_path / 'composer.json'
        if not composer_json.exists():
            return {'runtime': [], 'dev': []}

        try:
            data = json.loads(composer_json.read_text())
            deps = {'runtime': [], 'dev': []}

            # Runtime dependencies
            if 'require' in data:
                for name, version in data['require'].items():
                    if name != 'php':  # Exclude PHP version itself
                        deps['runtime'].append({
                            'name': name,
                            'version': version,
                            'source': 'composer.json'
                        })

            # Dev dependencies
            if 'require-dev' in data:
                for name, version in data['require-dev'].items():
                    deps['dev'].append({
                        'name': name,
                        'version': version,
                        'source': 'composer.json'
                    })

            return deps

        except (json.JSONDecodeError, KeyError):
            return {'runtime': [], 'dev': []}


class TextDependencyParser:
    """Parse text-based dependency files"""

    @staticmethod
    def parse_requirements_txt(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Python requirements.txt.

        Returns:
            {'runtime': [...], 'dev': []} (dev empty for requirements.txt)
        """
        req_file = project_path / 'requirements.txt'
        if not req_file.exists():
            return {'runtime': [], 'dev': []}

        deps = {'runtime': [], 'dev': []}

        for line in req_file.read_text().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Match: package==1.2.3 or package>=1.2
                match = re.match(r'([a-zA-Z0-9_-]+)([><=!]+)([\d.]+)', line)
                if match:
                    deps['runtime'].append({
                        'name': match.group(1),
                        'version': match.group(3),
                        'source': 'requirements.txt'
                    })
                else:
                    # Just package name
                    name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if name:
                        deps['runtime'].append({
                            'name': name,
                            'version': 'latest',
                            'source': 'requirements.txt'
                        })

        return deps

    @staticmethod
    def parse_gemfile(project_path: Path) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Ruby Gemfile.

        Returns:
            {'runtime': [...], 'dev': [...]}
        """
        gemfile = project_path / 'Gemfile'
        if not gemfile.exists():
            return {'runtime': [], 'dev': []}

        deps = {'runtime': [], 'dev': []}
        in_dev_group = False

        for line in gemfile.read_text().split('\n'):
            line = line.strip()

            # Check for development group
            if 'group :development' in line or 'group :test' in line:
                in_dev_group = True
            elif line.startswith('end'):
                in_dev_group = False
            elif line.startswith('gem '):
                # Match: gem 'name', '~> 1.2.3'
                match = re.search(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?", line)
                if match:
                    dep = {
                        'name': match.group(1),
                        'version': match.group(2) if match.group(2) else 'latest',
                        'source': 'Gemfile'
                    }
                    if in_dev_group:
                        deps['dev'].append(dep)
                    else:
                        deps['runtime'].append(dep)

        return deps


# ========== Convenience Functions ==========

def extract_python_imports(project_path: Path) -> str:
    """Extract all unique Python import statements"""
    return extract_imports(
        project_path,
        file_pattern='**/*.py',
        import_keywords=['import ', 'from ']
    )