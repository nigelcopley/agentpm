"""
Built-in Fitness Policies for APM (Agent Project Manager) Detection Pack.

Provides default set of architecture fitness policies covering:
- Dependency rules (no cycles, max depth)
- Complexity limits (max complexity, max LOC per file)
- Pattern compliance (layering violations, etc.)
- Code standards (naming conventions, documentation)

Policies are categorized by tags for easy filtering:
- dependency: Dependency management
- complexity: Code complexity
- size: File/function size
- architecture: Architectural patterns
- layering: Layer violations
- maintainability: Code maintainability
- code_quality: General code quality

Author: APM (Agent Project Manager) Detection Pack Team
Layer: Layer 3 (Detection Services - Business Logic)
Version: 1.0.0
"""

from typing import List, Optional, Dict, Any

# Import from database layer (Layer 2)
from agentpm.core.database.models.detection_fitness import Policy
from agentpm.core.database.enums.detection import PolicyLevel


# ============================================================================
# Built-in Default Policies
# ============================================================================

DEFAULT_POLICIES = [
    # --- Dependency Policies ---
    {
        'policy_id': 'NO_CIRCULAR_DEPENDENCIES',
        'name': 'No Circular Dependencies',
        'description': 'Project must not have circular dependencies between modules',
        'level': 'error',
        'validation_fn': 'validate_no_cycles',
        'tags': ['dependency', 'architecture'],
        'enabled': True,
        'metadata': {
            'severity_threshold': 'high',  # Only fail on high-severity cycles
            'rationale': 'Circular dependencies make code harder to understand, test, and maintain',
        }
    },

    {
        'policy_id': 'MAX_DEPENDENCY_DEPTH',
        'name': 'Maximum Dependency Depth',
        'description': 'Dependency chain must not exceed 10 levels deep',
        'level': 'warning',
        'validation_fn': 'validate_max_depth',
        'tags': ['dependency', 'architecture'],
        'enabled': True,
        'metadata': {
            'max_depth': 10,
            'rationale': 'Deep dependency chains indicate tight coupling and complex architecture',
        }
    },

    # --- Complexity Policies ---
    {
        'policy_id': 'MAX_CYCLOMATIC_COMPLEXITY',
        'name': 'Maximum Cyclomatic Complexity',
        'description': 'Functions must not exceed cyclomatic complexity of 10',
        'level': 'warning',
        'validation_fn': 'validate_max_complexity',
        'tags': ['complexity', 'code_quality'],
        'enabled': True,
        'metadata': {
            'threshold': 10,
            'rationale': 'Complex functions are harder to test and maintain',
            'recommendation': 'Break complex functions into smaller, single-purpose functions',
        }
    },

    {
        'policy_id': 'MAX_FUNCTION_COMPLEXITY_STRICT',
        'name': 'Strict Maximum Function Complexity',
        'description': 'No function should exceed complexity of 20 (hard limit)',
        'level': 'error',
        'validation_fn': 'validate_max_complexity',
        'tags': ['complexity', 'code_quality'],
        'enabled': True,
        'metadata': {
            'threshold': 20,
            'rationale': 'Extremely complex functions are technical debt',
        }
    },

    # --- Size Policies ---
    {
        'policy_id': 'MAX_FILE_LOC',
        'name': 'Maximum File Size',
        'description': 'Files must not exceed 500 lines of code',
        'level': 'warning',
        'validation_fn': 'validate_max_file_loc',
        'tags': ['size', 'maintainability'],
        'enabled': True,
        'metadata': {
            'threshold': 500,
            'rationale': 'Large files are harder to navigate and understand',
            'recommendation': 'Split large files into multiple focused modules',
        }
    },

    {
        'policy_id': 'MAX_FUNCTION_LOC',
        'name': 'Maximum Function Size',
        'description': 'Functions must not exceed 50 lines of code',
        'level': 'info',
        'validation_fn': 'validate_max_function_loc',
        'tags': ['size', 'maintainability'],
        'enabled': True,
        'metadata': {
            'threshold': 50,
            'rationale': 'Long functions are harder to understand and test',
        }
    },

    # --- Architecture Policies ---
    {
        'policy_id': 'NO_LAYERING_VIOLATIONS',
        'name': 'No Layering Violations',
        'description': 'Lower layers must not depend on higher layers',
        'level': 'error',
        'validation_fn': 'validate_layering',
        'tags': ['architecture', 'layering'],
        'enabled': True,
        'metadata': {
            'layer_order': ['utils', 'plugins', 'detection'],  # From lowest to highest
            'rationale': 'Layering violations create circular dependencies and coupling',
        }
    },

    # --- Maintainability Policies ---
    {
        'policy_id': 'MIN_MAINTAINABILITY_INDEX',
        'name': 'Minimum Maintainability Index',
        'description': 'Files must have maintainability index >= 65',
        'level': 'warning',
        'validation_fn': 'validate_maintainability',
        'tags': ['maintainability', 'code_quality'],
        'enabled': True,
        'metadata': {
            'threshold': 65,
            'rationale': 'Low maintainability indicates technical debt',
            'recommendation': 'Reduce complexity, improve documentation, break up large functions',
        }
    },

    {
        'policy_id': 'MIN_MAINTAINABILITY_INDEX_STRICT',
        'name': 'Strict Minimum Maintainability Index',
        'description': 'No file should have MI < 40 (critical threshold)',
        'level': 'error',
        'validation_fn': 'validate_maintainability',
        'tags': ['maintainability', 'code_quality'],
        'enabled': True,
        'metadata': {
            'threshold': 40,
            'rationale': 'Extremely low MI indicates severe technical debt',
        }
    },

    # --- Code Quality Policies ---
    {
        'policy_id': 'MAX_COUPLING',
        'name': 'Maximum Module Coupling',
        'description': 'Modules should not have instability > 0.8',
        'level': 'info',
        'validation_fn': 'validate_max_coupling',
        'tags': ['dependency', 'code_quality'],
        'enabled': True,
        'metadata': {
            'threshold': 0.8,
            'rationale': 'High instability indicates modules are highly dependent on others',
            'recommendation': 'Apply dependency inversion, extract interfaces',
        }
    },

    {
        'policy_id': 'REQUIRE_DOCSTRINGS',
        'name': 'Require Module Docstrings',
        'description': 'All modules should have docstrings',
        'level': 'info',
        'validation_fn': 'validate_docstrings',
        'tags': ['documentation', 'code_quality'],
        'enabled': False,  # Disabled by default (opt-in)
        'metadata': {
            'check_modules': True,
            'check_classes': True,
            'check_functions': False,  # Only public functions
            'rationale': 'Documentation improves code understandability',
        }
    },
]


