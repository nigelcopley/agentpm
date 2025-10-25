# APM (Agent Project Manager) CLI and External Tool Integrations - Comprehensive Analysis

## Executive Summary

APM (Agent Project Manager) implements four critical CLI/external tool integrations for orchestrating development workflows:

1. **Integration with External CLI Tools** (pytest, coverage, git)
2. **Shell Completion Integration** (bash/zsh argument completion)
3. **Git Integration** (repository status, commit tracking, metadata capture)
4. **Shell Command Execution** (secure subprocess management)

---

## 1. INTEGRATION WITH OTHER CLI TOOLS (Task 695)

### 1.1 External Tools Integrated

#### A. pytest (Python Testing Framework)
**Location**: `/agentpm/cli/commands/task/submit_review.py`

```python
# Execute pytest for test health check
result = subprocess.run(
    ["python", "-m", "pytest", "-q", "--maxfail=1"],
    cwd=str(project_root),
    capture_output=True,
    text=True,
    timeout=60
)
```

**Use Case**: When submitting tasks for review, AIPM runs the full test suite to detect global test failures outside the task's scope.

**Error Handling**:
- Timeout: 60 seconds
- Non-zero exit codes are captured (no exception thrown)
- Graceful failure: Silent failure if pytest not available
- Best-effort: Results are advisory, not blocking

**Data Exchange**:
- Input: Project root path
- Output: Return code (0 = pass, non-zero = failures), stdout, stderr

#### B. coverage (Python Coverage.py)
**Location**: `/agentpm/core/testing/coverage.py`

```python
# Run coverage analysis
cmd = [
    'python3', '-m', 'coverage', 'run', '--source=.', '-m', 'pytest'
]
result = subprocess.run(
    cmd,
    cwd=self.project_path,
    capture_output=True,
    text=True,
    timeout=300  # 5 minutes
)

# Get coverage report as JSON
report_cmd = ['python3', '-m', 'coverage', 'json', '-o', '-']
report_result = subprocess.run(report_cmd, ...)
coverage_data = json.loads(report_result.stdout)
```

**Use Case**: Calculate test coverage by category (critical_paths, user_facing, etc.)

**Features**:
- Category-specific coverage calculation
- Requirement validation (e.g., "critical_paths" must be >= 95%)
- JSON output parsing for programmatic access

**Timeout Handling**: 300 seconds (5 minutes) with timeout exception handling

### 1.2 Data Exchange Format

#### subprocess.run() Pattern
All external tool execution uses the **safe command list format**:

```python
# SAFE: Command as list (no shell injection)
subprocess.run(
    ["python", "-m", "pytest"],
    capture_output=True,
    text=True,
    timeout=SECONDS
)

# UNSAFE (never used): String shell commands
# subprocess.run("python -m pytest", shell=True)  # NEVER
```

#### Output Capture
```python
result = subprocess.run(...)
success = result.returncode == 0
stdout = result.stdout  # Sanitized for logging
stderr = result.stderr
```

### 1.3 End-to-End Workflow Example: Submit Task for Review

```
User Input: apm task submit-review 123 --notes "Complete"
         │
         ├─→ [Workflow Service] Validate task state
         │
         ├─→ [SecureCommandExecutor] Run pytest
         │   └─→ subprocess.run(["python", "-m", "pytest", "-q", "--maxfail=1"])
         │       ├─→ Success (RC=0): Task can proceed to REVIEW
         │       └─→ Failure (RC!=0): Show guidance to fix tests
         │
         └─→ Return to user with pass/fail status
```

### 1.4 Error Handling Patterns

```python
try:
    result = subprocess.run(cmd, timeout=TIMEOUT)
    
except subprocess.TimeoutExpired as e:
    return {
        "success": False,
        "error": "timeout",
        "stderr": f"Command timed out after {e.timeout} seconds"
    }
    
except Exception as e:
    return {
        "success": False,
        "error": "execution_failed",
        "stderr": str(e)
    }
```

**Key Characteristics**:
- Non-blocking: Failures don't stop workflow (advisory)
- Graceful degradation: Missing tools don't break AIPM
- Silent fail: Unrelated test failures are warnings, not blockers

---

## 2. SHELL COMPLETION INTEGRATION (Task 696)

### 2.1 CLI Architecture: LazyGroup Pattern

**Location**: `/agentpm/cli/main.py`

