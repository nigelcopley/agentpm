# Three-Tier Orchestration Architecture

**Version**: 2.0
**Status**: Production
**Last Updated**: 2025-10-19
**Component**: Agent System

---

## Executive Summary

The APM (Agent Project Manager) agent system implements a **three-tier orchestration architecture** that organizes 84+ specialized AI agents into a hierarchical structure for efficient project development. This architecture enables intelligent routing, phase-based coordination, and specialized task execution through a clear delegation hierarchy.

**Key Architecture Principles**:
- **Separation of Concerns**: Each tier has distinct responsibilities
- **Hierarchical Delegation**: Work flows from orchestrators to specialists
- **Database-Driven**: Agent metadata stored in database, files generated on-demand
- **Provider-Agnostic**: Core system supports multiple LLM providers

---

## 1. Architecture Overview

### 1.1 Three-Tier Structure

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Master Orchestrator (1 agent)                      │
│                                                              │
│ Role: Route work by phase and artifact type                │
│ Never executes: Always delegates to Tier 2                 │
└───────────────────────┬──────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼─────────────────────────────────────────────────────┐
│ TIER 2: Phase Orchestrators (6 agents)                      │
│                                                              │
│ • D1: Definition Orchestrator (Discovery)                   │
│ • P1: Planning Orchestrator (Planning)                      │
│ • I1: Implementation Orchestrator (Implementation)          │
│ • R1: Review & Test Orchestrator (Review)                   │
│ • O1: Release & Operations Orchestrator (Operations)        │
│ • E1: Evolution Orchestrator (Continuous Improvement)       │
│                                                              │
│ Role: Coordinate phase-specific workflows, delegate to Tier 3│
└───────────────────────┬──────────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
┌───────▼──────────────────────────────────────────────────────┐
│ TIER 3: Execution Agents (77+ agents)                        │
│                                                               │
│ • Sub-Agents (36): Single-purpose research/analysis          │
│   - context-delivery, ac-writer, test-runner, etc.          │
│                                                               │
│ • Specialists (40+): Domain experts                          │
│   - python-implementer, django-tester, react-frontend, etc. │
│                                                               │
│ • Utilities (3): Service agents                              │
│   - evidence-writer, workflow-updater, decision-recorder     │
│                                                               │
│ Role: Execute specific tasks, return results to orchestrators│
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Work Flow Pattern

```
User Request
    ↓
Master Orchestrator (Tier 1)
    ├─ Analyze artifact type
    └─ Route to appropriate Phase Orchestrator
        ↓
Phase Orchestrator (Tier 2)
    ├─ Break down into tasks
    ├─ Delegate to Sub-Agents (Tier 3)
    ├─ Aggregate results
    └─ Validate gate requirements
        ↓
Sub-Agents / Specialists (Tier 3)
    ├─ Execute specific tasks
    ├─ Apply domain expertise
    └─ Return results
        ↓
Phase Orchestrator
    ├─ Check gate criteria
    └─ Return artifact
        ↓
Master Orchestrator
    └─ Route to next phase or user
```

---

## 2. Tier 1: Master Orchestrator

### 2.1 Responsibilities

The Master Orchestrator is the **entry point** for all work requests. It:
1. **Routes by artifact type** (not by content analysis)
2. **Never executes work directly** (pure delegation)
3. **Coordinates phase transitions** (D1→P1→I1→R1→O1→E1)
4. **Validates gate progression** (queries gate-check agents)

### 2.2 Routing Logic

```python
# Conceptual routing algorithm
def route_work(artifact):
    if artifact.type == "request.raw":
        return "definition-orch"  # D1 phase
    elif artifact.type == "workitem.ready":
        return "planning-orch"    # P1 phase
    elif artifact.type == "plan.snapshot":
        return "implementation-orch"  # I1 phase
    elif artifact.type == "build.bundle":
        return "review-test-orch"  # R1 phase
    elif artifact.type == "review.approved":
        return "release-ops-orch"  # O1 phase
    elif artifact.type == "telemetry.snapshot":
        return "evolution-orch"  # E1 phase
```

### 2.3 Artifact Type Mapping

