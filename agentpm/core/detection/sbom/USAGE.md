# SBOM Service Usage Guide

## Overview

The SBOM (Software Bill of Materials) Service generates comprehensive dependency inventories for projects, including license detection and multiple export formats.

**Layer**: Layer 3 (Detection Services)
**Dependencies**: Layer 1 utilities (`file_parsers`)
**Version**: 1.0.0

---

## Quick Start

```python
from pathlib import Path
from agentpm.core.detection.sbom import SBOMService

# Initialize service
service = SBOMService(Path("."))

# Generate SBOM
sbom = service.generate_sbom(include_licenses=True)

# View results
print(f"Project: {sbom.project_name}")
print(f"Total components: {sbom.total_components}")
print(f"License distribution: {sbom.license_summary}")
```

---

## Core Functionality

### 1. Generate SBOM

```python
# Full SBOM with licenses
sbom = service.generate_sbom(
    include_licenses=True,      # Detect licenses
    include_dev_deps=False      # Exclude dev dependencies
)

# Quick SBOM (no licenses)
sbom = service.generate_sbom(include_licenses=False)

# Include dev dependencies
sbom = service.generate_sbom(include_dev_deps=True)
```

### 2. Extract Components by Type

#### Python Components

```python
# Extract Python dependencies
python_components = service.extract_python_components(include_dev=False)

for component in python_components:
    print(f"{component.name}@{component.version}")
    if component.license:
        print(f"  License: {component.license.license_type.value}")
    print(f"  PURL: {component.purl}")
```

#### JavaScript Components

```python
# Extract JavaScript/Node dependencies
js_components = service.extract_javascript_components(include_dev=False)

for component in js_components:
    print(f"{component.name}@{component.version}")
    print(f"  Type: {component.type}")
```

### 3. License Detection

```python
# Detect license for specific package
license_info = service.detect_license("requests", "2.31.0")

if license_info:
    print(f"Package: {license_info.package_name}")
    print(f"License: {license_info.license_type.value}")
    print(f"Source: {license_info.source}")
    print(f"Confidence: {license_info.confidence:.0%}")
```

### 4. Export Formats

#### CycloneDX (JSON)

```python
# Export to CycloneDX format
cyclonedx_json = service.export_cyclonedx(
    sbom,
    output_path=Path("sbom.json"),
    format="json"
)

print(f"Exported to sbom.json")
```

#### SPDX (JSON)

```python
# Export to SPDX format
spdx_json = service.export_spdx(
    sbom,
    output_path=Path("sbom.spdx.json")
)

print(f"Exported to sbom.spdx.json")
```

### 5. License Summary

```python
# Get license distribution
summary = service.get_license_summary(sbom)

for license_type, count in summary.items():
    print(f"{license_type}: {count} components")
```

---

## Data Models

### SBOM

Complete Software Bill of Materials.

```python
sbom = SBOM(
    project_name="my-project",
    project_version="1.0.0",
    components=[...],
    license_summary={"MIT": 10, "Apache-2.0": 5},
    generated_at=datetime.now()
)

# Access properties
print(sbom.total_components)      # Computed automatically
print(sbom.license_summary)       # License distribution
```

### SBOMComponent

Individual dependency component.

```python
component = SBOMComponent(
    name="click",
    version="8.1.7",
    type="library",
    purl="pkg:pypi/click@8.1.7",
    description="CLI toolkit"
)

# With license
component.license = LicenseInfo(
    package_name="click",
    version="8.1.7",
    license_type=LicenseType.BSD_3_CLAUSE,
    source="pypi",
    confidence=1.0
)
```

### LicenseInfo

License information for a component.

```python
license_info = LicenseInfo(
    package_name="requests",
    version="2.31.0",
    license_type=LicenseType.APACHE_2_0,
    license_text="Apache License 2.0...",
    source="file",           # 'metadata', 'file', 'spdx', 'pypi'
    confidence=0.95
)
```

---

## Supported License Types

```python
from agentpm.core.detection.sbom import LicenseType

# Permissive licenses
LicenseType.MIT
LicenseType.APACHE_2_0
LicenseType.BSD_3_CLAUSE
LicenseType.BSD_2_CLAUSE
LicenseType.ISC

# Copyleft licenses
LicenseType.GPL_2_0
LicenseType.GPL_3_0
LicenseType.LGPL_2_1
LicenseType.LGPL_3_0
LicenseType.AGPL_3_0

# Other
LicenseType.MPL_2_0
LicenseType.UNLICENSE
LicenseType.PROPRIETARY
LicenseType.UNKNOWN
```

---

## Advanced Usage

### Filter Components by License

