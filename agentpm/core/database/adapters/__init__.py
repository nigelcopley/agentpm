"""
Database Adapters

Model <-> Database conversion layer.

Adapters handle the translation between Pydantic domain models
and database row dictionaries, including JSON serialization,
enum conversion, and datetime handling.

THREE-LAYER PATTERN (DP-001):
  CLI -> Adapter (validates Pydantic) -> Methods (executes SQL)

CLI commands should use Adapter CRUD methods:
  - WorkItemAdapter.create(db, work_item)
  - TaskAdapter.create(db, task)
  - DocumentReferenceAdapter.create(db, document)

NOT direct methods calls:
  - work_items.create_work_item(db, work_item)  # BYPASS - Don't use
"""

from .base_adapter import BaseAdapter
from .project_adapter import ProjectAdapter
from .work_item_adapter import WorkItemAdapter
from .task_adapter import TaskAdapter
from .idea_adapter import IdeaAdapter
from .idea_element_adapter import IdeaElementAdapter
from .session import SessionAdapter
from .agent_adapter import AgentAdapter
from .rule_adapter import RuleAdapter
from .context_adapter import ContextAdapter
from .dependencies_adapter import (
    TaskDependencyAdapter,
    TaskBlockerAdapter,
    WorkItemDependencyAdapter
)
from .work_item_summary_adapter import WorkItemSummaryAdapter
from .summary_adapter import SummaryAdapter
from .search_index_adapter import SearchIndexAdapter
from .search_metrics_adapter import SearchMetricsAdapter
from .document_reference_adapter import DocumentReferenceAdapter
from .provider import (
    ProviderInstallationAdapter,
    CursorMemoryAdapter,
    ProviderFileAdapter,
)
from .skill_adapter import SkillAdapter

__all__ = [
    "BaseAdapter",
    "ProjectAdapter",
    "WorkItemAdapter",
    "TaskAdapter",
    "IdeaAdapter",
    "IdeaElementAdapter",
    "SessionAdapter",
    "AgentAdapter",
    "RuleAdapter",
    "ContextAdapter",
    "TaskDependencyAdapter",
    "TaskBlockerAdapter",
    "WorkItemDependencyAdapter",
    "WorkItemSummaryAdapter",
    "SummaryAdapter",
    "DocumentReferenceAdapter",
    # Search adapters
    "SearchIndexAdapter",
    "SearchMetricsAdapter",
    # Provider adapters
    "ProviderInstallationAdapter",
    "CursorMemoryAdapter",
    "ProviderFileAdapter",
    # Skills adapters (WI-171)
    "SkillAdapter",
]
