"""
SBOM Service - Software Bill of Materials Generation

Layer 3 (Detection Services) - Uses Layer 1 file_parsers utilities.

Responsibilities:
- Extract dependencies from package manifests (requirements.txt, package.json, pyproject.toml)
- Detect licenses from package metadata and files
- Generate SBOM in multiple formats (CycloneDX, SPDX, JSON)
- Provide license compliance reporting

Example:
    >>> from pathlib import Path
    >>> service = SBOMService(Path("."))
    >>> sbom = service.generate_sbom(include_licenses=True)
    >>> print(f"Found {sbom.total_components} components")
    >>> print(f"Licenses: {sbom.license_summary}")

Performance Targets:
- SBOM generation: <1s for typical projects
- Cached: <100ms
- License detection: <100ms per package (with caching)

Version: 1.0.0
"""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Database layer imports (database-first architecture)
from agentpm.core.database.models.detection_sbom import LicenseInfo, SBOMComponent, SBOM
from agentpm.core.database.enums.detection import LicenseType
from agentpm.core.database.models.detection_runtime import RuntimeOverlay

# Layer 1 imports - Shared utilities (NO circular dependencies)
from agentpm.utils.file_parsers import (
    parse_python_dependencies,
    parse_javascript_dependencies,
    parse_toml,
    parse_json
)

# Optional CycloneDX support
try:
    from cyclonedx.model import bom as cyclonedx_bom
    from cyclonedx.model import component as cyclonedx_component
    from cyclonedx.output import make_outputter
    from cyclonedx.output.json import JsonV1Dot5
    CYCLONEDX_AVAILABLE = True
except ImportError:
    CYCLONEDX_AVAILABLE = False


