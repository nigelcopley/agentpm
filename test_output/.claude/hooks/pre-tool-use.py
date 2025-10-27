#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Template Generated

Validates operations before tool execution.
Enforces DOC-020 rule: Database-first document creation.

Generated: 2025-10-27T11:34:30.479549
Template: hooks/pre-tool-use.py.j2
"""

import json
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def validate_write_operation(hook_data: dict) -> tuple[bool, str]:
    """
    Validate Write tool operations.

    Enforces DOC-020: Database-first document creation.

    Args:
        hook_data: Hook input data

    Returns:
        Tuple of (is_valid, message)
    """
    tool_name = hook_data.get('tool_name', '')
    tool_params = hook_data.get('tool_params', {})

    if tool_name != 'Write':
        return True, ""

    file_path = tool_params.get('file_path', '')

    # Check if writing to docs/ directory
    if '/docs/' in file_path or file_path.startswith('docs/'):
        return False, """
⚠️ BLOCK: DOC-020 Violation - Database-First Document Creation

You attempted to write directly to: {file_path}

✅ CORRECT APPROACH:
Use the database-first document command:

apm document add \\
  --entity-type=<work-item|task|project> \\
  --entity-id=<id> \\
  --category=<category> \\
  --type=<type> \\
  --title="<title>" \\
  --content="<content>"

File path will be AUTO-GENERATED based on category and type.

📚 Available Categories:
- planning, architecture, guides, reference, processes, operations

📝 Available Types:
- requirements, design_doc, user_guide, developer_guide, api_doc, adr, test_plan, runbook, deployment_guide, monitoring_guide, incident_report

🔒 This is a BLOCK-level rule. Direct file writes to docs/ are prohibited.

See: .agentpm/docs/governance/quality_gates_spec/agent-operating-protocol-mandatory-workflow-compliance.md
""".format(file_path=file_path)

    return True, ""


def main():
    """Main hook entry point."""
    try:
        hook_data = read_hook_input()

        # Log to stderr
        tool_name = hook_data.get('tool_name', 'unknown')
        print(f"🪝 PreToolUse: tool={tool_name}", file=sys.stderr)

        # Validate Write operations
        is_valid, message = validate_write_operation(hook_data)

        if not is_valid:
            # Block operation
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "blockTool": True,
                    "blockMessage": message
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # Allow operation
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "blockTool": False
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(f"❌ PreToolUse hook error: {e}", file=sys.stderr)
        # On error, allow operation to proceed
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "blockTool": False
            }
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
