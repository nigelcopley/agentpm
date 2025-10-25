"""
Plugin Utilities

Plugin-specific utilities for plugin development.

These utilities are specific to plugin implementations:
- Dependency parsing (TOML, JSON, text formats)
- Code extraction (classes, functions, imports)
- Structure analysis (project layout, entry points)

NOTE: General-purpose utilities (AST parsing, graph building, metrics, pattern matching, file parsing)
have been moved to agentpm.utils/ for use by both plugins AND detection services.

Usage:
    from agentpm.core.plugins.utils import (
        TomlDependencyParser,
        extract_python_classes,
        detect_project_pattern
    )

    deps = TomlDependencyParser.parse_poetry_deps(project_path)
    classes = extract_python_classes(project_path)
    structure = detect_project_pattern(project_path)
"""

from .dependency_parsers import (
    TomlDependencyParser,
    JsonDependencyParser,
    TextDependencyParser,
)

from .code_extractors import (
    extract_definitions,
    extract_python_classes,
    extract_python_functions,
    extract_imports,
    filter_project_files,
)

# Convenience alias
extract_python_imports = extract_imports

from .structure_analyzers import (
    detect_project_pattern,
    find_entry_points,
    discover_test_directory,
    discover_key_modules,
    find_config_files,
    detect_build_tool,
    analyze_directory_stats,
)

__all__ = [
    # Dependency parsers
    "TomlDependencyParser",
    "JsonDependencyParser",
    "TextDependencyParser",
    # Code extractors
    "extract_definitions",
    "extract_python_classes",
    "extract_python_functions",
    "extract_imports",
    "extract_python_imports",  # Alias
    "filter_project_files",
    # Structure analyzers
    "detect_project_pattern",
    "find_entry_points",
    "discover_test_directory",
    "discover_key_modules",
    "find_config_files",
    "detect_build_tool",
    "analyze_directory_stats",
]