"""
Research Blueprint - Evidence Sources, Events, and Documents Routes

Handles:
- Evidence sources with confidence tracking
- Events audit log with timeline view
- Document references with grouping and filters
"""

from flask import Blueprint, render_template, request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ...core.database.methods import evidence_sources as evidence_methods
from ...core.database.methods import events as event_methods
from ...core.database.methods import document_references as doc_methods
from ...core.database.enums import (
    EntityType, SourceType, EventType, DocumentType, DocumentFormat
)
from ...core.database.models.event import EventCategory, EventSeverity

# Import helper functions from app
from ..app import get_database_service

research_bp = Blueprint('research', __name__)


# ========================================
# Pydantic Models for View Data
# ========================================

class EvidenceSourceView(BaseModel):
    """Evidence source for list view with entity details"""
    id: int
    entity_type: str
    entity_id: int
    entity_name: Optional[str]  # Resolved entity name
    url: str
    source_type: str
    excerpt: Optional[str]
    confidence: float
    captured_at: Any
    created_by: Optional[str]


class EvidenceListView(BaseModel):
    """Evidence sources list view"""
    total_evidence: int
    evidence_list: List[EvidenceSourceView]
    entity_type_filter: Optional[str]
    source_type_filter: Optional[str]
    min_confidence_filter: Optional[float]


class EventView(BaseModel):
    """Event for timeline view"""
    id: int
    event_type: str
    event_category: str
    event_severity: str
    timestamp: Any
    source: str
    event_data: Dict[str, Any]
    project_id: Optional[int]
    work_item_id: Optional[int]
    task_id: Optional[int]
    # Resolved names
    work_item_name: Optional[str]
    task_name: Optional[str]


class EventsTimelineView(BaseModel):
    """Events timeline view"""
    total_events: int
    events_list: List[EventView]
    category_filter: Optional[str]
    type_filter: Optional[str]
    severity_filter: Optional[str]
    category_counts: Dict[str, int]


class DocumentView(BaseModel):
    """Document reference for list view"""
    id: int
    entity_type: str
    entity_id: int
    entity_name: Optional[str]  # Resolved entity name
    file_path: str
    document_type: str
    title: Optional[str]
    description: Optional[str]
    format: Optional[str]
    file_size_bytes: Optional[int]
    created_at: Any
    updated_at: Any


class DocumentsListView(BaseModel):
    """Documents list view with grouping"""
    total_documents: int
    documents_list: List[DocumentView]
    grouped_by_type: Dict[str, List[DocumentView]]
    entity_type_filter: Optional[str]
    document_type_filter: Optional[str]
    format_filter: Optional[str]
    type_counts: Dict[str, int]


# ========================================
# Helper Functions
# ========================================

def _resolve_entity_name(db, entity_type: str, entity_id: int) -> Optional[str]:
    """
    Resolve entity name from type and ID.

    Args:
        db: DatabaseService instance
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID

    Returns:
        Entity name or None if not found
    """
    from ...core.database.methods import projects as project_methods
    from ...core.database.methods import work_items as wi_methods
    from ...core.database.methods import tasks as task_methods

    try:
        if entity_type == EntityType.PROJECT.value:
            project = project_methods.get_project(db, entity_id)
            return project.name if project else None
        elif entity_type == EntityType.WORK_ITEM.value:
            work_item = wi_methods.get_work_item(db, entity_id)
            return work_item.name if work_item else None
        elif entity_type == EntityType.TASK.value:
            task = task_methods.get_task(db, entity_id)
            return task.name if task else None
    except Exception:
        return None

    return None


def _format_file_size(size_bytes: Optional[int]) -> str:
    """
    Format bytes to human-readable size.

    Args:
        size_bytes: File size in bytes

    Returns:
        Human-readable size string (e.g., "15.2 KB")
    """
    if size_bytes is None:
        return "Unknown"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ========================================
# Routes
# ========================================

@research_bp.route('/evidence')
def evidence_list():
    """
    Evidence sources list view with filtering.

    Query params:
        - entity_type: Filter by entity type (project, work_item, task)
        - source_type: Filter by source type (documentation, research, etc.)
        - min_confidence: Minimum confidence score (0.0-1.0)

    Returns:
        Rendered evidence sources list template
    """
    db = get_database_service()

    # Get query params
    entity_type_str = request.args.get('entity_type')
    source_type_str = request.args.get('source_type')
    min_confidence_str = request.args.get('min_confidence')

    # Convert to enums if provided
    entity_type = EntityType(entity_type_str) if entity_type_str else None
    source_type = SourceType(source_type_str) if source_type_str else None
    min_confidence = float(min_confidence_str) if min_confidence_str else None

    # Get evidence sources using database methods
    evidence_sources = evidence_methods.list_evidence_sources(
        db,
        entity_type=entity_type,
        source_type=source_type,
        min_confidence=min_confidence,
        limit=100
    )

    # Build view models with resolved entity names
    evidence_list_data = []
    for evidence in evidence_sources:
        entity_name = _resolve_entity_name(
            db, evidence.entity_type.value, evidence.entity_id
        )

        evidence_list_data.append(
            EvidenceSourceView(
                id=evidence.id,
                entity_type=evidence.entity_type.value,
                entity_id=evidence.entity_id,
                entity_name=entity_name,
                url=evidence.url,
                source_type=evidence.source_type.value,
                excerpt=evidence.excerpt,
                confidence=evidence.confidence,
                captured_at=evidence.captured_at,
                created_by=evidence.created_by
            )
        )

    view = EvidenceListView(
        total_evidence=len(evidence_list_data),
        evidence_list=evidence_list_data,
        entity_type_filter=entity_type_str,
        source_type_filter=source_type_str,
        min_confidence_filter=min_confidence
    )

    return render_template('evidence/list.html', view=view)


