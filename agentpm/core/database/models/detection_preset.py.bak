"""
Pydantic Model for Detection Pack Presets.

Defines data structures for preset configurations that allow users to quickly
apply predefined policy sets and detection configurations.

Models follow APM (Agent Project Manager) database-first architecture:
- Layer 2 models (database domain)
- Used by FitnessEngine and other Detection services (Layer 3)
- Serializable for storage/transmission

Presets allow saving and reusing:
- Fitness policies to enable/disable
- Analysis thresholds (complexity, maintainability)
- Pattern detection confidence levels
- SBOM generation options

Author: APM (Agent Project Manager) Detection Pack Team
Layer: Layer 2 (Database - Domain Models)
Version: 1.0.0
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Dict, Optional, Any
from datetime import datetime


class DetectionPreset(BaseModel):
    """
    Detection Pack preset configuration.

    Presets allow users to save and quickly apply predefined configurations
    for detection tools (fitness tests, analysis, SBOM, patterns).

    Attributes:
        id: Database primary key (None for new presets)
        name: Preset name (e.g., "Strict Quality Standards")
        description: Human-readable description of preset purpose
        preset_type: Type of preset (fitness, analysis, sbom, patterns)
        configuration: JSON configuration dict with preset-specific settings
        is_builtin: Whether this is a built-in preset (immutable)
        created_at: When preset was created
        updated_at: When preset was last modified

    Configuration Schema (preset_type="fitness"):
        {
            "max_complexity": int,           # Maximum cyclomatic complexity
            "max_file_loc": int,             # Maximum lines per file
            "min_maintainability": float,    # Minimum maintainability index
            "enforce_no_cycles": bool,       # Require no circular dependencies
            "policies": List[str]            # Policy IDs to enable (or ["ALL"], ["DEFAULT"], ["ESSENTIAL"])
        }

    Example:
        >>> from agentpm.core.database.models.detection_preset import DetectionPreset
        >>>
        >>> preset = DetectionPreset(
        ...     name="Strict Quality Standards",
        ...     description="Enterprise-grade quality requirements",
        ...     preset_type="fitness",
        ...     configuration={
        ...         "max_complexity": 5,
        ...         "max_file_loc": 250,
        ...         "min_maintainability": 75,
        ...         "enforce_no_cycles": True,
        ...         "policies": ["ALL"]
        ...     },
        ...     is_builtin=True
        ... )
        >>> print(f"Preset: {preset.name}")
        >>> print(f"Max complexity: {preset.configuration['max_complexity']}")
    """
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[int] = Field(None, description="Database primary key")
    name: str = Field(..., min_length=1, max_length=100, description="Preset name")
    description: str = Field(default="", max_length=500, description="Preset description")
    preset_type: str = Field(
        default="fitness",
        description="Preset type: fitness, analysis, sbom, patterns"
    )

    # Configuration as JSON-serializable dict
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Preset-specific configuration (JSON)"
    )

    # Metadata
    is_builtin: bool = Field(default=False, description="Built-in preset (immutable)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty after stripping whitespace."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Preset name cannot be empty or whitespace-only")
        return cleaned

    @field_validator('preset_type')
    @classmethod
    def validate_preset_type(cls, v: str) -> str:
        """Ensure preset_type is one of the allowed values."""
        allowed_types = {'fitness', 'analysis', 'sbom', 'patterns'}
        if v not in allowed_types:
            raise ValueError(
                f"preset_type must be one of {allowed_types}, got '{v}'"
            )
        return v

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting by key.

        Args:
            key: Configuration key to retrieve
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> preset = DetectionPreset(
            ...     name="Test",
            ...     configuration={"max_complexity": 10}
            ... )
            >>> max_complexity = preset.get_setting("max_complexity", 15)
            >>> print(f"Max complexity: {max_complexity}")  # 10
            >>> min_coverage = preset.get_setting("min_coverage", 80)
            >>> print(f"Min coverage: {min_coverage}")  # 80 (default)
        """
        return self.configuration.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a configuration setting.

        Args:
            key: Configuration key to set
            value: Value to set

        Example:
            >>> preset = DetectionPreset(name="Test")
            >>> preset.set_setting("max_complexity", 10)
            >>> assert preset.configuration["max_complexity"] == 10
        """
        self.configuration[key] = value
        self.updated_at = datetime.now()

    def is_fitness_preset(self) -> bool:
        """Check if this is a fitness testing preset."""
        return self.preset_type == "fitness"

    def is_analysis_preset(self) -> bool:
        """Check if this is an analysis preset."""
        return self.preset_type == "analysis"

    def is_sbom_preset(self) -> bool:
        """Check if this is an SBOM generation preset."""
        return self.preset_type == "sbom"

    def is_patterns_preset(self) -> bool:
        """Check if this is a pattern detection preset."""
        return self.preset_type == "patterns"

    def clone(self, new_name: str) -> "DetectionPreset":
        """
        Clone this preset with a new name.

        Args:
            new_name: Name for the cloned preset

        Returns:
            New DetectionPreset with same configuration

        Example:
            >>> original = DetectionPreset(
            ...     name="Strict",
            ...     configuration={"max_complexity": 5}
            ... )
            >>> clone = original.clone("My Strict")
            >>> assert clone.name == "My Strict"
            >>> assert clone.configuration == original.configuration
            >>> assert clone.id is None  # New preset, no ID yet
        """
        return DetectionPreset(
            name=new_name,
            description=self.description,
            preset_type=self.preset_type,
            configuration=self.configuration.copy(),
            is_builtin=False  # Clones are never built-in
        )


# Module exports
__all__ = [
    'DetectionPreset',
]