```python
sbom = service.generate_sbom(include_licenses=True)

# Find all GPL-licensed components
gpl_components = [
    c for c in sbom.components
    if c.license and c.license.license_type == LicenseType.GPL_3_0
]

print(f"GPL-3.0 components: {len(gpl_components)}")
for component in gpl_components:
    print(f"  - {component.name}@{component.version}")
```

### Custom License Detection

```python
class CustomSBOMService(SBOMService):
    def detect_license(self, package_name: str, version: str):
        # Check custom license database first
        custom_license = self._check_custom_db(package_name)
        if custom_license:
            return custom_license

        # Fall back to default detection
        return super().detect_license(package_name, version)
```

### Integrate with CI/CD

```python
from pathlib import Path

def validate_licenses(project_path: Path, allowed_licenses: list):
    """Validate that all dependencies use allowed licenses."""
    service = SBOMService(project_path)
    sbom = service.generate_sbom(include_licenses=True)

    violations = []
    for component in sbom.components:
        if component.license:
            if component.license.license_type not in allowed_licenses:
                violations.append(component)

    if violations:
        print(f"License violations found: {len(violations)}")
        for component in violations:
            print(f"  - {component.name}: {component.license.license_type.value}")
        return False

    return True

# Usage in CI
allowed = [LicenseType.MIT, LicenseType.APACHE_2_0, LicenseType.BSD_3_CLAUSE]
if not validate_licenses(Path("."), allowed):
    exit(1)
```

---

## Performance Considerations

### Caching

License detection results are cached in-memory:

```python
service = SBOMService(Path("."))

# First call: detects license
license1 = service.detect_license("requests", "2.31.0")

# Second call: uses cache (instant)
license2 = service.detect_license("requests", "2.31.0")
```

### Large Projects

For projects with many dependencies:

```python
# Skip license detection for speed
sbom = service.generate_sbom(include_licenses=False)  # <100ms

# Add licenses later only for specific components
for component in sbom.components[:10]:  # Top 10 only
    component.license = service.detect_license(component.name, component.version)
```

---

## Integration with Detection Pack

### CLI Integration

```bash
# Generate SBOM via CLI
apm detect sbom --format json --output sbom.json --include-licenses

# Export to different formats
apm detect sbom --format cyclonedx --output sbom.cdx.json
apm detect sbom --format spdx --output sbom.spdx.json
```

### Service Integration

```python
from agentpm.core.detection.analysis import StaticAnalysisService
from agentpm.core.detection.sbom import SBOMService

# Combine with static analysis
analysis_service = StaticAnalysisService(db, project_path)
sbom_service = SBOMService(project_path)

# Generate both
ast_graph = analysis_service.parse_project()
sbom = sbom_service.generate_sbom(include_licenses=True)

# Comprehensive report
print(f"Code metrics: {ast_graph.nodes}")
print(f"Dependencies: {sbom.total_components}")
print(f"Licenses: {sbom.license_summary}")
```

---

## Troubleshooting

### No Dependencies Found

```python
sbom = service.generate_sbom()

if sbom.total_components == 0:
    # Check if dependency files exist
    print("Looking for:")
    print("  - pyproject.toml")
    print("  - requirements.txt")
    print("  - package.json")
```

### License Detection Failed

```python
license_info = service.detect_license("my-package", "1.0.0")

if not license_info:
    # License detection failed
    # Reasons:
    # 1. No LICENSE file in project root
    # 2. No metadata in pyproject.toml/package.json
    # 3. Package not installed locally
    # 4. License format not recognized

    # Manual override
    license_info = LicenseInfo(
        package_name="my-package",
        version="1.0.0",
        license_type=LicenseType.MIT,
        source="manual",
        confidence=1.0
    )
```

---

## Future Enhancements

### Planned Features

1. **PyPI/npm API Integration**: Query package registries for license information
2. **Transitive Dependencies**: Include indirect dependencies
3. **Vulnerability Scanning**: Integrate with security databases
4. **License Compatibility**: Check for license conflicts
5. **Historical Tracking**: Track dependency changes over time

### API Enhancement

```python
# Future API (not yet implemented)
sbom = service.generate_sbom(
    include_transitive=True,        # Include indirect deps
    scan_vulnerabilities=True,      # Check CVE databases
    validate_compatibility=True     # Check license conflicts
)
```

---

## References

- [CycloneDX Specification](https://cyclonedx.org/)
- [SPDX Specification](https://spdx.dev/)
- [Package URL (PURL)](https://github.com/package-url/purl-spec)
- AIPM Architecture: `docs/architecture/architecture/detection-pack-architecture.md`
