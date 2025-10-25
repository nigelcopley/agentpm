"""
Search Result Model

Unified search result model for vector search across all APM (Agent Project Manager) entities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

from ..enums import EntityType


class SearchResultType(str, Enum):
    """Types of search results for categorization."""
    
    # Entity results
    WORK_ITEM = "work_item"
    TASK = "task"
    IDEA = "idea"
    DOCUMENT = "document"
    SUMMARY = "summary"
    EVIDENCE = "evidence"
    LEARNING = "learning"
    SESSION = "session"
    
    # Content results
    CONTENT_MATCH = "content_match"
    METADATA_MATCH = "metadata_match"
    TAG_MATCH = "tag_match"
    RELATIONSHIP_MATCH = "relationship_match"


class SearchResult(BaseModel):
    """
    Unified search result model for vector search across all APM (Agent Project Manager) entities.
    
    This model represents a single search result that can come from any entity
    type in the APM (Agent Project Manager) hierarchy, with relevance scoring and context.
    """
    
    # Core identification
    id: int = Field(..., description="Unique identifier for the search result")
    entity_type: EntityType = Field(..., description="Type of entity this result represents")
    entity_id: int = Field(..., gt=0, description="ID of the entity")
    result_type: SearchResultType = Field(..., description="Type of search result")
    
    # Content and context
    title: str = Field(..., min_length=1, description="Display title for the result")
    content: str = Field(..., min_length=1, description="Main content text")
    excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from content")
    
    # Search relevance
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    match_type: str = Field(..., description="How the match was found (exact, fuzzy, semantic)")
    matched_fields: List[str] = Field(default_factory=list, description="Fields that matched the search")
    
    # Metadata
    created_at: Optional[datetime] = Field(default=None, description="When the entity was created")
    updated_at: Optional[datetime] = Field(default=None, description="When the entity was last updated")
    created_by: Optional[str] = Field(default=None, description="Who created the entity")
    
    # Context and relationships
    project_id: Optional[int] = Field(default=None, description="Associated project ID")
    work_item_id: Optional[int] = Field(default=None, description="Associated work item ID")
    task_id: Optional[int] = Field(default=None, description="Associated task ID")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Tags associated with the entity")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    # Search context
    search_query: str = Field(..., description="Original search query")
    search_timestamp: datetime = Field(default_factory=datetime.now, description="When search was performed")
    
    def get_entity_reference(self) -> str:
        """Get human-readable entity reference."""
        return f"{self.entity_type.value} #{self.entity_id}"
    
    def get_display_title(self) -> str:
        """Get formatted display title with entity reference."""
        return f"{self.title} ({self.get_entity_reference()})"
    
    def get_relevance_indicator(self) -> str:
        """Get visual indicator for relevance score."""
        if self.relevance_score >= 0.8:
            return "🟢"  # High relevance
        elif self.relevance_score >= 0.6:
            return "🟡"  # Medium relevance
        elif self.relevance_score >= 0.4:
            return "🟠"  # Low relevance
        else:
            return "🔴"  # Very low relevance
    
    def get_match_summary(self) -> str:
        """Get summary of how the match was found."""
        if not self.matched_fields:
            return f"{self.match_type} match"
        
        fields_str = ", ".join(self.matched_fields)
        return f"{self.match_type} match in {fields_str}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'entity_type': self.entity_type.value,
            'entity_id': self.entity_id,
            'result_type': self.result_type.value,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'relevance_score': self.relevance_score,
            'match_type': self.match_type,
            'matched_fields': self.matched_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'project_id': self.project_id,
            'work_item_id': self.work_item_id,
            'task_id': self.task_id,
            'tags': self.tags,
            'metadata': self.metadata,
            'search_query': self.search_query,
            'search_timestamp': self.search_timestamp.isoformat(),
            'entity_reference': self.get_entity_reference(),
            'display_title': self.get_display_title(),
            'relevance_indicator': self.get_relevance_indicator(),
            'match_summary': self.get_match_summary()
        }


class SearchResults(BaseModel):
    """
    Container for multiple search results with metadata.
    """
    
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., ge=0, description="Total number of results found")
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    
    # Search metadata
    search_time_ms: float = Field(..., ge=0, description="Search execution time in milliseconds")
    search_timestamp: datetime = Field(default_factory=datetime.now, description="When search was performed")
    
    # Result categorization
    entity_type_counts: Dict[str, int] = Field(default_factory=dict, description="Count by entity type")
    result_type_counts: Dict[str, int] = Field(default_factory=dict, description="Count by result type")
    
    # Relevance statistics
    avg_relevance_score: float = Field(..., ge=0.0, le=1.0, description="Average relevance score")
    high_relevance_count: int = Field(..., ge=0, description="Count of high relevance results (>=0.8)")
    
    def get_summary(self) -> str:
        """Get human-readable search summary."""
        return (
            f"Found {self.total_results} results for '{self.query}' "
            f"in {self.search_time_ms:.1f}ms "
            f"(avg relevance: {self.avg_relevance_score:.2f})"
        )
    
    def get_entity_type_summary(self) -> str:
        """Get summary of results by entity type."""
        if not self.entity_type_counts:
            return "No entity type breakdown available"
        
        parts = []
        for entity_type, count in sorted(self.entity_type_counts.items(), key=lambda x: x[1], reverse=True):
            parts.append(f"{entity_type}: {count}")
        
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'query': self.query,
            'total_results': self.total_results,
            'results': [result.to_dict() for result in self.results],
            'search_time_ms': self.search_time_ms,
            'search_timestamp': self.search_timestamp.isoformat(),
            'entity_type_counts': self.entity_type_counts,
            'result_type_counts': self.result_type_counts,
            'avg_relevance_score': self.avg_relevance_score,
            'high_relevance_count': self.high_relevance_count,
            'summary': self.get_summary(),
            'entity_type_summary': self.get_entity_type_summary()
        }
