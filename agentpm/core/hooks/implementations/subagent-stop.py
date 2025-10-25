#!/usr/bin/env python3
"""
Claude Code SubagentStop Hook - Python Version

Called when a sub-agent task completes (launched via Task tool).
Can log sub-agent results, track performance, or inject follow-up guidance.

Hook Input (JSON):
{
    "subagent_type": "quality-engineer",
    "task_description": "Review Task 123",
    "success": true,
    "session_id": "uuid"
}

Hook Output (stdout): Injected into main agent's context
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main hook entry point."""
    try:
        hook_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
        subagent_type = hook_data.get('subagent_type', 'unknown')
        task_desc = hook_data.get('task_description', '')
        success = hook_data.get('success', False)
        session_id = hook_data.get('session_id', 'unknown')

        # Log completion
        status = "✅" if success else "❌"
        print(f"🪝 SubagentStop: type={subagent_type}, success={status}",
              file=sys.stderr)

        # For AIPM, we could:
        # - Log sub-agent usage in database
        # - Track which agents are most useful
        # - Suggest follow-up actions based on agent type
        # - Auto-update task status based on results

        # Inject minimal context
        if success:
            print(f"\n✅ Sub-agent completed: {subagent_type}\n")
            print(f"Task: {task_desc[:80]}{'...' if len(task_desc) > 80 else ''}")
            print("Review their output and decide next steps\n")

        sys.exit(0)

    except Exception as e:
        print(f"❌ SubagentStop hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
