"""
User detection utilities for CLI commands.

Provides consistent user detection across all CLI commands.
"""

import os
from typing import Optional


def get_current_user() -> str:
    """
    Get the current user identifier from environment variables.
    
    Detection order:
    1. USER environment variable (Unix/Linux/macOS)
    2. USERNAME environment variable (Windows)
    3. Fallback to 'system'
    
    Returns:
        Current user identifier string
    """
    return os.environ.get('USER', os.environ.get('USERNAME', 'system'))


def get_created_by_value(provided_value: Optional[str]) -> str:
    """
    Get the created_by value, using environment detection if not provided.
    
    Args:
        provided_value: User-provided created_by value (can be None)
        
    Returns:
        Final created_by value to use
    """
    if provided_value is not None:
        return provided_value
    return get_current_user()
