#!/usr/bin/env python3
"""
Document Registration Script

Registers valuable untracked documents into the database using the apm document add command.
Reads file paths from /tmp/files_to_register.txt and intelligently determines entity type,
document type, and other metadata.

This script ensures proper document tracking in the APM (Agent Project Manager) system.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


# Document type mapping based on path patterns
DOCUMENT_TYPE_MAPPING = {
    # Architecture
    'architecture': 'architecture',
    'design': 'design',
    'adr': 'adr',
    'decision': 'adr',

    # Planning
    'requirements': 'requirements',
    'requirement': 'requirements',
    'user-story': 'user_story',
    'user_story': 'user_story',
    'use-case': 'use_case',
    'use_case': 'use_case',
    'implementation-plan': 'implementation_plan',
    'implementation_plan': 'implementation_plan',

    # Guides
    'user-guide': 'user_guide',
    'user_guide': 'user_guide',
    'admin-guide': 'admin_guide',
    'admin_guide': 'admin_guide',
    'troubleshooting': 'troubleshooting',
    'migration-guide': 'migration_guide',
    'migration_guide': 'migration_guide',

    # Reference
    'specification': 'specification',
    'spec': 'specification',
    'api-doc': 'api_doc',
    'api_doc': 'api_doc',
    'api': 'api_doc',

    # Process
    'test-plan': 'test_plan',
    'test_plan': 'test_plan',

    # Operations
    'runbook': 'runbook',

    # Communication
    'market-research': 'market_research_report',
    'competitive-analysis': 'competitive_analysis',
    'stakeholder-analysis': 'stakeholder_analysis',
    'business-pillars': 'business_pillars_analysis',
}


def detect_document_type(file_path: str) -> str:
    """
    Detect document type from file path.

    Args:
        file_path: Path to the document

    Returns:
        Document type string
    """
    path_lower = file_path.lower()

    # Check for specific patterns
    for pattern, doc_type in DOCUMENT_TYPE_MAPPING.items():
        if pattern in path_lower:
            return doc_type

    # Default based on directory structure
    if '/planning/' in path_lower:
        return 'requirements'
    elif '/architecture/' in path_lower:
        return 'architecture'
    elif '/guides/' in path_lower:
        return 'user_guide'
    elif '/reference/' in path_lower:
        return 'specification'
    elif '/processes/' in path_lower:
        return 'test_plan'
    elif '/operations/' in path_lower:
        return 'runbook'
    elif '/governance/' in path_lower:
        return 'quality_gates_specification'
    elif '/communication/' in path_lower:
        return 'market_research_report'

    # Default to 'other' for unclassifiable documents
    return 'other'


def generate_title(file_path: str) -> str:
    """
    Generate a human-readable title from file path.

    Args:
        file_path: Path to the document

    Returns:
        Title string
    """
    filename = Path(file_path).stem
    # Replace separators with spaces
    title = filename.replace('-', ' ').replace('_', ' ')
    # Capitalize words
    title = ' '.join(word.capitalize() for word in title.split())
    return title


def register_document(
    file_path: str,
    entity_type: str = 'project',
    entity_id: int = 1,
    dry_run: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Register a document in the database using apm document add.

    Args:
        file_path: Relative path to the document
        entity_type: Entity type (project, work_item, task)
        entity_id: Entity ID (default: 1 for project-level docs)
        dry_run: If True, only print what would be done

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Detect document type
    doc_type = detect_document_type(file_path)

    # Generate title
    title = generate_title(file_path)

    # Build command
    cmd = [
        'apm', 'document', 'add',
        '--entity-type', entity_type,
        '--entity-id', str(entity_id),
        '--file-path', file_path,
        '--type', doc_type,
        '--title', title,
        '--created-by', 'system_cleanup',
        '--no-validate-file'  # Skip file validation for performance
    ]

    if dry_run:
        print(f"[DRY RUN] Would register: {file_path}")
        print(f"          Type: {doc_type}, Title: {title}")
        return True, None

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Registered: {file_path}")
        return True, None
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        print(f"❌ Failed to register: {file_path}")
        print(f"   Error: {error_msg}")
        return False, error_msg


def main():
    """Main execution function."""
    input_file = Path('/tmp/files_to_register.txt')

    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("   Waiting for pattern-applier to create the file...")
        sys.exit(1)

    # Read file paths
    try:
        with open(input_file, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        sys.exit(1)

    if not file_paths:
        print("⚠️  No files to register (input file is empty)")
        sys.exit(0)

    print(f"📄 Found {len(file_paths)} files to register")
    print()

    # Track statistics
    success_count = 0
    failure_count = 0
    errors = []

    # Register each file
    for file_path in file_paths:
        success, error = register_document(file_path)

        if success:
            success_count += 1
        else:
            failure_count += 1
            errors.append((file_path, error))

    # Print summary
    print()
    print("=" * 60)
    print("📊 Registration Summary")
    print("=" * 60)
    print(f"✅ Successfully registered: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📝 Total: {len(file_paths)}")
    print()

    if errors:
        print("⚠️  Errors encountered:")
        for file_path, error in errors:
            print(f"   • {file_path}")
            if error:
                print(f"     {error}")
        print()

    # Exit code based on results
    if failure_count > 0:
        sys.exit(1)
    else:
        print("✅ All documents registered successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
