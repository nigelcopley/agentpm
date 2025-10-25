#!/usr/bin/env python3
"""
Update all agent files with Universal Agent Rules section.

This script adds mandatory summary and document reference obligations
to all agent definitions in .claude/agents/
"""

import os
import re
from pathlib import Path

# Universal Rules Section Template
UNIVERSAL_RULES_SECTION = """
---

## 🚨 Universal Agent Rules (MANDATORY)

**Before completing any work, you MUST follow these obligations:**

### Rule 1: Summary Creation (REQUIRED)

Create a summary for the entity you worked on:

```bash
# After working on a work item
apm summary create \\
  --entity-type=work_item \\
  --entity-id=<id> \\
  --summary-type=work_item_progress \\
  --content="Progress update, what was accomplished, decisions made, next steps"

# After working on a task
apm summary create \\
  --entity-type=task \\
  --entity-id=<id> \\
  --summary-type=task_completion \\
  --content="What was implemented, tests added, issues encountered"

# After working on a project
apm summary create \\
  --entity-type=project \\
  --entity-id=<id> \\
  --summary-type=session_progress \\
  --content="Session accomplishments, key decisions, next actions"
```

**Summary Types**:
- **Work Item**: `work_item_progress`, `work_item_milestone`, `work_item_decision`
- **Task**: `task_completion`, `task_progress`, `task_technical_notes`
- **Project**: `project_status_report`, `session_progress`
- **Session**: `session_handover`

### Rule 2: Document References (REQUIRED)

Add references for any documents you create or modify:

```bash
# When creating a document
apm document add \\
  --entity-type=work_item \\
  --entity-id=<id> \\
  --file-path="<path>" \\
  --document-type=<type> \\
  --title="<descriptive title>"

# When modifying a document
apm document update <doc-id> \\
  --content-hash=$(sha256sum <path> | cut -d' ' -f1)
```

**Document Types**: `requirements`, `design`, `architecture`, `adr`, `specification`, `test_plan`, `runbook`, `user_guide`

### Validation Checklist

Before marking work complete, verify:

- [ ] Summary created for entity worked on
- [ ] Document references added for files created
- [ ] Document references updated for files modified
- [ ] Summary includes: what was done, decisions made, next steps

**Enforcement**: R1 gate validates summaries and document references exist.

**See**: `docs/agents/UNIVERSAL-AGENT-RULES.md` for complete details.
"""


def find_insertion_point(content: str) -> int:
    """
    Find the best insertion point for Universal Rules section.

    Returns line index where section should be inserted.
    """
    lines = content.split('\n')

    # Strategy: Insert before last section or at end
    # Look for common final sections
    final_sections = [
        '## Prohibited Actions',
        '## Non-Negotiables',
        '## Error Handling',
        '## Examples',
        '## Integration Points',
        '## Quality Standards',
        '## Usage Patterns'
    ]

    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        for section in final_sections:
            if line.startswith(section):
                # Insert before this section
                return i

    # If no final section found, insert at end (before last few empty lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            return i + 1

    return len(lines)


def has_universal_rules(content: str) -> bool:
    """Check if agent file already has Universal Rules section."""
    return '## 🚨 Universal Agent Rules' in content or 'Universal Agent Rules (MANDATORY)' in content


def update_agent_file(file_path: Path) -> tuple[bool, str]:
    """
    Update a single agent file with Universal Rules section.

    Returns:
        (success: bool, message: str)
    """
    try:
        content = file_path.read_text()

        # Check if already updated
        if has_universal_rules(content):
            return True, f"Already has Universal Rules: {file_path.name}"

        # Find insertion point
        lines = content.split('\n')
        insertion_index = find_insertion_point(content)

        # Insert Universal Rules section
        updated_lines = (
            lines[:insertion_index] +
            UNIVERSAL_RULES_SECTION.split('\n') +
            lines[insertion_index:]
        )

        # Write updated content
        file_path.write_text('\n'.join(updated_lines))

        return True, f"✅ Updated: {file_path.name}"

    except Exception as e:
        return False, f"❌ Failed to update {file_path.name}: {str(e)}"


def main():
    """Update all agent files with Universal Rules section."""

    # Find all agent files
    agents_dir = Path(__file__).parent.parent / '.claude' / 'agents'

    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return 1

    # Collect all .md files
    agent_files = list(agents_dir.rglob('*.md'))

    print(f"Found {len(agent_files)} agent files to update\n")

    # Track results
    updated = []
    already_updated = []
    failed = []

    # Update each file
    for agent_file in sorted(agent_files):
        success, message = update_agent_file(agent_file)

        print(message)

        if not success:
            failed.append(agent_file.name)
        elif "Already has" in message:
            already_updated.append(agent_file.name)
        else:
            updated.append(agent_file.name)

    # Print summary
    print("\n" + "="*60)
    print("UPDATE SUMMARY")
    print("="*60)
    print(f"✅ Newly Updated: {len(updated)}")
    print(f"ℹ️  Already Updated: {len(already_updated)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Total Processed: {len(agent_files)}")

    if failed:
        print("\nFailed files:")
        for name in failed:
            print(f"  - {name}")

    return 0 if not failed else 1


if __name__ == '__main__':
    exit(main())
