"""
Migration File Loader

Discovers and imports migration files from filesystem.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Any

from .models import MigrationFile


class MigrationLoader:
    """
    Discovers and loads migration files from filesystem.

    Responsibilities:
    - Scan migrations directory
    - Extract version and description from files
    - Import migration modules
    """

    def __init__(self, migrations_dir: Path):
        """
        Initialize loader.

        Args:
            migrations_dir: Path to migrations/files/ directory
        """
        self.migrations_dir = Path(migrations_dir)

    def discover_migrations(self) -> List[MigrationFile]:
        """
        Scan migrations directory for migration files.

        Returns:
            List of discovered migration files (sorted by version)
        """
        migrations = []

        # Scan for migration_NNNN.py files
        for file_path in sorted(self.migrations_dir.glob("migration_*.py")):
            # Extract version from filename: migration_0001.py → 0001
            version = file_path.stem.split("_")[1]

            # Import module to get description
            module = self._import_migration_module(file_path, version)
            description = getattr(module, "DESCRIPTION", "No description")

            migrations.append(MigrationFile(
                version=version,
                description=description,
                file_path=file_path,
                applied=False  # Will be updated by manager
            ))

        return sorted(migrations, key=lambda m: m.version)

    def load_migration_module(self, migration_file: MigrationFile) -> Any:
        """
        Import a migration module.

        Args:
            migration_file: Migration file metadata

        Returns:
            Imported Python module
        """
        return self._import_migration_module(
            migration_file.file_path,
            migration_file.version
        )

    def _import_migration_module(self, file_path: Path, version: str) -> Any:
        """
        Import a migration file as a Python module.

        Args:
            file_path: Path to migration file
            version: Migration version

        Returns:
            Imported module
        """
        module_name = f"aipm_migration_{version}"

        # Create module spec from file
        spec = importlib.util.spec_from_file_location(
            module_name,
            file_path
        )

        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import migration {version} from {file_path}")

        # Create and load module
        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules to allow relative imports (if needed)
        sys.modules[module_name] = module

        # Execute module
        spec.loader.exec_module(module)

        return module

    def validate_migration_file(self, migration_file: MigrationFile) -> bool:
        """
        Validate that a migration file has required functions.

        Args:
            migration_file: Migration file to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            module = self.load_migration_module(migration_file)

            # Check for required upgrade function
            if not hasattr(module, 'upgrade'):
                return False

            # Check upgrade is callable
            if not callable(getattr(module, 'upgrade')):
                return False

            return True

        except Exception:
            return False
