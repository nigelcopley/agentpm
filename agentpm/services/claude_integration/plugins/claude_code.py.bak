"""
Claude Code Plugin

Comprehensive plugin for Claude Code integration providing:
- Lifecycle hooks (session start/end, tool use, etc.)
- Memory management (context persistence)
- Slash commands (custom commands for Claude)
- Checkpointing (state snapshots)
- Subagent orchestration

This plugin consolidates all Claude Code capabilities into a single,
cohesive integration following the APM (Agent Project Manager) plugin pattern.

Example:
    from agentpm.services.claude_integration.plugins import get_registry
    from agentpm.services.claude_integration.plugins.claude_code import ClaudeCodePlugin

    registry = get_registry()
    plugin = ClaudeCodePlugin()
    registry.register_plugin(plugin)

    # Handle events
    result = plugin.handle({
        "type": "session-start",
        "payload": {"session_id": "abc123"},
        "session_id": "abc123",
        "correlation_id": "req-001"
    })
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from .base import BaseClaudePlugin, PluginCapability
from ..hooks.models import EventType, HookEvent, EventResult
from ..subagents import get_invocation_handler, get_subagent_registry
from ..tools.memory_tool import MemoryTool

logger = logging.getLogger(__name__)


class ClaudeCodePlugin(BaseClaudePlugin):
    """
    Claude Code integration plugin.

    Provides comprehensive Claude Code capabilities:
    - HOOKS: Lifecycle event handling (session, tools, etc.)
    - MEMORY: Persistent context management
    - COMMANDS: Slash command execution
    - CHECKPOINTING: State snapshot creation
    - SUBAGENTS: Subagent orchestration

    Pattern: Capability-based handler routing with event normalization

    Example:
        plugin = ClaudeCodePlugin()

        # Handle session start
        result = plugin.handle({
            "type": "session-start",
            "payload": {"session_id": "abc123"},
            "session_id": "abc123",
            "correlation_id": "req-001"
        })

        # Handle tool use
        result = plugin.handle({
            "type": "pre-tool-use",
            "payload": {"tool": "bash", "args": {...}},
            "session_id": "abc123",
            "correlation_id": "req-002"
        })
    """

    VERSION = "1.0.0"
    NAME = "claude-code"

    def __init__(self):
        """
        Initialize Claude Code plugin.

        Registers all supported capabilities and initializes internal state.
        """
        super().__init__(name=self.NAME)

        # Register all capabilities
        self.register_capability(PluginCapability.HOOKS)
        self.register_capability(PluginCapability.MEMORY)
        self.register_capability(PluginCapability.COMMANDS)
        self.register_capability(PluginCapability.CHECKPOINTING)
        self.register_capability(PluginCapability.SUBAGENTS)

        # Internal state
        self._initialized = False
        self._session_contexts: Dict[str, Dict[str, Any]] = {}
        self._command_handlers: Dict[str, callable] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

        # Subagent integration
        self._subagent_handler = get_invocation_handler()
        self._subagent_registry = get_subagent_registry()

        # Memory tool (initialized on first use)
        self._memory_tool: Optional[MemoryTool] = None

        logger.info(f"ClaudeCodePlugin initialized (version {self.VERSION})")

    def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle plugin input and route to appropriate capability handler.

        Routing strategy:
        - "type" field indicates event type → route to hooks handler
        - "command" field indicates command → route to commands handler
        - "scope" field indicates memory operation → route to memory handler
        - "checkpoint_id" field indicates checkpoint operation → route to checkpointing handler
        - "subagent" field indicates subagent operation → route to subagents handler

        Args:
            input_data: Plugin input dictionary with routing hints

        Returns:
            Plugin-specific output dictionary with "status" field

        Raises:
            ValueError: If input_data is invalid or missing required fields
            RuntimeError: If processing fails

        Example:
            # Hook event
            result = plugin.handle({
                "type": "session-start",
                "payload": {...},
                "session_id": "abc123",
                "correlation_id": "req-001"
            })

            # Command
            result = plugin.handle({
                "command": "checkpoint",
                "args": {"name": "before-refactor"},
                "session_id": "abc123"
            })

            # Memory operation
            result = plugin.handle({
                "scope": "session",
                "action": "get",
                "key": "last_prompt",
                "session_id": "abc123"
            })
        """
        try:
            # Initialize on first use
            if not self._initialized:
                self._initialize()

            # Route based on input structure
            # Note: Check subagent BEFORE checkpoint to avoid action="list" conflict
            if "type" in input_data:
                # Hook event
                return self._handle_hook_event(input_data)
            elif "command" in input_data:
                # Slash command
                return self._handle_command(input_data)
            elif "scope" in input_data:
                # Memory operation
                return self._handle_memory(input_data)
            elif "subagent" in input_data or input_data.get("action") == "invoke":
                # Subagent operation (check before checkpoint to avoid action="list" conflict)
                # Also route action="invoke" to subagent handler for natural language invocations
                return self._handle_subagent(input_data)
            elif "checkpoint_id" in input_data or input_data.get("action") in ["checkpoint", "restore", "list"]:
                # Checkpointing
                return self._handle_checkpoint(input_data)
            else:
                raise ValueError(
                    f"Unable to route input: missing routing field (type/command/scope/checkpoint_id/subagent). "
                    f"Input keys: {list(input_data.keys())}"
                )

        except Exception as e:
            logger.error(f"Error handling plugin input: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Plugin error: {str(e)}",
                "error": str(e)
            }

    def _initialize(self) -> None:
        """
        Initialize plugin on first use.

        Sets up:
        - Command handlers
        - Default memory scopes
        - Event subscriptions
        """
        logger.info("Initializing ClaudeCodePlugin handlers")

        # Register command handlers
        self._command_handlers = {
            "checkpoint": self._cmd_checkpoint,
            "restore": self._cmd_restore,
            "context": self._cmd_context,
            "subagent": self._cmd_subagent,
        }

        self._initialized = True
        logger.info("ClaudeCodePlugin initialization complete")

    def _handle_hook_event(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle lifecycle hook events.

        Processes events like session-start, session-end, tool-use, etc.

        Args:
            input_data: Event data with "type", "payload", "session_id", "correlation_id"

        Returns:
            Hook handling result

        Example:
            result = plugin._handle_hook_event({
                "type": "session-start",
                "payload": {"session_id": "abc123"},
                "session_id": "abc123",
                "correlation_id": "req-001"
            })
        """
        event_type = input_data.get("type")
        session_id = input_data.get("session_id")
        payload = input_data.get("payload", {})

        logger.debug(f"Handling hook event: {event_type} for session {session_id}")

        # Normalize to EventType if possible
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                # Allow custom event types
                pass

        # Route to specific handler
        if event_type == EventType.SESSION_START or event_type == "session-start":
            return self._on_session_start(session_id, payload)
        elif event_type == EventType.SESSION_END or event_type == "session-end":
            return self._on_session_end(session_id, payload)
        elif event_type == EventType.PROMPT_SUBMIT or event_type == "prompt-submit":
            return self._on_prompt_submit(session_id, payload)
        elif event_type == EventType.PRE_TOOL_USE or event_type == "pre-tool-use":
            return self._on_pre_tool_use(session_id, payload)
        elif event_type == EventType.POST_TOOL_USE or event_type == "post-tool-use":
            return self._on_post_tool_use(session_id, payload)
        elif event_type == EventType.TOOL_RESULT or event_type == "tool-result":
            return self._on_tool_result(session_id, payload)
        elif event_type == EventType.STOP or event_type == "stop":
            return self._on_stop(session_id, payload)
        elif event_type == EventType.SUBAGENT_STOP or event_type == "subagent-stop":
            return self._on_subagent_stop(session_id, payload)
        elif event_type == EventType.PRE_COMPACT or event_type == "pre-compact":
            return self._on_pre_compact(session_id, payload)
        elif event_type == EventType.NOTIFICATION or event_type == "notification":
            return self._on_notification(session_id, payload)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {
                "status": "success",
                "message": f"Event type {event_type} not handled",
                "data": {"event_type": str(event_type)}
            }

    def _on_session_start(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session-start event."""
        logger.info(f"Session started: {session_id}")

        # Initialize session context
        self._session_contexts[session_id] = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "metadata": payload,
            "prompts": [],
            "tool_uses": []
        }

        return {
            "status": "success",
            "message": f"Session {session_id} initialized",
            "data": {"session_id": session_id}
        }

    def _on_session_end(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session-end event."""
        logger.info(f"Session ended: {session_id}")

        # Cleanup session context
        if session_id in self._session_contexts:
            context = self._session_contexts[session_id]
            context["end_time"] = datetime.now().isoformat()

            # Archive context (in real implementation, persist to database)
            logger.debug(f"Archived session context for {session_id}")

            del self._session_contexts[session_id]

        return {
            "status": "success",
            "message": f"Session {session_id} ended",
            "data": {"session_id": session_id}
        }

    def _on_prompt_submit(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompt-submit event."""
        prompt = payload.get("prompt", "")
        logger.debug(f"Prompt submitted in session {session_id}: {prompt[:50]}...")

        # Track prompt in session context
        if session_id in self._session_contexts:
            self._session_contexts[session_id]["prompts"].append({
                "prompt": prompt,
                "timestamp": datetime.now().isoformat()
            })

        return {
            "status": "success",
            "message": "Prompt tracked",
            "data": {"prompt_length": len(prompt)}
        }

    def _on_pre_tool_use(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pre-tool-use event."""
        tool_name = payload.get("tool", "unknown")
        logger.debug(f"Pre-tool-use: {tool_name} in session {session_id}")

        return {
            "status": "success",
            "message": f"Pre-tool-use hook for {tool_name}",
            "data": {"tool": tool_name}
        }

    def _on_post_tool_use(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle post-tool-use event."""
        tool_name = payload.get("tool", "unknown")
        logger.debug(f"Post-tool-use: {tool_name} in session {session_id}")

        # Track tool use
        if session_id in self._session_contexts:
            self._session_contexts[session_id]["tool_uses"].append({
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            })

        return {
            "status": "success",
            "message": f"Post-tool-use hook for {tool_name}",
            "data": {"tool": tool_name}
        }

    def _on_tool_result(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool-result event."""
        logger.debug(f"Tool result in session {session_id}")

        return {
            "status": "success",
            "message": "Tool result tracked",
            "data": {}
        }

    def _on_stop(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stop event."""
        logger.info(f"Stop signal received for session {session_id}")

        return {
            "status": "success",
            "message": "Stop signal handled",
            "data": {"session_id": session_id}
        }

    def _on_subagent_stop(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subagent-stop event."""
        subagent_name = payload.get("subagent", "unknown")
        logger.info(f"Subagent {subagent_name} stopped in session {session_id}")

        return {
            "status": "success",
            "message": f"Subagent {subagent_name} stop handled",
            "data": {"subagent": subagent_name}
        }

    def _on_pre_compact(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pre-compact event."""
        logger.debug(f"Pre-compact hook for session {session_id}")

        return {
            "status": "success",
            "message": "Pre-compact hook executed",
            "data": {}
        }

    def _on_notification(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification event."""
        notification = payload.get("message", "")
        logger.info(f"Notification in session {session_id}: {notification}")

        return {
            "status": "success",
            "message": "Notification handled",
            "data": {"notification": notification}
        }

    def _handle_command(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle slash command execution.

        Args:
            input_data: Command data with "command", "args", "session_id"

        Returns:
            Command execution result

        Example:
            result = plugin._handle_command({
                "command": "checkpoint",
                "args": {"name": "before-refactor"},
                "session_id": "abc123"
            })
        """
        command = input_data.get("command")
        args = input_data.get("args", {})
        session_id = input_data.get("session_id")

        logger.debug(f"Handling command: {command} in session {session_id}")

        handler = self._command_handlers.get(command)
        if handler:
            return handler(session_id, args)
        else:
            return {
                "status": "error",
                "message": f"Unknown command: {command}",
                "error": f"Command '{command}' not registered"
            }

    def _cmd_checkpoint(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /checkpoint command."""
        checkpoint_name = args.get("name", f"checkpoint-{datetime.now().isoformat()}")
        logger.info(f"Creating checkpoint: {checkpoint_name} for session {session_id}")

        # Create checkpoint
        checkpoint_id = f"{session_id}-{checkpoint_name}"
        self._checkpoints[checkpoint_id] = {
            "checkpoint_id": checkpoint_id,
            "session_id": session_id,
            "name": checkpoint_name,
            "timestamp": datetime.now().isoformat(),
            "context": self._session_contexts.get(session_id, {}).copy()
        }

        return {
            "status": "success",
            "message": f"Checkpoint '{checkpoint_name}' created",
            "data": {"checkpoint_id": checkpoint_id}
        }

    def _cmd_restore(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /restore command."""
        checkpoint_id = args.get("checkpoint_id")
        logger.info(f"Restoring checkpoint: {checkpoint_id} for session {session_id}")

        if checkpoint_id in self._checkpoints:
            checkpoint = self._checkpoints[checkpoint_id]
            self._session_contexts[session_id] = checkpoint["context"].copy()

            return {
                "status": "success",
                "message": f"Restored checkpoint '{checkpoint_id}'",
                "data": {"checkpoint_id": checkpoint_id}
            }
        else:
            return {
                "status": "error",
                "message": f"Checkpoint '{checkpoint_id}' not found",
                "error": "Checkpoint does not exist"
            }

    def _cmd_context(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /context command."""
        logger.debug(f"Retrieving context for session {session_id}")

        context = self._session_contexts.get(session_id, {})

        return {
            "status": "success",
            "message": "Context retrieved",
            "data": {"context": context}
        }

    def _cmd_subagent(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /subagent command."""
        subagent_name = args.get("name", "unknown")
        logger.info(f"Subagent command: {subagent_name} in session {session_id}")

        return {
            "status": "success",
            "message": f"Subagent '{subagent_name}' command handled",
            "data": {"subagent": subagent_name}
        }

    def _handle_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory operations.

        Supports two scopes:
        - "session": Ephemeral session context (in-memory)
        - "aipm": Persistent AIPM memory files (database-backed)

        Args:
            input_data: Memory data with "scope", "action", "key", "value", "session_id"

        Returns:
            Memory operation result

        Example:
            # Session memory (ephemeral)
            result = plugin._handle_memory({
                "scope": "session",
                "action": "get",
                "key": "last_prompt",
                "session_id": "abc123"
            })

            # AIPM memory (persistent)
            result = plugin._handle_memory({
                "scope": "aipm",
                "action": "read",
                "memory_type": "RULES",
                "session_id": "abc123"
            })

            # Search AIPM memory
            result = plugin._handle_memory({
                "scope": "aipm",
                "action": "search",
                "query": "quality gates",
                "session_id": "abc123"
            })
        """
        scope = input_data.get("scope")
        action = input_data.get("action")
        session_id = input_data.get("session_id")

        logger.debug(f"Memory operation: {action} {scope} in session {session_id}")

        # Route based on scope
        if scope == "session":
            # Session-scoped memory (ephemeral)
            return self._handle_session_memory(input_data)
        elif scope == "aipm":
            # AIPM memory files (persistent)
            return self._handle_aipm_memory(input_data)
        else:
            return {
                "status": "error",
                "message": f"Unknown memory scope: {scope}",
                "error": f"Scope '{scope}' not supported. Use 'session' or 'aipm'."
            }

    def _handle_session_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session-scoped memory operations (ephemeral)."""
        action = input_data.get("action")
        key = input_data.get("key")
        value = input_data.get("value")
        session_id = input_data.get("session_id")

        if action == "get":
            # Get value from session context
            context = self._session_contexts.get(session_id, {})
            result_value = context.get(key)

            return {
                "status": "success",
                "message": f"Retrieved session.{key}",
                "data": {"key": key, "value": result_value}
            }
        elif action == "set":
            # Set value in session context
            if session_id not in self._session_contexts:
                self._session_contexts[session_id] = {}

            self._session_contexts[session_id][key] = value

            return {
                "status": "success",
                "message": f"Set session.{key}",
                "data": {"key": key, "value": value}
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown session memory action: {action}",
                "error": f"Action '{action}' not supported. Use 'get' or 'set'."
            }

    def _handle_aipm_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AIPM memory file operations (persistent)."""
        try:
            # Initialize memory tool if needed
            if self._memory_tool is None:
                from agentpm.core.database.service import get_db
                db = get_db()
                self._memory_tool = MemoryTool(db)

            action = input_data.get("action")

            if action == "read":
                # Read memory file
                memory_type = input_data.get("memory_type")
                query = input_data.get("query")

                if not memory_type:
                    return {
                        "status": "error",
                        "message": "Missing 'memory_type' field",
                        "error": "memory_type required for read action"
                    }

                content = self._memory_tool.read_memory(memory_type, query=query)

                return {
                    "status": "success",
                    "message": f"Read AIPM memory: {memory_type}",
                    "data": {
                        "memory_type": memory_type,
                        "content": content,
                        "content_length": len(content)
                    }
                }

            elif action == "search":
                # Search memory files
                query = input_data.get("query")
                memory_types = input_data.get("memory_types")
                limit = input_data.get("limit", 10)

                if not query:
                    return {
                        "status": "error",
                        "message": "Missing 'query' field",
                        "error": "query required for search action"
                    }

                results = self._memory_tool.search_memory(
                    query=query,
                    memory_types=memory_types,
                    limit=limit
                )

                return {
                    "status": "success",
                    "message": f"Found {len(results)} results for '{query}'",
                    "data": {
                        "query": query,
                        "results": results,
                        "result_count": len(results)
                    }
                }

            elif action == "list":
                # List available memory types
                memory_types = self._memory_tool.list_memory_types()

                return {
                    "status": "success",
                    "message": f"Found {len(memory_types)} memory types",
                    "data": {
                        "memory_types": memory_types
                    }
                }

            elif action == "stats":
                # Get memory statistics
                stats = self._memory_tool.get_memory_stats()

                return {
                    "status": "success",
                    "message": "Memory statistics retrieved",
                    "data": stats
                }

            else:
                return {
                    "status": "error",
                    "message": f"Unknown AIPM memory action: {action}",
                    "error": f"Action '{action}' not supported. Use: read, search, list, stats."
                }

        except Exception as e:
            logger.error(f"Error handling AIPM memory operation: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "AIPM memory operation failed",
                "error": str(e)
            }

    def _handle_checkpoint(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle checkpointing operations.

        Args:
            input_data: Checkpoint data with "action", "checkpoint_id", "session_id"

        Returns:
            Checkpoint operation result

        Example:
            # Create
            result = plugin._handle_checkpoint({
                "action": "checkpoint",
                "session_id": "abc123"
            })

            # Restore
            result = plugin._handle_checkpoint({
                "action": "restore",
                "checkpoint_id": "abc123-checkpoint-001",
                "session_id": "abc123"
            })
        """
        action = input_data.get("action")
        checkpoint_id = input_data.get("checkpoint_id")
        session_id = input_data.get("session_id")

        logger.debug(f"Checkpoint operation: {action} for session {session_id}")

        if action == "checkpoint":
            # Create checkpoint
            return self._cmd_checkpoint(session_id, {})
        elif action == "restore":
            # Restore checkpoint
            return self._cmd_restore(session_id, {"checkpoint_id": checkpoint_id})
        elif action == "list":
            # List checkpoints
            session_checkpoints = [
                cp for cp in self._checkpoints.values()
                if cp["session_id"] == session_id
            ]

            return {
                "status": "success",
                "message": f"Found {len(session_checkpoints)} checkpoints",
                "data": {"checkpoints": session_checkpoints}
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown checkpoint action: {action}",
                "error": f"Action '{action}' not supported"
            }

    def _handle_subagent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subagent operations.

        Integrates with SubagentInvocationHandler to execute AIPM subagents.

        Args:
            input_data: Subagent data with:
                - "subagent": Subagent name
                - "action": Action to perform (invoke/list/get-guide)
                - "task_description": Task description (for invoke)
                - "context": Context data (for invoke)
                - "session_id": Session identifier
                - "correlation_id": Request correlation ID (optional)

        Returns:
            Subagent operation result

        Example:
            # Invoke subagent
            result = plugin._handle_subagent({
                "subagent": "test-implementer",
                "action": "invoke",
                "task_description": "Create tests for UserService",
                "context": {"service": "UserService"},
                "session_id": "abc123",
                "correlation_id": "req-001"
            })

            # Get invocation guide
            result = plugin._handle_subagent({
                "action": "get-guide",
                "session_id": "abc123"
            })
        """
        subagent = input_data.get("subagent")
        action = input_data.get("action", "invoke")
        session_id = input_data.get("session_id")
        correlation_id = input_data.get("correlation_id", f"claude-{session_id}")

        logger.info(f"Subagent operation: {action} {subagent} in session {session_id}")

        # Handle different actions
        if action == "invoke":
            # Invoke subagent
            task_description = input_data.get("task_description", "")
            context = input_data.get("context", {})

            if not subagent:
                return {
                    "status": "error",
                    "message": "Subagent name required for invoke action",
                    "error": "Missing 'subagent' field"
                }

            if not task_description:
                return {
                    "status": "error",
                    "message": "Task description required for invoke action",
                    "error": "Missing 'task_description' field"
                }

            # Use sync version since we're in sync context
            result = self._subagent_handler.invoke_subagent_sync(
                subagent_name=subagent,
                task_description=task_description,
                context=context,
                session_id=session_id,
                correlation_id=correlation_id
            )

            return {
                "status": "success" if result.success else "error",
                "message": result.message,
                "data": {
                    "subagent": result.subagent_name,
                    "result": result.data,
                    "artifacts": result.artifacts,
                    "errors": result.errors
                }
            }

        elif action == "list":
            # List available subagents
            subagents = self._subagent_registry.list_subagents()
            return {
                "status": "success",
                "message": f"Found {len(subagents)} registered subagents",
                "data": {
                    "subagents": [
                        {
                            "name": spec.name,
                            "description": spec.description,
                            "capabilities": [
                                cap.value if hasattr(cap, "value") else cap
                                for cap in spec.capabilities
                            ],
                            "tier": spec.tier
                        }
                        for spec in subagents
                    ]
                }
            }

        elif action == "get-guide":
            # Get invocation guide
            guide = self._subagent_registry.get_invocation_guide()
            return {
                "status": "success",
                "message": "Generated invocation guide",
                "data": {
                    "guide": guide
                }
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown subagent action: {action}",
                "error": f"Action '{action}' not supported. Use: invoke, list, get-guide"
            }

    def get_version(self) -> str:
        """Get plugin version."""
        return self.VERSION

    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session context for debugging/testing.

        Args:
            session_id: Session identifier

        Returns:
            Session context or None if not found
        """
        return self._session_contexts.get(session_id)

    def clear_session_context(self, session_id: str) -> None:
        """
        Clear session context (useful for testing).

        Args:
            session_id: Session identifier
        """
        if session_id in self._session_contexts:
            del self._session_contexts[session_id]
            logger.debug(f"Cleared session context for {session_id}")
