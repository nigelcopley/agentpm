"""
Ideas CRUD Methods - Type-Safe Database Operations (WI-50)

Implements CRUD operations for Idea entities using:
- Pydantic models for type safety
- Adapters for model ↔ database conversion
- State machine validation for workflow enforcement

Ideas System Pattern:
- Lightweight brainstorming entity before work items
- Simple 6-state lifecycle: idea → research → design → accepted → converted OR rejected
- Democratic voting for prioritization
- Full traceability: idea ↔ work_item bidirectional links

Pattern: Type-safe method signatures with Idea model
"""

from typing import Optional, List
import sqlite3

from ..models import Idea, WorkItem
from ..adapters import IdeaAdapter, WorkItemAdapter
from ..enums import IdeaStatus, WorkItemType


def create_idea(service, idea: Idea) -> Idea:
    """
    Create a new idea.

    Type-safe: accepts Idea model, returns Idea model.

    Args:
        service: DatabaseService instance
        idea: Idea model to create

    Returns:
        Created Idea with database ID

    Raises:
        ValidationError: If idea data is invalid (Pydantic validation)
        TransactionError: If database operation fails

    Example:
        idea = Idea(
            project_id=1,
            title="Add OAuth2 authentication",
            description="Support Google/GitHub sign-in",
            source=IdeaSource.CUSTOMER_FEEDBACK,
            tags=["security", "ux"]
        )
        created = create_idea(service, idea)
    """
    db_data = IdeaAdapter.to_db(idea)

    query = """
        INSERT INTO ideas (
            project_id, title, description, source, created_by,
            votes, tags, status, rejection_reason,
            converted_to_work_item_id, converted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['project_id'],
        db_data['title'],
        db_data['description'],
        db_data['source'],
        db_data['created_by'],
        db_data['votes'],
        db_data['tags'],
        db_data['status'],
        db_data['rejection_reason'],
        db_data['converted_to_work_item_id'],
        db_data['converted_at'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        idea_id = cursor.lastrowid

    return get_idea(service, idea_id)


def get_idea(service, idea_id: int) -> Optional[Idea]:
    """
    Get idea by ID.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID

    Returns:
        Idea model or None if not found
    """
    query = "SELECT * FROM ideas WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (idea_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return IdeaAdapter.from_db(dict(row))


def list_ideas(
    service,
    project_id: Optional[int] = None,
    status: Optional[IdeaStatus] = None,
    tags: Optional[List[str]] = None,
    source: Optional[str] = None,
    sort_by: str = "created_at",
    ascending: bool = False,
    limit: Optional[int] = None
) -> List[Idea]:
    """
    List ideas with filtering.

    Args:
        service: DatabaseService instance
        project_id: Optional project ID to filter by
        status: Optional status filter
        tags: Optional tag filter (ideas matching ANY tag)
        source: Optional source filter
        sort_by: Sort field (default: created_at)
        ascending: Sort direction (default: False)
        limit: Optional result limit

    Returns:
        List of Idea models (ordered by specified sort criteria)

    Example:
        # Top 10 ideas
        top_ideas = list_ideas(service, project_id=1, limit=10)

        # Ideas in research phase
        research_ideas = list_ideas(service, project_id=1, status=IdeaStatus.RESEARCH)

        # Ideas with specific tags
        backend_ideas = list_ideas(service, project_id=1, tags=["backend", "api"])
    """
    # Base query
    query = "SELECT * FROM ideas"
    params = []
    conditions = []

    # Add project filter
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)

    # Add status filter
    if status:
        conditions.append("status = ?")
        params.append(status.value)

    # Add source filter
    if source:
        conditions.append("source = ?")
        params.append(source)

    # Add tag filter (OR condition for multiple tags)
    if tags:
        tag_conditions = " OR ".join(["tags LIKE ?"] * len(tags))
        conditions.append(f"({tag_conditions})")
        params.extend([f'%"{tag}"%' for tag in tags])

    # Apply conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add sorting
    sort_direction = "ASC" if ascending else "DESC"
    if sort_by == "votes":
        query += f" ORDER BY votes {sort_direction}, created_at DESC"
    elif sort_by == "created_at":
        query += f" ORDER BY created_at {sort_direction}"
    elif sort_by == "updated_at":
        query += f" ORDER BY updated_at {sort_direction}"
    else:
        # Default to created_at DESC
        query += " ORDER BY created_at DESC"

    # Add limit
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

    return [IdeaAdapter.from_db(dict(row)) for row in rows]


def update_idea(service, idea: Idea) -> Idea:
    """
    Update idea (full model update).

    Type-safe: Pydantic validates before database update.

    Args:
        service: DatabaseService instance
        idea: Updated Idea model (must have id)

    Returns:
        Updated Idea model

    Raises:
        ValueError: If idea.id is None
        ValidationError: If idea data is invalid

    Example:
        idea = get_idea(service, 5)
        idea.description = "Enhanced description"
        updated = update_idea(service, idea)
    """
    if not idea.id:
        raise ValueError("Idea must have id for update")

    db_data = IdeaAdapter.to_db(idea)

    query = """
        UPDATE ideas SET
            title = ?, description = ?, source = ?, created_by = ?,
            votes = ?, tags = ?, status = ?, rejection_reason = ?,
            converted_to_work_item_id = ?, converted_at = ?
        WHERE id = ?
    """
    params = (
        db_data['title'],
        db_data['description'],
        db_data['source'],
        db_data['created_by'],
        db_data['votes'],
        db_data['tags'],
        db_data['status'],
        db_data['rejection_reason'],
        db_data['converted_to_work_item_id'],
        db_data['converted_at'],
        idea.id,
    )

    with service.transaction() as conn:
        conn.execute(query, params)

    # Return updated idea (triggers will have updated updated_at)
    return get_idea(service, idea.id)


def vote_on_idea(service, idea_id: int, delta: int = 1) -> Idea:
    """
    Vote on idea (+1 upvote or -1 downvote).

    Votes cannot go below 0.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        delta: Vote change (+1 or -1)

    Returns:
        Updated Idea with new vote count

    Raises:
        ValueError: If idea not found or is in terminal state
        ValueError: If delta not in (+1, -1)

    Example:
        # Upvote
        idea = vote_on_idea(service, 5, delta=+1)

        # Downvote
        idea = vote_on_idea(service, 5, delta=-1)
    """
    if delta not in (-1, 1):
        raise ValueError("delta must be +1 or -1")

    # Get idea
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    # Cannot vote on terminal states
    if idea.is_terminal():
        raise ValueError(f"Cannot vote on idea in '{idea.status}' state")

    # Update votes (cannot go negative)
    new_votes = max(0, idea.votes + delta)
    idea.votes = new_votes

    return update_idea(service, idea)


def transition_idea(service, idea_id: int, new_status: IdeaStatus) -> Idea:
    """
    Transition idea to new status (state machine validation).

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        new_status: Target status

    Returns:
        Updated Idea with new status

    Raises:
        ValueError: If idea not found
        ValueError: If transition not allowed (state machine violation)

    Example:
        # Progress idea through workflow
        idea = transition_idea(service, 5, IdeaStatus.RESEARCH)
        idea = transition_idea(service, 5, IdeaStatus.DESIGN)
        idea = transition_idea(service, 5, IdeaStatus.ACTIVE)
    """
    # Get idea
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    # Validate transition
    if not idea.can_transition_to(new_status):
        allowed = idea.get_allowed_transitions()
        raise ValueError(
            f"Invalid transition: {idea.status} → {new_status}. "
            f"Allowed: {[s.value for s in allowed]}"
        )

    # Update status
    idea.status = new_status

    return update_idea(service, idea)


def reject_idea(service, idea_id: int, reason: str) -> Idea:
    """
    Reject idea with reason (terminal state).

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        reason: Rejection reason (required, min 10 characters)

    Returns:
        Updated Idea with status='rejected'

    Raises:
        ValueError: If idea not found, already terminal, or reason too short

    Example:
        idea = reject_idea(service, 5, "Duplicate of existing work item #15")
    """
    if not reason or len(reason) < 10:
        raise ValueError("rejection_reason must be at least 10 characters")

    # Get idea
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    # Cannot reject terminal states
    if idea.is_terminal():
        raise ValueError(f"Idea already in terminal state '{idea.status}'")

    # Update status and reason
    idea.status = IdeaStatus.REJECTED
    idea.rejection_reason = reason

    return update_idea(service, idea)


def convert_idea_to_work_item(
    service,
    idea_id: int,
    work_item_type: WorkItemType = WorkItemType.FEATURE,
    priority: int = 3,
    business_context: Optional[str] = None,
    start_phase: Optional[str] = None
) -> tuple[Idea, WorkItem]:
    """
    Convert accepted idea to work item with full traceability and enhanced metadata.

    Process:
    1. Validate idea is in 'accepted' state
    2. Create work item with idea content and enhanced metadata
    3. Auto-set work item to DRAFT status with appropriate phase
    4. Copy idea metadata to work item (tags, source, created_by)
    5. Link work_item.originated_from_idea_id → idea.id
    6. Transition idea to 'converted' status
    7. Set idea.converted_to_work_item_id → work_item.id
    8. Return both entities

    Args:
        service: DatabaseService instance
        idea_id: ID of accepted idea
        work_item_type: Type of work item (default: FEATURE)
        priority: Priority 1-5 (default: 3)
        business_context: Optional business rationale
        start_phase: Optional phase to start work item in (D1_DISCOVERY, P1_PLAN, I1_IMPLEMENTATION)

    Returns:
        (converted_idea, new_work_item)

    Raises:
        ValueError: If idea not found or not in 'accepted' state

    Example:
        converted_idea, work_item = convert_idea_to_work_item(
            service, idea_id=5,
            work_item_type=WorkItemType.FEATURE,
            priority=1,
            business_context="Critical customer request",
            start_phase="P1_PLAN"  # Skip discovery if already done
        )
    """
    # Import work_items methods (avoid circular import)
    from . import work_items as wi_methods
    from ..enums import Phase, WorkItemStatus
    import json
    from datetime import datetime

    # 1. Get idea
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    if not idea.can_convert():
        raise ValueError(
            f"Idea must be 'accepted' for conversion (currently '{idea.status}')"
        )

    # 2. Determine starting phase based on idea status and start_phase parameter
    if start_phase:
        # Validate start_phase
        try:
            phase = Phase(start_phase)
        except ValueError:
            valid_phases = [p.value for p in Phase]
            raise ValueError(f"Invalid start_phase '{start_phase}'. Valid: {valid_phases}")
    else:
        # Auto-determine phase based on idea status
        phase_mapping = {
            IdeaStatus.IDEA: Phase.D1_DISCOVERY,
            IdeaStatus.RESEARCH: Phase.D1_DISCOVERY,
            IdeaStatus.DESIGN: Phase.P1_PLAN,
            IdeaStatus.ACTIVE: Phase.P1_PLAN,  # Ready for implementation
        }
        phase = phase_mapping.get(idea.status, Phase.D1_DISCOVERY)

    # 3. Create enhanced metadata for work item
    metadata = {
        "originated_from": {
            "idea_id": idea_id,
            "idea_title": idea.title,
            "idea_source": idea.source.value,
            "idea_created_by": idea.created_by,
            "idea_votes": idea.votes,
            "idea_tags": idea.tags,
            "conversion_timestamp": datetime.now().isoformat()
        },
        "tags": idea.tags,  # Copy idea tags to work item metadata
        "conversion_phase_alignment": {
            "idea_status": idea.status.value,
            "work_item_start_phase": phase.value,
            "alignment_note": f"Idea {idea.status.value} → Work Item {phase.value}"
        }
    }

    # 4. Create work item with enhanced context
    work_item = WorkItem(
        project_id=idea.project_id,
        name=idea.title,
        description=idea.description,
        type=work_item_type,
        priority=priority,
        business_context=business_context or idea.description or f"Originated from idea #{idea_id}: {idea.title}",
        metadata=json.dumps(metadata),
        status=WorkItemStatus.DRAFT,  # Always start in DRAFT
        phase=phase,  # Set the determined phase
        originated_from_idea_id=idea_id  # Forward traceability
    )

    created_work_item = wi_methods.create_work_item(service, work_item)

    # 5. Transfer rich context from idea to work item
    _transfer_idea_context_to_work_item(service, idea_id, created_work_item.id)

    # 6. Update idea (transition to converted)
    idea.status = IdeaStatus.CONVERTED
    idea.converted_to_work_item_id = created_work_item.id
    idea.converted_at = datetime.now()  # Set timestamp explicitly

    updated_idea = update_idea(service, idea)

    return (updated_idea, created_work_item)


def delete_idea(service, idea_id: int) -> bool:
    """
    Delete idea by ID.

    Note: Prefer rejection over deletion for audit trail.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM ideas WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (idea_id,))
        return cursor.rowcount > 0


