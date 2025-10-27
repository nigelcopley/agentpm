"""
Database Core Module

Provides database service with connection management, transaction handling,
and CRUD operations for all APM (Agent Project Manager) entities.

Usage:
    # Direct usage (legacy)
    from agentpm.core.database import DatabaseService
    service = DatabaseService("~/.agentpm/agentpm.db")
    
    # Centralized initialization (recommended)
    from agentpm.core.database import DatabaseInitializer
    db = DatabaseInitializer.initialize()
"""

from .service import (
    DatabaseService,
    DatabaseError,
    ConnectionError,
    TransactionError,
    ValidationError,
)

from .initializer import (
    DatabaseInitializer,
    initialize_database,
    get_database,
    cleanup_database,
)

__all__ = [
    "DatabaseService",
    "DatabaseError",
    "ConnectionError",
    "TransactionError",
    "ValidationError",
    "DatabaseInitializer",
    "initialize_database",
    "get_database",
    "cleanup_database",
]