"""
Database Query Utilities

Common query building patterns used across database methods for:
- Dynamic WHERE clause construction
- Filter building
- Pagination
- Sorting
- Complex joins
- Aggregation queries

This module provides reusable query building utilities that ensure
consistent SQL generation across all database operations.
"""

from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum


class SortDirection(Enum):
    """Sort direction enumeration."""
    ASC = "ASC"
    DESC = "DESC"


class FilterOperator(Enum):
    """Filter operator enumeration."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"


class QueryBuilder:
    """
    SQL query builder with support for dynamic WHERE clauses, sorting, and pagination.
    
    This class provides a fluent interface for building complex SQL queries
    while maintaining type safety and preventing SQL injection.
    """
    
    def __init__(self, base_table: str):
        """
        Initialize query builder.
        
        Args:
            base_table: Base table name for the query
        """
        self.base_table = base_table
        self.select_fields = ["*"]
        self.joins = []
        self.where_conditions = []
        self.where_params = []
        self.group_by_fields = []
        self.having_conditions = []
        self.having_params = []
        self.order_by_fields = []
        self.limit_value = None
        self.offset_value = None
    
    def select(self, fields: Union[str, List[str]]) -> 'QueryBuilder':
        """
        Set SELECT fields.
        
        Args:
            fields: Field name(s) to select
            
        Returns:
            Self for method chaining
        """
        if isinstance(fields, str):
            self.select_fields = [fields]
        else:
            self.select_fields = fields
        return self
    
    def join(
        self,
        table: str,
        condition: str,
        join_type: str = "INNER"
    ) -> 'QueryBuilder':
        """
        Add a JOIN clause.
        
        Args:
            table: Table to join
            condition: JOIN condition
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)
            
        Returns:
            Self for method chaining
        """
        self.joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def where(
        self,
        field: str,
        operator: Union[FilterOperator, str],
        value: Any = None
    ) -> 'QueryBuilder':
        """
        Add a WHERE condition.
        
        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare against
            
        Returns:
            Self for method chaining
        """
        if isinstance(operator, FilterOperator):
            operator = operator.value
        
        if operator in ["IS NULL", "IS NOT NULL"]:
            self.where_conditions.append(f"{field} {operator}")
        elif operator in ["IN", "NOT IN"]:
            if isinstance(value, (list, tuple)):
                placeholders = ", ".join("?" * len(value))
                self.where_conditions.append(f"{field} {operator} ({placeholders})")
                self.where_params.extend(value)
            else:
                raise ValueError(f"IN/NOT IN operator requires a list or tuple, got {type(value)}")
        elif operator == "BETWEEN":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                self.where_conditions.append(f"{field} BETWEEN ? AND ?")
                self.where_params.extend(value)
            else:
                raise ValueError("BETWEEN operator requires a list/tuple with exactly 2 values")
        else:
            self.where_conditions.append(f"{field} {operator} ?")
            self.where_params.append(value)
        
        return self
    
    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """
        Add WHERE field IN (values) condition.
        
        Args:
            field: Field name
            values: List of values
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.IN, values)
    
    def where_not_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """
        Add WHERE field NOT IN (values) condition.
        
        Args:
            field: Field name
            values: List of values
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.NOT_IN, values)
    
    def where_like(self, field: str, pattern: str) -> 'QueryBuilder':
        """
        Add WHERE field LIKE pattern condition.
        
        Args:
            field: Field name
            pattern: LIKE pattern
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.LIKE, pattern)
    
    def where_null(self, field: str) -> 'QueryBuilder':
        """
        Add WHERE field IS NULL condition.
        
        Args:
            field: Field name
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.IS_NULL)
    
    def where_not_null(self, field: str) -> 'QueryBuilder':
        """
        Add WHERE field IS NOT NULL condition.
        
        Args:
            field: Field name
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.IS_NOT_NULL)
    
    def where_between(self, field: str, start: Any, end: Any) -> 'QueryBuilder':
        """
        Add WHERE field BETWEEN start AND end condition.
        
        Args:
            field: Field name
            start: Start value
            end: End value
            
        Returns:
            Self for method chaining
        """
        return self.where(field, FilterOperator.BETWEEN, [start, end])
    
    def group_by(self, fields: Union[str, List[str]]) -> 'QueryBuilder':
        """
        Add GROUP BY clause.
        
        Args:
            fields: Field name(s) to group by
            
        Returns:
            Self for method chaining
        """
        if isinstance(fields, str):
            self.group_by_fields = [fields]
        else:
            self.group_by_fields = fields
        return self
    
    def having(
        self,
        field: str,
        operator: Union[FilterOperator, str],
        value: Any = None
    ) -> 'QueryBuilder':
        """
        Add a HAVING condition.
        
        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare against
            
        Returns:
            Self for method chaining
        """
        if isinstance(operator, FilterOperator):
            operator = operator.value
        
        if operator in ["IS NULL", "IS NOT NULL"]:
            self.having_conditions.append(f"{field} {operator}")
        elif operator in ["IN", "NOT IN"]:
            if isinstance(value, (list, tuple)):
                placeholders = ", ".join("?" * len(value))
                self.having_conditions.append(f"{field} {operator} ({placeholders})")
                self.having_params.extend(value)
            else:
                raise ValueError(f"IN/NOT IN operator requires a list or tuple, got {type(value)}")
        else:
            self.having_conditions.append(f"{field} {operator} ?")
            self.having_params.append(value)
        
        return self
    
    def order_by(
        self,
        field: str,
        direction: Union[SortDirection, str] = SortDirection.ASC
    ) -> 'QueryBuilder':
        """
        Add ORDER BY clause.
        
        Args:
            field: Field name to sort by
            direction: Sort direction
            
        Returns:
            Self for method chaining
        """
        if isinstance(direction, SortDirection):
            direction = direction.value
        
        self.order_by_fields.append(f"{field} {direction}")
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        Add LIMIT clause.
        
        Args:
            count: Maximum number of results
            
        Returns:
            Self for method chaining
        """
        self.limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """
        Add OFFSET clause.
        
        Args:
            count: Number of results to skip
            
        Returns:
            Self for method chaining
        """
        self.offset_value = count
        return self
    
    def paginate(self, page: int, page_size: int) -> 'QueryBuilder':
        """
        Add pagination (LIMIT and OFFSET).
        
        Args:
            page: Page number (1-based)
            page_size: Number of results per page
            
        Returns:
            Self for method chaining
        """
        self.limit_value = page_size
        self.offset_value = (page - 1) * page_size
        return self
    
    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the final SQL query.
        
        Returns:
            Tuple of (SQL query, parameters)
        """
        # Build SELECT clause
        select_clause = f"SELECT {', '.join(self.select_fields)}"
        
        # Build FROM clause
        from_clause = f"FROM {self.base_table}"
        
        # Build JOIN clauses
        join_clause = " ".join(self.joins) if self.joins else ""
        
        # Build WHERE clause
        where_clause = ""
        if self.where_conditions:
            where_clause = f"WHERE {' AND '.join(self.where_conditions)}"
        
        # Build GROUP BY clause
        group_by_clause = ""
        if self.group_by_fields:
            group_by_clause = f"GROUP BY {', '.join(self.group_by_fields)}"
        
        # Build HAVING clause
        having_clause = ""
        if self.having_conditions:
            having_clause = f"HAVING {' AND '.join(self.having_conditions)}"
        
        # Build ORDER BY clause
        order_by_clause = ""
        if self.order_by_fields:
            order_by_clause = f"ORDER BY {', '.join(self.order_by_fields)}"
        
        # Build LIMIT clause
        limit_clause = ""
        if self.limit_value is not None:
            limit_clause = f"LIMIT {self.limit_value}"
        
        # Build OFFSET clause
        offset_clause = ""
        if self.offset_value is not None:
            offset_clause = f"OFFSET {self.offset_value}"
        
        # Combine all clauses
        query_parts = [
            select_clause,
            from_clause,
            join_clause,
            where_clause,
            group_by_clause,
            having_clause,
            order_by_clause,
            limit_clause,
            offset_clause
        ]
        
        query = " ".join(part for part in query_parts if part)
        
        # Combine parameters
        params = self.where_params + self.having_params
        
        return query, params


