---
version: "1.0"
architecture: flat
generated: 2025-10-27T13:20:11.003648Z
project:
  id: 1
  name: "Agent PM"
  tech_stack: []
---

# APM Agent System

**Project**: Agent PM
**Total Active Agents**: 85
**Active Rules**: 76
**Generated**: 2025-10-27 13:20:11 UTC

---

## Subagent Directory (Flat - Organized by Function)

### Planning & Analysis (21)

- **backend-architect**: Backend Architect - SOP for Backend Architect agent
- **core-designer**: Core Designer - SOP for Core Designer agent
- **definition-gate-check**: Definition Gate Check - Use when you need to validate if a work item passes the D1 quality gate
- **definition-orch**: Definition Orch - Use when you have a raw request that needs to be transformed into a well-defined work item with acceptance criteria and risks
- **deploy-orchestrator**: Deploy Orchestrator - Use when you need to execute deployment to production
- **devops-architect**: Devops Architect - SOP for Devops Architect agent
- **discovery-orch**: Discovery Orch - Discovery Orchestrator - Coordinates external/internal/risk discovery when confidence < threshold
- **evolution-orch**: Evolution Orch - Use when you have production telemetry that needs analysis to identify improvements, technical debt, or new opportunities
- **flask-ux-designer**: Flask Ux Designer - Create professional, accessible Flask web application UI/UX designs with Bootstrap 5, HTMX, Alpine.js, and Chart.js. Specializes in interactive compon...
- **frontend-architect**: Frontend Architect - SOP for Frontend Architect agent
- **implementation-orch**: Implementation Orch - Use when you have a plan with time-boxed tasks that need to be executed into working code, tests-BAK, and documentation
- **master-orchestrator**: Master Orchestrator - Use when user provides any request - routes to appropriate mini-orchestrator based on artifact type, never executes work directly
- **mitigation-planner**: Mitigation Planner - Use when you need to create concrete plans for addressing identified risks
- **planner**: Planner - Task breakdown and estimation specialist in this project
- **planning-gate-check**: Planning Gate Check - Use when you need to validate if a plan passes the P1 quality gate
- **planning-orch**: Planning Orch - Use when you have a well-defined work item that needs to be decomposed into time-boxed tasks with estimates and dependencies
- **problem-framer**: Problem Framer - Use when you need to transform a vague request into a clear, scoped problem statement
- **release-ops-orch**: Release Ops Orch - Use when you have quality-approved code that needs to be versioned, deployed, and monitored in production
- **review-test-orch**: Review Test Orch - Use when you have implemented code that needs quality validation - runs tests-BAK, static analysis, security checks, and AC verification
- **sunset-planner**: Sunset Planner - Use when you need to plan deprecation of features or technical approaches
- **system-architect**: System Architect - SOP for System Architect agent

### Implementation (10)

- **agent-builder**: Agent System Architect - Creates new agents from specifications, generates agent files for multiple LLM providers, and maintains agent architecture consistency. Ensures all ag...
- **aipm-database-schema-explorer**: Aipm Database Schema Explorer - SOP for Aipm Database Schema Explorer agent
- **code-implementer**: Code Implementer - Use when you need to write production code following project patterns
- **database-query-agent**: Database Operations Specialist - Executes safe, efficient database queries with proper error handling and transaction management. Generates SQL from natural language queries and valid...
- **migration-author**: Migration Author - Use when database schema changes are needed - creates migration files with upgrade/downgrade paths
- **performance-engineer**: Performance Engineer - SOP for Performance Engineer agent
- **python-expert**: Python Expert - SOP for Python Expert agent
- **quality-engineer**: Quality Engineer - SOP for Quality Engineer agent
- **security-engineer**: Security Engineer - SOP for Security Engineer agent
- **test-implementer**: Test Implementer - Use when you need to write comprehensive tests-BAK for implemented code

### Testing & Quality (16)

