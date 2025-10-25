"""
InitOrchestrator - Unified initialization orchestrator for APM projects.

Coordinates all initialization phases:
1. Pre-flight checks
2. Directory creation
3. Database initialization
4. Technology detection
5. Rules loading
6. Verification

Performance Target: <3 minutes for complete initialization
Pattern: Pydantic models for type safety
"""

import logging
import sqlite3
import os
import time
import shutil
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any

from agentpm.core.models.init_models import (
    InitProgress,
    InitResult,
    InitConfig,
    InitPhase,
    InitMode,
    DetectionSummary,
    RollbackPlan,
    RollbackAction,
)
from agentpm.core.database import DatabaseService
from agentpm.core.database.models import Project, Context, UnifiedSixW
from agentpm.core.database.enums import ProjectStatus, ContextType, EntityType
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import contexts as context_methods
from agentpm.core.detection import DetectionOrchestrator
from agentpm.core.detection.models import DetectionResult
from agentpm.core.plugins import PluginOrchestrator
from agentpm.core.rules.generator import RuleGenerationService
from agentpm.core.rules.questionnaire import QuestionnaireService
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class VerificationCheck(BaseModel):
    """Single verification check result"""
    name: str
    passed: bool
    details: str = ""
    error: str = ""
    is_critical: bool = False


