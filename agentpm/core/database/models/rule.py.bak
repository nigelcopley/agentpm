"""Rule model for governance rules system.

This module defines the Pydantic model for project governance rules.
Rules enforce project-specific development standards and practices.

Three-Layer Pattern:
    - This file: Pydantic models with validation
    - adapters/rule.py: SQLite conversion logic
    - methods/rules.py: CRUD operations

Schema Correspondence:
    - rule_id: Unique identifier (e.g., "DP-001", "WR-002")
    - name: Human-readable name (e.g., "time-boxing-implementation")
    - description: What the rule enforces
    - enforcement_level: BLOCK, LIMIT, GUIDE, ENHANCE
    - config: JSON configuration (e.g., {"max_hours": 4.0})
    - enabled: Whether rule is active
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class EnforcementLevel(str, Enum):
    """Rule enforcement levels.

    BLOCK: Hard constraint - operation fails if rule violated
    LIMIT: Soft constraint - warning but operation succeeds
    GUIDE: Suggestion - informational only
    ENHANCE: Context enrichment - adds intelligence, no enforcement
    """

    BLOCK = "BLOCK"
    LIMIT = "LIMIT"
    GUIDE = "GUIDE"
    ENHANCE = "ENHANCE"


class Rule(BaseModel):
    """Governance rule model.

    Attributes:
        id: Database primary key (auto-generated)
        project_id: Parent project reference
        rule_id: Unique rule identifier (e.g., "DP-001")
        name: Machine-readable name (e.g., "time-boxing-implementation")
        description: Human-readable explanation
        enforcement_level: How strictly to enforce
        config: Rule-specific configuration (JSON dict)
        enabled: Whether rule is currently active
        created_at: Creation timestamp
        updated_at: Last modification timestamp

    Examples:
        >>> rule = Rule(
        ...     project_id=1,
        ...     rule_id="DP-001",
        ...     name="time-boxing-implementation",
        ...     description="IMPLEMENTATION tasks must be ≤4 hours",
        ...     enforcement_level=EnforcementLevel.BLOCK,
        ...     config={"max_hours": 4.0},
        ...     enabled=True
        ... )
        >>> rule.rule_id
        'DP-001'
        >>> rule.config["max_hours"]
        4.0
    """

    # Database fields
    id: Optional[int] = None
    project_id: int = Field(..., gt=0, description="Parent project ID")

    # Rule identity
    rule_id: str = Field(
        ...,
        min_length=5,
        max_length=50,
        pattern=r"^[A-Z]{2,4}-\d{3}$",
        description="Unique rule ID (format: XX-NNN or XXXX-NNN, e.g., DP-001, TEST-001)",
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Machine-readable rule name",
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Human-readable explanation"
    )
    category: Optional[str] = Field(
        default=None, max_length=100, description="Rule category (e.g., development_principles, code_quality)"
    )

    # Enforcement
    enforcement_level: EnforcementLevel = Field(
        ..., description="How strictly to enforce this rule"
    )
    validation_logic: Optional[str] = Field(
        default=None, max_length=1000, description="Pattern-based validation logic"
    )
    error_message: Optional[str] = Field(
        default=None, max_length=500, description="Message to show when rule is violated"
    )

    # Configuration
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Rule-specific configuration"
    )

    # Status
    enabled: bool = Field(default=True, description="Whether rule is active")

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        use_enum_values = False  # Keep enums as Enum objects
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            EnforcementLevel: lambda v: v.value,
        }

    @field_validator("rule_id")
    @classmethod
    def validate_rule_id_format(cls, v: str) -> str:
        """Validate rule_id follows XX-NNN or XXXX-NNN pattern.

        Args:
            v: Rule ID to validate

        Returns:
            Validated rule ID

        Raises:
            ValueError: If format is invalid
        """
        if not v:
            raise ValueError("rule_id cannot be empty")

        parts = v.split("-")
        if len(parts) != 2:
            raise ValueError(
                f"rule_id must be format XX-NNN or XXXX-NNN (e.g., DP-001, TEST-001), got: {v}"
            )

        prefix, number = parts
        if not prefix.isupper() or not (2 <= len(prefix) <= 4):
            raise ValueError(
                f"rule_id prefix must be 2-4 uppercase letters, got: {prefix}"
            )

        if not number.isdigit() or len(number) != 3:
            raise ValueError(
                f"rule_id number must be 3 digits, got: {number}"
            )

        return v

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Validate name is kebab-case.

        Args:
            v: Name to validate

        Returns:
            Validated name

        Raises:
            ValueError: If format is invalid
        """
        if not v:
            raise ValueError("name cannot be empty")

        # Check for valid characters (lowercase, numbers, hyphens)
        if not all(c.islower() or c.isdigit() or c == "-" for c in v):
            raise ValueError(
                f"name must be kebab-case (lowercase-with-hyphens), got: {v}"
            )

        # Check doesn't start/end with hyphen
        if v.startswith("-") or v.endswith("-"):
            raise ValueError(
                f"name cannot start or end with hyphen, got: {v}"
            )

        # Check no consecutive hyphens
        if "--" in v:
            raise ValueError(
                f"name cannot contain consecutive hyphens, got: {v}"
            )

        return v

    def __str__(self) -> str:
        """String representation."""
        status = "enabled" if self.enabled else "disabled"
        return f"Rule({self.rule_id}: {self.name} [{self.enforcement_level.value}, {status}])"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Rule(id={self.id}, rule_id='{self.rule_id}', name='{self.name}', "
            f"enforcement_level={self.enforcement_level.value}, enabled={self.enabled})"
        )
