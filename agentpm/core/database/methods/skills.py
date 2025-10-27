"""
Skills CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Skill entities with progressive loading support.

Part of WI-171: Claude Code Provider Enhancement
Task #1130: Implementation: Skills Database Schema and Models

Pattern: Type-safe method signatures with Skill model
Methods: create_skill, get_skill, get_skill_by_name, update_skill, delete_skill,
         list_skills, list_skills_metadata, link_skill_to_agent, unlink_skill_from_agent,
         get_agent_skills, get_skill_agents
"""

from typing import Optional, List, Dict, Any
import sqlite3

from ..models.skill import Skill, AgentSkill, SkillCategory
from ..adapters.skill_adapter import SkillAdapter


# ============================================================================
# SKILL CRUD OPERATIONS
# ============================================================================


def create_skill(service, skill: Skill) -> Skill:
    """
    Create a new skill.

    Args:
        service: DatabaseService instance
        skill: Skill model to create

    Returns:
        Created Skill with database ID

    Raises:
        ValidationError: If skill name already exists
        ValueError: If skill data is invalid

    Example:
        >>> from agentpm.core.database.models.skill import Skill
        >>> skill = Skill(
        ...     name="python-testing",
        ...     display_name="Python Testing",
        ...     description="Testing best practices for Python",
        ...     category=SkillCategory.TESTING,
        ...     instructions="# Python Testing Guide\\n\\n...",
        ... )
        >>> created = create_skill(db, skill)
        >>> print(created.id)  # 42
    """
    # Convert model to database format
    db_data = SkillAdapter.to_db(skill)

    # Validate data
    SkillAdapter.validate_skill_data(db_data)

    # Check if skill name already exists
    existing = get_skill_by_name(service, skill.name)
    if existing:
        from ..service import ValidationError

        raise ValidationError(f"Skill with name '{skill.name}' already exists")

    # Insert into database
    query = """
        INSERT INTO skills (
            name, display_name, description, category,
            instructions, resources, provider_config,
            enabled, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = (
        db_data["name"],
        db_data["display_name"],
        db_data["description"],
        db_data["category"],
        db_data["instructions"],
        db_data["resources"],
        db_data["provider_config"],
        db_data["enabled"],
        db_data["created_at"],
        db_data["updated_at"],
    )

    cursor = service.conn.execute(query, params)
    service.conn.commit()

    # Return created skill with ID
    skill.id = cursor.lastrowid
    return skill


def get_skill(service, skill_id: int) -> Optional[Skill]:
    """
    Get a skill by ID (full data, Level 3).

    Args:
        service: DatabaseService instance
        skill_id: Skill ID to retrieve

    Returns:
        Skill model if found, None otherwise

    Example:
        >>> skill = get_skill(db, 42)
        >>> if skill:
        ...     print(skill.name)  # "python-testing"
    """
    query = """
        SELECT id, name, display_name, description, category,
               instructions, resources, provider_config,
               enabled, created_at, updated_at
        FROM skills
        WHERE id = ?
    """

    cursor = service.conn.execute(query, (skill_id,))
    row = cursor.fetchone()

    if not row:
        return None

    return SkillAdapter.from_db(dict(row))


def get_skill_by_name(service, name: str) -> Optional[Skill]:
    """
    Get a skill by unique name (full data, Level 3).

    Args:
        service: DatabaseService instance
        name: Skill name (kebab-case)

    Returns:
        Skill model if found, None otherwise

    Example:
        >>> skill = get_skill_by_name(db, "python-testing")
        >>> if skill:
        ...     print(skill.display_name)  # "Python Testing"
    """
    query = """
        SELECT id, name, display_name, description, category,
               instructions, resources, provider_config,
               enabled, created_at, updated_at
        FROM skills
        WHERE name = ?
    """

    cursor = service.conn.execute(query, (name,))
    row = cursor.fetchone()

    if not row:
        return None

    return SkillAdapter.from_db(dict(row))


def update_skill(service, skill: Skill) -> Skill:
    """
    Update an existing skill.

    Args:
        service: DatabaseService instance
        skill: Skill model with updated data (must have id)

    Returns:
        Updated Skill model

    Raises:
        ValidationError: If skill ID not found or name conflict
        ValueError: If skill data is invalid

    Example:
        >>> skill = get_skill(db, 42)
        >>> skill.description = "Updated description"
        >>> updated = update_skill(db, skill)
    """
    if not skill.id:
        from ..service import ValidationError

        raise ValidationError("Skill ID is required for update")

    # Check if skill exists
    existing = get_skill(service, skill.id)
    if not existing:
        from ..service import ValidationError

        raise ValidationError(f"Skill with ID {skill.id} not found")

    # Check name uniqueness (if name changed)
    if existing.name != skill.name:
        name_conflict = get_skill_by_name(service, skill.name)
        if name_conflict and name_conflict.id != skill.id:
            from ..service import ValidationError

            raise ValidationError(f"Skill with name '{skill.name}' already exists")

    # Convert model to database format
    db_data = SkillAdapter.to_db(skill)

    # Validate data
    SkillAdapter.validate_skill_data(db_data)

    # Update database (trigger will set updated_at)
    query = """
        UPDATE skills
        SET name = ?,
            display_name = ?,
            description = ?,
            category = ?,
            instructions = ?,
            resources = ?,
            provider_config = ?,
            enabled = ?
        WHERE id = ?
    """

    params = (
        db_data["name"],
        db_data["display_name"],
        db_data["description"],
        db_data["category"],
        db_data["instructions"],
        db_data["resources"],
        db_data["provider_config"],
        db_data["enabled"],
        skill.id,
    )

    service.conn.execute(query, params)
    service.conn.commit()

    # Return updated skill
    return get_skill(service, skill.id)


def delete_skill(service, skill_id: int) -> bool:
    """
    Delete a skill by ID.

    Cascade deletes all agent_skills assignments.

    Args:
        service: DatabaseService instance
        skill_id: Skill ID to delete

    Returns:
        True if deleted, False if not found

    Example:
        >>> deleted = delete_skill(db, 42)
        >>> if deleted:
        ...     print("Skill deleted successfully")
    """
    # Check if skill exists
    existing = get_skill(service, skill_id)
    if not existing:
        return False

    # Delete skill (cascades to agent_skills)
    query = "DELETE FROM skills WHERE id = ?"
    service.conn.execute(query, (skill_id,))
    service.conn.commit()

    return True


def list_skills(
    service,
    category: Optional[SkillCategory] = None,
    enabled_only: bool = True,
    metadata_only: bool = False,
) -> List[Skill]:
    """
    List skills with optional filtering.

    Args:
        service: DatabaseService instance
        category: Filter by category (optional)
        enabled_only: Only return enabled skills (default: True)
        metadata_only: Return Level 1 metadata only for performance (default: False)

    Returns:
        List of Skill models

    Example:
        >>> # Get all enabled skills (metadata only)
        >>> skills = list_skills(db, metadata_only=True)
        >>> for skill in skills:
        ...     print(f"{skill.name}: {skill.description}")

        >>> # Get all testing skills (full data)
        >>> testing_skills = list_skills(db, category=SkillCategory.TESTING)
    """
    # Build query
    if metadata_only:
        # Level 1: Metadata only (fast)
        query = """
            SELECT id, name, display_name, description, category, enabled,
                   created_at, updated_at
            FROM skills
            WHERE 1=1
        """
    else:
        # Level 3: Full data (slower)
        query = """
            SELECT id, name, display_name, description, category,
                   instructions, resources, provider_config,
                   enabled, created_at, updated_at
            FROM skills
            WHERE 1=1
        """

    params = []

    # Add filters
    if category:
        query += " AND category = ?"
        params.append(category.value)

    if enabled_only:
        query += " AND enabled = 1"

    # Order by category and name
    query += " ORDER BY category, name"

    # Execute query
    cursor = service.conn.execute(query, params)
    rows = cursor.fetchall()

    # Convert rows to models
    if metadata_only:
        # For metadata-only, construct partial Skill objects
        skills = []
        for row in rows:
            row_dict = dict(row)
            # Add placeholder instructions to satisfy model validation
            row_dict["instructions"] = ""
            skills.append(SkillAdapter.from_db(row_dict))
        return skills
    else:
        return [SkillAdapter.from_db(dict(row)) for row in rows]


def list_skills_metadata(
    service, category: Optional[SkillCategory] = None, enabled_only: bool = True
) -> List[Dict[str, Any]]:
    """
    List skills metadata only (Level 1, lightweight).

    Returns plain dictionaries for maximum performance.

    Args:
        service: DatabaseService instance
        category: Filter by category (optional)
        enabled_only: Only return enabled skills (default: True)

    Returns:
        List of dictionaries with id, name, display_name, description, category, enabled

    Example:
        >>> metadata = list_skills_metadata(db)
        >>> for skill_meta in metadata:
        ...     print(f"{skill_meta['name']}: {skill_meta['description']}")
    """
    query = """
        SELECT id, name, display_name, description, category, enabled
        FROM skills
        WHERE 1=1
    """

    params = []

    # Add filters
    if category:
        query += " AND category = ?"
        params.append(category.value)

    if enabled_only:
        query += " AND enabled = 1"

    # Order by category and name
    query += " ORDER BY category, name"

    # Execute query
    cursor = service.conn.execute(query, params)
    rows = cursor.fetchall()

    return [dict(row) for row in rows]


# ============================================================================
# AGENT-SKILL JUNCTION OPERATIONS
# ============================================================================


def link_skill_to_agent(
    service, agent_id: int, skill_id: int, priority: int = 50
) -> AgentSkill:
    """
    Link a skill to an agent with priority.

    Args:
        service: DatabaseService instance
        agent_id: Agent ID
        skill_id: Skill ID
        priority: Loading priority (0-100, higher = earlier, default: 50)

    Returns:
        Created AgentSkill model

    Raises:
        ValidationError: If agent or skill doesn't exist, or link already exists
        ValueError: If priority out of range

    Example:
        >>> agent_skill = link_skill_to_agent(db, agent_id=1, skill_id=42, priority=80)
        >>> print(f"Priority: {agent_skill.priority}")  # 80
    """
    # Validate priority
    if not (0 <= priority <= 100):
        raise ValueError("Priority must be between 0 and 100")

    # Check if agent exists
    agent_exists = _check_agent_exists(service, agent_id)
    if not agent_exists:
        from ..service import ValidationError

        raise ValidationError(f"Agent {agent_id} does not exist")

    # Check if skill exists
    skill = get_skill(service, skill_id)
    if not skill:
        from ..service import ValidationError

        raise ValidationError(f"Skill {skill_id} does not exist")

    # Check if link already exists
    existing = _get_agent_skill_link(service, agent_id, skill_id)
    if existing:
        from ..service import ValidationError

        raise ValidationError(
            f"Agent {agent_id} already linked to skill {skill_id}. "
            "Use update to change priority."
        )

    # Create agent_skill model
    agent_skill = AgentSkill(agent_id=agent_id, skill_id=skill_id, priority=priority)

    # Convert to database format
    db_data = SkillAdapter.agent_skill_to_db(agent_skill)

    # Insert into database
    query = """
        INSERT INTO agent_skills (agent_id, skill_id, priority, created_at)
        VALUES (?, ?, ?, ?)
    """

    params = (
        db_data["agent_id"],
        db_data["skill_id"],
        db_data["priority"],
        db_data["created_at"],
    )

    cursor = service.conn.execute(query, params)
    service.conn.commit()

    # Return created agent_skill with ID
    agent_skill.id = cursor.lastrowid
    return agent_skill


def unlink_skill_from_agent(service, agent_id: int, skill_id: int) -> bool:
    """
    Remove skill link from agent.

    Args:
        service: DatabaseService instance
        agent_id: Agent ID
        skill_id: Skill ID

    Returns:
        True if unlinked, False if link not found

    Example:
        >>> unlinked = unlink_skill_from_agent(db, agent_id=1, skill_id=42)
        >>> if unlinked:
        ...     print("Skill unlinked successfully")
    """
    query = "DELETE FROM agent_skills WHERE agent_id = ? AND skill_id = ?"
    cursor = service.conn.execute(query, (agent_id, skill_id))
    service.conn.commit()

    return cursor.rowcount > 0


def get_agent_skills(
    service, agent_id: int, metadata_only: bool = False
) -> List[Skill]:
    """
    Get all skills for an agent, ordered by priority.

    Args:
        service: DatabaseService instance
        agent_id: Agent ID
        metadata_only: Return Level 1 metadata only (default: False)

    Returns:
        List of Skill models, ordered by priority (highest first)

    Example:
        >>> skills = get_agent_skills(db, agent_id=1)
        >>> for skill in skills:
        ...     print(f"{skill.name} (priority: {skill.priority})")
    """
    if metadata_only:
        # Level 1: Metadata only
        query = """
            SELECT s.id, s.name, s.display_name, s.description, s.category, s.enabled,
                   s.created_at, s.updated_at, ags.priority
            FROM skills s
            JOIN agent_skills ags ON s.id = ags.skill_id
            WHERE ags.agent_id = ?
            ORDER BY ags.priority DESC, s.name
        """
    else:
        # Level 3: Full data
        query = """
            SELECT s.id, s.name, s.display_name, s.description, s.category,
                   s.instructions, s.resources, s.provider_config,
                   s.enabled, s.created_at, s.updated_at, ags.priority
            FROM skills s
            JOIN agent_skills ags ON s.id = ags.skill_id
            WHERE ags.agent_id = ?
            ORDER BY ags.priority DESC, s.name
        """

    cursor = service.conn.execute(query, (agent_id,))
    rows = cursor.fetchall()

    if metadata_only:
        # For metadata-only, construct partial Skill objects
        skills = []
        for row in rows:
            row_dict = dict(row)
            # Add placeholder instructions to satisfy model validation
            row_dict["instructions"] = ""
            skills.append(SkillAdapter.from_db(row_dict))
        return skills
    else:
        return [SkillAdapter.from_db(dict(row)) for row in rows]


def get_skill_agents(service, skill_id: int) -> List[Dict[str, Any]]:
    """
    Get all agents that have this skill.

    Args:
        service: DatabaseService instance
        skill_id: Skill ID

    Returns:
        List of dictionaries with agent data + priority

    Example:
        >>> agents = get_skill_agents(db, skill_id=42)
        >>> for agent in agents:
        ...     print(f"{agent['role']} (priority: {agent['priority']})")
    """
    query = """
        SELECT a.id, a.role, a.display_name, a.description, ags.priority
        FROM agents a
        JOIN agent_skills ags ON a.id = ags.agent_id
        WHERE ags.skill_id = ?
        ORDER BY ags.priority DESC, a.role
    """

    cursor = service.conn.execute(query, (skill_id,))
    rows = cursor.fetchall()

    return [dict(row) for row in rows]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _check_agent_exists(service, agent_id: int) -> bool:
    """Check if an agent exists"""
    cursor = service.conn.execute("SELECT 1 FROM agents WHERE id = ?", (agent_id,))
    return cursor.fetchone() is not None


def _get_agent_skill_link(
    service, agent_id: int, skill_id: int
) -> Optional[AgentSkill]:
    """Get existing agent_skill link"""
    query = """
        SELECT id, agent_id, skill_id, priority, created_at
        FROM agent_skills
        WHERE agent_id = ? AND skill_id = ?
    """

    cursor = service.conn.execute(query, (agent_id, skill_id))
    row = cursor.fetchone()

    if not row:
        return None

    return SkillAdapter.agent_skill_from_db(dict(row))
