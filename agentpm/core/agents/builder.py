"""
Agent Builder - Programmatic API for Agent Definition

Provides a clean, transaction-safe API for defining agents and their relationships
in the database using the migration_0014 schema.

Example:
    builder = AgentBuilder(db_session)
    agent = builder.define_agent(
        role='definition-orch',
        tier=2,
        execution_mode='parallel',
        symbol_mode=True
    )
    builder.add_relationship(agent.id, 'master-orchestrator', 'reports_to')
    builder.add_tool(agent.id, 'context7', phase='discovery', priority=1)
    builder.commit()

Design Principles:
- Simple, clean API (no over-engineering)
- Transaction support (commit/rollback)
- Validation (required fields, enums, foreign keys)
- Uses migration_0014 schema directly
- Follows existing adapter patterns
"""

import json
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

from ..database.models.agent import Agent
from ..database.adapters.agent_adapter import AgentAdapter
from ..database.enums import AgentTier


# Valid enum values from migration_0014
VALID_EXECUTION_MODES = {'parallel', 'sequential'}
VALID_RELATIONSHIP_TYPES = {'delegates_to', 'reports_to'}
VALID_PHASES = {'discovery', 'implementation', 'reasoning', 'testing', 'documentation', 'deployment'}
VALID_ORCHESTRATOR_TYPES = {'master', 'mini', None}


@dataclass
class AgentDefinition:
    """Result of define_agent() - contains agent ID and details"""
    id: int
    role: str
    tier: Optional[int]
    execution_mode: str
    symbol_mode: bool


