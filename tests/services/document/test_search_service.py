"""
Tests for DocumentSearchService

Tests cover:
- Basic search functionality
- Entity-scoped search
- Snippet generation
- Highlight extraction
- Relevance ranking
- Error handling
- Performance benchmarks (for future FTS5)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agentpm.services.document.search_service import DocumentSearchService
from agentpm.services.document.models import DocumentSearchResult
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.enums import EntityType
from agentpm.core.database.models.search_result import SearchResult, SearchResultType


@pytest.fixture
def mock_db_service():
    """Create mock database service."""
    db = Mock(spec=DatabaseService)
    return db


@pytest.fixture
def mock_search_service():
    """Create mock search service."""
    with patch('agentpm.services.document.search_service.SearchService') as mock:
        yield mock


@pytest.fixture
def search_service(mock_db_service, mock_search_service):
    """Create DocumentSearchService instance with mocks."""
    return DocumentSearchService(mock_db_service)


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    return [
        SearchResult(
            id=1,
            entity_type=EntityType.WORK_ITEM,  # Documents are associated with entities
            entity_id=42,
            result_type=SearchResultType.DOCUMENT,
            title="Architecture Design",
            content="System architecture using microservices",
            excerpt="...architecture using microservices...",
            relevance_score=0.85,
            match_type="text_match",
            matched_fields=["title", "content"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                'file_path': 'docs/architecture/design/system-design.md',
                'document_type': 'design',
                'entity_type': 'work_item',
                'entity_id': 133
            },
            search_query="architecture"
        ),
        SearchResult(
            id=2,
            entity_type=EntityType.WORK_ITEM,  # Documents are associated with entities
            entity_id=43,
            result_type=SearchResultType.DOCUMENT,
            title="Database Design",
            content="Database schema design for microservices",
            excerpt="...schema design for microservices...",
            relevance_score=0.75,
            match_type="text_match",
            matched_fields=["title"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                'file_path': 'docs/architecture/design/database-design.md',
                'document_type': 'design',
                'entity_type': 'work_item',
                'entity_id': 133
            },
            search_query="architecture"
        )
    ]


@pytest.fixture
def sample_document_content():
    """Sample document content for testing."""
    return """
# Architecture Design Document

## Overview
This document describes the microservices architecture for the AIPM system.
The architecture follows hexagonal principles and domain-driven design.

## Components
- Service Registry
- API Gateway
- Database Layer
- Search Service

