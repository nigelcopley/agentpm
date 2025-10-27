"""
Migration 0048: Context Consolidation

Consolidates context storage from multiple locations into unified Context model:
- Moves WorkItem.business_context data to Context.context_data
- Migrates existing Context.six_w data to Context.context_data["six_w"]
- Establishes Context model as single source of truth

This migration ensures data preservation while enabling unified context management.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.context import UnifiedSixW


def upgrade(conn) -> None:
    """
    Consolidate context storage into unified Context model.
    
    Migration steps:
    1. Create work item contexts for all work items with business_context
    2. Move business_context data to Context.context_data["business_context"]
    3. Migrate existing six_w data to Context.context_data["six_w"]
    4. Update confidence scoring for consolidated contexts
    """
    print("🔄 Starting context consolidation migration...")
    
    # Use database connection directly
    # Step 1: Migrate WorkItem.business_context to Context records
    _migrate_business_context(conn)
    
    # Step 2: Migrate existing six_w data to context_data
    _migrate_six_w_data(conn)
    
    # Step 3: Update confidence scores for consolidated contexts
    _update_confidence_scores(conn)
    
    print("✅ Context consolidation migration completed")


def _migrate_business_context(conn) -> None:
    """Migrate WorkItem.business_context to Context.context_data."""
    print("  📋 Migrating WorkItem.business_context to Context records...")
    
    # Get all work items with business_context
    work_items_query = """
    SELECT id, project_id, business_context, created_at, updated_at
    FROM work_items 
    WHERE business_context IS NOT NULL AND business_context != ''
    """
    
    cursor = conn.cursor()
    cursor.execute(work_items_query)
    work_items = cursor.fetchall()
    migrated_count = 0
    
    for wi in work_items:
        work_item_id = wi[0]  # id
        project_id = wi[1]    # project_id
        business_context = wi[2]  # business_context
        
        # Check if context already exists
        existing_context_query = """
        SELECT id FROM contexts 
        WHERE entity_type = 'work_item' 
        AND entity_id = ? 
        AND context_type = 'work_item_context'
        """
        
        cursor.execute(existing_context_query, (work_item_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing context
            context_id = existing[0]
            _update_context_with_business_context(conn, context_id, business_context)
        else:
            # Create new context record
            _create_business_context_record(conn, project_id, work_item_id, business_context)
        
        migrated_count += 1
    
    print(f"    ✅ Migrated {migrated_count} work item business contexts")


def _migrate_six_w_data(conn) -> None:
    """Migrate existing six_w data to context_data structure."""
    print("  📋 Migrating six_w data to context_data structure...")
    
    # Get all contexts with six_w data
    contexts_query = """
    SELECT id, six_w_data, context_data, entity_type, entity_id
    FROM contexts 
    WHERE six_w_data IS NOT NULL
    """
    
    cursor = conn.cursor()
    cursor.execute(contexts_query)
    contexts = cursor.fetchall()
    migrated_count = 0
    
    for ctx in contexts:
        context_id = ctx[0]  # id
        six_w_json = ctx[1]  # six_w
        existing_context_data = ctx[2]  # context_data
        
        if six_w_json:
            try:
                # Parse existing six_w data
                six_w_data = json.loads(six_w_json) if isinstance(six_w_json, str) else six_w_json
                
                # Parse existing context_data
                context_data = {}
                if existing_context_data:
                    context_data = json.loads(existing_context_data) if isinstance(existing_context_data, str) else existing_context_data
                
                # Add six_w to context_data
                context_data['six_w'] = six_w_data
                
                # Update context record
                update_query = """
                UPDATE contexts 
                SET context_data = ?, updated_at = ?
                WHERE id = ?
                """
                
                cursor.execute(
                    update_query, 
                    (json.dumps(context_data), datetime.now(), context_id)
                )
                
                migrated_count += 1
                
            except (json.JSONDecodeError, TypeError) as e:
                print(f"    ⚠️  Warning: Could not migrate six_w for context {context_id}: {e}")
    
    print(f"    ✅ Migrated {migrated_count} six_w contexts")


def _update_confidence_scores(conn) -> None:
    """Update confidence scores for consolidated contexts."""
    print("  📋 Updating confidence scores for consolidated contexts...")
    
    # Get all contexts with context_data
    contexts_query = """
    SELECT id, context_data, context_type, entity_type
    FROM contexts 
    WHERE context_data IS NOT NULL
    """
    
    cursor = conn.cursor()
    cursor.execute(contexts_query)
    contexts = cursor.fetchall()
    updated_count = 0
    
    for ctx in contexts:
        context_id = ctx[0]  # id
        context_data_json = ctx[1]  # context_data
        context_type = ctx[2]  # context_type
        
        try:
            context_data = json.loads(context_data_json) if isinstance(context_data_json, str) else context_data_json
            
            # Calculate new confidence score based on consolidated data
            confidence_score = _calculate_consolidated_confidence(context_data, context_type)
            confidence_band = _score_to_band(confidence_score)
            
            # Update confidence scores
            update_query = """
            UPDATE contexts 
            SET confidence_score = ?, confidence_band = ?, updated_at = ?
            WHERE id = ?
            """
            
            cursor.execute(
                update_query,
                (confidence_score, confidence_band, datetime.now(), context_id)
            )
            
            updated_count += 1
            
        except (json.JSONDecodeError, TypeError) as e:
            print(f"    ⚠️  Warning: Could not update confidence for context {context_id}: {e}")
    
    print(f"    ✅ Updated confidence scores for {updated_count} contexts")


def _update_context_with_business_context(conn, context_id: int, business_context: str) -> None:
    """Update existing context with business_context data."""
    # Get existing context_data
    get_query = "SELECT context_data FROM contexts WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(get_query, (context_id,))
    result = cursor.fetchone()
    
    if result:
        existing_data = result[0]  # context_data
        context_data = {}
        
        if existing_data:
            try:
                context_data = json.loads(existing_data) if isinstance(existing_data, str) else existing_data
            except (json.JSONDecodeError, TypeError):
                context_data = {}
        
        # Add business_context
        context_data['business_context'] = business_context
        
        # Update context
        update_query = """
        UPDATE contexts 
        SET context_data = ?, updated_at = ?
        WHERE id = ?
        """
        
        cursor.execute(
            update_query,
            (json.dumps(context_data), datetime.now(), context_id)
        )


def _create_business_context_record(conn, project_id: int, work_item_id: int, business_context: str) -> None:
    """Create new context record for work item business context."""
    context_data = {
        'business_context': business_context
    }
    
    confidence_score = _calculate_consolidated_confidence(context_data, 'work_item_context')
    confidence_band = _score_to_band(confidence_score)
    
    insert_query = """
    INSERT INTO contexts (
        project_id, context_type, entity_type, entity_id, 
        context_data, confidence_score, confidence_band,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    now = datetime.now()
    cursor = conn.cursor()
    cursor.execute(
        insert_query,
        (
            project_id, 'work_item_context', 'work_item', work_item_id,
            json.dumps(context_data), confidence_score, confidence_band,
            now, now
        )
    )


def _calculate_consolidated_confidence(context_data: Dict[str, Any], context_type: str) -> float:
    """Calculate confidence score for consolidated context data."""
    if not context_data:
        return 0.3
    
    score = 0.5  # Base score
    
    # Business context presence
    if 'business_context' in context_data and context_data['business_context']:
        score += 0.2
    
    # Six W data presence
    if 'six_w' in context_data and context_data['six_w']:
        six_w = context_data['six_w']
        six_w_fields = ['who', 'what', 'where', 'when', 'why', 'how']
        filled_fields = sum(1 for field in six_w_fields if field in six_w and six_w[field])
        score += (filled_fields / len(six_w_fields)) * 0.2
    
    # Rich context presence
    rich_context_fields = ['business_pillars', 'market_research', 'competitive_analysis']
    rich_context_count = sum(1 for field in rich_context_fields if field in context_data)
    score += (rich_context_count / len(rich_context_fields)) * 0.1
    
    return min(1.0, score)


def _score_to_band(score: float) -> str:
    """Convert confidence score to band."""
    if score < 0.5:
        return 'RED'
    elif score < 0.8:
        return 'YELLOW'
    else:
        return 'GREEN'


# Migration metadata
VERSION = "0048"
DESCRIPTION = "Context consolidation - unify context storage into Context model"
