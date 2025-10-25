#!/usr/bin/env python3
"""
Script to fix document structure to ensure all files follow the correct format:
docs/{category}/{document_type}/{filename}
"""

import os
import shutil
from pathlib import Path

def get_correct_path(file_path: str) -> str:
    """Determine the correct path for a file based on its current location and content."""
    path_parts = file_path.split('/')
    
    # Check if file doesn't follow the 3-level structure (docs/{category}/{document_type}/{filename})
    if len(path_parts) < 4:
        # Map files to their correct locations based on content and naming
        file_mappings = {
            # Root level files in docs/
            'docs/AGENTS.md': 'docs/architecture/other/agents.md',
            'docs/CLAUDE.md': 'docs/architecture/other/claude.md',
            
            # Files missing document_type level (2-level structure)
            'docs/providers/google-formatter.md': 'docs/reference/other/google-formatter.md',
            'docs/planning/V1.0-LAUNCH-READINESS-FINAL.md': 'docs/planning/status_report/v1-0-launch-readiness-final.md',
            'docs/operations/RUNBOOK.md': 'docs/operations/runbook/runbook.md',
            'docs/architecture/SYSTEM_OVERVIEW.md': 'docs/architecture/architecture_doc/system-overview.md',
            'docs/implementation/task-763-search-summaries.md': 'docs/processes/other/task-763-search-summaries.md',
            'docs/api/README.md': 'docs/reference/api_doc/readme.md',
            'docs/developer-guide/ONBOARDING.md': 'docs/guides/developer_guide/onboarding.md',
            'docs/reviews/task-794-contexts-list-ux-review.md': 'docs/processes/test_report/task-794-contexts-list-ux-review.md',
            'docs/reviews/task-794-quick-fixes.md': 'docs/processes/test_report/task-794-quick-fixes.md',
            'docs/reviews/task-795-documents-ux-review.md': 'docs/processes/test_report/task-795-documents-ux-review.md',
            'docs/reviews/task-795-quick-reference.md': 'docs/processes/test_report/task-795-quick-reference.md',
        }
        
        return file_mappings.get(file_path, None)
    
    return None  # Already in correct format

def fix_document_structure():
    """Fix document structure to ensure all files follow the correct format."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    print("🔍 Scanning for files with incorrect structure...")
    
    # Find all markdown files
    all_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                all_files.append(rel_path)
    
    # Check each file
    files_to_move = []
    for file_path in all_files:
        correct_path = get_correct_path(file_path)
        if correct_path:
            files_to_move.append((file_path, correct_path))
    
    print(f"📁 Found {len(all_files)} total markdown files")
    print(f"🔧 Found {len(files_to_move)} files that need to be moved")
    
    if not files_to_move:
        print("✅ All files are already in the correct structure!")
        return
    
    # Show what will be moved
    print("\n📋 Files to be moved:")
    for old_path, new_path in files_to_move:
        print(f"  {old_path} → {new_path}")
    
    # Create directories and move files
    moved_count = 0
    for old_path, new_path in files_to_move:
        try:
            # Create target directory if it doesn't exist
            target_dir = os.path.dirname(new_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # Move the file
            shutil.move(old_path, new_path)
            moved_count += 1
            print(f"✅ Moved: {old_path} → {new_path}")
            
        except Exception as e:
            print(f"❌ Error moving {old_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Successfully moved {moved_count} files")
    print(f"  ❌ Failed to move {len(files_to_move) - moved_count} files")
    
    # Clean up empty directories
    cleanup_empty_directories(docs_dir)

def cleanup_empty_directories(docs_dir):
    """Remove empty directories after moving files."""
    print("\n🧹 Cleaning up empty directories...")
    
    removed_count = 0
    for root, dirs, files in os.walk(docs_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Directory is empty
                    os.rmdir(dir_path)
                    removed_count += 1
                    print(f"🗑️  Removed empty directory: {dir_path}")
            except OSError:
                pass  # Directory not empty or can't be removed
    
    print(f"🧹 Removed {removed_count} empty directories")

def verify_structure():
    """Verify that all files follow the correct structure."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    print("🔍 Verifying document structure...")
    
    incorrect_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                
                # Check if path follows docs/{category}/{document_type}/{filename}
                path_parts = rel_path.split('/')
                if len(path_parts) < 4 or path_parts[0] != 'docs':
                    incorrect_files.append(rel_path)
    
    if incorrect_files:
        print(f"❌ Found {len(incorrect_files)} files with incorrect structure:")
        for path in incorrect_files:
            print(f"  - {path}")
        return False
    else:
        print("✅ All files follow the correct structure!")
        return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_structure()
    else:
        fix_document_structure()
        print("\n🔍 Verifying final structure...")
        verify_structure()
