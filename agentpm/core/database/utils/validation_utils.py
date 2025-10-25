"""
Database Validation Utilities

Common validation patterns used across database methods for:
- Entity existence checks
- Foreign key validation
- Dependency validation
- Constraint validation

This module centralises validation logic to reduce duplication and ensure
consistent validation behaviour across all database operations.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from ..enums import EntityType


def check_entity_exists(
    service, 
    entity_type: EntityType, 
    entity_id: int
) -> bool:
    """
    Check if an entity exists in the database.
    
    Args:
        service: DatabaseService instance
        entity_type: Type of entity to check
        entity_id: ID of the entity
        
    Returns:
        True if entity exists, False otherwise
        
    Example:
        >>> exists = check_entity_exists(service, EntityType.PROJECT, 1)
        >>> exists  # True or False
    """
    table_map = {
        EntityType.PROJECT: 'projects',
        EntityType.WORK_ITEM: 'work_items',
        EntityType.TASK: 'tasks',
        EntityType.IDEA: 'ideas',
        EntityType.AGENT: 'agents',
        EntityType.CONTEXT: 'contexts',
        EntityType.RULE: 'rules',
        EntityType.DOCUMENT_REFERENCE: 'document_references',
        EntityType.EVIDENCE_SOURCE: 'evidence_sources',
        EntityType.SESSION: 'sessions',
    }
    
    table_name = table_map.get(entity_type)
    if not table_name:
        return False
    
    query = f"SELECT 1 FROM {table_name} WHERE id = ?"
    
    with service.connect() as conn:
        cursor = conn.execute(query, (entity_id,))
        return cursor.fetchone() is not None


def check_project_exists(service, project_id: int) -> bool:
    """
    Check if a project exists.
    
    Args:
        service: DatabaseService instance
        project_id: Project ID to check
        
    Returns:
        True if project exists, False otherwise
    """
    return check_entity_exists(service, EntityType.PROJECT, project_id)


def check_work_item_exists(service, work_item_id: int) -> bool:
    """
    Check if a work item exists.
    
    Args:
        service: DatabaseService instance
        work_item_id: Work item ID to check
        
    Returns:
        True if work item exists, False otherwise
    """
    return check_entity_exists(service, EntityType.WORK_ITEM, work_item_id)


def check_task_exists(service, task_id: int) -> bool:
    """
    Check if a task exists.
    
    Args:
        service: DatabaseService instance
        task_id: Task ID to check
        
    Returns:
        True if task exists, False otherwise
    """
    return check_entity_exists(service, EntityType.TASK, task_id)


def check_agent_exists(service, agent_id: int) -> bool:
    """
    Check if an agent exists.
    
    Args:
        service: DatabaseService instance
        agent_id: Agent ID to check
        
    Returns:
        True if agent exists, False otherwise
    """
    return check_entity_exists(service, EntityType.AGENT, agent_id)


def check_idea_exists(service, idea_id: int) -> bool:
    """
    Check if an idea exists.
    
    Args:
        service: DatabaseService instance
        idea_id: Idea ID to check
        
    Returns:
        True if idea exists, False otherwise
    """
    return check_entity_exists(service, EntityType.IDEA, idea_id)


def validate_foreign_key_constraints(
    service,
    constraints: Dict[str, int]
) -> List[str]:
    """
    Validate multiple foreign key constraints at once.
    
    Args:
        service: DatabaseService instance
        constraints: Dictionary mapping entity types to IDs to validate
        
    Returns:
        List of error messages for failed validations (empty if all valid)
        
    Example:
        >>> errors = validate_foreign_key_constraints(service, {
        ...     'project_id': 1,
        ...     'parent_work_item_id': 2
        ... })
        >>> if errors:
        ...     raise ValidationError("; ".join(errors))
    """
    errors = []
    
    for field_name, entity_id in constraints.items():
        if entity_id is None:
            continue
            
        # Map field names to entity types
        field_to_entity = {
            'project_id': EntityType.PROJECT,
            'work_item_id': EntityType.WORK_ITEM,
            'parent_work_item_id': EntityType.WORK_ITEM,
            'task_id': EntityType.TASK,
            'agent_id': EntityType.AGENT,
            'idea_id': EntityType.IDEA,
            'context_id': EntityType.CONTEXT,
            'rule_id': EntityType.RULE,
            'document_reference_id': EntityType.DOCUMENT_REFERENCE,
            'evidence_source_id': EntityType.EVIDENCE_SOURCE,
            'session_id': EntityType.SESSION,
        }
        
        entity_type = field_to_entity.get(field_name)
        if entity_type and not check_entity_exists(service, entity_type, entity_id):
            errors.append(f"{field_name} {entity_id} does not exist")
    
    return errors


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str]
) -> List[str]:
    """
    Validate that required fields are present and not empty.
    
    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names
        
    Returns:
        List of error messages for missing fields (empty if all present)
        
    Example:
        >>> errors = validate_required_fields({
        ...     'name': 'Test Project',
        ...     'description': ''
        ... }, ['name', 'description'])
        >>> if errors:
        ...     raise ValidationError("; ".join(errors))
    """
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Field '{field}' is required")
        elif data[field] is None:
            errors.append(f"Field '{field}' cannot be None")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"Field '{field}' cannot be empty")
    
    return errors


def validate_field_constraints(
    data: Dict[str, Any],
    constraints: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Validate field constraints (length, range, etc.).
    
    Args:
        data: Dictionary of data to validate
        constraints: Dictionary mapping field names to constraint definitions
        
    Returns:
        List of error messages for constraint violations (empty if all valid)
        
    Example:
        >>> errors = validate_field_constraints({
        ...     'name': 'Test',
        ...     'priority': 6
        ... }, {
        ...     'name': {'min_length': 3, 'max_length': 200},
        ...     'priority': {'min': 1, 'max': 5}
        ... })
    """
    errors = []
    
    for field_name, field_constraints in constraints.items():
        if field_name not in data or data[field_name] is None:
            continue
            
        value = data[field_name]
        
        # String length constraints
        if isinstance(value, str):
            if 'min_length' in field_constraints and len(value) < field_constraints['min_length']:
                errors.append(f"Field '{field_name}' must be at least {field_constraints['min_length']} characters")
            if 'max_length' in field_constraints and len(value) > field_constraints['max_length']:
                errors.append(f"Field '{field_name}' must be at most {field_constraints['max_length']} characters")
        
        # Numeric range constraints
        if isinstance(value, (int, float)):
            if 'min' in field_constraints and value < field_constraints['min']:
                errors.append(f"Field '{field_name}' must be at least {field_constraints['min']}")
            if 'max' in field_constraints and value > field_constraints['max']:
                errors.append(f"Field '{field_name}' must be at most {field_constraints['max']}")
        
        # Enum constraints
        if 'allowed_values' in field_constraints and value not in field_constraints['allowed_values']:
            allowed = ', '.join(str(v) for v in field_constraints['allowed_values'])
            errors.append(f"Field '{field_name}' must be one of: {allowed}")
    
    return errors


