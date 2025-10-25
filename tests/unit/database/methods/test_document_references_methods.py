"""
Comprehensive unit tests for document_references methods module.

Tests CRUD operations, filters, search functionality, and edge cases.
Target: ≥90% coverage for agentpm/core/database/methods/document_references.py
"""

import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime
import sqlite3

from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.models import DocumentReference
from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat


class TestCreateDocumentReference:
    """Test create_document_reference function."""

    def test_create_document_reference_success(self, db_service, work_item):
        """
        GIVEN a valid DocumentReference model
        WHEN calling create_document_reference
        THEN document is created and returned with ID
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS,
            title="Test Requirements",
            format=DocumentFormat.MARKDOWN,
            created_by="test-user"
        )

        # Act
        result = doc_methods.create_document_reference(db_service, doc)

        # Assert
        assert result.id is not None
        assert result.title == "Test Requirements"
        assert result.file_path == "docs/planning/requirements/test.md"
        assert result.entity_type == EntityType.WORK_ITEM
        assert result.entity_id == work_item.id

    def test_create_document_with_all_metadata(self, db_service, work_item):
        """
        GIVEN DocumentReference with all optional metadata
        WHEN creating document
        THEN all metadata is persisted
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/system.md",
            category="architecture",
            document_type=DocumentType.DESIGN,
            title="System Design",
            description="Complete system architecture",
            file_size_bytes=4096,
            content_hash="abc123",
            format=DocumentFormat.MARKDOWN,
            segment_type="technical",
            component="auth",
            domain="security",
            audience="developer",
            maturity="approved",
            priority="high",
            tags=["architecture", "security"],
            phase="I1",
            work_item_id=work_item.id,
            created_by="architect"
        )

        # Act
        result = doc_methods.create_document_reference(db_service, doc)

        # Assert
        assert result.id is not None
        assert result.tags == ["architecture", "security"]
        assert result.component == "auth"
        assert result.maturity == "approved"
        assert result.phase == "I1"


class TestGetDocumentReference:
    """Test get_document_reference function."""

    def test_get_existing_document(self, db_service, work_item):
        """
        GIVEN an existing document ID
        WHEN calling get_document_reference
        THEN document is returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )
        created = doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_document_reference(db_service, created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.file_path == created.file_path

    def test_get_nonexistent_document_returns_none(self, db_service):
        """
        GIVEN a non-existent document ID
        WHEN calling get_document_reference
        THEN None is returned
        """
        # Act
        result = doc_methods.get_document_reference(db_service, 99999)

        # Assert
        assert result is None


class TestListDocumentReferences:
    """Test list_document_references function with filters."""

    def test_list_all_documents(self, db_service, work_item):
        """
        GIVEN multiple documents in database
        WHEN listing without filters
        THEN all documents are returned
        """
        # Arrange
        for i in range(3):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning",
                document_type=DocumentType.REQUIREMENTS
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.list_document_references(db_service)

        # Assert
        assert len(result) >= 3

    def test_list_filtered_by_entity_type(self, db_service, work_item, task):
        """
        GIVEN documents for different entity types
        WHEN filtering by entity_type
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/wi.md",
            category="planning"
        )
        doc2 = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=task.id,
            file_path="docs/planning/requirements/task.md",
            category="planning"
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.list_document_references(
            db_service,
            entity_type=EntityType.WORK_ITEM
        )

        # Assert
        assert all(doc.entity_type == EntityType.WORK_ITEM for doc in result)

    def test_list_filtered_by_entity_id(self, db_service, work_item):
        """
        GIVEN documents for different entities
        WHEN filtering by entity_id
        THEN only documents for that entity are returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.list_document_references(
            db_service,
            entity_id=work_item.id
        )

        # Assert
        assert all(doc.entity_id == work_item.id for doc in result)

    def test_list_filtered_by_document_type(self, db_service, work_item):
        """
        GIVEN documents of different types
        WHEN filtering by document_type
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/test.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.list_document_references(
            db_service,
            document_type=DocumentType.REQUIREMENTS
        )

        # Assert
        assert all(doc.document_type == DocumentType.REQUIREMENTS for doc in result)

    def test_list_filtered_by_format(self, db_service, work_item):
        """
        GIVEN documents in different formats
        WHEN filtering by format
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            format=DocumentFormat.MARKDOWN
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.yaml",
            category="planning",
            format=DocumentFormat.YAML
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.list_document_references(
            db_service,
            format=DocumentFormat.MARKDOWN
        )

        # Assert
        assert all(doc.format == DocumentFormat.MARKDOWN for doc in result)

    def test_list_filtered_by_created_by(self, db_service, work_item):
        """
        GIVEN documents created by different users
        WHEN filtering by created_by
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test1.md",
            category="planning",
            created_by="alice"
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test2.md",
            category="planning",
            created_by="bob"
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.list_document_references(
            db_service,
            created_by="alice"
        )

        # Assert
        assert all(doc.created_by == "alice" for doc in result)

    def test_list_with_limit(self, db_service, work_item):
        """
        GIVEN many documents
        WHEN listing with limit
        THEN only limited number returned
        """
        # Arrange
        for i in range(10):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.list_document_references(db_service, limit=5)

        # Assert
        assert len(result) <= 5


