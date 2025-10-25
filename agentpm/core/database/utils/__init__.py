"""
Database Utilities

Common utilities for database operations in APM (Agent Project Manager):
- Validation utilities for entity existence and constraints
- CRUD utilities for standard database operations
- Query utilities for dynamic SQL building
- Error utilities for consistent error handling
- Migration utilities for schema management
- Task-agent mapping utilities for workflow integration

These utilities follow APM (Agent Project Manager)'s three-layer architecture and
agent-first design principles.
"""

from .validation_utils import (
    check_entity_exists,
    check_project_exists,
    check_work_item_exists,
    check_task_exists,
    check_agent_exists,
    check_idea_exists,
    validate_foreign_key_constraints,
    validate_required_fields,
    validate_field_constraints,
    check_columns_exist,
    validate_unique_constraints,
    get_entity_project_id
)

from .crud_utils import (
    CRUDOperations,
    create_entity_with_validation,
    batch_create_entities,
    soft_delete_entity,
    restore_soft_deleted_entity
)

from .query_utils import (
    QueryBuilder,
    SortDirection,
    FilterOperator,
    build_filter_query,
    build_count_query,
    build_exists_query,
    build_aggregation_query,
    build_join_query
)

from .error_utils import (
    DatabaseError,
    ValidationError,
    TransactionError,
    ConnectionError,
    ConstraintError,
    NotFoundError,
    handle_sqlite_error,
    format_validation_errors,
    create_agent_friendly_error,
    handle_database_errors,
    retry_on_locked_database,
    ErrorContext,
    error_context,
    log_database_operation,
    log_validation_error
)

from .migration_utils import (
    get_schema_version,
    record_migration,
    rollback_migration,
    get_migration_history,
    check_table_exists,
    check_column_exists,
    check_columns_exist,
    get_table_columns,
    get_table_indexes,
    get_table_foreign_keys,
    validate_table_schema,
    add_column_if_not_exists,
    create_index_if_not_exists,
    drop_index_if_exists,
    backup_table_data,
    restore_table_data,
    get_database_info,
    validate_database_integrity,
    optimize_database
)

from .task_agent_mapping import (
    get_agent_for_task_type,
    get_all_supported_task_types,
    get_all_agent_roles,
    get_task_types_for_agent,
    validate_task_agent_mapping,
    get_mapping_coverage_report
)

__all__ = [
    # Validation utilities
    'check_entity_exists',
    'check_project_exists',
    'check_work_item_exists',
    'check_task_exists',
    'check_agent_exists',
    'check_idea_exists',
    'validate_foreign_key_constraints',
    'validate_required_fields',
    'validate_field_constraints',
    'check_columns_exist',
    'validate_unique_constraints',
    'get_entity_project_id',
    
    # CRUD utilities
    'CRUDOperations',
    'create_entity_with_validation',
    'batch_create_entities',
    'soft_delete_entity',
    'restore_soft_deleted_entity',
    
    # Query utilities
    'QueryBuilder',
    'SortDirection',
    'FilterOperator',
    'build_filter_query',
    'build_count_query',
    'build_exists_query',
    'build_aggregation_query',
    'build_join_query',
    
    # Error utilities
    'DatabaseError',
    'ValidationError',
    'TransactionError',
    'ConnectionError',
    'ConstraintError',
    'NotFoundError',
    'handle_sqlite_error',
    'format_validation_errors',
    'create_agent_friendly_error',
    'handle_database_errors',
    'retry_on_locked_database',
    'ErrorContext',
    'error_context',
    'log_database_operation',
    'log_validation_error',
    
    # Migration utilities
    'get_schema_version',
    'record_migration',
    'rollback_migration',
    'get_migration_history',
    'check_table_exists',
    'check_column_exists',
    'check_columns_exist',
    'get_table_columns',
    'get_table_indexes',
    'get_table_foreign_keys',
    'validate_table_schema',
    'add_column_if_not_exists',
    'create_index_if_not_exists',
    'drop_index_if_exists',
    'backup_table_data',
    'restore_table_data',
    'get_database_info',
    'validate_database_integrity',
    'optimize_database',
    
    # Task-agent mapping utilities
    'get_agent_for_task_type',
    'get_all_supported_task_types',
    'get_all_agent_roles',
    'get_task_types_for_agent',
    'validate_task_agent_mapping',
    'get_mapping_coverage_report'
]
