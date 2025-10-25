"""
Task type to agent mapping utilities.

This module provides utilities for mapping task types to appropriate agents,
following APM (Agent Project Manager)'s agent specialization patterns.
"""

from typing import Dict, Optional
from ..enums.types import TaskType


def get_agent_for_task_type(task_type: TaskType) -> str:
    """
    Get the appropriate agent for a given task type.
    
    Args:
        task_type: The task type to get an agent for
        
    Returns:
        The agent role name for the task type
        
    Raises:
        ValueError: If task_type is not supported
    """
    mapping = _get_task_type_to_agent_mapping()
    
    if task_type not in mapping:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    return mapping[task_type]


def get_all_supported_task_types() -> list[TaskType]:
    """
    Get all task types that have agent mappings.
    
    Returns:
        List of all supported TaskType values
    """
    return list(_get_task_type_to_agent_mapping().keys())


def get_all_agent_roles() -> list[str]:
    """
    Get all unique agent roles used in the mapping.
    
    Returns:
        List of unique agent role names
    """
    mapping = _get_task_type_to_agent_mapping()
    return list(set(mapping.values()))


def get_task_types_for_agent(agent_role: str) -> list[TaskType]:
    """
    Get all task types that map to a specific agent role.
    
    Args:
        agent_role: The agent role to find task types for
        
    Returns:
        List of TaskType values that map to the agent role
    """
    mapping = _get_task_type_to_agent_mapping()
    return [task_type for task_type, role in mapping.items() if role == agent_role]


def _get_task_type_to_agent_mapping() -> Dict[TaskType, str]:
    """
    Get the complete task type to agent mapping.
    
    This is the authoritative mapping that defines which agent
    should handle each type of task.
    
    Returns:
        Dictionary mapping TaskType to agent role name
    """
    return {
        # Design and Planning
        TaskType.DESIGN: "ac-writer",              # Design/planning → acceptance criteria writer
        TaskType.PLANNING: "ac-writer",            # Planning → acceptance criteria writer
        TaskType.MEETING: "ac-writer",             # Meetings → acceptance criteria writer
        
        # Implementation and Development
        TaskType.IMPLEMENTATION: "code-implementer",  # Code implementation → code implementer
        TaskType.BUGFIX: "code-implementer",       # Bug fixes → code implementer
        TaskType.REFACTORING: "code-implementer",  # Code improvement → code implementer
        TaskType.MAINTENANCE: "code-implementer",  # Maintenance → code implementer
        TaskType.OPTIMIZATION: "code-implementer", # Optimization → code implementer
        TaskType.INTEGRATION: "code-implementer",  # Integration → code implementer
        TaskType.SIMPLE: "code-implementer",       # Simple tasks → code implementer (default)
        TaskType.OTHER: "code-implementer",        # Other tasks → code implementer (default)
        
        # Testing and Quality
        TaskType.TESTING: "test-implementer",      # Write tests → test implementer
        TaskType.REVIEW: "quality-gatekeeper",     # Code review → quality gatekeeper
        
        # Research and Analysis
        TaskType.ANALYSIS: "intent-triage",        # Analysis/research → intent triage
        TaskType.RESEARCH: "intent-triage",        # Research/spike → intent triage
        TaskType.DEPENDENCY: "intent-triage",      # Dependencies → intent triage
        TaskType.BLOCKER: "intent-triage",         # Blockers → intent triage
        
        # Documentation and Training
        TaskType.DOCUMENTATION: "doc-toucher",     # Documentation → doc toucher
        TaskType.TRAINING: "doc-toucher",          # Training → doc toucher
        
        # Deployment and Operations
        TaskType.DEPLOYMENT: "code-implementer", # Deployment → code implementer
    }


def validate_task_agent_mapping() -> bool:
    """
    Validate that all TaskType enum values have agent mappings.
    
    This is useful for ensuring the mapping stays up-to-date when
    new TaskType values are added.
    
    Returns:
        True if all TaskType values are mapped, False otherwise
    """
    mapping = _get_task_type_to_agent_mapping()
    all_task_types = set(TaskType)
    mapped_task_types = set(mapping.keys())
    
    return all_task_types == mapped_task_types


def get_mapping_coverage_report() -> Dict[str, any]:
    """
    Get a report on the coverage of the task type to agent mapping.
    
    Returns:
        Dictionary containing coverage statistics and missing mappings
    """
    mapping = _get_task_type_to_agent_mapping()
    all_task_types = set(TaskType)
    mapped_task_types = set(mapping.keys())
    
    missing_types = all_task_types - mapped_task_types
    extra_types = mapped_task_types - all_task_types
    
    return {
        "total_task_types": len(all_task_types),
        "mapped_task_types": len(mapped_task_types),
        "coverage_percentage": (len(mapped_task_types) / len(all_task_types)) * 100,
        "missing_types": list(missing_types),
        "extra_types": list(extra_types),
        "is_complete": len(missing_types) == 0 and len(extra_types) == 0,
        "agent_distribution": {
            agent: len(get_task_types_for_agent(agent))
            for agent in get_all_agent_roles()
        }
    }
