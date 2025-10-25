"""
Search Index Adapter

Database adapter for SearchIndex model following APM (Agent Project Manager) patterns.
"""

from typing import Optional, List, Dict, Any
import sqlite3

from ..models.search_index import SearchIndex
from ..enums import EntityType
from .base_adapter import BaseAdapter


class SearchIndexAdapter(BaseAdapter[SearchIndex]):
    """Database adapter for SearchIndex model."""

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> SearchIndex:
        """Create SearchIndex from database row."""
        return SearchIndex(
            id=row.get('id'),
            entity_type=EntityType(row['entity_type']),
            index_version=row['index_version'],
            total_documents=row['total_documents'],
            last_updated=cls._parse_datetime(row['last_updated']),
            index_size_bytes=row['index_size_bytes'],
            avg_document_size=row['avg_document_size'],
            unique_terms=row['unique_terms'],
            total_terms=row['total_terms'],
            build_time_ms=row['build_time_ms'],
            query_time_ms=row['query_time_ms'],
            created_at=cls._parse_datetime(row.get('created_at')),
            updated_at=cls._parse_datetime(row.get('updated_at'))
        )

    @classmethod
    def to_row(cls, model: SearchIndex) -> Dict[str, Any]:
        """Convert SearchIndex to database row."""
        return {
            'id': model.id,
            'entity_type': model.entity_type.value,
            'index_version': model.index_version,
            'total_documents': model.total_documents,
            'last_updated': cls._format_datetime(model.last_updated),
            'index_size_bytes': model.index_size_bytes,
            'avg_document_size': model.avg_document_size,
            'unique_terms': model.unique_terms,
            'total_terms': model.total_terms,
            'build_time_ms': model.build_time_ms,
            'query_time_ms': model.query_time_ms,
            'created_at': cls._format_datetime(model.created_at),
            'updated_at': cls._format_datetime(model.updated_at)
        }

    @classmethod
    def get_table_name(cls) -> str:
        """Get database table name."""
        return 'search_indexes'

    @classmethod
    def get_create_table_sql(cls) -> str:
        """Get SQL to create the search_indexes table."""
        return """
        CREATE TABLE IF NOT EXISTS search_indexes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            index_version TEXT NOT NULL,
            total_documents INTEGER NOT NULL DEFAULT 0,
            last_updated DATETIME NOT NULL,
            index_size_bytes INTEGER NOT NULL DEFAULT 0,
            avg_document_size REAL NOT NULL DEFAULT 0.0,
            unique_terms INTEGER NOT NULL DEFAULT 0,
            total_terms INTEGER NOT NULL DEFAULT 0,
            build_time_ms REAL NOT NULL DEFAULT 0.0,
            query_time_ms REAL NOT NULL DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type)
        )
        """

    @classmethod
    def get_indexes_sql(cls) -> List[str]:
        """Get SQL to create indexes."""
        return [
            "CREATE INDEX IF NOT EXISTS idx_search_indexes_entity_type ON search_indexes(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_search_indexes_last_updated ON search_indexes(last_updated)"
        ]
