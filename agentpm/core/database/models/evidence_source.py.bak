"""
Evidence Source Model

Tracks research evidence and decision rationale for work items and tasks.
Enables traceability and verification of decisions.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from agentpm.core.database.enums import EntityType, SourceType


class EvidenceSource(BaseModel):
    """
    Evidence source for research traceability.

    Tracks where information came from (research, documentation, meetings, etc.)
    and links it to the entity (project, work item, or task) that used it.

    Used for:
    - Decision traceability ("why did we choose this approach?")
    - Research evidence ("what sources support this requirement?")
    - Compliance documentation ("how do we know this meets the standard?")

    Example:
        evidence = EvidenceSource(
            entity_type=EntityType.WORK_ITEM,
            entity_id=43,
            url="https://docs.djangoproject.com/en/4.2/topics/auth/",
            source_type=SourceType.DOCUMENTATION,
            excerpt="Django provides authentication out of the box",
            confidence=0.9,
            created_by="requirements-analyst"
        )
    """

    id: Optional[int] = None
    entity_type: EntityType = Field(..., description="Type of entity this evidence supports")
    entity_id: int = Field(..., gt=0, description="ID of the entity")

    # Evidence details
    url: Optional[str] = Field(None, max_length=2000, description="Source URL")
    source_type: Optional[SourceType] = Field(None, description="Classification of source")
    excerpt: Optional[str] = Field(None, max_length=1000, description="Key quote or summary")
    captured_at: datetime = Field(default_factory=datetime.utcnow, description="When evidence was captured")

    # Verification
    content_hash: Optional[str] = Field(None, max_length=64, description="SHA256 hash of content for change detection")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in this source (0.0-1.0)")

    # Metadata
    created_by: Optional[str] = Field(None, max_length=200, description="Agent or user who added this evidence")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "entity_type": "work_item",
                "entity_id": 43,
                "url": "https://example.com/research",
                "source_type": "research",
                "excerpt": "Market research shows 85% demand for this feature",
                "confidence": 0.85,
                "created_by": "market-researcher"
            }
        }

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
