"""
Agent Definitions - YAML Source of Truth

This module provides access to agent definitions stored in YAML files.
These definitions are the source of truth for all agents in the AIPM system.
"""

from pathlib import Path
from typing import List, Dict, Any
import yaml

# Path to definitions directory
DEFINITIONS_DIR = Path(__file__).parent

def load_agent_definitions(definition_file: str) -> List[Dict[str, Any]]:
    """
    Load agent definitions from a YAML file.
    
    Args:
        definition_file: Name of the YAML file (e.g., 'orchestrators.yaml')
        
    Returns:
        List of agent definitions
    """
    file_path = DEFINITIONS_DIR / definition_file
    if not file_path.exists():
        raise FileNotFoundError(f"Agent definitions file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Handle both single agent and multiple agents formats
    if isinstance(data, dict) and 'agents' in data:
        return data['agents']
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Invalid YAML format in {definition_file}")

def list_definition_files() -> List[str]:
    """List all available definition files."""
    return [f.name for f in DEFINITIONS_DIR.glob("*.yaml")]

__all__ = [
    "load_agent_definitions",
    "list_definition_files",
    "DEFINITIONS_DIR"
]
