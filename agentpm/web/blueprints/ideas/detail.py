"""
Ideas Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for ideas including:
- Individual idea detail views with comprehensive context
- Idea voting functionality
- Idea status transitions
- Idea conversion to work items
- Idea elements management
"""

from flask import render_template, abort, request, jsonify
from datetime import datetime
import logging

from . import ideas_bp
from ..utils import get_database_service, safe_get_entity, create_success_response, create_error_response

logger = logging.getLogger(__name__)

@ideas_bp.route('/<int:idea_id>')
def idea_detail(idea_id: int):
    """
    Comprehensive idea detail view.
    
    Shows all idea information in a single view:
    - Basic information (title, description, status)
    - Context and relationships
    - Voting history
    - Transition history
    - Related work items (if converted)
    - Idea elements
    - Project context
    - Related contexts
    """
    try:
        # Fetch idea data
        db = get_database_service()
        from ....core.database.methods import ideas, projects, work_items, contexts
        from ....core.database.enums import EntityType
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        
        if not idea:
            abort(404, description=f"Idea {idea_id} not found")
        
        # Get project information
        project = None
        if idea.project_id:
            projects_list = projects.list_projects(db) or []
            project = next((p for p in projects_list if p.id == idea.project_id), None)
        
        # Fetch idea elements
        from ....core.database.adapters.idea_element_adapter import IdeaElementAdapter
        try:
            elements = IdeaElementAdapter.list(db, idea_id=idea_id, order_by="order_index")
        except Exception as e:
            logger.warning(f"Error fetching idea elements: {e}")
            elements = []
        
        # Get related work items (if idea was converted)
        related_work_items = []
        if idea.status and idea.status.value == 'converted':
            try:
                all_work_items = work_items.list_work_items(db, project_id=idea.project_id) or []
                related_work_items = [wi for wi in all_work_items if wi.originated_from_idea_id == idea_id]
            except Exception as e:
                logger.warning(f"Error fetching related work items: {e}")
        
        # Get idea contexts
        idea_contexts = []
        try:
            idea_contexts = contexts.get_rich_contexts_by_entity(
                db, EntityType.IDEA, idea_id
            ) or []
        except Exception as e:
            logger.warning(f"Error fetching idea contexts: {e}")
        
        # Calculate idea statistics
        idea_stats = {
            'is_active': idea.status and idea.status.value in ['idea', 'research', 'design'],
            'is_converted': idea.status and idea.status.value == 'converted',
            'is_terminal': idea.is_terminal(),
            'can_vote': not idea.is_terminal(),
            'can_transition': idea.status and idea.status.value in ['idea', 'research', 'design'],
            'can_convert': idea.status and idea.status.value == 'accepted',
            'days_since_created': (datetime.now() - idea.created_at).days if idea.created_at else None,
            'days_since_updated': (datetime.now() - idea.updated_at).days if idea.updated_at else None,
            'has_elements': len(elements) > 0,
            'has_contexts': len(idea_contexts) > 0,
            'has_work_items': len(related_work_items) > 0,
            'vote_strength': 'high' if idea.votes and idea.votes >= 5 else 'medium' if idea.votes and idea.votes >= 2 else 'low'
        }
        
        # Get available transitions
        available_transitions = []
        if idea.status:
            try:
                available_transitions = idea.get_available_transitions()
            except Exception as e:
                logger.warning(f"Error getting available transitions: {e}")
        
        return render_template('ideas/detail.html', 
                             idea=idea, 
                             idea_id=idea_id, 
                             project=project,
                             elements=elements,
                             related_work_items=related_work_items,
                             idea_contexts=idea_contexts,
                             idea_stats=idea_stats,
                             available_transitions=available_transitions)
        
    except Exception as e:
        logger.error(f"Unexpected error in idea_detail: {e}")
        abort(500, description="Internal server error")

@ideas_bp.route('/<int:idea_id>/vote', methods=['POST'])
def vote_idea(idea_id: int):
    """Vote for an idea"""
    try:
        db = get_database_service()
        from ....core.database.methods import ideas
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return create_error_response('Idea not found', 404)
        
        # Check if idea can receive votes
        if idea.is_terminal():
            return create_error_response('Cannot vote on terminal ideas', 400)
        
        # Increment vote count
        idea.votes = (idea.votes or 0) + 1
        idea.updated_at = datetime.now()
        
        # Update in database
        from ....core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify(create_success_response('Vote recorded', {'votes': idea.votes}))
        
    except Exception as e:
        logger.error(f"Error voting for idea {idea_id}: {e}")
        return create_error_response('Internal server error', 500)

@ideas_bp.route('/<int:idea_id>/transition', methods=['POST'])
def transition_idea(idea_id: int):
    """Transition idea to a new status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return create_error_response('Status is required', 400)
        
        db = get_database_service()
        from ....core.database.methods import ideas
        from ....core.database.enums import IdeaStatus
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return create_error_response('Idea not found', 404)
        
        # Validate transition
        try:
            new_status_enum = IdeaStatus(new_status)
        except ValueError:
            return create_error_response('Invalid status', 400)
        
        if not idea.can_transition_to(new_status_enum):
            return create_error_response(f'Cannot transition from {idea.status.value} to {new_status}', 400)
        
        # Update status
        idea.status = new_status_enum
        idea.updated_at = datetime.now()
        
        # Update in database
        from ....core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify(create_success_response(f'Idea transitioned to {new_status}', {'status': new_status}))
        
    except Exception as e:
        logger.error(f"Error transitioning idea {idea_id}: {e}")
        return create_error_response('Internal server error', 500)

@ideas_bp.route('/<int:idea_id>/convert', methods=['POST'])
def convert_idea(idea_id: int):
    """Convert idea to work item"""
    try:
        data = request.get_json()
        work_item_name = data.get('name', '').strip()
        work_item_description = data.get('description', '').strip()
        work_item_type = data.get('type', 'feature')
        priority = int(data.get('priority', 3))
        
        if not work_item_name:
            return create_error_response('Work item name is required', 400)
        
        db = get_database_service()
        from ....core.database.methods import ideas, work_items
        from ....core.database.models import WorkItem
        from ....core.database.enums import WorkItemType, WorkItemStatus
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return create_error_response('Idea not found', 404)
        
        # Check if idea can be converted
        if not idea.can_transition_to('converted'):
            return create_error_response('Idea cannot be converted in its current state', 400)
        
        # Create work item
        work_item = WorkItem(
            name=work_item_name,
            description=work_item_description if work_item_description else idea.description,
            type=WorkItemType(work_item_type),
            priority=priority,
            project_id=idea.project_id,
            originated_from_idea_id=idea_id,
            status=WorkItemStatus.DRAFT
        )
        
        created_work_item = work_items.create_work_item(db, work_item)
        
        # Update idea status to converted
        idea.status = 'converted'
        idea.updated_at = datetime.now()
        
        from ....core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify(create_success_response(
            'Idea converted to work item successfully', 
            {'work_item_id': created_work_item.id, 'work_item_name': created_work_item.name}
        ))
        
    except Exception as e:
        logger.error(f"Error converting idea {idea_id}: {e}")
        return create_error_response('Internal server error', 500)
