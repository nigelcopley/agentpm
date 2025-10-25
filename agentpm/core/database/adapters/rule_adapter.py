"""
Rule Adapter - Model ↔ Database Conversion

Handles conversion between Rule domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.rule import Rule
from ..enums import EnforcementLevel


class RuleAdapter:
    """
    Handles Rule model <-> Database row conversions.

    This is the BOUNDARY LAYER between CLI and database methods.
    CLI commands should call these methods, NOT methods directly.
    """

    # ============================================================================
    # CRUD OPERATIONS (CLI Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, rule: Rule) -> Rule:
        """
        Create a new rule (CLI entry point).

        Three-layer pattern:
          1. Validate Pydantic model (automatic via type hints)
          2. Delegate to methods layer
          3. Return validated Rule

        Args:
            service: DatabaseService instance
            rule: Validated Rule Pydantic model

        Returns:
            Created Rule with database ID

        Raises:
            ValidationError: If project_id invalid

        Example:
            >>> from agentpm.core.database.adapters import RuleAdapter
            >>> rule = Rule(project_id=1, rule_id="CUSTOM-001", ...)
            >>> created = RuleAdapter.create(db, rule)
        """
        from ..methods import rules as rule_methods
        return rule_methods.create_rule(service, rule)

    @staticmethod
    def get(service, rule_db_id: int) -> Optional[Rule]:
        """
        Get rule by database ID (CLI entry point).

        Args:
            service: DatabaseService instance
            rule_db_id: Rule database ID

        Returns:
            Rule if found, None otherwise
        """
        from ..methods import rules as rule_methods
        return rule_methods.get_rule(service, rule_db_id)

    @staticmethod
    def get_by_rule_id(service, project_id: int, rule_id: str) -> Optional[Rule]:
        """
        Get rule by project and rule_id (e.g., 'CI-004') (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Project ID
            rule_id: Rule ID (e.g., "DP-001", "CI-004")

        Returns:
            Rule if found, None otherwise
        """
        from ..methods import rules as rule_methods
        return rule_methods.get_rule_by_rule_id(service, project_id, rule_id)

    @staticmethod
    def list(
        service,
        project_id: Optional[int] = None,
        enforcement_level: Optional[EnforcementLevel] = None,
        enabled_only: bool = False
    ) -> List[Rule]:
        """
        List rules with optional filters (CLI entry point).

        Args:
            service: DatabaseService instance
            project_id: Optional project filter
            enforcement_level: Optional enforcement level filter
            enabled_only: If True, only return enabled rules

        Returns:
            List of Rule models
        """
        from ..methods import rules as rule_methods
        return rule_methods.list_rules(
            service,
            project_id=project_id,
            enforcement_level=enforcement_level,
            enabled_only=enabled_only
        )

    @staticmethod
    def update(service, rule_db_id: int, **updates) -> Optional[Rule]:
        """
        Update rule fields (CLI entry point).

        Args:
            service: DatabaseService instance
            rule_db_id: Rule database ID to update
            **updates: Field updates (e.g., enabled=True, enforcement_level=EnforcementLevel.BLOCK)

        Returns:
            Updated Rule if found, None otherwise
        """
        from ..methods import rules as rule_methods
        return rule_methods.update_rule(service, rule_db_id, **updates)

    @staticmethod
    def delete(service, rule_db_id: int) -> bool:
        """
        Delete rule by ID (CLI entry point).

        Args:
            service: DatabaseService instance
            rule_db_id: Rule database ID to delete

        Returns:
            True if deleted, False if not found
        """
        from ..methods import rules as rule_methods
        return rule_methods.delete_rule(service, rule_db_id)

    @staticmethod
    def get_blocking_rules(service, project_id: int) -> List[Rule]:
        """
        Get all enabled BLOCK-level rules for a project (CLI entry point).

        These rules must be enforced (hard stop if violated).

        Args:
            service: DatabaseService instance
            project_id: Project ID

        Returns:
            List of blocking Rule models
        """
        from ..methods import rules as rule_methods
        return rule_methods.get_blocking_rules(service, project_id)

    # ============================================================================
    # MODEL CONVERSION (Used by Methods Layer)
    # ============================================================================

    @staticmethod
    def to_db(rule: Rule) -> Dict[str, Any]:
        """
        Convert Rule model to database row format.

        Args:
            rule: Rule domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'project_id': rule.project_id,
            'rule_id': rule.rule_id,
            'name': rule.name,
            'description': rule.description,
            'category': rule.category,
            'enforcement_level': rule.enforcement_level.value,
            'validation_logic': rule.validation_logic,
            'error_message': rule.error_message,
            'config': json.dumps(rule.config) if rule.config else None,
            'enabled': 1 if rule.enabled else 0,  # SQLite boolean
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Rule:
        """
        Convert database row to Rule model with hybrid YAML/JSON parsing.

        Supports both JSON (V2 standard) and YAML (legacy V1 format) for
        backwards compatibility during migration period.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Rule model

        Note:
            Config parsing tries JSON first (future format), falls back to YAML
            (current format). This allows gradual migration from YAML to JSON.
        """
        # Parse config with hybrid YAML/JSON support
        config_data = row.get('config')
        if config_data:
            try:
                # Try JSON first (V2 standard format)
                config = json.loads(config_data)
                # Handle JSON null
                if config is None:
                    config = {}
            except json.JSONDecodeError:
                # Fall back to YAML (legacy V1 format from migration)
                import yaml
                try:
                    config = yaml.safe_load(config_data)
                    # Handle YAML null or None
                    if config is None:
                        config = {}
                except yaml.YAMLError:
                    # If both parsers fail, use empty config
                    config = {}
        else:
            config = {}

        return Rule(
            id=row.get('id'),
            project_id=row['project_id'],
            rule_id=row['rule_id'],
            name=row['name'],
            description=row.get('description'),
            category=row.get('category'),
            enforcement_level=EnforcementLevel(
                row.get('enforcement_level', EnforcementLevel.GUIDE.value)
            ),
            validation_logic=row.get('validation_logic'),
            error_message=row.get('error_message'),
            config=config,
            enabled=bool(row.get('enabled', 1)),
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