- **ac-verifier**: Ac Verifier - Use when you need to verify that all acceptance criteria are met
- **aipm-documentation-analyzer**: Aipm Documentation Analyzer - SOP for Aipm Documentation Analyzer agent
- **aipm-plugin-system-analyzer**: Aipm Plugin System Analyzer - SOP for Aipm Plugin System Analyzer agent
- **aipm-rules-compliance-checker**: Aipm Rules Compliance Checker - SOP for Aipm Rules Compliance Checker agent
- **aipm-test-pattern-analyzer**: Aipm Test Pattern Analyzer - SOP for Aipm Test Pattern Analyzer agent
- **aipm-workflow-analyzer**: Aipm Workflow Analyzer - SOP for Aipm Workflow Analyzer agent
- **code-analyzer**: Code Analyzer - SOP for Code Analyzer agent
- **evolution-gate-check**: Evolution Gate Check - Use when you need to validate if evolution analysis passes the E1 quality gate
- **health-verifier**: Health Verifier - Use when you need to verify system health after deployment
- **implementation-gate-check**: Implementation Gate Check - Use when you need to validate if implementation passes the I1 quality gate
- **operability-gatecheck**: Operability Gatecheck - Use when you need to validate if deployment passes the O1 quality gate
- **quality-gatekeeper**: Quality Gatekeeper - Use when you need to validate if implementation passes the R1 quality gate
- **reviewer**: Reviewer - Code review and quality assurance specialist in this project
- **static-analyzer**: Static Analyzer - Use when you need to run linters, type checkers, and code quality tools
- **test-runner**: Test Runner - Use when you need to execute test suites and report coverage
- **wi-perpetual-reviewer**: Work Item Perpetual Reviewer - Prevents false work item completions by validating all ACs, tasks, and quality gates before marking done

### Documentation (6)

- **ac-writer**: Ac Writer - Use when you need to generate testable acceptance criteria for a work item
- **backlog-curator**: Backlog Curator - Use when you need to create tasks in the database with proper metadata and links
- **changelog-curator**: Changelog Curator - Use when you need to update the changelog with release notes
- **doc-toucher**: Doc Toucher - Use when documentation needs to be updated to reflect code changes
- **evidence-writer**: Evidence Writer - Records evidence sources and research findings to database
- **technical-writer**: Technical Writer - SOP for Technical Writer agent

### Utilities (32)

- **aipm-codebase-navigator**: Aipm Codebase Navigator - SOP for Aipm Codebase Navigator agent
- **audit-logger**: Audit Logger - Logs decisions, architectural choices, and rationale for audit trail
- **business-panel-experts**: Business Panel Experts - SOP for Business Panel Experts agent
- **context-assembler**: Context Assembler - Use when you need to gather relevant project context from the database and codebase
- **context-delivery**: Context Delivery - Context Agent - Assembles session context from database (MANDATORY at session start)
- **context-generator**: Context Assembly Specialist - Assembles comprehensive session context from database records, project files, and plugin intelligence. Calculates context confidence and identifies ga...
- **debt-registrar**: Debt Registrar - Use when you need to document and prioritize technical debt
- **decomposer**: Decomposer - Use when you need to break a work item into atomic, time-boxed tasks
- **deep-research-agent**: Deep Research Agent - SOP for Deep Research Agent agent
- **dependency-mapper**: Dependency Mapper - Use when you need to identify task dependencies and critical paths
- **estimator**: Estimator - Use when you need to provide effort estimates for tasks
- **file-operations-agent**: File System Operations Specialist - Performs safe file system operations with proper error handling, atomic operations, and backup capabilities. Handles file creation, reading, updating,...
- **incident-scribe**: Incident Scribe - Use when deployment fails or incidents occur - documents for post-mortem
- **information-gatherer**: Information Gatherer - SOP for Information Gatherer agent
- **insight-synthesizer**: Insight Synthesizer - Use when you need to identify patterns and opportunities from telemetry data
- **intent-triage**: Intent Triage - Use when you need to classify a raw request by type, domain, complexity, and priority
- **learning-guide**: Learning Guide - SOP for Learning Guide agent
- **pattern-applier**: Pattern Applier - Use when you need to identify which project patterns to apply for consistent implementation
- **refactor-proposer**: Refactor Proposer - Use when you need to propose improvements based on insights and debt analysis
- **refactoring-expert**: Refactoring Expert - SOP for Refactoring Expert agent
- **requirements-analyst**: Requirements Analyst - SOP for Requirements Analyst agent
- **risk-notary**: Risk Notary - Use when you need to identify risks, dependencies, and constraints for a work item
- **root-cause-analyst**: Root Cause Analyst - SOP for Root Cause Analyst agent
- **shopify-metafield-admin-dev**: Shopify Metafield Admin Dev - SOP for Shopify Metafield Admin Dev agent
- **signal-harvester**: Signal Harvester - Use when you need to collect production telemetry and user feedback signals
- **socratic-mentor**: Socratic Mentor - SOP for Socratic Mentor agent
- **specifier**: Specifier - Requirements specification specialist for the detected technology stack in this project
- **threat-screener**: Threat Screener - Use when you need to scan for security vulnerabilities
- **value-articulator**: Value Articulator - Use when you need to document why work matters and what business value it provides
- **versioner**: Versioner - Use when you need to increment version numbers according to semver rules
- **workflow-coordinator**: State Machine Orchestrator - Manages workflow state transitions for tasks and work items. Validates transitions against state machine rules, enforces gate requirements, and mainta...
- **workflow-updater**: Workflow Updater - Updates work item and task status in database via CLI commands

