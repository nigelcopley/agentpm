"""
Sessions Blueprint - Session Management and Timeline Routes

Handles:
- Sessions list view with provider, duration, work items
- Session detail view with metadata, learnings, git commits
- Sessions timeline view with visual timeline
"""

from flask import Blueprint, render_template, abort, request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ...core.database.methods import sessions as session_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import projects as project_methods
from ...core.database.models.session import SessionStatus

# Import helper functions from app
from ..app import get_database_service

sessions_bp = Blueprint('sessions', __name__)


# ========================================
# Pydantic Models for View Data
# ========================================

class SessionView(BaseModel):
    """Session for list view with key metrics"""
    id: int
    session_id: str
    tool_name: str
    llm_model: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    work_items_touched: int
    tasks_completed: int
    decisions_made: int
    git_commits: int
    developer_name: Optional[str]
    status: str
    project_id: Optional[int]
    project_name: Optional[str]


class SessionsListView(BaseModel):
    """Sessions list view with filtering"""
    total_sessions: int
    sessions_list: List[SessionView]
    provider_filter: Optional[str]
    status_filter: Optional[str]
    date_range_filter: Optional[str]
    provider_counts: Dict[str, int]


class SessionDetailView(BaseModel):
    """Session detail view with complete metadata"""
    session: Any  # Session model
    metadata: Dict[str, Any]
    work_items: List[Any]
    tasks: List[Any]
    project: Optional[Any]
    git_commits: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    next_session_context: Optional[str]


class SessionsTimelineView(BaseModel):
    """Sessions timeline view with visual data"""
    total_sessions: int
    sessions_by_date: Dict[str, List[SessionView]]
    daily_activity: Dict[str, int]
    provider_activity: Dict[str, int]
    work_items_progress: Dict[str, int]


# ========================================
# Helper Functions
# ========================================

def _resolve_project_name(db, project_id: Optional[int]) -> Optional[str]:
    """Resolve project name from ID"""
    if not project_id:
        return None
    
    try:
        project = project_methods.get_project(db, project_id)
        return project.name if project else None
    except Exception:
        return None


