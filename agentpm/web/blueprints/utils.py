"""
Shared Blueprint Utilities for APM (Agent Project Manager) Web Application

Common utilities and helper functions used across all blueprints.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Tuple

from flask import request, jsonify, flash, redirect, url_for

from ...core.database.service import DatabaseService
from ...cli.utils.services import get_database_service as cli_get_database_service

logger = logging.getLogger(__name__)

def get_database_service() -> DatabaseService:
    """
    Get database service instance with robust path resolution.
    
    Uses the CLI service factory for consistency and caching.
    Falls back to direct instantiation if CLI service fails.
    """
    try:
        # Try to use the CLI service factory for consistency
        project_root = Path.cwd()
        return cli_get_database_service(project_root)
    except FileNotFoundError:
        # Fallback to direct instantiation for web context
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

def _is_htmx_request() -> bool:
    """Check if request is from HTMX."""
    return request.headers.get('HX-Request') == 'true'

def handle_error(error: Exception, error_message: str, redirect_url: Optional[str] = None) -> Any:
    """
    Universal error handling for blueprints.
    
    Args:
        error: The exception that occurred
        error_message: User-friendly error message
        redirect_url: Optional URL to redirect to (for form submissions)
    
    Returns:
        JSON response for AJAX requests, redirect for form submissions
    """
    logger.error(f"{error_message}: {error}")
    
    if _is_htmx_request() or request.is_json:
        return jsonify({'error': str(error)}), 500
    else:
        flash(f'{error_message}: {str(error)}', 'error')
        if redirect_url:
            return redirect(redirect_url)
        return redirect(url_for('dashboard.dashboard'))

def validate_required_fields(fields: Dict[str, str], form_data: Dict[str, Any]) -> Optional[str]:
    """
    Validate required form fields.
    
    Args:
        fields: Dictionary mapping field names to error messages
        form_data: Form data to validate
    
    Returns:
        Error message if validation fails, None if successful
    """
    for field_name, error_message in fields.items():
        value = form_data.get(field_name, '').strip()
        if not value:
            return error_message
    return None

def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standard success response for AJAX requests.
    
    Args:
        message: Success message
        data: Optional additional data
    
    Returns:
        Standardized success response dictionary
    """
    response = {
        'success': True,
        'message': message
    }
    if data:
        response.update(data)
    return response

def create_error_response(message: str, status_code: int = 400) -> tuple:
    """
    Create a standard error response for AJAX requests.
    
    Args:
        message: Error message
        status_code: HTTP status code
    
    Returns:
        Tuple of (jsonify response, status code)
    """
    return jsonify({'error': message}), status_code

def safe_get_entity(entity_method: Callable, db: DatabaseService, entity_id: int, entity_name: str) -> Optional[Any]:
    """
    Safely get an entity from the database with error handling.
    
    Args:
        entity_method: Database method to call
        db: Database service instance
        entity_id: ID of the entity to retrieve
        entity_name: Name of the entity type for error messages
    
    Returns:
        Entity if found, None if not found or error
    """
    try:
        entity = entity_method(db, entity_id)
        if not entity:
            logger.warning(f"{entity_name} {entity_id} not found")
        return entity
    except Exception as e:
        logger.error(f"Error fetching {entity_name} {entity_id}: {e}")
        return None

def calculate_progress_stats(items: List[Any], status_field: str = 'status') -> Dict[str, int]:
    """
    Calculate progress statistics for a list of items.
    
    Args:
        items: List of items to analyze
        status_field: Name of the status field on each item
    
    Returns:
        Dictionary with progress statistics
    """
    total = len(items)
    completed = sum(1 for item in items if getattr(item, status_field) and getattr(item, status_field).value == 'done')
    in_progress = sum(1 for item in items if getattr(item, status_field) and getattr(item, status_field).value in ['in_progress', 'active'])
    blocked = sum(1 for item in items if getattr(item, status_field) and getattr(item, status_field).value == 'blocked')
    pending = sum(1 for item in items if getattr(item, status_field) and getattr(item, status_field).value in ['pending', 'ready', 'draft'])
    
    progress_percentage = round((completed / total) * 100, 1) if total > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'blocked': blocked,
        'pending': pending,
        'progress_percentage': progress_percentage
    }