| Incoming Artifact | Phase Orchestrator | Expected Output | Gate |
|-------------------|-------------------|-----------------|------|
| `request.raw` | definition-orch | `workitem.ready` | D1 |
| `workitem.ready` | planning-orch | `plan.snapshot` | P1 |
| `plan.snapshot` | implementation-orch | `build.bundle` | I1 |
| `build.bundle` | review-test-orch | `review.approved` | R1 |
| `review.approved` | release-ops-orch | `release.deployed` | O1 |
| `telemetry.snapshot` | evolution-orch | `evolution.backlog_delta` | E1 |

### 2.4 Prohibited Actions

The Master Orchestrator **NEVER**:
- ❌ Implements code or tests
- ❌ Reads/writes files directly
- ❌ Queries database directly
- ❌ Runs CLI commands
- ❌ Validates gates (delegates to gate-check agents)
- ❌ Skips phases or bypasses orchestrators

**Pattern**: Pure routing and coordination only.

---

## 3. Tier 2: Phase Orchestrators

### 3.1 Overview

Phase orchestrators manage **specific phases** of the AIPM workflow. Each orchestrator:
- **Owns a quality gate** (D1, P1, I1, R1, O1, E1)
- **Delegates to sub-agents** (Tier 3)
- **Aggregates results** into phase artifacts
- **Validates gate criteria** before phase completion

### 3.2 Phase Orchestrator Details

#### 3.2.1 Definition Orchestrator (D1)

**Purpose**: Transform raw requests into well-defined work items

**Gate**: D1 (Discovery)
- business_context ≥50 chars
- acceptance_criteria ≥3
- risks identified (≥1)
- 6W confidence ≥0.70

**Sub-Agents**:
```
intent-triage          → Classify request type
context-assembler      → Gather project context
problem-framer         → Define problem statement
value-articulator      → Document business value
ac-writer              → Generate acceptance criteria
risk-notary            → Identify risks and mitigations
definition-gate-check  → Validate D1 criteria
```

**Input**: `request.raw`
**Output**: `workitem.ready`

**Delegation Pattern**:
```python
# Conceptual flow
def execute_d1_phase(request):
    # Step 1: Triage
    classification = delegate_to("intent-triage", request)

    # Step 2: Gather context
    context = delegate_to("context-assembler", classification)

    # Step 3: Frame problem
    problem = delegate_to("problem-framer", {request, context})

    # Step 4: Articulate value
    value = delegate_to("value-articulator", problem)

    # Step 5: Define criteria
    ac = delegate_to("ac-writer", {problem, value})

    # Step 6: Identify risks
    risks = delegate_to("risk-notary", {problem, context})

    # Step 7: Validate gate
    gate_result = delegate_to("definition-gate-check", {
        problem, value, ac, risks
    })

    if gate_result.passed:
        return create_artifact("workitem.ready", {
            problem, value, ac, risks
        })
    else:
        return escalate_missing_elements(gate_result.missing)
```

#### 3.2.2 Planning Orchestrator (P1)

**Purpose**: Create implementation plans from work items

**Gate**: P1 (Planning)
- Tasks created (≥1 per AC)
- Effort estimates (≤4 hours each)
- Dependencies mapped
- Risk mitigations planned

**Sub-Agents**:
```
decomposer             → Break work into tasks
estimator              → Estimate task effort
dependency-mapper      → Map task dependencies
mitigation-planner     → Plan risk mitigations
backlog-curator        → Organize backlog
planning-gate-check    → Validate P1 criteria
```

**Input**: `workitem.ready`
**Output**: `plan.snapshot`

#### 3.2.3 Implementation Orchestrator (I1)

**Purpose**: Execute implementation tasks

**Gate**: I1 (Implementation)
- Tests updated and passing
- Feature flags added (if needed)
- Documentation updated
- Migrations created (if schema changes)

**Sub-Agents**:
```
pattern-applier        → Apply project patterns
code-implementer       → Write production code
test-implementer       → Write tests
migration-author       → Create migrations
doc-toucher            → Update documentation
implementation-gate-check → Validate I1 criteria
```

**Input**: `plan.snapshot`
**Output**: `build.bundle`

#### 3.2.4 Review & Test Orchestrator (R1)

**Purpose**: Validate quality and functionality

**Gate**: R1 (Review)
- All acceptance criteria verified
- 100% test pass rate
- Coverage ≥90%
- Static analysis clean
- Security checks passed

**Sub-Agents**:
```
static-analyzer        → Run static analysis
test-runner            → Execute test suite
threat-screener        → Security scanning
ac-verifier            → Verify acceptance criteria
quality-gatekeeper     → Aggregate R1 validation
```

