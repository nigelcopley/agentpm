"""
Common Patterns for Provider Generators

Shared patterns, dataclasses, and utilities used across all provider generators.
This module provides universal context structures and common exclusion patterns
that are provider-agnostic.

Pattern: Dataclasses with Pydantic validation for serialization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule


# ============================================================================
# Helper Context Dataclasses
# ============================================================================


@dataclass
class ProjectContext:
    """
    Simplified project context for template rendering.

    Contains only fields needed for AGENTS.md and provider-specific
    context files (not full database model).

    Attributes:
        id: Project ID
        name: Project name
        description: Project description
        tech_stack: List of detected technologies
        frameworks: List of detected frameworks
        root_path: Project root directory path
    """

    id: int
    name: str
    description: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    root_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for template rendering"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tech_stack": self.tech_stack,
            "frameworks": self.frameworks,
            "root_path": self.root_path,
        }


@dataclass
class WorkItemContext:
    """
    Simplified work item context for template rendering.

    Contains only fields needed for agent context (not full database model).

    Attributes:
        id: Work item ID
        name: Work item name
        type: Work item type (feature/analysis/objective/research)
        status: Current workflow status
        phase: Current phase (D1/P1/I1/R1/O1/E1)
        business_context: Business rationale
        effort_estimate_hours: Estimated effort
        priority: Priority level (1-5)
    """

    id: int
    name: str
    type: str
    status: str
    phase: Optional[str] = None
    business_context: Optional[str] = None
    effort_estimate_hours: Optional[float] = None
    priority: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for template rendering"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "phase": self.phase,
            "business_context": self.business_context,
            "effort_estimate_hours": self.effort_estimate_hours,
            "priority": self.priority,
        }


@dataclass
class TaskContext:
    """
    Simplified task context for template rendering.

    Contains only fields needed for agent context (not full database model).

    Attributes:
        id: Task ID
        name: Task name
        type: Task type (implementation/testing/documentation/research)
        status: Current workflow status
        description: Task description
        effort_hours: Estimated effort
        priority: Priority level (1-5)
        assigned_to: Assigned agent role
        quality_metadata: Quality gate tracking data
    """

    id: int
    name: str
    type: str
    status: str
    description: Optional[str] = None
    effort_hours: Optional[float] = None
    priority: int = 3
    assigned_to: Optional[str] = None
    quality_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for template rendering"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "description": self.description,
            "effort_hours": self.effort_hours,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "quality_metadata": self.quality_metadata,
        }


# ============================================================================
# Universal Context Structure
# ============================================================================


@dataclass
class UniversalContext:
    """
    Universal context format for AGENTS.md structure.

    This is the canonical context format that all providers use to generate
    their AGENTS.md files. It contains hierarchical context (project → work_item → task)
    plus rules, agents, and detection data.

    This structure maps to AGENTS.md sections:
    - Project information
    - Active work item (if any)
    - Active task (if any)
    - Applicable rules (BLOCK/LIMIT/GUIDE/ENHANCE)
    - Available agents
    - Tech stack and frameworks

    Attributes:
        version: Context format version (e.g., "1.0.0")
        project: Project context
        generated: Generation timestamp
        providers: List of provider names this context supports
        work_item: Optional active work item context
        task: Optional active task context
        rules: List of applicable rules (filtered by enabled)
        agents: List of available agents (filtered by is_active)
        tech_stack: Detected technologies
        detected_frameworks: Detected frameworks
    """

    version: str
    project: ProjectContext
    generated: datetime
    providers: List[str]

    # Optional hierarchical context
    work_item: Optional[WorkItemContext] = None
    task: Optional[TaskContext] = None

    # Rules and agents
    rules: List[Rule] = field(default_factory=list)
    agents: List[Agent] = field(default_factory=list)

    # Detection data
    tech_stack: List[str] = field(default_factory=list)
    detected_frameworks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary for template rendering.

        Returns:
            Dictionary with all context fields, suitable for Jinja2 templates
        """
        return {
            "version": self.version,
            "project": self.project.to_dict(),
            "generated": self.generated.isoformat(),
            "providers": self.providers,
            "work_item": self.work_item.to_dict() if self.work_item else None,
            "task": self.task.to_dict() if self.task else None,
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "enforcement_level": rule.enforcement_level.value,
                    "category": rule.category,
                    "enabled": rule.enabled,
                }
                for rule in self.rules
            ],
            "agents": [
                {
                    "id": agent.id,
                    "role": agent.role,
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "capabilities": agent.capabilities,
                    "tier": agent.tier.value if agent.tier else None,
                    "is_active": agent.is_active,
                }
                for agent in self.agents
            ],
            "tech_stack": self.tech_stack,
            "detected_frameworks": self.detected_frameworks,
        }

    def get_blocking_rules(self) -> List[Rule]:
        """Get only BLOCK-level rules"""
        return [rule for rule in self.rules if rule.enforcement_level.value == "BLOCK"]

    def get_rules_by_category(self, category: str) -> List[Rule]:
        """Get rules filtered by category"""
        return [rule for rule in self.rules if rule.category == category]

    def get_agents_by_tier(self, tier: int) -> List[Agent]:
        """Get agents filtered by tier"""
        return [agent for agent in self.agents if agent.tier and agent.tier.value == tier]


