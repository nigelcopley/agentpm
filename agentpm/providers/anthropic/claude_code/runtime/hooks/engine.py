"""
Hooks Engine

Event normalization and dispatch to registered plugins.
Core event bus for Claude lifecycle management.

Pattern: Event bus with capability-based routing
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .models import HookEvent, EventResult, EventType
from ..plugins import get_registry, PluginCapability


logger = logging.getLogger(__name__)


class HooksEngine:
    """
    Event bus for Claude lifecycle hooks.

    Normalizes incoming events, dispatches to registered plugins,
    and aggregates results.

    Example:
        engine = get_hooks_engine()

        # Dispatch event
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={"session_id": "abc123"},
            session_id="abc123",
            correlation_id="req-001"
        )

        if result.success:
            print(f"Event handled: {result.data}")
    """

    def __init__(self):
        """Initialize hooks engine with empty state."""
        self._enabled = True
        self._event_handlers: Dict[str, List[callable]] = {}

    def enable(self) -> None:
        """Enable event processing."""
        self._enabled = True
        logger.info("Hooks engine enabled")

    def disable(self) -> None:
        """Disable event processing (for testing/debugging)."""
        self._enabled = False
        logger.info("Hooks engine disabled")

    def is_enabled(self) -> bool:
        """Check if engine is enabled."""
        return self._enabled

    def dispatch_event(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EventResult:
        """
        Dispatch event to registered plugins.

        Normalizes event data, finds supporting plugins, dispatches event,
        and aggregates results.

        Args:
            event_type: Event type (enum or string)
            payload: Event-specific data
            session_id: Session identifier
            correlation_id: Request correlation ID
            metadata: Optional event metadata

        Returns:
            EventResult with aggregated plugin results

        Example:
            result = engine.dispatch_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Hello Claude"},
                session_id="session-123",
                correlation_id="req-456"
            )
        """
        if not self._enabled:
            return EventResult.success_result(
                message="Hooks engine disabled, event skipped"
            )

        try:
            # Normalize event
            event = self._normalize_event(
                event_type, payload, session_id, correlation_id, metadata
            )

            # Get plugins supporting hooks
            registry = get_registry()
            plugins = registry.get_plugins_by_capability(PluginCapability.HOOKS)

            # Dispatch to plugins and custom handlers
            results = self._dispatch_to_plugins(event, plugins)

            # If no plugins AND no custom handlers, return early
            event_key = event.type.value if isinstance(event.type, EventType) else event.type
            if not plugins and event_key not in self._event_handlers:
                logger.debug(f"No hook plugins or handlers registered for event: {event_type}")
                return EventResult.success_result(
                    message="No hook plugins or handlers registered",
                    data={"event": event.to_dict()}
                )

            # Aggregate results
            return self._aggregate_results(results, event)

        except Exception as e:
            logger.error(f"Error dispatching event {event_type}: {e}", exc_info=True)
            return EventResult.error_result(
                message=f"Error dispatching event: {str(e)}",
                errors=[str(e)]
            )

    def register_handler(
        self, event_type: EventType | str, handler: callable
    ) -> None:
        """
        Register a custom event handler.

        Allows direct handler registration without plugin system.
        Useful for simple hooks or testing.

        Args:
            event_type: Event type to handle
            handler: Callable accepting (event: HookEvent) -> Dict[str, Any]

        Example:
            def on_session_start(event: HookEvent) -> Dict[str, Any]:
                print(f"Session started: {event.session_id}")
                return {"status": "logged"}

            engine.register_handler(EventType.SESSION_START, on_session_start)
        """
        event_key = event_type.value if isinstance(event_type, EventType) else event_type
        if event_key not in self._event_handlers:
            self._event_handlers[event_key] = []

        self._event_handlers[event_key].append(handler)
        logger.info(f"Registered handler for event: {event_key}")

    def unregister_handler(
        self, event_type: EventType | str, handler: callable
    ) -> None:
        """
        Unregister a custom event handler.

        Args:
            event_type: Event type
            handler: Handler to remove
        """
        event_key = event_type.value if isinstance(event_type, EventType) else event_type
        if event_key in self._event_handlers:
            try:
                self._event_handlers[event_key].remove(handler)
                logger.info(f"Unregistered handler for event: {event_key}")
            except ValueError:
                logger.warning(f"Handler not found for event: {event_key}")

    def clear_handlers(self) -> None:
        """Clear all registered handlers (useful for testing)."""
        self._event_handlers.clear()
        logger.info("Cleared all event handlers")

    def _normalize_event(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HookEvent:
        """
        Normalize event data into canonical HookEvent.

        Args:
            event_type: Event type
            payload: Event payload
            session_id: Session ID
            correlation_id: Correlation ID
            metadata: Optional metadata

        Returns:
            Normalized HookEvent

        Raises:
            ValueError: If required fields missing
        """
        if not session_id:
            raise ValueError("session_id is required")
        if not correlation_id:
            raise ValueError("correlation_id is required")

        # Convert string to EventType if possible
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                # Keep as string if not in enum (allows custom events)
                pass

        return HookEvent(
            type=event_type,
            payload=payload or {},
            session_id=session_id,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

    def _dispatch_to_plugins(
        self, event: HookEvent, plugins: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Dispatch event to plugins and collect results.

        Args:
            event: Normalized event
            plugins: List of plugins supporting hooks

        Returns:
            List of plugin results
        """
        results = []

        for plugin in plugins:
            try:
                # Convert event to plugin input format
                input_data = event.to_dict()

                # Call plugin handler
                result = plugin.handle(input_data)

                results.append({
                    "plugin": plugin.name,
                    "status": "success",
                    "result": result
                })

            except Exception as e:
                logger.error(
                    f"Plugin {plugin.name} failed to handle event {event.type}: {e}",
                    exc_info=True
                )
                results.append({
                    "plugin": plugin.name,
                    "status": "error",
                    "error": str(e)
                })

        # Also dispatch to custom handlers
        event_key = event.type.value if isinstance(event.type, EventType) else event.type
        if event_key in self._event_handlers:
            for handler in self._event_handlers[event_key]:
                try:
                    result = handler(event)
                    results.append({
                        "plugin": f"handler-{handler.__name__}",
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    logger.error(
                        f"Handler {handler.__name__} failed: {e}",
                        exc_info=True
                    )
                    results.append({
                        "plugin": f"handler-{handler.__name__}",
                        "status": "error",
                        "error": str(e)
                    })

        return results

    def _aggregate_results(
        self, results: List[Dict[str, Any]], event: HookEvent
    ) -> EventResult:
        """
        Aggregate plugin results into EventResult.

        Args:
            results: List of plugin results
            event: Original event

        Returns:
            Aggregated EventResult
        """
        # Check if any plugins failed
        errors = [
            f"{r['plugin']}: {r['error']}"
            for r in results
            if r.get("status") == "error"
        ]

        # Count successes
        success_count = sum(1 for r in results if r.get("status") == "success")

        if errors:
            return EventResult(
                success=False,
                message=f"Event handled with errors ({success_count}/{len(results)} succeeded)",
                data={
                    "event": event.to_dict(),
                    "results": results,
                    "success_count": success_count,
                    "error_count": len(errors)
                },
                errors=errors
            )
        else:
            return EventResult(
                success=True,
                message=f"Event handled successfully by {len(results)} plugin(s)",
                data={
                    "event": event.to_dict(),
                    "results": results,
                    "success_count": success_count
                }
            )


# Global engine instance (singleton pattern)
_engine: Optional[HooksEngine] = None


def get_hooks_engine() -> HooksEngine:
    """
    Get global hooks engine instance.

    Returns:
        Singleton HooksEngine instance

    Example:
        from agentpm.providers.anthropic.claude_code.runtime.hooks import get_hooks_engine

        engine = get_hooks_engine()
        result = engine.dispatch_event(...)
    """
    global _engine
    if _engine is None:
        _engine = HooksEngine()
    return _engine


def reset_hooks_engine() -> None:
    """
    Reset global engine to None.

    Useful for testing to ensure clean state.

    Example:
        # In test teardown
        reset_hooks_engine()
    """
    global _engine
    _engine = None