**Input**: `build.bundle`
**Output**: `review.approved`

#### 3.2.5 Release & Operations Orchestrator (O1)

**Purpose**: Deploy to production and monitor

**Gate**: O1 (Operations)
- Version bumped
- Changelog updated
- Deployment successful
- Health checks passing
- Monitoring active

**Sub-Agents**:
```
versioner              → Bump version numbers
changelog-curator      → Update changelog
deploy-orchestrator    → Execute deployment
health-verifier        → Validate health checks
operability-gatecheck  → Validate O1 criteria
incident-scribe        → Log deployment events
```

**Input**: `review.approved`
**Output**: `release.deployed`

#### 3.2.6 Evolution Orchestrator (E1)

**Purpose**: Continuous improvement and debt management

**Gate**: E1 (Evolution)
- Telemetry analyzed
- Improvements identified
- Technical debt registered
- Backlog updated

**Sub-Agents**:
```
signal-harvester       → Collect telemetry
insight-synthesizer    → Analyze patterns
debt-registrar         → Track technical debt
refactor-proposer      → Suggest improvements
sunset-planner         → Plan deprecations
evolution-gate-check   → Validate E1 criteria
```

**Input**: `telemetry.snapshot`
**Output**: `evolution.backlog_delta`

### 3.3 Common Patterns

All phase orchestrators follow these patterns:

**1. Delegation Pattern**:
```
Phase Orchestrator receives input
    ↓
Delegates to sub-agents sequentially or in parallel
    ↓
Aggregates results
    ↓
Calls gate-check agent
    ↓
Returns artifact or escalates missing elements
```

**2. Gate Validation Pattern**:
```python
def validate_gate(orchestrator, results):
    # Always delegate to gate-check agent
    gate_agent = f"{orchestrator.phase}-gate-check"
    gate_result = delegate_to(gate_agent, results)

    if not gate_result.passed:
        # Escalate with specific missing elements
        return {
            "status": "BLOCKED",
            "missing": gate_result.missing_elements,
            "recommendation": gate_result.suggested_action
        }

    return {"status": "PASS", "artifact": create_artifact(...)}
```

**3. Error Handling Pattern**:
```python
def execute_phase(orchestrator, input_artifact):
    try:
        # Execute sub-agents
        results = orchestrator.coordinate_sub_agents(input_artifact)

        # Validate gate
        gate_result = orchestrator.validate_gate(results)

        if gate_result.passed:
            return gate_result.artifact
        else:
            # Escalate to Master Orchestrator
            return escalate_to_master(gate_result.missing)

    except Exception as e:
        # Log error and escalate
        log_error(orchestrator, e)
        return escalate_error(e)
```

---

## 4. Tier 3: Execution Agents

### 4.1 Categories

Tier 3 agents perform **actual work**. They are organized into three categories:

#### 4.1.1 Sub-Agents (36 agents)

**Purpose**: Single-purpose research, analysis, and validation

**Characteristics**:
- **Focused scope**: One specific task
- **No dependencies**: Can run in isolation
- **Quick execution**: Typically <2 seconds
- **Idempotent**: Same input → same output

**Examples**:
```
Research & Analysis:
  - context-delivery     → Assemble session context
  - intent-triage        → Classify requests
  - problem-framer       → Define problems
  - value-articulator    → Document value

Creation:
  - ac-writer            → Generate acceptance criteria
  - risk-notary          → Identify risks
  - decomposer           → Break into tasks
  - estimator            → Estimate effort

Validation:
  - definition-gate-check     → Validate D1
  - planning-gate-check       → Validate P1
  - implementation-gate-check → Validate I1
  - quality-gatekeeper        → Validate R1
  - operability-gatecheck     → Validate O1
  - evolution-gate-check      → Validate E1

Execution:
  - test-runner          → Run tests
  - static-analyzer      → Static analysis
  - threat-screener      → Security scanning
  - deploy-orchestrator  → Execute deployments
```

**Total Sub-Agents**: 36

#### 4.1.2 Specialists (40+ agents)

**Purpose**: Domain-specific implementation expertise

**Characteristics**:
- **Technology-specific**: Framework/language expertise
- **Project-selected**: Only relevant specialists generated
- **Deep knowledge**: Patterns, best practices, anti-patterns
- **Context-aware**: Understands project structure

**Examples by Domain**:

