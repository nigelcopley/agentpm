"""
Document Search Service

Full-text search across document content with ranking, snippets, and highlights.

Current Implementation: File-based search (reads content from disk)
Future Migration: FTS5-based search when Task #711 completes (content column added)

Performance Target: <200ms for 1000+ documents (with FTS5)
"""

from typing import List, Optional, Tuple
from pathlib import Path
import time

from ...core.database.service import DatabaseService
from ...core.database.enums import EntityType
from ...core.search.models import SearchQuery, SearchFilter, SearchScope
from ...core.search.service import SearchService
from .models import DocumentSearchResult


class DocumentSearchService:
    """
    Full-text search service for documents.

    Provides enterprise-grade document search with:
    - Full-text content search
    - Relevance ranking (BM25 algorithm when FTS5 enabled)
    - Context-aware snippets
    - Multi-term highlighting
    - Entity-scoped search
    - Query suggestions

    Current Implementation:
        Hybrid approach - searches metadata via existing DocumentSearchAdapter,
        then enhances with file-based content search for matched documents.

    Future Implementation (after Task #711):
        FTS5-based search with database content column for optimal performance.

    Example:
        >>> service = DocumentSearchService(db_service)
        >>> results = service.search_content("microservices architecture", limit=10)
        >>> for result in results:
        ...     print(f"{result.title}: {result.snippet}")
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize document search service.

        Args:
            db_service: Database service instance for queries
        """
        self.db = db_service
        self.search_service = SearchService(db_service)

    def search_content(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        document_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[DocumentSearchResult]:
        """
        Full-text search across document content.

        Searches document title, description, and content (read from files).
        Returns results ranked by relevance with highlighted snippets.

        Args:
            query: Search query text (supports multi-word queries)
            entity_type: Filter by entity type (work_item, task, etc.)
            document_type: Filter by document type (design, requirements, etc.)
            limit: Maximum results to return
            offset: Number of results to skip (pagination)

        Returns:
            List of DocumentSearchResult objects sorted by relevance

        Example:
            >>> results = service.search_content("database migration")
            >>> print(f"Found {len(results)} documents")
            >>> print(f"Top result: {results[0].title}")
        """
        start_time = time.time()

        # Build search filters
        filters = SearchFilter()
        if entity_type:
            filters.entity_types = [entity_type]

        # Search using existing document adapter (title/description only)
        search_query = SearchQuery(
            query=query,
            scope=SearchScope.DOCUMENTS if hasattr(SearchScope, 'DOCUMENTS') else SearchScope.ALL,
            limit=limit * 3,  # Get more candidates for content filtering
            offset=offset,
            highlight=True
        )
        search_query.filters = filters

        # Get basic results from metadata search
        basic_results = self.search_service.search_documents(
            query=query,
            filters=filters,
            limit=limit * 3,
            offset=offset
        )

        # Enhance with file content search
        enhanced_results = []
        for result in basic_results:
            file_path = result.metadata.get('file_path') if result.metadata else None
            if not file_path:
                continue

            # Read file content (temporary until Task #711 adds content column)
            content = self._read_file_content(file_path)
            if not content:
                # If can't read content, still include if title/description matched
                if query.lower() in (result.title or "").lower():
                    enhanced_results.append(self._create_result_from_metadata(
                        result, query
                    ))
                continue

            # Check if query matches in content
            if self._content_matches(content, query):
                snippet = self._create_snippet(content, query)
                highlights = self._find_highlights(content, query)
                matched_terms = self._extract_matched_terms(content, query)

                # Calculate enhanced relevance score
                # TODO: Replace with BM25 when FTS5 is available
                rank = self._calculate_relevance(
                    content=content,
                    query=query,
                    base_score=result.relevance_score
                )

                enhanced_results.append(DocumentSearchResult(
                    document_id=result.entity_id,
                    title=result.title or "Untitled Document",
                    file_path=file_path,
                    snippet=snippet,
                    rank=rank,
                    matched_terms=matched_terms,
                    highlights=highlights,
                    document_type=result.metadata.get('document_type') if result.metadata else None,
                    entity_type=result.entity_type.value if result.entity_type else None,
                    entity_id=result.metadata.get('entity_id') if result.metadata else None
                ))

        # Sort by rank (descending) and apply limit
        enhanced_results.sort(key=lambda r: r.rank, reverse=True)
        final_results = enhanced_results[:limit]

        # Log search performance
        search_time_ms = (time.time() - start_time) * 1000
        if search_time_ms > 200:  # Performance target
            print(f"WARNING: Document search took {search_time_ms:.1f}ms (target: <200ms)")
            print(f"  Searched {len(basic_results)} documents, returned {len(final_results)} results")

        return final_results

    def search_by_entity(
        self,
        entity_type: EntityType,
        entity_id: int,
        query: str,
        limit: int = 10
    ) -> List[DocumentSearchResult]:
        """
        Search documents associated with a specific entity.

        Args:
            entity_type: Entity type (work_item, task, etc.)
            entity_id: Entity ID
            query: Search query text
            limit: Maximum results to return

        Returns:
            List of DocumentSearchResult objects for the entity

        Example:
            >>> results = service.search_by_entity(
            ...     EntityType.WORK_ITEM,
            ...     133,
            ...     "architecture"
            ... )
        """
        # Build entity filter
        filters = SearchFilter(
            entity_types=[entity_type]
        )

        # TODO: Add entity_id filtering when SearchFilter supports it
        # For now, filter in Python after retrieval
        all_results = self.search_content(
            query=query,
            entity_type=entity_type,
            limit=limit * 2  # Get more to filter
        )

        # Filter by entity_id
        filtered_results = [
            r for r in all_results
            if r.entity_id == entity_id
        ]

        return filtered_results[:limit]

    def get_search_suggestions(
        self,
        partial: str,
        limit: int = 10
    ) -> List[str]:
        """
        Get search query suggestions based on partial input.

        Returns suggested completions based on:
        - Document titles
        - Common terms in content
        - Previous successful searches

        Args:
            partial: Partial search query
            limit: Maximum suggestions to return

        Returns:
            List of suggested query completions

        Note:
            Current implementation returns empty list (stub).
            Will be implemented with FTS5 when Task #711 completes.

        TODO (Task #711):
            - Create FTS5 auxiliary table for term suggestions
            - Implement prefix matching on document content
            - Track popular/successful queries for suggestions
        """
        # TODO: Implement after Task #711 (FTS5 suggestion queries)
        return []

    # Private helper methods

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read document content from file.

        Temporary implementation - reads from disk.
        Will be replaced with database query when Task #711 completes.

        Args:
            file_path: Path to document file (relative to project root)

        Returns:
            File content as string, or None if read fails
        """
        try:
            # Try absolute path first
            path = Path(file_path)
            if not path.is_absolute():
                # Make relative to project root
                # Assumes service is running from project root
                path = Path.cwd() / file_path

            if path.exists() and path.is_file():
                return path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
        return None

    def _content_matches(self, content: str, query: str) -> bool:
        """
        Check if content matches search query.

        Implements simple multi-word matching.
        Will be replaced with FTS5 MATCH when Task #711 completes.

        Args:
            content: Document content
            query: Search query

        Returns:
            True if content matches query
        """
        content_lower = content.lower()
        query_lower = query.lower()

        # Check if all query words are in content
        query_words = query_lower.split()
        return all(word in content_lower for word in query_words)

    def _create_snippet(
        self,
        content: str,
        query: str,
        max_length: int = 200
    ) -> str:
        """
        Create content snippet centered on query match.

        Args:
            content: Full document content
            query: Search query
            max_length: Maximum snippet length

        Returns:
            Content snippet with query match in context
        """
        query_lower = query.lower()
        content_lower = content.lower()

        # Find first occurrence of any query word
        query_words = query_lower.split()
        positions = []
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1:
                positions.append(pos)

        if not positions:
            # No match found, return beginning
            return content[:max_length] + ('...' if len(content) > max_length else '')

        # Use earliest match position
        match_pos = min(positions)

        # Calculate snippet boundaries (centered on match)
        half_length = max_length // 2
        start = max(0, match_pos - half_length)
        end = min(len(content), match_pos + half_length)

        # Adjust start to avoid cutting words
        if start > 0:
            while start < len(content) and content[start] not in ' \n\t':
                start += 1
            start += 1  # Skip the whitespace

        # Extract snippet
        snippet = content[start:end].strip()

        # Add ellipsis
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'

        return snippet

    def _find_highlights(
        self,
        content: str,
        query: str,
        max_highlights: int = 10
    ) -> List[Tuple[int, int]]:
        """
        Find character positions for highlighting matches.

        Args:
            content: Document content
            query: Search query
            max_highlights: Maximum number of highlights to return

        Returns:
            List of (start, end) character positions
        """
        highlights = []
        content_lower = content.lower()

        # Find all query words
        query_words = query.lower().split()

        for word in query_words:
            pos = 0
            while len(highlights) < max_highlights:
                pos = content_lower.find(word, pos)
                if pos == -1:
                    break
                highlights.append((pos, pos + len(word)))
                pos += len(word)

            if len(highlights) >= max_highlights:
                break

        # Sort by position and remove duplicates
        highlights = sorted(list(set(highlights)))
        return highlights[:max_highlights]

    def _extract_matched_terms(self, content: str, query: str) -> List[str]:
        """
        Extract query terms that matched in content.

        Args:
            content: Document content
            query: Search query

        Returns:
            List of query terms found in content
        """
        content_lower = content.lower()
        query_words = query.lower().split()

        matched = []
        for word in query_words:
            if word in content_lower and word not in matched:
                matched.append(word)

        return matched

    def _calculate_relevance(
        self,
        content: str,
        query: str,
        base_score: float
    ) -> float:
        """
        Calculate relevance score for search result.

        Simple algorithm for now - will be replaced with BM25 when FTS5 available.

        Args:
            content: Document content
            query: Search query
            base_score: Base score from metadata search

        Returns:
            Relevance score between 0.0 and 1.0
        """
        content_lower = content.lower()
        query_lower = query.lower()
        query_words = query_lower.split()

        # Count matches
        match_count = sum(content_lower.count(word) for word in query_words)

        # Calculate score based on match density
        content_length = len(content.split())
        density = min(1.0, match_count / max(1, content_length / 100))

        # Boost if query appears as exact phrase
        phrase_boost = 1.2 if query_lower in content_lower else 1.0

        # Combine with base score
        final_score = min(1.0, (base_score * 0.3 + density * 0.7) * phrase_boost)

        return round(final_score, 3)

    def _create_result_from_metadata(
        self,
        search_result,
        query: str
    ) -> DocumentSearchResult:
        """
        Create DocumentSearchResult from metadata-only match.

        Used when file content is not available.

        Args:
            search_result: SearchResult from metadata search
            query: Search query

        Returns:
            DocumentSearchResult with metadata-based snippet
        """
        snippet = search_result.excerpt or search_result.content or ""
        return DocumentSearchResult(
            document_id=search_result.entity_id,
            title=search_result.title or "Untitled Document",
            file_path=search_result.metadata.get('file_path', ''),
            snippet=snippet,
            rank=search_result.relevance_score,
            matched_terms=query.lower().split(),
            highlights=[],
            document_type=search_result.metadata.get('document_type') if search_result.metadata else None,
            entity_type=search_result.entity_type.value if search_result.entity_type else None,
            entity_id=search_result.metadata.get('entity_id') if search_result.metadata else None
        )


# TODO: Future enhancements when Task #711 completes
#
# 1. Add content column to document_references table
# 2. Create FTS5 virtual table:
#    CREATE VIRTUAL TABLE document_content_fts USING fts5(
#        document_id, title, content,
#        tokenize='porter unicode61'
#    );
# 3. Implement rebuild_search_index() method
# 4. Implement update_search_index_for_document(document_id)
# 5. Replace file-based search with FTS5 queries
# 6. Add BM25 ranking with custom weights
# 7. Implement sophisticated query parsing (quoted phrases, boolean operators)
# 8. Add query suggestion using FTS5 auxiliary functions
# 9. Performance optimization: <200ms for 1000+ documents
# 10. Add search analytics and metrics tracking


__all__ = ['DocumentSearchService']
