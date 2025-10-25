#!/usr/bin/env python3
"""
SBOM Generation Example

Demonstrates how to use the SBOM Service to generate Software Bill of Materials
for a project.

Usage:
    python examples/sbom_generation_example.py
"""

from pathlib import Path
from agentpm.core.detection.sbom import SBOMService, LicenseType


def example_basic_sbom():
    """Generate basic SBOM without license detection."""
    print("=" * 70)
    print("Example 1: Basic SBOM Generation")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=False)

    print(f"\nProject: {sbom.project_name}")
    print(f"Version: {sbom.project_version}")
    print(f"Total Components: {sbom.total_components}")
    print(f"Generated: {sbom.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\nComponents:")
    for component in sbom.components[:10]:  # Show first 10
        print(f"  - {component.name}@{component.version} ({component.type})")
        if component.purl:
            print(f"    PURL: {component.purl}")


def example_sbom_with_licenses():
    """Generate SBOM with license detection."""
    print("\n" + "=" * 70)
    print("Example 2: SBOM with License Detection")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True)

    print(f"\nProject: {sbom.project_name}")
    print(f"Components with licenses: {sum(1 for c in sbom.components if c.license)}")

    print(f"\nLicense Distribution:")
    for license_type, count in sbom.license_summary.items():
        print(f"  {license_type}: {count} components")

    print(f"\nComponents with detected licenses:")
    for component in sbom.components:
        if component.license:
            print(f"  - {component.name}: {component.license.license_type.value}")
            print(f"    Source: {component.license.source}")
            print(f"    Confidence: {component.license.confidence:.0%}")


def example_python_only():
    """Extract Python dependencies only."""
    print("\n" + "=" * 70)
    print("Example 3: Python Dependencies Only")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    python_components = service.extract_python_components(include_dev=True)

    print(f"\nFound {len(python_components)} Python packages")

    # Group by type
    runtime = [c for c in python_components if c.type == "library"]
    dev = [c for c in python_components if c.type == "development"]

    print(f"\nRuntime dependencies: {len(runtime)}")
    for comp in runtime[:5]:
        print(f"  - {comp.name}@{comp.version}")

    if dev:
        print(f"\nDevelopment dependencies: {len(dev)}")
        for comp in dev[:5]:
            print(f"  - {comp.name}@{comp.version}")


def example_export_cyclonedx():
    """Export SBOM to CycloneDX format."""
    print("\n" + "=" * 70)
    print("Example 4: Export to CycloneDX Format")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True)

    output_path = Path("/tmp/aipm_sbom_cyclonedx.json")
    cyclonedx_json = service.export_cyclonedx(sbom, output_path, format="json")

    print(f"\nExported CycloneDX SBOM:")
    print(f"  Path: {output_path}")
    print(f"  Size: {len(cyclonedx_json)} bytes")
    print(f"  Format: CycloneDX 1.5 (JSON)")

    # Show sample of output
    import json
    data = json.loads(cyclonedx_json)
    print(f"\nSample output:")
    print(f"  BOM Format: {data['bomFormat']}")
    print(f"  Spec Version: {data['specVersion']}")
    print(f"  Components: {len(data['components'])}")

    print(f"\n✓ Full SBOM written to: {output_path}")


def example_export_spdx():
    """Export SBOM to SPDX format."""
    print("\n" + "=" * 70)
    print("Example 5: Export to SPDX Format")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True)

    output_path = Path("/tmp/aipm_sbom_spdx.json")
    spdx_json = service.export_spdx(sbom, output_path)

    print(f"\nExported SPDX SBOM:")
    print(f"  Path: {output_path}")
    print(f"  Size: {len(spdx_json)} bytes")
    print(f"  Format: SPDX 2.3 (JSON)")

    # Show sample of output
    import json
    data = json.loads(spdx_json)
    print(f"\nSample output:")
    print(f"  SPDX Version: {data['spdxVersion']}")
    print(f"  Data License: {data['dataLicense']}")
    print(f"  Packages: {len(data['packages'])}")

    print(f"\n✓ Full SBOM written to: {output_path}")


