"""
Agent Loader - YAML to Database Agent Loading

Loads agent definitions from YAML files and populates the agents table.

Supports:
- Single file or directory loading
- Pydantic validation
- Dependency checking
- Conflict detection
- Dry-run mode

Usage:
    loader = AgentLoader(db_service)
    result = loader.load_from_yaml(Path("agents.yaml"))
    result = loader.load_all(Path(".claude/agents/"))
"""

from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime
import yaml
import hashlib

from pydantic import BaseModel, Field, ValidationError, field_validator

from ..database.models.agent import Agent
from ..database.enums import AgentTier


class AgentDefinition(BaseModel):
    """
    Agent definition schema for YAML files.

    Validates agent configuration before database insertion.
    Maps YAML structure to Agent model fields.

    Example YAML:
        role: intent-triage
        display_name: Intent Triage Agent
        description: Classifies requests by type, domain, complexity
        tier: 1
        category: sub-agent
        sop_content: |
          You are the Intent Triage agent...
        capabilities:
          - request_classification
          - domain_mapping
          - priority_assignment
        tools:
          - Read
          - Grep
          - Write
        dependencies:
          - context-assembler
        triggers:
          - raw_request_received
          - classification_needed
        examples:
          - "Classify 'Add OAuth2 login' request"
    """

    # Core identification
    role: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique agent role identifier (e.g., 'intent-triage')"
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable agent name"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Agent purpose and responsibilities"
    )

    # Classification
    tier: int = Field(
        ...,
        ge=1,
        le=3,
        description="Agent tier (1=sub-agent, 2=specialist, 3=orchestrator)"
    )
    category: str = Field(
        ...,
        description="Agent category (orchestrator, sub-agent, specialist, utility, generic)"
    )

    # SOP and capabilities
    sop_content: str = Field(
        ...,
        min_length=10,
        description="Standard Operating Procedure (markdown)"
    )
    capabilities: List[str] = Field(
        default_factory=list,
        description="List of agent capabilities"
    )
    tools: List[str] = Field(
        default_factory=list,
        description="Required tools (Read, Write, Bash, etc.)"
    )

    # Relationships and triggers
    dependencies: List[str] = Field(
        default_factory=list,
        description="Other agents this depends on"
    )
    triggers: List[str] = Field(
        default_factory=list,
        description="When to invoke (for auto-selection)"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Usage examples"
    )

    # Optional metadata
    agent_type: Optional[str] = Field(
        default=None,
        description="Base template type (e.g., 'implementer', 'tester')"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional agent metadata"
    )
    is_active: bool = Field(
        default=True,
        description="Whether agent is currently active"
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role format (lowercase, hyphens only)"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                f"Role must contain only alphanumeric, hyphens, underscores: {v}"
            )
        return v.lower()

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is recognized"""
        valid = {'orchestrator', 'sub-agent', 'specialist', 'utility', 'generic'}
        if v not in valid:
            raise ValueError(
                f"Category must be one of {valid}, got: {v}"
            )
        return v

    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v: int) -> int:
        """Validate tier matches AgentTier enum"""
        valid_tiers = {1, 2, 3}
        if v not in valid_tiers:
            raise ValueError(
                f"Tier must be one of {valid_tiers}, got: {v}"
            )
        return v

    def to_agent_model(self, project_id: int) -> Agent:
        """
        Convert AgentDefinition to Agent model for database insertion.

        Args:
            project_id: Project to associate agent with

        Returns:
            Agent model ready for database insertion
        """
        import json

        # Convert tier int to AgentTier enum
        tier_enum = AgentTier(self.tier)

        # Build metadata JSON
        metadata_dict = {
            'category': self.category,
            'dependencies': self.dependencies,
            'triggers': self.triggers,
            'examples': self.examples,
            'tools': self.tools,
            **self.metadata  # Merge any additional metadata
        }

        return Agent(
            project_id=project_id,
            role=self.role,
            display_name=self.display_name,
            description=self.description,
            sop_content=self.sop_content,
            capabilities=self.capabilities,
            is_active=self.is_active,
            agent_type=self.agent_type,
            tier=tier_enum,
            metadata=json.dumps(metadata_dict),
        )


@dataclass
class LoadResult:
    """
    Result of agent loading operation.

    Provides statistics and validation results.
    """

    success: bool
    loaded_count: int
    skipped_count: int
    error_count: int
    agents: List[Agent]
    errors: List[str]
    warnings: List[str]
    conflicts: Dict[str, List[str]]  # role -> [conflict reasons]
    dependency_graph: Dict[str, List[str]]  # role -> [dependencies]

    def summary(self) -> str:
        """Generate human-readable summary"""
        lines = [
            f"Load Result: {'SUCCESS' if self.success else 'FAILURE'}",
            f"  Loaded: {self.loaded_count}",
            f"  Skipped: {self.skipped_count}",
            f"  Errors: {self.error_count}",
        ]

        if self.warnings:
            lines.append(f"  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                lines.append(f"    - {warning}")

        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.conflicts:
            lines.append("\nConflicts:")
            for role, reasons in self.conflicts.items():
                lines.append(f"  {role}:")
                for reason in reasons:
                    lines.append(f"    - {reason}")

        return "\n".join(lines)


class AgentLoader:
    """
    Loads agent definitions from YAML files to database.

    Features:
    - Pydantic validation
    - Dependency checking
    - Conflict detection
    - Dry-run mode
    - Batch loading

    Usage:
        loader = AgentLoader(db_service)
        result = loader.load_from_yaml(Path("intent-triage.yaml"))
        if result.success:
            print(f"Loaded {result.loaded_count} agents")
    """

    def __init__(self, db_service, project_id: Optional[int] = None):
        """
        Initialize loader.

        Args:
            db_service: Database service instance
            project_id: Default project ID (can be overridden per load)
        """
        self.db_service = db_service
        self.default_project_id = project_id

    def load_from_yaml(
        self,
        yaml_path: Path,
        project_id: Optional[int] = None,
        dry_run: bool = False,
        force: bool = False
    ) -> LoadResult:
        """
        Load agent definitions from single YAML file.

        Supports both single-agent and multi-agent YAML files.

        Single agent format:
            role: intent-triage
            display_name: Intent Triage
            ...

        Multi-agent format:
            agents:
              - role: intent-triage
                display_name: Intent Triage
                ...
              - role: context-assembler
                display_name: Context Assembler
                ...

        Args:
            yaml_path: Path to YAML file
            project_id: Project to associate agents with
            dry_run: Validate only, don't insert
            force: Overwrite existing agents

        Returns:
            LoadResult with statistics and any errors
        """
        project_id = project_id or self.default_project_id
        if not project_id:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=1,
                agents=[],
                errors=["No project_id provided"],
                warnings=[],
                conflicts={},
                dependency_graph={}
            )

        errors = []
        warnings = []
        agents = []

        # Read YAML file
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=1,
                agents=[],
                errors=[f"Failed to read YAML: {e}"],
                warnings=[],
                conflicts={},
                dependency_graph={}
            )

        # Determine if single or multi-agent format
        if isinstance(data, dict):
            if 'agents' in data:
                # Multi-agent format
                agent_defs = data['agents']
            else:
                # Single agent format
                agent_defs = [data]
        elif isinstance(data, list):
            # List of agents
            agent_defs = data
        else:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=1,
                agents=[],
                errors=["Invalid YAML format: expected dict or list"],
                warnings=[],
                conflicts={},
                dependency_graph={}
            )

        # Parse and validate each agent
        for idx, agent_data in enumerate(agent_defs):
            try:
                # Validate with Pydantic
                agent_def = AgentDefinition(**agent_data)

                # Convert to Agent model
                agent = agent_def.to_agent_model(project_id)
                agents.append(agent)

            except ValidationError as e:
                error_msg = f"Agent {idx + 1}: Validation failed:\n"
                for error in e.errors():
                    field = '.'.join(str(x) for x in error['loc'])
                    error_msg += f"  {field}: {error['msg']}\n"
                errors.append(error_msg.strip())
            except Exception as e:
                errors.append(f"Agent {idx + 1}: Unexpected error: {e}")

        if errors:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=len(errors),
                agents=[],
                errors=errors,
                warnings=warnings,
                conflicts={},
                dependency_graph={}
            )

        # Validate dependencies
        dependency_graph = {}
        conflicts = {}

        for agent in agents:
            # Build dependency graph
            import json
            metadata = json.loads(agent.metadata or '{}')
            deps = metadata.get('dependencies', [])
            dependency_graph[agent.role] = deps

            # Check for missing dependencies
            missing_deps = [
                dep for dep in deps
                if dep not in [a.role for a in agents]
            ]
            if missing_deps:
                warnings.append(
                    f"{agent.role}: Missing dependencies: {', '.join(missing_deps)}"
                )

        # Check for conflicts with existing agents (if not force)
        if not force and not dry_run:
            existing_roles = self._get_existing_roles(project_id)
            for agent in agents:
                if agent.role in existing_roles:
                    conflicts[agent.role] = ["Agent already exists"]

        if conflicts and not force:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=len(conflicts),
                error_count=0,
                agents=[],
                errors=[],
                warnings=warnings,
                conflicts=conflicts,
                dependency_graph=dependency_graph
            )

        # Insert agents (if not dry_run)
        loaded_count = 0
        skipped_count = 0

        if not dry_run:
            for agent in agents:
                try:
                    if force:
                        # Update if exists, insert if not
                        self._upsert_agent(agent)
                    else:
                        # Insert only
                        self._insert_agent(agent)
                    loaded_count += 1
                except Exception as e:
                    errors.append(f"{agent.role}: Insert failed: {e}")
                    skipped_count += 1
        else:
            # Dry run - just count what would be loaded
            loaded_count = len(agents)

        return LoadResult(
            success=(len(errors) == 0 and len(conflicts) == 0),
            loaded_count=loaded_count,
            skipped_count=skipped_count,
            error_count=len(errors),
            agents=agents if dry_run else [],
            errors=errors,
            warnings=warnings,
            conflicts=conflicts,
            dependency_graph=dependency_graph
        )

    def load_all(
        self,
        definitions_dir: Path,
        project_id: Optional[int] = None,
        dry_run: bool = False,
        force: bool = False,
        pattern: str = "*.yaml"
    ) -> LoadResult:
        """
        Load all agent definitions from directory.

        Recursively scans directory for YAML files.
        Validates all files before inserting any.

        Args:
            definitions_dir: Directory containing YAML files
            project_id: Project to associate agents with
            dry_run: Validate only, don't insert
            force: Overwrite existing agents
            pattern: File pattern to match (default: *.yaml)

        Returns:
            Consolidated LoadResult from all files
        """
        project_id = project_id or self.default_project_id
        if not project_id:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=1,
                agents=[],
                errors=["No project_id provided"],
                warnings=[],
                conflicts={},
                dependency_graph={}
            )

        # Find all YAML files
        yaml_files = list(definitions_dir.rglob(pattern))
        if not yaml_files:
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=0,
                error_count=1,
                agents=[],
                errors=[f"No {pattern} files found in {definitions_dir}"],
                warnings=[],
                conflicts={},
                dependency_graph={}
            )

        # Collect all agents first (validation phase)
        all_agents = []
        all_errors = []
        all_warnings = []
        all_conflicts = {}
        all_dependency_graph = {}

        for yaml_file in yaml_files:
            result = self.load_from_yaml(
                yaml_file,
                project_id=project_id,
                dry_run=True,  # Always dry-run first
                force=force
            )

            all_agents.extend(result.agents)
            all_errors.extend([f"{yaml_file.name}: {e}" for e in result.errors])
            all_warnings.extend([f"{yaml_file.name}: {w}" for w in result.warnings])
            all_conflicts.update({
                f"{yaml_file.name}:{k}": v
                for k, v in result.conflicts.items()
            })
            all_dependency_graph.update(result.dependency_graph)

        # Check for duplicate roles across files
        role_counts = {}
        for agent in all_agents:
            role_counts[agent.role] = role_counts.get(agent.role, 0) + 1

        duplicates = {role: count for role, count in role_counts.items() if count > 1}
        if duplicates:
            for role, count in duplicates.items():
                all_conflicts[role] = [f"Role defined {count} times across files"]

        # Validate cross-file dependencies
        all_roles = {agent.role for agent in all_agents}
        for role, deps in all_dependency_graph.items():
            missing_deps = [dep for dep in deps if dep not in all_roles]
            if missing_deps:
                all_warnings.append(
                    f"{role}: Missing dependencies: {', '.join(missing_deps)}"
                )

        # If validation failed, stop
        if all_errors or (all_conflicts and not force):
            return LoadResult(
                success=False,
                loaded_count=0,
                skipped_count=len(all_conflicts),
                error_count=len(all_errors),
                agents=[],
                errors=all_errors,
                warnings=all_warnings,
                conflicts=all_conflicts,
                dependency_graph=all_dependency_graph
            )

        # Insert all agents (if not dry_run)
        loaded_count = 0
        skipped_count = 0
        insert_errors = []

        if not dry_run:
            for agent in all_agents:
                try:
                    if force:
                        self._upsert_agent(agent)
                    else:
                        self._insert_agent(agent)
                    loaded_count += 1
                except Exception as e:
                    insert_errors.append(f"{agent.role}: {e}")
                    skipped_count += 1
        else:
            loaded_count = len(all_agents)

        return LoadResult(
            success=(len(insert_errors) == 0),
            loaded_count=loaded_count,
            skipped_count=skipped_count,
            error_count=len(insert_errors),
            agents=all_agents if dry_run else [],
            errors=insert_errors,
            warnings=all_warnings,
            conflicts=all_conflicts,
            dependency_graph=all_dependency_graph
        )

    def _get_existing_roles(self, project_id: int) -> Set[str]:
        """Get set of existing agent roles for project"""
        query = """
            SELECT role FROM agents
            WHERE project_id = ?
        """
        rows = self.db_service.execute_query(query, (project_id,))
        return {row[0] for row in rows}

    def _insert_agent(self, agent: Agent) -> None:
        """Insert new agent into database"""
        query = """
            INSERT INTO agents (
                project_id, role, display_name, description,
                sop_content, capabilities, is_active,
                agent_type, tier, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        import json
        now = datetime.utcnow()

        self.db_service.execute_update(
            query,
            (
                agent.project_id,
                agent.role,
                agent.display_name,
                agent.description,
                agent.sop_content,
                json.dumps(agent.capabilities),
                agent.is_active,
                agent.agent_type,
                agent.tier.value if agent.tier else None,
                agent.metadata,
                now,
                now,
            )
        )

    def _upsert_agent(self, agent: Agent) -> None:
        """Update existing agent or insert if not exists"""
        # Check if exists
        query = "SELECT id FROM agents WHERE project_id = ? AND role = ?"
        rows = self.db_service.execute_query(
            query,
            (agent.project_id, agent.role)
        )

        if rows:
            # Update existing
            agent_id = rows[0][0]
            self._update_agent(agent_id, agent)
        else:
            # Insert new
            self._insert_agent(agent)

    def _update_agent(self, agent_id: int, agent: Agent) -> None:
        """Update existing agent"""
        query = """
            UPDATE agents SET
                display_name = ?,
                description = ?,
                sop_content = ?,
                capabilities = ?,
                is_active = ?,
                agent_type = ?,
                tier = ?,
                metadata = ?,
                updated_at = ?
            WHERE id = ?
        """
        import json
        now = datetime.utcnow()

        self.db_service.execute_update(
            query,
            (
                agent.display_name,
                agent.description,
                agent.sop_content,
                json.dumps(agent.capabilities),
                agent.is_active,
                agent.agent_type,
                agent.tier.value if agent.tier else None,
                agent.metadata,
                now,
                agent_id,
            )
        )