def _parse_session_metadata(metadata_json: Optional[str]) -> Dict[str, Any]:
    """Parse session metadata JSON"""
    if not metadata_json:
        return {}
    
    try:
        import json
        return json.loads(metadata_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _extract_git_commits(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract git commits from session metadata"""
    commits = metadata.get('git_commits', [])
    if isinstance(commits, list):
        # Convert string commit hashes to dictionaries if needed
        result = []
        for commit in commits:
            if isinstance(commit, str):
                # Convert string hash to dictionary
                result.append({
                    'hash': commit,
                    'message': f'Commit {commit[:7]}',
                    'author': 'Unknown',
                    'date': 'Unknown'
                })
            elif isinstance(commit, dict):
                # Already a dictionary
                result.append(commit)
        return result
    return []


def _extract_decisions(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract decisions from session metadata"""
    decisions = metadata.get('decisions_made', [])
    if isinstance(decisions, list):
        return decisions
    return []


def _extract_patterns(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract patterns from session metadata"""
    patterns = metadata.get('patterns_identified', [])
    if isinstance(patterns, list):
        return patterns
    return []


# ========================================
# Routes
# ========================================

@sessions_bp.route('/sessions')
def sessions_list():
    """
    Sessions list view with filtering.
    
    Shows all sessions with key metrics:
    - Session ID, provider (Claude/Cursor/Aider)
    - Start/end time, duration
    - Work items touched, tasks completed
    - Decisions made, git commits
    - Developer name, status
    
    Query params:
        - provider: Filter by tool name
        - status: Filter by session status
        - date_range: Filter by date range (today, week, month)
    """
    db = get_database_service()
    
    # Get query params
    provider_filter = request.args.get('provider')
    status_filter = request.args.get('status')
    date_range_filter = request.args.get('date_range', 'week')
    
    # Calculate date range
    now = datetime.now()
    if date_range_filter == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range_filter == 'week':
        start_date = now - timedelta(days=7)
    elif date_range_filter == 'month':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)  # Default to week
    
    # Get sessions using database methods
    # Note: list_sessions requires project_id, so we'll get all sessions for now
    # TODO: Add project filtering or get all projects first
    try:
        sessions = session_methods.list_sessions(
            db,
            project_id=1,  # Default to project 1 for now
            limit=100
        )
    except Exception as e:
        # Handle case where no sessions exist or project doesn't exist
        sessions = []
    
    # Build view models with resolved project names
    sessions_list_data = []
    provider_counts = {}
    
    for session in sessions:
        project_name = _resolve_project_name(db, session.project_id)
        # Handle metadata - it's already a SessionMetadata object, not JSON
        if hasattr(session.metadata, 'work_items_touched'):
            # It's a SessionMetadata object
            work_items_touched = len(session.metadata.work_items_touched or [])
            tasks_completed = len(session.metadata.tasks_completed or [])
            decisions_made = len(session.metadata.decisions_made or [])
            git_commits = len(session.metadata.git_commits or [])
        else:
            # Fallback to JSON parsing for backward compatibility
            metadata = _parse_session_metadata(session.metadata)
            work_items_touched = len(metadata.get('work_items_touched', []))
            tasks_completed = len(metadata.get('tasks_completed', []))
            decisions_made = len(_extract_decisions(metadata))
            git_commits = len(_extract_git_commits(metadata))
        
        # Calculate duration
        duration_minutes = None
        if session.start_time and session.end_time:
            duration = session.end_time - session.start_time
            duration_minutes = int(duration.total_seconds() / 60)
        
        # Count providers
        provider = session.tool_name or 'unknown'
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        sessions_list_data.append(
            SessionView(
                id=session.id,
                session_id=session.session_id,
                tool_name=session.tool_name or 'Unknown',
                llm_model=session.llm_model,
                start_time=session.start_time,
                end_time=session.end_time,
                duration_minutes=duration_minutes,
                work_items_touched=work_items_touched,
                tasks_completed=tasks_completed,
                decisions_made=decisions_made,
                git_commits=git_commits,
                developer_name=session.developer_name,
                status=session.status.value if session.status else 'unknown',
                project_id=session.project_id,
                project_name=project_name
            )
        )
    
    view = SessionsListView(
        total_sessions=len(sessions_list_data),
        sessions_list=sessions_list_data,
        provider_filter=provider_filter,
        status_filter=status_filter,
        date_range_filter=date_range_filter,
        provider_counts=provider_counts
    )
    
    return render_template('sessions/list.html', view=view)


@sessions_bp.route('/session/<session_id>')
def session_detail(session_id: str):
    """
    Session detail view with complete metadata.
    
    Shows:
    - Complete session metadata
    - Work items and tasks involved
    - Git commits made
    - Decisions made
    - Patterns identified
    - Next session context
    
    Args:
        session_id: Session identifier
    """
    db = get_database_service()
    
    # Get session using database methods
    session = session_methods.get_session(db, session_id)
    
    if not session:
        abort(404, description=f"Session {session_id} not found")
    
    # Handle metadata - it's already a SessionMetadata object, not JSON
    if hasattr(session.metadata, 'work_items_touched'):
        # It's a SessionMetadata object - convert to dict for template
        metadata = {
            'work_items_touched': session.metadata.work_items_touched or [],
            'tasks_completed': session.metadata.tasks_completed or [],
            'decisions_made': session.metadata.decisions_made or [],
            'git_commits': session.metadata.git_commits or [],
            'blockers_resolved': session.metadata.blockers_resolved or [],
            'commands_executed': session.metadata.commands_executed or 0,
            'session_summary': session.metadata.session_summary,
            'next_session': session.metadata.next_session,
            'tool_specific': session.metadata.tool_specific or {}
        }
    else:
        # Fallback to JSON parsing for backward compatibility
        metadata = _parse_session_metadata(session.metadata)
    
    # Get related entities
    work_items = []
    tasks = []
    project = None
    
    if session.project_id:
        project = project_methods.get_project(db, session.project_id)
    
    # Get work items and tasks from metadata
    work_item_ids = metadata.get('work_items_touched', [])
    task_ids = metadata.get('tasks_completed', [])
    
    for wi_id in work_item_ids:
        try:
            work_item = wi_methods.get_work_item(db, wi_id)
            if work_item:
                work_items.append(work_item)
        except Exception:
            continue
    
    for task_id in task_ids:
        try:
            task = task_methods.get_task(db, task_id)
            if task:
                tasks.append(task)
        except Exception:
            continue
    
    # Extract structured data from metadata
    git_commits = _extract_git_commits(metadata)
    decisions = _extract_decisions(metadata)
    patterns = _extract_patterns(metadata)
    next_session_context = metadata.get('next_session_context')
    
    view = SessionDetailView(
        session=session,
        metadata=metadata,
        work_items=work_items,
        tasks=tasks,
        project=project,
        git_commits=git_commits,
        decisions=decisions,
        patterns=patterns,
        next_session_context=next_session_context
    )
    
    return render_template('sessions/detail.html', view=view)


@sessions_bp.route('/sessions/timeline')
def sessions_timeline():
    """
    Sessions timeline view with visual timeline.
    
    Shows:
    - Sessions grouped by date
    - Daily activity levels
    - Provider activity breakdown
    - Work items progress over time
    """
    db = get_database_service()
    
    # Get sessions from last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    sessions: List[Any] = []
    try:
        projects = project_methods.list_projects(db)
    except Exception:
        projects = []

    for project in projects:
        try:
            sessions.extend(
                session_methods.get_sessions_by_date_range(
                    db,
                    project.id,
                    start_date,
                    end_date
                )
            )
        except Exception:
            continue

    sessions.sort(key=lambda s: s.start_time or datetime.min, reverse=True)
    
    # Group sessions by date
    sessions_by_date = {}
    daily_activity = {}
    provider_activity = {}
    work_items_progress = {}
    
    for session in sessions:
        if not session.start_time:
            continue
            
        date_key = session.start_time.strftime('%Y-%m-%d')
        
        # Group by date
        if date_key not in sessions_by_date:
            sessions_by_date[date_key] = []
        sessions_by_date[date_key].append(session)
        
        # Count daily activity
        daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        # Count provider activity
        provider = session.tool_name or 'unknown'
        provider_activity[provider] = provider_activity.get(provider, 0) + 1
        
        # Count work items progress
        metadata = _parse_session_metadata(session.metadata)
        work_items_count = len(metadata.get('work_items_touched', []))
        work_items_progress[date_key] = work_items_progress.get(date_key, 0) + work_items_count
    
    # Convert sessions to view models
    sessions_by_date_views = {}
    for date_key, date_sessions in sessions_by_date.items():
        sessions_by_date_views[date_key] = []
        for session in date_sessions:
            project_name = _resolve_project_name(db, session.project_id)
            metadata = _parse_session_metadata(session.metadata)
            
            work_items_touched = len(metadata.get('work_items_touched', []))
            tasks_completed = len(metadata.get('tasks_completed', []))
            decisions_made = len(_extract_decisions(metadata))
            git_commits = len(_extract_git_commits(metadata))
            
            duration_minutes = None
            if session.start_time and session.end_time:
                duration = session.end_time - session.start_time
                duration_minutes = int(duration.total_seconds() / 60)
            
            sessions_by_date_views[date_key].append(
                SessionView(
                    id=session.id,
                    session_id=session.session_id,
                    tool_name=session.tool_name or 'Unknown',
                    llm_model=session.llm_model,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    duration_minutes=duration_minutes,
                    work_items_touched=work_items_touched,
                    tasks_completed=tasks_completed,
                    decisions_made=decisions_made,
                    git_commits=git_commits,
                    developer_name=session.developer_name,
                    status=session.status.value if session.status else 'unknown',
                    project_id=session.project_id,
                    project_name=project_name
                )
            )
    
    view = SessionsTimelineView(
        total_sessions=len(sessions),
        sessions_by_date=sessions_by_date_views,
        daily_activity=daily_activity,
        provider_activity=provider_activity,
        work_items_progress=work_items_progress
    )
    
    return render_template('sessions/timeline.html', view=view)