class SBOMService:
    """
    Service for SBOM generation and license detection.

    This service follows the three-layer architecture:
    - Layer 3 (Detection Service): This class
    - Layer 1 (Utilities): file_parsers for dependency extraction
    - Layer 2 (Plugins): Not used (plugins use Layer 1 utilities directly)

    Attributes:
        project_path: Root directory of the project
        _license_cache: In-memory cache for license lookups

    Example:
        >>> service = SBOMService(Path("/path/to/project"))
        >>> sbom = service.generate_sbom()
        >>> print(f"Project: {sbom.project_name}")
        >>> print(f"Components: {sbom.total_components}")
        >>>
        >>> # Export to CycloneDX format
        >>> cyclonedx_json = service.export_cyclonedx(sbom, Path("sbom.json"))
    """

    # Common license keywords for detection from package metadata
    LICENSE_PATTERNS = {
        LicenseType.MIT: [r'\bMIT\b', r'MIT License'],
        LicenseType.APACHE_2_0: [r'Apache-2\.0', r'Apache License 2\.0', r'ASL 2'],
        LicenseType.GPL_3_0: [r'GPL-?3\.0', r'GNU General Public License v3'],
        LicenseType.GPL_2_0: [r'GPL-?2\.0', r'GNU General Public License v2'],
        LicenseType.BSD_3_CLAUSE: [r'BSD-3-Clause', r'3-Clause BSD'],
        LicenseType.BSD_2_CLAUSE: [r'BSD-2-Clause', r'2-Clause BSD'],
        LicenseType.ISC: [r'\bISC\b', r'ISC License'],
        LicenseType.LGPL_3_0: [r'LGPL-?3\.0', r'Lesser GPL v3'],
        LicenseType.MPL_2_0: [r'MPL-?2\.0', r'Mozilla Public License 2\.0'],
    }

    def __init__(self, project_path: Path):
        """
        Initialize SBOM service.

        Args:
            project_path: Root directory of the project to analyze
        """
        self.project_path = project_path
        self._license_cache: Dict[str, LicenseInfo] = {}

    def generate_sbom(
        self,
        include_licenses: bool = True,
        include_dev_deps: bool = False,
        include_runtime: bool = True
    ) -> SBOM:
        """
        Generate complete SBOM for project.

        Steps:
        1. Detect project type (Python/JavaScript/both)
        2. Extract dependencies using file_parsers utilities
        3. Detect licenses for each dependency (if requested)
        4. Capture runtime overlay (if requested)
        5. Enrich components with runtime metadata
        6. Build SBOM model with all components

        Args:
            include_licenses: Whether to detect and include license information
            include_dev_deps: Include development dependencies
            include_runtime: Include runtime environment overlay

        Returns:
            Complete SBOM with all components and license information

        Example:
            >>> service = SBOMService(Path("."))
            >>> sbom = service.generate_sbom(include_licenses=True, include_runtime=True)
            >>> print(f"Runtime deps: {len([c for c in sbom.components if c.type == 'library'])}")
        """
        components: List[SBOMComponent] = []

        # Extract Python components
        python_components = self.extract_python_components(include_dev_deps)
        components.extend(python_components)

        # Extract JavaScript components
        js_components = self.extract_javascript_components(include_dev_deps)
        components.extend(js_components)

        # Capture runtime overlay if requested
        runtime_overlay: Optional[RuntimeOverlay] = None
        if include_runtime:
            from agentpm.core.detection.runtime import RuntimeDetectorService
            runtime_service = RuntimeDetectorService(self.project_path)
            runtime_overlay = runtime_service.capture_runtime_overlay()

            # Enrich components with runtime metadata
            for component in components:
                if runtime_overlay.has_package(component.name):
                    runtime_version = runtime_overlay.get_package_version(component.name)
                    component.metadata['runtime_verified'] = True
                    component.metadata['runtime_version'] = runtime_version

                    # Update version to actual installed version
                    if runtime_version:
                        component.version = runtime_version
                else:
                    component.metadata['runtime_verified'] = False

        # Detect licenses if requested
        if include_licenses:
            for component in components:
                license_info = self.detect_license(component.name, component.version)
                if license_info:
                    component.license = license_info

        # Determine project name and version
        project_name = self._get_project_name()
        project_version = self._get_project_version()

        # Build SBOM with optional runtime metadata
        sbom = SBOM(
            project_name=project_name,
            project_version=project_version,
            components=components,
            generated_at=datetime.now()
        )

        # Add runtime metadata to SBOM if captured
        if runtime_overlay:
            sbom.runtime_metadata = {
                "python_version": runtime_overlay.python_version,
                "venv_path": runtime_overlay.venv_path,
                "total_installed_packages": runtime_overlay.get_total_packages(),
                "build_tools": runtime_overlay.build_tools,
                "captured_at": runtime_overlay.captured_at.isoformat(),
            }

        return sbom

    def extract_python_components(
        self,
        include_dev: bool = False
    ) -> List[SBOMComponent]:
        """
        Extract Python dependencies as SBOM components.

        Uses file_parsers.parse_python_dependencies() utility (Layer 1).

        Args:
            include_dev: Whether to include development dependencies

        Returns:
            List of SBOM components for Python packages

        Example:
            >>> service = SBOMService(Path("."))
            >>> components = service.extract_python_components()
            >>> for comp in components:
            ...     print(f"{comp.name}@{comp.version}")
        """
        components: List[SBOMComponent] = []

        # Use Layer 1 utility to extract dependencies
        deps_data = parse_python_dependencies(self.project_path)

        if deps_data['source'] == 'none':
            return components

        # Extract version information from pyproject.toml or requirements.txt
        version_map = self._extract_python_versions()

        # Process runtime dependencies
        for dep_name in deps_data['runtime']:
            version = version_map.get(dep_name, 'latest')
            component = SBOMComponent(
                name=dep_name,
                version=version,
                type="library",
                purl=f"pkg:pypi/{dep_name}@{version}" if version != 'latest' else f"pkg:pypi/{dep_name}"
            )
            components.append(component)

        # Process dev dependencies if requested
        if include_dev:
            for dep_name in deps_data['dev']:
                version = version_map.get(dep_name, 'latest')
                component = SBOMComponent(
                    name=dep_name,
                    version=version,
                    type="development",
                    purl=f"pkg:pypi/{dep_name}@{version}" if version != 'latest' else f"pkg:pypi/{dep_name}"
                )
                components.append(component)

        return components

    def extract_javascript_components(
        self,
        include_dev: bool = False
    ) -> List[SBOMComponent]:
        """
        Extract JavaScript/Node dependencies as SBOM components.

        Uses file_parsers.parse_javascript_dependencies() utility (Layer 1).

        Args:
            include_dev: Whether to include development dependencies

        Returns:
            List of SBOM components for JavaScript packages

        Example:
            >>> service = SBOMService(Path("."))
            >>> components = service.extract_javascript_components()
            >>> npm_packages = [c for c in components if 'npm' in c.purl]
        """
        components: List[SBOMComponent] = []

        # Use Layer 1 utility to extract dependencies
        deps_data = parse_javascript_dependencies(self.project_path)

        if deps_data['source'] == 'none':
            return components

        # Extract version information from package.json
        package_json_path = self.project_path / 'package.json'
        package_data = parse_json(package_json_path)

        if not package_data:
            return components

        # Process runtime dependencies
        runtime_deps = package_data.get('dependencies', {})
        for dep_name in deps_data['runtime']:
            version = runtime_deps.get(dep_name, 'latest').lstrip('^~')
            component = SBOMComponent(
                name=dep_name,
                version=version,
                type="library",
                purl=f"pkg:npm/{dep_name}@{version}" if version != 'latest' else f"pkg:npm/{dep_name}"
            )
            components.append(component)

        # Process dev dependencies if requested
        if include_dev:
            dev_deps = package_data.get('devDependencies', {})
            for dep_name in deps_data['dev']:
                version = dev_deps.get(dep_name, 'latest').lstrip('^~')
                component = SBOMComponent(
                    name=dep_name,
                    version=version,
                    type="development",
                    purl=f"pkg:npm/{dep_name}@{version}" if version != 'latest' else f"pkg:npm/{dep_name}"
                )
                components.append(component)

        return components

    def detect_license(
        self,
        package_name: str,
        version: str
    ) -> Optional[LicenseInfo]:
        """
        Detect license for a package.

        Sources (in priority order):
        1. Cache (if previously detected)
        2. Package metadata from pyproject.toml or package.json
        3. LICENSE file detection (if package installed locally)
        4. Pattern matching in package metadata strings

        Note: PyPI/npm API integration is reserved for future enhancement.
        Current implementation uses local metadata only.

        Args:
            package_name: Package name to lookup
            version: Package version

        Returns:
            LicenseInfo if detected, None otherwise

        Example:
            >>> service = SBOMService(Path("."))
            >>> license_info = service.detect_license("requests", "2.31.0")
            >>> if license_info:
            ...     print(f"License: {license_info.license_type.value}")
        """
        cache_key = f"{package_name}@{version}"

        # Check cache first
        if cache_key in self._license_cache:
            return self._license_cache[cache_key]

        license_info = None

        # Try to detect from package metadata (pyproject.toml for Python)
        license_info = self._detect_license_from_metadata(package_name)

        # Try to detect from LICENSE file (if package installed)
        if not license_info:
            license_info = self._detect_license_from_file(package_name)

        # Cache result (even if None to avoid repeated lookups)
        if license_info:
            self._license_cache[cache_key] = license_info

        return license_info

    def export_cyclonedx(
        self,
        sbom: SBOM,
        output_path: Path,
        format: str = "json"
    ) -> str:
        """
        Export SBOM to CycloneDX format.

        Requires cyclonedx-python-lib package to be installed.
        Falls back to manual JSON generation if not available.

        Args:
            sbom: SBOM to export
            output_path: Path to write output file
            format: 'json' or 'xml' (json is better supported)

        Returns:
            Serialized CycloneDX string

        Example:
            >>> service = SBOMService(Path("."))
            >>> sbom = service.generate_sbom()
            >>> json_output = service.export_cyclonedx(sbom, Path("sbom.json"))
        """
        if CYCLONEDX_AVAILABLE and format == "json":
            # Use official CycloneDX library
            return self._export_cyclonedx_official(sbom, output_path)
        else:
            # Manual JSON generation (fallback)
            return self._export_cyclonedx_manual(sbom, output_path, format)

    def export_spdx(
        self,
        sbom: SBOM,
        output_path: Path
    ) -> str:
        """
        Export SBOM to SPDX format (JSON).

        Generates SPDX 2.3 compliant JSON output.

        Args:
            sbom: SBOM to export
            output_path: Path to write output file

        Returns:
            Serialized SPDX JSON string

        Example:
            >>> service = SBOMService(Path("."))
            >>> sbom = service.generate_sbom()
            >>> spdx_output = service.export_spdx(sbom, Path("sbom.spdx.json"))
        """
        spdx_doc = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{sbom.project_name} SBOM",
            "documentNamespace": f"https://sbom.{sbom.project_name}/{sbom.project_version}",
            "creationInfo": {
                "created": sbom.generated_at.isoformat(),
                "creators": ["Tool: AIPM-v2-SBOM-Service"],
                "licenseListVersion": "3.21"
            },
            "packages": []
        }

        # Add components as SPDX packages
        for idx, component in enumerate(sbom.components):
            package = {
                "SPDXID": f"SPDXRef-Package-{idx}",
                "name": component.name,
                "versionInfo": component.version,
                "downloadLocation": component.purl or "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": component.license.license_type.value if component.license else "NOASSERTION",
                "licenseDeclared": component.license.license_type.value if component.license else "NOASSERTION",
                "copyrightText": "NOASSERTION"
            }
            spdx_doc["packages"].append(package)

        # Write to file
        spdx_json = json.dumps(spdx_doc, indent=2)
        output_path.write_text(spdx_json)

        return spdx_json

    def get_license_summary(self, sbom: SBOM) -> Dict[str, int]:
        """
        Get license distribution summary.

        Args:
            sbom: SBOM to analyze

        Returns:
            Dict mapping license_type -> count

        Example:
            >>> service = SBOMService(Path("."))
            >>> sbom = service.generate_sbom(include_licenses=True)
            >>> summary = service.get_license_summary(sbom)
            >>> print(f"MIT licenses: {summary.get('MIT', 0)}")
        """
        return sbom.license_summary

    # ========== Private Helper Methods ==========

    def _extract_python_versions(self) -> Dict[str, str]:
        """
        Extract version information for Python packages.

        Returns:
            Dict mapping package_name -> version
        """
        version_map: Dict[str, str] = {}

        # Try pyproject.toml first
        pyproject_path = self.project_path / 'pyproject.toml'
        if pyproject_path.exists():
            pyproject_data = parse_toml(pyproject_path)
            if pyproject_data:
                # Poetry format
                poetry_deps = pyproject_data.get('tool', {}).get('poetry', {}).get('dependencies', {})
                for name, version_spec in poetry_deps.items():
                    if isinstance(version_spec, str):
                        version_map[name] = self._normalize_version(version_spec)
                    elif isinstance(version_spec, dict) and 'version' in version_spec:
                        version_map[name] = self._normalize_version(version_spec['version'])

                # PEP 621 format
                project_deps = pyproject_data.get('project', {}).get('dependencies', [])
                for dep_spec in project_deps:
                    # Parse "package>=1.0.0" format
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*([><=!]+)\s*(.+)$', dep_spec)
                    if match:
                        name, op, version = match.groups()
                        version_map[name] = self._normalize_version(version)

        return version_map

    def _normalize_version(self, version_spec: str) -> str:
        """
        Normalize version specifier to concrete version.

        Args:
            version_spec: Version specifier (e.g., "^1.0.0", ">=2.0.0")

        Returns:
            Normalized version string
        """
        # Remove operators
        version = re.sub(r'^[~^><=!]+\s*', '', version_spec)
        # Remove comma-separated constraints (take first)
        version = version.split(',')[0].strip()
        return version if version else 'latest'

    def _get_project_name(self) -> str:
        """
        Determine project name from configuration files.

        Priority:
        1. pyproject.toml [tool.poetry.name] or [project.name]
        2. package.json name
        3. Directory name

        Returns:
            Project name
        """
        # Try pyproject.toml
        pyproject_path = self.project_path / 'pyproject.toml'
        if pyproject_path.exists():
            pyproject_data = parse_toml(pyproject_path)
            if pyproject_data:
                # Poetry format
                name = pyproject_data.get('tool', {}).get('poetry', {}).get('name')
                if name:
                    return name
                # PEP 621 format
                name = pyproject_data.get('project', {}).get('name')
                if name:
                    return name

        # Try package.json
        package_json_path = self.project_path / 'package.json'
        if package_json_path.exists():
            package_data = parse_json(package_json_path)
            if package_data:
                name = package_data.get('name')
                if name:
                    return name

        # Fallback to directory name
        return self.project_path.name

    def _get_project_version(self) -> str:
        """
        Determine project version from configuration files.

        Priority:
        1. pyproject.toml [tool.poetry.version] or [project.version]
        2. package.json version
        3. Default "0.1.0"

        Returns:
            Project version
        """
        # Try pyproject.toml
        pyproject_path = self.project_path / 'pyproject.toml'
        if pyproject_path.exists():
            pyproject_data = parse_toml(pyproject_path)
            if pyproject_data:
                # Poetry format
                version = pyproject_data.get('tool', {}).get('poetry', {}).get('version')
                if version:
                    return version
                # PEP 621 format
                version = pyproject_data.get('project', {}).get('version')
                if version:
                    return version

        # Try package.json
        package_json_path = self.project_path / 'package.json'
        if package_json_path.exists():
            package_data = parse_json(package_json_path)
            if package_data:
                version = package_data.get('version')
                if version:
                    return version

        return "0.1.0"

    def _detect_license_from_metadata(self, package_name: str) -> Optional[LicenseInfo]:
        """
        Detect license from package metadata.

        Tries multiple sources:
        1. importlib.metadata (installed Python packages)
        2. package.json (JavaScript packages in node_modules)
        3. Falls back to Unknown

        Args:
            package_name: Package to lookup

        Returns:
            LicenseInfo if detected, None otherwise
        """
        # Try Python package metadata first
        try:
            import importlib.metadata
            metadata = importlib.metadata.metadata(package_name)
            license_str = metadata.get('License', '').strip()

            # If no License field, try License-Expression (PEP 639)
            if not license_str or license_str.upper() == 'UNKNOWN':
                license_str = metadata.get('License-Expression', '').strip()

            # If still no license, try to extract from classifiers
            if not license_str or license_str.upper() == 'UNKNOWN':
                classifiers = metadata.get_all('Classifier', [])
                for classifier in classifiers:
                    if 'License ::' in classifier:
                        # Extract license from classifier like "License :: OSI Approved :: MIT License"
                        license_str = classifier.split('::')[-1].strip()
                        break

            if license_str and license_str.upper() != 'UNKNOWN':
                license_type = self._parse_license_string(license_str)
                version = metadata.get('Version', 'unknown')

                return LicenseInfo(
                    package_name=package_name,
                    version=version,
                    license_type=license_type,
                    license_text=license_str if len(license_str) < 200 else None,
                    source="importlib.metadata",
                    confidence=0.9 if license_type != LicenseType.UNKNOWN else 0.2
                )
        except Exception:
            # Package not installed or metadata unavailable
            pass

        # Try JavaScript package.json
        js_license = self._detect_js_license_from_package_json(package_name)
        if js_license:
            return js_license

        # No license found
        return None

    def _detect_js_license_from_package_json(self, package_name: str) -> Optional[LicenseInfo]:
        """
        Detect license from package.json in node_modules.

        Args:
            package_name: JavaScript package name (e.g., 'alpinejs', '@playwright/mcp')

        Returns:
            LicenseInfo if detected, None otherwise
        """
        # Handle scoped packages (@org/package)
        node_modules = self.project_path / "node_modules" / package_name
        package_json_path = node_modules / "package.json"

        if not package_json_path.exists():
            return None

        try:
            package_data = parse_json(package_json_path)
            if not package_data:
                return None

            license_str = package_data.get('license', '').strip()
            version = package_data.get('version', 'unknown')

            if license_str and license_str.upper() != 'UNKNOWN':
                license_type = self._parse_license_string(license_str)

                return LicenseInfo(
                    package_name=package_name,
                    version=version,
                    license_type=license_type,
                    license_text=license_str if len(license_str) < 200 else None,
                    source="package.json",
                    confidence=0.9 if license_type != LicenseType.UNKNOWN else 0.2
                )
        except Exception:
            pass

        return None

    def _parse_license_string(self, license_str: str) -> LicenseType:
        """
        Parse license string to LicenseType enum.

        Handles common variations and aliases.

        Args:
            license_str: License string from package metadata

        Returns:
            Parsed LicenseType or UNKNOWN if not recognized
        """
        if not license_str or license_str.upper() == 'UNKNOWN':
            return LicenseType.UNKNOWN

        license_upper = license_str.upper().strip()

        # MIT variations
        if 'MIT' in license_upper:
            return LicenseType.MIT

        # Apache variations
        if 'APACHE' in license_upper or 'APACHE-2' in license_upper:
            return LicenseType.APACHE_2_0

        # BSD variations - check specific clause counts first (most specific to least specific)
        if '0BSD' in license_upper or 'BSD-0' in license_upper or '0-CLAUSE BSD' in license_upper:
            return LicenseType.BSD_0
        if 'BSD-3' in license_upper or '3-CLAUSE BSD' in license_upper or 'BSD 3-CLAUSE' in license_upper:
            return LicenseType.BSD_3_CLAUSE
        if 'BSD-2' in license_upper or '2-CLAUSE BSD' in license_upper or 'BSD 2-CLAUSE' in license_upper:
            return LicenseType.BSD_2_CLAUSE
        if 'BSD' in license_upper and 'SIMPLIFIED' in license_upper:
            return LicenseType.BSD_2_CLAUSE
        # Generic BSD License without clause specification - default to BSD-3-Clause
        if 'BSD LICENSE' in license_upper or license_upper == 'BSD':
            return LicenseType.BSD_3_CLAUSE

        # GPL variations
        if 'GPL-3' in license_upper or 'GPLV3' in license_upper:
            return LicenseType.GPL_3_0
        if 'LGPL-3' in license_upper:
            return LicenseType.LGPL_3_0

        # ISC
        if 'ISC' in license_upper:
            return LicenseType.ISC

        # Mozilla
        if 'MPL' in license_upper or 'MOZILLA' in license_upper:
            return LicenseType.MPL_2_0

        # Other standard licenses
        if 'UNLICENSE' in license_upper:
            return LicenseType.UNLICENSE
        if 'CC0' in license_upper:
            return LicenseType.CC0_1_0
        if 'PROPRIETARY' in license_upper or 'PRIVATE' in license_upper:
            return LicenseType.PROPRIETARY

        return LicenseType.UNKNOWN

    def _detect_license_from_file(self, package_name: str) -> Optional[LicenseInfo]:
        """
        Detect license from LICENSE file.

        Looks for LICENSE file in common locations and uses pattern matching.

        Args:
            package_name: Package to lookup

        Returns:
            LicenseInfo if detected, None otherwise
        """
        # Check for LICENSE file in project root (main project license)
        license_files = [
            'LICENSE',
            'LICENSE.txt',
            'LICENSE.md',
            'COPYING',
            'COPYING.txt'
        ]

        for license_file in license_files:
            license_path = self.project_path / license_file
            if license_path.exists():
                try:
                    license_text = license_path.read_text()
                    license_type = self._match_license_pattern(license_text)

                    if license_type:
                        return LicenseInfo(
                            package_name=package_name,
                            version="unknown",
                            license_type=license_type,
                            license_text=license_text[:1000],  # First 1000 chars
                            source="file",
                            confidence=0.8
                        )
                except Exception:
                    continue

        return None

    def _match_license_pattern(self, license_text: str) -> Optional[LicenseType]:
        """
        Match license text against known license patterns.

        Args:
            license_text: Text content of license file

        Returns:
            Detected LicenseType or None
        """
        for license_type, patterns in self.LICENSE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, license_text, re.IGNORECASE):
                    return license_type

        return LicenseType.UNKNOWN

    def _export_cyclonedx_official(self, sbom: SBOM, output_path: Path) -> str:
        """Use official CycloneDX library for export."""
        # This would use the cyclonedx-python-lib
        # Implementation left for when library is available
        return self._export_cyclonedx_manual(sbom, output_path, "json")

    def _export_cyclonedx_manual(
        self,
        sbom: SBOM,
        output_path: Path,
        format: str
    ) -> str:
        """
        Manual CycloneDX JSON generation (fallback).

        Generates CycloneDX 1.5 compliant JSON.
        """
        cyclonedx_doc = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{self._generate_uuid()}",
            "version": 1,
            "metadata": {
                "timestamp": sbom.generated_at.isoformat(),
                "tools": [
                    {
                        "vendor": "AIPM",
                        "name": "AIPM-v2-SBOM-Service",
                        "version": "1.0.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": sbom.project_name,
                    "version": sbom.project_version
                }
            },
            "components": []
        }

        # Add components
        for component in sbom.components:
            cdx_component = {
                "type": component.type,
                "name": component.name,
                "version": component.version,
                "purl": component.purl or ""
            }

            if component.license:
                cdx_component["licenses"] = [
                    {
                        "license": {
                            "id": component.license.license_type.value
                        }
                    }
                ]

            cyclonedx_doc["components"].append(cdx_component)

        # Write to file
        cdx_json = json.dumps(cyclonedx_doc, indent=2)
        output_path.write_text(cdx_json)

        return cdx_json

    def _generate_uuid(self) -> str:
        """Generate a UUID for the SBOM."""
        # Simple UUID generation based on timestamp and project
        import uuid
        return str(uuid.uuid4())
