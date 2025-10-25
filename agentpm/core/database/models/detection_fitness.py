"""
Pydantic Models for Fitness Testing.

Defines data structures for architecture fitness policies, violations,
and test results.

Models follow APM (Agent Project Manager) database-first architecture:
- Layer 2 models (database domain)
- Used by FitnessEngine service (Layer 3)
- Serializable for storage/transmission

Moved from: agentpm/core/detection/fitness/models.py
To support: Database-first architecture pattern

Author: APM (Agent Project Manager) Detection Pack Team
Layer: Layer 2 (Database - Domain Models)
Version: 1.0.0
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..enums.detection import PolicyLevel


class Policy(BaseModel):
    """
    Architecture fitness policy rule.

    Defines a single validation rule for code quality, architecture patterns,
    or best practices compliance.

    Attributes:
        policy_id: Unique identifier (e.g., "NO_CIRCULAR_DEPENDENCIES")
        name: Human-readable name
        description: What the policy validates
        level: Enforcement level (error, warning, info)
        validation_fn: Function name to execute (must exist in FitnessEngine)
        tags: Categorization tags for filtering
        enabled: Whether policy is active
        metadata: Additional policy-specific configuration

    Example:
        >>> from agentpm.core.database.models.detection_fitness import Policy
        >>> from agentpm.core.database.enums.detection import PolicyLevel
        >>>
        >>> policy = Policy(
        ...     policy_id="MAX_COMPLEXITY",
        ...     name="Maximum Cyclomatic Complexity",
        ...     description="Functions must not exceed complexity of 10",
        ...     level=PolicyLevel.WARNING,
        ...     validation_fn="validate_max_complexity",
        ...     tags=["complexity", "code_quality"],
        ...     metadata={"threshold": 10}
        ... )
        >>> print(f"Checking: {policy.name}")
    """
    model_config = ConfigDict(validate_assignment=True)

    policy_id: str = Field(..., min_length=1, description="Unique policy identifier")
    name: str = Field(..., min_length=1, description="Human-readable name")
    description: str = Field(..., min_length=1, description="Policy description")
    level: PolicyLevel = Field(..., description="Enforcement level")
    validation_fn: Optional[str] = Field(None, description="Validation function name")
    tags: List[str] = Field(default_factory=list, description="Classification tags")
    enabled: bool = Field(default=True, description="Whether policy is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Policy-specific config")

    @field_validator('policy_id')
    @classmethod
    def validate_policy_id(cls, v: str) -> str:
        """Ensure policy_id is uppercase with underscores."""
        if not v.isupper():
            raise ValueError("policy_id must be uppercase")
        if ' ' in v:
            raise ValueError("policy_id cannot contain spaces")
        return v


class PolicyViolation(BaseModel):
    """
    Policy violation instance.

    Represents a single instance where code violates a fitness policy.

    Attributes:
        policy_id: Which policy was violated
        level: Severity level (from policy)
        message: Human-readable violation message
        location: File/component where violation occurred
        suggestion: How to fix the violation
        metadata: Additional violation-specific data

    Example:
        >>> from agentpm.core.database.models.detection_fitness import PolicyViolation
        >>> from agentpm.core.database.enums.detection import PolicyLevel
        >>>
        >>> violation = PolicyViolation(
        ...     policy_id="NO_CIRCULAR_DEPENDENCIES",
        ...     level=PolicyLevel.ERROR,
        ...     message="Circular dependency detected: module_a -> module_b -> module_a",
        ...     location="src/module_a.py",
        ...     suggestion="Extract shared functionality to a third module"
        ... )
        >>> print(f"{violation.level.upper()}: {violation.message}")
    """
    model_config = ConfigDict(validate_assignment=True)

    policy_id: str = Field(..., min_length=1, description="Policy identifier")
    level: PolicyLevel = Field(..., description="Violation severity")
    message: str = Field(..., min_length=1, description="Violation description")
    location: str = Field(..., min_length=1, description="Where violation occurred")
    suggestion: Optional[str] = Field(None, description="How to fix")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional data")


class FitnessResult(BaseModel):
    """
    Architecture fitness test results.

    Complete results from running fitness tests, including all violations,
    counts by severity, and overall compliance score.

    Attributes:
        violations: All policy violations found
        passed_count: Number of policies that passed
        warning_count: Number of warnings
        error_count: Number of errors
        compliance_score: Overall compliance (0.0-1.0)
        tested_at: When tests were run
        metadata: Additional result data

    Compliance Score Calculation:
    - Start at 1.0 (perfect compliance)
    - Subtract 0.1 for each error
    - Subtract 0.05 for each warning
    - Minimum: 0.0

    Example:
        >>> from agentpm.core.database.models.detection_fitness import FitnessResult
        >>>
        >>> result = FitnessResult(
        ...     violations=[violation1, violation2],
        ...     passed_count=8,
        ...     warning_count=2,
        ...     error_count=0,
        ...     compliance_score=0.90
        ... )
        >>> if result.is_passing():
        ...     print(f"Passed! Compliance: {result.compliance_score:.0%}")
        ... else:
        ...     print(f"Failed: {result.error_count} critical violations")
    """
    model_config = ConfigDict(validate_assignment=True)

    violations: List[PolicyViolation] = Field(
        default_factory=list,
        description="All violations found"
    )
    passed_count: int = Field(default=0, ge=0, description="Policies passed")
    warning_count: int = Field(default=0, ge=0, description="Warning count")
    error_count: int = Field(default=0, ge=0, description="Error count")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Overall compliance")
    tested_at: datetime = Field(default_factory=datetime.now, description="Test timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional data")

    def is_passing(self) -> bool:
        """
        Check if fitness test passed (no errors).

        Returns:
            True if error_count == 0, False otherwise

        Example:
            >>> result = FitnessResult(error_count=0, compliance_score=1.0)
            >>> assert result.is_passing() == True
            >>>
            >>> result2 = FitnessResult(error_count=1, compliance_score=0.9)
            >>> assert result2.is_passing() == False
        """
        return self.error_count == 0

    def get_violations_by_level(self, level: PolicyLevel) -> List[PolicyViolation]:
        """
        Get violations filtered by severity level.

        Args:
            level: PolicyLevel to filter by

        Returns:
            List of violations matching level

        Example:
            >>> from agentpm.core.database.enums.detection import PolicyLevel
            >>> result = FitnessResult(violations=[...])
            >>> errors = result.get_violations_by_level(PolicyLevel.ERROR)
            >>> for error in errors:
            ...     print(f"ERROR: {error.message}")
        """
        return [v for v in self.violations if v.level == level]

    def get_summary(self) -> str:
        """
        Get human-readable summary.

        Returns:
            Summary string with pass/fail status and counts

        Example:
            >>> result = FitnessResult(
            ...     passed_count=8,
            ...     warning_count=2,
            ...     error_count=0,
            ...     compliance_score=0.90
            ... )
            >>> print(result.get_summary())
            PASSED - 8 passed, 2 warnings, 0 errors (90% compliance)
        """
        status = "PASSED" if self.is_passing() else "FAILED"
        return (
            f"{status} - {self.passed_count} passed, "
            f"{self.warning_count} warnings, {self.error_count} errors "
            f"({self.compliance_score:.0%} compliance)"
        )


# Module exports
__all__ = [
    'Policy',
    'PolicyViolation',
    'FitnessResult',
]
