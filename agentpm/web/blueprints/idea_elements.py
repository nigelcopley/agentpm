"""
Idea Elements Blueprint for APM (Agent Project Manager) Web Application

Handles idea element management functionality.
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

# Create idea elements blueprint
idea_elements_bp = Blueprint('idea_elements', __name__, url_prefix='/idea-elements')

logger = logging.getLogger(__name__)

def get_database_service():
    """Get database service instance"""
    from ...core.database.service import DatabaseService
    import os
    
    # Try different database paths
    db_paths = [
        '.agentpm/data/agentpm.db',
        '../.agentpm/data/agentpm.db',
        '../../.agentpm/data/agentpm.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            return DatabaseService(db_path)
    
    # If no database found, return service with default path
    return DatabaseService('.agentpm/data/agentpm.db')

@idea_elements_bp.route('/<int:element_id>', methods=['GET'])
def get_idea_element(element_id: int):
    """Get a specific idea element"""
    try:
        db = get_database_service()
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        
        # Get element
        element = IdeaElementAdapter.get(db, element_id)
        if not element:
            return jsonify({'success': False, 'message': 'Idea element not found'}), 404
        
        # Convert to dict for JSON response
        element_data = {
            'id': element.id,
            'idea_id': element.idea_id,
            'title': element.title,
            'description': element.description,
            'type': element.type.value,
            'effort_hours': element.effort_hours,
            'order_index': element.order_index,
            'is_completed': element.is_completed,
            'completed_at': element.completed_at.isoformat() if element.completed_at else None,
            'created_at': element.created_at.isoformat() if element.created_at else None,
            'updated_at': element.updated_at.isoformat() if element.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'element': element_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching idea element {element_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@idea_elements_bp.route('/', methods=['POST'])
def create_idea_element():
    """Create a new idea element"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['idea_id', 'title', 'type', 'effort_hours', 'order_index']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        db = get_database_service()
        from ...core.database.models.idea_element import IdeaElement
        from ...core.database.enums import TaskType
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        
        # Create idea element
        idea_element = IdeaElement(
            idea_id=data['idea_id'],
            title=data['title'],
            description=data.get('description'),
            type=TaskType(data['type']),
            effort_hours=float(data['effort_hours']),
            order_index=int(data['order_index']),
            is_completed=False
        )
        
        # Save to database
        created_element = IdeaElementAdapter.create(db, idea_element)
        
        return jsonify({
            'success': True,
            'element_id': created_element.id,
            'message': 'Idea element created successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error creating idea element: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@idea_elements_bp.route('/<int:element_id>', methods=['PUT'])
def update_idea_element(element_id: int):
    """Update an existing idea element"""
    try:
        data = request.get_json()
        
        db = get_database_service()
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        from ...core.database.enums import TaskType
        
        # Get existing element
        element = IdeaElementAdapter.get(db, element_id)
        if not element:
            return jsonify({'success': False, 'message': 'Idea element not found'}), 404
        
        # Update fields
        if 'title' in data:
            element.title = data['title']
        if 'description' in data:
            element.description = data['description']
        if 'type' in data:
            element.type = TaskType(data['type'])
        if 'effort_hours' in data:
            element.effort_hours = float(data['effort_hours'])
        if 'order_index' in data:
            element.order_index = int(data['order_index'])
        
        element.updated_at = datetime.now()
        
        # Save to database
        IdeaElementAdapter.update(db, element)
        
        return jsonify({
            'success': True,
            'message': 'Idea element updated successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error updating idea element {element_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@idea_elements_bp.route('/<int:element_id>', methods=['DELETE'])
def delete_idea_element(element_id: int):
    """Delete an idea element"""
    try:
        db = get_database_service()
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        
        # Check if element exists
        element = IdeaElementAdapter.get_by_id(db, element_id)
        if not element:
            return jsonify({'success': False, 'message': 'Idea element not found'}), 404
        
        # Delete from database
        IdeaElementAdapter.delete(db, element_id)
        
        return jsonify({
            'success': True,
            'message': 'Idea element deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting idea element {element_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@idea_elements_bp.route('/<int:element_id>/toggle-completion', methods=['POST'])
def toggle_element_completion(element_id: int):
    """Toggle completion status of an idea element"""
    try:
        db = get_database_service()
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        
        # Get existing element
        element = IdeaElementAdapter.get(db, element_id)
        if not element:
            return jsonify({'success': False, 'message': 'Idea element not found'}), 404
        
        # Toggle completion
        if element.is_completed:
            element.mark_incomplete()
        else:
            element.mark_completed()
        
        element.updated_at = datetime.now()
        
        # Save to database
        IdeaElementAdapter.update(db, element)
        
        return jsonify({
            'success': True,
            'is_completed': element.is_completed,
            'message': f'Element marked as {"completed" if element.is_completed else "incomplete"}'
        })
        
    except Exception as e:
        logger.error(f"Error toggling completion for idea element {element_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
