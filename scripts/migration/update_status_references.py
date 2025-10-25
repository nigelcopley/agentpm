#!/usr/bin/env python3
"""
Status Reference Update Script

This script updates all references to the old 9-state workflow system
to the new 6-state system across all Python files in the APM (Agent Project Manager) codebase.

Old → New Status Mappings:
- PROPOSED → DRAFT
- VALIDATED → READY  
- ACCEPTED → ACTIVE
- IN_PROGRESS → ACTIVE
- COMPLETED → DONE

The script handles:
- WorkItemStatus and TaskStatus enum references
- String literals in comments and docstrings
- Default values in model definitions
- Method names and variable names
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Status mappings for the 6-state system
STATUS_MAPPINGS = {
    # WorkItemStatus mappings
    'WorkItemStatus.PROPOSED': 'WorkItemStatus.DRAFT',
    'WorkItemStatus.VALIDATED': 'WorkItemStatus.READY',
    'WorkItemStatus.ACCEPTED': 'WorkItemStatus.ACTIVE',
    'WorkItemStatus.IN_PROGRESS': 'WorkItemStatus.ACTIVE',
    'WorkItemStatus.COMPLETED': 'WorkItemStatus.DONE',
    
    # TaskStatus mappings
    'TaskStatus.PROPOSED': 'TaskStatus.DRAFT',
    'TaskStatus.VALIDATED': 'TaskStatus.READY',
    'TaskStatus.ACCEPTED': 'TaskStatus.ACTIVE',
    'TaskStatus.IN_PROGRESS': 'TaskStatus.ACTIVE',
    'TaskStatus.COMPLETED': 'TaskStatus.DONE',
    
    # String literal mappings (for comments, docstrings, etc.)
    'PROPOSED': 'DRAFT',
    'VALIDATED': 'READY',
    'ACCEPTED': 'ACTIVE',
    'IN_PROGRESS': 'ACTIVE',
    'COMPLETED': 'DONE',
    
    # Method name mappings
    'is_in_progress': 'is_active',
    'is_completed': 'is_done',
}

# Files to exclude from processing
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    '.pytest_cache',
    'node_modules',
    'htmlcov',
    '.egg-info',
    'tests-BAK',  # Exclude the backup test directory
]

# File extensions to process
INCLUDE_EXTENSIONS = {'.py', '.md', '.html', '.json', '.yaml', '.yml'}

def should_exclude_file(file_path: Path) -> bool:
    """Check if file should be excluded from processing."""
    path_str = str(file_path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)

def should_include_file(file_path: Path) -> bool:
    """Check if file should be included for processing."""
    return (file_path.suffix in INCLUDE_EXTENSIONS and 
            not should_exclude_file(file_path))

def find_files_to_process(root_dir: Path) -> List[Path]:
    """Find all files that need status reference updates."""
    files_to_process = []
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_include_file(file_path):
            files_to_process.append(file_path)
    
    return files_to_process

def update_file_content(content: str, file_path: Path) -> Tuple[str, List[str]]:
    """Update status references in file content."""
    changes_made = []
    updated_content = content
    
    # Apply all status mappings
    for old_ref, new_ref in STATUS_MAPPINGS.items():
        if old_ref in updated_content:
            # Count occurrences
            count = updated_content.count(old_ref)
            updated_content = updated_content.replace(old_ref, new_ref)
            changes_made.append(f"  {old_ref} → {new_ref} ({count} occurrences)")
    
    # Special handling for method names and variable names
    method_mappings = {
        'is_in_progress': 'is_active',
        'is_completed': 'is_done',
    }
    
    for old_method, new_method in method_mappings.items():
        if old_method in updated_content:
            count = updated_content.count(old_method)
            updated_content = updated_content.replace(old_method, new_method)
            changes_made.append(f"  {old_method}() → {new_method}() ({count} occurrences)")
    
    return updated_content, changes_made

def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single file for status reference updates."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content, changes_made = update_file_content(original_content, file_path)
        
        if changes_made:
            print(f"\n📝 {file_path}")
            for change in changes_made:
                print(change)
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✅ Updated successfully")
            else:
                print(f"  🔍 Would update (dry run)")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update status references to 6-state system')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--root-dir', type=str, default='agentpm',
                       help='Root directory to process (default: agentpm)')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir)
    if not root_dir.exists():
        print(f"❌ Root directory {root_dir} does not exist")
        sys.exit(1)
    
    print(f"🔍 Scanning {root_dir} for status references...")
    print(f"📋 Status mappings:")
    for old, new in STATUS_MAPPINGS.items():
        if '.' in old:  # Only show enum mappings
            print(f"  {old} → {new}")
    
    files_to_process = find_files_to_process(root_dir)
    print(f"\n📁 Found {len(files_to_process)} files to process")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified")
    
    files_updated = 0
    total_changes = 0
    
    for file_path in files_to_process:
        if process_file(file_path, dry_run=args.dry_run):
            files_updated += 1
    
    print(f"\n📊 Summary:")
    print(f"  Files processed: {len(files_to_process)}")
    print(f"  Files updated: {files_updated}")
    
    if args.dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Status reference update complete!")
        print(f"\n🔧 Next steps:")
        print(f"  1. Test the CLI: apm status")
        print(f"  2. Run tests to verify changes")
        print(f"  3. Check for any remaining issues")

if __name__ == '__main__':
    main()
