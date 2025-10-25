"""
Provider Models - Layer 1: Pydantic Domain Models

Type-safe models for provider system including:
- Provider installation metadata
- Cursor configuration
- Memory sync models
- Custom modes
- Guardrails/security
- Rule templates
- Result types

Pattern: Pydantic BaseModel with comprehensive validation
Architecture: Database layer (core/database/) - NOT provider-specific
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path


class ProviderType(str, Enum):
    """Supported provider types."""
    CURSOR = "cursor"
    VSCODE = "vscode"
    ZED = "zed"
    CLAUDE_CODE = "claude_code"


class InstallationStatus(str, Enum):
    """Provider installation status."""
    INSTALLED = "installed"
    PARTIAL = "partial"
    FAILED = "failed"
    UNINSTALLED = "uninstalled"


class MemorySyncDirection(str, Enum):
    """Memory sync direction."""
    TO_CURSOR = "to_cursor"
    FROM_CURSOR = "from_cursor"
    BI_DIRECTIONAL = "bi_directional"


class SafetyLevel(str, Enum):
    """Command safety levels for guardrails."""
    SAFE_AUTO = "safe_auto"  # Auto-run without confirmation
    SAFE_CONFIRM = "safe_confirm"  # Safe but confirm first
    UNSAFE = "unsafe"  # Require explicit confirmation


# Core Models

class ProviderInstallation(BaseModel):
    """
    Provider installation record.

    Tracks provider installation state in database.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: Optional[int] = None
    project_id: int
    provider_type: ProviderType
    provider_version: str = Field(default="1.0.0")

    # Installation metadata
    install_path: str = Field(..., description="Root path for provider files")
    status: InstallationStatus = Field(default=InstallationStatus.INSTALLED)
    config: Dict[str, Any] = Field(default_factory=dict)

    # File tracking
    installed_files: List[str] = Field(default_factory=list)
    file_hashes: Dict[str, str] = Field(default_factory=dict)

    # Timestamps
    installed_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_verified_at: Optional[datetime] = None


