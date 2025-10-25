"""
Document Path Generator Service

Automatically generates file paths from document metadata using slugification,
visibility policies, conflict resolution, and validation.

Part of Work Item #164: Auto-Generate Document File Paths
Task #1079: Implement File Path Generator Service

Architecture: Service Layer (Business Logic)
  - Slugifies titles into URL-safe filenames
  - Determines base directory from visibility policy
  - Resolves filename conflicts
  - Validates paths for security and compliance
  - Corrects incorrect paths with automatic file moves

Integration:
  - Uses VisibilityPolicyEngine for base directory determination
  - Uses DatabaseService for conflict detection
  - Uses file system for path validation and file moves

Example:
    >>> generator = DocumentPathGenerator(db)
    >>> result = generator.generate_path(
    ...     title="Authentication Requirements",
    ...     category="planning",
    ...     doc_type="requirements",
    ...     entity_type="work_item",
    ...     entity_id=158,
    ...     visibility="private",
    ...     lifecycle="draft"
    ... )
    >>> print(result.final_path)
    .agentpm/docs/planning/requirements/authentication-requirements.md
"""

import unicodedata
import re
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime
from dataclasses import dataclass

from ..database.service import DatabaseService
from .document_visibility import VisibilityPolicyEngine


@dataclass
class GeneratedPathResult:
    """
    Output of path generation algorithm.

    Contains final path, correction information, file operation metadata,
    and validation status.
    """
    # Generated path information
    final_path: str              # Complete path to use
    filename: str                # Just the filename part
    directory: str               # Just the directory part

    # Correction information
    was_corrected: bool          # True if provided_path was incorrect
    original_path: Optional[str] # Original provided_path (if corrected)
    correction_reason: str       # Why correction was needed

    # File operation metadata
    needs_move: bool             # True if file needs to be moved
    move_from: Optional[str]     # Source path for move operation

    # Validation status
    is_valid: bool               # Path passes all validation checks
    validation_errors: List[str] # Any validation failures


@dataclass
class CorrectionResult:
    """Result of path correction logic."""
    final_path: str
    was_corrected: bool
    original_path: Optional[str]
    correction_reason: str
    needs_move: bool
    move_from: Optional[str]


