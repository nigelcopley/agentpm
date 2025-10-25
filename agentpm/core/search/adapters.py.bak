"""
Search Adapters

Entity-specific search adapters that handle search logic for different
entity types in the APM (Agent Project Manager) system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import re
import sqlite3

from ..database.service import DatabaseService
from ..database.enums import EntityType, SearchResultType
from ..database.models.search_result import SearchResult
from .models import SearchQuery, SearchFilter


class BaseSearchAdapter(ABC):
    """Base class for entity-specific search adapters."""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.entity_type = self.get_entity_type()
    
    @abstractmethod
    def get_entity_type(self) -> EntityType:
        """Get the entity type this adapter handles."""
        pass
    
    @abstractmethod
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search for entities matching the query and filters."""
        pass
    
    @abstractmethod
    def index_entity(self, entity_id: int) -> bool:
        """Index a single entity for search."""
        pass
    
    @abstractmethod
    def reindex_all(self) -> int:
        """Reindex all entities of this type."""
        pass
    
    def calculate_relevance(self, query: str, text: str, matched_fields: List[str]) -> float:
        """
        Calculate relevance score for a text match.
        
        Args:
            query: Search query
            text: Text content that matched
            matched_fields: Fields that matched
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not text or not query:
            return 0.0
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Exact match gets highest score
        if query_lower in text_lower:
            base_score = 1.0
        else:
            # Partial match based on word overlap
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            overlap = len(query_words.intersection(text_words))
            base_score = overlap / len(query_words) if query_words else 0.0
        
        # Boost based on field importance
        field_boost = 1.0
        if 'title' in matched_fields or 'name' in matched_fields:
            field_boost = 1.2
        elif 'description' in matched_fields:
            field_boost = 1.1
        elif 'content' in matched_fields:
            field_boost = 1.0
        
        # Boost based on position (earlier matches are more relevant)
        position_boost = 1.0
        if query_lower in text_lower:
            position = text_lower.find(query_lower)
            if position < len(text_lower) * 0.1:  # First 10%
                position_boost = 1.1
            elif position < len(text_lower) * 0.3:  # First 30%
                position_boost = 1.05
        
        final_score = min(1.0, base_score * field_boost * position_boost)
        return round(final_score, 3)
    
    def create_excerpt(self, text: str, query: str, max_length: int = 200) -> str:
        """
        Create a relevant excerpt from text highlighting the query.
        
        Args:
            text: Full text content
            query: Search query
            max_length: Maximum excerpt length
            
        Returns:
            Excerpt with query highlighted
        """
        if not text or not query:
            return text[:max_length] if text else ""
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find query position
        query_pos = text_lower.find(query_lower)
        if query_pos == -1:
            # Query not found, return beginning
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Calculate excerpt boundaries
        start = max(0, query_pos - max_length // 2)
        end = min(len(text), start + max_length)
        
        # Adjust start to avoid cutting words
        if start > 0:
            while start < len(text) and text[start] not in ' \n\t':
                start += 1
        
        excerpt = text[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def apply_filters(self, base_query: str, params: List[Any], filters: Optional[SearchFilter]) -> Tuple[str, List[Any]]:
        """
        Apply search filters to a base SQL query.
        
        Args:
            base_query: Base SQL query
            params: Current query parameters
            filters: Search filters to apply
            
        Returns:
            Tuple of (modified_query, updated_params)
        """
        if not filters:
            return base_query, params
        
        query_parts = [base_query]
        
        # Entity type filter
        if filters.entity_types and self.entity_type not in filters.entity_types:
            return base_query + " AND 1=0", params  # No results
        
        # Entity ID filter
        if filters.entity_ids:
            placeholders = ",".join(["?"] * len(filters.entity_ids))
            query_parts.append(f"AND id IN ({placeholders})")
            params.extend(filters.entity_ids)
        
        # Project filter
        if filters.project_id:
            query_parts.append("AND project_id = ?")
            params.append(filters.project_id)
        
        # Work item filter
        if filters.work_item_id and hasattr(self, 'work_item_id'):
            query_parts.append("AND work_item_id = ?")
            params.append(filters.work_item_id)
        
        # Task filter
        if filters.task_id and hasattr(self, 'task_id'):
            query_parts.append("AND task_id = ?")
            params.append(filters.task_id)
        
        # Creator filter
        if filters.created_by:
            query_parts.append("AND created_by = ?")
            params.append(filters.created_by)
        
        # Date filters
        if filters.created_after:
            query_parts.append("AND created_at >= ?")
            params.append(filters.created_after)
        
        if filters.created_before:
            query_parts.append("AND created_at <= ?")
            params.append(filters.created_before)
        
        if filters.updated_after:
            query_parts.append("AND updated_at >= ?")
            params.append(filters.updated_after)
        
        if filters.updated_before:
            query_parts.append("AND updated_at <= ?")
            params.append(filters.updated_before)
        
        # Archive filter
        if not filters.include_archived:
            query_parts.append("AND status != 'archived'")
        
        return " ".join(query_parts), params


class WorkItemSearchAdapter(BaseSearchAdapter):
    """Search adapter for work items."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.WORK_ITEM
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search work items."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, name, description, status, type, created_at, updated_at, 
                   created_by, project_id, tags
            FROM work_items 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(name LIKE ? OR description LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            # Split query into words for partial matching
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(name LIKE ? OR description LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check name match
                if query_lower in (row['name'] or "").lower():
                    matched_fields.append('name')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['name'], ['name']))
                
                # Check description match
                if row['description'] and query_lower in row['description'].lower():
                    matched_fields.append('description')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['description'], ['description']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['description'] or row['name']
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.WORK_ITEM,
                    entity_id=row['id'],
                    result_type=SearchResultType.WORK_ITEM,
                    title=row['name'],
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    search_query=query.query
                ))
        
        except Exception as e:
            # Log error and return empty results
            print(f"Work item search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        """Index a single work item."""
        # For now, just return True - indexing will be implemented later
        return True
    
    def reindex_all(self) -> int:
        """Reindex all work items."""
        # For now, just return 0 - indexing will be implemented later
        return 0


class TaskSearchAdapter(BaseSearchAdapter):
    """Search adapter for tasks."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.TASK
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search tasks."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query with work item join
        base_query = """
            SELECT t.id, t.name, t.description, t.status, t.created_at, t.updated_at,
                   t.created_by, t.work_item_id, wi.project_id
            FROM tasks t
            JOIN work_items wi ON t.work_item_id = wi.id
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(t.name LIKE ? OR t.description LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(t.name LIKE ? OR t.description LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check name match
                if query_lower in (row['name'] or "").lower():
                    matched_fields.append('name')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['name'], ['name']))
                
                # Check description match
                if row['description'] and query_lower in row['description'].lower():
                    matched_fields.append('description')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['description'], ['description']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['description'] or row['name']
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.TASK,
                    entity_id=row['id'],
                    result_type=SearchResultType.TASK,
                    title=row['name'],
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    work_item_id=row['work_item_id'],
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Task search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class IdeaSearchAdapter(BaseSearchAdapter):
    """Search adapter for ideas."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.IDEA
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search ideas."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, title, description, status, created_at, updated_at,
                   created_by, project_id, tags, votes
            FROM ideas 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(title LIKE ? OR description LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(title LIKE ? OR description LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY votes DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check title match
                if query_lower in (row['title'] or "").lower():
                    matched_fields.append('title')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['title'], ['title']))
                
                # Check description match
                if row['description'] and query_lower in row['description'].lower():
                    matched_fields.append('description')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['description'], ['description']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['description'] or row['title']
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.IDEA,
                    entity_id=row['id'],
                    result_type=SearchResultType.IDEA,
                    title=row['title'],
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Idea search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class DocumentSearchAdapter(BaseSearchAdapter):
    """Search adapter for documents."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.DOCUMENT
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search documents."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, title, summary, file_path, category, tags, created_at, updated_at,
                   created_by, project_id, entity_type, entity_id
            FROM document_references 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(title LIKE ? OR summary LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(title LIKE ? OR summary LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check title match
                if query_lower in (row['title'] or "").lower():
                    matched_fields.append('title')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['title'], ['title']))
                
                # Check summary match
                if row['summary'] and query_lower in row['summary'].lower():
                    matched_fields.append('summary')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['summary'], ['summary']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['summary'] or row['title']
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.DOCUMENT,
                    entity_id=row['id'],
                    result_type=SearchResultType.DOCUMENT,
                    title=row['title'],
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    metadata={'file_path': row['file_path'], 'category': row['category']},
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Document search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class SummarySearchAdapter(BaseSearchAdapter):
    """Search adapter for summaries."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.SUMMARY
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search summaries."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, entity_type, entity_id, summary_type, summary_text, 
                   created_at, updated_at, created_by, project_id
            FROM summaries 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("summary_text LIKE ?")
            search_params.append(f"%{query.query}%")
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("summary_text LIKE ?")
                search_params.append(f"%{word}%")
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                relevance = self.calculate_relevance(query.query, row['summary_text'], ['summary_text'])
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                excerpt = self.create_excerpt(row['summary_text'], query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.SUMMARY,
                    entity_id=row['id'],
                    result_type=SearchResultType.SUMMARY,
                    title=f"Summary for {row['entity_type']} #{row['entity_id']}",
                    content=row['summary_text'],
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=['summary_text'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    metadata={'entity_type': row['entity_type'], 'entity_id': row['entity_id'], 'summary_type': row['summary_type']},
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Summary search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class EvidenceSearchAdapter(BaseSearchAdapter):
    """Search adapter for evidence sources."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.EVIDENCE
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search evidence sources."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, source_type, source_url, description, confidence_score,
                   created_at, updated_at, created_by, project_id, entity_type, entity_id
            FROM evidence_sources 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(source_url LIKE ? OR description LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(source_url LIKE ? OR description LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY confidence_score DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check URL match
                if query_lower in (row['source_url'] or "").lower():
                    matched_fields.append('source_url')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['source_url'], ['source_url']))
                
                # Check description match
                if row['description'] and query_lower in row['description'].lower():
                    matched_fields.append('description')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['description'], ['description']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['description'] or row['source_url']
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.EVIDENCE,
                    entity_id=row['id'],
                    result_type=SearchResultType.EVIDENCE,
                    title=f"Evidence: {row['source_type']}",
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['created_by'],
                    project_id=row['project_id'],
                    metadata={'source_type': row['source_type'], 'source_url': row['source_url'], 'confidence_score': row['confidence_score']},
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Evidence search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class LearningSearchAdapter(BaseSearchAdapter):
    """Search adapter for learnings."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.LEARNING
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search learnings."""
        # For now, return empty results as learnings table may not exist yet
        return []
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


class SessionSearchAdapter(BaseSearchAdapter):
    """Search adapter for sessions."""
    
    def get_entity_type(self) -> EntityType:
        return EntityType.SESSION
    
    def search(self, query: SearchQuery, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """Search sessions."""
        results = []
        query_lower = query.query.lower()
        
        # Build base query
        base_query = """
            SELECT id, session_id, developer, start_time, end_time, metadata,
                   created_at, updated_at, project_id
            FROM sessions 
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        sql_query, params = self.apply_filters(base_query, params, filters)
        
        # Add text search conditions
        search_conditions = []
        search_params = []
        
        if query.exact_match:
            search_conditions.append("(developer LIKE ? OR metadata LIKE ?)")
            search_params.extend([f"%{query.query}%", f"%{query.query}%"])
        else:
            query_words = query.query.split()
            for word in query_words:
                search_conditions.append("(developer LIKE ? OR metadata LIKE ?)")
                search_params.extend([f"%{word}%", f"%{word}%"])
        
        if search_conditions:
            sql_query += " AND (" + " OR ".join(search_conditions) + ")"
            params.extend(search_params)
        
        # Add ordering and limit
        sql_query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        try:
            with self.db_service.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            for row in rows:
                # Calculate relevance
                matched_fields = []
                relevance = 0.0
                
                # Check developer match
                if query_lower in (row['developer'] or "").lower():
                    matched_fields.append('developer')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['developer'], ['developer']))
                
                # Check metadata match
                if row['metadata'] and query_lower in row['metadata'].lower():
                    matched_fields.append('metadata')
                    relevance = max(relevance, self.calculate_relevance(query.query, row['metadata'], ['metadata']))
                
                # Skip if below minimum relevance
                if relevance < (filters.min_relevance if filters else 0.0):
                    continue
                
                # Create excerpt
                content = row['metadata'] or f"Session by {row['developer']}"
                excerpt = self.create_excerpt(content, query.query)
                
                results.append(SearchResult(
                    id=row['id'],
                    entity_type=EntityType.SESSION,
                    entity_id=row['id'],
                    result_type=SearchResultType.SESSION,
                    title=f"Session: {row['developer']}",
                    content=content,
                    excerpt=excerpt,
                    relevance_score=relevance,
                    match_type="text_match",
                    matched_fields=matched_fields,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    created_by=row['developer'],
                    project_id=row['project_id'],
                    metadata={'session_id': row['session_id'], 'start_time': row['start_time'], 'end_time': row['end_time']},
                    search_query=query.query
                ))
        
        except Exception as e:
            print(f"Session search error: {e}")
        
        return results
    
    def index_entity(self, entity_id: int) -> bool:
        return True
    
    def reindex_all(self) -> int:
        return 0


# Registry of all search adapters
SEARCH_ADAPTERS = {
    EntityType.WORK_ITEM: WorkItemSearchAdapter,
    EntityType.TASK: TaskSearchAdapter,
    EntityType.IDEA: IdeaSearchAdapter,
    EntityType.DOCUMENT: DocumentSearchAdapter,
    EntityType.SUMMARY: SummarySearchAdapter,
    EntityType.EVIDENCE: EvidenceSearchAdapter,
    EntityType.SESSION: SessionSearchAdapter,
    EntityType.LEARNING: LearningSearchAdapter,
}

__all__ = [
    'BaseSearchAdapter',
    'WorkItemSearchAdapter',
    'TaskSearchAdapter',
    'IdeaSearchAdapter',
    'DocumentSearchAdapter',
    'SummarySearchAdapter',
    'EvidenceSearchAdapter',
    'LearningSearchAdapter',
    'SessionSearchAdapter',
    'SEARCH_ADAPTERS'
]
