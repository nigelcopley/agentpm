# APM (Agent Project Manager): Universal Context Persistence & Orchestration Platform
## Complete System Specification

**Version:** 2.0.0
**Date:** 2025-10-12
**Status:** Strategic Specification
**Scope:** Enterprise-scale AI-assisted software development

---

## Executive Summary

### Vision
APM (Agent Project Manager) is the **universal context persistence and orchestration platform** for AI-assisted development of complex, enterprise-scale software systems. It enables multiple AI agents (Claude, Codex, Gemini, Cursor, etc.) to collaboratively build and maintain sophisticated applications while preserving full audit trails, decision context, and architectural knowledge across sessions, agents, and time.

### Core Problem
Building complex systems (multi-tenant SaaS platforms, enterprise applications, large-scale architectures) with AI assistance fails because:

1. **Context Loss**: AI agents lose critical context between sessions
2. **No Coordination**: Multiple agents can't share knowledge or coordinate work
3. **No Audit Trail**: Decisions, patterns, and architectural choices disappear
4. **Scale Limits**: Simple projects work, complex projects fail at token limits
5. **Provider Lock-in**: Solutions tied to specific AI providers (Claude, Cursor, etc.)

### Solution Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    APM (Agent Project Manager) Platform                          │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │   Provider     │  │   Provider     │  │   Provider    │ │
│  │   Adapters     │  │   Adapters     │  │   Adapters    │ │
│  │                │  │                │  │               │ │
│  │  Claude Code   │  │    Cursor      │  │    Codex      │ │
│  │  Gemini        │  │    Aider       │  │   Custom      │ │
│  └────────┬───────┘  └────────┬───────┘  └───────┬───────┘ │
│           │                   │                   │          │
│  ┌────────┴───────────────────┴───────────────────┴───────┐ │
│  │         Universal Context & Orchestration Core         │ │
│  │                                                         │ │
│  │  • Context Persistence (hierarchical, versioned)       │ │
│  │  • Agent Orchestration (sub-agent delegation)          │ │
│  │  • Work Management (projects → work items → tasks)     │ │
│  │  • Decision Tracking (ADRs, patterns, constraints)     │ │
│  │  • Document Store (fast search, duplicate detection)   │ │
│  │  • Quality Gates (automated validation & compliance)   │ │
│  │  • Session Management (lifecycle, hooks, events)       │ │
│  │  • Evidence Tracking (sources, confidence, lineage)    │ │
│  │  • Audit System (who, what, when, why, how)           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                             │                                │
│  ┌──────────────────────────┴─────────────────────────────┐ │
│  │              Database & Storage Layer                   │ │
│  │                                                         │ │
│  │  • SQLite/PostgreSQL (structured data)                 │ │
│  │  • Document Store (artifacts, decisions, evidence)     │ │
│  │  • Version Control Integration (git, commits)          │ │
│  │  • Plugin System (framework detection, intelligence)   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Differentiators

1. **Provider-Agnostic**: Works with any AI coding assistant
2. **Enterprise-Scale**: Designed for complex, multi-year projects
3. **Context Compression**: 10x context capacity through sub-agent delegation
4. **Full Auditability**: Complete decision trail for compliance/review
5. **Multi-Agent Coordination**: Enables specialized agents to collaborate
6. **Continuous Learning**: System gets smarter with every session

---

## Use Case: Complex System Development

### Example Project
**Multi-Tenant E-Commerce Platform**

**Requirements:**
- Multi-tenant architecture (isolated data, custom domains)
- Django backend with REST API
- React/Next.js SPA admin panels (per tenant)
- Multiple rendering options: Django templates, JSON API, GraphQL
- Plugin system: CMS, CRM, E-commerce, Marketing modules
- Subscription management (per-tenant app access)
- Multi-domain support with custom DNS
- Enterprise-grade: audit logs, RBAC, data isolation

**Complexity:**
- ~150,000+ lines of code
- 50+ database models
- 200+ API endpoints
- 30+ React components
- 15+ background jobs
- Multiple deployment configurations
- Extensive test coverage
- Comprehensive documentation

### How AIPM Enables This

#### Phase 1: Architecture & Planning (Weeks 1-2)
```yaml
Work Item: "Multi-Tenant Platform Architecture"
Type: RESEARCH
Tasks:
  - Database isolation strategy analysis (8h)
  - Multi-tenancy pattern selection (6h)
  - Subdomain routing architecture (4h)
  - Plugin system design (8h)

AI Agents Involved:
  - aipm-requirements-specifier (research, analysis)
  - aipm-database-developer (schema design)
  - aipm-development-orchestrator (architecture decisions)

AIPM Captures:
  - Decision: "Schema-based isolation over database-per-tenant"
  - Rationale: "Balance complexity vs. cost, 10K+ tenant scale"
  - Pattern: "Tenant context via middleware, row-level security"
  - Evidence: Research from Wagtail, Django-tenants, Mezzanine
  - Documents Created:
    • ADR: Multi-Tenancy Strategy (docs/adrs/ADR-001-multi-tenancy.md)
    • Spec: Database Isolation Design (docs/specs/db-isolation.md)
    • Guide: Multi-Tenancy Implementation (docs/guides/multi-tenancy.md)
  - Document Search: Prevents duplicate architecture docs
```

#### Phase 2: Core Infrastructure (Weeks 3-6)
```yaml
Work Item: "Tenant Management Infrastructure"
Type: FEATURE
Tasks:
  - Tenant model & middleware (4h)
  - Domain routing system (4h)
  - Tenant-aware database queries (4h)
  - Tenant admin interface (4h)
  - Integration tests-BAK (6h)

AI Agents Involved:
  - aipm-python-cli-developer (implementation)
  - aipm-database-developer (schema, migrations)
  - aipm-testing-specialist (test coverage)

AIPM Tracks:
  - Implementation decisions (middleware vs. decorators)
  - Code patterns (TenantMixin, tenant_context manager)
  - Quality gates (>90% test coverage, security review)
  - Cross-cutting concerns (logging, monitoring, caching)
  - Documents Referenced:
    • Multi-Tenancy Strategy ADR (from Phase 1)
    • Database Isolation Design spec
    • TenantMixin pattern documentation
  - Documents Created:
    • Implementation Guide: Tenant Middleware
    • API Spec: Tenant Context API
    • Test Plan: Multi-Tenant Integration Tests
```

