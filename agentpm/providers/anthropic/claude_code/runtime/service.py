from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .hooks import HooksEngine, get_hooks_engine, HookEvent, EventResult, EventType
from .plugins import ClaudePluginRegistry, get_registry, ClaudePlugin, PluginCapability


logger = logging.getLogger(__name__)


class ClaudeIntegrationService:
    """
    Service coordinator for consolidated Claude integration.

    This service provides a unified interface for Claude-related functionality:
    - Lifecycle hooks (session, tools, events)
    - Plugin management (registration, discovery)
    - Event dispatch and aggregation

    Follows the APM (Agent Project Manager) service pattern with three-layer architecture:
    - Models: HookEvent, EventResult, PluginCapability
    - Methods: Event dispatch, plugin routing
    - Integration: Hooks engine, plugin registry

    Example:
        service = ClaudeIntegrationService()

        # Register plugins
        service.register_plugin(hooks_plugin)
        service.register_plugin(memory_plugin)

        # Dispatch events
        result = service.handle_event(
            event_type=EventType.SESSION_START,
            payload={"session_id": "abc123"},
            session_id="abc123",
            correlation_id="req-001"
        )

        if result.success:
            print(f"Event handled: {result.data}")
    """

    def __init__(
        self,
        hooks_engine: Optional[HooksEngine] = None,
        plugin_registry: Optional[ClaudePluginRegistry] = None
    ) -> None:
        """
        Initialize service coordinator.

        Args:
            hooks_engine: Optional hooks engine (uses global singleton if None)
            plugin_registry: Optional plugin registry (uses global singleton if None)
        """
        self._hooks_engine = hooks_engine or get_hooks_engine()
        self._plugin_registry = plugin_registry or get_registry()
        logger.info("ClaudeIntegrationService initialized")

    def register_plugin(self, plugin: ClaudePlugin) -> None:
        """
        Register a Claude integration plugin.

        Args:
            plugin: Plugin implementing ClaudePlugin protocol

        Raises:
            ValueError: If plugin already registered
            TypeError: If plugin doesn't implement protocol

        Example:
            service.register_plugin(MyHooksPlugin())
        """
        self._plugin_registry.register_plugin(plugin)
        logger.info(f"Registered plugin: {plugin.name}")

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin by name.

        Args:
            plugin_name: Name of plugin to unregister

        Raises:
            KeyError: If plugin not found
        """
        self._plugin_registry.unregister_plugin(plugin_name)
        logger.info(f"Unregistered plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[ClaudePlugin]:
        """
        Get plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugin_registry.get_plugin(plugin_name)

    def list_plugins(self) -> list[Dict[str, Any]]:
        """
        List all registered plugins.

        Returns:
            List of plugin metadata dictionaries
        """
        return self._plugin_registry.list_plugins()

    def handle_event(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EventResult:
        """
        Dispatch hook event to registered plugins.

        Normalizes event, finds supporting plugins, dispatches event,
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
            result = service.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Hello"},
                session_id="session-123",
                correlation_id="req-456"
            )
        """
        return self._hooks_engine.dispatch_event(
            event_type=event_type,
            payload=payload,
            session_id=session_id,
            correlation_id=correlation_id,
            metadata=metadata
        )

    def enable_hooks(self) -> None:
        """Enable hook processing."""
        self._hooks_engine.enable()
        logger.info("Hooks enabled")

    def disable_hooks(self) -> None:
        """Disable hook processing (for testing/debugging)."""
        self._hooks_engine.disable()
        logger.info("Hooks disabled")

    def is_hooks_enabled(self) -> bool:
        """Check if hooks are enabled."""
        return self._hooks_engine.is_enabled()

    @property
    def hooks_engine(self) -> HooksEngine:
        """Get hooks engine instance (for advanced usage)."""
        return self._hooks_engine

    @property
    def plugin_registry(self) -> ClaudePluginRegistry:
        """Get plugin registry instance (for advanced usage)."""
        return self._plugin_registry




