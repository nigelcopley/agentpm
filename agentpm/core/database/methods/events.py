"""Event tracking methods for CRUD and query operations.

This module provides database operations for Event entities.
Part of the three-layer pattern:
- Layer 1: Pydantic models (validation)
- Layer 2: Adapters (conversion)
- Layer 3: Methods (CRUD operations) ← THIS FILE

Methods:
- CRUD: create_event, get_event, list_events, delete_event
- Queries: get_session_events, get_events_by_type, get_events_by_category,
           get_events_by_severity, get_events_by_task, get_events_by_work_item,
           get_events_by_time_range
- Analytics: count_events_by_category, get_error_events, get_workflow_events
"""

from datetime import datetime, timedelta
from typing import List, Optional

from agentpm.core.database.adapters.event import EventAdapter
from agentpm.core.database.models.event import Event, EventType, EventCategory, EventSeverity


def create_event(db: 'DatabaseService', event: Event) -> Event:
    """Create a new event record.

    Args:
        db: DatabaseService instance
        event: Event model (id will be auto-assigned)

    Returns:
        Event with id populated

    Example:
        >>> event = Event(
        ...     event_type=EventType.TASK_STARTED,
        ...     event_category=EventCategory.WORKFLOW,
        ...     session_id=1,
        ...     source='workflow_service',
        ...     event_data={'task_id': 239}
        ... )
        >>> created = create_event(db, event)
        >>> print(created.id)  # 1
    """
    with db.connect() as conn:
        data = EventAdapter.to_db(event)

        # Remove id if present (auto-increment)
        data.pop('id', None)

        cursor = conn.execute('''
            INSERT INTO session_events (
                event_type, event_category, event_severity,
                session_id, timestamp, source, event_data,
                project_id, work_item_id, task_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['event_type'], data['event_category'], data['event_severity'],
            data['session_id'], data['timestamp'], data['source'],
            data['event_data'], data['project_id'], data['work_item_id'],
            data['task_id']
        ))
        conn.commit()

        event.id = cursor.lastrowid
        return event


def get_event(db: 'DatabaseService', event_id: int) -> Optional[Event]:
    """Get event by ID.

    Args:
        db: DatabaseService instance
        event_id: Event ID

    Returns:
        Event model or None if not found

    Example:
        >>> event = get_event(db, 1)
        >>> if event:
        ...     print(event.event_type, event.timestamp)
    """
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT * FROM session_events WHERE id = ?
        ''', (event_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return EventAdapter.from_db(dict(row))


def get_session_events(
    db: 'DatabaseService',
    session_id: int,
    event_category: Optional[EventCategory] = None,
    event_type: Optional[EventType] = None,
    event_severity: Optional[EventSeverity] = None,
    limit: Optional[int] = None
) -> List[Event]:
    """Get all events for a session with optional filtering.

    Args:
        db: DatabaseService instance
        session_id: Session ID
        event_category: Filter by category (optional)
        event_type: Filter by type (optional)
        event_severity: Filter by severity (optional)
        limit: Max events to return (optional)

    Returns:
        List of Event models, newest first

    Example:
        >>> # All events for session
        >>> events = get_session_events(db, session_id=1)

        >>> # Only workflow events
        >>> workflow_events = get_session_events(
        ...     db, session_id=1,
        ...     event_category=EventCategory.WORKFLOW
        ... )

        >>> # Only error events
        >>> errors = get_session_events(
        ...     db, session_id=1,
        ...     event_category=EventCategory.ERROR,
        ...     event_severity=EventSeverity.ERROR
        ... )
    """
    with db.connect() as conn:
        # Build query with optional filters
        query = "SELECT * FROM session_events WHERE session_id = ?"
        params = [session_id]

        if event_category:
            query += " AND event_category = ?"
            params.append(event_category.value)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)

        if event_severity:
            query += " AND event_severity = ?"
            params.append(event_severity.value)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_type(
    db: 'DatabaseService',
    event_type: EventType,
    session_id: Optional[int] = None,
    limit: int = 100
) -> List[Event]:
    """Get events by type.

    Args:
        db: DatabaseService instance
        event_type: Event type to filter by
        session_id: Optional session filter
        limit: Max events to return (default 100)

    Returns:
        List of Event models

    Example:
        >>> # All task started events
        >>> task_starts = get_events_by_type(db, EventType.TASK_STARTED)

        >>> # Task started events for specific session
        >>> session_task_starts = get_events_by_type(
        ...     db, EventType.TASK_STARTED, session_id=1
        ... )
    """
    with db.connect() as conn:
        if session_id:
            query = '''
                SELECT * FROM session_events
                WHERE event_type = ? AND session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_type.value, session_id, limit)
        else:
            query = '''
                SELECT * FROM session_events
                WHERE event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_type.value, limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_category(
    db: 'DatabaseService',
    event_category: EventCategory,
    session_id: Optional[int] = None,
    limit: int = 100
) -> List[Event]:
    """Get events by category.

    Args:
        db: DatabaseService instance
        event_category: Event category to filter by
        session_id: Optional session filter
        limit: Max events to return (default 100)

    Returns:
        List of Event models

    Example:
        >>> # All workflow events across all sessions
        >>> workflow = get_events_by_category(db, EventCategory.WORKFLOW)

        >>> # Tool usage events for specific session
        >>> tools = get_events_by_category(
        ...     db, EventCategory.TOOL_USAGE, session_id=1
        ... )
    """
    with db.connect() as conn:
        if session_id:
            query = '''
                SELECT * FROM session_events
                WHERE event_category = ? AND session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_category.value, session_id, limit)
        else:
            query = '''
                SELECT * FROM session_events
                WHERE event_category = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_category.value, limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_severity(
    db: 'DatabaseService',
    event_severity: EventSeverity,
    session_id: Optional[int] = None,
    limit: int = 100
) -> List[Event]:
    """Get events by severity (primarily for error filtering).

    Args:
        db: DatabaseService instance
        event_severity: Event severity to filter by
        session_id: Optional session filter
        limit: Max events to return (default 100)

    Returns:
        List of Event models

    Example:
        >>> # All errors across all sessions
        >>> errors = get_events_by_severity(db, EventSeverity.ERROR)

        >>> # Critical issues for specific session
        >>> critical = get_events_by_severity(
        ...     db, EventSeverity.CRITICAL, session_id=1
        ... )
    """
    with db.connect() as conn:
        if session_id:
            query = '''
                SELECT * FROM session_events
                WHERE event_severity = ? AND session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_severity.value, session_id, limit)
        else:
            query = '''
                SELECT * FROM session_events
                WHERE event_severity = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            params = (event_severity.value, limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_task(
    db: 'DatabaseService',
    task_id: int,
    limit: int = 100
) -> List[Event]:
    """Get all events for a specific task.

    Args:
        db: DatabaseService instance
        task_id: Task ID
        limit: Max events to return (default 100)

    Returns:
        List of Event models

    Example:
        >>> # All events for task #239
        >>> task_events = get_events_by_task(db, task_id=239)
    """
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT * FROM session_events
            WHERE task_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (task_id, limit))

        rows = cursor.fetchall()
        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_work_item(
    db: 'DatabaseService',
    work_item_id: int,
    limit: int = 100
) -> List[Event]:
    """Get all events for a specific work item.

    Args:
        db: DatabaseService instance
        work_item_id: Work item ID
        limit: Max events to return (default 100)

    Returns:
        List of Event models

    Example:
        >>> # All events for WI-35
        >>> wi_events = get_events_by_work_item(db, work_item_id=35)
    """
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT * FROM session_events
            WHERE work_item_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (work_item_id, limit))

        rows = cursor.fetchall()
        return [EventAdapter.from_db(dict(row)) for row in rows]