class AgentBuilder:
    """
    Programmatic API for defining agents in the database.

    Provides transaction-safe operations for creating agents, relationships,
    tools, and examples using the migration_0014 schema.

    Usage:
        builder = AgentBuilder(db_connection)
        agent = builder.define_agent(role='test-agent', tier=1)
        builder.add_tool(agent.id, 'sequential-thinking', phase='reasoning')
        builder.commit()  # or builder.rollback()
    """

    def __init__(self, db_connection: sqlite3.Connection, project_id: int = 1):
        """
        Initialize agent builder.

        Args:
            db_connection: SQLite database connection
            project_id: Project ID for agent assignment (default: 1)
        """
        self.conn = db_connection
        self.project_id = project_id
        self._pending_operations: List[str] = []

        # Enable dict cursor
        self.conn.row_factory = sqlite3.Row

    def define_agent(
        self,
        role: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tier: Optional[int] = None,
        execution_mode: str = 'parallel',
        symbol_mode: bool = False,
        orchestrator_type: Optional[str] = None,
        agent_file_path: Optional[str] = None,
        sop_content: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        is_active: bool = True
    ) -> AgentDefinition:
        """
        Define an agent in the database.

        Args:
            role: Agent role/name (required, e.g., 'definition-orch')
            display_name: Human-readable name (defaults to role)
            description: Agent purpose and responsibilities
            tier: Agent tier (1=sub-agent, 2=mini-orch, 3=master, None=specialist)
            execution_mode: 'parallel' (default) or 'sequential'
            symbol_mode: Enable compressed symbol-based reporting
            orchestrator_type: 'master', 'mini', or None
            agent_file_path: Path to agent SOP file (e.g., '.claude/agents/...')
            sop_content: Standard Operating Procedure (markdown)
            capabilities: List of agent capabilities
            is_active: Whether agent is active (default: True)

        Returns:
            AgentDefinition with agent ID and details

        Raises:
            ValueError: If validation fails (invalid enum values, required fields missing)
            sqlite3.IntegrityError: If database constraints violated
        """
        # Validation
        if not role or not role.strip():
            raise ValueError("role is required and cannot be empty")

        if execution_mode not in VALID_EXECUTION_MODES:
            raise ValueError(f"execution_mode must be one of {VALID_EXECUTION_MODES}")

        if orchestrator_type not in VALID_ORCHESTRATOR_TYPES:
            raise ValueError(f"orchestrator_type must be one of {VALID_ORCHESTRATOR_TYPES}")

        # Convert tier to enum if provided
        tier_enum = AgentTier(tier) if tier else None

        # Create Agent model
        agent = Agent(
            project_id=self.project_id,
            role=role,
            display_name=display_name or role,
            description=description,
            sop_content=sop_content,
            capabilities=capabilities or [],
            is_active=is_active,
            tier=tier_enum,
            metadata=json.dumps({
                'execution_mode': execution_mode,
                'symbol_mode': symbol_mode,
                'orchestrator_type': orchestrator_type,
                'agent_file_path': agent_file_path
            })
        )

        # Convert to database format
        db_data = AgentAdapter.to_db(agent)

        # Add migration_0014 specific columns
        db_data['execution_mode'] = execution_mode
        db_data['symbol_mode'] = 1 if symbol_mode else 0
        db_data['orchestrator_type'] = orchestrator_type
        db_data['agent_file_path'] = agent_file_path

        # Build INSERT query
        columns = ', '.join(db_data.keys())
        placeholders = ', '.join(['?' for _ in db_data])
        values = tuple(db_data.values())

        query = f"INSERT INTO agents ({columns}) VALUES ({placeholders})"

        # Execute
        cursor = self.conn.execute(query, values)
        agent_id = cursor.lastrowid

        self._pending_operations.append(f"Created agent: {role} (id={agent_id})")

        return AgentDefinition(
            id=agent_id,
            role=role,
            tier=tier,
            execution_mode=execution_mode,
            symbol_mode=symbol_mode
        )

    def add_relationship(
        self,
        agent_id: int,
        related_agent_id: int,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a relationship between two agents.

        Args:
            agent_id: Source agent ID
            related_agent_id: Target agent ID (or role name - will be resolved)
            relationship_type: 'delegates_to' or 'reports_to'
            metadata: Optional relationship metadata (phases, conditions, etc.)

        Returns:
            Relationship ID

        Raises:
            ValueError: If validation fails or agents not found
        """
        # Validation
        if relationship_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(f"relationship_type must be one of {VALID_RELATIONSHIP_TYPES}")

        # Resolve related_agent_id if it's a role name (string)
        if isinstance(related_agent_id, str):
            cursor = self.conn.execute(
                "SELECT id FROM agents WHERE role = ? AND project_id = ?",
                (related_agent_id, self.project_id)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Agent with role '{related_agent_id}' not found")
            related_agent_id = row['id']

        # Verify both agents exist
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM agents WHERE id IN (?, ?)",
            (agent_id, related_agent_id)
        )
        if cursor.fetchone()['count'] != 2:
            raise ValueError(f"One or both agents not found: {agent_id}, {related_agent_id}")

        # Insert relationship
        metadata_json = json.dumps(metadata or {})

        cursor = self.conn.execute("""
            INSERT INTO agent_relationships (agent_id, related_agent_id, relationship_type, metadata)
            VALUES (?, ?, ?, ?)
        """, (agent_id, related_agent_id, relationship_type, metadata_json))

        rel_id = cursor.lastrowid
        self._pending_operations.append(
            f"Added {relationship_type}: agent {agent_id} -> {related_agent_id}"
        )

        return rel_id

    def add_tool(
        self,
        agent_id: int,
        tool_name: str,
        phase: str,
        priority: int = 1,
        config: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a tool preference for an agent in a specific phase.

        Args:
            agent_id: Agent ID
            tool_name: Tool name (e.g., 'sequential-thinking', 'context7')
            phase: Workflow phase ('discovery', 'implementation', etc.)
            priority: Tool priority (1=primary, 2=fallback, 3=optional)
            config: Optional tool configuration

        Returns:
            Tool record ID

        Raises:
            ValueError: If validation fails or agent not found
        """
        # Validation
        if phase not in VALID_PHASES:
            raise ValueError(f"phase must be one of {VALID_PHASES}")

        if not 1 <= priority <= 3:
            raise ValueError("priority must be 1 (primary), 2 (fallback), or 3 (optional)")

        # Verify agent exists
        cursor = self.conn.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        if not cursor.fetchone():
            raise ValueError(f"Agent {agent_id} not found")

        # Insert tool
        config_json = json.dumps(config or {})

        cursor = self.conn.execute("""
            INSERT INTO agent_tools (agent_id, phase, tool_name, priority, config)
            VALUES (?, ?, ?, ?, ?)
        """, (agent_id, phase, tool_name, priority, config_json))

        tool_id = cursor.lastrowid
        self._pending_operations.append(
            f"Added tool: {tool_name} for agent {agent_id} in {phase} phase (priority={priority})"
        )

        return tool_id

    def add_example(
        self,
        agent_id: int,
        scenario_name: str,
        input_context: Dict[str, Any],
        expected_output: Dict[str, Any],
        scenario_description: Optional[str] = None,
        category: Optional[str] = None,
        success_criteria: Optional[str] = None,
        edge_cases: Optional[List[str]] = None
    ) -> int:
        """
        Add a learning example (input/output pair) for an agent.

        Args:
            agent_id: Agent ID
            scenario_name: Example scenario name
            input_context: Input context (request, constraints, etc.)
            expected_output: Expected output (response, artifacts, decisions)
            scenario_description: Optional description
            category: Optional category (e.g., 'discovery', 'error-handling')
            success_criteria: What makes this example successful
            edge_cases: List of edge cases this example covers

        Returns:
            Example record ID

        Raises:
            ValueError: If validation fails or agent not found
        """
        # Verify agent exists
        cursor = self.conn.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        if not cursor.fetchone():
            raise ValueError(f"Agent {agent_id} not found")

        # Convert to JSON
        input_json = json.dumps(input_context)
        output_json = json.dumps(expected_output)
        edge_cases_json = json.dumps(edge_cases or [])

        # Insert example
        cursor = self.conn.execute("""
            INSERT INTO agent_examples (
                agent_id, scenario_name, scenario_description, category,
                input_context, expected_output, success_criteria, edge_cases
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id, scenario_name, scenario_description, category,
            input_json, output_json, success_criteria, edge_cases_json
        ))

        example_id = cursor.lastrowid
        self._pending_operations.append(
            f"Added example: {scenario_name} for agent {agent_id}"
        )

        return example_id

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """
        Retrieve an agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent model or None if not found
        """
        cursor = self.conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return AgentAdapter.from_db(dict(row))

    def get_agent_by_role(self, role: str) -> Optional[Agent]:
        """
        Retrieve an agent by role name.

        Args:
            role: Agent role name

        Returns:
            Agent model or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM agents WHERE role = ? AND project_id = ?",
            (role, self.project_id)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return AgentAdapter.from_db(dict(row))

    def commit(self) -> None:
        """
        Commit all pending operations.

        Raises:
            sqlite3.Error: If commit fails
        """
        self.conn.commit()
        self._pending_operations.clear()

    def rollback(self) -> None:
        """
        Rollback all pending operations.
        """
        self.conn.rollback()
        self._pending_operations.clear()

    def get_pending_operations(self) -> List[str]:
        """
        Get list of pending operations (for debugging/logging).

        Returns:
            List of operation descriptions
        """
        return self._pending_operations.copy()


# Convenience function for common patterns
def create_orchestrator_agent(
    builder: AgentBuilder,
    role: str,
    tier: int,
    delegates_to: Optional[List[str]] = None,
    reports_to: Optional[str] = None,
    tools: Optional[Dict[str, List[str]]] = None
) -> AgentDefinition:
    """
    Convenience function to create an orchestrator agent with relationships and tools.

    Args:
        builder: AgentBuilder instance
        role: Agent role name
        tier: Agent tier (1=sub, 2=mini, 3=master)
        delegates_to: List of agent roles this agent delegates to
        reports_to: Agent role this agent reports to
        tools: Dict of phase -> [tool_names] mappings

    Returns:
        AgentDefinition

    Example:
        agent = create_orchestrator_agent(
            builder,
            role='planning-orch',
            tier=2,
            delegates_to=['decomposer', 'estimator'],
            reports_to='master-orchestrator',
            tools={'discovery': ['context7'], 'reasoning': ['sequential-thinking']}
        )
    """
    # Determine orchestrator type
    orch_type = 'master' if tier == 3 else 'mini' if tier == 2 else None

    # Create agent
    agent = builder.define_agent(
        role=role,
        tier=tier,
        execution_mode='parallel',
        symbol_mode=True,
        orchestrator_type=orch_type
    )

    # Add relationships
    if reports_to:
        builder.add_relationship(agent.id, reports_to, 'reports_to')

    if delegates_to:
        for delegate_role in delegates_to:
            builder.add_relationship(agent.id, delegate_role, 'delegates_to')

    # Add tools
    if tools:
        for phase, tool_names in tools.items():
            for priority, tool_name in enumerate(tool_names, start=1):
                builder.add_tool(agent.id, tool_name, phase, priority)

    return agent
