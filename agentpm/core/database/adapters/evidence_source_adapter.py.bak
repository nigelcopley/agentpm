"""
Evidence Source Adapter - Model ↔ Database Conversion

Handles conversion between EvidenceSource domain models and database rows.

Migration: 0011 (evidence_sources table)
"""

from typing import Dict, Any
from datetime import datetime

from ..models.evidence_source import EvidenceSource
from ..enums import EntityType, SourceType


class EvidenceSourceAdapter:
    """Handles EvidenceSource model <-> Database row conversions"""

    @staticmethod
    def to_db(evidence: EvidenceSource) -> Dict[str, Any]:
        """
        Convert EvidenceSource model to database row format.

        Args:
            evidence: EvidenceSource domain model

        Returns:
            Dictionary ready for database insertion/update
        """
        return {
            'entity_type': evidence.entity_type.value,  # Enum to string
            'entity_id': evidence.entity_id,
            'url': evidence.url,
            'source_type': evidence.source_type.value if evidence.source_type else None,  # Enum to string
            'excerpt': evidence.excerpt,
            'captured_at': evidence.captured_at.isoformat() if evidence.captured_at else None,
            'content_hash': evidence.content_hash,
            'confidence': evidence.confidence,
            'created_by': evidence.created_by,
            'created_at': evidence.created_at.isoformat() if evidence.created_at else None,
        }

    @staticmethod
    def from_db(row: Dict[str, Any]) -> EvidenceSource:
        """
        Convert database row to EvidenceSource model.

        Args:
            row: Database row (dict-like from sqlite3.Row)

        Returns:
            Validated EvidenceSource model
        """
        return EvidenceSource(
            id=row.get('id'),
            entity_type=EntityType(row['entity_type']),  # String to Enum
            entity_id=row['entity_id'],
            url=row.get('url'),
            source_type=SourceType(row['source_type']) if row.get('source_type') else None,  # String to Enum
            excerpt=row.get('excerpt'),
            captured_at=_parse_datetime(row.get('captured_at')),
            content_hash=row.get('content_hash'),
            confidence=row.get('confidence'),
            created_by=row.get('created_by'),
            created_at=_parse_datetime(row.get('created_at')),
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
