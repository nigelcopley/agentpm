"""
File Parsing Utilities for APM (Agent Project Manager) Detection Pack

Layer 1 (Shared Utilities) - Configuration file parsing primitives.
NO dependencies on plugins or detection services.

Provides safe parsing for:
- TOML (pyproject.toml, Cargo.toml, config files)
- YAML (.gitlab-ci.yml, docker-compose.yml, workflows)
- JSON (package.json, tsconfig.json, config files)
- INI/CFG (setup.cfg, tox.ini, .coveragerc)
- Requirements.txt (Python dependencies)
- Setup.py (AST-based, no execution)

Example Usage:
    >>> from agentpm.core.plugins.utils.file_parsers import (
    ...     parse_toml, parse_python_dependencies
    ... )
    >>>
    >>> # Parse pyproject.toml
    >>> config = parse_toml(Path("pyproject.toml"))
    >>> if config:
    ...     print(config.get("tool", {}).get("poetry", {}).get("name"))
    >>>
    >>> # Extract all Python dependencies
    >>> deps = parse_python_dependencies(Path("."))
    >>> print(f"Runtime: {deps['runtime']}")
    >>> print(f"Dev: {deps['dev']}")
    >>> print(f"Source: {deps['source']}")

Performance:
- Parse <50ms per file
- Handle files up to 1MB
- Efficient regex compilation

Safety:
- NO code execution (setup.py parsed via AST only)
- YAML safe_load only (no unsafe deserialization)
- Graceful degradation if optional deps missing

Version: 1.0.0
"""

import ast
import json
import re
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ========== Optional Dependencies with Graceful Degradation ==========

# TOML support (Python 3.11+ has tomllib, otherwise use tomli/toml)
TOML_AVAILABLE = False
tomli = None

try:
    import tomllib as tomli  # Python 3.11+
    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli  # Backport for Python <3.11
        TOML_AVAILABLE = True
    except ImportError:
        try:
            import toml as tomli  # Fallback to older toml library
            TOML_AVAILABLE = True
        except ImportError:
            pass

# YAML support
YAML_AVAILABLE = False
yaml = None

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    pass


# ========== Compiled Regex Patterns (Performance Optimization) ==========

# Requirements.txt patterns
REQUIREMENT_PATTERN = re.compile(
    r'^([a-zA-Z0-9_\-\.]+)'  # Package name
    r'(?:\[([^\]]+)\])?'      # Optional extras: [dev,test]
    r'\s*'
    r'((?:[><=!]+)[\d\.\*]+(?:,\s*[><=!]+[\d\.\*]+)*)?'  # Version specifiers
)

GIT_REQUIREMENT_PATTERN = re.compile(
    r'^(?:-e\s+)?'
    r'git\+https?://[^\s#]+'
    r'(?:#egg=([a-zA-Z0-9_\-]+))?'
)

LOCAL_REQUIREMENT_PATTERN = re.compile(
    r'^-e\s+\.?/.*'
)

# Setup.py AST extraction patterns
SETUP_CALL_KEYWORDS = {'name', 'version', 'install_requires', 'extras_require', 'python_requires'}


# ========== Core File Parsers ==========

