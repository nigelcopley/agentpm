"""
Contexts CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Context entities with:
- Polymorphic entity handling (project/work_item/task contexts)
- Resource file management
- Confidence scoring and band calculation

Pattern: Type-safe method signatures with Context model
"""

from typing import Optional, List
import sqlite3

from ..models import Context, UnifiedSixW
from ..adapters import ContextAdapter
from ..enums import ContextType, ResourceType, EntityType, ConfidenceBand


def create_context(service, context: Context) -> Context:
    """
    Create a new context (resource file or entity context).

    Validates:
    - project_id exists
    - entity_id exists (if entity context)
    - Proper fields for context_type

    Args:
        service: DatabaseService instance
        context: Context model to create

    Returns:
        Created Context with database ID
    """
    # Validate project exists
    project_exists = _check_project_exists(service, context.project_id)
    if not project_exists:
        from ..service import ValidationError
        raise ValidationError(f"Project {context.project_id} does not exist")

    # Validate entity exists (for entity contexts)
    if context.is_entity_context() and context.entity_type and context.entity_id:
        entity_exists = _check_entity_exists(service, context.entity_type, context.entity_id)
        if not entity_exists:
            from ..service import ValidationError
            raise ValidationError(
                f"Entity {context.entity_type.value} {context.entity_id} does not exist"
            )

    # Calculate confidence band if score provided
    if context.confidence_score is not None and context.confidence_band is None:
        context.confidence_band = context.calculate_confidence_band()

    # Convert model to database format
    db_data = ContextAdapter.to_db(context)

    # Build insert query based on context type
    if context.is_resource_file():
        query = """
            INSERT INTO contexts (project_id, context_type, file_path, file_hash, resource_type)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            db_data['project_id'],
            db_data['context_type'],
            db_data.get('file_path'),
            db_data.get('file_hash'),
            db_data.get('resource_type'),
        )
    else:  # Entity context
        query = """
            INSERT INTO contexts (project_id, context_type, entity_type, entity_id,
                                 six_w_data, confidence_score, confidence_band, confidence_factors, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            db_data['project_id'],
            db_data['context_type'],
            db_data.get('entity_type'),
            db_data.get('entity_id'),
            db_data.get('six_w_data'),
            db_data.get('confidence_score'),
            db_data.get('confidence_band'),
            db_data.get('confidence_factors'),
            db_data.get('context_data'),
        )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        context_id = cursor.lastrowid

    return get_context(service, context_id)


def get_context(service, context_id: int) -> Optional[Context]:
    """Get context by ID"""
    query = "SELECT * FROM contexts WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (context_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return ContextAdapter.from_db(dict(row))


def get_entity_context(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_type: Optional[ContextType] = None
) -> Optional[Context]:
    """
    Get context for a specific entity.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity (project, work_item, task)
        entity_id: Entity ID
        context_type: Optional context type filter

    Returns:
        Context model or None if not found

    Example:
        context = get_entity_context(service, EntityType.TASK, 123)
        if context and context.six_w:
            print(f"Implementers: {context.six_w.implementers}")
    """
    if context_type:
        query = "SELECT * FROM contexts WHERE entity_type = ? AND entity_id = ? AND context_type = ?"
        params = (entity_type.value, entity_id, context_type.value)
    else:
        query = "SELECT * FROM contexts WHERE entity_type = ? AND entity_id = ?"
        params = (entity_type.value, entity_id)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        row = cursor.fetchone()

    if not row:
        return None

    return ContextAdapter.from_db(dict(row))


def get_context_by_entity_and_type(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType
) -> Optional[Context]:
    """
    Get context by entity and context type.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity (PROJECT, WORK_ITEM, TASK, IDEA)
        entity_id: ID of the entity
        context_type: Type of context to retrieve

    Returns:
        Context model or None if not found
    """
    query = """
        SELECT * FROM contexts
        WHERE entity_type = ? AND entity_id = ? AND context_type = ?
    """
    params = (entity_type.value, entity_id, context_type.value)

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        row = cursor.fetchone()

    if not row:
        return None

    return ContextAdapter.from_db(dict(row))


