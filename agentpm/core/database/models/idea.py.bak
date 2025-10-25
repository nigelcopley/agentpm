"""
Idea Model - Pydantic Domain Model

Lightweight brainstorming entity before work items.

Ideas support a simple 6-state lifecycle:
  idea → research → design → accepted → converted (terminal) OR rejected (terminal)

Pattern: Pydantic BaseModel with Field validation (APM (Agent Project Manager) three-layer standard)
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

from ..enums import IdeaStatus, IdeaSource


class Idea(BaseModel):
    """
    Idea domain model with Pydantic validation.

    Lightweight brainstorming entity before work items.
    Simple lifecycle: idea → research → design → accepted → converted OR rejected

    Ideas enable low-friction capture of concepts that can be voted on,
    refined through research/design, and eventually converted to work items.

    Attributes:
        id: Database primary key (None for new ideas)
        project_id: Parent project ID
        title: Idea title (3-200 characters, required)
        description: Optional detailed description
        source: Origin of idea (user, ai_suggestion, customer_feedback, etc.)
        created_by: Creator identifier (username, email, agent)
        votes: Team votes (≥0, higher = more popular)
        tags: List of tags (["ux", "backend", "quick-win"])
        status: Lifecycle state (idea/research/design/accepted/converted/rejected)
        rejection_reason: Required when status='rejected'
        converted_to_work_item_id: FK to work_items (set when converted)
        converted_at: Timestamp of conversion
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )

    # Primary key
    id: Optional[int] = None

    # Relationships
    project_id: int = Field(..., gt=0)

    # Core fields
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None

    # Attribution
    source: IdeaSource = IdeaSource.USER
    created_by: Optional[str] = None

    # Social engagement
    votes: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)

    # Lifecycle
    status: IdeaStatus = IdeaStatus.IDEA
    rejection_reason: Optional[str] = None

    # Conversion tracking
    converted_to_work_item_id: Optional[int] = Field(default=None, gt=0)
    converted_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('rejection_reason')
    @classmethod
    def validate_rejection_reason(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate rejection_reason is provided when status is 'rejected'.

        Pydantic field validation ensures business rule compliance.
        """
        status = info.data.get('status')
        if status == IdeaStatus.REJECTED and not v:
            raise ValueError("rejection_reason is required when status is 'rejected'")
        return v

    @field_validator('converted_to_work_item_id')
    @classmethod
    def validate_conversion_fields(cls, v: Optional[int], info) -> Optional[int]:
        """
        Validate conversion fields are consistent with status.

        Business rules:
        - status='converted' requires converted_to_work_item_id
        - status!='converted' forbids converted_to_work_item_id
        """
        status = info.data.get('status')

        if status == IdeaStatus.CONVERTED:
            if not v:
                raise ValueError("converted_to_work_item_id is required when status is 'converted'")
        else:
            if v:
                raise ValueError(f"converted_to_work_item_id must be NULL when status is '{status}'")

        return v

    def is_terminal(self) -> bool:
        """Check if idea is in terminal state (converted or rejected)"""
        return IdeaStatus.is_terminal_state(self.status)

    def can_convert(self) -> bool:
        """Check if idea is ready for conversion to work item"""
        return self.status == IdeaStatus.ACTIVE

    def can_vote(self) -> bool:
        """Check if idea can receive votes (not in terminal state)"""
        return not self.is_terminal()

    def can_transition_to(self, new_status: IdeaStatus) -> bool:
        """
        Check if transition to new status is allowed.

        Uses IdeaStatus.allowed_transitions() for state machine validation.

        Args:
            new_status: Target status

        Returns:
            True if transition is allowed
        """
        return new_status in IdeaStatus.allowed_transitions(self.status)

    def get_allowed_transitions(self) -> list[IdeaStatus]:
        """
        Get list of allowed next states from current state.

        Returns:
            List of valid next states
        """
        return IdeaStatus.allowed_transitions(self.status)
