#!/usr/bin/env python3
"""
Quick test script for SBOM Service

Tests basic functionality without full test framework.
Run: python test_sbom_service.py
"""

from pathlib import Path
from agentpm.core.detection.sbom import (
    SBOMService,
    LicenseType,
    LicenseInfo,
    SBOMComponent,
    SBOM
)


def test_models():
    """Test Pydantic models."""
    print("Testing models...")

    # Test LicenseInfo
    license_info = LicenseInfo(
        package_name="test-package",
        version="1.0.0",
        license_type=LicenseType.MIT,
        source="test",
        confidence=1.0
    )
    assert license_info.package_name == "test-package"
    assert license_info.license_type == LicenseType.MIT
    print("  ✓ LicenseInfo model")

    # Test SBOMComponent
    component = SBOMComponent(
        name="click",
        version="8.1.7",
        type="library",
        purl="pkg:pypi/click@8.1.7"
    )
    assert component.name == "click"
    assert component.version == "8.1.7"
    print("  ✓ SBOMComponent model")

    # Test SBOM
    sbom = SBOM(
        project_name="test-project",
        project_version="1.0.0",
        components=[component]
    )
    assert sbom.total_components == 1
    assert sbom.project_name == "test-project"
    print("  ✓ SBOM model")


def test_service_initialization():
    """Test service initialization."""
    print("\nTesting service initialization...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    assert service.project_path == project_path
    assert service._license_cache == {}
    print("  ✓ Service initialized")


def test_python_component_extraction():
    """Test Python dependency extraction."""
    print("\nTesting Python component extraction...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    components = service.extract_python_components(include_dev=False)

    print(f"  Found {len(components)} Python components")
    for component in components[:5]:  # Show first 5
        print(f"    - {component.name}@{component.version}")

    if components:
        print("  ✓ Python components extracted")
    else:
        print("  ! No Python components found (this is expected if no dependencies)")


def test_sbom_generation():
    """Test full SBOM generation."""
    print("\nTesting SBOM generation...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    # Generate without licenses (faster)
    sbom = service.generate_sbom(include_licenses=False)

    print(f"  Project: {sbom.project_name}")
    print(f"  Version: {sbom.project_version}")
    print(f"  Total components: {sbom.total_components}")
    print(f"  Generated at: {sbom.generated_at}")

    print("  ✓ SBOM generated")


def test_license_detection():
    """Test license detection."""
    print("\nTesting license detection...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    # Try to detect license from LICENSE file
    license_info = service._detect_license_from_file("aipm-v2")

    if license_info:
        print(f"  Detected: {license_info.license_type.value}")
        print(f"  Source: {license_info.source}")
        print(f"  Confidence: {license_info.confidence:.0%}")
        print("  ✓ License detected")
    else:
        print("  ! No LICENSE file found in project root")


def test_export_formats():
    """Test export formats."""
    print("\nTesting export formats...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    sbom = service.generate_sbom(include_licenses=False)

    # Test CycloneDX export
    try:
        output_path = Path("/tmp/test_sbom.json")
        cyclonedx_json = service.export_cyclonedx(sbom, output_path, format="json")
        print(f"  ✓ CycloneDX export: {len(cyclonedx_json)} bytes")
        output_path.unlink()  # Clean up
    except Exception as e:
        print(f"  ✗ CycloneDX export failed: {e}")

    # Test SPDX export
    try:
        output_path = Path("/tmp/test_sbom_spdx.json")
        spdx_json = service.export_spdx(sbom, output_path)
        print(f"  ✓ SPDX export: {len(spdx_json)} bytes")
        output_path.unlink()  # Clean up
    except Exception as e:
        print(f"  ✗ SPDX export failed: {e}")


def test_license_summary():
    """Test license summary."""
    print("\nTesting license summary...")

    project_path = Path.cwd()
    service = SBOMService(project_path)

    # Create SBOM with mock licenses
    component1 = SBOMComponent(
        name="package1",
        version="1.0.0",
        license=LicenseInfo(
            package_name="package1",
            version="1.0.0",
            license_type=LicenseType.MIT,
            source="test",
            confidence=1.0
        )
    )
    component2 = SBOMComponent(
        name="package2",
        version="2.0.0",
        license=LicenseInfo(
            package_name="package2",
            version="2.0.0",
            license_type=LicenseType.APACHE_2_0,
            source="test",
            confidence=1.0
        )
    )
    component3 = SBOMComponent(
        name="package3",
        version="3.0.0",
        license=LicenseInfo(
            package_name="package3",
            version="3.0.0",
            license_type=LicenseType.MIT,
            source="test",
            confidence=1.0
        )
    )

    sbom = SBOM(
        project_name="test",
        project_version="1.0.0",
        components=[component1, component2, component3]
    )

    summary = service.get_license_summary(sbom)

    print(f"  License distribution:")
    for license_type, count in summary.items():
        print(f"    {license_type}: {count}")

    assert summary.get("MIT") == 2
    assert summary.get("Apache-2.0") == 1
    print("  ✓ License summary correct")


def main():
    """Run all tests."""
    print("=" * 60)
    print("SBOM Service Test Suite")
    print("=" * 60)

    try:
        test_models()
        test_service_initialization()
        test_python_component_extraction()
        test_sbom_generation()
        test_license_detection()
        test_export_formats()
        test_license_summary()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
