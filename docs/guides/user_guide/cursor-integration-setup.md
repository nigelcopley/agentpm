# Cursor Integration Setup Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-20
**Related Work Item**: WI-118 "Full Cursor Integration"

---

## Quick Start Checklist

- [ ] Cursor installed (latest version)
- [ ] APM (Agent Project Manager) project initialized (`apm init`)
- [ ] 5 active rule files verified in `.cursor/rules/`
- [ ] Master rule loads automatically
- [ ] Test auto-attach by opening different file types
- [ ] Run `apm status` in Cursor terminal
- [ ] Verify database connection

**Setup Time**: 5-10 minutes

---

## Prerequisites

### Required Software

1. **Cursor IDE** (version 0.40.0 or later)
   - Download from: https://cursor.sh
   - Ensure latest version for best rule support

2. **APM (Agent Project Manager) Project**
   - Project initialized: `apm init`
   - Database created: `.aipm/data/aipm.db`
   - Python environment active

3. **System Requirements**
   - Python 3.11 or later
   - SQLite 3.35.0 or later
   - Terminal access within Cursor

### Knowledge Prerequisites

- Basic understanding of APM (Agent Project Manager) workflow phases (D1 → P1 → I1 → R1 → O1 → E1)
- Familiarity with `apm` command-line interface
- Understanding of database-first architecture

---

## File Structure Overview

### Active Rules (5 Files)

```
.cursor/rules/
├── aipm-master.mdc                 # Master orchestrator (ALWAYS active)
├── cli-development.mdc             # Auto-attach: agentpm/cli/**/*.py
├── database-patterns.mdc           # Auto-attach: **/adapters/**/*.py, **/methods/**/*.py
├── documentation-quality.mdc       # Auto-attach: docs/**/*.md
└── testing-standards.mdc           # Auto-attach: tests/**/*.py

.cursor/rules/_archive/
└── [22 archived rule files]        # Old rules (reference only)
```

**Total Active Rules**: 5 files (down from 22)
**Space Savings**: 65% reduction in active content

### Rule Hierarchy

```
aipm-master.mdc (Priority: 100, Always Active)
  ├─ Database-first command patterns
  ├─ Workflow phase progression (D1 → E1)
  ├─ Quality gate validation
  └─ Agent delegation patterns

Auto-Attach Rules (Context-Aware)
  ├─ cli-development.mdc           → Triggered by: agentpm/cli/**/*.py
  ├─ database-patterns.mdc         → Triggered by: **/adapters/**/*.py, **/methods/**/*.py
  ├─ documentation-quality.mdc     → Triggered by: docs/**/*.md
  └─ testing-standards.mdc         → Triggered by: tests/**/*.py
```

---

## Installation Steps

### 1. Verify File Locations

The Cursor integration files should already be in place from the implementation phase. Verify they exist:

```bash
# Navigate to project root
cd /path/to/aipm-v2

# Check for active rules (should show 5 files)
ls -1 .cursor/rules/*.mdc | grep -v "_archive"

# Expected output:
# .cursor/rules/aipm-master.mdc
# .cursor/rules/cli-development.mdc
# .cursor/rules/database-patterns.mdc
# .cursor/rules/documentation-quality.mdc
# .cursor/rules/testing-standards.mdc
```

If files are missing, they need to be created from the implementation phase (see WI-118).

### 2. Open Project in Cursor

```bash
# Open Cursor in APM (Agent Project Manager) project directory
cursor .

# Or from Cursor:
# File → Open Folder → Select aipm-v2 directory
```

### 3. Verify Rule Loading

**Check Cursor Settings:**
1. Open Cursor Settings (Cmd+, or Ctrl+,)
2. Navigate to: Extensions → Cursor Rules
3. Verify: "Enable Rules" is checked
4. Check loaded rules: Should show `aipm-master.mdc` as always active

**Test in Terminal:**
```bash
# Open integrated terminal in Cursor (Cmd+` or Ctrl+`)
apm status

# Expected: Project dashboard with active work items
# If you see an error, verify database is initialized
```

---

## Verification Checklist

### Master Rule Verification

**Test 1: Master Rule Always Loads**

1. Open Cursor in APM (Agent Project Manager) project
2. Create or open any file (e.g., `test.txt`)
3. Ask Cursor: "What workflow phase am I in?"
4. Expected: Cursor should reference D1 → E1 phases from master rule

