"""
Project Model - Pydantic Domain Model

Type-safe project model with validation following professional standards.

Pattern: Pydantic BaseModel with Field validation
Industry Standards: FastAPI, SQLAlchemy 2.0, Django Ninja
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from ..enums import ProjectStatus, ProjectType


class Project(BaseModel):
    """
    Project domain model with Pydantic validation.

    Projects are the top-level organizational unit in AIPM,
    containing work items, tasks, and context.

    Lifecycle: initiated → active → on_hold → completed → archived

    Note: Development philosophy (kiss_first, professional_standards, etc.)
    is enforced through the Rules system, not stored as a project field.

    Attributes:
        id: Database primary key (None for new projects)
        name: Project name (unique, 1-200 characters)
        description: Optional project description
        path: Filesystem path to project directory
        tech_stack: List of detected technologies
        detected_frameworks: List of detected frameworks
        status: Project lifecycle status (simple workflow)
        business_domain: Optional business domain (Migration 0011)
        business_description: Optional business description (Migration 0011)
        project_type: Optional project type (Migration 0011)
        team: Optional team name (Migration 0011)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        validate_assignment=True,  # Validate on attribute assignment
        use_enum_values=False,     # Keep enum types (don't convert to strings)
        str_strip_whitespace=True, # Strip whitespace from strings
    )

    # Primary key
    id: Optional[int] = None

    # Core fields
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    path: str = Field(..., min_length=1)

    # Technical context (detected by plugin system)
    tech_stack: list[str] = Field(default_factory=list)
    detected_frameworks: list[str] = Field(default_factory=list)

    # Configuration metadata (JSON - WI-40 consolidation)
    metadata: Optional[str] = Field(default='{}')

    # Lifecycle (simple project workflow)
    status: ProjectStatus = ProjectStatus.INITIATED

    # NEW (Migration 0011): Business and team fields
    business_domain: Optional[str] = Field(default=None, max_length=200)
    business_description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    team: Optional[str] = Field(default=None, max_length=200)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if project is in active development"""
        return ProjectStatus.is_active_state(self.status)

    def is_complete(self) -> bool:
        """Check if project is completed"""
        return self.status == ProjectStatus.DONE

    def can_transition_to(self, new_status: ProjectStatus) -> bool:
        """
        Check if transition to new status is valid.

        Note: Full transition validation is in utils/state_validators.py
        This is a simple check for the model itself.
        """
        # Can always move to same status
        if self.status == new_status:
            return True

        # Completed can only move to archived
        if self.status == ProjectStatus.DONE:
            return new_status == ProjectStatus.ARCHIVED

        # Otherwise, use workflow order
        return True  # Full validation in state_validators