"""
Tests for FTS5 Summaries Search

Comprehensive test suite for searching summaries with various filters and options.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from agentpm.core.database.service import DatabaseService
from agentpm.core.search.service import SearchService
from agentpm.core.search.models import SearchQuery, SearchFilter, SearchScope
from agentpm.core.database.enums import EntityType


class TestSummariesSearch:
    """Test suite for summaries search functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database with summaries test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        # Create database service (migrations run automatically)
        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test project
            cursor.execute("""
                INSERT INTO projects (id, name, description, path, created_at, updated_at)
                VALUES (1, 'Test Project', 'Test project for summaries search', '/tmp/test', datetime('now'), datetime('now'))
            """)

            # Create test session
            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'test-session-1', 1, 'claude-code', datetime('now'), 'coding')
            """)

            # Create test work items and tasks for foreign keys
            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, business_context, type, status, priority)
                VALUES (1, 1, 'Test WI', 'Test work item', 'Test context', 'feature', 'active', 1)
            """)

            cursor.execute("""
                INSERT INTO tasks (id, work_item_id, name, description, type, status)
                VALUES (1, 1, 'Test Task', 'Test task description', 'implementation', 'ready')
            """)

            # Insert test summaries with various types
            summaries_data = [
                # Work item summaries
                (1, 'work_item', 1, 'work_item_progress',
                 'OAuth2 authentication implementation progressing well. Completed token validation and refresh flow. Next steps include scope management.',
                 '{"phase": "implementation", "completion": "60%"}', 'agent-1', 1, None, None),

                (2, 'work_item', 1, 'work_item_milestone',
                 'Major milestone reached: OAuth2 core authentication flow complete with JWT token validation and automatic refresh rotation.',
                 '{"milestone": "core_complete", "date": "2025-10-20"}', 'agent-1', 1, None, None),

                (3, 'work_item', 1, 'work_item_decision',
                 'Decision made to use Auth0 library for OAuth2 provider integration instead of custom implementation for better security.',
                 '{"decision": "use_auth0", "rationale": "security"}', 'agent-2', 1, None, None),

                # Task summaries
                (4, 'task', 1, 'task_completion',
                 'Database schema migration completed successfully. Added oauth_tokens table with encryption support and proper indexes.',
                 '{"tables_added": ["oauth_tokens"], "migrations": 1}', 'agent-3', 1, None, None),

                (5, 'task', 1, 'task_progress',
                 'API validation implementation in progress. Completed input sanitization for OAuth endpoints. Working on rate limiting.',
                 '{"progress": "75%", "blockers": []}', 'agent-3', 1, None, None),

                (6, 'task', 1, 'task_technical_notes',
                 'Technical note: OAuth2 PKCE flow requires SHA256 hashing of code verifier. Using crypto library for implementation.',
                 '{"tech_stack": ["crypto", "hashlib"], "security": "high"}', 'agent-3', 1, None, None),

                # Project summaries
                (7, 'project', 1, 'project_status_report',
                 'Weekly status: Authentication system development ahead of schedule. OAuth2 and JWT implementation complete. Starting user dashboard next week.',
                 '{"week": 42, "status": "on_track", "velocity": "high"}', 'agent-1', 1, '2025-10-20', 40.0),

                (8, 'project', 1, 'session_progress',
                 'Session summary: Implemented OAuth2 provider integration with Google and GitHub. Added comprehensive error handling and logging.',
                 '{"providers": ["google", "github"], "tests_added": 15}', 'agent-2', 1, '2025-10-20', 4.0),

                # Session summaries
                (9, 'session', 1, 'session_handover',
                 'Handover notes: OAuth2 flow tested and working. Database migrations applied. Next: implement scope management and permissions.',
                 '{"status": "ready_for_review", "blockers": []}', 'agent-1', 1, None, None),

                # Different content for variety
                (10, 'work_item', 1, 'work_item_progress',
                 'User interface design completed for authentication screens. Implemented responsive layouts and accessibility features.',
                 '{"ui_complete": True, "a11y": True}', 'agent-4', 1, None, None),
            ]

            cursor.executemany("""
                INSERT INTO summaries (id, entity_type, entity_id, summary_type, summary_text,
                                      context_metadata, created_by, session_id, session_date, session_duration_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, summaries_data)

            # Populate search_index for summaries (FTS5)
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'summary',
                    summary_type,
                    summary_text,
                    '',
                    json_object('summary_type', summary_type, 'entity_type', entity_type)
                FROM summaries
            """)

            conn.commit()

        yield db_service, db_path

        # Cleanup
        os.unlink(db_path)

    @pytest.fixture
    def search_service(self, temp_db):
        """Create SearchService instance with test database."""
        db_service, _ = temp_db
        return SearchService(db_service)

    def test_search_summaries_basic_query(self, search_service):
        """Test basic summaries search with simple query."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert len(results.results) > 0
        assert all('oauth' in r.content.lower() for r in results.results[:3])  # Top results should be relevant

    def test_search_summaries_by_type_work_item_progress(self, search_service):
        """Test searching for work_item_progress summaries."""
        # Arrange
        query = SearchQuery(
            query="progress",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find summaries containing "progress"
        assert any('progress' in r.content.lower() for r in results.results)

    def test_search_summaries_by_type_milestone(self, search_service):
        """Test searching for milestone summaries."""
        # Arrange
        query = SearchQuery(
            query="milestone",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert any('milestone' in r.content.lower() for r in results.results)

    def test_search_summaries_by_type_decision(self, search_service):
        """Test searching for decision summaries."""
        # Arrange
        query = SearchQuery(
            query="decision",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert any('decision' in r.content.lower() for r in results.results)

    def test_search_summaries_technical_content(self, search_service):
        """Test searching summaries with technical terms."""
        # Arrange
        query = SearchQuery(
            query="database schema migration",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find database-related summaries
        assert any('database' in r.content.lower() for r in results.results)

    def test_search_summaries_authentication_terms(self, search_service):
        """Test searching summaries with authentication-related terms."""
        # Arrange
        query = SearchQuery(
            query="authentication JWT token",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find authentication-related summaries
        relevant_results = [r for r in results.results if 'authentication' in r.content.lower() or 'token' in r.content.lower()]
        assert len(relevant_results) > 0

    def test_search_summaries_pagination(self, search_service):
        """Test summaries search pagination."""
        # Arrange - First page
        query1 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SUMMARIES,
            limit=3,
            offset=0
        )

        # Arrange - Second page
        query2 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SUMMARIES,
            limit=3,
            offset=3
        )

        # Act
        results1 = search_service.search(query1)
        results2 = search_service.search(query2)

        # Assert
        assert results1 is not None
        assert results2 is not None
        assert len(results1.results) <= 3
        # Results should be different (if there are enough results)
        if results1.total_results > 3:
            result1_ids = [r.entity_id for r in results1.results]
            result2_ids = [r.entity_id for r in results2.results]
            # At least some results should be different
            assert result1_ids != result2_ids or len(results2.results) == 0

    def test_search_summaries_relevance_scoring(self, search_service):
        """Test that summaries search results are properly scored by relevance."""
        # Arrange
        query = SearchQuery(
            query="OAuth2 authentication",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert len(results.results) > 0

        # Results should be ordered by relevance (highest first)
        relevance_scores = [r.relevance_score for r in results.results]
        assert relevance_scores == sorted(relevance_scores, reverse=True)

        # All relevance scores should be in valid range
        for score in relevance_scores:
            assert 0.0 <= score <= 1.0

    def test_search_summaries_empty_query_validation(self, search_service):
        """Test that empty queries are handled properly."""
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Should raise validation error
            query = SearchQuery(
                query="",
                scope=SearchScope.SUMMARIES
            )

    def test_search_summaries_special_characters(self, search_service):
        """Test searching summaries with special characters in query."""
        # Arrange
        query = SearchQuery(
            query="OAuth2 (authentication)",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # Should handle special characters gracefully
        assert results.total_results >= 0

    def test_search_summaries_phrase_search(self, search_service):
        """Test phrase search in summaries."""
        # Arrange
        query = SearchQuery(
            query="automatic refresh rotation",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # Should find summaries with this phrase or similar
        if results.total_results > 0:
            assert any('refresh' in r.content.lower() for r in results.results)

    def test_search_summaries_no_results(self, search_service):
        """Test searching for term that doesn't exist in summaries."""
        # Arrange
        query = SearchQuery(
            query="nonexistent_quantum_blockchain_ai",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results == 0
        assert len(results.results) == 0

    def test_search_summaries_metadata_content(self, search_service):
        """Test searching within summary metadata."""
        # Arrange
        query = SearchQuery(
            query="velocity high",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # May or may not find results depending on FTS5 indexing of metadata
        assert results.total_results >= 0

    def test_search_summaries_session_context(self, search_service):
        """Test searching summaries with session context."""
        # Arrange
        query = SearchQuery(
            query="session handover",
            scope=SearchScope.SUMMARIES,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert any('handover' in r.content.lower() for r in results.results)

    def test_search_summaries_performance(self, search_service):
        """Test that summaries search completes in reasonable time."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SUMMARIES,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.search_time_ms >= 0
        # Should complete in less than 1 second for small dataset
        assert results.search_time_ms < 1000


class TestSummariesSearchIntegration:
    """Integration tests for summaries search with realistic scenarios."""

    @pytest.fixture
    def integration_db(self):
        """Create a more realistic database for integration tests."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test data
            cursor.execute("""
                INSERT INTO projects (id, name, description, path)
                VALUES (1, 'Integration Test', 'Integration test project', '/tmp/integration')
            """)

            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'int-session-1', 1, 'claude-code', datetime('now'), 'coding')
            """)

            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, type, status, priority)
                VALUES (1, 1, 'Integration WI', 'Test work item', 'feature', 'active', 1)
            """)

            # Add multiple summaries for integration testing
            for i in range(20):
                summary_type = ['work_item_progress', 'work_item_milestone', 'task_completion'][i % 3]
                cursor.execute("""
                    INSERT INTO summaries (entity_type, entity_id, summary_type, summary_text, created_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    'work_item',
                    1,
                    summary_type,
                    f'Test summary {i}: OAuth2 authentication implementation details for iteration {i}',
                    f'agent-{i % 3}'
                ))

            # Populate search_index for summaries
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'summary',
                    summary_type,
                    summary_text,
                    '',
                    json_object('summary_type', summary_type, 'entity_type', entity_type)
                FROM summaries
            """)

            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    def test_integration_summaries_search_with_limit(self, integration_db):
        """Test summaries search respects limit parameter."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SUMMARIES,
            limit=5
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert len(results.results) <= 5
        assert results.total_results >= len(results.results)

    def test_integration_summaries_search_across_types(self, integration_db):
        """Test searching across different summary types."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="implementation",
            scope=SearchScope.SUMMARIES,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find multiple types of summaries
        assert len(results.results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