def check_columns_exist(
    service,
    table_name: str,
    column_names: List[str]
) -> bool:
    """
    Check if specified columns exist in a table.
    
    Used for migration compatibility - allows code to work with both
    old and new schema versions.
    
    Args:
        service: DatabaseService instance
        table_name: Name of the table to check
        column_names: List of column names to check for
        
    Returns:
        True if all columns exist, False otherwise
        
    Example:
        >>> has_tier_columns = check_columns_exist(service, 'agents', ['tier', 'last_used_at'])
        >>> if has_tier_columns:
        ...     # Use new schema
        ... else:
        ...     # Use old schema
    """
    with service.connect() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        return all(col in existing_columns for col in column_names)


def validate_unique_constraints(
    service,
    table_name: str,
    data: Dict[str, Any],
    unique_fields: List[str]
) -> List[str]:
    """
    Validate unique constraints for a table.
    
    Args:
        service: DatabaseService instance
        table_name: Name of the table
        data: Data to check for uniqueness
        unique_fields: List of field names that must be unique
        
    Returns:
        List of error messages for uniqueness violations (empty if all unique)
        
    Example:
        >>> errors = validate_unique_constraints(
        ...     service, 'projects', {'name': 'Test Project'}, ['name']
        ... )
    """
    errors = []
    
    for field in unique_fields:
        if field not in data or data[field] is None:
            continue
            
        query = f"SELECT 1 FROM {table_name} WHERE {field} = ?"
        
        with service.connect() as conn:
            cursor = conn.execute(query, (data[field],))
            if cursor.fetchone() is not None:
                errors.append(f"Field '{field}' with value '{data[field]}' already exists")
    
    return errors


def get_entity_project_id(
    service,
    entity_type: EntityType,
    entity_id: int
) -> Optional[int]:
    """
    Get the project ID for an entity.
    
    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: ID of the entity
        
    Returns:
        Project ID if found, None otherwise
        
    Example:
        >>> project_id = get_entity_project_id(service, EntityType.WORK_ITEM, 1)
        >>> project_id  # 1 or None
    """
    table_map = {
        EntityType.PROJECT: 'projects',
        EntityType.WORK_ITEM: 'work_items',
        EntityType.TASK: 'tasks',
        EntityType.IDEA: 'ideas',
        EntityType.AGENT: 'agents',
        EntityType.CONTEXT: 'contexts',
        EntityType.RULE: 'rules',
        EntityType.DOCUMENT_REFERENCE: 'document_references',
        EntityType.EVIDENCE_SOURCE: 'evidence_sources',
        EntityType.SESSION: 'sessions',
    }
    
    table_name = table_map.get(entity_type)
    if not table_name:
        return None
    
    # Projects don't have a project_id field
    if entity_type == EntityType.PROJECT:
        query = "SELECT id FROM projects WHERE id = ?"
    else:
        query = f"SELECT project_id FROM {table_name} WHERE id = ?"
    
    with service.connect() as conn:
        cursor = conn.execute(query, (entity_id,))
        row = cursor.fetchone()
        return row[0] if row else None
