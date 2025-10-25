# SBOM Service - Quick Reference

One-page reference for the SBOM Service API.

---

## Import

```python
from pathlib import Path
from agentpm.core.detection.sbom import (
    SBOMService,
    LicenseType,
    LicenseInfo,
    SBOMComponent,
    SBOM
)
```

---

## Initialize Service

```python
service = SBOMService(Path("."))  # Current directory
service = SBOMService(Path("/path/to/project"))  # Specific path
```

---

## Generate SBOM

```python
# Full SBOM with licenses
sbom = service.generate_sbom(
    include_licenses=True,
    include_dev_deps=False
)

# Quick SBOM (no licenses)
sbom = service.generate_sbom(include_licenses=False)

# Include dev dependencies
sbom = service.generate_sbom(include_dev_deps=True)
```

---

## Extract Components

```python
# Python dependencies
python_components = service.extract_python_components(include_dev=False)
python_components = service.extract_python_components(include_dev=True)

# JavaScript dependencies
js_components = service.extract_javascript_components(include_dev=False)
js_components = service.extract_javascript_components(include_dev=True)
```

---

## License Detection

```python
# Detect license for specific package
license_info = service.detect_license("requests", "2.31.0")

if license_info:
    print(license_info.license_type.value)  # "Apache-2.0"
    print(license_info.source)              # "file" or "metadata"
    print(license_info.confidence)          # 0.95
```

---

## Export Formats

```python
# CycloneDX (JSON)
service.export_cyclonedx(sbom, Path("sbom.json"), format="json")

# SPDX (JSON)
service.export_spdx(sbom, Path("sbom.spdx.json"))
```

---

## License Summary

```python
summary = service.get_license_summary(sbom)
# Returns: {"MIT": 10, "Apache-2.0": 5, ...}

for license_type, count in summary.items():
    print(f"{license_type}: {count}")
```

---

## SBOM Model

```python
sbom = service.generate_sbom()

# Properties
sbom.project_name           # "aipm-v2"
sbom.project_version        # "0.1.1"
sbom.total_components       # 12 (auto-computed)
sbom.components             # List[SBOMComponent]
sbom.license_summary        # Dict[str, int] (auto-computed)
sbom.generated_at           # datetime
sbom.format_version         # "1.0"
```

---

## SBOMComponent Model

```python
for component in sbom.components:
    print(component.name)           # "click"
    print(component.version)        # "8.1.7"
    print(component.type)           # "library"
    print(component.purl)           # "pkg:pypi/click@8.1.7"
    print(component.license)        # LicenseInfo or None
    print(component.dependencies)   # List[str]
    print(component.description)    # Optional[str]
```

---

## LicenseInfo Model

```python
if component.license:
    print(component.license.package_name)   # "click"
    print(component.license.version)        # "8.1.7"
    print(component.license.license_type)   # LicenseType.BSD_3_CLAUSE
    print(component.license.source)         # "file", "metadata", etc.
    print(component.license.confidence)     # 0.95
    print(component.license.license_text)   # Optional full text
```

---

## LicenseType Enum

```python
# Permissive
LicenseType.MIT
LicenseType.APACHE_2_0
LicenseType.BSD_3_CLAUSE
LicenseType.BSD_2_CLAUSE
LicenseType.ISC

# Copyleft
LicenseType.GPL_2_0
LicenseType.GPL_3_0
LicenseType.LGPL_2_1
LicenseType.LGPL_3_0
LicenseType.AGPL_3_0

# Other
LicenseType.MPL_2_0
LicenseType.EPL_2_0
LicenseType.UNLICENSE
LicenseType.CC0_1_0
LicenseType.PROPRIETARY
LicenseType.UNKNOWN
```

---

## Filter Components

```python
# By license type
mit_components = [
    c for c in sbom.components
    if c.license and c.license.license_type == LicenseType.MIT
]

# By component type
libraries = [c for c in sbom.components if c.type == "library"]
dev_deps = [c for c in sbom.components if c.type == "development"]

# By language (via PURL)
python_deps = [c for c in sbom.components if c.purl and "pypi" in c.purl]
npm_deps = [c for c in sbom.components if c.purl and "npm" in c.purl]
```

---

## License Compliance Check

```python
allowed = [LicenseType.MIT, LicenseType.APACHE_2_0, LicenseType.BSD_3_CLAUSE]

violations = [
    c for c in sbom.components
    if c.license and c.license.license_type not in allowed
]

if violations:
    for component in violations:
        print(f"{component.name}: {component.license.license_type.value}")
```

---

## Common Patterns

### Generate and Export

```python
service = SBOMService(Path("."))
sbom = service.generate_sbom(include_licenses=True)
service.export_cyclonedx(sbom, Path("sbom.json"))
```

### Analyze License Distribution

```python
sbom = service.generate_sbom(include_licenses=True)
summary = service.get_license_summary(sbom)

for license_type, count in sorted(summary.items(), key=lambda x: -x[1]):
    print(f"{license_type}: {count}")
```

### Check for Copyleft Licenses

```python
copyleft = [LicenseType.GPL_2_0, LicenseType.GPL_3_0, LicenseType.AGPL_3_0]

copyleft_components = [
    c for c in sbom.components
    if c.license and c.license.license_type in copyleft
]

if copyleft_components:
    print(f"Found {len(copyleft_components)} copyleft licenses")
```

### Python-Only Analysis

```python
python_components = service.extract_python_components(include_dev=True)

runtime = [c for c in python_components if c.type == "library"]
dev = [c for c in python_components if c.type == "development"]

print(f"Runtime: {len(runtime)}, Dev: {len(dev)}")
```

---

## Performance Tips

### Caching

```python
# License detection is cached automatically
service = SBOMService(Path("."))

# First call: slow
license1 = service.detect_license("requests", "2.31.0")

# Second call: instant (cached)
license2 = service.detect_license("requests", "2.31.0")
```

### Skip Licenses for Speed

```python
# Fast: no license detection
sbom = service.generate_sbom(include_licenses=False)  # ~50ms

# Slower: with license detection
sbom = service.generate_sbom(include_licenses=True)   # ~200ms
```

---

## Error Handling

```python
try:
    sbom = service.generate_sbom()

    if sbom.total_components == 0:
        print("No dependencies found")
        print("Check for: pyproject.toml, requirements.txt, package.json")

except Exception as e:
    print(f"SBOM generation failed: {e}")
```

---

## Examples Location

- **Basic Tests**: `test_sbom_service.py`
- **Comprehensive Examples**: `examples/sbom_generation_example.py`
- **Documentation**: `agentpm/core/detection/sbom/USAGE.md`

---

## Performance Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| SBOM generation (no licenses) | <100ms | ~50ms |
| SBOM generation (with licenses) | <1s | ~200ms |
| License detection (cached) | <10ms | <5ms |
| CycloneDX export | <50ms | ~10ms |
| SPDX export | <50ms | ~15ms |

---

**Version**: 1.0.0
**Layer**: Layer 3 (Detection Services)
**Documentation**: See `USAGE.md` for detailed examples