#### Phase 3: Plugin System (Weeks 7-10)
```yaml
Work Item: "Plugin Architecture Implementation"
Type: FEATURE
Tasks:
  - Plugin discovery system (4h)
  - Plugin lifecycle management (4h)
  - Plugin dependency resolution (6h)
  - Plugin API contracts (4h)
  - Plugin marketplace (8h)

AI Agents Involved:
  - aipm-plugin-developer (plugin system)
  - aipm-frontend-developer (marketplace UI)
  - aipm-documentation-specialist (API docs)

AIPM Enables:
  - Pattern reuse from Phase 2 (tenant awareness)
  - Decision reference (why plugin approach chosen)
  - Cross-session continuity (any agent can continue work)
  - Quality enforcement (all plugins must pass gates)
```

#### Phase 4-10: Feature Development (Weeks 11-40)
**CMS Module, CRM Module, E-Commerce, Marketing, Analytics, Reporting...**

Each module:
- References architectural decisions from Phase 1
- Reuses patterns from Core Infrastructure
- Maintains quality gates and testing standards
- Fully documented and auditable
- Built by coordinated AI agents with zero context loss

---

## System Architecture

### 1. Core Data Model

#### Hierarchy
```
PROJECT
  ├─ Metadata: name, description, tech_stack, created_at
  ├─ Configuration: quality_gates, time_boxing_rules, workflow_config
  ├─ Rules: coding_standards, architectural_principles, constraints
  └─ WORK ITEMS (objectives, features, bugs, research)
       ├─ Metadata: title, type, status, priority, phase
       ├─ Content: description, objectives, acceptance_criteria, DoD
       ├─ Context: decisions, patterns, constraints, risks
       └─ TASKS (implementation units)
            ├─ Metadata: title, type, status, effort, owner
            ├─ Details: implementation_notes, code_files, patterns
            ├─ Evidence: decisions, sources, confidence_scores
            └─ Assignments: agent_id, assignee, reviewer
```

#### Relationships
```sql
projects (1) ──→ (n) work_items
projects (1) ──→ (n) documents
work_items (1) ──→ (n) tasks
work_items (1) ──→ (n) documents
work_items (1) ──→ (n) decisions
tasks (1) ──→ (1) agents (assigned)
tasks (1) ──→ (n) evidence_entries
tasks (1) ──→ (n) documents
decisions (1) ──→ (n) documents (ADRs)
documents (1) ──→ (n) document_tags
documents (1) ──→ (n) document_references
projects (1) ──→ (n) rules
agents (1) ──→ (n) tasks (history)
sessions (1) ──→ (n) work_items (active)
sessions (1) ──→ (n) documents (created during session)
```

### 2. Context System

#### Hierarchical Context Assembly
```python
class ContextAssemblyService:
    """
    Assembles context from database for AI agents.
    Compresses 200K+ tokens → 20K tokens through intelligent layering.
    """

    def assemble_project_context(self, project_id: int) -> ProjectContext:
        """
        Project-level context (governance layer)

        Returns:
        - Tech stack (Django 4.2, React 18, PostgreSQL 15)
        - Coding standards (PEP 8, ESLint config)
        - Architecture principles (hexagonal, DDD, event-driven)
        - Quality gates (CI-001 through CI-006)
        - Active constraints (no external APIs, security requirements)

        Token budget: ~3-5K tokens
        """

    def assemble_work_item_context(self, work_item_id: int) -> WorkItemContext:
        """
        Work item-level context (outcome layer)

        Returns:
        - Objective (what we're building and why)
        - Acceptance criteria (definition of done)
        - Architecture decisions made (ADRs)
        - Discovered patterns (code patterns, best practices)
        - Related documents (specs, designs, guides) via document store
        - Risks and constraints
        - Quality gates specific to this work item

        Token budget: ~5-8K tokens
        Includes: Project context (inherited) + document references

        Document Integration:
        - Searches document store for related docs (tags, work_item_id)
        - Includes document summaries (not full content)
        - Links to ADRs, specs, guides relevant to this work
        - Prevents loading irrelevant documentation
        """

    def assemble_task_context(self, task_id: int) -> TaskContext:
        """
        Task-level context (execution layer)

        Returns:
        - Task objective and implementation details
        - Code files involved
        - Patterns to follow (from work item discoveries)
        - Sub-task breakdown
        - Agent assignment and SOP
        - Previous session learnings

        Token budget: ~8-12K tokens
        Includes: Work item + Project context (inherited)
        """

    def compress_for_agent(self, context: Context, agent_type: str) -> str:
        """
        Compress context based on agent needs.

        Examples:
        - aipm-testing-specialist: Emphasize test patterns, coverage
        - aipm-database-developer: Emphasize schema, migrations
        - aipm-frontend-developer: Emphasize UI patterns, components

        Token budget: Optimized for agent role
        """
```

#### Context Persistence
```python
class ContextPersistenceService:
    """
    Saves discoveries, decisions, and learnings back to database.
    Enables continuous learning and cross-session knowledge transfer.
    """

    def save_decision(
        self,
        work_item_id: int,
        decision: str,
        rationale: str,
        alternatives_considered: List[str],
        evidence: List[EvidenceEntry]
    ) -> Decision:
        """
        Persist architectural/implementation decision.

        Examples:
        - "Use schema-based multi-tenancy over database-per-tenant"
        - "JWT authentication over session-based"
        - "GraphQL for complex queries, REST for CRUD"
        """

    def save_pattern(
        self,
        work_item_id: int,
        pattern_name: str,
        pattern_description: str,
        code_example: Optional[str],
        when_to_use: str
    ) -> Pattern:
        """
        Persist discovered code pattern for reuse.

        Examples:
        - "TenantMixin: Base class for all tenant-scoped models"
        - "ServiceLayer: Business logic isolation pattern"
        - "RepositoryPattern: Data access abstraction"
        """

    def save_constraint(
        self,
        work_item_id: int,
        constraint: str,
        reason: str,
        enforcement: str
    ) -> Constraint:
        """
        Persist constraint that must be followed.

        Examples:
        - "All models must inherit TenantMixin"
        - "No direct database queries in views"
        - "All external APIs must use circuit breaker"
        """
```

