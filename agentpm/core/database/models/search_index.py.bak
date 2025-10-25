"""
Search Index Model - Pydantic Domain Model

Type-safe search index model with validation.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from ..enums import EntityType


class SearchIndex(BaseModel):
    """
    Search index domain model with Pydantic validation.

    Represents metadata and statistics for a search index
    for a specific entity type.

    Attributes:
        id: Database primary key (None for new indexes)
        entity_type: Entity type this index covers
        index_version: Version of the index format
        total_documents: Total number of documents in index
        last_updated: When index was last updated
        index_size_bytes: Size of index in bytes
        avg_document_size: Average document size in bytes
        unique_terms: Number of unique terms in index
        total_terms: Total number of terms in index
        build_time_ms: Time taken to build index in milliseconds
        query_time_ms: Average query time in milliseconds
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

    # Core fields
    entity_type: EntityType = Field(..., description="Entity type this index covers")
    index_version: str = Field(..., min_length=1, description="Index version")
    total_documents: int = Field(..., ge=0, description="Total documents in index")
    last_updated: datetime = Field(..., description="Last index update")
    index_size_bytes: int = Field(..., ge=0, description="Index size in bytes")

    # Index statistics
    avg_document_size: float = Field(..., ge=0, description="Average document size")
    unique_terms: int = Field(..., ge=0, description="Number of unique terms")
    total_terms: int = Field(..., ge=0, description="Total terms in index")

    # Performance metrics
    build_time_ms: float = Field(..., ge=0, description="Index build time in milliseconds")
    query_time_ms: float = Field(..., ge=0, description="Average query time in milliseconds")

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
