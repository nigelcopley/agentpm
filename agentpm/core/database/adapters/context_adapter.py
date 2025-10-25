"""
Context Adapter - Model ↔ Database Conversion

Handles conversion between Context domain models and database rows.

Most complex adapter due to:
- Polymorphic relationships (entity_type + entity_id)
- UnifiedSixW JSON serialization
- Resource file vs entity context handling

THREE-LAYER PATTERN (DP-001):
  CLI -> ContextAdapter (validates Pydantic) -> context_methods (executes SQL)
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.context import Context, UnifiedSixW
from ..enums import ContextType, ResourceType, EntityType, ConfidenceBand


class ContextAdapter:
    """Handles Context model <-> Database row conversions"""

    @staticmethod
    def to_db(context: Context) -> Dict[str, Any]:
        """
        Convert Context model to database row format.

        Handles both resource files and entity contexts with appropriate fields.

        Args:
            context: Context domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        db_data = {
            'project_id': context.project_id,
            'context_type': context.context_type.value,
        }

        # Resource file fields
        if context.is_resource_file():
            db_data['file_path'] = context.file_path
            db_data['file_hash'] = context.file_hash
            db_data['resource_type'] = context.resource_type.value if context.resource_type else None

        # Entity context fields
        elif context.is_entity_context():
            db_data['entity_type'] = context.entity_type.value if context.entity_type else None
            db_data['entity_id'] = context.entity_id

            # Serialize UnifiedSixW to JSON
            if context.six_w:
                db_data['six_w_data'] = json.dumps({
                    # WHO
                    'end_users': context.six_w.end_users,
                    'implementers': context.six_w.implementers,
                    'reviewers': context.six_w.reviewers,
                    # WHAT
                    'functional_requirements': context.six_w.functional_requirements,
                    'technical_constraints': context.six_w.technical_constraints,
                    'acceptance_criteria': context.six_w.acceptance_criteria,
                    # WHERE
                    'affected_services': context.six_w.affected_services,
                    'repositories': context.six_w.repositories,
                    'deployment_targets': context.six_w.deployment_targets,
                    # WHEN
                    'deadline': context.six_w.deadline.isoformat() if context.six_w.deadline else None,
                    'dependencies_timeline': context.six_w.dependencies_timeline,
                    # WHY
                    'business_value': context.six_w.business_value,
                    'risk_if_delayed': context.six_w.risk_if_delayed,
                    # HOW
                    'suggested_approach': context.six_w.suggested_approach,
                    'existing_patterns': context.six_w.existing_patterns,
                }, default=str)
            else:
                db_data['six_w_data'] = None

            # Confidence scoring
            db_data['confidence_score'] = context.confidence_score
            db_data['confidence_band'] = context.confidence_band.value if context.confidence_band else None
            db_data['confidence_factors'] = json.dumps(context.confidence_factors) if context.confidence_factors else None

            # NEW: Rich context data
            db_data['context_data'] = json.dumps(context.context_data) if context.context_data else None

        return db_data

    @staticmethod
    def from_db(row: Dict[str, Any]) -> Context:
        """
        Convert database row to Context model.

        Handles polymorphic structure and optional fields.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated Context model
        """
        # Parse UnifiedSixW from JSON
        six_w_data = row.get('six_w_data')
        six_w = None
        if six_w_data:
            try:
                data = json.loads(six_w_data)

                # Parse deadline datetime
                deadline_str = data.get('deadline')
                deadline = None
                if deadline_str:
                    try:
                        deadline = datetime.fromisoformat(deadline_str)
                    except (ValueError, AttributeError):
                        deadline = None

                six_w = UnifiedSixW(
                    # WHO
                    end_users=data.get('end_users', []),
                    implementers=data.get('implementers', []),
                    reviewers=data.get('reviewers', []),
                    # WHAT
                    functional_requirements=data.get('functional_requirements', []),
                    technical_constraints=data.get('technical_constraints', []),
                    acceptance_criteria=data.get('acceptance_criteria', []),
                    # WHERE
                    affected_services=data.get('affected_services', []),
                    repositories=data.get('repositories', []),
                    deployment_targets=data.get('deployment_targets', []),
                    # WHEN
                    deadline=deadline,
                    dependencies_timeline=data.get('dependencies_timeline', []),
                    # WHY
                    business_value=data.get('business_value'),
                    risk_if_delayed=data.get('risk_if_delayed'),
                    # HOW
                    suggested_approach=data.get('suggested_approach'),
                    existing_patterns=data.get('existing_patterns', []),
                )
            except (json.JSONDecodeError, TypeError):
                six_w = None

        # Parse entity_type enum
        entity_type_str = row.get('entity_type')
        entity_type = EntityType(entity_type_str) if entity_type_str else None

        # Parse resource_type enum
        resource_type_str = row.get('resource_type')
        resource_type = ResourceType(resource_type_str) if resource_type_str else None

        # Parse confidence_band enum
        confidence_band_str = row.get('confidence_band')
        confidence_band = ConfidenceBand(confidence_band_str) if confidence_band_str else None

        # Parse confidence_factors JSON
        confidence_factors_str = row.get('confidence_factors')
        confidence_factors = json.loads(confidence_factors_str) if confidence_factors_str else None

        # NEW: Parse context_data JSON
        context_data_str = row.get('context_data')
        context_data = json.loads(context_data_str) if context_data_str else None

        return Context(
            id=row.get('id'),
            project_id=row['project_id'],
            context_type=ContextType(row['context_type']),

            # Resource file fields
            file_path=row.get('file_path'),
            file_hash=row.get('file_hash'),
            resource_type=resource_type,

            # Entity context fields
            entity_type=entity_type,
            entity_id=row.get('entity_id'),
            six_w=six_w,

            # Confidence scoring
            confidence_score=row.get('confidence_score'),
            confidence_band=confidence_band,
            confidence_factors=confidence_factors,

            # NEW: Rich context data
            context_data=context_data,

            # Timestamps
            created_at=_parse_datetime(row.get('created_at')),
            updated_at=_parse_datetime(row.get('updated_at')),
        )


    # ========================================================================
    # CRUD OPERATIONS (Three-Layer Pattern)
    # ========================================================================
    # These methods delegate to context_methods for actual database operations
    # CLI commands should call these adapter methods instead of direct methods calls

    @staticmethod
    def create(db, context: Context) -> Context:
        """
        Create a new context.

        THREE-LAYER: CLI -> Adapter (validates model) -> Methods (executes SQL)

        Args:
            db: DatabaseService instance
            context: Context model to create

        Returns:
            Created Context with database ID
        """
        from ..methods import contexts as context_methods
        return context_methods.create_context(db, context)

    @staticmethod
    def get(db, context_id: int) -> Optional[Context]:
        """
        Get context by ID.

        Args:
            db: DatabaseService instance
            context_id: Context ID

        Returns:
            Context model or None if not found
        """
        from ..methods import contexts as context_methods
        return context_methods.get_context(db, context_id)

    @staticmethod
    def get_entity_context(
        db,
        entity_type: EntityType,
        entity_id: int,
        context_type: Optional[ContextType] = None
    ) -> Optional[Context]:
        """
        Get context for a specific entity.

        Args:
            db: DatabaseService instance
            entity_type: Type of entity
            entity_id: Entity ID
            context_type: Optional context type filter

        Returns:
            Context model or None if not found
        """
        from ..methods import contexts as context_methods
        return context_methods.get_entity_context(db, entity_type, entity_id, context_type)

    @staticmethod
    def update(db, context_id: int, **updates) -> Optional[Context]:
        """
        Update context fields.

        Args:
            db: DatabaseService instance
            context_id: Context ID
            **updates: Field updates (six_w, confidence_score, etc.)

        Returns:
            Updated Context model or None if not found
        """
        from ..methods import contexts as context_methods
        return context_methods.update_context(db, context_id, **updates)

    @staticmethod
    def delete(db, context_id: int) -> bool:
        """
        Delete context.

        Args:
            db: DatabaseService instance
            context_id: Context ID

        Returns:
            True if deleted, False if not found
        """
        from ..methods import contexts as context_methods
        return context_methods.delete_context(db, context_id)

    @staticmethod
    def list_contexts(
        db,
        project_id: Optional[int] = None,
        entity_type: Optional[EntityType] = None,
        context_type: Optional[ContextType] = None
    ) -> List[Context]:
        """
        List contexts with optional filters.

        Args:
            db: DatabaseService instance
            project_id: Optional project filter
            entity_type: Optional entity type filter
            context_type: Optional context type filter

        Returns:
            List of Context models
        """
        from ..methods import contexts as context_methods
        return context_methods.list_contexts(db, project_id, entity_type, context_type)

    # ========================================================================
    # RICH CONTEXT OPERATIONS
    # ========================================================================

    @staticmethod
    def create_rich_context(
        db,
        entity_type: EntityType,
        entity_id: int,
        context_type: ContextType,
        context_data: dict,
        confidence_score: Optional[float] = None
    ) -> Context:
        """
        Create rich context for an entity.

        Args:
            db: DatabaseService instance
            entity_type: Type of entity
            entity_id: Entity ID
            context_type: Type of rich context
            context_data: Rich context data dictionary
            confidence_score: Optional confidence score (auto-calculated if not provided)

        Returns:
            Created Context with rich context data
        """
        from ..methods import contexts as context_methods
        return context_methods.create_rich_context(
            db, entity_type, entity_id, context_type, context_data, confidence_score
        )

    @staticmethod
    def update_rich_context(
        db,
        context_id: int,
        context_data: dict,
        confidence_score: Optional[float] = None
    ) -> Optional[Context]:
        """
        Update rich context data.

        Args:
            db: DatabaseService instance
            context_id: Context ID
            context_data: Updated rich context data
            confidence_score: Optional updated confidence score

        Returns:
            Updated Context or None if not found
        """
        from ..methods import contexts as context_methods
        return context_methods.update_rich_context(db, context_id, context_data, confidence_score)

    @staticmethod
    def get_rich_contexts_by_entity(
        db,
        entity_type: EntityType,
        entity_id: int,
        context_types: Optional[List[ContextType]] = None
    ) -> List[Context]:
        """
        Get all rich contexts for an entity.

        Args:
            db: DatabaseService instance
            entity_type: Type of entity
            entity_id: Entity ID
            context_types: Optional list of context types to filter

        Returns:
            List of Context models with rich context data
        """
        from ..methods import contexts as context_methods
        return context_methods.get_rich_contexts_by_entity(db, entity_type, entity_id, context_types)

    @staticmethod
    def validate_rich_context_completeness(
        db,
        entity_type: EntityType,
        entity_id: int,
        required_context_types: Optional[List[ContextType]] = None
    ) -> dict:
        """
        Validate completeness of rich context for an entity.

        Args:
            db: DatabaseService instance
            entity_type: Type of entity
            entity_id: Entity ID
            required_context_types: Optional list of required context types

        Returns:
            Validation result dictionary with completeness score and missing types
        """
        from ..methods import contexts as context_methods
        return context_methods.validate_rich_context_completeness(
            db, entity_type, entity_id, required_context_types
        )

    @staticmethod
    def generate_documents_from_rich_context(
        db,
        entity_type: EntityType,
        entity_id: int,
        context_type: ContextType,
        document_type: 'DocumentType'
    ) -> dict:
        """
        Generate document from rich context data.

        Args:
            db: DatabaseService instance
            entity_type: Type of entity
            entity_id: Entity ID
            context_type: Type of rich context
            document_type: Type of document to generate

        Returns:
            Result dictionary with success status and generated content
        """
        from ..methods import contexts as context_methods
        return context_methods.generate_documents_from_rich_context(
            db, entity_type, entity_id, context_type, document_type
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