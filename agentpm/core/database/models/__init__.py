"""
Database Models

Pydantic domain models with validation.

These models represent business entities with type safety and validation,
separate from database persistence concerns (handled by adapters).
"""

from .project import Project
from .work_item import WorkItem
from .task import Task
from .idea import Idea
from .idea_element import IdeaElement
from .agent import Agent
from .rule import Rule
from .context import Context, UnifiedSixW
from .dependencies import TaskDependency, TaskBlocker, WorkItemDependency
from .work_item_summary import WorkItemSummary
from .summary import Summary
from .evidence_source import EvidenceSource
from .event import Event
from .document_reference import DocumentReference
from .document_audit_log import DocumentAuditLog
from .search_index import SearchIndex
from .search_metrics import SearchMetrics
from .provider import (
    ProviderInstallation,
    CursorConfig,
    CursorMemory,
    CustomMode,
    ProviderType,
    InstallationStatus,
    MemorySyncDirection,
    SafetyLevel,
    AllowlistEntry,
    Guardrails,
    RuleTemplate,
    InstallResult,
    VerifyResult,
    MemorySyncResult,
    UpdateResult,
)
from .detection_analysis import (
    FileAnalysis,
    ProjectAnalysis,
    ComplexityReport,
    MaintainabilityReport,
)
from .detection_graph import (
    DependencyNode,
    CircularDependency,
    CouplingMetrics,
    DependencyGraphAnalysis,
)
from .detection_sbom import (
    LicenseInfo,
    SBOMComponent,
    SBOM,
)
from .detection_pattern import (
    PatternMatch,
    PatternAnalysis,
)
from .detection_fitness import (
    Policy,
    PolicyViolation,
    FitnessResult,
)
from .detection_preset import (
    DetectionPreset,
)
from .detection_runtime import (
    RuntimeOverlay,
)

__all__ = [
    "Project",
    "WorkItem",
    "Task",
    "Idea",
    "IdeaElement",
    "Agent",
    "Rule",
    "Context",
    "UnifiedSixW",
    "TaskDependency",
    "TaskBlocker",
    "WorkItemDependency",
    "WorkItemSummary",
    "Summary",
    # Migration 0011 models
    "EvidenceSource",
    "Event",
    "DocumentReference",
    # Document publishing models (WI-164)
    "DocumentAuditLog",
    # Search models
    "SearchIndex",
    "SearchMetrics",
    # Provider models
    "ProviderInstallation",
    "CursorConfig",
    "CursorMemory",
    "CustomMode",
    "ProviderType",
    "InstallationStatus",
    "MemorySyncDirection",
    "SafetyLevel",
    "AllowlistEntry",
    "Guardrails",
    "RuleTemplate",
    "InstallResult",
    "VerifyResult",
    "MemorySyncResult",
    "UpdateResult",
    # Detection analysis models
    "FileAnalysis",
    "ProjectAnalysis",
    "ComplexityReport",
    "MaintainabilityReport",
    # Detection graph models
    "DependencyNode",
    "CircularDependency",
    "CouplingMetrics",
    "DependencyGraphAnalysis",
    # Detection SBOM models
    "LicenseInfo",
    "SBOMComponent",
    "SBOM",
    # Detection pattern models
    "PatternMatch",
    "PatternAnalysis",
    # Detection fitness models
    "Policy",
    "PolicyViolation",
    "FitnessResult",
    # Detection preset models
    "DetectionPreset",
    # Detection runtime models
    "RuntimeOverlay",
]