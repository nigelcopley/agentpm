"""
Example: Complete Provider Implementation

This example demonstrates how to implement a complete provider
using the template architecture.
"""

from pathlib import Path
from typing import Dict, Optional, Any
from abc import ABC

from agentpm.core.database.service import DatabaseService
from agentpm.providers.base.provider import BaseProvider
from agentpm.providers.base.renderer import TemplateRenderer
from agentpm.providers.base.context import (
    TemplateContext,
    RenderResult,
    ProjectContext,
    AgentContext,
    RuleContext,
    ProviderConfig,
)


class ExampleProvider(BaseProvider):
    """
    Example provider implementation.

    This demonstrates the pattern for creating a new provider
    using the template architecture.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize example provider.

        Args:
            db: Database service instance
        """
        # Set template directory
        template_dir = Path(__file__).parent / "templates" / "example_provider"

        # Initialize base provider (sets up renderer)
        super().__init__(db, template_dir)

        # Provider-specific configuration
        self.provider_name = "example"
        self.provider_version = "1.0.0"

    def install(
        self,
        project_path: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Install example provider for project.

        Args:
            project_path: Project root directory
            config: Optional provider configuration

        Returns:
            True if installation successful
        """
        print(f"Installing {self.provider_name} provider for {project_path}")

        try:
            # 1. Load project context from database
            context = self._load_project_context(project_path)

            # 2. Apply provider-specific config overrides
            if config:
                context.provider.features_enabled.update(
                    config.get("features", {})
                )
                context.provider.custom_settings.update(
                    config.get("settings", {})
                )

            # 3. Render all configuration files
            results = self.render_configs(context)

            # 4. Write rendered files to disk
            output_dir = project_path / f".{self.provider_name}"
            output_dir.mkdir(parents=True, exist_ok=True)

            for filename, result in results.items():
                if not result.success:
                    print(f"ERROR rendering {filename}:")
                    for error in result.errors:
                        print(f"  - {error}")
                    return False

                # Write file
                output_path = output_dir / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(result.content)
                print(f"  Created: {output_path}")

                # Print warnings if any
                if result.warnings:
                    print(f"  Warnings for {filename}:")
                    for warning in result.warnings:
                        print(f"    - {warning}")

            # 5. Record installation in database
            self._record_installation(project_path, list(results.keys()))

            print(f"\n{self.provider_name} provider installed successfully!")
            return True

        except Exception as e:
            print(f"ERROR: Installation failed: {e}")
            return False

    def uninstall(self, project_path: Path) -> bool:
        """
        Uninstall example provider.

        Args:
            project_path: Project root directory

        Returns:
            True if uninstallation successful
        """
        print(f"Uninstalling {self.provider_name} provider from {project_path}")

        try:
            # 1. Remove provider directory
            provider_dir = project_path / f".{self.provider_name}"
            if provider_dir.exists():
                import shutil
                shutil.rmtree(provider_dir)
                print(f"  Removed: {provider_dir}")

            # 2. Remove database records
            self._remove_installation_record(project_path)

            print(f"\n{self.provider_name} provider uninstalled successfully!")
            return True

        except Exception as e:
            print(f"ERROR: Uninstallation failed: {e}")
            return False

    def update(self, project_path: Path) -> bool:
        """
        Update example provider installation.

        Args:
            project_path: Project root directory

        Returns:
            True if update successful
        """
        print(f"Updating {self.provider_name} provider for {project_path}")

        # For updates, we can re-run install to regenerate files
        return self.install(project_path)

    def verify(self, project_path: Path) -> bool:
        """
        Verify example provider installation.

        Args:
            project_path: Project root directory

        Returns:
            True if installation is valid
        """
        print(f"Verifying {self.provider_name} provider for {project_path}")

        provider_dir = project_path / f".{self.provider_name}"

        # Check if provider directory exists
        if not provider_dir.exists():
            print("  ERROR: Provider directory not found")
            return False

        # Check if expected files exist
        expected_files = [
            "config.md",
            "agents.md",
            "rules.md",
        ]

        missing_files = []
        for filename in expected_files:
            file_path = provider_dir / filename
            if not file_path.exists():
                missing_files.append(filename)

        if missing_files:
            print(f"  ERROR: Missing files: {', '.join(missing_files)}")
            return False

        print("  All files present")
        return True

    def render_configs(
        self,
        context: TemplateContext
    ) -> Dict[str, RenderResult]:
        """
        Render all provider-specific configuration files.

        Args:
            context: Template context with project data

        Returns:
            Dictionary mapping filename to RenderResult
        """
        results = {}

        # 1. Main configuration file
        results["config.md"] = self.renderer.render(
            "config.j2",
            context
        )

        # 2. Agents reference
        results["agents.md"] = self.renderer.render(
            "agents.j2",
            context
        )

        # 3. Rules reference
        results["rules.md"] = self.renderer.render(
            "rules.j2",
            context
        )

        # 4. Quick reference (cheat sheet)
        results["QUICKREF.md"] = self.renderer.render(
            "quickref.j2",
            context
        )

        return results

    def _record_installation(
        self,
        project_path: Path,
        installed_files: list
    ):
        """
        Record installation in database.

        Args:
            project_path: Project root directory
            installed_files: List of installed filenames
        """
        with self.db.connect() as conn:
            # Get project ID
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

            if not project_row:
                raise ValueError(f"Project not found: {project_path}")

            project_id = project_row['id']

            # Record installation
            conn.execute(
                """
                INSERT OR REPLACE INTO provider_installations
                (project_id, provider_type, provider_version, status, installed_files)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    self.provider_name,
                    self.provider_version,
                    "active",
                    str(installed_files),
                )
            )
            conn.commit()

    def _remove_installation_record(self, project_path: Path):
        """
        Remove installation record from database.

        Args:
            project_path: Project root directory
        """
        with self.db.connect() as conn:
            # Get project ID
            project_row = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_path),)
            ).fetchone()

            if not project_row:
                return

            project_id = project_row['id']

            # Remove installation record
            conn.execute(
                "DELETE FROM provider_installations WHERE project_id = ? AND provider_type = ?",
                (project_id, self.provider_name)
            )
            conn.commit()