def get_events_by_time_range(
    db: 'DatabaseService',
    start: datetime,
    end: datetime,
    session_id: Optional[int] = None
) -> List[Event]:
    """Get events within time range.

    Args:
        db: DatabaseService instance
        start: Start datetime (inclusive)
        end: End datetime (inclusive)
        session_id: Optional session filter

    Returns:
        List of Event models in range

    Example:
        >>> from datetime import datetime, timedelta
        >>> now = datetime.now()
        >>> hour_ago = now - timedelta(hours=1)
        >>> recent_events = get_events_by_time_range(db, hour_ago, now)
    """
    with db.connect() as conn:
        if session_id:
            query = '''
                SELECT * FROM session_events
                WHERE timestamp >= ? AND timestamp <= ? AND session_id = ?
                ORDER BY timestamp DESC
            '''
            params = (start.isoformat(), end.isoformat(), session_id)
        else:
            query = '''
                SELECT * FROM session_events
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            '''
            params = (start.isoformat(), end.isoformat())

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        return [EventAdapter.from_db(dict(row)) for row in rows]


def delete_event(db: 'DatabaseService', event_id: int) -> bool:
    """Delete event (hard delete).

    Note: Events are audit trail, deletion should be rare.
    Consider retention policies instead.

    Args:
        db: DatabaseService instance
        event_id: Event ID to delete

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_event(db, event_id=1)
    """
    with db.connect() as conn:
        cursor = conn.execute('''
            DELETE FROM session_events WHERE id = ?
        ''', (event_id,))
        conn.commit()

        return cursor.rowcount > 0


