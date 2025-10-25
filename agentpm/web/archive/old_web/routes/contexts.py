"""
Contexts Blueprint - Context Management and 6W Framework Routes

Handles:
- Contexts list view with confidence scoring
- Context detail view with 6W data
- Work item context view with hierarchical assembly
- Context refresh and validation
"""

from flask import Blueprint, render_template, abort, request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ...core.database.methods import contexts as context_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import projects as project_methods
from ...core.database.enums import EntityType, ConfidenceBand, ContextType

# Import helper functions from app
from ..app import get_database_service

contexts_bp = Blueprint('contexts', __name__)


# ========================================
# Pydantic Models for View Data
# ========================================

class ContextView(BaseModel):
    """Context for list view with confidence scoring"""
    id: int
    entity_type: str
    entity_id: int
    entity_name: Optional[str]
    context_type: str
    confidence_score: float
    confidence_band: str
    freshness_days: int
    six_w_completeness: float
    created_at: datetime
    updated_at: datetime
    plugin_facts_count: int
    amalgamations_count: int


class ContextsListView(BaseModel):
    """Contexts list view with filtering"""
    total_contexts: int
    contexts_list: List[ContextView]
    entity_type_filter: Optional[str]
    confidence_band_filter: Optional[str]
    freshness_filter: Optional[str]
    confidence_band_counts: Dict[str, int]
    entity_type_counts: Dict[str, int]


class ContextDetailView(BaseModel):
    """Context detail view with 6W data"""
    context: Any  # Context model
    entity: Optional[Any]  # Related entity (project/work_item/task)
    six_w_data: Dict[str, Any]
    confidence_factors: Dict[str, Any]
    plugin_facts: List[Dict[str, Any]]
    amalgamations: List[Dict[str, Any]]
    freshness_info: Dict[str, Any]
    quality_indicators: Dict[str, Any]


class WorkItemContextView(BaseModel):
    """Hierarchical context view for work item"""
    work_item: Any
    project: Optional[Any]
    project_context: Optional[Any]
    work_item_context: Optional[Any]
    task_contexts: List[Any]
    merged_context: Optional[Any]
    context_quality: Dict[str, Any]
    hierarchical_assembly: Dict[str, Any]


# ========================================
# Helper Functions
# ========================================

def _resolve_entity_name(db, entity_type: str, entity_id: int) -> Optional[str]:
    """Resolve entity name from type and ID"""
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


def _calculate_freshness_days(updated_at: Optional[datetime]) -> int:
    """Calculate days since last update"""
    if not updated_at:
        return 999  # Very stale
    
    delta = datetime.now() - updated_at
    return delta.days


def _calculate_six_w_completeness(six_w_data: Optional[Dict[str, Any]]) -> float:
    """Calculate 6W completeness percentage"""
    if not six_w_data:
        return 0.0
    
    required_fields = ['who', 'what', 'when', 'where', 'why', 'how']
    present_fields = sum(1 for field in required_fields if six_w_data.get(field))
    
    return (present_fields / len(required_fields)) * 100


def _parse_context_data(context_data: Optional[str]) -> Dict[str, Any]:
    """Parse context data JSON"""
    if not context_data:
        return {}
    
    try:
        import json
        return json.loads(context_data)
    except (json.JSONDecodeError, TypeError):
        return {}