def example_usage():
    """
    Demonstrate provider usage.
    """
    print("=" * 60)
    print("EXAMPLE: Provider Implementation")
    print("=" * 60)
    print()

    # Initialize database (mock for example)
    db = DatabaseService(Path("/tmp/example.db"))

    # Create provider instance
    provider = ExampleProvider(db)

    # Project path
    project_path = Path("/tmp/example_project")
    project_path.mkdir(exist_ok=True)

    # Install provider
    print("STEP 1: Install Provider")
    print("-" * 60)
    success = provider.install(
        project_path=project_path,
        config={
            "features": {
                "agents": True,
                "rules": True,
                "quick_ref": True,
            },
            "settings": {
                "format": "markdown",
            }
        }
    )
    print()

    if not success:
        print("Installation failed!")
        return

    # Verify installation
    print("STEP 2: Verify Installation")
    print("-" * 60)
    is_valid = provider.verify(project_path)
    print(f"Verification result: {'PASS' if is_valid else 'FAIL'}")
    print()

    # Update provider
    print("STEP 3: Update Provider")
    print("-" * 60)
    success = provider.update(project_path)
    print()

    # Uninstall provider
    print("STEP 4: Uninstall Provider")
    print("-" * 60)
    success = provider.uninstall(project_path)
    print()


def example_custom_renderer():
    """
    Example: Using custom renderer directly
    """
    print("=" * 60)
    print("EXAMPLE: Custom Renderer Usage")
    print("=" * 60)
    print()

    # Create custom renderer
    template_dir = Path(__file__).parent / "templates" / "example_provider"
    renderer = TemplateRenderer(
        template_dirs=[template_dir],
        cache_size=64,
        auto_escape=True,
        strict_undefined=True,
    )

    # Build sample context
    from example_context import build_sample_context
    context = build_sample_context()

    # Render custom template
    custom_template = """
# Custom Report

## Project Summary
- **Name**: {{ project.name }}
- **Type**: {{ project.app_type }}
- **Languages**: {{ project.languages | join(', ') }}

## Agent Distribution
- Tier 3 (Orchestrators): {{ agents | filter_by_tier(3) | length }}
- Tier 2 (Specialists): {{ agents | filter_by_tier(2) | length }}
- Tier 1 (Sub-Agents): {{ agents | filter_by_tier(1) | length }}

## Rule Summary
- Total Rules: {{ rules | length }}
- Blocking Rules: {{ rules | filter_rules(enforcement='BLOCK') | length }}
- Warning Rules: {{ rules | filter_rules(enforcement='WARN') | length }}

## Critical Rules
{% for rule in rules | filter_rules(enforcement='BLOCK') | sort_agents('priority', reverse=True) %}
{{ loop.index }}. **{{ rule.rule_id }}**: {{ rule.name }}
   {{ rule.description }}
{% endfor %}
    """

    result = renderer.render_string(custom_template, context)

    if result.success:
        print("Rendered output:")
        print(result.content)
    else:
        print("Rendering failed:")
        for error in result.errors:
            print(f"  - {error}")

    print()


def example_error_recovery():
    """
    Example: Handling rendering errors gracefully
    """
    print("=" * 60)
    print("EXAMPLE: Error Recovery")
    print("=" * 60)
    print()

    template_dir = Path(__file__).parent / "templates" / "example_provider"
    renderer = TemplateRenderer(
        template_dirs=[template_dir],
        strict_undefined=False,  # Don't raise on undefined
    )

    from example_context import build_sample_context
    context = build_sample_context()

    # Template with potential errors
    error_template = """
# Report with Potential Errors

## Valid Section
Project: {{ project.name }}

## Section with Undefined Variable
This might fail: {{ undefined_var | default('N/A') }}

## Section with Safe Access
Database: {{ project.database | default('Not specified') }}

## Loop with Error Handling
{% for agent in agents %}
- {{ agent.role }}: {{ agent.description | default('No description') }}
{% endfor %}
    """

    result = renderer.render_string(error_template, context)

    if result.success:
        print("Successfully rendered with error recovery:")
        print(result.content)

        if result.warnings:
            print("\nWarnings encountered:")
            for warning in result.warnings:
                print(f"  - {warning}")
    else:
        print("Rendering failed even with error recovery:")
        for error in result.errors:
            print(f"  - {error}")

    print()


if __name__ == "__main__":
    # Run examples (comment out database-dependent ones for now)
    # example_usage()  # Requires real database
    example_custom_renderer()
    example_error_recovery()

    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)
