"""
Skill Adapter - Model ↔ Database Conversion

Handles conversion between Skill domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..models.skill import Skill, AgentSkill, SkillCategory


class SkillAdapter:
    """
    Handles Skill model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ========================================================================
    # MODEL → DATABASE CONVERSIONS
    # ========================================================================

    @staticmethod
    def to_db(skill: Skill) -> Dict[str, Any]:
        """
        Convert Skill model to database row format.

        Args:
            skill: Validated Skill Pydantic model

        Returns:
            Dictionary ready for database insertion/update

        Example:
            >>> skill = Skill(name="python-testing", display_name="Python Testing", ...)
            >>> row = SkillAdapter.to_db(skill)
            >>> # row = {
            >>> #   "name": "python-testing",
            >>> #   "display_name": "Python Testing",
            >>> #   "resources": '{"examples": [], "templates": []}',
            >>> #   ...
            >>> # }
        """
        row = {
            "name": skill.name,
            "display_name": skill.display_name,
            "description": skill.description,
            "category": (
                skill.category.value
                if skill.category and hasattr(skill.category, "value")
                else skill.category
            ),
            "instructions": skill.instructions,
            "resources": json.dumps(skill.resources) if skill.resources else None,
            "provider_config": (
                json.dumps(skill.provider_config) if skill.provider_config else None
            ),
            "enabled": 1 if skill.enabled else 0,
            "created_at": skill.created_at.isoformat(),
            "updated_at": skill.updated_at.isoformat(),
        }

        # Include ID if updating existing skill
        if skill.id is not None:
            row["id"] = skill.id

        return row

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Skill:
        """
        Convert database row to Skill model.

        Args:
            row: Database row dictionary (from sqlite3.Row)

        Returns:
            Validated Skill Pydantic model

        Raises:
            ValueError: If row data is invalid

        Example:
            >>> row = db.fetchone()
            >>> skill = SkillAdapter.from_db(row)
            >>> print(skill.name)  # "python-testing"
        """
        # Parse JSON fields
        resources = None
        if row.get("resources"):
            try:
                resources = json.loads(row["resources"])
            except json.JSONDecodeError:
                resources = None

        provider_config = None
        if row.get("provider_config"):
            try:
                provider_config = json.loads(row["provider_config"])
            except json.JSONDecodeError:
                provider_config = None

        # Parse timestamps
        created_at = (
            datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else datetime.now()
        )
        updated_at = (
            datetime.fromisoformat(row["updated_at"])
            if row.get("updated_at")
            else datetime.now()
        )

        # Parse category enum (may already be a string due to use_enum_values)
        category = row.get("category") if row.get("category") else None

        # Construct Skill model
        return Skill(
            id=row.get("id"),
            name=row["name"],
            display_name=row["display_name"],
            description=row["description"],
            category=category,
            instructions=row["instructions"],
            resources=resources,
            provider_config=provider_config,
            enabled=bool(row.get("enabled", True)),
            created_at=created_at,
            updated_at=updated_at,
        )

    # ========================================================================
    # AGENT SKILL JUNCTION CONVERSIONS
    # ========================================================================

    @staticmethod
    def agent_skill_to_db(agent_skill: AgentSkill) -> Dict[str, Any]:
        """
        Convert AgentSkill model to database row format.

        Args:
            agent_skill: Validated AgentSkill Pydantic model

        Returns:
            Dictionary ready for database insertion/update
        """
        row = {
            "agent_id": agent_skill.agent_id,
            "skill_id": agent_skill.skill_id,
            "priority": agent_skill.priority,
            "created_at": agent_skill.created_at.isoformat(),
        }

        # Include ID if updating existing assignment
        if agent_skill.id is not None:
            row["id"] = agent_skill.id

        return row

    @staticmethod
    def agent_skill_from_db(row: Dict[str, Any]) -> AgentSkill:
        """
        Convert database row to AgentSkill model.

        Args:
            row: Database row dictionary (from sqlite3.Row)

        Returns:
            Validated AgentSkill Pydantic model
        """
        # Parse timestamp
        created_at = (
            datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else datetime.now()
        )

        return AgentSkill(
            id=row.get("id"),
            agent_id=row["agent_id"],
            skill_id=row["skill_id"],
            priority=row.get("priority", 50),
            created_at=created_at,
        )

    # ========================================================================
    # PROGRESSIVE LOADING CONVERSIONS
    # ========================================================================

    @staticmethod
    def to_metadata_only(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert database row to Level 1 metadata (lightweight).

        Excludes instructions and resources for fast loading.

        Args:
            row: Database row dictionary

        Returns:
            Dictionary with id, name, display_name, description, category, enabled
        """
        return {
            "id": row.get("id"),
            "name": row["name"],
            "display_name": row["display_name"],
            "description": row["description"],
            "category": row.get("category"),
            "enabled": bool(row.get("enabled", True)),
        }

    @staticmethod
    def to_instructions_level(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert database row to Level 2 (metadata + instructions).

        Excludes resources for moderate loading.

        Args:
            row: Database row dictionary

        Returns:
            Dictionary with metadata + instructions + provider_config
        """
        metadata = SkillAdapter.to_metadata_only(row)

        # Parse provider_config
        provider_config = None
        if row.get("provider_config"):
            try:
                provider_config = json.loads(row["provider_config"])
            except json.JSONDecodeError:
                provider_config = None

        return {
            **metadata,
            "instructions": row["instructions"],
            "provider_config": provider_config,
        }

    @staticmethod
    def validate_skill_data(data: Dict[str, Any]) -> None:
        """
        Validate skill data before database operations.

        Args:
            data: Dictionary with skill data

        Raises:
            ValueError: If validation fails

        Example:
            >>> SkillAdapter.validate_skill_data({"name": "test", ...})
        """
        # Name validation
        if not data.get("name"):
            raise ValueError("Skill name is required")

        if len(data["name"]) > 64:
            raise ValueError("Skill name must be ≤64 characters")

        # Display name validation
        if not data.get("display_name"):
            raise ValueError("Skill display_name is required")

        if len(data["display_name"]) > 100:
            raise ValueError("Skill display_name must be ≤100 characters")

        # Description validation
        if not data.get("description"):
            raise ValueError("Skill description is required")

        if len(data["description"]) > 1000:
            raise ValueError("Skill description must be ≤1000 characters")

        # Instructions validation
        if not data.get("instructions"):
            raise ValueError("Skill instructions are required")

        # Category validation
        if data.get("category"):
            valid_categories = [cat.value for cat in SkillCategory]
            if data["category"] not in valid_categories:
                raise ValueError(
                    f"Invalid category. Must be one of: {valid_categories}"
                )

        # Resources validation (if provided)
        if data.get("resources"):
            if isinstance(data["resources"], str):
                try:
                    resources = json.loads(data["resources"])
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in resources: {e}")
            else:
                resources = data["resources"]

            # Validate structure
            if not isinstance(resources, dict):
                raise ValueError("Resources must be a dictionary")

            allowed_keys = {"examples", "templates", "docs"}
            for key in resources.keys():
                if key not in allowed_keys:
                    raise ValueError(
                        f"Invalid resources key '{key}'. Allowed: {allowed_keys}"
                    )

        # Provider config validation (if provided)
        if data.get("provider_config"):
            if isinstance(data["provider_config"], str):
                try:
                    provider_config = json.loads(data["provider_config"])
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in provider_config: {e}")
            else:
                provider_config = data["provider_config"]

            # Validate structure
            if not isinstance(provider_config, dict):
                raise ValueError("Provider config must be a dictionary")

            allowed_providers = {"claude-code", "cursor", "codex"}
            for provider in provider_config.keys():
                if provider not in allowed_providers:
                    raise ValueError(
                        f"Invalid provider '{provider}'. Allowed: {allowed_providers}"
                    )

    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================

    @staticmethod
    def to_db_batch(skills: List[Skill]) -> List[Dict[str, Any]]:
        """
        Convert multiple Skill models to database row format.

        Args:
            skills: List of validated Skill Pydantic models

        Returns:
            List of dictionaries ready for batch insertion
        """
        return [SkillAdapter.to_db(skill) for skill in skills]

    @staticmethod
    def from_db_batch(rows: List[Dict[str, Any]]) -> List[Skill]:
        """
        Convert multiple database rows to Skill models.

        Args:
            rows: List of database row dictionaries

        Returns:
            List of validated Skill Pydantic models
        """
        return [SkillAdapter.from_db(row) for row in rows]
