#!/usr/bin/env python3
"""
Generate All Agents - Three-Tier Agent Architecture Setup

Orchestrates the complete agent system setup:
1. Run database migration (migration_0014) if not already applied
2. Define mini-orchestrators (6 agents)
3. Define sub-agents (~25 agents)
4. Generate all agent .md files via CLI
5. Validate generated files
6. Report summary statistics

Author: WI-46 (Three-Tier Agent Architecture)
Date: 2025-10-12
"""

import sys
import subprocess
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import json

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.migrations.manager import MigrationManager


@dataclass
class AgentDefinition:
    """Agent definition for database insertion"""
    role: str
    tier: int
    description: str
    orchestrator_type: Optional[str] = None
    execution_mode: str = "parallel"
    symbol_mode: bool = True


@dataclass
class GenerationResult:
    """Result of agent generation process"""
    total_defined: int
    files_generated: int
    files_validated: int
    mini_orchestrators: List[str]
    sub_agents: List[str]
    errors: List[str]


class AgentSystemGenerator:
    """Orchestrates complete agent system setup"""

    def __init__(self, db_path: Path = None, project_id: int = None):
        """Initialize generator with database path"""
        if db_path is None:
            db_path = PROJECT_ROOT / ".aipm" / "data" / "aipm.db"

        self.db_path = db_path
        self.db_service = DatabaseService(str(db_path))
        self.migration_manager = MigrationManager(self.db_service)

        # Get project_id
        if project_id is None:
            with self.db_service.connect() as conn:
                cursor = conn.execute("SELECT id FROM projects LIMIT 1")
                row = cursor.fetchone()
                if row:
                    self.project_id = row[0]
                else:
                    raise ValueError("No project found in database")
        else:
            self.project_id = project_id

        # Output directories
        self.agent_dir = PROJECT_ROOT / ".claude" / "agents"
        self.orch_dir = self.agent_dir / "orchestrators"
        self.specialists_dir = self.agent_dir / "specialists"
        self.sub_agent_dir = self.agent_dir / "sub-agents"

    def check_migration_status(self) -> bool:
        """Check if migration_0014 is already applied"""
        print("Checking migration status...")

        migrations = self.migration_manager.discover_migrations()
        migration_0014 = next((m for m in migrations if m.version == "0014"), None)

        if migration_0014 is None:
            print("❌ Migration 0014 not found in migrations directory")
            return False

        if migration_0014.applied:
            print("✅ Migration 0014 already applied")
            return True

        print("⚠️  Migration 0014 not yet applied")
        return False

    def run_migration(self) -> bool:
        """Run migration_0014 if not already applied"""
        try:
            if self.check_migration_status():
                return True

            print("Running migration_0014...")

            pending = [m for m in self.migration_manager.get_pending_migrations()
                      if m.version == "0014"]

            if not pending:
                print("❌ Migration 0014 not in pending list")
                return False

            success = self.migration_manager.run_migration(pending[0])

            if success:
                print("✅ Migration 0014 applied successfully")

                # Verify schema changes
                with self.db_service.connect() as conn:
                    cursor = conn.execute("PRAGMA table_info(agents)")
                    columns = {row[1] for row in cursor.fetchall()}

                    required = ['execution_mode', 'symbol_mode', 'orchestrator_type', 'agent_file_path']
                    missing = [col for col in required if col not in columns]

                    if missing:
                        print(f"❌ Missing columns after migration: {missing}")
                        return False

                    print(f"✅ Schema validated: {len(required)} new columns added")

            return success

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

    def define_mini_orchestrators(self) -> List[str]:
        """Define 6 mini-orchestrator agents in database"""
        print("\nDefining mini-orchestrators...")

        orchestrators = [
            AgentDefinition(
                role="definition-orch",
                tier=2,
                description="Definition Phase Orchestrator - Drives requirements definition until gate D1 passes",
                orchestrator_type="mini",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="planning-orch",
                tier=2,
                description="Planning Phase Orchestrator - Drives planning until gate P1 passes",
                orchestrator_type="mini",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="implementation-orch",
                tier=2,
                description="Implementation Phase Orchestrator - Drives implementation until gate I1 passes",
                orchestrator_type="mini",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="review-test-orch",
                tier=2,
                description="Review & Testing Orchestrator - Drives quality validation until gate R1 passes",
                orchestrator_type="mini",
                execution_mode="sequential"  # Quality checks are sequential
            ),
            AgentDefinition(
                role="release-ops-orch",
                tier=2,
                description="Release & Operations Orchestrator - Drives deployment until gate O1 passes",
                orchestrator_type="mini",
                execution_mode="sequential"  # Deployment is sequential
            ),
            AgentDefinition(
                role="evolution-orch",
                tier=2,
                description="Evolution Phase Orchestrator - Drives continuous improvement until gate E1 passes",
                orchestrator_type="mini",
                execution_mode="parallel"
            ),
        ]

        created = []

        with self.db_service.connect() as conn:
            for orch in orchestrators:
                try:
                    # Check if already exists
                    cursor = conn.execute(
                        "SELECT id FROM agents WHERE role = ?",
                        (orch.role,)
                    )

                    if cursor.fetchone():
                        print(f"  ⚠️  {orch.role} already exists, skipping")
                        created.append(orch.role)
                        continue

                    # Insert new orchestrator
                    display_name = orch.role.replace("-", " ").title()
                    conn.execute("""
                        INSERT INTO agents (
                            project_id, role, display_name, tier, description, is_active,
                            orchestrator_type, execution_mode, symbol_mode,
                            agent_file_path
                        ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
                    """, (
                        self.project_id,
                        orch.role,
                        display_name,
                        orch.tier,
                        orch.description,
                        orch.orchestrator_type,
                        orch.execution_mode,
                        1 if orch.symbol_mode else 0,
                        f".claude/agents/orchestrators/{orch.role}.md"
                    ))

                    conn.commit()
                    print(f"  ✅ {orch.role} defined")
                    created.append(orch.role)

                except Exception as e:
                    print(f"  ❌ Failed to define {orch.role}: {e}")

        print(f"✅ Mini-orchestrators defined: {len(created)}/6")
        return created

    def define_sub_agents(self) -> List[str]:
        """Define ~25 sub-agent agents in database"""
        print("\nDefining sub-agents...")

        # Sub-agents organized by category
        sub_agents = [
            # Context & Discovery (2 agents)
            AgentDefinition(
                role="context-delivery",
                tier=1,
                description="Context Agent - Assembles session context from database (MANDATORY at session start)",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="discovery-orch",
                tier=1,
                description="Discovery Orchestrator - Coordinates external/internal/risk discovery when confidence < threshold",
                execution_mode="parallel"
            ),

            # Definition Phase Sub-Agents (5 agents)
            AgentDefinition(
                role="intent-triage",
                tier=1,
                description="Intent Triage - Analyzes incoming requests and routes to appropriate phase",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="problem-framer",
                tier=1,
                description="Problem Framer - Articulates problem context and constraints",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="value-articulator",
                tier=1,
                description="Value Articulator - Documents business value and success metrics",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="ac-writer",
                tier=1,
                description="Acceptance Criteria Writer - Creates testable acceptance criteria (≥3 required)",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="risk-notary",
                tier=1,
                description="Risk Notary - Identifies and documents technical/business risks",
                execution_mode="parallel"
            ),

            # Planning Phase Sub-Agents (5 agents)
            AgentDefinition(
                role="decomposer",
                tier=1,
                description="Task Decomposer - Breaks work into time-boxed tasks (≤4h each)",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="estimator",
                tier=1,
                description="Effort Estimator - Provides realistic effort estimates with uncertainty",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="dependency-mapper",
                tier=1,
                description="Dependency Mapper - Identifies task dependencies and critical path",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="mitigation-planner",
                tier=1,
                description="Mitigation Planner - Creates risk mitigation strategies",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="backlog-curator",
                tier=1,
                description="Backlog Curator - Organizes and prioritizes work items",
                execution_mode="sequential"
            ),

            # Implementation Phase Sub-Agents (5 agents)
            AgentDefinition(
                role="pattern-applier",
                tier=1,
                description="Pattern Applier - Applies architectural patterns and best practices",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="code-implementer",
                tier=1,
                description="Code Implementer - Writes production-ready code following standards",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="test-implementer",
                tier=1,
                description="Test Implementer - Creates comprehensive test suites (unit/integration)",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="migration-author",
                tier=1,
                description="Migration Author - Creates database migrations with rollback support",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="doc-toucher",
                tier=1,
                description="Documentation Toucher - Updates affected documentation and examples",
                execution_mode="parallel"
            ),

            # Review & Test Phase Sub-Agents (4 agents)
            AgentDefinition(
                role="static-analyzer",
                tier=1,
                description="Static Analyzer - Runs linting, type checking, and code quality analysis",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="test-runner",
                tier=1,
                description="Test Runner - Executes test suites and validates coverage",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="threat-screener",
                tier=1,
                description="Security Screener - Performs security and vulnerability analysis",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="ac-verifier",
                tier=1,
                description="AC Verifier - Validates all acceptance criteria are met",
                execution_mode="sequential"
            ),

            # Release & Ops Phase Sub-Agents (4 agents)
            AgentDefinition(
                role="versioner",
                tier=1,
                description="Version Manager - Handles semantic versioning and tagging",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="changelog-curator",
                tier=1,
                description="Changelog Curator - Maintains structured changelog entries",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="deploy-orchestrator",
                tier=1,
                description="Deployment Orchestrator - Manages deployment process and verification",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="health-verifier",
                tier=1,
                description="Health Verifier - Validates system health post-deployment",
                execution_mode="sequential"
            ),

            # Evolution Phase Sub-Agents (3 agents)
            AgentDefinition(
                role="signal-harvester",
                tier=1,
                description="Signal Harvester - Collects telemetry and user feedback",
                execution_mode="parallel"
            ),
            AgentDefinition(
                role="insight-synthesizer",
                tier=1,
                description="Insight Synthesizer - Analyzes patterns and generates recommendations",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="debt-registrar",
                tier=1,
                description="Technical Debt Registrar - Tracks and prioritizes technical debt",
                execution_mode="parallel"
            ),

            # Gate Check Agents (6 agents - one per phase)
            AgentDefinition(
                role="definition-gate-check",
                tier=1,
                description="Definition Gate Checker - Validates D1 gate requirements",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="planning-gate-check",
                tier=1,
                description="Planning Gate Checker - Validates P1 gate requirements",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="implementation-gate-check",
                tier=1,
                description="Implementation Gate Checker - Validates I1 gate requirements",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="quality-gatekeeper",
                tier=1,
                description="Quality Gatekeeper - Validates R1 gate requirements",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="operability-gatecheck",
                tier=1,
                description="Operability Gatekeeper - Validates O1 gate requirements",
                execution_mode="sequential"
            ),
            AgentDefinition(
                role="evolution-gate-check",
                tier=1,
                description="Evolution Gate Checker - Validates E1 gate requirements",
                execution_mode="sequential"
            ),
        ]

        created = []

        with self.db_service.connect() as conn:
            for agent in sub_agents:
                try:
                    # Check if already exists
                    cursor = conn.execute(
                        "SELECT id FROM agents WHERE role = ?",
                        (agent.role,)
                    )

                    if cursor.fetchone():
                        print(f"  ⚠️  {agent.role} already exists, skipping")
                        created.append(agent.role)
                        continue

                    # Insert new sub-agent
                    display_name = agent.role.replace("-", " ").title()
                    conn.execute("""
                        INSERT INTO agents (
                            project_id, role, display_name, tier, description, is_active,
                            orchestrator_type, execution_mode, symbol_mode,
                            agent_file_path
                        ) VALUES (?, ?, ?, ?, ?, 1, NULL, ?, ?, ?)
                    """, (
                        self.project_id,
                        agent.role,
                        display_name,
                        agent.tier,
                        agent.description,
                        agent.execution_mode,
                        1 if agent.symbol_mode else 0,
                        f".claude/agents/sub-agents/{agent.role}.md"
                    ))

                    conn.commit()
                    print(f"  ✅ {agent.role} defined")
                    created.append(agent.role)

                except Exception as e:
                    print(f"  ❌ Failed to define {agent.role}: {e}")

        print(f"✅ Sub-agents defined: {len(created)}/{len(sub_agents)}")
        return created

    def generate_agent_files(self) -> Tuple[int, List[str]]:
        """Generate all agent .md files via CLI"""
        print("\nGenerating agent files...")

        try:
            # Run CLI command: apm agents generate --all --llm claude
            result = subprocess.run(
                ["apm", "agents", "generate", "--all", "--llm", "claude"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                print(f"❌ Generation failed:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return 0, []

            # Parse output to count generated files
            output = result.stdout
            print(output)

            # Count files in directories
            orch_files = list(self.orch_dir.glob("*.md")) if self.orch_dir.exists() else []
            specialist_files = list(self.specialists_dir.glob("*.md")) if self.specialists_dir.exists() else []
            sub_agent_files = list(self.sub_agent_dir.glob("*.md")) if self.sub_agent_dir.exists() else []

            total_generated = len(orch_files) + len(specialist_files) + len(sub_agent_files)

            print(f"✅ Generated {total_generated} agent files")
            print(f"  - Orchestrators: {len(orch_files)}")
            print(f"  - Specialists: {len(specialist_files)}")
            print(f"  - Sub-agents: {len(sub_agent_files)}")

            return total_generated, [f.name for f in orch_files + sub_agent_files]

        except subprocess.TimeoutExpired:
            print("❌ Generation timed out after 5 minutes")
            return 0, []
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return 0, []

    def validate_generated_files(self) -> Tuple[int, List[str]]:
        """Validate generated files exist in correct locations"""
        print("\nValidating generated files...")

        errors = []
        validated_count = 0

        # Check orchestrators directory (master orchestrator)
        if not self.orch_dir.exists():
            errors.append("Orchestrators directory missing")
        else:
            orch_files = list(self.orch_dir.glob("*.md"))
            print(f"  ✅ Found {len(orch_files)} master orchestrator files")
            validated_count += len(orch_files)

            # Check for master orchestrator
            if not (self.orch_dir / "master-orchestrator.md").exists():
                errors.append("Missing master-orchestrator.md")

        # Check specialists directory (mini-orchestrators)
        if not self.specialists_dir.exists():
            errors.append("Specialists directory missing")
        else:
            specialist_files = list(self.specialists_dir.glob("*.md"))
            print(f"  ✅ Found {len(specialist_files)} specialist files (mini-orchestrators)")
            validated_count += len(specialist_files)

            # Check for mini-orchestrators
            expected_orchs = [
                "definition-orch.md",
                "planning-orch.md",
                "implementation-orch.md",
                "review-test-orch.md",
                "release-ops-orch.md",
                "evolution-orch.md"
            ]

            for expected in expected_orchs:
                if not (self.specialists_dir / expected).exists():
                    errors.append(f"Missing mini-orchestrator: {expected}")

        # Check sub-agents directory
        if not self.sub_agent_dir.exists():
            errors.append("Sub-agents directory missing")
        else:
            sub_files = list(self.sub_agent_dir.glob("*.md"))
            print(f"  ✅ Found {len(sub_files)} sub-agent files")
            validated_count += len(sub_files)

            # Check critical sub-agents
            critical = [
                "context-delivery.md",
                "definition-gate-check.md",
                "planning-gate-check.md",
                "implementation-gate-check.md",
                "quality-gatekeeper.md"
            ]

            for critical_agent in critical:
                if not (self.sub_agent_dir / critical_agent).exists():
                    errors.append(f"Missing critical sub-agent: {critical_agent}")

        if errors:
            print(f"⚠️  Validation warnings ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✅ All files validated successfully")

        return validated_count, errors

    def run(self) -> GenerationResult:
        """Run complete agent system setup"""
        print("=" * 60)
        print("APM (Agent Project Manager) - Three-Tier Agent System Setup")
        print("=" * 60)

        result = GenerationResult(
            total_defined=0,
            files_generated=0,
            files_validated=0,
            mini_orchestrators=[],
            sub_agents=[],
            errors=[]
        )

        # Step 1: Run migration
        print("\n[1/5] Running database migration...")
        if not self.run_migration():
            result.errors.append("Migration failed")
            return result

        # Step 2: Define mini-orchestrators
        print("\n[2/5] Defining mini-orchestrators...")
        result.mini_orchestrators = self.define_mini_orchestrators()

        # Step 3: Define sub-agents
        print("\n[3/5] Defining sub-agents...")
        result.sub_agents = self.define_sub_agents()

        result.total_defined = len(result.mini_orchestrators) + len(result.sub_agents)

        # Step 4: Generate files
        print("\n[4/5] Generating agent .md files...")
        files_generated, generated_files = self.generate_agent_files()
        result.files_generated = files_generated

        # Step 5: Validate files
        print("\n[5/5] Validating generated files...")
        validated_count, validation_errors = self.validate_generated_files()
        result.files_validated = validated_count
        result.errors.extend(validation_errors)

        return result

    def print_summary(self, result: GenerationResult):
        """Print summary statistics"""
        print("\n" + "=" * 60)
        print("GENERATION SUMMARY")
        print("=" * 60)

        print(f"\n📊 Statistics:")
        print(f"  Total agents defined: {result.total_defined}")
        print(f"  - Mini-orchestrators:  {len(result.mini_orchestrators)}")
        print(f"  - Sub-agents:          {len(result.sub_agents)}")
        print(f"  Files generated:       {result.files_generated}")
        print(f"  Files validated:       {result.files_validated}")

        if result.errors:
            print(f"\n⚠️  Warnings ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ All validation checks passed")

        print(f"\n📁 Output Locations:")
        print(f"  Master Orchestrator: {self.orch_dir}")
        print(f"  Mini-Orchestrators:  {self.specialists_dir}")
        print(f"  Sub-agents:          {self.sub_agent_dir}")

        print(f"\n🎯 Next Steps:")
        print(f"  1. Review generated agent files")
        print(f"  2. Verify agent file content quality")
        print(f"  3. Test agent delegation via Task tool")
        print(f"  4. Update CLAUDE.md to reference new agents")

        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    try:
        generator = AgentSystemGenerator()
        result = generator.run()
        generator.print_summary(result)

        # Exit with error code if there were critical errors
        if any("failed" in err.lower() for err in result.errors):
            sys.exit(1)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
