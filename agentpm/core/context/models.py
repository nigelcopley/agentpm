"""
Context Assembly Models - Type-Safe Context Delivery

Pydantic models for context assembly and delivery:
- ContextPayload: Complete assembled context for agent consumption
- AgentValidationError: Agent assignment validation failures

Pattern: Pydantic BaseModel with comprehensive validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..database.models.context import UnifiedSixW
from ..database.models.rule import Rule
from ..database.enums import ConfidenceBand


class ContextPayload(BaseModel):
    """
    Complete context payload for agent consumption.

    This is the primary output of ContextAssemblyService.assemble_task_context().
    Contains hierarchically merged 6W context, plugin intelligence, agent SOPs,
    session history, and quality assessment.

    All fields are guaranteed to be present (use empty structures for missing data).

    Attributes:
        project: Project entity data (dict)
        work_item: Work item entity data (None for project-level context)
        task: Task entity data (None for work-item/project-level context)
        merged_6w: Hierarchically merged 6W structure (Task > WorkItem > Project)
        plugin_facts: Plugin intelligence (empty dict if no plugins)
        amalgamations: Code amalgamation file paths (lazy loading)
        agent_sop: Agent Standard Operating Procedure (None if no agent)
        assigned_agent: Agent role name (None if no agent)
        temporal_context: Recent session summaries for continuity
        applicable_rules: All enabled rules applicable to this task (NEW)
        blocking_rules: BLOCK-level rules only (subset of applicable_rules) (NEW)
        rule_summary: Compressed text summary of rules for agent context (NEW)
        confidence_score: Overall confidence score (0.0-1.0)
        confidence_band: Confidence band (RED/YELLOW/GREEN)
        confidence_breakdown: Detailed factor breakdown
        warnings: Staleness, quality, missing data warnings
        assembled_at: Assembly timestamp
        assembly_duration_ms: Performance tracking
        cache_hit: Cache performance indicator
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,  # Allow UnifiedSixW dataclass
    )

    # Entity data
    project: Dict[str, Any]
    work_item: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None

    # Hierarchical 6W (merged Task > WorkItem > Project)
    merged_6w: UnifiedSixW

    # Plugin intelligence
    plugin_facts: Dict[str, Any] = Field(default_factory=dict)
    amalgamations: Dict[str, str] = Field(default_factory=dict)

    # Agent-specific context
    agent_sop: Optional[str] = None
    assigned_agent: Optional[str] = None

    # Temporal context (session history)
    temporal_context: List[Dict[str, Any]] = Field(default_factory=list)

    # Rules (NEW - Phase 1: WI-77 integration)
    applicable_rules: List[Rule] = Field(default_factory=list)
    blocking_rules: List[Rule] = Field(default_factory=list)
    rule_summary: str = ""

    # Quality assessment
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_band: ConfidenceBand
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

    # Metadata
    assembled_at: datetime
    assembly_duration_ms: float = Field(ge=0.0)
    cache_hit: bool = False


class AgentValidationError(Exception):
    """
    Raised when agent assignment is invalid.

    Scenarios:
    - Agent role not found in database
    - Agent is inactive
    - Agent role doesn't exist for project
    """
    pass