### 3. Agent Orchestration

#### Agent Types & Roles
```yaml
Orchestrators (Strategic):
  - aipm-owner: Product vision, prioritization
  - aipm-team-leader: Work item management, agent coordination
  - aipm-development-orchestrator: Technical planning, architecture

Specialists (Implementation):
  - aipm-requirements-specifier: Research, analysis, specification
  - aipm-python-cli-developer: Python/Django implementation
  - aipm-database-developer: Schema design, migrations, queries
  - aipm-frontend-developer: React/Next.js UI development
  - aipm-plugin-developer: Plugin system, extensibility
  - aipm-testing-specialist: Test implementation, coverage
  - aipm-devops-specialist: Deployment, infrastructure
  - aipm-documentation-specialist: Documentation, knowledge base

Sub-Agents (Context Compression):
  - aipm-codebase-navigator: Code discovery (50K → 1.2K tokens)
  - aipm-database-schema-explorer: Schema analysis (30K → 1.2K tokens)
  - aipm-rules-compliance-checker: Compliance validation (20K → 1K tokens)
  - aipm-workflow-analyzer: Task analysis (15K → 900 tokens)
  - aipm-plugin-system-analyzer: Plugin intelligence (50K → 1.5K tokens)
  - aipm-test-pattern-analyzer: Test coverage (25K → 1.1K tokens)
  - aipm-documentation-analyzer: Doc quality (30K → 1.3K tokens)
  - aipm-document-search: Fast doc discovery (<100ms vs 5-10s grep)
```

#### Sub-Agent Delegation Pattern
```python
# Main orchestrator context: 20K tokens (after compression)

# Need codebase analysis
result = delegate_to_subagent(
    agent="aipm-codebase-navigator",
    query="Find all tenant-scoped models and their relationships",
    context=minimal_context  # Only what sub-agent needs
)

# Sub-agent processes:
# 1. Loads work item context (knows about multi-tenancy)
# 2. Searches entire codebase (50K+ lines)
# 3. Analyzes patterns, relationships
# 4. Compresses findings to 1.2K tokens
# 5. Returns structured report

# Main orchestrator receives:
compressed_report = {
    "tenant_models": ["Tenant", "Domain", "TenantUser"],
    "relationships": "Tenant → Domain (1:n), Tenant → TenantUser (1:n)",
    "patterns": "All use TenantMixin, tenant_id FK",
    "files": ["models/tenant.py:15-80", "models/domain.py:10-45"]
}
# Token cost: 1.2K tokens (97% reduction from 50K)
```

### 4. Session Management

#### Session Lifecycle
```python
class SessionService:
    """
    Manages AI agent session lifecycle with persistent context.
    """

    def start_session(self, work_item_id: Optional[int] = None) -> Session:
        """
        Session start (automatic via hooks)

        1. Detect active work item/task
        2. Load compressed context from database
        3. Identify relevant agents for this work
        4. Prepare session workspace
        5. Return session context for AI agent

        Output: SessionContext (5-15K tokens)
        """

    def update_session(
        self,
        session_id: int,
        learnings: List[Learning],
        decisions: List[Decision],
        progress: Dict[str, Any]
    ):
        """
        Continuous session updates (during work)

        1. Save decisions as they're made
        2. Record patterns as discovered
        3. Update task progress
        4. Persist evidence and sources

        Frequency: Real-time (as discoveries happen)
        """

    def end_session(self, session_id: int) -> SessionSummary:
        """
        Session end (automatic via hooks)

        1. Capture final state
        2. Update all context (work item, tasks, patterns)
        3. Generate session summary
        4. Update agent assignments
        5. Trigger quality gates if applicable

        Output: SessionSummary (audit record)
        """
```

#### Session Hooks (Provider-Specific)
```python
# Claude Code: .claude/hooks/session-start.py
def session_start():
    session = aipm.start_session(auto_detect=True)
    context = session.get_context(format="markdown")

    # Output for Claude Code to auto-load
    print(context)

    # Activates agent SOP if relevant
    if session.assigned_agent:
        agent_sop = aipm.agents.get_sop(session.assigned_agent)
        print(agent_sop)

# Cursor: .cursor/hooks/session-start.ts
function sessionStart() {
    const session = aipm.startSession({ autoDetect: true });
    const context = session.getContext({ format: "json" });

    // Cursor-specific context format
    return {
        workspace: context.project,
        objective: context.workItem,
        task: context.task,
        patterns: context.patterns
    };
}

# Aider: .aider/config.yml
hooks:
  session_start:
    command: "apm session start --format=aider"
    output: "inject-context"
```

### 5. Work Management

#### Work Item Types
```yaml
FEATURE:
  Purpose: User-facing functionality
  Required Tasks: [DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION]
  Time-boxing: Implementation ≤4h per task
  Quality Gates: All CI gates + feature-specific acceptance criteria
  Example: "Multi-tenant domain routing system"

BUGFIX:
  Purpose: Resolve defects
  Required Tasks: [ANALYSIS, FIX, TESTING]
  Time-boxing: Fix ≤2h, testing ≤2h
  Quality Gates: Regression tests-BAK, root cause analysis
  Example: "Tenant isolation leak in admin panel"

REFACTORING:
  Purpose: Improve code quality without changing behavior
  Required Tasks: [ANALYSIS, REFACTOR, TESTING]
  Time-boxing: Refactor ≤4h per task
  Quality Gates: All existing tests-BAK pass, no behavior changes
  Example: "Extract tenant context to middleware"

RESEARCH:
  Purpose: Investigate options, analyze feasibility
  Required Tasks: [RESEARCH, ANALYSIS, DOCUMENTATION]
  Time-boxing: Research ≤8h per task
  Quality Gates: Evidence-based conclusions, multiple sources
  Example: "Multi-tenancy pattern evaluation"

PLANNING:
  Purpose: Strategic planning, architecture design
  Required Tasks: [ANALYSIS, DESIGN, DOCUMENTATION]
  Time-boxing: Design ≤8h per task
  Quality Gates: ADRs created, stakeholder review
  Example: "Plugin system architecture design"
```

