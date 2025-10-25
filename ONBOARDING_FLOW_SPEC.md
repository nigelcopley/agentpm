# APM Frictionless Onboarding Flow Specification

**Version**: 1.0
**Date**: October 25, 2025
**Status**: Requirements Analysis & UX Design Complete
**Target**: Single-command onboarding in <3 minutes

---

## Executive Summary

This specification transforms APM's installation experience from a **3-command, 8-10 minute fragmented workflow** to a **single-command, <3 minute seamless experience** that matches industry best practices (Vercel, Netlify, Poetry, Create React App).

**Current State**:
```bash
pip install agentpm         # ✅ Works
apm init "Project"          # ⚠️ Incomplete (DB only)
apm agents generate --all   # ❌ Required but presented as optional
apm work-item create "Task" # Finally ready
```

**Target State**:
```bash
pip install agentpm
apm init "Project"          # ✅ Complete and ready
# Ready to use immediately
```

---

## 1. User Journey Map

### 1.1 Complete User Journey (Start to First Work Item)

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 0: INSTALLATION (30-60 seconds)                       │
├─────────────────────────────────────────────────────────────┤
│ User Action: pip install agentpm                            │
│                                                              │
│ System Actions:                                              │
│ • Download package from PyPI                                 │
│ • Install dependencies (click, rich, pydantic, etc.)        │
│ • Register 'apm' entry point                                 │
│                                                              │
│ Success Indicator:                                           │
│ • apm --version shows version                                │
│ • apm --help shows commands                                  │
│                                                              │
│ Error Scenarios:                                             │
│ • Python < 3.9 → Clear error: "APM requires Python 3.9+"    │
│ • Network failure → Retry suggestion                         │
│ • Permission denied → Suggest: pip install --user           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: INITIALIZATION (2-3 minutes)                       │
├─────────────────────────────────────────────────────────────┤
│ User Action: apm init "My Project"                          │
│                                                              │
│ Stage 1: Pre-flight Checks (200ms)                          │
│ ├─ Detect existing .agentpm (prevent re-init)              │
│ ├─ Validate project name (no special chars)                │
│ ├─ Check write permissions                                  │
│ ├─ Detect project type (Django/Flask/etc.)                 │
│ └─ Check git repository                                     │
│                                                              │
│ Stage 2: Database Setup (2-3 seconds)                       │
│ ├─ Create .agentpm/ directory structure                     │
│ ├─ Initialize DatabaseService                               │
│ ├─ Run all 43 migrations                                    │
│ ├─ Insert project record                                    │
│ └─ [CHECKPOINT] Database ready (57 tables)                  │
│                                                              │
│ Stage 3: Framework Detection (1-2 seconds)                  │
│ ├─ Scan project files                                       │
│ ├─ Run DetectionOrchestrator (11 plugins)                  │
│ ├─ Generate code amalgamations                              │
│ ├─ Store detection results                                  │
│ └─ [CHECKPOINT] Detection complete                          │
│                                                              │
│ Stage 4: Smart Configuration (30-60 seconds)                │
│ ├─ Present minimal questionnaire (5-7 questions)           │
│ ├─ Use smart defaults from detection                       │
│ ├─ Generate rules based on answers                         │
│ ├─ Load rules into database (75 rules)                     │
│ └─ [CHECKPOINT] Rules configured                            │
│                                                              │
│ Stage 5: Agent Generation (30-60 seconds) **NEW**          │
│ ├─ Generate 85 agent SOPs from rules                       │
│ ├─ Write agent files to .claude/agents/                    │
│ ├─ Register agents in database                              │
│ └─ [CHECKPOINT] Agents ready                                │
│                                                              │
│ Stage 6: Context Assembly (500ms)                           │
│ ├─ Assemble hierarchical context                            │
│ ├─ Extract framework facts                                  │
│ ├─ Calculate confidence scores                              │
│ └─ [CHECKPOINT] Context ready                               │
│                                                              │
│ Stage 7: Verification (500ms)                               │
│ ├─ Verify all components initialized                        │
│ ├─ Show success summary                                     │
│ ├─ Display detected technologies                            │
│ └─ [CHECKPOINT] Initialization complete                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: FIRST USE (10-30 seconds)                         │
├─────────────────────────────────────────────────────────────┤
│ User Action: apm work-item create "Add user auth"          │
│                                                              │
│ System Actions:                                              │
│ • Validate against rules (agents loaded ✓)                  │
│ • Create work item with requirements                        │
│ • Show next steps                                            │
│                                                              │
│ Success Indicator:                                           │
│ • Work item created with ID #1                               │
│ • No agent-related errors                                    │
│ • Clear guidance on next actions                             │
└─────────────────────────────────────────────────────────────┘

TOTAL TIME: <3 minutes from pip install to first work item
```

---

## 2. Question Decision Tree

### 2.1 Current 18 Questions → Categorization

| # | Question | Category | Decision | Rationale |
|---|----------|----------|----------|-----------|
| 1 | Project name | ✅ REQUIRED | Command arg | Must have (from CLI) |
| 2 | Description | 🤖 AUTO-DEFAULT | "Project managed by APM" | Optional, low value |
| 3 | Project type | 🤖 AUTO-DETECT | From codebase | Django→web_app, Click→cli |
| 4 | Primary language | 🤖 AUTO-DETECT | From files | .py files → Python |
| 5 | Dev stage | ❓ ASK | User knows best | prototype/mvp/production |
| 6 | Backend framework | 🤖 AUTO-DETECT | From imports | Django/Flask/FastAPI |
| 7 | Frontend framework | 🤖 AUTO-DETECT | From package.json | React/Vue/Alpine |
| 8 | Database | 🤖 AUTO-DETECT | From dependencies | postgresql/sqlite |
| 9 | Team size | ❓ ASK | User context | solo/small/medium/large |
| 10 | Architecture style | 🤖 AUTO-INFER | From structure | Monolith default |
| 11 | Development approach | 🤖 AUTO-DEFAULT | "agile" | Low impact |
| 12 | Code review required | 🤖 AUTO-DEFAULT | True | Best practice |
| 13 | Compliance requirements | ❓ ASK (optional) | User-specific | HIPAA/SOC2/etc. |
| 14 | Test coverage target | 🤖 AUTO-DEFAULT | 90% | Standard |
| 15 | Max task duration | 🤖 AUTO-DEFAULT | 4h | APM standard |
| 16 | Deployment strategy | 🤖 AUTO-DETECT | From CI files | GitHub Actions→ci_cd |
| 17 | DevOps practices | 🤖 AUTO-DETECT | From files | Docker→containerization |
| 18 | Rules preset | 🤖 AUTO-SELECT | From detection | strict/standard/flexible |

### 2.2 Minimal Question Set (5-7 Questions)

**Priority 1: ALWAYS ASK** (2-3 questions)
```
Q1: Development Stage?
   • Prototype (fast iteration, flexible rules)
   • MVP (balanced, standard rules)
   • Production (strict rules, full gates)
   • Enterprise (maximum governance)

   Why: Determines rule strictness
   Default: Auto-detect from git history (commits < 50 → prototype)

