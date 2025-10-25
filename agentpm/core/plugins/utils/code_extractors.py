"""
Code Extraction Utilities

Reusable utilities for extracting code definitions from source files.

Used by multiple plugins to generate code amalgamations.

Pattern: Generic extraction with language-specific configuration
"""

from pathlib import Path
from typing import List, Set, Callable
from datetime import datetime
import re


def filter_project_files(
    files: List[Path],
    exclude_patterns: List[str] = None
) -> List[Path]:
    """
    Filter out non-project files (venv, caches, build artifacts).

    Args:
        files: List of file paths
        exclude_patterns: Patterns to exclude (default: common excludes)

    Returns:
        Filtered list of project files
    """
    if exclude_patterns is None:
        exclude_patterns = [
            'venv', '.venv', 'env', 'virtualenv',
            '__pycache__', '.pyc', '.pyo',
            'node_modules', 'bower_components',
            '.git', '.svn', '.hg',
            'site-packages', 'dist', 'build',
            'target',  # Rust/Java
            'vendor',  # PHP/Go
        ]

    return [
        f for f in files
        if not any(pattern in str(f) for pattern in exclude_patterns)
    ]


def extract_definitions(
    project_path: Path,
    file_pattern: str,
    definition_regex: str,
    definition_name: str,
    max_files: int = 100,
    exclude_patterns: List[str] = None,
    extract_body: bool = True
) -> str:
    """
    Generic code definition extractor.

    Extracts classes, functions, interfaces, etc. based on regex pattern.

    Args:
        project_path: Path to project
        file_pattern: Glob pattern for files (e.g., '**/*.py')
        definition_regex: Regex to match definitions (e.g., r'^class\\s+\\w+')
        definition_name: Name for header (e.g., 'Classes', 'Functions')
        max_files: Maximum files to process
        exclude_patterns: Patterns to exclude
        extract_body: Whether to extract full body or just signature

    Returns:
        Amalgamated code content with file references
    """
    content = f"# All {definition_name} in Project\n"
    content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Find and filter files
    all_files = list(project_path.glob(file_pattern))
    project_files = filter_project_files(all_files, exclude_patterns)

    for file_path in sorted(project_files)[:max_files]:
        try:
            file_content = file_path.read_text(errors='ignore')
            definitions = _extract_from_content(
                file_content,
                file_path,
                project_path,
                definition_regex,
                extract_body
            )
            if definitions:
                content += definitions
        except Exception:
            continue

    return content


def _extract_from_content(
    content: str,
    file_path: Path,
    project_path: Path,
    definition_regex: str,
    extract_body: bool
) -> str:
    """Extract definitions from file content"""
    result = ""
    lines = content.split('\n')
    in_definition = False
    definition_lines = []
    indent_level = 0

    for i, line in enumerate(lines):
        # Match definition start
        if re.match(definition_regex, line):
            # Save previous definition if exists
            if definition_lines:
                result += ''.join(definition_lines) + '\n\n'
                definition_lines = []

            # Start new definition
            relative_path = file_path.relative_to(project_path)
            result += f"# File: {relative_path} (line {i+1})\n"
            definition_lines = [line + '\n']

            if extract_body:
                in_definition = True
                indent_level = len(line) - len(line.lstrip())
            else:
                # Just signature
                result += line + '\n\n'
                in_definition = False
            continue

        # Collect definition body
        if in_definition and extract_body:
            current_indent = len(line) - len(line.lstrip())
            # Stop at next same-level non-comment line
            if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                in_definition = False
                continue
            definition_lines.append(line + '\n')

    # Save last definition
    if definition_lines:
        result += ''.join(definition_lines) + '\n\n'

    return result


# ========== Language-Specific Helpers ==========

def extract_python_classes(project_path: Path, max_files: int = 100) -> str:
    """Extract Python class definitions"""
    return extract_definitions(
        project_path,
        file_pattern='**/*.py',
        definition_regex=r'^class\s+\w+',
        definition_name='Python Classes',
        max_files=max_files,
        extract_body=True
    )


def extract_python_functions(project_path: Path, max_files: int = 100) -> str:
    """Extract Python module-level functions"""
    content = "# All Python Functions in Project\n"
    content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    all_files = list(project_path.glob('**/*.py'))
    project_files = filter_project_files(all_files)

    for file_path in sorted(project_files)[:max_files]:
        try:
            file_content = file_path.read_text(errors='ignore')
            functions = _extract_python_functions_from_content(file_content, file_path, project_path)
            if functions:
                content += functions
        except Exception:
            continue

    return content


def _extract_python_functions_from_content(content: str, file_path: Path, project_path: Path) -> str:
    """Extract module-level Python functions with docstrings"""
    result = ""
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match module-level function (not indented)
        if re.match(r'^def\s+\w+', line):
            relative_path = file_path.relative_to(project_path)
            result += f"# File: {relative_path} (line {i+1})\n"
            result += line + '\n'

            # Get docstring if exists
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j]
                if next_line.strip().startswith('"""') or next_line.strip().startswith("'''"):
                    result += next_line + '\n'
                    # Find end of docstring
                    for k in range(j+1, min(j+20, len(lines))):
                        result += lines[k] + '\n'
                        if '"""' in lines[k] or "'''" in lines[k]:
                            break
                    break
                elif next_line.strip() and not next_line.strip().startswith('#'):
                    break

            result += '\n'

    return result


def extract_imports(
    project_path: Path,
    file_pattern: str = '**/*.py',
    import_keywords: List[str] = None
) -> str:
    """
    Extract unique import statements.

    Args:
        project_path: Path to project
        file_pattern: Glob pattern for files
        import_keywords: Keywords that start import lines (default: ['import', 'from'])

    Returns:
        Sorted unique imports
    """
    if import_keywords is None:
        import_keywords = ['import ', 'from ']

    content = "# All Import Statements in Project\n"
    content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    imports: Set[str] = set()
    all_files = list(project_path.glob(file_pattern))
    project_files = filter_project_files(all_files)

    for file_path in project_files:
        try:
            file_content = file_path.read_text(errors='ignore')
            for line in file_content.split('\n'):
                line = line.strip()
                if any(line.startswith(kw) for kw in import_keywords):
                    imports.add(line)
        except Exception:
            continue

    # Sort and format
    for imp in sorted(imports):
        content += imp + '\n'

    return content