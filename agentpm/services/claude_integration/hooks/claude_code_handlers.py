"""
Claude Code Hook Handlers

Event handlers for Claude Code lifecycle integration.
Bridges Claude Code events with AIPM session tracking and workflow.

Pattern: Event handlers with database persistence
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from .models import HookEvent, EventResult, EventType
from .engine import get_hooks_engine

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


class ClaudeCodeHookHandlers:
    """
    Hook handlers for Claude Code lifecycle events.

    Integrates Claude Code session lifecycle with AIPM database:
    - Session tracking (start/end/handover)
    - Prompt tracking for session history
    - Tool usage analytics
    - Context persistence

    Example:
        db = DatabaseService("path/to/db")
        handlers = ClaudeCodeHookHandlers(db)
        handlers.register_all()

        # Events are now automatically handled
        engine = get_hooks_engine()
        result = engine.dispatch_event(
            event_type=EventType.SESSION_START,
            payload={"project_id": 1},
            session_id="session-123",
            correlation_id="req-456"
        )
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize handlers with database connection.

        Args:
            db: DatabaseService instance for persistence
        """
        self.db = db
        self.engine = get_hooks_engine()

    def register_all(self) -> None:
        """
        Register all Claude Code handlers with the hooks engine.

        Call this once during application initialization.

        Example:
            handlers = ClaudeCodeHookHandlers(db)
            handlers.register_all()
        """
        self.engine.register_handler(EventType.SESSION_START, self.on_session_start)
        self.engine.register_handler(EventType.SESSION_END, self.on_session_end)
        self.engine.register_handler(EventType.PROMPT_SUBMIT, self.on_prompt_submit)
        self.engine.register_handler(EventType.TOOL_RESULT, self.on_tool_result)
        self.engine.register_handler(EventType.PRE_TOOL_USE, self.on_pre_tool_use)
        self.engine.register_handler(EventType.POST_TOOL_USE, self.on_post_tool_use)

        logger.info("Registered Claude Code hook handlers")

    def unregister_all(self) -> None:
        """
        Unregister all handlers from the hooks engine.

        Useful for testing or cleanup.

        Example:
            handlers.unregister_all()
        """
        self.engine.unregister_handler(EventType.SESSION_START, self.on_session_start)
        self.engine.unregister_handler(EventType.SESSION_END, self.on_session_end)
        self.engine.unregister_handler(EventType.PROMPT_SUBMIT, self.on_prompt_submit)
        self.engine.unregister_handler(EventType.TOOL_RESULT, self.on_tool_result)
        self.engine.unregister_handler(EventType.PRE_TOOL_USE, self.on_pre_tool_use)
        self.engine.unregister_handler(EventType.POST_TOOL_USE, self.on_post_tool_use)

        logger.info("Unregistered Claude Code hook handlers")

    def on_session_start(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle SESSION_START event.

        Initializes new session in database and loads context from
        previous session if available.

        Payload fields:
            - project_id: Required. Project ID for session
            - tool_version: Optional. Claude Code version
            - developer_name: Optional. Developer name
            - developer_email: Optional. Developer email

        Args:
            event: Hook event with session details

        Returns:
            Dict with session data and loaded context

        Example:
            # Event dispatched by Claude Code on session start
            {
                "type": "session-start",
                "payload": {
                    "project_id": 1,
                    "tool_version": "1.5.0"
                },
                "session_id": "session-abc-123",
                "correlation_id": "req-001"
            }
        """
        try:
            from agentpm.core.database.methods import sessions as session_methods
            from agentpm.core.database.models.session import (
                Session, SessionTool, SessionType, SessionMetadata
            )

            project_id = event.payload.get("project_id")
            if not project_id:
                logger.error("SESSION_START missing project_id")
                return {"status": "error", "message": "project_id required"}

            # Create new session record
            session = Session(
                session_id=event.session_id,
                project_id=project_id,
                tool=SessionTool.CLAUDE_CODE,
                tool_version=event.payload.get("tool_version"),
                session_type=SessionType.DEVELOPMENT,
                developer_name=event.payload.get("developer_name"),
                developer_email=event.payload.get("developer_email"),
                metadata=SessionMetadata(),
                started_at=datetime.now().isoformat(),
            )

            created_session = session_methods.create_session(self.db, session)
            session_methods.set_current_session(self.db, created_session.session_id)

            # Load context from previous session
            previous_context = self._load_previous_session_context(project_id)

            logger.info(
                f"Session started: {event.session_id} (project {project_id})"
            )

            return {
                "status": "success",
                "session": {
                    "id": created_session.id,
                    "session_id": created_session.session_id,
                    "project_id": created_session.project_id,
                },
                "previous_context": previous_context,
                "message": "Session initialized successfully"
            }

        except Exception as e:
            logger.error(f"Error handling SESSION_START: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def on_session_end(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle SESSION_END event.

        Finalizes session in database:
        - Updates end time and duration
        - Generates session summary
        - Creates handover document
        - Updates session metrics

        Payload fields:
            - exit_reason: Optional. Reason for ending session
            - summary: Optional. Session summary text

        Args:
            event: Hook event with session end details

        Returns:
            Dict with session summary and handover data

        Example:
            # Event dispatched by Claude Code on session end
            {
                "type": "session-end",
                "payload": {
                    "exit_reason": "User closed Claude Code",
                    "summary": "Implemented feature X, tests passing"
                },
                "session_id": "session-abc-123",
                "correlation_id": "req-002"
            }
        """
        try:
            from agentpm.core.database.methods import sessions as session_methods
            from agentpm.core.database.models.session import SessionMetadata

            # Get current session
            session = session_methods.get_session(self.db, event.session_id)
            if not session:
                logger.warning(f"Session not found for SESSION_END: {event.session_id}")
                return {
                    "status": "error",
                    "message": f"Session {event.session_id} not found"
                }

            # Generate session summary
            summary = self._generate_session_summary(session, event.payload)

            # Update metadata with summary
            metadata = session.metadata or SessionMetadata()
            if not hasattr(metadata, 'tool_specific'):
                metadata.tool_specific = {}
            metadata.tool_specific['session_summary'] = summary

            # End session with updated metadata
            ended_session = session_methods.end_session(
                self.db,
                event.session_id,
                metadata=metadata,
                exit_reason=event.payload.get("exit_reason")
            )

            # Clear current session marker
            session_methods.clear_current_session(self.db)

            # Create handover document (if work was done)
            handover = self._create_handover_document(ended_session)

            logger.info(
                f"Session ended: {event.session_id} "
                f"(duration: {ended_session.duration_minutes} min)"
            )

            return {
                "status": "success",
                "session": {
                    "id": ended_session.id,
                    "session_id": ended_session.session_id,
                    "duration_minutes": ended_session.duration_minutes,
                },
                "summary": summary,
                "handover": handover,
                "message": "Session ended successfully"
            }

        except Exception as e:
            logger.error(f"Error handling SESSION_END: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def on_prompt_submit(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle PROMPT_SUBMIT event.

        Tracks user prompts for session history and context analysis.

        Payload fields:
            - prompt: Required. User prompt text
            - prompt_number: Optional. Sequence number in session

        Args:
            event: Hook event with prompt data

        Returns:
            Dict confirming prompt tracking

        Example:
            # Event dispatched when user submits prompt
            {
                "type": "prompt-submit",
                "payload": {
                    "prompt": "Implement user authentication",
                    "prompt_number": 5
                },
                "session_id": "session-abc-123",
                "correlation_id": "req-003"
            }
        """
        try:
            from agentpm.core.database.methods import sessions as session_methods

            prompt = event.payload.get("prompt")
            if not prompt:
                return {"status": "skipped", "message": "No prompt in payload"}

            # Update session metadata with prompt tracking
            session = session_methods.get_current_session(self.db)
            if not session:
                logger.warning("No active session for PROMPT_SUBMIT")
                return {"status": "warning", "message": "No active session"}

            # Track prompt in tool_specific metadata
            if not hasattr(session.metadata, 'tool_specific'):
                session.metadata.tool_specific = {}

            if 'prompts' not in session.metadata.tool_specific:
                session.metadata.tool_specific['prompts'] = []

            session.metadata.tool_specific['prompts'].append({
                'text': prompt[:200],  # Truncate for storage
                'timestamp': datetime.now().isoformat(),
                'prompt_number': event.payload.get('prompt_number'),
            })

            # Update session
            session_methods.update_session(self.db, session)

            logger.debug(f"Tracked prompt submit in session {event.session_id}")

            return {
                "status": "success",
                "message": "Prompt tracked",
                "prompt_count": len(session.metadata.tool_specific['prompts'])
            }

        except Exception as e:
            logger.error(f"Error handling PROMPT_SUBMIT: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def on_tool_result(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle TOOL_RESULT event.

        Tracks tool execution results for analytics and debugging.

        Payload fields:
            - tool_name: Required. Name of tool executed
            - success: Required. Whether tool succeeded
            - duration_ms: Optional. Execution duration
            - error: Optional. Error message if failed

        Args:
            event: Hook event with tool result

        Returns:
            Dict confirming tool result tracking

        Example:
            # Event dispatched when tool completes
            {
                "type": "tool-result",
                "payload": {
                    "tool_name": "Bash",
                    "success": true,
                    "duration_ms": 234
                },
                "session_id": "session-abc-123",
                "correlation_id": "req-004"
            }
        """
        try:
            from agentpm.core.database.methods import sessions as session_methods

            tool_name = event.payload.get("tool_name")
            success = event.payload.get("success", False)

            if not tool_name:
                return {"status": "skipped", "message": "No tool_name in payload"}

            # Update session metadata with tool usage
            session = session_methods.get_current_session(self.db)
            if not session:
                return {"status": "warning", "message": "No active session"}

            # Track tool usage in metadata
            if not hasattr(session.metadata, 'tool_specific'):
                session.metadata.tool_specific = {}

            if 'tool_usage' not in session.metadata.tool_specific:
                session.metadata.tool_specific['tool_usage'] = {}

            # Increment tool counter
            if tool_name not in session.metadata.tool_specific['tool_usage']:
                session.metadata.tool_specific['tool_usage'][tool_name] = {
                    'count': 0,
                    'failures': 0
                }

            session.metadata.tool_specific['tool_usage'][tool_name]['count'] += 1
            if not success:
                session.metadata.tool_specific['tool_usage'][tool_name]['failures'] += 1

            # Update session
            session_methods.update_session(self.db, session)

            logger.debug(
                f"Tracked tool result: {tool_name} "
                f"({'success' if success else 'failure'})"
            )

            return {
                "status": "success",
                "message": "Tool result tracked",
                "tool_usage": session.metadata.tool_specific['tool_usage']
            }

        except Exception as e:
            logger.error(f"Error handling TOOL_RESULT: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def on_pre_tool_use(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle PRE_TOOL_USE event.

        Called before tool execution. Can be used for validation or
        preparation.

        Payload fields:
            - tool_name: Required. Name of tool about to execute
            - tool_input: Optional. Tool input parameters

        Args:
            event: Hook event with pre-tool data

        Returns:
            Dict acknowledging pre-tool event
        """
        try:
            tool_name = event.payload.get("tool_name")
            logger.debug(f"Pre-tool use: {tool_name} in session {event.session_id}")

            return {
                "status": "success",
                "message": f"Pre-tool acknowledged: {tool_name}"
            }

        except Exception as e:
            logger.error(f"Error handling PRE_TOOL_USE: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def on_post_tool_use(self, event: HookEvent) -> Dict[str, Any]:
        """
        Handle POST_TOOL_USE event.

        Called after tool execution completes. Similar to TOOL_RESULT
        but provides different timing/context.

        Payload fields:
            - tool_name: Required. Name of completed tool
            - result: Optional. Tool result data

        Args:
            event: Hook event with post-tool data

        Returns:
            Dict acknowledging post-tool event
        """
        try:
            tool_name = event.payload.get("tool_name")
            logger.debug(f"Post-tool use: {tool_name} in session {event.session_id}")

            return {
                "status": "success",
                "message": f"Post-tool acknowledged: {tool_name}"
            }

        except Exception as e:
            logger.error(f"Error handling POST_TOOL_USE: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # Private helper methods

    def _load_previous_session_context(self, project_id: int) -> Dict[str, Any]:
        """
        Load context from most recent completed session.

        Provides handover information from previous work.

        Args:
            project_id: Project ID to query

        Returns:
            Dict with previous session context
        """
        try:
            from agentpm.core.database.methods import sessions as session_methods

            # Get most recent completed session
            sessions = session_methods.list_sessions(
                self.db,
                project_id=project_id,
                limit=1,
                active_only=False
            )

            if not sessions:
                return {"available": False, "message": "No previous sessions"}

            prev_session = sessions[0]

            # Extract handover information
            metadata_dict = {}
            if prev_session.metadata:
                metadata_dict = prev_session.metadata.model_dump() if hasattr(prev_session.metadata, 'model_dump') else {}

            handover = {
                "available": True,
                "session_id": prev_session.session_id,
                "ended_at": prev_session.ended_at,
                "duration_minutes": prev_session.duration_minutes,
                "work_items": metadata_dict.get('work_items_touched', []),
                "tasks": metadata_dict.get('tasks_completed', []),
                "summary": metadata_dict.get('tool_specific', {}).get('session_summary', ''),
            }

            return handover

        except Exception as e:
            logger.error(f"Error loading previous context: {e}", exc_info=True)
            return {"available": False, "error": str(e)}

    def _generate_session_summary(
        self, session: 'Session', payload: Dict[str, Any]
    ) -> str:
        """
        Generate session summary text.

        Combines session metrics with user-provided summary.

        Args:
            session: Session object
            payload: Event payload (may contain user summary)

        Returns:
            Generated summary text
        """
        try:
            parts = []

            # User-provided summary
            if payload.get('summary'):
                parts.append(payload['summary'])

            # Session metrics
            metadata = session.metadata
            if metadata:
                # Convert to dict if needed to access dynamic fields
                metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else {}

                work_items = metadata_dict.get('work_items_touched', [])
                if work_items:
                    parts.append(f"Work items: {len(work_items)}")

                tasks = metadata_dict.get('tasks_completed', [])
                if tasks:
                    parts.append(f"Tasks completed: {len(tasks)}")

                decisions = metadata_dict.get('decisions_made', [])
                if decisions:
                    parts.append(f"Decisions made: {len(decisions)}")

            if parts:
                return " | ".join(parts)
            else:
                return "Session completed"

        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return "Session completed (summary generation failed)"

    def _create_handover_document(self, session: 'Session') -> Dict[str, Any]:
        """
        Create handover document for next session.

        Summarizes work done and provides context for continuation.

        Args:
            session: Completed session

        Returns:
            Dict with handover information
        """
        try:
            handover = {
                "session_id": session.session_id,
                "duration_minutes": session.duration_minutes,
                "ended_at": session.ended_at,
                "work_completed": {},
                "next_steps": []
            }

            if session.metadata:
                # Convert to dict to access dynamic fields
                metadata_dict = session.metadata.model_dump() if hasattr(session.metadata, 'model_dump') else {}

                # Work items
                work_items = metadata_dict.get('work_items_touched', [])
                if work_items:
                    handover["work_completed"]["work_items"] = work_items

                # Tasks
                tasks = metadata_dict.get('tasks_completed', [])
                if tasks:
                    handover["work_completed"]["tasks"] = tasks

                # Decisions (for context)
                decisions = metadata_dict.get('decisions_made', [])
                if decisions:
                    handover["decisions"] = [
                        d.get('decision', '') if isinstance(d, dict) else str(d)
                        for d in decisions
                    ]

                # Tool usage (for debugging)
                tool_specific = metadata_dict.get('tool_specific', {})
                if tool_specific and 'tool_usage' in tool_specific:
                    handover["tool_usage"] = tool_specific['tool_usage']

            return handover

        except Exception as e:
            logger.error(f"Error creating handover: {e}", exc_info=True)
            return {
                "session_id": session.session_id,
                "error": str(e)
            }
