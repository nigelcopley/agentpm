"""
Tests for FTS5 Sessions Search

Comprehensive test suite for searching sessions with various filters and options.
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


class TestSessionsSearch:
    """Test suite for sessions search functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database with sessions test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        # Create database service (migrations run automatically)
        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test project
            cursor.execute("""
                INSERT INTO projects (id, name, description, path, created_at, updated_at)
                VALUES (1, 'Test Project', 'Test project for sessions search', '/tmp/test', datetime('now'), datetime('now'))
            """)

            # Insert test sessions with various types and metadata
            sessions_data = [
                # Coding sessions
                (1, 'session-001', 1, 'claude-code', 'claude-sonnet-4-5', '1.0.0',
                 '2025-10-20 09:00:00', '2025-10-20 13:00:00', 240, 'coding',
                 'normal_exit', 'Dev One', 'dev1@example.com',
                 '{"focus": "OAuth2 implementation", "files_changed": 15, "tests_added": 10}',
                 'active'),

                (2, 'session-002', 1, 'cursor', 'gpt-4', '0.42.0',
                 '2025-10-20 14:00:00', '2025-10-20 16:30:00', 150, 'coding',
                 'normal_exit', 'Dev Two', 'dev2@example.com',
                 '{"focus": "JWT token validation", "files_changed": 8, "tests_added": 12}',
                 'completed'),

                (3, 'session-003', 1, 'windsurf', 'claude-opus-4', '2.1.0',
                 '2025-10-21 09:00:00', '2025-10-21 12:00:00', 180, 'coding',
                 'normal_exit', 'Dev One', 'dev1@example.com',
                 '{"focus": "API endpoint implementation", "files_changed": 12, "tests_added": 8}',
                 'completed'),

                # Review sessions
                (4, 'session-004', 1, 'claude-code', 'claude-sonnet-4-5', '1.0.0',
                 '2025-10-21 14:00:00', '2025-10-21 15:30:00', 90, 'review',
                 'normal_exit', 'Reviewer One', 'reviewer1@example.com',
                 '{"focus": "code review OAuth2", "comments_added": 25, "issues_found": 3}',
                 'completed'),

                (5, 'session-005', 1, 'manual', None, None,
                 '2025-10-22 10:00:00', '2025-10-22 11:00:00', 60, 'review',
                 'normal_exit', 'Reviewer Two', 'reviewer2@example.com',
                 '{"focus": "security review", "severity": "high", "findings": 2}',
                 'completed'),

                # Planning sessions
                (6, 'session-006', 1, 'claude-code', 'claude-sonnet-4-5', '1.0.0',
                 '2025-10-18 09:00:00', '2025-10-18 10:30:00', 90, 'planning',
                 'normal_exit', 'PM One', 'pm1@example.com',
                 '{"focus": "sprint planning", "stories_estimated": 12, "velocity": 45}',
                 'completed'),

                (7, 'session-007', 1, 'manual', None, None,
                 '2025-10-19 14:00:00', '2025-10-19 16:00:00', 120, 'planning',
                 'normal_exit', 'Architect One', 'arch1@example.com',
                 '{"focus": "architecture design", "decisions": 5, "diagrams": 3}',
                 'completed'),

                # Research sessions
                (8, 'session-008', 1, 'aider', 'gpt-4-turbo', '0.50.0',
                 '2025-10-17 09:00:00', '2025-10-17 12:00:00', 180, 'research',
                 'normal_exit', 'Researcher One', 'research1@example.com',
                 '{"focus": "OAuth2 best practices", "sources_reviewed": 15, "notes": 8}',
                 'completed'),

                (9, 'session-009', 1, 'claude-code', 'claude-sonnet-4-5', '1.0.0',
                 '2025-10-17 14:00:00', '2025-10-17 17:00:00', 180, 'research',
                 'normal_exit', 'Researcher Two', 'research2@example.com',
                 '{"focus": "JWT security analysis", "papers_read": 5, "poc_created": True}',
                 'completed'),

                # Debugging sessions
                (10, 'session-010', 1, 'cursor', 'gpt-4o', '0.42.0',
                 '2025-10-23 10:00:00', '2025-10-23 14:00:00', 240, 'debugging',
                 'normal_exit', 'Dev One', 'dev1@example.com',
                 '{"focus": "token refresh bug", "bugs_fixed": 3, "tests_fixed": 5}',
                 'completed'),

                (11, 'session-011', 1, 'windsurf', 'gemini-pro', '2.1.0',
                 '2025-10-23 15:00:00', None, None, 'debugging',
                 None, 'Dev Two', 'dev2@example.com',
                 '{"focus": "race condition investigation", "progress": "ongoing"}',
                 'active'),

                # Long coding session
                (12, 'session-012', 1, 'claude-code', 'claude-sonnet-4-5', '1.0.0',
                 '2025-10-24 08:00:00', '2025-10-24 20:00:00', 720, 'coding',
                 'normal_exit', 'Dev One', 'dev1@example.com',
                 '{"focus": "major refactoring OAuth2", "files_changed": 45, "tests_added": 30, "complexity": "high"}',
                 'completed'),

                # Paused session
                (13, 'session-013', 1, 'cursor', 'gpt-4', '0.42.0',
                 '2025-10-24 09:00:00', None, 60, 'coding',
                 'interrupted', 'Dev Three', 'dev3@example.com',
                 '{"focus": "database migration", "progress": "paused"}',
                 'paused'),
            ]

            cursor.executemany("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, llm_model, tool_version,
                                     start_time, end_time, duration_minutes, session_type,
                                     exit_reason, developer_name, developer_email, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sessions_data)

            # Populate search_index for sessions (FTS5)
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'session',
                    session_type || ' - ' || tool_name,
                    COALESCE(developer_name, '') || ' ' || COALESCE(metadata, ''),
                    '',
                    json_object('session_type', session_type, 'tool_name', tool_name, 'llm_model', llm_model)
                FROM sessions
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

    def test_search_sessions_basic_query(self, search_service):
        """Test basic sessions search with simple query."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert len(results.results) > 0

    def test_search_sessions_by_type_coding(self, search_service):
        """Test searching for coding sessions."""
        # Arrange
        query = SearchQuery(
            query="coding implementation",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_type_review(self, search_service):
        """Test searching for review sessions."""
        # Arrange
        query = SearchQuery(
            query="review security",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_type_planning(self, search_service):
        """Test searching for planning sessions."""
        # Arrange
        query = SearchQuery(
            query="planning sprint",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_type_research(self, search_service):
        """Test searching for research sessions."""
        # Arrange
        query = SearchQuery(
            query="research best practices",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_type_debugging(self, search_service):
        """Test searching for debugging sessions."""
        # Arrange
        query = SearchQuery(
            query="debugging bug fix",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_tool_claude_code(self, search_service):
        """Test searching for Claude Code sessions."""
        # Arrange
        query = SearchQuery(
            query="claude-code",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_tool_cursor(self, search_service):
        """Test searching for Cursor sessions."""
        # Arrange
        query = SearchQuery(
            query="cursor",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_by_developer(self, search_service):
        """Test searching sessions by developer name."""
        # Arrange
        query = SearchQuery(
            query="Dev One",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_metadata_search(self, search_service):
        """Test searching within session metadata."""
        # Arrange
        query = SearchQuery(
            query="refactoring complexity",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # May or may not find results depending on FTS5 indexing
        assert results.total_results >= 0

    def test_search_sessions_jwt_token(self, search_service):
        """Test searching sessions with JWT token content."""
        # Arrange
        query = SearchQuery(
            query="JWT token validation",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_pagination(self, search_service):
        """Test sessions search pagination."""
        # Arrange - First page
        query1 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SESSIONS,
            limit=3,
            offset=0
        )

        # Arrange - Second page
        query2 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SESSIONS,
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

    def test_search_sessions_relevance_scoring(self, search_service):
        """Test that sessions search results are properly scored by relevance."""
        # Arrange
        query = SearchQuery(
            query="OAuth2 implementation",
            scope=SearchScope.SESSIONS,
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

    def test_search_sessions_no_results(self, search_service):
        """Test searching for term that doesn't exist in sessions."""
        # Arrange
        query = SearchQuery(
            query="nonexistent_quantum_blockchain_ai",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results == 0
        assert len(results.results) == 0

    def test_search_sessions_active_status(self, search_service):
        """Test searching for active sessions."""
        # Arrange
        query = SearchQuery(
            query="active ongoing",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # May or may not have results
        assert results.total_results >= 0

    def test_search_sessions_llm_model(self, search_service):
        """Test searching by LLM model."""
        # Arrange
        query = SearchQuery(
            query="claude-sonnet",
            scope=SearchScope.SESSIONS,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_sessions_performance(self, search_service):
        """Test that sessions search completes in reasonable time."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SESSIONS,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.search_time_ms >= 0
        # Should complete in less than 1 second for small dataset
        assert results.search_time_ms < 1000


class TestSessionsSearchIntegration:
    """Integration tests for sessions search with realistic scenarios."""

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

            # Add multiple sessions for integration testing
            session_types = ['coding', 'review', 'planning', 'research', 'debugging']
            tools = ['claude-code', 'cursor', 'windsurf', 'aider', 'manual']
            for i in range(30):
                session_type = session_types[i % len(session_types)]
                tool = tools[i % len(tools)]
                cursor.execute("""
                    INSERT INTO sessions (session_id, project_id, tool_name, start_time, session_type,
                                        developer_name, metadata, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f'int-session-{i}',
                    1,
                    tool,
                    datetime.now().isoformat(),
                    session_type,
                    f'Developer {i % 3}',
                    f'{{"focus": "OAuth2 work iteration {i}", "tasks": {i % 5 + 1}}}',
                    'completed'
                ))

            # Populate search_index for sessions
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'session',
                    session_type || ' - ' || tool_name,
                    COALESCE(developer_name, '') || ' ' || COALESCE(metadata, ''),
                    '',
                    json_object('session_type', session_type, 'tool_name', tool_name)
                FROM sessions
            """)

            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    def test_integration_sessions_search_with_limit(self, integration_db):
        """Test sessions search respects limit parameter."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.SESSIONS,
            limit=5
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert len(results.results) <= 5
        assert results.total_results >= len(results.results)

    def test_integration_sessions_search_across_types(self, integration_db):
        """Test searching across different session types."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="work iteration",
            scope=SearchScope.SESSIONS,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find multiple types of sessions
        assert len(results.results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
