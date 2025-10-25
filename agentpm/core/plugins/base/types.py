"""
Plugin Types - Pydantic Models for Plugin System

Type-safe models for plugin fact extraction and code amalgamations.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Dict, Any
from datetime import datetime


class PluginCategory(str, Enum):
    """Plugin categorization"""
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"


class ProjectFacts(BaseModel):
    """
    Plugin-extracted project facts.

    Contains framework-specific technical facts that agents use
    to understand the project's technical foundation.

    Stored in database contexts table with entity_type='project'.

    Attributes:
        plugin_id: Plugin identifier
        facts: Dictionary of extracted facts
        extracted_at: When facts were extracted
    """
    model_config = ConfigDict(validate_assignment=True)

    plugin_id: str = Field(..., min_length=1)
    facts: Dict[str, Any] = Field(default_factory=dict)
    extracted_at: datetime = Field(default_factory=datetime.now)


class CodeAmalgamation(BaseModel):
    """
    Generated code grouping for agent reference.

    Stored as .aipm/contexts/{plugin_id}_{amalgamation_type}.txt

    Attributes:
        plugin_id: Plugin identifier
        amalgamation_type: Type of grouping (classes, functions, models, etc.)
        content: Amalgamated code content
        file_count: Number of files processed
        generated_at: When amalgamation was generated
    """
    model_config = ConfigDict(validate_assignment=True)

    plugin_id: str = Field(..., min_length=1)
    amalgamation_type: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    file_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(default_factory=datetime.now)


class ContextDelta(BaseModel):
    """
    Plugin-specific context changes.

    Represents what a single plugin wants to add to project context.

    Attributes:
        plugin_id: Plugin identifier
        additions: Context data to add
        recommendations: Suggested improvements
    """
    model_config = ConfigDict(validate_assignment=True)

    plugin_id: str = Field(..., min_length=1)
    additions: Dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class EnrichmentResult(BaseModel):
    """
    Combined result from all plugins.

    Aggregates context deltas from multiple plugins.

    Attributes:
        project_path: Path to project that was enriched
        deltas: List of ContextDelta from each plugin
        total_plugins: Number of plugins that contributed
        enriched_at: When enrichment occurred
        enrichment_time_ms: Time taken for enrichment in milliseconds
    """
    model_config = ConfigDict(validate_assignment=True)

    project_path: str = Field(..., min_length=1)
    deltas: list[ContextDelta] = Field(default_factory=list)
    total_plugins: int = Field(default=0, ge=0)
    enriched_at: datetime = Field(default_factory=datetime.now)
    enrichment_time_ms: float = Field(default=0.0, ge=0)

    def add_delta(self, delta: ContextDelta) -> None:
        """Add a context delta from a plugin."""
        self.deltas.append(delta)
        self.total_plugins += 1

    def get_all_recommendations(self) -> list[str]:
        """Get all recommendations from all plugin deltas."""
        all_recs = []
        for delta in self.deltas:
            all_recs.extend(delta.recommendations)
        return all_recs