#### Task Workflow
```yaml
States:
  PROPOSED: Initial creation, needs validation
  VALIDATED: Meets quality standards, ready for acceptance
  ACCEPTED: Assigned to agent, ready to start
  IN_PROGRESS: Active work in progress
  REVIEW: Work complete, needs validation
  COMPLETED: Work validated and accepted
  CANCELLED: Work abandoned or superseded

Transitions:
  PROPOSED → VALIDATED: Validation checks pass
  VALIDATED → ACCEPTED: Agent assigned, work committed
  ACCEPTED → IN_PROGRESS: Agent starts work
  IN_PROGRESS → REVIEW: Agent submits work
  REVIEW → COMPLETED: Validation passes
  REVIEW → IN_PROGRESS: Changes requested
  ANY → CANCELLED: Work no longer needed

Agent Separation:
  Implementation: Agent that does the work
  Review: Different agent validates work
  Approval: Quality validator confirms completion

  Pattern: No self-approval, ensures quality
```

### 6. Quality Gates

#### CI Gates (Continuous Integration)
```yaml
CI-001 Agent Validation:
  Purpose: Ensure agents exist and are properly configured
  Check: Agent assignment exists in database
  Enforcement: Automatic validation on task acceptance

CI-002 Context Quality:
  Purpose: Ensure adequate context for work
  Check: Context confidence ≥0.70 (70% threshold)
  Enforcement: Automatic context assembly and scoring

CI-003 Framework Agnosticism:
  Purpose: Prevent vendor lock-in
  Check: No provider-specific code in core
  Enforcement: Code review, dependency analysis

CI-004 Testing Quality:
  Purpose: Ensure comprehensive test coverage
  Check: Test coverage ≥90%
  Enforcement: Automatic coverage analysis

CI-005 Security Practices:
  Purpose: Enforce security best practices
  Check: Security scan passes, no critical vulnerabilities
  Enforcement: Automated security scanning

CI-006 Documentation Standards:
  Purpose: Maintain documentation quality
  Check: All public APIs documented, ADRs present
  Enforcement: Automated documentation validation
```

#### Work Item Quality Gates
```yaml
FEATURE Gates:
  - All required task types completed (DESIGN, IMPL, TEST, DOC)
  - All acceptance criteria met
  - All tests-BAK passing (>90% coverage)
  - Documentation complete
  - Security review passed
  - Performance benchmarks met

BUGFIX Gates:
  - Root cause identified and documented
  - Fix implemented and tested
  - Regression tests-BAK added
  - No new bugs introduced

REFACTORING Gates:
  - All existing tests-BAK still pass
  - No behavior changes
  - Code quality metrics improved
  - Documentation updated
```

### 7. Evidence & Decision Tracking

#### Evidence Model
```python
@dataclass
class EvidenceEntry:
    """
    Tracks sources and confidence for all claims and decisions.
    """
    source_url: str
    source_type: Literal["primary", "secondary", "internal"]
    excerpt: str  # ≤25 words
    captured_at: datetime
    content_hash: str  # SHA256 for verification
    confidence: float  # 0.0-1.0
    relevance: float  # 0.0-1.0

@dataclass
class Decision:
    """
    Architectural or implementation decision with rationale.
    """
    work_item_id: int
    title: str
    decision: str
    rationale: str
    alternatives_considered: List[str]
    evidence: List[EvidenceEntry]
    confidence: float
    made_by: str  # agent or human
    made_at: datetime
    status: Literal["proposed", "accepted", "superseded"]
```

#### Decision Tracking Examples
```python
# Decision 1: Multi-Tenancy Pattern
Decision(
    work_item_id=1,
    title="Multi-Tenancy Isolation Strategy",
    decision="Use schema-based isolation with tenant_id column",
    rationale="""
    Balance between complexity and scalability:
    - Database-per-tenant: Too complex at 10K+ tenants
    - Schema-per-tenant: Better but PostgreSQL schema limits
    - Shared schema: Simplest, scales to millions of tenants
    """,
    alternatives_considered=[
        "Database-per-tenant (rejected: operational complexity)",
        "Schema-per-tenant (rejected: PostgreSQL 9.6 limit 100K schemas)",
    ],
    evidence=[
        EvidenceEntry(
            source_url="https://django-tenants.readthedocs.io",
            source_type="primary",
            excerpt="Schema approach recommended for <100K tenants",
            confidence=0.9
        ),
        EvidenceEntry(
            source_url="internal://architecture/multi-tenancy-analysis.md",
            source_type="internal",
            excerpt="Cost analysis: schema = $5K/mo, database = $50K/mo",
            confidence=0.95
        )
    ],
    confidence=0.85,
    made_by="aipm-database-developer",
    made_at=datetime.now(),
    status="accepted"
)
```

### 8. Provider Abstraction Layer