```python
class LazyGroup(click.Group):
    """Lazy-loading command group for fast CLI startup"""
    
    def get_command(self, ctx: click.Context, cmd_name: str):
        COMMANDS = {
            'init': 'agentpm.cli.commands.init:init',
            'work-item': 'agentpm.cli.commands.work_item:work_item',
            'task': 'agentpm.cli.commands.task:task',
            # ... 20+ commands
        }
        
        # Dynamic import only when invoked
        module_path, attr = COMMANDS[cmd_name].rsplit(':', 1)
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
```

**Performance Impact**:
- Standard import: 400-600ms startup
- Lazy loading: 80-120ms startup (70-85% faster)

### 2.2 Click Framework Integration

AIPM uses **Click 8.1.7+** for CLI parameter handling:

```python
@click.command()
@click.argument('task_id', type=int)
@click.option('--notes', type=str, help='Submission notes')
@click.pass_context
def submit_review(ctx: click.Context, task_id: int, notes: str = None):
    """Submit task for review"""
    pass
```

### 2.3 Bash Completion Support

**How It Works**:
1. Click generates completion context automatically
2. Shell (bash/zsh) requests available commands
3. LazyGroup's `list_commands()` returns all 20+ commands

```python
def list_commands(self, ctx: click.Context) -> list[str]:
    return [
        'init', 'work-item', 'task', 'idea', 'session',
        'context', 'status', 'agents', 'rules', 'testing',
        'commands', 'migrate', 'migrate-v1-to-v2', 'document',
        'template', 'summary', 'search', 'skills', 'claude-code',
        'provider', 'memory'
    ]
```

### 2.4 Shell Completion Installation

**Expected Implementation** (not yet found in codebase):
```bash
# bash completion
eval "$(_APM_COMPLETE=bash_source apm)"

# zsh completion
eval "$(_APM_COMPLETE=zsh_source apm)"
```

**Click handles this automatically via `_COMPLETE` environment variable**

### 2.5 Completion Types Supported

1. **Command Completion**: `apm [TAB]` → Lists commands
2. **Argument Completion**: `apm task [TAB]` → Lists subcommands
3. **Option Completion**: `apm task --[TAB]` → Lists options
4. **Dynamic Completion**: Click calls command `shell_complete()` method

---

## 3. GIT INTEGRATION (Task 698)

### 3.1 Git Commands Used

**Location**: Multiple files use git integration via subprocess

#### A. Session-Start Hook: Developer Identity
```python
# Get developer name and email from git config
name_result = subprocess.run(
    ['git', 'config', 'user.name'],
    capture_output=True,
    text=True,
    timeout=1
)
developer_name = name_result.stdout.strip()
```

#### B. Session-End Hook: Repository Status
```python
# Capture uncommitted files
result = subprocess.run(
    ['git', 'status', '--porcelain'],
    capture_output=True,
    text=True,
    timeout=2
)
uncommitted = [line[3:] for line in result.stdout.strip().split('\n')]

# Get current branch
result = subprocess.run(
    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
    capture_output=True,
    text=True,
    timeout=2
)
current_branch = result.stdout.strip()

# Recent commits (3 most recent)
result = subprocess.run(
    ['git', 'log', '-3', '--pretty=format:%H|%s|%an'],
    capture_output=True,
    text=True,
    timeout=2
)
```

### 3.2 Data Exchange Format (Git Integration)

**Input**: None (queries repository state)

**Output**: Structured metadata captured in session

```python
SessionMetadata {
    current_branch: str          # e.g., "main"
    uncommitted_files: [str]     # e.g., ["agentpm/core/database.py"]
    recent_commits: [{
        sha: str                 # Full commit hash
        message: str             # Commit message
        author: str              # Committer name
    }]
    git_commits: int            # Count of commits in session
}
```

### 3.3 Git Repository Operations

**Location**: `/agentpm/utils/ignore_patterns.py`

```python
def _load_gitignore(self) -> List[str]:
    """Load patterns from .gitignore"""
    gitignore_path = self.project_root / ".gitignore"
    if not gitignore_path.exists():
        return []
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
```

**Purpose**: Respect .gitignore patterns when:
- Scanning source files
- Detecting project structure
- Analyzing code changes

### 3.4 End-to-End Workflow Example: Session Lifecycle

