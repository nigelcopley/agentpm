"""
Skill Model - Pydantic Domain Model

Type-safe skill model with validation.

Skills represent reusable capability modules that can be assigned to agents.
They support progressive loading (metadata → instructions → resources) and
multi-provider configurations.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SkillCategory(str, Enum):
    """Valid skill categories for grouping and discovery"""
    TESTING = "testing"
    DATABASE = "database"
    API = "api"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    PROJECT_MANAGEMENT = "project-management"


class Skill(BaseModel):
    """
    Skill domain model with Pydantic validation.

    Skills are reusable capability modules that can be assigned to agents:
    - Progressive Loading: metadata → instructions → resources
    - Multi-Provider: Support for claude-code, cursor, codex
    - Categorization: Grouped by category for discovery
    - State Management: Enable/disable skills dynamically

    Attributes:
        id: Database primary key (None for new skills)
        name: Unique kebab-case identifier (e.g., 'python-testing')
        display_name: Human-readable name for UI (e.g., 'Python Testing')
        description: Brief description for discovery (~100 chars)
        category: Skill category for grouping (optional)
        instructions: Main markdown instructions (Level 2 loading, ~5-20 KB)
        resources: JSON resources dict (Level 3 loading, optional)
        provider_config: JSON provider-specific configuration (optional)
        enabled: Enable/disable flag (default: True)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    # Primary key
    id: Optional[int] = Field(default=None, description="Database primary key")

    # Identifiers
    name: str = Field(
        min_length=1,
        max_length=64,
        description="Unique kebab-case identifier (e.g., 'python-testing')",
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",  # Enforce kebab-case
    )

    display_name: str = Field(
        min_length=1,
        max_length=100,
        description="Human-readable name for UI (e.g., 'Python Testing')",
    )

    description: str = Field(
        min_length=1,
        max_length=1000,
        description="Brief description for discovery (~100 chars recommended)",
    )

    category: Optional[SkillCategory] = Field(
        default=None,
        description="Skill category for grouping and discovery",
    )

    # Content sections (progressive loading)
    instructions: str = Field(
        min_length=1,
        description="Main markdown instructions (Level 2, ~5-20 KB)",
    )

    resources: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON resources (Level 3): {examples: [], templates: [], docs: []}",
    )

    provider_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON provider-specific config: {claude_code: {allowed_tools: []}}",
    )

    # State
    enabled: bool = Field(
        default=True,
        description="Enable/disable skill",
    )

    # Audit timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )

    # ========================================================================
    # VALIDATORS
    # ========================================================================

    @field_validator("name")
    @classmethod
    def validate_name_kebab_case(cls, v: str) -> str:
        """Ensure name is valid kebab-case"""
        if not v:
            raise ValueError("Name cannot be empty")

        # Allow lowercase letters, numbers, and hyphens (not at start/end)
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Name must contain only lowercase letters, numbers, and hyphens"
            )

        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Name cannot start or end with hyphen")

        if "--" in v:
            raise ValueError("Name cannot contain consecutive hyphens")

        return v.lower()

    @field_validator("resources", mode="before")
    @classmethod
    def validate_resources_structure(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Validate resources JSON structure"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Resources must be a dictionary")

        # Expected structure: {examples: [], templates: [], docs: []}
        allowed_keys = {"examples", "templates", "docs"}
        for key in v.keys():
            if key not in allowed_keys:
                raise ValueError(
                    f"Invalid resources key '{key}'. Allowed: {allowed_keys}"
                )

        # Ensure arrays
        for key in ["examples", "templates", "docs"]:
            if key in v and not isinstance(v[key], list):
                raise ValueError(f"resources.{key} must be an array")

        return v

    @field_validator("provider_config", mode="before")
    @classmethod
    def validate_provider_config_structure(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Validate provider_config JSON structure"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Provider config must be a dictionary")

        # Expected structure: {claude_code: {...}, cursor: {...}, codex: {...}}
        allowed_providers = {"claude-code", "cursor", "codex"}
        for provider in v.keys():
            if provider not in allowed_providers:
                raise ValueError(
                    f"Invalid provider '{provider}'. Allowed: {allowed_providers}"
                )

        return v

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def get_provider_tools(self, provider: str = "claude-code") -> List[str]:
        """
        Get allowed tools for a specific provider.

        Args:
            provider: Provider name (default: 'claude-code')

        Returns:
            List of allowed tool names (empty if not configured)
        """
        if not self.provider_config:
            return []

        provider_data = self.provider_config.get(provider, {})
        return provider_data.get("allowed_tools", [])

    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Export Level 1 metadata only (lightweight).

        Returns:
            Dictionary with id, name, display_name, description, category
        """
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "enabled": self.enabled,
        }

    def to_full_dict(self) -> Dict[str, Any]:
        """
        Export full skill data (all levels).

        Returns:
            Dictionary with all fields including instructions and resources
        """
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "instructions": self.instructions,
            "resources": self.resources,
            "provider_config": self.provider_config,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"Skill(id={self.id}, name='{self.name}', "
            f"category={self.category}, enabled={self.enabled})"
        )


class AgentSkill(BaseModel):
    """
    Agent-Skill junction model for many-to-many relationships.

    Tracks which skills are assigned to which agents with priority ordering.

    Attributes:
        id: Database primary key (None for new assignments)
        agent_id: Foreign key to agents table
        skill_id: Foreign key to skills table
        priority: Loading priority (0-100, higher = load earlier, default: 50)
        created_at: Assignment timestamp
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
    )

    id: Optional[int] = Field(default=None, description="Database primary key")

    agent_id: int = Field(
        gt=0,
        description="Foreign key to agents table",
    )

    skill_id: int = Field(
        gt=0,
        description="Foreign key to skills table",
    )

    priority: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Loading priority (0-100, higher = earlier, default: 50)",
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Assignment timestamp",
    )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"AgentSkill(id={self.id}, agent_id={self.agent_id}, "
            f"skill_id={self.skill_id}, priority={self.priority})"
        )
