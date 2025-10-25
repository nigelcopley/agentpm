"""
Search Service

Unified search service that orchestrates all search functionality
across the APM (Agent Project Manager) system.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import time
from collections import defaultdict

from ..database.service import DatabaseService
from ..database.enums import EntityType
from ..database.models.search_result import SearchResult, SearchResults
from .models import (
    SearchQuery, SearchFilter, SearchConfig, SearchScope, SearchMode
)
from ..database.models import SearchIndex, SearchMetrics
from .adapters import (
    BaseSearchAdapter, SEARCH_ADAPTERS, WorkItemSearchAdapter,
    TaskSearchAdapter, IdeaSearchAdapter, DocumentSearchAdapter,
    SummarySearchAdapter, EvidenceSearchAdapter, LearningSearchAdapter,
    SessionSearchAdapter
)
from .methods import (
    TextSearchEngine, MetadataSearchEngine, RelevanceCalculator,
    SearchIndexer, SearchRanker
)
from .fts5_service import FTS5SearchService


class SearchService:
    """
    Unified search service for APM (Agent Project Manager).
    
    Provides a single interface for searching across all entity types
    with support for text search, metadata filtering, and relevance scoring.
    """
    
    def __init__(self, db_service: DatabaseService, config: Optional[SearchConfig] = None):
        self.db_service = db_service
        self.config = config or SearchConfig()
        
        # Initialize FTS5 service (preferred) and fallback engines
        self.fts5_service = FTS5SearchService(db_service, self.config)
        self.text_engine = TextSearchEngine(self.config)
        self.metadata_engine = MetadataSearchEngine(self.config)
        self.relevance_calculator = RelevanceCalculator(self.config)
        self.indexer = SearchIndexer(db_service, self.config)
        self.ranker = SearchRanker(self.config)
        
        # Initialize search adapters
        self.adapters: Dict[EntityType, BaseSearchAdapter] = {}
        self._initialize_adapters()
        
        # Search metrics
        self.metrics = SearchMetrics(
            project_id=1,  # Default project ID for metrics
            total_queries=0,
            avg_query_time_ms=0.0,
            avg_results_per_query=0.0,
            avg_relevance_score=0.0,
            high_relevance_ratio=0.0,
            zero_result_ratio=0.0,
            cache_hit_ratio=0.0,
            index_size_mb=0.0,
            memory_usage_mb=0.0,
            metrics_period_start=datetime.now(),
            metrics_period_end=datetime.now()
        )
    
    def _initialize_adapters(self):
        """Initialize search adapters for all entity types."""
        for entity_type, adapter_class in SEARCH_ADAPTERS.items():
            self.adapters[entity_type] = adapter_class(self.db_service)
    
    def search(self, query: SearchQuery) -> SearchResults:
        """
        Perform unified search across all entity types using FTS5 when available.
        
        Args:
            query: Search query configuration
            
        Returns:
            Search results with metadata
        """
        # Use FTS5 service for high-performance search
        return self.fts5_service.search(query)
    
    def search_work_items(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search work items specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.WORK_ITEMS,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_tasks(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search tasks specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.TASKS,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_ideas(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search ideas specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.IDEAS,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_documents(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search documents specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.DOCUMENTS,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_summaries(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search summaries specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.SUMMARIES,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_evidence(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search evidence sources specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.EVIDENCE,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def search_sessions(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search sessions specifically."""
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.SESSIONS,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        results = self.search(search_query)
        return results.results
    
    def _get_adapters_for_scope(self, scope: SearchScope) -> Dict[EntityType, BaseSearchAdapter]:
        """Get adapters to use based on search scope."""
        if scope == SearchScope.ALL:
            return self.adapters
        elif scope == SearchScope.WORK_ITEMS:
            return {EntityType.WORK_ITEM: self.adapters[EntityType.WORK_ITEM]}
        elif scope == SearchScope.TASKS:
            return {EntityType.TASK: self.adapters[EntityType.TASK]}
        elif scope == SearchScope.IDEAS:
            return {EntityType.IDEA: self.adapters[EntityType.IDEA]}
        else:
            return self.adapters
    
    def _update_metrics(self, search_results: SearchResults):
        """Update search metrics with new search results."""
        self.metrics.total_queries += 1
        
        # Update average query time
        total_time = self.metrics.avg_query_time_ms * (self.metrics.total_queries - 1)
        self.metrics.avg_query_time_ms = (total_time + search_results.search_time_ms) / self.metrics.total_queries
        
        # Update average results per query
        total_results = self.metrics.avg_results_per_query * (self.metrics.total_queries - 1)
        self.metrics.avg_results_per_query = (total_results + search_results.total_results) / self.metrics.total_queries
        
        # Update average relevance score
        if search_results.results:
            total_relevance = self.metrics.avg_relevance_score * (self.metrics.total_queries - 1)
            self.metrics.avg_relevance_score = (total_relevance + search_results.avg_relevance_score) / self.metrics.total_queries
        
        # Update high relevance ratio
        if search_results.total_results > 0:
            high_relevance_ratio = search_results.high_relevance_count / search_results.total_results
            total_ratio = self.metrics.high_relevance_ratio * (self.metrics.total_queries - 1)
            self.metrics.high_relevance_ratio = (total_ratio + high_relevance_ratio) / self.metrics.total_queries
        
        # Update zero result ratio
        zero_results = 1 if search_results.total_results == 0 else 0
        total_zero = self.metrics.zero_result_ratio * (self.metrics.total_queries - 1)
        self.metrics.zero_result_ratio = (total_zero + zero_results) / self.metrics.total_queries
        
        # Update entity type distribution
        for entity_type, count in search_results.entity_type_counts.items():
            self.metrics.entity_type_distribution[entity_type] = (
                self.metrics.entity_type_distribution.get(entity_type, 0) + count
            )
        
        # Update period end
        self.metrics.metrics_period_end = datetime.now()
    
    def get_metrics(self) -> SearchMetrics:
        """Get current search metrics."""
        return self.metrics
    
    def reset_metrics(self):
        """Reset search metrics."""
        self.metrics = SearchMetrics(
            project_id=1,  # Default project ID for metrics
            total_queries=0,
            avg_query_time_ms=0.0,
            avg_results_per_query=0.0,
            avg_relevance_score=0.0,
            high_relevance_ratio=0.0,
            zero_result_ratio=0.0,
            cache_hit_ratio=0.0,
            index_size_mb=0.0,
            memory_usage_mb=0.0,
            metrics_period_start=datetime.now(),
            metrics_period_end=datetime.now()
        )
    
    def get_index_stats(self, entity_type: Optional[EntityType] = None) -> Dict[EntityType, SearchIndex]:
        """Get index statistics for entity types."""
        if entity_type:
            stats = self.indexer.get_index_stats(entity_type)
            return {entity_type: stats} if stats else {}
        else:
            stats = {}
            for et in EntityType:
                stat = self.indexer.get_index_stats(et)
                if stat:
                    stats[et] = stat
            return stats
    
    def rebuild_index(self, entity_type: Optional[EntityType] = None) -> int:
        """Rebuild search index for entity type or all entities."""
        return self.indexer.rebuild_index(entity_type)
    
    def index_entity(self, entity_type: EntityType, entity_id: int) -> bool:
        """Index a specific entity."""
        if entity_type in self.adapters:
            return self.adapters[entity_type].index_entity(entity_id)
        return False
    
    def reindex_entity_type(self, entity_type: EntityType) -> int:
        """Reindex all entities of a specific type."""
        if entity_type in self.adapters:
            return self.adapters[entity_type].reindex_all()
        return 0
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions for a partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of search suggestions
        """
        # This would implement search suggestions based on:
        # - Common queries
        # - Entity names/titles
        # - Tags
        # - Recent searches
        
        # For now, return empty list
        return []
    
    def get_popular_searches(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get popular search queries.
        
        Args:
            limit: Maximum number of popular searches
            
        Returns:
            List of (query, count) tuples
        """
        # This would return actual popular searches from metrics
        # For now, return empty list
        return []


__all__ = ['SearchService']
