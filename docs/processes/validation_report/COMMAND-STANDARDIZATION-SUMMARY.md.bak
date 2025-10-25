# AIPM Command Standardization Summary

**Date**: 2025-10-20
**Task**: Standardize on `apm task next` and `apm work-item next` commands throughout all documentation

## Overview

Successfully updated APM (Agent Project Manager) documentation and agent SOPs to emphasize the simpler `next` command pattern over explicit state transition commands. This change improves usability while maintaining support for explicit commands when needed.

## Files Updated

### Core Documentation (4 files)

1. **CLAUDE.md** - Master orchestrator instructions
   - Moved `next` pattern to primary recommendation
   - Reorganized workflow commands section
   - Clarified when to use explicit vs automatic commands

2. **docs/user-guides/01-getting-started.md** - Getting started guide
   - Updated phase advancement examples to use `apm work-item next`
   - Updated task examples to use `apm task next`
   - Simplified workflow instructions

3. **docs/user-guides/02-quick-reference.md** - Quick reference card
   - Reorganized lifecycle commands section (automatic first, explicit second)
   - Updated all workflow examples to use `next` pattern
   - Updated troubleshooting guide with simplified commands

4. **docs/user-guides/03-cli-commands.md** - CLI command reference
   - Updated `apm work-item next` documentation
   - Updated `apm task next` documentation with comprehensive guidance
   - Added "when to use" sections for both patterns

### Agent SOP Files (130 files)

Updated all agent SOP files in `.claude/agents/` directory with pattern replacements:

**Patterns Replaced**:
- `apm task start <id>` → `apm task next <id>`
- `apm work-item phase-advance <id>` → `apm work-item next <id>`
- "Begin work via `apm task start <id>`" → "Begin work via `apm task next <id>`"
- "Submit for review via `apm task submit-review <id>`" → "Submit for review via `apm task next <id>` (or `apm task submit-review <id>`)"

**Total Agent Files Updated**: 130 files
- Orchestrators: 6 files
- Sub-agents: 37 files
- Utilities: 3 files
- Specialists: 84 files

## Command Pattern Philosophy

### Primary Pattern: Automatic Progression (Recommended)

```bash
# Task lifecycle
apm task next <id>               # Auto-advances to next logical state

# Work item lifecycle
apm work-item next <id>          # Auto-advances phase + status
```

**Use cases**:
- ✅ Happy path workflows (most common)
- ✅ Quick development iteration
- ✅ Simple state progression
- ✅ Solo development
- ✅ Reduces command complexity

### Advanced Pattern: Explicit State Control

```bash
# Task commands
apm task validate <id>
apm task accept <id> --agent <role>      # REQUIRES --agent flag
apm task start <id>
apm task submit-review <id>
apm task approve <id>
apm task request-changes <id> --reason "..." # REQUIRES --reason

# Work item commands
apm work-item validate <id>
apm work-item accept <id> --agent <role>
apm work-item start <id>
apm work-item submit-review <id>
apm work-item approve <id>
apm work-item request-changes <id> --reason "..."
```

**Use cases**:
- Agent assignments (need `accept --agent` flag)
- Review workflows (need `request-changes --reason` or `approve`)
- Complex workflows with specific requirements
- Audit trail with detailed reasons
- Production environments with strict controls

## Key Changes

### 1. Documentation Emphasis

**Before**: Pattern A (explicit) listed first as "Recommended for Production"
**After**: Pattern B (automatic/next) listed first as "Recommended" with explicit as "Advanced"

### 2. User Guides

**Before**: Examples showed explicit state transitions
```bash
apm work-item phase-advance 1
apm task start 1
apm task submit-review 1
```

**After**: Examples show simple `next` pattern
```bash
apm work-item next 1
apm task next 1
# (explicit commands mentioned as alternatives)
```

### 3. Agent SOPs

**Before**: "Begin work via `apm task start <id>`"
**After**: "Begin work via `apm task next <id>`"

## Verification

### Test Commands

```bash
# Verify documentation updated
grep -r "phase-advance" docs/user-guides/
grep -r "task start" docs/user-guides/

# Verify agent SOPs updated
grep -r "task start <id>" .claude/agents/
grep -r "task next <id>" .claude/agents/
```

### Expected Behavior

Users should now:
1. Primarily see and use `apm task next` and `apm work-item next`
2. Understand explicit commands exist for advanced use cases
3. Know when each pattern is appropriate
4. Have simpler mental model for typical workflows

## Migration Impact

### User Impact
- **Positive**: Simpler command interface for common workflows
- **Neutral**: Existing explicit commands still work
- **Documentation**: Updated examples are clearer and more concise

### Agent Impact
- **Behavior**: Agent SOPs now recommend simpler pattern
- **Compatibility**: Both patterns supported (hybrid interface)
- **Training**: Agents learn preferred pattern from updated SOPs

### System Impact
- **Code**: No code changes required (commands already exist)
- **Database**: No schema changes
- **CLI**: Full backward compatibility maintained

## Tools Created

### Batch Update Script

Created `/scripts/update_agent_workflow_commands.py`:
- Automated pattern replacement across 130+ agent files
- Configurable regex patterns for precise replacements
- Safe with dry-run mode and verification
- Reusable for future documentation updates

**Usage**:
```bash
python scripts/update_agent_workflow_commands.py
```

## Recommendations

### For Users
1. Start using `apm task next` and `apm work-item next` for typical workflows
2. Use explicit commands when you need agent assignment or review workflows
3. Refer to updated documentation for examples

### For Developers
1. Emphasize `next` pattern in new documentation
2. Keep explicit commands for advanced scenarios
3. Maintain hybrid interface for flexibility

### For Documentation
1. Always show `next` pattern first in examples
2. Mention explicit commands as "Advanced" or "Alternative"
3. Clearly document when explicit commands are required (--agent, --reason flags)

## Success Metrics

✅ **Documentation Consistency**: All user guides standardized
✅ **Agent SOP Updates**: 130 agent files updated
✅ **Pattern Priority**: Automatic progression now primary recommendation
✅ **Backward Compatibility**: Explicit commands still documented and supported
✅ **User Experience**: Simplified command interface for common workflows

## Files Modified

### Documentation
- `/CLAUDE.md`
- `/docs/user-guides/01-getting-started.md`
- `/docs/user-guides/02-quick-reference.md`
- `/docs/user-guides/03-cli-commands.md`

### Scripts
- `/scripts/update_agent_workflow_commands.py` (created)

### Agent SOPs (all files in)
- `.claude/agents/orchestrators/` (6 files)
- `.claude/agents/sub-agents/` (37 files)
- `.claude/agents/utilities/` (3 files)
- `.claude/agents/*.md` (84 specialist files)

## Validation

All changes have been verified:
- ✅ Patterns replaced correctly
- ✅ No syntax errors introduced
- ✅ Examples remain coherent
- ✅ Both command patterns documented
- ✅ Agent SOPs updated consistently

## Conclusion

The standardization successfully simplifies the AIPM command interface while maintaining full backward compatibility. Users now have a clearer, simpler path for common workflows, with explicit commands available when needed for advanced scenarios.

This change aligns with AIPM's goal of being intuitive and user-friendly while preserving power and flexibility for complex workflows.

---

**Generated**: 2025-10-20
**Scope**: Documentation and agent SOP standardization
**Impact**: User experience improvement with zero breaking changes
