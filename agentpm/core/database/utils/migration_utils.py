"""
Database Migration Utilities

Common migration and schema utilities used across database operations for:
- Schema version management
- Migration tracking
- Column existence checks
- Schema validation
- Migration rollback support

This module provides utilities for managing database schema evolution
in APM (Agent Project Manager)'s migration system.
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from .error_utils import DatabaseError, ValidationError


def get_schema_version(conn: sqlite3.Connection) -> Optional[str]:
    """
    Get current schema version from migrations table.
    
    Args:
        conn: Database connection
        
    Returns:
        Current schema version or None if no migrations
    """
    try:
        cursor = conn.execute("""
            SELECT version FROM schema_migrations
            ORDER BY applied_at DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return None


def record_migration(
    conn: sqlite3.Connection,
    version: str,
    description: str,
    applied_by: Optional[str] = None
) -> None:
    """
    Record a migration as applied.
    
    Args:
        conn: Database connection
        version: Migration version
        description: Migration description
        applied_by: Who applied the migration
    """
    conn.execute("""
        INSERT INTO schema_migrations (version, description, applied_by)
        VALUES (?, ?, ?)
    """, (version, description, applied_by))


def rollback_migration(
    conn: sqlite3.Connection,
    version: str,
    reason: str,
    rolled_back_by: Optional[str] = None
) -> None:
    """
    Record a migration rollback.
    
    Args:
        conn: Database connection
        version: Migration version to rollback
        reason: Reason for rollback
        rolled_back_by: Who rolled back the migration
    """
    conn.execute("""
        UPDATE schema_migrations
        SET rollback_at = CURRENT_TIMESTAMP,
            rollback_reason = ?,
            applied_by = ?
        WHERE version = ?
    """, (reason, rolled_back_by, version))


def get_migration_history(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Get complete migration history.
    
    Args:
        conn: Database connection
        
    Returns:
        List of migration records
    """
    cursor = conn.execute("""
        SELECT version, description, applied_at, rollback_at, 
               rollback_reason, applied_by
        FROM schema_migrations
        ORDER BY applied_at ASC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        conn: Database connection
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None


def check_column_exists(
    conn: sqlite3.Connection, 
    table_name: str, 
    column_name: str
) -> bool:
    """
    Check if a column exists in a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column
        
    Returns:
        True if column exists, False otherwise
    """
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def check_columns_exist(
    conn: sqlite3.Connection,
    table_name: str,
    column_names: List[str]
) -> bool:
    """
    Check if multiple columns exist in a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        column_names: List of column names to check
        
    Returns:
        True if all columns exist, False otherwise
    """
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}
    return all(col in existing_columns for col in column_names)


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        
    Returns:
        List of column information dictionaries
    """
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = []
    
    for row in cursor.fetchall():
        columns.append({
            'cid': row[0],
            'name': row[1],
            'type': row[2],
            'notnull': bool(row[3]),
            'default_value': row[4],
            'pk': bool(row[5])
        })
    
    return columns


def get_table_indexes(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Get index information for a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        
    Returns:
        List of index information dictionaries
    """
    cursor = conn.execute(f"PRAGMA index_list({table_name})")
    indexes = []
    
    for row in cursor.fetchall():
        index_info = {
            'seq': row[0],
            'name': row[1],
            'unique': bool(row[2]),
            'origin': row[3],
            'partial': bool(row[4])
        }
        
        # Get index columns
        index_cursor = conn.execute(f"PRAGMA index_info({index_info['name']})")
        index_info['columns'] = [col_row[2] for col_row in index_cursor.fetchall()]
        
        indexes.append(index_info)
    
    return indexes


