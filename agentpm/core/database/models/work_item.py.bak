"""
WorkItem Model - Pydantic Domain Model

Type-safe work item model with validation.

Work items represent discrete deliverables: features, analyses, objectives, or research.
They follow the complete workflow lifecycle.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import datetime

from ..enums import WorkItemStatus, WorkItemType, Phase


class WorkItem(BaseModel):
    """
    Work item domain model with Pydantic validation.

    Work items are discrete deliverables within a project:
    - Features: New functionality
    - Analysis: Research or investigation
    - Objective: Goal or milestone
    - Research: Exploration or study

    Lifecycle: ideas → proposed → validated → accepted → in_progress → review → completed → archived

    Attributes:
        id: Database primary key (None for new work items)
        project_id: Parent project ID
        parent_work_item_id: Optional parent work item (for hierarchical breakdown)
        name: Work item name (1-200 characters)
        description: Optional detailed description
        type: Work item type (feature/analysis/objective/research)
        business_context: Business rationale and context
        is_continuous: Continuous backlog flag (never completes)
        effort_estimate_hours: Estimated effort in hours
        status: Work item workflow status
        priority: Priority level (1-5, 1=highest)
        phase: Optional project phase (Migration 0011)
        due_date: Optional due date (Migration 0011)
        not_before: Optional earliest start date (Migration 0011)
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
    parent_work_item_id: Optional[int] = Field(default=None, gt=0)
    originated_from_idea_id: Optional[int] = Field(default=None, gt=0)

    # Core fields
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: WorkItemType = WorkItemType.FEATURE

    # Context
    business_context: Optional[str] = None

    # Configuration metadata (JSON - WI-40 consolidation)
    metadata: Optional[str] = Field(default='{}')
    is_continuous: bool = False

    # Planning
    effort_estimate_hours: Optional[float] = Field(default=None, ge=0)
    priority: int = Field(default=3, ge=1, le=5)

    # Lifecycle
    status: WorkItemStatus = WorkItemStatus.DRAFT

    # NEW (Migration 0011): Phase and scheduling fields
    phase: Optional[Phase] = None
    due_date: Optional[datetime] = None
    not_before: Optional[datetime] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="after")
    def _enforce_continuous_flag(self):
        """
        Ensure continuous flag aligns with work item type.

        Continuous types (maintenance/monitoring/documentation/security/fix_bugs_issues)
        always persist with `is_continuous=True` regardless of incoming value.
        """
        if WorkItemType.is_continuous_type(self.type):
            object.__setattr__(self, 'is_continuous', True)
        return self

    def is_active(self) -> bool:
        """Check if work item is actively being worked on"""
        return self.status == WorkItemStatus.ACTIVE

    def is_complete(self) -> bool:
        """Check if work item is completed"""
        if self.is_continuous:
            return False
        return self.status == WorkItemStatus.DONE

    def has_parent(self) -> bool:
        """Check if this work item is a sub-item"""
        return self.parent_work_item_id is not None
