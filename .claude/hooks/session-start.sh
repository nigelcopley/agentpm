#!/usr/bin/env bash
#
# Claude Code SessionStart Hook - Load AIPM Context
#
# This hook runs when a Claude Code session starts and injects AIPM project
# context into the conversation to help Claude understand the current state.
#
# Execution Environment:
# - Receives JSON via stdin with: session_id, transcript_path, hook_event_name, source
# - Stdout is added to Claude's context
# - Exit 0 = success, Exit 2 = blocking error (stderr fed to Claude)
# - 60 second timeout
# - Runs in project directory (pwd = CLAUDE_PROJECT_DIR)
#
# CRITICAL: Keep output concise! Large context = token waste + slow startup
#

set -uo pipefail
# Note: NOT using -e (exit on error) because some apm commands may fail gracefully
# We want to show as much context as possible, even if some commands fail

# Read hook input (JSON via stdin)
HOOK_INPUT=$(cat)

# Extract session info for logging (optional)
SESSION_ID=$(echo "$HOOK_INPUT" | jq -r '.session_id // "unknown"')
HOOK_EVENT=$(echo "$HOOK_INPUT" | jq -r '.hook_event_name // "unknown"')

# Log to stderr (visible in transcript mode Ctrl-R, not in context)
echo "🪝 AIPM SessionStart Hook triggered (session: $SESSION_ID)" >&2

# Output to stdout (injected into Claude's context)
echo ""
echo "---"
echo "## 🤖 AIPM Session Context Loaded"
echo ""
echo "**Session Started**: $(date +%Y-%m-%d\ %H:%M:%S)"
echo "**Project**: APM (Agent Project Manager) - AI Project Manager"
echo ""
echo "### 📊 Project Status"

# Run apm status command and capture output
if command -v apm &> /dev/null; then
    echo ""
    apm status 2>&1 || echo "⚠️ apm status failed - check installation"
    echo ""
else
    echo "⚠️ apm command not found - check installation" >&2
    echo "⚠️ apm not available (see installation instructions)"
fi

cat <<'CONTEXT'

### 🎯 Active Work Items
CONTEXT

# Show in-progress work items
if command -v apm &> /dev/null; then
    echo ""
    apm work-item list --status=in_progress 2>&1 | head -20 || echo "No active work items"
    echo ""
fi

cat <<'CONTEXT'

### 📋 Active Tasks
CONTEXT

# Show in-progress and review tasks
if command -v apm &> /dev/null; then
    echo ""
    apm task list --status=in_progress --status=review 2>&1 | head -20 || echo "No active tasks"
    echo ""
fi

cat <<'CONTEXT'

### 📝 Last Session Handover
CONTEXT

# Load NEXT-SESSION.md if it exists (created by SessionEnd hook)
if [ -f "NEXT-SESSION.md" ]; then
    echo ""
    echo "**Handover from previous session:**"
    echo ""
    # Show first 30 lines (active work items, tasks, changes)
    head -50 NEXT-SESSION.md 2>/dev/null || echo "Error reading handover file"
    echo ""
    echo "_(Full handover in NEXT-SESSION.md)_"
    echo ""
else
    echo ""
    echo "No handover from previous session (NEXT-SESSION.md not found)"
    echo ""

    # Fallback: Try to show recent work item summaries
    if command -v apm &> /dev/null; then
        RECENT_WI=$(apm work-item list --status=in_progress --status=review 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "")
        if [ -n "$RECENT_WI" ]; then
            echo "**Recent Work Item #$RECENT_WI:**"
            apm work-item show-history "$RECENT_WI" 2>/dev/null | tail -5 || echo ""
            echo ""
        fi
    fi
fi

cat <<'CONTEXT'

### ⚠️ Critical Reminders

**Workflow Rules** (`RULES.md`):
- Commit early, commit often (every 30-60 min)
- Three-layer database pattern (Models → Adapters → Methods)
- Time-boxing STRICT: IMPLEMENTATION ≤4h
- Use specialist agents via Task tool (never implement directly!)
- Testing >90% coverage (CI-004)

**Agent Selection** (`_RULES/AGENT_SELECTION.md`):
- Always delegate to specialist agents
- Research first: Use sub-agents for discovery (aipm-codebase-navigator, etc.)
- Quality gates: aipm-quality-validator for reviews

**State Transitions**:
- Tasks cannot progress beyond their parent work item's state
- Use workflow commands: `apm task start/submit-review/approve`
- REVIEW state = different agent should review (no self-approval)

### 🚀 Quick Start Commands
```bash
# Check task details
apm task show <id>

# Start work
apm work-item start <id>  # Must do first!
apm task start <id>       # Then start task

# Submit for review
apm task submit-review <id> --notes "Work complete"

# View dependencies
apm task list-dependencies <id>
apm task list-blockers <id>
```

---

CONTEXT

# Exit successfully (output injected into Claude's context)
exit 0
