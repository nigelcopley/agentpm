"""
Document Visibility Models - Pydantic Domain Models

Defines models for document visibility policy evaluation.
Part of Work Item #164: Auto-Generate Document File Paths

Architecture: Three-Layer Pattern
  Layer 1 (Models): This file - Pydantic models for type safety
  Layer 2 (Services): document_visibility.py - Business logic
  Layer 3 (Adapters): visibility_policy_adapter.py - Database I/O
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class VisibilityPolicy(BaseModel):
    """
    Policy definition for a document type.

    Stored in document_visibility_policies table.
    Defines visibility rules, review requirements, and auto-publish triggers.
    """

    id: Optional[int] = None
    category: str = Field(..., min_length=1, description="Document category (e.g., 'planning', 'architecture')")
    doc_type: str = Field(..., min_length=1, description="Document type within category (e.g., 'idea', 'adr')")

    default_visibility: str = Field(default="private", description="Default visibility level")
    default_audience: str = Field(default="internal", description="Default target audience")

    requires_review: bool = Field(default=False, description="Whether document requires review before approval")
    auto_publish_on_approved: bool = Field(default=False, description="Whether to auto-publish when approved")

    base_score: int = Field(ge=0, le=100, default=50, description="Base visibility score (0-100)")

    force_private: bool = Field(default=False, description="Force private regardless of score")
    force_public: bool = Field(default=False, description="Force public when approved/published")

    description: Optional[str] = Field(default=None, description="Human-readable description")
    rationale: Optional[str] = Field(default=None, description="Why this policy exists")
    auto_publish_trigger: Optional[str] = Field(default=None, description="Auto-publish trigger (e.g., 'on_approved', 'on_work_item_phase_O1')")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('default_visibility')
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        """Validate visibility is a valid enum value"""
        valid_values = ['private', 'restricted', 'public', 'context_aware']
        if v not in valid_values:
            raise ValueError(f"Invalid visibility: {v}. Must be one of {valid_values}")
        return v

    @field_validator('default_audience')
    @classmethod
    def validate_audience(cls, v: str) -> str:
        """Validate audience is a valid enum value"""
        valid_values = ['internal', 'team', 'contributors', 'users', 'public']
        if v not in valid_values:
            raise ValueError(f"Invalid audience: {v}. Must be one of {valid_values}")
        return v

    class Config:
        from_attributes = True


class ProjectVisibilityContext(BaseModel):
    """
    Project context for visibility calculations.

    Provides environmental context that modifies base visibility scores.
    Loaded from project settings in database.
    """

    team_size: str = Field(default="solo", description="Team size category")
    dev_stage: str = Field(default="development", description="Development stage")
    collaboration_model: str = Field(default="private", description="Collaboration model")

    @field_validator('team_size')
    @classmethod
    def validate_team_size(cls, v: str) -> str:
        """Validate team size is valid"""
        valid_values = ['solo', 'small', 'medium', 'large']
        if v not in valid_values:
            raise ValueError(f"Invalid team_size: {v}. Must be one of {valid_values}")
        return v

    @field_validator('dev_stage')
    @classmethod
    def validate_dev_stage(cls, v: str) -> str:
        """Validate development stage is valid"""
        valid_values = ['development', 'staging', 'production']
        if v not in valid_values:
            raise ValueError(f"Invalid dev_stage: {v}. Must be one of {valid_values}")
        return v

    @field_validator('collaboration_model')
    @classmethod
    def validate_collaboration_model(cls, v: str) -> str:
        """Validate collaboration model is valid"""
        valid_values = ['private', 'internal', 'open_source']
        if v not in valid_values:
            raise ValueError(f"Invalid collaboration_model: {v}. Must be one of {valid_values}")
        return v

    class Config:
        from_attributes = True


class VisibilityEvaluation(BaseModel):
    """
    Result of visibility evaluation.

    Contains final visibility decision, scoring details, and rationale.
    Returned by VisibilityPolicyEngine.determine_visibility().
    """

    visibility: str = Field(..., description="Final visibility level (private|restricted|public)")
    audience: str = Field(..., description="Target audience")

    base_score: int = Field(ge=0, le=100, description="Base score from policy")
    final_score: int = Field(description="Final score after modifiers (can exceed 100)")

    context_modifiers: Dict[str, int] = Field(default_factory=dict, description="Applied context modifiers")

    requires_review: bool = Field(default=False, description="Whether review is required")
    auto_publish_on_approved: bool = Field(default=False, description="Whether to auto-publish when approved")

    rationale: str = Field(..., description="Why this visibility was chosen")

    @field_validator('visibility')
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        """Validate visibility is valid"""
        valid_values = ['private', 'restricted', 'public']
        if v not in valid_values:
            raise ValueError(f"Invalid visibility: {v}. Must be one of {valid_values}")
        return v

    @field_validator('audience')
    @classmethod
    def validate_audience(cls, v: str) -> str:
        """Validate audience is valid"""
        valid_values = ['internal', 'team', 'contributors', 'users', 'public']
        if v not in valid_values:
            raise ValueError(f"Invalid audience: {v}. Must be one of {valid_values}")
        return v

    class Config:
        from_attributes = True


class AutoPublishResult(BaseModel):
    """
    Result of auto-publish evaluation.

    Returned by VisibilityPolicyEngine.should_auto_publish().
    """

    should_publish: bool = Field(..., description="Whether to auto-publish")
    trigger_reason: str = Field(..., description="Why auto-publish was triggered (or not)")
    trigger_type: Optional[str] = Field(default=None, description="Type of trigger (on_approved, on_work_item_phase_R1, etc.)")

    class Config:
        from_attributes = True