**Python Specialists**:
```
- python-implementer        → General Python code
- python-tester             → pytest testing
- python-debugger           → Error analysis
```

**Django Specialists**:
```
- django-backend-implementer → Models, views, serializers
- django-api-integrator      → REST API development
- django-tester              → Django TestCase
```

**React Specialists**:
```
- react-frontend-implementer → Components, hooks
- react-tester               → React Testing Library
```

**Flask Specialists**:
```
- flask-api-implementer      → Routes, blueprints
```

**FastAPI Specialists**:
```
- fastapi-implementer        → Async endpoints, Pydantic
```

**Database Specialists**:
```
- aipm-database-developer    → Schema changes, migrations
```

**Quality Specialists**:
```
- aipm-quality-validator     → Quality gate validation
- aipm-testing-specialist    → Test strategy
```

**Documentation Specialists**:
```
- aipm-documentation-specialist → User guides, API docs
- api-documenter                → OpenAPI/Swagger
```

**Infrastructure Specialists**:
```
- cicd-automator            → CI/CD pipelines
- deployment-specialist     → Cloud deployment
```

**Total Specialists**: 40+ (project-specific selection)

#### 4.1.3 Utilities (3 agents)

**Purpose**: Cross-cutting service agents

**Characteristics**:
- **Stateless**: No internal state
- **Service-oriented**: Used by multiple orchestrators
- **Database-focused**: CRUD operations

**Examples**:
```
- evidence-writer      → Write evidence entries
- workflow-updater     → Update workflow state
- decision-recorder    → Log ADRs
```

**Total Utilities**: 3

### 4.2 Agent Selection Algorithm

Not all 77+ Tier 3 agents are generated for every project. The system uses **intelligent selection** based on project characteristics.

**Selection Criteria**:
1. **Universal Agents** (always included):
   - context-delivery, ac-writer, test-runner, quality-gatekeeper (sub-agents)
   - All utilities

2. **Language-Specific**:
   - Python detected → python-implementer, python-tester, python-debugger
   - TypeScript detected → typescript-implementer, typescript-tester

3. **Framework-Specific**:
   - Django detected → django-backend-implementer, django-api-integrator, django-tester
   - React detected → react-frontend-implementer, react-tester

4. **Project Type**:
   - Web/API → api-documenter
   - Mobile → mobile-tester

5. **Infrastructure**:
   - CI/CD detected → cicd-automator, deployment-specialist

**Example** (Django + React project):
```python
# Detected: Python, TypeScript, Django, React, PostgreSQL
# Generated: 13 agents

Universal:
  - context-delivery, ac-writer, test-runner, quality-gatekeeper

Python:
  - python-implementer, python-tester, python-debugger

TypeScript:
  - typescript-implementer, typescript-tester

Django:
  - django-backend-implementer, django-api-integrator, django-tester

React:
  - react-frontend-implementer, react-tester

API:
  - api-documenter

# Total: 15 agents (not all 77+)
```

**Code Reference**: `agentpm/core/agents/selection.py`

---

## 5. Communication Protocols

### 5.1 Delegation Contract

All agent communication follows a **standardized contract**:

```python
@dataclass
class AgentRequest:
    """Request sent to an agent"""
    requesting_agent: str      # Who is asking
    input_artifact: dict       # Input data
    context: dict             # Additional context
    expected_output: str      # Output artifact type

@dataclass
class AgentResponse:
    """Response from an agent"""
    responding_agent: str     # Who responded
    output_artifact: dict     # Result data
    status: str               # SUCCESS | FAILURE | BLOCKED
    metadata: dict            # Execution metadata (time, errors, etc.)
```

### 5.2 Master → Phase Orchestrator

```python
# Example: Master delegates to Definition Orchestrator
request = AgentRequest(
    requesting_agent="master-orchestrator",
    input_artifact={
        "type": "request.raw",
        "content": "User wants feature X"
    },
    context={
        "project_id": 42,
        "tech_stack": ["Python", "Django"]
    },
    expected_output="workitem.ready"
)

response = definition_orch.execute(request)
# response.output_artifact = {
#     "type": "workitem.ready",
#     "problem": "...",
#     "value": "...",
#     "acceptance_criteria": [...],
#     "risks": [...]
# }
```

### 5.3 Phase Orchestrator → Sub-Agent

