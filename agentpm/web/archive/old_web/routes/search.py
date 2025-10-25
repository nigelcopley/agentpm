"""
Search Blueprint - Search Functionality Routes

Handles:
- Search results page (/search)
- Search API endpoints
- Search filtering and pagination
"""

from flask import Blueprint, render_template, request, jsonify, abort
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ...core.database.service import DatabaseService
from ...core.search.service import SearchService
from ...core.search.models import SearchQuery, SearchFilter, SearchScope
from ...core.database.enums import EntityType
from ..app import get_database_service

search_bp = Blueprint('search', __name__)


class SearchResultView(BaseModel):
    """Search result view model for templates."""
    entity_id: int
    entity_type: str
    title: str
    content: str
    relevance_score: float
    highlighted_title: Optional[str] = None
    highlighted_content: Optional[str] = None
    snippet: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    url: str = ""


class SearchResultsView(BaseModel):
    """Search results page view model."""
    query: str
    results: List[SearchResultView]
    total_results: int
    page: int
    per_page: int
    total_pages: int
    entity_types: List[str]
    selected_entity_types: List[str]
    execution_time_ms: float
    suggestions: Optional[List[str]] = None


@search_bp.route('/search')
def search_results():
    """
    Search results page.
    
    Query parameters:
    - q: Search query (required)
    - entity_type: Filter by entity type (optional)
    - page: Page number (default: 1)
    - per_page: Results per page (default: 20)
    
    Returns:
        Rendered search results template
    """
    # Get query parameters
    query = request.args.get('q', '').strip()
    entity_type = request.args.get('entity_type', '')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)  # Cap at 100
    
    if not query:
        # Show empty search page
        return render_template('search/results.html', 
                             model=SearchResultsView(
                                 query="",
                                 results=[],
                                 total_results=0,
                                 page=1,
                                 per_page=per_page,
                                 total_pages=0,
                                 entity_types=[e.value for e in EntityType],
                                 selected_entity_types=[],
                                 execution_time_ms=0.0
                             ))
    
    # Initialize services
    db = get_database_service()
    search_service = SearchService(db)
    
    # Build search query
    search_query = SearchQuery(
        query=query,
        limit=per_page,
        offset=(page - 1) * per_page,
        highlight=True,
        include_content=False
    )
    
    # Add entity type filter if specified
    if entity_type and entity_type in [e.value for e in EntityType]:
        search_query.filters = SearchFilter(
            entity_types=[EntityType(entity_type)]
        )
    
    # Execute search
    import time
    start_time = time.time()
    search_results = search_service.search(search_query)
    execution_time = (time.time() - start_time) * 1000
    
    # Convert results to view models
    result_views = []
    for result in search_results.results:
        # Determine URL based on entity type
        url = _get_entity_url(result.entity_type, result.entity_id)
        
        result_view = SearchResultView(
            entity_id=result.entity_id,
            entity_type=result.entity_type.value,
            title=result.title,
            content=result.content,
            relevance_score=result.relevance_score,
            highlighted_title=getattr(result, 'highlighted_title', None),
            highlighted_content=getattr(result, 'highlighted_content', None),
            snippet=getattr(result, 'snippet', None),
            metadata=result.metadata or {},
            url=url
        )
        result_views.append(result_view)
    
    # Calculate pagination
    total_pages = (search_results.total_results + per_page - 1) // per_page
    
    # Build view model
    model = SearchResultsView(
        query=query,
        results=result_views,
        total_results=search_results.total_results,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        entity_types=[e.value for e in EntityType],
        selected_entity_types=[entity_type] if entity_type else [],
        execution_time_ms=execution_time,
        suggestions=getattr(search_results, 'suggestions', None)
    )
    
    return render_template('search/results.html', model=model)


@search_bp.route('/api/search')
def search_api():
    """
    Search API endpoint for AJAX requests.
    
    Returns:
        JSON response with search results
    """
    # Get query parameters
    query = request.args.get('q', '').strip()
    entity_type = request.args.get('entity_type', '')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    
    if not query:
        return jsonify({
            'error': 'Query parameter "q" is required'
        }), 400
    
    # Initialize services
    db = get_database_service()
    search_service = SearchService(db)
    
    # Build search query
    search_query = SearchQuery(
        query=query,
        limit=per_page,
        offset=(page - 1) * per_page,
        highlight=True,
        include_content=False
    )
    
    # Add entity type filter if specified
    if entity_type and entity_type in [e.value for e in EntityType]:
        search_query.filters = SearchFilter(
            entity_types=[EntityType(entity_type)]
        )
    
    # Execute search
    import time
    start_time = time.time()
    search_results = search_service.search(search_query)
    execution_time = (time.time() - start_time) * 1000
    
    # Convert results to JSON-serializable format
    results_data = []
    for result in search_results.results:
        url = _get_entity_url(result.entity_type, result.entity_id)
        
        result_data = {
            'entity_id': result.entity_id,
            'entity_type': result.entity_type.value,
            'title': result.title,
            'content': result.content,
            'relevance_score': result.relevance_score,
            'highlighted_title': getattr(result, 'highlighted_title', None),
            'highlighted_content': getattr(result, 'highlighted_content', None),
            'snippet': getattr(result, 'snippet', None),
            'metadata': result.metadata or {},
            'url': url
        }
        results_data.append(result_data)
    
    # Calculate pagination
    total_pages = (search_results.total_results + per_page - 1) // per_page
    
    return jsonify({
        'query': query,
        'results': results_data,
        'total_results': search_results.total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'execution_time_ms': execution_time,
        'suggestions': getattr(search_results, 'suggestions', None)
    })


def _get_entity_url(entity_type: str, entity_id: int) -> str:
    """Get the URL for an entity based on its type and ID."""
    entity_type_map = {
        'work_item': f'/work-item/{entity_id}',
        'task': f'/task/{entity_id}',
        'idea': f'/idea/{entity_id}',
        'document': f'/document/{entity_id}',
        'summary': f'/summary/{entity_id}',
        'evidence': f'/evidence/{entity_id}',
        'learning': f'/learning/{entity_id}',
        'session': f'/session/{entity_id}',
    }
    
    return entity_type_map.get(entity_type, '#')
