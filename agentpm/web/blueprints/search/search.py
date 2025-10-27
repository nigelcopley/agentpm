"""
Search Module for APM (Agent Project Manager) Web Application

Handles comprehensive search functionality including:
- Cross-entity search across all system entities
- Search suggestions and autocomplete
- Advanced search filters
"""

from flask import render_template, request
import logging

from . import search_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@search_bp.route('/')
def search():
    """
    Search results with inline suggestions.
    
    Provides comprehensive search across:
    - Work items
    - Tasks
    - Ideas
    - Agents
    - Context
    - Rules
    - Documents
    """
    try:
        db = get_database_service()
        
        # Get search query
        query = request.args.get('q', '').strip()
        
        # Get search results from all entities
        search_results = {
            'work_items': [],
            'tasks': [],
            'ideas': [],
            'agents': [],
            'contexts': [],
            'rules': [],
            'documents': []
        }
        
        if query:
            # Search work items
            try:
                from ....core.database.methods import work_items, projects
                projects_list = projects.list_projects(db) or []
                project_id = projects_list[0].id if projects_list else 1
                all_work_items = work_items.list_work_items(db, project_id=project_id) or []
                search_results['work_items'] = [
                    wi for wi in all_work_items
                    if query.lower() in (wi.name or '').lower() or 
                       query.lower() in (wi.description or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching work items: {e}")
            
            # Search tasks
            try:
                from ....core.database.methods import tasks
                all_tasks = tasks.list_tasks(db) or []
                search_results['tasks'] = [
                    task for task in all_tasks
                    if query.lower() in (task.name or '').lower() or 
                       query.lower() in (task.description or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching tasks: {e}")
            
            # Search ideas
            try:
                from ....core.database.methods import ideas
                projects_list = projects.list_projects(db) or []
                project_id = projects_list[0].id if projects_list else 1
                all_ideas = ideas.list_ideas(db, project_id=project_id) or []
                search_results['ideas'] = [
                    idea for idea in all_ideas
                    if query.lower() in (idea.title or '').lower() or 
                       query.lower() in (idea.description or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching ideas: {e}")
            
            # Search agents
            try:
                from ....core.database.methods import agents
                all_agents = agents.list_agents(db) or []
                search_results['agents'] = [
                    agent for agent in all_agents
                    if query.lower() in (agent.name or '').lower() or 
                       query.lower() in (agent.description or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching agents: {e}")
            
            # Search contexts
            try:
                from ....core.database.methods import contexts
                projects_list = projects.list_projects(db) or []
                project_id = projects_list[0].id if projects_list else 1
                all_contexts = contexts.list_contexts(db, project_id=project_id) or []
                search_results['contexts'] = [
                    ctx for ctx in all_contexts
                    if query.lower() in (ctx.what or '').lower() or 
                       query.lower() in (ctx.why or '').lower() or
                       query.lower() in (ctx.how or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching contexts: {e}")
            
            # Search rules
            try:
                from ....core.database.methods import rules
                all_rules = rules.list_rules(db) or []
                search_results['rules'] = [
                    rule for rule in all_rules
                    if query.lower() in (rule.name or '').lower() or 
                       query.lower() in (rule.description or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching rules: {e}")
            
            # Search documents
            try:
                from ....core.database.methods import document_references
                projects_list = projects.list_projects(db) or []
                project_id = projects_list[0].id if projects_list else 1
                all_documents = document_references.list_document_references(db, project_id=project_id) or []
                search_results['documents'] = [
                    doc for doc in all_documents
                    if query.lower() in (doc.title or '').lower() or 
                       query.lower() in (doc.content or '').lower()
                ]
            except Exception as e:
                logger.warning(f"Error searching documents: {e}")
        
        # Calculate total results
        total_results = sum(len(results) for results in search_results.values())
        
        # Create search model
        search_model = {
            'query': query,
            'results': search_results,
            'total_results': total_results,
            'has_results': total_results > 0
        }
        
        return render_template('search/results.html', search=search_model)
    
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return render_template('search/results.html', 
                             search={
                                 'query': request.args.get('q', ''),
                                 'results': {},
                                 'total_results': 0,
                                 'has_results': False,
                                 'error': str(e)
                             })
