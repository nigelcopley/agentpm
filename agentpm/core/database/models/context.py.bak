"""
Context Model - Pydantic Domain Model

Type-safe context model with validation.

Unified context system supporting:
- Resource files (SOPs, code, specifications, documentation)
- Entity contexts (project_context, work_item_context, task_context)
- UnifiedSixW structure for entity contexts
- Integrated confidence scoring

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from ..enums import ContextType, ResourceType, EntityType, ConfidenceBand


@dataclass
class UnifiedSixW:
    """
    Unified 6W framework structure for entity contexts.

    CONSISTENT STRUCTURE across all levels (Project/WorkItem/Task).
    Same fields, different GRANULARITY:

    WHO - People and roles:
        Project level: @cto, @team, @stakeholders
        WorkItem level: @team, @tech-lead, @designer
        Task level: @alice, @bob, @agent-python-dev

    WHAT - Requirements:
        Project level: System requirements, business goals
        WorkItem level: Component requirements, feature scope
        Task level: Function requirements, specific acceptance criteria

    WHERE - Technical context:
        Project level: Infrastructure, all services, cloud platform
        WorkItem level: Specific services, microservices, modules
        Task level: Files, functions, specific code locations

    WHEN - Timeline:
        Project level: Quarters, major milestones
        WorkItem level: Weeks, sprint goals
        Task level: Days, hours, immediate dependencies

    WHY - Value proposition:
        Project level: Business value, market impact
        WorkItem level: Feature value, user benefit
        Task level: Technical necessity, debt reduction

    HOW - Approach:
        Project level: Architecture, system patterns
        WorkItem level: Design patterns, component patterns
        Task level: Implementation details, algorithms
    """
    # WHO: People and roles (scales: @cto → @team → @alice)
    end_users: list[str] = None
    implementers: list[str] = None
    reviewers: list[str] = None

    # WHAT: Requirements (scales: system → component → function)
    functional_requirements: list[str] = None
    technical_constraints: list[str] = None
    acceptance_criteria: list[str] = None

    # WHERE: Technical context (scales: infrastructure → services → files)
    affected_services: list[str] = None
    repositories: list[str] = None
    deployment_targets: list[str] = None

    # WHEN: Timeline (scales: quarters → weeks → days)
    deadline: Optional[datetime] = None
    dependencies_timeline: list[str] = None  # List of dependency descriptions

    # WHY: Value proposition (scales: business → feature → technical)
    business_value: Optional[str] = None
    risk_if_delayed: Optional[str] = None

    # HOW: Approach (scales: architecture → patterns → implementation)
    suggested_approach: Optional[str] = None
    existing_patterns: list[str] = None

    def __post_init__(self):
        """Initialize list fields to empty lists if None"""
        if self.end_users is None:
            self.end_users = []
        if self.implementers is None:
            self.implementers = []
        if self.reviewers is None:
            self.reviewers = []
        if self.functional_requirements is None:
            self.functional_requirements = []
        if self.technical_constraints is None:
            self.technical_constraints = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.affected_services is None:
            self.affected_services = []
        if self.repositories is None:
            self.repositories = []
        if self.deployment_targets is None:
            self.deployment_targets = []
        if self.dependencies_timeline is None:
            self.dependencies_timeline = []
        if self.existing_patterns is None:
            self.existing_patterns = []

    @property
    def who(self) -> Optional[str]:
        """WHO dimension - combines implementers, reviewers, and end_users."""
        parts = []
        if self.implementers:
            parts.append(f"Implementers: {', '.join(self.implementers)}")
        if self.reviewers:
            parts.append(f"Reviewers: {', '.join(self.reviewers)}")
        if self.end_users:
            parts.append(f"End Users: {', '.join(self.end_users)}")
        return '; '.join(parts) if parts else None

    @property
    def what(self) -> Optional[str]:
        """WHAT dimension - functional requirements and acceptance criteria."""
        parts = []
        if self.functional_requirements:
            parts.extend(self.functional_requirements)
        if self.acceptance_criteria:
            parts.extend([f"AC: {ac}" for ac in self.acceptance_criteria])
        return '; '.join(parts) if parts else None

    @property
    def where(self) -> Optional[str]:
        """WHERE dimension - affected services and repositories."""
        parts = []
        if self.affected_services:
            parts.append(f"Services: {', '.join(self.affected_services)}")
        if self.repositories:
            parts.append(f"Repos: {', '.join(self.repositories)}")
        if self.deployment_targets:
            parts.append(f"Targets: {', '.join(self.deployment_targets)}")
        return '; '.join(parts) if parts else None

    @property
    def when(self) -> Optional[str]:
        """WHEN dimension - deadline and dependencies timeline."""
        parts = []
        if self.deadline:
            parts.append(f"Deadline: {self.deadline.strftime('%Y-%m-%d')}")
        if self.dependencies_timeline:
            parts.append(f"Dependencies: {'; '.join(self.dependencies_timeline)}")
        return '; '.join(parts) if parts else None

    @property
    def why(self) -> Optional[str]:
        """WHY dimension - business value and risk."""
        parts = []
        if self.business_value:
            parts.append(self.business_value)
        if self.risk_if_delayed:
            parts.append(f"Risk: {self.risk_if_delayed}")
        return '; '.join(parts) if parts else None

    @property
    def how(self) -> Optional[str]:
        """HOW dimension - suggested approach and existing patterns."""
        parts = []
        if self.suggested_approach:
            parts.append(self.suggested_approach)
        if self.existing_patterns:
            parts.append(f"Patterns: {', '.join(self.existing_patterns)}")
        return '; '.join(parts) if parts else None


class Context(BaseModel):
    """
    Context domain model with Pydantic validation.

    Unified context system handles two types:

    1. **Resource Files**: SOPs, code, specifications, documentation
       - Has file_path, file_hash, resource_type
       - No entity relationship

    2. **Entity Contexts**: project_context, work_item_context, task_context
       - Has entity_type + entity_id (polymorphic relationship)
       - Has UnifiedSixW structure
       - Has confidence scoring

    Attributes:
        id: Database primary key
        project_id: Parent project ID
        context_type: Type of context (resource_file or entity_context)

        # For resource files:
        file_path: Path to resource file
        file_hash: SHA256 hash for change detection
        resource_type: Type of resource (sop, code, specification, documentation)

        # For entity contexts:
        entity_type: Type of linked entity (project, work_item, task)
        entity_id: ID of linked entity
        six_w: UnifiedSixW structure (who/what/when/where/why/how)

        # Confidence scoring (for entity contexts):
        confidence_score: Score 0.0-1.0
        confidence_band: RED/YELLOW/GREEN
        confidence_factors: JSON breakdown of scoring factors

        # Timestamps:
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

    # Context type
    context_type: ContextType

    # For resource files
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    resource_type: Optional[ResourceType] = None

    # For entity contexts (polymorphic relationship)
    entity_type: Optional[EntityType] = None
    entity_id: Optional[int] = Field(default=None, gt=0)

    # 6W structure (for entity contexts)
    six_w: Optional[UnifiedSixW] = None

    # Confidence scoring (for entity contexts)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence_band: Optional[ConfidenceBand] = None
    confidence_factors: Optional[dict] = None

    # NEW: Rich context data storage (for new context types)
    context_data: Optional[dict] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_resource_file(self) -> bool:
        """Check if this is a resource file context"""
        return self.context_type == ContextType.RESOURCE_FILE

    def is_entity_context(self) -> bool:
        """Check if this is an entity context"""
        return self.context_type in (
            ContextType.PROJECT_CONTEXT,
            ContextType.WORK_ITEM_CONTEXT,
            ContextType.TASK_CONTEXT,
            # NEW: Rich context types
            ContextType.BUSINESS_PILLARS_CONTEXT,
            ContextType.MARKET_RESEARCH_CONTEXT,
            ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
            ContextType.QUALITY_GATES_CONTEXT,
            ContextType.STAKEHOLDER_CONTEXT,
            ContextType.TECHNICAL_CONTEXT,
            ContextType.IMPLEMENTATION_CONTEXT,
            # NEW: Ideas integration
            ContextType.IDEA_CONTEXT,
            ContextType.IDEA_TO_WORK_ITEM_MAPPING
        )

    def has_high_confidence(self) -> bool:
        """Check if context has high confidence (GREEN band)"""
        return self.confidence_band == ConfidenceBand.GREEN

    def calculate_confidence_band(self) -> ConfidenceBand:
        """Calculate confidence band from score"""
        if self.confidence_score is None:
            return ConfidenceBand.RED
        return ConfidenceBand.from_score(self.confidence_score)

    # Convenience properties for 6W access (makes display code cleaner)
    @property
    def who(self) -> Optional[str]:
        """WHO dimension - combines implementers and reviewers"""
        if not self.six_w:
            return None
        parts = []
        if self.six_w.implementers:
            parts.append(f"Implementers: {', '.join(self.six_w.implementers)}")
        if self.six_w.reviewers:
            parts.append(f"Reviewers: {', '.join(self.six_w.reviewers)}")
        return ' | '.join(parts) if parts else None

    @property
    def what(self) -> Optional[str]:
        """WHAT dimension - functional requirements"""
        if not self.six_w or not self.six_w.functional_requirements:
            return None
        return '; '.join(self.six_w.functional_requirements)

    @property
    def where(self) -> Optional[str]:
        """WHERE dimension - affected services"""
        if not self.six_w or not self.six_w.affected_services:
            return None
        return ', '.join(self.six_w.affected_services)

    @property
    def when_context(self) -> Optional[str]:
        """WHEN dimension - timeline"""
        if not self.six_w:
            return None
        parts = []
        if self.six_w.deadline:
            parts.append(f"Deadline: {self.six_w.deadline}")
        if self.six_w.dependencies_timeline:
            parts.append(f"Dependencies: {', '.join(self.six_w.dependencies_timeline)}")
        return ' | '.join(parts) if parts else None

    @property
    def why(self) -> Optional[str]:
        """WHY dimension - business value"""
        if not self.six_w:
            return None
        return self.six_w.business_value

    @property
    def how(self) -> Optional[str]:
        """HOW dimension - approach and patterns"""
        if not self.six_w:
            return None
        parts = []
        if self.six_w.suggested_approach:
            parts.append(f"Approach: {self.six_w.suggested_approach}")
        if self.six_w.existing_patterns:
            parts.append(f"Patterns: {', '.join(self.six_w.existing_patterns)}")
        return ' | '.join(parts) if parts else None