def update_context(service, context_id: int, **updates) -> Optional[Context]:
    """
    Update context.

    Automatically recalculates confidence_band if confidence_score changes.

    Args:
        service: DatabaseService instance
        context_id: Context ID
        **updates: Fields to update

    Returns:
        Updated Context or None if not found
    """
    existing = get_context(service, context_id)
    if not existing:
        return None

    # Recalculate confidence band if score updated
    if 'confidence_score' in updates:
        score = updates['confidence_score']
        if score is not None:
            updates['confidence_band'] = ConfidenceBand.from_score(score)

    updated_context = existing.model_copy(update=updates)
    db_data = ContextAdapter.to_db(updated_context)

    # Build update query (varies by context type)
    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE contexts SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), context_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_context(service, context_id)


def delete_context(service, context_id: int) -> bool:
    """Delete context by ID"""
    query = "DELETE FROM contexts WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (context_id,))
        return cursor.rowcount > 0


def list_contexts(
    service,
    project_id: Optional[int] = None,
    context_type: Optional[ContextType] = None,
    confidence_band: Optional[ConfidenceBand] = None
) -> List[Context]:
    """
    List contexts with optional filters.

    Args:
        service: DatabaseService instance
        project_id: Optional project filter
        context_type: Optional context type filter
        confidence_band: Optional confidence band filter

    Returns:
        List of Context models
    """
    query = "SELECT * FROM contexts WHERE 1=1"
    params = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    if context_type:
        query += " AND context_type = ?"
        params.append(context_type.value)

    if confidence_band:
        query += " AND confidence_band = ?"
        params.append(confidence_band.value)

    query += " ORDER BY created_at DESC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [ContextAdapter.from_db(dict(row)) for row in rows]


def list_resource_files(
    service,
    project_id: int,
    resource_type: Optional[ResourceType] = None
) -> List[Context]:
    """
    List resource file contexts for a project.

    Args:
        service: DatabaseService instance
        project_id: Project ID
        resource_type: Optional resource type filter (sop, code, etc.)

    Returns:
        List of resource file Context models
    """
    query = "SELECT * FROM contexts WHERE project_id = ? AND context_type = ?"
    params = [project_id, ContextType.RESOURCE_FILE.value]

    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type.value)

    query += " ORDER BY file_path ASC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [ContextAdapter.from_db(dict(row)) for row in rows]


def get_low_confidence_contexts(service, project_id: int) -> List[Context]:
    """
    Get all entity contexts with RED confidence band.

    These contexts need improvement before agents can operate effectively.

    Args:
        service: DatabaseService instance
        project_id: Project ID

    Returns:
        List of RED-band Context models
    """
    return list_contexts(
        service,
        project_id=project_id,
        confidence_band=ConfidenceBand.RED
    )


# ─────────────────────────────────────────────────────────────────
# NEW: Rich Context Methods
# ─────────────────────────────────────────────────────────────────

def create_rich_context(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType,
    context_data: dict,
    confidence_score: Optional[float] = None
) -> Context:
    """
    Create rich context for an entity.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity (IDEA, WORK_ITEM, TASK, PROJECT)
        entity_id: ID of the entity
        context_type: Type of rich context to create
        context_data: Rich context data dictionary
        confidence_score: Optional confidence score (auto-calculated if None)

    Returns:
        Created Context with rich context data
    """
    # Get project_id from entity
    project_id = _get_project_id_from_entity(service, entity_type, entity_id)
    if not project_id:
        from ..service import ValidationError
        raise ValidationError(f"Could not determine project_id for {entity_type.value} {entity_id}")

    # Calculate confidence score if not provided
    if confidence_score is None:
        confidence_score = _calculate_rich_context_confidence(context_data, context_type)

    # Create context model
    context = Context(
        project_id=project_id,
        context_type=context_type,
        entity_type=entity_type,
        entity_id=entity_id,
        context_data=context_data,
        confidence_score=confidence_score,
        confidence_band=ConfidenceBand.from_score(confidence_score)
    )

    return create_context(service, context)


def update_rich_context(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType,
    context_data: dict,
    confidence_score: Optional[float] = None
) -> Optional[Context]:
    """
    Update rich context for an entity.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: ID of the entity
        context_type: Type of rich context to update
        context_data: Updated rich context data
        confidence_score: Optional confidence score (auto-calculated if None)

    Returns:
        Updated Context or None if not found
    """
    # Find existing context
    existing = get_context_by_entity_and_type(service, entity_type, entity_id, context_type)
    if not existing:
        return None

    # Calculate confidence score if not provided
    if confidence_score is None:
        confidence_score = _calculate_rich_context_confidence(context_data, context_type)

    # Update context
    return update_context(
        service,
        existing.id,
        context_data=context_data,
        confidence_score=confidence_score,
        confidence_band=ConfidenceBand.from_score(confidence_score)
    )


