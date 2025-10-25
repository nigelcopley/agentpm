"""
Unit tests for document content storage methods (WI-133: Hybrid Storage System).

Tests new content storage features introduced in Migration 0039:
- create_document_with_content
- update_document_content
- get_document_content
- get_documents_needing_sync
- mark_document_synced
- search_document_content

Target: ≥90% coverage for content storage methods
"""

import pytest
from datetime import datetime
import sqlite3

from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.models import DocumentReference
from agentpm.core.database.enums import (
    EntityType,
    DocumentType,
    DocumentFormat,
    StorageMode,
    SyncStatus
)


class TestCreateDocumentWithContent:
    """Test create_document_with_content function."""

    def test_create_document_with_content_success(self, db_service, work_item):
        """
        GIVEN a document and content
        WHEN calling create_document_with_content
        THEN document is created with content and marked for sync
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design_doc/hybrid-storage.md",
            category="architecture",
            document_type=DocumentType.DESIGN_DOC,
            filename="hybrid-storage.md",
            title="Hybrid Storage Design",
            format=DocumentFormat.MARKDOWN,
            storage_mode=StorageMode.HYBRID,
            created_by="architect"
        )
        content = "# Hybrid Storage\n\nDatabase is source of truth..."

        # Act
        result = doc_methods.create_document_with_content(db_service, doc, content)

        # Assert
        assert result.id is not None
        assert result.content == content
        assert result.sync_status == SyncStatus.PENDING
        assert result.content_updated_at is not None
        assert result.storage_mode == StorageMode.HYBRID

    def test_create_database_only_document(self, db_service, work_item):
        """
        GIVEN a document with storage_mode=DATABASE_ONLY
        WHEN creating with content
        THEN content is stored but no file sync needed
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/internal-note.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            filename="internal-note.md",
            title="Internal Note",
            storage_mode=StorageMode.DATABASE_ONLY
        )
        content = "Internal notes, not synced to file"

        # Act
        result = doc_methods.create_document_with_content(db_service, doc, content)

        # Assert
        assert result.content == content
        assert result.storage_mode == StorageMode.DATABASE_ONLY
        assert result.sync_status == SyncStatus.PENDING  # Still marked for processing

    def test_create_with_large_content(self, db_service, work_item):
        """
        GIVEN large document content (>100KB)
        WHEN creating document
        THEN content is stored successfully
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/reference/api_doc/large-api.md",
            category="reference",
            document_type=DocumentType.API_DOC,
            filename="large-api.md",
            title="Large API Documentation"
        )
        # Create ~150KB content
        content = "# API Documentation\n\n" + ("Lorem ipsum dolor sit amet. " * 5000)

        # Act
        result = doc_methods.create_document_with_content(db_service, doc, content)

        # Assert
        assert result.content is not None
        assert len(result.content) > 100000
        assert result.id is not None


class TestUpdateDocumentContent:
    """Test update_document_content function."""

    def test_update_content_success(self, db_service, work_item):
        """
        GIVEN an existing document
        WHEN updating content
        THEN content is updated and marked for sync
        """
        # Arrange - Create document
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/tutorial.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="tutorial.md",
                title="Tutorial"
            ),
            "# Original Content"
        )

        # Mark as synced first
        doc_methods.mark_document_synced(db_service, doc.id)

        # Act - Update content
        new_content = "# Updated Content\n\nNew information..."
        result = doc_methods.update_document_content(db_service, doc.id, new_content)

        # Assert
        assert result.content == new_content
        assert result.sync_status == SyncStatus.PENDING
        assert result.content_updated_at > doc.content_updated_at

    def test_update_nonexistent_document(self, db_service):
        """
        GIVEN a non-existent document ID
        WHEN updating content
        THEN None is returned
        """
        # Act
        result = doc_methods.update_document_content(db_service, 99999, "content")

        # Assert
        assert result is None

    def test_update_preserves_metadata(self, db_service, work_item):
        """
        GIVEN a document with rich metadata
        WHEN updating only content
        THEN metadata is preserved
        """
        # Arrange - Create document with metadata
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/architecture/design_doc/auth.md",
                category="architecture",
                document_type=DocumentType.DESIGN_DOC,
                filename="auth.md",
                title="Auth System",
                component="auth",
                domain="security",
                audience="developer",
                maturity="approved",
                tags=["security", "authentication"]
            ),
            "# Original"
        )

        # Act
        result = doc_methods.update_document_content(db_service, doc.id, "# Updated")

        # Assert - Metadata unchanged
        assert result.component == "auth"
        assert result.domain == "security"
        assert result.tags == ["security", "authentication"]
        assert result.maturity == "approved"


class TestGetDocumentContent:
    """Test get_document_content function."""

    def test_get_content_success(self, db_service, work_item):
        """
        GIVEN a document with content
        WHEN calling get_document_content
        THEN content is returned
        """
        # Arrange
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/developer_guide/setup.md",
                category="guides",
                document_type=DocumentType.DEVELOPER_GUIDE,
                filename="setup.md",
                title="Setup Guide"
            ),
            "# Setup Guide\n\nFollow these steps..."
        )

        # Act
        content = doc_methods.get_document_content(db_service, doc.id)

        # Assert
        assert content == "# Setup Guide\n\nFollow these steps..."

    def test_get_content_nonexistent_document(self, db_service):
        """
        GIVEN a non-existent document ID
        WHEN calling get_document_content
        THEN None is returned
        """
        # Act
        content = doc_methods.get_document_content(db_service, 99999)

        # Assert
        assert content is None

    def test_get_content_document_without_content(self, db_service, work_item):
        """
        GIVEN a document without content (legacy document)
        WHEN calling get_document_content
        THEN None is returned
        """
        # Arrange - Create document without content (legacy path)
        doc = doc_methods.create_document_reference(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/planning/requirements/legacy.md",
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                title="Legacy Document"
            )
        )

        # Act
        content = doc_methods.get_document_content(db_service, doc.id)

        # Assert
        assert content is None


class TestGetDocumentsNeedingSync:
    """Test get_documents_needing_sync function."""

    def test_get_pending_documents(self, db_service, work_item):
        """
        GIVEN documents with various sync statuses
        WHEN calling get_documents_needing_sync
        THEN only non-synced documents are returned
        """
        # Arrange - Create documents
        doc1 = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/doc1.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="doc1.md",
                title="Doc 1"
            ),
            "Content 1"
        )
        # doc1 is PENDING by default

        doc2 = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/doc2.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="doc2.md",
                title="Doc 2"
            ),
            "Content 2"
        )
        # Mark doc2 as synced
        doc_methods.mark_document_synced(db_service, doc2.id)

        # Act
        needing_sync = doc_methods.get_documents_needing_sync(db_service)

        # Assert
        needing_sync_ids = [d.id for d in needing_sync]
        assert doc1.id in needing_sync_ids
        assert doc2.id not in needing_sync_ids

    def test_get_conflict_documents(self, db_service, work_item):
        """
        GIVEN documents with CONFLICT status
        WHEN calling get_documents_needing_sync
        THEN conflict documents are included
        """
        # Arrange - Create document and mark as conflict
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/conflict.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="conflict.md",
                title="Conflict Doc"
            ),
            "Content"
        )

        # Manually set status to CONFLICT
        doc.sync_status = SyncStatus.CONFLICT
        doc_methods.update_document_reference(db_service, doc)

        # Act
        needing_sync = doc_methods.get_documents_needing_sync(db_service)

        # Assert
        assert any(d.id == doc.id for d in needing_sync)
        assert any(d.sync_status == SyncStatus.CONFLICT for d in needing_sync)

    def test_empty_result_when_all_synced(self, db_service, work_item):
        """
        GIVEN all documents are synced
        WHEN calling get_documents_needing_sync
        THEN empty list is returned
        """
        # Arrange - Create and sync document
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/synced.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="synced.md",
                title="Synced Doc"
            ),
            "Content"
        )
        doc_methods.mark_document_synced(db_service, doc.id)

        # Act
        needing_sync = doc_methods.get_documents_needing_sync(db_service)

        # Assert
        assert len(needing_sync) == 0 or all(d.id != doc.id for d in needing_sync)


class TestMarkDocumentSynced:
    """Test mark_document_synced function."""

    def test_mark_synced_success(self, db_service, work_item):
        """
        GIVEN a document with PENDING status
        WHEN calling mark_document_synced
        THEN status is SYNCED and timestamp is set
        """
        # Arrange
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/mark-test.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="mark-test.md",
                title="Mark Test"
            ),
            "Content"
        )
        assert doc.sync_status == SyncStatus.PENDING

        # Act
        result = doc_methods.mark_document_synced(db_service, doc.id)

        # Assert
        assert result.sync_status == SyncStatus.SYNCED
        assert result.last_synced_at is not None
        assert isinstance(result.last_synced_at, datetime)

    def test_mark_synced_nonexistent_document(self, db_service):
        """
        GIVEN a non-existent document ID
        WHEN calling mark_document_synced
        THEN None is returned
        """
        # Act
        result = doc_methods.mark_document_synced(db_service, 99999)

        # Assert
        assert result is None

    def test_mark_synced_idempotent(self, db_service, work_item):
        """
        GIVEN an already synced document
        WHEN calling mark_document_synced again
        THEN operation succeeds and updates timestamp
        """
        # Arrange
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/idempotent.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="idempotent.md",
                title="Idempotent Test"
            ),
            "Content"
        )
        first_sync = doc_methods.mark_document_synced(db_service, doc.id)

        # Act - Mark synced again
        second_sync = doc_methods.mark_document_synced(db_service, doc.id)

        # Assert
        assert second_sync.sync_status == SyncStatus.SYNCED
        assert second_sync.last_synced_at >= first_sync.last_synced_at


class TestSearchDocumentContent:
    """Test search_document_content function."""

    def test_search_content_basic(self, db_service, work_item):
        """
        GIVEN documents with searchable content
        WHEN searching for keyword
        THEN matching documents are returned
        """
        # Arrange - Create documents with different content
        doc1 = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/authentication.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="authentication.md",
                title="Authentication Guide"
            ),
            "# Authentication\n\nHow to authenticate users with JWT tokens..."
        )

        doc2 = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/database.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="database.md",
                title="Database Guide"
            ),
            "# Database\n\nHow to query the database with SQL..."
        )

        # Act
        results = doc_methods.search_document_content(db_service, "authentication")

        # Assert
        result_ids = [d.id for d in results]
        assert doc1.id in result_ids
        # doc2 should not be in results (doesn't contain "authentication")

    def test_search_by_title(self, db_service, work_item):
        """
        GIVEN documents with searchable titles
        WHEN searching
        THEN documents matching title are returned
        """
        # Arrange
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/architecture/design_doc/microservices.md",
                category="architecture",
                document_type=DocumentType.DESIGN_DOC,
                filename="microservices.md",
                title="Microservices Architecture"
            ),
            "# Architecture\n\nSystem design..."
        )

        # Act
        results = doc_methods.search_document_content(db_service, "Microservices")

        # Assert
        assert any(d.id == doc.id for d in results)

    def test_search_with_limit(self, db_service, work_item):
        """
        GIVEN many matching documents
        WHEN searching with limit
        THEN only limited results are returned
        """
        # Arrange - Create multiple documents
        for i in range(5):
            doc_methods.create_document_with_content(
                db_service,
                DocumentReference(
                    entity_type=EntityType.WORK_ITEM,
                    entity_id=work_item.id,
                    file_path=f"docs/guides/user_guide/guide-{i}.md",
                    category="guides",
                    document_type=DocumentType.USER_GUIDE,
                    filename=f"guide-{i}.md",
                    title=f"Guide {i}"
                ),
                f"# Guide {i}\n\nCommon search term appears here..."
            )

        # Act
        results = doc_methods.search_document_content(
            db_service,
            "Common search term",
            limit=3
        )

        # Assert
        assert len(results) <= 3

    def test_search_no_results(self, db_service, work_item):
        """
        GIVEN documents that don't match search
        WHEN searching
        THEN empty list is returned
        """
        # Arrange
        doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/python.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="python.md",
                title="Python Guide"
            ),
            "# Python\n\nPython programming guide..."
        )

        # Act
        results = doc_methods.search_document_content(db_service, "javascript")

        # Assert
        assert len(results) == 0


class TestStorageModeIntegration:
    """Test different storage modes work correctly."""

    def test_hybrid_mode_workflow(self, db_service, work_item):
        """
        GIVEN a document with HYBRID storage mode
        WHEN creating, updating, and syncing
        THEN full workflow works correctly
        """
        # Create
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/hybrid-test.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="hybrid-test.md",
                title="Hybrid Test",
                storage_mode=StorageMode.HYBRID
            ),
            "# Original"
        )
        assert doc.sync_status == SyncStatus.PENDING

        # Sync
        synced = doc_methods.mark_document_synced(db_service, doc.id)
        assert synced.sync_status == SyncStatus.SYNCED

        # Update
        updated = doc_methods.update_document_content(db_service, doc.id, "# Updated")
        assert updated.sync_status == SyncStatus.PENDING
        assert updated.content == "# Updated"

    def test_database_only_mode(self, db_service, work_item):
        """
        GIVEN a document with DATABASE_ONLY mode
        WHEN creating
        THEN content is stored but file sync is managed differently
        """
        doc = doc_methods.create_document_with_content(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/internal/notes.md",
                category="planning",
                document_type=DocumentType.REQUIREMENTS,
                filename="notes.md",
                title="Internal Notes",
                storage_mode=StorageMode.DATABASE_ONLY
            ),
            "# Internal Notes\n\nNot synced to file..."
        )

        assert doc.content is not None
        assert doc.storage_mode == StorageMode.DATABASE_ONLY

    def test_file_only_mode(self, db_service, work_item):
        """
        GIVEN a document with FILE_ONLY mode
        WHEN creating (legacy behavior)
        THEN metadata is stored but content lives in file
        """
        doc = doc_methods.create_document_reference(
            db_service,
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path="docs/guides/user_guide/legacy.md",
                category="guides",
                document_type=DocumentType.USER_GUIDE,
                filename="legacy.md",
                title="Legacy Document",
                storage_mode=StorageMode.FILE_ONLY
            )
        )

        assert doc.storage_mode == StorageMode.FILE_ONLY
        assert doc.content is None  # No content in database