```python
# Example: Definition Orch delegates to AC Writer
request = AgentRequest(
    requesting_agent="definition-orch",
    input_artifact={
        "problem": "Add user authentication",
        "value": "Secure user data"
    },
    context={
        "project_id": 42,
        "existing_ac": []
    },
    expected_output="acceptance_criteria"
)

response = ac_writer.execute(request)
# response.output_artifact = {
#     "acceptance_criteria": [
#         "Users can register with email/password",
#         "Passwords are hashed with bcrypt",
#         "Users can log in and receive JWT token"
#     ]
# }
```

### 5.4 Error Handling Protocol

```python
# If sub-agent fails
response = AgentResponse(
    responding_agent="ac-writer",
    output_artifact={},
    status="FAILURE",
    metadata={
        "error": "Insufficient context",
        "missing": ["user_stories", "requirements"],
        "suggestion": "Run discovery phase first"
    }
)

# Phase orchestrator escalates to Master
escalation = {
    "phase": "D1_DISCOVERY",
    "blocker": "Insufficient context for AC generation",
    "required_action": "USER_INPUT_NEEDED",
    "details": response.metadata
}
```

---

## 6. Database-Driven Architecture

### 6.1 Agent Storage

All agents are stored in the `agents` table:

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    role TEXT UNIQUE,               -- e.g., "definition-orch"
    display_name TEXT,              -- "Definition Orchestrator"
    description TEXT,
    agent_type TEXT,                -- orchestrator, specialist, utility, sub-agent
    tier INTEGER,                   -- 1, 2, or 3
    capabilities TEXT,              -- JSON array
    sop_content TEXT,               -- Markdown SOP
    file_path TEXT,                 -- Generated .md file path
    generated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

**Key Principles**:
- **Database = Source of Truth**: Agent metadata lives in database
- **Files = Artifacts**: `.claude/agents/*.md` files generated from database
- **Regenerable**: Files can be deleted and regenerated anytime
- **Provider-Agnostic**: Same database → multiple provider formats

### 6.2 Generation Workflow

```
Database (agents table)
    ↓
AgentGenerator (provider-specific)
    ↓
Template Rendering (Jinja2)
    ↓
File Output (.claude/agents/*.md)
```

**Example**:
```bash
# Generate all agents from database
apm agents generate --all

# Output:
# ✅ Generated: .claude/agents/master-orchestrator.md
# ✅ Generated: .claude/agents/orchestrators/definition-orch.md
# ✅ Generated: .claude/agents/orchestrators/planning-orch.md
# ... (all agents)
```

### 6.3 Multi-Provider Support

```
Database (Single Source)
    ↓
    ├─ ClaudeCodeGenerator → .claude/agents/*.md (Markdown)
    ├─ GeminiGenerator → .gemini/agents/*.xml (XML)
    └─ CursorGenerator → .cursor/agents/*.json (JSON)
```

---

## 7. Practical Examples

### 7.1 Complete Feature Workflow

**Scenario**: Implement "Add user authentication"

**Step 1: User Request**
```bash
apm work-item create "Add user authentication" --type=feature
# Creates work item #123 in PROPOSED state
```

**Step 2: D1 Phase (Definition Orchestrator)**
```
Master Orchestrator receives "request.raw"
    ↓
Routes to definition-orch
    ↓
definition-orch:
    1. Delegates to intent-triage
       → Returns: {type: FEATURE, domain: SECURITY, complexity: MEDIUM}

    2. Delegates to context-assembler
       → Returns: {tech_stack: [Django], auth_method: JWT, database: PostgreSQL}

    3. Delegates to problem-framer
       → Returns: {problem: "Users need secure authentication mechanism"}

    4. Delegates to value-articulator
       → Returns: {value: "Protect user data, comply with security standards"}

    5. Delegates to ac-writer
       → Returns: {
           AC1: "Users can register with email/password",
           AC2: "Passwords hashed with bcrypt",
           AC3: "Login returns JWT token"
         }

    6. Delegates to risk-notary
       → Returns: {
           R1: "Password storage vulnerability (HIGH)",
           mitigation: "Use Django's auth system"
         }

    7. Delegates to definition-gate-check
       → Returns: {passed: true, confidence: 0.85}

    8. Creates artifact: "workitem.ready"
```