## Development Standards

### Code Quality

- **CQ-001** (GUIDE): Language-specific naming (snake_case, camelCase)
- **CQ-002** (GUIDE): Names describe purpose
- **CQ-003** (GUIDE): Avoid cryptic abbreviations
- **CQ-004** (GUIDE): Booleans: is_/has_/can_
- **CQ-005** (GUIDE): Classes are nouns
- **CQ-006** (GUIDE): Functions are verbs
- **CQ-007** (GUIDE): Constants in UPPER_SNAKE_CASE
- **CQ-008** (GUIDE): Private methods start with _
- **CQ-009** (LIMIT): Names ≤50 characters
- **CQ-010** (GUIDE): No single-letter names (except i, j, k in loops)
- **CQ-011** (GUIDE): One class per file (Java/TS style)
- **CQ-012** (GUIDE): Proper __init__.py exports (Python)
- **CQ-013** (GUIDE): Tests in tests-BAK/ directory
- **CQ-014** (LIMIT): Max 20 imports per file
- **CQ-015** (GUIDE): No circular imports
- **CQ-016** (GUIDE): Explicit __all__ in modules
- **CQ-017** (GUIDE): Domain-based directories (not by type)
- **CQ-018** (GUIDE): Config in dedicated files
- **CQ-019** (GUIDE): Remove unused imports

### Development Principles

- **DP-001** (BLOCK): IMPLEMENTATION tasks ≤4h
- **DP-002** (BLOCK): TESTING tasks ≤6h
- **DP-003** (BLOCK): DESIGN tasks ≤8h
- **DP-004** (BLOCK): DOCUMENTATION tasks ≤4h
- **DP-005** (BLOCK): DEPLOYMENT tasks ≤2h
- **DP-006** (BLOCK): ANALYSIS tasks ≤8h
- **DP-007** (BLOCK): RESEARCH tasks ≤12h
- **DP-008** (BLOCK): REFACTORING tasks ≤6h
- **DP-009** (BLOCK): BUGFIX tasks ≤4h
- **DP-010** (BLOCK): HOTFIX tasks ≤2h
- **DP-011** (BLOCK): PLANNING tasks ≤8h
- **DP-030** (GUIDE): No Dict[str, Any] in public APIs
- **DP-036** (BLOCK): No secrets in code
- **DP-046** (GUIDE): API responses <200ms (p95)

### Documentation Principles

- **DOC-020** (BLOCK): All document creation MUST use 'apm document add' command. Agents PROHIBITED from creating documentation files directly using Write, Edit, or Bash tools.

### Documentation Standards

