"""
Event Adapter - Model ↔ Database Conversion

Handles conversion between Event domain models and database rows.

Migration: 0011 (events table)
"""

import json
from typing import Dict, Any
from datetime import datetime

from ..models.event import Event, EventType, EventCategory, EventSeverity


class EventAdapter:
    """Handles Event model <-> Database row conversions"""

    @staticmethod
    def to_db(event: Event) -> Dict[str, Any]:
        """
        Convert Event model to database row format.

        Note: After Migration 0023, session_events table supports all 38 EventType values.
        No lossy mapping required - event types preserved with full fidelity.

        Args:
            event: Event domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'project_id': event.project_id or 0,  # Required NOT NULL
            'event_type': event.event_type.value,  # Direct mapping (no loss after migration 0023)
            'event_category': event.event_category.value,
            'event_severity': event.event_severity.value,
            'session_id': event.session_id,
            'timestamp': event.timestamp.isoformat(),
            'source': event.source,
            'event_data': json.dumps(event.event_data) if event.event_data else '{}',
            'work_item_id': event.work_item_id,
            'task_id': event.task_id,
            'created_at': event.created_at.isoformat() if event.created_at else None,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Event:
        """
        Convert database row to Event model.

        Note: After Migration 0023, session_events table has all EventType values.
        Direct reconstruction with no data loss.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Event model
        """
        # Parse event_data JSON
        event_data_raw = row.get('event_data', '{}')
        event_data = json.loads(event_data_raw) if event_data_raw else {}

        return Event(
            id=row.get('id'),
            event_type=EventType(row['event_type']),  # Direct from database (after migration 0023)
            event_category=EventCategory(row['event_category']),
            event_severity=EventSeverity(row['event_severity']),
            session_id=row['session_id'],
            timestamp=_parse_datetime(row['timestamp']),
            source=row['source'],
            event_data=event_data,
            project_id=row.get('project_id'),
            work_item_id=row.get('work_item_id'),
            task_id=row.get('task_id'),
            created_at=_parse_datetime(row.get('created_at')),
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
