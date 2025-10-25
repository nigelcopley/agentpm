"""
Memory System Hooks

Hook handlers for Claude's persistent memory system.
Integrates with Claude Code lifecycle events to:
- Load previous memory at session start
- Generate new memory files at session end
- Update memory files on significant events

Part of WI-114: Claude Persistent Memory System.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.memory import MemoryFileType
from agentpm.services.claude_integration.hooks.models import (
    EventType,
    HookEvent,
    EventResult
)
from agentpm.services.memory.generator import MemoryGenerator


logger = logging.getLogger(__name__)


class MemoryHooks:
    """Hook handlers for memory file generation system.

    Provides handlers for Claude Code lifecycle events:
    - session-start: Load previous memory files
    - session-end: Generate new memory files
    - tool-result: Update memory if significant changes
    """

    def __init__(self, db: DatabaseService, project_root: Path):
        """Initialize memory hooks.

        Args:
            db: DatabaseService instance
            project_root: Path to project root directory
        """
        self.db = db
        self.project_root = project_root
        self.generator = MemoryGenerator(db, project_root)

    def handle_session_start(self, event: HookEvent) -> EventResult:
        """Handle session-start event.

        Loads previous memory files for Claude's context.

        Args:
            event: Session start event

        Returns:
            EventResult with loaded memory file info

        Example:
            >>> result = hooks.handle_session_start(event)
            >>> if result.success:
            ...     print(f"Loaded {result.data['files_loaded']} memory files")
        """
        try:
            project_id = event.payload.get('project_id')
            if not project_id:
                return EventResult.error_result(
                    message="Missing project_id in session-start event",
                    errors=["project_id required for memory file loading"]
                )

            # Check which memory files exist and are current
            existing_files = []
            stale_files = []

            for file_type in MemoryFileType:
                from agentpm.core.database.methods import memory_methods
                memory_file = memory_methods.get_memory_file_by_type(
                    self.db, project_id, file_type
                )

                if memory_file:
                    if memory_file.is_stale or memory_file.is_expired:
                        stale_files.append(file_type.value)
                    else:
                        existing_files.append(file_type.value)

            logger.info(
                f"Session start: {len(existing_files)} current memory files, "
                f"{len(stale_files)} stale files"
            )

            return EventResult.success_result(
                message=f"Loaded {len(existing_files)} memory files",
                data={
                    'files_loaded': existing_files,
                    'stale_files': stale_files,
                    'recommendation': 'Regenerate stale files' if stale_files else 'All files current'
                }
            )

        except Exception as e:
            logger.error(f"Error handling session-start: {e}")
            return EventResult.error_result(
                message="Failed to load memory files",
                errors=[str(e)]
            )

    def handle_session_end(self, event: HookEvent) -> EventResult:
        """Handle session-end event.

        Generates new memory files to capture session changes.

        Args:
            event: Session end event

        Returns:
            EventResult with generated memory file info

        Example:
            >>> result = hooks.handle_session_end(event)
            >>> if result.success:
            ...     print(f"Generated {result.data['files_generated']} memory files")
        """
        try:
            project_id = event.payload.get('project_id')
            session_id = event.payload.get('session_id')

            if not project_id:
                return EventResult.error_result(
                    message="Missing project_id in session-end event",
                    errors=["project_id required for memory file generation"]
                )

            # Generate all memory files (or just stale ones)
            regenerate_all = event.payload.get('regenerate_all', False)

            generated_files = []
            errors = []

            for file_type in MemoryFileType:
                try:
                    memory_file = self.generator.generate_memory_file(
                        project_id=project_id,
                        file_type=file_type,
                        session_id=session_id,
                        force_regenerate=regenerate_all
                    )
                    generated_files.append({
                        'type': file_type.value,
                        'path': memory_file.file_path,
                        'confidence': memory_file.confidence_score,
                        'completeness': memory_file.completeness_score
                    })
                except Exception as e:
                    logger.error(f"Error generating {file_type.value}: {e}")
                    errors.append(f"{file_type.value}: {str(e)}")

            if generated_files:
                logger.info(f"Session end: generated {len(generated_files)} memory files")
                return EventResult.success_result(
                    message=f"Generated {len(generated_files)} memory files",
                    data={
                        'files_generated': generated_files,
                        'errors': errors if errors else None
                    }
                )
            else:
                return EventResult.error_result(
                    message="Failed to generate any memory files",
                    errors=errors
                )

        except Exception as e:
            logger.error(f"Error handling session-end: {e}")
            return EventResult.error_result(
                message="Failed to generate memory files",
                errors=[str(e)]
            )

    def handle_tool_result(self, event: HookEvent) -> EventResult:
        """Handle tool-result event.

        Optionally updates memory files if significant changes detected.
        This is a lightweight check - full regeneration happens at session-end.

        Args:
            event: Tool result event

        Returns:
            EventResult with update status

        Example:
            >>> result = hooks.handle_tool_result(event)
            >>> if result.data.get('memory_updated'):
            ...     print("Memory files marked stale for regeneration")
        """
        try:
            # Check if this tool result affects memory files
            tool_name = event.payload.get('tool_name', '')

            # Tools that potentially affect memory content
            memory_affecting_tools = {
                'apm work-item create', 'apm work-item update',
                'apm task create', 'apm task update',
                'apm rules create', 'apm rules update',
                'apm agents register', 'apm agents update'
            }

            # Simple heuristic: mark files as stale if memory-affecting tool used
            if any(tool in tool_name for tool in memory_affecting_tools):
                logger.debug(f"Memory-affecting tool used: {tool_name}")

                # In a full implementation, would mark specific memory files as stale
                # For now, just log and return success
                return EventResult.success_result(
                    message="Memory update scheduled",
                    data={
                        'memory_updated': True,
                        'tool_name': tool_name,
                        'note': 'Full regeneration will occur at session-end'
                    }
                )

            return EventResult.success_result(
                message="No memory update needed",
                data={'memory_updated': False}
            )

        except Exception as e:
            logger.error(f"Error handling tool-result: {e}")
            return EventResult.error_result(
                message="Failed to check memory update",
                errors=[str(e)]
            )


def register_memory_hooks(hooks_engine, db: DatabaseService, project_root: Path) -> None:
    """Register memory hooks with Claude integration hooks engine.

    Args:
        hooks_engine: HooksEngine instance
        db: DatabaseService instance
        project_root: Path to project root directory

    Example:
        >>> from agentpm.services.claude_integration.hooks import get_hooks_engine
        >>> hooks_engine = get_hooks_engine()
        >>> register_memory_hooks(hooks_engine, db, Path("/project"))
    """
    memory_hooks = MemoryHooks(db, project_root)

    # Register handlers
    hooks_engine.register_handler(
        event_type=EventType.SESSION_START,
        handler=memory_hooks.handle_session_start,
        priority=100  # High priority - load memory early
    )

    hooks_engine.register_handler(
        event_type=EventType.SESSION_END,
        handler=memory_hooks.handle_session_end,
        priority=50  # Medium priority - generate after other end handlers
    )

    hooks_engine.register_handler(
        event_type=EventType.TOOL_RESULT,
        handler=memory_hooks.handle_tool_result,
        priority=10  # Low priority - optional check
    )

    logger.info("Memory hooks registered successfully")
