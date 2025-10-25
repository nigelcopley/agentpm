"""
Provider Methods - Layer 3: Business Logic

Core business logic for provider operations:
- Installation/uninstallation
- File management and verification
- Memory sync (AIPM ↔ Provider)
- Template rendering
- Guardrails configuration

Pattern: ServiceResult for all operations
Database-first: All state tracked in database
Architecture: Database layer (core/database/) - shared by ALL providers
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.provider import (
    ProviderInstallation,
    CursorMemory,
    CursorConfig,
    InstallResult,
    VerifyResult,
    MemorySyncResult,
    UpdateResult,
    InstallationStatus,
    ProviderType,
    MemorySyncDirection,
)
from agentpm.core.database.adapters.provider import (
    ProviderInstallationAdapter,
    CursorMemoryAdapter,
    ProviderFileAdapter,
)


logger = logging.getLogger(__name__)


class InstallationMethods:
    """
    Installation business logic.

    Handles provider installation, uninstallation, and updates.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize installation methods.

        Args:
            db: Database service instance
        """
        self.db = db

    def install(
        self,
        project_id: int,
        config: CursorConfig,
    ) -> InstallResult:
        """
        Install Cursor provider for project.

        Args:
            project_id: Project ID
            config: Cursor configuration

        Returns:
            Installation result with success status and file list
        """
        try:
            project_path = Path(config.project_path)
            cursor_dir = project_path / ".cursor"

            # Create installation record
            installation = ProviderInstallation(
                project_id=project_id,
                provider_type=ProviderType.CURSOR,
                provider_version="1.0.0",
                install_path=str(cursor_dir),
                status=InstallationStatus.INSTALLED,
                config=config.model_dump(),
                installed_files=[],
                file_hashes={},
            )

            # Create .cursor directory structure
            directories = [
                cursor_dir / "rules",
                cursor_dir / "memories",
            ]

            if config.modes_enabled:
                directories.append(cursor_dir / "modes")

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            installed_files = []
            file_hashes = {}
            errors = []

            # Install rules
            if config.rules_enabled:
                rule_result = self._install_rules(cursor_dir, config, project_id)
                installed_files.extend(rule_result["files"])
                file_hashes.update(rule_result["hashes"])
                errors.extend(rule_result["errors"])

            # Install indexing config
            if config.indexing_enabled:
                ignore_result = self._install_cursorignore(cursor_dir, config)
                installed_files.extend(ignore_result["files"])
                file_hashes.update(ignore_result["hashes"])
                errors.extend(ignore_result["errors"])

            # Install modes
            if config.modes_enabled:
                mode_result = self._install_modes(cursor_dir, config)
                installed_files.extend(mode_result["files"])
                file_hashes.update(mode_result["hashes"])
                errors.extend(mode_result["errors"])

            # Update installation record
            installation.installed_files = installed_files
            installation.file_hashes = file_hashes

            if errors:
                installation.status = InstallationStatus.PARTIAL

            # Save to database
            row_data = ProviderInstallationAdapter.to_db(installation)
            with self.db.transaction() as conn:
                result = conn.execute(
                    """
                    INSERT INTO provider_installations (
                        project_id, provider_type, provider_version,
                        install_path, status, config,
                        installed_files, file_hashes,
                        installed_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row_data["project_id"],
                        row_data["provider_type"],
                        row_data["provider_version"],
                        row_data["install_path"],
                        row_data["status"],
                        row_data["config"],
                        row_data["installed_files"],
                        row_data["file_hashes"],
                        row_data["installed_at"],
                        row_data["updated_at"],
                    ),
                )

                installation_id = result.lastrowid

                # Track files in provider_files table
                for file_path, file_hash in file_hashes.items():
                    file_type = self._determine_file_type(file_path)
                    file_data = ProviderFileAdapter.to_db(
                        installation_id, file_path, file_hash, file_type
                    )
                    conn.execute(
                        """
                        INSERT INTO provider_files (
                            installation_id, file_path, file_hash, file_type, installed_at
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            file_data["installation_id"],
                            file_data["file_path"],
                            file_data["file_hash"],
                            file_data["file_type"],
                            file_data["installed_at"],
                        ),
                    )

            return InstallResult(
                success=len(errors) == 0,
                installation_id=installation_id,
                installed_files=installed_files,
                errors=errors,
                message=(
                    f"Cursor provider installed successfully ({len(installed_files)} files)"
                    if not errors
                    else f"Cursor provider partially installed with {len(errors)} errors"
                ),
            )

        except Exception as e:
            return InstallResult(
                success=False,
                errors=[f"Installation failed: {str(e)}"],
                message="Installation failed",
            )

    def uninstall(self, project_id: int, backup: bool = True) -> bool:
        """
        Uninstall Cursor provider with optional backup.

        Creates backup before deletion for safety, then removes all
        provider files and database records.

        Args:
            project_id: Project ID
            backup: Whether to create backup before deletion (default: True)

        Returns:
            True if successful, False otherwise

        Example:
            methods = InstallationMethods(db)

            # Uninstall with backup (safe)
            success = methods.uninstall(project_id=123)

            # Uninstall without backup (unsafe, faster)
            success = methods.uninstall(project_id=123, backup=False)
        """
        try:
            # Get installation record
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    "SELECT * FROM provider_installations WHERE project_id = ? AND provider_type = ?",
                    (project_id, ProviderType.CURSOR.value),
                ).fetchone()

            if not row:
                return False

            installation = ProviderInstallationAdapter.from_db(row)
            cursor_dir = Path(installation.install_path)

            # Create backup before deletion (safety)
            if backup and cursor_dir.exists():
                backup_dir = cursor_dir.parent / f".cursor-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                backup_dir.mkdir(parents=True, exist_ok=True)

                import shutil

                # Backup each installed file
                for file_rel_path in installation.installed_files:
                    file_path = cursor_dir / file_rel_path
                    if file_path.exists():
                        backup_file = backup_dir / file_rel_path
                        backup_file.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file to backup
                        if file_path.is_file():
                            shutil.copy2(file_path, backup_file)

            # Delete files
            if cursor_dir.exists():
                import shutil
                shutil.rmtree(cursor_dir)

            # Delete database records
            with self.db.transaction() as conn:
                # Temporarily disable foreign key constraints to avoid issues with learnings table
                # (which might not exist yet)
                conn.execute("PRAGMA foreign_keys = OFF")

                try:
                    # Delete provider files records (CASCADE will handle this too, but explicit is better)
                    conn.execute(
                        "DELETE FROM provider_files WHERE installation_id = ?",
                        (installation.id,),
                    )

                    # Delete cursor memories records
                    # Note: cursor_memories has project_id FK with CASCADE, so deleting project would
                    # handle this. But since we're deleting provider directly, we need explicit deletion.
                    cursor_memories_exists = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='cursor_memories'"
                    ).fetchone()

                    if cursor_memories_exists:
                        conn.execute(
                            "DELETE FROM cursor_memories WHERE project_id = ?",
                            (project_id,),
                        )

                    # Delete installation record
                    conn.execute(
                        "DELETE FROM provider_installations WHERE id = ?",
                        (installation.id,),
                    )
                finally:
                    # Re-enable foreign key constraints
                    conn.execute("PRAGMA foreign_keys = ON")

            return True

        except Exception as e:
            logger.error(f"Error uninstalling provider: {e}", exc_info=True)
            return False

    def _install_rules(
        self, cursor_dir: Path, config: CursorConfig, project_id: int
    ) -> Dict[str, Any]:
        """
        Install rule files dynamically from database.

        Queries database for rule categories in this project,
        generates .mdc file for each category.
        """
        installed_files = []
        file_hashes = {}
        errors = []

        rules_dir = cursor_dir / "rules"
        template_methods = TemplateMethods(self.db)

        # Step 1: Always install AIPM master rule
        try:
            content = template_methods.render_rule('aipm-master', config, project_id)
            if content:
                file_path = rules_dir / "aipm-master.mdc"
                file_path.write_text(content, encoding='utf-8')

                file_hash = hashlib.sha256(content.encode()).hexdigest()
                rel_path = str(file_path.relative_to(cursor_dir))
                installed_files.append(rel_path)
                file_hashes[rel_path] = file_hash
        except Exception as e:
            errors.append(f"Failed to install aipm-master: {str(e)}")

        # Step 2: Query database for categories with rules in THIS project
        with self.db.connect() as conn:
            categories = conn.execute(
                """
                SELECT DISTINCT category
                FROM rules
                WHERE project_id = ? AND enabled = 1 AND category IS NOT NULL
                ORDER BY category
                """,
                (project_id,)
            ).fetchall()

        # Step 3: Generate rule file for each category
        category_to_filename = {
            'Code Quality': 'code-quality',
            'Testing Standards': 'testing-standards',
            'Development Principles': 'development-principles',
            'Workflow Rules': 'workflow-rules',
            'Documentation Standards': 'documentation-standards',  # Skip if already installed above
        }

        for row in categories:
            category = row['category']

            filename = category_to_filename.get(category)
            if not filename:
                # Convert category name to filename (lowercase, hyphens)
                filename = category.lower().replace(' ', '-')

            try:
                content = template_methods.render_rule(filename, config, project_id)
                if content:  # Only install if rules exist
                    file_path = rules_dir / f"{filename}.mdc"
                    file_path.write_text(content, encoding='utf-8')

                    file_hash = hashlib.sha256(content.encode()).hexdigest()
                    rel_path = str(file_path.relative_to(cursor_dir))
                    installed_files.append(rel_path)
                    file_hashes[rel_path] = file_hash
            except Exception as e:
                errors.append(f"Failed to install category {category}: {str(e)}")

        return {"files": installed_files, "hashes": file_hashes, "errors": errors}

    def _install_cursorignore(
        self, cursor_dir: Path, config: CursorConfig
    ) -> Dict[str, Any]:
        """Install .cursorignore file."""
        installed_files = []
        file_hashes = {}
        errors = []

        try:
            content = "\n".join(config.exclude_patterns)
            file_path = cursor_dir / ".cursorignore"
            file_path.write_text(content)

            file_hash = hashlib.sha256(content.encode()).hexdigest()
            rel_path = ".cursorignore"
            installed_files.append(rel_path)
            file_hashes[rel_path] = file_hash

        except Exception as e:
            errors.append(f"Failed to install .cursorignore: {str(e)}")

        return {"files": installed_files, "hashes": file_hashes, "errors": errors}

    def _install_modes(
        self, cursor_dir: Path, config: CursorConfig
    ) -> Dict[str, Any]:
        """Install custom mode files."""
        # P1 feature - placeholder for now
        return {"files": [], "hashes": {}, "errors": []}

    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from path."""
        if file_path.endswith(".mdc"):
            return "rule"
        elif file_path.endswith(".json"):
            return "mode"
        elif "ignore" in file_path:
            return "config"
        elif "memories" in file_path:
            return "memory"
        else:
            return "config"


class VerificationMethods:
    """
    Verification business logic.

    Validates provider installation integrity.
    """

    def __init__(self, db: DatabaseService):
        """Initialize verification methods."""
        self.db = db

    def verify(self, project_id: int) -> VerifyResult:
        """
        Verify provider installation.

        Args:
            project_id: Project ID

        Returns:
            Verification result with missing/modified files
        """
        try:
            # Get installation record
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                row = conn.execute(
                    "SELECT * FROM provider_installations WHERE project_id = ? AND provider_type = ?",
                    (project_id, ProviderType.CURSOR.value),
                ).fetchone()

            if not row:
                return VerifyResult(
                    success=False,
                    message="Cursor provider not installed",
                )

            installation = ProviderInstallationAdapter.from_db(row)
            cursor_dir = Path(installation.install_path)

            missing_files = []
            modified_files = []
            verified_count = 0

            for rel_path, expected_hash in installation.file_hashes.items():
                file_path = cursor_dir / rel_path

                if not file_path.exists():
                    missing_files.append(rel_path)
                    continue

                # Verify hash
                content = file_path.read_text()
                actual_hash = hashlib.sha256(content.encode()).hexdigest()

                if actual_hash != expected_hash:
                    modified_files.append(rel_path)
                else:
                    verified_count += 1

            # Update last_verified_at
            with self.db.transaction() as conn:
                conn.execute(
                    "UPDATE provider_installations SET last_verified_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), installation.id),
                )

            return VerifyResult(
                success=len(missing_files) == 0 and len(modified_files) == 0,
                verified_files=verified_count,
                missing_files=missing_files,
                modified_files=modified_files,
                message=(
                    f"Verification passed ({verified_count} files)"
                    if not missing_files and not modified_files
                    else f"Verification failed: {len(missing_files)} missing, {len(modified_files)} modified"
                ),
            )

        except Exception as e:
            return VerifyResult(
                success=False,
                errors=[f"Verification failed: {str(e)}"],
                message="Verification error",
            )


class MemoryMethods:
    """
    Memory sync business logic.

    Syncs AIPM learnings with Cursor memories.
    """

    def __init__(self, db: DatabaseService):
        """Initialize memory methods."""
        self.db = db

    def sync_to_cursor(self, project_id: int) -> MemorySyncResult:
        """
        Sync AIPM learnings to Cursor memories.

        Args:
            project_id: Project ID

        Returns:
            Memory sync result
        """
        try:
            # Get installation
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                install_row = conn.execute(
                    "SELECT * FROM provider_installations WHERE project_id = ? AND provider_type = ?",
                    (project_id, ProviderType.CURSOR.value),
                ).fetchone()

            if not install_row:
                return MemorySyncResult(
                    success=False,
                    message="Cursor provider not installed",
                )

            installation = ProviderInstallationAdapter.from_db(install_row)
            cursor_dir = Path(installation.install_path)
            memories_dir = cursor_dir / "memories"
            memories_dir.mkdir(parents=True, exist_ok=True)

            # Get recent learnings (not yet synced)
            with self.db.connect() as conn:
                conn.row_factory = lambda cursor, row: dict(
                    zip([col[0] for col in cursor.description], row)
                )
                learning_rows = conn.execute(
                    """
                    SELECT l.* FROM learnings l
                    LEFT JOIN cursor_memories cm ON l.id = cm.source_learning_id
                    WHERE l.project_id = ? AND cm.id IS NULL
                    ORDER BY l.created_at DESC
                    LIMIT 20
                    """,
                    (project_id,),
                ).fetchall()

            synced_count = 0

            with self.db.transaction() as conn:
                for learning in learning_rows:
                    try:
                        # Create memory from learning
                        memory_name = f"learning-{learning['id']}"
                        file_path = f"{memory_name}.md"

                        memory = CursorMemory(
                            project_id=project_id,
                            name=memory_name,
                            description=learning.get("title", "Learning from AIPM"),
                            category=learning.get("type", "general"),
                            content=learning.get("content", ""),
                            tags=[],
                            file_path=file_path,
                            source_learning_id=learning["id"],
                            last_synced_at=datetime.now(),
                        )

                        # Write file
                        memory_file = memories_dir / file_path
                        memory_file.write_text(memory.content)

                        # Calculate hash
                        memory.file_hash = hashlib.sha256(memory.content.encode()).hexdigest()

                        # Save to database
                        row_data = CursorMemoryAdapter.to_db(memory)
                        conn.execute(
                            """
                            INSERT INTO cursor_memories (
                                project_id, name, description, category, content,
                                tags, file_path, file_hash, source_learning_id,
                                last_synced_at, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                row_data["project_id"],
                                row_data["name"],
                                row_data["description"],
                                row_data["category"],
                                row_data["content"],
                                row_data["tags"],
                                row_data["file_path"],
                                row_data["file_hash"],
                                row_data["source_learning_id"],
                                row_data["last_synced_at"],
                                row_data["created_at"],
                                row_data["updated_at"],
                            ),
                        )

                        synced_count += 1

                    except Exception as e:
                        continue

            return MemorySyncResult(
                success=True,
                synced_to_cursor=synced_count,
                message=f"Synced {synced_count} learnings to Cursor memories",
            )

        except Exception as e:
            return MemorySyncResult(
                success=False,
                errors=[f"Sync failed: {str(e)}"],
                message="Memory sync error",
            )


class TemplateMethods:
    """
    Template rendering business logic.

    Renders Jinja2 templates for rules, modes, hooks.
    """

    def __init__(self, db: DatabaseService):
        """Initialize template methods."""
        self.db = db

    def render_rule(
        self, rule_id: str, config: CursorConfig, project_id: int
    ) -> str:
        """
        Render rule from database.

        Generates Cursor rule files dynamically from database rules, not static templates.

        For category-based rules (e.g., 'code-quality'):
        - Queries database for all rules in that category
        - Generates .mdc file with all rules from DB

        For common rules (e.g., 'aipm-master'):
        - Uses template with minimal project customization

        Args:
            rule_id: Rule file ID (e.g., 'aipm-master', 'code-quality', 'testing-standards')
            config: Cursor configuration
            project_id: Project ID

        Returns:
            Rendered rule content
        """
        # Special case: AIPM master integration file
        if rule_id == 'aipm-master':
            return self._render_aipm_master(config, project_id)

        # Category-based rules: Query database and generate dynamically
        # Map rule_id to category
        category_map = {
            'code-quality': 'Code Quality',
            'testing-standards': 'Testing Standards',
            'development-principles': 'Development Principles',
            'workflow-rules': 'Workflow Rules',
            'documentation-standards': 'Documentation Standards',
        }

        category = category_map.get(rule_id)
        if category:
            return self._render_category_rules(category, config, project_id)
        else:
            raise ValueError(f"Unknown rule_id: {rule_id}")

    def _render_aipm_master(self, config: CursorConfig, project_id: int) -> str:
        """Render common AIPM master rule."""
        from jinja2 import Template

        # Import from providers/cursor/templates to access template files
        # This is the only cross-layer dependency (database layer accessing provider templates)
        # which is acceptable for template rendering
        from pathlib import Path as P
        import agentpm.providers.cursor as cursor_module
        cursor_pkg_dir = P(cursor_module.__file__).parent
        template_dir = cursor_pkg_dir / "templates" / "rules"
        template_file = template_dir / "aipm-master.mdc.j2"

        template_content = template_file.read_text(encoding='utf-8')
        template = Template(template_content)

        return template.render(
            project_name=config.project_name,
            project_path=config.project_path,
            tech_stack=", ".join(config.tech_stack) if config.tech_stack else "",
            database_path=str(Path(config.project_path) / ".aipm" / "data" / "aipm.db"),
        )

    def _render_documentation_quality(self, config: CursorConfig, project_id: int) -> str:
        """Render documentation quality rule."""
        from jinja2 import Template
        from pathlib import Path as P
        import agentpm.providers.cursor as cursor_module
        cursor_pkg_dir = P(cursor_module.__file__).parent
        template_dir = cursor_pkg_dir / "templates" / "rules"
        template_file = template_dir / "documentation-quality.mdc.j2"

        if template_file.exists():
            template_content = template_file.read_text(encoding='utf-8')
            template = Template(template_content)
            return template.render(
                project_name=config.project_name,
                project_path=config.project_path,
            )
        else:
            # Fallback: generate from DB rules
            return self._render_category_rules('Documentation Standards', config, project_id)

    def _render_category_rules(self, category: str, config: CursorConfig, project_id: int) -> str:
        """
        Generate rule file dynamically from database rules in a category.

        Queries database for all enabled rules in category and formats them.
        """
        # Query database for rules in this category
        with self.db.connect() as conn:
            rules = conn.execute(
                """
                SELECT rule_id, name, description, enforcement_level, error_message
                FROM rules
                WHERE project_id = ? AND category = ? AND enabled = 1
                ORDER BY rule_id
                """,
                (project_id, category)
            ).fetchall()

        if not rules:
            return None  # No rules in this category, skip file generation

        # Determine glob patterns based on category and tech stack
        globs = self._get_globs_for_category(category, config.tech_stack)

        # Build rule content
        content = f"""---
description: {category} rules for this project
globs: {globs}
priority: 80
---

# {category}

## Rules from Database

Query these rules dynamically:
```bash
apm rules list --category="{category}"
```

"""

        # Add each rule from database
        for rule in rules:
            content += f"### {rule['rule_id']}: {rule['name']}\n\n"
            content += f"**Enforcement**: {rule['enforcement_level']}\n\n"
            if rule['description']:
                content += f"{rule['description']}\n\n"
            if rule['error_message']:
                content += f"**Error**: {rule['error_message']}\n\n"
            content += "---\n\n"

        return content

    def _get_globs_for_category(self, category: str, tech_stack: list) -> list:
        """Determine glob patterns based on category and tech stack."""
        # Base patterns by category
        if category in ['Code Quality', 'Development Principles']:
            patterns = ["**/*.py"] if not tech_stack or 'Python' in tech_stack else []
            if 'JavaScript' in tech_stack or 'TypeScript' in tech_stack:
                patterns.extend(["**/*.js", "**/*.ts"])
            return patterns
        elif category == 'Testing Standards':
            return ["tests/**/*.py", "**/*_test.py", "**/test_*.py"]
        elif category == 'Documentation Standards':
            return ["docs/**/*.md", "**/*.md"]
        elif category == 'Workflow Rules':
            return ["**/*"]  # All files
        else:
            return ["**/*"]
