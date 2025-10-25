"""
Work Items CRUD Methods - Refactored Example Using Database Utilities

This is an example of how to refactor existing database methods to use
the new database utilities. This shows the before/after comparison
and demonstrates the benefits of using the utility modules.

Key improvements:
- Reduced code duplication
- Consistent error handling
- Better validation
- Cleaner, more maintainable code
"""

from typing import Optional, List
import sqlite3

from ..models import WorkItem
from ..adapters import WorkItemAdapter
from ..enums import WorkItemStatus, WorkItemType
from ..utils import (
    # Validation utilities
    validate_foreign_key_constraints,
    check_columns_exist,
    
    # CRUD utilities
    CRUDOperations,
    create_entity_with_validation,
    
    # Query utilities
    QueryBuilder,
    build_filter_query,
    
    # Error utilities
    ValidationError,
    handle_database_errors,
    error_context,
    
    # Migration utilities
    check_columns_exist as migration_check_columns_exist
)


# Initialize CRUD operations for work items
def _get_work_item_crud(service):
    """Get CRUD operations instance for work items."""
    return CRUDOperations('work_items', WorkItem, WorkItemAdapter, service)


def create_work_item(service, work_item: WorkItem) -> WorkItem:
    """
    Create a new work item with dependency validation.
    
    REFACTORED VERSION: Uses database utilities for cleaner, more maintainable code.
    
    Validates:
    - project_id exists
    - parent_work_item_id exists (if provided)
    
    Args:
        service: DatabaseService instance
        work_item: WorkItem model to create
        
    Returns:
        Created WorkItem with database ID
        
    Raises:
        ValidationError: If dependencies don't exist
    """
    with error_context("create_work_item", work_item_id=work_item.id):
        # Prepare foreign key validations
        foreign_key_checks = {'project_id': work_item.project_id}
        if work_item.parent_work_item_id:
            foreign_key_checks['parent_work_item_id'] = work_item.parent_work_item_id
        
        # Use utility for validation and creation
        return create_entity_with_validation(
            service=service,
            table_name='work_items',
            model=work_item,
            adapter_class=WorkItemAdapter,
            foreign_key_checks=foreign_key_checks
        )


def get_work_item(service, work_item_id: int) -> Optional[WorkItem]:
    """
    Get work item by ID.
    
    REFACTORED VERSION: Uses CRUD operations for consistency.
    """
    crud = _get_work_item_crud(service)
    return crud.get(work_item_id)


def update_work_item(service, work_item_id: int, **updates) -> Optional[WorkItem]:
    """
    Update work item with new data.
    
    REFACTORED VERSION: Uses CRUD operations and validation utilities.
    """
    with error_context("update_work_item", work_item_id=work_item_id, updates=updates):
        crud = _get_work_item_crud(service)
        
        # Validate foreign key constraints if updating related fields
        foreign_key_checks = {}
        if 'project_id' in updates:
            foreign_key_checks['project_id'] = updates['project_id']
        if 'parent_work_item_id' in updates and updates['parent_work_item_id']:
            foreign_key_checks['parent_work_item_id'] = updates['parent_work_item_id']
        
        if foreign_key_checks:
            errors = validate_foreign_key_constraints(service, foreign_key_checks)
            if errors:
                raise ValidationError("; ".join(errors))
        
        return crud.update(work_item_id, updates)


def delete_work_item(service, work_item_id: int) -> bool:
    """
    Delete work item by ID.
    
    REFACTORED VERSION: Uses CRUD operations for consistency.
    """
    crud = _get_work_item_crud(service)
    return crud.delete(work_item_id)


