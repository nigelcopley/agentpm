"""
Test Database Utilities - Centralized database testing support

Provides utilities for testing with the centralized database initializer,
including proper setup, teardown, and isolation between tests.

Usage:
    # In test files
    from tests.utils.database import TestDatabaseManager
    
    def test_something():
        with TestDatabaseManager() as db:
            # Test code here
            pass
"""

import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Optional

from agentpm.core.database.initializer import DatabaseInitializer
from agentpm.core.database.service import DatabaseService


class TestDatabaseManager:
    """
    Context manager for test database setup and cleanup.
    
    Creates isolated test databases for each test with proper cleanup.
    Ensures tests don't interfere with each other or production data.
    
    Example:
        def test_work_item_creation():
            with TestDatabaseManager() as db:
                # Test code here
                work_item = db.work_items.create_work_item(...)
                assert work_item.id is not None
    """
    
    def __init__(self, db_name: str = "test.db"):
        """
        Initialize test database manager.
        
        Args:
            db_name: Name of the test database file
        """
        self.db_name = db_name
        self.temp_dir: Optional[Path] = None
        self.original_instance = None
        self.original_initialized = False
    
    def __enter__(self) -> DatabaseService:
        """Setup test database and return service instance."""
        # Create temporary directory for test database
        self.temp_dir = Path(tempfile.mkdtemp(prefix="apm_test_"))
        db_path = self.temp_dir / self.db_name
        
        # Backup original state
        self.original_instance = DatabaseInitializer._instance
        self.original_initialized = DatabaseInitializer._initialized
        
        # Initialize test database
        DatabaseInitializer.initialize(db_path, force_reinit=True)
        
        return DatabaseInitializer.get_instance()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup test database and restore original state."""
        # Cleanup database initializer
        DatabaseInitializer.cleanup()
        
        # Restore original state
        DatabaseInitializer._instance = self.original_instance
        DatabaseInitializer._initialized = self.original_initialized
        
        # Remove temporary directory
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)


@contextmanager
def isolated_test_database(db_name: str = "test.db") -> Generator[DatabaseService, None, None]:
    """
    Context manager for isolated test database.
    
    Convenience function for test database setup with automatic cleanup.
    
    Args:
        db_name: Name of the test database file
        
    Yields:
        DatabaseService instance for testing
        
    Example:
        def test_something():
            with isolated_test_database() as db:
                # Test code here
                pass
    """
    with TestDatabaseManager(db_name) as db:
        yield db


def reset_database_initializer():
    """
    Reset database initializer state for testing.
    
    Useful for test setup/teardown to ensure clean state.
    """
    DatabaseInitializer.cleanup()


def mock_database_service(mock_service: DatabaseService):
    """
    Mock the database service for testing.
    
    Args:
        mock_service: Mock database service instance
    """
    DatabaseInitializer._instance = mock_service
    DatabaseInitializer._initialized = True


def unmock_database_service():
    """Remove database service mock."""
    DatabaseInitializer._instance = None
    DatabaseInitializer._initialized = False
