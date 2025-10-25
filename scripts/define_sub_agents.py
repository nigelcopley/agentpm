#!/usr/bin/env python3
"""
Define all sub-agents in the APM (Agent Project Manager) database using AgentBuilder API.

Sub-agents are Tier 1 agents with single responsibilities that execute
specific tasks within phase workflows. They report to mini-orchestrators
and never orchestrate themselves.

Usage:
    python scripts/define_sub_agents.py

Architecture:
    - Tier: 1 (Sub-Agent)
    - Orchestrator Type: NULL (not orchestrators)
    - Execution Mode: sequential (focused execution)
    - Symbol Mode: True (token efficiency)
    - Reports To: Appropriate mini-orchestrator
"""

import sys
from pathlib import Path
from typing import Optional, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentpm.core.agents.builder import AgentBuilder
from agentpm.core.database.service import DatabaseService


# Agent definitions organized by phase
SUB_AGENTS = [
    # ========== DEFINITION PHASE ==========
    {
        "role": "intent-triage",
        "display_name": "Intent Triage Agent",
        "description": "Classifies incoming requests into work item types (FEATURE/ANALYSIS/OBJECTIVE) and urgency levels",
        "sop": """1. Read incoming request artifact
2. Analyze language patterns and requirements
3. Classify as FEATURE, ANALYSIS, or OBJECTIVE
4. Assess urgency (critical/high/medium/low)
5. Extract initial context requirements
6. Return classification + confidence score""",
        "reports_to": "definition-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "context-assembler",
        "display_name": "Context Assembly Agent",
        "description": "Gathers and assembles relevant context from database, filesystem, and external sources",
        "sop": """1. Receive context requirements from triage
2. Query database for related work items/tasks
3. Search filesystem for relevant artifacts
4. Fetch external documentation if needed
5. Calculate context confidence score
6. Package context bundle with evidence""",
        "reports_to": "definition-orch",
        "tool": {"name": "context7", "phase": "discovery"}
    },
    {
        "role": "problem-framer",
        "display_name": "Problem Framing Agent",
        "description": "Articulates clear problem statements and frames issues for solution design",
        "sop": """1. Analyze assembled context
2. Identify core problem(s) to solve
3. Frame problem in user/business terms
4. Document current vs desired state
5. Identify stakeholders affected
6. Return structured problem statement""",
        "reports_to": "definition-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "value-articulator",
        "display_name": "Value Articulation Agent",
        "description": "Defines business value, success metrics, and ROI for proposed work",
        "sop": """1. Analyze problem statement
2. Identify quantifiable benefits
3. Define success metrics (KPIs)
4. Estimate effort/value ratio
5. Document assumptions about value
6. Return value proposition with evidence""",
        "reports_to": "definition-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "ac-writer",
        "display_name": "Acceptance Criteria Writer",
        "description": "Creates clear, testable acceptance criteria (minimum 3) for work items",
        "sop": """1. Review problem and value statements
2. Generate testable criteria (Given/When/Then)
3. Ensure minimum 3 criteria per work item
4. Validate criteria are measurable
5. Link criteria to success metrics
6. Return structured AC list""",
        "reports_to": "definition-orch"
    },
    {
        "role": "risk-notary",
        "display_name": "Risk Notary Agent",
        "description": "Identifies and documents technical, business, and operational risks",
        "sop": """1. Analyze problem and proposed solution
2. Identify technical risks (complexity, debt)
3. Identify business risks (market, value)
4. Assess operational risks (deploy, support)
5. Score each risk (probability × impact)
6. Return risk register with mitigations""",
        "reports_to": "definition-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },

    # ========== PLANNING PHASE ==========
    {
        "role": "decomposer",
        "display_name": "Task Decomposition Agent",
        "description": "Breaks work items into time-boxed tasks (≤4h) aligned with acceptance criteria",
        "sop": """1. Review work item and acceptance criteria
2. Decompose into atomic tasks (≤4h each)
3. Map tasks to AC (ensure full coverage)
4. Sequence tasks by dependencies
5. Identify parallel execution opportunities
6. Return task breakdown with AC mapping""",
        "reports_to": "planning-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "estimator",
        "display_name": "Effort Estimation Agent",
        "description": "Provides evidence-based effort estimates with confidence intervals",
        "sop": """1. Analyze task complexity and scope
2. Query historical similar tasks
3. Calculate baseline estimate
4. Apply complexity multipliers
5. Add confidence interval (±hours)
6. Return estimate with evidence""",
        "reports_to": "planning-orch"
    },
    {
        "role": "dependency-mapper",
        "display_name": "Dependency Mapping Agent",
        "description": "Maps task dependencies and identifies critical path",
        "sop": """1. Analyze all tasks in plan
2. Identify technical dependencies
3. Identify resource dependencies
4. Map external dependencies (APIs, services)
5. Calculate critical path
6. Return dependency graph with blocking chains""",
        "reports_to": "planning-orch"
    },
    {
        "role": "mitigation-planner",
        "display_name": "Risk Mitigation Planner",
        "description": "Creates mitigation strategies for identified risks",
        "sop": """1. Review risk register from Definition
2. For each high-severity risk, design mitigation
3. Create contingency plans (Plan B)
4. Define risk monitoring metrics
5. Assign risk owners
6. Return mitigation plan with triggers""",
        "reports_to": "planning-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "backlog-curator",
        "display_name": "Backlog Curator Agent",
        "description": "Organizes and prioritizes task backlog for execution",
        "sop": """1. Receive decomposed tasks
2. Apply priority scoring (value × urgency)
3. Sequence by dependencies and priorities
4. Group related tasks for efficiency
5. Validate against resource capacity
6. Return prioritized backlog ready for execution""",
        "reports_to": "planning-orch"
    },

    # ========== IMPLEMENTATION PHASE ==========
    {
        "role": "pattern-applier",
        "display_name": "Design Pattern Applier",
        "description": "Applies architectural patterns and design principles to implementation",
        "sop": """1. Analyze task technical requirements
2. Identify applicable design patterns
3. Retrieve pattern templates from context
4. Validate pattern fit with architecture
5. Document pattern application rationale
6. Return pattern specification for implementation""",
        "reports_to": "implementation-orch",
        "tool": {"name": "context7", "phase": "discovery"}
    },
    {
        "role": "code-implementer",
        "display_name": "Code Implementation Agent",
        "description": "Writes production-quality code following project standards and patterns",
        "sop": """1. Review task specification and patterns
2. Write implementation code
3. Apply code quality standards (CI-003)
4. Add inline documentation
5. Create feature flags if needed
6. Return code artifacts with evidence""",
        "reports_to": "implementation-orch"
    },
    {
        "role": "test-implementer",
        "display_name": "Test Implementation Agent",
        "description": "Creates comprehensive tests-BAK meeting CI-004 coverage requirements (>90%)",
        "sop": """1. Review implementation and AC
2. Write unit tests-BAK (>90% coverage)
3. Write integration tests-BAK for interactions
4. Add edge case and error handling tests-BAK
5. Validate tests-BAK against AC
6. Return test suite with coverage report""",
        "reports_to": "implementation-orch"
    },
    {
        "role": "migration-author",
        "display_name": "Migration Authoring Agent",
        "description": "Creates database migrations and data transformation scripts",
        "sop": """1. Detect schema changes from implementation
2. Generate forward migration script
3. Generate rollback migration script
4. Validate migration safety (backups, locks)
5. Test migration on dev environment
6. Return migration artifacts with safety checklist""",
        "reports_to": "implementation-orch"
    },
    {
        "role": "doc-toucher",
        "display_name": "Documentation Touch Agent",
        "description": "Updates documentation to reflect implementation changes (CI-006)",
        "sop": """1. Identify documentation affected by changes
2. Update API/module documentation
3. Update README and guides if needed
4. Generate docstrings for new code
5. Validate documentation completeness (CI-006)
6. Return documentation artifacts""",
        "reports_to": "implementation-orch"
    },

    # ========== REVIEW/TEST PHASE ==========
    {
        "role": "static-analyzer",
        "display_name": "Static Analysis Agent",
        "description": "Runs static analysis tools (linters, type checkers, complexity metrics)",
        "sop": """1. Run linters (ruff, pylint) on changed files
2. Run type checkers (mypy, pyright)
3. Calculate complexity metrics (cyclomatic)
4. Check code style compliance
5. Aggregate findings by severity
6. Return analysis report with violations""",
        "reports_to": "review-test-orch"
    },
    {
        "role": "test-runner",
        "display_name": "Test Execution Agent",
        "description": "Executes test suites and generates coverage reports",
        "sop": """1. Run unit test suite with coverage
2. Run integration test suite
3. Generate coverage report (must be >90%)
4. Identify untested code paths
5. Check test execution time (<threshold)
6. Return test results with coverage metrics""",
        "reports_to": "review-test-orch"
    },
    {
        "role": "threat-screener",
        "display_name": "Security Threat Screener",
        "description": "Scans for security vulnerabilities and compliance issues (CI-005)",
        "sop": """1. Run security scanners (bandit, safety)
2. Check for known vulnerabilities in deps
3. Validate input sanitization
4. Check authentication/authorization
5. Scan for hardcoded secrets
6. Return security report with risk scores""",
        "reports_to": "review-test-orch"
    },
    {
        "role": "ac-verifier",
        "display_name": "Acceptance Criteria Verifier",
        "description": "Validates that all acceptance criteria are met by implementation",
        "sop": """1. Load work item acceptance criteria
2. Map each AC to implementation/tests-BAK
3. Execute AC validation tests-BAK
4. Document evidence for each AC
5. Calculate AC satisfaction score
6. Return verification report (pass/fail per AC)""",
        "reports_to": "review-test-orch"
    },
    {
        "role": "quality-gatekeeper",
        "display_name": "Quality Gate Evaluation Agent",
        "description": "Evaluates all quality gates (R1) and makes pass/fail decision",
        "sop": """1. Collect all quality check results
2. Evaluate CI-003 (code quality)
3. Evaluate CI-004 (test coverage >90%)
4. Evaluate CI-005 (security)
5. Check AC verification results
6. Return gate status (PASS/FAIL) with evidence""",
        "reports_to": "review-test-orch"
    },

    # ========== RELEASE/OPS PHASE ==========
    {
        "role": "versioner",
        "display_name": "Version Management Agent",
        "description": "Determines semantic version bump and manages version artifacts",
        "sop": """1. Analyze changes (breaking/feature/fix)
2. Calculate semantic version bump
3. Update version files (setup.py, __init__.py)
4. Create version tag
5. Validate version consistency
6. Return version artifacts""",
        "reports_to": "release-ops-orch"
    },
    {
        "role": "changelog-curator",
        "display_name": "Changelog Curation Agent",
        "description": "Generates user-facing changelog entries from work items",
        "sop": """1. Collect completed work items in release
2. Categorize changes (Added/Changed/Fixed)
3. Write user-facing descriptions
4. Link to relevant documentation
5. Format according to Keep a Changelog
6. Return changelog section for version""",
        "reports_to": "release-ops-orch"
    },
    {
        "role": "deploy-orchestrator",
        "display_name": "Deployment Orchestration Agent",
        "description": "Coordinates deployment steps and manages rollback procedures",
        "sop": """1. Execute pre-deployment checks
2. Run database migrations if needed
3. Deploy code artifacts to target environment
4. Run post-deployment smoke tests-BAK
5. Verify deployment health
6. Return deployment status with rollback plan""",
        "reports_to": "release-ops-orch"
    },
    {
        "role": "health-verifier",
        "display_name": "System Health Verifier",
        "description": "Validates system health post-deployment and monitors key metrics",
        "sop": """1. Run health check endpoints
2. Verify critical user flows work
3. Check error rates and latency
4. Validate monitoring/alerting active
5. Compare metrics to baseline
6. Return health report (healthy/degraded/failing)""",
        "reports_to": "release-ops-orch"
    },
    {
        "role": "incident-scribe",
        "display_name": "Incident Documentation Agent",
        "description": "Documents deployment incidents and creates postmortem artifacts",
        "sop": """1. Detect deployment failure or degradation
2. Document incident timeline
3. Capture error logs and metrics
4. Record mitigation actions taken
5. Create incident ticket
6. Return incident report for review""",
        "reports_to": "release-ops-orch"
    },

    # ========== EVOLUTION PHASE ==========
    {
        "role": "signal-harvester",
        "display_name": "Telemetry Signal Harvester",
        "description": "Collects telemetry, user feedback, and operational metrics",
        "sop": """1. Query production metrics/logs
2. Collect user feedback from channels
3. Analyze error rates and patterns
4. Track feature usage statistics
5. Identify anomalies and trends
6. Return signal snapshot with highlights""",
        "reports_to": "evolution-orch"
    },
    {
        "role": "insight-synthesizer",
        "display_name": "Insight Synthesis Agent",
        "description": "Transforms signals into actionable insights and improvement opportunities",
        "sop": """1. Analyze harvested signals
2. Identify patterns and correlations
3. Link signals to outcomes (success/failure)
4. Generate hypotheses for improvements
5. Prioritize insights by impact
6. Return insight report with recommendations""",
        "reports_to": "evolution-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "debt-registrar",
        "display_name": "Technical Debt Registrar",
        "description": "Tracks and quantifies technical debt with cost/benefit analysis",
        "sop": """1. Identify tech debt from code/signals
2. Classify debt by type (code/arch/test/doc)
3. Estimate cost to fix (hours)
4. Estimate cost of delay (risk × time)
5. Calculate debt priority score
6. Return debt register with recommendations""",
        "reports_to": "evolution-orch"
    },
    {
        "role": "refactor-proposer",
        "display_name": "Refactoring Proposal Agent",
        "description": "Proposes refactoring work items to address debt and improve quality",
        "sop": """1. Review debt register and insights
2. Identify refactoring opportunities
3. Design refactoring approach (strategy)
4. Estimate effort and risk
5. Define success criteria for refactor
6. Return refactor proposal as work item draft""",
        "reports_to": "evolution-orch",
        "tool": {"name": "sequential-thinking", "phase": "reasoning"}
    },
    {
        "role": "sunset-planner",
        "display_name": "Feature Sunset Planner",
        "description": "Plans deprecation and removal of unused or obsolete features",
        "sop": """1. Identify low-usage features
2. Analyze maintenance cost vs value
3. Design deprecation timeline
4. Plan user migration path
5. Estimate removal effort/risk
6. Return sunset plan as work item""",
        "reports_to": "evolution-orch"
    },

    # ========== UTILITY AGENTS ==========
    {
        "role": "workitem-writer",
        "display_name": "WorkItem Writer Agent",
        "description": "Writes and updates work items in database with validation",
        "sop": """1. Receive work item data structure
2. Validate required fields present
3. Validate state transitions allowed
4. Write to database with transaction
5. Update relationships (parent/children)
6. Return work item ID with confirmation""",
        "reports_to": "multiple-orchestrators"
    },
    {
        "role": "evidence-writer",
        "display_name": "Evidence Writer Agent",
        "description": "Persists evidence artifacts and maintains evidence chains",
        "sop": """1. Receive evidence entry with metadata
2. Hash evidence content (sha256)
3. Write to artifact storage
4. Link evidence to work item/task
5. Update evidence chain
6. Return evidence reference ID""",
        "reports_to": "multiple-orchestrators"
    },
    {
        "role": "audit-logger",
        "display_name": "Audit Logging Agent",
        "description": "Records all agent actions and state changes for compliance",
        "sop": """1. Receive action/state change event
2. Capture timestamp, agent, action, artifact
3. Write to audit log (append-only)
4. Update audit index for querying
5. Verify write integrity
6. Return audit entry ID""",
        "reports_to": "multiple-orchestrators"
    },

    # ========== GATE CHECK AGENTS ==========
    {
        "role": "definition-gate-check",
        "display_name": "Definition Gate Check Agent",
        "description": "Evaluates Definition phase gate (D1): why_value + AC≥3 + risks",
        "sop": """1. Verify why_value articulated
2. Count acceptance criteria (must be ≥3)
3. Verify risk register present with scores
4. Check context confidence ≥0.70
5. Validate evidence completeness
6. Return gate status (PASS/FAIL) with missing items""",
        "reports_to": "definition-orch"
    },
    {
        "role": "planning-gate-check",
        "display_name": "Planning Gate Check Agent",
        "description": "Evaluates Planning phase gate (P1): steps↔AC + estimates + deps + mitigations",
        "sop": """1. Verify all AC mapped to tasks
2. Check all tasks have estimates (≤4h)
3. Verify dependencies identified
4. Check mitigation plans for high risks
5. Validate backlog prioritization
6. Return gate status (PASS/FAIL) with gaps""",
        "reports_to": "planning-orch"
    },
    {
        "role": "implementation-gate-check",
        "display_name": "Implementation Gate Check Agent",
        "description": "Evaluates Implementation phase gate (I1): tests-BAK + flags + docs + migrations",
        "sop": """1. Verify tests-BAK present (unit + integration)
2. Check feature flags created if needed
3. Validate documentation updated (CI-006)
4. Verify migrations present for schema changes
5. Check code quality standards met
6. Return gate status (PASS/FAIL) with missing artifacts""",
        "reports_to": "implementation-orch"
    },
    {
        "role": "evolution-gate-check",
        "display_name": "Evolution Gate Check Agent",
        "description": "Evaluates Evolution phase gate (E1): metric/risk link + outcome + priority",
        "sop": """1. Verify insights linked to metrics
2. Check outcome tracking defined
3. Validate priority scoring applied
4. Ensure proposals have effort estimates
5. Check debt register updated
6. Return gate status (PASS/FAIL) with gaps""",
        "reports_to": "evolution-orch"
    },
    {
        "role": "operability-gatecheck",
        "display_name": "Operability Gate Check Agent",
        "description": "Evaluates Release/Ops phase gate (O1): version + changelog + rollback + monitors",
        "sop": """1. Verify version bumped correctly
2. Check changelog generated
3. Validate rollback procedure defined
4. Verify monitoring/alerting active
5. Check deployment health verified
6. Return gate status (PASS/FAIL) with missing items""",
        "reports_to": "release-ops-orch"
    },
]


def main():
    """Define all sub-agents in the database."""

    print("=" * 60)
    print("APM (Agent Project Manager) Sub-Agent Definition Script")
    print("=" * 60)
    print(f"\nDefining {len(SUB_AGENTS)} sub-agents in database...")

    # Initialize database service
    db_service = DatabaseService("~/.aipm/data/aipm.db")

    # Use transaction context for all operations
    with db_service.transaction() as conn:
        try:
            # Initialize AgentBuilder
            builder = AgentBuilder(conn)

            # Create all agents
            phase_counts = {}
            for agent_def in SUB_AGENTS:
                # Extract phase from reports_to
                reports_to = agent_def.get("reports_to", "unknown")
                phase = reports_to.replace("-orch", "").replace("multiple-", "utility/")
                phase_counts[phase] = phase_counts.get(phase, 0) + 1

                # Create agent
                agent = builder.define_agent(
                    role=agent_def["role"],
                    display_name=agent_def["display_name"],
                    description=agent_def["description"],
                    tier=1,
                    orchestrator_type=None,
                    execution_mode="sequential",
                    symbol_mode=True,
                    sop_content=agent_def["sop"],
                    is_active=True
                )

                print(f"  ✅ {agent_def['role']:<30} (phase: {phase})")

                # Add tool if specified
                if "tool" in agent_def:
                    tool = agent_def["tool"]
                    builder.add_tool(
                        agent.id,
                        tool["name"],
                        tool["phase"],
                        priority=1
                    )

                # Add relationship
                if reports_to != "multiple-orchestrators":
                    # Will be added later when orchestrators exist
                    pass

            # Commit happens automatically when transaction context exits without exception
            print("\n" + "=" * 60)
            print("✅ SUCCESS: All sub-agents defined in database")
            print("=" * 60)

            # Summary statistics
            cursor = conn.execute("SELECT COUNT(*) FROM agents WHERE tier = 1")
            sub_agent_count = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM agents WHERE tier = 1 AND symbol_mode = 1")
            symbol_mode_count = cursor.fetchone()[0]

            print(f"\n📊 Summary:")
            print(f"  • Total sub-agents created: {len(SUB_AGENTS)}")
            print(f"  • Total Tier 1 agents in DB: {sub_agent_count}")
            print(f"  • Symbol mode enabled: {symbol_mode_count}")
            print(f"\n📋 By Phase:")
            for phase, count in sorted(phase_counts.items()):
                print(f"  • {phase:20} {count} agents")

            print(f"\n⚠️  Note: Relationships to orchestrators will be added after orchestrators are defined")
            print("\n🔍 Verify with:")
            print("  SELECT role, display_name, tier, execution_mode, symbol_mode FROM agents WHERE tier = 1;")

        except Exception as e:
            # Transaction will auto-rollback on exception
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