Q2: Team Size?
   • Solo developer
   • Small team (2-5)
   • Medium team (6-15)
   • Large team (16+)

   Why: Affects collaboration features, review requirements
   Default: solo
```

**Priority 2: ASK IF AMBIGUOUS** (1-2 questions)
```
Q3: Compliance Requirements? (only if not obvious)
   • None
   • HIPAA
   • SOC2
   • PCI-DSS
   • GDPR
   • Multiple

   Why: Enables security gates
   When: Only if handling sensitive data detected
   Default: None
   Skip if: Project type is "library" or "cli"

Q4: Test Coverage Target? (only if non-standard)
   • 70% (lenient)
   • 80% (standard)
   • 90% (strict) ← DEFAULT
   • 95%+ (critical systems)

   Why: Sets quality bar
   When: Only if dev_stage = enterprise
   Default: 90% (skip question)
```

**Priority 3: ASK IF DETECTED MULTIPLE** (0-2 questions)
```
Q5: Primary Backend Framework? (only if >1 detected)
   Detected: Django 5.0, Flask 3.0
   Which is primary? [Django]

   Why: Focus context extraction
   When: Multiple frameworks detected with similar confidence
   Default: Highest confidence

Q6: Deployment Target? (only if ambiguous)
   • Cloud (AWS/GCP/Azure)
   • On-premise
   • Hybrid
   • Edge/CDN

   Why: Enables deployment checks
   When: No CI/CD files detected
   Default: Cloud
   Skip if: Obvious from files (Docker Compose → on-premise)
```

### 2.3 Question Flow Logic

```python
def determine_questions(detection_result: DetectionResult) -> List[Question]:
    """Dynamically determine which questions to ask."""

    questions = []

    # ALWAYS: Development stage
    questions.append(Question.DEV_STAGE)

    # ALWAYS: Team size
    questions.append(Question.TEAM_SIZE)

    # CONDITIONAL: Compliance (only if sensitive data detected)
    if detection_result.has_database or detection_result.has_auth:
        questions.append(Question.COMPLIANCE)

    # CONDITIONAL: Framework choice (only if multiple detected)
    if len(detection_result.backend_frameworks) > 1:
        questions.append(Question.PRIMARY_BACKEND)

    # CONDITIONAL: Test coverage (only if enterprise stage)
    if answers.get('dev_stage') == 'enterprise':
        questions.append(Question.TEST_COVERAGE)

    # CONDITIONAL: Deployment (only if not obvious)
    if not detection_result.has_ci_cd and not detection_result.has_docker:
        questions.append(Question.DEPLOYMENT)

    return questions

    # Result: 2-7 questions dynamically
```

---

## 3. Smart Defaults Catalog

### 3.1 Auto-Detection Matrix

| Attribute | Detection Method | Confidence | Fallback |
|-----------|-----------------|------------|----------|
| **Project Type** | Import analysis | High (90%) | "cli" |
| - Django detected | → web_app | 95% | |
| - Flask detected | → web_app | 95% | |
| - Click detected | → cli | 90% | |
| - FastAPI detected | → api | 95% | |
| - React detected | → web_app | 90% | |
| **Primary Language** | File extensions | High (95%) | "python" |
| - .py files majority | → python | 95% | |
| - .js/.ts majority | → javascript/typescript | 95% | |
| - .go majority | → go | 95% | |
| **Backend Framework** | Import/package scan | High (90%) | None |
| - `import django` | → Django + version | 95% | |
| - `from flask` | → Flask + version | 95% | |
| - `import fastapi` | → FastAPI + version | 95% | |
| **Frontend Framework** | package.json/imports | High (85%) | None |
| - `react` in package.json | → React + version | 90% | |
| - `vue` in package.json | → Vue + version | 90% | |
| - Alpine.js in HTML | → Alpine + version | 85% | |
| **Database** | Dependencies | Medium (75%) | "sqlite" |
| - `psycopg2` detected | → PostgreSQL | 80% | |
| - `pymongo` detected | → MongoDB | 85% | |
| - No DB deps | → SQLite | 60% | |
| **Testing Framework** | Dependencies | High (90%) | "pytest" |
| - `pytest` in deps | → pytest + version | 95% | |
| - `unittest` imports | → unittest | 90% | |
| **Architecture Style** | Project structure | Medium (65%) | "monolith" |
| - Single app | → monolith | 70% | |
| - Multiple services | → microservices | 75% | |
| - hexagonal structure | → hexagonal | 80% | |
| **Deployment Strategy** | CI/CD files | Medium (70%) | "manual" |
| - .github/workflows | → ci_cd (GitHub Actions) | 85% | |
| - .gitlab-ci.yml | → ci_cd (GitLab) | 85% | |
| - Dockerfile | → containerization | 75% | |
| **DevOps Practices** | File scan | Medium (70%) | [] |
| - Dockerfile | → containerization | 80% | |
| - docker-compose.yml | → orchestration | 75% | |
| - terraform/ | → infrastructure_as_code | 80% | |

### 3.2 Rules Preset Auto-Selection

```python
def select_rules_preset(detection: DetectionResult, answers: Dict) -> str:
    """Auto-select rules preset based on detection and answers."""

    score = 0

    # Team size factor
    if answers.get('team_size') in ['medium', 'large']:
        score += 2
    elif answers.get('team_size') == 'small':
        score += 1

    # Development stage factor
    if answers.get('dev_stage') == 'enterprise':
        score += 3
    elif answers.get('dev_stage') == 'production':
        score += 2
    elif answers.get('dev_stage') == 'mvp':
        score += 1

    # Compliance factor
    if answers.get('compliance_requirements'):
        score += 2

    # Framework maturity factor
    if detection.has_framework('django') or detection.has_framework('react'):
        score += 1  # Mature frameworks → stricter patterns

    # Select preset
    if score >= 6:
        return 'strict'      # Enterprise, large team, compliance
    elif score >= 3:
        return 'standard'    # MVP, small team, no compliance
    else:
        return 'flexible'    # Prototype, solo, rapid iteration
