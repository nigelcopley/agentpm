# AIPM Command Migration Guide

**Version**: 2.0
**Date**: 2025-10-20
**Audience**: AIPM users transitioning to simplified command pattern

## What's Changed?

APM (Agent Project Manager) now recommends simpler `next` commands for typical workflows, while keeping explicit commands available for advanced scenarios.

## Quick Reference: Old vs New

### Task Lifecycle

| Old Pattern (Still Works) | New Pattern (Recommended) | Notes |
|---------------------------|---------------------------|-------|
| `apm task validate 1` | `apm task next 1` | Automatic progression |
| `apm task start 1` | `apm task next 1` | Simpler syntax |
| `apm task submit-review 1` | `apm task next 1` | One command for all |
| `apm task accept 1 --agent python-dev` | `apm task accept 1 --agent python-dev` | **Keep explicit** (needs --agent) |
| `apm task request-changes 1 --reason "..."` | `apm task request-changes 1 --reason "..."` | **Keep explicit** (needs --reason) |

### Work Item Lifecycle

| Old Pattern (Still Works) | New Pattern (Recommended) | Notes |
|---------------------------|---------------------------|-------|
| `apm work-item phase-advance 1` | `apm work-item next 1` | Simpler syntax |
| `apm work-item validate 1` | `apm work-item next 1` | Automatic progression |
| `apm work-item start 1` | `apm work-item next 1` | One command for all |

## When to Use Each Pattern

### Use `next` for (Most Common)

✅ **Happy path workflows**
```bash
# Create and progress work item
apm work-item create "My Feature" --type=feature
apm work-item next 1  # Advance through phases

# Create and work on task
apm task create "Implement feature" --work-item-id=1 --type=implementation --effort=4
apm task next 1  # Start working
apm task next 1  # Submit for review
apm task next 1  # Complete
```

✅ **Quick iteration**
```bash
# Rapid development cycle
apm work-item next 1  # Next phase
apm task next 1       # Next state
```

✅ **Solo development**
```bash
# No need for complex workflows
apm task next 1  # Just keep moving forward
```

### Use Explicit Commands for (Advanced)

🔧 **Agent assignment**
```bash
# Must use explicit accept command
apm task accept 1 --agent python-developer
```

🔧 **Review workflows**
```bash
# Reviewer provides feedback
apm task request-changes 1 --reason "Missing unit tests for edge cases"

# Reviewer approves
apm task approve 1
```

🔧 **Precise state control**
```bash
# When you need exact state transitions
apm task validate 1
apm task start 1
apm task submit-review 1
```

🔧 **Audit trail requirements**
```bash
# Production environments with strict controls
apm work-item validate 1
apm work-item accept 1 --agent backend-team
apm work-item start 1
```

## Migration Examples

### Example 1: Basic Feature Workflow

**Before** (Explicit pattern):
```bash
# Create feature
apm work-item create "User Authentication" --type=feature

# Start D1 phase
apm work-item phase-advance 1

# Create design task
apm task create "Design auth flow" --work-item-id=1 --type=design --effort=3

# Work on task
apm task validate 1
apm task accept 1 --agent designer
apm task start 1
# ... do work ...
apm task submit-review 1
apm task approve 1

# Advance to next phase
apm work-item phase-advance 1
```

**After** (Simplified pattern):
```bash
# Create feature
apm work-item create "User Authentication" --type=feature

# Start D1 phase
apm work-item next 1

# Create design task
apm task create "Design auth flow" --work-item-id=1 --type=design --effort=3

# Work on task
apm task accept 1 --agent designer  # Still need explicit for --agent
apm task next 1  # Start
# ... do work ...
apm task next 1  # Submit for review
apm task next 1  # Complete

# Advance to next phase
apm work-item next 1
```

**Benefits**:
- Fewer commands to remember
- Faster workflow iteration
- Clearer intent ("next" vs multiple state names)

### Example 2: Bug Fix Workflow

**Before** (Explicit pattern):
```bash
apm work-item create "Fix login timeout" --type=bugfix
apm work-item phase-advance 1  # Skip to I1
apm task create "Fix timeout logic" --work-item-id=1 --type=bugfix --effort=2
apm task validate 1
apm task start 1
# ... fix bug ...
apm task submit-review 1
```

