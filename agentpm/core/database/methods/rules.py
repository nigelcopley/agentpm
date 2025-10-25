"""
Rules CRUD Methods - Type-Safe Database Operations

Implements CRUD operations for Rule entities with enforcement level queries.

Pattern: Type-safe method signatures with Rule model
"""

from typing import Optional, List
import sqlite3

from ..models import Rule
from ..adapters import RuleAdapter
from ..enums import EnforcementLevel


def create_rule(service, rule: Rule) -> Rule:
    """
    Create a new rule.

    Args:
        service: DatabaseService instance
        rule: Rule model to create

    Returns:
        Created Rule with database ID
    """
    # Validate project exists
    project_exists = _check_project_exists(service, rule.project_id)
    if not project_exists:
        from ..service import ValidationError
        raise ValidationError(f"Project {rule.project_id} does not exist")

    # Convert model to database format
    db_data = RuleAdapter.to_db(rule)

    query = """
        INSERT INTO rules (project_id, rule_id, name, description, category,
                          enforcement_level, validation_logic, error_message,
                          config, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        db_data['project_id'],
        db_data['rule_id'],
        db_data['name'],
        db_data['description'],
        db_data['category'],
        db_data['enforcement_level'],
        db_data['validation_logic'],
        db_data['error_message'],
        db_data['config'],
        db_data['enabled'],
    )

    with service.transaction() as conn:
        cursor = conn.execute(query, params)
        rule_db_id = cursor.lastrowid

    return get_rule(service, rule_db_id)


def get_rule(service, rule_db_id: int) -> Optional[Rule]:
    """Get rule by database ID"""
    query = "SELECT * FROM rules WHERE id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (rule_db_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return RuleAdapter.from_db(dict(row))


def get_rule_by_rule_id(service, project_id: int, rule_id: str) -> Optional[Rule]:
    """Get rule by project and rule_id (e.g., 'CI-004')"""
    query = "SELECT * FROM rules WHERE project_id = ? AND rule_id = ?"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, (project_id, rule_id))
        row = cursor.fetchone()

    if not row:
        return None

    return RuleAdapter.from_db(dict(row))


def update_rule(service, rule_db_id: int, **updates) -> Optional[Rule]:
    """Update rule with validation"""
    existing = get_rule(service, rule_db_id)
    if not existing:
        return None

    updated_rule = existing.model_copy(update=updates)
    db_data = RuleAdapter.to_db(updated_rule)

    set_clause = ', '.join(f"{k} = ?" for k in db_data.keys())
    query = f"UPDATE rules SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params = (*db_data.values(), rule_db_id)

    with service.transaction() as conn:
        conn.execute(query, params)

    return get_rule(service, rule_db_id)


def delete_rule(service, rule_db_id: int) -> bool:
    """Delete rule by ID"""
    query = "DELETE FROM rules WHERE id = ?"

    with service.transaction() as conn:
        cursor = conn.execute(query, (rule_db_id,))
        return cursor.rowcount > 0


def list_rules(
    service,
    project_id: Optional[int] = None,
    enforcement_level: Optional[EnforcementLevel] = None,
    enabled_only: bool = False
) -> List[Rule]:
    """
    List rules with optional filters.

    Args:
        service: DatabaseService instance
        project_id: Optional project filter
        enforcement_level: Optional enforcement level filter
        enabled_only: If True, only return enabled rules

    Returns:
        List of Rule models
    """
    query = "SELECT * FROM rules WHERE 1=1"
    params = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    if enforcement_level:
        query += " AND enforcement_level = ?"
        params.append(enforcement_level.value)

    if enabled_only:
        query += " AND enabled = 1"

    query += " ORDER BY enforcement_level ASC, rule_id ASC"

    with service.connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

    return [RuleAdapter.from_db(dict(row)) for row in rows]


def get_blocking_rules(service, project_id: int) -> List[Rule]:
    """
    Get all enabled BLOCK-level rules for a project.

    These rules must be enforced (hard stop if violated).

    Args:
        service: DatabaseService instance
        project_id: Project ID

    Returns:
        List of blocking Rule models
    """
    return list_rules(
        service,
        project_id=project_id,
        enforcement_level=EnforcementLevel.BLOCK,
        enabled_only=True
    )


def _check_project_exists(service, project_id: int) -> bool:
    """Check if project exists"""
    query = "SELECT 1 FROM projects WHERE id = ?"
    with service.connect() as conn:
        cursor = conn.execute(query, (project_id,))
        return cursor.fetchone() is not None