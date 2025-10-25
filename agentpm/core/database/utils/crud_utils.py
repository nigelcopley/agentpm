"""
Database CRUD Utilities

Common CRUD operation patterns used across database methods for:
- Standard create, read, update, delete operations
- List operations with filtering
- Batch operations
- Transaction management

This module provides reusable CRUD patterns that follow APM (Agent Project Manager)'s
three-layer architecture (Models → Adapters → Methods).
"""

import sqlite3
from typing import Optional, List, Dict, Any, Type, TypeVar, Generic
from datetime import datetime

from ..service import ValidationError, TransactionError

# Type variable for Pydantic models
T = TypeVar('T')


class CRUDOperations(Generic[T]):
    """
    Generic CRUD operations for database entities.
    
    This class provides standard CRUD patterns that can be used
    across all entity types in APM (Agent Project Manager).
    """
    
    def __init__(
        self,
        table_name: str,
        model_class: Type[T],
        adapter_class: Type,
        service
    ):
        """
        Initialize CRUD operations for an entity type.
        
        Args:
            table_name: Database table name
            model_class: Pydantic model class
            adapter_class: Adapter class for model ↔ database conversion
            service: DatabaseService instance
        """
        self.table_name = table_name
        self.model_class = model_class
        self.adapter_class = adapter_class
        self.service = service
    
    def create(
        self,
        model: T,
        validate_dependencies: bool = True,
        foreign_key_checks: Optional[Dict[str, int]] = None
    ) -> T:
        """
        Create a new entity with validation.
        
        Args:
            model: Pydantic model to create
            validate_dependencies: Whether to validate foreign key dependencies
            foreign_key_checks: Dictionary of foreign key validations
            
        Returns:
            Created model with database ID
            
        Raises:
            ValidationError: If validation fails
            TransactionError: If database operation fails
        """
        from .validation_utils import validate_foreign_key_constraints
        
        # Validate foreign key dependencies
        if validate_dependencies and foreign_key_checks:
            errors = validate_foreign_key_constraints(self.service, foreign_key_checks)
            if errors:
                raise ValidationError("; ".join(errors))
        
        # Convert model to database format
        db_data = self.adapter_class.to_db(model)
        
        # Build insert query dynamically
        columns = list(db_data.keys())
        placeholders = ', '.join('?' * len(columns))
        column_names = ', '.join(columns)
        
        query = f"INSERT INTO {self.table_name} ({column_names}) VALUES ({placeholders})"
        params = tuple(db_data[col] for col in columns)
        
        try:
            with self.service.transaction() as conn:
                cursor = conn.execute(query, params)
                entity_id = cursor.lastrowid
            
            # Return created entity
            return self.get(entity_id)
            
        except sqlite3.Error as e:
            raise TransactionError(f"Failed to create {self.table_name}: {e}") from e
    
    def get(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Entity model if found, None otherwise
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        
        with self.service.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (entity_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self.adapter_class.from_db(dict(row))
    
    def update(
        self,
        entity_id: int,
        updates: Dict[str, Any],
        validate_constraints: bool = True
    ) -> Optional[T]:
        """
        Update entity with new data.
        
        Args:
            entity_id: ID of the entity to update
            updates: Dictionary of field updates
            validate_constraints: Whether to validate constraints
            
        Returns:
            Updated entity model if found, None otherwise
            
        Raises:
            ValidationError: If validation fails
            TransactionError: If database operation fails
        """
        if not updates:
            return self.get(entity_id)
        
        # Get existing entity
        existing = self.get(entity_id)
        if not existing:
            return None
        
        # Create updated model
        existing_data = existing.model_dump()
        existing_data.update(updates)
        updated_model = self.model_class(**existing_data)
        
        # Convert to database format
        db_data = self.adapter_class.to_db(updated_model)
        
        # Build update query
        set_clauses = ', '.join(f"{col} = ?" for col in db_data.keys() if col != 'id')
        params = tuple(db_data[col] for col in db_data.keys() if col != 'id')
        params += (entity_id,)  # Add WHERE clause parameter
        
        query = f"UPDATE {self.table_name} SET {set_clauses} WHERE id = ?"
        
        try:
            with self.service.transaction() as conn:
                cursor = conn.execute(query, params)
                if cursor.rowcount == 0:
                    return None
            
            return self.get(entity_id)
            
        except sqlite3.Error as e:
            raise TransactionError(f"Failed to update {self.table_name}: {e}") from e
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            TransactionError: If database operation fails
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        
        try:
            with self.service.transaction() as conn:
                cursor = conn.execute(query, (entity_id,))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            raise TransactionError(f"Failed to delete {self.table_name}: {e}") from e
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        List entities with optional filtering and pagination.
        
        Args:
            filters: Dictionary of field filters
            order_by: ORDER BY clause (e.g., "created_at DESC")
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of entity models
        """
        query = f"SELECT * FROM {self.table_name}"
        params = []
        
        # Add WHERE clause
        if filters:
            where_conditions = []
            for field, value in filters.items():
                if value is not None:
                    if isinstance(value, list):
                        # Handle IN clause for list values
                        placeholders = ', '.join('?' * len(value))
                        where_conditions.append(f"{field} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_conditions.append(f"{field} = ?")
                        params.append(value)
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
        
        # Add ORDER BY clause
        if order_by:
            query += f" ORDER BY {order_by}"
        
        # Add LIMIT and OFFSET
        if limit:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
        
        with self.service.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, tuple(params))
            rows = cursor.fetchall()
        
        return [self.adapter_class.from_db(dict(row)) for row in rows]
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching entities
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params = []
        
        # Add WHERE clause
        if filters:
            where_conditions = []
            for field, value in filters.items():
                if value is not None:
                    if isinstance(value, list):
                        placeholders = ', '.join('?' * len(value))
                        where_conditions.append(f"{field} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_conditions.append(f"{field} = ?")
                        params.append(value)
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
        
        with self.service.connect() as conn:
            cursor = conn.execute(query, tuple(params))
            return cursor.fetchone()[0]
    
    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            True if entity exists, False otherwise
        """
        query = f"SELECT 1 FROM {self.table_name} WHERE id = ?"
        
        with self.service.connect() as conn:
            cursor = conn.execute(query, (entity_id,))
            return cursor.fetchone() is not None


def create_entity_with_validation(
    service,
    table_name: str,
    model: T,
    adapter_class: Type,
    foreign_key_checks: Optional[Dict[str, int]] = None,
    unique_checks: Optional[List[str]] = None
) -> T:
    """
    Create entity with comprehensive validation.
    
    Args:
        service: DatabaseService instance
        table_name: Database table name
        model: Pydantic model to create
        adapter_class: Adapter class for model ↔ database conversion
        foreign_key_checks: Dictionary of foreign key validations
        unique_checks: List of fields to check for uniqueness
        
    Returns:
        Created model with database ID
        
    Raises:
        ValidationError: If validation fails
    """
    from .validation_utils import (
        validate_foreign_key_constraints,
        validate_unique_constraints
    )
    
    # Validate foreign key dependencies
    if foreign_key_checks:
        errors = validate_foreign_key_constraints(service, foreign_key_checks)
        if errors:
            raise ValidationError("; ".join(errors))
    
    # Validate unique constraints
    if unique_checks:
        db_data = adapter_class.to_db(model)
        errors = validate_unique_constraints(service, table_name, db_data, unique_checks)
        if errors:
            raise ValidationError("; ".join(errors))
    
    # Create the entity
    crud = CRUDOperations(table_name, type(model), adapter_class, service)
    return crud.create(model, validate_dependencies=False)


def batch_create_entities(
    service,
    table_name: str,
    models: List[T],
    adapter_class: Type,
    batch_size: int = 100
) -> List[T]:
    """
    Create multiple entities in batches for better performance.
    
    Args:
        service: DatabaseService instance
        table_name: Database table name
        models: List of Pydantic models to create
        adapter_class: Adapter class for model ↔ database conversion
        batch_size: Number of entities to create per batch
        
    Returns:
        List of created models with database IDs
        
    Raises:
        TransactionError: If database operation fails
    """
    if not models:
        return []
    
    created_entities = []
    
    # Process in batches
    for i in range(0, len(models), batch_size):
        batch = models[i:i + batch_size]
        
        # Convert models to database format
        db_data_list = [adapter_class.to_db(model) for model in batch]
        
        if not db_data_list:
            continue
        
        # Build batch insert query
        columns = list(db_data_list[0].keys())
        placeholders = ', '.join('?' * len(columns))
        column_names = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        try:
            with service.transaction() as conn:
                cursor = conn.executemany(
                    query,
                    [tuple(data[col] for col in columns) for data in db_data_list]
                )
                
                # Get the IDs of created entities
                first_id = cursor.lastrowid - len(batch) + 1
                for j, model in enumerate(batch):
                    entity_id = first_id + j
                    created_entities.append(service.get(entity_id))
                    
        except sqlite3.Error as e:
            raise TransactionError(f"Failed to batch create {table_name}: {e}") from e
    
    return created_entities


def soft_delete_entity(
    service,
    table_name: str,
    entity_id: int,
    deleted_at_field: str = "deleted_at"
) -> bool:
    """
    Soft delete an entity by setting a deleted_at timestamp.
    
    Args:
        service: DatabaseService instance
        table_name: Database table name
        entity_id: ID of the entity to soft delete
        deleted_at_field: Name of the deleted_at field
        
    Returns:
        True if entity was soft deleted, False if not found
    """
    query = f"UPDATE {table_name} SET {deleted_at_field} = ? WHERE id = ?"
    deleted_at = datetime.now().isoformat()
    
    try:
        with service.transaction() as conn:
            cursor = conn.execute(query, (deleted_at, entity_id))
            return cursor.rowcount > 0
            
    except sqlite3.Error as e:
        raise TransactionError(f"Failed to soft delete {table_name}: {e}") from e


def restore_soft_deleted_entity(
    service,
    table_name: str,
    entity_id: int,
    deleted_at_field: str = "deleted_at"
) -> bool:
    """
    Restore a soft deleted entity by clearing the deleted_at timestamp.
    
    Args:
        service: DatabaseService instance
        table_name: Database table name
        entity_id: ID of the entity to restore
        deleted_at_field: Name of the deleted_at field
        
    Returns:
        True if entity was restored, False if not found
    """
    query = f"UPDATE {table_name} SET {deleted_at_field} = NULL WHERE id = ?"
    
    try:
        with service.transaction() as conn:
            cursor = conn.execute(query, (entity_id,))
            return cursor.rowcount > 0
            
    except sqlite3.Error as e:
        raise TransactionError(f"Failed to restore {table_name}: {e}") from e
