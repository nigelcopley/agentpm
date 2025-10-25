"""
Contexts Blueprint - Context Management and 6W Framework

Handles:
- /contexts - List all contexts
- /contexts/<id> - Get context details
- /contexts/<id>/refresh - Refresh context data
- /work-items/<id>/context - Work item context
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for
from datetime import datetime, timedelta

from ...core.database.methods import contexts as context_methods
from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as work_item_methods
from ...core.database.enums import EntityType

# Import helper functions from app
from ..app import get_database_service

contexts_bp = Blueprint('contexts', __name__)


@contexts_bp.route('/contexts')
def contexts_list():
    """List all contexts with filtering and quality metrics."""
    db = get_database_service()

    # Get filter params
    project_id = request.args.get('project_id', type=int)
    entity_type = request.args.get('entity_type')
    confidence_min = request.args.get('confidence_min', type=float)
    limit = request.args.get('limit', 50, type=int)

    # Get contexts
    contexts = context_methods.list_contexts(
        db,
        project_id=project_id,
        context_type=entity_type,
        confidence_band=confidence_min  # This might need adjustment
    )[:limit] if limit else context_methods.list_contexts(
        db,
        project_id=project_id,
        context_type=entity_type
    )

    # Get projects for filter dropdown
    projects = project_methods.list_projects(db)

    # Calculate quality metrics
    quality_metrics = _calculate_context_quality_metrics(contexts)

    return render_template(
        'contexts/list.html',
        contexts=contexts,
        projects=projects,
        quality_metrics=quality_metrics,
        current_project_id=project_id,
        current_entity_type=entity_type,
        current_confidence_min=confidence_min,
        show_sidebar='contexts'
    )


@contexts_bp.route('/contexts/<int:context_id>')
def context_detail(context_id: int):
    """Get context details with 6W analysis."""
    db = get_database_service()

    context = context_methods.get_context(db, context_id)
    if not context:
        abort(404, description=f"Context {context_id} not found")

    # Get entity info
    entity_info = _get_entity_info(db, context.entity_type, context.entity_id)

    # Calculate freshness
    freshness_days = _calculate_context_freshness(context)

    # Get related contexts (using existing method)
    related_contexts = context_methods.get_rich_contexts_by_entity(
        db,
        context.entity_type,
        context.entity_id
    )

    return render_template(
        'contexts/detail.html',
        context=context,
        entity_info=entity_info,
        freshness_days=freshness_days,
        related_contexts=related_contexts
    )


@contexts_bp.route('/contexts/<int:context_id>/refresh', methods=['POST'])
def context_refresh(context_id: int):
    """Refresh context data."""
    db = get_database_service()

    context = context_methods.get_context(db, context_id)
    if not context:
        abort(404, description=f"Context {context_id} not found")

    # TODO: Implement context refresh logic
    # This would trigger context assembly for the entity

    return redirect(url_for('contexts.context_detail', context_id=context_id))


@contexts_bp.route('/work-items/<int:work_item_id>/context')
def work_item_context(work_item_id: int):
    """Work item context view with hierarchical assembly."""
    db = get_database_service()

    # Get work item
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")

    # Get project
    project = project_methods.get_project(db, work_item.project_id)

    # Get contexts
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=work_item.project_id
    )

    work_item_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.WORK_ITEM,
        entity_id=work_item_id
    )

    # Get all tasks for this work item
    from ...core.database.methods import tasks as task_methods
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)

    # Get task contexts
    task_contexts = []
    for task in tasks:
        task_context = context_methods.get_entity_context(
            db,
            entity_type=EntityType.TASK,
            entity_id=task.id
        )
        if task_context:
            task_contexts.append(task_context)

    # Calculate context quality
    context_quality = _calculate_work_item_context_quality(
        project_context, work_item_context, task_contexts, tasks
    )

    # Hierarchical assembly info
    hierarchical_assembly = {
        'project_level': {
            'context': project_context,
            'confidence': project_context.confidence_score if project_context else 0.0,
            'freshness': _calculate_context_freshness(project_context) if project_context else 999
        },
        'work_item_level': {
            'context': work_item_context,
            'confidence': work_item_context.confidence_score if work_item_context else 0.0,
            'freshness': _calculate_context_freshness(work_item_context) if work_item_context else 999
        },
        'task_level': {
            'contexts': task_contexts,
            'average_confidence': sum(tc.confidence_score or 0.0 for tc in task_contexts) / len(task_contexts) if task_contexts else 0.0,
            'average_freshness': sum(_calculate_context_freshness(tc) for tc in task_contexts) / len(task_contexts) if task_contexts else 999
        }
    }

    return render_template(
        'contexts/work_item_context.html',
        work_item=work_item,
        project=project,
        project_context=project_context,
        work_item_context=work_item_context,
        task_contexts=task_contexts,
        context_quality=context_quality,
        hierarchical_assembly=hierarchical_assembly
    )


def _calculate_context_quality_metrics(contexts):
    """Calculate context quality metrics."""
    if not contexts:
        return {
            'total_contexts': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'fresh_contexts': 0,
            'stale_contexts': 0,
            'average_confidence': 0.0
        }

    total = len(contexts)
    high_confidence = sum(1 for c in contexts if (c.confidence_score or 0) >= 0.8)
    medium_confidence = sum(1 for c in contexts if 0.5 <= (c.confidence_score or 0) < 0.8)
    low_confidence = sum(1 for c in contexts if (c.confidence_score or 0) < 0.5)
    
    fresh_contexts = sum(1 for c in contexts if _calculate_context_freshness(c) <= 7)
    stale_contexts = total - fresh_contexts
    
    average_confidence = sum(c.confidence_score or 0.0 for c in contexts) / total

    return {
        'total_contexts': total,
        'high_confidence': high_confidence,
        'medium_confidence': medium_confidence,
        'low_confidence': low_confidence,
        'fresh_contexts': fresh_contexts,
        'stale_contexts': stale_contexts,
        'average_confidence': round(average_confidence, 2)
    }


def _get_entity_info(db, entity_type: EntityType, entity_id: int):
    """Get entity information for context display."""
    if entity_type == EntityType.PROJECT:
        project = project_methods.get_project(db, entity_id)
        return {
            'type': 'Project',
            'name': project.name if project else 'Unknown',
            'id': entity_id
        }
    elif entity_type == EntityType.WORK_ITEM:
        work_item = work_item_methods.get_work_item(db, entity_id)
        return {
            'type': 'Work Item',
            'name': work_item.name if work_item else 'Unknown',
            'id': entity_id
        }
    elif entity_type == EntityType.TASK:
        from ...core.database.methods import tasks as task_methods
        task = task_methods.get_task(db, entity_id)
        return {
            'type': 'Task',
            'name': task.name if task else 'Unknown',
            'id': entity_id
        }
    else:
        return {
            'type': entity_type.value,
            'name': f'Entity {entity_id}',
            'id': entity_id
        }


def _calculate_context_freshness(context) -> int:
    """Calculate context freshness in days."""
    if not context or not context.updated_at:
        return 999  # Very stale
    
    delta = datetime.now() - context.updated_at
    return delta.days


def _calculate_work_item_context_quality(project_context, work_item_context, task_contexts, tasks):
    """Calculate work item context quality."""
    has_project_context = project_context is not None
    has_work_item_context = work_item_context is not None
    task_contexts_count = len(task_contexts)
    total_tasks = len(tasks)
    context_coverage = (task_contexts_count / total_tasks * 100) if tasks else 0
    
    overall_quality = 'high'
    if not has_project_context or not has_work_item_context or task_contexts_count == 0:
        overall_quality = 'medium'
    if not has_project_context and not has_work_item_context:
        overall_quality = 'low'
    
    return {
        'has_project_context': has_project_context,
        'has_work_item_context': has_work_item_context,
        'task_contexts_count': task_contexts_count,
        'total_tasks': total_tasks,
        'context_coverage': round(context_coverage, 1),
        'overall_quality': overall_quality
    }
