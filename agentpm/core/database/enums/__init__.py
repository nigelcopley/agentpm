"""
Database Enumerations

Type-safe enumerations for all categorical fields in the database.

Usage:
    from agentpm.core.database.enums import ProjectStatus, WorkItemStatus, TaskStatus

    project = Project(
        name="AIPM",
        status=ProjectStatus.ACTIVE,
        development_philosophy=DevelopmentPhilosophy.PROFESSIONAL_STANDARDS
    )

    work_item = WorkItem(
        name="Database Foundation",
        status=WorkItemStatus.ACTIVE,
        type=WorkItemType.FEATURE
    )
"""

from .status import ProjectStatus, WorkItemStatus, TaskStatus
from .idea import IdeaStatus, IdeaSource
from .types import (
    WorkItemType,
    TaskType,
    DevelopmentPhilosophy,
    EntityType,
    ContextType,
    ResourceType,
    ConfidenceBand,
    EnforcementLevel,
    ProjectType,
    ApplicationProjectType,
    Phase,
    SourceType,
    EventType,
    EventCategory,
    EventSeverity,
    DocumentCategory,
    DocumentType,
    DocumentFormat,
    AgentTier,
    AgentFunctionalCategory,
    SummaryType,
    SearchResultType,
    StorageMode,
    SyncStatus,
    DocumentLifecycle,
    DocumentVisibility,
)
from .development_principles import (
    DevelopmentPrinciple,
    PrincipleDefinition,
    PrincipleCategory,
    PrinciplePriority,
    get_principle_definition,
    resolve_principle_conflict,
    get_principles_by_priority,
    get_principles_for_ai_agents,
)
from .detection import (
    PolicyLevel,
    ArchitecturePattern,
    LicenseType,
)

__all__ = [
    # Status enums (hierarchical)
    "ProjectStatus",
    "WorkItemStatus",
    "TaskStatus",
    # Idea enums (WI-50)
    "IdeaStatus",
    "IdeaSource",
    # Type enums
    "WorkItemType",
    "TaskType",
    "DevelopmentPhilosophy",
    "EntityType",
    "ContextType",
    "ResourceType",
    "ConfidenceBand",
    "EnforcementLevel",
    # Migration 0011 enums
    "ProjectType",
    "ApplicationProjectType",
    "Phase",
    "SourceType",
    "EventType",
    "EventCategory",
    "EventSeverity",
    "DocumentCategory",
    "DocumentType",
    "DocumentFormat",
    "AgentTier",
    "AgentFunctionalCategory",
    # Summary system enums
    "SummaryType",
    # Search system enums
    "SearchResultType",
    # Document storage enums (WI-133)
    "StorageMode",
    "SyncStatus",
    # Document publishing enums (WI-164)
    "DocumentLifecycle",
    "DocumentVisibility",
    # Development Principles (Pyramid)
    "DevelopmentPrinciple",
    "PrincipleDefinition",
    "PrincipleCategory",
    "PrinciplePriority",
    "get_principle_definition",
    "resolve_principle_conflict",
    "get_principles_by_priority",
    "get_principles_for_ai_agents",
    # Detection system enums
    "PolicyLevel",
    "ArchitecturePattern",
    "LicenseType",
]