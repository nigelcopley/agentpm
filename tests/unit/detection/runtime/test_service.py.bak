"""
Unit tests for RuntimeDetectorService

Tests runtime environment detection capabilities.
"""

import pytest
from pathlib import Path

from agentpm.core.detection.runtime import RuntimeDetectorService, RuntimeOverlay


class TestRuntimeDetectorService:
    """Test suite for RuntimeDetectorService"""

    def test_initialization(self):
        """Test service initialization"""
        project_path = Path(".")
        service = RuntimeDetectorService(project_path)

        assert service.project_path == project_path

    def test_capture_runtime_overlay(self):
        """Test capturing runtime overlay"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        # Verify overlay is created
        assert isinstance(overlay, RuntimeOverlay)

        # Verify basic fields
        assert overlay.project_path
        assert overlay.python_version
        assert overlay.captured_at

        # Verify Python version format
        parts = overlay.python_version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_get_python_version(self):
        """Test Python version detection"""
        service = RuntimeDetectorService(Path("."))
        version = service._get_python_version()

        assert isinstance(version, str)
        assert "." in version

        # Should be in format "major.minor.micro"
        parts = version.split(".")
        assert len(parts) == 3

    def test_get_installed_packages(self):
        """Test installed package enumeration"""
        service = RuntimeDetectorService(Path("."))
        packages = service._get_installed_packages()

        assert isinstance(packages, dict)
        # Should have at least some packages installed
        assert len(packages) > 0

        # Verify format
        for name, version in packages.items():
            assert isinstance(name, str)
            assert isinstance(version, str)
            assert len(name) > 0
            assert len(version) > 0

    def test_get_environment(self):
        """Test environment variable collection"""
        service = RuntimeDetectorService(Path("."))
        env = service._get_environment()

        assert isinstance(env, dict)

        # Should have basic environment info
        assert "OS" in env
        assert "PLATFORM" in env
        assert "PATH" in env

    def test_get_build_tool_versions(self):
        """Test build tool version detection"""
        service = RuntimeDetectorService(Path("."))
        tools = service._get_build_tool_versions()

        assert isinstance(tools, dict)

        # pip should be available in most Python environments
        if "pip" in tools:
            assert isinstance(tools["pip"], str)
            assert len(tools["pip"]) > 0

    def test_overlay_has_package(self):
        """Test RuntimeOverlay.has_package method"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        # Should have pytest installed (since we're running tests)
        assert overlay.has_package("pytest") or overlay.has_package("pytest-asyncio")

    def test_overlay_get_package_version(self):
        """Test RuntimeOverlay.get_package_version method"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        # Get version of a known package
        if overlay.has_package("pytest"):
            version = overlay.get_package_version("pytest")
            assert version is not None
            assert isinstance(version, str)
            assert len(version) > 0

    def test_overlay_get_total_packages(self):
        """Test RuntimeOverlay.get_total_packages method"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        total = overlay.get_total_packages()
        assert isinstance(total, int)
        assert total > 0

    def test_enrich_component_with_runtime(self):
        """Test component enrichment with runtime metadata"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        # Test with a package that should be installed
        enrichment = service.enrich_component_with_runtime(
            component_name="pytest",
            static_version="8.0.0",
            overlay=overlay
        )

        assert isinstance(enrichment, dict)
        assert "runtime_verified" in enrichment
        assert "runtime_version" in enrichment
        assert "version_mismatch" in enrichment

        # If pytest is installed, verify the enrichment
        if enrichment["runtime_verified"]:
            assert enrichment["runtime_version"] is not None
            assert isinstance(enrichment["version_mismatch"], bool)

    def test_enrich_component_not_installed(self):
        """Test component enrichment for non-installed package"""
        service = RuntimeDetectorService(Path("."))
        overlay = service.capture_runtime_overlay()

        # Test with a package that's unlikely to be installed
        enrichment = service.enrich_component_with_runtime(
            component_name="this-package-does-not-exist",
            static_version="1.0.0",
            overlay=overlay
        )

        assert enrichment["runtime_verified"] is False
        assert enrichment["runtime_version"] is None
        assert enrichment["version_mismatch"] is False
