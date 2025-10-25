"""
Search Methods

Core search algorithms, indexing, and ranking functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import time
import re
import sqlite3
from collections import defaultdict, Counter

from ..database.service import DatabaseService
from ..database.enums import EntityType
from ..database.models.search_result import SearchResult, SearchResults
from .models import SearchQuery, SearchFilter, SearchConfig
from ..database.models import SearchIndex, SearchMetrics


class TextSearchEngine:
    """Text-based search engine with relevance scoring."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'can', 'only', 'other',
            'new', 'some', 'could', 'these', 'may', 'say', 'use', 'her',
            'than', 'first', 'been', 'call', 'who', 'oil', 'sit', 'now',
            'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made',
            'may', 'part'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter out stop words
        words = [word for word in text.split() if word not in self.stop_words and len(word) > 2]
        
        return words
    
    def calculate_tf_idf(self, term: str, document: str, corpus: List[str]) -> float:
        """
        Calculate TF-IDF score for a term in a document.
        
        Args:
            term: Search term
            document: Document text
            corpus: All documents in the corpus
            
        Returns:
            TF-IDF score
        """
        # Term frequency in document
        doc_words = self.tokenize(document)
        tf = doc_words.count(term.lower()) / len(doc_words) if doc_words else 0
        
        # Document frequency in corpus
        doc_freq = sum(1 for doc in corpus if term.lower() in self.tokenize(doc))
        idf = 1.0 if doc_freq == 0 else len(corpus) / doc_freq
        
        return tf * idf
    
    def calculate_relevance(self, query: str, text: str, field_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate relevance score between query and text.
        
        Args:
            query: Search query
            text: Text to match against
            field_weights: Optional field-specific weights
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not query or not text:
            return 0.0
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Exact match gets highest score
        if query_lower in text_lower:
            base_score = 1.0
        else:
            # Calculate word overlap
            query_words = set(self.tokenize(query))
            text_words = set(self.tokenize(text))
            
            if not query_words:
                return 0.0
            
            # Jaccard similarity
            intersection = len(query_words.intersection(text_words))
            union = len(query_words.union(text_words))
            base_score = intersection / union if union > 0 else 0.0
        
        # Apply field weights if provided
        if field_weights:
            field_weight = field_weights.get('default', 1.0)
            base_score *= field_weight
        
        return min(1.0, base_score)
    
    def highlight_matches(self, text: str, query: str, max_length: int = 200) -> str:
        """
        Create highlighted excerpt from text.
        
        Args:
            text: Full text
            query: Search query
            max_length: Maximum excerpt length
            
        Returns:
            Highlighted excerpt
        """
        if not text or not query:
            return text[:max_length] if text else ""
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find query position
        query_pos = text_lower.find(query_lower)
        if query_pos == -1:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Calculate excerpt boundaries
        start = max(0, query_pos - max_length // 2)
        end = min(len(text), start + max_length)
        
        # Adjust start to avoid cutting words
        if start > 0:
            while start < len(text) and text[start] not in ' \n\t':
                start += 1
        
        excerpt = text[start:end]
        
        # Highlight the query term
        excerpt = re.sub(
            re.escape(query),
            f"**{query}**",
            excerpt,
            flags=re.IGNORECASE
        )
        
        # Add ellipsis if needed
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        return excerpt


class MetadataSearchEngine:
    """Metadata-based search engine for structured data."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
    
    def search_by_tags(self, tags: List[str], entity_type: Optional[EntityType] = None) -> List[int]:
        """
        Search for entities by tags.
        
        Args:
            tags: List of tags to search for
            entity_type: Optional entity type filter
            
        Returns:
            List of entity IDs
        """
        # This would be implemented with proper tag indexing
        # For now, return empty list
        return []
    
    def search_by_status(self, status: str, entity_type: Optional[EntityType] = None) -> List[int]:
        """
        Search for entities by status.
        
        Args:
            status: Status to search for
            entity_type: Optional entity type filter
            
        Returns:
            List of entity IDs
        """
        # This would be implemented with proper status indexing
        # For now, return empty list
        return []
    
    def search_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        entity_type: Optional[EntityType] = None,
        date_field: str = 'created_at'
    ) -> List[int]:
        """
        Search for entities by date range.
        
        Args:
            start_date: Start date
            end_date: End date
            entity_type: Optional entity type filter
            date_field: Date field to search (created_at, updated_at)
            
        Returns:
            List of entity IDs
        """
        # This would be implemented with proper date indexing
        # For now, return empty list
        return []


class RelevanceCalculator:
    """Calculate and rank search result relevance."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.field_weights = {
            'title': 2.0,
            'name': 2.0,
            'description': 1.5,
            'summary': 1.5,
            'content': 1.0,
            'tags': 1.2,
            'metadata': 0.8
        }
    
    def calculate_field_relevance(
        self,
        query: str,
        field_value: str,
        field_name: str
    ) -> float:
        """
        Calculate relevance for a specific field.
        
        Args:
            query: Search query
            field_value: Field value to match
            field_name: Name of the field
            
        Returns:
            Relevance score for this field
        """
        if not field_value or not query:
            return 0.0
        
        # Get field weight
        weight = self.field_weights.get(field_name, 1.0)
        
        # Calculate base relevance
        query_lower = query.lower()
        field_lower = field_value.lower()
        
        # Exact match
        if query_lower == field_lower:
            return 1.0 * weight
        
        # Contains match
        if query_lower in field_lower:
            # Boost based on position (earlier is better)
            position = field_lower.find(query_lower)
            position_boost = 1.0 - (position / len(field_lower)) * 0.2
            return 0.9 * weight * position_boost
        
        # Word overlap
        query_words = set(query_lower.split())
        field_words = set(field_lower.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(field_words))
        word_score = overlap / len(query_words)
        
        return word_score * weight * 0.7
    
    def calculate_overall_relevance(
        self,
        query: str,
        matched_fields: Dict[str, str]
    ) -> float:
        """
        Calculate overall relevance score from multiple field matches.
        
        Args:
            query: Search query
            matched_fields: Dictionary of field_name -> field_value
            
        Returns:
            Overall relevance score
        """
        if not matched_fields:
            return 0.0
        
        field_scores = []
        for field_name, field_value in matched_fields.items():
            score = self.calculate_field_relevance(query, field_value, field_name)
            field_scores.append(score)
        
        # Use maximum score as base, with bonus for multiple matches
        max_score = max(field_scores) if field_scores else 0.0
        match_bonus = min(0.2, len(field_scores) * 0.05)  # Up to 20% bonus
        
        return min(1.0, max_score + match_bonus)
    
    def rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Rank search results by relevance and other factors.
        
        Args:
            results: List of search results
            
        Returns:
            Ranked list of search results
        """
        def sort_key(result: SearchResult) -> Tuple[float, datetime]:
            # Primary sort by relevance score (descending)
            # Secondary sort by creation date (descending)
            return (-result.relevance_score, result.created_at or datetime.min)
        
        return sorted(results, key=sort_key)


class SearchIndexer:
    """Search index management and maintenance."""
    
    def __init__(self, db_service: DatabaseService, config: SearchConfig):
        self.db_service = db_service
        self.config = config
        self.index_cache = {}
    
    def create_index(self, entity_type: EntityType) -> bool:
        """
        Create search index for an entity type.
        
        Args:
            entity_type: Entity type to index
            
        Returns:
            True if successful
        """
        try:
            # This would create proper search indexes
            # For now, just return True
            return True
        except Exception as e:
            print(f"Error creating index for {entity_type}: {e}")
            return False
    
    def update_index(self, entity_type: EntityType, entity_id: int) -> bool:
        """
        Update search index for a specific entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            True if successful
        """
        try:
            # This would update the search index
            # For now, just return True
            return True
        except Exception as e:
            print(f"Error updating index for {entity_type}#{entity_id}: {e}")
            return False
    
    def rebuild_index(self, entity_type: Optional[EntityType] = None) -> int:
        """
        Rebuild search index for entity type or all entities.
        
        Args:
            entity_type: Optional specific entity type
            
        Returns:
            Number of entities indexed
        """
        try:
            # This would rebuild the search index
            # For now, just return 0
            return 0
        except Exception as e:
            print(f"Error rebuilding index: {e}")
            return 0
    
    def get_index_stats(self, entity_type: EntityType) -> Optional[SearchIndex]:
        """
        Get index statistics for an entity type.
        
        Args:
            entity_type: Entity type
            
        Returns:
            Search index statistics
        """
        try:
            # This would return actual index statistics
            # For now, return a mock index
            return SearchIndex(
                entity_type=entity_type,
                index_version="1.0.0",
                total_documents=0,
                last_updated=datetime.now(),
                index_size_bytes=0,
                avg_document_size=0.0,
                unique_terms=0,
                total_terms=0,
                build_time_ms=0.0,
                query_time_ms=0.0
            )
        except Exception as e:
            print(f"Error getting index stats for {entity_type}: {e}")
            return None


class SearchRanker:
    """Advanced search result ranking and boosting."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.boost_factors = {
            'recency': 1.1,      # Recent content gets boost
            'popularity': 1.2,   # Popular content gets boost
            'completeness': 1.05, # Complete content gets boost
            'authority': 1.15    # Authoritative content gets boost
        }
    
    def apply_recency_boost(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Apply recency boost to search results.
        
        Args:
            results: List of search results
            
        Returns:
            Results with recency boost applied
        """
        if not results:
            return results
        
        # Find the most recent result
        max_date = max(
            (r.created_at for r in results if r.created_at),
            default=datetime.now()
        )
        
        for result in results:
            if result.created_at:
                # Calculate days since creation
                days_old = (max_date - result.created_at).days
                
                # Apply boost for recent content (within 30 days)
                if days_old <= 30:
                    boost = 1.0 + (30 - days_old) / 30 * 0.1  # Up to 10% boost
                    result.relevance_score = min(1.0, result.relevance_score * boost)
        
        return results
    
    def apply_popularity_boost(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Apply popularity boost to search results.
        
        Args:
            results: List of search results
            
        Returns:
            Results with popularity boost applied
        """
        # This would apply popularity boost based on views, votes, etc.
        # For now, just return results as-is
        return results
    
    def apply_completeness_boost(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Apply completeness boost to search results.
        
        Args:
            results: List of search results
            
        Returns:
            Results with completeness boost applied
        """
        for result in results:
            # Boost results with more complete information
            completeness_score = 0.0
            
            # Check for title
            if result.title and len(result.title.strip()) > 0:
                completeness_score += 0.3
            
            # Check for content
            if result.content and len(result.content.strip()) > 0:
                completeness_score += 0.4
            
            # Check for tags
            if result.tags and len(result.tags) > 0:
                completeness_score += 0.2
            
            # Check for metadata
            if result.metadata and len(result.metadata) > 0:
                completeness_score += 0.1
            
            # Apply boost
            if completeness_score > 0.8:
                boost = 1.0 + (completeness_score - 0.8) * 0.5  # Up to 10% boost
                result.relevance_score = min(1.0, result.relevance_score * boost)
        
        return results
    
    def rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Apply all ranking boosts and sort results.
        
        Args:
            results: List of search results
            
        Returns:
            Ranked and boosted results
        """
        if not results:
            return results
        
        # Apply various boosts
        results = self.apply_recency_boost(results)
        results = self.apply_popularity_boost(results)
        results = self.apply_completeness_boost(results)
        
        # Sort by final relevance score
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results


__all__ = [
    'TextSearchEngine',
    'MetadataSearchEngine',
    'RelevanceCalculator',
    'SearchIndexer',
    'SearchRanker'
]
