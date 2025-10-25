"""
Search Index Database Methods

Database operations for SearchIndex model following APM (Agent Project Manager) patterns.
"""

from typing import Optional, List
import sqlite3

from ..service import DatabaseService
from ..models.search_index import SearchIndex
from ..adapters.search_index_adapter import SearchIndexAdapter
from ..enums import EntityType


def create_search_index(service: DatabaseService, search_index: SearchIndex) -> SearchIndex:
    """
    Create a new search index record.
    
    Args:
        service: DatabaseService instance
        search_index: SearchIndex model to create
        
    Returns:
        Created SearchIndex with ID set
    """
    adapter = SearchIndexAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"""
            INSERT INTO {adapter.get_table_name()} (
                entity_type, index_version, total_documents, last_updated,
                index_size_bytes, avg_document_size, unique_terms, total_terms,
                build_time_ms, query_time_ms, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                search_index.entity_type.value,
                search_index.index_version,
                search_index.total_documents,
                adapter._format_datetime(search_index.last_updated),
                search_index.index_size_bytes,
                search_index.avg_document_size,
                search_index.unique_terms,
                search_index.total_terms,
                search_index.build_time_ms,
                search_index.query_time_ms,
                adapter._format_datetime(search_index.created_at),
                adapter._format_datetime(search_index.updated_at)
            )
        )
        
        search_index.id = cursor.lastrowid
        return search_index


def get_search_index(service: DatabaseService, index_id: int) -> Optional[SearchIndex]:
    """
    Get search index by ID.
    
    Args:
        service: DatabaseService instance
        index_id: Search index ID
        
    Returns:
        SearchIndex model or None if not found
    """
    adapter = SearchIndexAdapter()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"SELECT * FROM {adapter.get_table_name()} WHERE id = ?",
            (index_id,)
        )
        row = cursor.fetchone()
    
    if not row:
        return None
    
    return adapter.from_row(dict(row))


def get_search_index_by_entity_type(service: DatabaseService, entity_type: EntityType) -> Optional[SearchIndex]:
    """
    Get search index by entity type.
    
    Args:
        service: DatabaseService instance
        entity_type: Entity type
        
    Returns:
        SearchIndex model or None if not found
    """
    adapter = SearchIndexAdapter()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"SELECT * FROM {adapter.get_table_name()} WHERE entity_type = ?",
            (entity_type.value,)
        )
        row = cursor.fetchone()
    
    if not row:
        return None
    
    return adapter.from_row(dict(row))


def list_search_indexes(service: DatabaseService) -> List[SearchIndex]:
    """
    List all search indexes.
    
    Args:
        service: DatabaseService instance
        
    Returns:
        List of SearchIndex models
    """
    adapter = SearchIndexAdapter()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(f"SELECT * FROM {adapter.get_table_name()} ORDER BY entity_type")
        rows = cursor.fetchall()
    
    return [adapter.from_row(dict(row)) for row in rows]


def update_search_index(service: DatabaseService, search_index: SearchIndex) -> SearchIndex:
    """
    Update an existing search index.
    
    Args:
        service: DatabaseService instance
        search_index: SearchIndex model to update
        
    Returns:
        Updated SearchIndex model
    """
    adapter = SearchIndexAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"""
            UPDATE {adapter.get_table_name()} SET
                entity_type = ?, index_version = ?, total_documents = ?,
                last_updated = ?, index_size_bytes = ?, avg_document_size = ?,
                unique_terms = ?, total_terms = ?, build_time_ms = ?,
                query_time_ms = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                search_index.entity_type.value,
                search_index.index_version,
                search_index.total_documents,
                adapter._format_datetime(search_index.last_updated),
                search_index.index_size_bytes,
                search_index.avg_document_size,
                search_index.unique_terms,
                search_index.total_terms,
                search_index.build_time_ms,
                search_index.query_time_ms,
                adapter._format_datetime(search_index.updated_at),
                search_index.id
            )
        )
        
        if cursor.rowcount == 0:
            raise ValueError(f"Search index with ID {search_index.id} not found")
        
        return search_index


def delete_search_index(service: DatabaseService, index_id: int) -> bool:
    """
    Delete a search index.
    
    Args:
        service: DatabaseService instance
        index_id: Search index ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    adapter = SearchIndexAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"DELETE FROM {adapter.get_table_name()} WHERE id = ?",
            (index_id,)
        )
        
        return cursor.rowcount > 0


def upsert_search_index(service: DatabaseService, search_index: SearchIndex) -> SearchIndex:
    """
    Insert or update search index (upsert operation).
    
    Args:
        service: DatabaseService instance
        search_index: SearchIndex model to upsert
        
    Returns:
        Upserted SearchIndex model
    """
    adapter = SearchIndexAdapter()
    
    with service.transaction() as conn:
        # Try to update first
        cursor = conn.execute(
            f"""
            UPDATE {adapter.get_table_name()} SET
                index_version = ?, total_documents = ?, last_updated = ?,
                index_size_bytes = ?, avg_document_size = ?, unique_terms = ?,
                total_terms = ?, build_time_ms = ?, query_time_ms = ?,
                updated_at = ?
            WHERE entity_type = ?
            """,
            (
                search_index.index_version,
                search_index.total_documents,
                adapter._format_datetime(search_index.last_updated),
                search_index.index_size_bytes,
                search_index.avg_document_size,
                search_index.unique_terms,
                search_index.total_terms,
                search_index.build_time_ms,
                search_index.query_time_ms,
                adapter._format_datetime(search_index.updated_at),
                search_index.entity_type.value
            )
        )
        
        if cursor.rowcount > 0:
            # Update successful, get the updated record
            cursor = conn.execute(
                f"SELECT * FROM {adapter.get_table_name()} WHERE entity_type = ?",
                (search_index.entity_type.value,)
            )
            row = cursor.fetchone()
            return adapter.from_row(dict(row))
        else:
            # No update, insert new record
            cursor = conn.execute(
                f"""
                INSERT INTO {adapter.get_table_name()} (
                    entity_type, index_version, total_documents, last_updated,
                    index_size_bytes, avg_document_size, unique_terms, total_terms,
                    build_time_ms, query_time_ms, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    search_index.entity_type.value,
                    search_index.index_version,
                    search_index.total_documents,
                    adapter._format_datetime(search_index.last_updated),
                    search_index.index_size_bytes,
                    search_index.avg_document_size,
                    search_index.unique_terms,
                    search_index.total_terms,
                    search_index.build_time_ms,
                    search_index.query_time_ms,
                    adapter._format_datetime(search_index.created_at),
                    adapter._format_datetime(search_index.updated_at)
                )
            )
            
            search_index.id = cursor.lastrowid
            return search_index
