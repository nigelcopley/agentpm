"""
Database Error Utilities

Common error handling patterns used across database methods for:
- Custom exception definitions
- Error message formatting
- Error context tracking
- Error recovery strategies
- Logging integration

This module provides consistent error handling across all database operations
following APM (Agent Project Manager)'s agent-first design principles.
"""

import sqlite3
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from contextlib import contextmanager


# Custom Database Exceptions

class DatabaseError(Exception):
    """Base exception for all database errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize database error.
        
        Args:
            message: Error message
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp
        }


class ValidationError(DatabaseError):
    """Exception raised when data validation fails."""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            context: Additional context
        """
        super().__init__(message, context)
        self.field = field
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation error to dictionary."""
        result = super().to_dict()
        result.update({
            'field': self.field,
            'value': str(self.value) if self.value is not None else None
        })
        return result


class TransactionError(DatabaseError):
    """Exception raised when database transaction fails."""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize transaction error.
        
        Args:
            message: Error message
            operation: Operation that failed
            context: Additional context
        """
        super().__init__(message, context)
        self.operation = operation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction error to dictionary."""
        result = super().to_dict()
        result.update({
            'operation': self.operation
        })
        return result


class ConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    pass


class ConstraintError(DatabaseError):
    """Exception raised when database constraint is violated."""
    
    def __init__(
        self, 
        message: str, 
        constraint_type: Optional[str] = None,
        constraint_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize constraint error.
        
        Args:
            message: Error message
            constraint_type: Type of constraint (UNIQUE, FOREIGN KEY, etc.)
            constraint_name: Name of the constraint
            context: Additional context
        """
        super().__init__(message, context)
        self.constraint_type = constraint_type
        self.constraint_name = constraint_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraint error to dictionary."""
        result = super().to_dict()
        result.update({
            'constraint_type': self.constraint_type,
            'constraint_name': self.constraint_name
        })
        return result


class NotFoundError(DatabaseError):
    """Exception raised when requested entity is not found."""
    
    def __init__(
        self, 
        entity_type: str, 
        entity_id: Union[int, str],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize not found error.
        
        Args:
            entity_type: Type of entity not found
            entity_id: ID of entity not found
            context: Additional context
        """
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message, context)
        self.entity_type = entity_type
        self.entity_id = entity_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert not found error to dictionary."""
        result = super().to_dict()
        result.update({
            'entity_type': self.entity_type,
            'entity_id': self.entity_id
        })
        return result


# Error Handling Utilities

def handle_sqlite_error(
    error: sqlite3.Error,
    operation: str,
    context: Optional[Dict[str, Any]] = None
) -> DatabaseError:
    """
    Convert SQLite errors to appropriate APM (Agent Project Manager) database exceptions.
    
    Args:
        error: SQLite error to convert
        operation: Operation that failed
        context: Additional context
        
    Returns:
        Appropriate APM (Agent Project Manager) database exception
    """
    error_context = context or {}
    error_context['operation'] = operation
    error_context['sqlite_error'] = str(error)
    
    if isinstance(error, sqlite3.IntegrityError):
        # Parse constraint violation
        error_msg = str(error)
        
        if "UNIQUE constraint failed" in error_msg:
            return ConstraintError(
                f"Unique constraint violation: {error_msg}",
                constraint_type="UNIQUE",
                context=error_context
            )
        elif "FOREIGN KEY constraint failed" in error_msg:
            return ConstraintError(
                f"Foreign key constraint violation: {error_msg}",
                constraint_type="FOREIGN KEY",
                context=error_context
            )
        elif "CHECK constraint failed" in error_msg:
            return ConstraintError(
                f"Check constraint violation: {error_msg}",
                constraint_type="CHECK",
                context=error_context
            )
        else:
            return ConstraintError(
                f"Integrity constraint violation: {error_msg}",
                context=error_context
            )
    
    elif isinstance(error, sqlite3.OperationalError):
        if "database is locked" in str(error):
            return ConnectionError(
                "Database is locked - another process may be using it",
                context=error_context
            )
        elif "no such table" in str(error):
            return DatabaseError(
                f"Database schema error: {error_msg}",
                context=error_context
            )
        else:
            return DatabaseError(
                f"Database operation failed: {error_msg}",
                context=error_context
            )
    
    elif isinstance(error, sqlite3.ProgrammingError):
        return DatabaseError(
            f"Database programming error: {error_msg}",
            context=error_context
        )
    
    else:
        return DatabaseError(
            f"Database error: {error_msg}",
            context=error_context
        )


def format_validation_errors(errors: List[str]) -> str:
    """
    Format a list of validation errors into a single message.
    
    Args:
        errors: List of error messages
        
    Returns:
        Formatted error message
    """
    if not errors:
        return ""
    
    if len(errors) == 1:
        return errors[0]
    
    return f"Multiple validation errors: {'; '.join(errors)}"


def create_agent_friendly_error(
    error: Exception,
    operation: str,
    guidance: Optional[str] = None,
    next_actions: Optional[List[str]] = None
) -> str:
    """
    Create an agent-friendly error message with actionable guidance.
    
    Args:
        error: Exception that occurred
        operation: Operation that failed
        guidance: Specific guidance for the agent
        next_actions: List of suggested next actions
        
    Returns:
        Formatted error message for agent consumption
    """
    error_parts = [f"❌ ERROR: {operation} failed"]
    
    # Add error details
    if isinstance(error, ValidationError):
        error_parts.append(f"Validation Error: {error.message}")
        if error.field:
            error_parts.append(f"Field: {error.field}")
    elif isinstance(error, NotFoundError):
        error_parts.append(f"Not Found: {error.message}")
    elif isinstance(error, ConstraintError):
        error_parts.append(f"Constraint Violation: {error.message}")
    else:
        error_parts.append(f"Error: {str(error)}")
    
    # Add guidance
    if guidance:
        error_parts.append(f"\n💡 GUIDANCE: {guidance}")
    
    # Add next actions
    if next_actions:
        error_parts.append("\n🎯 NEXT ACTIONS:")
        for action in next_actions:
            error_parts.append(f"  - {action}")
    
    return "\n".join(error_parts)


# Error Recovery Utilities

@contextmanager
def handle_database_errors(
    operation: str,
    logger: Optional[logging.Logger] = None,
    reraise: bool = True
):
    """
    Context manager for handling database errors with logging.
    
    Args:
        operation: Name of the operation being performed
        logger: Logger instance for error logging
        reraise: Whether to reraise the converted exception
        
    Yields:
        None
        
    Raises:
        DatabaseError: Converted database error (if reraise=True)
    """
    try:
        yield
    except sqlite3.Error as e:
        # Convert SQLite error to APM (Agent Project Manager) error
        aipm_error = handle_sqlite_error(e, operation)
        
        # Log the error
        if logger:
            logger.error(
                f"Database error in {operation}",
                extra=aipm_error.to_dict()
            )
        
        if reraise:
            raise aipm_error


def retry_on_locked_database(
    max_retries: int = 3,
    delay: float = 0.1
):
    """
    Decorator to retry operations when database is locked.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    if "database is locked" in str(e) and attempt < max_retries:
                        last_error = e
                        import time
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        raise e
                except Exception as e:
                    raise e
            
            # If we get here, all retries failed
            raise last_error
        
        return wrapper
    return decorator


