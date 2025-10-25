"""
Pytest fixtures for document integration tests.

Provides reusable test fixtures for document migration and path validation tests.
"""

import pytest
import sqlite3
from pathlib import Path
from click.testing import CliRunner
from agentpm.cli.main import main
from agentpm.core.database import DatabaseService
from agentpm.core.database.models import DocumentReference, WorkItem
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.enums import EntityType, DocumentType, WorkItemType


def get_document_bypassing_validation(db: DatabaseService, doc_id: int) -> dict:
    """
    Get a document from database without Pydantic validation.

    This is useful for testing legacy documents that don't meet current validation rules.

    Args:
        db: Database service
        doc_id: Document ID

    Returns:
        Dictionary with document data (raw from database)
    """
    with db.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM document_references WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def list_documents_bypassing_validation(db: DatabaseService) -> list[dict]:
    """
    List all documents from database without Pydantic validation.

    This is useful for testing legacy documents that don't meet current validation rules.

    Args:
        db: Database service

    Returns:
        List of dictionaries with document data (raw from database)
    """
    with db.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM document_references")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def insert_legacy_document_bypassing_constraints(
    db: DatabaseService,
    entity_type: str,
    entity_id: int,
    file_path: str,
    document_type: str,
    **kwargs
) -> int:
    """
    Insert a legacy document that doesn't meet current CHECK constraints.

    This is specifically for testing migration of legacy documents.
    Temporarily recreates the table without path constraints.

    Args:
        db: Database service
        entity_type: Entity type (work_item, task, etc)
        entity_id: Entity ID
        file_path: File path (can be non-compliant)
        document_type: Document type
        **kwargs: Additional fields (title, description, etc)

    Returns:
        Document ID of inserted record
    """
    with db.connect() as conn:
        # Step 1: Backup existing documents
        conn.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS doc_backup AS
            SELECT * FROM document_references
        """)

        # Step 2: Drop the constrained table
        conn.execute("DROP TABLE document_references")

        # Step 3: Recreate without path CHECK constraint
        conn.execute("""
            CREATE TABLE document_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'work_item', 'task', 'idea')),
                entity_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                document_type TEXT CHECK(document_type IN ('idea', 'requirements', 'refactoring_guide', 'user_story', 'use_case', 'architecture', 'design', 'specification', 'api_doc', 'user_guide', 'admin_guide', 'troubleshooting', 'adr', 'test_plan', 'migration_guide', 'runbook', 'business_pillars_analysis', 'market_research_report', 'competitive_analysis', 'quality_gates_specification', 'stakeholder_analysis', 'technical_specification', 'implementation_plan', 'other')),
                title TEXT,
                description TEXT,
                file_size_bytes INTEGER,
                content_hash TEXT,
                format TEXT CHECK(format IN ('markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other')),
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                document_type_dir TEXT,
                segment_type TEXT,
                component TEXT,
                domain TEXT,
                audience TEXT,
                maturity TEXT,
                priority TEXT,
                tags TEXT,
                phase TEXT,
                work_item_id INTEGER,
                CHECK (entity_id > 0),
                CHECK (file_path IS NOT NULL AND length(file_path) > 0),
                UNIQUE(entity_type, entity_id, file_path)
            )
        """)

        # Step 4: Restore backed up documents
        conn.execute("INSERT INTO document_references SELECT * FROM doc_backup")

        # Step 5: Insert the legacy document
        cursor = conn.execute("""
            INSERT INTO document_references
            (entity_type, entity_id, file_path, document_type, title, description,
             created_at, updated_at, tags)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
        """, (
            entity_type,
            entity_id,
            file_path,
            document_type,
            kwargs.get('title'),
            kwargs.get('description'),
            kwargs.get('tags')
        ))
        doc_id = cursor.lastrowid

        # Step 6: Clean up
        conn.execute("DROP TABLE doc_backup")

        conn.commit()
        return doc_id


@pytest.fixture
def cli_runner():
    """Provide Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def initialized_project(cli_runner, tmp_path):
    """
    Provide initialized AIPM project in isolated filesystem.

    Returns:
        Tuple of (runner, project_root_path, database_service)
    """
    with cli_runner.isolated_filesystem(temp_dir=tmp_path):
        result = cli_runner.invoke(main, ['init', 'Test Project', '--skip-questionnaire'])
        assert result.exit_code == 0

        db = DatabaseService('.aipm/data/aipm.db')
        yield cli_runner, Path.cwd(), db


