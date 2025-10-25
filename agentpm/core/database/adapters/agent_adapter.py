"""
Agent Adapter - Model ↔ Database Conversion

Handles conversion between Agent domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)

NEW (WI-009.3): Added agent_type, file_path, generated_at conversions
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.agent import Agent
from ..enums import AgentTier


class AgentAdapter:
    """
    Handles Agent model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, agent: Agent) -> Agent:
        """
        Create a new agent (CLI entry point).

        Three-layer pattern:
          1. Validate Pydantic model (automatic via type hints)
          2. Delegate to methods layer
          3. Return validated Agent

        Args:
            service: DatabaseService instance
            agent: Validated Agent Pydantic model

        Returns:
            Created Agent with database ID

        Raises:
            ValidationError: If project_id invalid

        Example:
            >>> from agentpm.core.database.adapters import AgentAdapter
            >>> agent = Agent(project_id=1, role="my-agent", ...)
            >>> created = AgentAdapter.create(db, agent)
        """
        from ..methods import agents as agent_methods
        return agent_methods.create_agent(service, agent)

    @staticmethod
    def get(service, agent_id: int) -> Optional[Agent]:
        """
        Get agent by database ID (CLI entry point).

        Args:
            service: DatabaseService instance
            agent_id: Agent database ID

        Returns:
            Agent if found, None otherwise
        """
        from ..methods import agents as agent_methods
        return agent_methods.get_agent(service, agent_id)

    @staticmethod
    def get_by_role(service, project_id: int, role: str) -> Optional[Agent]:
        """
        Get agent by project and role (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            role: Agent role (e.g., "aipm-database-developer")

        Returns:
            Agent if found, None otherwise
        """
        from ..methods import agents as agent_methods
        return agent_methods.get_agent_by_role(service, project_id, role)

    @staticmethod
    def list(
        service,
        project_id: Optional[int] = None,
        active_only: bool = False
    ) -> List[Agent]:
        """
        List agents with optional filters (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Optional project filter
            active_only: If True, only return active agents

        Returns:
            List of Agent models
        """
        from ..methods import agents as agent_methods
        return agent_methods.list_agents(
            service,
            project_id=project_id,
            active_only=active_only
        )

    @staticmethod
    def update(service, agent_id: int, **updates) -> Optional[Agent]:
        """
        Update agent fields (CLI entry point).

        Args:
            service: DatabaseService instance
            agent_id: Agent database ID to update
            **updates: Field updates (e.g., is_active=True, display_name="New Name")

        Returns:
            Updated Agent if found, None otherwise
        """
        from ..methods import agents as agent_methods
        return agent_methods.update_agent(service, agent_id, **updates)

    @staticmethod
    def delete(service, agent_id: int) -> bool:
        """
        Delete agent by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            agent_id: Agent database ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import agents as agent_methods
        return agent_methods.delete_agent(service, agent_id)

    @staticmethod
    def validate_exists(
        service,
        project_id: int,
        role: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate agent exists and is active (CLI entry point).

        Used by WorkflowService before task assignment (CI-001 gate).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            role: Agent role to validate

        Returns:
            (is_valid, error_message)
            - (True, None) if agent exists and active
            - (False, error) otherwise
        """
        from ..methods import agents as agent_methods
        return agent_methods.validate_agent_exists(service, project_id, role)

    @staticmethod
    def mark_generated(
        service,
        agent_id: int,
        file_path: str
    ) -> Optional[Agent]:
        """
        Mark agent as generated with file path and timestamp (CLI entry point).

        Called after successfully writing agent SOP file.

        Args:
            service: DatabaseService instance
            agent_id: Agent ID
            file_path: Path to generated .md file

        Returns:
            Updated Agent if found, None otherwise
        """
        from ..methods import agents as agent_methods
        return agent_methods.mark_agent_generated(service, agent_id, file_path)

    @staticmethod
    def get_stale_agents(
        service,
        project_id: int,
        threshold_days: int = 7
    ) -> List[Agent]:
        """
        Get agents that need regeneration (stale or never generated) (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            threshold_days: Days before considering stale (default: 7)

        Returns:
            List of agents needing regeneration
        """
        from ..methods import agents as agent_methods
        return agent_methods.get_stale_agents(service, project_id, threshold_days)

    # ============================================================================
    # MODEL CONVERSION (Used by Methods Layer)
    # ============================================================================

    @staticmethod
    def to_db(agent: Agent) -> Dict[str, Any]:
        """
        Convert Agent model to database row format.

        NEW (WI-009.3): Includes agent_type, file_path, generated_at

        Args:
            agent: Agent domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'project_id': agent.project_id,
            'role': agent.role,
            'display_name': agent.display_name,
            'description': agent.description,
            'sop_content': agent.sop_content,
            'capabilities': json.dumps(agent.capabilities) if agent.capabilities else '[]',
            'is_active': 1 if agent.is_active else 0,  # SQLite boolean
            # NEW (WI-009.3): Generation tracking
            'agent_type': agent.agent_type,
            'file_path': agent.file_path,
            'generated_at': agent.generated_at.isoformat() if agent.generated_at else None,
            # NEW (Migration 0011): Agent tier and usage tracking
            'tier': agent.tier.value if agent.tier else None,
            'last_used_at': agent.last_used_at.isoformat() if agent.last_used_at else None,
            'metadata': agent.metadata or '{}',
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Agent:
        """
        Convert database row to Agent model.

        NEW (WI-009.3): Parses agent_type, file_path, generated_at

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Agent model
        """
        # Parse tier enum
        tier_value = row.get('tier')
        tier = AgentTier(tier_value) if tier_value else None

        return Agent(
            id=row.get('id'),
            project_id=row['project_id'],
            role=row['role'],
            display_name=row['display_name'],
            description=row.get('description'),
            sop_content=row.get('sop_content'),
            capabilities=json.loads(row.get('capabilities', '[]')),
            is_active=bool(row.get('is_active', 1)),
            # NEW (WI-009.3): Generation tracking (use .get() for backwards compatibility)
            agent_type=row.get('agent_type'),
            file_path=row.get('file_path'),
            generated_at=_parse_datetime(row.get('generated_at')),
            # NEW (Migration 0011): Agent tier and usage tracking
            tier=tier,
            last_used_at=_parse_datetime(row.get('last_used_at')),
            metadata=row.get('metadata', '{}'),
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
        )


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from database value"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace(' ', 'T'))
    except (ValueError, AttributeError):
        return None