"""
Research Blueprint - Research, Evidence, and Documentation

Handles:
- /research/evidence - Evidence sources
- /research/events - Events timeline
- /research/documents - Document references
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for
from datetime import datetime, timedelta

from ...core.database.methods import evidence_sources as evidence_methods
from ...core.database.methods import events as event_methods
from ...core.database.methods import document_references
from ...core.database.enums import EntityType
from ...core.database.methods import projects as project_methods

# Import helper functions from app
from ..app import get_database_service

research_bp = Blueprint('research', __name__)


@research_bp.route('/evidence')
def evidence_list():
    """Standalone evidence list view."""
    return redirect(url_for('research.evidence_sources'))


@research_bp.route('/research/evidence')
def evidence_sources():
    """Evidence sources view."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    source_type = request.args.get('source_type')
    sort_by = request.args.get('sort', 'created_desc')
    limit = request.args.get('limit', 50, type=int)

    # Get evidence sources
    evidence_list = evidence_methods.list_evidence_sources(
        db,
        entity_type=EntityType.PROJECT if project_id else None,
        entity_id=project_id,
        source_type=source_type,
        limit=limit
    )

    # Apply sorting
    if sort_by == 'created_desc':
        evidence_list.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    elif sort_by == 'created_asc':
        evidence_list.sort(key=lambda x: x.created_at or datetime.min, reverse=False)
    elif sort_by == 'source_asc':
        evidence_list.sort(key=lambda x: (x.source_url or '').lower())
    elif sort_by == 'source_desc':
        evidence_list.sort(key=lambda x: (x.source_url or '').lower(), reverse=True)
    elif sort_by == 'confidence_desc':
        evidence_list.sort(key=lambda x: x.confidence_score or 0, reverse=True)
    elif sort_by == 'confidence_asc':
        evidence_list.sort(key=lambda x: x.confidence_score or 0)

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    # Get source type distribution
    source_types = {}
    for source in evidence_list:
        stype = source.source_type or 'unknown'
        source_types[stype] = source_types.get(stype, 0) + 1

    return render_template(
        'research/evidence.html',
        evidence_sources=evidence_list,
        projects=projects,
        source_types=source_types,
        current_project_id=project_id,
        current_source_type=source_type,
        current_sort=sort_by,
        show_sidebar='research'
    )


@research_bp.route('/events')
def events_list():
    """Standalone events list view."""
    return redirect(url_for('research.events_timeline'))


@research_bp.route('/research/events')
def events_timeline():
    """Events timeline view."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    days = request.args.get('days', 30, type=int)
    event_type = request.args.get('event_type')

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get events
    events = event_methods.get_events_by_time_range(
        db,
        start_date,
        end_date
    )
    
    # Filter by project_id and event_type if specified
    if project_id:
        events = [e for e in events if hasattr(e, 'project_id') and e.project_id == project_id]
    if event_type:
        events = [e for e in events if hasattr(e, 'event_type') and e.event_type == event_type]
    
    events = events[:100]  # Limit to 100

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    # Group events by date
    events_by_date = {}
    for event in events:
        date_key = event.timestamp.strftime('%Y-%m-%d')
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    # Get event type distribution
    event_types = {}
    for event in events:
        etype = event.event_type or 'unknown'
        event_types[etype] = event_types.get(etype, 0) + 1

    return render_template(
        'research/events.html',
        events_by_date=events_by_date,
        projects=projects,
        event_types=event_types,
        current_project_id=project_id,
        current_days=days,
        current_event_type=event_type,
        show_sidebar='research'
    )


@research_bp.route('/documents')
def documents_list():
    """Standalone documents list view."""
    return redirect(url_for('research.document_references_view'))


@research_bp.route('/research/documents')
def document_references_view():
    """Document references view."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    document_type = request.args.get('document_type')
    sort_by = request.args.get('sort', 'created_desc')
    limit = request.args.get('limit', 50, type=int)

    # Get document references
    documents_list = document_references.list_document_references(
        db,
        entity_type=EntityType.PROJECT if project_id else None,
        entity_id=project_id,
        document_type=document_type,
        limit=limit
    )

    # Apply sorting
    if sort_by == 'created_desc':
        documents_list.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    elif sort_by == 'created_asc':
        documents_list.sort(key=lambda x: x.created_at or datetime.min, reverse=False)
    elif sort_by == 'title_asc':
        documents_list.sort(key=lambda x: (x.title or '').lower())
    elif sort_by == 'title_desc':
        documents_list.sort(key=lambda x: (x.title or '').lower(), reverse=True)
    elif sort_by == 'path_asc':
        documents_list.sort(key=lambda x: (x.file_path or '').lower())
    elif sort_by == 'path_desc':
        documents_list.sort(key=lambda x: (x.file_path or '').lower(), reverse=True)

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    # Get document type distribution
    doc_types = {}
    for doc in documents_list:
        dtype = doc.document_type or 'unknown'
        doc_types[dtype] = doc_types.get(dtype, 0) + 1

    return render_template(
        'research/documents.html',
        documents=documents_list,
        projects=projects,
        doc_types=doc_types,
        current_project_id=project_id,
        current_document_type=document_type,
        current_sort=sort_by,
        show_sidebar='research'
    )
