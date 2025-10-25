# Cursor Hooks Integration Design

**Status**: DRAFT - Awaiting Cursor hooks documentation from https://cursor.com/docs/agent/hooks#hook-events
**Work Item**: WI-120
**Created**: 2025-10-20

---

## Overview

Design for integrating Cursor's hooks system into the AIPM provider, enabling automated workflows triggered by Cursor events.

**⚠️ Note**: This design is based on standard IDE hook patterns. Once we have access to Cursor's official hooks documentation, we'll refine this to match their exact implementation.

---

## Assumed Hook Events

Based on standard IDE patterns and the URL structure, Cursor likely supports:

### 1. Agent Lifecycle Hooks
```typescript
// Before agent processes request
beforeAgentRequest: {
  event: "beforeAgentRequest",
  data: {
    prompt: string,
    model: string,
    context: string[],
    timestamp: string
  }
}

// After agent completes
afterAgentRequest: {
  event: "afterAgentRequest",
  data: {
    prompt: string,
    response: string,
    model: string,
    duration: number,
    success: boolean
  }
}

// On agent error
onAgentError: {
  event: "onAgentError",
  data: {
    error: string,
    prompt: string,
    model: string,
    timestamp: string
  }
}
```

### 2. Model/Settings Hooks
```typescript
// On model switch
onModelSwitch: {
  event: "onModelSwitch",
  data: {
    previousModel: string,
    newModel: string,
    timestamp: string
  }
}

// On settings change
onSettingsChange: {
  event: "onSettingsChange",
  data: {
    changedSettings: Record<string, any>,
    timestamp: string
  }
}
```

### 3. File/Editor Hooks
```typescript
// On file open
onFileOpen: {
  event: "onFileOpen",
  data: {
    filePath: string,
    language: string,
    timestamp: string
  }
}

// On file save
onFileSave: {
  event: "onFileSave",
  data: {
    filePath: string,
    language: string,
    timestamp: string
  }
}
```

---

## AIPM Hook Integration Strategy

### Hook Configuration Format

```yaml
# .cursor/hooks.yml (installed by provider)
hooks:
  beforeAgentRequest:
    enabled: true
    script: ".cursor/hooks/before-agent-request.sh"
    description: "Capture context before AI request"

  afterAgentRequest:
    enabled: true
    script: ".cursor/hooks/after-agent-request.sh"
    description: "Record decisions after AI response"

  onFileSave:
    enabled: true
    script: ".cursor/hooks/on-file-save.sh"
    description: "Track file modifications"
    glob: "**/*.py"  # Only Python files
```

### Hook Scripts (Shell-based)

**`.cursor/hooks/before-agent-request.sh`**:
```bash
#!/bin/bash
# Hook: beforeAgentRequest
# Captures context before AI processes request

# Event data passed as JSON via stdin
EVENT_DATA=$(cat)

# Extract fields
PROMPT=$(echo "$EVENT_DATA" | jq -r '.prompt')
MODEL=$(echo "$EVENT_DATA" | jq -r '.model')

# Capture AIPM context
apm context show --work-item-id=current > /tmp/aipm-context-before.txt

# Log the request
apm learnings record --type=ai-request \
  --content="AI Request: $PROMPT" \
  --metadata="{\"model\": \"$MODEL\", \"timestamp\": \"$(date -Iseconds)\"}"

# Return 0 for success (allows request to proceed)
exit 0
```

**`.cursor/hooks/after-agent-request.sh`**:
```bash
#!/bin/bash
# Hook: afterAgentRequest
# Records decisions and learnings after AI response

EVENT_DATA=$(cat)

RESPONSE=$(echo "$EVENT_DATA" | jq -r '.response')
SUCCESS=$(echo "$EVENT_DATA" | jq -r '.success')
DURATION=$(echo "$EVENT_DATA" | jq -r '.duration')

if [ "$SUCCESS" = "true" ]; then
  # Record the decision
  apm learnings record --type=decision \
    --content="AI-assisted decision: $RESPONSE" \
    --confidence=0.8

  # Update task if in progress
  CURRENT_TASK=$(apm task list --status=active | head -1 | awk '{print $1}')
  if [ -n "$CURRENT_TASK" ]; then
    apm task update $CURRENT_TASK \
      --quality-metadata="{\"ai_assisted\": true, \"model\": \"$MODEL\"}"
  fi
fi

exit 0
```

**`.cursor/hooks/on-file-save.sh`**:
```bash
#!/bin/bash
# Hook: onFileSave
# Tracks file modifications for work item tracking

EVENT_DATA=$(cat)

FILE_PATH=$(echo "$EVENT_DATA" | jq -r '.filePath')
LANGUAGE=$(echo "$EVENT_DATA" | jq -r '.language')

# Update work item artifacts
CURRENT_WI=$(apm work-item list --status=active | head -1 | awk '{print $1}')
if [ -n "$CURRENT_WI" ]; then
  apm work-item update $CURRENT_WI \
    --artifacts="{\"code_paths\": [\"$FILE_PATH\"]}"
fi

# Trigger linting/testing based on file type
if [[ "$FILE_PATH" == *.py ]]; then
  ruff check "$FILE_PATH" || true
fi

exit 0
```