#### Provider Interface
```python
class ProviderAdapter(ABC):
    """
    Abstract interface for AI coding assistant providers.
    Each provider implements this for AIPM integration.
    """

    @abstractmethod
    def get_session_context(self) -> Dict[str, Any]:
        """
        How this provider identifies current session/task/project.

        Returns:
        - project_path: Path to project root
        - active_files: Currently open/edited files
        - active_task: Task identifier (if any)
        - session_id: Provider's session identifier
        """

    @abstractmethod
    def inject_context(self, context: str, format: str):
        """
        How to inject AIPM context into this provider.

        Formats:
        - markdown: For Claude Code, Aider
        - json: For Cursor, Codex
        - structured: For custom integrations
        """

    @abstractmethod
    def capture_session_learning(self) -> Dict[str, Any]:
        """
        How to capture what this provider learned during session.

        Returns:
        - decisions: Decisions made
        - patterns: Patterns discovered
        - code_changes: Files modified
        - evidence: Sources referenced
        """

    @abstractmethod
    def register_hooks(self) -> Dict[str, str]:
        """
        Where to install session lifecycle hooks.

        Returns:
        - session_start: Hook script location
        - session_end: Hook script location
        - continuous_update: Real-time update mechanism
        """
```

#### Provider Implementations

##### Claude Code Adapter
```python
class ClaudeCodeAdapter(ProviderAdapter):
    """
    Integration with Claude Code (Anthropic CLI)
    """

    def get_session_context(self) -> Dict[str, Any]:
        """
        Claude Code identifies context through:
        - Current working directory (project root)
        - CLAUDE.md.backup-20251018 instructions
        - Open files in editor
        """
        return {
            "project_path": os.getcwd(),
            "claude_md": Path(".claude/CLAUDE.md.backup-20251018").read_text(),
            "active_files": self._get_open_files(),
            "session_id": self._generate_session_id()
        }

    def inject_context(self, context: str, format: str = "markdown"):
        """
        Claude Code loads context through:
        1. Session start hook output (auto-injected)
        2. Agent CLAUDE.md.backup-20251018 files
        3. System reminders
        """
        if format == "markdown":
            # Output for hook to return
            return context
        elif format == "structured":
            # For agent SOPs
            return self._format_for_agent(context)

    def register_hooks(self) -> Dict[str, str]:
        """
        Install hooks in .claude/hooks/
        """
        return {
            "session_start": ".claude/hooks/session-start.py",
            "session_end": ".claude/hooks/session-end.py",
            "continuous_update": None  # Manual commands during session
        }
```

##### Cursor Adapter
```python
class CursorAdapter(ProviderAdapter):
    """
    Integration with Cursor IDE
    """

    def get_session_context(self) -> Dict[str, Any]:
        """
        Cursor identifies context through:
        - Workspace root
        - .cursorrules file
        - Active editor tabs
        - Composer session
        """
        return {
            "project_path": self._get_workspace_root(),
            "cursor_rules": Path(".cursorrules").read_text(),
            "active_files": self._get_active_tabs(),
            "composer_session": self._get_composer_state()
        }

    def inject_context(self, context: str, format: str = "json"):
        """
        Cursor loads context through:
        1. .cursorrules file (project-level)
        2. Inline @-mentions
        3. Composer context
        """
        if format == "json":
            return json.dumps({
                "project_context": context,
                "active_work_item": self._get_active_work_item(),
                "patterns": self._get_patterns()
            })

    def register_hooks(self) -> Dict[str, str]:
        """
        Install hooks in .cursor/hooks/
        """
        return {
            "session_start": ".cursor/hooks/session-start.ts",
            "session_end": ".cursor/hooks/session-end.ts",
            "continuous_update": ".cursor/hooks/on-save.ts"
        }
```

##### Aider Adapter
```python
class AiderAdapter(ProviderAdapter):
    """
    Integration with Aider (command-line AI coding)
    """

    def get_session_context(self) -> Dict[str, Any]:
        """
        Aider identifies context through:
        - Git repository
        - .aider.conf.yml
        - Command-line arguments
        """
        return {
            "project_path": self._get_git_root(),
            "aider_config": self._load_aider_config(),
            "active_files": self._get_watched_files(),
            "git_branch": self._get_current_branch()
        }

    def inject_context(self, context: str, format: str = "markdown"):
        """
        Aider loads context through:
        1. --read flag (files to read)
        2. --message flag (initial instructions)
        3. Config file
        """
        if format == "markdown":
            # Write to temp file for --read
            context_file = "/tmp/aipm-context.md"
            Path(context_file).write_text(context)
            return context_file

    def register_hooks(self) -> Dict[str, str]:
        """
        Install hooks via .aider.conf.yml
        """
        return {
            "session_start": "hooks.session_start: apm session start --format=aider",
            "session_end": "hooks.session_end: apm session end --capture-learning",
            "continuous_update": "hooks.on_commit: apm session update"
        }
```

### 9. Document Store (Knowledge Management)

#### Document Management System

**Problem:** Complex projects generate 100s of documents (ADRs, specs, guides). Finding relevant documentation takes 5-10 seconds (grep) or fails entirely (wrong keywords). Teams duplicate documentation because they can't find existing docs.

**Solution:** Fast indexed document store with semantic search and duplicate detection.

```python
@dataclass
class Document:
    """
    Metadata for project documentation.

    Content stored on filesystem, metadata in database for fast search.
    """

    # Identification
    id: str  # UUID
    project_id: int
    file_path: str  # Relative to project root
    content_hash: str  # SHA256

    # Metadata
    title: str
    document_type: Literal["adr", "spec", "api", "guide", "plan", "design"]
    status: Literal["draft", "review", "approved", "superseded", "archived"]
    summary: str  # ≤200 words, searchable

    # Authorship
    author: str  # Agent or human
    created_at: datetime
    updated_at: datetime
    version: int

    # Relationships
    work_item_id: Optional[int]
    task_id: Optional[int]
    decision_ids: List[str]
    supersedes: Optional[str]  # Previous version
    superseded_by: Optional[str]  # Newer version

    # Search optimization
    tags: List[DocumentTag]  # Auto-generated + manual
    search_hit_count: int  # Popularity metric

@dataclass
class DocumentTag:
    """Auto-generated semantic tags for search"""
    tag: str  # "jwt", "authentication", "database"
    tag_type: Literal["concept", "technology", "entity", "pattern"]
    confidence: float  # Auto-tag confidence
    source: Literal["auto", "manual"]
```