@pytest.fixture
def sample_documents(initialized_project):
    """
    Create sample documents for testing.

    Returns:
        Tuple of (runner, project_root, db, document_list)
    """
    runner, project_root, db = initialized_project

    documents = []

    # Create valid docs/ structure documents
    valid_docs = [
        {
            "path": "docs/planning/requirements/auth-spec.md",
            "category": "planning",
            "type": DocumentType.REQUIREMENTS,
            "content": "# Authentication Requirements"
        },
        {
            "path": "docs/architecture/design/database-schema.md",
            "category": "architecture",
            "type": DocumentType.DESIGN,
            "content": "# Database Schema Design"
        },
        {
            "path": "docs/guides/user_guide/getting-started.md",
            "category": "guides",
            "type": DocumentType.USER_GUIDE,
            "content": "# Getting Started Guide"
        }
    ]

    for doc_info in valid_docs:
        # Create physical file
        doc_path = Path(doc_info["path"])
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(doc_info["content"])

        # Create database reference
        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category=doc_info["category"],
            document_type=doc_info["type"],
            file_path=doc_info["path"],
            title=doc_info["content"].split('\n')[0].replace('# ', '')
        )
        created = doc_methods.create_document_reference(db, doc)
        documents.append(created)

    yield runner, project_root, db, documents


@pytest.fixture
def legacy_documents(initialized_project):
    """
    Create legacy (non-compliant) documents for migration testing.

    Uses helper function to bypass CHECK constraints during test setup.

    Returns:
        Tuple of (runner, project_root, db, legacy_doc_list)
    """
    runner, project_root, db = initialized_project

    legacy_docs = []

    # Create root-level files (legacy pattern)
    legacy_files = [
        ("requirements.md", DocumentType.REQUIREMENTS, "# Requirements"),
        ("design-doc.md", DocumentType.DESIGN, "# Design Document"),
        ("api-guide.md", DocumentType.API_DOC, "# API Guide"),
    ]

    for filename, doc_type, content in legacy_files:
        # Create physical file at root
        Path(filename).write_text(content)

        # Insert into database bypassing CHECK constraints
        # This simulates legacy documents created before constraint was added
        doc_id = insert_legacy_document_bypassing_constraints(
            db,
            entity_type='work_item',
            entity_id=1,
            file_path=filename,
            document_type=doc_type.value
        )

        legacy_docs.append({
            'id': doc_id,
            'filename': filename,
            'doc_type': doc_type,
            'content': content
        })

    yield runner, project_root, db, legacy_docs


@pytest.fixture
def work_item_with_docs(initialized_project):
    """
    Create work item with associated documents.

    Returns:
        Tuple of (runner, project_root, db, work_item, documents)
    """
    runner, project_root, db = initialized_project

    # Create work item
    wi = WorkItem(
        project_id=1,
        name="Feature Implementation",
        work_item_type=WorkItemType.FEATURE,
        business_context="Implement new authentication feature"
    )
    created_wi = wi_methods.create_work_item(db, wi)

    # Create associated documents
    docs_info = [
        {
            "path": f"docs/planning/requirements/wi-{created_wi.id}-requirements.md",
            "type": DocumentType.REQUIREMENTS,
            "title": "Feature Requirements"
        },
        {
            "path": f"docs/architecture/design/wi-{created_wi.id}-design.md",
            "type": DocumentType.DESIGN,
            "title": "Feature Design"
        }
    ]

    documents = []
    for doc_info in docs_info:
        doc_path = Path(doc_info["path"])
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(f"# {doc_info['title']}")

        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=created_wi.id,
            work_item_id=created_wi.id,
            category=doc_info["path"].split('/')[1],
            document_type=doc_info["type"],
            file_path=doc_info["path"],
            title=doc_info["title"]
        )
        created = doc_methods.create_document_reference(db, doc)
        documents.append(created)

    yield runner, project_root, db, created_wi, documents


@pytest.fixture
def migration_test_data(initialized_project):
    """
    Create comprehensive test data for migration testing.

    Returns:
        Tuple of (runner, project_root, db, test_data_dict)
    """
    runner, project_root, db = initialized_project

    test_data = {
        'valid_docs': [],
        'legacy_docs': [],
        'incomplete_paths': [],
        'exception_docs': []
    }

    # Valid docs/ structure
    valid_paths = [
        "docs/planning/requirements/spec.md",
        "docs/architecture/design/system.md",
    ]

    for path in valid_paths:
        doc_path = Path(path)
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(f"# {path}")

        doc = DocumentReference(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            category=path.split('/')[1],
            file_path=path
        )
        created = doc_methods.create_document_reference(db, doc)
        test_data['valid_docs'].append(created)

    # Legacy root-level files
    legacy_files = ["old-requirements.md", "legacy-design.md"]
    for filename in legacy_files:
        Path(filename).write_text(f"# {filename}")

        doc_id = insert_legacy_document_bypassing_constraints(
            db,
            entity_type='work_item',
            entity_id=1,
            file_path=filename,
            document_type='requirements'
        )
        test_data['legacy_docs'].append({
            'id': doc_id,
            'filename': filename
        })

    # Exception files (allowed at root)
    exception_files = ["README.md", "CHANGELOG.md"]
    for filename in exception_files:
        Path(filename).write_text(f"# {filename}")

        doc = DocumentReference(
            entity_type=EntityType.PROJECT,
            entity_id=1,
            file_path=filename
        )
        created = doc_methods.create_document_reference(db, doc)
        test_data['exception_docs'].append(created)

    yield runner, project_root, db, test_data
