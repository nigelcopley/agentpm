"""
Sub-Agent Registry Validator

Validates sub-agent assignments against the registry of available agents
in .claude/agents/sub-agents/ directory.

This module provides centralized validation for agent assignments to ensure
tasks are only assigned to agents that exist in the system.

Usage:
    from agentpm.core.agents.registry_validator import validate_agent, get_all_agents

    # Validate single agent
    if validate_agent("code-implementer"):
        print("Agent exists")

    # Get all valid agents
    agents = get_all_agents()
    print(f"Found {len(agents)} agents")
"""

from pathlib import Path
from typing import List, Optional, Set
import functools


# Cache for agent registry (refreshes every 60 seconds)
_AGENT_CACHE: Optional[Set[str]] = None
_CACHE_TIMESTAMP: Optional[float] = None
CACHE_TTL_SECONDS = 60


def get_agents_directory() -> Path:
    """
    Get the sub-agents directory path.

    Returns:
        Path to .claude/agents/sub-agents/ directory
    """
    # Get project root (4 levels up from this file)
    # File is at: agentpm/core/agents/registry_validator.py
    # Root is at: aipm-v2/
    project_root = Path(__file__).parent.parent.parent.parent
    return project_root / ".claude" / "agents" / "sub-agents"


def _load_agent_registry() -> Set[str]:
    """
    Load all valid sub-agent names from the registry.

    Returns:
        Set of valid agent names (without .md extension)
    """
    agents_dir = get_agents_directory()

    if not agents_dir.exists():
        import warnings
        warnings.warn(
            f"Sub-agents directory not found: {agents_dir}",
            RuntimeWarning
        )
        return set()

    # Get all .md files in sub-agents directory
    agent_files = agents_dir.glob("*.md")
    return {f.stem for f in agent_files}


def _get_cached_registry() -> Set[str]:
    """
    Get cached agent registry or reload if cache expired.

    Returns:
        Set of valid agent names
    """
    global _AGENT_CACHE, _CACHE_TIMESTAMP

    import time
    current_time = time.time()

    # Check if cache needs refresh
    if (
        _AGENT_CACHE is None
        or _CACHE_TIMESTAMP is None
        or (current_time - _CACHE_TIMESTAMP) > CACHE_TTL_SECONDS
    ):
        _AGENT_CACHE = _load_agent_registry()
        _CACHE_TIMESTAMP = current_time

    return _AGENT_CACHE


def validate_agent(agent_name: str) -> bool:
    """
    Validate that a sub-agent exists in the registry.

    Args:
        agent_name: Name of sub-agent (without .md extension)

    Returns:
        True if agent exists, False otherwise

    Examples:
        >>> validate_agent("code-implementer")
        True
        >>> validate_agent("non-existent-agent")
        False
    """
    if not agent_name or not agent_name.strip():
        return False

    registry = _get_cached_registry()
    return agent_name in registry


def get_all_agents() -> List[str]:
    """
    Get list of all valid sub-agent names.

    Returns:
        Sorted list of valid agent names

    Examples:
        >>> agents = get_all_agents()
        >>> len(agents)
        36
        >>> "code-implementer" in agents
        True
    """
    registry = _get_cached_registry()
    return sorted(registry)


def get_agent_suggestions(partial_name: str, max_suggestions: int = 5) -> List[str]:
    """
    Get agent name suggestions based on partial match.

    Useful for providing helpful error messages when invalid agent names are provided.

    Args:
        partial_name: Partial agent name to match
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of suggested agent names

    Examples:
        >>> get_agent_suggestions("code")
        ['code-implementer']
        >>> get_agent_suggestions("test")
        ['test-implementer', 'test-runner']
    """
    if not partial_name:
        return []

    registry = _get_cached_registry()
    partial_lower = partial_name.lower()

    # Find agents that contain the partial name
    matches = [
        agent for agent in registry
        if partial_lower in agent.lower()
    ]

    return sorted(matches)[:max_suggestions]


def validate_agent_with_suggestions(agent_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate agent and provide helpful error message if invalid.

    Args:
        agent_name: Name of sub-agent to validate

    Returns:
        Tuple of (is_valid, error_message)
        - If valid: (True, None)
        - If invalid: (False, "error message with suggestions")

    Examples:
        >>> validate_agent_with_suggestions("code-implementer")
        (True, None)
        >>> valid, msg = validate_agent_with_suggestions("code-impl")
        >>> valid
        False
        >>> "code-implementer" in msg
        True
    """
    if validate_agent(agent_name):
        return (True, None)

    # Get suggestions
    suggestions = get_agent_suggestions(agent_name, max_suggestions=3)

    if suggestions:
        error_msg = (
            f"Agent '{agent_name}' not found. Did you mean: "
            f"{', '.join(suggestions)}?"
        )
    else:
        all_agents = get_all_agents()
        error_msg = (
            f"Agent '{agent_name}' not found. "
            f"Valid agents: {', '.join(all_agents[:5])}..."
            f" ({len(all_agents)} total)"
        )

    return (False, error_msg)


def refresh_cache() -> None:
    """
    Force refresh of the agent registry cache.

    Useful when agents are added/removed during runtime and immediate
    cache invalidation is needed.
    """
    global _AGENT_CACHE, _CACHE_TIMESTAMP
    _AGENT_CACHE = None
    _CACHE_TIMESTAMP = None


def get_registry_stats() -> dict:
    """
    Get statistics about the agent registry.

    Returns:
        Dictionary with registry statistics:
        - total_agents: Total number of registered agents
        - cache_age: Age of cache in seconds
        - agents_dir: Path to agents directory

    Examples:
        >>> stats = get_registry_stats()
        >>> stats['total_agents']
        36
    """
    import time

    registry = _get_cached_registry()
    cache_age = (
        time.time() - _CACHE_TIMESTAMP
        if _CACHE_TIMESTAMP else 0
    )

    return {
        "total_agents": len(registry),
        "cache_age_seconds": round(cache_age, 2),
        "agents_dir": str(get_agents_directory()),
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
    }