**Test 2: Database-First Commands Work**

```bash
# In Cursor terminal:
apm status                        # Should show project dashboard
apm work-item list               # Should list work items
apm rules list                   # Should show rules from database
```

If commands fail, check:
- Python environment is activated
- Database exists at `.aipm/data/aipm.db`
- `apm` command is in PATH

### Auto-Attach Verification

**Test 3: Python Implementation Rules**

1. Open any Python file: `agentpm/cli/status.py`
2. Ask Cursor: "What coding standards should I follow?"
3. Expected: Cursor should reference:
   - Three-layer architecture (from database-patterns.mdc if in adapters/)
   - Click + Rich patterns (from cli-development.mdc if in cli/)
   - Type safety requirements

**Test 4: Testing Standards Rules**

1. Open any test file: `tests/test_workflow.py`
2. Ask Cursor: "What test patterns should I use?"
3. Expected: Cursor should reference:
   - AAA pattern (Arrange-Act-Assert)
   - Coverage requirements (≥ 90%)
   - Pytest fixtures

**Test 5: Documentation Quality Rules**

1. Open any markdown file: `docs/README.md`
2. Ask Cursor: "What documentation standards apply?"
3. Expected: Cursor should reference:
   - Document path structure: `docs/{category}/{document_type}/{filename}`
   - Required categories
   - Quality gate requirements

**Test 6: Database Patterns Rules**

1. Open adapter file: `agentpm/database/adapters/work_item_adapter.py`
2. Ask Cursor: "What patterns should I follow for database code?"
3. Expected: Cursor should reference:
   - Three-layer pattern (Models → Adapters → Methods)
   - Pydantic models for validation
   - ServiceResult pattern

### Command Pattern Verification

**Test 7: Phase-Specific Commands**

```bash
# Test command suggestions based on workflow phase
apm work-item show 118

# Check current phase (e.g., I1_IMPLEMENTATION)
# Ask Cursor: "What commands should I use in this phase?"
# Expected: Cursor suggests I1-appropriate commands:
#   - apm task start <id>
#   - apm context show --task-id=<id>
#   - pytest tests/ -v --cov=agentpm
```

---

## Troubleshooting Common Issues

### Issue 1: Master Rule Not Loading

**Symptoms:**
- Cursor doesn't recognize APM (Agent Project Manager) workflow phases
- No database-first command suggestions

**Diagnosis:**
```bash
# Check if file exists
ls -l .cursor/rules/aipm-master.mdc

# Check file size (should be ~13KB)
du -h .cursor/rules/aipm-master.mdc
```

**Resolution:**
1. Verify file exists and is not corrupted
2. Check Cursor settings: Enable Rules is checked
3. Restart Cursor
4. If still failing, check Cursor logs for errors

### Issue 2: Auto-Attach Rules Not Triggering

**Symptoms:**
- Opening Python files doesn't load Python patterns
- No context-specific suggestions

**Diagnosis:**
1. Check glob pattern in rule file:
```bash
# View rule frontmatter
head -n 20 .cursor/rules/testing-standards.mdc
# Should show:
# ---
# globs:
#   - "tests/**/*.py"
# ---
```

**Resolution:**
1. Verify file paths match glob patterns
2. Close and reopen files to trigger auto-attach
3. Check Cursor version supports glob patterns (≥ 0.40.0)

### Issue 3: apm Commands Not Found

**Symptoms:**
```
bash: apm: command not found
```

**Diagnosis:**
```bash
# Check Python environment
which python
python --version  # Should be 3.11+

# Check if apm is installed
pip show aipm-v2
```

**Resolution:**
1. Activate Python environment:
   ```bash
   source venv/bin/activate  # or appropriate activation command
   ```
2. Install APM (Agent Project Manager) if missing:
   ```bash
   pip install -e .
   ```
3. Verify installation:
   ```bash
   apm --version
   ```

### Issue 4: Database Errors

**Symptoms:**
```
Error: Database not initialized
Error: SQLite version too old
```

**Diagnosis:**
```bash
# Check database exists
ls -lh .aipm/data/aipm.db

# Check SQLite version
sqlite3 --version  # Should be ≥ 3.35.0
```

**Resolution:**
1. Initialize database if missing:
   ```bash
   apm init
   ```
2. Verify database integrity:
   ```bash
   apm status
   ```
