"""
Memory File Model

Pydantic models for Claude's persistent memory file system.
Part of WI-114: Claude Persistent Memory System.

This module provides validated models for memory files that give Claude
always-current access to APM (Agent Project Manager) database content.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MemoryFileType(str, Enum):
    """Types of memory files generated for Claude."""
    RULES = "rules"              # RULES.md - Governance rules system
    PRINCIPLES = "principles"    # PRINCIPLES.md - Development principles
    WORKFLOW = "workflow"        # WORKFLOW.md - Quality-gated workflow
    AGENTS = "agents"            # AGENTS.md - Agent system architecture
    CONTEXT = "context"          # CONTEXT.md - Context assembly system
    PROJECT = "project"          # PROJECT.md - Project information
    IDEAS = "ideas"              # IDEAS.md - Ideas analysis pipeline


class ValidationStatus(str, Enum):
    """Validation status for memory files."""
    PENDING = "pending"          # Not yet validated
    VALIDATED = "validated"      # Validated and current
    STALE = "stale"             # Needs regeneration (source changed)
    FAILED = "failed"           # Validation failed


class MemoryFile(BaseModel):
    """
    Memory File entity for Claude's persistent memory system.

    Tracks generated memory files that provide Claude with always-current
    access to APM (Agent Project Manager) database content (rules, agents, workflow, contexts, etc.).
    """

    # Primary key
    id: Optional[int] = Field(None, description="Memory file ID (auto-assigned)")

    # Foreign keys
    project_id: int = Field(..., description="Associated project ID")
    session_id: Optional[int] = Field(None, description="Session that generated this file")

    # Memory file metadata
    file_type: MemoryFileType = Field(..., description="Type of memory file")
    file_path: str = Field(..., description="Relative path in .claude/ directory")
    file_hash: Optional[str] = Field(None, description="SHA-256 hash for change detection")

    # Content
    content: str = Field(..., description="Generated markdown content")
    source_tables: List[str] = Field(
        default_factory=list,
        description="Database tables used to generate content"
    )
    template_version: str = Field(
        default="1.0.0",
        description="Template version used for generation"
    )

    # Quality metrics
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in content accuracy (0.0-1.0)"
    )
    completeness_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Completeness of content (0.0-1.0)"
    )
    validation_status: ValidationStatus = Field(
        default=ValidationStatus.PENDING,
        description="Validation status"
    )

    # Generation metadata
    generated_by: str = Field(..., description="Agent or service that generated file")
    generation_duration_ms: Optional[int] = Field(
        None,
        description="Time taken to generate file (milliseconds)"
    )

    # Timestamps
    generated_at: str = Field(..., description="Generation timestamp (ISO format)")
    validated_at: Optional[str] = Field(None, description="Validation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiry timestamp for cache")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    @property
    def is_stale(self) -> bool:
        """Check if memory file needs regeneration."""
        return self.validation_status == ValidationStatus.STALE

    @property
    def is_validated(self) -> bool:
        """Check if memory file is validated and current."""
        return self.validation_status == ValidationStatus.VALIDATED

    @property
    def is_expired(self) -> bool:
        """Check if memory file has expired."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return False

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "file_type": "rules",
                "file_path": ".claude/RULES.md",
                "content": "# APM (Agent Project Manager) Governance Rules\n\n...",
                "source_tables": ["rules"],
                "generated_by": "memory-generator",
                "generated_at": "2025-10-21T10:00:00",
            }
        }