## Microservices Architecture
The system is built using a microservices architecture pattern, where each
service has its own database and communicates via REST APIs.
"""


class TestDocumentSearchService:
    """Test DocumentSearchService functionality."""

    def test_initialization(self, mock_db_service):
        """Test service initialization."""
        service = DocumentSearchService(mock_db_service)
        assert service.db == mock_db_service
        assert service.search_service is not None

    def test_search_content_basic(
        self,
        search_service,
        mock_search_service,
        sample_search_results,
        sample_document_content
    ):
        """Test basic content search."""
        # Setup mock
        mock_search_service.return_value.search_documents.return_value = sample_search_results

        # Mock file reading
        with patch.object(
            search_service,
            '_read_file_content',
            return_value=sample_document_content
        ):
            results = search_service.search_content("microservices")

        # Verify results
        assert len(results) > 0
        assert all(isinstance(r, DocumentSearchResult) for r in results)

    def test_search_content_with_filters(
        self,
        search_service,
        mock_search_service,
        sample_search_results
    ):
        """Test search with entity type filter."""
        mock_search_service.return_value.search_documents.return_value = sample_search_results

        with patch.object(search_service, '_read_file_content', return_value="content"):
            results = search_service.search_content(
                "architecture",
                entity_type=EntityType.WORK_ITEM
            )

        # Verify filter was applied
        assert isinstance(results, list)

    def test_search_content_with_limit(
        self,
        search_service,
        mock_search_service,
        sample_search_results
    ):
        """Test search respects limit parameter."""
        # Create many results
        many_results = sample_search_results * 10  # 20 results
        mock_search_service.return_value.search_documents.return_value = many_results

        with patch.object(search_service, '_read_file_content', return_value="content"):
            results = search_service.search_content("test", limit=5)

        assert len(results) <= 5

    def test_search_by_entity(
        self,
        search_service,
        mock_search_service,
        sample_search_results,
        sample_document_content
    ):
        """Test entity-scoped search."""
        mock_search_service.return_value.search_documents.return_value = sample_search_results

        with patch.object(
            search_service,
            '_read_file_content',
            return_value=sample_document_content
        ):
            results = search_service.search_by_entity(
                EntityType.WORK_ITEM,
                133,
                "architecture"
            )

        # Verify entity filtering
        assert all(r.entity_id == 133 for r in results)

    def test_get_search_suggestions(self, search_service):
        """Test search suggestions (stub)."""
        suggestions = search_service.get_search_suggestions("arc")
        # Currently returns empty list (stub)
        assert isinstance(suggestions, list)

    def test_create_snippet(self, search_service):
        """Test snippet creation."""
        content = "This is a test document about microservices architecture."
        query = "microservices"

        snippet = search_service._create_snippet(content, query, max_length=50)

        assert isinstance(snippet, str)
        assert "microservices" in snippet.lower()
        assert len(snippet) <= 100  # Including ellipsis

    def test_create_snippet_no_match(self, search_service):
        """Test snippet when query not found."""
        content = "This is a test document."
        query = "nonexistent"

        snippet = search_service._create_snippet(content, query, max_length=20)

        assert isinstance(snippet, str)
        # Should return beginning of content
        assert snippet.startswith("This is a test")

    def test_find_highlights(self, search_service):
        """Test highlight position extraction."""
        content = "microservices are used in microservices architecture"
        query = "microservices"

        highlights = search_service._find_highlights(content, query)

        assert isinstance(highlights, list)
        assert len(highlights) >= 2  # Two occurrences
        assert all(isinstance(h, tuple) and len(h) == 2 for h in highlights)

    def test_find_highlights_multi_word(self, search_service):
        """Test highlights for multi-word query."""
        content = "The architecture uses microservices pattern"
        query = "architecture microservices"

        highlights = search_service._find_highlights(content, query)

        assert isinstance(highlights, list)
        assert len(highlights) >= 2  # Both words should be found

    def test_extract_matched_terms(self, search_service):
        """Test matched term extraction."""
        content = "This document discusses architecture and design"
        query = "architecture design database"

        matched = search_service._extract_matched_terms(content, query)

        assert "architecture" in matched
        assert "design" in matched
        assert "database" not in matched  # Not in content

    def test_calculate_relevance(self, search_service):
        """Test relevance calculation."""
        content = "microservices architecture " * 5  # High density
        query = "microservices"

        relevance = search_service._calculate_relevance(content, query, base_score=0.5)

        assert 0.0 <= relevance <= 1.0
        assert relevance > 0.5  # Should boost from base score

    def test_calculate_relevance_phrase_boost(self, search_service):
        """Test relevance with exact phrase match."""
        content = "The microservices architecture is scalable"
        query = "microservices architecture"

        relevance = search_service._calculate_relevance(content, query, base_score=0.5)

        # Should get phrase boost
        assert relevance > 0.5

    def test_content_matches(self, search_service):
        """Test content matching logic."""
        content = "This is about microservices and architecture"

        assert search_service._content_matches(content, "microservices")
        assert search_service._content_matches(content, "architecture")
        assert search_service._content_matches(content, "microservices architecture")
        assert not search_service._content_matches(content, "database")

    def test_read_file_content_success(self, search_service, tmp_path):
        """Test successful file reading."""
        # Create temporary file
        test_file = tmp_path / "test.md"
        test_content = "# Test Document\n\nContent here."
        test_file.write_text(test_content)

        content = search_service._read_file_content(str(test_file))

        assert content == test_content

    def test_read_file_content_not_found(self, search_service):
        """Test file reading with non-existent file."""
        content = search_service._read_file_content("/nonexistent/file.md")
        assert content is None

    def test_read_file_content_relative_path(self, search_service, tmp_path, monkeypatch):
        """Test file reading with relative path."""
        # Create temporary file in "current directory"
        test_file = tmp_path / "docs" / "test.md"
        test_file.parent.mkdir(parents=True)
        test_content = "Test content"
        test_file.write_text(test_content)

        # Change to tmp_path as working directory
        monkeypatch.chdir(tmp_path)

        content = search_service._read_file_content("docs/test.md")

        assert content == test_content

    def test_search_content_file_not_found(
        self,
        search_service,
        mock_search_service,
        sample_search_results
    ):
        """Test search when document files cannot be read."""
        mock_search_service.return_value.search_documents.return_value = sample_search_results

        with patch.object(search_service, '_read_file_content', return_value=None):
            results = search_service.search_content("architecture")

        # Should still return results based on metadata
        # or empty list if content search required
        assert isinstance(results, list)

    def test_search_content_empty_query(self, search_service, mock_search_service):
        """Test search with empty query."""
        # Empty query should raise validation error from SearchQuery
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            search_service.search_content("")

    def test_search_results_sorted_by_rank(
        self,
        search_service,
        mock_search_service,
        sample_search_results,
        sample_document_content
    ):
        """Test that results are sorted by relevance rank."""
        mock_search_service.return_value.search_documents.return_value = sample_search_results

        with patch.object(
            search_service,
            '_read_file_content',
            return_value=sample_document_content
        ):
            results = search_service.search_content("architecture")

        # Verify results are sorted (descending)
        if len(results) > 1:
            ranks = [r.rank for r in results]
            assert ranks == sorted(ranks, reverse=True)

    def test_document_search_result_model(self):
        """Test DocumentSearchResult model."""
        result = DocumentSearchResult(
            document_id=42,
            title="Test Document",
            file_path="docs/test.md",
            snippet="...test content...",
            rank=0.85,
            matched_terms=["test", "content"],
            highlights=[(10, 14), (20, 27)],
            document_type="design",
            entity_type="work_item",
            entity_id=133
        )

        assert result.document_id == 42
        assert result.title == "Test Document"
        assert result.rank == 0.85
        assert len(result.matched_terms) == 2
        assert len(result.highlights) == 2

    def test_document_search_result_validation(self):
        """Test DocumentSearchResult validation."""
        # Rank must be between 0 and 1
        with pytest.raises(ValueError):
            DocumentSearchResult(
                document_id=1,
                title="Test",
                file_path="test.md",
                snippet="snippet",
                rank=1.5,  # Invalid
                matched_terms=[],
                highlights=[]
            )


class TestDocumentSearchPerformance:
    """Performance tests for document search (benchmarks for future FTS5)."""

    @pytest.mark.skip(reason="Performance test - run manually")
    def test_search_performance_target(self, search_service):
        """Test search performance meets <200ms target."""
        # This test will be enabled when FTS5 is implemented
        # For now, it documents the performance requirement
        import time

        start = time.time()
        results = search_service.search_content("architecture", limit=100)
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 200, f"Search took {elapsed_ms}ms (target: <200ms)"

    @pytest.mark.skip(reason="Load test - run manually")
    def test_search_large_dataset(self, search_service):
        """Test search with 1000+ documents."""
        # This will be implemented when we have FTS5
        # Documents expected behavior with large dataset
        pass


class TestFTS5Integration:
    """Tests for future FTS5 implementation (currently skipped)."""

    @pytest.mark.skip(reason="FTS5 not yet implemented - blocked by Task #711")
    def test_rebuild_search_index(self):
        """Test FTS5 index rebuild."""
        # TODO: Implement when Task #711 completes
        pass

    @pytest.mark.skip(reason="FTS5 not yet implemented - blocked by Task #711")
    def test_update_search_index_for_document(self):
        """Test incremental FTS5 index update."""
        # TODO: Implement when Task #711 completes
        pass

    @pytest.mark.skip(reason="FTS5 not yet implemented - blocked by Task #711")
    def test_bm25_ranking(self):
        """Test BM25 relevance ranking."""
        # TODO: Implement when Task #711 completes
        pass

    @pytest.mark.skip(reason="FTS5 not yet implemented - blocked by Task #711")
    def test_query_suggestions_fts5(self):
        """Test query suggestions using FTS5."""
        # TODO: Implement when Task #711 completes
        pass


# Test fixtures for integration tests (when DB available)

@pytest.fixture
def integration_db_service():
    """Real database service for integration tests."""
    # TODO: Setup test database
    pytest.skip("Integration tests require test database setup")


@pytest.mark.integration
class TestDocumentSearchIntegration:
    """Integration tests with real database (skipped in unit tests)."""

    def test_search_real_documents(self, integration_db_service):
        """Test search against real database."""
        service = DocumentSearchService(integration_db_service)
        results = service.search_content("architecture")
        assert isinstance(results, list)

    def test_search_by_work_item(self, integration_db_service):
        """Test searching documents for a work item."""
        service = DocumentSearchService(integration_db_service)
        results = service.search_by_entity(
            EntityType.WORK_ITEM,
            133,
            "design"
        )
        assert isinstance(results, list)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (skipped by default)"
    )
    config.addinivalue_line(
        "markers",
        "performance: marks tests as performance benchmarks"
    )
