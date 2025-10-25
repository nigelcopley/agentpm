"""
Init Models - Pydantic Models for Initialization System

Type-safe models for project initialization orchestration.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
from typing import List, Optional
from enum import Enum
from datetime import datetime


class InitPhase(str, Enum):
    """Initialization phases"""
    PREFLIGHT = "preflight"
    DATABASE = "database"
    DETECTION = "detection"
    RULES = "rules"
    AGENTS = "agents"
    VERIFICATION = "verification"


class InitMode(str, Enum):
    """Initialization modes"""
    AUTO = "auto"  # Fully automatic with defaults
    WIZARD = "wizard"  # Interactive questionnaire
    CUSTOM = "custom"  # Custom configuration


class DetectionSummary(BaseModel):
    """
    Summary of detection results for initialization.

    Lightweight model containing only what's needed for the questionnaire
    and initial setup, not the full detection data.
    """
    model_config = ConfigDict(validate_assignment=True)

    frameworks: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    testing_frameworks: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    primary_language: Optional[str] = None


class InitProgress(BaseModel):
    """
    Tracks progress through initialization phases.

    Used for progress callbacks and user feedback.
    """
    model_config = ConfigDict(validate_assignment=True)

    phase: InitPhase
    current_step: int = Field(ge=1)
    total_steps: int = Field(ge=1)
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class InitResult(BaseModel):
    """
    Result of initialization operation.

    Contains all relevant information about what was created/configured.
    """
    model_config = ConfigDict(validate_assignment=True)

    success: bool
    project_name: str
    project_id: Optional[int] = None
    database_path: Optional[Path] = None
    agents_generated: int = Field(ge=0, default=0)
    rules_loaded: int = Field(ge=0, default=0)
    technologies_detected: List[str] = Field(default_factory=list)
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    duration_ms: float = Field(ge=0.0, default=0.0)

    def has_errors(self) -> bool:
        """Check if initialization had errors"""
        return self.errors is not None and len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if initialization had warnings"""
        return self.warnings is not None and len(self.warnings) > 0


class InitConfig(BaseModel):
    """
    Configuration for initialization process.

    Defines how initialization should proceed and what options to use.
    """
    model_config = ConfigDict(validate_assignment=True)

    project_name: str = Field(..., min_length=1, max_length=200)
    project_path: Path
    project_description: str = ""
    mode: InitMode = InitMode.AUTO

    # Options
    skip_detection: bool = False
    skip_rules: bool = False
    skip_agents: bool = False
    force_reset: bool = False  # Delete existing .agentpm and reinitialize

    # Advanced options
    custom_db_path: Optional[Path] = None
    enable_telemetry: bool = True
    verbose: bool = False


class RollbackAction(BaseModel):
    """
    Represents an action that can be rolled back if initialization fails.
    """
    model_config = ConfigDict(validate_assignment=True)

    action_type: str  # "create_directory", "create_file", "database_init", etc.
    target: str  # Path or identifier
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class RollbackPlan(BaseModel):
    """
    Plan for rolling back partial initialization.

    Tracks all actions taken during initialization for potential rollback.
    """
    model_config = ConfigDict(validate_assignment=True)

    actions: List[RollbackAction] = Field(default_factory=list)

    def add_action(self, action_type: str, target: str, metadata: dict = None) -> None:
        """Add rollback action"""
        action = RollbackAction(
            action_type=action_type,
            target=target,
            metadata=metadata or {}
        )
        self.actions.append(action)

    def get_rollback_order(self) -> List[RollbackAction]:
        """Get actions in reverse order for rollback"""
        return list(reversed(self.actions))