def example_license_compliance():
    """Check license compliance."""
    print("\n" + "=" * 70)
    print("Example 6: License Compliance Check")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True)

    # Define allowed licenses
    allowed_licenses = [
        LicenseType.MIT,
        LicenseType.APACHE_2_0,
        LicenseType.BSD_3_CLAUSE,
        LicenseType.BSD_2_CLAUSE,
        LicenseType.ISC,
    ]

    print(f"\nAllowed licenses:")
    for license_type in allowed_licenses:
        print(f"  - {license_type.value}")

    # Check for violations
    violations = []
    for component in sbom.components:
        if component.license:
            if component.license.license_type not in allowed_licenses:
                violations.append(component)

    if violations:
        print(f"\n⚠ License compliance violations: {len(violations)}")
        for component in violations:
            print(f"  - {component.name}: {component.license.license_type.value}")
    else:
        print(f"\n✓ All licenses compliant")

    # Summary
    print(f"\nCompliance Summary:")
    print(f"  Total components: {sbom.total_components}")
    print(f"  Violations: {len(violations)}")
    print(f"  Compliance rate: {((sbom.total_components - len(violations)) / sbom.total_components * 100):.1f}%")


def example_filter_by_license():
    """Filter components by license type."""
    print("\n" + "=" * 70)
    print("Example 7: Filter Components by License")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True)

    # Find all MIT-licensed components
    mit_components = [
        c for c in sbom.components
        if c.license and c.license.license_type == LicenseType.MIT
    ]

    print(f"\nMIT-licensed components: {len(mit_components)}")
    for component in mit_components:
        print(f"  - {component.name}@{component.version}")

    # Find all copyleft licenses
    copyleft = [LicenseType.GPL_2_0, LicenseType.GPL_3_0, LicenseType.AGPL_3_0]
    copyleft_components = [
        c for c in sbom.components
        if c.license and c.license.license_type in copyleft
    ]

    if copyleft_components:
        print(f"\nCopyleft-licensed components: {len(copyleft_components)}")
        for component in copyleft_components:
            print(f"  - {component.name}: {component.license.license_type.value}")
    else:
        print(f"\n✓ No copyleft licenses found")


def example_comprehensive_report():
    """Generate comprehensive SBOM report."""
    print("\n" + "=" * 70)
    print("Example 8: Comprehensive SBOM Report")
    print("=" * 70)

    service = SBOMService(Path.cwd())
    sbom = service.generate_sbom(include_licenses=True, include_dev_deps=True)

    print(f"\n{'=' * 70}")
    print(f"Software Bill of Materials Report")
    print(f"{'=' * 70}")

    print(f"\nProject Information:")
    print(f"  Name: {sbom.project_name}")
    print(f"  Version: {sbom.project_version}")
    print(f"  Generated: {sbom.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\nDependency Summary:")
    print(f"  Total components: {sbom.total_components}")

    runtime = [c for c in sbom.components if c.type == "library"]
    dev = [c for c in sbom.components if c.type == "development"]
    print(f"  Runtime dependencies: {len(runtime)}")
    print(f"  Development dependencies: {len(dev)}")

    print(f"\nLicense Distribution:")
    for license_type, count in sorted(sbom.license_summary.items(), key=lambda x: -x[1]):
        print(f"  {license_type}: {count}")

    print(f"\nPackage URLs (PURL):")
    for component in sbom.components[:5]:
        if component.purl:
            print(f"  - {component.purl}")

    print(f"\n{'=' * 70}")
    print("End of Report")
    print(f"{'=' * 70}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SBOM Service Examples")
    print("=" * 70)

    try:
        example_basic_sbom()
        example_sbom_with_licenses()
        example_python_only()
        example_export_cyclonedx()
        example_export_spdx()
        example_license_compliance()
        example_filter_by_license()
        example_comprehensive_report()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