class InitOrchestrator:
    """
    Orchestrates complete APM project initialization.

    Coordinates:
    - Directory structure creation
    - Database initialization
    - Technology detection
    - Plugin enrichment
    - Rules loading
    - Verification

    Uses Pydantic models for type safety throughout.
    """

    def __init__(
        self,
        config: InitConfig,
        progress_callback: Optional[Callable[[InitProgress], None]] = None,
        console: Optional[Any] = None
    ):
        """
        Initialize orchestrator with Pydantic config.

        Args:
            config: InitConfig with project details
            progress_callback: Optional progress callback
            console: Optional console for questionnaire (Rich Console)
        """
        self.config = config
        self.progress_callback = progress_callback
        self.console = console

        # State
        self.db: Optional[DatabaseService] = None
        self.project: Optional[Project] = None
        self.detection_result: Optional[DetectionResult] = None
        self.rollback_plan = RollbackPlan()
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def orchestrate(self) -> InitResult:
        """
        Execute complete initialization workflow.

        Returns:
            InitResult with status and details (Pydantic model)
        """
        start_time = time.perf_counter()

        try:
            # Phase 1: Pre-flight checks
            self._update_progress(1, 6, "Running pre-flight checks...", InitPhase.PREFLIGHT)
            self._preflight_checks()

            # Phase 2: Create directories
            self._update_progress(2, 6, "Creating directory structure...", InitPhase.DATABASE)
            self._create_directories()

            # Phase 3: Initialize database
            self._update_progress(3, 6, "Initializing database...", InitPhase.DATABASE)
            self._initialize_database()

            # Phase 4: Detect technologies
            self._update_progress(4, 6, "Detecting technologies...", InitPhase.DETECTION)
            self._detect_technologies()

            # Phase 5: Load rules
            self._update_progress(5, 6, "Loading project rules...", InitPhase.RULES)
            rules_loaded = self._load_rules()

            # Phase 6: Verify installation
            self._update_progress(6, 6, "Verifying installation...", InitPhase.VERIFICATION)
            self._verify_installation()

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Build result (Pydantic model)
            return InitResult(
                success=True,
                project_name=self.config.project_name,
                database_path=self.config.project_path / ".agentpm" / "data" / "agentpm.db",
                agents_generated=0,  # Agent generation is separate command
                rules_loaded=rules_loaded,
                technologies_detected=list(self.detection_result.matches.keys()) if self.detection_result else [],
                warnings=self.warnings if self.warnings else None,
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.exception("Initialization failed")
            self.errors.append(str(e))

            # Attempt rollback
            try:
                self.rollback()
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}", exc_info=True)
                self.errors.append(f"Rollback failed: {rollback_error}")

            # Calculate duration even on failure
            duration_ms = (time.perf_counter() - start_time) * 1000

            return InitResult(
                success=False,
                project_name=self.config.project_name,
                database_path=None,
                errors=self.errors,
                warnings=self.warnings if self.warnings else None,
                duration_ms=duration_ms
            )

    def _update_progress(self, current: int, total: int, message: str, phase: InitPhase):
        """Update progress if callback registered (uses Pydantic InitProgress)"""
        if self.progress_callback:
            progress = InitProgress(
                current_step=current,
                total_steps=total,
                message=message,
                phase=phase
            )
            self.progress_callback(progress)

        logger.info(f"[{current}/{total}] {message}")

    def _preflight_checks(self):
        """Run pre-flight validation checks"""
        # Check project path exists
        if not self.config.project_path.exists():
            raise RuntimeError(
                f"Project path does not exist: {self.config.project_path}"
            )

        if not self.config.project_path.is_dir():
            raise RuntimeError(
                f"Project path is not a directory: {self.config.project_path}"
            )

        # Check if already initialized
        aipm_dir = self.config.project_path / '.agentpm'
        if aipm_dir.exists():
            if self.config.force_reset:
                logger.warning(f"Removing existing .agentpm directory (force_reset=True)")
                shutil.rmtree(aipm_dir)
            else:
                raise RuntimeError(
                    f"Project already initialized at {self.config.project_path}. "
                    f"Use force_reset=True to reinitialize."
                )

        # Check write permissions
        try:
            test_file = self.config.project_path / ".agentpm_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            raise RuntimeError(
                f"Insufficient permissions to write to {self.config.project_path}: {e}"
            ) from e

        logger.info("Pre-flight checks passed")

    def _create_directories(self):
        """Create .agentpm directory structure with rollback tracking"""
        aipm_dir = self.config.project_path / '.agentpm'

        # Create main directory
        aipm_dir.mkdir(exist_ok=False)
        self.rollback_plan.add_action("create_directory", str(aipm_dir))

        # Create subdirectories
        (aipm_dir / 'data').mkdir()
        (aipm_dir / 'logs').mkdir()
        (aipm_dir / 'contexts').mkdir()
        (aipm_dir / 'cache').mkdir()

        # Create .claude directory for agents
        claude_dir = self.config.project_path / '.claude'
        claude_dir.mkdir(exist_ok=True)
        (claude_dir / 'agents').mkdir(exist_ok=True)

        logger.info(f"Directory structure created at {aipm_dir}")

    def _initialize_database(self):
        """Initialize database with schema and rollback tracking"""
        db_path = (
            self.config.custom_db_path
            if self.config.custom_db_path
            else self.config.project_path / ".agentpm" / "data" / "agentpm.db"
        )

        # Create database (schema initialized automatically via migrations)
        self.db = DatabaseService(str(db_path))
        self.rollback_plan.add_action("database_init", str(db_path))

        # Create project record
        project = Project(
            name=self.config.project_name,
            description=self.config.project_description,
            path=str(self.config.project_path.absolute()),
            status=ProjectStatus.INITIATED
        )
        self.project = project_methods.create_project(self.db, project)

        logger.info(f"Database initialized at {db_path}: project_id={self.project.id}")

    def _detect_technologies(self):
        """Run technology detection and plugin enrichment"""
        if self.config.skip_detection:
            logger.info("Detection skipped (skip_detection=True)")
            # Create empty detection result
            from agentpm.core.detection.models import DetectionResult
            self.detection_result = DetectionResult(
                matches={},
                scan_time_ms=0.0,
                project_path=str(self.config.project_path.absolute())
            )
            return

        try:
            # Phase 1: Technology Detection
            detection_orchestrator = DetectionOrchestrator(min_confidence=0.6)
            self.detection_result = detection_orchestrator.detect_all(self.config.project_path)

            # Phase 2: Plugin Enrichment
            if self.detection_result.matches:
                plugin_orchestrator = PluginOrchestrator(min_confidence=0.5)
                enrichment = plugin_orchestrator.enrich_context(
                    self.config.project_path,
                    self.detection_result
                )

                # Store detection results in database
                import json
                detected_frameworks = list(self.detection_result.matches.keys())
                tech_stack = [
                    f"{tech} (confidence: {match.confidence:.0%})"
                    for tech, match in self.detection_result.matches.items()
                ]

                with self.db.transaction() as conn:
                    conn.execute("""
                        UPDATE projects
                        SET detected_frameworks = ?,
                            tech_stack = ?
                        WHERE id = ?
                    """, (
                        json.dumps(detected_frameworks),
                        json.dumps(tech_stack),
                        self.project.id
                    ))

                logger.info(f"Detected {len(detected_frameworks)} technologies")
            else:
                logger.info("No technologies detected (generic project)")

        except Exception as e:
            warning = f"Technology detection failed: {e}"
            logger.warning(warning)
            self.warnings.append(warning)
            # Create empty detection result
            from agentpm.core.detection.models import DetectionResult
            self.detection_result = DetectionResult(
                matches={},
                scan_time_ms=0.0,
                project_path=str(self.config.project_path.absolute())
            )

    def _load_rules(self) -> int:
        """Load project rules (via questionnaire or defaults)"""
        if self.config.skip_rules:
            logger.info("Rules loading skipped (skip_rules=True)")
            return 0

        try:
            generator = RuleGenerationService(self.db)

            # Use AUTO mode for non-interactive, wizard for interactive
            if self.config.mode == InitMode.AUTO or not self.console:
                # Use default preset
                loaded_rules = generator.generate_with_preset(
                    project_id=self.project.id,
                    preset='standard',
                    overwrite=False
                )
                logger.info(f"Loaded {len(loaded_rules)} default rules (AUTO mode)")
                return len(loaded_rules)
            else:
                # Run questionnaire (WIZARD mode)
                questionnaire = QuestionnaireService(
                    console=self.console,
                    detection_result=self.detection_result
                )
                answers = questionnaire.run()

                loaded_rules = generator.generate(
                    answers=answers,
                    project_id=self.project.id,
                    overwrite=False
                )

                # Store questionnaire context
                rules_context = self._create_rules_context(
                    project_id=self.project.id,
                    answers=answers,
                    loaded_count=len(loaded_rules)
                )
                context_methods.create_context(self.db, rules_context)

                logger.info(f"Loaded {len(loaded_rules)} rules via questionnaire")
                return len(loaded_rules)

        except Exception as e:
            warning = f"Rules loading failed: {e}"
            logger.warning(warning)
            self.warnings.append(warning)
            return 0

    def _create_rules_context(
        self,
        project_id: int,
        answers: Dict[str, Any],
        loaded_count: int
    ) -> Context:
        """Convert questionnaire answers to 6W context format"""
        six_w = UnifiedSixW()

        # WHO: Team composition
        six_w.who = [
            f"Team size: {answers.get('team_size', 'solo')}",
            f"Development stage: {answers.get('development_stage', 'prototype')}"
        ]

        # WHAT: Project characteristics
        six_w.what = [
            f"Project type: {answers.get('project_type', 'cli')}",
            f"Primary language: {answers.get('primary_language', 'python')}",
            f"Architecture: {answers.get('architecture_style', 'not specified')}"
        ]

        # WHERE: Technical environment
        tech_stack = []
        if answers.get('backend_framework'):
            tech_stack.append(f"Backend: {answers['backend_framework']}")
        if answers.get('frontend_framework'):
            tech_stack.append(f"Frontend: {answers['frontend_framework']}")
        if answers.get('database'):
            tech_stack.append(f"Database: {answers['database']}")
        six_w.where = tech_stack or ["No framework specified"]

        # WHEN: Development constraints
        six_w.when = [
            f"Expected task duration: {answers.get('time_boxing', 4)}h",
            f"Test coverage target: {answers.get('test_coverage', 90)}%"
        ]

        # WHY: Development philosophy
        six_w.why = [
            f"Development approach: {answers.get('development_approach', 'not specified')}",
            f"Code review required: {answers.get('code_review', True)}",
            f"Compliance needs: {answers.get('compliance_requirements', [])}"
        ]

        # HOW: Implementation standards
        six_w.how = [
            f"Rules preset selected: {answers.get('_selected_preset', 'standard')}",
            f"Rules loaded: {loaded_count}",
            f"Deployment: {answers.get('deployment_strategy', 'not specified')}"
        ]

        # Technical constraints from rules
        six_w.technical_constraints = [
            f"Test coverage >= {answers.get('test_coverage', 90)}%",
            f"Max task duration: {answers.get('time_boxing', 4)}h"
        ]

        return Context(
            project_id=project_id,
            context_type=ContextType.RULES_CONTEXT,
            entity_type=EntityType.PROJECT,
            entity_id=project_id,
            six_w=six_w,
            confidence_score=0.9,
            confidence_factors={'source': 'questionnaire', 'answers': answers}
        )

    def _verify_installation(self):
        """
        Verify all components initialized correctly.
        Raises exception if critical checks fail.
        """
        checks: List[VerificationCheck] = []

        # Check 1: Database exists and has tables
        checks.append(self._verify_database())

        # Check 2: Agent files created (or can be created)
        checks.append(self._verify_agents())

        # Check 3: Rules loaded
        checks.append(self._verify_rules())

        # Check 4: Directory structure
        checks.append(self._verify_directories())

        # Evaluate results
        failed_critical = [c for c in checks if not c.passed and c.is_critical]
        failed_non_critical = [c for c in checks if not c.passed and not c.is_critical]

        if failed_critical:
            errors = "\n".join([f"  • {c.name}: {c.error}" for c in failed_critical])
            raise RuntimeError(
                f"Critical verification failures:\n{errors}\n\n"
                f"Run 'apm repair' to attempt fixes."
            )

        if failed_non_critical:
            for check in failed_non_critical:
                warning = f"Verification warning - {check.name}: {check.error}"
                logger.warning(warning)
                self.warnings.append(warning)

        logger.info("Verification complete - all checks passed")

    def _verify_database(self) -> VerificationCheck:
        """Verify database is functional"""
        db_path = self.config.project_path / ".agentpm" / "data" / "agentpm.db"

        if not db_path.exists():
            return VerificationCheck(
                name="Database",
                passed=False,
                error="Database file not found",
                is_critical=True
            )

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check tables exist
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table'"
            )
            table_count = cursor.fetchone()[0]

            if table_count < 50:  # Expect 57 tables
                return VerificationCheck(
                    name="Database",
                    passed=False,
                    error=f"Only {table_count} tables found (expected 57)",
                    is_critical=True
                )

            # Check can query a table
            cursor.execute("SELECT count(*) FROM projects")
            project_count = cursor.fetchone()[0]

            conn.close()

            return VerificationCheck(
                name="Database",
                passed=True,
                details=f"{table_count} tables, {project_count} projects"
            )

        except Exception as e:
            return VerificationCheck(
                name="Database",
                passed=False,
                error=f"Database check failed: {e}",
                is_critical=True
            )

    def _verify_agents(self) -> VerificationCheck:
        """Verify agent files generated (or can be generated)"""
        agents_dir = self.config.project_path / ".claude" / "agents"

        if not agents_dir.exists():
            return VerificationCheck(
                name="Agents",
                passed=False,
                error=".claude/agents directory not found",
                is_critical=False  # Can regenerate
            )

        # Count agent files
        agent_files = list(agents_dir.rglob("*.md"))

        # NOTE: Agent generation is a separate command, so 0 files is OK
        # We just verify the directory exists
        return VerificationCheck(
            name="Agents",
            passed=True,
            details=f"{len(agent_files)} agent definitions (use 'apm agents generate --all' to create)"
        )

    def _verify_rules(self) -> VerificationCheck:
        """Verify rules loaded in database"""
        db_path = self.config.project_path / ".agentpm" / "data" / "agentpm.db"

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT count(*) FROM rules WHERE enabled=1")
            rules_count = cursor.fetchone()[0]

            conn.close()

            # Allow 0 rules if rules were skipped
            if rules_count == 0 and not self.config.skip_rules:
                return VerificationCheck(
                    name="Rules",
                    passed=False,
                    error="No rules loaded",
                    is_critical=False
                )

            return VerificationCheck(
                name="Rules",
                passed=True,
                details=f"{rules_count} governance rules"
            )

        except Exception as e:
            return VerificationCheck(
                name="Rules",
                passed=False,
                error=f"Rules check failed: {e}",
                is_critical=False
            )

    def _verify_directories(self) -> VerificationCheck:
        """Verify directory structure created"""
        required_dirs = [
            self.config.project_path / ".agentpm",
            self.config.project_path / ".agentpm" / "data",
            self.config.project_path / ".agentpm" / "logs",
            self.config.project_path / ".claude" / "agents"
        ]

        missing = [d for d in required_dirs if not d.exists()]

        if missing:
            missing_paths = ", ".join([str(d) for d in missing])
            return VerificationCheck(
                name="Directories",
                passed=False,
                error=f"Missing directories: {missing_paths}",
                is_critical=True
            )

        return VerificationCheck(
            name="Directories",
            passed=True,
            details="All required directories present"
        )

    def rollback(self):
        """Rollback initialization on failure using RollbackPlan"""
        logger.info("Starting rollback of partial initialization")

        for action in self.rollback_plan.get_rollback_order():
            try:
                if action.action_type == "create_directory":
                    target_path = Path(action.target)
                    if target_path.exists():
                        shutil.rmtree(target_path)
                        logger.info(f"Removed directory: {target_path}")

                elif action.action_type == "create_file":
                    target_path = Path(action.target)
                    if target_path.exists():
                        target_path.unlink()
                        logger.info(f"Removed file: {target_path}")

                elif action.action_type == "database_init":
                    # Database rollback is handled by removing the directory
                    pass

            except Exception as e:
                logger.warning(f"Failed to rollback {action.action_type} for {action.target}: {e}")

        logger.info("Rollback completed")
