"""
Document Reference Model

Tracks documents created during tasks, work items, and at project level.
Enables document discovery and organization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat, DocumentCategory, StorageMode, SyncStatus


class DocumentReference(BaseModel):
    """
    Document reference for Universal Documentation System.

    Path Structure: docs/{category}/{document_type}/{filename}

    Links documents to entities with rich metadata for multi-dimensional queries.

    Example:
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=112,
            category="architecture",
            document_type=DocumentType.DESIGN,
            file_path="docs/architecture/design/doc-system.md",
            title="Documentation System Architecture",
            component="documentation",
            domain="knowledge-management",
            audience="developer",
            maturity="approved",
            tags=["architecture", "metadata", "database-first"]
        )
    """

    id: Optional[int] = None
    entity_type: EntityType = Field(..., description="Type of entity this document belongs to")
    entity_id: int = Field(..., gt=0, description="ID of the entity")

    # Hierarchical categorization (NEW - Universal Documentation System)
    category: Optional[str] = Field(None, description="Top-level category (planning, architecture, guides, etc.)")
    document_type: Optional[DocumentType] = Field(None, description="Document classification")
    document_type_dir: Optional[str] = Field(None, description="Physical subdirectory under category")

    # File metadata
    file_path: str = Field(..., min_length=1, max_length=500, description="Path: docs/{category}/{document_type}/{filename}")
    title: Optional[str] = Field(None, max_length=200, description="Human-readable title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    content_hash: Optional[str] = Field(None, max_length=64, description="SHA256 hash for change detection")
    format: Optional[DocumentFormat] = Field(None, description="Document format")

    # Rich metadata for multi-dimensional queries (NEW)
    segment_type: Optional[str] = Field(None, description="Content segment (functional, technical, business, etc.)")
    component: Optional[str] = Field(None, description="Related component (auth, payment, workflow, etc.)")
    domain: Optional[str] = Field(None, description="Business/technical domain (security, performance, etc.)")
    audience: Optional[str] = Field(None, description="Target audience (developer, user, admin, stakeholder)")
    maturity: Optional[str] = Field(None, description="Lifecycle state (draft, review, approved, deprecated)")
    priority: Optional[str] = Field(None, description="Priority level (critical, high, medium, low)")
    tags: List[str] = Field(default_factory=list, description="Flexible tags for search")

    # Workflow integration (NEW)
    phase: Optional[str] = Field(None, description="SDLC phase (D1, P1, I1, R1, O1, E1)")
    work_item_id: Optional[int] = Field(None, description="Originating work item")

    # Content storage (WI-133: Hybrid Storage System - Migration 0039)
    content: Optional[str] = Field(None, description="Full document content (database is source of truth)")
    filename: Optional[str] = Field(None, max_length=255, description="Base filename for path construction")
    storage_mode: StorageMode = Field(default=StorageMode.HYBRID, description="Storage strategy (database_only, file_only, hybrid)")
    content_updated_at: Optional[datetime] = Field(None, description="When content was last modified")
    last_synced_at: Optional[datetime] = Field(None, description="When file was last synced from database")
    sync_status: SyncStatus = Field(default=SyncStatus.SYNCED, description="Synchronization state (synced, pending, conflict, error)")

    # Visibility and lifecycle (WI-164: Document Visibility System - Migration 0044)
    visibility: Optional[str] = Field(None, description="Visibility level (private|restricted|public)")
    lifecycle_stage: Optional[str] = Field('draft', description="Lifecycle stage (draft|review|approved|published|archived)")
    published_path: Optional[str] = Field(None, description="Path where public copy exists")
    published_date: Optional[datetime] = Field(None, description="When document was published")
    unpublished_date: Optional[datetime] = Field(None, description="When document was unpublished")
    review_status: Optional[str] = Field(None, description="Review status (pending|approved|rejected)")
    reviewer_id: Optional[str] = Field(None, description="Who is/was reviewing")
    reviewer_assigned_at: Optional[datetime] = Field(None, description="When reviewer was assigned")
    review_comment: Optional[str] = Field(None, description="Reviewer feedback")
    review_completed_at: Optional[datetime] = Field(None, description="When review was completed")
    auto_publish: Optional[bool] = Field(False, description="Auto-publish when approved")

    # Lifecycle
    created_by: Optional[str] = Field(None, max_length=200, description="Agent or user who created this document")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "entity_type": "task",
                "entity_id": 240,
                "file_path": "docs/components/agents/New/integration-plan.md",
                "document_type": "design",
                "title": "Integration Architecture",
                "description": "Plan for wiring agent components",
                "format": "markdown",
                "created_by": "system-architect"
            }
        }

    @field_validator('file_path')
    @classmethod
    def validate_path_structure(cls, v: str, info) -> str:
        """Validate path follows docs/ structure with exceptions for legacy files."""
        # Check if path is valid according to migration 0032 constraints
        is_valid = (
            # Primary rule: Must start with 'docs/' (public)
            v.startswith('docs/')
            # NEW: Private documents in .agentpm/docs/ (WI-164)
            or v.startswith('.agentpm/docs/')
            # Exception 1: Project root markdown files
            or v in ('CHANGELOG.md', 'README.md', 'LICENSE.md')
            # Exception 2: Project root artifacts (deployment, gates, etc.)
            or (v.endswith('.md') and '/' not in v)
            # Exception 3: Module documentation
            or v.startswith('agentpm/') and v.endswith('/README.md')
            # Exception 4: Test reports and test code
            or v.startswith('testing/')
            or v.startswith('tests/')
        )

        if not is_valid:
            raise ValueError(
                f"Document path must start with 'docs/' or '.agentpm/docs/' or be an allowed exception. "
                f"Got: {v}"
            )

        # For docs/ and .agentpm/docs/ paths, validate structure
        if v.startswith('docs/') or v.startswith('.agentpm/docs/'):
            parts = v.split('/')
            min_parts = 4 if v.startswith('docs/') else 5  # .agentpm/docs/ has extra level

            if len(parts) < min_parts:
                raise ValueError(
                    f"Path must follow pattern: docs/{{category}}/{{document_type}}/{{filename}} "
                    f"or .agentpm/docs/{{category}}/{{document_type}}/{{filename}}. "
                    f"Got: {v}"
                )

            # Extract category from path
            category_index = 1 if v.startswith('docs/') else 2
            path_category = parts[category_index]

            # Validate category matches if available (skip if None)
            if 'category' in info.data and info.data['category'] is not None and path_category != info.data['category']:
                raise ValueError(
                    f"Path category '{path_category}' doesn't match field category '{info.data['category']}'"
                )

            # Note: Path document_type directory and field document_type can be different
            # Path structure is for organization, document_type field is for classification
            # This allows flexible document organization while maintaining proper classification

        return v

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """Parse tags from JSON string or list."""
        if v is None:
            return []
        if isinstance(v, str):
            if not v or v == '[]':
                return []
            import json
            return json.loads(v)
        return v

    @property
    def computed_path(self) -> str:
        """
        Compute document path from category, document_type, and filename.

        For hybrid storage: Database stores content + metadata (filename, category, type).
        Path is computed, not stored. This enables flexible path reorganization.

        Returns:
            Canonical path if category/type/filename available, else file_path

        Examples:
            >>> doc = DocumentReference(
            ...     category="architecture",
            ...     document_type=DocumentType.DESIGN_DOC,
            ...     filename="auth-system.md",
            ...     file_path="docs/architecture/design_doc/auth-system.md"
            ... )
            >>> doc.computed_path
            "docs/architecture/design_doc/auth-system.md"
        """
        if self.filename and self.category and self.document_type:
            return DocumentReference.construct_path(
                self.category,
                self.document_type.value,
                self.filename
            )
        return self.file_path

    @staticmethod
    def construct_path(category: str, document_type: str, filename: str) -> str:
        """
        Construct canonical document path.

        Args:
            category: One of 8 categories (planning, architecture, guides, etc.)
            document_type: Document type (requirements, design, user_guide, etc.)
            filename: Base filename (e.g., auth-functional.md)

        Returns:
            Canonical path: docs/{category}/{document_type}/{filename}

        Examples:
            >>> DocumentReference.construct_path("planning", "requirements", "auth-functional.md")
            "docs/planning/requirements/auth-functional.md"

            >>> DocumentReference.construct_path("architecture", "design", "database.md")
            "docs/architecture/design/database.md"
        """
        return f"docs/{category}/{document_type}/{filename}"

    @staticmethod
    def parse_path(file_path: str) -> dict:
        """
        Parse path to extract category, document_type, filename.

        Args:
            file_path: Full path (e.g., docs/planning/requirements/auth.md)

        Returns:
            Dict with category, document_type, filename

        Raises:
            ValueError: If path doesn't match expected structure

        Examples:
            >>> DocumentReference.parse_path("docs/planning/requirements/auth.md")
            {"category": "planning", "document_type": "requirements", "filename": "auth.md"}
        """
        parts = file_path.split('/')
        if len(parts) < 4 or parts[0] != 'docs':
            raise ValueError(
                f"Invalid path structure. Expected: docs/{{category}}/{{document_type}}/{{filename}}. "
                f"Got: {file_path}"
            )

        return {
            'category': parts[1],
            'document_type': parts[2],
            'filename': '/'.join(parts[3:])  # Handle nested filenames
        }