# Error Context Utilities

class ErrorContext:
    """Context manager for tracking error context."""
    
    def __init__(self, operation: str, **context):
        """
        Initialize error context.
        
        Args:
            operation: Operation being performed
            **context: Additional context data
        """
        self.operation = operation
        self.context = context
        self.start_time = datetime.now()
    
    def add_context(self, **context):
        """Add additional context data."""
        self.context.update(context)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'operation': self.operation,
            'context': self.context,
            'start_time': self.start_time.isoformat(),
            'duration_ms': (datetime.now() - self.start_time).total_seconds() * 1000
        }


@contextmanager
def error_context(operation: str, **context):
    """
    Context manager for error context tracking.
    
    Args:
        operation: Operation being performed
        **context: Additional context data
        
    Yields:
        ErrorContext instance
    """
    error_ctx = ErrorContext(operation, **context)
    try:
        yield error_ctx
    except Exception as e:
        # Add context to exception if it's a DatabaseError
        if isinstance(e, DatabaseError):
            e.context.update(error_ctx.to_dict())
        raise


# Logging Utilities

def log_database_operation(
    logger: logging.Logger,
    operation: str,
    success: bool,
    duration_ms: float,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log database operation with structured data.
    
    Args:
        logger: Logger instance
        operation: Operation name
        success: Whether operation succeeded
        duration_ms: Operation duration in milliseconds
        context: Additional context data
    """
    log_data = {
        'event': 'database_operation',
        'operation': operation,
        'success': success,
        'duration_ms': duration_ms,
        'timestamp': datetime.now().isoformat()
    }
    
    if context:
        log_data.update(context)
    
    if success:
        logger.info(f"Database operation completed: {operation}", extra=log_data)
    else:
        logger.error(f"Database operation failed: {operation}", extra=log_data)


def log_validation_error(
    logger: logging.Logger,
    field: str,
    value: Any,
    error_message: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Log validation error with structured data.
    
    Args:
        logger: Logger instance
        field: Field that failed validation
        value: Value that failed validation
        error_message: Error message
        context: Additional context data
    """
    log_data = {
        'event': 'validation_error',
        'field': field,
        'value': str(value) if value is not None else None,
        'error_message': error_message,
        'timestamp': datetime.now().isoformat()
    }
    
    if context:
        log_data.update(context)
    
    logger.warning(f"Validation error in field '{field}': {error_message}", extra=log_data)