#### Document Services

```python
class DocumentSearchService:
    """
    Fast multi-field search (<100ms vs 5-10s grep).

    Search by:
    - Title, summary, tags, keywords
    - Document type (ADR, spec, guide)
    - Work item, task, decision links
    - Date range, author, status
    """

    def search(self, query: str, **filters) -> SearchResult:
        """
        Example:
        search("jwt authentication", document_type="adr")

        Returns in <100ms:
        1. JWT Authentication Strategy (ADR-003) - 95% relevance
        2. API Auth Spec - 68% relevance
        3. Token Refresh Guide - 52% relevance
        """

class DocumentDuplicateDetectionService:
    """
    Prevent duplicate documentation.

    Before creating doc, check for similar:
    - Title similarity
    - Tag overlap
    - Summary similarity

    Warns if >70% similar doc exists.
    """

class DocumentAutoTaggingService:
    """
    Automatically extract tags from content.

    Detects:
    - Technologies (Django, React, PostgreSQL)
    - Concepts (authentication, caching, testing)
    - Entities (User model, JWT token)
    - Patterns (service layer, repository)

    Achieves >80% tagging accuracy.
    """
```

#### Document Integration with Context

```python
# When loading work item context
def assemble_work_item_context(self, work_item_id: int):
    # ... load decisions, patterns ...

    # Load related documents (FAST - from indexed database)
    related_docs = DocumentSearchService().get_related_documents(
        work_item_id=work_item_id,
        limit=10
    )

    # Include document summaries in context (not full content)
    context.documents = [
        {
            "title": doc.title,
            "type": doc.document_type,
            "path": doc.file_path,
            "summary": doc.summary[:100],  # First 100 chars
            "tags": [t.tag for t in doc.tags[:5]]  # Top 5 tags
        }
        for doc in related_docs
    ]

    # Agent can now say:
    # "I see there's an ADR about JWT authentication (ADR-003).
    #  Let me read that for implementation details."
```

#### CLI Commands

```bash
# Register document (auto-tags, duplicate detection)
apm doc register docs/adrs/ADR-007-caching.md \
  --work-item=10 \
  --summary="Redis caching strategy for session data"

# Search documents (<100ms)
apm doc search "authentication jwt"

# Find related docs
apm doc related --work-item=5

# List by type
apm doc list --type=adr --status=approved

# Document coverage report
apm doc report --work-item=5
```

#### Benefits

1. **Fast Search**: <100ms (vs 5-10s grep on large codebases)
2. **Prevent Duplication**: Warns before creating similar doc
3. **Better Organization**: Know what docs exist and where
4. **Context Integration**: Documents automatically included in work item context
5. **Audit Trail**: Track document evolution and relationships

### 10. Plugin System (Framework Intelligence)

#### Plugin Architecture
```python
class FrameworkPlugin(ABC):
    """
    Detects and provides intelligence about frameworks/technologies.
    """

    @abstractmethod
    def detect(self, project_path: Path) -> DetectionResult:
        """
        Detect if this framework is present in project.

        Returns:
        - detected: bool
        - confidence: float (0.0-1.0)
        - version: Optional[str]
        - evidence: List[str] (files that indicate presence)
        """

    @abstractmethod
    def get_context(self) -> FrameworkContext:
        """
        Provide framework-specific context for AI agents.

        Returns:
        - patterns: Code patterns for this framework
        - best_practices: Framework-specific guidelines
        - common_pitfalls: Things to avoid
        - useful_docs: Links to documentation
        """

class DjangoPlugin(FrameworkPlugin):
    """
    Django framework detection and intelligence
    """

    def detect(self, project_path: Path) -> DetectionResult:
        """
        Detect Django through:
        - requirements.txt contains 'django'
        - manage.py present
        - Django project structure (settings.py, urls.py)
        """

    def get_context(self) -> FrameworkContext:
        """
        Django-specific context:
        - Patterns: CBV, mixins, managers, middleware
        - Best practices: Fat models, thin views
        - Pitfalls: N+1 queries, migration conflicts
        - Docs: Django docs, Two Scoops of Django
        """
```

### 10. Audit & Compliance

#### Audit Trail
```python
@dataclass
class AuditEntry:
    """
    Complete audit trail for all system actions.
    """
    timestamp: datetime
    actor: str  # agent or human user
    actor_type: Literal["agent", "human"]
    action: str  # what was done
    entity_type: str  # work_item, task, decision, etc.
    entity_id: int
    changes: Dict[str, Any]  # what changed (before/after)
    context: Dict[str, Any]  # why it was done
    session_id: Optional[int]

# Examples
AuditEntry(
    timestamp=datetime.now(),
    actor="aipm-database-developer",
    actor_type="agent",
    action="CREATE_MIGRATION",
    entity_type="migration",
    entity_id=15,
    changes={
        "file": "migrations/0015_add_tenant_domain.py",
        "operations": ["AddField(model='tenant', name='domain')"]
    },
    context={
        "work_item_id": 5,
        "task_id": 42,
        "decision_id": 8,
        "rationale": "Support custom domains per tenant"
    },
    session_id=123
)
```

#### Compliance Reporting
```python
class ComplianceService:
    """
    Generate compliance reports for audit/review.
    """

    def generate_work_item_report(self, work_item_id: int) -> Report:
        """
        Complete report for work item:
        - All tasks and their status
        - All decisions made and rationale
        - All evidence and sources
        - All code changes (git commits)
        - All agents involved
        - Quality gate results
        - Timeline (start to completion)
        """

    def generate_agent_report(self, agent_id: str, date_range: DateRange) -> Report:
        """
        What specific agent did:
        - Tasks completed
        - Decisions made
        - Code changes
        - Quality metrics
        - Learning captured
        """

    def generate_project_report(self, project_id: int) -> Report:
        """
        Complete project audit:
        - All work items and status
        - Architecture decisions (ADRs)
        - Technology choices and rationale
        - Quality metrics over time
        - Agent utilization
        - Timeline and milestones
        """
```

