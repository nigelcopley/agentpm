#!/usr/bin/env python3
"""
Claude Code PreCompact Hook - Python Version

Called before Claude compacts/summarizes context (when approaching token limit).
Can mark important context to preserve, log what's being compacted, or
inject priority information.

Hook Input (JSON):
{
    "session_id": "uuid",
    "context_size": 950000,
    "context_limit": 1000000
}

Hook Output (stdout): Injected before compaction
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
        session_id = hook_data.get('session_id', 'unknown')
        context_size = hook_data.get('context_size', 0)
        context_limit = hook_data.get('context_limit', 1000000)

        # Log compaction
        usage_pct = (context_size / context_limit * 100) if context_limit > 0 else 0
        print(f"🪝 PreCompact: {usage_pct:.1f}% context usage", file=sys.stderr)

        # For AIPM, we could:
        # - Mark active work items/tasks as "preserve"
        # - Inject summary of critical state
        # - Save full context to file before compaction
        # - Update NEXT-SESSION.md with current state

        # Inject preservation markers
        print("\n---")
        print("## 🎯 Context Preservation Priorities")
        print("")
        print("**High Priority** (preserve during compaction):")
        print("- Active work items and tasks")
        print("- Recent commits and uncommitted changes")
        print("- Current workflow state and blockers")
        print("- AIPM workflow rules and patterns")
        print("")
        print("**Low Priority** (can compact):")
        print("- Historical sessions and completed work")
        print("- Extensive documentation and guides")
        print("- Detailed logs and verbose output")
        print("---\n")

        sys.exit(0)

    except Exception as e:
        print(f"❌ PreCompact hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
