"""
Cursor Provider - Main Provider Class

High-level interface for Cursor provider operations.
Orchestrates installation, verification, memory sync, and updates.

Pattern: Facade over methods classes
Database-first: All operations tracked in database
"""

from pathlib import Path
from typing import Dict, Any, Optional

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.provider import (
    CursorConfig,
    InstallResult,
    VerifyResult,
    MemorySyncResult,
    UpdateResult,
)
from agentpm.core.database.methods.provider_methods import (
    InstallationMethods,
    VerificationMethods,
    MemoryMethods,
    TemplateMethods,
)


class CursorProvider:
    """
    Cursor IDE Provider.

    Main interface for Cursor provider operations including:
    - Installation/uninstallation
    - Configuration management
    - Memory sync with AIPM learnings
    - Verification and updates
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize Cursor provider.

        Args:
            db: Database service instance
        """
        self.db = db
        self.installation_methods = InstallationMethods(db)
        self.verification_methods = VerificationMethods(db)
        self.memory_methods = MemoryMethods(db)
        self.template_methods = TemplateMethods(db)

    def install(
        self,
        project_path: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> InstallResult:
        """
        Install Cursor provider for project.

        Creates .cursor directory structure with:
        - Rules (6 consolidated rules from WI-118)
        - .cursorignore (indexing exclusions)
        - Custom modes (optional, P1)
        - Memory templates (optional, P1)

        Args:
            project_path: Path to project root
            config: Optional configuration overrides

        Returns:
            Installation result with success status and file list

        Example:
            ```python
            provider = CursorProvider(db)
            result = provider.install(
                project_path=Path("/path/to/project"),
                config={
                    "tech_stack": ["Python", "SQLite"],
                    "memory_sync_enabled": True,
                }
            )
            ```
        """
        # Get project ID from database
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT id, name FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

        if not project_row:
            return InstallResult(
                success=False,
                errors=["Project not found in database"],
                message="Project must be initialized with 'apm init' first",
            )

        project_id = project_row["id"]
        project_name = project_row["name"]

        # Build configuration
        cursor_config = CursorConfig(
            project_name=project_name,
            project_path=str(project_path),
            tech_stack=config.get("tech_stack", []) if config else [],
            rules_enabled=config.get("rules_enabled", True) if config else True,
            memory_sync_enabled=config.get("memory_sync_enabled", True) if config else True,
            modes_enabled=config.get("modes_enabled", True) if config else True,
            indexing_enabled=config.get("indexing_enabled", True) if config else True,
            guardrails_enabled=config.get("guardrails_enabled", True) if config else True,
        )

        # Perform installation
        result = self.installation_methods.install(project_id, cursor_config)

        return result

    def uninstall(self, project_path: Path) -> bool:
        """
        Uninstall Cursor provider.

        Removes:
        - All .cursor directory files
        - Database records (installation, files, memories)

        Args:
            project_path: Path to project root

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            provider = CursorProvider(db)
            success = provider.uninstall(Path("/path/to/project"))
            ```
        """
        # Get project ID
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

        if not project_row:
            return False

        project_id = project_row["id"]

        return self.installation_methods.uninstall(project_id)

    def verify(self, project_path: Path) -> VerifyResult:
        """
        Verify provider installation integrity.

        Checks:
        - All installed files exist
        - File hashes match (detect modifications)
        - Database records are consistent

        Args:
            project_path: Path to project root

        Returns:
            Verification result with missing/modified files

        Example:
            ```python
            provider = CursorProvider(db)
            result = provider.verify(Path("/path/to/project"))
            if not result.success:
                print(f"Missing files: {result.missing_files}")
                print(f"Modified files: {result.modified_files}")
            ```
        """
        # Get project ID
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

        if not project_row:
            return VerifyResult(
                success=False,
                message="Project not found",
            )

        project_id = project_row["id"]

        return self.verification_methods.verify(project_id)

    def update(self, project_path: Path) -> UpdateResult:
        """
        Update provider installation.

        Updates:
        - Rules (re-renders templates)
        - Configuration (applies new settings)
        - Modes (adds new modes)

        Args:
            project_path: Path to project root

        Returns:
            Update result with updated/added/removed files

        Example:
            ```python
            provider = CursorProvider(db)
            result = provider.update(Path("/path/to/project"))
            print(f"Updated {len(result.updated_files)} files")
            ```
        """
        # P1 feature - placeholder
        return UpdateResult(
            success=True,
            message="Update feature coming in P1",
        )

    def sync_memories(
        self,
        project_path: Path,
        direction: str = "to_cursor",
    ) -> MemorySyncResult:
        """
        Sync AIPM learnings with Cursor memories.

        Directions:
        - "to_cursor": AIPM learnings → Cursor memories
        - "from_cursor": Cursor memories → AIPM learnings (P1)
        - "bi_directional": Both directions (P1)

        Args:
            project_path: Path to project root
            direction: Sync direction

        Returns:
            Memory sync result

        Example:
            ```python
            provider = CursorProvider(db)
            result = provider.sync_memories(
                project_path=Path("/path/to/project"),
                direction="to_cursor"
            )
            print(f"Synced {result.synced_to_cursor} memories")
            ```
        """
        # Get project ID
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

        if not project_row:
            return MemorySyncResult(
                success=False,
                message="Project not found",
            )

        project_id = project_row["id"]

        if direction == "to_cursor":
            return self.memory_methods.sync_to_cursor(project_id)
        else:
            # P1 features
            return MemorySyncResult(
                success=False,
                message=f"Sync direction '{direction}' coming in P1",
            )

    def configure(self, project_path: Path, config: Dict[str, Any]) -> bool:
        """
        Update provider configuration.

        Args:
            project_path: Path to project root
            config: Configuration updates

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            provider = CursorProvider(db)
            success = provider.configure(
                project_path=Path("/path/to/project"),
                config={"memory_sync_enabled": False}
            )
            ```
        """
        # P1 feature - placeholder
        return True

    def get_status(self, project_path: Path) -> Dict[str, Any]:
        """
        Get provider installation status.

        Returns:
            Status dictionary with installation details

        Example:
            ```python
            provider = CursorProvider(db)
            status = provider.get_status(Path("/path/to/project"))
            print(f"Status: {status['status']}")
            print(f"Files: {status['installed_files']}")
            ```
        """
        # Get project ID
        with self.db.connect() as conn:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

        if not project_row:
            return {"status": "not_found", "message": "Project not found"}

        project_id = project_row["id"]

        # Get installation record
        with self.db.connect() as conn:
            install_row = conn.execute(
                "SELECT * FROM provider_installations WHERE project_id = ? AND provider_type = ?",
                (project_id, "cursor")
            ).fetchone()

        if not install_row:
            return {"status": "not_installed", "message": "Cursor provider not installed"}

        # Convert Row to dict for easier access
        install_dict = dict(install_row)

        return {
            "status": install_dict["status"],
            "installed_at": install_dict["installed_at"],
            "updated_at": install_dict["updated_at"],
            "last_verified_at": install_dict.get("last_verified_at"),
            "installed_files": len(eval(install_dict["installed_files"])) if install_dict.get("installed_files") else 0,
            "version": install_dict["provider_version"],
        }