**Step 3: P1 Phase (Planning Orchestrator)**
```
Master Orchestrator receives "workitem.ready"
    ↓
Routes to planning-orch
    ↓
planning-orch:
    1. Delegates to decomposer
       → Returns: [
           Task 1: "Add User model with auth fields",
           Task 2: "Implement registration endpoint",
           Task 3: "Implement login endpoint",
           Task 4: "Add JWT token generation",
           Task 5: "Write authentication tests"
         ]

    2. Delegates to estimator
       → Returns: {T1: 2h, T2: 3h, T3: 2h, T4: 2h, T5: 3h}

    3. Delegates to dependency-mapper
       → Returns: {
           T2 depends_on T1,
           T3 depends_on T1,
           T4 depends_on T3,
           T5 depends_on [T2, T3, T4]
         }

    4. Creates artifact: "plan.snapshot"
```

**Step 4: I1 Phase (Implementation Orchestrator)**
```
Master Orchestrator receives "plan.snapshot"
    ↓
Routes to implementation-orch
    ↓
implementation-orch:
    For each task:
        1. Delegates to pattern-applier
           → Returns: {pattern: "Django auth patterns", examples: [...]}

        2. Delegates to code-implementer (specialist)
           → Selects: django-backend-implementer
           → Implements: User model, views, serializers

        3. Delegates to test-implementer (specialist)
           → Selects: django-tester
           → Writes: TestCase classes

        4. Delegates to migration-author
           → Creates: 0001_add_user_model.py

        5. Delegates to doc-toucher
           → Updates: API documentation

    6. Delegates to implementation-gate-check
       → Returns: {passed: true}

    7. Creates artifact: "build.bundle"
```

**Step 5: R1 Phase (Review & Test Orchestrator)**
```
Master Orchestrator receives "build.bundle"
    ↓
Routes to review-test-orch
    ↓
review-test-orch:
    1. Delegates to test-runner
       → Runs: pytest tests/
       → Returns: {passed: 15, failed: 0, coverage: 94%}

    2. Delegates to static-analyzer
       → Runs: flake8, mypy, black
       → Returns: {issues: 0}

    3. Delegates to threat-screener
       → Runs: bandit, safety
       → Returns: {vulnerabilities: 0}

    4. Delegates to ac-verifier
       → Validates: All 3 acceptance criteria met
       → Returns: {AC1: ✅, AC2: ✅, AC3: ✅}

    5. Delegates to quality-gatekeeper
       → Aggregates all results
       → Returns: {passed: true, score: 98}

    6. Creates artifact: "review.approved"
```

**Step 6: O1 Phase (Release & Operations Orchestrator)**
```
Master Orchestrator receives "review.approved"
    ↓
Routes to release-ops-orch
    ↓
release-ops-orch:
    1. Delegates to versioner
       → Bumps: 1.2.3 → 1.3.0

    2. Delegates to changelog-curator
       → Adds: "Added user authentication with JWT"

    3. Delegates to deploy-orchestrator
       → Deploys to production

    4. Delegates to health-verifier
       → Checks: /health endpoint
       → Returns: {status: healthy, response_time: 45ms}

    5. Creates artifact: "release.deployed"
```

**Complete Workflow Time**: ~30 minutes (automated)

### 7.2 Blocked Workflow Example

**Scenario**: Missing context causes D1 gate failure

```
definition-orch attempts D1 phase
    ↓
Delegates to ac-writer
    ↓
ac-writer returns: {
    status: "BLOCKED",
    missing: ["user_stories", "security_requirements"],
    confidence: 0.45  # Below 0.70 threshold
}
    ↓
definition-gate-check returns: {
    passed: false,
    missing_elements: [
        "business_context insufficient",
        "acceptance_criteria incomplete (1 of 3 minimum)",
        "confidence too low (0.45 < 0.70)"
    ]
}
    ↓
definition-orch escalates to Master Orchestrator
    ↓
Master Orchestrator returns to user:
    "❌ D1 gate blocked. Required actions:
     1. Provide user stories for authentication feature
     2. Document security requirements
     3. Answer discovery questions (sent to email)"
```

---

## 8. Performance Characteristics

### 8.1 Benchmarks

| Metric | Target | Actual (Measured) |
|--------|--------|-------------------|
| Master routing decision | <50ms | 12ms |
| Phase orchestrator setup | <100ms | 45ms |
| Sub-agent execution | <2s | 0.5-1.8s |
| Full D1 phase | <30s | 18-25s |
| Full workflow (D1-O1) | <5 minutes | 3-4 minutes |

### 8.2 Scalability

