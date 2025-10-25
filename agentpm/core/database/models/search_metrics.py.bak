"""
Search Metrics Model - Pydantic Domain Model

Type-safe search metrics model with validation.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class SearchMetrics(BaseModel):
    """
    Search metrics domain model with Pydantic validation.

    Represents performance and usage metrics for the search system.

    Attributes:
        id: Database primary key (None for new metrics)
        project_id: Parent project ID
        total_queries: Total queries executed
        avg_query_time_ms: Average query time in milliseconds
        avg_results_per_query: Average results per query
        avg_relevance_score: Average relevance score (0.0-1.0)
        high_relevance_ratio: Ratio of high relevance results (>=0.8)
        zero_result_ratio: Ratio of queries with no results
        cache_hit_ratio: Cache hit ratio (0.0-1.0)
        index_size_mb: Total index size in MB
        memory_usage_mb: Memory usage in MB
        most_common_queries: List of (query, count) tuples
        entity_type_distribution: Results count by entity type
        search_mode_distribution: Usage count by search mode
        metrics_period_start: Start of metrics collection period
        metrics_period_end: End of metrics collection period
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
    project_id: int = Field(..., gt=0, description="Parent project ID")

    # Query metrics
    total_queries: int = Field(..., ge=0, description="Total queries executed")
    avg_query_time_ms: float = Field(..., ge=0, description="Average query time")
    avg_results_per_query: float = Field(..., ge=0, description="Average results per query")

    # Quality metrics
    avg_relevance_score: float = Field(..., ge=0.0, le=1.0, description="Average relevance score")
    high_relevance_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of high relevance results")
    zero_result_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of queries with no results")

    # Performance metrics
    cache_hit_ratio: float = Field(..., ge=0.0, le=1.0, description="Cache hit ratio")
    index_size_mb: float = Field(..., ge=0, description="Total index size in MB")
    memory_usage_mb: float = Field(..., ge=0, description="Memory usage in MB")

    # Usage patterns
    most_common_queries: List[Tuple[str, int]] = Field(
        default_factory=list, 
        description="Most common queries"
    )
    entity_type_distribution: Dict[str, int] = Field(
        default_factory=dict, 
        description="Results by entity type"
    )
    search_mode_distribution: Dict[str, int] = Field(
        default_factory=dict, 
        description="Usage by search mode"
    )

    # Timestamps
    metrics_period_start: datetime = Field(..., description="Metrics period start")
    metrics_period_end: datetime = Field(..., description="Metrics period end")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