---

## Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-4)
**Goal:** Provider-agnostic core with basic context persistence

```yaml
Week 1-2: Data Model & Database
  Tasks:
    - Finalize schema for decisions, evidence, patterns
    - Implement context assembly service (hierarchical loading)
    - Create context persistence service (save learnings)
    - Migration system for schema evolution

  Deliverables:
    - Complete database schema
    - Context assembly API
    - Context persistence API
    - Migration scripts

  Success Criteria:
    - Context loads in <1s
    - Context compresses 200K → 20K tokens
    - All CRUD operations work

Week 3-4: Session Management, Hooks & Document Store
  Tasks:
    - Session lifecycle implementation
    - Hook system (session start/end/update)
    - Claude Code adapter (reference implementation)
    - Evidence tracking system
    - Document store database schema
    - Document registration and search

  Deliverables:
    - Session management API
    - Hook templates for Claude Code
    - Claude Code integration working
    - Evidence model implemented
    - Document store models and services
    - CLI: apm doc register/search/list

  Success Criteria:
    - Sessions start/end automatically
    - Context persists across sessions
    - Evidence captured with confidence scores
    - Document search <100ms
    - Duplicate detection works
```

### Phase 2: Sub-Agent Orchestration (Weeks 5-8)
**Goal:** Context compression through sub-agent delegation

```yaml
Week 5-6: Sub-Agent Framework
  Tasks:
    - Sub-agent Task tool integration
    - Context loading for sub-agents
    - Compressed report format
    - Sub-agent catalog implementation

  Deliverables:
    - 7 sub-agents implemented:
      • aipm-codebase-navigator
      • aipm-database-schema-explorer
      • aipm-rules-compliance-checker
      • aipm-workflow-analyzer
      • aipm-plugin-system-analyzer
      • aipm-test-pattern-analyzer
      • aipm-documentation-analyzer

  Success Criteria:
    - Sub-agents compress 50K → 1.2K tokens (97% reduction)
    - Sub-agents have access to work item context
    - Parallel sub-agent execution works

Week 7-8: Agent Coordination
  Tasks:
    - Agent assignment system
    - Agent SOP loading
    - Cross-agent context sharing
    - Agent performance tracking

  Deliverables:
    - Agent assignment workflow
    - Agent SOPs in database
    - Context sharing between agents
    - Agent metrics dashboard

  Success Criteria:
    - Agents auto-assigned based on task type
    - Agents load relevant SOPs automatically
    - Context persists across agent handoffs
```

### Phase 3: Multi-Provider Support (Weeks 9-12)
**Goal:** Support Cursor, Aider, Codex, Gemini

```yaml
Week 9-10: Provider Abstraction
  Tasks:
    - Provider adapter interface
    - Cursor adapter implementation
    - Aider adapter implementation
    - Provider detection system

  Deliverables:
    - ProviderAdapter base class
    - Cursor integration working
    - Aider integration working
    - Auto-detection of active provider

  Success Criteria:
    - Same AIPM context works in Cursor and Aider
    - Hooks work in all providers
    - Session management provider-agnostic

Week 11-12: Advanced Provider Features
  Tasks:
    - Codex adapter (GitHub Copilot)
    - Gemini adapter (Google)
    - Provider-specific optimizations
    - Cross-provider session handoff

  Deliverables:
    - 5 providers supported:
      • Claude Code
      • Cursor
      • Aider
      • GitHub Copilot
      • Gemini

  Success Criteria:
    - Can switch providers mid-project
    - Context persists across provider changes
    - All providers access same work items
```

### Phase 4: Quality & Audit (Weeks 13-16)
**Goal:** Enterprise-grade audit trails and quality gates

```yaml
Week 13-14: Audit System
  Tasks:
    - Complete audit trail implementation
    - Decision tracking with evidence
    - Compliance reporting
    - Historical analysis

  Deliverables:
    - Full audit trail for all actions
    - Decision reports with rationale
    - Compliance dashboard
    - Historical queries API

  Success Criteria:
    - Every action logged with context
    - Can generate work item audit report
    - Can answer "why was X decision made?"
    - Can track agent performance over time

Week 15-16: Quality Gates
  Tasks:
    - All 6 CI gates implemented
    - Work item quality gates
    - Automated validation
    - Quality dashboard

  Deliverables:
    - CI-001 through CI-006 enforcement
    - Feature/bugfix/refactor gates
    - Quality metrics tracking
    - Quality trend analysis

  Success Criteria:
    - Gates automatically enforce standards
    - Work items can't complete without gates passing
    - Quality trends visible over time
```

### Phase 5: Intelligence & Learning (Weeks 17-20)
**Goal:** System learns and improves from every session

```yaml
Week 17-18: Pattern Recognition
  Tasks:
    - Pattern extraction from sessions
    - Pattern similarity detection
    - Pattern recommendation system
    - Pattern library

  Deliverables:
    - Automatic pattern extraction
    - Pattern search and discovery
    - Pattern suggestions for tasks
    - Community pattern sharing

  Success Criteria:
    - System extracts patterns from code
    - Suggests relevant patterns for tasks
    - Patterns improve over time

Week 19-20: Continuous Improvement
  Tasks:
    - Decision effectiveness tracking
    - A/B testing for approaches
    - Performance metrics
    - Learning analytics

  Deliverables:
    - Decision outcome tracking
    - Approach comparison
    - Performance dashboards
    - Learning insights

  Success Criteria:
    - Can measure decision quality
    - Can compare approaches
    - System recommends better approaches
```

---

## Success Metrics

### Phase 1 Metrics
```yaml
Context Performance:
  - Context load time: <1s
  - Token compression: 200K → 20K (90% reduction)
  - Session start time: <2s
  - Cross-session context persistence: 100%

Integration Quality:
  - Claude Code integration: Working
  - Hook reliability: 100% (no missed sessions)
  - Evidence capture: >90% of decisions

Document Store:
  - Search performance: <100ms (vs 5-10s grep)
  - Duplicate detection accuracy: >80%
  - Auto-tagging accuracy: >80%
  - Document registration rate: >90% of new docs
```