class CursorConfig(BaseModel):
    """
    Cursor IDE configuration.

    Complete configuration for Cursor provider installation.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Project context
    project_name: str
    project_path: str
    tech_stack: List[str] = Field(default_factory=list)

    # Rules configuration
    rules_enabled: bool = Field(default=True)
    rules_to_install: List[str] = Field(
        default_factory=lambda: [
            "aipm-master",
            "python-implementation",
            "testing-standards",
            "cli-development",
            "database-patterns",
            "documentation-quality"
        ]
    )

    # Memory sync configuration
    memory_sync_enabled: bool = Field(default=True)
    memory_sync_direction: MemorySyncDirection = Field(default=MemorySyncDirection.BI_DIRECTIONAL)
    memory_sync_interval_hours: int = Field(default=1, ge=1, le=24)

    # Custom modes configuration
    modes_enabled: bool = Field(default=True)
    modes_to_install: List[str] = Field(
        default_factory=lambda: [
            "aipm-discovery",
            "aipm-planning",
            "aipm-implementation",
            "aipm-review",
            "aipm-operations",
            "aipm-evolution"
        ]
    )

    # Guardrails configuration
    guardrails_enabled: bool = Field(default=True)
    guardrails: Optional["Guardrails"] = None

    # Indexing configuration
    indexing_enabled: bool = Field(default=True)
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            ".aipm/",
            "htmlcov/",
            ".pytest_cache/",
            "**/__pycache__/",
            "*.pyc",
            ".git/",
            "node_modules/"
        ]
    )

    # Hooks configuration
    hooks_enabled: bool = Field(default=False)  # P2 feature

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """Ensure project path is absolute."""
        path = Path(v)
        if not path.is_absolute():
            raise ValueError("project_path must be an absolute path")
        return str(path)


class CursorMemory(BaseModel):
    """
    Cursor Memory file.

    Represents a single memory file in Cursor's .cursor/memories/ directory.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: Optional[int] = None
    project_id: int

    # Memory metadata
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    category: str = Field(default="general")

    # Memory content
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)

    # File metadata
    file_path: str = Field(..., description="Relative path in .cursor/memories/")
    file_hash: Optional[str] = None

    # Sync metadata
    source_learning_id: Optional[int] = Field(
        default=None,
        description="AIPM learning ID that generated this memory"
    )
    last_synced_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CustomMode(BaseModel):
    """
    Cursor Custom Mode configuration.

    Represents a phase-specific Cursor mode.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Mode identification
    mode_id: str = Field(..., description="Unique mode ID (e.g., 'aipm-discovery')")
    display_name: str
    description: str

    # Mode configuration
    system_prompt: str = Field(..., description="System prompt for this mode")
    tools_enabled: List[str] = Field(default_factory=list)
    rules_active: List[str] = Field(default_factory=list)

    # Mode metadata
    phase: str = Field(..., description="AIPM workflow phase (D1, P1, I1, R1, O1, E1)")
    icon: str = Field(default="🔧")
    color: str = Field(default="#1e90ff")

    # Behavior
    auto_activate: bool = Field(default=False)
    default_for_phase: bool = Field(default=True)


class AllowlistEntry(BaseModel):
    """Single allowlist entry for guardrails."""

    model_config = ConfigDict(validate_assignment=True)

    pattern: str = Field(..., description="Regex pattern or exact command")
    safety: SafetyLevel = Field(default=SafetyLevel.SAFE_CONFIRM)
    auto_run: bool = Field(default=False)
    description: str = Field(default="")


class Guardrails(BaseModel):
    """
    Security guardrails configuration.

    Defines safe commands and auto-run permissions.
    """

    model_config = ConfigDict(validate_assignment=True)

    # Allowlists by category
    allowlists: Dict[str, List[AllowlistEntry]] = Field(
        default_factory=lambda: {
            "apm_commands": [
                AllowlistEntry(
                    pattern="^apm status$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Project dashboard"
                ),
                AllowlistEntry(
                    pattern="^apm work-item (list|show).*$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Read-only work item queries"
                ),
                AllowlistEntry(
                    pattern="^apm context show.*$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Context assembly"
                ),
                AllowlistEntry(
                    pattern="^apm task (list|show).*$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Read-only task queries"
                ),
            ],
            "testing": [
                AllowlistEntry(
                    pattern="^pytest tests/.*$",
                    safety=SafetyLevel.SAFE_CONFIRM,
                    auto_run=False,
                    description="Run tests (requires confirmation)"
                ),
            ],
            "linting": [
                AllowlistEntry(
                    pattern="^ruff check.*$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Linting check"
                ),
                AllowlistEntry(
                    pattern="^black --check.*$",
                    safety=SafetyLevel.SAFE_AUTO,
                    auto_run=True,
                    description="Format check"
                ),
            ]
        }
    )

    # Global settings
    require_confirmation_by_default: bool = Field(default=True)
    allow_destructive_operations: bool = Field(default=False)
    max_auto_runs_per_session: int = Field(default=10, ge=0)


class RuleTemplate(BaseModel):
    """
    Rule template metadata.

    Tracks rule template files and their rendering.
    """

    model_config = ConfigDict(validate_assignment=True)

    rule_id: str = Field(..., description="Rule ID (e.g., 'aipm-master')")
    template_path: str = Field(..., description="Path to Jinja2 template")
    output_filename: str = Field(..., description="Output filename (e.g., 'aipm-master.mdc')")

    # Template variables
    required_vars: List[str] = Field(default_factory=list)
    optional_vars: List[str] = Field(default_factory=list)

    # Metadata
    priority: int = Field(default=100, ge=0, le=100)
    always_apply: bool = Field(default=True)
    description: str = Field(default="")


# Result Models

class InstallResult(BaseModel):
    """Result of provider installation."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool
    installation_id: Optional[int] = None
    installed_files: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    message: str = Field(default="")


class VerifyResult(BaseModel):
    """Result of provider verification."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool
    verified_files: int = 0
    missing_files: List[str] = Field(default_factory=list)
    modified_files: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    message: str = Field(default="")


class MemorySyncResult(BaseModel):
    """Result of memory sync operation."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool
    synced_to_cursor: int = 0
    synced_from_cursor: int = 0
    skipped: int = 0
    errors: List[str] = Field(default_factory=list)
    message: str = Field(default="")


class UpdateResult(BaseModel):
    """Result of provider update operation."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool
    updated_files: List[str] = Field(default_factory=list)
    added_files: List[str] = Field(default_factory=list)
    removed_files: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    message: str = Field(default="")
