"""
Ideas List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for ideas including:
- Ideas listing with filtering and search
- Vote-based filtering
- Comprehensive metrics
"""

from flask import render_template, request
from datetime import datetime
import logging

from . import ideas_bp
from ..utils import get_database_service, _is_htmx_request
from ...utils.pagination import paginate_items, get_pagination_from_request, get_query_params_from_request

logger = logging.getLogger(__name__)

@ideas_bp.route('/')
def ideas_list():
    """Ideas list view with comprehensive metrics, filtering, search, and pagination"""
    try:
        db = get_database_service()
        
        # Get pagination parameters
        page, per_page = get_pagination_from_request(request, default_per_page=20)
        
        # Get project ID for ideas
        from ....core.database.methods import projects, ideas
        from ....core.database.enums import IdeaStatus
        
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
            filtered_ideas.sort(key=lambda x: x.created_at or datetime.min)
        elif sort_by == 'created_desc':
            filtered_ideas.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        else:  # updated_desc (default)
            filtered_ideas.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
        
        # Apply pagination
        paginated_ideas, pagination = paginate_items(
            items=filtered_ideas,
            page=page,
            per_page=per_page,
            base_url=request.path,
            query_params=get_query_params_from_request(request)
        )
        
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
                             ideas=paginated_ideas, 
                             metrics=metrics,
                             filter_options=filter_options,
                             pagination=pagination,
                             current_filters={
                                 'search': search_query,
                                 'status': status_filter,
                                 'votes': vote_filter,
                                 'sort': sort_by
                             })
    
    except Exception as e:
        logger.error(f"Error in ideas list: {e}")
        return render_template('ideas/list.html', 
                             ideas=[], 
                             metrics={'total_ideas': 0},
                             filter_options={'statuses': [], 'vote_ranges': [], 'sort_options': []},
                             current_filters={'search': '', 'status': '', 'votes': '', 'sort': 'updated_desc'})
