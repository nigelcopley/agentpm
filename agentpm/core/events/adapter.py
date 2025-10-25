"""EventAdapter for Event ↔ SQLite conversion.

This module provides the adapter layer for converting between:
- Event Pydantic models ↔ SQLite dictionaries

Three-Layer Pattern:
- Models (models.py) → Adapter (this file) → Methods (methods.py)

Conversion includes:
- Enum serialization (EventType, EventCategory, EventSeverity)
- Datetime serialization (ISO 8601 format)
- JSON serialization for event_data
- Optional field handling
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict

from agentpm.core.events.models import Event, EventCategory, EventSeverity, EventType


class EventAdapter:
    """Adapter for Event ↔ SQLite conversion.

    Handles serialization and deserialization of Event models
    to/from SQLite database dictionaries.
    """

    @staticmethod
    def to_dict(event: Event) -> Dict[str, Any]:
        """Convert Event Pydantic model to SQLite dict.

        Args:
            event: Event model to convert

        Returns:
            Dictionary ready for SQLite insertion

        Example:
            event = Event(
                event_type=EventType.TASK_STARTED,
                event_category=EventCategory.WORKFLOW,
                session_id=1,
                source='workflow_service',
                event_data={'task_id': 123}
            )
            data = EventAdapter.to_dict(event)
            # data = {
            #     'event_type': 'task.started',
            #     'event_category': 'workflow',
            #     'event_severity': 'info',
            #     'session_id': 1,
            #     'timestamp': '2025-10-10T14:30:00',
            #     'source': 'workflow_service',
            #     'event_data': '{"task_id": 123}',
            #     ...
            # }
        """
        return {
            'id': event.id,
            'event_type': event.event_type.value,  # Enum to string
            'event_category': event.event_category.value,  # Enum to string
            'event_severity': event.event_severity.value,  # Enum to string
            'session_id': event.session_id,
            'timestamp': event.timestamp.isoformat(),  # Datetime to ISO 8601
            'source': event.source,
            'event_data': json.dumps(event.event_data),  # Dict to JSON string
            'project_id': event.project_id,
            'work_item_id': event.work_item_id,
            'task_id': event.task_id,
            'created_at': event.created_at.isoformat() if event.created_at else None,
        }

    @staticmethod
    def from_row(row: sqlite3.Row) -> Event:
        """Convert SQLite row to Event Pydantic model.

        Args:
            row: SQLite row from session_events table

        Returns:
            Event Pydantic model with validation

        Example:
            cursor = db.execute("SELECT * FROM session_events WHERE id = ?", (1,))
            row = cursor.fetchone()
            event = EventAdapter.from_row(row)
        """
        return Event(
            id=row['id'],
            event_type=EventType(row['event_type']),  # String to Enum
            event_category=EventCategory(row['event_category']),  # String to Enum
            event_severity=EventSeverity(row['event_severity']),  # String to Enum
            session_id=row['session_id'],
            timestamp=datetime.fromisoformat(row['timestamp']),  # ISO 8601 to datetime
            source=row['source'],
            event_data=json.loads(row['event_data']),  # JSON string to dict
            project_id=row['project_id'],
            work_item_id=row['work_item_id'],
            task_id=row['task_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        )
