#!/usr/bin/env python3
"""
Test Suite Cleanup Script

Based on agent analysis showing 43% over-engineering:
- Remove framework behavior tests-BAK (94% waste)
- Archive legacy migration tests-BAK
- Consolidate redundant phase gate tests-BAK

Usage:
    python scripts/cleanup-redundant-tests-BAK.py --dry-run  # Preview changes
    python scripts/cleanup-redundant-tests-BAK.py --execute  # Apply changes
"""

import os
import shutil
from pathlib import Path
import argparse


def find_framework_tests():
    """Find tests-BAK that test framework behavior instead of our code."""
    framework_patterns = [
        "test.*click.*",
        "test.*sqlite.*pragma",
        "test.*shutil.*",
        "test.*stdlib.*",
        "test.*typer.*",
        "test.*pydantic.*validation",
    ]
    
    framework_tests = []
    tests_dir = Path("tests-BAK")
    
    for test_file in tests_dir.rglob("test_*.py"):
        content = test_file.read_text()
        
        # Check for framework testing patterns
        if any(pattern.replace(".*", "") in content.lower() for pattern in framework_patterns):
            framework_tests.append(test_file)
    
    return framework_tests


def find_redundant_phase_gate_tests():
    """Find redundant phase gate tests-BAK (15+ files testing same logic)."""
    phase_gate_files = [
        "tests-BAK/core/workflow/test_phase_gate_validation.py",
        "tests-BAK/core/workflow/test_phase_gate_integration.py",
        "tests-BAK/core/workflow/test_phase_gate_integration_additional.py",
        "tests-BAK/core/workflow/test_workflow_validator_integration.py",
    ]
    
    return [Path(f) for f in phase_gate_files if Path(f).exists()]


def find_legacy_migration_tests():
    """Find legacy migration tests-BAK (obsolete migrations 0001-0017)."""
    migration_tests = []
    migration_dir = Path("tests-BAK/core/database/migrations")
    
    if migration_dir.exists():
        for test_file in migration_dir.rglob("test_*.py"):
            content = test_file.read_text()
            # Look for tests-BAK of old migrations
            if any(f"migration_{i:04d}" in content for i in range(1, 18)):
                migration_tests.append(test_file)
    
    return migration_tests


def archive_file(file_path, archive_dir="tests-BAK/archived"):
    """Archive a file instead of deleting it."""
    archive_path = Path(archive_dir)
    archive_path.mkdir(exist_ok=True)
    
    # Preserve directory structure in archive
    relative_path = file_path.relative_to("tests-BAK")
    target_path = archive_path / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.move(str(file_path), str(target_path))
    return target_path


def main():
    parser = argparse.ArgumentParser(description="Clean up redundant tests-BAK")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--execute", action="store_true", help="Apply the changes")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return
    
    print("🧹 APM (Agent Project Manager) Test Suite Cleanup")
    print("=" * 50)
    
    # Find redundant tests-BAK
    framework_tests = find_framework_tests()
    phase_gate_tests = find_redundant_phase_gate_tests()
    migration_tests = find_legacy_migration_tests()
    
    total_files = len(framework_tests) + len(phase_gate_tests) + len(migration_tests)
    
    print(f"📊 Found {total_files} redundant test files:")
    print(f"  - Framework tests-BAK: {len(framework_tests)}")
    print(f"  - Redundant phase gate tests-BAK: {len(phase_gate_tests)}")
    print(f"  - Legacy migration tests-BAK: {len(migration_tests)}")
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN - Files that would be archived:")
        print()
        
        if framework_tests:
            print("Framework Tests (94% waste reduction):")
            for test in framework_tests:
                print(f"  📁 {test}")
            print()
        
        if phase_gate_tests:
            print("Redundant Phase Gate Tests (57% reduction):")
            for test in phase_gate_tests:
                print(f"  📁 {test}")
            print()
        
        if migration_tests:
            print("Legacy Migration Tests (obsolete):")
            for test in migration_tests:
                print(f"  📁 {test}")
            print()
        
        print(f"💾 Total files to archive: {total_files}")
        print("💡 Run with --execute to apply changes")
        
    elif args.execute:
        print("🚀 EXECUTING CLEANUP...")
        print()
        
        archived_count = 0
        
        # Archive framework tests-BAK
        for test in framework_tests:
            archived_path = archive_file(test)
            print(f"📦 Archived: {test} → {archived_path}")
            archived_count += 1
        
        # Archive redundant phase gate tests-BAK (keep one)
        if phase_gate_tests:
            # Keep the main one, archive the rest
            keep_file = phase_gate_tests[0]
            redundant_files = phase_gate_tests[1:]
            
            for test in redundant_files:
                archived_path = archive_file(test)
                print(f"📦 Archived: {test} → {archived_path}")
                archived_count += 1
        
        # Archive legacy migration tests-BAK
        for test in migration_tests:
            archived_path = archive_file(test)
            print(f"📦 Archived: {test} → {archived_path}")
            archived_count += 1
        
        print()
        print(f"✅ Cleanup complete! Archived {archived_count} files")
        print("📝 Note: Files are archived, not deleted. You can restore them if needed.")
        print()
        print("🎯 Next steps:")
        print("  1. Run smoke tests-BAK: pytest -c pytest-smoke.ini")
        print("  2. Run remaining tests-BAK: pytest tests-BAK/ -m 'not smoke'")
        print("  3. Update CI to use smoke tests-BAK for fast feedback")


if __name__ == "__main__":
    main()
