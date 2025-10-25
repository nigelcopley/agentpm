"""
Document Publishing Workflow Service

Manages document lifecycle: draft → review → approved → published → archived
Handles file copying between private/public locations, maintains audit log, updates lifecycle stages.

Implements specification from: docs/architecture/design_doc/publishing-workflow-specification.md

Pattern: Service layer with type-safe operations
Architecture: Three-layer (Models → Adapters → Methods → Service)
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import shutil
import hashlib
import logging

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.document_reference import DocumentReference
from agentpm.core.database.models.document_audit_log import DocumentAuditLog
from agentpm.core.database.enums import DocumentLifecycle, DocumentVisibility
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.adapters.document_audit_adapter import DocumentAuditAdapter


logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    """Result of publish operation"""
    success: bool
    document_id: int
    source_path: str
    destination_path: Optional[str]
    lifecycle_stage: str
    error: Optional[str] = None


@dataclass
class SyncResult:
    """Result of sync operation"""
    stats: Dict[str, Any]
    orphaned_files: List[Path]
    dry_run: bool


class PublishError(Exception):
    """Publishing workflow error"""
    pass


class ValidationError(Exception):
    """Validation error"""
    pass


class DocumentPublisher:
    """
    Manages document publishing workflow and lifecycle transitions.

    Implements state machine for document lifecycle:
    DRAFT → REVIEW → APPROVED → PUBLISHED → ARCHIVED

    Also handles REJECTED state which auto-reverts to DRAFT.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize document publisher.

        Args:
            db: DatabaseService instance
        """
        self.db = db
        self.logger = logger

    def submit_review(
        self,
        document_id: int,
        reviewer_id: Optional[str] = None,
        priority: str = "normal"
    ) -> bool:
        """
        Submit document for review.

        Transitions: DRAFT → REVIEW

        Actions:
        1. Validate can transition (must be DRAFT)
        2. Update lifecycle_stage = 'review'
        3. Set review_status = 'pending'
        4. Assign reviewer (or auto-assign from work item)
        5. Set reviewer_assigned_at timestamp
        6. Create audit log entry
        7. Optionally notify reviewer

        Args:
            document_id: Document reference ID
            reviewer_id: Optional reviewer email/ID (auto-assign if None)
            priority: Review priority (high|normal|low)

        Returns:
            True if successful

        Raises:
            ValidationError: If document cannot transition to review
        """
        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        # Validate current state
        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)
        if current_lifecycle != DocumentLifecycle.DRAFT.value:
            raise ValidationError(
                f"Document must be in DRAFT state to submit for review. "
                f"Current state: {current_lifecycle}"
            )

        # Auto-assign reviewer from work item if not provided
        if not reviewer_id and doc.work_item_id:
            reviewer_id = self._auto_assign_reviewer(doc.work_item_id)

        # Update document
        doc.lifecycle_stage = DocumentLifecycle.REVIEW.value
        doc.review_status = "pending"
        doc.reviewer_id = reviewer_id
        doc.reviewer_assigned_at = datetime.utcnow()

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log
        self._create_audit_log_entry(
            document_id=document_id,
            action="submit_review",
            actor="system",  # TODO: Get current user
            from_state=DocumentLifecycle.DRAFT.value,
            to_state=DocumentLifecycle.REVIEW.value,
            details={
                "reviewer_id": reviewer_id,
                "priority": priority,
                "auto_assigned": reviewer_id is not None and not reviewer_id
            },
            comment=None
        )

        self.logger.info(f"Document {document_id} submitted for review (reviewer: {reviewer_id})")
        return True

    def approve(
        self,
        document_id: int,
        reviewer_id: str,
        comment: Optional[str] = None,
        publish_now: bool = False
    ) -> bool:
        """
        Approve document after review.

        Transitions: REVIEW → APPROVED

        Actions:
        1. Validate can transition (must be REVIEW)
        2. Validate reviewer authorization
        3. Update lifecycle_stage = 'approved'
        4. Set review_status = 'approved'
        5. Set review_comment
        6. Set review_completed_at timestamp
        7. Create audit log entry
        8. Check auto-publish rules
        9. If should_auto_publish OR publish_now → call publish()

        Args:
            document_id: Document reference ID
            reviewer_id: Reviewer email/ID (must match assigned reviewer)
            comment: Optional approval comment
            publish_now: Force immediate publish (bypass auto-publish logic)

        Returns:
            True if successful

        Raises:
            ValidationError: If document cannot be approved
        """
        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        # Validate current state
        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)
        if current_lifecycle != DocumentLifecycle.REVIEW.value:
            raise ValidationError(
                f"Document must be in REVIEW state to approve. "
                f"Current state: {current_lifecycle}"
            )

        # Validate reviewer authorization
        assigned_reviewer = getattr(doc, 'reviewer_id', None)
        if assigned_reviewer and assigned_reviewer != reviewer_id:
            raise ValidationError(
                f"Reviewer {reviewer_id} not authorized. "
                f"Assigned reviewer: {assigned_reviewer}"
            )

        # Update document
        doc.lifecycle_stage = DocumentLifecycle.APPROVED.value
        doc.review_status = "approved"
        doc.review_comment = comment
        doc.review_completed_at = datetime.utcnow()

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log
        self._create_audit_log_entry(
            document_id=document_id,
            action="approve",
            actor=reviewer_id,
            from_state=DocumentLifecycle.REVIEW.value,
            to_state=DocumentLifecycle.APPROVED.value,
            details={
                "review_duration_hours": self._calculate_review_duration(doc)
            },
            comment=comment
        )

        self.logger.info(f"Document {document_id} approved by {reviewer_id}")

        # Check auto-publish rules
        if publish_now or self._should_auto_publish(doc):
            try:
                result = self.publish(document_id, actor=reviewer_id, trigger="auto" if not publish_now else "manual")
                if result.success:
                    self.logger.info(f"Document {document_id} auto-published after approval")
                else:
                    self.logger.warning(f"Auto-publish failed for document {document_id}: {result.error}")
            except Exception as e:
                self.logger.error(f"Auto-publish error for document {document_id}: {e}")

        return True

    def reject(
        self,
        document_id: int,
        reviewer_id: str,
        reason: str
    ) -> bool:
        """
        Reject document after review.

        Transitions: REVIEW → REJECTED → DRAFT (automatic)

        Actions:
        1. Validate can transition (must be REVIEW)
        2. Update lifecycle_stage = 'rejected'
        3. Set review_status = 'rejected'
        4. Set review_comment = reason
        5. Create audit log entry
        6. Auto-revert to DRAFT for rework
        7. Notify author with rejection reason

        Args:
            document_id: Document reference ID
            reviewer_id: Reviewer email/ID
            reason: Rejection reason (required)

        Returns:
            True if successful

        Raises:
            ValidationError: If document cannot be rejected
        """
        if not reason or not reason.strip():
            raise ValidationError("Rejection reason is required")

        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        # Validate current state
        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)
        if current_lifecycle != DocumentLifecycle.REVIEW.value:
            raise ValidationError(
                f"Document must be in REVIEW state to reject. "
                f"Current state: {current_lifecycle}"
            )

        # Update to rejected first
        doc.lifecycle_stage = DocumentLifecycle.REJECTED.value
        doc.review_status = "rejected"
        doc.review_comment = reason
        doc.review_completed_at = datetime.utcnow()

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log for rejection
        self._create_audit_log_entry(
            document_id=document_id,
            action="reject",
            actor=reviewer_id,
            from_state=DocumentLifecycle.REVIEW.value,
            to_state=DocumentLifecycle.REJECTED.value,
            details={},
            comment=reason
        )

        # Auto-revert to DRAFT for rework
        doc.lifecycle_stage = DocumentLifecycle.DRAFT.value

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log for auto-revert
        self._create_audit_log_entry(
            document_id=document_id,
            action="auto_revert_to_draft",
            actor="system",
            from_state=DocumentLifecycle.REJECTED.value,
            to_state=DocumentLifecycle.DRAFT.value,
            details={"reason": "Auto-revert after rejection for rework"},
            comment="Document reverted to DRAFT for rework"
        )

        self.logger.info(f"Document {document_id} rejected by {reviewer_id} and reverted to DRAFT")
        return True

    def publish(
        self,
        document_id: int,
        actor: str = "system",
        trigger: str = "manual"
    ) -> PublishResult:
        """
        Publish document to public location.

        Transitions: APPROVED → PUBLISHED

        Actions:
        1. Validate can publish (must be APPROVED, visibility=public)
        2. Get source path (.agentpm/docs/...)
        3. Get destination path (docs/...)
        4. Create destination directory if needed
        5. Copy file preserving content
        6. Update lifecycle_stage = 'published'
        7. Set published_path and published_date
        8. Create audit log entry
        9. Optionally trigger external sync (GitHub Pages, etc.)

        Args:
            document_id: Document reference ID
            actor: User/agent performing publish
            trigger: Trigger type (manual, auto, phase_change)

        Returns:
            PublishResult with success status and paths

        Raises:
            ValidationError: If document cannot be published
        """
        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        # Validate can publish
        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)
        if current_lifecycle != DocumentLifecycle.APPROVED.value:
            raise ValidationError(
                f"Document must be APPROVED to publish. "
                f"Current state: {current_lifecycle}"
            )

        visibility = getattr(doc, 'visibility', DocumentVisibility.PRIVATE.value)
        if visibility != DocumentVisibility.PUBLIC.value:
            raise ValidationError(
                f"Only PUBLIC documents can be published. "
                f"Current visibility: {visibility}"
            )

        if not doc.content:
            raise ValidationError("Document has no content to publish")

        # Determine paths
        source_path = Path(doc.computed_path)
        dest_path = Path(f"docs/{doc.category}/{doc.document_type.value}/{doc.filename}")

        # Ensure source exists (sync from database if needed)
        if not source_path.exists():
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(doc.content, encoding='utf-8')

        # Create destination directory
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            error_msg = f"Failed to copy file: {e}"
            self.logger.error(error_msg)
            return PublishResult(
                success=False,
                document_id=document_id,
                source_path=str(source_path),
                destination_path=None,
                lifecycle_stage=current_lifecycle,
                error=error_msg
            )

        # Update document
        doc.lifecycle_stage = DocumentLifecycle.PUBLISHED.value
        doc.published_path = str(dest_path)
        doc.published_date = datetime.utcnow()

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return PublishResult(
                success=False,
                document_id=document_id,
                source_path=str(source_path),
                destination_path=str(dest_path),
                lifecycle_stage=current_lifecycle,
                error="Failed to update document in database"
            )

        # Create audit log
        self._create_audit_log_entry(
            document_id=document_id,
            action="publish",
            actor=actor,
            from_state=DocumentLifecycle.APPROVED.value,
            to_state=DocumentLifecycle.PUBLISHED.value,
            details={
                "source": str(source_path),
                "destination": str(dest_path),
                "trigger": trigger
            },
            comment=f"Published via {trigger} trigger"
        )

        self.logger.info(f"Document {document_id} published to {dest_path}")

        return PublishResult(
            success=True,
            document_id=document_id,
            source_path=str(source_path),
            destination_path=str(dest_path),
            lifecycle_stage=DocumentLifecycle.PUBLISHED.value,
            error=None
        )

    def unpublish(
        self,
        document_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """
        Remove document from public location.

        Transitions: PUBLISHED → APPROVED

        Actions:
        1. Validate is published
        2. Remove file from public docs/ directory
        3. Update lifecycle_stage = 'approved'
        4. Set unpublished_date
        5. Keep source in .agentpm/docs/ (source of truth)
        6. Create audit log entry

        Args:
            document_id: Document reference ID
            reason: Optional reason for unpublishing

        Returns:
            True if successful

        Raises:
            ValidationError: If document cannot be unpublished
        """
        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        # Validate current state
        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)
        if current_lifecycle != DocumentLifecycle.PUBLISHED.value:
            raise ValidationError(
                f"Document is not published. Current state: {current_lifecycle}"
            )

        # Remove public file
        published_path = getattr(doc, 'published_path', None)
        if published_path:
            public_path = Path(published_path)
            if public_path.exists():
                try:
                    public_path.unlink()
                    self.logger.info(f"Removed public file: {public_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove public file {public_path}: {e}")

        # Update document (revert to approved, keep published_path for reference)
        doc.lifecycle_stage = DocumentLifecycle.APPROVED.value
        doc.unpublished_date = datetime.utcnow()

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log
        self._create_audit_log_entry(
            document_id=document_id,
            action="unpublish",
            actor="system",  # TODO: Get current user
            from_state=DocumentLifecycle.PUBLISHED.value,
            to_state=DocumentLifecycle.APPROVED.value,
            details={
                "removed_path": published_path,
                "reason": reason
            },
            comment=reason
        )

        self.logger.info(f"Document {document_id} unpublished")
        return True

    def archive(
        self,
        document_id: int,
        remove_public: bool = True
    ) -> bool:
        """
        Archive document (no longer active).

        Transitions: ANY → ARCHIVED

        Actions:
        1. Update lifecycle_stage = 'archived'
        2. If remove_public and published → unpublish first
        3. Create audit log entry
        4. Document stays in .agentpm/docs/ but marked archived

        Args:
            document_id: Document reference ID
            remove_public: If True and published, remove from public docs/

        Returns:
            True if successful
        """
        doc = doc_methods.get_document_reference(self.db, document_id)
        if not doc:
            raise ValidationError(f"Document {document_id} not found")

        current_lifecycle = getattr(doc, 'lifecycle_stage', DocumentLifecycle.DRAFT.value)

        # Unpublish if needed
        if remove_public and current_lifecycle == DocumentLifecycle.PUBLISHED.value:
            self.unpublish(document_id, reason="Archiving document")

        # Update document
        doc.lifecycle_stage = DocumentLifecycle.ARCHIVED.value

        updated = doc_methods.update_document_reference(self.db, doc)
        if not updated:
            return False

        # Create audit log
        self._create_audit_log_entry(
            document_id=document_id,
            action="archive",
            actor="system",  # TODO: Get current user
            from_state=current_lifecycle,
            to_state=DocumentLifecycle.ARCHIVED.value,
            details={"removed_public": remove_public},
            comment="Document archived"
        )

        self.logger.info(f"Document {document_id} archived")
        return True

    def sync_all(self, dry_run: bool = False) -> SyncResult:
        """
        Sync all published documents.

        Checks:
        1. Query all docs where lifecycle = 'published'
        2. For each:
           a. Verify source exists in .agentpm/docs/
           b. Verify destination matches published_path
           c. Compare content checksums
           d. If mismatch: re-copy (or report in dry-run)
        3. Find orphaned public docs (in docs/ but not in DB)
        4. Report sync status

        Args:
            dry_run: If True, report issues without making changes

        Returns:
            SyncResult with counts and any issues
        """
        # Query published documents
        published_docs = self._get_published_documents()

        stats = {
            "checked": 0,
            "synced": 0,
            "missing_source": [],
            "missing_dest": [],
            "content_mismatch": [],
            "synced_files": [],
        }

        for doc in published_docs:
            stats["checked"] += 1

            source_path = Path(doc.computed_path)
            dest_path = Path(getattr(doc, 'published_path', ''))

            # Check source exists
            if not source_path.exists():
                stats["missing_source"].append(str(source_path))
                if not dry_run:
                    # Sync from database to file
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    if doc.content:
                        source_path.write_text(doc.content, encoding='utf-8')
                continue

            # Check destination exists
            if not dest_path.exists():
                stats["missing_dest"].append(str(dest_path))
                if not dry_run:
                    # Re-publish
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    stats["synced_files"].append(str(dest_path))
                continue

            # Compare content checksums
            source_hash = self._calculate_file_hash(source_path)
            dest_hash = self._calculate_file_hash(dest_path)

            if source_hash != dest_hash:
                stats["content_mismatch"].append({
                    "source": str(source_path),
                    "dest": str(dest_path),
                    "source_hash": source_hash,
                    "dest_hash": dest_hash,
                })
                if not dry_run:
                    # Re-sync
                    shutil.copy2(source_path, dest_path)
                    doc.content_hash = source_hash
                    doc_methods.update_document_reference(self.db, doc)
                    stats["synced_files"].append(str(dest_path))

            stats["synced"] += 1

        # Find orphaned files
        orphaned = self._find_orphaned_public_docs(published_docs)

        return SyncResult(
            stats=stats,
            orphaned_files=orphaned,
            dry_run=dry_run
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _create_audit_log_entry(
        self,
        document_id: int,
        action: str,
        actor: str,
        from_state: Optional[str],
        to_state: Optional[str],
        details: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None
    ):
        """
        Create audit log entry for document action.

        Inserts into document_audit_log table.
        """
        try:
            entry = DocumentAuditLog(
                document_id=document_id,
                action=action,
                actor=actor,
                from_state=from_state,
                to_state=to_state,
                details=details,
                comment=comment
            )
            DocumentAuditAdapter.create(self.db, entry)
            self.logger.info(
                f"Audit: doc={document_id}, action={action}, actor={actor}, "
                f"{from_state}→{to_state}"
            )
        except Exception as e:
            # Don't fail the operation if audit log fails
            self.logger.error(f"Failed to create audit log entry: {e}")

    def _auto_assign_reviewer(self, work_item_id: int) -> Optional[str]:
        """Auto-assign reviewer from work item."""
        # TODO: Implement work item lookup and reviewer extraction
        return None

    def _calculate_review_duration(self, doc: DocumentReference) -> Optional[float]:
        """Calculate review duration in hours."""
        assigned_at = getattr(doc, 'reviewer_assigned_at', None)
        completed_at = getattr(doc, 'review_completed_at', None)

        if not assigned_at or not completed_at:
            return None

        duration = completed_at - assigned_at
        return duration.total_seconds() / 3600.0  # Convert to hours

    def _should_auto_publish(self, doc: DocumentReference) -> bool:
        """Check if document should be auto-published based on rules."""
        # Type-based auto-publish rules
        auto_publish_types = {
            "user_guide": True,
            "admin_guide": True,
            "api_doc": True,
            "specification": True,
        }

        doc_type = doc.document_type.value if doc.document_type else None
        visibility = getattr(doc, 'visibility', DocumentVisibility.PRIVATE.value)

        # Must be public to auto-publish
        if visibility != DocumentVisibility.PUBLIC.value:
            return False

        # Check type-based rules
        return auto_publish_types.get(doc_type, False)

    def _get_published_documents(self) -> List[DocumentReference]:
        """Get all published documents."""
        # Query documents with lifecycle_stage = 'published'
        # TODO: Add lifecycle_stage filter to list_document_references
        all_docs = doc_methods.list_document_references(self.db)
        return [
            doc for doc in all_docs
            if getattr(doc, 'lifecycle_stage', '') == DocumentLifecycle.PUBLISHED.value
        ]

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _find_orphaned_public_docs(self, known_docs: List[DocumentReference]) -> List[Path]:
        """Identify files in docs/ not tracked in database."""
        known_paths = {
            Path(getattr(doc, 'published_path', ''))
            for doc in known_docs
            if getattr(doc, 'published_path', None)
        }

        docs_dir = Path("docs")
        if not docs_dir.exists():
            return []

        all_public_files = list(docs_dir.rglob("*.md"))

        orphaned = [f for f in all_public_files if f not in known_paths]
        return orphaned
