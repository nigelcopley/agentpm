---
description: Generate intelligent session handover summaries for AIPM database
allowed-tools: Bash(apm:*), Bash(git:*)
---

# /aipm:handover - Session Handover Generator

## Objective
Analyze this session's activity and generate two intelligent summaries for database storage, enabling seamless session continuity.

## Process

### Step 1: Gather Session Data
Execute and analyze:
```bash
apm session status        # Current session activity
apm work-item list        # Active work items
apm task list            # Active tasks
git log -5 --oneline     # Recent commits
git status --short       # Uncommitted changes
```

### Step 2: Generate current_status Summary

Write a 200-300 word project status summary that answers:
- What's the current phase? (e.g., "Phase 2: Core Systems - 85% complete")
- What work items are active? (e.g., "WI-35 in review, WI-25 in progress")
- What's completed recently? (e.g., "Completed 12 tasks, 5 git commits")
- What's blocked or needs attention? (e.g., "Migration issue blocking WI-25")
- What's the project health? (e.g., "90% test coverage, all CI gates passing")

Be specific with numbers, IDs, and concrete status.

### Step 3: Generate next_session Summary

Write a 200-300 word action plan that provides:
- Top priority (1-2 items): "Priority 1: Fix migration_0003 blocker"
- Quick start commands: "apm work-item show 35, pytest tests/", exact commands to run
- Critical context: "Remember: SessionEnd must block if summaries missing"
- Next steps: "1. Review WI-35, 2. Fix migration, 3. Test blocking behavior"
- Relevant resources: "See: docs/migrations/README.md, RULES.md section 3.2"

Be actionable with exact commands and file references.

### Step 4: Store in Database

Execute:
```bash
apm session update \
  --current-status "Your generated status summary" \
  --next-session "Your generated action plan"
```

Confirm storage:
```bash
apm session status  # Verify summaries saved
```

## Success Criteria
- ✅ current_status: Concrete project status with numbers and IDs
- ✅ next_session: Actionable priorities with exact commands
- ✅ Both stored in database (verify with `apm session status`)
- ✅ Next developer can resume in <5 minutes using these summaries

## Output
After completion, confirm:
```
✅ Session handover complete
   • current_status: [X] words, [Y] work items mentioned
   • next_session: [Z] priorities, [N] commands provided
   • Database updated: session [session-id]

Ready to close Claude Code - summaries preserved for next session.
```