# ─────────────────────────────────────────────────────────────────
# NEW: Ideas Rich Context Integration Methods
# ─────────────────────────────────────────────────────────────────

def create_idea_rich_context(
    service,
    idea_id: int,
    context_type,
    context_data: dict,
    confidence_score: Optional[float] = None
):
    """
    Create rich context for an idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        context_type: Type of rich context to create
        context_data: Rich context data dictionary
        confidence_score: Optional confidence score

    Returns:
        Created Context with rich context data
    """
    from . import contexts as context_methods
    from ..enums import EntityType, ContextType

    # Get idea to determine project_id
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    return context_methods.create_rich_context(
        service=service,
        entity_type=EntityType.IDEA,
        entity_id=idea_id,
        context_type=context_type,
        context_data=context_data,
        confidence_score=confidence_score
    )


def get_idea_rich_contexts(
    service,
    idea_id: int,
    context_types: Optional[List] = None
) -> List:
    """
    Get all rich contexts for an idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        context_types: Optional list of context types to filter by

    Returns:
        List of Context models with rich context data
    """
    from . import contexts as context_methods
    from ..enums import EntityType

    return context_methods.get_rich_contexts_by_entity(
        service=service,
        entity_type=EntityType.IDEA,
        entity_id=idea_id,
        context_types=context_types
    )


