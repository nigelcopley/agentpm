"""
Tests for search models.
"""

import pytest
from datetime import datetime
from typing import List

from agentpm.core.search.models import (
    SearchMode, SearchScope, SearchFilter, SearchQuery, SearchConfig
)
from agentpm.core.database.models import SearchIndex, SearchMetrics
from agentpm.core.database.enums import EntityType, WorkItemStatus, TaskStatus, IdeaStatus


class TestSearchMode:
    """Test SearchMode enum."""
    
    def test_search_mode_values(self):
        """Test search mode enum values."""
        assert SearchMode.TEXT == "text"
        assert SearchMode.SEMANTIC == "semantic"
        assert SearchMode.HYBRID == "hybrid"
        assert SearchMode.METADATA == "metadata"


class TestSearchScope:
    """Test SearchScope enum."""
    
    def test_search_scope_values(self):
        """Test search scope enum values."""
        assert SearchScope.ALL == "all"
        assert SearchScope.WORK_ITEMS == "work_items"
        assert SearchScope.TASKS == "tasks"
        assert SearchScope.IDEAS == "ideas"
        assert SearchScope.DOCUMENTS == "documents"
        assert SearchScope.SUMMARIES == "summaries"
        assert SearchScope.EVIDENCE == "evidence"
        assert SearchScope.LEARNINGS == "learnings"
        assert SearchScope.SESSIONS == "sessions"


