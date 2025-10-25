"""
Agents CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Agent entities with lifecycle management and validation.

NEW (WI-32 Task #154): Added 3 methods for workflow integration:
- validate_agent_exists() - CI-001 gate for task assignment
- mark_agent_generated() - Generation tracking
- get_stale_agents() - Regeneration detection

Pattern: Type-safe method signatures with Agent model
Methods: create_agent, get_agent, get_agent_by_role, update_agent, delete_agent,
         list_agents, validate_agent_exists, mark_agent_generated, get_stale_agents
"""

from typing import Optional, List
import sqlite3

from ..models import Agent
from ..adapters import AgentAdapter


def create_agent(service, agent: Agent) -> Agent:
    """
    Create a new agent.

    Args:
        service: DatabaseService instance
        agent: Agent model to create

    Returns:
        Created Agent with database ID
    """
    # Validate project exists
    project_exists = _check_project_exists(service, agent.project_id)
    if not project_exists:
        from ..service import ValidationError
        raise ValidationError(f"Project {agent.project_id} does not exist")

    # Convert model to database format
    db_data = AgentAdapter.to_db(agent)

    # Check if migration 0011 columns exist (tier, last_used_at, metadata)
    # This allows the code to work with both base schema and migrated schema
    has_tier_columns = _check_columns_exist(service, 'agents', ['tier', 'last_used_at', 'metadata'])

    if has_tier_columns:
        # NEW (Migration 0011): Full schema with tier, last_used_at, metadata
        query = """
            INSERT INTO agents (project_id, role, display_name, description,
                               sop_content, capabilities, is_active,
                               agent_type, file_path, generated_at,
                               tier, last_used_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            db_data['project_id'],
            db_data['role'],
            db_data['display_name'],
            db_data['description'],
            db_data['sop_content'],
            db_data['capabilities'],
            db_data['is_active'],
            # NEW (WI-009.3): Generation tracking fields
            db_data['agent_type'],
            db_data['file_path'],
            db_data['generated_at'],
            # NEW (Migration 0011): Agent tier and usage tracking
            db_data['tier'],
            db_data['last_used_at'],
            db_data['metadata'],
        )
    else:
        # Base schema without migration 0011 columns
        query = """
            INSERT INTO agents (project_id, role, display_name, description,
                               sop_content, capabilities, is_active,
                               agent_type, file_path, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            db_data['project_id'],
            db_data['role'],
            db_data['display_name'],
            db_data['description'],
            db_data['sop_content'],
            db_data['capabilities'],
            db_data['is_active'],
            # NEW (WI-009.3): Generation tracking fields
            db_data['agent_type'],
            db_data['file_path'],
            db_data['generated_at'],
        )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        agent_id = cursor.lastrowid

    return get_agent(service, agent_id)


def get_agent(service, agent_id: int) -> Optional[Agent]:
    """Get agent by ID"""
    query = "SELECT * FROM agents WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (agent_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return AgentAdapter.from_db(dict(row))


def get_agent_by_role(service, project_id: int, role: str) -> Optional[Agent]:
    """Get agent by project and role"""
    query = "SELECT * FROM agents WHERE project_id = ? AND role = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (project_id, role))
        row = cursor.fetchone()

    if not row:
        return None

    return AgentAdapter.from_db(dict(row))


def update_agent(service, agent_id: int, **updates) -> Optional[Agent]:
    """Update agent with validation"""
    existing = get_agent(service, agent_id)
    if not existing:
        return None

    updated_agent = existing.model_copy(update=updates)
    db_data = AgentAdapter.to_db(updated_agent)

    # Check if migration 0011 columns exist (tier, last_used_at, metadata)
    # Filter out these columns if they don't exist in the schema
    has_tier_columns = _check_columns_exist(service, 'agents', ['tier', 'last_used_at', 'metadata'])
    if not has_tier_columns:
        # Remove migration 0011 columns from update
        db_data = {k: v for k, v in db_data.items() if k not in ['tier', 'last_used_at', 'metadata']}

    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE agents SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), agent_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_agent(service, agent_id)


