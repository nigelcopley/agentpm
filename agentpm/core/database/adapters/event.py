"""Event Adapter - Model ↔ Database Conversion

Handles conversion between Event domain models and database rows.
Part of the three-layer pattern:
- Layer 1: Pydantic models (validation)
- Layer 2: Adapters (conversion) ← THIS FILE
- Layer 3: Methods (CRUD operations)

Design:
- to_db(): Event → Dict (for INSERT/UPDATE)
- from_db(): Dict → Event (from SELECT)
- JSON serialization for event_data field
"""

import json
from datetime import datetime
from typing import Any, Dict

from ..models.event import Event, EventType, EventCategory, EventSeverity


class EventAdapter:
    """Handles Event model <-> Database row conversions"""

    @staticmethod
    def to_db(event: Event) -> Dict[str, Any]:
        """Convert Event model to database row format.

        Args:
            event: Event domain model

        Returns:
            Dictionary ready for database insertion/update

        Example:
            >>> event = Event(event_type=EventType.TASK_STARTED, ...)
            >>> data = EventAdapter.to_db(event)
            >>> cursor.execute("INSERT INTO session_events (...) VALUES (...)", tuple(data.values()))
        """
        return {
            'id': event.id,
            'event_type': event.event_type.value,
            'event_category': event.event_category.value,
            'event_severity': event.event_severity.value,
            'session_id': event.session_id,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'source': event.source,
            'event_data': json.dumps(event.event_data) if event.event_data else '{}',
            'project_id': event.project_id,
            'work_item_id': event.work_item_id,
            'task_id': event.task_id,
            'created_at': event.created_at.isoformat() if event.created_at else None,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Event:
        """Convert database row to Event model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Event model

        Example:
            >>> cursor = conn.execute("SELECT * FROM session_events WHERE id = ?", (1,))
            >>> row = cursor.fetchone()
            >>> event = EventAdapter.from_db(dict(row))
        """
        # Parse event_data JSON
        event_data_raw = row.get('event_data')
        if event_data_raw:
            if isinstance(event_data_raw, str):
                event_data = json.loads(event_data_raw)
            else:
                # Already a dict (from memory)
                event_data = event_data_raw
        else:
            event_data = {}

        # Parse timestamps
        timestamp = _parse_datetime(row.get('timestamp'))
        created_at = _parse_datetime(row.get('created_at'))

        return Event(
            id=row.get('id'),
            event_type=EventType(row['event_type']),
            event_category=EventCategory(row['event_category']),
            event_severity=EventSeverity(row.get('event_severity', EventSeverity.INFO.value)),
            session_id=row['session_id'],
            timestamp=timestamp or datetime.now(),
            source=row['source'],
            event_data=event_data,
            project_id=row.get('project_id'),
            work_item_id=row.get('work_item_id'),
            task_id=row.get('task_id'),
            created_at=created_at,
        )


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from database value (ISO 8601 string or datetime object).

    Args:
        value: Database value (string, datetime, or None)

    Returns:
        datetime object or None

    Example:
        >>> _parse_datetime("2025-10-10T14:30:00")
        datetime(2025, 10, 10, 14, 30, 0)
        >>> _parse_datetime(None)
        None
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # Handle both 'T' and space separators
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None
