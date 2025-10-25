# Agent Base Templates

**Purpose**: Domain-agnostic agent templates for Claude Code specialization

**Location**: Packaged with APM (Agent Project Manager) (`agentpm/templates/agents/`)

**Usage**: During `apm agents generate`, these templates are:
1. Loaded from the package
2. Filled with project-specific context by Claude Code headless
3. Written to user's `.claude/agents/` directory

---

## Template Inventory

### 15 Universal Agent Roles

| Template | Role | Primary Function |
|----------|------|------------------|
| **implementer.md** | Implementation Agent | Transform specifications into working code |
| **tester.md** | Testing Agent | Write tests and validate coverage |
| **specifier.md** | Specification Agent | Define requirements and acceptance criteria |
| **reviewer.md** | Code Review Agent | Review code quality and patterns |
| **documenter.md** | Documentation Agent | Write technical documentation |
| **debugger.md** | Debugging Agent | Investigate and fix bugs |
| **analyzer.md** | Analysis Agent | Analyze code and generate metrics |
| **optimizer.md** | Optimization Agent | Improve performance |
| **integrator.md** | Integration Agent | Connect systems and APIs |
| **validator.md** | Validation Agent | Enforce quality gates |
| **planner.md** | Planning Agent | Break down work and estimate |
| **automator.md** | Automation Agent | Create CI/CD and workflows |
| **deployer.md** | Deployment Agent | Deploy and operate systems |
| **refactorer.md** | Refactoring Agent | Restructure and improve code |
| **researcher.md** | Research Agent | Evaluate technologies |

---

## Template Structure

### 12-Section Standard Operating Procedure

All templates follow this proven structure:

1. **Role & Authority** - What this agent does and decides
2. **Rule Compliance** - Project rules and constraints
3. **Core Expertise** - Principles and capabilities
4. **Required Context** - How to load project context
5. **Standard Operating Procedures** - Step-by-step process
6. **Communication Protocols** - Input/output specifications
7. **Quality Gates** - Success criteria
8. **Domain-Specific Patterns** - Project-specific examples
9. **Push-Back Mechanisms** - When to challenge requests
10. **Success Metrics** - How to measure success
11. **Escalation Paths** - When and how to escalate
12. **Context-Specific Examples** - Project code examples

### [INSTRUCTION] Placeholders

Templates contain `[INSTRUCTION: ...]` markers where Claude Code headless will inject:
- Detected technology stack (languages, frameworks, versions)
- Project-specific patterns (from code analysis)
- Actual code examples (from existing files)
- Quality requirements (from rules table)
- Time-boxing limits (from project rules)

**Example**:
```
[INSTRUCTION: List detected languages, frameworks, libraries with versions]
```

Claude fills with:
```
- Python 3.11
- Pydantic 2.5+
- Click 8.1+
- Rich 13.7+
- pytest (testing)
```

---

## Design Principles

### 1. Domain-Agnostic

Templates describe **universal agent functions**, not technology-specific roles:
- ✅ "Implementation Agent" (universal)
- ❌ "Python Django Implementer" (too specific)

### 2. Role-Focused

Templates emphasize **what the agent does**, not what technology it uses:
- ✅ "Transform specifications into working solutions"
- ❌ "Write Python code with Django ORM"

### 3. Context-Driven

Templates have placeholders for Claude to fill with **project-specific** content:
- Tech stack detection (via PluginOrchestrator)
- Pattern extraction (via code analysis)
- Rules query (from rules table)
- Example code (from actual project files)

### 4. Composable

One base template → Many specialized agents:
- `implementer.md` → `python-django-implementer.md`
- `implementer.md` → `typescript-react-implementer.md`
- `implementer.md` → `rust-backend-implementer.md`

**Result**: 15 bases × N frameworks = Hundreds of specialized agents

---

## Usage in APM (Agent Project Manager)

### Generation Flow

```
1. User runs: apm agents generate
2. PluginOrchestrator detects: Python, Django, pytest, SQLite
3. For each base template (15 total):
   a. Load template from agentpm/templates/agents/
   b. Compose project context (tech stack, patterns, rules)
   c. Invoke Claude Code headless with template + context
   d. Claude fills [INSTRUCTION] placeholders
   e. Write specialized agent to .claude/agents/
4. Result: 15 specialized agents (10-20KB each with project context)
```

### Example Specialization

**Base Template** (`implementer.md`):
```markdown
**Tech Stack**:
[INSTRUCTION: List detected languages, frameworks, libraries with versions]
```

**Specialized Agent** (`python-django-implementer.md` after Claude fills):
```markdown
**Tech Stack**:
- Python 3.11 (detected from pyproject.toml)
- Django 4.2 (detected from requirements.txt)
- Pydantic 2.5+ (validation framework)
- SQLite 3.35+ (database)
- pytest 7.4+ (testing)
```

---

## File Format

### YAML Frontmatter

```yaml
---
name: <role>
description: <Agent Role> - <Primary Function>
tools: Read, Grep, Glob, Write, Edit, Bash
---
```

### Markdown Body

- 12 sections (## headings)
- [INSTRUCTION] placeholders for Claude
- Code blocks for examples
- Checklists for quality gates
- Cross-references to other agents

### Size

- **Base templates**: 3-5KB each (with placeholders)
- **Filled templates**: 10-20KB each (with project context)

---

## Testing

Templates are validated during agent generation tests (WI-009.9):
- All 15 templates loadable
- YAML frontmatter parses correctly
- 12-section structure present
- [INSTRUCTION] placeholders identifiable
- Claude Code can fill placeholders

---

## Maintenance

### Adding New Template

1. Create `<role>.md` in this directory
2. Follow 12-section structure
3. Use [INSTRUCTION] placeholders
4. Keep domain-agnostic (no hardcoded tech)
5. Update this README with new template

### Updating Templates

1. Preserve 12-section structure
2. Keep [INSTRUCTION] placeholders
3. Test with `apm agents generate --force`
4. Validate filled agents are correct

---

**Template Set Version**: 2.0 (Domain-Agnostic)
**Created**: WI-009.4
**Revised**: 2025-10-02 (removed all framework-specific language)
**Maintained**: APM (Agent Project Manager) Core Team
