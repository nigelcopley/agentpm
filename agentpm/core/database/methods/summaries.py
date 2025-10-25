"""
Summary CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Summary entities with:
- Entity existence validation
- Polymorphic summary support
- Recent summaries query for context assembly
- Type filtering and search capabilities

Pattern: Type-safe method signatures with Summary model
"""

from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime

from ..models.summary import Summary
from ..adapters.summary_adapter import SummaryAdapter
from ..enums import EntityType, SummaryType


def create_summary(service, summary: Summary) -> Summary:
    """
    Create a new summary with validation.
    
    Validates:
    - Entity exists (project, session, work_item, or task)
    - Summary type is appropriate for entity type
    - Required fields are present
    
    Args:
        service: DatabaseService instance
        summary: Summary model to create
        
    Returns:
        Created Summary with database ID
        
    Raises:
        ValidationError: If entity doesn't exist or validation fails
    """
    # Validate entity exists
    entity_exists = _check_entity_exists(service, summary.entity_type, summary.entity_id)
    if not entity_exists:
        from ..service import ValidationError
        raise ValidationError(f"{summary.entity_type.value} {summary.entity_id} does not exist")
    
    # Convert model to database format
    db_data = SummaryAdapter.to_db(summary)
    
    # Execute insert
    query = """
        INSERT INTO summaries (
            entity_type, entity_id, summary_type, summary_text,
            context_metadata, created_by, session_id, session_date,
            session_duration_hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['entity_type'],
        db_data['entity_id'],
        db_data['summary_type'],
        db_data['summary_text'],
        db_data['context_metadata'],
        db_data['created_by'],
        db_data['session_id'],
        db_data['session_date'],
        db_data['session_duration_hours'],
    )
    
    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        summary_id = cursor.lastrowid
    
    return get_summary(service, summary_id)


def get_summary(service, summary_id: int) -> Optional[Summary]:
    """
    Get summary by ID.
    
    Args:
        service: DatabaseService instance
        summary_id: Summary ID
        
    Returns:
        Summary model or None if not found
    """
    query = "SELECT * FROM summaries WHERE id = ?"
    
    with service.transaction() as conn:
        cursor = conn.execute(query, (summary_id,))
        row = cursor.fetchone()
    
    if not row:
        return None
    
    # Convert row to dict
    row_dict = dict(zip([col[0] for col in cursor.description], row))
    return SummaryAdapter.from_row(row_dict)


def get_summaries_for_entity(
    service, 
    entity_type: EntityType, 
    entity_id: int,
    limit: Optional[int] = None,
    summary_type: Optional[SummaryType] = None
) -> List[Summary]:
    """
    Get summaries for a specific entity.
    
    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: Entity ID
        limit: Optional limit on number of results
        summary_type: Optional filter by summary type
        
    Returns:
        List of Summary models, ordered by created_at DESC
    """
    query = """
        SELECT * FROM summaries 
        WHERE entity_type = ? AND entity_id = ?
    """
    params = [entity_type.value, entity_id]
    
    if summary_type:
        query += " AND summary_type = ?"
        params.append(summary_type.value)
    
    query += " ORDER BY created_at DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Convert rows to models
    summaries = []
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        summaries.append(SummaryAdapter.from_row(row_dict))
    
    return summaries


def get_recent_summaries(
    service, 
    limit: int = 10,
    entity_type: Optional[EntityType] = None,
    summary_type: Optional[SummaryType] = None
) -> List[Summary]:
    """
    Get recent summaries across all entities.
    
    Args:
        service: DatabaseService instance
        limit: Maximum number of summaries to return
        entity_type: Optional filter by entity type
        summary_type: Optional filter by summary type
        
    Returns:
        List of Summary models, ordered by created_at DESC
    """
    query = "SELECT * FROM summaries WHERE 1=1"
    params = []
    
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)
    
    if summary_type:
        query += " AND summary_type = ?"
        params.append(summary_type.value)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Convert rows to models
    summaries = []
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        summaries.append(SummaryAdapter.from_row(row_dict))
    
    return summaries


def get_summaries_by_session(service, session_id: int) -> List[Summary]:
    """
    Get all summaries for a specific session.
    
    Args:
        service: DatabaseService instance
        session_id: Session ID
        
    Returns:
        List of Summary models for the session
    """
    query = """
        SELECT * FROM summaries 
        WHERE session_id = ? 
        ORDER BY created_at ASC
    """
    
    with service.transaction() as conn:
        cursor = conn.execute(query, (session_id,))
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Convert rows to models
    summaries = []
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        summaries.append(SummaryAdapter.from_row(row_dict))
    
    return summaries


def search_summaries(
    service,
    search_text: str,
    entity_type: Optional[EntityType] = None,
    summary_type: Optional[SummaryType] = None,
    limit: int = 20
) -> List[Summary]:
    """
    Search summaries by text content.
    
    Args:
        service: DatabaseService instance
        search_text: Text to search for in summary_text
        entity_type: Optional filter by entity type
        summary_type: Optional filter by summary type
        limit: Maximum number of results
        
    Returns:
        List of Summary models matching search criteria
    """
    query = """
        SELECT * FROM summaries 
        WHERE summary_text LIKE ?
    """
    params = [f"%{search_text}%"]
    
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)
    
    if summary_type:
        query += " AND summary_type = ?"
        params.append(summary_type.value)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Convert rows to models
    summaries = []
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        summaries.append(SummaryAdapter.from_row(row_dict))
    
    return summaries


def update_summary(service, summary: Summary) -> Summary:
    """
    Update an existing summary.
    
    Args:
        service: DatabaseService instance
        summary: Summary model with updated data
        
    Returns:
        Updated Summary model
        
    Raises:
        ValidationError: If summary doesn't exist
    """
    if not summary.id:
        from ..service import ValidationError
        raise ValidationError("Summary ID is required for update")
    
    # Check if summary exists
    existing = get_summary(service, summary.id)
    if not existing:
        from ..service import ValidationError
        raise ValidationError(f"Summary {summary.id} does not exist")
    
    # Convert model to database format
    db_data = SummaryAdapter.to_db(summary)
    
    # Execute update
    query = """
        UPDATE summaries SET
            entity_type = ?, entity_id = ?, summary_type = ?,
            summary_text = ?, context_metadata = ?, created_by = ?,
            session_id = ?, session_date = ?, session_duration_hours = ?
        WHERE id = ?
    """
    params = (
        db_data['entity_type'],
        db_data['entity_id'],
        db_data['summary_type'],
        db_data['summary_text'],
        db_data['context_metadata'],
        db_data['created_by'],
        db_data['session_id'],
        db_data['session_date'],
        db_data['session_duration_hours'],
        summary.id
    )
    
    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        if cursor.rowcount == 0:
            from ..service import ValidationError
            raise ValidationError(f"Summary {summary.id} not found for update")
    
    return get_summary(service, summary.id)


def delete_summary(service, summary_id: int) -> bool:
    """
    Delete a summary.
    
    Args:
        service: DatabaseService instance
        summary_id: Summary ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM summaries WHERE id = ?"
    
    with service.transaction() as conn:
        cursor = conn.execute(query, (summary_id,))
        return cursor.rowcount > 0


