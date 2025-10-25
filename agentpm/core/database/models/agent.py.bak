"""
Agent Model - Pydantic Domain Model

Type-safe agent model with validation.

Agents are AI assistants with specific roles and SOPs (Standard Operating Procedures).

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from ..enums import AgentTier


class Agent(BaseModel):
    """
    Agent domain model with Pydantic validation.

    Agents are AI assistants assigned to projects with specific roles
    and SOPs that define their behavior and capabilities.

    NEW (WI-009.3): Added agent_type, file_path, generated_at for file generation
    NEW (Migration 0011): Added tier, last_used_at, metadata

    Attributes:
        id: Database primary key (None for new agents)
        project_id: Parent project ID
        role: Agent role/name (e.g., 'aipm-database-developer')
        display_name: Human-readable name
        description: Agent purpose and responsibilities
        sop_content: Standard Operating Procedure (markdown)
        capabilities: JSON array of capabilities
        is_active: Whether agent is currently active
        agent_type: Base template type (e.g., 'implementer', 'tester')
        file_path: Generated file path (e.g., '.claude/agents/python-implementer.md')
        generated_at: When agent file was last generated
        tier: Agent tier (1=sub-agent, 2=specialist, 3=reserved) (Migration 0011)
        last_used_at: When agent was last assigned to a task (Migration 0011)
        metadata: Optional JSON metadata (Migration 0011)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )

    # Primary key
    id: Optional[int] = None

    # Relationships
    project_id: int = Field(..., gt=0)

    # Core fields
    role: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # SOP and capabilities
    sop_content: Optional[str] = None  # Markdown content
    capabilities: list[str] = Field(default_factory=list)

    # Status
    is_active: bool = True

    # NEW (WI-009.3): File generation tracking
    agent_type: Optional[str] = Field(
        default=None,
        description="Base template type (e.g., 'implementer', 'tester')"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Generated file path (e.g., '.claude/agents/python-implementer.md')"
    )
    generated_at: Optional[datetime] = Field(
        default=None,
        description="When agent file was last generated (for staleness detection)"
    )

    # NEW (Migration 0011): Agent tier and usage tracking
    tier: Optional[AgentTier] = None
    last_used_at: Optional[datetime] = None
    metadata: Optional[str] = Field(default='{}')

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def has_sop(self) -> bool:
        """Check if agent has SOP content"""
        return bool(self.sop_content and self.sop_content.strip())

    def has_capability(self, capability: str) -> bool:
        """Check if agent has specific capability"""
        return capability in self.capabilities

    # NEW (WI-009.3): Generation tracking methods
    def has_generated_file(self) -> bool:
        """Check if agent has a generated file"""
        return bool(self.file_path and self.generated_at)

    def is_stale(self, threshold_days: int = 7) -> bool:
        """
        Check if agent file is stale (needs regeneration)

        Args:
            threshold_days: Number of days before considering stale (default: 7)

        Returns:
            True if generated ≥threshold_days ago or never generated, False otherwise
        """
        if not self.generated_at:
            return True  # Never generated = stale

        age_days = (datetime.utcnow() - self.generated_at).days
        return age_days >= threshold_days