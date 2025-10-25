"""
Evidence Sources CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for EvidenceSource entities with research traceability and verification.

Pattern: Type-safe method signatures with EvidenceSource model
Methods: create_evidence_source, get_evidence_source, list_evidence_sources, update_evidence_source,
         delete_evidence_source, get_evidence_by_entity
"""

from typing import Optional, List
import sqlite3

from ..models import EvidenceSource
from ..adapters.evidence_source_adapter import EvidenceSourceAdapter
from ..enums import EntityType, SourceType


def create_evidence_source(service, evidence: EvidenceSource) -> EvidenceSource:
    """
    Create a new evidence source.

    Args:
        service: DatabaseService instance
        evidence: EvidenceSource model to create

    Returns:
        Created EvidenceSource with database ID

    Example:
        >>> evidence = EvidenceSource(
        ...     entity_type=EntityType.WORK_ITEM,
        ...     entity_id=43,
        ...     url="https://docs.djangoproject.com/en/4.2/",
        ...     source_type=SourceType.DOCUMENTATION,
        ...     excerpt="Django auth is built-in",
        ...     confidence=0.9
        ... )
        >>> created = create_evidence_source(db, evidence)
    """
    # Convert model to database format
    db_data = EvidenceSourceAdapter.to_db(evidence)

    query = """
        INSERT INTO evidence_sources (entity_type, entity_id, url, source_type,
                                     excerpt, captured_at, content_hash, confidence,
                                     created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['entity_type'],
        db_data['entity_id'],
        db_data['url'],
        db_data['source_type'],
        db_data['excerpt'],
        db_data['captured_at'],
        db_data['content_hash'],
        db_data['confidence'],
        db_data['created_by'],
        db_data['created_at'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        evidence_id = cursor.lastrowid

    return get_evidence_source(service, evidence_id)


def get_evidence_source(service, evidence_id: int) -> Optional[EvidenceSource]:
    """
    Get evidence source by ID.

    Args:
        service: DatabaseService instance
        evidence_id: Evidence source ID

    Returns:
        EvidenceSource if found, None otherwise
    """
    query = "SELECT * FROM evidence_sources WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (evidence_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return EvidenceSourceAdapter.from_db(dict(row))


def list_evidence_sources(
    service,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[int] = None,
    source_type: Optional[SourceType] = None,
    min_confidence: Optional[float] = None,
    limit: Optional[int] = None
) -> List[EvidenceSource]:
    """
    List evidence sources with optional filters.

    Args:
        service: DatabaseService instance
        entity_type: Filter by entity type (project, work_item, task)
        entity_id: Filter by entity ID
        source_type: Filter by source type (documentation, research, etc.)
        min_confidence: Minimum confidence score (0.0-1.0)
        limit: Maximum number of results

    Returns:
        List of EvidenceSource models

    Example:
        >>> # Get all evidence for a work item
        >>> evidence = list_evidence_sources(
        ...     db, entity_type=EntityType.WORK_ITEM, entity_id=43
        ... )
        >>> # Get high-confidence research sources
        >>> research = list_evidence_sources(
        ...     db, source_type=SourceType.RESEARCH, min_confidence=0.8
        ... )
    """
    query = "SELECT * FROM evidence_sources WHERE 1=1"
    params = []

    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type.value)

    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)

    if source_type:
        query += " AND source_type = ?"
        params.append(source_type.value)

    if min_confidence is not None:
        query += " AND confidence >= ?"
        params.append(min_confidence)

    query += " ORDER BY captured_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [EvidenceSourceAdapter.from_db(dict(row)) for row in rows]


def update_evidence_source(service, evidence_id: int, **updates) -> Optional[EvidenceSource]:
    """
    Update evidence source with validation.

    Args:
        service: DatabaseService instance
        evidence_id: Evidence source ID
        **updates: Fields to update

    Returns:
        Updated EvidenceSource if found, None otherwise

    Example:
        >>> # Update confidence score
        >>> updated = update_evidence_source(db, 1, confidence=0.95)
        >>> # Update content hash
        >>> updated = update_evidence_source(db, 1, content_hash="abc123")
    """
    existing = get_evidence_source(service, evidence_id)
    if not existing:
        return None

    updated_evidence = existing.model_copy(update=updates)
    db_data = EvidenceSourceAdapter.to_db(updated_evidence)

    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE evidence_sources SET {set_clause} WHERE id = ?"
    params = (*db_data.values(), evidence_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_evidence_source(service, evidence_id)


def delete_evidence_source(service, evidence_id: int) -> bool:
    """
    Delete evidence source by ID.

    Args:
        service: DatabaseService instance
        evidence_id: Evidence source ID

    Returns:
        True if deleted, False if not found
    """
    query = "DELETE FROM evidence_sources WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (evidence_id,))
        return cursor.rowcount > 0


def get_evidence_by_entity(
    service,
    entity_type: EntityType,
    entity_id: int,
    source_type: Optional[SourceType] = None
) -> List[EvidenceSource]:
    """
    Get all evidence for a specific entity.

    Convenience method for retrieving complete evidence trail for a project, work item, or task.

    Args:
        service: DatabaseService instance
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID
        source_type: Optional filter by source type

    Returns:
        List of EvidenceSource models sorted by capture time (newest first)

    Example:
        >>> # Get all evidence for work item #43
        >>> evidence = get_evidence_by_entity(db, EntityType.WORK_ITEM, 43)
        >>> # Get only research evidence
        >>> research = get_evidence_by_entity(
        ...     db, EntityType.WORK_ITEM, 43, SourceType.RESEARCH
        ... )
    """
    return list_evidence_sources(
        service,
        entity_type=entity_type,
        entity_id=entity_id,
        source_type=source_type
    )


def get_high_confidence_evidence(
    service,
    entity_type: EntityType,
    entity_id: int,
    min_confidence: float = 0.8
) -> List[EvidenceSource]:
    """
    Get high-confidence evidence for an entity.

    Useful for decision-making where only trusted sources should be considered.

    Args:
        service: DatabaseService instance
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID
        min_confidence: Minimum confidence threshold (default: 0.8)

    Returns:
        List of high-confidence EvidenceSource models

    Example:
        >>> # Get only highly trusted evidence for task #238
        >>> trusted = get_high_confidence_evidence(db, EntityType.TASK, 238)
    """
    return list_evidence_sources(
        service,
        entity_type=entity_type,
        entity_id=entity_id,
        min_confidence=min_confidence
    )


def count_evidence_by_type(
    service,
    entity_type: EntityType,
    entity_id: int
) -> dict:
    """
    Count evidence sources by source type for an entity.

    Args:
        service: DatabaseService instance
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID

    Returns:
        Dict mapping source types to counts

    Example:
        >>> counts = count_evidence_by_type(db, EntityType.WORK_ITEM, 43)
        >>> counts
        {'documentation': 5, 'research': 3, 'stackoverflow': 2}
    """
    query = """
        SELECT source_type, COUNT(*) as count
        FROM evidence_sources
        WHERE entity_type = ? AND entity_id = ?
        GROUP BY source_type
    """

    with service.connect() as conn:
        cursor = conn.execute(query, (entity_type.value, entity_id))
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}