3. If corrupted, backup and reinitialize:
   ```bash
   cp .aipm/data/aipm.db .aipm/data/aipm.db.backup
   apm init --force
   ```

### Issue 5: Conflicting Rules

**Symptoms:**
- Contradictory suggestions from Cursor
- Unexpected rule precedence

**Diagnosis:**
```bash
# Check for duplicate rules
find .cursor/rules -name "*.mdc" | sort

# Should only show 5 active rules + archive directory
```

**Resolution:**
1. Verify only 5 active rules (not counting archive)
2. Check rule priorities in frontmatter (master should be 100)
3. Remove any stray rule files from old setup
4. Restart Cursor

---

## Rollback Procedure

If you need to restore the archived rules (e.g., for comparison or debugging):

### Temporary Restoration (Safe)

```bash
# Navigate to project root
cd /path/to/aipm-v2

# Copy archived rule to temporary location
cp .cursor/rules/_archive/old-rule.mdc .cursor/rules/old-rule.mdc.test

# Test in Cursor (rule will load)
# When done, remove:
rm .cursor/rules/old-rule.mdc.test
```

### Full Rollback (Use with Caution)

```bash
# Backup current rules
mkdir -p .cursor/rules/_current_backup
cp .cursor/rules/*.mdc .cursor/rules/_current_backup/

# Restore archived rules
cp .cursor/rules/_archive/*.mdc .cursor/rules/

# Remove consolidated rules
rm .cursor/rules/aipm-master.mdc
rm .cursor/rules/cli-development.mdc
rm .cursor/rules/database-patterns.mdc
rm .cursor/rules/documentation-quality.mdc
rm .cursor/rules/testing-standards.mdc

# Restart Cursor
```

**Warning**: Full rollback restores 22 rule files. Only use if critical issues found.

---

## Custom Mode Support (Future)

**Status**: Designed but not yet implemented (see design spec section 5)

When available, custom modes will provide phase-specific environments:

- **D1 Discovery Mode**: Requirements gathering tools
- **P1 Planning Mode**: Task decomposition tools
- **I1 Implementation Mode**: Build and debug tools
- **R1 Review Mode**: Quality validation tools
- **O1 Operations Mode**: Deployment tools
- **E1 Evolution Mode**: Analytics and improvement tools

**Location**: `.cursor/modes/*.json` (not yet created)

**Activation**: Via Cursor mode selector (when implemented)

---

## Performance Expectations

### Rule Loading Times

| Metric | Target | Typical |
|--------|--------|---------|
| Master rule load | < 200ms | ~50ms |
| Auto-attach trigger | < 100ms | ~30ms |
| Mode activation | < 100ms | N/A (not implemented) |
| Command suggestion | < 50ms | ~20ms |

### Resource Usage

- **Active rules in memory**: 5 files, ~60KB total
- **Archived rules**: 22 files, ~154KB (not loaded)
- **Space savings**: 65% reduction in active content

---

## Next Steps

After verifying setup:

1. **Read Usage Guide**: `docs/cursor-integration/usage.md`
   - Learn how auto-attach works by file type
   - Common workflows with examples
   - Best practices

2. **Review Reference**: `docs/cursor-integration/reference.md`
   - Complete rule specifications
   - Auto-attach pattern reference
   - Command quick reference
   - Migration details

3. **Start Working**: Begin using Cursor with APM (Agent Project Manager)
   - Open files in your workflow phase
   - Use `apm` commands as suggested by rules
   - Let auto-attach rules guide your work

---

## Support Resources

### Documentation

- **Architecture Design**: `docs/architecture/cursor-integration-consolidation-design.md`
- **Usage Guide**: `docs/cursor-integration/usage.md`
- **Reference**: `docs/cursor-integration/reference.md`
- **Developer Guide**: `docs/developer-guide/`

### Commands

```bash
# Get help with any command
apm --help
apm work-item --help
apm task --help

# Check system status
apm status

# List active rules (from database)
apm rules list

# View specific rule
apm rules show DP-001
```

### Troubleshooting

1. Check Cursor version: Help → About
2. Check rule loading: Settings → Extensions → Cursor Rules
3. Check logs: View → Output → Cursor
4. Verify database: `apm status`

---

**Setup Complete!** Proceed to the [Usage Guide](usage.md) to learn how to work with the Cursor integration effectively.
