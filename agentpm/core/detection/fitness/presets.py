"""
Built-in Fitness Presets for APM (Agent Project Manager) Detection Pack.

Provides predefined preset configurations for common use cases:
- Strict: Enterprise-grade quality requirements
- Balanced: Moderate quality standards (default)
- Lenient: Relaxed standards for legacy code
- Startup: Fast iteration, lower quality bars
- Security Focused: Security and compliance emphasis

Presets configure:
- Complexity thresholds
- File size limits
- Maintainability requirements
- Policy selection (which policies to enable)

Author: APM (Agent Project Manager) Detection Pack Team
Layer: Layer 3 (Detection Services - Configuration)
Version: 1.0.0
"""

from typing import Dict, List, Any
from agentpm.core.database.models.detection_preset import DetectionPreset


# ============================================================================
# Built-in Preset Definitions
# ============================================================================

BUILTIN_PRESETS: Dict[str, Dict[str, Any]] = {
    'strict': {
        'name': 'Strict Quality Standards',
        'description': 'Enterprise-grade quality requirements with high standards',
        'preset_type': 'fitness',
        'configuration': {
            'max_complexity': 5,
            'max_file_loc': 250,
            'min_maintainability': 75,
            'enforce_no_cycles': True,
            'max_function_loc': 30,
            'max_dependency_depth': 8,
            'policies': ['ALL']  # Enable all policies
        }
    },

    'balanced': {
        'name': 'Balanced Standards',
        'description': 'Moderate quality requirements suitable for most projects (default)',
        'preset_type': 'fitness',
        'configuration': {
            'max_complexity': 10,
            'max_file_loc': 500,
            'min_maintainability': 65,
            'enforce_no_cycles': True,
            'max_function_loc': 50,
            'max_dependency_depth': 10,
            'policies': [
                'NO_CIRCULAR_DEPENDENCIES',
                'MAX_CYCLOMATIC_COMPLEXITY',
                'MAX_FUNCTION_COMPLEXITY_STRICT',
                'MAX_FILE_LOC',
                'NO_LAYERING_VIOLATIONS',
                'MIN_MAINTAINABILITY_INDEX',
                'MIN_MAINTAINABILITY_INDEX_STRICT'
            ]
        }
    },

    'lenient': {
        'name': 'Lenient Standards',
        'description': 'Relaxed quality standards for legacy code or rapid prototyping',
        'preset_type': 'fitness',
        'configuration': {
            'max_complexity': 20,
            'max_file_loc': 1000,
            'min_maintainability': 40,
            'enforce_no_cycles': False,
            'max_function_loc': 100,
            'max_dependency_depth': 15,
            'policies': [
                'MAX_FUNCTION_COMPLEXITY_STRICT',  # Only hard limits
                'MIN_MAINTAINABILITY_INDEX_STRICT'
            ]
        }
    },

    'startup': {
        'name': 'Startup Velocity',
        'description': 'Fast iteration focus with lower quality bars for early-stage development',
        'preset_type': 'fitness',
        'configuration': {
            'max_complexity': 15,
            'max_file_loc': 750,
            'min_maintainability': 50,
            'enforce_no_cycles': False,
            'max_function_loc': 75,
            'max_dependency_depth': 12,
            'policies': [
                'MAX_FUNCTION_COMPLEXITY_STRICT',
                'MAX_FILE_LOC',
                'MIN_MAINTAINABILITY_INDEX'
            ]
        }
    },

    'security_focused': {
        'name': 'Security Focused',
        'description': 'Security and compliance emphasis with architecture validation',
        'preset_type': 'fitness',
        'configuration': {
            'max_complexity': 8,
            'max_file_loc': 400,
            'min_maintainability': 70,
            'enforce_no_cycles': True,
            'max_function_loc': 40,
            'max_dependency_depth': 8,
            'policies': [
                'NO_CIRCULAR_DEPENDENCIES',
                'MAX_CYCLOMATIC_COMPLEXITY',
                'NO_LAYERING_VIOLATIONS',
                'MIN_MAINTAINABILITY_INDEX'
            ]
        }
    }
}


# ============================================================================
# Preset Loading Functions
# ============================================================================

def get_builtin_preset_names() -> List[str]:
    """
    Get list of all built-in preset names.

    Returns:
        List of preset names

    Example:
        >>> names = get_builtin_preset_names()
        >>> print(names)
        ['strict', 'balanced', 'lenient', 'startup', 'security_focused']
    """
    return list(BUILTIN_PRESETS.keys())


def get_builtin_preset(preset_name: str) -> DetectionPreset:
    """
    Get a built-in preset by name.

    Args:
        preset_name: Name of preset ('strict', 'balanced', 'lenient', 'startup', 'security_focused')

    Returns:
        DetectionPreset instance

    Raises:
        ValueError: If preset_name is not a valid built-in preset

    Example:
        >>> preset = get_builtin_preset('strict')
        >>> print(f"Preset: {preset.name}")
        >>> print(f"Max complexity: {preset.get_setting('max_complexity')}")
        Preset: Strict Quality Standards
        Max complexity: 5
    """
    if preset_name not in BUILTIN_PRESETS:
        available = ', '.join(BUILTIN_PRESETS.keys())
        raise ValueError(
            f"Unknown preset: '{preset_name}'. "
            f"Available presets: {available}"
        )

    preset_data = BUILTIN_PRESETS[preset_name]

    return DetectionPreset(
        name=preset_data['name'],
        description=preset_data['description'],
        preset_type=preset_data['preset_type'],
        configuration=preset_data['configuration'].copy(),
        is_builtin=True
    )


