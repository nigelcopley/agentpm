"""
Slash Command Handlers

Implementation of AIPM slash commands.

Provides:
- /aipm:context - Load AIPM context
- /aipm:status - Show project status
- /aipm:memory - Manage memory files
- /aipm:checkpoint - Create checkpoints

Pattern: Handler functions with database access
"""

from __future__ import annotations

import logging
import argparse
from typing import TYPE_CHECKING, List, Dict, Any
from datetime import datetime

from .models import CommandResult, CommandStatus, CommandError

if TYPE_CHECKING:
    from agentpm.core.database.service import DatabaseService

logger = logging.getLogger(__name__)


class CommandHandlers:
    """
    Handler class for AIPM slash commands.

    Provides stateful handlers with database access.

    Example:
        db = DatabaseService("path/to/db")
        handlers = CommandHandlers(db)

        # Use handlers with registry
        registry.register(
            name="aipm:context",
            handler=handlers.context,
            ...
        )
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize command handlers.

        Args:
            db: Database service instance (required)
        """
        self.db = db
        logger.debug("CommandHandlers initialized")

    def context(self, args: List[str]) -> CommandResult:
        """
        Handle /aipm:context command.

        Load AIPM context for current session.

        Args:
            args: Command arguments:
                --work-item=ID : Load specific work item context
                --task=ID : Load specific task context
                --full : Load full hierarchical context

        Returns:
            CommandResult with context data

        Example:
            /aipm:context
            /aipm:context --work-item=123
            /aipm:context --task=456 --full
        """
        try:
            # Parse arguments
            parser = argparse.ArgumentParser(prog="aipm:context")
            parser.add_argument("--work-item", type=int, help="Work item ID")
            parser.add_argument("--task", type=int, help="Task ID")
            parser.add_argument("--full", action="store_true", help="Full context")

            try:
                parsed = parser.parse_args(args)
            except SystemExit:
                # argparse calls sys.exit on error
                raise CommandError(
                    command="aipm:context",
                    message="Invalid arguments. Usage: /aipm:context [--work-item=ID] [--task=ID] [--full]"
                )

            # Load context based on arguments
            context_data = {}

            if parsed.work_item:
                # Load work item context
                context_data = self._load_work_item_context(parsed.work_item, parsed.full)
            elif parsed.task:
                # Load task context
                context_data = self._load_task_context(parsed.task, parsed.full)
            else:
                # Load current session context
                context_data = self._load_current_context()

            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"Context loaded: {len(context_data)} items",
                data=context_data
            )

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error in context command: {e}", exc_info=True)
            raise CommandError(
                command="aipm:context",
                message=str(e)
            )

    def status(self, args: List[str]) -> CommandResult:
        """
        Handle /aipm:status command.

        Show APM project status with active work items, tasks, and progress.

        Args:
            args: Command arguments:
                --detailed : Show detailed status
                --work-items-only : Show only work items
                --tasks-only : Show only tasks

        Returns:
            CommandResult with status data

        Example:
            /aipm:status
            /aipm:status --detailed
            /aipm:status --work-items-only
        """
        try:
            # Parse arguments
            parser = argparse.ArgumentParser(prog="aipm:status")
            parser.add_argument("--detailed", action="store_true", help="Detailed status")
            parser.add_argument("--work-items-only", action="store_true", help="Work items only")
            parser.add_argument("--tasks-only", action="store_true", help="Tasks only")

            try:
                parsed = parser.parse_args(args)
            except SystemExit:
                raise CommandError(
                    command="aipm:status",
                    message="Invalid arguments. Usage: /aipm:status [--detailed] [--work-items-only] [--tasks-only]"
                )

            # Build status data
            status_data = {}

            if not parsed.tasks_only:
                # Get work items
                from agentpm.core.database.methods import work_items as wi_methods

                active_wis = wi_methods.list_work_items(
                    self.db,
                    status="active",
                    limit=20
                )

                status_data["work_items"] = {
                    "active": len(active_wis),
                    "items": [
                        {
                            "id": wi.id,
                            "name": wi.name,
                            "type": wi.type,
                            "phase": wi.phase,
                            "status": wi.status
                        }
                        for wi in active_wis
                    ]
                }

            if not parsed.work_items_only:
                # Get tasks
                from agentpm.core.database.methods import tasks as task_methods

                active_tasks = task_methods.list_tasks(
                    self.db,
                    status="active",
                    limit=20
                )

                ready_tasks = task_methods.list_tasks(
                    self.db,
                    status="ready",
                    limit=20
                )

                status_data["tasks"] = {
                    "active": len(active_tasks),
                    "ready": len(ready_tasks),
                    "active_items": [
                        {
                            "id": task.id,
                            "objective": task.objective,
                            "type": task.type,
                            "status": task.status
                        }
                        for task in active_tasks
                    ],
                    "ready_items": [
                        {
                            "id": task.id,
                            "objective": task.objective,
                            "type": task.type,
                            "status": task.status
                        }
                        for task in ready_tasks
                    ]
                }

            # Add session info if available
            from agentpm.core.database.methods import sessions as session_methods
            current_session = session_methods.get_current_session(self.db)

            if current_session:
                status_data["session"] = {
                    "id": current_session.id,
                    "session_id": current_session.session_id,
                    "started_at": current_session.started_at,
                    "duration_minutes": current_session.duration_minutes or 0
                }

            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"Status loaded: {len(status_data)} sections",
                data=status_data
            )

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error in status command: {e}", exc_info=True)
            raise CommandError(
                command="aipm:status",
                message=str(e)
            )

    def memory(self, args: List[str]) -> CommandResult:
        """
        Handle /aipm:memory command.

        Generate or show memory files for context persistence.

        Args:
            args: Command arguments:
                generate : Generate memory files
                --all : Generate all memory files
                status : Show memory file status

        Returns:
            CommandResult with memory operation result

        Example:
            /aipm:memory status
            /aipm:memory generate --all
        """
        try:
            # Parse arguments
            if not args:
                action = "status"
            else:
                action = args[0]

            result_data = {}

            if action == "generate":
                # Generate memory files
                generate_all = "--all" in args

                from agentpm.services.memory.generator import MemoryGenerator
                generator = MemoryGenerator(self.db)

                if generate_all:
                    # Generate all memory types
                    generator.generate_all()
                    result_data["generated"] = "all"
                    result_data["files"] = [
                        ".agentpm/MEMORY/PROJECT.md",
                        ".agentpm/MEMORY/WORK_ITEMS.md",
                        ".agentpm/MEMORY/TASKS.md",
                        ".agentpm/MEMORY/RECENT_PROGRESS.md"
                    ]
                else:
                    # Generate current context only
                    generator.generate_current_context()
                    result_data["generated"] = "current"
                    result_data["files"] = [".agentpm/MEMORY/CURRENT_CONTEXT.md"]

                message = f"Memory files generated: {result_data['generated']}"

            elif action == "status":
                # Show memory file status
                import os

                memory_dir = ".agentpm/MEMORY"
                result_data["directory"] = memory_dir
                result_data["exists"] = os.path.exists(memory_dir)

                if result_data["exists"]:
                    files = os.listdir(memory_dir)
                    result_data["files"] = [
                        {
                            "name": f,
                            "size": os.path.getsize(os.path.join(memory_dir, f)),
                            "modified": datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(memory_dir, f))
                            ).isoformat()
                        }
                        for f in files if f.endswith(".md")
                    ]
                    result_data["count"] = len(result_data["files"])

                message = f"Memory status: {result_data.get('count', 0)} files"

            else:
                raise CommandError(
                    command="aipm:memory",
                    message=f"Unknown action: {action}. Use 'generate' or 'status'"
                )

            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=message,
                data=result_data
            )

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error in memory command: {e}", exc_info=True)
            raise CommandError(
                command="aipm:memory",
                message=str(e)
            )

    def checkpoint(self, args: List[str]) -> CommandResult:
        """
        Handle /aipm:checkpoint command.

        Create session checkpoint for state preservation with full state capture.

        Args:
            args: Command arguments:
                --name=NAME : Checkpoint name
                --message=MSG : Checkpoint message
                --list : List all checkpoints
                --restore=ID : Restore checkpoint by ID

        Returns:
            CommandResult with checkpoint data

        Example:
            /aipm:checkpoint
            /aipm:checkpoint --name="before-refactor"
            /aipm:checkpoint --name="feature-complete" --message="All tests passing"
            /aipm:checkpoint --list
            /aipm:checkpoint --restore=5
        """
        try:
            # Parse arguments
            parser = argparse.ArgumentParser(prog="aipm:checkpoint")
            parser.add_argument("--name", type=str, help="Checkpoint name")
            parser.add_argument("--message", type=str, help="Checkpoint message")
            parser.add_argument("--list", action="store_true", help="List checkpoints")
            parser.add_argument("--restore", type=int, help="Restore checkpoint ID")

            try:
                parsed = parser.parse_args(args)
            except SystemExit:
                raise CommandError(
                    command="aipm:checkpoint",
                    message="Invalid arguments. Usage: /aipm:checkpoint [--name=NAME] [--message=MSG] [--list] [--restore=ID]"
                )

            # Get current session
            from agentpm.core.database.methods import sessions as session_methods
            current_session = session_methods.get_current_session(self.db)

            if not current_session:
                raise CommandError(
                    command="aipm:checkpoint",
                    message="No active session. Start a session first."
                )

            # Import checkpoint manager
            from agentpm.providers.anthropic.claude_code.runtime.checkpoints import CheckpointManager
            manager = CheckpointManager(self.db)

            # Handle list command
            if parsed.list:
                checkpoints = manager.list_checkpoints(session_id=current_session.id, limit=20)

                checkpoint_data = {
                    "session_id": current_session.session_id,
                    "count": len(checkpoints),
                    "checkpoints": [
                        {
                            "id": cp.id,
                            "name": cp.checkpoint_name,
                            "created_at": cp.created_at.isoformat(),
                            "size_bytes": cp.size_bytes,
                            "restore_count": cp.restore_count,
                            "notes_preview": cp.notes_preview
                        }
                        for cp in checkpoints
                    ]
                }

                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=f"Found {len(checkpoints)} checkpoint(s)",
                    data=checkpoint_data
                )

            # Handle restore command
            if parsed.restore:
                checkpoint_id = parsed.restore

                # Restore checkpoint
                success = manager.restore_checkpoint(checkpoint_id)

                if success:
                    checkpoint = manager.get_checkpoint(checkpoint_id)
                    return CommandResult(
                        status=CommandStatus.SUCCESS,
                        message=f"Checkpoint restored: {checkpoint.checkpoint_name}",
                        data={
                            "id": checkpoint.id,
                            "name": checkpoint.checkpoint_name,
                            "restored_at": datetime.now().isoformat()
                        }
                    )
                else:
                    raise CommandError(
                        command="aipm:checkpoint",
                        message=f"Failed to restore checkpoint {checkpoint_id}"
                    )

            # Handle create checkpoint (default)
            checkpoint_name = parsed.name or f"checkpoint-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            checkpoint_message = parsed.message or "Manual checkpoint"

            # Create checkpoint with full state capture
            checkpoint = manager.create_checkpoint(
                session_id=current_session.id,
                name=checkpoint_name,
                notes=checkpoint_message,
                created_by="claude-code"
            )

            checkpoint_data = {
                "id": checkpoint.id,
                "name": checkpoint.checkpoint_name,
                "message": checkpoint.session_notes,
                "session_id": current_session.session_id,
                "created_at": checkpoint.created_at.isoformat(),
                "size_bytes": checkpoint.size_bytes,
                "work_items_count": len(checkpoint.work_items_snapshot),
                "tasks_count": len(checkpoint.tasks_snapshot)
            }

            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"Checkpoint created: {checkpoint_name}",
                data=checkpoint_data
            )

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error in checkpoint command: {e}", exc_info=True)
            raise CommandError(
                command="aipm:checkpoint",
                message=str(e)
            )

    # Private helper methods

    def _load_work_item_context(self, work_item_id: int, full: bool = False) -> Dict[str, Any]:
        """Load work item context."""
        from agentpm.core.database.methods import work_items as wi_methods

        wi = wi_methods.get_work_item(self.db, work_item_id)
        if not wi:
            raise CommandError(
                command="aipm:context",
                message=f"Work item {work_item_id} not found"
            )

        context = {
            "entity_type": "work_item",
            "id": wi.id,
            "name": wi.name,
            "type": wi.type,
            "phase": wi.phase,
            "status": wi.status,
            "business_context": wi.business_context,
            "acceptance_criteria": wi.acceptance_criteria
        }

        if full:
            # Add tasks
            from agentpm.core.database.methods import tasks as task_methods
            tasks = task_methods.list_tasks(self.db, work_item_id=work_item_id)
            context["tasks"] = [
                {
                    "id": t.id,
                    "objective": t.objective,
                    "type": t.type,
                    "status": t.status
                }
                for t in tasks
            ]

        return context

    def _load_task_context(self, task_id: int, full: bool = False) -> Dict[str, Any]:
        """Load task context."""
        from agentpm.core.database.methods import tasks as task_methods

        task = task_methods.get_task(self.db, task_id)
        if not task:
            raise CommandError(
                command="aipm:context",
                message=f"Task {task_id} not found"
            )

        context = {
            "entity_type": "task",
            "id": task.id,
            "objective": task.objective,
            "type": task.type,
            "status": task.status,
            "acceptance_criteria": task.acceptance_criteria
        }

        if full and task.work_item_id:
            # Add work item context
            from agentpm.core.database.methods import work_items as wi_methods
            wi = wi_methods.get_work_item(self.db, task.work_item_id)
            if wi:
                context["work_item"] = {
                    "id": wi.id,
                    "name": wi.name,
                    "type": wi.type,
                    "phase": wi.phase
                }

        return context

    def _load_current_context(self) -> Dict[str, Any]:
        """Load current session context."""
        from agentpm.core.database.methods import sessions as session_methods

        current_session = session_methods.get_current_session(self.db)

        if not current_session:
            return {"message": "No active session"}

        context = {
            "session": {
                "id": current_session.id,
                "session_id": current_session.session_id,
                "started_at": current_session.started_at,
                "duration_minutes": current_session.duration_minutes or 0
            }
        }

        # Add active work items
        from agentpm.core.database.methods import work_items as wi_methods
        active_wis = wi_methods.list_work_items(self.db, status="active", limit=5)

        context["active_work_items"] = [
            {"id": wi.id, "name": wi.name, "phase": wi.phase}
            for wi in active_wis
        ]

        # Add active tasks
        from agentpm.core.database.methods import tasks as task_methods
        active_tasks = task_methods.list_tasks(self.db, status="active", limit=5)

        context["active_tasks"] = [
            {"id": t.id, "objective": t.objective, "type": t.type}
            for t in active_tasks
        ]

        return context