```

### 3.3 Fixed Defaults (No Detection Needed)

| Attribute | Default Value | Rationale |
|-----------|--------------|-----------|
| Description | "Project managed by APM" | Generic, user can update later |
| Code Review | True | Best practice, can disable later |
| Test Coverage | 90% | APM standard, adjustable |
| Max Task Duration | 4h | APM core principle (time-boxing) |
| Development Approach | "agile" | Generic modern practice |
| Architecture (unknown) | "monolith" | Simplest assumption |

---

## 4. Interaction Patterns

### 4.1 Default Mode: Progressive Disclosure (Recommended)

**Goal**: Fast onboarding with smart defaults, minimal questions

```bash
$ apm init "My Django App"

🚀 Initializing APM project: My Django App
📁 Location: /Users/john/projects/myapp

✓ Creating directory structure...
✓ Initializing database schema...
✓ Creating project record...

🔍 Detecting frameworks and tools...
   Scanning project files...

   Detected Technologies:
   ┌─────────────┬────────────┬──────────────┐
   │ Technology  │ Confidence │ Version      │
   ├─────────────┼────────────┼──────────────┤
   │ Python      │ 95%        │ 3.11         │
   │ Django      │ 95%        │ 5.0.3        │
   │ PostgreSQL  │ 80%        │ 15.2         │
   │ pytest      │ 95%        │ 8.0.1        │
   └─────────────┴────────────┴──────────────┘

   📊 Detected 4 technologies in 1.2s
   📁 Generated 8 code amalgamation files

⚙️  Project Configuration (2 questions)

   ? Development Stage:
     > MVP (recommended based on git history)
       Prototype (fast iteration)
       Production (stable)
       Enterprise (maximum governance)

   ? Team Size:
     > Solo developer (recommended)
       Small team (2-5)
       Medium team (6-15)
       Large team (16+)

✓ Rules configured (75 rules loaded, preset: standard)

🤖 Generating agents...
   Creating 85 specialized agents...
   ✓ Phase orchestrators (6)
   ✓ Specialist agents (15)
   ✓ Sub-agents (25)
   ✓ Utility agents (10)

   📝 Agent files written to .claude/agents/

✓ Context assembled (confidence: 87%)
✓ Verification complete

✅ Project initialized successfully!

┌──────────────────────────────────────────────┐
│ Ready to use! Try:                           │
│                                              │
│ apm work-item create "Add user auth"        │
│ apm status                                   │
│ apm context show                             │
└──────────────────────────────────────────────┘

💾 Database: .agentpm/data/agentpm.db (5.8 MB)
📁 Project ID: 1
⏱️  Total time: 2m 34s
```

**Key Features**:
- Only 2 questions asked (others auto-detected)
- Smart defaults clearly marked
- Agent generation automatic
- Clear success indicators
- Next steps obvious

### 4.2 Wizard Mode: Detailed Walkthrough

**Goal**: Educational, full control, ideal for first-time users

```bash
$ apm init "My Project" --wizard

╔════════════════════════════════════════════╗
║  APM Initialization Wizard                 ║
║  Step-by-step setup with explanations      ║
╚════════════════════════════════════════════╝

Step 1 of 7: Project Information
─────────────────────────────────

Project Name: My Project
Description: [Project managed by APM]
> Full-stack e-commerce application

ℹ️  The description helps agents understand project context
   and provide more relevant suggestions.

Step 2 of 7: Framework Detection
─────────────────────────────────

🔍 Scanning your project...

Detected:
  • Python 3.11 (99% confidence)
  • Django 5.0.3 (95% confidence)
  • React 18.2 (90% confidence)
  • PostgreSQL 15.2 (85% confidence)

? Multiple frameworks detected. Primary backend?
  > Django 5.0.3 (recommended)
    React 18.2
    Other

ℹ️  The primary framework determines which code examples
   and patterns agents will prioritize.

Step 3 of 7: Development Stage
───────────────────────────────

? What stage is this project?
  • Prototype - Fast iteration, minimal gates
  • MVP - Balanced approach, core quality gates
  > Production - Full quality enforcement
  • Enterprise - Maximum governance and compliance

ℹ️  This determines rule strictness:
   • Prototype: 45 rules (flexible)
   • MVP: 60 rules (balanced)
   • Production: 75 rules (strict)
   • Enterprise: 90 rules (comprehensive)

[Continue with remaining steps...]

Step 7 of 7: Agent Generation
──────────────────────────────

? Generate AI agent files now?
  > Yes (recommended) - Ready to use immediately
    No - Generate later with 'apm agents generate --all'

ℹ️  Agent files enable Claude, Cursor, and other AI tools
   to understand your project's quality requirements.

Generating 85 specialized agents... ━━━━━━ 100%

✅ Setup Complete!

[Show summary as in default mode]
```

**Key Features**:
- 7 clear steps with progress
- Explanations for each choice
- Can go back to previous steps
- Educational (first-time friendly)
- ~5-7 minutes total

### 4.3 Silent Mode: Zero-Interaction Automation

**Goal**: CI/CD, scripting, experienced users, fastest possible

```bash
$ apm init "My Project" --auto

🚀 APM Auto-Init: My Project

✓ Database initialized (57 tables)
✓ Frameworks detected: Python, Django, PostgreSQL, pytest
✓ Rules loaded: 75 rules (standard preset)
✓ Agents generated: 85 agents
✓ Context assembled (confidence: 82%)

✅ Complete in 1m 43s

