"""
Visibility Policy Adapter - Model ↔ Database Conversion

Handles conversion between VisibilityPolicy domain models and database rows.
Provides CRUD operations following three-layer pattern:
  CLI → Adapter (validates Pydantic) → Methods (executes SQL)

Part of Work Item #164: Auto-Generate Document File Paths
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...models.document_visibility import VisibilityPolicy


class VisibilityPolicyAdapter:
    """
    Handles VisibilityPolicy model <-> Database row conversions.

    This is the BOUNDARY LAYER between services and database.
    Services should call these methods for policy data access.
    """

    # ============================================================================
    # CRUD OPERATIONS (Service Entry Points)
    # ============================================================================

    @staticmethod
    def create(service, policy: VisibilityPolicy) -> VisibilityPolicy:
        """
        Create a new visibility policy.

        Args:
            service: DatabaseService instance
            policy: Validated VisibilityPolicy Pydantic model

        Returns:
            Created VisibilityPolicy with database ID

        Example:
            >>> from agentpm.core.database.adapters import VisibilityPolicyAdapter
            >>> policy = VisibilityPolicy(category="planning", doc_type="idea", base_score=20)
            >>> created = VisibilityPolicyAdapter.create(db, policy)
        """
        # Convert model to database format
        data = VisibilityPolicyAdapter.to_db(policy)

        # Insert into database
        with service.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO document_visibility_policies (
                    category, doc_type, default_visibility, default_audience,
                    requires_review, auto_publish_on_approved, base_score,
                    force_private, force_public, description, rationale,
                    auto_publish_trigger, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['category'],
                data['doc_type'],
                data['default_visibility'],
                data['default_audience'],
                data['requires_review'],
                data['auto_publish_on_approved'],
                data['base_score'],
                data['force_private'],
                data['force_public'],
                data['description'],
                data['rationale'],
                data['auto_publish_trigger'],
                data['created_at'],
                data['updated_at'],
            ))

            policy_id = cursor.lastrowid

        # Fetch and return created policy
        return VisibilityPolicyAdapter.get(service, policy_id)

    @staticmethod
    def get(service, policy_id: int) -> Optional[VisibilityPolicy]:
        """
        Get visibility policy by ID.

        Args:
            service: DatabaseService instance
            policy_id: Policy database ID

        Returns:
            VisibilityPolicy if found, None otherwise
        """
        with service.connect() as conn:
            cursor = conn.execute("""
                SELECT * FROM document_visibility_policies
                WHERE id = ?
            """, (policy_id,))

            row = cursor.fetchone()

            if not row:
                return None

            return VisibilityPolicyAdapter.from_db(dict(row))

    @staticmethod
    def get_by_type(service, category: str, doc_type: str) -> Optional[VisibilityPolicy]:
        """
        Get visibility policy by category and document type.

        Args:
            service: DatabaseService instance
            category: Document category (e.g., 'planning', 'architecture')
            doc_type: Document type (e.g., 'idea', 'adr')

        Returns:
            VisibilityPolicy if found, None otherwise
        """
        with service.connect() as conn:
            cursor = conn.execute("""
                SELECT * FROM document_visibility_policies
                WHERE category = ? AND doc_type = ?
            """, (category, doc_type))

            row = cursor.fetchone()

            if not row:
                return None

            return VisibilityPolicyAdapter.from_db(dict(row))

    @staticmethod
    def list(service, category: Optional[str] = None) -> List[VisibilityPolicy]:
        """
        List all visibility policies with optional category filter.

        Args:
            service: DatabaseService instance
            category: Optional category filter

        Returns:
            List of VisibilityPolicy models
        """
        with service.connect() as conn:
            if category:
                cursor = conn.execute("""
                    SELECT * FROM document_visibility_policies
                    WHERE category = ?
                    ORDER BY category, doc_type
                """, (category,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM document_visibility_policies
                    ORDER BY category, doc_type
                """)

            rows = cursor.fetchall()

            return [VisibilityPolicyAdapter.from_db(dict(row)) for row in rows]

    @staticmethod
    def update(service, policy: VisibilityPolicy) -> Optional[VisibilityPolicy]:
        """
        Update visibility policy.

        Args:
            service: DatabaseService instance
            policy: VisibilityPolicy model with updated fields

        Returns:
            Updated VisibilityPolicy if found, None otherwise

        Raises:
            ValueError: If policy.id is None
        """
        if policy.id is None:
            raise ValueError("Cannot update policy without ID")

        # Convert model to database format
        data = VisibilityPolicyAdapter.to_db(policy)
        data['updated_at'] = datetime.now().isoformat()

        with service.transaction() as conn:
            conn.execute("""
                UPDATE document_visibility_policies
                SET category = ?,
                    doc_type = ?,
                    default_visibility = ?,
                    default_audience = ?,
                    requires_review = ?,
                    auto_publish_on_approved = ?,
                    base_score = ?,
                    force_private = ?,
                    force_public = ?,
                    description = ?,
                    rationale = ?,
                    auto_publish_trigger = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                data['category'],
                data['doc_type'],
                data['default_visibility'],
                data['default_audience'],
                data['requires_review'],
                data['auto_publish_on_approved'],
                data['base_score'],
                data['force_private'],
                data['force_public'],
                data['description'],
                data['rationale'],
                data['auto_publish_trigger'],
                data['updated_at'],
                policy.id,
            ))

        # Fetch and return updated policy
        return VisibilityPolicyAdapter.get(service, policy.id)

    @staticmethod
    def delete(service, policy_id: int) -> bool:
        """
        Delete visibility policy by ID.

        Args:
            service: DatabaseService instance
            policy_id: Policy database ID

        Returns:
            True if deleted, False if not found
        """
        with service.transaction() as conn:
            cursor = conn.execute("""
                DELETE FROM document_visibility_policies
                WHERE id = ?
            """, (policy_id,))

            return cursor.rowcount > 0

    # ============================================================================
    # MODEL CONVERSION (Internal Use)
    # ============================================================================

    @staticmethod
    def to_db(policy: VisibilityPolicy) -> Dict[str, Any]:
        """
        Convert VisibilityPolicy model to database row format.

        Args:
            policy: VisibilityPolicy domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        now = datetime.now().isoformat()

        return {
            'category': policy.category,
            'doc_type': policy.doc_type,
            'default_visibility': policy.default_visibility,
            'default_audience': policy.default_audience,
            'requires_review': 1 if policy.requires_review else 0,  # Boolean to int
            'auto_publish_on_approved': 1 if policy.auto_publish_on_approved else 0,  # Boolean to int
            'base_score': policy.base_score,
            'force_private': 1 if policy.force_private else 0,  # Boolean to int
            'force_public': 1 if policy.force_public else 0,  # Boolean to int
            'description': policy.description,
            'rationale': policy.rationale,
            'auto_publish_trigger': policy.auto_publish_trigger,
            'created_at': policy.created_at.isoformat() if policy.created_at else now,
            'updated_at': policy.updated_at.isoformat() if policy.updated_at else now,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> VisibilityPolicy:
        """
        Convert database row to VisibilityPolicy model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated VisibilityPolicy model
        """
        return VisibilityPolicy(
            id=row.get('id'),
            category=row['category'],
            doc_type=row['doc_type'],
            default_visibility=row.get('default_visibility', 'private'),
            default_audience=row.get('default_audience', 'internal'),
            requires_review=bool(row.get('requires_review', 0)),  # Int to boolean
            auto_publish_on_approved=bool(row.get('auto_publish_on_approved', 0)),  # Int to boolean
            base_score=row.get('base_score', 50),
            force_private=bool(row.get('force_private', 0)),  # Int to boolean
            force_public=bool(row.get('force_public', 0)),  # Int to boolean
            description=row.get('description'),
            rationale=row.get('rationale'),
            auto_publish_trigger=row.get('auto_publish_trigger'),
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
