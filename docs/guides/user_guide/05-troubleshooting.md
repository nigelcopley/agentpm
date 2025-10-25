# AIPM Troubleshooting Guide

**Solutions to Common Issues** | Version 2.0 | Real Errors from fullstack-ecommerce Walkthrough

This guide documents real issues encountered during testing and their solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Initialization Errors](#initialization-errors)
3. [Validation Failures](#validation-failures)
4. [Phase Advancement Issues](#phase-advancement-issues)
5. [Task Lifecycle Errors](#task-lifecycle-errors)
6. [Quality Gate Problems](#quality-gate-problems)
7. [Database Issues](#database-issues)
8. [Performance Problems](#performance-problems)
9. [Common User Mistakes](#common-user-mistakes)
10. [Getting Help](#getting-help)

---

## Installation Issues

### Issue: Module Not Found

**Error**:
```
ModuleNotFoundError: No module named 'agentpm'
```

**Cause**: AIPM not installed or not in Python path

**Solution**:
```bash
# Install in development mode
cd /path/to/aipm-v2
pip install -e .

# Verify installation
python -c "import agentpm; print('✅ Installed')"
```

**Verification**:
```bash
apm --version
# Should show version number
```

---

### Issue: Python Version Too Old

**Error**:
```
SyntaxError: ... (pattern matching or type hints)
```

**Cause**: Python version <3.10

**Solution**:
```bash
# Check Python version
python --version

# Must be Python 3.10 or higher
# Upgrade if needed:
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10
```

---

## Initialization Errors

### Issue: Permission Denied Creating .agentpm Directory

**Error**:
```
PermissionError: [Errno 13] Permission denied: '.agentpm'
```

**Cause**: No write permissions in project directory

**Solution**:
```bash
# Check directory permissions
ls -la .

# Fix permissions if needed
chmod u+w .

# Or run from a directory where you have write access
cd ~/my-projects/my-project
apm init "My Project"
```

---

### Issue: Rules Configuration Failed

**Real Error from fullstack-ecommerce**:
```
Warning: Input is not a terminal (fd=0).
⚠️  Rules configuration failed ([Errno 22] Invalid argument)
You can configure rules later with: apm rules configure
✓ Testing configuration installed
```

**Cause**: Interactive questionnaire cannot run in non-interactive shell

**Solution**:
```bash
# Option 1: Run init with --skip-questionnaire flag
apm init "Project Name" --skip-questionnaire

# Option 2: Configure rules later interactively
apm rules configure

# Option 3: This is just a warning - init still succeeds with defaults
# Continue with default rules and configure later if needed
```

**Impact**: Non-blocking - project initializes with default rules

---

## Validation Failures

### Issue: Task Validation Fails - Work Item Not Ready

**Real Error from fullstack-ecommerce**:
```bash
apm task validate 1
```

**Real Output**:
```
❌ Validation failed:
❌ Cannot validate task: Work item #1 must be 'ready' (currently 'draft')

Fix: apm work-item validate 1

📋 Validation Requirements:
   ✅ Description: 103 characters
   ✅ Effort: 3.0h
   ✅ Time-boxing: 3.0h ≤ 8.0h (design)

💡 Fix the issues above, then run:
   apm task validate 1

Aborted!
```

**Cause**: Task lifecycle depends on parent work item lifecycle. Work item must be in `ready` status before tasks can be validated.

**Solution**:
```bash
# Step 1: Validate work item first
apm work-item validate 1

# Step 2: Then validate task
apm task validate 1

# Or use phase-based workflow instead (recommended)
apm work-item phase-advance 1
```

**Root Cause**: State machine dependency - validates parent before child

---

### Issue: Work Item Validation Error - Metadata Format

**Real Error from fullstack-ecommerce**:
```bash
apm work-item validate 1
```

**Real Output**:
```
❌ Validation failed: Validation error: 'bool' object has no attribute 'get'
```

**Cause**: Metadata structure mismatch between old gate system and new phase system

**Solution**:
```bash
# Use phase-based workflow instead of validate command
# This is the preferred approach in APM (Agent Project Manager)

# Check phase status
apm work-item phase-status 1

# Advance to first phase
apm work-item phase-advance 1

# Continue with phase workflow
apm work-item phase-status 1
```

**Why This Works**: Phase-based workflow is the current implementation, while `validate` command may use deprecated metadata format

---

### Issue: Missing Required Tasks

**Error**:
```
❌ Validation failed: Missing required task types
   ❌ DESIGN task required
   ❌ TESTING task required
```

**Cause**: Work item type has quality gates requiring specific task types

**Solution**:
```bash
# Check which tasks are required
apm work-item show <id>

# Create missing tasks
# For FEATURE work items:
apm task create "Design Task" --work-item-id=<id> --type=design --effort=3
apm task create "Implementation Task" --work-item-id=<id> --type=implementation --effort=4
apm task create "Testing Task" --work-item-id=<id> --type=testing --effort=3
apm task create "Documentation Task" --work-item-id=<id> --type=documentation --effort=2

# Verify quality gates satisfied
apm work-item show <id>
```

**Real Example from fullstack-ecommerce**:
```
Quality Gates:
  FEATURE work items require:
    ✅ DESIGN task
    ✅ IMPLEMENTATION task
    ✅ TESTING task
    ✅ DOCUMENTATION task
```

---

## Phase Advancement Issues

### Issue: Phase Validation Fails

**Error**:
```
❌ Phase gate validation FAILED
Missing requirements:
  • Required task types not present
  • Quality standards not met
```

**Cause**: Phase gate requirements not satisfied

**Solution**:
```bash
# Step 1: Check phase requirements
apm work-item phase-status <id>

# Step 2: Create required tasks for this phase
# See phase requirements in output

# Step 3: Validate before advancing
apm work-item phase-validate <id>

# Step 4: Advance when ready
apm work-item phase-advance <id>
```

**Phase-Specific Requirements**:

**D1 Discovery**:
- Required task types: analysis, research, design
- Must have: business context, requirements

**P1 Planning**:
- Required task types: planning, design
- Must have: effort estimates, dependencies

**I1 Implementation**:
- Required task types: implementation, testing
- Must have: >90% test coverage

**R1 Review**:
- Required task types: testing, review
- Must have: all tests passing

---

### Issue: Cannot Skip Phases

**Error**:
```
❌ Cannot advance: Must progress through phases sequentially
Current: D1_DISCOVERY
Requested: I1_IMPLEMENTATION
Next allowed: P1_PLAN
```

**Cause**: Attempting to skip phases

**Solution**:
```bash
# Phases must be completed in order:
# D1 → P1 → I1 → R1 → O1 → E1

# Advance one phase at a time
apm work-item phase-advance <id>  # D1 → P1
apm work-item phase-advance <id>  # P1 → I1
apm work-item phase-advance <id>  # I1 → R1
# etc.

# OR create work item at specific phase
apm work-item create "Feature" --type=feature --phase=i1_implementation
```

---

## Task Lifecycle Errors

### Issue: Task Time-Boxing Violation

**Error**:
```
❌ Validation failed:
   ❌ Effort 12.0h exceeds maximum 4.0h for implementation tasks
```

**Cause**: Task effort estimate exceeds type-specific limits

**Time-Boxing Limits**:

| Task Type | Max Effort |
|-----------|-----------|
| `implementation` | 4h |
| `bugfix` | 4h |
| `refactoring` | 4h |
| `testing` | 6h |
| `deployment` | 6h |
| `review` | 4h |
| `design` | 8h |
| `analysis` | 8h |
| `documentation` | 8h |
| `planning` | 8h |

**Solution**:
```bash
# Option 1: Break into smaller tasks
apm task create "Implement Part 1" --work-item-id=<id> --type=implementation --effort=4
apm task create "Implement Part 2" --work-item-id=<id> --type=implementation --effort=4
apm task create "Implement Part 3" --work-item-id=<id> --type=implementation --effort=4

# Option 2: Use different task type if appropriate
# e.g., if it's design work, not implementation:
apm task create "Detailed Design" --work-item-id=<id> --type=design --effort=8
```

**Why Time-Boxing**: Keeps tasks manageable, improves estimates, enables better tracking

---

### Issue: Invalid State Transition

**Error**:
```
❌ Invalid state transition: draft → in_progress
Required sequence: draft → validated → accepted → in_progress
```

**Cause**: Attempting to skip required state transitions

**Valid Task Lifecycle**:
```
draft → validated → accepted → in_progress → review → completed
```

**Solution**:
```bash
# Follow proper sequence
apm task validate <id>          # draft → validated
apm task accept <id> --agent <agent>  # validated → accepted
apm task start <id>             # accepted → in_progress
apm task submit-review <id>     # in_progress → review
apm task approve <id>           # review → completed

# OR use automatic transition
apm task next <id>              # Auto-advances to next valid state
```

---

## Quality Gate Problems

### Issue: Feature Quality Gates Not Satisfied

**Error**:
```
❌ Quality gates not satisfied for FEATURE:
   ❌ DESIGN task missing
   ❌ DOCUMENTATION task missing
```

**Cause**: FEATURE work items require 4 specific task types

**Solution**:
```bash
# Check current status
apm work-item show <id>

# Create all required tasks:
apm task create "Design" --work-item-id=<id> --type=design --effort=3
apm task create "Implement" --work-item-id=<id> --type=implementation --effort=4
apm task create "Test" --work-item-id=<id> --type=testing --effort=3
apm task create "Document" --work-item-id=<id> --type=documentation --effort=2

# Verify gates satisfied
apm work-item show <id>
```

**Real Example from fullstack-ecommerce**:
```
Quality Gates:
  FEATURE work items require:
    ✅ DESIGN task
    ✅ IMPLEMENTATION task
    ✅ TESTING task
    ✅ DOCUMENTATION task
```

---

### Issue: Test Coverage Below 90%

**Error**:
```
❌ CI-004 violation: Test coverage 75% < required 90%
```

**Cause**: AIPM enforces >90% test coverage for quality

**Solution**:
```bash
# Step 1: Run coverage report
pytest --cov=your_module --cov-report=html

# Step 2: Identify untested code
# Open htmlcov/index.html in browser

# Step 3: Write missing tests
# Add tests for uncovered code paths

# Step 4: Verify coverage
pytest --cov=your_module --cov-report=term
# Should show >90%
```

**Tips**:
- Write tests during implementation, not after
- Test edge cases and error paths
- Use TDD (Test-Driven Development) approach

---

## Database Issues

### Issue: Database Locked

**Error**:
```
sqlite3.OperationalError: database is locked
```

**Cause**: Multiple processes accessing database simultaneously

**Solution**:
```bash
# Step 1: Check for running AIPM processes
ps aux | grep aipm

# Step 2: Kill any hanging processes
kill -9 <pid>

# Step 3: Remove lock file if exists
rm .agentpm/data/agentpm.db-shm
rm .agentpm/data/agentpm.db-wal

# Step 4: Retry command
apm status
```

**Prevention**: Don't run multiple APM commands simultaneously

---

### Issue: Database Schema Out of Date

**Error**:
```
sqlite3.OperationalError: no such table: work_items
```

**Cause**: Database migrations not run

**Solution**:
```bash
# Run migrations
apm migrate

# Or reinitialize (WARNING: loses data)
rm -rf .agentpm
apm init "Project Name"
```

---

## Performance Problems

### Issue: Slow Commands

**Symptom**: Commands take >5 seconds

**Common Causes**:

1. **Large Database**
   - Database has thousands of records
   - Solution: Add indexes, archive old data

2. **Plugin Overhead**
   - Many plugins running detection
   - Solution: Disable unused plugins

3. **Network Issues**
   - Trying to reach external services
   - Solution: Work offline, check network

**Diagnostic**:
```bash
# Enable verbose mode
apm -v status
apm -v work-item list

# Check database size
du -sh .agentpm/data/agentpm.db

# Check plugin performance
# (plugins run during init)
time apm init "Test Project"
```

---

## Common User Mistakes

### Mistake 1: Not Understanding Work Item Types

**Wrong**:
```bash
# Creating feature but treating like bugfix
apm work-item create "Add Feature" --type=bugfix
```

**Right**:
```bash
# Use correct type for the work
apm work-item create "Add Feature" --type=feature
apm work-item create "Fix Bug" --type=bugfix
apm work-item create "Research Approach" --type=research
```

**Impact**: Wrong quality gates, wrong required tasks

---

### Mistake 2: Skipping Phase Workflow

**Wrong**:
```bash
# Trying to manually change status
apm work-item update <id> --status=completed
```

**Right**:
```bash
# Use phase workflow
apm work-item phase-advance <id>  # Progress through phases
apm work-item phase-status <id>   # Check requirements
```

**Why**: Phase workflow ensures quality gates and proper progression

---

### Mistake 3: Tasks Too Large

**Wrong**:
```bash
# Huge implementation task
apm task create "Build Entire Feature" --work-item-id=<id> --type=implementation --effort=40
```

**Right**:
```bash
# Break into smaller tasks (≤4h each)
apm task create "Implement API Endpoints" --work-item-id=<id> --type=implementation --effort=4
apm task create "Implement Business Logic" --work-item-id=<id> --type=implementation --effort=4
apm task create "Implement Data Layer" --work-item-id=<id> --type=implementation --effort=3
```

**Why**: Better estimates, easier tracking, clearer progress

---

### Mistake 4: Not Providing Context

**Wrong**:
```bash
# Minimal context
apm work-item create "Feature" --type=feature
```

**Right**:
```bash
# Rich context with 6W framework
apm work-item create "Product Catalog API" \
  --type=feature \
  --business-context "Enable product discovery for 1000+ SKUs" \
  --who "E-commerce customers, Product managers" \
  --what "RESTful API for product catalog" \
  --where "backend/api/products/" \
  --when "Sprint 1, Q1 2025" \
  --why "Core business functionality, Revenue generation" \
  --how "Django REST Framework, PostgreSQL, Redis"
```

**Why**: Better AI assistance, clearer requirements, improved planning

---

### Mistake 5: Ignoring Quality Gates

**Wrong**:
```bash
# Trying to bypass gates
# (manually marking as complete without meeting criteria)
```

**Right**:
```bash
# Satisfy quality gates
apm work-item show <id>           # Check requirements
# Create missing tasks
# Complete all required work
apm work-item phase-validate <id> # Validate before advancing
apm work-item phase-advance <id>  # Advance when ready
```

**Why**: Quality gates ensure completeness and prevent technical debt

---

## Getting Help

### Check Command Help

```bash
# General help
apm --help

# Command group help
apm work-item --help
apm task --help

# Specific command help
apm work-item create -h
apm task create -h
```

### Enable Verbose Mode

```bash
# See detailed logging
apm -v status
apm -v work-item create "Feature" --type=feature
```

### Check Documentation

- **Getting Started**: [01-getting-started.md](01-getting-started.md)
- **Quick Reference**: [02-quick-reference.md](02-quick-reference.md)
- **CLI Commands**: [03-cli-commands.md](03-cli-commands.md)
- **Phase Workflow**: [04-phase-workflow.md](04-phase-workflow.md)

### Common Diagnostic Commands

```bash
# Check system status
apm status

# Check database
sqlite3 .agentpm/data/agentpm.db ".tables"
sqlite3 .agentpm/data/agentpm.db "SELECT COUNT(*) FROM work_items;"

# Check project detection
# (re-run init to see detection results)
apm init "Test Project" --skip-questionnaire

# Verify Python environment
python --version
pip list | grep aipm
```

### Debug Database Issues

```bash
# Connect to database
sqlite3 .agentpm/data/agentpm.db

# Useful queries:
.schema work_items              # View table structure
SELECT * FROM work_items;       # View all work items
SELECT * FROM tasks;            # View all tasks
SELECT * FROM rules;            # View all rules
.quit                           # Exit
```

### Reset Project (Last Resort)

```bash
# WARNING: This deletes all data!

# Backup first
cp -r .agentpm .agentpm.backup

# Remove AIPM
rm -rf .agentpm
rm -rf .claude/agents

# Reinitialize
apm init "Project Name"
```

---

## Error Message Reference

### Common Error Patterns

| Error Pattern | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `No such table` | Database not initialized | Run `apm migrate` |
| `database is locked` | Multiple processes | Kill processes, retry |
| `Permission denied` | No write access | Check directory permissions |
| `Invalid state transition` | Skipping states | Use proper lifecycle commands |
| `Quality gates not satisfied` | Missing required tasks | Create missing tasks |
| `Effort exceeds maximum` | Task too large | Break into smaller tasks |
| `Work item must be 'ready'` | Parent not ready | Validate work item first |
| `Validation error: 'bool'` | Metadata format issue | Use phase-based workflow |

---

## Preventive Measures

### Best Practices to Avoid Issues

1. **Always Check Status First**
   ```bash
   apm status
   apm work-item show <id>
   apm work-item phase-status <id>
   ```

2. **Use Phase Workflow**
   - Prefer `phase-advance` over manual status changes
   - Check `phase-status` before advancing
   - Validate with `phase-validate`

3. **Follow Time-Boxing**
   - Keep tasks ≤8h (≤4h for implementation)
   - Break large tasks into smaller ones
   - Use realistic estimates

4. **Satisfy Quality Gates**
   - Check required tasks with `work-item show`
   - Create all required task types
   - Achieve >90% test coverage

5. **Provide Rich Context**
   - Use 6W framework
   - Add business context
   - Define acceptance criteria

6. **Test Before Deploying**
   - Run full test suite
   - Check coverage
   - Validate acceptance criteria

---

## See Also

- [Getting Started Guide](01-getting-started.md) - Learn the basics
- [Quick Reference Card](02-quick-reference.md) - Common workflows
- [CLI Command Reference](03-cli-commands.md) - Complete command docs
- [Phase Workflow Guide](04-phase-workflow.md) - Detailed phase progression

---

**Generated**: 2025-10-17
**APM Version**: 2.0
**Real Examples**: All errors from live walkthrough of fullstack-ecommerce project