Next: apm work-item create "Feature name"
```

**Key Features**:
- Zero questions
- 100% automatic detection
- Minimal output (CI-friendly)
- Fastest possible (<2 minutes)
- Ideal for scripting

### 4.4 Configuration Mode: Custom Presets

**Goal**: Reusable configurations for teams

```bash
$ apm init "My Project" --preset team-standard

Using preset: team-standard
  • Team size: small
  • Dev stage: production
  • Rules: strict (80 rules)
  • Code review: required
  • Test coverage: 95%
  • Compliance: SOC2

[Continue with auto-detection and agent generation...]
```

**Key Features**:
- Shareable presets (JSON/YAML)
- Team consistency
- Overrides auto-detection
- Can be version-controlled

---

## 5. Error Handling Matrix

### 5.1 Pre-Init Errors

| Error | User Message | Recovery Action | Auto-Recovery |
|-------|--------------|-----------------|---------------|
| **Already initialized** | ❌ Project already initialized at /path<br><br>💡 To re-initialize:<br>  1. Backup database: cp .agentpm/data/agentpm.db backup.db<br>  2. Remove: rm -rf .agentpm<br>  3. Retry: apm init "Project" | Manual cleanup | No |
| **Python version < 3.9** | ❌ APM requires Python 3.9+<br>Current: Python 3.8.10<br><br>💡 Upgrade:<br>  • Ubuntu: sudo apt install python3.9<br>  • macOS: brew install python@3.9<br>  • Windows: Download from python.org | User upgrade | No |
| **No write permissions** | ❌ Cannot create .agentpm directory<br>Permission denied: /project/path<br><br>💡 Fix permissions:<br>  sudo chown -R $USER /project/path<br>OR<br>  Choose different location: apm init "Project" ~/myproject | Manual fix or relocate | No |
| **Insufficient disk space** | ❌ Insufficient disk space<br>Required: 50 MB, Available: 12 MB<br><br>💡 Free up space:<br>  • Clear cache: rm -rf ~/.cache/<br>  • Check usage: df -h | Manual cleanup | No |
| **Invalid project name** | ❌ Invalid project name: "My/Project"<br>Names cannot contain: / \\ : * ? " < > \|<br><br>💡 Use alphanumeric and spaces:<br>  apm init "My Project" | Retry with valid name | No |
| **Parent directory missing** | ❌ Directory not found: /path/to/project<br><br>💡 Create directory first:<br>  mkdir -p /path/to/project<br>  apm init "Project" /path/to/project | Manual directory creation | No |
| **Nested APM project** | ⚠️  Parent directory /parent has .agentpm/<br>Nested APM projects are not recommended.<br><br>? Continue anyway? [y/N] | User confirmation | No |

### 5.2 Init Phase Errors

| Phase | Error | User Message | Recovery | Rollback |
|-------|-------|--------------|----------|----------|
| **Database Setup** | Migration failure | ❌ Database initialization failed<br>Error: migration 0012 failed (duplicate column)<br><br>💡 This usually indicates a corrupted init.<br>Recovery:<br>  rm -rf .agentpm<br>  apm init "Project" | Manual cleanup + retry | Auto (cleanup partial DB) |
| **Framework Detection** | Detection timeout | ⚠️  Framework detection timed out (>30s)<br>Continuing with defaults...<br><br>You can re-run detection later:<br>  apm detect analyze | Continue with defaults | No (graceful degradation) |
| **Framework Detection** | Detection crash | ⚠️  Framework detection failed<br>Error: FileNotFoundError: package.json<br><br>Continuing with generic project setup...<br><br>Detection can be run later:<br>  apm detect analyze | Continue without detection | No (graceful degradation) |
| **Rules Loading** | Rule validation error | ❌ Rules loading failed<br>Error: Invalid rule DP-001 (missing severity)<br><br>💡 This is a system error. Please report:<br>  https://github.com/.../issues | Abort and report | Auto (cleanup) |
| **Agent Generation** | Agent file write error | ❌ Cannot write agent files<br>Permission denied: .claude/agents/<br><br>💡 Fix permissions:<br>  mkdir -p .claude/agents<br>  chmod 755 .claude | Manual fix + retry | Partial (keep DB, retry agents) |
| **Agent Generation** | Template error | ❌ Agent generation failed<br>Error: Template not found: orchestrator.j2<br><br>💡 APM installation may be corrupted.<br>Reinstall:<br>  pip install --force-reinstall agentpm | Reinstall + retry | Auto (cleanup agents) |
| **Context Assembly** | Low confidence | ⚠️  Context confidence low (42%)<br>Reason: Few frameworks detected<br><br>This is okay. Confidence improves as you work.<br>Continuing... | Continue | No |
| **Verification** | Database corrupt | ❌ Verification failed<br>Database integrity check failed<br>Expected: 57 tables, Found: 45<br><br>💡 Initialization incomplete. Clean up:<br>  rm -rf .agentpm<br>  apm init "Project" | Manual cleanup + retry | Auto (cleanup) |

### 5.3 Network/External Errors

| Error | User Message | Recovery | Retry Logic |
|-------|--------------|----------|-------------|
| **PyPI timeout** | ❌ Package download timed out<br><br>💡 Check network connection:<br>  ping pypi.org<br>Retry: pip install agentpm | Manual retry | 3 attempts with backoff |
| **Git repository error** | ⚠️  Not a git repository<br>Git integration disabled.<br><br>Initialize git:<br>  git init | Continue without git | No (optional feature) |
| **Plugin download fail** | ⚠️  Plugin assets download failed<br>Continuing with cached plugins...<br><br>Network required for updates:<br>  Check connection and retry later | Use cached | 2 attempts, then cache |

### 5.4 Rollback Strategy

```python
class InitOrchestrator:
    """Manages init with automatic rollback on failure."""

    def __init__(self):
        self.checkpoints = []
        self.cleanup_actions = []

    def execute(self) -> InitResult:
        """Execute init with rollback on failure."""

        try:
            # Stage 1: Database
            self.checkpoint("database_created")
            self.setup_database()

            # Stage 2: Detection
            self.checkpoint("detection_complete")
            self.run_detection()

            # Stage 3: Rules
            self.checkpoint("rules_loaded")
            self.load_rules()

            # Stage 4: Agents
            self.checkpoint("agents_generated")
            self.generate_agents()

            # Stage 5: Context
            self.checkpoint("context_assembled")
            self.assemble_context()

            return InitResult(success=True)

        except Exception as e:
            # Rollback to last successful checkpoint
            self.rollback()
            raise InitError(f"Initialization failed: {e}")

    def rollback(self):
        """Clean up partial initialization."""

        last_checkpoint = self.checkpoints[-1]

        if last_checkpoint == "database_created":
            # Only database exists, remove it
            shutil.rmtree(".agentpm")

        elif last_checkpoint == "agents_generated":
            # Keep database and rules, only remove agents
            shutil.rmtree(".claude/agents", ignore_errors=True)

        # Execute custom cleanup actions
        for action in reversed(self.cleanup_actions):
            try:
                action()
            except Exception:
                pass  # Best effort