def validate_idea_context_completeness(
    service,
    idea_id: int,
    required_context_types: Optional[List] = None
) -> dict:
    """
    Validate completeness of rich context for an idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        required_context_types: List of required context types (defaults to idea-specific types)

    Returns:
        Dictionary with validation results
    """
    from . import contexts as context_methods
    from ..enums import EntityType, ContextType

    # Default required context types for ideas
    if required_context_types is None:
        required_context_types = [
            ContextType.IDEA_CONTEXT,
            ContextType.BUSINESS_PILLARS_CONTEXT,
            ContextType.MARKET_RESEARCH_CONTEXT,
            ContextType.COMPETITIVE_ANALYSIS_CONTEXT
        ]

    return context_methods.validate_rich_context_completeness(
        service=service,
        entity_type=EntityType.IDEA,
        entity_id=idea_id,
        required_context_types=required_context_types
    )


def assemble_idea_context(
    service,
    idea_id: int,
    include_document_context: bool = True
) -> dict:
    """
    Assemble comprehensive context for an idea.

    Args:
        service: DatabaseService instance
        idea_id: Idea ID
        include_document_context: Whether to include document-driven context

    Returns:
        Dictionary with assembled idea context
    """
    from . import contexts as context_methods
    from ..enums import EntityType

    # Get idea basic info
    idea = get_idea(service, idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    # Assemble rich context using the context assembly service
    from ...context.assembly_service import ContextAssemblyService
    from pathlib import Path
    from . import projects
    
    # Get project path from the idea's project
    project = projects.get_project(service, idea.project_id)
    project_path = Path(project.path) if project else Path.cwd()
    
    assembly_service = ContextAssemblyService(service, project_path)
    rich_context = assembly_service.assemble_rich_context(
        entity_type=EntityType.IDEA,
        entity_id=idea_id
    )

    # Assemble document context if requested
    document_context = {}
    if include_document_context:
        document_context = assembly_service.assemble_document_driven_context(
            entity_type=EntityType.IDEA,
            entity_id=idea_id
        )

    return {
        'idea': {
            'id': idea.id,
            'title': idea.title,
            'description': idea.description,
            'status': idea.status.value,
            'votes': idea.votes,
            'tags': idea.tags,
            'created_at': idea.created_at,
            'updated_at': idea.updated_at
        },
        'rich_context': rich_context,
        'document_context': document_context,
        'context_completeness': validate_idea_context_completeness(service, idea_id)
    }


def _transfer_idea_context_to_work_item(service, idea_id: int, work_item_id: int) -> None:
    """
    Transfer rich context from idea to work item during conversion.

    Args:
        service: DatabaseService instance
        idea_id: Source idea ID
        work_item_id: Target work item ID
    """
    from . import contexts as context_methods
    from ..enums import EntityType, ContextType

    # Get all idea contexts
    idea_contexts = get_idea_rich_contexts(service, idea_id)

    # Transfer each context to work item
    for idea_context in idea_contexts:
        if idea_context.context_data:
            # Create corresponding work item context
            context_methods.create_rich_context(
                service=service,
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item_id,
                context_type=idea_context.context_type,
                context_data=idea_context.context_data,
                confidence_score=idea_context.confidence_score
            )

    # Create idea-to-work-item mapping context
    mapping_data = {
        'original_idea_id': idea_id,
        'conversion_timestamp': idea_context.created_at.isoformat() if idea_contexts else None,
        'transferred_context_types': [ctx.context_type.value for ctx in idea_contexts],
        'context_count': len(idea_contexts)
    }

    context_methods.create_rich_context(
        service=service,
        entity_type=EntityType.WORK_ITEM,
        entity_id=work_item_id,
        context_type=ContextType.IDEA_TO_WORK_ITEM_MAPPING,
        context_data=mapping_data,
        confidence_score=1.0  # High confidence for mapping data
    )