### Phase 2 Metrics
```yaml
Sub-Agent Performance:
  - Context compression: 50K → 1.2K (97% reduction)
  - Sub-agent execution time: <5s per query
  - Parallel execution: 3+ sub-agents
  - Context accuracy: >90% relevance

Agent Coordination:
  - Agent assignment accuracy: >95%
  - Cross-agent context sharing: 100%
  - Agent performance tracking: Real-time
```

### Phase 3 Metrics
```yaml
Multi-Provider:
  - Providers supported: 5 (Claude, Cursor, Aider, Copilot, Gemini)
  - Provider-agnostic context: 100%
  - Cross-provider handoff: <30s
  - Provider-specific optimizations: Measured

Market Adoption:
  - Active users: Target 100 in month 1
  - Projects managed: Target 50 in month 1
  - Work items created: Target 500 in month 1
```

### Phase 4 Metrics
```yaml
Audit & Compliance:
  - Audit completeness: 100% (all actions logged)
  - Decision traceability: 100%
  - Compliance report generation: <5s
  - Historical query performance: <1s

Quality Gates:
  - Gate enforcement: 100%
  - False positives: <5%
  - Quality improvement over time: Measured
```

### Phase 5 Metrics
```yaml
Intelligence & Learning:
  - Pattern extraction accuracy: >80%
  - Pattern recommendation relevance: >70%
  - Decision quality improvement: Measured
  - Time to productivity: -50% (vs. no AIPM)
```

---

## Technical Requirements

### Performance Targets
```yaml
Response Times:
  - Context load: <1s (P95)
  - Sub-agent query: <5s (P95)
  - Session start: <2s (P95)
  - Database queries: <100ms (P95)

Scalability:
  - Projects: 1,000+ concurrent
  - Work items: 10,000+ per project
  - Tasks: 100,000+ per project
  - Sessions: 1,000+ concurrent

Storage:
  - Database: SQLite (small) / PostgreSQL (large)
  - Context compression: 90%+ reduction
  - Evidence retention: 5 years
  - Audit logs: Infinite retention
```

### Compatibility
```yaml
Python: 3.10+
Databases: SQLite 3.35+, PostgreSQL 13+
Operating Systems: macOS, Linux, Windows
AI Providers: Claude Code, Cursor, Aider, Copilot, Gemini
Version Control: Git 2.30+
```

### Security
```yaml
Data Protection:
  - Sensitive data encryption at rest
  - Secure credential storage
  - API key management
  - Access control (RBAC)

Compliance:
  - Complete audit trail
  - Data retention policies
  - GDPR compliance (data export/deletion)
  - SOC 2 readiness
```

---

## Documentation Requirements

### User Documentation
```yaml
Quick Start:
  - 5-minute getting started guide
  - Installation instructions
  - First project walkthrough
  - Provider integration guides

User Guides:
  - Work item management
  - Task workflows
  - Session management
  - Quality gates
  - Agent coordination

Reference:
  - CLI command reference
  - API documentation
  - Configuration options
  - Troubleshooting guide
```

### Developer Documentation
```yaml
Architecture:
  - System architecture overview
  - Data model documentation
  - Provider adapter guide
  - Plugin development guide

Contributing:
  - Development setup
  - Code style guide
  - Testing requirements
  - Pull request process

API Reference:
  - Context assembly API
  - Session management API
  - Evidence tracking API
  - Audit system API
```

---

## Open Questions & Decisions Needed

### Architecture Decisions
1. **Database Choice**: SQLite (simplicity) vs PostgreSQL (scale)?
2. **Context Format**: Markdown (readable) vs JSON (structured)?
3. **Plugin System**: Python-only or multi-language?
4. **Evidence Storage**: Database (queryable) vs files (simple)?

### Product Decisions
1. **Licensing**: Open-source (MIT/Apache) or commercial?
2. **Monetization**: Free tier + paid features? Enterprise only?
3. **Community**: Public development or private during beta?
4. **Support Model**: Community support or commercial support?

### Technical Decisions
1. **Sub-Agent Communication**: Direct (in-process) or RPC?
2. **Context Caching**: Redis (performance) or memory (simplicity)?
3. **Event System**: Database (durable) or message queue (scale)?
4. **Provider Detection**: Auto-detect or explicit configuration?

---

## Related Documents

### ADRs (Complete Set - 11 ADRs)

**Core Architecture:**
- ✅ ADR-001: Provider Abstraction Architecture
- ✅ ADR-002: Context Compression Strategy
- ✅ ADR-003: Sub-Agent Communication Protocol
- ✅ ADR-004: Evidence Storage and Retrieval
- ✅ ADR-005: Multi-Provider Session Management
- ✅ ADR-006: Document Store and Knowledge Management

**Enterprise Features:**
- ✅ ADR-007: Human-in-the-Loop Workflows
- ✅ ADR-008: Data Privacy and Security
- ✅ ADR-009: Event System and Integrations
- ✅ ADR-010: Dependency Management and Scheduling
- ✅ ADR-011: Cost Tracking and Resource Management

**See:** docs/adrs/README.md for complete ADR index and implementation sequence

### Specifications (To Be Created)
- Context Assembly Service Specification
- Session Management Service Specification
- Provider Adapter Interface Specification
- Sub-Agent Protocol Specification
- Quality Gate Validation Specification
- Evidence Tracking Specification
- Audit System Specification

### Guides (To Be Created)
- Provider Integration Guide (Claude Code)
- Provider Integration Guide (Cursor)
- Provider Integration Guide (Aider)
- Sub-Agent Development Guide
- Plugin Development Guide
- Quality Gate Configuration Guide

---

**Document Status:** DRAFT v1.0
**Next Steps:** Review → ADR Creation → Implementation Planning
**Owner:** AIPM Development Team
**Last Updated:** 2025-10-12
