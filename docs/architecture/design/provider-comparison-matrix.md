# Provider Comparison Matrix

**Detailed comparison of Claude Code, Cursor, and OpenAI Codex provider implementations**

## Quick Comparison Table

| Feature | Claude Code | Cursor | OpenAI Codex |
|---------|-------------|--------|--------------|
| **Output Format** | Directory | Single File | Multi-File |
| **Config Location** | `.claude/` | `.cursorrules` | `.openai/` |
| **Agent Files** | Multiple `.md` | N/A | Multiple `.json` |
| **Template Engine** | Jinja2 | Jinja2 | JSON Schema |
| **Slash Commands** | ✅ Yes | ❌ No | ✅ Yes (custom) |
| **Hooks** | ✅ Python | ❌ No | ⚠️ Webhooks only |
| **Memory** | ✅ File-based | ❌ No | ✅ Conversation history |
| **Subagents** | ✅ Task tool | ❌ No | ⚠️ Assistants API |
| **Custom Tools** | ✅ Python | ❌ No | ✅ Function calling |
| **Context Files** | ✅ CLAUDE.md | ⚠️ Inline | ✅ System prompts |
| **Rule Enforcement** | BLOCK/LIMIT/GUIDE | Inline suggestions | Function validation |
| **Complexity** | High | Low | Medium |
| **Best For** | Complex workflows | Simple instructions | API integration |

**Legend:**
- ✅ Full support
- ⚠️ Partial support
- ❌ Not supported

---

## Detailed Feature Breakdown

### 1. Output Structure

#### Claude Code

```
project/
├── .claude/
│   ├── CLAUDE.md              # Project instructions
│   ├── agents/                 # Agent definitions
│   │   ├── orchestrators/
│   │   │   ├── definition-orch.md
│   │   │   ├── planning-orch.md
│   │   │   └── implementation-orch.md
│   │   ├── specialists/
│   │   │   ├── aipm-python-cli-developer.md
│   │   │   ├── aipm-database-developer.md
│   │   │   └── aipm-testing-specialist.md
│   │   └── utilities/
│   │       ├── context-delivery.md
│   │       └── workitem-writer.md
│   ├── commands/               # Slash commands
│   │   ├── sc:implement.md
│   │   ├── sc:test.md
│   │   └── sc:document.md
│   ├── hooks/                  # Python hooks
│   │   ├── pre-tool-use.py
│   │   └── post-tool-use.py
│   └── memory/                 # Persistent memory
│       ├── test/
│       └── other/
```

**Characteristics:**
- Directory-based
- Hierarchical organization
- Supports complex multi-agent systems
- Python-based hooks
- File-based memory

#### Cursor

```
project/
└── .cursorrules               # Single file with all rules
```

**File content:**
```markdown
# Project Rules

## Code Style
- Use TypeScript strict mode
- Single quotes, no semicolons

## Architecture
- Follow hexagonal architecture
- Use dependency injection

## Testing
- 90% code coverage required
- AAA pattern for tests

## Security
- No hardcoded credentials
- Validate all inputs
```

**Characteristics:**
- Single monolithic file
- Simple markdown format
- No agent support
- Inline rules only
- Best for straightforward projects

#### OpenAI Codex

```
project/
├── .openai/
│   ├── config.json            # Main configuration
│   ├── assistants/            # Assistant definitions
│   │   ├── python-dev.json
│   │   ├── tester.json
│   │   └── reviewer.json
│   ├── functions/             # Tool definitions
│   │   ├── run-tests.json
│   │   └── analyze-code.json
│   └── prompts/               # System prompts
│       ├── system.txt
│       └── instructions.txt
```

**Characteristics:**
- JSON-based configuration
- Assistants API integration
- Function calling support
- Conversation history
- API-first design

---

## 2. Agent/Assistant Definition

### Claude Code

**File:** `.claude/agents/specialists/aipm-python-cli-developer.md`

