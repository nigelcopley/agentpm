"""
Agent Templates - Legacy Template System

This module provides access to legacy agent templates.
These templates are deprecated in favor of the new YAML-based system.
"""

from pathlib import Path
from typing import List

# Path to templates directory
TEMPLATES_DIR = Path(__file__).parent

def list_template_files() -> List[str]:
    """List all available template files."""
    return [f.name for f in TEMPLATES_DIR.glob("*.md")]

def get_template_path(template_name: str) -> Path:
    """Get the path to a specific template file."""
    return TEMPLATES_DIR / template_name

__all__ = [
    "list_template_files",
    "get_template_path",
    "TEMPLATES_DIR"
]