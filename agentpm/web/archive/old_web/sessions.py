"""
Sessions Blueprint - Session Management and Timeline

Handles:
- /sessions - List all sessions
- /sessions/<id> - Get session details
- /sessions/timeline - Sessions timeline view
"""

from flask import Blueprint, render_template, abort, request
from datetime import datetime, timedelta

from ...core.database.methods import sessions as session_methods
from ...core.database.methods import projects as project_methods

# Import helper functions from app
from ..app import get_database_service

sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route('/sessions')
def sessions_list():
    """List all sessions with filtering and pagination."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 50, type=int)

    # Parse dates
    start_datetime = None
    end_datetime = None
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            pass
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            pass

    # Get sessions
    if start_datetime and end_datetime:
        sessions = session_methods.get_sessions_by_date_range(
            db,
            project_id=project_id,
            start=start_datetime,
            end=end_datetime
        )[:limit]
    else:
        sessions = session_methods.list_sessions(
            db,
            project_id=project_id,
            limit=limit
        )

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    return render_template(
        'sessions/list.html',
        sessions=sessions,
        projects=projects,
        current_project_id=project_id,
        current_start_date=start_date,
        current_end_date=end_date,
        show_sidebar='sessions'
    )


@sessions_bp.route('/sessions/<session_id>')
def session_detail(session_id: str):
    """Get session details."""
    db = get_database_service()

    session = session_methods.get_session(db, session_id)
    if not session:
        abort(404, description=f"Session {session_id} not found")

    # Get project info
    project = None
    if session.project_id:
        project = project_methods.get_project(db, session.project_id)

    # Parse metadata
    metadata = session.metadata or {}
    parsed_metadata = _parse_session_metadata(metadata)

    return render_template(
        'sessions/detail.html',
        session=session,
        project=project,
        metadata=parsed_metadata
    )


@sessions_bp.route('/sessions/timeline')
def sessions_timeline():
    """Sessions timeline view."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    days = request.args.get('days', 30, type=int)

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get sessions
    sessions = session_methods.get_sessions_by_date_range(
        db,
        project_id=project_id,
        start=start_date,
        end=end_date
    )[:100]  # Limit to 100

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    # Group sessions by date
    sessions_by_date = {}
    for session in sessions:
        date_key = session.created_at.strftime('%Y-%m-%d')
        if date_key not in sessions_by_date:
            sessions_by_date[date_key] = []
        sessions_by_date[date_key].append(session)

    return render_template(
        'sessions/timeline.html',
        sessions_by_date=sessions_by_date,
        projects=projects,
        current_project_id=project_id,
        current_days=days,
        show_sidebar='sessions'
    )


def _parse_session_metadata(metadata: dict) -> dict:
    """Parse session metadata into structured format."""
    parsed = {
        'agent': metadata.get('agent'),
        'model': metadata.get('model'),
        'temperature': metadata.get('temperature'),
        'max_tokens': metadata.get('max_tokens'),
        'tools_used': metadata.get('tools_used', []),
        'context_sources': metadata.get('context_sources', []),
        'work_items': metadata.get('work_items', []),
        'tasks': metadata.get('tasks', []),
        'decisions': metadata.get('decisions', []),
        'artifacts': metadata.get('artifacts', []),
        'errors': metadata.get('errors', []),
        'performance': metadata.get('performance', {}),
        'quality_metrics': metadata.get('quality_metrics', {})
    }
    
    return parsed
