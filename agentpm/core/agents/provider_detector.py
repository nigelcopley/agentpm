"""
Provider Detection Utility

Detects AI coding provider from filesystem and returns provider-specific paths.
Supports multiple providers with different directory structures.

Providers:
- Claude Code: .claude/agents/ (flat and tiered structure)
- Cursor: .cursor/ (rules only, no agents)
- Codex: .codex/agents/ (if exists)

Usage:
    from agentpm.core.agents.provider_detector import detect_provider, get_agent_paths

    # Detect current provider
    provider = detect_provider()
    print(f"Using provider: {provider}")

    # Get agent file paths for validation
    agent_paths = get_agent_paths()
    for path in agent_paths:
        print(f"Found agent: {path}")
"""

from pathlib import Path
from typing import List, Optional, Tuple
from enum import Enum


class Provider(str, Enum):
    """Supported AI coding providers."""
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    CODEX = "codex"
    UNKNOWN = "unknown"


def get_project_root() -> Path:
    """
    Get project root directory.

    Returns:
        Path to project root (4 levels up from this file)

    File location: agentpm/core/agents/provider_detector.py
    Project root: aipm-v2/
    """
    return Path(__file__).parent.parent.parent.parent


def detect_provider(project_root: Optional[Path] = None) -> Provider:
    """
    Detect AI coding provider from filesystem.

    Checks for provider-specific directories in order of precedence:
    1. .claude/ → Claude Code
    2. .codex/ → Codex
    3. .cursor/ → Cursor (fallback)

    Args:
        project_root: Optional project root path (defaults to auto-detected)

    Returns:
        Provider enum value

    Examples:
        >>> provider = detect_provider()
        >>> provider == Provider.CLAUDE_CODE
        True
    """
    if project_root is None:
        project_root = get_project_root()

    # Check for Claude Code
    claude_dir = project_root / ".claude"
    if claude_dir.exists() and claude_dir.is_dir():
        return Provider.CLAUDE_CODE

    # Check for Codex
    codex_dir = project_root / ".codex"
    if codex_dir.exists() and codex_dir.is_dir():
        return Provider.CODEX

    # Check for Cursor
    cursor_dir = project_root / ".cursor"
    if cursor_dir.exists() and cursor_dir.is_dir():
        return Provider.CURSOR

    return Provider.UNKNOWN


def get_provider_base_path(
    provider: Optional[Provider] = None,
    project_root: Optional[Path] = None
) -> Optional[Path]:
    """
    Get base path for provider files.

    Args:
        provider: Optional provider (auto-detected if not provided)
        project_root: Optional project root (auto-detected if not provided)

    Returns:
        Path to provider's base directory, or None if not found

    Examples:
        >>> path = get_provider_base_path(Provider.CLAUDE_CODE)
        >>> path.name
        '.claude'
    """
    if project_root is None:
        project_root = get_project_root()

    if provider is None:
        provider = detect_provider(project_root)

    provider_dirs = {
        Provider.CLAUDE_CODE: ".claude",
        Provider.CODEX: ".codex",
        Provider.CURSOR: ".cursor",
    }

    dir_name = provider_dirs.get(provider)
    if not dir_name:
        return None

    provider_path = project_root / dir_name
    return provider_path if provider_path.exists() else None


def get_agents_directory(
    provider: Optional[Provider] = None,
    project_root: Optional[Path] = None
) -> Optional[Path]:
    """
    Get agents directory for provider.

    Handles provider-specific agent directory structures:
    - Claude Code: .claude/agents/ (flat and tiered)
    - Codex: .codex/agents/
    - Cursor: None (no agent files)

    Args:
        provider: Optional provider (auto-detected if not provided)
        project_root: Optional project root (auto-detected if not provided)

    Returns:
        Path to agents directory, or None if provider doesn't support agents

    Examples:
        >>> agents_dir = get_agents_directory(Provider.CLAUDE_CODE)
        >>> agents_dir.name
        'agents'
    """
    if project_root is None:
        project_root = get_project_root()

    if provider is None:
        provider = detect_provider(project_root)

    # Cursor doesn't have agent files, only rules
    if provider == Provider.CURSOR:
        return None

    base_path = get_provider_base_path(provider, project_root)
    if not base_path:
        return None

    agents_dir = base_path / "agents"
    return agents_dir if agents_dir.exists() else None


def get_agent_paths(
    provider: Optional[Provider] = None,
    project_root: Optional[Path] = None,
    include_subdirs: bool = True
) -> List[Path]:
    """
    Get all agent file paths for provider.

    Scans agent directory and optionally subdirectories for .md files.
    Supports both flat and tiered directory structures.

    Args:
        provider: Optional provider (auto-detected if not provided)
        project_root: Optional project root (auto-detected if not provided)
        include_subdirs: Whether to include subdirectories (default: True)

    Returns:
        List of paths to agent .md files

    Examples:
        >>> paths = get_agent_paths(Provider.CLAUDE_CODE)
        >>> len(paths) > 0
        True
        >>> all(p.suffix == '.md' for p in paths)
        True
    """
    if project_root is None:
        project_root = get_project_root()

    if provider is None:
        provider = detect_provider(project_root)

    agents_dir = get_agents_directory(provider, project_root)
    if not agents_dir:
        return []

    # Scan for .md files
    if include_subdirs:
        # Recursive glob: **/*.md (flat + subdirectories)
        agent_files = list(agents_dir.glob("**/*.md"))
    else:
        # Flat glob: *.md (only top-level)
        agent_files = list(agents_dir.glob("*.md"))

    return sorted(agent_files)


def get_agent_names(
    provider: Optional[Provider] = None,
    project_root: Optional[Path] = None,
    include_subdirs: bool = True
) -> List[str]:
    """
    Get all agent names (stems without .md extension).

    Args:
        provider: Optional provider (auto-detected if not provided)
        project_root: Optional project root (auto-detected if not provided)
        include_subdirs: Whether to include subdirectories (default: True)

    Returns:
        List of agent names (file stems)

    Examples:
        >>> names = get_agent_names(Provider.CLAUDE_CODE)
        >>> 'code-implementer' in names
        True
    """
    agent_paths = get_agent_paths(provider, project_root, include_subdirs)
    return [path.stem for path in agent_paths]


def get_provider_info(
    provider: Optional[Provider] = None,
    project_root: Optional[Path] = None
) -> dict:
    """
    Get comprehensive provider information.

    Args:
        provider: Optional provider (auto-detected if not provided)
        project_root: Optional project root (auto-detected if not provided)

    Returns:
        Dictionary with provider details:
        - provider: Provider enum value
        - base_path: Provider base directory
        - agents_dir: Agents directory (if exists)
        - agent_count: Number of agent files
        - supports_agents: Whether provider supports agents

    Examples:
        >>> info = get_provider_info()
        >>> info['provider'] == Provider.CLAUDE_CODE
        True
        >>> info['supports_agents']
        True
    """
    if project_root is None:
        project_root = get_project_root()

    if provider is None:
        provider = detect_provider(project_root)

    base_path = get_provider_base_path(provider, project_root)
    agents_dir = get_agents_directory(provider, project_root)
    agent_paths = get_agent_paths(provider, project_root)

    return {
        "provider": provider,
        "base_path": str(base_path) if base_path else None,
        "agents_dir": str(agents_dir) if agents_dir else None,
        "agent_count": len(agent_paths),
        "supports_agents": agents_dir is not None,
    }