def get_rich_contexts_by_entity(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_types: Optional[List[ContextType]] = None
) -> List[Context]:
    """
    Get all rich contexts for an entity.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: ID of the entity
        context_types: Optional list of context types to filter by

    Returns:
        List of Context models with rich context data
    """
    # Build query
    if context_types:
        placeholders = ', '.join('?' * len(context_types))
        query = f"""
            SELECT * FROM contexts
            WHERE entity_type = ? AND entity_id = ? 
            AND context_type IN ({placeholders})
            AND context_data IS NOT NULL
        """
        params = (entity_type.value, entity_id) + tuple(ct.value for ct in context_types)
    else:
        query = """
            SELECT * FROM contexts
            WHERE entity_type = ? AND entity_id = ? 
            AND context_data IS NOT NULL
        """
        params = (entity_type.value, entity_id)

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

    return [ContextAdapter.from_db(dict(row)) for row in rows]


def validate_rich_context_completeness(
    service,
    entity_type: EntityType,
    entity_id: int,
    required_context_types: List[ContextType]
) -> dict:
    """
    Validate completeness of rich context for an entity.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: ID of the entity
        required_context_types: List of required context types

    Returns:
        Dictionary with validation results
    """
    # Get existing rich contexts
    existing_contexts = get_rich_contexts_by_entity(service, entity_type, entity_id, required_context_types)
    existing_types = {ctx.context_type for ctx in existing_contexts}

    # Check completeness
    missing_types = set(required_context_types) - existing_types
    present_types = set(required_context_types) & existing_types

    # Calculate completeness score
    completeness_score = len(present_types) / len(required_context_types) if required_context_types else 1.0

    return {
        'complete': len(missing_types) == 0,
        'completeness_score': completeness_score,
        'missing_context_types': [ct.value for ct in missing_types],
        'present_context_types': [ct.value for ct in present_types],
        'total_required': len(required_context_types),
        'total_present': len(present_types)
    }


