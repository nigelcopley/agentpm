"""
Summary Model - Polymorphic Summary System

Pydantic model for hierarchical summary system supporting summaries at all levels
of the APM (Agent Project Manager) hierarchy: projects, sessions, work items, and tasks.

Design:
- Polymorphic assignment to any entity type
- Rich metadata for AI parsing
- Session linkage for traceability
- Legacy support for existing work_item_summaries

Pattern: Pydantic BaseModel with Field validation (APM (Agent Project Manager) three-layer standard)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from ..enums import EntityType, SummaryType


class Summary(BaseModel):
    """
    Polymorphic summary model for all entity types.
    
    Supports summaries at any level of the APM (Agent Project Manager) hierarchy:
    - Project summaries (strategic, milestone, retrospective)
    - Session summaries (handover, progress, error analysis)
    - Work item summaries (progress, milestone, decision)
    - Task summaries (completion, progress, blocker resolution)
    
    Attributes:
        id: Database primary key (None for new summaries)
        entity_type: Type of entity this summary belongs to (project, session, work_item, task)
        entity_id: ID of the entity this summary belongs to
        summary_type: Type of summary (milestone, decision, retrospective, etc.)
        summary_text: Markdown-formatted summary content (min 10 chars)
        context_metadata: Structured metadata for AI parsing (JSON)
        created_at: Creation timestamp
        created_by: Creator identifier (username, email, agent)
        session_id: Optional link to session for traceability
        session_date: Optional session date (YYYY-MM-DD format)
        session_duration_hours: Optional session duration in hours
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "entity_type": "work_item",
                "entity_id": 42,
                "summary_type": "work_item_progress",
                "summary_text": "## Progress Update\n\nCompleted the database schema design and started implementation.",
                "context_metadata": {
                    "key_decisions": ["PostgreSQL for primary storage"],
                    "technical_changes": ["Added database models"],
                    "blockers_resolved": [],
                    "next_steps": ["Complete implementation"]
                },
                "created_by": "claude-agent",
                "session_id": 15,
                "session_date": "2025-01-15",
                "session_duration_hours": 2.5
            }
        }
    )

    # Primary key
    id: Optional[int] = None

    # Polymorphic assignment (follows APM (Agent Project Manager) EntityType pattern)
    entity_type: EntityType = Field(..., description="Type of entity this summary belongs to")
    entity_id: int = Field(..., gt=0, description="ID of the entity this summary belongs to")

    # Summary classification
    summary_type: SummaryType = Field(..., description="Type of summary")
    summary_text: str = Field(
        ..., 
        min_length=10, 
        description="Markdown-formatted summary content"
    )

    # Structured metadata (AI parseable)
    context_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured metadata for AI parsing (JSON)"
    )

    # Attribution & traceability
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    created_by: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Creator identifier (username, email, agent)"
    )
    session_id: Optional[int] = Field(
        default=None, 
        gt=0,
        description="Optional link to session for traceability"
    )

    # Optional session context (for session-level summaries)
    session_date: Optional[str] = Field(
        default=None,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Optional session date in YYYY-MM-DD format"
    )
    session_duration_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Optional session duration in hours"
    )

    @field_validator('summary_type')
    @classmethod
    def validate_summary_type_for_entity(cls, v: SummaryType, info) -> SummaryType:
        """Validate that summary type is appropriate for entity type."""
        entity_type = info.data.get('entity_type')
        if entity_type:
            appropriate_types = SummaryType.get_appropriate_types(entity_type)
            if v not in appropriate_types:
                # For legacy support, allow all types but warn
                # In future versions, this could be stricter
                pass
        return v

    @field_validator('session_date')
    @classmethod
    def validate_session_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate session date format."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError("session_date must be in YYYY-MM-DD format")
        return v

    def to_legacy_work_item_summary(self) -> 'WorkItemSummary':
        """Convert to legacy WorkItemSummary format for migration."""
        from .work_item_summary import WorkItemSummary
        
        if self.entity_type != EntityType.WORK_ITEM:
            raise ValueError("Can only convert work item summaries to legacy format")
        
        return WorkItemSummary(
            id=self.id,
            work_item_id=self.entity_id,
            session_date=self.session_date or datetime.now().strftime('%Y-%m-%d'),
            session_duration_hours=self.session_duration_hours,
            summary_text=self.summary_text,
            context_metadata=self.context_metadata,
            created_at=self.created_at,
            created_by=self.created_by,
            summary_type=self.summary_type.value
        )

    @classmethod
    def from_legacy_work_item_summary(cls, legacy: 'WorkItemSummary') -> 'Summary':
        """Create Summary from legacy WorkItemSummary."""
        return cls(
            id=legacy.id,
            entity_type=EntityType.WORK_ITEM,
            entity_id=legacy.work_item_id,
            summary_type=SummaryType(legacy.summary_type),
            summary_text=legacy.summary_text,
            context_metadata=legacy.context_metadata,
            created_at=legacy.created_at,
            created_by=legacy.created_by,
            session_date=legacy.session_date,
            session_duration_hours=legacy.session_duration_hours
        )

    def get_entity_reference(self) -> str:
        """Get human-readable entity reference."""
        return f"{self.entity_type.value} #{self.entity_id}"

    def get_summary_title(self) -> str:
        """Get human-readable summary title."""
        return f"{self.summary_type.value.replace('_', ' ').title()} for {self.get_entity_reference()}"

    def is_legacy_type(self) -> bool:
        """Check if this uses a legacy summary type."""
        legacy_types = {
            SummaryType.SESSION,
            SummaryType.MILESTONE,
            SummaryType.DECISION,
            SummaryType.RETROSPECTIVE,
        }
        return self.summary_type in legacy_types

    def get_modern_type(self) -> SummaryType:
        """Get the modern equivalent of legacy summary types."""
        legacy_mapping = {
            SummaryType.SESSION: SummaryType.SESSION_HANDOVER,
            SummaryType.MILESTONE: SummaryType.WORK_ITEM_MILESTONE,
            SummaryType.DECISION: SummaryType.WORK_ITEM_DECISION,
            SummaryType.RETROSPECTIVE: SummaryType.WORK_ITEM_RETROSPECTIVE,
        }
        return legacy_mapping.get(self.summary_type, self.summary_type)
