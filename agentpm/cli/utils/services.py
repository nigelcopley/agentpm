"""
Service Factory - Centralized service initialization with caching

Provides lazy-initialized, cached service instances for database, workflow,
and context operations. Single source of truth for service configuration.

Benefits:
- Uses centralized database initialization for consistency
- Caching prevents redundant service creation
- Consistent error handling across all commands
- Easy to mock for testing
- Lazy initialization (services created only when needed)
"""

from pathlib import Path
from functools import lru_cache
from agentpm.core.database import DatabaseService
from agentpm.core.workflow import WorkflowService
from agentpm.core.context import ContextService
import click


def get_database_service(project_root: Path = None) -> DatabaseService:
    """
    Get database service instance from centralized initializer.
    
    Uses the centralized DatabaseInitializer to ensure single instance
    per application with proper lifecycle management.
    
    Args:
        project_root: Optional project root (for backward compatibility)
        
    Returns:
        DatabaseService instance
        
    Raises:
        RuntimeError: If database not initialized
        
    Example:
        ```python
        db = get_database_service()
        tasks = db.tasks.list_tasks()
        ```
    """
    from agentpm.core.database.initializer import DatabaseInitializer
    
    if not DatabaseInitializer.is_initialized():
        # Try to initialize if not already done
        try:
            DatabaseInitializer.initialize()
        except Exception as e:
            raise RuntimeError(
                f"Database not initialized and initialization failed: {e}\n"
                f"Run 'apm init' to initialize the project."
            ) from e
    
    return DatabaseInitializer.get_instance()


@lru_cache(maxsize=1)
def get_workflow_service(project_root: Path = None) -> WorkflowService:
    """
    Get workflow service with centralized database dependency.

    Creates WorkflowService instance with centralized DatabaseService.
    No caching on WorkflowService itself (lightweight wrapper).

    Args:
        project_root: Optional project root (for backward compatibility)

    Returns:
        WorkflowService instance for quality gate operations

    Example:
        ```python
        workflow = get_workflow_service()
        updated_task = workflow.transition_task(task_id=123, new_status="in_progress")
        ```
    """
    db = get_database_service(project_root)
    return WorkflowService(db)


def get_context_service(project_root: Path = None) -> ContextService:
    """
    Get context service with centralized database and path dependencies.

    Creates ContextService instance with centralized DatabaseService and project path.
    No caching on ContextService itself (stateless operations).

    Args:
        project_root: Optional project root (for backward compatibility)

    Returns:
        ContextService instance for context assembly and scoring

    Example:
        ```python
        context_svc = get_context_service()
        context = context_svc.get_task_context(task_id=123)
        ```
    """
    db = get_database_service(project_root)
    return ContextService(db, project_root)


def clear_service_cache():
    """
    Clear service caches (for testing or when project changes).

    Useful when:
    - Switching between projects in same session
    - Running tests that need fresh service instances
    - Database has been modified externally

    Example:
        ```python
        # In tests
        clear_service_cache()
        db = get_database_service(project_root)  # Fresh instance
        ```
    """
    get_database_service.cache_clear()
