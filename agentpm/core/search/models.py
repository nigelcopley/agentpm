"""
Search Configuration Models

Core configuration models for the search system including search queries,
filters, and configuration. Database models are in core/database/models/.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum

from ..database.enums import EntityType, WorkItemStatus, TaskStatus, IdeaStatus


class SearchMode(str, Enum):
    """Search execution modes."""
    
    TEXT = "text"           # Basic text matching
    SEMANTIC = "semantic"   # Vector/semantic search (future)
    HYBRID = "hybrid"       # Combined text + semantic
    METADATA = "metadata"   # Metadata-only search


class SearchScope(str, Enum):
    """Search scope options."""

    ALL = "all"                    # Search all entities
    WORK_ITEMS = "work_items"      # Work items only
    TASKS = "tasks"               # Tasks only
    IDEAS = "ideas"               # Ideas only
    DOCUMENTS = "documents"        # Documents only
    SUMMARIES = "summaries"        # Summaries only
    EVIDENCE = "evidence"          # Evidence sources only
    SESSIONS = "sessions"          # Sessions only
    LEARNINGS = "learnings"        # Learnings only (reserved for future use)


class SearchFilter(BaseModel):
    """Search filter configuration."""
    
    # Entity filters
    entity_types: Optional[List[EntityType]] = Field(default=None, description="Filter by entity types")
    entity_ids: Optional[List[int]] = Field(default=None, description="Filter by specific entity IDs")
    
    # Status filters
    work_item_statuses: Optional[List[WorkItemStatus]] = Field(default=None, description="Filter by work item status")
    task_statuses: Optional[List[TaskStatus]] = Field(default=None, description="Filter by task status")
    idea_statuses: Optional[List[IdeaStatus]] = Field(default=None, description="Filter by idea status")
    
    # Project and relationship filters
    project_id: Optional[int] = Field(default=None, description="Filter by project ID")
    work_item_id: Optional[int] = Field(default=None, description="Filter by work item ID")
    task_id: Optional[int] = Field(default=None, description="Filter by task ID")
    
    # Content filters
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    created_by: Optional[str] = Field(default=None, description="Filter by creator")
    
    # Date filters
    created_after: Optional[datetime] = Field(default=None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(default=None, description="Filter by creation date (before)")
    updated_after: Optional[datetime] = Field(default=None, description="Filter by update date (after)")
    updated_before: Optional[datetime] = Field(default=None, description="Filter by update date (before)")
    
    # Content-specific filters
    min_relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum relevance score")
    include_archived: bool = Field(default=False, description="Include archived entities")
    
    @validator('entity_types')
    def validate_entity_types(cls, v):
        if v is not None and not v:
            raise ValueError("entity_types cannot be empty list")
        return v


class SearchQuery(BaseModel):
    """Search query configuration."""
    
    # Core query
    query: str = Field(..., min_length=1, description="Search query text")
    
    # Search configuration
    mode: SearchMode = Field(default=SearchMode.TEXT, description="Search mode")
    scope: SearchScope = Field(default=SearchScope.ALL, description="Search scope")
    
    # Result configuration
    limit: int = Field(default=20, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Result offset for pagination")
    
    # Search options
    case_sensitive: bool = Field(default=False, description="Case-sensitive search")
    exact_match: bool = Field(default=False, description="Exact phrase matching")
    include_content: bool = Field(default=False, description="Include full content in results")
    
    # Filters
    filters: Optional[SearchFilter] = Field(default=None, description="Search filters")
    
    # Advanced options
    boost_fields: Optional[Dict[str, float]] = Field(default=None, description="Field boost weights")
    highlight: bool = Field(default=True, description="Enable search highlighting")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()
    
    @validator('boost_fields')
    def validate_boost_fields(cls, v):
        if v is not None:
            for field, weight in v.items():
                if weight < 0 or weight > 10:
                    raise ValueError(f"Boost weight for '{field}' must be between 0 and 10")
        return v


class SearchConfig(BaseModel):
    """Search system configuration."""
    
    # Performance settings
    max_results: int = Field(default=1000, ge=1, le=10000, description="Maximum results per query")
    timeout_ms: int = Field(default=5000, ge=100, le=30000, description="Search timeout in milliseconds")
    cache_enabled: bool = Field(default=True, description="Enable search result caching")
    cache_ttl_seconds: int = Field(default=300, ge=60, le=3600, description="Cache TTL in seconds")
    
    # Search quality settings
    default_min_relevance: float = Field(default=0.1, ge=0.0, le=1.0, description="Default minimum relevance")
    fuzzy_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Fuzzy matching threshold")
    semantic_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Semantic matching threshold")
    
    # Indexing settings
    auto_index: bool = Field(default=True, description="Automatically index new entities")
    index_batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size for indexing")
    index_refresh_interval: int = Field(default=60, ge=10, le=3600, description="Index refresh interval in seconds")
    
    # Feature flags
    enable_semantic_search: bool = Field(default=False, description="Enable semantic/vector search")
    enable_highlighting: bool = Field(default=True, description="Enable search result highlighting")
    enable_suggestions: bool = Field(default=True, description="Enable search suggestions")
    enable_analytics: bool = Field(default=True, description="Enable search analytics")




# Re-export existing search result models
from ..database.models.search_result import SearchResult, SearchResults, SearchResultType
# Re-export database models
from ..database.models.search_index import SearchIndex
from ..database.models.search_metrics import SearchMetrics

__all__ = [
    'SearchMode',
    'SearchScope', 
    'SearchFilter',
    'SearchQuery',
    'SearchConfig',
    'SearchIndex',
    'SearchMetrics',
    'SearchResult',
    'SearchResults',
    'SearchResultType'
]