def get_table_foreign_keys(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Get foreign key information for a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        
    Returns:
        List of foreign key information dictionaries
    """
    cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = []
    
    for row in cursor.fetchall():
        foreign_keys.append({
            'id': row[0],
            'seq': row[1],
            'table': row[2],
            'from': row[3],
            'to': row[4],
            'on_update': row[5],
            'on_delete': row[6],
            'match': row[7]
        })
    
    return foreign_keys


def validate_table_schema(
    conn: sqlite3.Connection,
    table_name: str,
    expected_columns: List[Dict[str, Any]],
    expected_indexes: Optional[List[str]] = None
) -> List[str]:
    """
    Validate that a table matches expected schema.
    
    Args:
        conn: Database connection
        table_name: Name of the table to validate
        expected_columns: List of expected column definitions
        expected_indexes: List of expected index names
        
    Returns:
        List of validation errors (empty if schema is valid)
    """
    errors = []
    
    # Check if table exists
    if not check_table_exists(conn, table_name):
        errors.append(f"Table '{table_name}' does not exist")
        return errors
    
    # Get actual columns
    actual_columns = get_table_columns(conn, table_name)
    actual_column_names = {col['name'] for col in actual_columns}
    
    # Check expected columns
    for expected_col in expected_columns:
        col_name = expected_col['name']
        if col_name not in actual_column_names:
            errors.append(f"Column '{col_name}' missing from table '{table_name}'")
            continue
        
        # Find actual column
        actual_col = next(col for col in actual_columns if col['name'] == col_name)
        
        # Check column properties
        if 'type' in expected_col and actual_col['type'].upper() != expected_col['type'].upper():
            errors.append(f"Column '{col_name}' has wrong type: expected {expected_col['type']}, got {actual_col['type']}")
        
        if 'notnull' in expected_col and actual_col['notnull'] != expected_col['notnull']:
            errors.append(f"Column '{col_name}' has wrong notnull constraint: expected {expected_col['notnull']}, got {actual_col['notnull']}")
        
        if 'pk' in expected_col and actual_col['pk'] != expected_col['pk']:
            errors.append(f"Column '{col_name}' has wrong primary key constraint: expected {expected_col['pk']}, got {actual_col['pk']}")
    
    # Check expected indexes
    if expected_indexes:
        actual_indexes = get_table_indexes(conn, table_name)
        actual_index_names = {idx['name'] for idx in actual_indexes}
        
        for expected_idx in expected_indexes:
            if expected_idx not in actual_index_names:
                errors.append(f"Index '{expected_idx}' missing from table '{table_name}'")
    
    return errors


def add_column_if_not_exists(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str
) -> bool:
    """
    Add a column to a table if it doesn't exist.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column to add
        column_definition: Column definition (e.g., "TEXT DEFAULT ''")
        
    Returns:
        True if column was added, False if it already existed
    """
    if check_column_exists(conn, table_name, column_name):
        return False
    
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
    return True


def create_index_if_not_exists(
    conn: sqlite3.Connection,
    index_name: str,
    table_name: str,
    columns: List[str],
    unique: bool = False
) -> bool:
    """
    Create an index if it doesn't exist.
    
    Args:
        conn: Database connection
        index_name: Name of the index
        table_name: Name of the table
        columns: List of column names
        unique: Whether the index should be unique
        
    Returns:
        True if index was created, False if it already existed
    """
    # Check if index exists
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name=?
    """, (index_name,))
    
    if cursor.fetchone() is not None:
        return False
    
    # Create index
    unique_clause = "UNIQUE " if unique else ""
    columns_str = ", ".join(columns)
    
    conn.execute(f"""
        CREATE {unique_clause}INDEX {index_name} 
        ON {table_name} ({columns_str})
    """)
    
    return True


def drop_index_if_exists(conn: sqlite3.Connection, index_name: str) -> bool:
    """
    Drop an index if it exists.
    
    Args:
        conn: Database connection
        index_name: Name of the index to drop
        
    Returns:
        True if index was dropped, False if it didn't exist
    """
    # Check if index exists
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name=?
    """, (index_name,))
    
    if cursor.fetchone() is None:
        return False
    
    conn.execute(f"DROP INDEX {index_name}")
    return True


def backup_table_data(
    conn: sqlite3.Connection,
    table_name: str,
    backup_table_name: Optional[str] = None
) -> str:
    """
    Create a backup of table data.
    
    Args:
        conn: Database connection
        table_name: Name of the table to backup
        backup_table_name: Name for the backup table (auto-generated if None)
        
    Returns:
        Name of the backup table
    """
    if backup_table_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_table_name = f"{table_name}_backup_{timestamp}"
    
    # Create backup table with same structure
    conn.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}")
    
    return backup_table_name


def restore_table_data(
    conn: sqlite3.Connection,
    table_name: str,
    backup_table_name: str
) -> None:
    """
    Restore table data from backup.
    
    Args:
        conn: Database connection
        table_name: Name of the table to restore
        backup_table_name: Name of the backup table
    """
    # Clear existing data
    conn.execute(f"DELETE FROM {table_name}")
    
    # Restore from backup
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM {backup_table_name}")


def get_database_info(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Get comprehensive database information.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary containing database information
    """
    info = {
        'schema_version': get_schema_version(conn),
        'tables': [],
        'total_size_bytes': 0
    }
    
    # Get all tables
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    for (table_name,) in cursor.fetchall():
        table_info = {
            'name': table_name,
            'columns': get_table_columns(conn, table_name),
            'indexes': get_table_indexes(conn, table_name),
            'foreign_keys': get_table_foreign_keys(conn, table_name)
        }
        
        # Get row count
        count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        table_info['row_count'] = count_cursor.fetchone()[0]
        
        info['tables'].append(table_info)
    
    # Get database size (approximate)
    cursor = conn.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor = conn.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    info['total_size_bytes'] = page_count * page_size
    
    return info


def validate_database_integrity(conn: sqlite3.Connection) -> List[str]:
    """
    Validate database integrity.
    
    Args:
        conn: Database connection
        
    Returns:
        List of integrity issues (empty if database is valid)
    """
    issues = []
    
    # Check foreign key constraints
    cursor = conn.execute("PRAGMA foreign_key_check")
    fk_issues = cursor.fetchall()
    
    for issue in fk_issues:
        issues.append(f"Foreign key constraint violation: {issue}")
    
    # Check for orphaned records (basic check)
    # This is a simplified check - in practice, you'd want more comprehensive validation
    
    return issues


def optimize_database(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Optimize database performance.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary with optimization results
    """
    results = {
        'analyzed': False,
        'vacuumed': False,
        'indexes_rebuilt': False
    }
    
    try:
        # Analyze database
        conn.execute("ANALYZE")
        results['analyzed'] = True
        
        # Vacuum database
        conn.execute("VACUUM")
        results['vacuumed'] = True
        
        # Rebuild indexes
        conn.execute("REINDEX")
        results['indexes_rebuilt'] = True
        
    except sqlite3.Error as e:
        results['error'] = str(e)
    
    return results