```

---

## 6. Success Output Specification

### 6.1 Ideal Success Output (Default Mode)

```
✅ Project initialized successfully!

┌─────────────────────────────────────────────────────────┐
│ 🔍 Detected Technologies                                │
├─────────────┬────────────┬───────────────────────────────┤
│ Technology  │ Confidence │ Details                       │
├─────────────┼────────────┼───────────────────────────────┤
│ Python      │ 95%        │ 3.11.5                        │
│ Django      │ 95%        │ 5.0.3                         │
│ PostgreSQL  │ 80%        │ 15.2                          │
│ pytest      │ 95%        │ 8.0.1                         │
│ React       │ 90%        │ 18.2.0                        │
│ Tailwind    │ 85%        │ 3.4.1                         │
└─────────────┴────────────┴───────────────────────────────┘

📊 Detected 6 technologies in 1.4s
📁 Generated 12 code amalgamation files (.agentpm/contexts/)

┌─────────────────────────────────────────────────────────┐
│ ⚙️  Project Configuration                                │
├─────────────────────┬───────────────────────────────────┤
│ Rules Loaded        │ 75 rules                          │
│ Preset              │ Standard                          │
│ Team Size           │ Solo developer                    │
│ Dev Stage           │ MVP                               │
│ Test Coverage       │ 90%                               │
│ Max Task Duration   │ 4h                                │
│ Code Review         │ Required                          │
└─────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🤖 Agents Generated                                      │
├─────────────────────┬───────────────────────────────────┤
│ Phase Orchestrators │ 6 agents                          │
│ Specialist Agents   │ 15 agents                         │
│ Sub-Agents          │ 25 agents                         │
│ Utility Agents      │ 10 agents                         │
├─────────────────────┼───────────────────────────────────┤
│ Total               │ 56 agents                         │
│ Location            │ .claude/agents/                   │
└─────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 Project Intelligence                                  │
├─────────────────────┬───────────────────────────────────┤
│ Context Confidence  │ 87%                               │
│ Code Patterns       │ 24 patterns extracted             │
│ Framework Facts     │ 156 facts stored                  │
│ Test Discovery      │ 89 tests found                    │
└─────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🚀 Ready to Use!                                        │
│                                                          │
│ Create your first work item:                            │
│   apm work-item create "Add user authentication"       │
│                                                          │
│ View project dashboard:                                 │
│   apm status                                            │
│                                                          │
│ Explore detected frameworks:                            │
│   apm context show                                      │
│                                                          │
│ Get help:                                               │
│   apm --help                                            │
└─────────────────────────────────────────────────────────┘

💾 Database: .agentpm/data/agentpm.db (5.8 MB, 57 tables)
📁 Project ID: 1
⏱️  Total time: 2m 34s

Need help? https://docs.apm.dev/getting-started
Report issues: https://github.com/nigelcopley/agentpm/issues
```

### 6.2 Minimal Success Output (Silent Mode)

```
✅ APM initialized: My Project

Detected: Python 3.11, Django 5.0, PostgreSQL 15.2, pytest 8.0
Rules: 75 loaded (standard)
Agents: 56 generated
Context: 87% confidence

Next: apm work-item create "Feature name"

⏱️  1m 43s
```

### 6.3 Warning Output (Partial Success)

```
⚠️  Project initialized with warnings

✓ Database initialized (57 tables)
✓ Frameworks detected: Python, Django
✓ Rules loaded (75 rules)
⚠️  Agent generation: 12 of 85 agents failed
    Failed agents written to: .agentpm/agent-generation-errors.log
✓ Context assembled (confidence: 72%)

💡 Some agents failed to generate. This won't prevent
   basic usage, but some advanced features may not work.

   View errors: cat .agentpm/agent-generation-errors.log
   Retry: apm agents generate --all --force

You can still create work items:
  apm work-item create "Feature name"

