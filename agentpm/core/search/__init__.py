"""
Core Search Module

Unified search functionality for APM (Agent Project Manager) with support for:
- Text search across all entities
- Semantic/vector search (future)
- Metadata filtering
- Relevance scoring
- Search result ranking

Architecture:
- Models: Search configuration and result models
- Adapters: Entity-specific search adapters
- Methods: Core search algorithms and indexing
- Service: Unified search service interface
"""

from .models import (
    SearchConfig,
    SearchQuery,
    SearchFilter,
    SearchResult,
    SearchResults,
    SearchIndex,
    SearchMetrics
)

from .adapters import (
    BaseSearchAdapter,
    WorkItemSearchAdapter,
    TaskSearchAdapter,
    IdeaSearchAdapter,
    DocumentSearchAdapter,
    SummarySearchAdapter,
    EvidenceSearchAdapter,
    LearningSearchAdapter,
    SessionSearchAdapter
)

from .methods import (
    TextSearchEngine,
    MetadataSearchEngine,
    RelevanceCalculator,
    SearchIndexer,
    SearchRanker
)

from .service import SearchService

__all__ = [
    # Models
    'SearchConfig',
    'SearchQuery', 
    'SearchFilter',
    'SearchResult',
    'SearchResults',
    'SearchIndex',
    'SearchMetrics',
    
    # Adapters
    'BaseSearchAdapter',
    'WorkItemSearchAdapter',
    'TaskSearchAdapter',
    'IdeaSearchAdapter',
    'DocumentSearchAdapter',
    'SummarySearchAdapter',
    'EvidenceSearchAdapter',
    'LearningSearchAdapter',
    'SessionSearchAdapter',
    
    # Methods
    'TextSearchEngine',
    'MetadataSearchEngine',
    'RelevanceCalculator',
    'SearchIndexer',
    'SearchRanker',
    
    # Service
    'SearchService'
]
