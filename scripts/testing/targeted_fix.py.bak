#!/usr/bin/env python3
"""
Targeted fix script for the most common test issues
Only fixes the most critical patterns that cause the most failures
"""

import os
import re
from pathlib import Path

def fix_agent_names(file_path):
    """Fix invalid agent names - the most common issue"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Only fix the most common invalid agent names
        agent_replacements = {
            '"agent"': '"code-implementer"',
            "'agent'": "'code-implementer'",
            '"test-agent"': '"code-implementer"',
            "'test-agent'": "'code-implementer'",
        }
        
        for old, new in agent_replacements.items():
            content = content.replace(old, new)
        
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
    """Main function to fix agent names in test files"""
    test_dir = Path("tests")
    fixed_count = 0
    total_count = 0
    
    # Process all Python test files
    for py_file in test_dir.rglob("test_*.py"):
        if "archived" in str(py_file):
            continue
            
        total_count += 1
        if fix_agent_names(py_file):
            fixed_count += 1
            print(f"Fixed agent names: {py_file}")
    
    print(f"\nAgent name fix complete: {fixed_count}/{total_count} files modified")

if __name__ == "__main__":
    main()