⏱️  2m 18s
```

---

## 7. Implementation Checklist

### 7.1 Phase 1: Core Integration (Critical Path)

**Goal**: Make `apm init` automatically call agent generation

- [ ] **Refactor init.py to call agent generation**
  - Move lines 293-299 (agent generation message) inside progress block
  - Import `agentpm.cli.commands.agents.generate`
  - Call `generate_all_agents()` after rules configuration
  - Handle errors gracefully (warnings, not failures)

- [ ] **Create InitOrchestrator service**
  - File: `agentpm/core/init/orchestrator.py`
  - Phases: Database → Detection → Rules → Agents → Context → Verify
  - Checkpoint system with rollback
  - Error handling at each phase

- [ ] **Implement rollback mechanism**
  - Partial cleanup on failure
  - Preserve database if only agents fail
  - Clear error messages
  - Recovery instructions

- [ ] **Add verification phase**
  - Check database integrity (57 tables)
  - Verify agent files written (85 files)
  - Validate rules loaded (count)
  - Calculate context confidence

**Estimated Effort**: 6-8 hours

### 7.2 Phase 2: Smart Questionnaire (UX Improvement)

**Goal**: Reduce questions from 18 to 5-7 with smart defaults

- [ ] **Refactor questionnaire to use detection results**
  - Pass `DetectionResult` to all question functions
  - Skip questions when confidence > 80%
  - Show auto-detected values as defaults
  - Explain why each question is asked

- [ ] **Implement conditional question logic**
  - Function: `determine_questions(detection: DetectionResult) -> List[Question]`
  - Always ask: dev_stage, team_size
  - Conditionally ask: compliance, primary_backend, deployment
  - Skip if obvious from detection

- [ ] **Create rules preset auto-selection**
  - Function: `select_rules_preset(detection, answers) -> str`
  - Score-based algorithm (team size + dev stage + compliance)
  - Result: flexible/standard/strict
  - Show reasoning: "Selected 'standard' preset (MVP, solo developer)"

- [ ] **Add smart defaults display**
  - Show what was auto-detected
  - Format: "Django 5.0 detected (95% confidence) → web_app"
  - Allow override: "Press Enter to accept, or type to override"

- [ ] **Implement progressive disclosure UI**
  - Rich progress bars for each stage
  - Collapsible sections for advanced options
  - Clear stage indicators (1/7, 2/7, etc.)

**Estimated Effort**: 4-6 hours

### 7.3 Phase 3: Wizard & Silent Modes (Optional Modes)

**Goal**: Support different user preferences

- [ ] **Implement --wizard flag**
  - 7-step wizard with explanations
  - Back button (return to previous step)
  - Help text for each choice
  - Show impact of choices

- [ ] **Implement --auto flag**
  - Skip all questions
  - 100% auto-detection
  - Minimal output (CI-friendly)
  - Complete in <2 minutes

- [ ] **Implement --preset option**
  - Load preset from file or name
  - Format: JSON/YAML
  - Built-in presets: solo, team, enterprise, ci-cd
  - Override auto-detection

- [ ] **Add --dry-run flag**
  - Show what would happen
  - Don't create files
  - Useful for understanding dependencies

**Estimated Effort**: 6-8 hours

### 7.4 Phase 4: Error Handling & Recovery (Robustness)

**Goal**: Clear errors, automatic recovery where possible

- [ ] **Pre-flight checks**
  - Python version check
  - Write permission check
  - Disk space check
  - Existing .agentpm detection
  - Git repository detection

- [ ] **Phase-specific error handling**
  - Database: rollback on migration failure
  - Detection: graceful degradation (continue with defaults)
  - Rules: clear validation errors
  - Agents: partial success handling (some agents fail)

- [ ] **Create error taxonomy**
  - Critical errors (abort init)
  - Warnings (continue with degraded functionality)
  - Info (optional features disabled)

- [ ] **Implement recovery commands**
  - `apm init --cleanup` - Remove broken .agentpm
  - `apm init --repair` - Fix partial initialization
  - `apm deinit` - Complete removal

- [ ] **Add detailed error logging**
  - Log file: `.agentpm/init-errors.log`
  - Include: stack traces, system info, detection results
  - Reference in error messages

**Estimated Effort**: 4-6 hours

### 7.5 Phase 5: Verification & Success Output (Polish)

**Goal**: Clear success indicators and next steps

- [ ] **Implement verification phase**
  - Database integrity check
  - Agent file check
  - Rules count validation
  - Context confidence calculation

- [ ] **Design success output**
  - Detected technologies table
  - Project configuration table
  - Agents generated summary
  - Context intelligence metrics
  - Next steps section

- [ ] **Add timing metrics**
  - Total time
  - Time per phase
  - Performance baseline (<3 minutes target)

- [ ] **Implement warning output**
  - Partial success display
  - What succeeded vs. what failed
  - Recovery instructions
  - Fallback commands

**Estimated Effort**: 2-3 hours

### 7.6 Phase 6: Documentation & Help (Usability)

**Goal**: Comprehensive documentation and help

- [ ] **Update --help text**
  - Add examples
  - Explain options
  - Show default behavior
  - Reference documentation

- [ ] **Create INSTALL.md**
  - Installation instructions
  - System requirements
  - Troubleshooting guide
  - FAQ

- [ ] **Update README.md**
  - Reflect single-command init
  - Remove manual agent generation step
  - Update quick start examples

- [ ] **Create init guide**
  - docs/user-guides/initialization.md
  - Explain each mode
  - Show examples
  - Troubleshooting section

- [ ] **Add video/GIF demo**
  - Record init process
  - Show <3 minute completion
  - Embed in README

**Estimated Effort**: 3-4 hours

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| **Time to First Work Item** | 8-10 min | <3 min | Timer from `pip install` to `apm work-item create` success |
| **Number of Commands** | 3 | 1 | Count commands required (init, agents, work-item) |
| **Questions Asked** | 18 | 5-7 | Average questions in questionnaire |
| **Init Success Rate** | ~85% | >95% | Success / total attempts |
| **Zero-Error Init Rate** | ~60% | >90% | Inits with no warnings or errors |
| **User Understanding** | ~60% | >95% | Survey: "Do you know what to do next?" |
| **Agent Generation Time** | N/A (manual) | <60s | Time for `generate_all_agents()` |
| **Total Init Time** | N/A | <180s | Time for complete `apm init` |

### 8.2 Qualitative Metrics

**User Satisfaction**:
- [ ] "Init was fast and clear"
- [ ] "I understood what was happening"
- [ ] "I knew what to do next"
- [ ] "Errors were clear and actionable"
- [ ] "I didn't need to read documentation"

**Comparison to Best Practices**:
- [ ] Matches Create React App simplicity
- [ ] Matches Poetry automation
- [ ] Matches Terraform clarity
- [ ] Matches Vercel speed

**Community Feedback**:
- [ ] GitHub Issues: init-related issues < 5%
- [ ] Discord: positive init feedback
- [ ] Reddit/HN: favorable comparisons to other tools

### 8.3 Performance Benchmarks

| Phase | Current | Target | Acceptable |
|-------|---------|--------|------------|
| Database Setup | 2-3s | 2-3s | ≤5s |
| Framework Detection | 1-2s | 1-2s | ≤3s |
| Rules Configuration | 30-60s | 30-60s | ≤90s |
| Agent Generation | N/A | 30-60s | ≤90s |
| Context Assembly | <1s | <1s | ≤2s |
| Verification | N/A | <1s | ≤2s |
| **Total** | **~4-6 min** | **<3 min** | **≤5 min** |

### 8.4 Validation Tests

**Integration Tests**:
```python
def test_init_complete_flow():
    """Test complete init from start to first work item."""

    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Create sample Django project structure
        create_sample_project()

        # Run init
        start = time.time()
        result = subprocess.run(
            ['apm', 'init', 'Test Project', '--auto'],
            capture_output=True,
            timeout=300  # 5 minute max
        )
        duration = time.time() - start

        # Assertions
        assert result.returncode == 0
        assert duration < 180  # <3 minutes
        assert Path('.agentpm/data/agentpm.db').exists()
        assert Path('.claude/agents/').exists()
        assert len(list(Path('.claude/agents/').rglob('*.md'))) >= 85

        # Verify can create work item
        result = subprocess.run(
            ['apm', 'work-item', 'create', 'Test Feature'],
            capture_output=True
        )
        assert result.returncode == 0
        assert 'Work item #1 created' in result.stdout.decode()