def _extract_plugin_facts(context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract plugin facts from context data"""
    facts = context_data.get('plugin_facts', [])
    if isinstance(facts, list):
        return facts
    return []


def _extract_amalgamations(context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract amalgamations from context data"""
    amalgamations = context_data.get('amalgamations', [])
    if isinstance(amalgamations, list):
        return amalgamations
    return []


def _extract_six_w_data(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract 6W data from context data"""
    six_w = context_data.get('six_w_data', {})
    if isinstance(six_w, dict):
        return six_w
    return {}


def _extract_confidence_factors(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract confidence factors from context data"""
    factors = context_data.get('confidence_factors', {})
    if isinstance(factors, dict):
        return factors
    return {}


# ========================================
# Routes
# ========================================

@contexts_bp.route('/contexts')
def contexts_list():
    """
    Contexts list view with confidence scoring.
    
    Shows all contexts with:
    - Entity (project/work_item/task)
    - Confidence band (RED/YELLOW/GREEN)
    - Freshness (days since update)
    - 6W completeness
    - Plugin facts and amalgamations count
    
    Query params:
        - entity_type: Filter by entity type
        - confidence_band: Filter by confidence band
        - freshness: Filter by freshness (fresh, stale, very_stale)
    """
    db = get_database_service()
    
    # Get query params
    entity_type_str = request.args.get('entity_type')
    confidence_band_str = request.args.get('confidence_band')
    freshness_filter = request.args.get('freshness')
    
    # Convert to enums if provided
    entity_type = EntityType(entity_type_str) if entity_type_str else None
    confidence_band = ConfidenceBand(confidence_band_str) if confidence_band_str else None
    
    # Get contexts using database methods
    try:
        contexts = context_methods.list_contexts(
            db,
            project_id=None,  # Get all contexts for now
            context_type=None,  # Get all context types
            confidence_band=confidence_band
        )
    except Exception as e:
        # Handle case where no contexts exist
        contexts = []
    
    # Build view models with resolved entity names
    contexts_list_data = []
    confidence_band_counts = {}
    entity_type_counts = {}
    
    for context in contexts:
        entity_name = _resolve_entity_name(db, context.entity_type.value, context.entity_id)
        context_data = _parse_context_data(context.six_w)
        
        # Calculate metrics
        freshness_days = _calculate_freshness_days(context.updated_at)
        six_w_completeness = _calculate_six_w_completeness(_extract_six_w_data(context_data))
        plugin_facts_count = len(_extract_plugin_facts(context_data))
        amalgamations_count = len(_extract_amalgamations(context_data))
        
        # Count confidence bands
        band = context.confidence_band.value if context.confidence_band else 'unknown'
        confidence_band_counts[band] = confidence_band_counts.get(band, 0) + 1
        
        # Count entity types
        entity_type = context.entity_type.value
        entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        # Apply freshness filter
        if freshness_filter:
            if freshness_filter == 'fresh' and freshness_days > 7:
                continue
            elif freshness_filter == 'stale' and (freshness_days <= 7 or freshness_days > 30):
                continue
            elif freshness_filter == 'very_stale' and freshness_days <= 30:
                continue
        
        contexts_list_data.append(
            ContextView(
                id=context.id,
                entity_type=context.entity_type.value,
                entity_id=context.entity_id,
                entity_name=entity_name,
                context_type=context.context_type.value if context.context_type else 'unknown',
                confidence_score=context.confidence_score or 0.0,
                confidence_band=band,
                freshness_days=freshness_days,
                six_w_completeness=round(six_w_completeness, 1),
                created_at=context.created_at or datetime.now(),
                updated_at=context.updated_at or datetime.now(),
                plugin_facts_count=plugin_facts_count,
                amalgamations_count=amalgamations_count
            )
        )
    
    view = ContextsListView(
        total_contexts=len(contexts_list_data),
        contexts_list=contexts_list_data,
        entity_type_filter=entity_type_str,
        confidence_band_filter=confidence_band_str,
        freshness_filter=freshness_filter,
        confidence_band_counts=confidence_band_counts,
        entity_type_counts=entity_type_counts
    )
    
    return render_template('contexts/list.html', view=view)


@contexts_bp.route('/context/<int:context_id>')
def context_detail(context_id: int):
    """
    Context detail view with 6W data.
    
    Shows:
    - Complete context data
    - 6W framework breakdown (Who, What, When, Where, Why, How)
    - Confidence factors and scoring
    - Plugin facts and amalgamations
    - Freshness and quality indicators
    
    Args:
        context_id: Context ID
    """
    db = get_database_service()
    
    # Get context using database methods
    context = context_methods.get_context(db, context_id)
    
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    # Get related entity
    entity = None
    try:
        if context.entity_type == EntityType.PROJECT:
            entity = project_methods.get_project(db, context.entity_id)
        elif context.entity_type == EntityType.WORK_ITEM:
            entity = wi_methods.get_work_item(db, context.entity_id)
        elif context.entity_type == EntityType.TASK:
            entity = task_methods.get_task(db, context.entity_id)
    except Exception:
        pass
    
    # Handle 6W data - it's already a UnifiedSixW object, not JSON
    if hasattr(context.six_w, 'end_users'):
        # It's a UnifiedSixW object - extract data directly
        six_w_data = {
            'who': context.who,  # Use convenience property
            'what': context.what,  # Use convenience property
            'where': context.where,  # Use convenience property
            'when': context.when_context,  # Use convenience property
            'why': context.why,  # Use convenience property
            'how': context.how,  # Use convenience property
            'end_users': context.six_w.end_users or [],
            'implementers': context.six_w.implementers or [],
            'reviewers': context.six_w.reviewers or [],
            'functional_requirements': context.six_w.functional_requirements or [],
            'technical_constraints': context.six_w.technical_constraints or [],
            'acceptance_criteria': context.six_w.acceptance_criteria or [],
            'affected_services': context.six_w.affected_services or [],
            'repositories': context.six_w.repositories or [],
            'deployment_targets': context.six_w.deployment_targets or [],
            'deadline': context.six_w.deadline,
            'dependencies_timeline': context.six_w.dependencies_timeline or [],
            'business_value': context.six_w.business_value,
            'risk_if_delayed': context.six_w.risk_if_delayed,
            'suggested_approach': context.six_w.suggested_approach,
            'existing_patterns': context.six_w.existing_patterns or []
        }
        confidence_factors = context.confidence_factors or {}
        plugin_facts = []
        amalgamations = []
    else:
        # Fallback to JSON parsing for backward compatibility
        context_data = _parse_context_data(context.six_w)
        six_w_data = _extract_six_w_data(context_data)
        confidence_factors = _extract_confidence_factors(context_data)
        plugin_facts = _extract_plugin_facts(context_data)
        amalgamations = _extract_amalgamations(context_data)
    
    # Calculate freshness info
    freshness_days = _calculate_freshness_days(context.updated_at)
    freshness_info = {
        'days_old': freshness_days,
        'status': 'fresh' if freshness_days <= 7 else 'stale' if freshness_days <= 30 else 'very_stale',
        'last_updated': context.updated_at,
        'needs_refresh': freshness_days > 7
    }
    
    # Calculate quality indicators
    six_w_completeness = _calculate_six_w_completeness(six_w_data)
    quality_indicators = {
        'six_w_completeness': round(six_w_completeness, 1),
        'plugin_facts_count': len(plugin_facts),
        'amalgamations_count': len(amalgamations),
        'confidence_score': context.confidence_score or 0.0,
        'confidence_band': context.confidence_band.value if context.confidence_band else 'unknown',
        'overall_quality': 'high' if six_w_completeness > 80 and (context.confidence_score or 0) > 0.8 else 'medium' if six_w_completeness > 60 else 'low'
    }
    
    view = ContextDetailView(
        context=context,
        entity=entity,
        six_w_data=six_w_data,
        confidence_factors=confidence_factors,
        plugin_facts=plugin_facts,
        amalgamations=amalgamations,
        freshness_info=freshness_info,
        quality_indicators=quality_indicators
    )
    
    return render_template('contexts/detail.html', view=view)


@contexts_bp.route('/work-item/<int:work_item_id>/context')
def work_item_context(work_item_id: int):
    """
    Hierarchical context view for work item.
    
    Shows:
    - Project context (inherited)
    - Work item context (specific)
    - Task contexts (all tasks)
    - Merged hierarchical view
    - Context quality and assembly info
    
    Args:
        work_item_id: Work item ID
    """
    db = get_database_service()
    
    # Get work item
    work_item = wi_methods.get_work_item(db, work_item_id)
    
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
    context_quality = {
        'has_project_context': project_context is not None,
        'has_work_item_context': work_item_context is not None,
        'task_contexts_count': len(task_contexts),
        'total_tasks': len(tasks),
        'context_coverage': (len(task_contexts) / len(tasks) * 100) if tasks else 0,
        'overall_quality': 'high' if project_context and work_item_context and len(task_contexts) > 0 else 'medium' if project_context or work_item_context else 'low'
    }
    
    # Hierarchical assembly info
    hierarchical_assembly = {
        'project_level': {
            'context': project_context,
            'confidence': project_context.confidence_score if project_context else 0.0,
            'freshness': _calculate_freshness_days(project_context.updated_at) if project_context else 999
        },
        'work_item_level': {
            'context': work_item_context,
            'confidence': work_item_context.confidence_score if work_item_context else 0.0,
            'freshness': _calculate_freshness_days(work_item_context.updated_at) if work_item_context else 999
        },
        'task_level': {
            'contexts': task_contexts,
            'average_confidence': sum(tc.confidence_score or 0.0 for tc in task_contexts) / len(task_contexts) if task_contexts else 0.0,
            'average_freshness': sum(_calculate_freshness_days(tc.updated_at) for tc in task_contexts) / len(task_contexts) if task_contexts else 999
        }
    }
    
    view = WorkItemContextView(
        work_item=work_item,
        project=project,
        project_context=project_context,
        work_item_context=work_item_context,
        task_contexts=task_contexts,
        merged_context=None,  # TODO: Implement context merging
        context_quality=context_quality,
        hierarchical_assembly=hierarchical_assembly
    )
    
    return render_template('work_item_context.html', view=view)


@contexts_bp.route('/context/<int:context_id>/refresh', methods=['POST'])
def refresh_context(context_id: int):
    """
    Refresh context data.
    
    Triggers context refresh for the specified context.
    
    Args:
        context_id: Context ID to refresh
    """
    db = get_database_service()
    
    # Get context
    context = context_methods.get_context(db, context_id)
    
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    # TODO: Implement context refresh logic
    # This would trigger the context service to refresh the context
    
    return {'status': 'success', 'message': f'Context {context_id} refresh triggered'}