def get_summary_statistics(service) -> Dict[str, Any]:
    """
    Get summary statistics for dashboard/analytics.
    
    Args:
        service: DatabaseService instance
        
    Returns:
        Dictionary with summary statistics
    """
    stats = {}
    
    with service.transaction() as conn:
        # Total summaries
        cursor = conn.execute("SELECT COUNT(*) FROM summaries")
        stats['total_summaries'] = cursor.fetchone()[0]
        
        # Summaries by entity type
        cursor = conn.execute("""
            SELECT entity_type, COUNT(*) 
            FROM summaries 
            GROUP BY entity_type
        """)
        stats['by_entity_type'] = dict(cursor.fetchall())
        
        # Summaries by summary type
        cursor = conn.execute("""
            SELECT summary_type, COUNT(*) 
            FROM summaries 
            GROUP BY summary_type
        """)
        stats['by_summary_type'] = dict(cursor.fetchall())
        
        # Recent activity (last 30 days)
        cursor = conn.execute("""
            SELECT COUNT(*) FROM summaries 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        stats['recent_30_days'] = cursor.fetchone()[0]
        
        # Most active entities
        cursor = conn.execute("""
            SELECT entity_type, entity_id, COUNT(*) as summary_count
            FROM summaries 
            GROUP BY entity_type, entity_id
            ORDER BY summary_count DESC
            LIMIT 10
        """)
        stats['most_active_entities'] = [
            {'entity_type': row[0], 'entity_id': row[1], 'summary_count': row[2]}
            for row in cursor.fetchall()
        ]
    
    return stats


def _check_entity_exists(service, entity_type: EntityType, entity_id: int) -> bool:
    """
    Check if entity exists in database.
    
    Args:
        service: DatabaseService instance
        entity_type: Type of entity to check
        entity_id: Entity ID to check
        
    Returns:
        True if entity exists, False otherwise
    """
    if entity_type == EntityType.PROJECT:
        table = "projects"
    elif entity_type == EntityType.WORK_ITEM:
        table = "work_items"
    elif entity_type == EntityType.TASK:
        table = "tasks"
    elif entity_type == EntityType.IDEA:
        table = "ideas"
    else:
        # For session entities, check sessions table
        table = "sessions"
    
    query = f"SELECT 1 FROM {table} WHERE id = ?"
    
    with service.transaction() as conn:
        cursor = conn.execute(query, (entity_id,))
        return cursor.fetchone() is not None


def migrate_work_item_summaries(service) -> int:
    """
    Migrate existing work_item_summaries to new summaries table.
    
    Args:
        service: DatabaseService instance
        
    Returns:
        Number of summaries migrated
    """
    # Check if work_item_summaries table exists
    with service.transaction() as conn:
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='work_item_summaries'
        """)
        if not cursor.fetchone():
            return 0  # No table to migrate
    
    # Get all work item summaries
    query = "SELECT * FROM work_item_summaries"
    
    with service.transaction() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
    
    if not rows:
        return 0
    
    migrated_count = 0
    
    for row in rows:
        row_dict = dict(zip([col[0] for col in cursor.description], row))
        
        # Convert to new format
        summary_data = {
            'entity_type': EntityType.WORK_ITEM.value,
            'entity_id': row_dict['work_item_id'],
            'summary_type': row_dict['summary_type'],
            'summary_text': row_dict['summary_text'],
            'context_metadata': row_dict['context_metadata'],
            'created_at': row_dict['created_at'],
            'created_by': row_dict['created_by'],
            'session_id': None,  # Not available in legacy format
            'session_date': row_dict['session_date'],
            'session_duration_hours': row_dict['session_duration_hours'],
        }
        
        # Insert into new table
        insert_query = """
            INSERT INTO summaries (
                entity_type, entity_id, summary_type, summary_text,
                context_metadata, created_at, created_by, session_id,
                session_date, session_duration_hours
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            summary_data['entity_type'],
            summary_data['entity_id'],
            summary_data['summary_type'],
            summary_data['summary_text'],
            summary_data['context_metadata'],
            summary_data['created_at'],
            summary_data['created_by'],
            summary_data['session_id'],
            summary_data['session_date'],
            summary_data['session_duration_hours'],
        )
        
        with service.transaction() as conn:
            conn.execute(insert_query, params)
            migrated_count += 1
    
    return migrated_count