```

**Smoke Tests**:
- [ ] Init in empty directory
- [ ] Init in Django project
- [ ] Init in Flask project
- [ ] Init in React project
- [ ] Init in multi-language project
- [ ] Init with no git
- [ ] Init with existing git
- [ ] Init with --auto
- [ ] Init with --wizard
- [ ] Init with --preset

**Error Scenario Tests**:
- [ ] Init twice (should fail gracefully)
- [ ] Init with invalid name
- [ ] Init with no permissions
- [ ] Init with low disk space
- [ ] Init with network failure
- [ ] Init with corrupted migration
- [ ] Init with missing templates

---

## 9. Migration Path for Existing Users

### 9.1 Existing Projects (Already Initialized)

**Scenario**: User has projects with `apm init` but no agents

```bash
$ cd existing-project
$ apm agents generate --all

# New behavior: Detect if this is needed
$ apm status
⚠️  Agents not generated
   Run: apm agents generate --all
```

**Upgrade Command** (optional):
```bash
$ apm init --upgrade

Detected existing APM project (ID: 1)
  • Database: ✓ (57 tables)
  • Rules: ✓ (75 rules)
  • Agents: ✗ (not generated)

Upgrading to new init format...
  ✓ Generating agents (85 agents)
  ✓ Assembling context (confidence: 84%)
  ✓ Verification complete

✅ Project upgraded to new format!
```

### 9.2 Version Detection

```python
def detect_init_version(project_path: Path) -> str:
    """Detect which init version was used."""

    db_path = project_path / '.agentpm' / 'data' / 'agentpm.db'
    agents_path = project_path / '.claude' / 'agents'

    if not db_path.exists():
        return 'not_initialized'

    if not agents_path.exists():
        return 'v1_incomplete'  # Old init (no agents)

    if agents_path.exists() and len(list(agents_path.rglob('*.md'))) >= 85:
        return 'v2_complete'  # New init (with agents)

    return 'v1_partial'  # Some agents but not all
```

### 9.3 Backward Compatibility

**Preserve Old Behavior** (optional flag):
```bash
$ apm init "Project" --no-agents

# Same as old behavior:
# - Database init
# - Framework detection
# - Rules configuration
# - NO agent generation (manual step)
```

**Support Old Workflows**:
```bash
$ apm agents generate --all

