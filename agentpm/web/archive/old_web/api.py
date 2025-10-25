"""
API Blueprint - RESTful API Endpoints

Handles:
- /api/projects - Projects API
- /api/work-items - Work items API
- /api/tasks - Tasks API
- /api/agents - Agents API
- /api/rules - Rules API
- /api/ideas - Ideas API
- /api/sessions - Sessions API
- /api/contexts - Contexts API
- /api/search - Search API
"""

from flask import Blueprint, request, jsonify, abort
from datetime import datetime

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as work_item_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods
from ...core.database.methods import ideas as idea_methods
from ...core.database.methods import sessions as session_methods
from ...core.database.methods import contexts as context_methods

# Import helper functions from app
from ..app import get_database_service

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/projects')
def api_projects():
    """Projects API endpoint."""
    db = get_database_service()
    projects = project_methods.list_projects(db)
    
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'status': p.status.value if p.status else None,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None
        }
        for p in projects
    ])


@api_bp.route('/projects/<int:project_id>')
def api_project_detail(project_id: int):
    """Project detail API endpoint."""
    db = get_database_service()
    project = project_methods.get_project(db, project_id)
    
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'status': project.status.value if project.status else None,
        'pm_philosophy': project.pm_philosophy.value if project.pm_philosophy else None,
        'project_type': project.project_type.value if project.project_type else None,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None
    })


@api_bp.route('/work-items')
def api_work_items():
    """Work items API endpoint."""
    db = get_database_service()
    project_id = request.args.get('project_id', type=int)
    
    work_items = work_item_methods.list_work_items(db, project_id=project_id)
    
    return jsonify([
        {
            'id': wi.id,
            'name': wi.name,
            'description': wi.description,
            'status': wi.status.value if wi.status else None,
            'type': wi.type.value if wi.type else None,
            'priority': wi.priority,
            'project_id': wi.project_id,
            'created_at': wi.created_at.isoformat() if wi.created_at else None,
            'updated_at': wi.updated_at.isoformat() if wi.updated_at else None
        }
        for wi in work_items
    ])


@api_bp.route('/work-items/<int:work_item_id>')
def api_work_item_detail(work_item_id: int):
    """Work item detail API endpoint."""
    db = get_database_service()
    work_item = work_item_methods.get_work_item(db, work_item_id)
    
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    return jsonify({
        'id': work_item.id,
        'name': work_item.name,
        'description': work_item.description,
        'status': work_item.status.value if work_item.status else None,
        'type': work_item.type.value if work_item.type else None,
        'priority': work_item.priority,
        'project_id': work_item.project_id,
        'created_at': work_item.created_at.isoformat() if work_item.created_at else None,
        'updated_at': work_item.updated_at.isoformat() if work_item.updated_at else None
    })


@api_bp.route('/tasks')
def api_tasks():
    """Tasks API endpoint."""
    db = get_database_service()
    work_item_id = request.args.get('work_item_id', type=int)
    
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
    
    return jsonify([
        {
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'status': t.status.value if t.status else None,
            'type': t.type.value if t.type else None,
            'priority': t.priority,
            'effort_hours': t.effort_hours,
            'assigned_to': t.assigned_to,
            'work_item_id': t.work_item_id,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'updated_at': t.updated_at.isoformat() if t.updated_at else None
        }
        for t in tasks
    ])


@api_bp.route('/tasks/<int:task_id>')
def api_task_detail(task_id: int):
    """Task detail API endpoint."""
    db = get_database_service()
    task = task_methods.get_task(db, task_id)
    
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    return jsonify({
        'id': task.id,
        'name': task.name,
        'description': task.description,
        'status': task.status.value if task.status else None,
        'type': task.type.value if task.type else None,
        'priority': task.priority,
        'effort_hours': task.effort_hours,
        'assigned_to': task.assigned_to,
        'work_item_id': task.work_item_id,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None
    })


@api_bp.route('/agents')
def api_agents():
    """Agents API endpoint."""
    db = get_database_service()
    agents = agent_methods.list_agents(db)
    
    return jsonify([
        {
            'id': a.id,
            'role': a.role,
            'display_name': a.display_name,
            'description': a.description,
            'capabilities': a.capabilities or [],
            'is_active': a.is_active,
            'project_id': a.project_id,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'updated_at': a.updated_at.isoformat() if a.updated_at else None
        }
        for a in agents
    ])


@api_bp.route('/rules')
def api_rules():
    """Rules API endpoint."""
    db = get_database_service()
    rules = rule_methods.list_rules(db)
    
    return jsonify([
        {
            'id': r.id,
            'rule_id': r.rule_id,
            'name': r.name,
            'description': r.description,
            'category': r.category,
            'enforcement_level': r.enforcement_level.value if r.enforcement_level else None,
            'enabled': r.enabled,
            'project_id': r.project_id,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'updated_at': r.updated_at.isoformat() if r.updated_at else None
        }
        for r in rules
    ])


@api_bp.route('/ideas')
def api_ideas():
    """Ideas API endpoint."""
    db = get_database_service()
    project_id = request.args.get('project_id', type=int)
    
    ideas = idea_methods.list_ideas(db, project_id=project_id)
    
    return jsonify([
        {
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'status': i.status,
            'votes': i.votes,
            'tags': i.tags or [],
            'project_id': i.project_id,
            'created_at': i.created_at.isoformat() if i.created_at else None,
            'updated_at': i.updated_at.isoformat() if i.updated_at else None
        }
        for i in ideas
    ])


@api_bp.route('/sessions')
def api_sessions():
    """Sessions API endpoint."""
    db = get_database_service()
    project_id = request.args.get('project_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    sessions = session_methods.list_sessions(db, project_id=project_id, limit=limit)
    
    return jsonify([
        {
            'id': s.id,
            'session_id': s.session_id,
            'project_id': s.project_id,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None
        }
        for s in sessions
    ])


@api_bp.route('/contexts')
def api_contexts():
    """Contexts API endpoint."""
    db = get_database_service()
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    
    contexts = context_methods.list_contexts(
        db,
        project_id=entity_id,  # Assuming entity_id is project_id for now
        context_type=entity_type
    )
    
    return jsonify([
        {
            'id': c.id,
            'entity_type': c.entity_type.value if c.entity_type else None,
            'entity_id': c.entity_id,
            'confidence_score': c.confidence_score,
            'confidence_band': c.confidence_band.value if c.confidence_band else None,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        }
        for c in contexts
    ])