class DocumentPathGenerator:
    """
    Service for generating document file paths from metadata.

    Implements complete path generation algorithm with 6 steps:
    1. Title slugification
    2. Base directory determination (via VisibilityPolicyEngine)
    3. Path construction
    4. Conflict resolution
    5. Path validation
    6. Path correction (if user provides incorrect path)

    Example:
        >>> generator = DocumentPathGenerator(db)
        >>> result = generator.generate_path(
        ...     title="Phase 1: Completion Report",
        ...     category="planning",
        ...     doc_type="requirements",
        ...     entity_type="work_item",
        ...     entity_id=158,
        ...     visibility="private",
        ...     lifecycle="draft"
        ... )
        >>> assert result.final_path == ".agentpm/docs/planning/requirements/phase-1-completion-report.md"
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize path generator.

        Args:
            db: DatabaseService instance for conflict detection
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.visibility_engine = VisibilityPolicyEngine(db)

    def generate_path(
        self,
        title: str,
        category: str,
        doc_type: str,
        entity_type: str,
        entity_id: int,
        visibility: str,
        lifecycle: str = "draft",
        provided_path: Optional[str] = None
    ) -> GeneratedPathResult:
        """
        Generate document path with all validations.

        Orchestrates all 6 steps of path generation algorithm:
        1. Slugify title
        2. Determine base directory (via visibility policy)
        3. Construct path
        4. Resolve conflicts
        5. Validate path
        6. Correct provided path (if needed)

        Args:
            title: Document title
            category: Top-level category (planning, architecture, guides, etc.)
            doc_type: Document type (requirements, design_doc, user_guide, etc.)
            entity_type: Entity type (work_item, task, project)
            entity_id: Entity ID
            visibility: Document visibility (private, restricted, public)
            lifecycle: Document lifecycle (draft, review, approved, published, archived)
            provided_path: Optional user-provided path

        Returns:
            GeneratedPathResult with final path and metadata

        Raises:
            ValueError: If path generation fails validation
            RuntimeError: If cannot resolve conflicts after 1000 attempts

        Example:
            >>> result = generator.generate_path(
            ...     title="OAuth 2.0: Implementation Guide",
            ...     category="guides",
            ...     doc_type="developer_guide",
            ...     entity_type="work_item",
            ...     entity_id=164,
            ...     visibility="public",
            ...     lifecycle="published"
            ... )
            >>> assert result.final_path == "docs/guides/developer_guide/oauth-2-0-implementation-guide.md"
        """
        # Step 1: Slugify title
        slug = self.slugify(title)
        if not slug:
            # Fallback for empty title
            slug = self.generate_fallback_slug(entity_type, entity_id)

        filename = f"{slug}.md"

        # Step 2: Determine base directory (via visibility policy)
        base_dir = self.determine_base_dir(visibility, lifecycle)

        # Step 3: Construct path
        proposed_path = self.construct_path(base_dir, category, doc_type, filename)

        # Step 4: Resolve conflicts
        final_path = self.resolve_conflicts(
            proposed_path,
            entity_type,
            entity_id
        )

        # Step 5: Validate path
        is_valid, validation_errors = self.validate_path(str(final_path))
        if not is_valid:
            raise ValueError(
                f"Generated path failed validation: {final_path}\n"
                f"Errors: {', '.join(validation_errors)}"
            )

        # Step 6: Handle provided path correction
        file_exists_at_provided = False
        if provided_path:
            file_exists_at_provided = Path(provided_path).exists()

        correction = self.correct_path(
            provided_path,
            str(final_path),
            file_exists_at_provided
        )

        # Build result
        return GeneratedPathResult(
            final_path=correction.final_path,
            filename=Path(correction.final_path).name,
            directory=str(Path(correction.final_path).parent),
            was_corrected=correction.was_corrected,
            original_path=correction.original_path,
            correction_reason=correction.correction_reason,
            needs_move=correction.needs_move,
            move_from=correction.move_from,
            is_valid=is_valid,
            validation_errors=validation_errors
        )

    def slugify(self, title: str, max_length: int = 100) -> str:
        """
        Convert title to URL-safe slug.

        Rules:
        1. Convert to lowercase
        2. Replace spaces with hyphens
        3. Remove special characters except - and _
        4. Collapse multiple consecutive hyphens to single hyphen
        5. Strip leading/trailing hyphens
        6. Transliterate Unicode to ASCII (é→e, ñ→n)
        7. Limit length to max_length at word boundary
        8. Handle empty result with empty string

        Args:
            title: Document title (e.g., "Phase 1: Completion Report")
            max_length: Maximum slug length (default: 100)

        Returns:
            URL-safe slug (e.g., "phase-1-completion-report")

        Examples:
            >>> slugify("Phase 1: Completion Report")
            'phase-1-completion-report'

            >>> slugify("User Guide (Getting Started)")
            'user-guide-getting-started'

            >>> slugify("API Documentation: v2.0")
            'api-documentation-v2-0'

            >>> slugify("Test Plan #158 - OAuth")
            'test-plan-158-oauth'

            >>> slugify("Configuración de Autenticación")
            'configuracion-de-autenticacion'

            >>> slugify("OAuth 2.0 Integration Guide")
            'oauth-2-0-integration-guide'
        """
        if not title or not title.strip():
            return ""

        # Step 1: Unicode normalization (decompose accents)
        # NFD = Canonical Decomposition (é becomes e + ́)
        slug = unicodedata.normalize('NFD', title)

        # Step 2: Remove combining characters (accents)
        # Category 'Mn' = Nonspacing Mark (accents, diacritics)
        slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')

        # Step 3: Convert to lowercase
        slug = slug.lower()

        # Step 4: Replace spaces and special chars with hyphens
        # Keep alphanumeric, hyphens, underscores
        slug = re.sub(r'[^a-z0-9_-]+', '-', slug)

        # Step 5: Collapse multiple hyphens to single
        slug = re.sub(r'-+', '-', slug)

        # Step 6: Strip leading/trailing hyphens
        slug = slug.strip('-')

        # Step 7: Truncate to max_length at word boundary
        if len(slug) > max_length:
            # Find last hyphen before max_length
            truncated = slug[:max_length]
            last_hyphen = truncated.rfind('-')

            if last_hyphen > max_length * 0.75:  # Don't truncate too much
                slug = truncated[:last_hyphen]
            else:
                slug = truncated

        return slug

    def generate_fallback_slug(
        self,
        entity_type: str,
        entity_id: int,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate fallback slug when title is empty or produces empty slug.

        Args:
            entity_type: Type of entity (work-item, task, project)
            entity_id: Entity ID
            timestamp: Optional timestamp for uniqueness

        Returns:
            Fallback slug

        Examples:
            >>> generate_fallback_slug("work_item", 158)
            'work-item-158'

            >>> generate_fallback_slug("task", 1075, datetime(2025, 10, 25, 14, 30))
            'document-20251025-143000'
        """
        if timestamp:
            # Use timestamp for generic documents
            return f"document-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        else:
            # Use entity type and ID
            # Convert underscores to hyphens for consistency
            entity_slug = entity_type.replace('_', '-')
            return f"{entity_slug}-{entity_id}"

    def determine_base_dir(self, visibility: str, lifecycle: str = "draft") -> str:
        """
        Determine if document goes in private or public location.

        Uses visibility policy engine to determine base directory.

        Rules:
        1. If visibility == "private" → .agentpm/docs/
        2. If visibility == "restricted" → .agentpm/docs/
        3. If visibility == "public" AND lifecycle == "published" → docs/
        4. Default (fallback) → .agentpm/docs/

        Args:
            visibility: Document visibility ("private" | "restricted" | "public")
            lifecycle: Document lifecycle ("draft" | "review" | "approved" | "published" | "archived")

        Returns:
            Base directory path

        Examples:
            >>> determine_base_dir("private", "draft")
            '.agentpm/docs'

            >>> determine_base_dir("restricted", "published")
            '.agentpm/docs'

            >>> determine_base_dir("public", "published")
            'docs'

            >>> determine_base_dir("public", "draft")
            '.agentpm/docs'  # Not published yet
        """
        # Private and restricted always go to .agentpm/docs
        if visibility in ["private", "restricted"]:
            return ".agentpm/docs"

        # Public documents only go to docs/ when published
        if visibility == "public" and lifecycle == "published":
            return "docs"

        # Default: private location
        return ".agentpm/docs"

    def construct_path(
        self,
        base_dir: str,
        category: str,
        doc_type: str,
        filename: str
    ) -> Path:
        """
        Construct canonical document path.

        Args:
            base_dir: Base directory (".agentpm/docs" or "docs")
            category: Top-level category (planning, architecture, etc.)
            doc_type: Document type (requirements, design_doc, etc.)
            filename: Base filename with extension (e.g., "auth-system.md")

        Returns:
            Complete path as Path object

        Examples:
            >>> construct_path(".agentpm/docs", "planning", "requirements", "auth-functional.md")
            Path(".agentpm/docs/planning/requirements/auth-functional.md")

            >>> construct_path("docs", "guides", "user_guide", "getting-started.md")
            Path("docs/guides/user_guide/getting-started.md")
        """
        return Path(base_dir) / category / doc_type / filename

    def resolve_conflicts(
        self,
        proposed_path: Path,
        entity_type: str,
        entity_id: int
    ) -> Path:
        """
        Resolve filename conflicts with numeric suffixes.

        Rules:
        1. Check if proposed path already exists in database
        2. If exists AND same entity → use existing path
        3. If exists AND different entity → append -2, -3, etc.
        4. Keep incrementing until unique path found
        5. Maximum attempts: 1000 (prevents infinite loops)

        Args:
            proposed_path: Initially proposed path
            entity_type: Type of entity creating document
            entity_id: ID of entity

        Returns:
            Unique path (may have numeric suffix)

        Raises:
            RuntimeError: If cannot find unique path after 1000 attempts

        Examples:
            # No conflict
            >>> resolve_conflicts(Path("docs/planning/requirements/auth.md"), "work_item", 158)
            Path("docs/planning/requirements/auth.md")

            # Conflict with different entity
            >>> resolve_conflicts(Path("docs/planning/requirements/auth.md"), "work_item", 159)
            Path("docs/planning/requirements/auth-2.md")

            # Same entity - reuse existing
            >>> resolve_conflicts(Path("docs/planning/requirements/auth.md"), "work_item", 158)
            Path("docs/planning/requirements/auth.md")  # Same entity, same path
        """
        from ..database.methods.document_references import get_document_by_path
        from ..database.enums import EntityType

        # Check if path already exists - first check for same entity
        try:
            entity_type_enum = EntityType(entity_type)
        except (ValueError, KeyError):
            # If entity_type is not a valid enum value, try using it as-is
            entity_type_enum = entity_type if isinstance(entity_type, EntityType) else None

        same_entity_doc = get_document_by_path(
            self.db,
            str(proposed_path),
            entity_type=entity_type_enum,
            entity_id=entity_id
        )

        # If same entity owns this path, reuse it
        if same_entity_doc:
            self.logger.debug(f"Reusing existing path for same entity: {proposed_path}")
            return proposed_path

        # Check if path exists for any entity
        existing_doc = get_document_by_path(self.db, str(proposed_path))

        # If no documents with this path, it's free
        if not existing_doc:
            return proposed_path

        # Path is taken by different entity, find unique variant
        base = proposed_path.stem  # "auth"
        ext = proposed_path.suffix  # ".md"
        directory = proposed_path.parent

        for counter in range(2, 1001):  # Try up to 1000 variants
            candidate = directory / f"{base}-{counter}{ext}"

            existing = get_document_by_path(self.db, str(candidate))
            if not existing:
                self.logger.info(f"Resolved conflict: {proposed_path} → {candidate}")
                return candidate

        # Failed to find unique path
        raise RuntimeError(
            f"Could not find unique path for {proposed_path} after 1000 attempts. "
            f"This indicates a serious issue with path generation."
        )

    def validate_path(self, path: str) -> Tuple[bool, List[str]]:
        """
        Validate generated path for security and platform compatibility.

        Rules:
        - Security: No .. in path (directory traversal)
        - Security: Must be relative (no leading /)
        - Structure: Must start with docs/ or .agentpm/docs/
        - Structure: Minimum 4 parts ({base}/{cat}/{type}/{file})
        - Platform: Length < 260 chars (Windows MAX_PATH)
        - Platform: Valid filename chars (no <>:"|?*)
        - Format: Must end with .md

        Args:
            path: Path to validate (relative string)

        Returns:
            Tuple of (is_valid, error_messages)

        Examples:
            >>> validate_path("docs/planning/requirements/auth.md")
            (True, [])

            >>> validate_path("/etc/passwd")
            (False, ["Path must be relative, not absolute"])

            >>> validate_path("docs/../../../etc/passwd")
            (False, ["Path cannot contain '..' (directory traversal)"])

            >>> validate_path("docs/planning/auth.md")
            (False, ["Path must follow pattern: docs/{category}/{doc_type}/{filename}"])
        """
        errors = []

        # Security: No absolute paths
        if path.startswith('/'):
            errors.append("Path must be relative, not absolute")

        # Security: No directory traversal
        if '..' in path:
            errors.append("Path cannot contain '..' (directory traversal)")

        # Structure: Must be in docs/ hierarchy
        if not (path.startswith('docs/') or path.startswith('.agentpm/docs/')):
            errors.append("Path must be in docs/ or .agentpm/docs/")

        # Structure: Must have minimum depth
        parts = path.split('/')
        min_parts = 4 if path.startswith('docs/') else 5  # .agentpm/docs/ has extra level
        if len(parts) < min_parts:
            errors.append(
                f"Path must follow pattern: docs/{{category}}/{{doc_type}}/{{filename}}. "
                f"Got only {len(parts)} parts: {path}"
            )

        # Platform: Check length (Windows MAX_PATH = 260)
        if len(path) > 260:
            errors.append(f"Path too long ({len(path)} chars, max 260)")

        # Format: Must end with .md
        if not path.endswith('.md'):
            errors.append("Path must end with .md")

        # Platform: Check for invalid characters
        # Windows reserved: < > : " | ? *
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            if char in path:
                errors.append(f"Path contains invalid character: '{char}'")

        # Platform: Check for reserved names (Windows)
        filename = Path(path).name
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'LPT1', 'LPT2']
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved_names:
            errors.append(f"Filename '{filename}' uses reserved name on Windows")

        return len(errors) == 0, errors

    def correct_path(
        self,
        provided_path: Optional[str],
        generated_path: str,
        file_exists_at_provided: bool
    ) -> CorrectionResult:
        """
        Handle path correction when user provides incorrect path.

        Scenarios:
        - No path provided → Use generated_path
        - Correct path → Use provided_path (matches)
        - Wrong path + file exists → Move file to generated_path
        - Wrong path + no file → Ignore provided_path, use generated_path

        Args:
            provided_path: User-provided path (may be wrong)
            generated_path: Algorithm-generated correct path
            file_exists_at_provided: True if file exists at provided_path

        Returns:
            CorrectionResult with final path and move instructions

        Examples:
            # No path provided
            >>> correct_path(None, "docs/planning/requirements/auth.md", False)
            CorrectionResult(
                final_path="docs/planning/requirements/auth.md",
                was_corrected=False,
                needs_move=False
            )

            # Correct path provided
            >>> correct_path("docs/planning/requirements/auth.md", "docs/planning/requirements/auth.md", True)
            CorrectionResult(
                final_path="docs/planning/requirements/auth.md",
                was_corrected=False,
                needs_move=False
            )

            # Wrong path, file exists - move it
            >>> correct_path("docs/old/auth.md", "docs/planning/requirements/auth.md", True)
            CorrectionResult(
                final_path="docs/planning/requirements/auth.md",
                was_corrected=True,
                original_path="docs/old/auth.md",
                correction_reason="Document moved to correct location based on visibility policy",
                needs_move=True,
                move_from="docs/old/auth.md"
            )

            # Wrong path, no file - ignore it
            >>> correct_path("docs/old/auth.md", "docs/planning/requirements/auth.md", False)
            CorrectionResult(
                final_path="docs/planning/requirements/auth.md",
                was_corrected=True,
                original_path="docs/old/auth.md",
                correction_reason="Provided path incorrect, file does not exist at that location",
                needs_move=False
            )
        """
        # Case 1: No path provided
        if not provided_path:
            return CorrectionResult(
                final_path=generated_path,
                was_corrected=False,
                original_path=None,
                correction_reason="",
                needs_move=False,
                move_from=None
            )

        # Case 2: Provided path matches generated (correct)
        if provided_path == generated_path:
            return CorrectionResult(
                final_path=generated_path,
                was_corrected=False,
                original_path=None,
                correction_reason="",
                needs_move=False,
                move_from=None
            )

        # Case 3: Provided path differs from generated

        # Sub-case 3a: File exists at provided path - move it
        if file_exists_at_provided:
            return CorrectionResult(
                final_path=generated_path,
                was_corrected=True,
                original_path=provided_path,
                correction_reason=(
                    f"Document moved from '{provided_path}' to '{generated_path}' "
                    f"to align with visibility policy and category structure"
                ),
                needs_move=True,
                move_from=provided_path
            )

        # Sub-case 3b: File doesn't exist - ignore provided path
        return CorrectionResult(
            final_path=generated_path,
            was_corrected=True,
            original_path=provided_path,
            correction_reason=(
                f"Provided path '{provided_path}' ignored (file does not exist). "
                f"Using generated path '{generated_path}' based on metadata."
            ),
            needs_move=False,
            move_from=None
        )

    def move_file_to_correct_location(self, result: GeneratedPathResult) -> bool:
        """
        Execute file move if correction requires it.

        Args:
            result: GeneratedPathResult with move information

        Returns:
            True if file was moved, False if no move needed

        Raises:
            FileNotFoundError: If source file doesn't exist
            FileExistsError: If target file already exists
            OSError: If move operation fails

        Example:
            >>> result = generator.generate_path(...)
            >>> if result.needs_move:
            ...     generator.move_file_to_correct_location(result)
        """
        if not result.needs_move:
            return False

        from_path = Path(result.move_from)
        to_path = Path(result.final_path)

        # Validate source exists
        if not from_path.exists():
            raise FileNotFoundError(
                f"Cannot move file: source does not exist: {from_path}"
            )

        # Validate target doesn't exist
        if to_path.exists():
            raise FileExistsError(
                f"Cannot move file: target already exists: {to_path}"
            )

        # Create target directory if needed
        to_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        try:
            shutil.move(str(from_path), str(to_path))
            self.logger.info(f"Moved file: {from_path} → {to_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to move file: {from_path} → {to_path}: {e}")
            raise