def build_filter_query(
    table_name: str,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> Tuple[str, List[Any]]:
    """
    Build a filtered query with common patterns.
    
    Args:
        table_name: Name of the table to query
        filters: Dictionary of field filters
        order_by: ORDER BY clause
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Tuple of (SQL query, parameters)
        
    Example:
        >>> query, params = build_filter_query(
        ...     'work_items',
        ...     {'project_id': 1, 'status': 'active'},
        ...     'created_at DESC',
        ...     10
        ... )
    """
    builder = QueryBuilder(table_name)
    
    # Add filters
    if filters:
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    builder.where_in(field, value)
                else:
                    builder.where(field, FilterOperator.EQUALS, value)
    
    # Add ordering
    if order_by:
        # Parse order_by string (e.g., "field ASC" or "field DESC")
        parts = order_by.split()
        field = parts[0]
        direction = parts[1] if len(parts) > 1 else SortDirection.ASC
        builder.order_by(field, direction)
    
    # Add pagination
    if limit:
        builder.limit(limit)
    if offset:
        builder.offset(offset)
    
    return builder.build()


def build_count_query(
    table_name: str,
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[Any]]:
    """
    Build a COUNT query with filters.
    
    Args:
        table_name: Name of the table to count
        filters: Dictionary of field filters
        
    Returns:
        Tuple of (SQL query, parameters)
    """
    builder = QueryBuilder(table_name).select("COUNT(*)")
    
    # Add filters
    if filters:
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    builder.where_in(field, value)
                else:
                    builder.where(field, FilterOperator.EQUALS, value)
    
    return builder.build()


def build_exists_query(
    table_name: str,
    filters: Dict[str, Any]
) -> Tuple[str, List[Any]]:
    """
    Build an EXISTS query with filters.
    
    Args:
        table_name: Name of the table to check
        filters: Dictionary of field filters
        
    Returns:
        Tuple of (SQL query, parameters)
    """
    builder = QueryBuilder(table_name).select("1")
    
    # Add filters
    for field, value in filters.items():
        if value is not None:
            if isinstance(value, list):
                builder.where_in(field, value)
            else:
                builder.where(field, FilterOperator.EQUALS, value)
    
    return builder.build()


def build_aggregation_query(
    table_name: str,
    aggregations: Dict[str, str],
    group_by: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    having: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[Any]]:
    """
    Build an aggregation query (SUM, COUNT, AVG, etc.).
    
    Args:
        table_name: Name of the table to aggregate
        aggregations: Dictionary mapping alias to aggregation function
        group_by: List of fields to group by
        filters: Dictionary of field filters
        having: Dictionary of HAVING conditions
        
    Returns:
        Tuple of (SQL query, parameters)
        
    Example:
        >>> query, params = build_aggregation_query(
        ...     'tasks',
        ...     {'total_effort': 'SUM(effort_hours)', 'task_count': 'COUNT(*)'},
        ...     ['work_item_id'],
        ...     {'status': 'completed'}
        ... )
    """
    # Build SELECT clause with aggregations
    select_fields = []
    for alias, func in aggregations.items():
        select_fields.append(f"{func} AS {alias}")
    
    builder = QueryBuilder(table_name).select(select_fields)
    
    # Add filters
    if filters:
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    builder.where_in(field, value)
                else:
                    builder.where(field, FilterOperator.EQUALS, value)
    
    # Add GROUP BY
    if group_by:
        builder.group_by(group_by)
    
    # Add HAVING conditions
    if having:
        for field, value in having.items():
            if value is not None:
                if isinstance(value, list):
                    builder.having(field, FilterOperator.IN, value)
                else:
                    builder.having(field, FilterOperator.EQUALS, value)
    
    return builder.build()


def build_join_query(
    base_table: str,
    joins: List[Tuple[str, str, str]],  # (table, join_type, condition)
    select_fields: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> Tuple[str, List[Any]]:
    """
    Build a query with multiple JOINs.
    
    Args:
        base_table: Base table name
        joins: List of join specifications
        select_fields: Fields to select
        filters: Dictionary of field filters
        order_by: ORDER BY clause
        limit: Maximum number of results
        
    Returns:
        Tuple of (SQL query, parameters)
        
    Example:
        >>> query, params = build_join_query(
        ...     'tasks',
        ...     [('work_items', 'INNER', 'tasks.work_item_id = work_items.id')],
        ...     ['tasks.*', 'work_items.name as work_item_name'],
        ...     {'work_items.status': 'active'}
        ... )
    """
    builder = QueryBuilder(base_table)
    
    # Set select fields
    if select_fields:
        builder.select(select_fields)
    
    # Add joins
    for table, join_type, condition in joins:
        builder.join(table, condition, join_type)
    
    # Add filters
    if filters:
        for field, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    builder.where_in(field, value)
                else:
                    builder.where(field, FilterOperator.EQUALS, value)
    
    # Add ordering
    if order_by:
        parts = order_by.split()
        field = parts[0]
        direction = parts[1] if len(parts) > 1 else SortDirection.ASC
        builder.order_by(field, direction)
    
    # Add limit
    if limit:
        builder.limit(limit)
    
    return builder.build()
