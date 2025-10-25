"""
SBOM Data Models

Pydantic models for Software Bill of Materials (SBOM) generation.

Layer: Database Models (Domain Models)
Purpose: Type-safe, validated domain models for SBOM/license detection
Architecture: Three-layer (Models → Adapters → Methods)

Models:
    - LicenseInfo: License information for a package
    - SBOMComponent: Single component in SBOM
    - SBOM: Complete Software Bill of Materials

Version: 1.0.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from ..enums.detection import LicenseType


class LicenseInfo(BaseModel):
    """
    License information for a package.

    Attributes:
        package_name: Package identifier
        version: Package version
        license_type: Detected license type
        license_text: Full license text (optional, can be large)
        source: Where license was detected ('metadata', 'file', 'spdx', 'pypi', 'npm')
        confidence: Detection confidence (0.0-1.0)

    Example:
        >>> license_info = LicenseInfo(
        ...     package_name="requests",
        ...     version="2.31.0",
        ...     license_type=LicenseType.APACHE_2_0,
        ...     source="pypi",
        ...     confidence=1.0
        ... )
        >>> print(f"{license_info.package_name}: {license_info.license_type.value}")
        requests: Apache-2.0
    """
    model_config = ConfigDict(validate_assignment=True)

    package_name: str = Field(..., min_length=1, description="Package name")
    version: str = Field(..., min_length=1, description="Package version")
    license_type: LicenseType = Field(..., description="Detected license type")
    license_text: Optional[str] = Field(None, description="Full license text")
    source: str = Field(..., min_length=1, description="Detection source")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")


class SBOMComponent(BaseModel):
    """
    Single component in Software Bill of Materials.

    Attributes:
        name: Component name
        version: Component version
        type: Component type (library, framework, application, etc.)
        license: License information (if detected)
        dependencies: List of direct dependency names
        purl: Package URL (https://github.com/package-url/purl-spec)
        description: Component description (optional)
        metadata: Additional metadata (runtime verification, etc.)

    Example:
        >>> component = SBOMComponent(
        ...     name="click",
        ...     version="8.1.7",
        ...     type="library",
        ...     purl="pkg:pypi/click@8.1.7",
        ...     description="Composable command line interface toolkit",
        ...     metadata={"runtime_verified": True}
        ... )
    """
    model_config = ConfigDict(validate_assignment=True)

    name: str = Field(..., min_length=1, description="Component name")
    version: str = Field(..., min_length=1, description="Component version")
    type: str = Field(default="library", description="Component type")
    license: Optional[LicenseInfo] = Field(None, description="License information")
    dependencies: List[str] = Field(default_factory=list, description="Direct dependencies")
    purl: Optional[str] = Field(None, description="Package URL")
    description: Optional[str] = Field(None, description="Component description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SBOM(BaseModel):
    """
    Complete Software Bill of Materials for a project.

    Provides comprehensive dependency inventory including licenses,
    versions, and dependency relationships.

    Attributes:
        project_name: Project identifier
        project_version: Project version
        components: List of all dependency components
        total_components: Total number of components (computed)
        license_summary: Count of components per license type
        generated_at: Timestamp when SBOM was generated
        format_version: SBOM format version
        runtime_metadata: Optional runtime environment metadata

    Example:
        >>> sbom = SBOM(
        ...     project_name="aipm-v2",
        ...     project_version="2.0.0",
        ...     components=[component1, component2],
        ...     license_summary={"MIT": 15, "Apache-2.0": 8}
        ... )
        >>> print(f"Total components: {sbom.total_components}")
        Total components: 2
    """
    model_config = ConfigDict(validate_assignment=True)

    project_name: str = Field(..., min_length=1, description="Project name")
    project_version: str = Field(default="0.1.0", description="Project version")
    components: List[SBOMComponent] = Field(
        default_factory=list,
        description="All dependency components"
    )
    total_components: int = Field(default=0, ge=0, description="Total component count")
    license_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="License distribution"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Generation timestamp"
    )
    format_version: str = Field(default="1.0", description="SBOM format version")
    runtime_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Runtime environment metadata (Python version, venv, etc.)"
    )

    def model_post_init(self, __context) -> None:
        """Update computed fields after initialization."""
        self.total_components = len(self.components)

        # Update license summary
        self.license_summary = {}
        for component in self.components:
            if component.license:
                license_key = component.license.license_type.value
                self.license_summary[license_key] = self.license_summary.get(license_key, 0) + 1
