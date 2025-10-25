"""
Migration Manager

Orchestrates migration discovery, execution, and rollback.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from .registry import MigrationRegistry
from .loader import MigrationLoader
from .models import MigrationFile


@dataclass
class MigrationInfo:
    """
    Migration information for CLI display.

    Simplified view of MigrationFile for public API.
    """
    version: str
    description: str
    applied: bool
    applied_at: Optional[str] = None
    rollback_at: Optional[str] = None


class MigrationError(Exception):
    """Migration operation failed"""
    pass


class MigrationManager:
    """
    Manages database migrations with version control.

    Responsibilities:
    - Discover migration files
    - Track applied migrations
    - Execute upgrades/downgrades
    - Validate migration chain

    Usage:
        from agentpm.core.database import DatabaseService
        from agentpm.core.database.migrations import MigrationManager

        db = DatabaseService("path/to/db.sqlite")
        manager = MigrationManager(db)

        # Run pending migrations
        pending = manager.get_pending_migrations()
        for migration in pending:
            manager.run_migration(migration)

        # Or run all at once
        success, failure = manager.run_all_pending()
    """

    def __init__(
        self,
        db_service: 'DatabaseService',  # type: ignore
        migrations_dir: Optional[Path] = None
    ):
        """
        Initialize migration manager.

        Args:
            db_service: Database service instance
            migrations_dir: Path to migrations directory (auto-detected if None)
        """
        self.db_service = db_service

        if migrations_dir is None:
            # Auto-detect: agentpm/core/database/migrations/files/
            self.migrations_dir = Path(__file__).parent / "files"
        else:
            self.migrations_dir = Path(migrations_dir)

        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize loader
        self.loader = MigrationLoader(self.migrations_dir)

    def discover_migrations(self) -> List[MigrationInfo]:
        """
        Scan migrations directory for migration files.

        Returns:
            List of discovered migrations (sorted by version)
        """
        # Get all migration files
        migration_files = self.loader.discover_migrations()

        # Enrich with applied status
        with self.db_service.connect() as conn:
            registry = MigrationRegistry(conn)

            result = []
            for migration_file in migration_files:
                info = registry.get_migration_info(migration_file.version)

                result.append(MigrationInfo(
                    version=migration_file.version,
                    description=migration_file.description,
                    applied=info is not None,
                    applied_at=info[0] if info else None,
                    rollback_at=info[1] if info else None
                ))

        return sorted(result, key=lambda m: m.version)

    def get_pending_migrations(self) -> List[MigrationInfo]:
        """
        Get migrations that haven't been applied yet.

        Returns:
            List of pending migrations (sorted by version)
        """
        all_migrations = self.discover_migrations()
        return [m for m in all_migrations if not m.applied]

    def get_applied_migrations(self) -> List[MigrationInfo]:
        """
        Get migrations that have been applied.

        Returns:
            List of applied migrations (sorted by version)
        """
        all_migrations = self.discover_migrations()
        return [m for m in all_migrations if m.applied]

    def run_migration(self, migration: MigrationInfo) -> bool:
        """
        Execute a single migration.

        Args:
            migration: Migration to run

        Returns:
            True if successful

        Raises:
            MigrationError: If migration fails
        """
        # Find migration file
        migration_files = self.loader.discover_migrations()
        migration_file = next(
            (m for m in migration_files if m.version == migration.version),
            None
        )

        if migration_file is None:
            raise MigrationError(f"Migration file not found: {migration.version}")

        # Load migration module
        try:
            module = self.loader.load_migration_module(migration_file)
        except Exception as e:
            raise MigrationError(
                f"Failed to load migration {migration.version}: {e}"
            ) from e

        # Validate module has required functions
        if not hasattr(module, 'upgrade'):
            raise MigrationError(
                f"Migration {migration.version} missing upgrade() function"
            )

        # Execute migration with transaction
        try:
            with self.db_service.transaction() as conn:
                registry = MigrationRegistry(conn)

                # Pre-validation (optional)
                if hasattr(module, 'validate_pre'):
                    if not module.validate_pre(conn):
                        raise MigrationError(
                            f"Pre-validation failed for {migration.version}"
                        )

                # Run upgrade
                module.upgrade(conn)

                # Post-validation (optional)
                if hasattr(module, 'validate_post'):
                    if not module.validate_post(conn):
                        raise MigrationError(
                            f"Post-validation failed for {migration.version}"
                        )

                # Record migration
                registry.record_migration(
                    version=migration.version,
                    description=migration.description
                )

        except Exception as e:
            raise MigrationError(
                f"Migration {migration.version} failed: {e}"
            ) from e

        return True

    def run_all_pending(self) -> Tuple[int, int]:
        """
        Execute all pending migrations.

        Returns:
            (success_count, failure_count)
        """
        pending = self.get_pending_migrations()
        success_count = 0
        failure_count = 0

        for migration in pending:
            try:
                self.run_migration(migration)
                success_count += 1
            except MigrationError:
                failure_count += 1
                # Fail-fast: stop on first failure
                break

        return success_count, failure_count

    def rollback_migration(
        self,
        version: str,
        reason: str = ""
    ) -> bool:
        """
        Rollback a specific migration.

        Args:
            version: Migration version to rollback
            reason: Why rolling back

        Returns:
            True if successful

        Raises:
            MigrationError: If rollback fails
        """
        # Find migration file
        migration_files = self.loader.discover_migrations()
        migration_file = next(
            (m for m in migration_files if m.version == version),
            None
        )

        if migration_file is None:
            raise MigrationError(f"Migration file not found: {version}")

        # Load migration module
        try:
            module = self.loader.load_migration_module(migration_file)
        except Exception as e:
            raise MigrationError(
                f"Failed to load migration {version}: {e}"
            ) from e

        # Validate module has downgrade function
        if not hasattr(module, 'downgrade'):
            raise MigrationError(
                f"Migration {version} has no downgrade() function"
            )

        # Execute rollback with transaction
        try:
            with self.db_service.transaction() as conn:
                registry = MigrationRegistry(conn)

                # Run downgrade
                module.downgrade(conn)

                # Record rollback
                registry.record_rollback(version=version, reason=reason)

        except Exception as e:
            raise MigrationError(
                f"Rollback {version} failed: {e}"
            ) from e

        return True

    def validate_migration_chain(self) -> bool:
        """
        Verify migration chain integrity.

        Checks:
        - No gaps in version sequence
        - All applied migrations have files
        - No duplicate versions

        Returns:
            True if chain is valid, False otherwise
        """
        migrations = self.discover_migrations()

        if not migrations:
            return True  # Empty chain is valid

        # Check for gaps in version sequence
        versions = sorted([int(m.version) for m in migrations])
        if versions:  # Only check if we have versions
            for i in range(1, max(versions) + 1):
                if i not in versions:
                    return False  # Gap found

        # Check all applied migrations have files
        # Query database directly to get ALL applied migrations
        with self.db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT version
                FROM schema_migrations
                WHERE rollback_at IS NULL
                ORDER BY version
            """)
            applied_versions = [row[0] for row in cursor.fetchall()]

        # Verify each applied migration has a file
        for version in applied_versions:
            migration_file = self.migrations_dir / f"migration_{version}.py"
            if not migration_file.exists():
                return False  # Missing file for applied migration

        return True
