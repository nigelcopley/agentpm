"""
Base Adapter

Base class for all database adapters following APM (Agent Project Manager) patterns.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, List, Optional
from datetime import datetime
import sqlite3

T = TypeVar('T')


class BaseAdapter(ABC, Generic[T]):
    """Base class for all database adapters."""

    @classmethod
    @abstractmethod
    def from_row(cls, row: Dict[str, Any]) -> T:
        """Create model from database row."""
        pass

    @classmethod
    @abstractmethod
    def to_row(cls, model: T) -> Dict[str, Any]:
        """Convert model to database row."""
        pass

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        """Get database table name."""
        pass

    @classmethod
    @abstractmethod
    def get_create_table_sql(cls) -> str:
        """Get SQL to create the table."""
        pass

    @classmethod
    def get_indexes_sql(cls) -> List[str]:
        """Get SQL to create indexes (optional)."""
        return []

    @classmethod
    def _parse_datetime(cls, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from database."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    @classmethod
    def _format_datetime(cls, dt: Optional[datetime]) -> Optional[str]:
        """Format datetime for database storage."""
        if not dt:
            return None
        return dt.isoformat()

    @classmethod
    def _parse_json(cls, json_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse JSON string from database."""
        if not json_str:
            return None
        try:
            import json
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None

    @classmethod
    def _format_json(cls, data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Format data as JSON string for database."""
        if not data:
            return None
        try:
            import json
            return json.dumps(data)
        except (TypeError, ValueError):
            return None
