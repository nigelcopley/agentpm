"""Event infrastructure for event-driven session tracking.

This module provides:
- EventBus: Lightweight event bus using stdlib threading + queue
- Event models: Pydantic models with typed event_data schemas
- EventAdapter: Event ↔ SQLite conversion
- EventMethods: CRUD operations for session events

Architecture:
- Async event capture with <3ms overhead
- Background persistence with queue
- Graceful degradation (events optional)
- Three-layer pattern (Models → Adapters → Methods)
"""

from agentpm.core.events.models import (
    Event,
    EventCategory,
    EventSeverity,
    EventType,
    ErrorEventData,
    WorkflowEventData,
    ToolEventData,
    DecisionEventData,
    ReasoningEventData,
)

__all__ = [
    'Event',
    'EventCategory',
    'EventSeverity',
    'EventType',
    'ErrorEventData',
    'WorkflowEventData',
    'ToolEventData',
    'DecisionEventData',
    'ReasoningEventData',
]