- **DOC-001** (GUIDE): Every module has docstring
- **DOC-002** (GUIDE): Every public class has docstring
- **DOC-003** (GUIDE): Every public function has docstring
- **DOC-004** (GUIDE): Document all parameters
- **DOC-005** (GUIDE): Document return values
- **DOC-006** (GUIDE): Document raised exceptions
- **DOC-007** (GUIDE): Include usage examples
- **DOC-008** (ENHANCE): Use Google-style docstrings (Python)
- **DOC-009** (ENHANCE): Use JSDoc (JavaScript/TypeScript)
- **DOC-010** (GUIDE): Complex code needs explanation
- **DOC-011** (LIMIT): README.md at project root
- **DOC-012** (GUIDE): Setup instructions in README
- **DOC-013** (GUIDE): API endpoints documented
- **DOC-014** (GUIDE): Architecture documented
- **DOC-015** (GUIDE): CHANGELOG.md updated
- **DOC-016** (GUIDE): CONTRIBUTING.md for open source
- **DOC-017** (GUIDE): ADRs for significant decisions
- **DOC-018** (GUIDE): Deployment instructions
- **DOC-019** (GUIDE): Common issues documented

### Testing Standards

- **TEST-002** (LIMIT): Unit tests-BAK for all logic
- **TEST-003** (LIMIT): Integration tests-BAK for APIs
- **TEST-004** (GUIDE): E2E for critical user flows
- **TEST-005** (GUIDE): Test suite <5min
- **TEST-006** (GUIDE): Tests run in parallel
- **TEST-007** (GUIDE): No flaky tests-BAK allowed
- **TEST-008** (GUIDE): Use fixtures/factories for test data
- **TEST-009** (GUIDE): Tests clean up after themselves
- **TEST-021** (BLOCK): Critical paths coverage requirement
- **TEST-022** (BLOCK): User-facing code coverage requirement
- **TEST-023** (BLOCK): Data layer coverage requirement
- **TEST-024** (BLOCK): Security code coverage requirement
- **TEST-025** (GUIDE): Utilities code coverage requirement
- **TEST-026** (GUIDE): Framework integration coverage requirement

### Workflow Rules

- **WR-001** (BLOCK): Work items validated before tasks start
- **WR-002** (BLOCK): FEATURE needs DESIGN+IMPL+TEST+DOC
- **WR-003** (BLOCK): BUGFIX needs ANALYSIS+FIX+TEST
- **WR-004** (GUIDE): Code review required
- **WR-005** (ENHANCE): Documents TDD/BDD/DDD
- **WR-006** (GUIDE): Tests before implementation (TDD)
- **WR-007** (LIMIT): Deployment tasks for releases
- **WR-008** (BLOCK): REFACTORING needs ANALYSIS+IMPL+TEST
- **WR-009** (BLOCK): RESEARCH needs ANALYSIS+DOC

## Current Work Context

### Active Work Item: #157

**Name**: Frictionless Installation & Setup Experience  
**Type**: feature  
**Status**: active  
**Priority**: 1  

## Provider-Specific Instructions

<!-- [CLAUDE_CODE] -->
### Claude Code

Use the Task tool for all subagent delegation:

```python
Task(
  subagent_type="agent-role",  # From directory above
  description="Brief task summary",
  prompt="Detailed instructions for the agent"
)
```

**Example**:
```python
Task(
  subagent_type="aipm-python-cli-developer",
  description="Implement CLI command",
  prompt="Create `apm context show` command that displays current work context"
)
```
<!-- [/CLAUDE_CODE] -->

<!-- [CURSOR] -->
### Cursor

Cursor does not support subagent delegation. Use the agent directory as a reference for expert personas and capabilities. When implementing tasks, adopt the role and follow the SOP of the most relevant agent.
<!-- [/CURSOR] -->

<!-- [CODEX] -->
### OpenAI Codex

Use the `codex` CLI for subagent orchestration:

```bash
codex --yolo exec "Invoke agent: agent-role
Task: [description]
Instructions: [detailed prompt]"
```

**Example**:
```bash
codex --yolo exec "Invoke agent: aipm-testing-specialist
Task: Create test suite
Instructions: Generate comprehensive unit tests for WorkItem model"
```
<!-- [/CODEX] -->

<!-- [GEMINI] -->
### Google Gemini

Use natural language delegation with explicit agent reference:

```
Delegate to [agent-role]:
[Detailed instructions]
```

The system will route your request to the appropriate agent based on the role reference and task description.
<!-- [/GEMINI] -->