def get_all_builtin_presets() -> List[DetectionPreset]:
    """
    Get all built-in presets.

    Returns:
        List of DetectionPreset instances

    Example:
        >>> presets = get_all_builtin_presets()
        >>> for preset in presets:
        ...     print(f"- {preset.name}: {preset.description}")
        - Strict Quality Standards: Enterprise-grade quality requirements...
        - Balanced Standards: Moderate quality requirements...
        - ...
    """
    return [get_builtin_preset(name) for name in BUILTIN_PRESETS.keys()]


def describe_preset(preset_name: str) -> str:
    """
    Get detailed description of a preset.

    Args:
        preset_name: Name of preset

    Returns:
        Multi-line description string

    Example:
        >>> print(describe_preset('strict'))
        Strict Quality Standards
        Enterprise-grade quality requirements with high standards

        Configuration:
          - Max Complexity: 5
          - Max File LOC: 250
          - Min Maintainability: 75
          - Enforce No Cycles: True
          - Policies: ALL
    """
    preset = get_builtin_preset(preset_name)
    config = preset.configuration

    lines = [
        preset.name,
        preset.description,
        "",
        "Configuration:"
    ]

    # Format configuration settings
    if 'max_complexity' in config:
        lines.append(f"  - Max Complexity: {config['max_complexity']}")
    if 'max_file_loc' in config:
        lines.append(f"  - Max File LOC: {config['max_file_loc']}")
    if 'min_maintainability' in config:
        lines.append(f"  - Min Maintainability: {config['min_maintainability']}")
    if 'enforce_no_cycles' in config:
        lines.append(f"  - Enforce No Cycles: {config['enforce_no_cycles']}")
    if 'max_function_loc' in config:
        lines.append(f"  - Max Function LOC: {config['max_function_loc']}")
    if 'max_dependency_depth' in config:
        lines.append(f"  - Max Dependency Depth: {config['max_dependency_depth']}")

    # Format policies
    if 'policies' in config:
        policies = config['policies']
        if policies == ['ALL']:
            lines.append("  - Policies: ALL")
        elif len(policies) <= 3:
            lines.append(f"  - Policies: {', '.join(policies)}")
        else:
            lines.append(f"  - Policies: {len(policies)} enabled")

    return "\n".join(lines)


def list_presets_summary() -> str:
    """
    Get summary of all built-in presets.

    Returns:
        Multi-line summary string

    Example:
        >>> print(list_presets_summary())
        Available Fitness Presets:

        1. strict - Strict Quality Standards
           Enterprise-grade quality requirements with high standards

        2. balanced - Balanced Standards
           Moderate quality requirements suitable for most projects (default)
        ...
    """
    lines = ["Available Fitness Presets:", ""]

    for idx, preset_name in enumerate(BUILTIN_PRESETS.keys(), 1):
        preset = get_builtin_preset(preset_name)
        lines.append(f"{idx}. {preset_name} - {preset.name}")
        lines.append(f"   {preset.description}")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Policy Selection Helpers
# ============================================================================

def get_policies_for_preset(preset_name: str) -> List[str]:
    """
    Get list of policy IDs that should be enabled for a preset.

    Args:
        preset_name: Name of preset

    Returns:
        List of policy IDs to enable

    Example:
        >>> policies = get_policies_for_preset('strict')
        >>> print(policies)
        ['ALL']
        >>> policies = get_policies_for_preset('balanced')
        >>> print(len(policies))
        7
    """
    preset = get_builtin_preset(preset_name)
    return preset.get_setting('policies', [])


def expand_policy_tags(policy_tags: List[str]) -> List[str]:
    """
    Expand policy tags like ['ALL'] or ['DEFAULT'] into actual policy IDs.

    Args:
        policy_tags: List that may contain tags like 'ALL', 'DEFAULT', 'ESSENTIAL'

    Returns:
        Expanded list of policy IDs

    Example:
        >>> # If policy_tags contains 'ALL', return all policy IDs
        >>> expand_policy_tags(['ALL'])
        ['NO_CIRCULAR_DEPENDENCIES', 'MAX_DEPENDENCY_DEPTH', ...]

        >>> # If policy_tags contains actual IDs, return as-is
        >>> expand_policy_tags(['NO_CIRCULAR_DEPENDENCIES', 'MAX_FILE_LOC'])
        ['NO_CIRCULAR_DEPENDENCIES', 'MAX_FILE_LOC']
    """
    from .policies import DEFAULT_POLICIES

    # If 'ALL' tag, return all policy IDs
    if 'ALL' in policy_tags:
        return [p['policy_id'] for p in DEFAULT_POLICIES]

    # If 'DEFAULT' tag, return enabled policies
    if 'DEFAULT' in policy_tags:
        return [p['policy_id'] for p in DEFAULT_POLICIES if p.get('enabled', True)]

    # If 'ESSENTIAL' tag, return only ERROR-level policies
    if 'ESSENTIAL' in policy_tags:
        return [p['policy_id'] for p in DEFAULT_POLICIES if p['level'] == 'error']

    # Otherwise, return as-is (assume they're actual policy IDs)
    return policy_tags


# Module exports
__all__ = [
    'BUILTIN_PRESETS',
    'get_builtin_preset_names',
    'get_builtin_preset',
    'get_all_builtin_presets',
    'describe_preset',
    'list_presets_summary',
    'get_policies_for_preset',
    'expand_policy_tags',
]
