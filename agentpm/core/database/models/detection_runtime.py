"""
Runtime Overlay Data Models

Pydantic models for runtime environment metadata overlay on detection results.

Layer: Database Models (Domain Models)
Purpose: Type-safe, validated domain models for runtime environment enrichment
Architecture: Three-layer (Models → Adapters → Methods)

Models:
    - RuntimeOverlay: Runtime metadata overlay for detection results

Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class RuntimeOverlay(BaseModel):
    """
    Runtime metadata overlay for detection results.

    Enriches static detection with runtime environment metadata discovered
    during actual project execution, not just static analysis.

    Attributes:
        project_path: Absolute path to project root
        python_version: Python version string (e.g., "3.11.5")
        venv_path: Virtual environment path (if active)
        installed_packages: Dict mapping package_name -> installed_version
        environment: Relevant environment variables
        build_tools: Build tool versions (pip, npm, etc.)
        captured_at: Timestamp when runtime data was captured

    Example:
        >>> overlay = RuntimeOverlay(
        ...     project_path="/path/to/project",
        ...     python_version="3.11.5",
        ...     installed_packages={"requests": "2.31.0", "click": "8.1.7"},
        ...     build_tools={"pip": "23.3.1"}
        ... )
        >>> print(f"Python: {overlay.python_version}")
        Python: 3.11.5

    Usage:
        Static analysis finds imports → Runtime overlay adds actual installed versions
        This enables:
        - Version mismatch detection (static vs. runtime)
        - Runtime environment verification
        - Build tool compatibility checks
        - Environment-specific configuration validation
    """
    model_config = ConfigDict(validate_assignment=True)

    project_path: str = Field(
        ...,
        min_length=1,
        description="Absolute path to project root"
    )

    python_version: Optional[str] = Field(
        None,
        description="Python version string (e.g., '3.11.5')"
    )

    venv_path: Optional[str] = Field(
        None,
        description="Virtual environment path if active"
    )

    installed_packages: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of package_name → installed_version"
    )

    environment: Dict[str, str] = Field(
        default_factory=dict,
        description="Relevant environment variables (OS, PYTHON_PATH, etc.)"
    )

    build_tools: Dict[str, str] = Field(
        default_factory=dict,
        description="Build tool versions (pip, npm, poetry, etc.)"
    )

    captured_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when runtime data was captured"
    )

    def get_package_version(self, package_name: str) -> Optional[str]:
        """
        Get installed version for a package.

        Args:
            package_name: Package name to lookup

        Returns:
            Installed version if found, None otherwise

        Example:
            >>> overlay = RuntimeOverlay(
            ...     project_path="/project",
            ...     installed_packages={"requests": "2.31.0"}
            ... )
            >>> version = overlay.get_package_version("requests")
            >>> print(version)
            2.31.0
        """
        return self.installed_packages.get(package_name)

    def has_package(self, package_name: str) -> bool:
        """
        Check if package is installed in runtime environment.

        Args:
            package_name: Package name to check

        Returns:
            True if package is installed, False otherwise

        Example:
            >>> overlay = RuntimeOverlay(
            ...     project_path="/project",
            ...     installed_packages={"requests": "2.31.0"}
            ... )
            >>> overlay.has_package("requests")
            True
            >>> overlay.has_package("flask")
            False
        """
        return package_name in self.installed_packages

    def get_total_packages(self) -> int:
        """
        Get total count of installed packages.

        Returns:
            Total number of installed packages

        Example:
            >>> overlay = RuntimeOverlay(
            ...     project_path="/project",
            ...     installed_packages={"requests": "2.31.0", "click": "8.1.7"}
            ... )
            >>> overlay.get_total_packages()
            2
        """
        return len(self.installed_packages)

    def get_build_tool_version(self, tool_name: str) -> Optional[str]:
        """
        Get version of a build tool.

        Args:
            tool_name: Build tool name (e.g., 'pip', 'npm', 'poetry')

        Returns:
            Version string if found, None otherwise

        Example:
            >>> overlay = RuntimeOverlay(
            ...     project_path="/project",
            ...     build_tools={"pip": "23.3.1"}
            ... )
            >>> overlay.get_build_tool_version("pip")
            '23.3.1'
        """
        return self.build_tools.get(tool_name)
