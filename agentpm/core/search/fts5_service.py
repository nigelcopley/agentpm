"""
FTS5 Search Service

High-performance search service using SQLite FTS5 for full-text search
with advanced features like relevance scoring, boolean queries, and highlighting.
"""

import sqlite3
import time
import hashlib
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..database.service import DatabaseService
from ..database.enums import EntityType
from ..database.models.search_result import SearchResult, SearchResults, SearchResultType
from .models import SearchQuery, SearchConfig, SearchScope
from ..database.models import SearchIndex, SearchMetrics


@dataclass
class FTS5SearchResult:
    """FTS5-specific search result with additional metadata."""
    entity_id: int
    entity_type: str
    title: str
    content: str
    relevance_score: float
    highlighted_title: Optional[str] = None
    highlighted_content: Optional[str] = None
    snippet: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FTS5SearchResults:
    """FTS5 search results with performance metrics."""
    results: List[FTS5SearchResult]
    total_count: int
    query_time_ms: float
    query_text: str
    filters_applied: Dict[str, Any]
    suggestions: Optional[List[str]] = None
    cache_hit: bool = False


class FTS5SearchService:
    """
    High-performance search service using SQLite FTS5.
    
    Provides advanced search features including:
    - BM25 relevance scoring
    - Boolean queries (AND, OR, NOT)
    - Phrase search with quotes
    - Prefix matching with wildcards
    - Text highlighting and snippets
    - Entity type filtering
    - Metadata-based filtering
    """
    
    def __init__(self, db_service: DatabaseService, config: Optional[SearchConfig] = None):
        self.db_service = db_service
        self.config = config or SearchConfig()
        self.fts5_available = self._check_fts5_availability()
        
        if not self.fts5_available:
            print("⚠️  FTS5 not available - using fallback search")
    
    def search(self, query: SearchQuery) -> SearchResults:
        """
        Perform FTS5 search with advanced features.
        
        Args:
            query: Search query with filters and options
            
        Returns:
            SearchResults with ranked and highlighted results
        """
        if not self.fts5_available:
            return self._fallback_search(query)
        
        # Check cache first (disabled for now due to serialization issues)
        # cached_result = self._get_cached_result(query)
        # if cached_result:
        #     cached_result.cache_hit = True
        #     return self._convert_to_search_results(cached_result)
        
        # Execute FTS5 search
        start_time = time.time()
        fts5_results = self._execute_fts5_search(query)
        execution_time = (time.time() - start_time) * 1000
        
        # Record metrics
        self._record_search_metrics(query.query, len(fts5_results.results), execution_time)
        
        # Cache results (disabled for now due to serialization issues)
        # self._cache_results(query, fts5_results)
        
        # Convert to standard format
        return self._convert_to_search_results(fts5_results)
    
    def _check_fts5_availability(self) -> bool:
        """Check if FTS5 is available in this SQLite build."""
        try:
            with self.db_service.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT fts5(?)", ("test",))
                return True
        except sqlite3.OperationalError:
            return False
    
    def _execute_fts5_search(self, query: SearchQuery) -> FTS5SearchResults:
        """Execute FTS5 search with advanced features."""
        # Build FTS5 query string
        fts5_query = self._build_fts5_query(query)
        
        # Build SQL with FTS5 features
        sql = """
        SELECT 
            entity_id,
            entity_type,
            title,
            content,
            bm25(search_index) as relevance_score,
            highlight(search_index, 2, '<mark>', '</mark>') as highlighted_title,
            highlight(search_index, 3, '<mark>', '</mark>') as highlighted_content,
            snippet(search_index, 3, '<b>', '</b>', '...', 32) as snippet,
            metadata
        FROM search_index 
        WHERE search_index MATCH ?
        ORDER BY relevance_score
        LIMIT ? OFFSET ?
        """
        
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (fts5_query, query.limit, query.offset))
            
            results = []
            for row in cursor.fetchall():
                result = FTS5SearchResult(
                    entity_id=row[0],
                    entity_type=row[1],
                    title=row[2],
                    content=row[3],
                    relevance_score=row[4],
                    highlighted_title=row[5],
                    highlighted_content=row[6],
                    snippet=row[7],
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                results.append(result)
            
            # Get total count
            count_sql = "SELECT COUNT(*) FROM search_index WHERE search_index MATCH ?"
            cursor.execute(count_sql, (fts5_query,))
            total_count = cursor.fetchone()[0]
            
        return FTS5SearchResults(
            results=results,
            total_count=total_count,
            query_time_ms=0,  # Will be set by caller
            query_text=query.query,
            filters_applied=query.filters or {}
        )
    
    def _build_fts5_query(self, query: SearchQuery) -> str:
        """Build FTS5 query string with entity type and metadata filtering."""
        fts5_query = query.query
        
        # Add entity type filtering
        if query.filters and query.filters.entity_types:
            entity_filters = [f'entity_type:{et.value}' for et in query.filters.entity_types]
            fts5_query += f' AND ({" OR ".join(entity_filters)})'
        
        # Add metadata filtering
        if query.filters:
            # Handle specific filter fields
            if query.filters.work_item_statuses:
                status_filters = [f'metadata.status:{status.value}' for status in query.filters.work_item_statuses]
                fts5_query += f' AND ({" OR ".join(status_filters)})'
            
            if query.filters.task_statuses:
                status_filters = [f'metadata.status:{status.value}' for status in query.filters.task_statuses]
                fts5_query += f' AND ({" OR ".join(status_filters)})'
            
            if query.filters.idea_statuses:
                status_filters = [f'metadata.status:{status.value}' for status in query.filters.idea_statuses]
                fts5_query += f' AND ({" OR ".join(status_filters)})'
        
        return fts5_query
    
    def _get_cached_result(self, query: SearchQuery) -> Optional[FTS5SearchResults]:
        """Get cached search results if available."""
        query_hash = self._hash_query(query)
        
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT result_data FROM search_cache 
                WHERE query_hash = ? AND expires_at > datetime('now')
            """, (query_hash,))
            
            row = cursor.fetchone()
            if row:
                try:
                    data = json.loads(row[0])
                    return FTS5SearchResults(**data)
                except (json.JSONDecodeError, TypeError):
                    # Invalid cache data, remove it
                    cursor.execute("DELETE FROM search_cache WHERE query_hash = ?", (query_hash,))
                    conn.commit()
        
        return None
    
    def _cache_results(self, query: SearchQuery, results: FTS5SearchResults) -> None:
        """Cache search results for future use."""
        query_hash = self._hash_query(query)
        expires_at = datetime.now() + timedelta(hours=1)  # Cache for 1 hour
        
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO search_cache 
                (query_hash, query_text, result_data, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                query_hash,
                query.query,
                json.dumps(results.__dict__, default=str),
                expires_at.isoformat()
            ))
            conn.commit()
    
    def _hash_query(self, query: SearchQuery) -> str:
        """Generate hash for query caching."""
        query_str = f"{query.query}|{query.filters}|{query.limit}|{query.offset}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _record_search_metrics(self, query_text: str, result_count: int, execution_time_ms: float) -> None:
        """Record search performance metrics."""
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_metrics 
                (project_id, query_text, result_count, execution_time_ms, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (1, query_text, result_count, execution_time_ms, "system"))
            conn.commit()
    
    def _convert_to_search_results(self, fts5_results: FTS5SearchResults) -> SearchResults:
        """Convert FTS5 results to standard SearchResults format."""
        standard_results = []
        for i, result in enumerate(fts5_results.results):
            # Convert FTS5 relevance score to 0-1 range (FTS5 uses negative scores)
            normalized_score = max(0.0, min(1.0, abs(result.relevance_score) / 10.0))
            
            standard_result = SearchResult(
                id=i + 1,  # Sequential ID for search results
                entity_id=result.entity_id,
                entity_type=EntityType(result.entity_type),
                result_type=SearchResultType(result.entity_type),
                title=result.title or "Untitled",
                content=result.content or result.title or "No content available",
                relevance_score=normalized_score,
                match_type="fts5",
                matched_fields=["title", "content"],
                search_query=fts5_results.query_text,
                metadata=result.metadata
            )
            standard_results.append(standard_result)
        
        # Calculate statistics
        avg_relevance = sum(r.relevance_score for r in standard_results) / len(standard_results) if standard_results else 0.0
        high_relevance_count = sum(1 for r in standard_results if r.relevance_score >= 0.8)
        
        # Count by entity type
        entity_type_counts = {}
        for result in standard_results:
            entity_type = result.entity_type.value
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        return SearchResults(
            query=fts5_results.query_text,
            total_results=fts5_results.total_count,
            results=standard_results,
            search_time_ms=fts5_results.query_time_ms,
            avg_relevance_score=avg_relevance,
            high_relevance_count=high_relevance_count,
            entity_type_counts=entity_type_counts
        )
    
    def _fallback_search(self, query: SearchQuery) -> SearchResults:
        """Fallback to LIKE-based search when FTS5 is not available."""
        # Simple LIKE-based search implementation
        sql = """
        SELECT entity_id, entity_type, title, content, metadata
        FROM search_index 
        WHERE (title LIKE ? OR content LIKE ?)
        LIMIT ? OFFSET ?
        """
        
        search_term = f"%{query.query}%"
        
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (search_term, search_term, query.limit, query.offset))
            
            results = []
            for i, row in enumerate(cursor.fetchall()):
                result = SearchResult(
                    id=i + 1,
                    entity_id=row[0],
                    entity_type=EntityType(row[1]),
                    result_type=SearchResultType(row[1]),
                    title=row[2],
                    content=row[3],
                    relevance_score=1.0,  # No relevance scoring in fallback
                    match_type="like",
                    matched_fields=["title", "content"],
                    search_query=query.query,
                    metadata=json.loads(row[4]) if row[4] else {}
                )
                results.append(result)
            
            # Get total count
            count_sql = "SELECT COUNT(*) FROM search_index WHERE (title LIKE ? OR content LIKE ?)"
            cursor.execute(count_sql, (search_term, search_term))
            total_count = cursor.fetchone()[0]
            
            # Calculate statistics for fallback
            avg_relevance = sum(r.relevance_score for r in results) / len(results) if results else 0.0
            high_relevance_count = sum(1 for r in results if r.relevance_score >= 0.8)
            
            # Count by entity type
            entity_type_counts = {}
            for result in results:
                entity_type = result.entity_type.value
                entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
            
            return SearchResults(
                query=query.query,
                total_results=total_count,
                results=results,
                search_time_ms=0,
                avg_relevance_score=avg_relevance,
                high_relevance_count=high_relevance_count,
                entity_type_counts=entity_type_counts
            )
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query."""
        if not self.fts5_available:
            return []
        
        # Get suggestions from search metrics
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT query_text, COUNT(*) as frequency
                FROM search_metrics 
                WHERE query_text LIKE ?
                GROUP BY query_text
                ORDER BY frequency DESC, query_text
                LIMIT ?
            """, (f"%{partial_query}%", limit))
            
            suggestions = [row[0] for row in cursor.fetchall()]
            return suggestions
    
    def get_search_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get search performance metrics."""
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            
            # Get metrics for the last N days
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_searches,
                    AVG(execution_time_ms) as avg_execution_time,
                    AVG(result_count) as avg_result_count,
                    COUNT(DISTINCT query_text) as unique_queries
                FROM search_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_searches': row[0],
                    'avg_execution_time_ms': row[1] or 0,
                    'avg_result_count': row[2] or 0,
                    'unique_queries': row[3],
                    'days': days
                }
            
            return {
                'total_searches': 0,
                'avg_execution_time_ms': 0,
                'avg_result_count': 0,
                'unique_queries': 0,
                'days': days
            }
    
    def clear_cache(self) -> None:
        """Clear all cached search results."""
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_cache")
            conn.commit()
    
    def cleanup_expired_cache(self) -> int:
        """Remove expired cache entries and return count of removed entries."""
        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_cache WHERE expires_at <= datetime('now')")
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count

    def search_summaries(
        self,
        query: str,
        entity_type: Optional[str] = None,
        summary_type: Optional[str] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search summaries using FTS5 full-text search.

        Args:
            query: Search query text
            entity_type: Filter by entity type (work_item, task, project, session, idea)
            summary_type: Filter by summary type (session, milestone, decision, etc.)
            limit: Maximum results to return

        Returns:
            List of SearchResult objects with summaries
        """
        if not self.fts5_available:
            return self._fallback_search_summaries(query, entity_type, summary_type, limit)

        # Check if summaries_fts table exists
        if not self._check_summaries_fts_exists():
            print("⚠️  summaries_fts table not found - using fallback search")
            return self._fallback_search_summaries(query, entity_type, summary_type, limit)

        # Build FTS5 query string with filters
        fts5_query = self._build_summaries_fts5_query(query, entity_type, summary_type)

        # Build SQL with FTS5 features
        sql = """
        SELECT
            s.id,
            s.entity_id,
            s.entity_type,
            s.summary_type,
            s.summary_text,
            bm25(summaries_fts) as relevance_score,
            snippet(summaries_fts, 4, '<b>', '</b>', '...', 32) as snippet,
            s.context_metadata,
            s.created_at
        FROM summaries_fts
        JOIN summaries s ON summaries_fts.summary_id = s.id
        WHERE summaries_fts MATCH ?
        ORDER BY relevance_score
        LIMIT ?
        """

        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (fts5_query, limit))

            results = []
            for i, row in enumerate(cursor.fetchall()):
                # Convert FTS5 relevance score to 0-1 range (FTS5 uses negative scores)
                normalized_score = max(0.0, min(1.0, abs(row[5]) / 10.0))

                # Build title from entity type and summary type
                title = f"{row[2].replace('_', ' ').title()} {row[3].replace('_', ' ').title()}"

                result = SearchResult(
                    id=i + 1,
                    entity_id=row[1],
                    entity_type=EntityType(row[2]),
                    result_type=SearchResultType.SUMMARY,
                    title=title,
                    content=row[6] or row[4][:200],  # Use snippet or truncated summary_text
                    relevance_score=normalized_score,
                    match_type="fts5",
                    matched_fields=["summary_text", "context_metadata"],
                    search_query=query,
                    metadata={
                        "summary_id": row[0],
                        "summary_type": row[3],
                        "context_metadata": json.loads(row[7]) if row[7] else {},
                        "created_at": row[8]
                    }
                )
                results.append(result)

            return results

    def _check_summaries_fts_exists(self) -> bool:
        """Check if summaries_fts virtual table exists."""
        try:
            with self.db_service.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='summaries_fts'
                """)
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False

    def _build_summaries_fts5_query(
        self,
        query: str,
        entity_type: Optional[str] = None,
        summary_type: Optional[str] = None
    ) -> str:
        """Build FTS5 query string with entity type and summary type filtering."""
        fts5_query = query

        # Add entity type filtering
        if entity_type:
            fts5_query += f' AND entity_type:{entity_type}'

        # Add summary type filtering
        if summary_type:
            fts5_query += f' AND summary_type:{summary_type}'

        return fts5_query

    def _fallback_search_summaries(
        self,
        query: str,
        entity_type: Optional[str] = None,
        summary_type: Optional[str] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """Fallback to LIKE-based search when FTS5 is not available."""
        search_term = f"%{query}%"

        # Build WHERE clause with optional filters
        where_clauses = ["(summary_text LIKE ? OR context_metadata LIKE ?)"]
        params = [search_term, search_term]

        if entity_type:
            where_clauses.append("entity_type = ?")
            params.append(entity_type)

        if summary_type:
            where_clauses.append("summary_type = ?")
            params.append(summary_type)

        params.append(limit)

        sql = f"""
        SELECT
            id, entity_id, entity_type, summary_type, summary_text,
            context_metadata, created_at
        FROM summaries
        WHERE {' AND '.join(where_clauses)}
        ORDER BY created_at DESC
        LIMIT ?
        """

        with self.db_service.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)

            results = []
            for i, row in enumerate(cursor.fetchall()):
                title = f"{row[2].replace('_', ' ').title()} {row[3].replace('_', ' ').title()}"

                result = SearchResult(
                    id=i + 1,
                    entity_id=row[1],
                    entity_type=EntityType(row[2]),
                    result_type=SearchResultType.SUMMARY,
                    title=title,
                    content=row[4][:200] if len(row[4]) > 200 else row[4],
                    relevance_score=1.0,  # No relevance scoring in fallback
                    match_type="like",
                    matched_fields=["summary_text", "context_metadata"],
                    search_query=query,
                    metadata={
                        "summary_id": row[0],
                        "summary_type": row[3],
                        "context_metadata": json.loads(row[5]) if row[5] else {},
                        "created_at": row[6]
                    }
                )
                results.append(result)

            return results