**Parallel Execution**:
- Sub-agents within a phase can run in parallel
- Example: D1 phase runs 6 sub-agents → 6s sequential, 2s parallel

**Resource Usage**:
- Memory per agent: ~10-50MB
- Disk per agent file: ~2-4KB
- Database per agent record: ~1KB

---

## 9. File Locations

### 9.1 Agent Files

```
.claude/agents/
├── master-orchestrator.md              # Tier 1 (1 file)
├── orchestrators/                       # Tier 2 (6 files)
│   ├── definition-orch.md
│   ├── planning-orch.md
│   ├── implementation-orch.md
│   ├── review-test-orch.md
│   ├── release-ops-orch.md
│   └── evolution-orch.md
├── sub-agents/                          # Tier 3: Sub-agents (36 files)
│   ├── context-delivery.md
│   ├── ac-writer.md
│   ├── test-runner.md
│   └── ... (33 more)
├── specialists/                         # Tier 3: Specialists (project-specific, 5-40 files)
│   ├── python-implementer.md
│   ├── django-backend-implementer.md
│   ├── react-frontend-implementer.md
│   └── ...
└── utilities/                           # Tier 3: Utilities (3 files)
    ├── evidence-writer.md
    ├── workflow-updater.md
    └── decision-recorder.md
```

### 9.2 Code Locations

```
agentpm/
├── core/
│   ├── agents/
│   │   ├── generator.py           # Agent generation logic
│   │   ├── selection.py           # Intelligent agent selection
│   │   └── templates/             # Base agent templates
│   ├── database/
│   │   ├── models/agent.py        # Agent model
│   │   └── methods/agents.py      # Agent CRUD
│   └── workflow/
│       ├── service.py             # Workflow coordination
│       └── phase_progression_service.py  # Phase transitions
├── providers/
│   ├── base.py                    # Provider interface
│   └── generators/
│       └── anthropic/
│           └── claude_code_generator.py  # Claude Code agent generation
└── cli/
    └── commands/
        └── agents/                # Agent CLI commands
```

---

## 10. Design Rationale

### 10.1 Why Three Tiers?

**Alternative Considered**: Flat structure (all agents equal)

**Rejected Because**:
- ❌ No clear coordination point
- ❌ Difficult to enforce phase gates
- ❌ Agents would need complex peer-to-peer communication
- ❌ Hard to trace decision flow

**Three-Tier Benefits**:
- ✅ Clear responsibility hierarchy
- ✅ Simple delegation model (always downward)
- ✅ Phase gates enforced at orchestrator level
- ✅ Easy to understand and debug

### 10.2 Why Phase-Based Orchestrators?

**Alternative Considered**: Capability-based orchestrators (e.g., CodeOrch, TestOrch, DocOrch)

**Rejected Because**:
- ❌ Doesn't align with AIPM workflow phases
- ❌ Hard to map to quality gates
- ❌ Cross-cutting concerns unclear
- ❌ Difficult to sequence work

**Phase-Based Benefits**:
- ✅ Aligns with AIPM's D1-P1-I1-R1-O1-E1 workflow
- ✅ Natural gate validation points
- ✅ Clear phase progression
- ✅ Familiar to users (matches `apm` CLI commands)

### 10.3 Why Database-Driven?

**Alternative Considered**: File-based definitions

**Rejected Because**:
- ❌ No runtime state tracking
- ❌ Difficult to query agent metadata
- ❌ Provider-specific formats mixed with definitions
- ❌ Hard to implement multi-provider support

**Database-Driven Benefits**:
- ✅ Single source of truth
- ✅ Runtime state (active, last_used, performance metrics)
- ✅ Easy querying (e.g., "Which agents handle Django?")
- ✅ Provider-agnostic core

---

## 11. Related Documentation

- **[Agent Selection Algorithm](agent-selection.md)**: How agents are intelligently selected per project
- **[Generation Pipeline](generation-pipeline.md)**: How agents are generated from templates
- **[Provider Generators](provider-generators.md)**: Multi-LLM provider support
- **[Implementation Guide](../guides/implementation-guide.md)**: Step-by-step agent development

---

## 12. Version History

- **v2.0** (2025-10-19): Three-tier architecture, database-driven, 84 agents
- **v1.5** (2025-10-15): Added E1 phase orchestrator
- **v1.0** (2025-10-12): Initial three-tier architecture with D1-O1 phases

---

**Maintained by**: AIPM Core Team
**License**: Proprietary
