"""
Principle-Based Agents System

Implements specialized agents that embody specific software engineering principles
and patterns for automated code quality enforcement.

Agents:
- SOLID Agent: Enforces SOLID principles (SRP, OCP, LSP, ISP, DIP)
- DRY Agent: Detects code duplication and suggests abstractions
- KISS Agent: Measures complexity and suggests simplifications
- And more...

Integration:
- Integrates with R1 quality gates
- Framework-specific adapters (Django, Python, React, etc.)
- Educational output with explanations
- Measurable metrics per principle
"""

from .base import PrincipleAgent, PrincipleViolation, AgentReport
from .solid_agent import SOLIDAgent
from .dry_agent import DRYAgent
from .kiss_agent import KISSAgent
from .registry import PrincipleAgentRegistry

__all__ = [
    'PrincipleAgent',
    'PrincipleViolation', 
    'AgentReport',
    'SOLIDAgent',
    'DRYAgent',
    'KISSAgent',
    'PrincipleAgentRegistry'
]
