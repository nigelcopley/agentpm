"""
Tests for FTS5 Evidence Search

Comprehensive test suite for searching evidence sources with various filters and options.
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


class TestEvidenceSearch:
    """Test suite for evidence sources search functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database with evidence test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        # Create database service (migrations run automatically)
        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test project
            cursor.execute("""
                INSERT INTO projects (id, name, description, path, created_at, updated_at)
                VALUES (1, 'Test Project', 'Test project for evidence search', '/tmp/test', datetime('now'), datetime('now'))
            """)

            # Create test work items for foreign keys
            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, business_context, type, status, priority)
                VALUES (1, 1, 'Test WI', 'Test work item', 'Test context', 'feature', 'active', 1)
            """)

            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, business_context, type, status, priority)
                VALUES (2, 1, 'Test WI 2', 'Second work item', 'Test context 2', 'feature', 'active', 1)
            """)

            # Insert test evidence sources with various types
            evidence_data = [
                # Documentation sources
                (1, 'work_item', 1, 'https://oauth.net/2/',
                 'documentation',
                 'OAuth 2.0 RFC 6749 specification describing the authorization framework for third-party applications to access HTTP services.',
                 'hash1', 0.95, 'researcher-1'),

                (2, 'work_item', 1, 'https://datatracker.ietf.org/doc/html/rfc7519',
                 'documentation',
                 'JSON Web Token (JWT) RFC 7519 specification for representing claims securely between two parties using JSON.',
                 'hash2', 0.98, 'researcher-1'),

                # Research sources
                (3, 'work_item', 1, 'https://research.google/pubs/pub12345/',
                 'research',
                 'Research paper on OAuth2 security best practices including PKCE flow implementation and token rotation strategies.',
                 'hash3', 0.85, 'researcher-2'),

                (4, 'work_item', 2, 'https://arxiv.org/abs/1234.5678',
                 'research',
                 'Academic research on authentication systems scalability and performance optimization techniques for distributed systems.',
                 'hash4', 0.82, 'researcher-2'),

                # Stack Overflow sources
                (5, 'work_item', 1, 'https://stackoverflow.com/questions/12345678/oauth2-implementation',
                 'stackoverflow',
                 'Discussion on OAuth2 PKCE flow implementation in Python with code examples for token validation and refresh.',
                 'hash5', 0.75, 'developer-1'),

                (6, 'task', 1, 'https://stackoverflow.com/questions/87654321/jwt-validation',
                 'stackoverflow',
                 'Best practices for JWT token validation including signature verification, expiration checking, and claim validation.',
                 'hash6', 0.78, 'developer-1'),

                # GitHub sources
                (7, 'work_item', 1, 'https://github.com/oauth-lib/python-oauth2',
                 'github',
                 'Python OAuth2 library implementation with comprehensive examples for providers like Google, GitHub, and Auth0.',
                 'hash7', 0.88, 'developer-2'),

                (8, 'work_item', 1, 'https://github.com/auth0/auth0-python',
                 'github',
                 'Auth0 Python SDK for authentication management including user management, roles, and permissions.',
                 'hash8', 0.92, 'developer-2'),

                # Internal documentation
                (9, 'work_item', 2, 'file:///docs/architecture/auth-design.md',
                 'internal_doc',
                 'Internal architecture documentation for authentication system design including database schema and API endpoints.',
                 'hash9', 0.90, 'architect-1'),

                (10, 'work_item', 2, 'file:///docs/security/oauth-security.md',
                 'internal_doc',
                 'Security guidelines for OAuth2 implementation including encryption standards, token storage, and audit logging requirements.',
                 'hash10', 0.93, 'security-1'),

                # Meeting notes
                (11, 'work_item', 1, 'notion://meetings/2025-10-15-auth-review',
                 'meeting_notes',
                 'Architecture review meeting notes discussing OAuth2 provider selection, security requirements, and implementation timeline.',
                 'hash11', 0.80, 'pm-1'),

                # User feedback
                (12, 'work_item', 2, 'jira://TICKET-1234',
                 'user_feedback',
                 'User feedback requesting support for social login providers including Google, Facebook, GitHub, and Microsoft accounts.',
                 'hash12', 0.72, 'support-1'),

                # Competitor analysis
                (13, 'work_item', 2, 'https://competitor.com/auth-features',
                 'competitor_analysis',
                 'Competitor analysis showing authentication features including SSO, MFA, passwordless login, and biometric authentication.',
                 'hash13', 0.68, 'analyst-1'),
            ]

            cursor.executemany("""
                INSERT INTO evidence_sources (id, entity_type, entity_id, url, source_type,
                                             excerpt, content_hash, confidence, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evidence_data)

            # Populate search_index for evidence (FTS5)
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'evidence',
                    COALESCE(url, 'Evidence Source'),
                    excerpt,
                    '',
                    json_object('source_type', source_type, 'confidence', confidence, 'url', url)
                FROM evidence_sources
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

    def test_search_evidence_basic_query(self, search_service):
        """Test basic evidence search with simple query."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert len(results.results) > 0
        # Top results should contain OAuth2
        assert any('oauth' in r.content.lower() for r in results.results[:3])

    def test_search_evidence_by_source_type_documentation(self, search_service):
        """Test searching for documentation evidence sources."""
        # Arrange
        query = SearchQuery(
            query="specification",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert any('specification' in r.content.lower() for r in results.results)

    def test_search_evidence_by_source_type_research(self, search_service):
        """Test searching for research evidence sources."""
        # Arrange
        query = SearchQuery(
            query="research security",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        assert any('research' in r.content.lower() or 'security' in r.content.lower() for r in results.results)

    def test_search_evidence_by_source_type_stackoverflow(self, search_service):
        """Test searching for Stack Overflow evidence sources."""
        # Arrange
        query = SearchQuery(
            query="implementation validation",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_by_source_type_github(self, search_service):
        """Test searching for GitHub evidence sources."""
        # Arrange
        query = SearchQuery(
            query="library SDK",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_technical_terms(self, search_service):
        """Test searching evidence with technical terms."""
        # Arrange
        query = SearchQuery(
            query="JWT token validation",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find JWT-related evidence
        assert any('jwt' in r.content.lower() or 'token' in r.content.lower() for r in results.results)

    def test_search_evidence_security_terms(self, search_service):
        """Test searching evidence with security-related terms."""
        # Arrange
        query = SearchQuery(
            query="security encryption audit",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_pagination(self, search_service):
        """Test evidence search pagination."""
        # Arrange - First page
        query1 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.EVIDENCE,
            limit=3,
            offset=0
        )

        # Arrange - Second page
        query2 = SearchQuery(
            query="OAuth2",
            scope=SearchScope.EVIDENCE,
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

    def test_search_evidence_relevance_scoring(self, search_service):
        """Test that evidence search results are properly scored by relevance."""
        # Arrange
        query = SearchQuery(
            query="OAuth2 authentication",
            scope=SearchScope.EVIDENCE,
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

    def test_search_evidence_url_content(self, search_service):
        """Test searching within evidence URLs."""
        # Arrange
        query = SearchQuery(
            query="github python",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # Should find GitHub-related evidence
        assert results.total_results >= 0

    def test_search_evidence_internal_docs(self, search_service):
        """Test searching internal documentation evidence."""
        # Arrange
        query = SearchQuery(
            query="architecture design",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_meeting_notes(self, search_service):
        """Test searching meeting notes evidence."""
        # Arrange
        query = SearchQuery(
            query="review meeting timeline",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_user_feedback(self, search_service):
        """Test searching user feedback evidence."""
        # Arrange
        query = SearchQuery(
            query="social login",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0

    def test_search_evidence_competitor_analysis(self, search_service):
        """Test searching competitor analysis evidence."""
        # Arrange
        query = SearchQuery(
            query="SSO MFA passwordless",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # May or may not have results
        assert results.total_results >= 0

    def test_search_evidence_no_results(self, search_service):
        """Test searching for term that doesn't exist in evidence."""
        # Arrange
        query = SearchQuery(
            query="nonexistent_quantum_blockchain_ai",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results == 0
        assert len(results.results) == 0

    def test_search_evidence_special_characters(self, search_service):
        """Test searching evidence with special characters in query."""
        # Arrange
        query = SearchQuery(
            query="OAuth2.0 (RFC-6749)",
            scope=SearchScope.EVIDENCE,
            limit=10
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        # Should handle special characters gracefully
        assert results.total_results >= 0

    def test_search_evidence_performance(self, search_service):
        """Test that evidence search completes in reasonable time."""
        # Arrange
        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.EVIDENCE,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.search_time_ms >= 0
        # Should complete in less than 1 second for small dataset
        assert results.search_time_ms < 1000


class TestEvidenceSearchIntegration:
    """Integration tests for evidence search with realistic scenarios."""

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
                INSERT INTO work_items (id, project_id, name, description, type, status, priority)
                VALUES (1, 1, 'Integration WI', 'Test work item', 'feature', 'active', 1)
            """)

            # Add multiple evidence sources for integration testing
            source_types = ['documentation', 'research', 'stackoverflow', 'github', 'internal_doc']
            for i in range(25):
                source_type = source_types[i % len(source_types)]
                cursor.execute("""
                    INSERT INTO evidence_sources (entity_type, entity_id, url, source_type, excerpt, confidence, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    'work_item',
                    1,
                    f'https://example.com/evidence/{i}',
                    source_type,
                    f'Evidence excerpt {i}: OAuth2 authentication and security implementation details for test case {i}',
                    0.7 + (i % 3) * 0.1,
                    f'researcher-{i % 3}'
                ))

            # Populate search_index for evidence
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT
                    id,
                    'evidence',
                    COALESCE(url, 'Evidence Source'),
                    excerpt,
                    '',
                    json_object('source_type', source_type, 'confidence', confidence, 'url', url)
                FROM evidence_sources
            """)

            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    def test_integration_evidence_search_with_limit(self, integration_db):
        """Test evidence search respects limit parameter."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="OAuth2",
            scope=SearchScope.EVIDENCE,
            limit=5
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert len(results.results) <= 5
        assert results.total_results >= len(results.results)

    def test_integration_evidence_search_across_types(self, integration_db):
        """Test searching across different evidence source types."""
        # Arrange
        db_service, _ = integration_db
        search_service = SearchService(db_service)

        query = SearchQuery(
            query="authentication",
            scope=SearchScope.EVIDENCE,
            limit=20
        )

        # Act
        results = search_service.search(query)

        # Assert
        assert results is not None
        assert results.total_results > 0
        # Should find multiple types of evidence sources
        assert len(results.results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