**After** (Simplified pattern):
```bash
apm work-item create "Fix login timeout" --type=bugfix
apm work-item next 1  # Skip to I1
apm task create "Fix timeout logic" --work-item-id=1 --type=bugfix --effort=2
apm task next 1  # Start
# ... fix bug ...
apm task next 1  # Submit for review
```

### Example 3: Team Workflow with Reviews

**Scenario**: Multi-person team with review process

```bash
# Developer creates and starts task
apm task create "Add user profile API" --work-item-id=1 --type=implementation --effort=4
apm task accept 1 --agent backend-dev  # Explicit: assign to self
apm task next 1  # Start work

# Developer submits for review
apm task next 1  # Submit to review state

# Reviewer requests changes (explicit)
apm task request-changes 1 --reason "Need input validation and error handling"

# Developer makes changes (auto back to in_progress)
# ... make changes ...
apm task next 1  # Re-submit for review

# Reviewer approves (explicit)
apm task approve 1
```

**Key points**:
- Use `accept --agent` for assignment
- Use `next` for standard transitions
- Use `request-changes --reason` for feedback
- Use `approve` for final approval

## Cheat Sheet

### Most Common Commands

```bash
# Work item progression
apm work-item next <id>     # Use for all phase advancement

# Task progression
apm task next <id>           # Use for most state transitions

# Agent assignment (keep explicit)
apm task accept <id> --agent <name>

# Review feedback (keep explicit)
apm task request-changes <id> --reason "..."
apm task approve <id>
```

### Command Frequency Guide

| Command | When to Use | Frequency |
|---------|-------------|-----------|
| `apm task next` | Most workflows | ⭐⭐⭐⭐⭐ |
| `apm work-item next` | Most workflows | ⭐⭐⭐⭐⭐ |
| `apm task accept --agent` | Agent assignment | ⭐⭐⭐⭐ |
| `apm task request-changes` | Review feedback | ⭐⭐⭐ |
| `apm task approve` | Review approval | ⭐⭐⭐ |
| `apm task validate` | Explicit workflows | ⭐⭐ |
| `apm task start` | Explicit workflows | ⭐ |

## FAQs

### Q: Will my old commands still work?

**A**: Yes! All explicit commands remain fully functional. This is a documentation change only - no breaking changes to the CLI.

### Q: Why should I switch to `next`?

**A**: Benefits include:
- Fewer commands to remember
- Faster workflow progression
- Clearer intent
- Reduced cognitive load
- Still explicit when needed

### Q: When must I use explicit commands?

**A**: Required for:
- Agent assignment (`--agent` flag)
- Review feedback (`--reason` flag)
- Specific state targeting (rare)

### Q: Can I mix both patterns?

**A**: Yes! Use `next` for standard progression and explicit commands when you need flags or precise control.

### Q: What about scripts and automation?

**A**: Both patterns work in scripts:
- Use `next` for simplicity
- Use explicit for audit trails
- Choose based on your needs

### Q: How do I know what state I'm in?

**A**: Check with:
```bash
apm task show <id>
apm work-item show <id>
```

## Learning Path

### Week 1: Try `next` for simple tasks
```bash
apm task next 1  # Instead of start
apm task next 1  # Instead of submit-review
```

### Week 2: Use `next` for work items
```bash
apm work-item next 1  # Instead of phase-advance
```

### Week 3: Master the hybrid approach
```bash
apm task accept 1 --agent python-dev  # Explicit for assignment
apm task next 1                       # Automatic for progression
apm task next 1                       # Automatic for review
apm task approve 1                    # Explicit for approval
```

## Support

**Documentation**:
- [Getting Started](01-getting-started.md) - Updated with `next` examples
- [Quick Reference](02-quick-reference.md) - Command cheat sheet
- [CLI Commands](03-cli-commands.md) - Complete reference

**Help**:
```bash
apm task next --help
apm work-item next --help
```

## Summary

✅ **Use `next` for**: Most workflows (simpler, faster)
🔧 **Use explicit for**: Agent assignment, review feedback, audit requirements

**Remember**: Both patterns work - choose based on your needs!

---

**Updated**: 2025-10-20
**AIPM Version**: 2.0
**Migration Impact**: Zero breaking changes - purely additive