```markdown
# Python CLI Developer

**Role:** aipm-python-cli-developer
**Tier:** specialist
**Type:** Domain Expert

## Description
Implements Python CLI commands following three-layer architecture:
- Models (Pydantic)
- Adapters (SQLite)
- Methods (Business logic)

## Capabilities
- Python 3.10+ development
- CLI command implementation
- Database operations
- Test-driven development
- Pydantic model design

## Project Rules

### Development Principles (BLOCK)
- **DP-001**: Time-box implementation tasks to ≤4 hours
- **DP-002**: Follow hexagonal architecture pattern
- **DP-003**: Use three-layer pattern (Model → Adapter → Method)

### Testing Standards (BLOCK)
- **TES-001**: Maintain ≥90% test coverage
- **TES-002**: Use AAA pattern for all tests
- **TES-003**: Create fixtures in conftest.py

## Standard Operating Procedure

1. **Read Task Requirements**
   - Extract acceptance criteria
   - Identify dependencies
   - Estimate effort

2. **Create Pydantic Models**
   - Define domain models
   - Add validation rules
   - Document fields

3. **Implement Database Adapters**
   - Convert Pydantic → SQLite
   - Handle type conversions
   - Manage relationships

4. **Write Business Logic Methods**
   - Implement CRUD operations
   - Add business rules
   - Handle edge cases

5. **Create Tests**
   - Unit tests (≥90% coverage)
   - Integration tests
   - AAA pattern

6. **Document**
   - Add docstrings
   - Update README if needed
   - Create examples

## Behavioral Rules
- NEVER skip tests
- ALWAYS validate inputs
- ALWAYS use type hints
- NEVER hardcode values
```

**Advantages:**
- Rich, structured format
- Explicit rules enforcement
- Detailed SOPs
- Tier-based organization

### Cursor

**Not applicable** - Cursor doesn't support individual agents. All rules are global in `.cursorrules`.

### OpenAI Codex

**File:** `.openai/assistants/python-dev.json`

```json
{
  "id": "asst_python_dev_001",
  "name": "Python CLI Developer",
  "description": "Implements Python CLI commands using three-layer architecture",
  "model": "gpt-4-turbo",
  "instructions": "You are a Python CLI developer expert. Follow three-layer architecture: Models (Pydantic), Adapters (SQLite), Methods (Business logic). Maintain ≥90% test coverage. Use AAA pattern for tests. Time-box tasks to ≤4 hours.",
  "tools": [
    {
      "type": "code_interpreter"
    },
    {
      "type": "function",
      "function": {
        "name": "run_tests",
        "description": "Run pytest test suite",
        "parameters": {
          "type": "object",
          "properties": {
            "test_path": {
              "type": "string",
              "description": "Path to test file or directory"
            },
            "coverage": {
              "type": "boolean",
              "description": "Generate coverage report"
            }
          }
        }
      }
    }
  ],
  "file_ids": [],
  "metadata": {
    "tier": "specialist",
    "capabilities": ["python", "cli", "database", "testing"],
    "project_id": "1"
  }
}
```

**Advantages:**
- Native Assistants API integration
- Function calling support
- Conversation threads
- File attachments

---

## 3. Rule Enforcement

### Claude Code

**Enforcement Levels:**
- **BLOCK**: Hard constraint - operation fails if violated
- **LIMIT**: Soft constraint - warning but operation succeeds
- **GUIDE**: Suggestion - informational only
- **ENHANCE**: Context enrichment - no enforcement

**Example:**

```markdown
## Development Principles

### DP-001: Time-Boxing Implementation (BLOCK)
All IMPLEMENTATION tasks must be ≤4 hours estimated effort.

**Validation:**
- Task effort_hours ≤ 4.0
- If violated: Task creation fails with error

### TES-001: Test Coverage (LIMIT)
Projects should maintain ≥90% test coverage.

**Validation:**
- Coverage < 90%: Warning displayed, commit allowed
- Coverage ≥ 90%: Success

### SEC-001: Input Validation (GUIDE)
Consider validating all external inputs.

**Validation:**
- Informational reminder only
- No enforcement
```

**Implementation:**

