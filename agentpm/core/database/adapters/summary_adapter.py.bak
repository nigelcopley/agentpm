"""
Summary Adapter - Database Conversion Layer

Handles conversion between Summary Pydantic models and database rows.
Follows APM (Agent Project Manager) three-layer architecture pattern.

Pattern: Type-safe conversion with validation
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.summary import Summary


class SummaryAdapter:
    """
    Adapter for converting between Summary models and database rows.
    
    Handles:
    - Model to database row conversion
    - Database row to model conversion
    - JSON serialization/deserialization for metadata
    - Type validation and error handling
    """

    @staticmethod
    def to_db(summary: Summary) -> Dict[str, Any]:
        """
        Convert Summary model to database row format.
        
        Args:
            summary: Summary model to convert
            
        Returns:
            Dictionary with database column names as keys
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not summary.entity_type:
            raise ValueError("entity_type is required")
        if not summary.entity_id or summary.entity_id <= 0:
            raise ValueError("entity_id must be positive integer")
        if not summary.summary_type:
            raise ValueError("summary_type is required")
        if not summary.summary_text or len(summary.summary_text.strip()) < 10:
            raise ValueError("summary_text must be at least 10 characters")
        if not summary.created_by or len(summary.created_by.strip()) == 0:
            raise ValueError("created_by is required")

        # Convert context_metadata to JSON string
        context_metadata_json = None
        if summary.context_metadata:
            try:
                context_metadata_json = json.dumps(summary.context_metadata)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid context_metadata: {e}")

        return {
            'id': summary.id,
            'entity_type': summary.entity_type.value,
            'entity_id': summary.entity_id,
            'summary_type': summary.summary_type.value,
            'summary_text': summary.summary_text,
            'context_metadata': context_metadata_json,
            'created_at': summary.created_at.isoformat() if summary.created_at else None,
            'created_by': summary.created_by,
            'session_id': summary.session_id,
            'session_date': summary.session_date,
            'session_duration_hours': summary.session_duration_hours,
        }

    @staticmethod
    def from_row(row: Dict[str, Any]) -> Summary:
        """
        Convert database row to Summary model.
        
        Args:
            row: Database row dictionary
            
        Returns:
            Summary model instance
            
        Raises:
            ValueError: If row data is invalid
            KeyError: If required columns are missing
        """
        if not row:
            raise ValueError("Row data is required")

        # Parse context_metadata from JSON
        context_metadata = None
        if row.get('context_metadata'):
            try:
                context_metadata = json.loads(row['context_metadata'])
            except (json.JSONDecodeError, TypeError) as e:
                # Log warning but don't fail - metadata is optional
                context_metadata = None

        # Parse created_at datetime
        created_at = None
        if row.get('created_at'):
            try:
                created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # If parsing fails, leave as None
                created_at = None

        return Summary(
            id=row.get('id'),
            entity_type=row['entity_type'],
            entity_id=row['entity_id'],
            summary_type=row['summary_type'],
            summary_text=row['summary_text'],
            context_metadata=context_metadata,
            created_at=created_at,
            created_by=row['created_by'],
            session_id=row.get('session_id'),
            session_date=row.get('session_date'),
            session_duration_hours=row.get('session_duration_hours'),
        )

    @staticmethod
    def validate_row(row: Dict[str, Any]) -> None:
        """
        Validate database row data before conversion.
        
        Args:
            row: Database row dictionary
            
        Raises:
            ValueError: If row data is invalid
            KeyError: If required columns are missing
        """
        if not row:
            raise ValueError("Row data is required")

        # Check required fields
        required_fields = ['entity_type', 'entity_id', 'summary_type', 'summary_text', 'created_by']
        for field in required_fields:
            if field not in row:
                raise KeyError(f"Required field '{field}' is missing")

        # Validate entity_id is positive integer
        if not isinstance(row['entity_id'], int) or row['entity_id'] <= 0:
            raise ValueError("entity_id must be positive integer")

        # Validate summary_text length
        if not isinstance(row['summary_text'], str) or len(row['summary_text'].strip()) < 10:
            raise ValueError("summary_text must be at least 10 characters")

        # Validate created_by is non-empty string
        if not isinstance(row['created_by'], str) or len(row['created_by'].strip()) == 0:
            raise ValueError("created_by must be non-empty string")

        # Validate session_id if present
        if row.get('session_id') is not None:
            if not isinstance(row['session_id'], int) or row['session_id'] <= 0:
                raise ValueError("session_id must be positive integer")

        # Validate session_duration_hours if present
        if row.get('session_duration_hours') is not None:
            if not isinstance(row['session_duration_hours'], (int, float)) or row['session_duration_hours'] < 0:
                raise ValueError("session_duration_hours must be non-negative number")

        # Validate context_metadata JSON if present
        if row.get('context_metadata'):
            try:
                json.loads(row['context_metadata'])
            except (json.JSONDecodeError, TypeError):
                raise ValueError("context_metadata must be valid JSON")

    @staticmethod
    def to_dict(summary: Summary) -> Dict[str, Any]:
        """
        Convert Summary model to dictionary for serialization.
        
        Args:
            summary: Summary model to convert
            
        Returns:
            Dictionary representation
        """
        return summary.model_dump()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Summary:
        """
        Create Summary model from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Summary model instance
        """
        return Summary(**data)

    @staticmethod
    def get_entity_reference(entity_type: str, entity_id: int) -> str:
        """
        Get human-readable entity reference.
        
        Args:
            entity_type: Entity type string
            entity_id: Entity ID
            
        Returns:
            Human-readable reference string
        """
        return f"{entity_type} #{entity_id}"

    @staticmethod
    def format_summary_for_display(summary: Summary) -> str:
        """
        Format summary for human-readable display.
        
        Args:
            summary: Summary model
            
        Returns:
            Formatted string for display
        """
        lines = []
        lines.append(f"Summary: {summary.get_summary_title()}")
        lines.append(f"Entity: {summary.get_entity_reference()}")
        lines.append(f"Type: {summary.summary_type.value.replace('_', ' ').title()}")
        lines.append(f"Created: {summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'}")
        lines.append(f"Author: {summary.created_by}")
        
        if summary.session_id:
            lines.append(f"Session: #{summary.session_id}")
        
        if summary.session_date:
            lines.append(f"Session Date: {summary.session_date}")
        
        if summary.session_duration_hours:
            lines.append(f"Duration: {summary.session_duration_hours:.1f}h")
        
        lines.append("")
        lines.append("Content:")
        lines.append(summary.summary_text)
        
        if summary.context_metadata:
            lines.append("")
            lines.append("Metadata:")
            for key, value in summary.context_metadata.items():
                if isinstance(value, list):
                    lines.append(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