@research_bp.route('/events')
def events_timeline():
    """
    Events audit log timeline view with filtering.

    Query params:
        - category: Filter by event category (workflow, tool_usage, etc.)
        - type: Filter by event type (workflow_transition, agent_action, etc.)
        - severity: Filter by severity (info, warning, error, critical)
        - limit: Maximum events to display (default 100)

    Returns:
        Rendered events timeline template
    """
    db = get_database_service()

    # Get query params
    category_str = request.args.get('category')
    type_str = request.args.get('type')
    severity_str = request.args.get('severity')
    limit = int(request.args.get('limit', '100'))

    # Convert to enums if provided
    category = EventCategory(category_str) if category_str else None
    event_type = EventType(type_str) if type_str else None
    severity = EventSeverity(severity_str) if severity_str else None

    # Get events using database methods
    if category:
        events = event_methods.get_events_by_category(db, category, limit=limit)
    elif event_type:
        events = event_methods.get_events_by_type(db, event_type, limit=limit)
    elif severity:
        events = event_methods.get_events_by_severity(db, severity, limit=limit)
    else:
        # Get recent events across all sessions
        from datetime import timedelta
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        events = event_methods.get_events_by_time_range(db, week_ago, now)
        events = events[:limit]  # Limit results

    # Build view models with resolved entity names
    from ...core.database.methods import work_items as wi_methods
    from ...core.database.methods import tasks as task_methods

    events_list_data = []
    for event in events:
        # Resolve work item and task names
        work_item_name = None
        task_name = None

        if event.work_item_id:
            work_item = wi_methods.get_work_item(db, event.work_item_id)
            work_item_name = work_item.name if work_item else None

        if event.task_id:
            task = task_methods.get_task(db, event.task_id)
            task_name = task.name if task else None

        events_list_data.append(
            EventView(
                id=event.id,
                event_type=event.event_type.value,
                event_category=event.event_category.value,
                event_severity=event.event_severity.value,
                timestamp=event.timestamp,
                source=event.source,
                event_data=event.event_data or {},
                project_id=event.project_id,
                work_item_id=event.work_item_id,
                task_id=event.task_id,
                work_item_name=work_item_name,
                task_name=task_name
            )
        )

    # Calculate category counts for filter UI
    category_counts = {}
    for event in events:
        cat = event.event_category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1

    view = EventsTimelineView(
        total_events=len(events_list_data),
        events_list=events_list_data,
        category_filter=category_str,
        type_filter=type_str,
        severity_filter=severity_str,
        category_counts=category_counts
    )

    return render_template('events/timeline.html', view=view)


@research_bp.route('/documents')
def documents_list():
    """
    Document references list view with grouping and filtering.

    Query params:
        - entity_type: Filter by entity type (project, work_item, task)
        - document_type: Filter by document type (architecture, design, etc.)
        - format: Filter by format (markdown, yaml, pdf, etc.)

    Returns:
        Rendered documents list template
    """
    db = get_database_service()

    # Get query params
    entity_type_str = request.args.get('entity_type')
    doc_type_str = request.args.get('document_type')
    format_str = request.args.get('format')

    # Convert to enums if provided
    entity_type = EntityType(entity_type_str) if entity_type_str else None
    document_type = DocumentType(doc_type_str) if doc_type_str else None
    doc_format = DocumentFormat(format_str) if format_str else None

    # Get documents using database methods
    documents = doc_methods.list_document_references(
        db,
        entity_type=entity_type,
        document_type=document_type,
        format=doc_format,
        limit=100
    )

    # Build view models with resolved entity names
    documents_list_data = []
    for doc in documents:
        entity_name = _resolve_entity_name(
            db, doc.entity_type.value, doc.entity_id
        )

        documents_list_data.append(
            DocumentView(
                id=doc.id,
                entity_type=doc.entity_type.value,
                entity_id=doc.entity_id,
                entity_name=entity_name,
                file_path=doc.file_path,
                document_type=doc.document_type.value if doc.document_type else 'unknown',
                title=doc.title,
                description=doc.description,
                format=doc.format.value if doc.format else None,
                file_size_bytes=doc.file_size_bytes,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
        )

    # Group by document type
    grouped_by_type: Dict[str, List[DocumentView]] = {}
    for doc in documents_list_data:
        if doc.document_type not in grouped_by_type:
            grouped_by_type[doc.document_type] = []
        grouped_by_type[doc.document_type].append(doc)

    # Count documents by type
    type_counts = {dt: len(docs) for dt, docs in grouped_by_type.items()}

    view = DocumentsListView(
        total_documents=len(documents_list_data),
        documents_list=documents_list_data,
        grouped_by_type=grouped_by_type,
        entity_type_filter=entity_type_str,
        document_type_filter=doc_type_str,
        format_filter=format_str,
        type_counts=type_counts
    )

    return render_template(
        'documents/list.html',
        view=view,
        format_file_size=_format_file_size,
        show_sidebar='documents'
    )