```python
# agentpm/core/rules/enforcer.py
def enforce_rule(rule: Rule, context: Dict) -> EnforcementResult:
    if rule.enforcement_level == EnforcementLevel.BLOCK:
        if not validate(rule, context):
            raise RuleViolationError(rule.error_message)

    elif rule.enforcement_level == EnforcementLevel.LIMIT:
        if not validate(rule, context):
            logger.warning(rule.error_message)

    elif rule.enforcement_level == EnforcementLevel.GUIDE:
        logger.info(rule.description)
```

### Cursor

**Enforcement:**
- Inline suggestions only
- No hard enforcement
- AI interprets rules as context

**Example:**

```markdown
# .cursorrules

All implementation tasks should be ≤4 hours.
Maintain ≥90% test coverage.
Always validate external inputs.
```

**Behavior:**
- Cursor AI reads rules as suggestions
- No validation or blocking
- Relies on AI's interpretation

### OpenAI Codex

**Enforcement via Function Calling:**

```json
{
  "function": {
    "name": "validate_task_effort",
    "description": "Validate task effort is within limits",
    "parameters": {
      "type": "object",
      "properties": {
        "effort_hours": {
          "type": "number",
          "maximum": 4.0,
          "description": "Task effort in hours (max 4)"
        }
      },
      "required": ["effort_hours"]
    }
  }
}
```

**Behavior:**
- Function parameters enforce constraints
- JSON schema validation
- API-level enforcement

---

## 4. Context Management

### Claude Code

**Context Files:**
- `.claude/CLAUDE.md` - Project instructions
- `.claude/agents/*.md` - Agent-specific context
- `.claude/memory/**/*.json` - Persistent memory

**Context Loading:**

```markdown
# CLAUDE.md

## Project Context
This is APM (Agent Project Manager), a database-driven project management system.

## Architecture
- Three-layer pattern (Model → Adapter → Method)
- Hexagonal architecture
- Database-first design

## Active Rules
- DP-001: Time-box tasks to ≤4 hours (BLOCK)
- TES-001: Maintain ≥90% coverage (LIMIT)
- SEC-001: Validate inputs (GUIDE)

## Agent Workflow
1. context-delivery agent gathers session state
2. Phase orchestrator coordinates work
3. Specialist agents execute tasks
4. Quality validator checks results
```

**Memory System:**

```bash
# Read memory
apm memory read test key1

# Write memory
apm memory write test key1 "Important context"

# List all memory
apm memory list
```

**Advantages:**
- Persistent across sessions
- Hierarchical organization
- Agent-specific context
- Project-level instructions

### Cursor

**Context:**
- Single `.cursorrules` file
- No persistent memory
- AI interprets rules each session

**Example:**

```markdown
# .cursorrules

## Project Info
This is APM (Agent Project Manager), built with Python + SQLite.

## Rules
- Time-box tasks to ≤4 hours
- Maintain ≥90% test coverage
- Follow three-layer architecture

## Tech Stack
- Python 3.10+
- SQLite
- Pydantic
- pytest
```

**Limitations:**
- No session persistence
- No agent-specific context
- Must be re-read each session

### OpenAI Codex

**Context via System Prompts:**

```json
{
  "assistant": {
    "instructions": "You are working on APM (Agent Project Manager), a Python CLI tool for project management. Follow three-layer architecture. Time-box tasks to ≤4 hours. Maintain ≥90% test coverage.",
    "file_ids": ["file-abc123"],  // Project documentation
    "metadata": {
      "project_id": "1",
      "tech_stack": ["python", "sqlite", "pydantic"],
      "active_rules": ["DP-001", "TES-001", "SEC-001"]
    }
  }
}
```

**Conversation History:**
- OpenAI stores conversation threads
- Context maintained across API calls
- File attachments supported

**Advantages:**
- Built-in conversation memory
- File attachment support
- API-managed persistence

---

## 5. Custom Tools/Functions

### Claude Code

**Python Hooks:**

```python
# .claude/hooks/pre-tool-use.py
def pre_tool_use(tool_name: str, params: dict) -> dict:
    """Hook called before tool execution"""

    if tool_name == "Edit":
        # Check if file is in docs/
        if params['file_path'].startswith('docs/'):
            raise ValueError(
                "Use 'apm document add' for docs/ files (DOC-020)"
            )

    return params


def post_tool_use(tool_name: str, result: Any) -> Any:
    """Hook called after tool execution"""

    if tool_name == "Bash" and "git commit" in result:
        # Log commit to database
        log_git_commit(result)

    return result
```

