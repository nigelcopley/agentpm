"""
Tests for FTS5 Search Service

Comprehensive test suite for the FTS5 full-text search functionality.
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.search.fts5_service import FTS5SearchService, FTS5SearchResult, FTS5SearchResults
from agentpm.core.search.models import SearchQuery, SearchConfig, SearchScope
from agentpm.core.database.enums import EntityType
from agentpm.core.database.models.search_result import SearchResult, SearchResults, SearchResultType


class TestFTS5SearchService:
    """Test suite for FTS5SearchService."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        # Create database service (this will run migrations automatically)
        db_service = DatabaseService(db_path)
        
        # The migrations will have already created the search_index table
        # We just need to populate it with test data
        with db_service.connect() as conn:
            cursor = conn.cursor()
            
            # Create a test project first (required for foreign key constraints)
            cursor.execute("""
                INSERT INTO projects (id, name, description, path, created_at, updated_at)
                VALUES (1, 'Test Project', 'Test project for FTS5', '/tmp/test_project', datetime('now'), datetime('now'))
            """)
            
            # Insert test data
            test_data = [
                (1, 'work_item', 'OAuth2 Authentication System', 'Implement secure OAuth2 authentication for user management system with JWT tokens and refresh token rotation.', '', '{"status": "active", "type": "feature"}'),
                (2, 'task', 'Database Schema Migration', 'Create migration scripts to update database schema for new user authentication requirements.', '', '{"status": "ready", "type": "implementation"}'),
                (3, 'idea', 'API Endpoint Validation', 'Add comprehensive validation for all API endpoints including input sanitization and error handling.', '', '{"status": "idea", "source": "user"}'),
                (4, 'work_item', 'User Management Dashboard', 'Build responsive dashboard for user management with real-time updates and role-based access control.', '', '{"status": "active", "type": "feature"}'),
                (5, 'task', 'Search Performance Optimization', 'Optimize search functionality using FTS5 for better performance and relevance scoring.', '', '{"status": "done", "type": "implementation"}'),
            ]
            
            cursor.executemany("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, test_data)
            
            conn.commit()
        
        yield db_service, db_path
        
        # Cleanup
        os.unlink(db_path)
    
    @pytest.fixture
    def fts5_service(self, temp_db):
        """Create FTS5SearchService instance with test database."""
        db_service, _ = temp_db
        return FTS5SearchService(db_service)
    
    def test_fts5_availability_check(self, fts5_service):
        """Test FTS5 availability detection."""
        assert fts5_service.fts5_available is True
    
    def test_basic_search(self, fts5_service):
        """Test basic FTS5 search functionality."""
        query = SearchQuery(query="authentication", limit=10)
        results = fts5_service.search(query)
        
        assert isinstance(results, SearchResults)
        assert len(results.results) > 0
        assert results.query == "authentication"
        assert results.total_results > 0
        assert results.search_time_ms >= 0
        assert results.avg_relevance_score >= 0.0
        assert results.avg_relevance_score <= 1.0
    
    def test_search_with_entity_type_filter(self, fts5_service):
        """Test search with entity type filtering."""
        from agentpm.core.search.models import SearchFilter
        
        query = SearchQuery(
            query="authentication",
            filters=SearchFilter(entity_types=[EntityType.WORK_ITEM]),
            limit=10
        )
        results = fts5_service.search(query)
        
        assert isinstance(results, SearchResults)
        # All results should be work items
        for result in results.results:
            assert result.entity_type == EntityType.WORK_ITEM
    
    def test_search_relevance_scoring(self, fts5_service):
        """Test that search results are properly scored by relevance."""
        query = SearchQuery(query="authentication", limit=10)
        results = fts5_service.search(query)
        
        assert isinstance(results, SearchResults)
        assert len(results.results) > 0
        
        # Results should be ordered by relevance (highest first)
        relevance_scores = [r.relevance_score for r in results.results]
        assert relevance_scores == sorted(relevance_scores, reverse=True)
        
        # All relevance scores should be in valid range
        for score in relevance_scores:
            assert 0.0 <= score <= 1.0
    
    def test_search_highlighting(self, fts5_service):
        """Test search result highlighting."""
        query = SearchQuery(query="authentication", limit=5)
        results = fts5_service.search(query)
        
        assert isinstance(results, SearchResults)
        assert len(results.results) > 0
        
        # Check that results contain the search term
        for result in results.results:
            assert "authentication" in result.title.lower() or "authentication" in result.content.lower()
    
    def test_search_pagination(self, fts5_service):
        """Test search result pagination."""
        # First page
        query1 = SearchQuery(query="authentication", limit=2, offset=0)
        results1 = fts5_service.search(query1)
        
        # Second page
        query2 = SearchQuery(query="authentication", limit=2, offset=2)
        results2 = fts5_service.search(query2)
        
        assert isinstance(results1, SearchResults)
        assert isinstance(results2, SearchResults)
        assert len(results1.results) <= 2
        assert len(results2.results) <= 2
        
        # Results should be different (if there are enough total results)
        if results1.total_results > 2:
            assert results1.results != results2.results
    
    def test_search_metrics_recording(self, fts5_service, temp_db):
        """Test that search metrics are properly recorded."""
        db_service, _ = temp_db
        
        query = SearchQuery(query="test metrics", limit=5)
        results = fts5_service.search(query)
        
        # Check that metrics were recorded
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM search_metrics 
                WHERE query_text = 'test metrics'
            """)
            count = cursor.fetchone()[0]
            assert count > 0
    
    def test_fallback_search(self, temp_db):
        """Test fallback search when FTS5 is not available."""
        db_service, _ = temp_db
        
        # Mock FTS5 as unavailable
        with patch.object(FTS5SearchService, '_check_fts5_availability', return_value=False):
            service = FTS5SearchService(db_service)
            assert service.fts5_available is False
            
            query = SearchQuery(query="authentication", limit=5)
            results = service.search(query)
            
            assert isinstance(results, SearchResults)
            assert len(results.results) > 0
    
    def test_search_suggestions(self, fts5_service, temp_db):
        """Test search suggestions functionality."""
        db_service, _ = temp_db
        
        # Add some search metrics for suggestions
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_metrics (project_id, query_text, result_count, execution_time_ms, user_id)
                VALUES (1, 'authentication system', 5, 10.5, 'test_user')
            """)
            cursor.execute("""
                INSERT INTO search_metrics (project_id, query_text, result_count, execution_time_ms, user_id)
                VALUES (1, 'authentication flow', 3, 8.2, 'test_user')
            """)
            conn.commit()
        
        suggestions = fts5_service.get_search_suggestions("auth", limit=5)
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_search_metrics_retrieval(self, fts5_service, temp_db):
        """Test search metrics retrieval."""
        db_service, _ = temp_db
        
        # Add some test metrics
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_metrics (project_id, query_text, result_count, execution_time_ms, user_id)
                VALUES (1, 'test query', 5, 10.5, 'test_user')
            """)
            conn.commit()
        
        metrics = fts5_service.get_search_metrics(days=7)
        assert isinstance(metrics, dict)
        assert 'total_searches' in metrics
        assert 'avg_execution_time_ms' in metrics
        assert 'avg_result_count' in metrics
        assert 'unique_queries' in metrics
        assert metrics['total_searches'] > 0
    
    def test_cache_cleanup(self, fts5_service, temp_db):
        """Test cache cleanup functionality."""
        db_service, _ = temp_db
        
        # Add some expired cache entries
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_cache (query_hash, query_text, result_data, expires_at)
                VALUES ('test_hash', 'test query', 'test data', datetime('now', '-1 day'))
            """)
            conn.commit()
        
        # Clean up expired entries
        removed_count = fts5_service.cleanup_expired_cache()
        assert removed_count > 0
    
    def test_clear_cache(self, fts5_service, temp_db):
        """Test cache clearing functionality."""
        db_service, _ = temp_db
        
        # Add some cache entries
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_cache (query_hash, query_text, result_data, expires_at)
                VALUES ('test_hash', 'test query', 'test data', datetime('now', '+1 day'))
            """)
            conn.commit()
        
        # Clear cache
        fts5_service.clear_cache()
        
        # Verify cache is empty
        with db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM search_cache")
            count = cursor.fetchone()[0]
            assert count == 0
    
    def test_fts5_query_building(self, fts5_service):
        """Test FTS5 query building with filters."""
        from agentpm.core.search.models import SearchFilter
        
        # Test basic query
        query = SearchQuery(query="authentication")
        fts5_query = fts5_service._build_fts5_query(query)
        assert fts5_query == "authentication"
        
        # Test query with entity type filter
        query_with_filter = SearchQuery(
            query="authentication",
            filters=SearchFilter(entity_types=[EntityType.WORK_ITEM])
        )
        fts5_query_with_filter = fts5_service._build_fts5_query(query_with_filter)
        assert "entity_type:work_item" in fts5_query_with_filter
        assert "authentication" in fts5_query_with_filter
    
    def test_fts5_result_conversion(self, fts5_service):
        """Test conversion from FTS5 results to standard SearchResults."""
        # Create mock FTS5 results
        fts5_results = FTS5SearchResults(
            results=[
                FTS5SearchResult(
                    entity_id=1,
                    entity_type="work_item",
                    title="Test Work Item",
                    content="Test content",
                    relevance_score=-5.0,
                    metadata={"status": "active"}
                )
            ],
            total_count=1,
            query_time_ms=10.5,
            query_text="test query",
            filters_applied={}
        )
        
        # Convert to standard results
        standard_results = fts5_service._convert_to_search_results(fts5_results)
        
        assert isinstance(standard_results, SearchResults)
        assert len(standard_results.results) == 1
        assert standard_results.query == "test query"
        assert standard_results.total_results == 1
        assert standard_results.search_time_ms == 10.5
        
        result = standard_results.results[0]
        assert isinstance(result, SearchResult)
        assert result.entity_id == 1
        assert result.entity_type == EntityType.WORK_ITEM
        assert result.title == "Test Work Item"
        assert result.content == "Test content"
        assert 0.0 <= result.relevance_score <= 1.0


class TestFTS5Migration:
    """Test suite for FTS5 migration functionality."""
    
    def test_fts5_migration_creation(self):
        """Test that FTS5 migration can be created and applied."""
        # This test would verify the migration script works correctly
        # For now, we'll test that the migration file exists and is valid
        migration_file = "agentpm/core/database/migrations/files/migration_0040_fts5_search_system.py"
        assert os.path.exists(migration_file)
        
        # Test that the migration can be imported
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration_0040", migration_file)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        # Verify migration has required functions
        assert hasattr(migration_module, 'upgrade')
        assert hasattr(migration_module, 'downgrade')
        assert hasattr(migration_module, 'MIGRATION_ID')
        assert hasattr(migration_module, 'MIGRATION_NAME')
        
        assert migration_module.MIGRATION_ID == "0040"
        assert migration_module.MIGRATION_NAME == "fts5_search_system"


class TestFTS5Integration:
    """Integration tests for FTS5 search system."""
    
    @pytest.fixture
    def integration_db(self):
        """Create a more realistic test database for integration tests."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        # Create database service (this will run migrations automatically)
        db_service = DatabaseService(db_path)
        
        # The migrations will have already created all the necessary tables
        # We just need to populate them with test data
        with db_service.connect() as conn:
            cursor = conn.cursor()
            
            # Insert test data
            cursor.execute("INSERT INTO projects (id, name, description, path, created_at, updated_at) VALUES (1, 'Test Project', 'Integration test project', '/tmp/integration_test', datetime('now'), datetime('now'))")
            
            work_items_data = [
                (1, 1, 'OAuth2 Authentication System', 'Implement secure OAuth2 authentication for user management system with JWT tokens and refresh token rotation.', 'Improve user security and authentication experience', 'feature', 'active', 2),
                (2, 1, 'User Management Dashboard', 'Build responsive dashboard for user management with real-time updates and role-based access control.', 'Provide administrators with comprehensive user management tools', 'feature', 'active', 1),
            ]
            
            cursor.executemany("""
                INSERT INTO work_items (id, project_id, name, description, business_context, type, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, work_items_data)
            
            tasks_data = [
                (1, 1, 'Database Schema Migration', 'Create migration scripts to update database schema for new user authentication requirements.', 'implementation', 'ready'),
                (2, 1, 'API Endpoint Validation', 'Add comprehensive validation for all API endpoints including input sanitization and error handling.', 'implementation', 'active'),
                (3, 2, 'Frontend Dashboard Components', 'Build React components for user management dashboard with real-time updates.', 'implementation', 'ready'),
            ]
            
            cursor.executemany("""
                INSERT INTO tasks (id, work_item_id, name, description, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, tasks_data)
            
            ideas_data = [
                (1, 1, 'Advanced Search Features', 'Implement advanced search features like faceted search, autocomplete, and search analytics.', 'idea', 'user'),
                (2, 1, 'Real-time Notifications', 'Add real-time notification system for user activities and system events.', 'idea', 'ai_suggestion'),
            ]
            
            cursor.executemany("""
                INSERT INTO ideas (id, project_id, title, description, status, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ideas_data)
            
            # Populate search index
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT 
                    id, 'work_item', name, 
                    COALESCE(description, '') || ' ' || COALESCE(business_context, ''),
                    '', json_object('status', status, 'type', type, 'priority', priority)
                FROM work_items
            """)
            
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT 
                    id, 'task', name, COALESCE(description, ''),
                    '', json_object('status', status, 'type', type, 'work_item_id', work_item_id)
                FROM tasks
            """)
            
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT 
                    id, 'idea', title, COALESCE(description, ''),
                    COALESCE(tags, ''), json_object('status', status, 'source', COALESCE(source, ''))
                FROM ideas
            """)
            
            conn.commit()
        
        yield db_service, db_path
        
        os.unlink(db_path)
    
    def test_integration_search_across_entities(self, integration_db):
        """Test searching across multiple entity types."""
        db_service, _ = integration_db
        service = FTS5SearchService(db_service)
        
        # Search for "authentication" across all entities
        query = SearchQuery(query="authentication", limit=10)
        results = service.search(query)
        
        assert isinstance(results, SearchResults)
        assert len(results.results) > 0
        
        # Should find work items and tasks related to authentication
        entity_types = {result.entity_type for result in results.results}
        assert EntityType.WORK_ITEM in entity_types or EntityType.TASK in entity_types
    
    def test_integration_search_with_filters(self, integration_db):
        """Test search with various filters."""
        db_service, _ = integration_db
        service = FTS5SearchService(db_service)
        
        from agentpm.core.search.models import SearchFilter
        
        # Search only work items
        query = SearchQuery(
            query="user",
            filters=SearchFilter(entity_types=[EntityType.WORK_ITEM]),
            limit=10
        )
        results = service.search(query)
        
        assert isinstance(results, SearchResults)
        for result in results.results:
            assert result.entity_type == EntityType.WORK_ITEM
    
    def test_integration_search_performance(self, integration_db):
        """Test search performance with realistic data."""
        db_service, _ = integration_db
        service = FTS5SearchService(db_service)
        
        # Perform multiple searches and measure performance
        queries = [
            "authentication",
            "user management", 
            "dashboard",
            "API",
            "database"
        ]
        
        total_time = 0
        for query_text in queries:
            query = SearchQuery(query=query_text, limit=10)
            results = service.search(query)
            total_time += results.search_time_ms
        
        # Average search time should be reasonable (less than 100ms per search)
        avg_time = total_time / len(queries)
        assert avg_time < 100.0, f"Average search time {avg_time}ms is too slow"
    
    def test_integration_search_relevance(self, integration_db):
        """Test that search results are relevant and properly ranked."""
        db_service, _ = integration_db
        service = FTS5SearchService(db_service)
        
        # Search for a specific term
        query = SearchQuery(query="OAuth2", limit=5)
        results = service.search(query)
        
        assert isinstance(results, SearchResults)
        assert len(results.results) > 0
        
        # Results should contain the search term
        for result in results.results:
            content = (result.title + " " + result.content).lower()
            assert "oauth2" in content or "oauth" in content
        
        # Results should be ranked by relevance
        relevance_scores = [r.relevance_score for r in results.results]
        assert relevance_scores == sorted(relevance_scores, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
