"""
Detection System Enumerations

Type-safe enumerations for detection system components:
- Architecture pattern types for pattern recognition system
- License types for SBOM generation and compliance
- Policy enforcement levels for fitness testing

Moved from:
- core/detection/patterns/models.py (ArchitecturePattern)
- core/detection/sbom/models.py (LicenseType)
- core/detection/fitness/models.py (PolicyLevel)

Following database-first architecture.
"""

from enum import Enum


class PolicyLevel(str, Enum):
    """
    Policy enforcement levels for architecture fitness testing.

    Determines the severity and action taken when a policy is violated.

    **Levels**:
    - ERROR: Blocks deployment, must be fixed immediately
    - WARNING: Logged but doesn't block, should be addressed soon
    - INFO: Informational only, for awareness and tracking

    **Usage**:
        from agentpm.core.database.enums.detection import PolicyLevel
        from agentpm.core.database.models.detection_fitness import Policy

        policy = Policy(
            policy_id="TEST-001",
            name="Test Policy",
            description="Example",
            level=PolicyLevel.ERROR,
            validation_fn="validate_test"
        )

        if policy.level == PolicyLevel.ERROR:
            print("This policy blocks deployment")

    **Integration**:
        Used by:
        - agentpm.core.database.models.detection_fitness (Policy, PolicyViolation)
        - agentpm.core.detection.fitness.engine (FitnessEngine)
        - agentpm.core.detection.fitness.policies (DEFAULT_POLICIES)
    """
    ERROR = "error"      # Blocks deployment - critical violations
    WARNING = "warning"  # Logged but doesn't block - should be addressed
    INFO = "info"        # Informational only - awareness and tracking


class ArchitecturePattern(str, Enum):
    """
    Recognized architecture patterns.

    **Patterns**:
    - HEXAGONAL: Ports & Adapters architecture
    - LAYERED: N-tier layered architecture
    - CLEAN: Clean Architecture (similar to hexagonal)
    - DDD: Domain-Driven Design
    - CQRS: Command Query Responsibility Segregation
    - EVENT_SOURCING: Event Sourcing pattern
    - MICROSERVICES: Microservices architecture
    - MVC: Model-View-Controller
    - MONOLITHIC: Monolithic architecture

    **Usage**:
        from agentpm.core.database.enums.detection import ArchitecturePattern

        pattern = ArchitecturePattern.HEXAGONAL
        print(pattern.value)  # "hexagonal"
    """

    HEXAGONAL = "hexagonal"
    LAYERED = "layered"
    CLEAN = "clean"
    DDD = "domain_driven_design"
    CQRS = "cqrs"
    EVENT_SOURCING = "event_sourcing"
    MICROSERVICES = "microservices"
    MVC = "mvc"
    MONOLITHIC = "monolithic"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class LicenseType(str, Enum):
    """
    Common open source and proprietary license types.

    Categories:
    - Permissive: MIT, Apache, BSD, ISC (minimal restrictions)
    - Copyleft: GPL, AGPL (requires derivative works to use same license)
    - Weak Copyleft: MPL, EPL (copyleft only for modified files)
    - Other: Unlicense, CC0, Proprietary, Unknown

    Used in SBOM generation and license compliance checking.
    """

    # Permissive licenses (most common in open source)
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    BSD_3_CLAUSE = "BSD-3-Clause"
    BSD_2_CLAUSE = "BSD-2-Clause"
    BSD_0 = "0BSD"  # Zero-Clause BSD (most permissive)
    ISC = "ISC"

    # Copyleft licenses (strong restrictions)
    GPL_2_0 = "GPL-2.0"
    GPL_3_0 = "GPL-3.0"
    LGPL_2_1 = "LGPL-2.1"
    LGPL_3_0 = "LGPL-3.0"
    AGPL_3_0 = "AGPL-3.0"

    # Weak copyleft licenses
    MPL_2_0 = "MPL-2.0"
    EPL_2_0 = "EPL-2.0"

    # Other
    UNLICENSE = "Unlicense"
    CC0_1_0 = "CC0-1.0"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")
