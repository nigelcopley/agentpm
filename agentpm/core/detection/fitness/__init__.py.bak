"""
Fitness Testing Engine for APM (Agent Project Manager) Detection Pack.

Policy-based architecture fitness testing to validate code quality,
architectural patterns, and best practices compliance.

Components:
- models.py: Pydantic models for policies and violations
- policies.py: Built-in default policies
- engine.py: FitnessEngine for test execution

Example:
    from agentpm.core.detection.fitness import FitnessEngine
    from pathlib import Path

    # Initialize engine
    engine = FitnessEngine(Path.cwd())

    # Load and run tests
    policies = engine.load_default_policies()
    result = engine.run_tests(policies)

    # Check results
    if result.is_passing():
        print("All fitness tests passed!")
    else:
        print(f"Found {result.error_count} critical violations")

Author: APM (Agent Project Manager) Detection Pack Team
Layer: Layer 3 (Detection Services)
Version: 1.0.0
"""

# Import from database layer (Layer 2)
from agentpm.core.database.models.detection_fitness import (
    Policy,
    PolicyViolation,
    FitnessResult,
)
from agentpm.core.database.enums.detection import PolicyLevel

# Import from detection layer (Layer 3)
from .engine import FitnessEngine
from .policies import (
    DEFAULT_POLICIES,
    get_policy_by_id,
    get_policies_by_tag,
)

__all__ = [
    # Models
    'PolicyLevel',
    'Policy',
    'PolicyViolation',
    'FitnessResult',

    # Engine
    'FitnessEngine',

    # Policies
    'DEFAULT_POLICIES',
    'get_policy_by_id',
    'get_policies_by_tag',
]

__version__ = '1.0.0'
__author__ = 'APM (Agent Project Manager) Detection Pack Team'
__layer__ = 'Layer 3 (Detection Services - Business Logic)'
