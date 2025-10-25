"""
Context System - Hierarchical Context Delivery

Provides AI agents with complete, scored, hierarchical context:
- Project context (tech stack, plugin facts, code amalgamations)
- Work item context (business requirements, design, scope)
- Task context (implementation details, acceptance criteria)

Main exports:
- ContextAssemblyService: <200ms context assembly orchestrator (WI-31)
- RefreshService: Context staleness detection & refresh (WI-31 Task #145)
- RefreshTriggers: Auto-refresh trigger detection
- ContextAssembler: Legacy assembler (Phase 1)
- ConfidenceScorer: Calculates quality scores
- SixWMerger: Merges 6W hierarchically
- ContextFreshness: Tracks staleness
- AgentSOPInjector: Loads agent SOPs from filesystem
- TemporalContextLoader: Loads session summaries for continuity
- ContextPayload: Complete context delivery model
"""

from .assembler import ContextAssembler
from .assembly_service import ContextAssemblyService, ContextAssemblyError
from .scoring import ConfidenceScorer, ConfidenceScore
from .merger import SixWMerger
from .freshness import ContextFreshness, FreshnessWarning
from .service import ContextService
from .sop_injector import AgentSOPInjector
from .temporal_loader import TemporalContextLoader
from .models import ContextPayload, AgentValidationError
from .refresh_service import RefreshService, StaleContext, RefreshReport
from .triggers import RefreshTriggers

__all__ = [
    # WI-31: Context Delivery Agent
    'ContextAssemblyService',
    'ContextAssemblyError',
    'ContextPayload',
    'AgentSOPInjector',
    'TemporalContextLoader',
    'AgentValidationError',
    # WI-31 Task #145: Context Refresh & Staleness
    'RefreshService',
    'StaleContext',
    'RefreshReport',
    'RefreshTriggers',
    # Phase 1: Existing components
    'ContextAssembler',
    'ConfidenceScorer',
    'ConfidenceScore',
    'SixWMerger',
    'ContextFreshness',
    'FreshnessWarning',
    'ContextService',
]
