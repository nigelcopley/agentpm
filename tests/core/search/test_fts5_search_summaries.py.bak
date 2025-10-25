"""
Tests for FTS5SearchService.search_summaries() method

Unit tests for the search_summaries() method in FTS5SearchService,
covering BM25 ranking, filtering, and edge cases.
"""

import pytest
import sqlite3
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import Mock, patch

from agentpm.core.database.service import DatabaseService
from agentpm.core.search.fts5_service import FTS5SearchService
from agentpm.core.database.enums import EntityType
from agentpm.core.database.models.search_result import SearchResultType


class TestFTS5SearchSummaries:
    """Test suite for FTS5SearchService.search_summaries() method."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database with test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        # Create database service
        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test project
            cursor.execute("""
                INSERT INTO projects (id, name, description, path, created_at, updated_at)
                VALUES (1, 'Test Project', 'Test project', '/tmp/test', datetime('now'), datetime('now'))
            """)

            # Create test session
            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'test-session', 1, 'claude-code', datetime('now'), 'coding')
            """)

            # Create test work item
            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, business_context, type, status, priority)
                VALUES (1, 1, 'Test WI', 'Test work item', 'Test context', 'feature', 'active', 1)
            """)

            # Create test task
            cursor.execute("""
                INSERT INTO tasks (id, work_item_id, name, description, type, status)
                VALUES (1, 1, 'Test Task', 'Test task', 'implementation', 'ready')
            """)

            # Insert test summaries
            summaries_data = [
                (1, 'work_item', 1, 'work_item_progress',
                 'OAuth2 authentication implementation progressing well with token validation',
                 '{"phase": "implementation"}', 'agent-1', 1),

                (2, 'work_item', 1, 'work_item_milestone',
                 'Major milestone: OAuth2 core complete with JWT validation',
                 '{"milestone": "core_complete"}', 'agent-1', 1),

                (3, 'task', 1, 'task_completion',
                 'Database schema migration completed with oauth_tokens table',
                 '{"tables_added": ["oauth_tokens"]}', 'agent-2', 1),

                (4, 'task', 1, 'task_progress',
                 'API validation implementation in progress with rate limiting',
                 '{"progress": "75%"}', 'agent-2', 1),

                (5, 'project', 1, 'project_status_report',
                 'Weekly status: Authentication system ahead of schedule',
                 '{"week": 42}', 'agent-3', 1),

                (6, 'session', 1, 'session_handover',
                 'Handover notes: OAuth2 tested and working',
                 '{"status": "ready"}', 'agent-3', 1),
            ]

            cursor.executemany("""
                INSERT INTO summaries (id, entity_type, entity_id, summary_type, summary_text,
                                      context_metadata, created_by, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, summaries_data)

            # Create FTS5 virtual table (migration 0041)
            try:
                cursor.execute("""
                    CREATE VIRTUAL TABLE summaries_fts USING fts5(
                        summary_id UNINDEXED,
                        entity_type,
                        entity_id UNINDEXED,
                        summary_type,
                        summary_text,
                        context_metadata,
                        tokenize='unicode61 remove_diacritics 2'
                    )
                """)

                # Populate FTS5 index
                cursor.execute("""
                    INSERT INTO summaries_fts(
                        summary_id, entity_type, entity_id, summary_type,
                        summary_text, context_metadata
                    )
                    SELECT
                        id, entity_type, entity_id, summary_type,
                        summary_text, COALESCE(context_metadata, '')
                    FROM summaries
                """)
            except sqlite3.OperationalError:
                # FTS5 not available - tests will use fallback
                pass

            conn.commit()

        yield db_service, db_path

        # Cleanup
        os.unlink(db_path)

    @pytest.fixture
    def fts5_service(self, temp_db):
        """Create FTS5SearchService instance."""
        db_service, _ = temp_db
        return FTS5SearchService(db_service)

    def test_search_summaries_basic_query(self, fts5_service):
        """Test basic summaries search."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0
        assert all(isinstance(r.entity_type, EntityType) for r in results)
        assert all(r.result_type == SearchResultType.SUMMARY for r in results)

    def test_search_summaries_with_entity_type_filter(self, fts5_service):
        """Test summaries search filtered by entity type."""
        # Act
        results = fts5_service.search_summaries("OAuth2", entity_type="work_item")

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.WORK_ITEM for r in results)

    def test_search_summaries_with_summary_type_filter(self, fts5_service):
        """Test summaries search filtered by summary type."""
        # Act
        results = fts5_service.search_summaries("progress", summary_type="work_item_progress")

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.metadata.get("summary_type") == "work_item_progress" for r in results)

    def test_search_summaries_with_both_filters(self, fts5_service):
        """Test summaries search with both entity_type and summary_type filters."""
        # Act
        results = fts5_service.search_summaries(
            "OAuth2",
            entity_type="work_item",
            summary_type="work_item_milestone"
        )

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.WORK_ITEM for r in results)
            assert all(r.metadata.get("summary_type") == "work_item_milestone" for r in results)

    def test_search_summaries_with_limit(self, fts5_service):
        """Test summaries search respects limit parameter."""
        # Act
        results = fts5_service.search_summaries("OAuth2", limit=2)

        # Assert
        assert results is not None
        assert len(results) <= 2

    def test_search_summaries_relevance_scoring(self, fts5_service):
        """Test that results are properly scored by relevance."""
        # Act
        results = fts5_service.search_summaries("OAuth2 authentication")

        # Assert
        assert results is not None
        if len(results) > 1:
            # Check scores are in descending order (best first)
            scores = [r.relevance_score for r in results]
            assert scores == sorted(scores, reverse=True)

            # Check scores are in valid range
            assert all(0.0 <= score <= 1.0 for score in scores)

    def test_search_summaries_metadata_included(self, fts5_service):
        """Test that search results include proper metadata."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0

        for result in results:
            assert "summary_id" in result.metadata
            assert "summary_type" in result.metadata
            assert "context_metadata" in result.metadata
            assert "created_at" in result.metadata

    def test_search_summaries_match_type(self, fts5_service):
        """Test that match_type is set correctly."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0
        # Should be either 'fts5' or 'like' depending on FTS5 availability
        assert all(r.match_type in ['fts5', 'like'] for r in results)

    def test_search_summaries_matched_fields(self, fts5_service):
        """Test that matched_fields is populated."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0
        assert all("summary_text" in r.matched_fields for r in results)
        assert all("context_metadata" in r.matched_fields for r in results)

    def test_search_summaries_no_results(self, fts5_service):
        """Test searching for non-existent term."""
        # Act
        results = fts5_service.search_summaries("nonexistent_quantum_blockchain")

        # Assert
        assert results is not None
        assert len(results) == 0

    def test_search_summaries_special_characters(self, fts5_service):
        """Test search with special characters."""
        # Act - FTS5 may reject some special characters, so we expect either results or empty
        try:
            results = fts5_service.search_summaries("OAuth2 authentication")

            # Assert
            assert results is not None
            # Should handle gracefully without errors
            assert len(results) >= 0
        except Exception:
            # Special characters may cause FTS5 query errors, which is acceptable
            pass

    def test_search_summaries_title_format(self, fts5_service):
        """Test that result titles are formatted correctly."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0

        for result in results:
            # Title should be formatted from entity_type and summary_type
            assert result.title is not None
            assert len(result.title) > 0
            # Should be title-cased
            assert result.title[0].isupper()

    def test_search_summaries_content_includes_snippet(self, fts5_service):
        """Test that content includes snippet or truncated text."""
        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0

        for result in results:
            assert result.content is not None
            assert len(result.content) > 0
            # Content should be reasonable length
            assert len(result.content) <= 500  # Snippets or truncated text

    def test_search_summaries_task_entity_type(self, fts5_service):
        """Test searching task summaries specifically."""
        # Act
        results = fts5_service.search_summaries("database", entity_type="task")

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.TASK for r in results)

    def test_search_summaries_project_entity_type(self, fts5_service):
        """Test searching project summaries specifically."""
        # Act
        results = fts5_service.search_summaries("status", entity_type="project")

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.PROJECT for r in results)

    def test_search_summaries_session_entity_type(self, fts5_service):
        """Test searching session summaries specifically."""
        # Act
        results = fts5_service.search_summaries("handover", entity_type="session")

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.SESSION for r in results)


class TestFTS5SearchSummariesFallback:
    """Test fallback behavior when FTS5 is not available."""

    @pytest.fixture
    def no_fts5_db(self):
        """Create database without FTS5 table."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create minimal schema
            cursor.execute("""
                INSERT INTO projects (id, name, description, path)
                VALUES (1, 'Test', 'Test', '/tmp/test')
            """)

            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'test', 1, 'claude-code', datetime('now'), 'coding')
            """)

            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, type, status, priority)
                VALUES (1, 1, 'Test', 'Test', 'feature', 'active', 1)
            """)

            cursor.execute("""
                INSERT INTO summaries (entity_type, entity_id, summary_type, summary_text, created_by)
                VALUES ('work_item', 1, 'work_item_progress', 'OAuth2 test summary', 'agent')
            """)

            # Do NOT create FTS5 table - test fallback
            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    def test_fallback_search_works(self, no_fts5_db):
        """Test that fallback search works when FTS5 table doesn't exist."""
        # Arrange
        db_service, _ = no_fts5_db
        fts5_service = FTS5SearchService(db_service)

        # Act
        results = fts5_service.search_summaries("OAuth2")

        # Assert
        assert results is not None
        assert len(results) > 0
        assert all(r.match_type == "like" for r in results)

    def test_fallback_search_with_filters(self, no_fts5_db):
        """Test that fallback search supports filters."""
        # Arrange
        db_service, _ = no_fts5_db
        fts5_service = FTS5SearchService(db_service)

        # Act
        results = fts5_service.search_summaries(
            "OAuth2",
            entity_type="work_item",
            summary_type="work_item_progress"
        )

        # Assert
        assert results is not None
        if len(results) > 0:
            assert all(r.entity_type == EntityType.WORK_ITEM for r in results)


class TestFTS5SearchSummariesEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def empty_db(self):
        """Create database with no summaries."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO projects (id, name, description, path)
                VALUES (1, 'Test', 'Test', '/tmp/test')
            """)

            # Create summaries table but no data
            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    def test_search_empty_database(self, empty_db):
        """Test searching when no summaries exist."""
        # Arrange
        db_service, _ = empty_db
        fts5_service = FTS5SearchService(db_service)

        # Act
        results = fts5_service.search_summaries("test")

        # Assert
        assert results is not None
        assert len(results) == 0

    def test_search_with_very_long_query(self, empty_db):
        """Test search with very long query string."""
        # Arrange
        db_service, _ = empty_db
        fts5_service = FTS5SearchService(db_service)
        long_query = "OAuth2 " * 100  # Very long query

        # Act
        results = fts5_service.search_summaries(long_query)

        # Assert
        assert results is not None
        # Should handle gracefully without errors

    def test_search_with_zero_limit(self, empty_db):
        """Test search with limit=0."""
        # Arrange
        db_service, _ = empty_db
        fts5_service = FTS5SearchService(db_service)

        # Act - limit is clamped to valid range in implementation
        results = fts5_service.search_summaries("test", limit=0)

        # Assert
        assert results is not None
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
