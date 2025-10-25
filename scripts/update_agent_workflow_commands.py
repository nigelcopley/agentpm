#!/usr/bin/env python3
"""
Batch update agent SOP files to standardize on `apm task next` and `apm work-item next` commands.

This script updates the Universal Agent Rules section in all agent SOPs to use the simplified
`next` pattern instead of explicit state transition commands.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
AGENTS_DIR = PROJECT_ROOT / ".claude" / "agents"

# Pattern replacements - order matters (most specific first)
REPLACEMENTS = [
    # Multi-line task lifecycle examples
    (
        r"apm task validate <id>.*?\n.*?apm task accept <id>.*?\n.*?apm task start <id>",
        "apm task next <id>  # Auto-advances through: draft → validated → accepted → in_progress"
    ),

    # Begin work via statements (common in agent SOPs)
    (
        r"Begin work via `apm task start <id>`",
        "Begin work via `apm task next <id>`"
    ),
    (
        r"Begin work via `apm task accept <id> --agent",
        "Accept task via `apm task accept <id> --agent"
    ),

    # Task command replacements
    (
        r"apm task start <task-id>",
        "apm task next <task-id>"
    ),
    (
        r"apm task start <id>",
        "apm task next <id>"
    ),
    (
        r"apm task start 1",
        "apm task next 1"
    ),
    (
        r"apm task start 45",
        "apm task next 45"
    ),
    (
        r"\$ apm task start",
        "$ apm task next"
    ),

    # Work item phase advance commands
    (
        r"apm work-item phase-advance <id>",
        "apm work-item next <id>"
    ),
    (
        r"apm work-item phase-advance 1",
        "apm work-item next 1"
    ),

    # Submit for review patterns (mention both options)
    (
        r"Submit for review via `apm task submit-review <id>`",
        "Submit for review via `apm task next <id>` (or `apm task submit-review <id>`)"
    ),
]


def find_agent_files() -> List[Path]:
    """Find all agent SOP markdown files."""
    agent_files = []

    # Search in all subdirectories
    for root, dirs, files in os.walk(AGENTS_DIR):
        for file in files:
            if file.endswith('.md'):
                agent_files.append(Path(root) / file)

    return sorted(agent_files)


def update_file(file_path: Path) -> Tuple[bool, str]:
    """
    Update a single agent file with new command patterns.

    Returns:
        (changed, message) tuple
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Apply replacements
        changes_made = []
        for pattern, replacement in REPLACEMENTS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"  - Replaced: {pattern[:50]}...")

        # Write back if changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            change_msg = "\n".join(changes_made)
            return True, f"Updated {file_path.relative_to(PROJECT_ROOT)}\n{change_msg}"
        else:
            return False, f"No changes needed: {file_path.relative_to(PROJECT_ROOT)}"

    except Exception as e:
        return False, f"Error updating {file_path.relative_to(PROJECT_ROOT)}: {e}"


def main():
    """Main execution."""
    print("🔍 Finding agent SOP files...")
    agent_files = find_agent_files()
    print(f"   Found {len(agent_files)} agent files\n")

    print("🔄 Updating files...\n")
    updated = 0
    unchanged = 0
    errors = 0

    for file_path in agent_files:
        changed, message = update_file(file_path)

        if changed:
            print(f"✅ {message}\n")
            updated += 1
        elif "Error" in message:
            print(f"❌ {message}\n")
            errors += 1
        else:
            unchanged += 1

    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"   ✅ Updated: {updated}")
    print(f"   ⏭️  Unchanged: {unchanged}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📁 Total: {len(agent_files)}")
    print("="*60)


if __name__ == "__main__":
    main()
