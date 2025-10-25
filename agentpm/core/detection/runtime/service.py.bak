"""
Runtime Detector Service

Layer 3 (Detection Services) - Runtime environment detection.

Responsibilities:
- Detect Python version and virtual environment
- Discover installed packages with actual versions
- Capture build tool versions (pip, npm, poetry, etc.)
- Collect relevant environment variables
- Provide runtime overlay for SBOM enrichment

Example:
    >>> from pathlib import Path
    >>> service = RuntimeDetectorService(Path("."))
    >>> overlay = service.capture_runtime_overlay()
    >>> print(f"Python: {overlay.python_version}")
    >>> print(f"Installed: {overlay.get_total_packages()} packages")

Performance Targets:
- Runtime capture: <500ms for typical projects
- Package enumeration: <200ms (uses importlib.metadata)
- Build tool detection: <100ms per tool

Version: 1.0.0
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from agentpm.core.database.models.detection_runtime import RuntimeOverlay


class RuntimeDetectorService:
    """
    Service for detecting runtime environment and installed packages.

    This service captures the actual runtime environment state to enrich
    static detection results with verified runtime metadata.

    Attributes:
        project_path: Root directory of the project to analyze

    Example:
        >>> service = RuntimeDetectorService(Path("/path/to/project"))
        >>> overlay = service.capture_runtime_overlay()
        >>>
        >>> # Check if package is actually installed
        >>> if overlay.has_package("requests"):
        ...     version = overlay.get_package_version("requests")
        ...     print(f"requests {version} is installed")
        >>>
        >>> # Check Python version
        >>> print(f"Running on Python {overlay.python_version}")
    """

    def __init__(self, project_path: Path):
        """
        Initialize runtime detector service.

        Args:
            project_path: Root directory of the project to analyze
        """
        self.project_path = project_path

    def capture_runtime_overlay(self) -> RuntimeOverlay:
        """
        Capture current runtime environment state.

        This method:
        1. Detects Python version
        2. Identifies active virtual environment
        3. Enumerates all installed packages with versions
        4. Captures relevant environment variables
        5. Detects build tool versions

        Returns:
            RuntimeOverlay with complete environment metadata

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> overlay = service.capture_runtime_overlay()
            >>> print(f"Captured {overlay.get_total_packages()} packages")
            >>> print(f"Python: {overlay.python_version}")
            >>> print(f"Venv: {overlay.venv_path or 'None'}")
        """
        return RuntimeOverlay(
            project_path=str(self.project_path.resolve()),
            python_version=self._get_python_version(),
            venv_path=self._detect_venv(),
            installed_packages=self._get_installed_packages(),
            environment=self._get_environment(),
            build_tools=self._get_build_tool_versions()
        )

    def _get_python_version(self) -> str:
        """
        Get Python version string.

        Returns:
            Python version in format "major.minor.micro"

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> version = service._get_python_version()
            >>> print(version)  # e.g., "3.11.5"
        """
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _detect_venv(self) -> Optional[str]:
        """
        Detect active virtual environment.

        Checks multiple sources:
        1. VIRTUAL_ENV environment variable (venv, virtualenv)
        2. CONDA_PREFIX environment variable (conda)
        3. sys.prefix comparison (fallback)

        Returns:
            Path to virtual environment if active, None otherwise

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> venv = service._detect_venv()
            >>> if venv:
            ...     print(f"Active venv: {venv}")
        """
        # Check VIRTUAL_ENV (standard venv/virtualenv)
        venv = os.environ.get('VIRTUAL_ENV')
        if venv:
            return venv

        # Check CONDA_PREFIX (conda environments)
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            return conda_prefix

        # Fallback: Compare sys.prefix with sys.base_prefix
        if hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix:
            return sys.prefix

        return None

    def _get_installed_packages(self) -> Dict[str, str]:
        """
        Get all installed packages with versions.

        Uses importlib.metadata to enumerate all installed distributions
        in the current Python environment.

        Returns:
            Dict mapping package_name -> version

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> packages = service._get_installed_packages()
            >>> print(f"Found {len(packages)} packages")
            >>> if "requests" in packages:
            ...     print(f"requests: {packages['requests']}")

        Note:
            This method enumerates packages in the current Python environment,
            which may include system packages if no virtual environment is active.
        """
        try:
            import importlib.metadata

            packages = {}
            for dist in importlib.metadata.distributions():
                # Normalize package name (lowercase, replace - with _)
                # This matches pip's package name normalization
                name = dist.name
                version = dist.version

                # Store with original name for maximum compatibility
                packages[name] = version

            return packages

        except Exception as e:
            # If metadata enumeration fails, return empty dict
            # This can happen in restricted environments
            return {}

    def _get_environment(self) -> Dict[str, str]:
        """
        Get relevant environment variables.

        Captures environment variables that are relevant for runtime analysis:
        - OS/Platform information
        - Python-related paths
        - Build configuration

        Returns:
            Dict of environment variable names -> values

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> env = service._get_environment()
            >>> print(f"OS: {env.get('OS')}")
            >>> print(f"Platform: {env.get('PLATFORM')}")

        Note:
            PATH is truncated to 200 characters to avoid excessive data.
        """
        return {
            'OS': os.name,
            'PLATFORM': sys.platform,
            'PYTHON_PATH': os.environ.get('PYTHONPATH', ''),
            'PATH': os.environ.get('PATH', '')[:200],  # Truncate for brevity
            'HOME': os.environ.get('HOME', ''),
            'USER': os.environ.get('USER', os.environ.get('USERNAME', '')),
        }

    def _get_build_tool_versions(self) -> Dict[str, str]:
        """
        Get build tool versions (pip, npm, poetry, etc.).

        Attempts to detect versions of common build tools by running
        their version commands. Each command has a 2-second timeout.

        Returns:
            Dict mapping tool_name -> version_string

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> tools = service._get_build_tool_versions()
            >>> if "pip" in tools:
            ...     print(f"pip: {tools['pip']}")
            >>> if "npm" in tools:
            ...     print(f"npm: {tools['npm']}")

        Supported Tools:
            - pip: Python package installer
            - poetry: Python dependency management
            - npm: Node package manager
            - yarn: Alternative Node package manager
            - pnpm: Fast Node package manager

        Note:
            Failed tool detections are silently ignored (tool not in PATH
            or execution error). Only successfully detected tools are returned.
        """
        tools = {}

        # Python tools
        self._detect_tool_version(tools, 'pip', ['pip', '--version'], r'pip ([\d.]+)')
        self._detect_tool_version(tools, 'poetry', ['poetry', '--version'], r'Poetry.*? ([\d.]+)')

        # Node.js tools
        self._detect_tool_version(tools, 'npm', ['npm', '--version'], None)  # Returns version directly
        self._detect_tool_version(tools, 'yarn', ['yarn', '--version'], None)
        self._detect_tool_version(tools, 'pnpm', ['pnpm', '--version'], None)

        return tools

    def _detect_tool_version(
        self,
        tools: Dict[str, str],
        tool_name: str,
        command: list,
        version_pattern: Optional[str] = None
    ) -> None:
        r"""
        Detect version of a single build tool.

        Runs the tool's version command and extracts version string.

        Args:
            tools: Dict to store detected version (mutated in place)
            tool_name: Name of the tool (key in tools dict)
            command: Command to run (e.g., ['pip', '--version'])
            version_pattern: Optional regex pattern to extract version from output.
                           If None, entire output (stripped) is used as version.

        Example:
            >>> tools = {}
            >>> service = RuntimeDetectorService(Path("."))
            >>> service._detect_tool_version(tools, 'pip', ['pip', '--version'], r'pip ([\d.]+)')
            >>> print(tools.get('pip'))  # e.g., "23.3.1"
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=2,
                check=False  # Don't raise on non-zero exit
            )

            if result.returncode == 0:
                output = result.stdout.strip()

                if version_pattern:
                    # Extract version using regex
                    import re
                    match = re.search(version_pattern, output)
                    if match:
                        tools[tool_name] = match.group(1)
                else:
                    # Use entire output as version
                    tools[tool_name] = output

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Tool not found or execution failed - silently ignore
            pass

    def enrich_component_with_runtime(
        self,
        component_name: str,
        static_version: str,
        overlay: RuntimeOverlay
    ) -> Dict[str, Any]:
        """
        Enrich a single component with runtime metadata.

        Compares static detection version with runtime installed version
        to identify mismatches.

        Args:
            component_name: Component/package name
            static_version: Version from static analysis (requirements.txt, etc.)
            overlay: Runtime overlay with installed packages

        Returns:
            Dict with enrichment metadata:
                - runtime_version: Actual installed version
                - runtime_verified: True if installed
                - version_mismatch: True if versions differ

        Example:
            >>> service = RuntimeDetectorService(Path("."))
            >>> overlay = service.capture_runtime_overlay()
            >>> enrichment = service.enrich_component_with_runtime(
            ...     "requests",
            ...     "2.30.0",  # Static version
            ...     overlay
            ... )
            >>> if enrichment["version_mismatch"]:
            ...     print(f"Version mismatch: {enrichment}")
        """
        runtime_version = overlay.get_package_version(component_name)
        runtime_verified = overlay.has_package(component_name)

        # Normalize versions for comparison (remove prefixes like ^, ~, >=)
        import re
        normalized_static = re.sub(r'^[~^><=!]+\s*', '', static_version)

        version_mismatch = False
        if runtime_verified and runtime_version:
            # Compare versions (simple string comparison)
            version_mismatch = normalized_static != runtime_version

        return {
            "runtime_version": runtime_version,
            "runtime_verified": runtime_verified,
            "version_mismatch": version_mismatch,
        }