class TestUpdateDocumentReference:
    """Test update_document_reference function."""

    def test_update_document_title(self, db_service, work_item):
        """
        GIVEN an existing document
        WHEN updating title
        THEN title is updated and timestamp changed
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            title="Original Title"
        )
        created = doc_methods.create_document_reference(db_service, doc)

        # Act
        created.title = "Updated Title"
        updated = doc_methods.update_document_reference(db_service, created)

        # Assert
        assert updated.title == "Updated Title"
        assert updated.id == created.id

    def test_update_document_without_id_returns_none(self, db_service):
        """
        GIVEN a DocumentReference without ID
        WHEN calling update
        THEN None is returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            file_path="docs/planning/requirements/test.md",
            category="planning"
        )
        doc.id = None

        # Act
        result = doc_methods.update_document_reference(db_service, doc)

        # Assert
        assert result is None


class TestDeleteDocumentReference:
    """Test delete_document_reference function."""

    def test_delete_existing_document_returns_true(self, db_service, work_item):
        """
        GIVEN an existing document
        WHEN deleting by ID
        THEN document is deleted and True returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning"
        )
        created = doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.delete_document_reference(db_service, created.id)

        # Assert
        assert result is True
        assert doc_methods.get_document_reference(db_service, created.id) is None

    def test_delete_nonexistent_document_returns_false(self, db_service):
        """
        GIVEN a non-existent document ID
        WHEN deleting
        THEN False is returned
        """
        # Act
        result = doc_methods.delete_document_reference(db_service, 99999)

        # Assert
        assert result is False


class TestGetDocumentsByEntity:
    """Test get_documents_by_entity convenience function."""

    def test_get_documents_by_entity_all_types(self, db_service, work_item):
        """
        GIVEN documents for an entity
        WHEN getting by entity
        THEN all documents for that entity are returned
        """
        # Arrange
        for i in range(3):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_documents_by_entity(
            db_service,
            EntityType.WORK_ITEM,
            work_item.id
        )

        # Assert
        assert len(result) >= 3
        assert all(doc.entity_id == work_item.id for doc in result)

    def test_get_documents_by_entity_filtered_by_type(self, db_service, work_item):
        """
        GIVEN documents of different types for an entity
        WHEN getting by entity and document_type
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/test.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.get_documents_by_entity(
            db_service,
            EntityType.WORK_ITEM,
            work_item.id,
            DocumentType.REQUIREMENTS
        )

        # Assert
        assert all(doc.document_type == DocumentType.REQUIREMENTS for doc in result)


class TestGetDocumentsByType:
    """Test get_documents_by_type function."""

    def test_get_documents_by_type_all_entities(self, db_service, work_item, task):
        """
        GIVEN documents of a specific type across entities
        WHEN getting by document_type
        THEN all matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/wi-design.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc2 = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=task.id,
            file_path="docs/architecture/design/task-design.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.get_documents_by_type(db_service, DocumentType.DESIGN)

        # Assert
        assert all(doc.document_type == DocumentType.DESIGN for doc in result)
        assert len(result) >= 2

    def test_get_documents_by_type_filtered_by_entity(self, db_service, work_item, task):
        """
        GIVEN documents of a type across entities
        WHEN filtering by entity_type
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/wi.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc2 = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=task.id,
            file_path="docs/architecture/design/task.md",
            category="architecture",
            document_type=DocumentType.DESIGN
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.get_documents_by_type(
            db_service,
            DocumentType.DESIGN,
            entity_type=EntityType.WORK_ITEM
        )

        # Assert
        assert all(doc.entity_type == EntityType.WORK_ITEM for doc in result)

    def test_get_documents_by_type_with_limit(self, db_service, work_item):
        """
        GIVEN many documents of a type
        WHEN getting with limit
        THEN limited results returned
        """
        # Arrange
        for i in range(10):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/architecture/design/test{i}.md",
                category="architecture",
                document_type=DocumentType.DESIGN
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_documents_by_type(
            db_service,
            DocumentType.DESIGN,
            limit=5
        )

        # Assert
        assert len(result) <= 5