def merge_rich_contexts_hierarchically(
    service,
    task_id: int,
    include_idea_context: bool = False
) -> dict:
    """
    Merge rich contexts hierarchically from Idea → Work Item → Task.

    Args:
        service: DatabaseService instance
        task_id: Task ID to merge contexts for
        include_idea_context: Whether to include idea context

    Returns:
        Dictionary with merged rich context data
    """
    from ..methods import tasks as task_methods
    from ..methods import work_items as wi_methods
    from ..methods import projects as project_methods

    # Load entities
    task = task_methods.get_task(service, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    work_item = wi_methods.get_work_item(service, task.work_item_id)
    if not work_item:
        raise ValueError(f"Work item {task.work_item_id} not found")

    project = project_methods.get_project(service, work_item.project_id)
    if not project:
        raise ValueError(f"Project {work_item.project_id} not found")

    # Merge contexts with task precedence
    merged_context = {}

    # Project context (lowest precedence)
    project_contexts = get_rich_contexts_by_entity(service, EntityType.PROJECT, project.id)
    for ctx in project_contexts:
        if ctx.context_data:
            merged_context[ctx.context_type.value] = ctx.context_data

    # Work item context (medium precedence)
    wi_contexts = get_rich_contexts_by_entity(service, EntityType.WORK_ITEM, work_item.id)
    for ctx in wi_contexts:
        if ctx.context_data:
            merged_context[ctx.context_type.value] = ctx.context_data

    # Task context (highest precedence)
    task_contexts = get_rich_contexts_by_entity(service, EntityType.TASK, task.id)
    for ctx in task_contexts:
        if ctx.context_data:
            merged_context[ctx.context_type.value] = ctx.context_data

    # Idea context (if requested and available)
    if include_idea_context:
        idea_context = _get_idea_context_for_work_item(service, work_item.id)
        if idea_context:
            merged_context.update(idea_context)

    return merged_context


def generate_documents_from_rich_context(
    service,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType,
    document_type: 'DocumentType',
    template_path: Optional[str] = None
) -> dict:
    """
    Generate document from rich context data.

    Args:
        service: DatabaseService instance
        entity_type: Type of entity
        entity_id: ID of the entity
        context_type: Type of rich context to use
        document_type: Type of document to generate
        template_path: Optional template path

    Returns:
        Dictionary with document generation results
    """
    from ..enums import DocumentType

    # Get rich context
    context = get_context_by_entity_and_type(service, entity_type, entity_id, context_type)
    if not context or not context.context_data:
        return {
            'success': False,
            'error': f'No rich context found for {entity_type.value} {entity_id}, type {context_type.value}'
        }

    # Generate document content (placeholder implementation)
    document_content = _render_document_from_context(
        context.context_data,
        document_type,
        template_path
    )

    return {
        'success': True,
        'document_type': document_type.value,
        'content': document_content,
        'context_type': context_type.value,
        'entity_type': entity_type.value,
        'entity_id': entity_id
    }


# Helper functions

def _check_project_exists(service, project_id: int) -> bool:
    """Check if project exists"""
    query = "SELECT 1 FROM projects WHERE id = ?"
    with service.connect() as conn:
        cursor = conn.execute(query, (project_id,))
        return cursor.fetchone() is not None


def _check_entity_exists(service, entity_type: EntityType, entity_id: int) -> bool:
    """Check if entity exists (polymorphic check)"""
    table_map = {
        EntityType.PROJECT: 'projects',
        EntityType.WORK_ITEM: 'work_items',
        EntityType.TASK: 'tasks',
        EntityType.IDEA: 'ideas',
    }

    table_name = table_map.get(entity_type)
    if not table_name:
        return False

    query = f"SELECT 1 FROM {table_name} WHERE id = ?"

    with service.connect() as conn:
        cursor = conn.execute(query, (entity_id,))
        return cursor.fetchone() is not None


def _get_project_id_from_entity(service, entity_type: EntityType, entity_id: int) -> Optional[int]:
    """Get project_id from any entity type"""
    if entity_type == EntityType.PROJECT:
        return entity_id
    elif entity_type == EntityType.WORK_ITEM:
        query = "SELECT project_id FROM work_items WHERE id = ?"
    elif entity_type == EntityType.TASK:
        query = """
            SELECT w.project_id FROM tasks t
            JOIN work_items w ON t.work_item_id = w.id
            WHERE t.id = ?
        """
    elif entity_type == EntityType.IDEA:
        query = "SELECT project_id FROM ideas WHERE id = ?"
    else:
        return None

    with service.connect() as conn:
        cursor = conn.execute(query, (entity_id,))
        row = cursor.fetchone()
        return row[0] if row else None


def _calculate_rich_context_confidence(context_data: dict, context_type: ContextType) -> float:
    """Calculate confidence score for rich context data"""
    if not context_data:
        return 0.0

    # Base confidence on data completeness
    base_score = 0.5

    # Add points for data richness
    if len(context_data) > 3:
        base_score += 0.2
    if len(context_data) > 6:
        base_score += 0.2

    # Add points for specific context types
    if context_type.value in ['business_pillars_context', 'market_research_context']:
        if 'analysis' in context_data or 'insights' in context_data:
            base_score += 0.1

    return min(base_score, 1.0)


def _get_idea_context_for_work_item(service, work_item_id: int) -> Optional[dict]:
    """Get idea context for a work item if it was converted from an idea"""
    # Look for idea-to-work-item mapping context
    mapping_context = get_context_by_entity_and_type(
        service, EntityType.WORK_ITEM, work_item_id, ContextType.IDEA_TO_WORK_ITEM_MAPPING
    )

    if mapping_context and mapping_context.context_data:
        idea_id = mapping_context.context_data.get('original_idea_id')
        if idea_id:
            # Get idea contexts
            idea_contexts = get_rich_contexts_by_entity(service, EntityType.IDEA, idea_id)
            idea_context = {}
            for ctx in idea_contexts:
                if ctx.context_data:
                    idea_context[ctx.context_type.value] = ctx.context_data
            return idea_context

    return None


def _render_document_from_context(context_data: dict, document_type: 'DocumentType', template_path: Optional[str]) -> str:
    """Render document content from rich context data"""
    # Placeholder implementation - would use actual templating in production
    content = f"# {document_type.value.replace('_', ' ').title()}\n\n"
    
    for key, value in context_data.items():
        content += f"## {key.replace('_', ' ').title()}\n\n"
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                content += f"**{sub_key.replace('_', ' ').title()}**: {sub_value}\n\n"
        else:
            content += f"{value}\n\n"
    
    return content