def delete_agent(service, agent_id: int) -> bool:
    """Delete agent by ID"""
    query = "DELETE FROM agents WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (agent_id,))
        return cursor.rowcount > 0


def list_agents(service, project_id: Optional[int] = None, active_only: bool = False) -> List[Agent]:
    """
    List agents with optional filters.

    Args:
        service: DatabaseService instance
        project_id: Optional project filter
        active_only: If True, only return active agents

    Returns:
        List of Agent models
    """
    query = "SELECT * FROM agents WHERE 1=1"
    params = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    if active_only:
        query += " AND is_active = 1"

    query += " ORDER BY role ASC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [AgentAdapter.from_db(dict(row)) for row in rows]


def validate_agent_exists(
    service,
    project_id: int,
    role: str
) -> tuple[bool, Optional[str]]:
    """
    Validate agent exists and is active.

    Used by WorkflowService before task assignment (CI-001 gate).

    Args:
        service: DatabaseService instance
        project_id: Project ID
        role: Agent role to validate

    Returns:
        (is_valid, error_message)
        - (True, None) if agent exists and active
        - (False, error) otherwise

    Example:
        >>> valid, error = validate_agent_exists(service, 1, 'aipm-database-developer')
        >>> valid  # True
        >>> error  # None

        >>> valid, error = validate_agent_exists(service, 1, 'nonexistent-agent')
        >>> valid  # False
        >>> error  # "Agent 'nonexistent-agent' not found"
    """
    agent = get_agent_by_role(service, project_id, role)

    if not agent:
        return False, f"Agent '{role}' not found"

    if not agent.is_active:
        return False, f"Agent '{role}' is inactive (is_active=False)"

    return True, None


def mark_agent_generated(
    service,
    agent_id: int,
    file_path: str
) -> Optional[Agent]:
    """
    Mark agent as generated with file path and timestamp.

    Called after successfully writing agent SOP file.

    Args:
        service: DatabaseService instance
        agent_id: Agent ID
        file_path: Path to generated .md file

    Returns:
        Updated Agent if found, None otherwise

    Example:
        >>> agent = mark_agent_generated(
        ...     service, 1, '.claude/agents/python-implementer.md'
        ... )
        >>> agent.generated_at  # 2025-10-09T14:30:00
    """
    from datetime import datetime

    return update_agent(
        service,
        agent_id,
        file_path=file_path,
        generated_at=datetime.utcnow()
    )


def get_stale_agents(
    service,
    project_id: int,
    threshold_days: int = 7
) -> List[Agent]:
    """
    Get agents that need regeneration (stale or never generated).

    Args:
        service: DatabaseService instance
        project_id: Project ID
        threshold_days: Days before considering stale (default: 7)

    Returns:
        List of agents needing regeneration

    Example:
        >>> stale = get_stale_agents(service, 1, threshold_days=7)
        >>> len(stale)  # 3 agents need regeneration
    """
    agents = list_agents(service, project_id, active_only=True)

    return [agent for agent in agents if agent.is_stale(threshold_days)]


def _check_project_exists(service, project_id: int) -> bool:
    """Check if project exists"""
    query = "SELECT 1 FROM projects WHERE id = ?"
    with service.connect() as conn:
        cursor = conn.execute(query, (project_id,))
        return cursor.fetchone() is not None


def _check_columns_exist(service, table: str, columns: List[str]) -> bool:
    """
    Check if specified columns exist in a table.

    Args:
        service: DatabaseService instance
        table: Table name
        columns: List of column names to check

    Returns:
        True if all columns exist, False otherwise
    """
    query = f"PRAGMA table_info({table})"
    with service.connect() as conn:
        cursor = conn.execute(query)
        existing_columns = {row[1] for row in cursor.fetchall()}  # row[1] is column name

    return all(col in existing_columns for col in columns)