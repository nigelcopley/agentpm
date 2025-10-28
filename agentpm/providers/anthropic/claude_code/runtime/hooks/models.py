"""
Hook Event Models

Type-safe models for Claude lifecycle events.
Extends the basic HookEvent from service.py with event types and enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EventType(Enum):
    """
    Claude lifecycle event types.

    Maps to Claude Code hook points documented in the API.
    """

    SESSION_START = "session-start"
    """Fired when a new Claude session begins"""

    SESSION_END = "session-end"
    """Fired when a Claude session ends"""

    PROMPT_SUBMIT = "prompt-submit"
    """Fired when user submits a prompt"""

    TOOL_RESULT = "tool-result"
    """Fired when a tool execution completes"""

    PRE_TOOL_USE = "pre-tool-use"
    """Fired before tool execution"""

    POST_TOOL_USE = "post-tool-use"
    """Fired after tool execution"""

    STOP = "stop"
    """Fired when session is stopped"""

    SUBAGENT_STOP = "subagent-stop"
    """Fired when a subagent completes"""

    PRE_COMPACT = "pre-compact"
    """Fired before message compaction"""

    NOTIFICATION = "notification"
    """Fired for user notifications"""


@dataclass(frozen=True)
class HookEvent:
    """
    Canonical hook event envelope.

    Extends the basic HookEvent from service.py with additional metadata.
    Immutable to ensure event integrity.

    Example:
        event = HookEvent(
            type=EventType.SESSION_START,
            payload={"session_id": "abc123", "user": "claude"},
            session_id="abc123",
            correlation_id="req-001",
        )
    """

    type: EventType | str
    """Event type (enum or string)"""

    payload: Dict[str, Any]
    """Event-specific data"""

    session_id: str
    """Session identifier for correlation"""

    correlation_id: str
    """Request correlation ID"""

    timestamp: datetime = field(default_factory=datetime.now)
    """Event timestamp (auto-generated)"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional event metadata"""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.

        Returns:
            Dictionary representation suitable for serialization

        Example:
            event_dict = event.to_dict()
            # {"type": "session-start", "payload": {...}, ...}
        """
        return {
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "payload": self.payload,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HookEvent:
        """
        Create event from dictionary.

        Args:
            data: Dictionary with event fields

        Returns:
            HookEvent instance

        Example:
            event = HookEvent.from_dict({
                "type": "session-start",
                "payload": {...},
                "session_id": "abc123",
                "correlation_id": "req-001"
            })
        """
        event_type = data.get("type")
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                pass  # Keep as string if not in enum

        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            type=event_type,
            payload=data.get("payload", {}),
            session_id=data["session_id"],
            correlation_id=data["correlation_id"],
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class EventResult:
    """
    Result of handling a hook event.

    Immutable to ensure result integrity.

    Example:
        result = EventResult(
            success=True,
            message="Event processed successfully",
            data={"records_updated": 5}
        )
    """

    success: bool
    """Whether event handling succeeded"""

    message: Optional[str] = None
    """Optional result message"""

    data: Optional[Dict[str, Any]] = None
    """Optional result data"""

    errors: Optional[List[str]] = None
    """Optional error messages"""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Returns:
            Dictionary representation

        Example:
            result_dict = result.to_dict()
            # {"success": true, "message": "...", "data": {...}}
        """
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data or {},
            "errors": self.errors or [],
        }

    @classmethod
    def success_result(
        cls, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None
    ) -> EventResult:
        """
        Create a success result.

        Args:
            message: Optional success message
            data: Optional result data

        Returns:
            EventResult with success=True

        Example:
            result = EventResult.success_result(
                message="Hook executed",
                data={"count": 3}
            )
        """
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_result(
        cls, message: str, errors: Optional[List[str]] = None
    ) -> EventResult:
        """
        Create an error result.

        Args:
            message: Error message
            errors: Optional list of detailed errors

        Returns:
            EventResult with success=False

        Example:
            result = EventResult.error_result(
                message="Hook failed",
                errors=["Invalid payload", "Missing session_id"]
            )
        """
        return cls(success=False, message=message, errors=errors)
