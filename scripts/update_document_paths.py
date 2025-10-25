#!/usr/bin/env python3
"""
Update Document Paths Script

Updates document_references table with new file paths after documentation reorganisation.
This script handles the migration of documents from root-level and non-standard locations
to the proper docs/{category}/{document_type}/ structure.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods.document_references import (
    list_document_references, 
    update_document_reference,
    get_document_by_path
)
from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat
from agentpm.core.database.models.document_reference import DocumentReference


def get_database_service():
    """Get database service instance."""
    db_path = project_root / "agentpm" / "aipm_v2.db"
    return DatabaseService(str(db_path))


def get_path_mappings():
    """Get mappings of old paths to new paths."""
    return {
        # Assessment reports
        "AGENT_SYSTEM_ASSESSMENT_SUMMARY.md": "docs/architecture/assessment_report/agent-system-assessment-summary.md",
        "DOCUMENT_STRUCTURE_CONSISTENCY_REPORT.md": "docs/architecture/assessment_report/document-structure-consistency-report.md",
        "TEST_SUITE_SUMMARY.md": "docs/architecture/assessment_report/test-suite-summary.md",
        
        # Implementation documents
        "IMPLEMENTATION-SUMMARY.md": "docs/processes/implementation/implementation-summary.md",
        "DEVELOPMENT.md": "docs/processes/implementation/development.md",
        "SBOM_CLI_IMPLEMENTATION.md": "docs/processes/implementation/sbom-cli-implementation.md",
        "PRESET_SYSTEM_IMPLEMENTATION.md": "docs/processes/implementation/preset-system-implementation.md",
        
        # Release/Operations documents
        "RELEASE.md": "docs/operations/release/release.md",
        "RELEASE_CHECKLIST.md": "docs/operations/release/release-checklist.md",
        "PRE_RELEASE_CHECKLIST.md": "docs/operations/release/pre-release-checklist.md",
        "CLEAN_RELEASE_GUIDE.md": "docs/operations/release/clean-release-guide.md",
        "ROOT_CLEANUP_SUMMARY.md": "docs/operations/release/root-cleanup-summary.md",
        
        # Migration documents
        "MIGRATION_SUMMARY.md": "docs/processes/migration/migration-summary.md",
        "COVERAGE-OVERRIDE-FIX.md": "docs/processes/migration/coverage-override-fix.md",
        
        # Completion documents
        "TASK-947-BRANDING-TEST-COMPLETION.md": "docs/processes/completion/task-947-branding-test-completion.md",
        "FIX_SUMMARY_TASK_1003.md": "docs/processes/completion/fix-summary-task-1003.md",
        "WI-141-TASK-933-COMPLETION.md": "docs/processes/completion/wi-141-task-933-completion.md",
        "WI-148-COMPLETION-SUMMARY.md": "docs/processes/completion/wi-148-completion-summary.md",
        
        # Communication documents
        "SESSION-HANDOVER-2025-10-25.md": "docs/communication/session/session-handover-2025-10-25.md",
        
        # Research documents
        "fitness_result.md": "docs/planning/research/fitness-result.md",
        "GITHUB_SETUP_OPTIONS.md": "docs/planning/research/github-setup-options.md",
        
        # Non-standard locations
        "claudedocs/research_apm_market_positioning_2025-10-25.md": "docs/planning/research/research-apm-market-positioning-2025-10-25.md",
        "agentpm/web/WEB_CONSOLIDATION_TASKS.md": "docs/architecture/web/web-consolidation-tasks.md",
        "agentpm/web/WEB_CONSOLIDATION_WORK_ITEM.md": "docs/architecture/web/web-consolidation-work-item.md",
    }


def get_document_metadata():
    """Get metadata for each document type."""
    return {
        # Assessment reports
        "docs/architecture/assessment_report/agent-system-assessment-summary.md": {
            "category": "architecture",
            "document_type": DocumentType.ASSESSMENT_REPORT,
            "document_type_dir": "assessment_report",
            "component": "agent-system",
            "domain": "system-assessment",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["assessment", "agent-system", "readiness"]
        },
        "docs/architecture/assessment_report/document-structure-consistency-report.md": {
            "category": "architecture",
            "document_type": DocumentType.ASSESSMENT_REPORT,
            "document_type_dir": "assessment_report",
            "component": "documentation",
            "domain": "documentation-system",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["assessment", "documentation", "structure"]
        },
        "docs/architecture/assessment_report/test-suite-summary.md": {
            "category": "architecture",
            "document_type": DocumentType.ASSESSMENT_REPORT,
            "document_type_dir": "assessment_report",
            "component": "testing",
            "domain": "quality-assurance",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["assessment", "testing", "quality"]
        },
        
        # Implementation documents
        "docs/processes/implementation/implementation-summary.md": {
            "category": "processes",
            "document_type": DocumentType.IMPLEMENTATION_PLAN,
            "document_type_dir": "implementation",
            "component": "system",
            "domain": "implementation",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["implementation", "summary", "process"]
        },
        "docs/processes/implementation/development.md": {
            "category": "processes",
            "document_type": DocumentType.IMPLEMENTATION_PLAN,
            "document_type_dir": "implementation",
            "component": "system",
            "domain": "development",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["development", "process", "guidelines"]
        },
        "docs/processes/implementation/sbom-cli-implementation.md": {
            "category": "processes",
            "document_type": DocumentType.IMPLEMENTATION_PLAN,
            "document_type_dir": "implementation",
            "component": "cli",
            "domain": "sbom",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["implementation", "cli", "sbom"]
        },
        "docs/processes/implementation/preset-system-implementation.md": {
            "category": "processes",
            "document_type": DocumentType.IMPLEMENTATION_PLAN,
            "document_type_dir": "implementation",
            "component": "preset-system",
            "domain": "configuration",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["implementation", "preset", "configuration"]
        },
        
        # Release/Operations documents
        "docs/operations/release/release.md": {
            "category": "operations",
            "document_type": DocumentType.RUNBOOK,
            "document_type_dir": "release",
            "component": "release",
            "domain": "deployment",
            "audience": "admin",
            "maturity": "approved",
            "tags": ["release", "deployment", "operations"]
        },
        "docs/operations/release/release-checklist.md": {
            "category": "operations",
            "document_type": DocumentType.RUNBOOK,
            "document_type_dir": "release",
            "component": "release",
            "domain": "deployment",
            "audience": "admin",
            "maturity": "approved",
            "tags": ["release", "checklist", "operations"]
        },
        "docs/operations/release/pre-release-checklist.md": {
            "category": "operations",
            "document_type": DocumentType.RUNBOOK,
            "document_type_dir": "release",
            "component": "release",
            "domain": "deployment",
            "audience": "admin",
            "maturity": "approved",
            "tags": ["release", "pre-release", "checklist"]
        },
        "docs/operations/release/clean-release-guide.md": {
            "category": "operations",
            "document_type": DocumentType.RUNBOOK,
            "document_type_dir": "release",
            "component": "release",
            "domain": "deployment",
            "audience": "admin",
            "maturity": "approved",
            "tags": ["release", "clean", "guide"]
        },
        "docs/operations/release/root-cleanup-summary.md": {
            "category": "operations",
            "document_type": DocumentType.RUNBOOK,
            "document_type_dir": "release",
            "component": "cleanup",
            "domain": "maintenance",
            "audience": "admin",
            "maturity": "approved",
            "tags": ["cleanup", "maintenance", "operations"]
        },
        
        # Migration documents
        "docs/processes/migration/migration-summary.md": {
            "category": "processes",
            "document_type": DocumentType.MIGRATION_GUIDE,
            "document_type_dir": "migration",
            "component": "database",
            "domain": "migration",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["migration", "database", "process"]
        },
        "docs/processes/migration/coverage-override-fix.md": {
            "category": "processes",
            "document_type": DocumentType.MIGRATION_GUIDE,
            "document_type_dir": "migration",
            "component": "testing",
            "domain": "coverage",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["migration", "coverage", "fix"]
        },
        
        # Completion documents
        "docs/processes/completion/task-947-branding-test-completion.md": {
            "category": "processes",
            "document_type": DocumentType.STATUS_REPORT,
            "document_type_dir": "completion",
            "component": "branding",
            "domain": "testing",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["completion", "branding", "testing"]
        },
        "docs/processes/completion/fix-summary-task-1003.md": {
            "category": "processes",
            "document_type": DocumentType.STATUS_REPORT,
            "document_type_dir": "completion",
            "component": "fix",
            "domain": "maintenance",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["completion", "fix", "maintenance"]
        },
        "docs/processes/completion/wi-141-task-933-completion.md": {
            "category": "processes",
            "document_type": DocumentType.STATUS_REPORT,
            "document_type_dir": "completion",
            "component": "work-item",
            "domain": "completion",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["completion", "work-item", "task"]
        },
        "docs/processes/completion/wi-148-completion-summary.md": {
            "category": "processes",
            "document_type": DocumentType.STATUS_REPORT,
            "document_type_dir": "completion",
            "component": "work-item",
            "domain": "completion",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["completion", "work-item", "summary"]
        },
        
        # Communication documents
        "docs/communication/session/session-handover-2025-10-25.md": {
            "category": "communication",
            "document_type": DocumentType.SESSION_SUMMARY,
            "document_type_dir": "session",
            "component": "session",
            "domain": "handover",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["session", "handover", "communication"]
        },
        
        # Research documents
        "docs/planning/research/fitness-result.md": {
            "category": "planning",
            "document_type": DocumentType.RESEARCH_REPORT,
            "document_type_dir": "research",
            "component": "fitness",
            "domain": "analysis",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["research", "fitness", "analysis"]
        },
        "docs/planning/research/github-setup-options.md": {
            "category": "planning",
            "document_type": DocumentType.RESEARCH_REPORT,
            "document_type_dir": "research",
            "component": "github",
            "domain": "setup",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["research", "github", "setup"]
        },
        "docs/planning/research/research-apm-market-positioning-2025-10-25.md": {
            "category": "planning",
            "document_type": DocumentType.RESEARCH_REPORT,
            "document_type_dir": "research",
            "component": "market",
            "domain": "positioning",
            "audience": "stakeholder",
            "maturity": "approved",
            "tags": ["research", "market", "positioning"]
        },
        
        # Web architecture documents
        "docs/architecture/web/web-consolidation-tasks.md": {
            "category": "architecture",
            "document_type": DocumentType.DESIGN_DOC,
            "document_type_dir": "web",
            "component": "web",
            "domain": "consolidation",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["architecture", "web", "consolidation"]
        },
        "docs/architecture/web/web-consolidation-work-item.md": {
            "category": "architecture",
            "document_type": DocumentType.DESIGN_DOC,
            "document_type_dir": "web",
            "component": "web",
            "domain": "consolidation",
            "audience": "developer",
            "maturity": "approved",
            "tags": ["architecture", "web", "consolidation"]
        },
    }


def update_document_paths():
    """Update document paths in the database."""
    service = get_database_service()
    path_mappings = get_path_mappings()
    metadata = get_document_metadata()
    
    updated_count = 0
    created_count = 0
    
    print("🔄 Updating document paths in database...")
    
    for old_path, new_path in path_mappings.items():
        print(f"  📄 Processing: {old_path} → {new_path}")
        
        # Check if document exists with old path
        doc = get_document_by_path(service, old_path)
        
        if doc:
            # Update existing document
            print(f"    ✅ Found existing document (ID: {doc.id})")
            
            # Update path and metadata
            doc.file_path = new_path
            doc.category = metadata[new_path]["category"]
            doc.document_type = metadata[new_path]["document_type"]
            doc.document_type_dir = metadata[new_path]["document_type_dir"]
            doc.component = metadata[new_path]["component"]
            doc.domain = metadata[new_path]["domain"]
            doc.audience = metadata[new_path]["audience"]
            doc.maturity = metadata[new_path]["maturity"]
            doc.tags = metadata[new_path]["tags"]
            
            # Update in database
            updated_doc = update_document_reference(service, doc)
            if updated_doc:
                print(f"    ✅ Updated document path and metadata")
                updated_count += 1
            else:
                print(f"    ❌ Failed to update document")
        else:
            # Check if document already exists with new path
            existing_doc = get_document_by_path(service, new_path)
            if existing_doc:
                print(f"    ℹ️  Document already exists at new path (ID: {existing_doc.id})")
                continue
            
            # Create new document reference
            print(f"    📝 Creating new document reference")
            
            # Read file content to get size and hash
            file_path = project_root / new_path
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                file_size = len(content.encode('utf-8'))
                content_hash = f"sha256:{hash(content)}"
                
                # Create document reference
                new_doc = DocumentReference(
                    entity_type=EntityType.PROJECT,
                    entity_id=1,  # Project-level document
                    file_path=new_path,
                    title=file_path.stem.replace('-', ' ').title(),
                    description=f"Document moved from {old_path}",
                    file_size_bytes=file_size,
                    content_hash=content_hash,
                    format=DocumentFormat.MARKDOWN,
                    created_by="documentation-reorganisation",
                    category=metadata[new_path]["category"],
                    document_type=metadata[new_path]["document_type"],
                    document_type_dir=metadata[new_path]["document_type_dir"],
                    component=metadata[new_path]["component"],
                    domain=metadata[new_path]["domain"],
                    audience=metadata[new_path]["audience"],
                    maturity=metadata[new_path]["maturity"],
                    tags=metadata[new_path]["tags"],
                    content=content
                )
                
                # Create in database
                from agentpm.core.database.methods.document_references import create_document_reference
                created_doc = create_document_reference(service, new_doc)
                if created_doc:
                    print(f"    ✅ Created new document reference (ID: {created_doc.id})")
                    created_count += 1
                else:
                    print(f"    ❌ Failed to create document reference")
            else:
                print(f"    ⚠️  File not found at new path: {new_path}")
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Updated: {updated_count} documents")
    print(f"  📝 Created: {created_count} documents")
    print(f"  📄 Total processed: {len(path_mappings)} documents")


def verify_document_structure():
    """Verify that all documents follow the proper structure."""
    service = get_database_service()
    
    print("\n🔍 Verifying document structure...")
    
    # Get all documents
    all_docs = list_document_references(service)
    
    compliant_count = 0
    non_compliant_count = 0
    
    for doc in all_docs:
        if doc.file_path.startswith('docs/') or doc.file_path in ['README.md', 'CHANGELOG.md', 'LICENSE.md']:
            compliant_count += 1
        else:
            print(f"  ⚠️  Non-compliant path: {doc.file_path}")
            non_compliant_count += 1
    
    print(f"\n📊 Structure Verification:")
    print(f"  ✅ Compliant: {compliant_count} documents")
    print(f"  ⚠️  Non-compliant: {non_compliant_count} documents")
    
    if non_compliant_count == 0:
        print("  🎉 All documents follow proper structure!")
    else:
        print("  ⚠️  Some documents need attention")


if __name__ == "__main__":
    try:
        update_document_paths()
        verify_document_structure()
        print("\n🎉 Document path update completed successfully!")
    except Exception as e:
        print(f"\n❌ Error updating document paths: {e}")
        sys.exit(1)