**Custom Commands:**

```bash
# .claude/commands/sc:implement.md
Feature implementation with intelligent persona activation.

Usage: /sc:implement [feature-name]

This command:
1. Activates implementation-orch agent
2. Creates tasks from requirements
3. Executes implementation workflow
4. Runs tests and validation
```

**Advantages:**
- Full Python scripting
- Before/after hooks
- Custom slash commands
- Direct tool integration

### Cursor

**Not Supported**
- No custom tools
- No hooks
- No extensions

### OpenAI Codex

**Function Calling:**

```json
{
  "function": {
    "name": "run_tests",
    "description": "Execute pytest test suite with coverage",
    "parameters": {
      "type": "object",
      "properties": {
        "test_path": {
          "type": "string",
          "description": "Path to test file/directory"
        },
        "coverage": {
          "type": "boolean",
          "description": "Generate coverage report",
          "default": true
        },
        "verbose": {
          "type": "boolean",
          "default": false
        }
      },
      "required": ["test_path"]
    }
  }
}
```

**Implementation:**

```python
# Server-side function handler
def run_tests(test_path: str, coverage: bool = True, verbose: bool = False):
    """Execute pytest"""
    cmd = ["pytest", test_path]
    if coverage:
        cmd.extend(["--cov", "--cov-report=term"])
    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd, capture_output=True)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout.decode(),
        "stderr": result.stderr.decode()
    }
```

**Advantages:**
- API-based tool registration
- JSON schema validation
- Async function execution
- Built-in error handling

---

## 6. Generation Complexity

### Claude Code

**Lines of Code:** ~500
**Template Complexity:** High
**Features:** 8+

**Implementation Effort:**

```python
class ClaudeCodeGenerator(BaseProviderGenerator, TemplateBasedMixin):
    # Required methods (4)
    def generate_from_agents(self, context) -> GenerationResult
    def validate_config(self, context) -> tuple[bool, List[str]]
    def format_context(self, context) -> Dict[str, Any]
    def get_output_paths(self, context) -> List[Path]

    # Optional overrides (3)
    def _validate_agent_for_provider(self, agent) -> List[str]
    def _extract_behavioral_rules(self, agents) -> List[str]
    def _infer_agent_type(self, role) -> str

    # Template rendering (inherited from mixin)
    def prepare_template_context(self, context) -> Dict[str, Any]
    def render_template(self, template_name, context) -> str
```

**Template Files:**
- `agent_file.md.j2` (~150 lines)
- `claude_md.j2` (~200 lines)
- `slash_command.md.j2` (~50 lines)
- `hook_template.py.j2` (~100 lines)

**Total:** ~1000 lines of code + templates

### Cursor

**Lines of Code:** ~150
**Template Complexity:** Low
**Features:** 1

**Implementation Effort:**

```python
class CursorGenerator(BaseProviderGenerator):
    # Required methods (4)
    def generate_from_agents(self, context) -> GenerationResult
    def validate_config(self, context) -> tuple[bool, List[str]]
    def format_context(self, context) -> Dict[str, Any]
    def get_output_paths(self, context) -> List[Path]

    # Simple content generation (no templates)
    def _build_cursorrules_content(self, context) -> str
```

**Template Files:**
- `cursorrules.md.j2` (~50 lines)

**Total:** ~200 lines of code + template

### OpenAI Codex

**Lines of Code:** ~350
**Template Complexity:** Medium
**Features:** 5

**Implementation Effort:**

```python
class OpenAICodexGenerator(BaseProviderGenerator):
    # Required methods (4)
    def generate_from_agents(self, context) -> GenerationResult
    def validate_config(self, context) -> tuple[bool, List[str]]
    def format_context(self, context) -> Dict[str, Any]
    def get_output_paths(self, context) -> List[Path]

    # JSON generation methods (3)
    def _build_assistant_config(self, agent) -> dict
    def _build_function_definition(self, capability) -> dict
    def _build_main_config(self, context) -> dict

    # Validation (1)
    def _validate_json_schema(self, config) -> bool
```

