---
title: Cursor Provider Troubleshooting Guide
category: troubleshooting
version: 1.0.0
status: active
author: AIPM Documentation
date: 2025-10-20
related:
  - docs/guides/setup_guide/cursor-provider-setup.md
  - docs/guides/user_guide/cursor-provider-usage.md
  - docs/reference/api/cursor-provider-reference.md
tags:
  - cursor
  - provider
  - troubleshooting
  - debugging
---

# Cursor Provider Troubleshooting Guide

## Overview

Comprehensive troubleshooting guide for common Cursor Provider issues, including installation failures, hook debugging, memory sync problems, performance issues, and configuration errors.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Rule Loading Issues](#rule-loading-issues)
- [Custom Mode Issues](#custom-mode-issues)
- [Memory Sync Issues](#memory-sync-issues)
- [Hook Issues](#hook-issues)
- [Performance Issues](#performance-issues)
- [@-Symbol Issues](#-symbol-issues)
- [Guardrail Issues](#guardrail-issues)
- [Uninstallation Issues](#uninstallation-issues)
- [Diagnostic Commands](#diagnostic-commands)

---

## Installation Issues

### Issue: "AIPM not initialized"

**Symptom**:
```bash
$ apm provider install cursor
❌ Error: AIPM project not initialized in current directory
Run 'apm init' to initialize AIPM in this project
```

**Cause**: No AIPM database in current directory.

**Solution**:

```bash
# Initialize AIPM first
apm init

# Then install provider
apm provider install cursor
```

**Verification**:
```bash
# Check AIPM status
apm status

# Should show project details, not error
```

---

### Issue: "Permission denied creating .cursor/ directory"

**Symptom**:
```bash
❌ Error: [Errno 13] Permission denied: '.cursor/rules/'
```

**Cause**: Insufficient file system permissions.

**Solution**:

**Option 1**: Fix directory permissions
```bash
# Create directory with correct permissions
mkdir -p .cursor/rules .cursor/hooks .cursor/memories
chmod 755 .cursor/
chmod 755 .cursor/rules/
chmod 755 .cursor/hooks/
chmod 755 .cursor/memories/

# Retry installation
apm provider install cursor
```

**Option 2**: Run with appropriate permissions
```bash
# If project is in restricted location, move it
mv /protected/path/project ~/projects/project
cd ~/projects/project
apm provider install cursor
```

**Verification**:
```bash
ls -ld .cursor/
# Should show: drwxr-xr-x (755 permissions)
```

---

### Issue: "Cursor not detected"

**Symptom**:
```bash
⚠️  Warning: Cursor IDE not detected on system
Installation will complete, but Cursor may need manual configuration
```

**Cause**: Cursor IDE not installed or not in PATH.

**Solution**:

**Step 1**: Verify Cursor installation
- Open Cursor manually
- Check version: Settings → About
- Should be version 0.40.0 or higher

**Step 2**: Installation continues (warning only)
```bash
# Installation completes despite warning
✅ Cursor Provider installed successfully!

# Restart Cursor IDE
# Rules should load automatically
```

**Step 3**: Manual verification
```bash
# Check if rules exist
ls -la .cursor/rules/

# Should show 6 .mdc files
```

**If Cursor version < 0.40.0**:
- Update Cursor from [https://cursor.com](https://cursor.com)
- Reinstall provider after update:
  ```bash
  apm provider uninstall cursor
  apm provider install cursor
  ```

---

### Issue: "Template rendering failed"

**Symptom**:
```bash
❌ Error: Template rendering failed: UndefinedError: 'project.name' is undefined
```

**Cause**: Missing project metadata in database.

**Solution**:

```bash
# Check project metadata
apm project show

# If missing, reinitialize
apm init --force

# Retry installation
apm provider install cursor
```

**Advanced**: Manually update project metadata
```bash
# Open database
sqlite3 .aipm/data/aipm.db

# Check project record
SELECT * FROM projects;

# If empty, insert project
INSERT INTO projects (name, description, created_at)
VALUES ('My Project', 'Project description', datetime('now'));

# Exit database
.quit

# Retry installation
apm provider install cursor
```

---

### Issue: "Configuration validation failed"

**Symptom**:
```bash
❌ Error: Configuration validation failed: Invalid value for 'guardrails.min_confidence': must be between 0.0 and 1.0
```

**Cause**: Invalid configuration file.

**Solution**:

**Step 1**: Check configuration file
```bash
cat .aipm/providers/cursor.yml
```

**Step 2**: Validate YAML syntax
```bash
# Use online YAML validator or:
python -c "import yaml; yaml.safe_load(open('.aipm/providers/cursor.yml'))"
```

**Step 3**: Fix validation errors
Common issues:
- `min_confidence` must be 0.0-1.0
- `sync_direction` must be: `to-cursor`, `from-cursor`, or `bidirectional`
- `enabled_rules` must be list of strings
- Boolean values must be `true`/`false` (lowercase)

**Step 4**: Retry installation
```bash
apm provider install cursor --config=.aipm/providers/cursor.yml
```

**If config is corrupt**: Use defaults
```bash
# Install without custom config (uses defaults)
apm provider install cursor

# Later customize via:
apm provider configure cursor --edit
```

---

## Rule Loading Issues

### Issue: "Rules not appearing in Cursor"

**Symptom**: Rules installed but not visible in Cursor chat.

**Diagnosis**:

```bash
# Step 1: Verify rules exist
ls -la .cursor/rules/

# Expected: 6 .mdc files
# aipm-master.mdc
# python-implementation.mdc
# testing-standards.mdc
# cli-development.mdc
# database-patterns.mdc
# documentation-quality.mdc

# Step 2: Check file permissions
ls -l .cursor/rules/*.mdc

# Should show: -rw-r--r-- (644 permissions)

# Step 3: Check file content
head -20 .cursor/rules/aipm-master.mdc

# Should show markdown content, not empty
```

**Solutions**:

**Solution 1**: Fix file permissions
```bash
chmod 644 .cursor/rules/*.mdc
```

**Solution 2**: Restart Cursor IDE
```bash
# Complete restart required (not just reload window)
# 1. Quit Cursor completely
# 2. Reopen project
```

**Solution 3**: Check Cursor settings
```
In Cursor:
1. Settings → Features → Rules
2. Ensure "Enable Rules" is checked
3. Check "Auto-attach project rules" is enabled
```

**Solution 4**: Reinstall rules
```bash
apm provider install cursor --force
```

**Solution 5**: Manual rule installation
```bash
# Copy rules to Cursor's global rules directory
# macOS:
cp .cursor/rules/*.mdc ~/Library/Application\ Support/Cursor/rules/

# Linux:
cp .cursor/rules/*.mdc ~/.config/Cursor/rules/

# Windows:
# Copy to: %APPDATA%\Cursor\rules\
```

---

### Issue: "Rule content outdated"

**Symptom**: Rules exist but contain old information.

**Cause**: AIPM rules updated but Cursor rules not synced.

**Solution**:

```bash
# Update rules from database
apm provider sync-rules cursor

# Or reinstall
apm provider install cursor --force
```

**Automatic sync**: Enable in config
```yaml
rules:
  update_on_sync: true
```

---

### Issue: "Rules conflicting with other projects"

**Symptom**: Rules from other projects appearing in current project.

**Cause**: Cursor using global rules directory instead of project rules.

**Solution**:

**Step 1**: Verify project-specific rules
```bash
# Rules should be in project directory
ls .cursor/rules/

# NOT in global directory
```

**Step 2**: Check Cursor settings
```
Settings → Features → Rules → Rule Sources:
- Ensure "Project Rules" is enabled
- Consider disabling "Global Rules" if conflicts occur
```

**Step 3**: Clear global rules (if needed)
```bash
# macOS:
rm ~/Library/Application\ Support/Cursor/rules/aipm-*.mdc

# Linux:
rm ~/.config/Cursor/rules/aipm-*.mdc
```

---

## Custom Mode Issues

### Issue: "Custom modes not appearing"

**Symptom**: Modes installed but not in Cursor settings.

**Diagnosis**:

```bash
# Check Cursor version
# In Cursor: Settings → About

# Custom modes require Cursor 0.40.0+
```

**Solutions**:

**If version < 0.40.0**: Update Cursor
```bash
# 1. Download latest Cursor from https://cursor.com
# 2. Install update
# 3. Reinstall provider
apm provider uninstall cursor
apm provider install cursor
```

**If version >= 0.40.0**: Check installation
```bash
# Verify modes configured
apm provider status cursor --verbose

# Should show:
# Custom Modes: 6 installed
```

**Manual verification**:
```
In Cursor:
1. Settings → Chat → Custom Modes
2. Should see 6 AIPM modes:
   - AIPM Discovery
   - AIPM Planning
   - AIPM Implementation
   - AIPM Review
   - AIPM Operations
   - AIPM Evolution
```

**If modes missing**: Reinstall with modes
```bash
apm provider install cursor --force
```

---

### Issue: "Custom mode not working as expected"

**Symptom**: Mode selected but behavior incorrect.

**Diagnosis**:

Check mode configuration:
```bash
# View mode configuration
apm provider configure cursor --get custom_modes.overrides.implementation

# Should show mode settings
```

**Common Issues**:

**1. Auto-apply edits not working**

Check configuration:
```yaml
custom_modes:
  overrides:
    implementation:
      auto_apply_edits: true  # Must be true
```

Also check guardrails:
```yaml
guardrails:
  auto_apply_edits_in_implementation: true  # Must be true
```

**2. Auto-run commands not working**

Check allowlist:
```yaml
guardrails:
  auto_run_safe_commands: true
  safe_commands:
    - pytest  # Must include desired commands
```

**3. Wrong tools enabled**

Each mode has specific tools. Cannot be customized (by design).

To use different tools, switch modes or use default mode.

---

## Memory Sync Issues

### Issue: "Memory sync failed: No completed work items"

**Symptom**:
```bash
$ apm provider sync-memories cursor
⚠️  No memories to sync: No completed work items found
```

**Cause**: Expected for new projects.

**Explanation**:

Memories sync from:
- Completed work items (O1 → E1 transition)
- Captured decisions (in work item metadata)
- Evolution phase learnings

**Solutions**:

**Option 1**: Complete a work item first
```bash
# Create work item
apm work-item create "Test Feature" --type=feature

# Work through phases
apm work-item next <id>  # D1 → P1
apm work-item next <id>  # P1 → I1
# ... implement ...
apm work-item next <id>  # I1 → R1
# ... review ...
apm work-item next <id>  # R1 → O1

# Memory auto-syncs on O1 → E1
```

**Option 2**: Manually create memory
```bash
# Generate memory from active work item
apm provider generate-memory cursor --work-item-id=<id>
```

**Option 3**: Import existing memories
```bash
# If you have manual memories in .cursor/memories/
apm provider sync-memories cursor --direction=from-cursor
```

---

### Issue: "Memory sync conflicts"

**Symptom**:
```bash
⚠️  Memory sync conflict: project_context-1.md
Local file modified, database has newer version
```

**Cause**: Manual edits to memory file while database has updates.

**Solutions**:

**Option 1**: Keep local changes (import to database)
```bash
apm provider sync-memories cursor --direction=from-cursor --force
```

**Option 2**: Keep database version (overwrite local)
```bash
apm provider sync-memories cursor --direction=to-cursor --force
```

**Option 3**: Resolve manually
```bash
# View database version
apm provider list-memories cursor --format=json | grep "project_context-1"

# View file version
cat .cursor/memories/project_context-1.md

# Edit file to merge changes
nano .cursor/memories/project_context-1.md

# Import merged version
apm provider sync-memories cursor --direction=from-cursor
```

**Prevention**: Use `--direction=bidirectional` with care
```bash
# Default bidirectional can cause conflicts
apm provider sync-memories cursor

# Use explicit direction to avoid conflicts
apm provider sync-memories cursor --direction=to-cursor
```

---

### Issue: "Low-confidence memories not syncing"

**Symptom**: Some memories missing after sync.

**Cause**: Confidence threshold filtering.

**Diagnosis**:

```bash
# Check confidence threshold
apm provider configure cursor --get memories.min_confidence

# Default: 0.70 (only memories ≥0.70 sync)
```

**Solutions**:

**Option 1**: Lower threshold temporarily
```bash
apm provider sync-memories cursor --min-confidence=0.50
```

**Option 2**: Update default threshold
```bash
# Edit config
apm provider configure cursor --edit

# Change:
memories:
  min_confidence: 0.50  # Lower threshold

# Sync
apm provider sync-memories cursor
```

**Option 3**: Manually sync specific memory
```bash
# Generate memory regardless of confidence
apm provider generate-memory cursor --work-item-id=<id>
```

---

### Issue: "Memory file format invalid"

**Symptom**:
```bash
❌ Error: Failed to parse memory file: project_context-1.md
Invalid frontmatter format
```

**Cause**: Manually edited memory file with syntax errors.

**Solution**:

**Step 1**: Check file format
```bash
cat .cursor/memories/project_context-1.md
```

**Expected format**:
```markdown
# Title

**Type**: project_context
**Source**: aipm_context
**Confidence**: 0.85
**Created**: 2025-10-20
**Work Item**: WI-125

---

Memory content here...

---

*Generated by APM (Agent Project Manager) Cursor Provider*
```

**Step 2**: Fix format issues
Common issues:
- Missing title (first line)
- Missing metadata (Type, Source, etc.)
- Missing separator lines (`---`)
- Invalid confidence value (must be 0.0-1.0)

**Step 3**: Retry sync
```bash
apm provider sync-memories cursor --direction=from-cursor
```

**If file is corrupt**: Delete and regenerate
```bash
rm .cursor/memories/project_context-1.md
apm provider sync-memories cursor --direction=to-cursor
```

---

## Hook Issues

### Issue: "Hooks not triggering"

**Symptom**: Hooks installed but not executing.

**Diagnosis**:

```bash
# Step 1: Check hooks exist
ls -la .cursor/hooks/

# Expected: 3 .sh files
# beforeAgentRequest.sh
# afterAgentRequest.sh
# onFileSave.sh

# Step 2: Check permissions
ls -l .cursor/hooks/*.sh

# Should show: -rwxr-xr-x (755, executable)

# Step 3: Check hook configuration
apm provider configure cursor --get hooks.enabled

# Should show: true
```

**Solutions**:

**Solution 1**: Fix file permissions
```bash
chmod +x .cursor/hooks/*.sh
```

**Solution 2**: Check Cursor version
```
Hooks require Cursor 0.41.0+
Settings → About → Check version
Update if needed
```

**Solution 3**: Enable hooks in config
```yaml
hooks:
  enabled: true
  beforeAgentRequest: true
  afterAgentRequest: true
```

```bash
# Reload configuration
apm provider configure cursor --reload
```

**Solution 4**: Test hooks manually
```bash
# Test beforeAgentRequest
.cursor/hooks/beforeAgentRequest.sh

# Should execute without errors

# Check for shell errors
bash -n .cursor/hooks/beforeAgentRequest.sh
```

---

### Issue: "Hook errors in console"

**Symptom**: Errors in Cursor console:
```
Hook error: beforeAgentRequest.sh exited with code 1
```

**Diagnosis**:

```bash
# Enable debug logging
apm provider configure cursor --set hooks.debug_logging=true
apm provider configure cursor --reload

# Run hooks manually to see errors
.cursor/hooks/beforeAgentRequest.sh

# Check logs
tail -f .aipm/logs/hooks.log
```

**Common Errors**:

**1. Database not found**
```bash
Error: .aipm/data/aipm.db: No such file or directory
```

**Solution**: Check database path
```bash
# Verify database exists
ls -la .aipm/data/aipm.db

# If missing, reinitialize
apm init
```

**2. Python import errors**
```bash
Error: ModuleNotFoundError: No module named 'agentpm'
```

**Solution**: Ensure AIPM installed
```bash
# Check installation
pip list | grep aipm

# Reinstall if needed
pip install -e .
```

**3. Permission errors**
```bash
Error: Permission denied: .aipm/logs/hooks.log
```

**Solution**: Fix log directory permissions
```bash
mkdir -p .aipm/logs
chmod 755 .aipm/logs
touch .aipm/logs/hooks.log
chmod 644 .aipm/logs/hooks.log
```

---

### Issue: "Hooks causing performance issues"

**Symptom**: Cursor slow when typing or saving files.

**Cause**: `onFileSave` hook running expensive operations.

**Solution**:

**Disable onFileSave hook**:
```yaml
hooks:
  onFileSave: false  # Disable for performance
```

```bash
# Reload configuration
apm provider configure cursor --reload
```

**Or optimize hook**:
```bash
# Edit hook to skip large files
nano .cursor/hooks/onFileSave.sh

# Add at top:
FILE_SIZE=$(stat -f%z "$CURSOR_FILE_PATH" 2>/dev/null || stat -c%s "$CURSOR_FILE_PATH" 2>/dev/null)
if [ "$FILE_SIZE" -gt 100000 ]; then
  exit 0  # Skip files >100KB
fi
```

**Alternative**: Reduce hook operations
```yaml
hooks:
  onFileSave_settings:
    run_linters: false  # Skip slow linters
    check_coverage: false
    validate_rules: true  # Keep fast validations
```

---

## Performance Issues

### Issue: "Slow Cursor startup"

**Symptom**: Cursor takes long to load with AIPM provider.

**Diagnosis**:

```bash
# Check rule file sizes
du -sh .cursor/rules/*

# Large rules slow startup
# Target: <50KB per rule
```

**Solutions**:

**Solution 1**: Reduce enabled rules
```yaml
rules:
  enabled_rules:
    - aipm-master  # Keep only essential
    # Comment out optional rules
    # - python-implementation
    # - testing-standards
```

**Solution 2**: Disable auto-attach
```yaml
rules:
  auto_attach: false  # Manual @-reference instead
```

Reference rules manually in chat:
```
@Rules aipm-master
```

**Solution 3**: Reduce memory count
```yaml
memories:
  max_memories: 50  # Default: 100
  auto_archive_old_memories: true
```

---

### Issue: "Slow indexing with provider"

**Symptom**: Cursor indexing slow after provider installation.

**Cause**: `.aipm/` directory being indexed unnecessarily.

**Solution**:

Check exclusions:
```yaml
indexing:
  exclude_aipm_metadata: true  # Should be true
  exclude_patterns:
    - .aipm/**  # Should be included
```

**Manual exclusion**:

Create `.cursorignore`:
```bash
# .cursorignore
.aipm/
.cursor/
__pycache__/
*.pyc
.venv/
venv/
node_modules/
```

**Verify exclusion**:
```
In Cursor:
1. View → Command Palette
2. "Cursor: Show Indexed Files"
3. Should NOT see .aipm/ files
```

---

### Issue: "Memory sync taking too long"

**Symptom**: `apm provider sync-memories cursor` slow.

**Diagnosis**:

```bash
# Check memory count
apm provider list-memories cursor | wc -l

# >100 memories can be slow
```

**Solutions**:

**Solution 1**: Sync specific types only
```bash
# Sync only recent decisions
apm provider sync-memories cursor --type=decision
```

**Solution 2**: Archive old memories
```yaml
memories:
  auto_archive_old_memories: true
  archive_after_days: 60  # Archive memories >60 days old
```

**Solution 3**: Increase confidence threshold
```bash
# Sync only high-confidence memories
apm provider sync-memories cursor --min-confidence=0.85
```

---

## @-Symbol Issues

### Issue: "@aipm-context not working"

**Symptom**: `@aipm-context` not recognized in Cursor.

**Diagnosis**:

```bash
# Check if custom symbols supported
# Requires Cursor 0.42.0+

# In Cursor: Settings → About
```

**Solutions**:

**If version < 0.42.0**: Update Cursor
```bash
# Update from https://cursor.com
# Then reinstall provider
apm provider install cursor --force
```

**If version >= 0.42.0**: Use hook injection instead

Custom symbols may not be supported yet. Context is injected via `beforeAgentRequest` hook automatically.

**Workaround**: Use standard symbols
```
@Files .aipm/contexts/context-123.txt
```

---

### Issue: "@aipm-context showing wrong work item"

**Symptom**: Context for different work item than expected.

**Cause**: Hook detecting work item from branch name.

**Diagnosis**:

```bash
# Check current branch
git branch --show-current

# Hook parses WI-XXX from branch name
# Example: feature/WI-125-priority → detects WI-125
```

**Solutions**:

**Solution 1**: Use branch naming convention
```bash
# Create branch with work item ID
git checkout -b feature/WI-125-task-priority

# Hook auto-detects WI-125
```

**Solution 2**: Manually specify work item
```bash
# Set environment variable
export AIPM_WORK_ITEM_ID=125

# Hook uses this instead of branch detection
```

**Solution 3**: Disable auto-detection
```yaml
hooks:
  beforeAgentRequest_settings:
    detect_branch_work_item: false
    inject_work_item_context: false
```

Then manually reference:
```
In chat:
"Using work item 125, implement priority field"
```

---

## Guardrail Issues

### Issue: "Safe commands requiring confirmation"

**Symptom**: `pytest` requiring manual confirmation despite being in safe list.

**Diagnosis**:

```bash
# Check guardrails configuration
apm provider configure cursor --get guardrails.safe_commands

# Should include pytest
```

**Solution**:

**Add command to safe list**:
```yaml
guardrails:
  auto_run_safe_commands: true
  safe_commands:
    - pytest
    - pytest *  # Add wildcard for arguments
    - python -m pytest
    - python -m pytest *
```

```bash
# Reload configuration
apm provider configure cursor --reload
```

**Pattern matching**: Commands must match exactly
```yaml
safe_commands:
  - pytest  # Matches: pytest
  - pytest *  # Matches: pytest tests/
  - pytest --cov=*  # Matches: pytest --cov=agentpm
```

---

### Issue: "Auto-apply edits not working"

**Symptom**: Edits not auto-applying in Implementation mode.

**Diagnosis**:

```bash
# Check mode override
apm provider configure cursor --get custom_modes.overrides.implementation.auto_apply_edits

# Should show: true

# Check global setting
apm provider configure cursor --get guardrails.auto_apply_edits_in_implementation

# Should show: true
```

**Solutions**:

**Enable auto-apply**:
```yaml
custom_modes:
  overrides:
    implementation:
      auto_apply_edits: true

guardrails:
  auto_apply_edits_in_implementation: true
```

```bash
# Reload configuration
apm provider configure cursor --reload

# Restart Cursor IDE (required)
```

---

### Issue: "Protected files being edited"

**Symptom**: `.env` file edited despite protection.

**Diagnosis**:

```bash
# Check protected files list
apm provider configure cursor --get guardrails.protected_files
```

**Solution**:

**Add to protected files**:
```yaml
guardrails:
  protected_files:
    - "*.db"
    - ".env"
    - ".env.*"
    - "credentials.json"
    - "secrets.yml"
    - "setup.py"  # Add as needed
```

**Pattern matching**: Use glob patterns
```yaml
protected_files:
  - "*.env"  # Matches: .env, production.env
  - ".env*"  # Matches: .env, .env.local, .env.production
  - "**/.env"  # Matches: .env in any directory
```

---

## Uninstallation Issues

### Issue: "Uninstall fails with errors"

**Symptom**:
```bash
$ apm provider uninstall cursor
❌ Error: Failed to remove .cursor/rules/: Permission denied
```

**Solution**:

**Fix permissions**:
```bash
# Make files writable
chmod -R u+w .cursor/

# Retry uninstall
apm provider uninstall cursor
```

**Force removal**:
```bash
# Manual cleanup
rm -rf .cursor/

# Remove from database
sqlite3 .aipm/data/aipm.db "DELETE FROM provider_installations WHERE provider_name='cursor';"
```

---

### Issue: "Memories not deleted after uninstall"

**Symptom**: `.cursor/memories/` still exists after uninstall.

**Cause**: Default behavior keeps memories.

**Explanation**: Memories preserved by default to prevent data loss.

**Solutions**:

**Option 1**: Delete memories manually
```bash
rm -rf .cursor/memories/
```

**Option 2**: Uninstall with purge
```bash
apm provider uninstall cursor --purge
```

**Option 3**: Keep memories (recommended)
- Memories can be imported when reinstalling
- Safe to keep for future use

---

## Diagnostic Commands

### Full System Diagnostic

```bash
#!/bin/bash
# Run complete diagnostic check

echo "=== AIPM Status ==="
apm status

echo -e "\n=== Provider Status ==="
apm provider status cursor --verbose

echo -e "\n=== Rule Files ==="
ls -la .cursor/rules/

echo -e "\n=== Hook Files ==="
ls -la .cursor/hooks/

echo -e "\n=== Memory Files ==="
ls -la .cursor/memories/

echo -e "\n=== Configuration ==="
cat .aipm/providers/cursor.yml

echo -e "\n=== Verification ==="
apm provider verify cursor --verbose

echo -e "\n=== Cursor Version ==="
# Manual check required in Cursor: Settings → About

echo -e "\n=== Database Check ==="
sqlite3 .aipm/data/aipm.db "SELECT * FROM provider_installations WHERE provider_name='cursor';"

echo -e "\n=== Recent Logs ==="
tail -20 .aipm/logs/hooks.log 2>/dev/null || echo "No hook logs"
```

**Save as**: `diagnose-cursor-provider.sh`

**Run**:
```bash
chmod +x diagnose-cursor-provider.sh
./diagnose-cursor-provider.sh > diagnostic-report.txt
```

---

### Individual Diagnostic Commands

**Check Installation**:
```bash
apm provider status cursor --verbose
```

**Verify Setup**:
```bash
apm provider verify cursor --verbose
```

**Test Rules**:
```bash
# Check if rules load in Cursor
# In Cursor chat: "What rules are active?"
# AI should list 6 AIPM rules
```

**Test Hooks**:
```bash
# Enable debug logging
apm provider configure cursor --set hooks.debug_logging=true
apm provider configure cursor --reload

# Trigger hooks
# In Cursor: Type a message in chat

# Check logs
tail -f .aipm/logs/hooks.log
```

**Test Memory Sync**:
```bash
# Full sync
apm provider sync-memories cursor --force

# Check results
apm provider list-memories cursor
```

**Test Custom Modes**:
```
In Cursor:
1. Click mode selector (top of chat)
2. Select "AIPM Implementation"
3. Verify mode description shows
4. Check enabled tools match Implementation mode
```

**Database Inspection**:
```bash
# Open database
sqlite3 .aipm/data/aipm.db

# Check provider installation
SELECT * FROM provider_installations WHERE provider_name='cursor';

# Check memories
SELECT id, title, memory_type, confidence FROM cursor_memories;

# Exit
.quit
```

---

## Getting Help

### Before Asking for Help

1. **Run diagnostics**:
   ```bash
   apm provider verify cursor --verbose > diagnostic.txt
   ```

2. **Check logs**:
   ```bash
   tail -100 .aipm/logs/hooks.log > hooks.log
   ```

3. **Gather system info**:
   ```bash
   apm --version
   # Cursor version (Settings → About)
   uname -a
   ```

4. **Search existing issues**:
   ```bash
   apm issue list --search="cursor provider"
   ```

### Creating Support Issue

```bash
# Create issue with diagnostic info
apm issue create "Cursor Provider: [describe issue]" \
  --attach=diagnostic.txt \
  --attach=hooks.log
```

**Include in description**:
- Symptom (what's happening)
- Expected behavior (what should happen)
- Steps to reproduce
- Error messages (exact text)
- System info (AIPM version, Cursor version, OS)
- Configuration (relevant sections of cursor.yml)

### Community Support

**Documentation**:
- Setup Guide: [cursor-provider-setup.md](../../guides/setup_guide/cursor-provider-setup.md)
- User Guide: [cursor-provider-usage.md](../../guides/user_guide/cursor-provider-usage.md)
- API Reference: [cursor-provider-reference.md](../../reference/api/cursor-provider-reference.md)

**Architecture**:
- [cursor-provider-architecture.md](../../architecture/design/cursor-provider-architecture.md)

---

## Related Documentation

- **Setup Guide**: [cursor-provider-setup.md](../../guides/setup_guide/cursor-provider-setup.md)
- **User Guide**: [cursor-provider-usage.md](../../guides/user_guide/cursor-provider-usage.md)
- **API Reference**: [cursor-provider-reference.md](../../reference/api/cursor-provider-reference.md)
- **Architecture**: [cursor-provider-architecture.md](../../architecture/design/cursor-provider-architecture.md)

---

**Last Updated**: 2025-10-20
**Version**: 1.0.0
**Status**: Active
