#!/usr/bin/env python3
"""
Debug script to understand the document test issue.
"""

import tempfile
from pathlib import Path
from agentpm.core.database import DatabaseService
from agentpm.core.database.migrations import MigrationManager
from agentpm.core.database.models import Project, WorkItem, Task, DocumentReference
from agentpm.core.database.methods import projects, work_items, tasks
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.core.database.enums import (
    WorkItemType, WorkItemStatus, TaskType, TaskStatus,
    EntityType, DocumentType, DocumentFormat
)

def debug_document_setup():
    """Debug the document setup to see what's being created."""
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create database
        db_path = Path(tmp_dir) / 'test.db'
        db = DatabaseService(str(db_path))
        
        # Apply migrations
        migration_manager = MigrationManager(db)
        migration_manager.run_all_pending()
        
        # Create project directory structure
        project_path = Path(tmp_dir) / "test_project"
        project_path.mkdir()
        
        docs_path = project_path / "docs"
        docs_path.mkdir()
        
        # Create sample document files
        sample_files = {
            "docs/architecture/system-overview.md": "# System Architecture\n\nThis is the system architecture document.",
            "docs/design/user-interface.md": "# UI Design\n\nUser interface design specifications.",
            "docs/api/api-specification.md": "# API Specification\n\nRESTful API documentation.",
            "docs/requirements/feature-requirements.md": "# Requirements\n\nFeature requirements and acceptance criteria.",
            "docs/test-plan.md": "# Test Plan\n\nComprehensive testing strategy.",
            "docs/README.md": "# Documentation\n\nProject documentation overview.",
        }
        
        for file_path, content in sample_files.items():
            full_path = project_path / file_path
            full_path.write_text(content)
        
        # Create project in database
        project = Project(name="Test Project", path=str(project_path))
        created_project = projects.create_project(db, project)
        print(f"Created project: {created_project.id}")
        
        # Create work item
        work_item = WorkItem(
            project_id=created_project.id,
            name="Document Management Feature",
            type=WorkItemType.FEATURE,
            status=WorkItemStatus.IN_PROGRESS,
            description="Implement document management system"
        )
        created_wi = work_items.create_work_item(db, work_item)
        print(f"Created work item: {created_wi.id}")
        
        # Create task
        task = Task(
            work_item_id=created_wi.id,
            name="Implement document CLI commands",
            type=TaskType.IMPLEMENTATION,
            status=TaskStatus.IN_PROGRESS,
            effort_hours=4.0,
            description="Create CLI commands for document management"
        )
        created_task = tasks.create_task(db, task)
        print(f"Created task: {created_task.id}")
        
        # Create document references in database (same as fixture)
        doc_refs = [
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=created_wi.id,
                file_path="docs/architecture/system-overview.md",
                document_type=DocumentType.ARCHITECTURE,
                title="System Architecture Overview",
                description="High-level system architecture",
                file_size_bytes=len(sample_files["docs/architecture/system-overview.md"]),
                format=DocumentFormat.MARKDOWN,
                created_by="test_user"
            ),
            DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=created_wi.id,
                file_path="docs/api/api-specification.md",
                document_type=DocumentType.SPECIFICATION,
                title="API Specification",
                description="RESTful API documentation",
                file_size_bytes=len(sample_files["docs/api/api-specification.md"]),
                format=DocumentFormat.MARKDOWN,
                created_by="test_user"
            ),
            DocumentReference(
                entity_type=EntityType.TASK,
                entity_id=created_task.id,
                file_path="docs/design/user-interface.md",
                document_type=DocumentType.DESIGN,
                title="User Interface Design",
                description="UI design specifications",
                file_size_bytes=len(sample_files["docs/design/user-interface.md"]),
                format=DocumentFormat.MARKDOWN,
                created_by="ai_agent"
            ),
        ]
        
        created_docs = []
        for doc_ref in doc_refs:
            created_doc = doc_methods.create_document_reference(db, doc_ref)
            created_docs.append(created_doc)
            print(f"Created document reference: {doc_ref.file_path} -> {doc_ref.entity_type.value} {doc_ref.entity_id}")
        
        # Now check what's in the database
        with db.connect() as conn:
            cursor = conn.execute('SELECT entity_type, entity_id, file_path FROM document_references')
            rows = cursor.fetchall()
            print(f"\nDocument references in database: {len(rows)}")
            for row in rows:
                print(f"  {row[0]} {row[1]} -> {row[2]}")
        
        # Now try to add the same document that the test is trying to add
        print(f"\nTrying to add docs/test-plan.md to work_item {created_wi.id}...")
        try:
            test_doc = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=created_wi.id,
                file_path="docs/test-plan.md",
                document_type=DocumentType.TEST_PLAN,
                title="Test Plan Document",
                file_size_bytes=len(sample_files["docs/test-plan.md"]),
                format=DocumentFormat.MARKDOWN,
                created_by="test_user"
            )
            created_test_doc = doc_methods.create_document_reference(db, test_doc)
            print(f"SUCCESS: Created document reference for docs/test-plan.md")
        except Exception as e:
            print(f"ERROR: {e}")
            
            # Check what's in the database again
            with db.connect() as conn:
                cursor = conn.execute('SELECT entity_type, entity_id, file_path FROM document_references')
                rows = cursor.fetchall()
                print(f"\nDocument references in database after error: {len(rows)}")
                for row in rows:
                    print(f"  {row[0]} {row[1]} -> {row[2]}")

if __name__ == "__main__":
    debug_document_setup()
