"""
Cursor Provider Hooks - Lifecycle Event Handlers

Event-driven integration with Cursor IDE through AIPM hooks system.
Responds to provider lifecycle events to maintain synchronization.

Pattern: Plugin-based event handling with database updates
Database-first: All state changes tracked in database
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from agentpm.core.database.service import DatabaseService
from agentpm.services.claude_integration.hooks import (
    HookEvent,
    EventResult,
    EventType,
    get_hooks_engine,
)
from agentpm.core.database.models.provider import (
    CursorConfig,
    ProviderType,
)
from agentpm.core.database.methods.provider_methods import (
    InstallationMethods,
    TemplateMethods,
)


logger = logging.getLogger(__name__)


class CursorHooks:
    """
    Cursor provider lifecycle hooks.

    Integrates with AIPM hooks engine to respond to:
    - Provider installation/uninstallation
    - Project context changes
    - Rule updates
    - Memory synchronization

    Example:
        db = DatabaseService()
        hooks = CursorHooks(db)
        hooks.register_all()

        # Hooks now respond to events automatically
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize Cursor hooks.

        Args:
            db: Database service instance
        """
        self.db = db
        self._engine = get_hooks_engine()
        self._registered = False

    def register_all(self) -> None:
        """
        Register all Cursor provider hooks with engine.

        Registers handlers for:
        - provider-install
        - provider-uninstall
        - context-change
        - rule-update
        """
        if self._registered:
            logger.warning("Cursor hooks already registered")
            return

        # Provider lifecycle events
        self._engine.register_handler("provider-install", self.on_provider_install)
        self._engine.register_handler("provider-uninstall", self.on_provider_uninstall)

        # Project events
        self._engine.register_handler("context-change", self.on_context_change)
        self._engine.register_handler("rule-update", self.on_rule_update)

        self._registered = True
        logger.info("Registered Cursor provider hooks")

    def unregister_all(self) -> None:
        """
        Unregister all hooks.

        Useful for cleanup or testing.
        """
        if not self._registered:
            return

        self._engine.unregister_handler("provider-install", self.on_provider_install)
        self._engine.unregister_handler("provider-uninstall", self.on_provider_uninstall)
        self._engine.unregister_handler("context-change", self.on_context_change)
        self._engine.unregister_handler("rule-update", self.on_rule_update)

        self._registered = False
        logger.info("Unregistered Cursor provider hooks")

    def on_provider_install(self, event: HookEvent) -> Dict[str, Any]:
        """
        Called when Cursor provider is installed.

        Generates .cursorrules files and registers with main hook system.

        Args:
            event: Hook event with payload:
                - provider_id: int
                - project_id: int
                - config: Dict[str, Any]

        Returns:
            Dict with status and files generated

        Example:
            event = HookEvent(
                type="provider-install",
                payload={
                    "provider_id": 1,
                    "project_id": 123,
                    "config": {...}
                },
                session_id="session-abc",
                correlation_id="req-123"
            )
            result = hooks.on_provider_install(event)
        """
        try:
            payload = event.payload
            provider_id = payload.get("provider_id")
            project_id = payload.get("project_id")
            config_data = payload.get("config", {})

            if not provider_id or not project_id:
                return {
                    "status": "error",
                    "message": "Missing provider_id or project_id"
                }

            # Convert config dict to CursorConfig
            config = CursorConfig(**config_data)

            # Generate rule files
            template_methods = TemplateMethods(self.db)
            cursor_dir = Path(config.project_path) / ".cursor"
            rules_dir = cursor_dir / "rules"
            rules_dir.mkdir(parents=True, exist_ok=True)

            generated_files = []

            # Generate files for each enabled rule
            for rule_id in config.rules_to_install:
                try:
                    content = template_methods.render_rule(rule_id, config, project_id)
                    if content:
                        file_path = rules_dir / f"{rule_id}.mdc"
                        file_path.write_text(content, encoding='utf-8')
                        generated_files.append(str(file_path))
                        logger.info(f"Generated rule file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to generate rule {rule_id}: {e}")

            # Update installation record with hook registration
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    UPDATE provider_installations
                    SET config = json_set(config, '$.hooks_registered', 1)
                    WHERE id = ?
                    """,
                    (provider_id,)
                )

            return {
                "status": "success",
                "files_generated": len(generated_files),
                "files": generated_files,
                "message": f"Generated {len(generated_files)} rule files"
            }

        except Exception as e:
            logger.error(f"Error in on_provider_install: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def on_provider_uninstall(self, event: HookEvent) -> Dict[str, Any]:
        """
        Called when Cursor provider is uninstalled.

        Cleans up generated files and unregisters hooks.

        Args:
            event: Hook event with payload:
                - provider_id: int
                - project_id: int

        Returns:
            Dict with cleanup status

        Example:
            event = HookEvent(
                type="provider-uninstall",
                payload={
                    "provider_id": 1,
                    "project_id": 123
                },
                session_id="session-abc",
                correlation_id="req-123"
            )
            result = hooks.on_provider_uninstall(event)
        """
        try:
            payload = event.payload
            provider_id = payload.get("provider_id")

            if not provider_id:
                return {
                    "status": "error",
                    "message": "Missing provider_id"
                }

            # Get installation details
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    "SELECT * FROM provider_installations WHERE id = ?",
                    (provider_id,)
                ).fetchone()

            if not row:
                return {
                    "status": "warning",
                    "message": "Provider installation not found"
                }

            # Files were already deleted by uninstall method
            # Just log the cleanup
            files_count = len(row.get("installed_files", "").split(",")) if row.get("installed_files") else 0

            return {
                "status": "success",
                "files_cleaned": files_count,
                "message": f"Cleaned up {files_count} files"
            }

        except Exception as e:
            logger.error(f"Error in on_provider_uninstall: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def on_context_change(self, event: HookEvent) -> Dict[str, Any]:
        """
        Called when project context changes.

        Regenerates relevant .cursorrules files to reflect changes.

        Args:
            event: Hook event with payload:
                - project_id: int
                - changes: Dict[str, Any] (what changed)

        Returns:
            Dict with regeneration status

        Example:
            event = HookEvent(
                type="context-change",
                payload={
                    "project_id": 123,
                    "changes": {"tech_stack": ["Python", "SQLite"]}
                },
                session_id="session-abc",
                correlation_id="req-123"
            )
            result = hooks.on_context_change(event)
        """
        try:
            payload = event.payload
            project_id = payload.get("project_id")
            changes = payload.get("changes", {})

            if not project_id:
                return {
                    "status": "error",
                    "message": "Missing project_id"
                }

            # Check if Cursor provider is installed
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    """
                    SELECT * FROM provider_installations
                    WHERE project_id = ? AND provider_type = ?
                    """,
                    (project_id, ProviderType.CURSOR.value)
                ).fetchone()

            if not row:
                return {
                    "status": "skipped",
                    "message": "Cursor provider not installed"
                }

            # Get config and regenerate affected files
            config_data = row.get("config", {})
            if isinstance(config_data, str):
                import json
                config_data = json.loads(config_data)

            config = CursorConfig(**config_data)
            template_methods = TemplateMethods(self.db)

            cursor_dir = Path(config.project_path) / ".cursor"
            rules_dir = cursor_dir / "rules"

            regenerated = []

            # Regenerate all rule files to ensure consistency
            for rule_id in config.rules_to_install:
                try:
                    content = template_methods.render_rule(rule_id, config, project_id)
                    if content:
                        file_path = rules_dir / f"{rule_id}.mdc"
                        file_path.write_text(content, encoding='utf-8')
                        regenerated.append(str(file_path))
                except Exception as e:
                    logger.error(f"Failed to regenerate rule {rule_id}: {e}")

            return {
                "status": "success",
                "files_regenerated": len(regenerated),
                "changes_applied": changes,
                "message": f"Regenerated {len(regenerated)} rule files"
            }

        except Exception as e:
            logger.error(f"Error in on_context_change: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    def on_rule_update(self, event: HookEvent) -> Dict[str, Any]:
        """
        Called when project rules are updated.

        Regenerates affected .cursorrules files.

        Args:
            event: Hook event with payload:
                - project_id: int
                - rule_category: str (category that changed)

        Returns:
            Dict with update status

        Example:
            event = HookEvent(
                type="rule-update",
                payload={
                    "project_id": 123,
                    "rule_category": "Code Quality"
                },
                session_id="session-abc",
                correlation_id="req-123"
            )
            result = hooks.on_rule_update(event)
        """
        try:
            payload = event.payload
            project_id = payload.get("project_id")
            rule_category = payload.get("rule_category")

            if not project_id:
                return {
                    "status": "error",
                    "message": "Missing project_id"
                }

            # Check if Cursor provider is installed
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    """
                    SELECT * FROM provider_installations
                    WHERE project_id = ? AND provider_type = ?
                    """,
                    (project_id, ProviderType.CURSOR.value)
                ).fetchone()

            if not row:
                return {
                    "status": "skipped",
                    "message": "Cursor provider not installed"
                }

            # Get config
            config_data = row.get("config", {})
            if isinstance(config_data, str):
                import json
                config_data = json.loads(config_data)

            config = CursorConfig(**config_data)
            template_methods = TemplateMethods(self.db)

            cursor_dir = Path(config.project_path) / ".cursor"
            rules_dir = cursor_dir / "rules"

            # Determine which rule file to regenerate based on category
            category_map = {
                'Code Quality': 'code-quality',
                'Testing Standards': 'testing-standards',
                'Development Principles': 'development-principles',
                'Workflow Rules': 'workflow-rules',
                'Documentation Standards': 'documentation-standards',
            }

            rule_id = category_map.get(rule_category)
            if not rule_id:
                return {
                    "status": "skipped",
                    "message": f"No rule file for category: {rule_category}"
                }

            # Regenerate the specific rule file
            try:
                content = template_methods.render_rule(rule_id, config, project_id)
                if content:
                    file_path = rules_dir / f"{rule_id}.mdc"
                    file_path.write_text(content, encoding='utf-8')

                    return {
                        "status": "success",
                        "file_updated": str(file_path),
                        "category": rule_category,
                        "message": f"Updated {rule_id}.mdc"
                    }
                else:
                    return {
                        "status": "skipped",
                        "message": f"No rules found for category: {rule_category}"
                    }
            except Exception as e:
                logger.error(f"Failed to update rule {rule_id}: {e}")
                return {
                    "status": "error",
                    "message": str(e)
                }

        except Exception as e:
            logger.error(f"Error in on_rule_update: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }


# Convenience function for registration
def register_cursor_hooks(db: DatabaseService) -> CursorHooks:
    """
    Create and register Cursor hooks.

    Args:
        db: Database service instance

    Returns:
        Configured CursorHooks instance

    Example:
        from agentpm.providers.cursor.hooks import register_cursor_hooks
        from agentpm.core.database.service import DatabaseService

        db = DatabaseService()
        hooks = register_cursor_hooks(db)
    """
    hooks = CursorHooks(db)
    hooks.register_all()
    return hooks
