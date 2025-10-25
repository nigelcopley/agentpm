#!/usr/bin/env python3
"""
Fix test setups to put work items in the correct state for task transitions
"""

import os
import re
from pathlib import Path

def fix_test_setup(file_path):
    """Fix test setups to use correct work item states"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Work items that need to be in VALIDATED state for task VALIDATED transitions
        # Pattern: WorkItem(status=WorkItemStatus.PROPOSED) followed by task VALIDATED transition
        content = re.sub(
            r'WorkItem\(\s*project_id=([^,]+),\s*name=([^,]+),\s*type=([^,]+),\s*status=WorkItemStatus\.PROPOSED([^)]*)\)',
            r'WorkItem(\n                project_id=\1,\n                name=\2,\n                type=\3,\n                status=WorkItemStatus.VALIDATED\4\n            )',
            content
        )
        
        # Fix 2: Work items that need to be in IN_PROGRESS state for task IN_PROGRESS transitions
        # Pattern: WorkItem(status=WorkItemStatus.PROPOSED) followed by task IN_PROGRESS transition
        content = re.sub(
            r'WorkItem\(\s*project_id=([^,]+),\s*name=([^,]+),\s*type=([^,]+),\s*status=WorkItemStatus\.PROPOSED([^)]*)\)',
            r'WorkItem(\n                project_id=\1,\n                name=\2,\n                type=\3,\n                status=WorkItemStatus.IN_PROGRESS\4\n            )',
            content
        )
        
        # Fix 3: Work items that need to be in REVIEW state for task REVIEW transitions
        # Pattern: WorkItem(status=WorkItemStatus.PROPOSED) followed by task REVIEW transition
        content = re.sub(
            r'WorkItem\(\s*project_id=([^,]+),\s*name=([^,]+),\s*type=([^,]+),\s*status=WorkItemStatus\.PROPOSED([^)]*)\)',
            r'WorkItem(\n                project_id=\1,\n                name=\2,\n                type=\3,\n                status=WorkItemStatus.REVIEW\4\n            )',
            content
        )
        
        # Fix 4: Add missing acceptance criteria to tasks that need them for REVIEW transitions
        # Pattern: Task(..., status=TaskStatus.REVIEW, ...) without quality_metadata
        content = re.sub(
            r'Task\(\s*work_item_id=([^,]+),\s*name=([^,]+),\s*type=([^,]+),\s*status=TaskStatus\.REVIEW([^,]*),\s*assigned_to=([^,]+),\s*effort_hours=([^,)]+)\)',
            r'Task(\n                work_item_id=\1,\n                name=\2,\n                type=\3,\n                status=TaskStatus.REVIEW\4,\n                assigned_to=\5,\n                effort_hours=\6,\n                quality_metadata={"acceptance_criteria": [{"criterion": "Task completed successfully", "met": True}]}\n            )',
            content
        )
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix test setups"""
    test_dir = Path("tests")
    fixed_count = 0
    total_count = 0
    
    # Process workflow test files
    for py_file in test_dir.rglob("test_ci_*.py"):
        if "archived" in str(py_file):
            continue
            
        total_count += 1
        if fix_test_setup(py_file):
            fixed_count += 1
            print(f"Fixed test setup: {py_file}")
    
    print(f"\nTest setup fix complete: {fixed_count}/{total_count} files modified")

if __name__ == "__main__":
    main()