class TestGetRecentDocuments:
    """Test get_recent_documents function."""

    def test_get_recent_documents_default_limit(self, db_service, work_item):
        """
        GIVEN multiple documents
        WHEN getting recent without explicit limit
        THEN default limit (20) is applied
        """
        # Arrange
        for i in range(25):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_recent_documents(db_service)

        # Assert
        assert len(result) <= 20

    def test_get_recent_documents_filtered_by_entity_type(self, db_service, work_item, task):
        """
        GIVEN documents for different entity types
        WHEN getting recent with entity_type filter
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/wi.md",
            category="planning"
        )
        doc2 = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=task.id,
            file_path="docs/planning/requirements/task.md",
            category="planning"
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.get_recent_documents(
            db_service,
            entity_type=EntityType.WORK_ITEM
        )

        # Assert
        assert all(doc.entity_type == EntityType.WORK_ITEM for doc in result)


class TestCountDocumentsByType:
    """Test count_documents_by_type function."""

    def test_count_all_documents_by_type(self, db_service, work_item):
        """
        GIVEN documents of different types
        WHEN counting by type
        THEN correct counts per type are returned
        """
        # Arrange
        for i in range(3):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning",
                document_type=DocumentType.REQUIREMENTS
            )
            doc_methods.create_document_reference(db_service, doc)

        for i in range(2):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/architecture/design/test{i}.md",
                category="architecture",
                document_type=DocumentType.DESIGN
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.count_documents_by_type(db_service)

        # Assert
        assert result.get('requirements') >= 3
        assert result.get('design') >= 2

    def test_count_filtered_by_entity(self, db_service, work_item, task):
        """
        GIVEN documents for different entities
        WHEN counting for specific entity
        THEN only that entity's counts are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/wi.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )
        doc2 = DocumentReference(
            entity_type=EntityType.TASK,
            entity_id=task.id,
            file_path="docs/planning/requirements/task.md",
            category="planning",
            document_type=DocumentType.REQUIREMENTS
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.count_documents_by_type(
            db_service,
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id
        )

        # Assert - only work_item documents should be counted
        assert 'requirements' in result


class TestGetDocumentByPath:
    """Test get_document_by_path function."""

    def test_get_document_by_path_exists(self, db_service, work_item):
        """
        GIVEN document with specific path
        WHEN getting by path
        THEN document is returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/unique-path.md",
            category="planning"
        )
        created = doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_document_by_path(
            db_service,
            "docs/planning/requirements/unique-path.md"
        )

        # Assert
        assert result is not None
        assert result.id == created.id

    def test_get_document_by_path_not_found(self, db_service):
        """
        GIVEN non-existent path
        WHEN getting by path
        THEN None is returned
        """
        # Act
        result = doc_methods.get_document_by_path(
            db_service,
            "docs/nonexistent/path.md"
        )

        # Assert
        assert result is None

    def test_get_document_by_path_with_entity_filters(self, db_service, work_item):
        """
        GIVEN document with specific entity
        WHEN getting by path and entity filters
        THEN matching document is returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning"
        )
        created = doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.get_document_by_path(
            db_service,
            "docs/planning/requirements/test.md",
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id
        )

        # Assert
        assert result is not None
        assert result.id == created.id