**Template Files:**
- N/A (programmatic JSON generation)

**Total:** ~350 lines of code

---

## 7. Use Case Recommendations

### Use Claude Code When:

✅ **Complex multi-agent workflows**
- Need orchestrators, specialists, and utilities
- Coordinated task execution
- Phase-based development process

✅ **Strict rule enforcement**
- BLOCK-level constraints required
- Quality gates must be enforced
- Validation critical

✅ **Persistent memory needed**
- Session state across interactions
- Historical context important
- Multi-session workflows

✅ **Custom tooling required**
- Python hooks for automation
- Custom slash commands
- Direct tool integration

**Example Projects:**
- Enterprise software development
- Regulated industries (healthcare, finance)
- Large codebases with complex workflows
- Multi-team collaboration

### Use Cursor When:

✅ **Simple, straightforward projects**
- Single developer
- Clear requirements
- Minimal workflow complexity

✅ **Quick prototyping**
- MVP development
- Proof of concepts
- Personal projects

✅ **Minimal configuration overhead**
- Don't want to manage multiple files
- Prefer simple markdown rules
- No need for complex enforcement

**Example Projects:**
- Personal side projects
- Small web applications
- Simple CLI tools
- Learning/tutorial projects

### Use OpenAI Codex When:

✅ **API-first architecture**
- Building AI-powered products
- Need programmatic access
- Embedding in other systems

✅ **Assistants API features**
- Conversation threads
- File attachments
- Function calling

✅ **Cloud-based deployment**
- Hosted AI services
- Multi-user systems
- Scalable infrastructure

✅ **Cross-platform support**
- Web, mobile, desktop
- API consumption from any language
- Cloud-native architecture

**Example Projects:**
- SaaS products
- AI-powered platforms
- Customer support systems
- Code analysis services

---

## 8. Migration Paths

### From Cursor to Claude Code

**When to migrate:**
- Project complexity increases
- Need agent-based workflows
- Want stricter rule enforcement

**Migration steps:**

```bash
# 1. Parse .cursorrules
apm import cursorrules .cursorrules

# 2. Generate Claude Code config
apm generate config --provider claude-code

# 3. Review generated agents
ls .claude/agents/

# 4. Test
claude-code chat
```

**Effort:** 1-2 hours

### From OpenAI to Claude Code

**When to migrate:**
- Want local-first development
- Need Python-based hooks
- Prefer file-based configuration

**Migration steps:**

```bash
# 1. Export OpenAI config
apm import openai .openai/config.json

# 2. Map assistants to agents
apm agents map-from-openai

# 3. Generate Claude Code config
apm generate config --provider claude-code

# 4. Migrate functions to hooks
apm hooks generate-from-functions .openai/functions/
```

**Effort:** 2-4 hours

### From Claude Code to OpenAI

**When to migrate:**
- Need API access
- Want cloud-hosted solution
- Building SaaS product

**Migration steps:**

```bash
# 1. Export Claude Code agents
apm export agents --format=json

# 2. Generate OpenAI config
apm generate config --provider openai

# 3. Upload to OpenAI
apm openai upload .openai/

# 4. Test assistants
apm openai test asst_python_dev_001
```

**Effort:** 3-5 hours

---

## Summary

| Aspect | Claude Code | Cursor | OpenAI Codex |
|--------|-------------|--------|--------------|
| **Complexity** | High | Low | Medium |
| **Setup Time** | 2-4 hours | 15 minutes | 1-2 hours |
| **Maintenance** | Medium | Low | Medium |
| **Flexibility** | Very High | Low | High |
| **Learning Curve** | Steep | Gentle | Moderate |
| **Best For** | Enterprise | Personal | SaaS |
| **Cost** | Local (free) | $20/mo | API usage |
| **Deployment** | Local | Local | Cloud |

**Recommendation:**
- **Start with Cursor** for simple projects
- **Upgrade to Claude Code** when complexity grows
- **Choose OpenAI Codex** for API-first products

All three providers can be generated from the same universal database, allowing easy migration between approaches as project needs evolve.
