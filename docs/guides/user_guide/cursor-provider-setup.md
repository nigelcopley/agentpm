---
title: Cursor Provider Setup Guide
category: setup_guide
version: 1.0.0
status: active
author: AIPM Documentation
date: 2025-10-20
related:
  - docs/guides/user_guide/cursor-provider-usage.md
  - docs/reference/api/cursor-provider-reference.md
  - docs/operations/troubleshooting/cursor-provider-issues.md
tags:
  - cursor
  - provider
  - installation
  - setup
---

# Cursor Provider Setup Guide

## Overview

The Cursor Provider integrates APM (Agent Project Manager)'s database-driven workflow with Cursor IDE's AI-powered development features. This guide walks you through installation, configuration, and verification.

**What You'll Get**:
- 6 auto-attach Cursor rules matching AIPM patterns
- Bi-directional memory sync (AIPM ↔ Cursor)
- 6 custom modes (one per workflow phase)
- Security guardrails for safe auto-execution
- Hook-based context injection

**Time Required**: 10-15 minutes

---

## Prerequisites

### Required

- **APM (Agent Project Manager) Installed**: Version 2.0.0 or higher
  ```bash
  apm --version  # Should show v2.0.0+
  ```

- **Cursor IDE Installed**: Latest version recommended
  - Download: [https://cursor.com](https://cursor.com)
  - Version: 0.40.0 or higher

- **Project Initialized**: AIPM database exists
  ```bash
  apm status  # Should show project details, not error
  ```

### Optional

- **Git Repository**: For version control integration (recommended)
- **Python 3.10+**: If using AIPM Python provider features
- **Write Access**: To `.cursor/` directory in project root

---

## Installation

### Quick Installation

For default configuration:

```bash
# Navigate to your project root
cd /path/to/your/project

# Install Cursor provider
apm provider install cursor
```

**Expected Output**:
```
🚀 Installing Cursor Provider...

✓ Validating project environment
✓ Creating provider installation record
✓ Rendering rule templates (6 rules)
✓ Installing rules to .cursor/rules/
✓ Generating custom modes (6 modes)
✓ Installing hooks (3 hooks)
✓ Syncing memories (AIPM → Cursor)
✓ Configuring guardrails

✅ Cursor Provider installed successfully!

Next Steps:
1. Restart Cursor IDE
2. Verify rules: Check .cursor/rules/ directory
3. Test integration: Open a file and reference @aipm-context
4. Review custom modes: Cursor Settings → Chat → Custom Modes

Installation ID: 42
Run 'apm provider verify cursor' to validate setup
```

### Interactive Installation

For custom configuration:

```bash
apm provider install cursor --interactive
```

**Interactive Prompts**:

1. **Rule Selection**:
   ```
   Which rules should be installed?
   [x] aipm-master.mdc (Core AIPM orchestration)
   [x] python-implementation.mdc (Python patterns)
   [x] testing-standards.mdc (Test requirements)
   [x] cli-development.mdc (Click CLI patterns)
   [x] database-patterns.mdc (Three-layer architecture)
   [x] documentation-quality.mdc (Doc standards)
   ```

2. **Memory Sync**:
   ```
   Sync AIPM learnings to Cursor Memories?
   [Y/n]: Y

   Include completed work items as memories? [Y/n]: Y
   Include project decisions as memories? [Y/n]: Y
   ```

3. **Custom Modes**:
   ```
   Install AIPM custom modes?
   [x] AIPM Discovery (D1 phase)
   [x] AIPM Planning (P1 phase)
   [x] AIPM Implementation (I1 phase)
   [x] AIPM Review (R1 phase)
   [x] AIPM Operations (O1 phase)
   [x] AIPM Evolution (E1 phase)
   ```

4. **Guardrails**:
   ```
   Configure security guardrails:
   - Auto-run safe commands (pytest, mypy)? [Y/n]: Y
   - Auto-apply edits in Implementation mode? [Y/n]: Y
   - Require confirmation for git operations? [Y/n]: Y
   - Require confirmation for database operations? [Y/n]: Y
   ```

### Installation with Custom Config

Provide configuration file:

```bash
apm provider install cursor --config=.aipm/cursor-config.yml
```

**Example Config** (`.aipm/cursor-config.yml`):

```yaml
# Cursor Provider Configuration
version: 1.0.0

# Rule Configuration
rules:
  enabled_rules:
    - aipm-master
    - python-implementation
    - testing-standards
    - cli-development
    - database-patterns
    - documentation-quality

  auto_attach: true
  update_on_sync: true

# Memory Configuration
memories:
  sync_enabled: true
  sync_direction: bidirectional  # to-cursor, from-cursor, bidirectional
  include_completed_work_items: true
  include_decisions: true
  include_learnings: true
  include_patterns: true
  min_confidence: 0.70

# Custom Modes
custom_modes:
  enabled: true
  install_all: true
  modes:
    - discovery
    - planning
    - implementation
    - review
    - operations
    - evolution

# Guardrails
guardrails:
  auto_run_safe_commands: true
  auto_apply_edits_in_implementation: true

  safe_commands:
    - pytest
    - mypy
    - pylint
    - bandit
    - apm status
    - apm work-item show
    - apm task show

  require_confirmation:
    - git push
    - git tag
    - apm work-item approve
    - rm -rf
    - database operations

# Hooks
hooks:
  enabled: true
  beforeAgentRequest: true
  afterAgentRequest: true
  onFileSave: false  # Can be slow on large projects

# Indexing
indexing:
  exclude_aipm_metadata: true
  exclude_patterns:
    - .aipm/**
    - .cursor/**
    - __pycache__/**
    - "*.pyc"
    - node_modules/**
```

---

## Post-Installation Steps

### 1. Restart Cursor IDE

**Required**: Cursor must be restarted to load new rules and modes.

```bash
# Close Cursor completely
# Reopen your project in Cursor
```

### 2. Verify Installation

Run verification checks:

```bash
apm provider verify cursor
```

**Expected Output**:
```
🔍 Verifying Cursor Provider Installation...

✓ Installation record found (ID: 42)
✓ Rules installed (6/6)
  - aipm-master.mdc
  - python-implementation.mdc
  - testing-standards.mdc
  - cli-development.mdc
  - database-patterns.mdc
  - documentation-quality.mdc
✓ Custom modes configured (6/6)
✓ Hooks installed (3/3)
  - beforeAgentRequest.sh
  - afterAgentRequest.sh
  - onFileSave.sh
✓ Memories synced (12 entries)
✓ Guardrails configured
✓ Cursor IDE detected (version 0.42.0)

✅ Cursor Provider is properly installed and configured!
```

### 3. Manual Verification Checklist

**Check Rule Files**:
```bash
ls -la .cursor/rules/
```

Expected files:
```
aipm-master.mdc
python-implementation.mdc
testing-standards.mdc
cli-development.mdc
database-patterns.mdc
documentation-quality.mdc
```

**Check Hooks**:
```bash
ls -la .cursor/hooks/
```

Expected files (executable):
```
beforeAgentRequest.sh
afterAgentRequest.sh
onFileSave.sh
```

**Check Memories**:
```bash
ls -la .cursor/memories/
```

Expected files (example):
```
project_context-1.md
decision-2.md
learning-3.md
pattern-4.md
```

**Check Cursor Settings**:

1. Open Cursor
2. Go to: Settings → Chat → Custom Modes
3. Verify 6 AIPM modes are listed:
   - AIPM Discovery
   - AIPM Planning
   - AIPM Implementation
   - AIPM Review
   - AIPM Operations
   - AIPM Evolution

### 4. Test @-Symbol Integration

In Cursor chat:

```
@aipm-context
```

**Expected**: Shows current work item context (name, phase, AC, tasks, risks)

```
@aipm-rules
```

**Expected**: Lists active AIPM rules from database

---

## Configuration

### Configuration File Location

**Project-Specific**: `.aipm/providers/cursor.yml`

**Global Defaults**: `~/.config/aipm/providers/cursor.yml`

### Configuration Options

#### Rule Configuration

```yaml
rules:
  # Which rules to install
  enabled_rules:
    - aipm-master           # Required: Core orchestration
    - python-implementation # Optional: Python patterns
    - testing-standards     # Optional: Test requirements
    - cli-development       # Optional: Click CLI
    - database-patterns     # Optional: Three-layer arch
    - documentation-quality # Optional: Doc standards

  # Auto-attach rules to Cursor sessions
  auto_attach: true

  # Update rules when AIPM rules change
  update_on_sync: true

  # Custom rule templates directory
  custom_templates_dir: null  # Or path to custom templates
```

#### Memory Configuration

```yaml
memories:
  # Enable memory sync
  sync_enabled: true

  # Sync direction: to-cursor, from-cursor, bidirectional
  sync_direction: bidirectional

  # What to sync
  include_completed_work_items: true
  include_decisions: true
  include_learnings: true
  include_patterns: true
  include_architectural_decisions: true

  # Quality threshold
  min_confidence: 0.70

  # Automatic sync schedule
  auto_sync_on_work_item_complete: true
  auto_sync_on_phase_change: true
```

#### Custom Modes Configuration

```yaml
custom_modes:
  # Enable custom modes
  enabled: true

  # Install all 6 AIPM modes
  install_all: true

  # Or select specific modes
  modes:
    - discovery        # D1 phase
    - planning         # P1 phase
    - implementation   # I1 phase
    - review           # R1 phase
    - operations       # O1 phase
    - evolution        # E1 phase

  # Mode-specific overrides
  overrides:
    implementation:
      auto_apply_edits: true
      auto_run_commands: true
```

#### Guardrails Configuration

```yaml
guardrails:
  # Auto-run safe commands without confirmation
  auto_run_safe_commands: true

  # Auto-apply edits in Implementation mode
  auto_apply_edits_in_implementation: true

  # Commands that can run without confirmation
  safe_commands:
    - pytest
    - mypy
    - pylint
    - bandit
    - ruff
    - black
    - apm status
    - apm work-item show
    - apm task show
    - apm context show

  # Commands that always require confirmation
  require_confirmation:
    - git push
    - git push --force
    - git tag
    - git reset --hard
    - rm -rf
    - apm work-item approve
    - apm task approve
    - database operations
    - deployment commands

  # File patterns to protect from auto-edit
  protected_files:
    - "*.db"
    - ".env"
    - "credentials.json"
    - "secrets.yml"
```

#### Hooks Configuration

```yaml
hooks:
  # Enable hooks system
  enabled: true

  # Individual hook toggles
  beforeAgentRequest: true   # Inject context before requests
  afterAgentRequest: true    # Update database after requests
  onFileSave: false          # Validate on file save (can be slow)

  # Hook-specific settings
  beforeAgentRequest_settings:
    inject_work_item_context: true
    inject_active_rules: true
    inject_phase_requirements: true

  afterAgentRequest_settings:
    update_task_status: true
    log_ai_interactions: true
```

#### Indexing Configuration

```yaml
indexing:
  # Exclude AIPM metadata from Cursor indexing
  exclude_aipm_metadata: true

  # Additional exclusion patterns
  exclude_patterns:
    - .aipm/**
    - .cursor/**
    - __pycache__/**
    - "*.pyc"
    - "*.pyo"
    - node_modules/**
    - venv/**
    - .venv/**
    - "*.egg-info/**"

  # Include patterns (override exclusions)
  include_patterns:
    - docs/**
    - agentpm/**
```

---

## Troubleshooting Installation

### Issue: "AIPM not initialized"

**Symptom**:
```
❌ Error: AIPM project not initialized in current directory
```

**Solution**:
```bash
# Initialize AIPM in current directory
apm init

# Then retry installation
apm provider install cursor
```

### Issue: "Permission denied creating .cursor/ directory"

**Symptom**:
```
❌ Error: Permission denied: .cursor/rules/
```

**Solution**:
```bash
# Check directory permissions
ls -ld .cursor/

# Create directory with correct permissions
mkdir -p .cursor/rules .cursor/hooks .cursor/memories
chmod 755 .cursor/

# Retry installation
apm provider install cursor
```

### Issue: "Cursor not detected"

**Symptom**:
```
⚠️  Warning: Cursor IDE not detected on system
```

**Solution**:

This is a warning only. Installation will complete, but:

1. **Verify Cursor is installed**: Open Cursor manually
2. **Check Cursor version**: Settings → About
3. **Restart Cursor**: Close completely and reopen
4. **Verify manually**: Check if rules appear in Cursor

### Issue: "Rules not appearing in Cursor"

**Symptom**: Rules installed but not visible in Cursor chat

**Solution**:

```bash
# Verify rules exist
ls -la .cursor/rules/

# Check rule file permissions
chmod 644 .cursor/rules/*.mdc

# Restart Cursor IDE (complete restart required)

# If still not working, check Cursor settings
# Settings → Features → Rules → Ensure "Enable Rules" is checked
```

### Issue: "Memory sync failed"

**Symptom**:
```
❌ Error: Failed to sync memories: No completed work items found
```

**Solution**:

This is expected for new projects. Memories sync from:
- Completed work items
- Captured decisions
- Evolution phase learnings

**To populate memories**:
```bash
# Complete a work item first
apm work-item create "Test Feature" --type=feature
# ... work through phases ...
apm work-item complete <id>

# Then sync memories
apm provider sync-memories cursor
```

### Issue: "Custom modes not appearing"

**Symptom**: Modes installed but not in Cursor settings

**Solution**:

Custom modes require Cursor 0.40.0+:

```bash
# Check Cursor version
# In Cursor: Settings → About

# If version < 0.40.0:
# Update Cursor from https://cursor.com

# After update:
apm provider uninstall cursor
apm provider install cursor
```

---

## Rollback Procedures

### Uninstall Provider

```bash
apm provider uninstall cursor
```

**Actions Taken**:
- Removes `.cursor/rules/` directory
- Removes `.cursor/hooks/` directory
- Keeps `.cursor/memories/` (preserved)
- Removes custom modes from Cursor settings
- Deletes provider installation record from database
- Preserves `.aipm/providers/cursor.yml` config (for re-installation)

**Preserved**:
- Cursor IDE installation (untouched)
- Project files (untouched)
- AIPM database (untouched)
- Memory files (can be deleted manually if needed)

### Partial Uninstall

**Remove only rules**:
```bash
rm -rf .cursor/rules/
```

**Remove only hooks**:
```bash
rm -rf .cursor/hooks/
```

**Remove only memories**:
```bash
rm -rf .cursor/memories/
```

### Re-installation

After uninstall, re-install with:

```bash
apm provider install cursor
```

Configuration from `.aipm/providers/cursor.yml` will be reused.

---

## Next Steps

After successful installation:

1. **Read User Guide**: [cursor-provider-usage.md](../user_guide/cursor-provider-usage.md)
2. **Test Integration**: Create a work item and use `@aipm-context`
3. **Explore Custom Modes**: Try AIPM Implementation mode
4. **Configure Guardrails**: Adjust auto-run settings to your preference
5. **Sync Memories**: Run `apm provider sync-memories cursor` after completing work items

---

## Related Documentation

- **User Guide**: [cursor-provider-usage.md](../user_guide/cursor-provider-usage.md)
- **API Reference**: [cursor-provider-reference.md](../../reference/api/cursor-provider-reference.md)
- **Troubleshooting**: [cursor-provider-issues.md](../../operations/troubleshooting/cursor-provider-issues.md)
- **Architecture**: [cursor-provider-architecture.md](../../architecture/design/cursor-provider-architecture.md)

---

## Support

**Issues**: Report via `apm issue create "Cursor Provider: [description]"`

**Questions**: Check troubleshooting guide first, then create issue

**Feature Requests**: Create improvement work item: `apm work-item create "Cursor Provider: [feature]" --type=improvement`

---

**Last Updated**: 2025-10-20
**Version**: 1.0.0
**Status**: Active