---

## Provider Installation of Hooks

### Hook Installation Flow

```python
# agentpm/providers/cursor/methods.py

class HookMethods:
    """Manages Cursor hook installation and configuration."""

    def install_hooks(self, project_path: Path, config: CursorConfig) -> HookInstallResult:
        """Install AIPM hooks for Cursor."""

        hooks_dir = project_path / ".cursor" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Copy hook templates
        hooks_installed = []
        for hook_name, hook_config in config.hooks.items():
            if hook_config.get("enabled", True):
                # Render hook template
                hook_script = self._render_hook_template(
                    hook_name,
                    project_config=config
                )

                # Write hook file
                hook_path = hooks_dir / f"{hook_name}.sh"
                hook_path.write_text(hook_script)
                hook_path.chmod(0o755)  # Make executable

                hooks_installed.append(hook_name)

        # Create hooks.yml configuration
        hooks_config = self._generate_hooks_config(config)
        (project_path / ".cursor" / "hooks.yml").write_text(hooks_config)

        return HookInstallResult(
            success=True,
            hooks_installed=hooks_installed,
            config_path=".cursor/hooks.yml"
        )

    def _render_hook_template(self, hook_name: str, project_config: CursorConfig) -> str:
        """Render Jinja2 hook template with project config."""
        template_path = TEMPLATES_DIR / "hooks" / f"{hook_name}.sh.j2"
        template = Template(template_path.read_text())

        return template.render(
            project_name=project_config.project.name,
            database_path=project_config.database_path,
            apm_commands=project_config.apm_commands,
        )
```

### Hook Templates Structure

```
agentpm/providers/cursor/templates/hooks/
├── beforeAgentRequest.sh.j2
├── afterAgentRequest.sh.j2
├── onAgentError.sh.j2
├── onModelSwitch.sh.j2
├── onFileSave.sh.j2
├── onFileOpen.sh.j2
└── hooks.yml.j2
```

---

## Hook Event Integration with AIPM

### Use Cases

#### 1. Automatic Context Capture
**Hook**: `beforeAgentRequest`
**AIPM Action**: Capture current work item context before AI processes request
**Value**: Ensures AI has full AIPM context for better responses

#### 2. Decision Recording
**Hook**: `afterAgentRequest`
**AIPM Action**: Record AI-assisted decisions to learnings database
**Value**: Builds institutional knowledge, audit trail

#### 3. Work Item Tracking
**Hook**: `onFileSave`
**AIPM Action**: Update work item artifacts with modified files
**Value**: Automatic work item → code mapping

#### 4. Quality Gates
**Hook**: `onFileSave`
**AIPM Action**: Trigger linting, testing based on file type
**Value**: Continuous quality enforcement

#### 5. Model Performance Tracking
**Hook**: `afterAgentRequest`
**AIPM Action**: Track model performance (success rate, duration)
**Value**: Data-driven model selection

#### 6. Error Analysis
**Hook**: `onAgentError`
**AIPM Action**: Log error patterns, suggest mitigations
**Value**: Proactive error prevention

---

## Configuration

### User-Facing Configuration

```yaml
# .aipm/providers/cursor.yml

# ... (other provider config)

hooks:
  enabled: true

  beforeAgentRequest:
    enabled: true
    capture_context: true
    log_requests: true

  afterAgentRequest:
    enabled: true
    record_decisions: true
    update_work_items: true
    track_performance: true

  onFileSave:
    enabled: true
    update_artifacts: true
    run_linting: true
    file_patterns:
      - "**/*.py"
      - "**/*.ts"

  onAgentError:
    enabled: true
    log_errors: true
    create_issue: false  # Don't auto-create work items for errors
```

### Provider Defaults

```python
# agentpm/providers/cursor/defaults.py

DEFAULT_HOOKS_CONFIG = {
    "enabled": True,
    "beforeAgentRequest": {
        "enabled": True,
        "capture_context": True,
        "log_requests": True,
    },
    "afterAgentRequest": {
        "enabled": True,
        "record_decisions": True,
        "update_work_items": True,
        "track_performance": True,
    },
    "onFileSave": {
        "enabled": True,
        "update_artifacts": True,
        "run_linting": True,
        "file_patterns": ["**/*.py", "**/*.ts", "**/*.js"],
    },
    "onAgentError": {
        "enabled": True,
        "log_errors": True,
        "create_issue": False,
    },
}
```

---

## Database Schema for Hook Tracking

