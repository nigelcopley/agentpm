"""
Base Provider Interface

Defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, NamedTuple

from agentpm.core.database.models.agent import Agent

# Global registry for formatters
_FORMATTER_REGISTRY = {}


def register_formatter(provider_name: str, formatter_class):
    """Register a formatter for a provider."""
    _FORMATTER_REGISTRY[provider_name] = formatter_class


def get_formatter(provider_name: str):
    """Get registered formatter for a provider."""
    return _FORMATTER_REGISTRY.get(provider_name)


class TokenAllocation(NamedTuple):
    """Token allocation for context formatting."""
    total_tokens: int
    context_tokens: int
    response_tokens: int
    safety_buffer: int


class LLMContextFormatter(ABC):
    """Base class for LLM context formatters."""
    
    provider: str
    
    @abstractmethod
    def format_task(self, payload, *, token_allocation=None, **metadata) -> str:
        """Format task context for the LLM."""
        pass
    
    @abstractmethod
    def format_session(self, history: str, *, token_allocation=None, **metadata) -> str:
        """Format session context for the LLM."""
        pass


class LLMContextAdapter(ABC):
    """Base class for LLM context adapters."""
    
    provider: str
    
    @abstractmethod
    def plan_tokens(self, payload) -> TokenAllocation:
        """Plan token allocation for the context payload."""
        pass


class BaseProvider(ABC):
    """
    Base class for all LLM providers.
    
    Each provider handles:
    - Agent file generation for their platform
    - Context formatting for their LLM
    - Hook template generation
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'openai')."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass
    
    @abstractmethod
    def generate_agent_files(
        self, 
        agents: List[Agent], 
        output_dir: Path
    ) -> None:
        """
        Generate provider-specific agent files.
        
        Args:
            agents: List of agents to generate files for
            output_dir: Directory to write files to
        """
        pass
    
    @abstractmethod
    def format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context for this provider's LLM.
        
        Args:
            context: Context data to format
            
        Returns:
            Formatted context string
        """
        pass
    
    @abstractmethod
    def get_hook_templates(self) -> Dict[str, str]:
        """
        Get provider-specific hook templates.
        
        Returns:
            Dictionary mapping hook names to template content
        """
        pass
    
    def validate_agent(self, agent: Agent) -> List[str]:
        """
        Validate an agent for this provider.
        
        Args:
            agent: Agent to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation
        if not agent.role:
            errors.append("Agent role is required")
        
        if not agent.display_name:
            errors.append("Agent display name is required")
        
        if not agent.sop_content:
            errors.append("Agent SOP content is required")
        
        return errors
    
    def get_output_directory(self, project_path: Path) -> Path:
        """
        Get the output directory for this provider.
        
        Args:
            project_path: Project root path
            
        Returns:
            Provider-specific output directory
        """
        # Default implementation - override in subclasses
        return project_path / f".{self.name}"