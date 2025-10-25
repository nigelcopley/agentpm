"""
Document Service Models

Pydantic models for document services including search results.
"""

from typing import List, Tuple, Optional
from pydantic import BaseModel, Field


class DocumentSearchResult(BaseModel):
    """
    Document search result with content snippet and highlighting.

    Attributes:
        document_id: Unique document identifier
        title: Document title
        file_path: Path to document file
        snippet: Content excerpt containing search match
        rank: Relevance score (0.0 to 1.0, higher is more relevant)
        matched_terms: List of query terms that matched
        highlights: List of (start, end) character positions for highlighting
    """

    document_id: int = Field(..., description="Document ID from database")
    title: str = Field(..., description="Document title")
    file_path: str = Field(..., description="File path relative to project root")
    snippet: str = Field(..., description="Content snippet with search match")
    rank: float = Field(..., ge=0.0, le=1.0, description="Relevance score (BM25)")
    matched_terms: List[str] = Field(
        default_factory=list,
        description="Query terms that matched in content"
    )
    highlights: List[Tuple[int, int]] = Field(
        default_factory=list,
        description="Character positions (start, end) for highlighting matches"
    )

    # Optional metadata
    document_type: Optional[str] = Field(None, description="Document type")
    entity_type: Optional[str] = Field(None, description="Associated entity type")
    entity_id: Optional[int] = Field(None, description="Associated entity ID")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": 42,
                "title": "Architecture Design Document",
                "file_path": "docs/architecture/design/system-design.md",
                "snippet": "...microservices architecture enables scalability...",
                "rank": 0.85,
                "matched_terms": ["architecture", "microservices"],
                "highlights": [(10, 22), (45, 58)],
                "document_type": "design",
                "entity_type": "work_item",
                "entity_id": 133
            }
        }


__all__ = ['DocumentSearchResult']
