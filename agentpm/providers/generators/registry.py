"""
Provider Generator Registry

Manages registration and discovery of provider-specific agent generators.
Supports extensible architecture for different LLM providers.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path

from .base import ProviderGenerator


# Registry of available provider generators
_PROVIDER_REGISTRY: Dict[str, Type[ProviderGenerator]] = {}


def register_provider_generator(provider_name: str, generator_class: Type[ProviderGenerator]) -> None:
    """
    Register a provider generator.
    
    Args:
        provider_name: Name of the provider (e.g., 'claude-code', 'cursor')
        generator_class: Generator class that implements ProviderGenerator
    """
    _PROVIDER_REGISTRY[provider_name.lower()] = generator_class


def get_provider_generator(provider_name: str) -> Optional[Type[ProviderGenerator]]:
    """
    Get a registered provider generator.
    
    Args:
        provider_name: Name of the provider
        
    Returns:
        Generator class if found, None otherwise
    """
    return _PROVIDER_REGISTRY.get(provider_name.lower())


def list_available_providers() -> List[str]:
    """
    List all registered provider names.
    
    Returns:
        List of provider names
    """
    return list(_PROVIDER_REGISTRY.keys())


def detect_current_provider(project_root: Path) -> str:
    """
    Auto-detect the current LLM provider based on project structure.
    
    Detection priority:
    1. AIPM_LLM_PROVIDER environment variable
    2. .claude/ directory (Claude Code)
    3. .cursor/ directory (Cursor)
    4. Default to claude-code
    
    Args:
        project_root: Path to project root
        
    Returns:
        Detected provider name
    """
    import os
    
    # Check environment variable first
    env_provider = os.getenv('AIPM_LLM_PROVIDER')
    if env_provider:
        return env_provider.lower()
    
    # Check for provider-specific directories
    if (project_root / '.claude').exists():
        return 'claude-code'
    
    if (project_root / '.cursor').exists():
        return 'cursor'
    
    # Default fallback
    return 'claude-code'


# Auto-register available generators
def _auto_register_generators():
    """Auto-register available provider generators."""
    try:
        from .anthropic.claude_code_generator import ClaudeCodeGenerator
        register_provider_generator('claude-code', ClaudeCodeGenerator)
    except ImportError:
        # Generator not available
        pass
    
    # Future providers can be registered here
    # try:
    #     from .cursor.cursor_generator import CursorGenerator
    #     register_provider_generator('cursor', CursorGenerator)
    # except ImportError:
    #     pass


# Initialize registry
_auto_register_generators()
