"""
Pagination utilities for APM (Agent Project Manager) Web Application

Provides reusable pagination functionality for list views including:
- Pagination calculation
- URL parameter handling
- Pagination data models
"""

from typing import List, Any, Optional, Dict
from urllib.parse import urlencode
import math


class PaginationInfo:
    """Pagination information container."""
    
    def __init__(self, 
                 page: int = 1, 
                 per_page: int = 20, 
                 total: int = 0,
                 base_url: str = '',
                 query_params: Optional[Dict[str, Any]] = None):
        """
        Initialize pagination info.
        
        Args:
            page: Current page number (1-based)
            per_page: Number of items per page
            total: Total number of items
            base_url: Base URL for pagination links
            query_params: Additional query parameters to preserve
        """
        self.page = max(1, page)
        self.per_page = max(1, min(per_page, 100))  # Cap at 100
        self.total = max(0, total)
        self.base_url = base_url
        self.query_params = query_params or {}
        
        # Calculate derived values
        self.total_pages = math.ceil(self.total / self.per_page) if self.total > 0 else 1
        self.offset = (self.page - 1) * self.per_page
        self.start_item = self.offset + 1 if self.total > 0 else 0
        self.end_item = min(self.offset + self.per_page, self.total)
        
        # Ensure page is within valid range
        if self.page > self.total_pages:
            self.page = self.total_pages
            self.offset = (self.page - 1) * self.per_page
            self.start_item = self.offset + 1 if self.total > 0 else 0
            self.end_item = min(self.offset + self.per_page, self.total)
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    @property
    def prev_page(self) -> Optional[int]:
        """Get previous page number."""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_page(self) -> Optional[int]:
        """Get next page number."""
        return self.page + 1 if self.has_next else None
    
    def get_page_url(self, page: int) -> str:
        """Generate URL for a specific page."""
        params = self.query_params.copy()
        params['page'] = page
        params['per_page'] = self.per_page
        
        # Remove empty values
        params = {k: v for k, v in params.items() if v is not None and v != ''}
        
        query_string = urlencode(params)
        return f"{self.base_url}?{query_string}" if query_string else self.base_url
    
    @property
    def prev_url(self) -> Optional[str]:
        """Get URL for previous page."""
        return self.get_page_url(self.prev_page) if self.has_prev else None
    
    @property
    def next_url(self) -> Optional[str]:
        """Get URL for next page."""
        return self.get_page_url(self.next_page) if self.has_next else None
    
    def get_page_numbers(self, max_pages: int = 7) -> List[Optional[int]]:
        """
        Get list of page numbers to display in pagination.
        
        Args:
            max_pages: Maximum number of page numbers to show
            
        Returns:
            List of page numbers, with None for ellipsis
        """
        if self.total_pages <= max_pages:
            return list(range(1, self.total_pages + 1))
        
        # Calculate range around current page
        half = max_pages // 2
        start = max(1, self.page - half)
        end = min(self.total_pages, start + max_pages - 1)
        
        # Adjust if we're near the end
        if end - start < max_pages - 1:
            start = max(1, end - max_pages + 1)
        
        pages = list(range(start, end + 1))
        
        # Add ellipsis if needed
        if start > 1:
            if start > 2:
                pages.insert(0, None)  # Ellipsis
            pages.insert(0, 1)
        
        if end < self.total_pages:
            if end < self.total_pages - 1:
                pages.append(None)  # Ellipsis
            pages.append(self.total_pages)
        
        return pages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering."""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total': self.total,
            'total_pages': self.total_pages,
            'start_item': self.start_item,
            'end_item': self.end_item,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'prev_page': self.prev_page,
            'next_page': self.next_page,
            'prev_url': self.prev_url,
            'next_url': self.next_url,
            'page_numbers': self.get_page_numbers(),
            'base_url': self.base_url,
            'query_params': self.query_params
        }


def paginate_items(items: List[Any], 
                   page: int = 1, 
                   per_page: int = 20,
                   base_url: str = '',
                   query_params: Optional[Dict[str, Any]] = None) -> tuple[List[Any], PaginationInfo]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        per_page: Number of items per page
        base_url: Base URL for pagination links
        query_params: Additional query parameters to preserve
        
    Returns:
        Tuple of (paginated_items, pagination_info)
    """
    total = len(items)
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total=total,
        base_url=base_url,
        query_params=query_params
    )
    
    # Get paginated items
    paginated_items = items[pagination.offset:pagination.offset + pagination.per_page]
    
    return paginated_items, pagination


def get_pagination_from_request(request, 
                               default_per_page: int = 20,
                               max_per_page: int = 100) -> tuple[int, int]:
    """
    Extract pagination parameters from Flask request.
    
    Args:
        request: Flask request object
        default_per_page: Default items per page
        max_per_page: Maximum items per page
        
    Returns:
        Tuple of (page, per_page)
    """
    try:
        page = int(request.args.get('page', 1))
        page = max(1, page)
    except (ValueError, TypeError):
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', default_per_page))
        per_page = max(1, min(per_page, max_per_page))
    except (ValueError, TypeError):
        per_page = default_per_page
    
    return page, per_page


def get_query_params_from_request(request, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract query parameters from Flask request, excluding pagination params.
    
    Args:
        request: Flask request object
        exclude: Additional parameters to exclude
        
    Returns:
        Dictionary of query parameters
    """
    exclude = exclude or []
    exclude.extend(['page', 'per_page'])
    
    params = {}
    for key, value in request.args.items():
        if key not in exclude and value:
            params[key] = value
    
    return params
