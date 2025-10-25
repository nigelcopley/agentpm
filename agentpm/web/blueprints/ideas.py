"""
Ideas Blueprint for APM (Agent Project Manager) Web Application

Ideas management functionality.
"""

from flask import Blueprint, render_template, abort, request, jsonify
import logging
from datetime import datetime

# Create ideas blueprint
ideas_bp = Blueprint('ideas', __name__, url_prefix='/ideas')

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

@ideas_bp.route('/')
def ideas_list():
    """Ideas list view with comprehensive metrics, filtering, and search"""
    try:
        db = get_database_service()
        
        # Get project ID for ideas
        from ...core.database.methods import projects, ideas
        from ...core.database.enums import IdeaStatus
        
        # Safely get projects list
        try:
            projects_list = projects.list_projects(db)
            if projects_list is None:
                projects_list = []
        except Exception as e:
            logger.warning(f"Error fetching projects: {e}")
            projects_list = []
        
        project_id = projects_list[0].id if projects_list else 1
        
        # Get filter parameters
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        vote_filter = request.args.get('votes', '')
        sort_by = request.args.get('sort', 'updated_desc')
        
        # Safely get ideas list
        try:
            ideas_list = ideas.list_ideas(db, project_id=project_id)
            if ideas_list is None:
                ideas_list = []
        except Exception as e:
            logger.warning(f"Error fetching ideas: {e}")
            ideas_list = []
        
        # Apply filters
        filtered_ideas = ideas_list
        
        # Search filter
        if search_query:
            filtered_ideas = [
                idea for idea in filtered_ideas
                if search_query.lower() in (idea.title or '').lower() or 
                   search_query.lower() in (idea.description or '').lower()
            ]
        
        # Status filter
        if status_filter:
            filtered_ideas = [
                idea for idea in filtered_ideas
                if idea.status and idea.status.value == status_filter
            ]
        
        # Vote filter
        if vote_filter:
            if vote_filter == 'high':
                filtered_ideas = [
                    idea for idea in filtered_ideas
                    if idea.votes and idea.votes >= 5
                ]
            elif vote_filter == 'medium':
                filtered_ideas = [
                    idea for idea in filtered_ideas
                    if idea.votes and idea.votes >= 2 and idea.votes < 5
                ]
            elif vote_filter == 'low':
                filtered_ideas = [
                    idea for idea in filtered_ideas
                    if idea.votes is None or idea.votes < 2
                ]
        
        # Apply sorting
        if sort_by == 'title_asc':
            filtered_ideas.sort(key=lambda x: (x.title or '').lower())
        elif sort_by == 'title_desc':
            filtered_ideas.sort(key=lambda x: (x.title or '').lower(), reverse=True)
        elif sort_by == 'status_asc':
            filtered_ideas.sort(key=lambda x: x.status.value if x.status else '')
        elif sort_by == 'status_desc':
            filtered_ideas.sort(key=lambda x: x.status.value if x.status else '', reverse=True)
        elif sort_by == 'votes_asc':
            filtered_ideas.sort(key=lambda x: x.votes or 0)
        elif sort_by == 'votes_desc':
            filtered_ideas.sort(key=lambda x: x.votes or 0, reverse=True)
        elif sort_by == 'created_asc':
            from datetime import datetime
            filtered_ideas.sort(key=lambda x: x.created_at or datetime.min)
        elif sort_by == 'created_desc':
            from datetime import datetime
            filtered_ideas.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        else:  # updated_desc (default)
            from datetime import datetime
            filtered_ideas.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
        
        # Calculate comprehensive metrics for the sidebar
        metrics = {
            # Basic counts
            'total_ideas': len(ideas_list),
            
            # Status-based counts
            'idea_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'idea']),
            'research_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'research']),
            'design_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'design']),
            'proposed_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'accepted']),
            'converted_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'converted']),
            'rejected_ideas': len([idea for idea in ideas_list if idea.status and idea.status.value == 'rejected']),
            
            # Priority-based counts - Ideas don't have priority, use votes instead
            'high_vote_ideas': len([idea for idea in ideas_list if idea.votes and idea.votes >= 5]),
            'medium_vote_ideas': len([idea for idea in ideas_list if idea.votes and idea.votes >= 2]),
            'low_vote_ideas': len([idea for idea in ideas_list if idea.votes and idea.votes < 2]),
        }
        
        # Get available filter options
        filter_options = {
            'statuses': [{'value': status.value, 'label': status.value.replace('_', ' ').title()} 
                        for status in IdeaStatus],
            # Ideas don't have priority, use vote ranges instead
            'vote_ranges': [
                {'value': 'high', 'label': 'High Votes (5+)'},
                {'value': 'medium', 'label': 'Medium Votes (2-4)'},
                {'value': 'low', 'label': 'Low Votes (0-1)'}
            ],
            'sort_options': [
                {'value': 'updated_desc', 'label': 'Last Updated (Newest)'},
                {'value': 'updated_asc', 'label': 'Last Updated (Oldest)'},
                {'value': 'created_desc', 'label': 'Created (Newest)'},
                {'value': 'created_asc', 'label': 'Created (Oldest)'},
                {'value': 'title_asc', 'label': 'Title (A-Z)'},
                {'value': 'title_desc', 'label': 'Title (Z-A)'},
                {'value': 'status_asc', 'label': 'Status (A-Z)'},
                {'value': 'status_desc', 'label': 'Status (Z-A)'},
                {'value': 'votes_asc', 'label': 'Votes (Low to High)'},
                {'value': 'votes_desc', 'label': 'Votes (High to Low)'},
            ]
        }
        
        return render_template('ideas/list.html', 
                             ideas=filtered_ideas, 
                             metrics=metrics,
                             filter_options=filter_options,
                             current_filters={
                                 'search': search_query,
                                 'status': status_filter,
                                 'votes': vote_filter,
                                 'sort': sort_by
                             })
    
    except Exception as e:
        logger.error(f"Unexpected error in ideas_list: {e}")
        # Return empty list on error
        return render_template('ideas/list.html', ideas=[], metrics={}, filter_options={}, current_filters={})

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
    """
    try:
        # Fetch idea data
        db = get_database_service()
        from ...core.database.methods import ideas
        
        idea = ideas.get_idea(db, idea_id)
        
        if not idea:
            abort(404, description=f"Idea {idea_id} not found")
        
        # Fetch idea elements
        from ...core.database.adapters.idea_element_adapter import IdeaElementAdapter
        try:
            elements = IdeaElementAdapter.list(db, idea_id=idea_id, order_by="order_index")
        except Exception as e:
            logger.warning(f"Error fetching idea elements: {e}")
            elements = []
        
        return render_template('ideas/detail.html', idea=idea, idea_id=idea_id, elements=elements)
        
    except Exception as e:
        logger.error(f"Unexpected error in idea_detail: {e}")
        abort(500, description="Internal server error")

@ideas_bp.route('/<int:idea_id>/vote', methods=['POST'])
def vote_idea(idea_id: int):
    """Vote for an idea"""
    try:
        db = get_database_service()
        from ...core.database.methods import ideas
        
        idea = ideas.get_idea(db, idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        # Check if idea can receive votes
        if idea.is_terminal():
            return jsonify({'success': False, 'message': 'Cannot vote on terminal ideas'}), 400
        
        # Increment vote count
        idea.votes = (idea.votes or 0) + 1
        idea.updated_at = datetime.now()
        
        # Update in database
        from ...core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify({'success': True, 'votes': idea.votes})
        
    except Exception as e:
        logger.error(f"Error voting for idea {idea_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@ideas_bp.route('/<int:idea_id>/transition', methods=['POST'])
def transition_idea(idea_id: int):
    """Transition idea to a new status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        db = get_database_service()
        from ...core.database.methods import ideas
        from ...core.database.enums import IdeaStatus
        
        idea = ideas.get_idea(db, idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        # Validate transition
        try:
            new_status_enum = IdeaStatus(new_status)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        if not idea.can_transition_to(new_status_enum):
            return jsonify({'success': False, 'message': f'Cannot transition from {idea.status.value} to {new_status}'}), 400
        
        # Update status
        idea.status = new_status_enum
        idea.updated_at = datetime.now()
        
        # Update in database
        from ...core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify({'success': True, 'status': idea.status.value})
        
    except Exception as e:
        logger.error(f"Error transitioning idea {idea_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@ideas_bp.route('/<int:idea_id>/convert', methods=['POST'])
def convert_idea(idea_id: int):
    """Convert idea to work item"""
    try:
        db = get_database_service()
        from ...core.database.methods import ideas, work_items
        from ...core.database.enums import IdeaStatus, WorkItemStatus, WorkItemType
        
        idea = ideas.get_idea(db, idea_id)
        if not idea:
            return jsonify({'success': False, 'message': 'Idea not found'}), 404
        
        # Check if idea can be converted
        if idea.status != IdeaStatus.ACTIVE:
            return jsonify({'success': False, 'message': 'Only accepted ideas can be converted to work items'}), 400
        
        if idea.converted_to_work_item_id:
            return jsonify({'success': False, 'message': 'Idea has already been converted'}), 400
        
        # Create work item from idea
        from ...core.database.models.work_item import WorkItem
        
        work_item = WorkItem(
            project_id=idea.project_id,
            name=idea.title,
            description=idea.description,
            type=WorkItemType.FEATURE,  # Default type
            status=WorkItemStatus.D1_DISCOVERY,  # Start in discovery phase
            created_by=idea.created_by,
            tags=idea.tags.copy() if idea.tags else []
        )
        
        # Create work item in database
        from ...core.database.adapters.work_item_adapter import WorkItemAdapter
        created_work_item = WorkItemAdapter.create(db, work_item)
        
        # Update idea to mark as converted
        idea.status = IdeaStatus.CONVERTED
        idea.converted_to_work_item_id = created_work_item.id
        idea.converted_at = datetime.now()
        idea.updated_at = datetime.now()
        
        # Update idea in database
        from ...core.database.adapters.idea_adapter import IdeaAdapter
        IdeaAdapter.update(db, idea)
        
        return jsonify({
            'success': True, 
            'work_item_id': created_work_item.id,
            'message': 'Idea converted to work item successfully'
        })
        
    except Exception as e:
        logger.error(f"Error converting idea {idea_id}: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
