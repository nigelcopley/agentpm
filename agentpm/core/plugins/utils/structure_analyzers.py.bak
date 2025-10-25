"""
Project Structure Analysis Utilities

Reusable utilities for analyzing project directory structure and organization.

Used by multiple plugins to understand project layout.

Pattern: Language-agnostic with configurable indicators
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


def detect_project_pattern(
    project_path: Path,
    package_indicator_file: str = '__init__.py',
    source_dir_names: List[str] = None
) -> Dict[str, Any]:
    """
    Detect project structure pattern.

    Patterns:
    - src-layout: Has src/ directory with code
    - package: Has package directory with __init__.py
    - flat: Code files in root

    Args:
        project_path: Path to project
        package_indicator_file: File that indicates package (e.g., __init__.py for Python, package.json for JS)
        source_dir_names: Common source directory names (default: ['src', 'lib', 'app'])

    Returns:
        {
            'pattern': 'src-layout' | 'package' | 'flat',
            'source_directory': 'src/' | 'package_name/' | None,
            'package_name': 'mypackage' | None
        }
    """
    if source_dir_names is None:
        source_dir_names = ['src', 'lib', 'app', 'source']

    structure = {}

    # Check for src-layout
    for src_name in source_dir_names:
        src_dir = project_path / src_name
        if src_dir.is_dir():
            structure['pattern'] = 'src-layout'
            structure['source_directory'] = f'{src_name}/'
            return structure

    # Check for package layout
    package_dirs = [
        d for d in project_path.iterdir()
        if d.is_dir()
        and (d / package_indicator_file).exists()
        and d.name not in ['tests', 'test', 'venv', '.venv', 'node_modules', 'docs']
    ]

    if package_dirs:
        structure['pattern'] = 'package'
        structure['package_name'] = package_dirs[0].name
        structure['source_directory'] = f'{package_dirs[0].name}/'
        return structure

    # Flat structure
    structure['pattern'] = 'flat'
    return structure


def find_entry_points(
    project_path: Path,
    entry_file_patterns: List[str]
) -> Dict[str, str]:
    """
    Find entry point files.

    Args:
        project_path: Path to project
        entry_file_patterns: List of entry point file names to check

    Returns:
        Dictionary mapping entry type to file path

    Example:
        entry_file_patterns = ['cli.py', 'main.py', '__main__.py', 'app.py']
        Returns: {'cli': 'cli.py', 'main': '__main__.py'}
    """
    entry_points = {}

    # Map common patterns to entry types
    pattern_map = {
        'cli.py': 'cli',
        'main.py': 'main',
        '__main__.py': 'main',
        'app.py': 'app',
        'index.js': 'main',
        'server.js': 'server',
        'main.go': 'main',
        'main.rs': 'main'
    }

    for pattern in entry_file_patterns:
        if (project_path / pattern).exists():
            entry_type = pattern_map.get(pattern, pattern.split('.')[0])
            entry_points[entry_type] = pattern

    return entry_points


def discover_test_directory(project_path: Path) -> Optional[str]:
    """
    Find test directory.

    Checks common test directory names.

    Returns:
        Test directory path or None
    """
    test_dirs = ['tests', 'test', '__tests__', 'spec', 'specs']

    for test_dir in test_dirs:
        if (project_path / test_dir).is_dir():
            return f'{test_dir}/'

    return None


def discover_key_modules(
    source_directory: Path,
    max_depth: int = 2,
    min_files: int = 1,
    file_extension: str = '.py'
) -> List[str]:
    """
    Discover key modules/packages in source directory.

    Args:
        source_directory: Path to source directory
        max_depth: Maximum depth to scan
        min_files: Minimum files for directory to be considered a module
        file_extension: File extension to count (e.g., '.py', '.js')

    Returns:
        List of key module paths
    """
    if not source_directory.exists():
        return []

    key_modules = []

    for subdir in source_directory.iterdir():
        if subdir.is_dir():
            # Count relevant files in this directory
            files = list(subdir.glob(f'**/*{file_extension}'))
            if len(files) >= min_files:
                key_modules.append(str(subdir))

    return sorted(key_modules)[:10]  # Return top 10


def find_config_files(
    project_path: Path,
    config_patterns: List[str]
) -> List[str]:
    """
    Find configuration files matching patterns.

    Args:
        project_path: Path to project
        config_patterns: List of config file patterns

    Returns:
        List of found config files

    Example:
        config_patterns = ['pytest.ini', 'setup.cfg', '.flake8']
        Returns: ['pytest.ini', 'setup.cfg']
    """
    found = []

    for pattern in config_patterns:
        if (project_path / pattern).exists():
            found.append(pattern)

    return found


def detect_build_tool(project_path: Path, build_files: Dict[str, str]) -> Optional[str]:
    """
    Detect build tool from build files.

    Args:
        project_path: Path to project
        build_files: Mapping of file -> tool name

    Returns:
        Build tool name or None

    Example:
        build_files = {
            'Makefile': 'make',
            'build.gradle': 'gradle',
            'pom.xml': 'maven'
        }
    """
    for build_file, tool_name in build_files.items():
        if (project_path / build_file).exists():
            return tool_name

    return None


def analyze_directory_stats(directory: Path, file_extension: str = '.py') -> Dict[str, int]:
    """
    Analyze directory statistics.

    Args:
        directory: Path to directory
        file_extension: File extension to analyze

    Returns:
        {
            'total_files': 145,
            'total_lines': 12500,
            'avg_file_size': 86  # lines per file
        }
    """
    if not directory.exists():
        return {'total_files': 0, 'total_lines': 0, 'avg_file_size': 0}

    files = list(directory.glob(f'**/*{file_extension}'))

    # Filter out non-project files
    from .code_extractors import filter_project_files
    files = filter_project_files(files)

    total_lines = 0
    for file in files:
        try:
            total_lines += len(file.read_text(errors='ignore').split('\n'))
        except Exception:
            continue

    total_files = len(files)
    avg_size = total_lines // total_files if total_files > 0 else 0

    return {
        'total_files': total_files,
        'total_lines': total_lines,
        'avg_file_size': avg_size
    }