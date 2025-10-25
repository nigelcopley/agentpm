"""
Tests for search service.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from agentpm.core.search.service import SearchService
from agentpm.core.search.models import SearchQuery, SearchFilter, SearchScope, SearchMode
from agentpm.core.database.enums import EntityType


class TestSearchService:
    """Test SearchService class."""
    
    def test_search_service_initialization(self):
        """Test search service initialization."""
        mock_db_service = Mock()
        search_service = SearchService(mock_db_service)
        
        assert search_service.db_service == mock_db_service
        assert search_service.config is not None
        assert len(search_service.adapters) > 0
        assert EntityType.WORK_ITEM in search_service.adapters
        assert EntityType.TASK in search_service.adapters
        assert EntityType.IDEA in search_service.adapters
    
    def test_search_query_creation(self):
        """Test search query creation."""
        query = SearchQuery(
            query="test search",
            scope=SearchScope.WORK_ITEMS,
            limit=10
        )
        
        assert query.query == "test search"
        assert query.scope == SearchScope.WORK_ITEMS
        assert query.limit == 10
        assert query.mode == SearchMode.TEXT
    
    def test_search_filter_creation(self):
        """Test search filter creation."""
        filter_obj = SearchFilter(
            entity_types=[EntityType.WORK_ITEM, EntityType.TASK],
            project_id=1,
            min_relevance=0.5
        )
        
        assert filter_obj.entity_types == [EntityType.WORK_ITEM, EntityType.TASK]
        assert filter_obj.project_id == 1
        assert filter_obj.min_relevance == 0.5
    
    def test_search_service_get_adapters_for_scope(self):
        """Test getting adapters for different scopes."""
        mock_db_service = Mock()
        search_service = SearchService(mock_db_service)
        
        # Test ALL scope
        all_adapters = search_service._get_adapters_for_scope(SearchScope.ALL)
        assert len(all_adapters) > 0
        
        # Test specific scope
        work_item_adapters = search_service._get_adapters_for_scope(SearchScope.WORK_ITEMS)
        assert len(work_item_adapters) == 1
        assert EntityType.WORK_ITEM in work_item_adapters
    
    def test_search_service_metrics_update(self):
        """Test search metrics update."""
        mock_db_service = Mock()
        search_service = SearchService(mock_db_service)
        
        # Create mock search results
        from agentpm.core.database.models.search_result import SearchResults
        mock_results = SearchResults(
            query="test",
            total_results=5,
            results=[],
            search_time_ms=100.0,
            avg_relevance_score=0.8,
            high_relevance_count=2
        )
        
        # Update metrics
        search_service._update_metrics(mock_results)
        
        assert search_service.metrics.total_queries == 1
        assert search_service.metrics.avg_query_time_ms == 100.0
        assert search_service.metrics.avg_results_per_query == 5.0
        assert search_service.metrics.avg_relevance_score == 0.8
    
    def test_search_service_reset_metrics(self):
        """Test search metrics reset."""
        mock_db_service = Mock()
        search_service = SearchService(mock_db_service)
        
        # Update metrics first
        from agentpm.core.database.models.search_result import SearchResults
        mock_results = SearchResults(
            query="test",
            total_results=5,
            results=[],
            search_time_ms=100.0,
            avg_relevance_score=0.8,
            high_relevance_count=2
        )
        search_service._update_metrics(mock_results)
        
        # Reset metrics
        search_service.reset_metrics()
        
        assert search_service.metrics.total_queries == 0
        assert search_service.metrics.avg_query_time_ms == 0.0
        assert search_service.metrics.avg_results_per_query == 0.0