```
Session Start:
├─→ SessionStart Hook (.claude/hooks/session-start.py)
│   ├─→ Create session record
│   ├─→ Get developer from git config
│   │   └─→ subprocess.run(['git', 'config', 'user.name'])
│   └─→ Emit SESSION_STARTED event
│
Developer Works (session active):
├─→ Make commits
├─→ Modify files
└─→ Track tasks in AIPM
│
Session End:
└─→ SessionEnd Hook (.claude/hooks/session-end.py)
    ├─→ Capture ACTIVE state
    ├─→ Capture git status
    │   ├─→ Uncomitted files: git status --porcelain
    │   ├─→ Current branch: git rev-parse --abbrev-ref HEAD
    │   └─→ Recent commits: git log -3 --pretty=format:%H|%s|%an
    ├─→ Store in SessionMetadata
    ├─→ Emit SESSION_ENDED event
    └─→ Generate NEXT-SESSION.md handover
```

### 3.5 Git Error Handling

```python
try:
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True,
        timeout=2
    )
    if result.returncode == 0:
        # Parse successful output
        uncommitted = [...]
except Exception:
    # Graceful degradation: missing git doesn't block session
    pass
```

**Error Patterns**:
- Git not installed: Silently skip (metadata empty)
- Not a git repository: Silently skip
- Git timeout (>2s): Skip this command
- Parse errors: Skip this command

**No blocking**: Git operations are optional metadata capture

---

## 4. SHELL COMMAND EXECUTION (Task 699)

### 4.1 Secure Command Execution Architecture

**Location**: `/agentpm/core/security/command_security.py`

#### Design Principles

1. **NO SHELL=TRUE**: Commands never execute via shell
2. **LIST FORMAT**: Commands passed as `["python", "-m", "pytest"]` not strings
3. **ALLOWLIST**: Dangerous commands (rm, sudo, etc.) are blocked
4. **ENVIRONMENT SANITIZATION**: Only safe vars passed to subprocess
5. **OUTPUT SANITIZATION**: Secrets redacted from logs

### 4.2 Command Execution API

```python
class SecureCommandExecutor:
    
    def execute_build_command(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute build command securely
        
        Returns: {
            "success": bool,
            "return_code": int,
            "stdout": str,
            "stderr": str,
            "execution_time_seconds": float,
            "command_executed": [str],  # Actual command list
            "sanitized": True
        }
        """
```

### 4.3 Command Validation & Sanitization

#### A. Pre-Execution Validation

```python
@classmethod
def validate_command_safety(cls, command_list: List[str]) -> bool:
    """Block dangerous commands"""
    
    dangerous_commands = {
        'rm', 'del', 'format', 'fdisk', 'dd', 'mkfs',
        'sudo', 'su', 'chmod', 'chown', 'passwd',
        'eval', 'exec', 'source', 'bash', 'sh',
        'curl', 'wget', 'nc', 'netcat', 'telnet'
    }
    
    base_command = command_list[0].lower()
    if base_command in dangerous_commands:
        raise SecurityError(f"Dangerous command not allowed: {base_command}")
```

#### B. Dangerous Pattern Detection

```python
dangerous_patterns = [
    r'--password', r'--secret', r'--token',  # Credential arguments
    r'>\s*/dev/', r'>\s*/proc/',             # System file redirects
    r'\|\s*sudo', r'\|\s*su',                # Pipe to privilege escalation
    r'&&\s*rm', r';\s*rm',                   # Chained dangerous commands
]

for pattern in dangerous_patterns:
    if re.search(pattern, full_command, re.IGNORECASE):
        raise SecurityError(f"Dangerous pattern detected: {pattern}")
```

#### C. Output Sanitization

```python
@classmethod
def _sanitize_output(cls, output: str) -> str:
    """Remove secrets from output"""
    
    sensitive_patterns = [
        r'password[=:]\s*\S+',
        r'token[=:]\s*\S+',
        r'key[=:]\s*\S+',
        r'secret[=:]\s*\S+',
        r'api_key[=:]\s*\S+',
        r'--password\s+\S+',
        r'--token\s+\S+',
    ]
    
    for pattern in sensitive_patterns:
        output = re.sub(pattern, '[REDACTED]', output, flags=re.IGNORECASE)
    
    # Limit output to 10KB
    if len(output) > 10000:
        output = output[:10000] + "\n... [OUTPUT TRUNCATED] ..."
    
    return output
```

### 4.4 Environment Isolation

