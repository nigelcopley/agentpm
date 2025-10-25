"""
Work Item Summary Adapter - Type Conversion

Converts between Pydantic WorkItemSummary model and SQLite database format.

Pattern: Two-way conversion
- to_db(): Pydantic model → SQLite dict (JSON serialization)
- from_db(): SQLite row → Pydantic model (JSON deserialization)
"""

import json
from typing import Dict, Any
from datetime import datetime

from ..models.work_item_summary import WorkItemSummary


class WorkItemSummaryAdapter:
    """Adapter for WorkItemSummary model ↔ database conversion"""

    @staticmethod
    def to_db(summary: WorkItemSummary) -> Dict[str, Any]:
        """
        Convert Pydantic model to database format.

        Args:
            summary: WorkItemSummary model

        Returns:
            Dictionary ready for SQLite insertion

        Note:
            - context_metadata serialized to JSON string
            - created_at handled by database DEFAULT
        """
        return {
            'id': summary.id,
            'work_item_id': summary.work_item_id,
            'session_date': summary.session_date,
            'session_duration_hours': summary.session_duration_hours,
            'summary_text': summary.summary_text,
            'context_metadata': json.dumps(summary.context_metadata) if summary.context_metadata else None,
            'created_by': summary.created_by,
            'summary_type': summary.summary_type,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> WorkItemSummary:
        """
        Convert database row to Pydantic model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated WorkItemSummary model

        Note:
            - Handles double-encoded JSON (like TaskAdapter)
            - context_metadata deserialized from JSON string
        """
        # Parse context_metadata - handle both string (from DB) and dict (from memory)
        metadata = row.get('context_metadata')
        if metadata:
            if isinstance(metadata, str):
                # Parse JSON - handle double-encoding if present
                metadata = json.loads(metadata)
                # If still a string after first parse, parse again (double-encoded)
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
            # else: already a dict, use as-is
        else:
            metadata = None

        return WorkItemSummary(
            id=row.get('id'),
            work_item_id=row['work_item_id'],
            session_date=row['session_date'],
            session_duration_hours=row.get('session_duration_hours'),
            summary_text=row['summary_text'],
            context_metadata=metadata,
            created_at=_parse_datetime(row.get('created_at')),
            created_by=row.get('created_by'),
            summary_type=row.get('summary_type', 'session'),
        )


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from database value"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None