class TestSearchFilter:
    """Test SearchFilter model."""
    
    def test_empty_filter(self):
        """Test creating empty search filter."""
        filter_obj = SearchFilter()
        assert filter_obj.entity_types is None
        assert filter_obj.entity_ids is None
        assert filter_obj.project_id is None
        assert filter_obj.min_relevance == 0.0
        assert filter_obj.include_archived is False
    
    def test_filter_with_entity_types(self):
        """Test filter with entity types."""
        filter_obj = SearchFilter(
            entity_types=[EntityType.WORK_ITEM, EntityType.TASK]
        )
        assert filter_obj.entity_types == [EntityType.WORK_ITEM, EntityType.TASK]
    
    def test_filter_with_statuses(self):
        """Test filter with statuses."""
        filter_obj = SearchFilter(
            work_item_statuses=[WorkItemStatus.ACTIVE, WorkItemStatus.DONE],
            task_statuses=[TaskStatus.IN_PROGRESS],
            idea_statuses=[IdeaStatus.RESEARCH]
        )
        assert filter_obj.work_item_statuses == [WorkItemStatus.ACTIVE, WorkItemStatus.DONE]
        assert filter_obj.task_statuses == [TaskStatus.IN_PROGRESS]
        assert filter_obj.idea_statuses == [IdeaStatus.RESEARCH]
    
    def test_filter_with_dates(self):
        """Test filter with date ranges."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        filter_obj = SearchFilter(
            created_after=start_date,
            created_before=end_date,
            updated_after=start_date,
            updated_before=end_date
        )
        assert filter_obj.created_after == start_date
        assert filter_obj.created_before == end_date
        assert filter_obj.updated_after == start_date
        assert filter_obj.updated_before == end_date
    
    def test_filter_validation_empty_entity_types(self):
        """Test validation of empty entity types list."""
        with pytest.raises(ValueError, match="entity_types cannot be empty list"):
            SearchFilter(entity_types=[])


class TestSearchQuery:
    """Test SearchQuery model."""
    
    def test_basic_query(self):
        """Test creating basic search query."""
        query = SearchQuery(query="test search")
        assert query.query == "test search"
        assert query.mode == SearchMode.TEXT
        assert query.scope == SearchScope.ALL
        assert query.limit == 20
        assert query.offset == 0
        assert query.case_sensitive is False
        assert query.exact_match is False
        assert query.include_content is False
        assert query.highlight is True
    
    def test_query_with_filters(self):
        """Test query with filters."""
        filters = SearchFilter(project_id=1, min_relevance=0.5)
        query = SearchQuery(
            query="test",
            filters=filters,
            limit=50,
            offset=10
        )
        assert query.filters == filters
        assert query.limit == 50
        assert query.offset == 10
    
    def test_query_validation_empty(self):
        """Test validation of empty query."""
        with pytest.raises(ValueError, match="Query cannot be empty or whitespace only"):
            SearchQuery(query="")
        
        with pytest.raises(ValueError, match="Query cannot be empty or whitespace only"):
            SearchQuery(query="   ")
    
    def test_query_validation_whitespace_trimming(self):
        """Test that query whitespace is trimmed."""
        query = SearchQuery(query="  test search  ")
        assert query.query == "test search"
    
    def test_query_boost_fields_validation(self):
        """Test boost fields validation."""
        # Valid boost fields
        query = SearchQuery(
            query="test",
            boost_fields={"title": 2.0, "description": 1.5}
        )
        assert query.boost_fields == {"title": 2.0, "description": 1.5}
        
        # Invalid boost field weight
        with pytest.raises(ValueError, match="Boost weight for 'title' must be between 0 and 10"):
            SearchQuery(
                query="test",
                boost_fields={"title": -1.0}
            )
        
        with pytest.raises(ValueError, match="Boost weight for 'title' must be between 0 and 10"):
            SearchQuery(
                query="test",
                boost_fields={"title": 11.0}
            )


class TestSearchConfig:
    """Test SearchConfig model."""
    
    def test_default_config(self):
        """Test default search configuration."""
        config = SearchConfig()
        assert config.max_results == 1000
        assert config.timeout_ms == 5000
        assert config.cache_enabled is True
        assert config.cache_ttl_seconds == 300
        assert config.default_min_relevance == 0.1
        assert config.fuzzy_threshold == 0.8
        assert config.semantic_threshold == 0.7
        assert config.auto_index is True
        assert config.index_batch_size == 100
        assert config.index_refresh_interval == 60
        assert config.enable_semantic_search is False
        assert config.enable_highlighting is True
        assert config.enable_suggestions is True
        assert config.enable_analytics is True
    
    def test_custom_config(self):
        """Test custom search configuration."""
        config = SearchConfig(
            max_results=500,
            timeout_ms=3000,
            cache_enabled=False,
            default_min_relevance=0.3,
            enable_semantic_search=True
        )
        assert config.max_results == 500
        assert config.timeout_ms == 3000
        assert config.cache_enabled is False
        assert config.default_min_relevance == 0.3
        assert config.enable_semantic_search is True


class TestSearchIndex:
    """Test SearchIndex model."""
    
    def test_search_index(self):
        """Test search index model."""
        now = datetime.now()
        index = SearchIndex(
            entity_type=EntityType.WORK_ITEM,
            index_version="1.0.0",
            total_documents=100,
            last_updated=now,
            index_size_bytes=1024000,
            avg_document_size=1024.0,
            unique_terms=500,
            total_terms=10000,
            build_time_ms=1500.0,
            query_time_ms=50.0
        )
        
        assert index.entity_type == EntityType.WORK_ITEM
        assert index.index_version == "1.0.0"
        assert index.total_documents == 100
        assert index.last_updated == now
        assert index.index_size_bytes == 1024000
        assert index.avg_document_size == 1024.0
        assert index.unique_terms == 500
        assert index.total_terms == 10000
        assert index.build_time_ms == 1500.0
        assert index.query_time_ms == 50.0


class TestSearchMetrics:
    """Test SearchMetrics model."""
    
    def test_search_metrics(self):
        """Test search metrics model."""
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 31)
        
        metrics = SearchMetrics(
            total_queries=1000,
            avg_query_time_ms=150.0,
            avg_results_per_query=25.5,
            avg_relevance_score=0.75,
            high_relevance_ratio=0.3,
            zero_result_ratio=0.1,
            cache_hit_ratio=0.8,
            index_size_mb=50.0,
            memory_usage_mb=100.0,
            most_common_queries=[("test", 50), ("search", 30)],
            entity_type_distribution={"work_item": 500, "task": 300},
            search_mode_distribution={"text": 800, "semantic": 200},
            metrics_period_start=start_time,
            metrics_period_end=end_time
        )
        
        assert metrics.total_queries == 1000
        assert metrics.avg_query_time_ms == 150.0
        assert metrics.avg_results_per_query == 25.5
        assert metrics.avg_relevance_score == 0.75
        assert metrics.high_relevance_ratio == 0.3
        assert metrics.zero_result_ratio == 0.1
        assert metrics.cache_hit_ratio == 0.8
        assert metrics.index_size_mb == 50.0
        assert metrics.memory_usage_mb == 100.0
        assert metrics.most_common_queries == [("test", 50), ("search", 30)]
        assert metrics.entity_type_distribution == {"work_item": 500, "task": 300}
        assert metrics.search_mode_distribution == {"text": 800, "semantic": 200}
        assert metrics.metrics_period_start == start_time
        assert metrics.metrics_period_end == end_time