```python
@classmethod
def _create_secure_environment(cls) -> Dict[str, str]:
    """Create isolated subprocess environment"""
    
    # Only include safe variables
    SAFE_ENV_VARS = {
        'PATH', 'HOME', 'USER', 'PWD', 'LANG', 'LC_ALL',
        'PYTHONPATH', 'NODE_ENV', 'JAVA_HOME', 'GOPATH'
    }
    
    secure_env = {}
    for var_name in SAFE_ENV_VARS:
        if var_name in os.environ:
            secure_env[var_name] = os.environ[var_name]
    
    # Set secure defaults
    secure_env['PS1'] = '$ '
    secure_env['IFS'] = ' \t\n'  # Standard field separators
    
    return secure_env
```

### 4.5 Timeout Management

```python
class SecureCommandExecutor:
    DEFAULT_TIMEOUT = 30        # 30 seconds
    BUILD_TIMEOUT = 300         # 5 minutes
    TEST_TIMEOUT = 600          # 10 minutes
    
    def execute_build_command(self, ..., timeout: Optional[int] = None):
        result = subprocess.run(
            command_list,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=timeout or cls.BUILD_TIMEOUT,  # Default 5 min
            env=secure_env,
            check=False  # Don't raise on exit code
        )
```

### 4.6 End-to-End Workflow: Build Command Execution

```
User Input: apm task submit-review 123
         │
         ├─→ [Workflow] transition_task() → REVIEW
         │
         ├─→ [SecureCommandExecutor] execute_build_command()
         │   │
         │   ├─→ Parse command: "python -m pytest -q --maxfail=1"
         │   │
         │   ├─→ Validate command safety
         │   │   ├─→ Check base command (python) ✓ Safe
         │   │   └─→ Check patterns (no injection) ✓ Safe
         │   │
         │   ├─→ Create secure environment
         │   │   ├─→ Include: PATH, PYTHONPATH
         │   │   ├─→ Exclude: AWS_KEY, API_TOKEN
         │   │   └─→ Set secure defaults: PS1='$ ', IFS=' \t\n'
         │   │
         │   ├─→ Execute subprocess.run()
         │   │   ├─→ Command: ["python", "-m", "pytest", "-q", "--maxfail=1"]
         │   │   ├─→ Timeout: 60 seconds
         │   │   ├─→ cwd: /path/to/project
         │   │   └─→ shell=False (NO shell injection possible)
         │   │
         │   ├─→ Capture output
         │   │   ├─→ stdout: Test results
         │   │   ├─→ stderr: Pytest warnings
         │   │   └─→ returncode: 0 = pass, non-zero = fail
         │   │
         │   └─→ Sanitize output
         │       ├─→ Redact: password=***, token=***, etc.
         │       └─→ Truncate: >10KB outputs
         │
         └─→ Return {success, return_code, stdout, stderr, time}
```

### 4.7 Security Features Summary

| Feature | Implementation | Purpose |
|---------|-----------------|---------|
| **No Shell** | `shell=False` always | Prevent shell injection |
| **List Format** | `["python", "-m", "pytest"]` | Atomic argument parsing |
| **Allowlist** | Block rm, sudo, eval, etc. | Prevent destructive ops |
| **Timeout** | 30-600 seconds | Prevent hung processes |
| **Environment** | Whitelist vars only | Prevent secret leakage |
| **Output Sanitization** | Regex redaction | Prevent credential exposure |
| **Output Truncation** | 10KB limit | Prevent memory exhaustion |

---

## Summary Table: Integration Points

| Integration | Entry Point | External Tool | Data Exchange | Timeout | Error Handling |
|------------|------------|---------------|---------------|---------|----|
| **CLI Tools** | `/cli/commands/task/submit_review.py` | pytest, coverage | Subprocess.run() | 60-300s | Graceful fail |
| **Completion** | `/cli/main.py` (LazyGroup) | Click + Shell | Command list | <100ms | Auto-complete |
| **Git** | `/core/hooks/implementations/` | git config/status/log | Metadata struct | 1-2s | Silent skip |
| **Shell Cmd** | `/core/security/command_security.py` | Any (validated) | Sanitized output | 30-600s | Sec blocked |

---

## Recommendations

1. **Document completion setup** in installation guide
2. **Add git_integration.py module** for DRY git operations
3. **Expand allowed commands** for plugin architecture
4. **Add command audit logging** for security compliance
