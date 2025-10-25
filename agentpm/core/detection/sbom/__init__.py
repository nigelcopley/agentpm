"""
SBOM (Software Bill of Materials) Package

Layer 3 (Detection Services) - SBOM generation and license detection.

Exports:
    - SBOMService: Main SBOM generation service
    - LicenseInfo: License information model (from database layer)
    - SBOMComponent: Individual component model (from database layer)
    - SBOM: Complete SBOM model (from database layer)
    - LicenseType: License type enumeration (from database layer)

Note: Models now imported from database layer following database-first architecture.
"""

# Import from database layer (database-first architecture)
from agentpm.core.database.models.detection_sbom import (
    LicenseInfo,
    SBOMComponent,
    SBOM
)
from agentpm.core.database.enums.detection import LicenseType

# Import service from this package
from .service import SBOMService

__all__ = [
    'LicenseType',
    'LicenseInfo',
    'SBOMComponent',
    'SBOM',
    'SBOMService',
]
