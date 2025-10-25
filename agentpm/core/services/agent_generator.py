"""
Agent Generation Service

Generates all APM agent definition files using the provider-based generator system.
This service wraps the existing provider generator architecture to provide:
- Automatic agent generation during `apm init`
- Progress tracking for user feedback
- Error handling and reporting
- Support for multiple providers (claude-code, cursor, gemini)
"""

from pathlib import Path
from typing import List, Optional, Callable
import logging
from dataclasses import dataclass

from agentpm.core.database import DatabaseService
from agentpm.core.database.adapters import AgentAdapter, RuleAdapter
from agentpm.providers.generators import (
    detect_current_provider,
    get_provider_generator,
)
from agentpm.providers.generators.base import (
    GenerationContext,
    GenerationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentGenerationProgress:
    """Track agent generation progress for UI feedback"""
    agent_role: str
    current: int
    total: int
    agent_type: str  # Based on database agent_type field


@dataclass
class AgentGenerationSummary:
    """Summary of agent generation results"""
    total_generated: int
    total_failed: int
    agents_by_type: dict
    failed_agents: List[str]
    warnings: List[str]
    output_directory: Path


class AgentGeneratorService:
    """
    Service for generating APM agent definition files.

    Uses the existing provider-based generator system to create agent files
    from database records. Supports multiple LLM providers (Claude Code, Cursor, Gemini).
    """

    def __init__(
        self,
        db: DatabaseService,
        project_path: Path,
        project_id: int = 1,
        provider: Optional[str] = None,
        progress_callback: Optional[Callable[[AgentGenerationProgress], None]] = None
    ):
        """
        Initialize agent generator service.

        Args:
            db: Database service instance
            project_path: Project root path
            project_id: Project ID (default: 1)
            provider: LLM provider name (auto-detected if None)
            progress_callback: Optional callback for progress updates
        """
        self.db = db
        self.project_path = project_path
        self.project_id = project_id
        self.progress_callback = progress_callback

        # Detect or use specified provider
        self.provider = provider if provider else detect_current_provider(project_path)
        if not self.provider:
            raise RuntimeError(
                "Could not detect LLM provider. "
                "Ensure .claude/ or .cursor/ directory exists, or specify --provider."
            )

        # Get provider generator
        generator_class = get_provider_generator(self.provider)
        if not generator_class:
            raise RuntimeError(f"Provider '{self.provider}' not available")

        self.generator = generator_class()

        logger.info(f"AgentGenerator initialized with provider: {self.provider}")

    def generate_all(self, force: bool = False) -> AgentGenerationSummary:
        """
        Generate all agent definition files from database records.

        Args:
            force: Regenerate even if files exist

        Returns:
            AgentGenerationSummary with generation results
        """
        logger.info("Starting agent generation for all agents in database")

        # Load all agents from database
        agents = AgentAdapter.list(self.db, project_id=self.project_id, active_only=False)

        if not agents:
            logger.warning("No agents found in database")
            return AgentGenerationSummary(
                total_generated=0,
                total_failed=0,
                agents_by_type={},
                failed_agents=[],
                warnings=["No agents found in database"],
                output_directory=self.project_path / ".claude" / "agents"
            )

        # Load project rules for embedding in agent SOPs
        project_rules = RuleAdapter.list(self.db, project_id=self.project_id)

        logger.info(f"Generating {len(agents)} agent files with {len(project_rules)} project rules")

        # Track results
        results: List[GenerationResult] = []
        agents_by_type = {}
        failed_agents = []
        warnings = []

        # Generate agents with progress tracking
        for i, agent in enumerate(agents, 1):
            # Update progress
            if self.progress_callback:
                self.progress_callback(AgentGenerationProgress(
                    agent_role=agent.role,
                    current=i,
                    total=len(agents),
                    agent_type=agent.agent_type or "utility"
                ))

            # Skip if file exists and not forcing
            output_path = self.generator.get_output_path(agent.role, self.project_path)
            if output_path.exists() and not force:
                logger.debug(f"Skipping {agent.role} (file exists)")
                warnings.append(f"Skipped {agent.role} (file exists, use --force to regenerate)")
                continue

            # Create generation context
            context = GenerationContext(
                agent=agent,
                project_rules=project_rules,
                project_path=self.project_path,
            )

            # Generate agent file
            result = self.generator.generate_agent_file(context)
            results.append(result)

            # Track by type
            agent_type = agent.agent_type or "utility"
            agents_by_type[agent_type] = agents_by_type.get(agent_type, 0) + 1

            # Write file if successful
            if result.success:
                try:
                    result.output_path.parent.mkdir(parents=True, exist_ok=True)
                    result.output_path.write_text(result.content, encoding='utf-8')
                    logger.debug(f"Generated {agent.role} -> {result.output_path}")
                except Exception as e:
                    logger.error(f"Failed to write {agent.role}: {e}")
                    failed_agents.append(agent.role)
                    result.success = False
                    result.error = str(e)
            else:
                logger.error(f"Generation failed for {agent.role}: {result.error}")
                failed_agents.append(agent.role)

            # Collect warnings
            if result.warnings:
                warnings.extend([f"{agent.role}: {w}" for w in result.warnings])

        # Calculate summary
        success_count = sum(1 for r in results if r.success)
        failure_count = len(results) - success_count

        summary = AgentGenerationSummary(
            total_generated=success_count,
            total_failed=failure_count,
            agents_by_type=agents_by_type,
            failed_agents=failed_agents,
            warnings=warnings,
            output_directory=results[0].output_path.parent if results else self.project_path / ".claude" / "agents"
        )

        logger.info(
            f"Agent generation complete: {success_count} succeeded, "
            f"{failure_count} failed, {len(warnings)} warnings"
        )

        return summary

    def generate_one(self, role: str, force: bool = False) -> GenerationResult:
        """
        Generate a single agent file by role.

        Args:
            role: Agent role identifier
            force: Regenerate even if file exists

        Returns:
            GenerationResult for the agent
        """
        # Load agent from database
        agent = AgentAdapter.get_by_role(self.db, self.project_id, role)
        if not agent:
            raise ValueError(f"Agent '{role}' not found in database")

        # Load project rules
        project_rules = RuleAdapter.list(self.db, project_id=self.project_id)

        # Check if file exists
        output_path = self.generator.get_output_path(role, self.project_path)
        if output_path.exists() and not force:
            logger.info(f"Agent '{role}' already exists at {output_path}")
            return GenerationResult(
                agent_role=role,
                output_path=output_path,
                content="",
                success=True,
                warnings=[f"File already exists (use --force to regenerate)"]
            )

        # Create generation context
        context = GenerationContext(
            agent=agent,
            project_rules=project_rules,
            project_path=self.project_path,
        )

        # Generate agent file
        result = self.generator.generate_agent_file(context)

        # Write file if successful
        if result.success:
            try:
                result.output_path.parent.mkdir(parents=True, exist_ok=True)
                result.output_path.write_text(result.content, encoding='utf-8')
                logger.info(f"Generated {role} -> {result.output_path}")
            except Exception as e:
                logger.error(f"Failed to write {role}: {e}")
                result.success = False
                result.error = str(e)

        return result

    def get_output_directory(self) -> Path:
        """
        Get the output directory where agent files will be written.

        Returns:
            Path to agent files directory
        """
        # Use a sample role to get the directory
        return self.generator.get_output_path("_sample", self.project_path).parent
