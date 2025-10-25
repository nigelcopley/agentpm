"""
Claude Code Orchestrator

Main orchestrator coordinating all Claude Code integration components.
Provides session lifecycle management, event routing, and resource coordination.

This orchestrator builds on ClaudeIntegrationService with:
- Session lifecycle management (start/end)
- Resource initialization and cleanup
- Error handling and recovery
- Event coordination across components
- Settings and configuration management

Architecture:
    ClaudeCodeOrchestrator
    ├── ClaudeIntegrationService (service coordinator)
    ├── ClaudeCodePlugin (comprehensive plugin)
    ├── HooksEngine (event processing)
    ├── PluginRegistry (plugin management)
    ├── SubagentInvocationHandler (subagent execution)
    ├── SettingsManager (configuration)
    └── SlashCommandRegistry (command handling)

Example:
    from agentpm.core.database import get_database
    from agentpm.services.claude_integration.orchestrator import ClaudeCodeOrchestrator

    db = get_database()
    orchestrator = ClaudeCodeOrchestrator(db, project_id=1)

    # Initialize all systems
    orchestrator.initialize()

    # Handle session lifecycle
    result = orchestrator.handle_session_start("session-123", {})
    result = orchestrator.handle_session_end("session-123", {})

    # Clean shutdown
    orchestrator.shutdown()
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from contextlib import contextmanager

from agentpm.core.database import DatabaseService
from .service import ClaudeIntegrationService
from .plugins import ClaudeCodePlugin, get_registry
from .hooks import get_hooks_engine, EventType, EventResult
from .subagents import get_invocation_handler, get_subagent_registry
from .settings import SettingsManager
from .commands import get_registry as get_command_registry


logger = logging.getLogger(__name__)


class ClaudeCodeOrchestrator:
    """
    Main orchestrator for Claude Code integration.

    Coordinates all subsystems for cohesive session lifecycle management.
    Provides unified interface for:
    - Session initialization and cleanup
    - Event routing across components
    - Resource management
    - Error handling and recovery
    - Settings and configuration

    Pattern: Orchestrator pattern with async lifecycle management

    Example:
        orchestrator = ClaudeCodeOrchestrator(db, project_id=1)

        # Initialize all systems
        orchestrator.initialize()

        # Start session
        result = orchestrator.handle_session_start("session-123", {
            "user_id": "user-456",
            "workspace": "/path/to/workspace"
        })

        # Handle events
        result = orchestrator.handle_event(
            event_type=EventType.PROMPT_SUBMIT,
            payload={"prompt": "Hello Claude"},
            session_id="session-123",
            correlation_id="req-789"
        )

        # End session
        result = orchestrator.handle_session_end("session-123", {})

        # Shutdown
        orchestrator.shutdown()
    """

    def __init__(
        self,
        db: DatabaseService,
        project_id: int,
        auto_initialize: bool = False
    ):
        """
        Initialize Claude Code orchestrator.

        Args:
            db: Database service instance
            project_id: Project identifier
            auto_initialize: If True, automatically call initialize() (default: False)

        Note:
            Call initialize() explicitly if auto_initialize=False
        """
        self.db = db
        self.project_id = project_id

        # Core service coordinator
        self._service = ClaudeIntegrationService()

        # Component references (initialized in initialize())
        self._plugin: Optional[ClaudeCodePlugin] = None
        self._hooks_engine = get_hooks_engine()
        self._plugin_registry = get_registry()
        self._subagent_handler = get_invocation_handler()
        self._subagent_registry = get_subagent_registry()
        self._settings_manager = SettingsManager(db)
        self._command_registry = get_command_registry()

        # State tracking
        self._initialized = False
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._startup_time: Optional[datetime] = None

        logger.info(
            f"ClaudeCodeOrchestrator created for project {project_id} "
            f"(auto_initialize={auto_initialize})"
        )

        if auto_initialize:
            # Note: Can't use await in __init__, so this is synchronous path
            # Better to call initialize() explicitly in async context
            logger.warning(
                "auto_initialize=True not recommended - call initialize() explicitly"
            )

    def initialize(self) -> None:
        """
        Initialize all subsystems.

        Performs:
        - Plugin registration
        - Hooks engine setup
        - Settings loading
        - Command registration
        - Subagent registration

        Raises:
            RuntimeError: If already initialized
            ValueError: If initialization fails

        Example:
            orchestrator = ClaudeCodeOrchestrator(db, project_id=1)
            orchestrator.initialize()
        """
        if self._initialized:
            logger.warning("Orchestrator already initialized")
            return

        logger.info("Initializing Claude Code orchestrator...")

        try:
            # 1. Create and register main plugin
            self._plugin = ClaudeCodePlugin()
            self._plugin_registry.register_plugin(self._plugin)
            logger.info(f"Registered plugin: {self._plugin.name}")

            # 2. Enable hooks engine
            self._hooks_engine.enable()
            logger.info("Hooks engine enabled")

            # 3. Load project settings
            settings = self._settings_manager.load_settings(project_id=self.project_id)
            logger.info(f"Loaded settings for project {self.project_id}")

            # 4. Register default commands
            # Commands are auto-registered via registry singleton
            commands = self._command_registry.list_commands()
            logger.info(f"Commands available: {len(commands)}")

            # 5. Load subagent specifications
            # Subagents are typically registered by plugin initialization
            subagents = self._subagent_registry.list_subagents()
            logger.info(f"Subagents available: {len(subagents)}")

            # Mark as initialized
            self._initialized = True
            self._startup_time = datetime.now()

            logger.info("Claude Code orchestrator initialization complete")

        except Exception as e:
            logger.error(f"Orchestrator initialization failed: {e}", exc_info=True)
            raise ValueError(f"Failed to initialize orchestrator: {e}") from e

    def handle_session_start(
        self,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> EventResult:
        """
        Orchestrate session start.

        Performs:
        - Load previous session checkpoint (if exists)
        - Initialize session context
        - Register session-specific handlers
        - Dispatch session-start event to all plugins

        Args:
            session_id: Session identifier
            payload: Optional session metadata (user_id, workspace, etc.)

        Returns:
            EventResult from session-start event

        Raises:
            RuntimeError: If not initialized
            ValueError: If session already active

        Example:
            result = orchestrator.handle_session_start("session-123", {
                "user_id": "user-456",
                "workspace": "/path/to/workspace"
            })

            if result.success:
                print("Session started successfully")
        """
        self._ensure_initialized()

        if session_id in self._active_sessions:
            raise ValueError(f"Session {session_id} already active")

        logger.info(f"Starting session: {session_id}")

        try:
            # Initialize session state
            session_state = {
                "session_id": session_id,
                "start_time": datetime.now().isoformat(),
                "payload": payload or {},
                "checkpoints": [],
                "event_count": 0,
            }
            self._active_sessions[session_id] = session_state

            # Try to load previous checkpoint
            # Note: Sync version for now (async version would need refactoring)
            checkpoint = None  # TODO: Implement sync checkpoint loading
            if checkpoint:
                logger.info(f"Loaded checkpoint for session {session_id}")
                session_state["checkpoint"] = checkpoint

            # Dispatch session-start event
            result = self._service.handle_event(
                event_type=EventType.SESSION_START,
                payload=payload or {},
                session_id=session_id,
                correlation_id=f"session-start-{session_id}"
            )

            session_state["event_count"] += 1

            logger.info(
                f"Session {session_id} started successfully "
                f"(success={result.success})"
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to start session {session_id}: {e}",
                exc_info=True
            )
            # Cleanup failed session
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            raise

    def handle_session_end(
        self,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> EventResult:
        """
        Orchestrate session end.

        Performs:
        - Create final checkpoint
        - Save session summary
        - Cleanup resources
        - Dispatch session-end event to all plugins

        Args:
            session_id: Session identifier
            payload: Optional session end metadata

        Returns:
            EventResult from session-end event

        Raises:
            RuntimeError: If not initialized
            ValueError: If session not active

        Example:
            result = orchestrator.handle_session_end("session-123", {
                "reason": "user_request",
                "duration_seconds": 3600
            })
        """
        self._ensure_initialized()

        if session_id not in self._active_sessions:
            logger.warning(f"Session {session_id} not active, ending anyway")

        logger.info(f"Ending session: {session_id}")

        try:
            # Get session state
            session_state = self._active_sessions.get(session_id, {})

            # Create final checkpoint
            self._create_session_checkpoint(session_id, "session-end")

            # Dispatch session-end event
            result = self._service.handle_event(
                event_type=EventType.SESSION_END,
                payload=payload or {},
                session_id=session_id,
                correlation_id=f"session-end-{session_id}"
            )

            # Save session summary
            self._save_session_summary(session_id, session_state)

            # Cleanup session state
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]

            logger.info(
                f"Session {session_id} ended successfully "
                f"(success={result.success})"
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to end session {session_id}: {e}",
                exc_info=True
            )
            # Still cleanup session
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            raise

    def handle_event(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        session_id: str,
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventResult:
        """
        Coordinate event across all components.

        Routes event through service coordinator with error handling.
        Tracks event metrics for active sessions.

        Args:
            event_type: Event type (enum or string)
            payload: Event-specific data
            session_id: Session identifier
            correlation_id: Request correlation ID
            metadata: Optional event metadata

        Returns:
            EventResult with aggregated plugin results

        Raises:
            RuntimeError: If not initialized

        Example:
            result = orchestrator.handle_event(
                event_type=EventType.PROMPT_SUBMIT,
                payload={"prompt": "Hello Claude"},
                session_id="session-123",
                correlation_id="req-789"
            )
        """
        self._ensure_initialized()

        logger.debug(
            f"Handling event: {event_type} for session {session_id} "
            f"(correlation={correlation_id})"
        )

        try:
            # Route to service
            result = self._service.handle_event(
                event_type=event_type,
                payload=payload,
                session_id=session_id,
                correlation_id=correlation_id,
                metadata=metadata
            )

            # Track event count for active sessions
            if session_id in self._active_sessions:
                self._active_sessions[session_id]["event_count"] += 1

            return result

        except Exception as e:
            logger.error(
                f"Event handling failed: {event_type} for session {session_id}: {e}",
                exc_info=True
            )

            # Return error result
            return EventResult(
                success=False,
                message=f"Event handling failed: {str(e)}",
                data={"error": str(e), "session_id": session_id, "correlation_id": correlation_id},
                errors=[str(e)]
            )

    def shutdown(self) -> None:
        """
        Clean shutdown of orchestrator.

        Performs:
        - End all active sessions
        - Save state
        - Cleanup resources
        - Disable hooks

        Example:
            orchestrator.shutdown()
        """
        logger.info("Shutting down Claude Code orchestrator...")

        try:
            # End all active sessions
            for session_id in list(self._active_sessions.keys()):
                try:
                    self.handle_session_end(session_id, {
                        "reason": "orchestrator_shutdown"
                    })
                except Exception as e:
                    logger.error(
                        f"Failed to end session {session_id} during shutdown: {e}"
                    )

            # Disable hooks
            self._hooks_engine.disable()

            # Clear plugin registry
            self._plugin_registry.clear()

            # Mark as uninitialized
            self._initialized = False

            logger.info("Claude Code orchestrator shutdown complete")

        except Exception as e:
            logger.error(f"Orchestrator shutdown failed: {e}", exc_info=True)
            raise

    # Helper methods

    def _ensure_initialized(self) -> None:
        """Ensure orchestrator is initialized."""
        if not self._initialized:
            raise RuntimeError(
                "Orchestrator not initialized. Call initialize() first."
            )

    def _load_session_checkpoint(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load previous session checkpoint if exists.

        Args:
            session_id: Session identifier

        Returns:
            Checkpoint data or None if not found
        """
        try:
            # Use plugin to list checkpoints
            if not self._plugin:
                return None

            result = self._plugin.handle({
                "action": "list",
                "session_id": session_id
            })

            if result.get("status") == "success":
                checkpoints = result.get("data", {}).get("checkpoints", [])
                if checkpoints:
                    # Return most recent checkpoint
                    return max(checkpoints, key=lambda x: x["timestamp"])

            return None

        except Exception as e:
            logger.warning(f"Failed to load checkpoint for {session_id}: {e}")
            return None

    def _create_session_checkpoint(
        self,
        session_id: str,
        checkpoint_name: str
    ) -> Optional[str]:
        """
        Create session checkpoint.

        Args:
            session_id: Session identifier
            checkpoint_name: Checkpoint name

        Returns:
            Checkpoint ID or None if failed
        """
        try:
            if not self._plugin:
                return None

            result = self._plugin.handle({
                "action": "checkpoint",
                "session_id": session_id,
                "name": checkpoint_name
            })

            if result.get("status") == "success":
                return result.get("data", {}).get("checkpoint_id")

            return None

        except Exception as e:
            logger.warning(f"Failed to create checkpoint for {session_id}: {e}")
            return None

    def _save_session_summary(
        self,
        session_id: str,
        session_state: Dict[str, Any]
    ) -> None:
        """
        Save session summary to database.

        Args:
            session_id: Session identifier
            session_state: Session state data
        """
        try:
            # Calculate session duration
            start_time = datetime.fromisoformat(session_state.get("start_time", ""))
            duration = (datetime.now() - start_time).total_seconds()

            summary = {
                "session_id": session_id,
                "project_id": self.project_id,
                "start_time": session_state.get("start_time"),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": duration,
                "event_count": session_state.get("event_count", 0),
                "checkpoints_created": len(session_state.get("checkpoints", [])),
            }

            logger.info(f"Session summary for {session_id}: {summary}")

            # TODO: Save to database when session_summaries table exists

        except Exception as e:
            logger.warning(f"Failed to save session summary for {session_id}: {e}")

    # Context manager support

    @contextmanager
    def session(self, session_id: str, payload: Optional[Dict[str, Any]] = None):
        """
        Context manager for session lifecycle.

        Automatically handles session start/end.

        Example:
            with orchestrator.session("session-123", {"user_id": "user-456"}):
                # Session is active
                orchestrator.handle_event(...)
            # Session automatically ended
        """
        self.handle_session_start(session_id, payload)
        try:
            yield
        finally:
            self.handle_session_end(session_id)

    # Properties

    @property
    def is_initialized(self) -> bool:
        """Check if orchestrator is initialized."""
        return self._initialized

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return len(self._active_sessions)

    @property
    def service(self) -> ClaudeIntegrationService:
        """Get service coordinator (for advanced usage)."""
        return self._service

    @property
    def plugin(self) -> Optional[ClaudeCodePlugin]:
        """Get main plugin (for advanced usage)."""
        return self._plugin

    @property
    def uptime_seconds(self) -> float:
        """Get orchestrator uptime in seconds."""
        if not self._startup_time:
            return 0.0
        return (datetime.now() - self._startup_time).total_seconds()


# Singleton instance (optional convenience)
_orchestrator_instance: Optional[ClaudeCodeOrchestrator] = None


def get_orchestrator(
    db: Optional[DatabaseService] = None,
    project_id: Optional[int] = None
) -> ClaudeCodeOrchestrator:
    """
    Get global orchestrator instance.

    Args:
        db: Database service (required on first call)
        project_id: Project ID (required on first call)

    Returns:
        Global orchestrator instance

    Raises:
        ValueError: If db/project_id not provided on first call

    Example:
        orchestrator = get_orchestrator(db, project_id=1)
        orchestrator.initialize()
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        if db is None or project_id is None:
            raise ValueError(
                "db and project_id required for first get_orchestrator() call"
            )
        _orchestrator_instance = ClaudeCodeOrchestrator(db, project_id)

    return _orchestrator_instance


def reset_orchestrator() -> None:
    """Reset global orchestrator instance (for testing)."""
    global _orchestrator_instance
    _orchestrator_instance = None
