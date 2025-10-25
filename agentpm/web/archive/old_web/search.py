"""
Search Blueprint - Search Functionality

Handles:
- /search - Search results page
- /api/search - Search API endpoint
"""

from flask import Blueprint, render_template, request, jsonify
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ...core.search.service import SearchService
from ...core.search.models import SearchQuery, SearchFilter
from ...core.database.enums import EntityType

# Import helper functions from app
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
    """Search results page."""
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
        # Build URL based on entity type
        url = ""
        if hasattr(result, 'entity_type'):
            if result.entity_type == 'work_item':
                url = f"/work-items/{result.entity_id}"
            elif result.entity_type == 'task':
                url = f"/tasks/{result.entity_id}"
            elif result.entity_type == 'idea':
                url = f"/ideas/{result.entity_id}"
            elif result.entity_type == 'project':
                url = f"/projects/{result.entity_id}"
            elif result.entity_type == 'agent':
                url = f"/agents/{result.entity_id}"
            elif result.entity_type == 'rule':
                url = f"/rules/{result.entity_id}"
        
        result_view = SearchResultView(
            entity_id=getattr(result, 'entity_id', getattr(result, 'id', 0)),
            entity_type=getattr(result, 'entity_type', 'unknown'),
            title=getattr(result, 'title', ''),
            content=getattr(result, 'content', ''),
            relevance_score=getattr(result, 'relevance_score', getattr(result, 'score', 0.0)),
            highlighted_title=getattr(result, 'highlighted_title', None),
            highlighted_content=getattr(result, 'highlighted_content', None),
            snippet=getattr(result, 'snippet', None),
            metadata=getattr(result, 'metadata', {}),
            url=url
        )
        result_views.append(result_view)
    
    # Calculate pagination
    total_results = getattr(search_results, 'total_results', len(result_views))
    total_pages = (total_results + per_page - 1) // per_page
    
    # Create model
    model = SearchResultsView(
        query=query,
        results=result_views,
        total_results=total_results,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        entity_types=[e.value for e in EntityType],
        selected_entity_types=[entity_type] if entity_type else [],
        execution_time_ms=execution_time
    )
    
    return render_template('search/results.html', model=model)


@search_bp.route('/api/search')
def search_api():
    """Search API endpoint."""
    query = request.args.get('q', '')
    entity_type = request.args.get('type', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    db = get_database_service()
    search_service = SearchService(db)
    
    search_query = SearchQuery(
        query=query,
        entity_types=[entity_type] if entity_type else None,
        limit=limit
    )
    
    search_results = search_service.search(search_query)
    
    # Handle different result formats
    if hasattr(search_results, 'results'):
        results = search_results.results
        total_results = search_results.total_results
    else:
        results = []
        total_results = 0
    
    return jsonify({
        'query': query,
        'total_results': total_results,
        'results': [
            {
                'id': getattr(result, 'id', None),
                'type': getattr(result, 'entity_type', None),
                'title': getattr(result, 'title', ''),
                'description': getattr(result, 'description', ''),
                'score': getattr(result, 'score', 0.0),
                'url': getattr(result, 'url', '')
            }
            for result in results
        ]
    })
