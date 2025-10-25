"""
Provider Generator Registry

Central registry for LLM provider generators with auto-detection capabilities.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Type, List

from .base import ProviderGenerator


# Global registry
_PROVIDER_GENERATORS: Dict[str, Type[ProviderGenerator]] = {}


def register_provider_generator(
    provider_name: str,
    generator_class: Type[ProviderGenerator]
) -> None:
    """
    Register a provider generator.

    Args:
        provider_name: Unique provider identifier (e.g., 'claude-code')
        generator_class: ProviderGenerator subclass
    """
    if not issubclass(generator_class, ProviderGenerator):
        raise TypeError(
            f"{generator_class} must be a subclass of ProviderGenerator"
        )

    _PROVIDER_GENERATORS[provider_name] = generator_class


def get_provider_generator(provider_name: str) -> Optional[ProviderGenerator]:
    """
    Get generator instance for provider.

    Args:
        provider_name: Provider identifier

    Returns:
        Generator instance or None if not found
    """
    generator_class = _PROVIDER_GENERATORS.get(provider_name)
    if generator_class:
        return generator_class()
    return None


def list_available_providers() -> List[str]:
    """
    List all registered providers.

    Returns:
        List of provider names
    """
    return list(_PROVIDER_GENERATORS.keys())


def detect_current_provider(
    project_path: Optional[Path] = None
) -> Optional[str]:
    """
    Auto-detect current LLM provider based on environment.

    Detection order:
    1. AIPM_LLM_PROVIDER environment variable
    2. .claude/ directory (Claude Code)
    3. .cursor/ directory (Cursor)
    4. Project settings in database
    5. Default to 'claude-code'

    Args:
        project_path: Optional project path to check for provider directories

    Returns:
        Provider name or None if cannot detect
    """
    # Check environment variable (highest priority)
    env_provider = os.environ.get('AIPM_LLM_PROVIDER')
    if env_provider and env_provider in _PROVIDER_GENERATORS:
        return env_provider

    # Check project path for provider directories
    if project_path:
        project_path = Path(project_path)

        # Check for .claude/ directory
        if (project_path / '.claude').is_dir():
            if 'claude-code' in _PROVIDER_GENERATORS:
                return 'claude-code'

        # Check for .cursor/ directory
        if (project_path / '.cursor').is_dir():
            if 'cursor' in _PROVIDER_GENERATORS:
                return 'cursor'

    # Check current working directory
    cwd = Path.cwd()

    if (cwd / '.claude').is_dir():
        if 'claude-code' in _PROVIDER_GENERATORS:
            return 'claude-code'

    if (cwd / '.cursor').is_dir():
        if 'cursor' in _PROVIDER_GENERATORS:
            return 'cursor'

    # Default to claude-code if available
    if 'claude-code' in _PROVIDER_GENERATORS:
        return 'claude-code'

    # No provider detected
    return None


def get_provider_info(provider_name: str) -> Optional[Dict[str, any]]:
    """
    Get metadata about a provider.

    Args:
        provider_name: Provider identifier

    Returns:
        Provider metadata or None
    """
    generator = get_provider_generator(provider_name)
    if generator:
        return generator.get_provider_metadata()
    return None


# Auto-register built-in providers on module import
def _register_builtin_providers():
    """Register built-in provider generators"""
    try:
        from agentpm.providers.generators.anthropic.claude_code_generator import (
            ClaudeCodeGenerator
        )
        register_provider_generator('claude-code', ClaudeCodeGenerator)
    except ImportError:
        pass  # Claude Code generator not available

    # Future providers can be registered here
    # try:
    #     from agentpm.core.plugins.domains.llms.generators.cursor.cursor_generator import (
    #         CursorGenerator
    #     )
    #     register_provider_generator('cursor', CursorGenerator)
    # except ImportError:
    #     pass


# Register on import
_register_builtin_providers()
