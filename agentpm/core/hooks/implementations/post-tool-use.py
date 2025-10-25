#!/usr/bin/env python3
"""
Claude Code PostToolUse Hook - Python Version (Severity-Based Exit Codes)

Called after each tool execution completes. Can log results, track patterns,
update AIPM database, or inject follow-up guidance.

Hook Input (JSON):
{
    "tool_name": "Bash",
    "parameters": {...},
    "result": "tool output or error",
    "success": true/false,
    "session_id": "uuid"
}

Hook Output (stderr): Injected based on exit code
Exit Codes:
  0 = Silent success (informational, not shown)
  1 = Warning (show stderr, allow continuation)
  2 = N/A (post-tool-use is reactive, cannot block)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def read_hook_input() -> dict:
    """Read JSON hook input from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return {}


def format_tool_feedback(tool_name: str, parameters: dict, result: str, success: bool) -> tuple:
    """
    Format feedback for specific tool execution.

    Returns:
        tuple: (feedback_text, exit_code)
            - exit_code 0: Silent (informational)
            - exit_code 1: Warning (show to user)
            - exit_code 2: N/A (post-tool-use is reactive)
    """
    info_feedback = []    # Exit 0 - silent
    warning_feedback = [] # Exit 1 - show to user

    # Bash tool feedback
    if tool_name == "Bash":
        command = parameters.get("command", "")

        # INFO: Task started
        if "apm task" in command and success and "start" in command:
            info_feedback.append("\n✅ **Task Started**")
            info_feedback.append("Remember to commit frequently (every 30-60 min)")
            info_feedback.append("Update progress notes as you work\n")

        # WARNING: Task submitted for review
        elif "apm task" in command and success and ("complete" in command or "submit-review" in command):
            warning_feedback.append("\n✅ **Task Transitioned**")
            warning_feedback.append("If submitting for review, a different agent should validate")
            warning_feedback.append("Ensure all acceptance criteria are met\n")

        # INFO: Git commit success
        if "git commit" in command and success:
            info_feedback.append("\n✅ **Committed**")
            info_feedback.append("Good practice! Continue committing every 30-60 min")
            info_feedback.append("Remember: Small, focused commits > large commits\n")

        # INFO: Tests passing
        # WARNING: Tests failed
        if "pytest" in command:
            if success and "passed" in result.lower():
                info_feedback.append("\n✅ **Tests Passing**")
                info_feedback.append("Coverage looks good! Target: ≥90% for core modules\n")
            elif not success:
                warning_feedback.append("\n❌ **Tests Failed**")
                warning_feedback.append("Follow workflow: debug → fix → test → commit")
                warning_feedback.append("Never skip or disable tests to make builds pass\n")

    # WARNING: Core code modified
    elif tool_name in ["Edit", "Write"]:
        file_path = parameters.get("file_path", "")
        if success and "agentpm" in file_path:
            warning_feedback.append("\n✅ **Core Code Modified**")
            warning_feedback.append("Next steps:")
            warning_feedback.append("1. Write tests (target ≥90% coverage)")
            warning_feedback.append("2. Run test suite: `pytest tests/core/`")
            warning_feedback.append("3. Commit when tests pass\n")

    # Determine exit code
    if warning_feedback:
        return "\n".join(warning_feedback), 1
    elif info_feedback:
        return "\n".join(info_feedback), 0
    else:
        return "", 0


def main():
    """Main hook entry point."""
    try:
        # Read hook input
        hook_data = read_hook_input()
        tool_name = hook_data.get('tool_name', 'unknown')
        parameters = hook_data.get('parameters', {})
        result = hook_data.get('result', '')
        success = hook_data.get('success', False)
        session_id = hook_data.get('session_id', 'unknown')

        # Log to stderr (not injected into context)
        status = "✅" if success else "❌"
        print(f"🪝 PostToolUse: tool={tool_name}, success={status}, session={session_id}",
              file=sys.stderr)

        # Generate contextual feedback (returns tuple: message, exit_code)
        feedback, exit_code = format_tool_feedback(tool_name, parameters, result, success)

        if feedback:
            # Output to stderr (shown based on exit code)
            print(feedback, file=sys.stderr)

        # Exit with severity-based code
        sys.exit(exit_code)

    except Exception as e:
        print(f"❌ PostToolUse hook error: {e}", file=sys.stderr)
        sys.exit(1)  # Hook error = warning


if __name__ == "__main__":
    main()