# ============================================================================
# Policy Lookup Functions
# ============================================================================

def get_policy_by_id(policy_id: str) -> Optional[Dict[str, Any]]:
    """
    Get policy by ID.

    Args:
        policy_id: Policy identifier (e.g., "NO_CIRCULAR_DEPENDENCIES")

    Returns:
        Policy dict or None if not found

    Example:
        >>> policy = get_policy_by_id("MAX_COMPLEXITY")
        >>> if policy:
        ...     print(f"Found: {policy['name']}")
    """
    for policy in DEFAULT_POLICIES:
        if policy['policy_id'] == policy_id:
            return policy
    return None


def get_policies_by_tag(tag: str) -> List[Dict[str, Any]]:
    """
    Get all policies with specific tag.

    Args:
        tag: Tag to filter by (e.g., "complexity", "architecture")

    Returns:
        List of policy dicts matching tag

    Example:
        >>> complexity_policies = get_policies_by_tag("complexity")
        >>> for policy in complexity_policies:
        ...     print(f"- {policy['name']}")
    """
    return [
        policy for policy in DEFAULT_POLICIES
        if tag in policy.get('tags', [])
    ]


def get_policies_by_level(level: str) -> List[Dict[str, Any]]:
    """
    Get all policies with specific enforcement level.

    Args:
        level: Enforcement level ("error", "warning", "info")

    Returns:
        List of policy dicts matching level

    Example:
        >>> error_policies = get_policies_by_level("error")
        >>> print(f"Found {len(error_policies)} critical policies")
    """
    return [
        policy for policy in DEFAULT_POLICIES
        if policy['level'] == level
    ]


def get_enabled_policies() -> List[Dict[str, Any]]:
    """
    Get all enabled policies.

    Returns:
        List of enabled policy dicts

    Example:
        >>> enabled = get_enabled_policies()
        >>> print(f"Running {len(enabled)} policies")
    """
    return [
        policy for policy in DEFAULT_POLICIES
        if policy.get('enabled', True)
    ]


def create_policy_from_dict(policy_dict: Dict[str, Any]) -> Policy:
    """
    Create Policy model from dictionary.

    Args:
        policy_dict: Policy dictionary (from DEFAULT_POLICIES)

    Returns:
        Policy Pydantic model

    Example:
        >>> policy_dict = get_policy_by_id("MAX_COMPLEXITY")
        >>> policy = create_policy_from_dict(policy_dict)
        >>> print(f"Policy: {policy.name}")
    """
    return Policy(
        policy_id=policy_dict['policy_id'],
        name=policy_dict['name'],
        description=policy_dict['description'],
        level=PolicyLevel(policy_dict['level']),
        validation_fn=policy_dict.get('validation_fn'),
        tags=policy_dict.get('tags', []),
        enabled=policy_dict.get('enabled', True),
        metadata=policy_dict.get('metadata', {})
    )


def create_all_policies() -> List[Policy]:
    """
    Create Policy models for all default policies.

    Returns:
        List of Policy models

    Example:
        >>> policies = create_all_policies()
        >>> for policy in policies:
        ...     if policy.enabled:
        ...         print(f"Active: {policy.name}")
    """
    return [create_policy_from_dict(p) for p in DEFAULT_POLICIES]


# ============================================================================
# Policy Statistics
# ============================================================================

def get_policy_statistics() -> Dict[str, Any]:
    """
    Get statistics about default policies.

    Returns:
        Dictionary with policy counts by level, tag, etc.

    Example:
        >>> stats = get_policy_statistics()
        >>> print(f"Total policies: {stats['total']}")
        >>> print(f"Errors: {stats['by_level']['error']}")
        >>> print(f"Tags: {', '.join(stats['all_tags'])}")
    """
    total = len(DEFAULT_POLICIES)
    enabled = len(get_enabled_policies())

    by_level = {
        'error': len(get_policies_by_level('error')),
        'warning': len(get_policies_by_level('warning')),
        'info': len(get_policies_by_level('info')),
    }

    all_tags = set()
    by_tag = {}
    for policy in DEFAULT_POLICIES:
        tags = policy.get('tags', [])
        for tag in tags:
            all_tags.add(tag)
            by_tag[tag] = by_tag.get(tag, 0) + 1

    return {
        'total': total,
        'enabled': enabled,
        'disabled': total - enabled,
        'by_level': by_level,
        'by_tag': by_tag,
        'all_tags': sorted(all_tags),
    }


# Module exports
__all__ = [
    'DEFAULT_POLICIES',
    'get_policy_by_id',
    'get_policies_by_tag',
    'get_policies_by_level',
    'get_enabled_policies',
    'create_policy_from_dict',
    'create_all_policies',
    'get_policy_statistics',
]