class TestSearchDocumentsByMetadata:
    """Test search_documents_by_metadata function."""

    def test_search_by_category(self, db_service, work_item):
        """
        GIVEN documents in different categories
        WHEN searching by category
        THEN only matching documents are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test1.md",
            category="planning"
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/test2.md",
            category="architecture"
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            category="planning"
        )

        # Assert
        assert all(doc.category == "planning" for doc in result)

    def test_search_by_tags(self, db_service, work_item):
        """
        GIVEN documents with different tags
        WHEN searching by tags (ANY match)
        THEN documents with any matching tag are returned
        """
        # Arrange
        doc1 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test1.md",
            category="planning",
            tags=["api", "rest", "v1"]
        )
        doc2 = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test2.md",
            category="planning",
            tags=["graphql", "v2"]
        )
        doc_methods.create_document_reference(db_service, doc1)
        doc_methods.create_document_reference(db_service, doc2)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            tags=["api", "graphql"]
        )

        # Assert
        assert len(result) >= 2  # Both documents match at least one tag

    def test_search_by_component(self, db_service, work_item):
        """Test search by component metadata."""
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/auth.md",
            category="architecture",
            component="auth"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            component="auth"
        )

        # Assert
        assert all(doc.component == "auth" for doc in result)

    def test_search_by_domain(self, db_service, work_item):
        """Test search by domain metadata."""
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/security.md",
            category="architecture",
            domain="security"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            domain="security"
        )

        # Assert
        assert all(doc.domain == "security" for doc in result)

    def test_search_by_audience(self, db_service, work_item):
        """Test search by audience metadata."""
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/guides/user_guide/intro.md",
            category="guides",
            audience="developer"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            audience="developer"
        )

        # Assert
        assert all(doc.audience == "developer" for doc in result)

    def test_search_by_maturity(self, db_service, work_item):
        """Test search by maturity metadata."""
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/system.md",
            category="architecture",
            maturity="approved"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            maturity="approved"
        )

        # Assert
        assert all(doc.maturity == "approved" for doc in result)

    def test_search_by_phase(self, db_service, work_item):
        """Test search by SDLC phase metadata."""
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/planning/requirements/test.md",
            category="planning",
            phase="D1"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            phase="D1"
        )

        # Assert
        assert all(doc.phase == "D1" for doc in result)

    def test_search_with_multiple_filters(self, db_service, work_item):
        """
        GIVEN documents with various metadata
        WHEN searching with multiple filters
        THEN only documents matching ALL filters are returned
        """
        # Arrange
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id,
            file_path="docs/architecture/design/auth-api.md",
            category="architecture",
            component="auth",
            audience="developer",
            maturity="approved"
        )
        doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            category="architecture",
            component="auth",
            audience="developer"
        )

        # Assert
        assert len(result) >= 1
        assert all(
            doc.category == "architecture" and
            doc.component == "auth" and
            doc.audience == "developer"
            for doc in result
        )

    def test_search_with_limit(self, db_service, work_item):
        """
        GIVEN many matching documents
        WHEN searching with limit
        THEN limited results are returned
        """
        # Arrange
        for i in range(10):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.search_documents_by_metadata(
            db_service,
            category="planning",
            limit=5
        )

        # Assert
        assert len(result) <= 5


class TestCountDocumentsByCategory:
    """Test count_documents_by_category function."""

    def test_count_documents_by_category(self, db_service, work_item):
        """
        GIVEN documents in different categories
        WHEN counting by category
        THEN correct counts per category are returned
        """
        # Arrange
        for i in range(3):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning"
            )
            doc_methods.create_document_reference(db_service, doc)

        for i in range(2):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/architecture/design/test{i}.md",
                category="architecture"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.count_documents_by_category(db_service)

        # Assert
        assert result.get('planning') >= 3
        assert result.get('architecture') >= 2


class TestCountDocumentsByMaturity:
    """Test count_documents_by_maturity function."""

    def test_count_documents_by_maturity(self, db_service, work_item):
        """
        GIVEN documents with different maturity levels
        WHEN counting by maturity
        THEN correct counts per maturity are returned
        """
        # Arrange
        for i in range(3):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/test{i}.md",
                category="planning",
                maturity="approved"
            )
            doc_methods.create_document_reference(db_service, doc)

        for i in range(2):
            doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item.id,
                file_path=f"docs/planning/requirements/draft{i}.md",
                category="planning",
                maturity="draft"
            )
            doc_methods.create_document_reference(db_service, doc)

        # Act
        result = doc_methods.count_documents_by_maturity(db_service)

        # Assert
        assert result.get('approved') >= 3
        assert result.get('draft') >= 2
