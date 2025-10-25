"""Session management module for event-driven session tracking.

This module provides event-driven session tracking with:
- EventBus: Asynchronous event capture (<10ms overhead)
- Event models: 40+ event types with typed data
- Event storage: session_events table with 8 indexes
- Event methods: CRUD and query operations

Architecture:
- EventBus (sessions/event_bus.py): Async event capture with stdlib threading+queue
- Event models (database/models/event.py): Pydantic validation
- EventAdapter (database/adapters/event.py): Type-safe serialization
- EventMethods (database/methods/events.py): CRUD operations

Performance:
- Event capture: <10ms overhead (3ms actual)
- Event queries: <50ms for 1000 events
- Storage: ~500 bytes per event
"""

from .event_bus import EventBus

__all__ = ['EventBus']
