"""
Database Initializer - Centralized database initialization and management

Provides singleton pattern for database service initialization with proper
lifecycle management, configuration validation, and resource cleanup.

Architecture:
- Singleton pattern ensures single database instance per application
- Lazy initialization with configuration validation
- Proper resource cleanup on application shutdown
- Environment-based configuration support
- Comprehensive error handling and logging

Usage:
    # Initialize at application startup
    DatabaseInitializer.initialize(db_path="path/to/database.db")
    
    # Get the singleton instance
    db_service = DatabaseInitializer.get_instance()
    
    # Cleanup on shutdown
    DatabaseInitializer.cleanup()
"""

import logging
import os
import threading
from pathlib import Path
from typing import Optional, Union

from .service import DatabaseService


class DatabaseInitializer:
    """
    Singleton database initializer with lifecycle management.
    
    Ensures single database instance per application with proper
    initialization, configuration validation, and cleanup.
    
    Thread-safe implementation with lazy initialization.
    """
    
    _instance: Optional[DatabaseService] = None
    _lock = threading.Lock()
    _initialized = False
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def initialize(
        cls,
        db_path: Optional[Union[str, Path]] = None,
        force_reinit: bool = False
    ) -> DatabaseService:
        """
        Initialize database service with configuration validation.
        
        Args:
            db_path: Path to database file. If None, auto-detects from environment
            force_reinit: Force reinitialization even if already initialized
            
        Returns:
            DatabaseService instance
            
        Raises:
            RuntimeError: If initialization fails or database is invalid
            FileNotFoundError: If database path doesn't exist and can't be created
            
        Example:
            # Auto-detect database path
            db = DatabaseInitializer.initialize()
            
            # Explicit path
            db = DatabaseInitializer.initialize(db_path="/path/to/db.db")
            
            # Force reinitialization
            db = DatabaseInitializer.initialize(force_reinit=True)
        """
        with cls._lock:
            if cls._initialized and not force_reinit:
                if cls._instance is None:
                    raise RuntimeError("Database was marked as initialized but instance is None")
                return cls._instance
            
            # Determine database path
            resolved_path = cls._resolve_database_path(db_path)
            
            # Validate configuration
            cls._validate_configuration(resolved_path)
            
            # Create database service
            cls._logger.info(f"Initializing database service: {resolved_path}")
            cls._instance = DatabaseService(resolved_path)
            cls._initialized = True
            
            cls._logger.info("Database service initialized successfully")
            return cls._instance
    
    @classmethod
    def get_instance(cls) -> DatabaseService:
        """
        Get the initialized database service instance.
        
        Returns:
            DatabaseService instance
            
        Raises:
            RuntimeError: If database not initialized
            
        Example:
            db = DatabaseInitializer.get_instance()
            projects = db.projects.list_projects()
        """
        if not cls._initialized or cls._instance is None:
            raise RuntimeError(
                "Database not initialized. Call DatabaseInitializer.initialize() first."
            )
        return cls._instance
    
    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if database service is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return cls._initialized and cls._instance is not None
    
    @classmethod
    def cleanup(cls) -> None:
        """
        Clean up database resources and reset state.
        
        Should be called on application shutdown to ensure proper cleanup.
        
        Example:
            DatabaseInitializer.cleanup()
        """
        with cls._lock:
            if cls._instance is not None:
                cls._logger.info("Cleaning up database service")
                # DatabaseService uses context managers, so no explicit cleanup needed
                cls._instance = None
                cls._initialized = False
                cls._logger.info("Database service cleanup completed")
    
    @classmethod
    def _resolve_database_path(cls, db_path: Optional[Union[str, Path]]) -> Path:
        """
        Resolve database path from various sources.
        
        Priority:
        1. Explicit db_path parameter
        2. APM_DB_PATH environment variable
        3. AIPM_DB_PATH environment variable (backward compatibility)
        4. Auto-detect from current directory
        5. Default global path
        
        Args:
            db_path: Explicit database path
            
        Returns:
            Resolved Path object
        """
        # 1. Explicit parameter
        if db_path is not None:
            return Path(db_path).expanduser().resolve()
        
        # 2. Environment variables
        env_paths = [
            os.environ.get('APM_DB_PATH'),
            os.environ.get('AIPM_DB_PATH'),  # Backward compatibility
        ]
        
        for env_path in env_paths:
            if env_path:
                resolved = Path(env_path).expanduser().resolve()
                if resolved.exists():
                    cls._logger.info(f"Using database from environment: {resolved}")
                    return resolved
        
        # 3. Auto-detect from current directory
        current_dir = Path.cwd()
        project_db = current_dir / '.agentpm' / 'data' / 'agentpm.db'
        if project_db.exists():
            cls._logger.info(f"Using project database: {project_db}")
            return project_db
        
        # 4. Walk up parent directories to find APM project
        search_dir = current_dir
        for _ in range(10):  # Limit search depth
            candidate_db = search_dir / '.agentpm' / 'data' / 'agentpm.db'
            if candidate_db.exists():
                cls._logger.info(f"Using database from parent directory: {candidate_db}")
                return candidate_db
            
            # Move to parent directory
            parent = search_dir.parent
            if parent == search_dir:  # Reached filesystem root
                break
            search_dir = parent
        
        # 5. Default global database
        global_db = Path.home() / '.agentpm' / 'agentpm.db'
        cls._logger.info(f"Using default global database: {global_db}")
        return global_db
    
    @classmethod
    def _validate_configuration(cls, db_path: Path) -> None:
        """
        Validate database configuration and path.
        
        Args:
            db_path: Database path to validate
            
        Raises:
            FileNotFoundError: If database doesn't exist and can't be created
            PermissionError: If insufficient permissions
            ValueError: If path is invalid
        """
        # Validate path format
        if not db_path.name.endswith('.db'):
            cls._logger.warning(f"Database path doesn't end with .db: {db_path}")
        
        # Check if database exists
        if not db_path.exists():
            # Check if parent directory exists and is writable
            parent_dir = db_path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                    cls._logger.info(f"Created database directory: {parent_dir}")
                except PermissionError as e:
                    raise PermissionError(
                        f"Cannot create database directory {parent_dir}: {e}"
                    ) from e
            
            # Check write permissions
            if not os.access(parent_dir, os.W_OK):
                raise PermissionError(
                    f"Insufficient permissions to write to {parent_dir}"
                )
        
        cls._logger.debug(f"Database configuration validated: {db_path}")


# Convenience functions for common usage patterns
def initialize_database(db_path: Optional[Union[str, Path]] = None) -> DatabaseService:
    """
    Convenience function to initialize database service.
    
    Args:
        db_path: Optional database path
        
    Returns:
        DatabaseService instance
    """
    return DatabaseInitializer.initialize(db_path)


def get_database() -> DatabaseService:
    """
    Convenience function to get database service instance.
    
    Returns:
        DatabaseService instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    return DatabaseInitializer.get_instance()


def cleanup_database() -> None:
    """
    Convenience function to cleanup database resources.
    """
    DatabaseInitializer.cleanup()
