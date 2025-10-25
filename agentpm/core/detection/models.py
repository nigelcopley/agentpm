"""
Detection Models - Pydantic Domain Models

Type-safe detection models with validation.

These models replace the dataclasses from V1 with professional Pydantic models
following the same pattern as database models.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class EvidenceType(str, Enum):
    """Type of detection evidence"""
    EXTENSION = "extension"
    CONFIG_FILE = "config_file"
    DIRECTORY = "directory"
    IMPORT_STATEMENT = "import_statement"
    DEPENDENCY = "dependency"


class TechnologyMatch(BaseModel):
    """
    Represents a detected technology with confidence and evidence.

    Pydantic model for validation and type safety.

    Attributes:
        technology: Technology name (e.g., 'python', 'django')
        confidence: Confidence score (0.0-1.0)
        evidence: List of evidence items (file paths, config files, etc.)
        evidence_types: Types of evidence found
        detected_at: When detection occurred
    """
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False
    )

    technology: str = Field(..., min_length=1, max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    evidence_types: List[EvidenceType] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.now)

    def add_evidence(self, evidence: str, evidence_type: EvidenceType) -> None:
        """Add evidence with type checking"""
        self.evidence.append(evidence)
        self.evidence_types.append(evidence_type)


class DetectionResult(BaseModel):
    """
    Complete detection results for a project.

    Type-safe collection of all detected technologies.

    Attributes:
        matches: Dictionary of technology -> TechnologyMatch
        scan_time_ms: Time taken for detection (milliseconds)
        project_path: Path to scanned project
        scanned_at: When scan occurred
    """
    model_config = ConfigDict(validate_assignment=True)

    matches: Dict[str, TechnologyMatch] = Field(default_factory=dict)
    scan_time_ms: float = Field(..., ge=0.0)
    project_path: str = Field(..., min_length=1)
    scanned_at: datetime = Field(default_factory=datetime.now)

    def get_primary_language(self) -> Optional[str]:
        """
        Get highest confidence language.

        Returns:
            Primary language name or None if no languages detected
        """
        languages = {k: v for k, v in self.matches.items()
                    if k in ['python', 'javascript', 'typescript', 'go', 'rust', 'java', 'ruby', 'php']}
        if not languages:
            return None
        return max(languages.items(), key=lambda x: x[1].confidence)[0]

    def get_detected_technologies(self, min_confidence: float = 0.5) -> List[str]:
        """
        Get all technologies above confidence threshold.

        Args:
            min_confidence: Minimum confidence score (default 0.5)

        Returns:
            List of technology names
        """
        return [tech for tech, match in self.matches.items()
                if match.confidence >= min_confidence]

    def has_technology(self, technology: str, min_confidence: float = 0.5) -> bool:
        """
        Check if specific technology is detected.

        Args:
            technology: Technology name to check
            min_confidence: Minimum confidence threshold

        Returns:
            True if technology detected above threshold
        """
        match = self.matches.get(technology)
        return match is not None and match.confidence >= min_confidence