# ============================================================================
# Common Exclusion Patterns
# ============================================================================


class CommonExclusions:
    """
    Common file exclusion patterns for all providers.

    These patterns define which files should be excluded from:
    - Context generation
    - File indexing
    - Amalgamation generation
    - Provider-specific processing

    Each provider has a base set plus provider-specific additions.

    Usage:
        >>> exclusions = CommonExclusions.CLAUDE_CODE
        >>> if any(pattern in file_path for pattern in exclusions):
        ...     # Skip this file
    """

    # Standard exclusions for all providers
    STANDARD: List[str] = [
        ".agentpm/",
        ".git/",
        ".gitignore",
        "node_modules/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".tox/",
        ".venv/",
        "venv/",
        "env/",
        "ENV/",
        "build/",
        "dist/",
        "*.egg-info/",
        ".DS_Store",
        "*.swp",
        "*.swo",
        "*~",
        ".idea/",
        ".vscode/",
        "*.log",
        ".env",
        ".env.local",
        "credentials.json",
        "secrets.yaml",
    ]

    # Claude Code specific exclusions
    CLAUDE_CODE: List[str] = STANDARD + [
        ".claude/cache/",
        ".claude/memory/",  # Exclude auto-generated memory
        ".claude/checkpoints/",
    ]

    # Cursor specific exclusions
    CURSOR: List[str] = STANDARD + [
        ".cursor/",
        ".cursor-cache/",
    ]

    # OpenAI Codex specific exclusions
    CODEX: List[str] = STANDARD + [
        ".codex/",
        ".codex-cache/",
    ]

    # Google Gemini specific exclusions
    GEMINI: List[str] = STANDARD + [
        ".gemini/",
        ".gemini/checkpoints/",
        ".gemini/cache/",
    ]

    @classmethod
    def get_for_provider(cls, provider_name: str) -> List[str]:
        """
        Get exclusions for specific provider.

        Args:
            provider_name: Provider name (anthropic, cursor, openai, google)

        Returns:
            List of exclusion patterns
        """
        provider_map = {
            "anthropic": cls.CLAUDE_CODE,
            "claude-code": cls.CLAUDE_CODE,
            "cursor": cls.CURSOR,
            "openai": cls.CODEX,
            "codex": cls.CODEX,
            "google": cls.GEMINI,
            "gemini": cls.GEMINI,
        }
        return provider_map.get(provider_name.lower(), cls.STANDARD)


# ============================================================================
# Common Rule Categories
# ============================================================================


class CommonRuleCategories:
    """
    Standard rule categories across providers.

    These categories are used for:
    - Grouping rules in AGENTS.md
    - Filtering rules by domain
    - Organizing quality gates
    - Provider-specific rule injection

    Categories map to database rule.category field and align with
    the rule catalog structure in _RULES/.

    Usage:
        >>> rules = universal_context.get_rules_by_category(
        ...     CommonRuleCategories.ARCHITECTURE
        ... )
    """

    # Development principles (DP-XXX)
    ARCHITECTURE = "development_principles"

    # Testing standards (TES-XXX, TEST-XXX)
    TESTING = "testing_standards"

    # Security requirements (SEC-XXX)
    SECURITY = "security_requirements"

    # Documentation standards (DOC-XXX)
    DOCUMENTATION = "documentation_standards"

    # Workflow governance (WF-XXX)
    WORKFLOW = "workflow_governance"

    # Code quality standards (CQ-XXX)
    CODE_QUALITY = "code_quality"

    # Performance requirements (PERF-XXX)
    PERFORMANCE = "performance_requirements"

    # Continuous Integration (CI-XXX)
    CI_CD = "continuous_integration"

    @classmethod
    def all_categories(cls) -> List[str]:
        """Get all standard categories"""
        return [
            cls.ARCHITECTURE,
            cls.TESTING,
            cls.SECURITY,
            cls.DOCUMENTATION,
            cls.WORKFLOW,
            cls.CODE_QUALITY,
            cls.PERFORMANCE,
            cls.CI_CD,
        ]

    @classmethod
    def get_display_name(cls, category: str) -> str:
        """
        Get human-readable category name.

        Args:
            category: Category identifier

        Returns:
            Human-readable name
        """
        display_names = {
            cls.ARCHITECTURE: "Development Principles",
            cls.TESTING: "Testing Standards",
            cls.SECURITY: "Security Requirements",
            cls.DOCUMENTATION: "Documentation Standards",
            cls.WORKFLOW: "Workflow Governance",
            cls.CODE_QUALITY: "Code Quality",
            cls.PERFORMANCE: "Performance Requirements",
            cls.CI_CD: "Continuous Integration",
        }
        return display_names.get(category, category.replace("_", " ").title())
