"""
Agent Registry Validator

Validates agent assignments against the registry of available agents.
Supports multiple providers with dynamic path resolution.

This module provides centralized validation for agent assignments to ensure
tasks are only assigned to agents that exist in the system. Uses provider
detection to find agent files across different directory structures.

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

from .provider_detector import (
    detect_provider,
    get_agents_directory as get_provider_agents_directory,
    get_agent_paths,
    get_agent_names as get_provider_agent_names,
    Provider,
)


# Cache for agent registry (refreshes every 60 seconds)
_AGENT_CACHE: Optional[Set[str]] = None
_CACHE_TIMESTAMP: Optional[float] = None
CACHE_TTL_SECONDS = 60


def get_agents_directory() -> Optional[Path]:
    """
    Get the agents directory path dynamically from provider detection.

    Returns:
        Path to provider's agents directory, or None if not found

    Examples:
        >>> agents_dir = get_agents_directory()
        >>> agents_dir is not None
        True
    """
    # Use provider detection for dynamic path resolution
    return get_provider_agents_directory()


def _load_agent_registry() -> Set[str]:
    """
    Load all valid agent names from the registry.

    Uses provider detection to scan for agent files across all
    directory structures (flat and tiered).

    Returns:
        Set of valid agent names (without .md extension)
    """
    agents_dir = get_agents_directory()

    if not agents_dir or not agents_dir.exists():
        import warnings
        provider = detect_provider()
        warnings.warn(
            f"Agents directory not found for provider: {provider}",
            RuntimeWarning
        )
        return set()

    # Get all agent names using provider-aware scanner
    # Includes both flat structure (.claude/agents/*.md) and
    # subdirectories (.claude/agents/sub-agents/*.md)
    agent_names = get_provider_agent_names(include_subdirs=True)
    return set(agent_names)


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
        - provider: Detected provider
        - supports_agents: Whether provider supports agents

    Examples:
        >>> stats = get_registry_stats()
        >>> stats['total_agents'] > 0
        True
    """
    import time

    registry = _get_cached_registry()
    cache_age = (
        time.time() - _CACHE_TIMESTAMP
        if _CACHE_TIMESTAMP else 0
    )

    agents_dir = get_agents_directory()
    provider = detect_provider()

    return {
        "total_agents": len(registry),
        "cache_age_seconds": round(cache_age, 2),
        "agents_dir": str(agents_dir) if agents_dir else None,
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
        "provider": provider.value,
        "supports_agents": agents_dir is not None,
    }
