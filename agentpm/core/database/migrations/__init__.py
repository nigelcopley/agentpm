"""
Database Migrations

Professional migration framework for version-controlled schema changes.

Components:
- MigrationManager: Orchestrates migration execution
- SchemaDiffer: Detects schema changes between current and target state
- MigrationGenerator: Generates migration files from schema changes
- Migration discovery and tracking
- Rollback support
- Pre/post validation
"""

from .manager import MigrationManager, MigrationInfo, MigrationError
from .differ import (
    SchemaDiffer,
    SchemaChange,
    ChangeType,
    TableChange,
    ColumnChange,
    IndexChange,
    TriggerChange
)
from .generator import MigrationGenerator, MigrationGenerationError


# Convenience functions for CLI
def get_pending_migrations(db_service):
    """Get pending migrations (convenience function for CLI)."""
    manager = MigrationManager(db_service)
    return manager.get_pending_migrations()


def get_applied_migrations(db_service):
    """Get applied migrations (convenience function for CLI)."""
    manager = MigrationManager(db_service)
    return manager.get_applied_migrations()


def run_pending_migrations(db_service):
    """Run all pending migrations (convenience function for CLI)."""
    manager = MigrationManager(db_service)
    return manager.run_all_pending()


__all__ = [
    # Management
    "MigrationManager",
    "MigrationInfo",
    "MigrationError",

    # Auto-generation
    "SchemaDiffer",
    "MigrationGenerator",
    "MigrationGenerationError",

    # Schema change models
    "SchemaChange",
    "ChangeType",
    "TableChange",
    "ColumnChange",
    "IndexChange",
    "TriggerChange",

    # Convenience functions
    "get_pending_migrations",
    "get_applied_migrations",
    "run_pending_migrations",
]
