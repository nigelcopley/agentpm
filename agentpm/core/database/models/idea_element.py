"""
Idea Element Model - Pydantic Domain Model

Represents components/parts of an idea that can be broken down into tasks
when the idea is converted to a work item.

Idea elements enable structured breakdown of complex ideas into manageable
components, providing better estimation and planning capabilities.

Pattern: Pydantic BaseModel with Field validation (APM (Agent Project Manager) three-layer standard)
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

from ..enums import TaskType


class IdeaElement(BaseModel):
    """
    Idea element domain model with Pydantic validation.

    Represents a component/part of an idea that can be broken down into
    a task when the idea is converted to a work item.

    Idea elements provide structured breakdown of complex ideas, enabling:
    - Better effort estimation through component-level estimates
    - Clearer planning and task creation during conversion
    - Improved understanding of idea scope and complexity
    - Better tracking of idea progress through element completion

    Attributes:
        id: Database primary key (None for new elements)
        idea_id: Parent idea ID
        title: Element title (3-200 characters, required)
        description: Optional detailed description
        type: Type of element (implementation, research, design, testing, etc.)
        effort_hours: Estimated effort in hours (≥0.1, required)
        order_index: Display order within idea (≥0, required)
        is_completed: Whether element is completed (default: False)
        completed_at: Timestamp of completion (set when is_completed=True)
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
    idea_id: int = Field(..., gt=0)

    # Core fields
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None

    # Element classification
    type: TaskType = TaskType.IMPLEMENTATION

    # Effort estimation
    effort_hours: float = Field(..., ge=0.1, le=1000.0)

    # Ordering and completion
    order_index: int = Field(..., ge=0)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('completed_at')
    @classmethod
    def validate_completion_fields(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """
        Validate completion fields are consistent with is_completed status.

        Business rules:
        - is_completed=True requires completed_at
        - is_completed=False forbids completed_at
        """
        is_completed = info.data.get('is_completed', False)

        if is_completed:
            if not v:
                raise ValueError("completed_at is required when is_completed is True")
        else:
            if v:
                raise ValueError("completed_at must be NULL when is_completed is False")

        return v

    def mark_completed(self) -> None:
        """Mark element as completed with current timestamp"""
        self.is_completed = True
        self.completed_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark element as incomplete, clearing completion timestamp"""
        self.is_completed = False
        self.completed_at = None

    def get_completion_percentage(self) -> float:
        """Get completion percentage (0.0 to 1.0)"""
        return 1.0 if self.is_completed else 0.0

    def to_task_data(self) -> dict:
        """
        Convert element to task creation data.

        Returns:
            Dictionary with task creation parameters
        """
        return {
            'name': self.title,
            'description': self.description,
            'type': self.type,
            'effort_hours': self.effort_hours,
            'status': 'proposed'  # Default status for new tasks
        }