def list_work_items(
    service,
    project_id: Optional[int] = None,
    status: Optional[WorkItemStatus] = None,
    type: Optional[WorkItemType] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[WorkItem]:
    """
    List work items with optional filters.
    
    REFACTORED VERSION: Uses query utilities for dynamic filtering.
    """
    # Build filters
    filters = {}
    if project_id:
        filters['project_id'] = project_id
    if status:
        filters['status'] = status.value
    if type:
        filters['type'] = type.value
    
    # Use query builder for complex queries
    builder = QueryBuilder('work_items')
    
    # Add filters
    for field, value in filters.items():
        builder.where(field, '=', value)
    
    # Add ordering
    builder.order_by('priority', 'ASC')
    builder.order_by('created_at', 'DESC')
    
    # Add pagination
    if limit:
        builder.limit(limit)
    if offset:
        builder.offset(offset)
    
    # Execute query
    query, params = builder.build()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    return [WorkItemAdapter.from_db(dict(row)) for row in rows]


def list_work_items_alternative(
    service,
    project_id: Optional[int] = None,
    status: Optional[WorkItemStatus] = None,
    type: Optional[WorkItemType] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[WorkItem]:
    """
    Alternative implementation using build_filter_query utility.
    """
    # Build filters
    filters = {}
    if project_id:
        filters['project_id'] = project_id
    if status:
        filters['status'] = status.value
    if type:
        filters['type'] = type.value
    
    # Use utility function
    query, params = build_filter_query(
        table_name='work_items',
        filters=filters,
        order_by='priority ASC, created_at DESC',
        limit=limit,
        offset=offset
    )
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    return [WorkItemAdapter.from_db(dict(row)) for row in rows]


def get_child_work_items(service, parent_id: int) -> List[WorkItem]:
    """
    Get child work items for a parent work item.
    
    REFACTORED VERSION: Uses query utilities for cleaner code.
    """
    builder = QueryBuilder('work_items')
    builder.where('parent_work_item_id', '=', parent_id)
    builder.order_by('priority', 'ASC')
    builder.order_by('created_at', 'DESC')
    
    query, params = builder.build()
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    return [WorkItemAdapter.from_db(dict(row)) for row in rows]


def count_work_items_by_status(service, project_id: int) -> dict:
    """
    Count work items by status for a project.
    
    REFACTORED VERSION: Uses aggregation query utilities.
    """
    from ..utils import build_aggregation_query
    
    query, params = build_aggregation_query(
        table_name='work_items',
        aggregations={
            'total_count': 'COUNT(*)',
            'active_count': 'SUM(CASE WHEN status = "in_progress" THEN 1 ELSE 0 END)',
            'completed_count': 'SUM(CASE WHEN status = "completed" THEN 1 ELSE 0 END)'
        },
        filters={'project_id': project_id}
    )
    
    with service.connect() as conn:
        cursor = conn.execute(query, params)
        row = cursor.fetchone()
    
    return {
        'total': row[0],
        'active': row[1],
        'completed': row[2]
    }


def get_work_items_with_tasks(service, project_id: int) -> List[dict]:
    """
    Get work items with their associated tasks.
    
    REFACTORED VERSION: Uses join query utilities.
    """
    from ..utils import build_join_query
    
    query, params = build_join_query(
        base_table='work_items',
        joins=[
            ('tasks', 'LEFT', 'work_items.id = tasks.work_item_id')
        ],
        select_fields=[
            'work_items.*',
            'COUNT(tasks.id) as task_count',
            'SUM(tasks.effort_hours) as total_effort'
        ],
        filters={'work_items.project_id': project_id},
        order_by='work_items.priority ASC'
    )
    
    # Add GROUP BY for aggregation
    query = query.replace('ORDER BY', 'GROUP BY work_items.id ORDER BY')
    
    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    return [dict(row) for row in rows]


# Migration compatibility example
def create_work_item_with_migration_check(service, work_item: WorkItem) -> WorkItem:
    """
    Create work item with migration compatibility checks.
    
    REFACTORED VERSION: Uses migration utilities for schema compatibility.
    """
    with error_context("create_work_item_with_migration_check"):
        # Check if migration 0011 columns exist
        has_migration_columns = migration_check_columns_exist(
            service, 'work_items', ['phase', 'due_date', 'not_before']
        )
        
        # Prepare foreign key validations
        foreign_key_checks = {'project_id': work_item.project_id}
        if work_item.parent_work_item_id:
            foreign_key_checks['parent_work_item_id'] = work_item.parent_work_item_id
        
        # Create with appropriate validation
        created_item = create_entity_with_validation(
            service=service,
            table_name='work_items',
            model=work_item,
            adapter_class=WorkItemAdapter,
            foreign_key_checks=foreign_key_checks
        )
        
        # Log migration compatibility
        if has_migration_columns:
            service.logger.debug("Created work item with migration 0011 fields")
        else:
            service.logger.debug("Created work item with base schema")
        
        return created_item


# Error handling example
def create_work_item_with_error_handling(service, work_item: WorkItem) -> WorkItem:
    """
    Create work item with comprehensive error handling.
    
    REFACTORED VERSION: Uses error utilities for consistent error handling.
    """
    from ..utils import handle_database_errors, create_agent_friendly_error
    
    try:
        with handle_database_errors("create_work_item"):
            # Prepare foreign key validations
            foreign_key_checks = {'project_id': work_item.project_id}
            if work_item.parent_work_item_id:
                foreign_key_checks['parent_work_item_id'] = work_item.parent_work_item_id
            
            return create_entity_with_validation(
                service=service,
                table_name='work_items',
                model=work_item,
                adapter_class=WorkItemAdapter,
                foreign_key_checks=foreign_key_checks
            )
    
    except ValidationError as e:
        # Create agent-friendly error message
        error_msg = create_agent_friendly_error(
            error=e,
            operation="create_work_item",
            guidance="Ensure all referenced entities exist before creating work item",
            next_actions=[
                "Check that project exists",
                "Verify parent work item exists (if specified)",
                "Retry the operation"
            ]
        )
        raise ValidationError(error_msg) from e
