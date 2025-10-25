"""
Search Metrics Adapter

Database adapter for SearchMetrics model following APM (Agent Project Manager) patterns.
"""

from typing import Optional, List, Dict, Any
import json
import sqlite3

from ..models.search_metrics import SearchMetrics
from .base_adapter import BaseAdapter


class SearchMetricsAdapter(BaseAdapter[SearchMetrics]):
    """Database adapter for SearchMetrics model."""

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> SearchMetrics:
        """Create SearchMetrics from database row."""
        return SearchMetrics(
            id=row.get('id'),
            project_id=row['project_id'],
            total_queries=row['total_queries'],
            avg_query_time_ms=row['avg_query_time_ms'],
            avg_results_per_query=row['avg_results_per_query'],
            avg_relevance_score=row['avg_relevance_score'],
            high_relevance_ratio=row['high_relevance_ratio'],
            zero_result_ratio=row['zero_result_ratio'],
            cache_hit_ratio=row['cache_hit_ratio'],
            index_size_mb=row['index_size_mb'],
            memory_usage_mb=row['memory_usage_mb'],
            most_common_queries=cls._parse_json_list(row.get('most_common_queries', '[]')),
            entity_type_distribution=cls._parse_json_dict(row.get('entity_type_distribution', '{}')),
            search_mode_distribution=cls._parse_json_dict(row.get('search_mode_distribution', '{}')),
            metrics_period_start=cls._parse_datetime(row['metrics_period_start']),
            metrics_period_end=cls._parse_datetime(row['metrics_period_end']),
            created_at=cls._parse_datetime(row.get('created_at')),
            updated_at=cls._parse_datetime(row.get('updated_at'))
        )

    @classmethod
    def to_row(cls, model: SearchMetrics) -> Dict[str, Any]:
        """Convert SearchMetrics to database row."""
        return {
            'id': model.id,
            'project_id': model.project_id,
            'total_queries': model.total_queries,
            'avg_query_time_ms': model.avg_query_time_ms,
            'avg_results_per_query': model.avg_results_per_query,
            'avg_relevance_score': model.avg_relevance_score,
            'high_relevance_ratio': model.high_relevance_ratio,
            'zero_result_ratio': model.zero_result_ratio,
            'cache_hit_ratio': model.cache_hit_ratio,
            'index_size_mb': model.index_size_mb,
            'memory_usage_mb': model.memory_usage_mb,
            'most_common_queries': cls._format_json_list(model.most_common_queries),
            'entity_type_distribution': cls._format_json_dict(model.entity_type_distribution),
            'search_mode_distribution': cls._format_json_dict(model.search_mode_distribution),
            'metrics_period_start': cls._format_datetime(model.metrics_period_start),
            'metrics_period_end': cls._format_datetime(model.metrics_period_end),
            'created_at': cls._format_datetime(model.created_at),
            'updated_at': cls._format_datetime(model.updated_at)
        }

    @classmethod
    def get_table_name(cls) -> str:
        """Get database table name."""
        return 'search_metrics'

    @classmethod
    def get_create_table_sql(cls) -> str:
        """Get SQL to create the search_metrics table."""
        return """
        CREATE TABLE IF NOT EXISTS search_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            total_queries INTEGER NOT NULL DEFAULT 0,
            avg_query_time_ms REAL NOT NULL DEFAULT 0.0,
            avg_results_per_query REAL NOT NULL DEFAULT 0.0,
            avg_relevance_score REAL NOT NULL DEFAULT 0.0,
            high_relevance_ratio REAL NOT NULL DEFAULT 0.0,
            zero_result_ratio REAL NOT NULL DEFAULT 0.0,
            cache_hit_ratio REAL NOT NULL DEFAULT 0.0,
            index_size_mb REAL NOT NULL DEFAULT 0.0,
            memory_usage_mb REAL NOT NULL DEFAULT 0.0,
            most_common_queries TEXT NOT NULL DEFAULT '[]',
            entity_type_distribution TEXT NOT NULL DEFAULT '{}',
            search_mode_distribution TEXT NOT NULL DEFAULT '{}',
            metrics_period_start DATETIME NOT NULL,
            metrics_period_end DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
        """

    @classmethod
    def get_indexes_sql(cls) -> List[str]:
        """Get SQL to create indexes."""
        return [
            "CREATE INDEX IF NOT EXISTS idx_search_metrics_project_id ON search_metrics(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_search_metrics_period ON search_metrics(metrics_period_start, metrics_period_end)"
        ]

    @classmethod
    def _parse_json_list(cls, json_str: str) -> List[tuple]:
        """Parse JSON string to list of tuples."""
        try:
            data = json.loads(json_str)
            return [tuple(item) if isinstance(item, list) else item for item in data]
        except (json.JSONDecodeError, TypeError):
            return []

    @classmethod
    def _format_json_list(cls, data: List[tuple]) -> str:
        """Format list of tuples to JSON string."""
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            return '[]'

    @classmethod
    def _parse_json_dict(cls, json_str: str) -> Dict[str, Any]:
        """Parse JSON string to dictionary."""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return {}

    @classmethod
    def _format_json_dict(cls, data: Dict[str, Any]) -> str:
        """Format dictionary to JSON string."""
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            return '{}'