# ============================================================================
# ANALYTICS METHODS
# ============================================================================


def count_events_by_category(
    db: 'DatabaseService',
    session_id: int
) -> dict[str, int]:
    """Count events by category for a session.

    Args:
        db: DatabaseService instance
        session_id: Session ID

    Returns:
        Dict mapping category to count

    Example:
        >>> counts = count_events_by_category(db, session_id=1)
        >>> print(counts)
        {'workflow': 45, 'tool_usage': 120, 'error': 3, 'decision': 8}
    """
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT event_category, COUNT(*) as count
            FROM session_events
            WHERE session_id = ?
            GROUP BY event_category
        ''', (session_id,))

        rows = cursor.fetchall()
        return {row['event_category']: row['count'] for row in rows}


def get_error_events(
    db: 'DatabaseService',
    session_id: int,
    unresolved_only: bool = False
) -> List[Event]:
    """Get error events for a session.

    Args:
        db: DatabaseService instance
        session_id: Session ID
        unresolved_only: Only return unresolved errors (default False)

    Returns:
        List of error Event models

    Example:
        >>> # All errors
        >>> all_errors = get_error_events(db, session_id=1)

        >>> # Unresolved errors only
        >>> active_errors = get_error_events(db, session_id=1, unresolved_only=True)
    """
    events = get_session_events(
        db,
        session_id=session_id,
        event_category=EventCategory.ERROR
    )

    if unresolved_only:
        # Filter events where event_data.resolved_at is None
        return [
            e for e in events
            if not e.event_data.get('resolved_at')
        ]

    return events


def get_workflow_events(
    db: 'DatabaseService',
    session_id: int,
    task_id: Optional[int] = None
) -> List[Event]:
    """Get workflow events for a session.

    Args:
        db: DatabaseService instance
        session_id: Session ID
        task_id: Optional task filter

    Returns:
        List of workflow Event models

    Example:
        >>> # All workflow events
        >>> workflow = get_workflow_events(db, session_id=1)

        >>> # Workflow events for specific task
        >>> task_workflow = get_workflow_events(db, session_id=1, task_id=239)
    """
    if task_id:
        return [
            e for e in get_session_events(
                db, session_id=session_id,
                event_category=EventCategory.WORKFLOW
            )
            if e.task_id == task_id
        ]

    return get_session_events(
        db,
        session_id=session_id,
        event_category=EventCategory.WORKFLOW
    )
