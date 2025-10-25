"""
Search Metrics Database Methods

Database operations for SearchMetrics model following APM (Agent Project Manager) patterns.
"""

from typing import Optional, List
import sqlite3
import json

from ..service import DatabaseService
from ..models.search_metrics import SearchMetrics
from ..adapters.search_metrics_adapter import SearchMetricsAdapter


def create_search_metrics(service: DatabaseService, search_metrics: SearchMetrics) -> SearchMetrics:
    """
    Create a new search metrics record.
    
    Args:
        service: DatabaseService instance
        search_metrics: SearchMetrics model to create
        
    Returns:
        Created SearchMetrics with ID set
    """
    adapter = SearchMetricsAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"""
            INSERT INTO {adapter.get_table_name()} (
                project_id, total_queries, avg_query_time_ms, avg_results_per_query,
                avg_relevance_score, high_relevance_ratio, zero_result_ratio,
                cache_hit_ratio, index_size_mb, memory_usage_mb,
                most_common_queries, entity_type_distribution, search_mode_distribution,
                metrics_period_start, metrics_period_end, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                search_metrics.project_id,
                search_metrics.total_queries,
                search_metrics.avg_query_time_ms,
                search_metrics.avg_results_per_query,
                search_metrics.avg_relevance_score,
                search_metrics.high_relevance_ratio,
                search_metrics.zero_result_ratio,
                search_metrics.cache_hit_ratio,
                search_metrics.index_size_mb,
                search_metrics.memory_usage_mb,
                adapter._format_json_list(search_metrics.most_common_queries),
                adapter._format_json_dict(search_metrics.entity_type_distribution),
                adapter._format_json_dict(search_metrics.search_mode_distribution),
                adapter._format_datetime(search_metrics.metrics_period_start),
                adapter._format_datetime(search_metrics.metrics_period_end),
                adapter._format_datetime(search_metrics.created_at),
                adapter._format_datetime(search_metrics.updated_at)
            )
        )
        
        search_metrics.id = cursor.lastrowid
        return search_metrics


def get_search_metrics(service: DatabaseService, metrics_id: int) -> Optional[SearchMetrics]:
    """
    Get search metrics by ID.
    
    Args:
        service: DatabaseService instance
        metrics_id: Search metrics ID
        
    Returns:
        SearchMetrics model or None if not found
    """
    adapter = SearchMetricsAdapter()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"SELECT * FROM {adapter.get_table_name()} WHERE id = ?",
            (metrics_id,)
        )
        row = cursor.fetchone()
    
    if not row:
        return None
    
    return adapter.from_row(dict(row))


def get_search_metrics_by_project(service: DatabaseService, project_id: int) -> Optional[SearchMetrics]:
    """
    Get search metrics by project ID.
    
    Args:
        service: DatabaseService instance
        project_id: Project ID
        
    Returns:
        SearchMetrics model or None if not found
    """
    adapter = SearchMetricsAdapter()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"SELECT * FROM {adapter.get_table_name()} WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,)
        )
        row = cursor.fetchone()
    
    if not row:
        return None
    
    return adapter.from_row(dict(row))


def list_search_metrics(service: DatabaseService, project_id: Optional[int] = None) -> List[SearchMetrics]:
    """
    List search metrics, optionally filtered by project.
    
    Args:
        service: DatabaseService instance
        project_id: Optional project ID filter
        
    Returns:
        List of SearchMetrics models
    """
    adapter = SearchMetricsAdapter()
    
    query = f"SELECT * FROM {adapter.get_table_name()}"
    params = []
    
    if project_id:
        query += " WHERE project_id = ?"
        params.append(project_id)
    
    query += " ORDER BY created_at DESC"
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    return [adapter.from_row(dict(row)) for row in rows]


def update_search_metrics(service: DatabaseService, search_metrics: SearchMetrics) -> SearchMetrics:
    """
    Update an existing search metrics record.
    
    Args:
        service: DatabaseService instance
        search_metrics: SearchMetrics model to update
        
    Returns:
        Updated SearchMetrics model
    """
    adapter = SearchMetricsAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"""
            UPDATE {adapter.get_table_name()} SET
                project_id = ?, total_queries = ?, avg_query_time_ms = ?,
                avg_results_per_query = ?, avg_relevance_score = ?,
                high_relevance_ratio = ?, zero_result_ratio = ?, cache_hit_ratio = ?,
                index_size_mb = ?, memory_usage_mb = ?, most_common_queries = ?,
                entity_type_distribution = ?, search_mode_distribution = ?,
                metrics_period_start = ?, metrics_period_end = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                search_metrics.project_id,
                search_metrics.total_queries,
                search_metrics.avg_query_time_ms,
                search_metrics.avg_results_per_query,
                search_metrics.avg_relevance_score,
                search_metrics.high_relevance_ratio,
                search_metrics.zero_result_ratio,
                search_metrics.cache_hit_ratio,
                search_metrics.index_size_mb,
                search_metrics.memory_usage_mb,
                adapter._format_json_list(search_metrics.most_common_queries),
                adapter._format_json_dict(search_metrics.entity_type_distribution),
                adapter._format_json_dict(search_metrics.search_mode_distribution),
                adapter._format_datetime(search_metrics.metrics_period_start),
                adapter._format_datetime(search_metrics.metrics_period_end),
                adapter._format_datetime(search_metrics.updated_at),
                search_metrics.id
            )
        )
        
        if cursor.rowcount == 0:
            raise ValueError(f"Search metrics with ID {search_metrics.id} not found")
        
        return search_metrics


