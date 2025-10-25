"""
Migration Pydantic Models

Domain models for migration metadata with validation.
"""

from datetime import datetime
from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field


class Migration(BaseModel):
    """
    Migration metadata model.

    Represents a database migration with version tracking and application state.
    """

    version: str = Field(..., min_length=4, max_length=4, pattern=r'^\d{4}$')
    description: str = Field(..., min_length=1, max_length=200)
    applied_at: Optional[datetime] = None
    rollback_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None
    applied_by: Optional[str] = None

    class Config:
        validate_assignment = True
        str_strip_whitespace = True


class MigrationFile(BaseModel):
    """
    Migration file metadata.

    Represents a discovered migration file with path and execution state.
    """

    version: str = Field(..., min_length=4, max_length=4, pattern=r'^\d{4}$')
    description: str = Field(..., min_length=1, max_length=200)
    file_path: Path
    applied: bool = False
    applied_at: Optional[str] = None
    rollback_at: Optional[str] = None

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True  # Allow Path