# Still works as separate command
# Detects if already generated (skip)
# Updates if rules changed
```

---

## 10. Open Questions & Decisions Needed

### 10.1 Technical Decisions

1. **Agent Generation Performance**
   - Q: Can we generate 85 agents in <60 seconds?
   - Current: Unknown (not benchmarked)
   - Decision: Need to measure current performance
   - Mitigation: If slow, show progress bar with ETA

2. **Question Interruptibility**
   - Q: Can users skip questionnaire with Ctrl+C without breaking init?
   - Current: Probably not (incomplete init)
   - Decision: Should we support "minimal init" if user interrupts?
   - Proposal: Ctrl+C during questionnaire → use all defaults

3. **Parallel Phase Execution**
   - Q: Can we run detection + rules in parallel?
   - Current: Sequential
   - Decision: Would save ~30-60 seconds
   - Risk: Race conditions, error handling complexity

4. **Plugin Download**
   - Q: Do plugins need to download external assets?
   - Current: Unknown
   - Decision: If yes, add network timeout handling
   - Fallback: Use cached/bundled versions

### 10.2 UX Decisions

1. **Default Mode Behavior**
   - Q: Should default mode ask questions or be fully automatic?
   - Option A: Ask 2-3 critical questions (recommended)
   - Option B: Fully automatic with `--interactive` for questions
   - Recommendation: Option A (progressive disclosure)

2. **Success Output Verbosity**
   - Q: How much detail to show in success message?
   - Option A: Comprehensive (as shown in spec)
   - Option B: Minimal (just "Ready! Try: apm work-item create")
   - Recommendation: Option A (default), add `--quiet` flag

3. **Warning vs. Error**
   - Q: Should agent generation failure be error or warning?
   - Option A: Error (abort init)
   - Option B: Warning (continue with partial)
   - Recommendation: Option B (usable without all agents)

4. **First-Time vs. Experienced Users**
   - Q: Optimize for first-time or experienced users?
   - Option A: First-time (explain everything)
   - Option B: Experienced (minimal output, fast)
   - Recommendation: Default to experienced, `--wizard` for first-time

### 10.3 Scope Decisions

1. **Preset Files**
   - Q: Should we support preset files for teams?
   - Value: High (team consistency)
   - Effort: Medium (2-3 hours)
   - Decision: Include in Phase 3 (optional modes)

2. **Init Templates**
   - Q: Should we support project templates (like create-react-app)?
   - Value: Very high (instant working code)
   - Effort: Very high (20+ hours)
   - Decision: Future enhancement (not in this spec)

3. **Cloud Integration**
   - Q: Should init support cloud deployments?
   - Value: Medium (nice-to-have)
   - Effort: High (10+ hours)
   - Decision: Future enhancement (not in this spec)

---

## 11. Risk Assessment

### 11.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Agent generation too slow** | Medium | High | Show progress, optimize templates, consider caching |
| **Database migration conflicts** | Low | Critical | Extensive testing, rollback mechanism |
| **Detection false positives** | Medium | Medium | Confidence thresholds, user override |
| **Rollback failures** | Low | High | Test exhaustively, manual recovery docs |
| **Network timeouts** | Medium | Low | Fallback to cached, graceful degradation |

### 11.2 UX Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Too much automation** | Medium | Medium | Provide --wizard for full control |
| **Not enough automation** | Low | High | Default to maximum automation |
| **Unclear next steps** | Low | High | Comprehensive success output |
| **Error messages unclear** | Medium | High | User testing, iterate on clarity |
| **Users skip verification** | High | Low | Always show, highlight issues |

### 11.3 Compatibility Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Breaking existing projects** | Low | Critical | Version detection, upgrade path |
| **CI/CD integration issues** | Medium | Medium | --auto mode, exit codes |
| **Cross-platform issues** | Medium | Medium | Test on Windows/Mac/Linux |
| **Python version incompatibility** | Low | Medium | Clear version check |

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Core Components**:
- [ ] InitOrchestrator phases
- [ ] Question determination logic
- [ ] Smart defaults selection
- [ ] Rules preset selection
- [ ] Error handling per phase
- [ ] Rollback mechanism

**Coverage Target**: >90%

### 12.2 Integration Tests

**End-to-End Flows**:
- [ ] Complete init flow (default mode)
- [ ] Complete init flow (wizard mode)
- [ ] Complete init flow (silent mode)
- [ ] Init with various project types
- [ ] Init with error recovery
- [ ] Init rollback scenarios

**Coverage Target**: All critical paths

### 12.3 User Acceptance Tests

**Real-World Scenarios**:
- [ ] Django project initialization
- [ ] Flask project initialization
- [ ] React project initialization
- [ ] Multi-language project
- [ ] Empty directory
- [ ] Existing project upgrade

**Validation**:
- [ ] <3 minute completion
- [ ] Clear success indicators
- [ ] No confusing errors
- [ ] Next steps obvious

### 12.4 Performance Tests

**Benchmarks**:
- [ ] Database setup time
- [ ] Framework detection time
- [ ] Agent generation time
- [ ] Total init time
- [ ] Memory usage
- [ ] Disk usage

**Target**: <3 minutes on standard hardware

---

## 13. Documentation Requirements

### 13.1 User Documentation

**Required Documents**:
- [ ] Installation guide (INSTALL.md)
- [ ] Quick start guide (README.md update)
- [ ] Initialization guide (docs/user-guides/init.md)
- [ ] Troubleshooting guide (docs/troubleshooting/init.md)
- [ ] FAQ (docs/faq/init.md)

### 13.2 Developer Documentation

**Required Documents**:
- [ ] InitOrchestrator architecture (docs/architecture/init.md)
- [ ] Plugin integration guide (docs/developers/plugins.md)
- [ ] Error handling guide (docs/developers/errors.md)
- [ ] Testing guide (docs/developers/testing-init.md)

### 13.3 Video/Visual Content

**Required Assets**:
- [ ] Init demo video (<2 minutes)
- [ ] GIF for README (init completion)
- [ ] Screenshots for documentation
- [ ] Architecture diagrams

---

## 14. Launch Plan

### 14.1 Alpha Release (Internal Testing)

**Target**: Week 1-2

**Goals**:
- [ ] Core integration complete
- [ ] Default mode working
- [ ] Basic error handling
- [ ] Internal dogfooding

**Validation**:
- [ ] 10 successful inits on real projects
- [ ] No critical bugs
- [ ] Performance within targets

### 14.2 Beta Release (Limited Users)

**Target**: Week 3-4

**Goals**:
- [ ] All modes working (default, wizard, silent)
- [ ] Comprehensive error handling
- [ ] Documentation complete
- [ ] User testing (10-20 users)

**Validation**:
- [ ] User satisfaction >80%
- [ ] Success rate >95%
- [ ] Performance <3 minutes
- [ ] No blocking issues

### 14.3 General Release (Public)

**Target**: Week 5

**Goals**:
- [ ] PyPI publication
- [ ] Public announcement
- [ ] Marketing materials
- [ ] Support channels ready

**Success Criteria**:
- [ ] 100 successful inits in first week
- [ ] <5% init-related issues
- [ ] Positive community feedback
- [ ] No regression reports

---

## 15. Future Enhancements (Post-Launch)

### 15.1 Short-Term (1-3 months)

1. **Interactive Dashboard**
   - Real-time init progress
   - Web UI for initialization
   - Visual framework detection

2. **Cloud Integration**
   - One-click deployment setup
   - GitHub/GitLab integration
   - CI/CD template generation

3. **Team Features**
   - Shared presets
   - Team templates
   - Centralized configuration

### 15.2 Long-Term (3-6 months)

1. **Project Templates**
   - Create-APM-App (like create-react-app)
   - Template marketplace
   - Custom template creation

2. **AI-Powered Detection**
   - ML-based framework detection
   - Confidence improvement
   - Pattern learning

3. **Init Analytics**
   - Telemetry (opt-in)
   - Performance tracking
   - Error pattern analysis

---

## 16. Conclusion

This specification provides a comprehensive blueprint for transforming APM's installation experience from a fragmented 3-command workflow to a seamless single-command experience that matches industry best practices.

**Key Achievements**:
- ✅ Reduced commands: 3 → 1
- ✅ Reduced time: 8-10 min → <3 min
- ✅ Reduced questions: 18 → 5-7
- ✅ Increased clarity: ~60% → >95%
- ✅ Industry-leading UX: Matches Vercel, Netlify, Create React App

**Implementation Priority**:
1. Phase 1: Core integration (6-8h) - **CRITICAL**
2. Phase 2: Smart questionnaire (4-6h) - **HIGH**
3. Phase 4: Error handling (4-6h) - **HIGH**
4. Phase 5: Success output (2-3h) - **MEDIUM**
5. Phase 3: Optional modes (6-8h) - **MEDIUM**
6. Phase 6: Documentation (3-4h) - **MEDIUM**

**Total Estimated Effort**: 25-35 hours

**Expected Outcome**: 90% of users go from `pip install` to first work item in <3 minutes with 95%+ clarity on next steps.

---

**Next Steps**: Review this specification, approve approach, and proceed with Phase 1 implementation.

**Version**: 1.0
**Status**: Ready for Review
**Author**: APM UX Specification Team
**Date**: October 25, 2025