def delete_search_metrics(service: DatabaseService, metrics_id: int) -> bool:
    """
    Delete search metrics.
    
    Args:
        service: DatabaseService instance
        metrics_id: Search metrics ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    adapter = SearchMetricsAdapter()
    
    with service.transaction() as conn:
        cursor = conn.execute(
            f"DELETE FROM {adapter.get_table_name()} WHERE id = ?",
            (metrics_id,)
        )
        
        return cursor.rowcount > 0


def upsert_search_metrics(service: DatabaseService, search_metrics: SearchMetrics) -> SearchMetrics:
    """
    Insert or update search metrics (upsert operation).
    
    Args:
        service: DatabaseService instance
        search_metrics: SearchMetrics model to upsert
        
    Returns:
        Upserted SearchMetrics model
    """
    adapter = SearchMetricsAdapter()
    
    with service.transaction() as conn:
        # Try to update first
        cursor = conn.execute(
            f"""
            UPDATE {adapter.get_table_name()} SET
                total_queries = ?, avg_query_time_ms = ?, avg_results_per_query = ?,
                avg_relevance_score = ?, high_relevance_ratio = ?, zero_result_ratio = ?,
                cache_hit_ratio = ?, index_size_mb = ?, memory_usage_mb = ?,
                most_common_queries = ?, entity_type_distribution = ?,
                search_mode_distribution = ?, metrics_period_start = ?,
                metrics_period_end = ?, updated_at = ?
            WHERE project_id = ?
            """,
            (
                search_metrics.total_queries,
                search_metrics.avg_query_time_ms,
                search_metrics.avg_results_per_query,
                search_metrics.avg_relevance_score,
                search_metrics.high_relevance_ratio,
                search_metrics.zero_result_ratio,
                search_metrics.cache_hit_ratio,
                search_metrics.index_size_mb,
                search_metrics.memory_usage_mb,
                adapter._format_json_list(search_metrics.most_common_queries),
                adapter._format_json_dict(search_metrics.entity_type_distribution),
                adapter._format_json_dict(search_metrics.search_mode_distribution),
                adapter._format_datetime(search_metrics.metrics_period_start),
                adapter._format_datetime(search_metrics.metrics_period_end),
                adapter._format_datetime(search_metrics.updated_at),
                search_metrics.project_id
            )
        )
        
        if cursor.rowcount > 0:
            # Update successful, get the updated record
            cursor = conn.execute(
                f"SELECT * FROM {adapter.get_table_name()} WHERE project_id = ?",
                (search_metrics.project_id,)
            )
            row = cursor.fetchone()
            return adapter.from_row(dict(row))
        else:
            # No update, insert new record
            cursor = conn.execute(
                f"""
                INSERT INTO {adapter.get_table_name()} (
                    project_id, total_queries, avg_query_time_ms, avg_results_per_query,
                    avg_relevance_score, high_relevance_ratio, zero_result_ratio,
                    cache_hit_ratio, index_size_mb, memory_usage_mb,
                    most_common_queries, entity_type_distribution, search_mode_distribution,
                    metrics_period_start, metrics_period_end, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    search_metrics.project_id,
                    search_metrics.total_queries,
                    search_metrics.avg_query_time_ms,
                    search_metrics.avg_results_per_query,
                    search_metrics.avg_relevance_score,
                    search_metrics.high_relevance_ratio,
                    search_metrics.zero_result_ratio,
                    search_metrics.cache_hit_ratio,
                    search_metrics.index_size_mb,
                    search_metrics.memory_usage_mb,
                    adapter._format_json_list(search_metrics.most_common_queries),
                    adapter._format_json_dict(search_metrics.entity_type_distribution),
                    adapter._format_json_dict(search_metrics.search_mode_distribution),
                    adapter._format_datetime(search_metrics.metrics_period_start),
                    adapter._format_datetime(search_metrics.metrics_period_end),
                    adapter._format_datetime(search_metrics.created_at),
                    adapter._format_datetime(search_metrics.updated_at)
                )
            )
            
            search_metrics.id = cursor.lastrowid
            return search_metrics