```sql
-- Track hook executions
CREATE TABLE hook_executions (
    id INTEGER PRIMARY KEY,
    hook_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSON,
    executed_at TEXT NOT NULL,
    duration_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    project_path TEXT,
    work_item_id INTEGER REFERENCES work_items(id),
    task_id INTEGER REFERENCES tasks(id)
);

CREATE INDEX idx_hook_executions_hook_name ON hook_executions(hook_name);
CREATE INDEX idx_hook_executions_event_type ON hook_executions(event_type);
CREATE INDEX idx_hook_executions_project_path ON hook_executions(project_path);

-- Track hook performance
CREATE TABLE hook_metrics (
    id INTEGER PRIMARY KEY,
    hook_name TEXT NOT NULL,
    metric_date TEXT NOT NULL,  -- YYYY-MM-DD
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    avg_duration_ms REAL,
    max_duration_ms INTEGER,
    min_duration_ms INTEGER,
    UNIQUE(hook_name, metric_date)
);
```

---

## CLI Commands for Hooks

```bash
# Install hooks
apm provider install cursor --with-hooks

# Manage hooks
apm hooks list                    # Show installed hooks
apm hooks status                  # Check hook execution status
apm hooks enable beforeAgentRequest
apm hooks disable onFileSave
apm hooks test beforeAgentRequest  # Test hook with sample data

# Hook metrics
apm hooks metrics                 # Show hook performance
apm hooks metrics --hook=afterAgentRequest
apm hooks errors                  # Show recent hook errors
```

---

## Error Handling

### Hook Failure Policy

**Default behavior**: Hooks fail gracefully (non-blocking)

```python
class HookExecutor:
    """Executes hooks with error handling."""

    def execute_hook(self, hook_name: str, event_data: dict) -> HookResult:
        try:
            # Execute hook with timeout
            result = subprocess.run(
                [hook_script],
                input=json.dumps(event_data),
                capture_output=True,
                timeout=5,  # 5 second timeout
                text=True
            )

            return HookResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                duration_ms=duration
            )

        except subprocess.TimeoutExpired:
            # Hook took too long - log and continue
            logger.warning(f"Hook {hook_name} timed out after 5s")
            return HookResult(success=False, error="Timeout")

        except Exception as e:
            # Hook failed - log and continue (don't block user)
            logger.error(f"Hook {hook_name} failed: {e}")
            return HookResult(success=False, error=str(e))
```

---

## Testing Strategy

### Hook Testing

```python
# tests/providers/cursor/test_hooks.py

def test_beforeAgentRequest_hook():
    """Test beforeAgentRequest hook captures context."""
    event_data = {
        "prompt": "Implement feature X",
        "model": "claude-3.5",
        "timestamp": "2025-10-20T10:00:00Z"
    }

    result = hook_executor.execute_hook("beforeAgentRequest", event_data)

    assert result.success
    assert "context" in result.output

def test_afterAgentRequest_hook_records_decision():
    """Test afterAgentRequest hook records to database."""
    event_data = {
        "response": "Implemented feature X using pattern Y",
        "success": True,
        "duration": 1500
    }

    result = hook_executor.execute_hook("afterAgentRequest", event_data)

    assert result.success
    # Verify learning was recorded
    learnings = db.query("SELECT * FROM learnings WHERE type='decision'")
    assert len(learnings) > 0
```

---

## Migration Path

### Phase 1: Basic Hooks (Included in WI-120)
- Install hook infrastructure
- Implement core hooks (beforeAgentRequest, afterAgentRequest)
- Basic AIPM integration (context capture, decision recording)

### Phase 2: Advanced Hooks (Future WI)
- File system hooks (onFileSave, onFileOpen)
- Model performance tracking
- Custom hook creation

### Phase 3: Hook Analytics (Future WI)
- Hook performance dashboard
- Hook effectiveness metrics
- Hook optimization recommendations

---

## Open Questions (Require Cursor Docs)

1. **Hook Event List**: What are the exact hook events Cursor supports?
2. **Hook Configuration**: Where do hooks get configured (.cursor/hooks.yml vs Cursor settings)?
3. **Event Data Format**: What exact data does each hook receive?
4. **Hook Execution**: How does Cursor execute hooks (shell scripts, Node.js, Python)?
5. **Hook Ordering**: Can multiple hooks be chained? Execution order?
6. **Hook Blocking**: Can hooks block Cursor operations or always async?
7. **Hook Errors**: How does Cursor handle hook failures?

**Action Required**: Obtain Cursor hooks documentation to answer these questions and refine design.

---

## Immediate Next Steps

1. **Access Cursor docs** at https://cursor.com/docs/agent/hooks#hook-events
2. **Refine this design** based on actual Cursor hook implementation
3. **Update WI-120 architecture** with accurate hooks integration
4. **Implement hooks** as part of provider installation

---

**Document Status**: DRAFT
**Blocked By**: Need access to Cursor hooks documentation
**Assignee**: Architecture team
**Related**: WI-120 (Cursor Provider)
