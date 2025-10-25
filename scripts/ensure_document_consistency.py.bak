#!/usr/bin/env python3
"""
Script to ensure consistency between filesystem documents and database entries.
This script will scan the docs/ directory and create document references for any files
that don't already have database entries, ensuring complete consistency.
"""

import os
import subprocess
import sys
from pathlib import Path

def get_document_type_and_category_from_path(file_path: str) -> tuple[str, str]:
    """Determine document type and category from file path structure."""
    path_parts = file_path.split('/')
    
    if len(path_parts) >= 3:
        category = path_parts[1]
        doc_type = path_parts[2]
        
        # Map path types to document types (matching database schema)
        type_mapping = {
            'session_summary': 'other',  # Map to valid DB type
            'status_report': 'other',
            'test_report': 'other',
            'validation_report': 'other',
            'assessment_report': 'other',
            'architecture_doc': 'architecture',
            'design_doc': 'design',
            'adr': 'adr',
            'technical_spec': 'specification',
            'user_guide': 'user_guide',
            'developer_guide': 'user_guide',
            'api_doc': 'api_doc',
            'runbook': 'runbook',
            'troubleshooting': 'troubleshooting',
            'faq': 'other',
            'test_plan': 'test_plan',
            'coverage_report': 'other',
            'deployment_guide': 'runbook',
            'monitoring_guide': 'runbook',
            'incident_report': 'other',
            'research_report': 'other',
            'analysis_report': 'other',
            'investigation_report': 'other',
            'feasibility_study': 'other',
            'competitive_analysis': 'other',
            'progress_report': 'other',
            'milestone_report': 'other',
            'retrospective_report': 'other',
            'business_pillars': 'other',
            'market_research': 'other',
            'stakeholder_analysis': 'other',
            'quality_gates_spec': 'other',
            'specification': 'specification',
        }
        
        return type_mapping.get(doc_type, 'other'), category
    
    return 'other', 'other'

def get_existing_document_paths() -> set:
    """Get all existing document paths from the database."""
    project_root = Path(__file__).parent.parent
    
    try:
        result = subprocess.run(['apm', 'document', 'list'], 
                              capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            existing_paths = set()
            lines = result.stdout.split('\n')
            for line in lines:
                if '│' in line and 'docs/' in line:
                    # Extract file path from table row
                    parts = line.split('│')
                    if len(parts) >= 3:
                        file_path = parts[2].strip()
                        if file_path and file_path.startswith('docs/'):
                            existing_paths.add(file_path)
            return existing_paths
        else:
            print(f"Warning: Could not get existing documents: {result.stderr}")
            return set()
    except Exception as e:
        print(f"Warning: Could not get existing documents: {e}")
        return set()

def create_document_entry(file_path: str, title: str, doc_type: str, category: str) -> bool:
    """Create a document entry in the database."""
    project_root = Path(__file__).parent.parent
    
    try:
        # Use CLI to create document reference
        cmd = [
            'apm', 'document', 'add',
            '--entity-type=work-item',
            '--entity-id=148',  # Use a valid work item ID
            '--file-path', file_path,
            '--title', title,
            '--created-by', 'consistency_script'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            return True
        else:
            # Check if it's a duplicate error (which is fine)
            if "already exists" in result.stderr.lower() or "duplicate" in result.stderr.lower():
                return True  # Consider this success
            else:
                print(f"❌ Error creating entry for {file_path}: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Exception creating entry for {file_path}: {e}")
        return False

def ensure_document_consistency():
    """Ensure all documentation files have corresponding database entries."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    created_count = 0
    existing_count = 0
    error_count = 0
    
    print("🔍 Scanning for document consistency...")
    
    # Get existing document references
    existing_paths = get_existing_document_paths()
    print(f"📊 Found {len(existing_paths)} existing document entries in database")
    
    # Scan docs directory
    all_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md') or file.endswith('.yaml') or file.endswith('.json'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                all_files.append(rel_path)
    
    print(f"📁 Found {len(all_files)} documentation files in filesystem")
    
    # Process each file
    for rel_path in all_files:
        if rel_path not in existing_paths:
            # Create document reference
            doc_type, category = get_document_type_and_category_from_path(rel_path)
            
            # Extract title from filename
            filename = Path(rel_path).name
            title = Path(filename).stem.replace('-', ' ').replace('_', ' ').title()
            
            print(f"📝 Creating database entry for: {rel_path}")
            
            if create_document_entry(rel_path, title, doc_type, category):
                created_count += 1
                print(f"✅ Created entry for: {rel_path}")
            else:
                error_count += 1
        else:
            existing_count += 1
    
    print(f"\n📊 Consistency Summary:")
    print(f"  ✅ Created {created_count} new document entries")
    print(f"  ℹ️  Found {existing_count} existing document entries")
    print(f"  ❌ Failed to create {error_count} document entries")
    print(f"  📁 Total files processed: {len(all_files)}")
    
    if error_count == 0:
        print(f"\n🎉 Document consistency achieved! All files have database entries.")
    else:
        print(f"\n⚠️  {error_count} files still need database entries. Check errors above.")

def verify_consistency():
    """Verify that all filesystem documents have database entries."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    print("🔍 Verifying document consistency...")
    
    # Get existing document references
    existing_paths = get_existing_document_paths()
    
    # Scan docs directory
    missing_entries = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md') or file.endswith('.yaml') or file.endswith('.json'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                
                if rel_path not in existing_paths:
                    missing_entries.append(rel_path)
    
    if missing_entries:
        print(f"❌ Found {len(missing_entries)} files without database entries:")
        for path in missing_entries:
            print(f"  - {path}")
        return False
    else:
        print("✅ All documentation files have corresponding database entries!")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_consistency()
    else:
        ensure_document_consistency()
