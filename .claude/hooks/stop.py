#!/usr/bin/env python3
"""
Claude Code Stop Hook - Python Version

Called when Claude Code session is interrupted (Ctrl+C, timeout, crash).
Can save emergency state, log interruption, or clean up resources.

Hook Input (JSON):
{
    "session_id": "uuid",
    "reason": "user_interrupt" | "timeout" | "error"
}

Hook Output (stdout): NOT injected into context (session ending)
Note: This hook should be FAST (<500ms) as user is waiting
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main hook entry point."""
    try:
        hook_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
        session_id = hook_data.get('session_id', 'unknown')
        reason = hook_data.get('reason', 'unknown')

        # Log interruption
        print(f"🪝 Stop: session={session_id}, reason={reason}", file=sys.stderr)

        # For AIPM, we could:
        # - Save emergency state to recovery file
        # - Log unfinished work
        # - Mark in-progress tasks as interrupted
        # But SessionEnd hook handles clean shutdowns better

        print(f"\n⚠️ Session interrupted: {reason}\n")
        print("Next session will resume from last known state")
        print("(via SessionStart hook loading NEXT-SESSION.md)\n")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Stop hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
