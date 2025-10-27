"""
Ideas Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for ideas including:
- Create, Read, Update, Delete operations
- Voting functionality
- Status transitions
- Idea conversion to work items
"""

import logging
from datetime import datetime
from typing import Optional

from flask import request, jsonify, flash, redirect, url_for

from ....core.database.methods import ideas
from ....core.database.models import Idea
from ....core.database.enums import IdeaStatus
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_idea():
    """Create a new idea."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'title': 'Idea title is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('ideas.ideas_list'))
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        project_id = int(request.form.get('project_id', 1))
        
        # Create idea
        idea = Idea(
            title=title,
            description=description if description else None,
            project_id=project_id,
            status=IdeaStatus.IDEA,
            votes=0
        )
        
        created_idea = ideas.create_idea(db, idea)
        
        flash(f'Idea "{created_idea.title}" created successfully', 'success')
        return redirect(url_for('ideas.idea_detail', idea_id=created_idea.id))
        
    except Exception as e:
        return handle_error(e, 'Error creating idea', url_for('ideas.ideas_list'))

def update_idea(idea_id: int):
    """Update an existing idea"""
    try:
        db = get_database_service()
        from ....core.database.methods import ideas
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            flash('Idea not found', 'error')
            return redirect(url_for('ideas.ideas_list'))
        
        # Validate required fields
        required_fields = {
            'title': 'Idea title is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('ideas.edit_idea', idea_id=idea_id))
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        project_id = int(request.form.get('project_id', 1))
        
        # Update idea using the correct method signature
        updated_idea = ideas.update_idea(db, idea)
        
        # Update the fields
        idea.title = title
        idea.description = description if description else None
        idea.project_id = project_id
        idea.updated_at = datetime.now()
        
        flash(f'Idea "{idea.title}" updated successfully', 'success')
        return redirect(url_for('ideas.idea_detail', idea_id=idea_id))
        
    except Exception as e:
        return handle_error(e, 'Error updating idea', url_for('ideas.edit_idea', idea_id=idea_id))

def delete_idea(idea_id: int):
    """Delete an idea"""
    try:
        db = get_database_service()
        from ....core.database.methods import ideas
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            flash('Idea not found', 'error')
            return redirect(url_for('ideas.ideas_list'))
        
        idea_title = idea.title
        ideas.delete_idea(db, idea_id)
        
        flash(f'Idea "{idea_title}" deleted successfully', 'success')
        return redirect(url_for('ideas.ideas_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting idea', url_for('ideas.idea_detail', idea_id=idea_id))

def vote_idea(idea_id: int):
    """Vote for an idea"""
    try:
        db = get_database_service()
        from ....core.database.methods import ideas
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return jsonify(create_error_response('Idea not found', 404))
        
        # Check if idea can receive votes
        if idea.is_terminal():
            return jsonify(create_error_response('Cannot vote on terminal ideas', 400))
        
        # Vote on the idea using the correct method signature
        voted_idea = ideas.vote_on_idea(db, idea_id, delta=1)
        
        return jsonify(create_success_response('Vote recorded', {'votes': voted_idea.votes}))
        
    except Exception as e:
        logger.error(f"Error voting for idea {idea_id}: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def transition_idea(idea_id: int):
    """Transition idea to a new status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify(create_error_response('Status is required', 400))
        
        db = get_database_service()
        from ....core.database.methods import ideas
        from ....core.database.enums import IdeaStatus
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return jsonify(create_error_response('Idea not found', 404))
        
        # Validate transition
        try:
            new_status_enum = IdeaStatus(new_status)
        except ValueError:
            return jsonify(create_error_response('Invalid status', 400))
        
        if not idea.can_transition_to(new_status_enum):
            return jsonify(create_error_response(f'Cannot transition from {idea.status.value} to {new_status}', 400))
        
        # Transition the idea using the correct method signature
        transitioned_idea = ideas.transition_idea(db, idea_id, new_status_enum)
        
        return jsonify(create_success_response(f'Idea transitioned to {new_status}', {'status': new_status}))
        
    except Exception as e:
        logger.error(f"Error transitioning idea {idea_id}: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def convert_idea(idea_id: int):
    """Convert idea to work item"""
    try:
        data = request.get_json()
        work_item_name = data.get('name', '').strip()
        work_item_description = data.get('description', '').strip()
        work_item_type = data.get('type', 'feature')
        priority = int(data.get('priority', 3))
        
        if not work_item_name:
            return jsonify(create_error_response('Work item name is required', 400))
        
        db = get_database_service()
        from ....core.database.methods import ideas
        from ....core.database.enums import WorkItemType
        
        idea = safe_get_entity(ideas.get_idea, db, idea_id, "Idea")
        if not idea:
            return jsonify(create_error_response('Idea not found', 404))
        
        # Check if idea can be converted
        if not idea.can_transition_to('converted'):
            return jsonify(create_error_response('Idea cannot be converted in its current state', 400))
        
        # Convert idea to work item using the correct method signature
        work_item = ideas.convert_idea_to_work_item(
            db, 
            idea_id, 
            work_item_name, 
            work_item_description if work_item_description else idea.description,
            WorkItemType(work_item_type),
            priority
        )
        
        return jsonify(create_success_response(
            'Idea converted to work item successfully', 
            {'work_item_id': work_item.id, 'work_item_name': work_item.name}
        ))
        
    except Exception as e:
        logger.error(f"Error converting idea {idea_id}: {e}")
        return jsonify(create_error_response('Internal server error', 500))