def parse_toml(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse TOML file safely.

    Uses tomli (Python 3.11+) or toml library.

    Args:
        file_path: Path to TOML file

    Returns:
        Parsed dict or None if parse fails

    Handles:
        - pyproject.toml (Poetry, setuptools)
        - Cargo.toml (Rust - future)
        - Config files

    Example:
        >>> config = parse_toml(Path("pyproject.toml"))
        >>> if config:
        ...     print(config["tool"]["poetry"]["name"])
    """
    if not TOML_AVAILABLE:
        return None

    if not file_path.exists():
        return None

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return None

        # Python 3.11+ tomllib requires binary mode
        if hasattr(tomli, 'load'):
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        else:
            # Older toml library uses text mode
            with open(file_path, 'r', encoding='utf-8') as f:
                return tomli.load(f)

    except (OSError, IOError, UnicodeDecodeError):
        return None
    except Exception:  # Catch all TOML parsing errors
        return None


def parse_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse YAML file safely.

    Uses PyYAML with safe_load (no code execution).

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed dict or None if parse fails

    Handles:
        - .gitlab-ci.yml
        - .github/workflows/*.yml
        - docker-compose.yml
        - Config files

    Example:
        >>> config = parse_yaml(Path(".gitlab-ci.yml"))
        >>> if config:
        ...     print(config.get("stages", []))
    """
    if not YAML_AVAILABLE:
        return None

    if not file_path.exists():
        return None

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            # Use safe_load to prevent code execution
            data = yaml.safe_load(f)

        # safe_load can return None for empty files
        if data is None:
            return {}

        return data if isinstance(data, dict) else None

    except (OSError, IOError, UnicodeDecodeError):
        return None
    except yaml.YAMLError:
        return None
    except Exception:
        return None


def parse_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse JSON file safely.

    Uses standard library json module.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed dict or None if parse fails

    Handles:
        - package.json
        - tsconfig.json
        - .eslintrc.json
        - Config files

    Example:
        >>> config = parse_json(Path("package.json"))
        >>> if config:
        ...     print(config.get("name"))
        ...     print(config.get("dependencies", {}).keys())
    """
    if not file_path.exists():
        return None

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data if isinstance(data, dict) else None

    except (OSError, IOError, UnicodeDecodeError):
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def parse_ini(file_path: Path) -> Optional[Dict[str, Dict[str, str]]]:
    """
    Parse INI/CFG file.

    Uses configparser from standard library.

    Args:
        file_path: Path to INI file

    Returns:
        Dict mapping section -> {key: value} or None

    Handles:
        - setup.cfg
        - tox.ini
        - .coveragerc
        - Config files

    Example:
        >>> config = parse_ini(Path("setup.cfg"))
        >>> if config:
        ...     metadata = config.get("metadata", {})
        ...     print(metadata.get("name"))
    """
    if not file_path.exists():
        return None

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return None

        parser = ConfigParser()
        parser.read(file_path, encoding='utf-8')

        # Convert to nested dict
        result = {}
        for section in parser.sections():
            result[section] = dict(parser.items(section))

        return result

    except (OSError, IOError, UnicodeDecodeError):
        return None
    except Exception:  # Catch configparser errors
        return None


# ========== Dependency Extraction Functions ==========

def parse_python_dependencies(project_path: Path) -> Dict[str, Any]:
    """
    Extract Python dependencies from project.

    Checks multiple sources (in priority order):
    1. pyproject.toml [tool.poetry.dependencies]
    2. pyproject.toml [project.dependencies]
    3. requirements.txt
    4. setup.py (parse, don't execute)

    Args:
        project_path: Root directory of Python project

    Returns:
        {
            'runtime': [list of runtime deps],
            'dev': [list of dev deps],
            'source': 'pyproject.toml' | 'requirements.txt' | 'setup.py' | 'none'
        }

    Example:
        >>> deps = parse_python_dependencies(Path("."))
        >>> print(f"Found {len(deps['runtime'])} runtime dependencies")
        >>> print(f"Source: {deps['source']}")
        >>> for dep in deps['runtime']:
        ...     print(f"  {dep}")
    """
    result = {
        'runtime': [],
        'dev': [],
        'source': 'none'
    }

    # Priority 1: pyproject.toml (Poetry format)
    pyproject_path = project_path / 'pyproject.toml'
    if pyproject_path.exists():
        pyproject = parse_toml(pyproject_path)
        if pyproject:
            # Try Poetry format first
            poetry_deps = pyproject.get('tool', {}).get('poetry', {})
            if 'dependencies' in poetry_deps:
                for name, version in poetry_deps['dependencies'].items():
                    if name.lower() != 'python':
                        result['runtime'].append(name)
                result['source'] = 'pyproject.toml'

            # Poetry dev dependencies
            dev_deps = poetry_deps.get('dev-dependencies', {})
            for name in dev_deps.keys():
                result['dev'].append(name)

            # Poetry group dependencies
            groups = poetry_deps.get('group', {})
            for group_name, group_data in groups.items():
                if group_name == 'dev':
                    for name in group_data.get('dependencies', {}).keys():
                        result['dev'].append(name)

            if result['runtime'] or result['dev']:
                return result

            # Try PEP 621 format (project.dependencies)
            project_deps = pyproject.get('project', {})
            if 'dependencies' in project_deps:
                for dep in project_deps['dependencies']:
                    # Extract package name (before any version specifier)
                    match = REQUIREMENT_PATTERN.match(dep)
                    if match:
                        result['runtime'].append(match.group(1))
                result['source'] = 'pyproject.toml'

            # PEP 621 optional dependencies
            optional_deps = project_deps.get('optional-dependencies', {})
            for group_name, deps in optional_deps.items():
                if group_name in ('dev', 'test', 'docs'):
                    for dep in deps:
                        match = REQUIREMENT_PATTERN.match(dep)
                        if match:
                            result['dev'].append(match.group(1))

            if result['runtime'] or result['dev']:
                return result

    # Priority 2: requirements.txt
    req_path = project_path / 'requirements.txt'
    if req_path.exists():
        req_data = parse_requirements_txt(req_path)
        result['runtime'] = [dep['name'] for dep in req_data]
        result['source'] = 'requirements.txt'

        # Check for dev requirements files
        for dev_file in ['requirements-dev.txt', 'dev-requirements.txt', 'test-requirements.txt']:
            dev_path = project_path / dev_file
            if dev_path.exists():
                dev_data = parse_requirements_txt(dev_path)
                result['dev'].extend([dep['name'] for dep in dev_data])

        if result['runtime']:
            return result

    # Priority 3: setup.py (AST parsing, no execution)
    setup_path = project_path / 'setup.py'
    if setup_path.exists():
        setup_data = parse_setup_py_safe(setup_path)
        if setup_data:
            # Extract package names from install_requires (may include version specs)
            install_requires = setup_data.get('install_requires', [])
            for dep in install_requires:
                match = REQUIREMENT_PATTERN.match(dep)
                if match:
                    result['runtime'].append(match.group(1))
                else:
                    # Fallback: simple name extraction
                    name = dep.split('>=')[0].split('==')[0].split('<')[0].strip()
                    if name:
                        result['runtime'].append(name)

            # Extract dev dependencies from extras_require
            extras = setup_data.get('extras_require', {})
            for key in ('dev', 'test', 'docs', 'development'):
                if key in extras:
                    for dep in extras[key]:
                        match = REQUIREMENT_PATTERN.match(dep)
                        if match:
                            result['dev'].append(match.group(1))
                        else:
                            name = dep.split('>=')[0].split('==')[0].split('<')[0].strip()
                            if name:
                                result['dev'].append(name)

            result['source'] = 'setup.py'

            if result['runtime'] or result['dev']:
                return result

    return result


def parse_javascript_dependencies(project_path: Path) -> Dict[str, Any]:
    """
    Extract JavaScript/Node dependencies from package.json.

    Args:
        project_path: Root directory of JavaScript project

    Returns:
        {
            'runtime': [dependencies],
            'dev': [devDependencies],
            'peer': [peerDependencies],
            'optional': [optionalDependencies],
            'source': 'package.json' | 'none'
        }

    Example:
        >>> deps = parse_javascript_dependencies(Path("."))
        >>> if deps['source'] != 'none':
        ...     print(f"Runtime: {', '.join(deps['runtime'])}")
        ...     print(f"Dev: {', '.join(deps['dev'])}")
    """
    result = {
        'runtime': [],
        'dev': [],
        'peer': [],
        'optional': [],
        'source': 'none'
    }

    package_json_path = project_path / 'package.json'
    if not package_json_path.exists():
        return result

    package_json = parse_json(package_json_path)
    if not package_json:
        return result

    # Extract dependencies
    if 'dependencies' in package_json:
        result['runtime'] = list(package_json['dependencies'].keys())

    if 'devDependencies' in package_json:
        result['dev'] = list(package_json['devDependencies'].keys())

    if 'peerDependencies' in package_json:
        result['peer'] = list(package_json['peerDependencies'].keys())

    if 'optionalDependencies' in package_json:
        result['optional'] = list(package_json['optionalDependencies'].keys())

    if any([result['runtime'], result['dev'], result['peer'], result['optional']]):
        result['source'] = 'package.json'

    return result


def parse_requirements_txt(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse requirements.txt file.

    Handles:
    - Simple: package==1.0.0
    - Operators: package>=1.0.0,<2.0.0
    - Git URLs: git+https://...
    - Local paths: -e ./local_package
    - Comments and blank lines
    - Extras: package[extra1,extra2]

    Args:
        file_path: Path to requirements.txt file

    Returns:
        List of dicts: [
            {'name': 'package', 'version': '==1.0.0', 'extras': None},
            {'name': 'package2', 'version': '>=1.0.0', 'extras': ['dev', 'test']},
            ...
        ]

    Example:
        >>> deps = parse_requirements_txt(Path("requirements.txt"))
        >>> for dep in deps:
        ...     extras = f"[{','.join(dep['extras'])}]" if dep['extras'] else ""
        ...     print(f"{dep['name']}{extras} {dep['version']}")
    """
    if not file_path.exists():
        return []

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

    except (OSError, IOError, UnicodeDecodeError):
        return []

    result = []

    for line in content.split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Handle Git URLs
        git_match = GIT_REQUIREMENT_PATTERN.match(line)
        if git_match:
            egg_name = git_match.group(1) if git_match.group(1) else 'unknown'
            result.append({
                'name': egg_name,
                'version': 'git',
                'extras': None,
                'url': line.replace('-e ', '')
            })
            continue

        # Handle local paths
        if LOCAL_REQUIREMENT_PATTERN.match(line):
            # Extract name from path if possible
            path_parts = line.replace('-e ', '').split('/')
            name = path_parts[-1] if path_parts else 'local'
            result.append({
                'name': name,
                'version': 'local',
                'extras': None,
                'path': line.replace('-e ', '')
            })
            continue

        # Handle standard requirements
        match = REQUIREMENT_PATTERN.match(line)
        if match:
            name = match.group(1)
            extras_str = match.group(2)
            version_spec = match.group(3) if match.group(3) else ''

            extras = None
            if extras_str:
                extras = [e.strip() for e in extras_str.split(',')]

            result.append({
                'name': name,
                'version': version_spec if version_spec else 'any',
                'extras': extras
            })

    return result


def parse_setup_py_safe(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse setup.py WITHOUT executing it (AST-based).

    Extracts from setup() call:
    - name
    - version
    - install_requires
    - extras_require
    - python_requires

    Args:
        file_path: Path to setup.py file

    Returns:
        Dict with extracted metadata or None

    Safety: Uses AST parsing only, no exec()

    Example:
        >>> setup_data = parse_setup_py_safe(Path("setup.py"))
        >>> if setup_data:
        ...     print(f"Package: {setup_data.get('name')}")
        ...     print(f"Version: {setup_data.get('version')}")
        ...     print(f"Requires: {setup_data.get('install_requires', [])}")
    """
    if not file_path.exists():
        return None

    try:
        # Check file size (max 1MB)
        if file_path.stat().st_size > 1_048_576:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse Python AST
        tree = ast.parse(content, filename=str(file_path))

    except (OSError, IOError, UnicodeDecodeError):
        return None
    except SyntaxError:
        return None

    # Find setup() or setuptools.setup() call
    result = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if it's a setup() call
            is_setup_call = False

            if isinstance(node.func, ast.Name) and node.func.id == 'setup':
                is_setup_call = True
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr == 'setup':
                    is_setup_call = True

            if not is_setup_call:
                continue

            # Extract keyword arguments
            for keyword in node.keywords:
                if keyword.arg not in SETUP_CALL_KEYWORDS:
                    continue

                try:
                    value = _ast_literal_eval(keyword.value)
                    if value is not None:
                        result[keyword.arg] = value
                except (ValueError, TypeError):
                    continue

            # If we found a setup call with data, return it
            if result:
                return result

    return result if result else None


def _ast_literal_eval(node: ast.AST) -> Any:
    """
    Safely evaluate AST node to Python literal.

    Supports:
    - Strings, numbers, booleans
    - Lists, tuples, dicts
    - None

    Does NOT support:
    - Function calls
    - Variables
    - Expressions

    Args:
        node: AST node to evaluate

    Returns:
        Python literal value or None if not evaluable
    """
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):  # Python <3.8
        return node.s
    elif isinstance(node, ast.Num):  # Python <3.8
        return node.n
    elif isinstance(node, ast.NameConstant):  # Python <3.8
        return node.value
    elif isinstance(node, ast.List):
        return [_ast_literal_eval(elem) for elem in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(_ast_literal_eval(elem) for elem in node.elts)
    elif isinstance(node, ast.Dict):
        result = {}
        for key, value in zip(node.keys, node.values):
            key_val = _ast_literal_eval(key)
            value_val = _ast_literal_eval(value)
            if key_val is not None and value_val is not None:
                result[key_val] = value_val
        return result
    else:
        return None


# ========== Module Exports ==========

__all__ = [
    'parse_toml',
    'parse_yaml',
    'parse_json',
    'parse_ini',
    'parse_python_dependencies',
    'parse_javascript_dependencies',
    'parse_requirements_txt',
    'parse_setup_py_safe',
    'TOML_AVAILABLE',
    'YAML_AVAILABLE',
]
