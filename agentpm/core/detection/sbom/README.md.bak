# SBOM Service Package

**Layer 3 Detection Service** - Software Bill of Materials generation and license detection.

## Overview

The SBOM (Software Bill of Materials) Service generates comprehensive dependency inventories for projects, including license information and support for multiple export formats (CycloneDX, SPDX).

### Key Features

- **Multi-Language Support**: Python and JavaScript/Node.js dependencies
- **License Detection**: Automatic license identification from metadata and files
- **Standard Formats**: Export to CycloneDX 1.5 and SPDX 2.3
- **Package URLs**: Generate standard PURL identifiers
- **License Compliance**: Built-in license analysis and filtering
- **Performance**: In-memory caching for fast repeated queries

### Architecture Compliance

This package follows the **three-layer architecture**:

```
Layer 3 (Detection Services) - This package
    ↓ uses
Layer 1 (Shared Utilities) - file_parsers
    ↓ NO dependencies on
Layer 2 (Plugins) - Not used
```

**No circular dependencies**: This service uses Layer 1 utilities directly, not Layer 2 plugins.

## Quick Start

```python
from pathlib import Path
from agentpm.core.detection.sbom import SBOMService

# Initialize service
service = SBOMService(Path("."))

# Generate SBOM
sbom = service.generate_sbom(include_licenses=True)

# View results
print(f"Total components: {sbom.total_components}")
print(f"Licenses: {sbom.license_summary}")

# Export to CycloneDX
service.export_cyclonedx(sbom, Path("sbom.json"))
```

## Components

### Models (`models.py`)

Pydantic models for SBOM data:

- **LicenseType**: Enumeration of common license types
- **LicenseInfo**: License information for a package
- **SBOMComponent**: Individual dependency component
- **SBOM**: Complete Software Bill of Materials

### Service (`service.py`)

Main SBOM generation service:

```python
class SBOMService:
    def generate_sbom(include_licenses=True, include_dev_deps=False) -> SBOM
    def extract_python_components(include_dev=False) -> List[SBOMComponent]
    def extract_javascript_components(include_dev=False) -> List[SBOMComponent]
    def detect_license(package_name, version) -> Optional[LicenseInfo]
    def export_cyclonedx(sbom, output_path, format="json") -> str
    def export_spdx(sbom, output_path) -> str
    def get_license_summary(sbom) -> Dict[str, int]
```

## Usage Examples

### Basic SBOM Generation

```python
service = SBOMService(Path("."))
sbom = service.generate_sbom()

print(f"Project: {sbom.project_name}")
print(f"Components: {sbom.total_components}")
```

### Python Dependencies Only

```python
components = service.extract_python_components(include_dev=True)

for comp in components:
    print(f"{comp.name}@{comp.version}")
```

### License Detection

```python
sbom = service.generate_sbom(include_licenses=True)

for component in sbom.components:
    if component.license:
        print(f"{component.name}: {component.license.license_type.value}")
```

### Export Formats

```python
# CycloneDX (JSON)
service.export_cyclonedx(sbom, Path("sbom.json"), format="json")

# SPDX (JSON)
service.export_spdx(sbom, Path("sbom.spdx.json"))
```

### License Compliance

```python
allowed = [LicenseType.MIT, LicenseType.APACHE_2_0]
violations = [
    c for c in sbom.components
    if c.license and c.license.license_type not in allowed
]

if violations:
    print(f"Found {len(violations)} license violations")
```

## Supported License Types

### Permissive Licenses
- MIT
- Apache-2.0
- BSD-3-Clause
- BSD-2-Clause
- ISC

### Copyleft Licenses
- GPL-2.0
- GPL-3.0
- LGPL-2.1
- LGPL-3.0
- AGPL-3.0

### Other
- MPL-2.0
- Unlicense
- Proprietary
- Unknown

## Performance

### Targets

| Operation | Target |
|-----------|--------|
| SBOM Generation (no licenses) | <100ms |
| SBOM Generation (with licenses) | <1s |
| License Detection (cached) | <10ms |
| Export to CycloneDX | <50ms |
| Export to SPDX | <50ms |

### Caching

License detection results are cached in-memory:

```python
service = SBOMService(Path("."))

# First call: detects license (slow)
license1 = service.detect_license("requests", "2.31.0")

# Second call: uses cache (fast)
license2 = service.detect_license("requests", "2.31.0")
```

## Dependencies

### Layer 1 Utilities (Required)

- `agentpm.core.plugins.utils.file_parsers`:
  - `parse_python_dependencies()`
  - `parse_javascript_dependencies()`
  - `parse_toml()`
  - `parse_json()`

### Optional Libraries

- `cyclonedx-python-lib`: Official CycloneDX support (falls back to manual JSON)

## Testing

Run basic tests:

```bash
python test_sbom_service.py
```

Run comprehensive examples:

```bash
python examples/sbom_generation_example.py
```

## CLI Integration

```bash
# Generate SBOM
apm detect sbom --format json --output sbom.json

# Include licenses
apm detect sbom --include-licenses --format cyclonedx

# Export to SPDX
apm detect sbom --format spdx --output sbom.spdx.json
```

## Future Enhancements

### Planned Features

1. **PyPI/npm API Integration**: Query package registries for license data
2. **Transitive Dependencies**: Include indirect dependencies
3. **Vulnerability Scanning**: CVE database integration
4. **License Compatibility**: Detect license conflicts
5. **Historical Tracking**: Track dependency changes over time

### API Enhancements

```python
# Future API (not yet implemented)
sbom = service.generate_sbom(
    include_transitive=True,        # Include indirect dependencies
    scan_vulnerabilities=True,      # Check CVE databases
    validate_compatibility=True     # Check license conflicts
)
```

## References

### Standards

- [CycloneDX Specification](https://cyclonedx.org/)
- [SPDX Specification](https://spdx.dev/)
- [Package URL (PURL) Spec](https://github.com/package-url/purl-spec)

### Documentation

- Architecture: `docs/architecture/architecture/detection-pack-architecture.md`
- Usage Guide: `USAGE.md`
- Examples: `examples/sbom_generation_example.py`

## License

Same license as APM (Agent Project Manager) project.

## Version

1.0.0
