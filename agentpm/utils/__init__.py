"""
APM (Agent Project Manager) Utilities

Universal utilities used across the AIPM system.
"""

from .ignore_patterns import IgnorePatternMatcher
from .dependency_graph import DependencyGraph, DependencyEdge

# AST utilities (Layer 1 - Detection Pack)
from .ast_utils import (
    parse_python_ast,
    extract_imports,
    extract_classes,
    extract_functions,
    calculate_complexity,
    extract_variables,
)

# Graph builders (Layer 1 - Detection Pack)
from .graph_builders import (
    build_import_graph,
    build_dependency_graph,
    detect_cycles,
    calculate_coupling_metrics,
    graph_to_dict,
    dict_to_graph,
    calculate_graph_metrics,
    find_root_nodes,
    find_leaf_nodes,
    find_isolated_nodes,
    get_node_depth,
    GraphSizeLimitError,
)

# Metrics calculator (Layer 1 - Detection Pack)
from .metrics_calculator import (
    count_lines,
    calculate_cyclomatic_complexity,
    calculate_maintainability_index,
    aggregate_file_metrics,
    calculate_size_metrics,
)

# Pattern matchers (Layer 1 - Detection Pack)
from .pattern_matchers import (
    detect_hexagonal_architecture,
    detect_layered_architecture,
    detect_ddd_patterns,
    detect_cqrs_pattern,
    detect_mvc_pattern,
    detect_pattern_violations,
)

# File parsers (Layer 1 - Detection Pack)
from .file_parsers import (
    parse_toml,
    parse_yaml,
    parse_json,
    parse_ini,
    parse_python_dependencies,
    parse_javascript_dependencies,
    parse_requirements_txt,
    parse_setup_py_safe,
    TOML_AVAILABLE,
    YAML_AVAILABLE,
)

__all__ = [
    # Core utilities
    'IgnorePatternMatcher',
    'DependencyGraph',
    'DependencyEdge',
    # AST utilities
    'parse_python_ast',
    'extract_imports',
    'extract_classes',
    'extract_functions',
    'calculate_complexity',
    'extract_variables',
    # Graph builders
    'build_import_graph',
    'build_dependency_graph',
    'detect_cycles',
    'calculate_coupling_metrics',
    'graph_to_dict',
    'dict_to_graph',
    'calculate_graph_metrics',
    'find_root_nodes',
    'find_leaf_nodes',
    'find_isolated_nodes',
    'get_node_depth',
    'GraphSizeLimitError',
    # Metrics calculator
    'count_lines',
    'calculate_cyclomatic_complexity',
    'calculate_maintainability_index',
    'aggregate_file_metrics',
    'calculate_size_metrics',
    # Pattern matchers
    'detect_hexagonal_architecture',
    'detect_layered_architecture',
    'detect_ddd_patterns',
    'detect_cqrs_pattern',
    'detect_mvc_pattern',
    'detect_pattern_violations',
    # File parsers
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
