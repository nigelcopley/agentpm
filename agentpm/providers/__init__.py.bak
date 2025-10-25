"""
AIPM Providers - LLM Provider Integrations

This module provides integrations with various LLM providers.
Each provider handles agent file generation and context formatting
for their specific platform.

Supported Providers:
- Anthropic (Claude Code)
- OpenAI (GPT)
- Google (Gemini)
- Cursor (Cursor IDE)
"""

from typing import Dict, Type, Optional
from .base import BaseProvider

# Provider registry
PROVIDERS: Dict[str, str] = {
    'anthropic': 'anthropic.ClaudeProvider',
    'openai': 'openai.OpenAIProvider', 
    'google': 'google.GeminiProvider',
    'cursor': 'cursor.CursorProvider',
}

def get_provider(name: str) -> Optional[BaseProvider]:
    """
    Get a provider by name.
    
    Args:
        name: Provider name (e.g., 'anthropic', 'openai')
        
    Returns:
        Provider instance or None if not found
    """
    if name not in PROVIDERS:
        return None
    
    # Dynamic import to avoid circular dependencies
    module_path, class_name = PROVIDERS[name].rsplit('.', 1)
    module = __import__(f'agentpm.providers.{module_path}', fromlist=[class_name])
    provider_class = getattr(module, class_name)
    return provider_class()

def list_available_providers() -> list[str]:
    """List all available providers."""
    return list(PROVIDERS.keys())

def register_provider(name: str, provider_class: Type[BaseProvider]) -> None:
    """
    Register a new provider.
    
    Args:
        name: Provider name
        provider_class: Provider class
    """
    PROVIDERS[name] = f"{provider_class.__module__}.{provider_class.__name__}"

__all__ = [
    "BaseProvider",
    "get_provider",
    "list_available_providers", 
    "register_provider",
    "PROVIDERS"
]