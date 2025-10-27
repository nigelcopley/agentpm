"""
Claude Code Orchestrator (Simplified)

DEPRECATED: This orchestrator is deprecated in favor of the new template-based
generator architecture (AgentGeneratorService + ClaudeCodeGenerator).

This file now serves as a thin compatibility wrapper for backward compatibility.
New code should use AgentGeneratorService directly.

Original functionality (7 managers, 6,581 LOC) has been replaced with:
- ClaudeCodeGenerator: Template-based agent file generation
- AgentGeneratorService: Service layer wrapping generator with DB access

See: deprecated/README.md for migration guide
"""

import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.services.agent_generator import (
    AgentGeneratorService,
    AgentGenerationSummary,
)
from .models import ClaudeCodeIntegration


class ClaudeCodeOrchestrator:
    """
    DEPRECATED: Compatibility wrapper for legacy Claude Code integration.

    This class is deprecated. Use AgentGeneratorService instead:

    ```python
    from agentpm.core.services.agent_generator import AgentGeneratorService
    generator = AgentGeneratorService(db_service, project_path)
    summary = generator.generate_all()
    ```

    The old manager-based architecture (plugins, hooks, subagents, settings,
    slash commands, checkpointing, memory tools) has been replaced with a
    simpler template-based generator system.
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize Claude Code orchestrator (deprecated).

        Args:
            db_service: Database service for accessing APM data
        """
        warnings.warn(
            "ClaudeCodeOrchestrator is deprecated. "
            "Use AgentGeneratorService instead. "
            "See agentpm.core.services.agent_generator",
            DeprecationWarning,
            stacklevel=2
        )
        self.db = db_service
        self._integration_cache: Dict[str, ClaudeCodeIntegration] = {}

    def create_comprehensive_integration(
        self,
        output_dir: Path,
        project_id: Optional[int] = None,
        integration_name: str = "APM Claude Code Integration"
    ) -> ClaudeCodeIntegration:
        """
        Create comprehensive Claude Code integration (deprecated).

        This method now uses the new AgentGeneratorService internally
        and returns a minimal ClaudeCodeIntegration for compatibility.

        Args:
            output_dir: Directory to write integration files
            project_id: Optional project ID for project-specific components
            integration_name: Name of the integration

        Returns:
            Minimal ClaudeCodeIntegration for backward compatibility
        """
        # Use new generator service
        generator = AgentGeneratorService(
            db=self.db,
            project_path=output_dir,
            project_id=project_id or 1
        )

        # Generate all agent files
        summary = generator.generate_all(force=True)

        # Create minimal integration response for backward compatibility
        integration = ClaudeCodeIntegration(
            name=integration_name,
            description="Claude Code integration generated via new template system",
            version="2.0.0",  # Bumped to indicate new architecture
            plugins=[],  # Deprecated - no longer generated
            hooks=[],  # Deprecated - no longer generated
            subagents=[],  # Now generated via AgentGeneratorService
            settings=[],  # Deprecated - no longer generated
            slash_commands=[],  # Deprecated - no longer generated
            checkpoints=[],  # Deprecated - no longer generated
            memory_tools=[],  # Deprecated - no longer generated
            dependencies=["agentpm", "jinja2"],
            requirements=["python>=3.9", "pydantic>=2.0.0", "jinja2>=3.0.0"],
            permissions=["read_project_files", "write_agent_files"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Cache integration
        self._integration_cache[integration_name] = integration

        return integration

    def generate_project_integration(
        self,
        project_id: int,
        output_dir: Path
    ) -> ClaudeCodeIntegration:
        """
        Generate Claude Code integration for specific project (deprecated).

        Args:
            project_id: Project ID
            output_dir: Directory to write integration files

        Returns:
            Project-specific ClaudeCodeIntegration
        """
        integration_name = f"APM Project {project_id} Integration"

        return self.create_comprehensive_integration(
            output_dir=output_dir,
            project_id=project_id,
            integration_name=integration_name
        )

    def generate_agent_integration(
        self,
        agent_role: str,
        output_dir: Path
    ) -> ClaudeCodeIntegration:
        """
        Generate Claude Code integration for specific agent (deprecated).

        Args:
            agent_role: Agent role name
            output_dir: Directory to write integration files

        Returns:
            Agent-specific ClaudeCodeIntegration
        """
        integration_name = f"APM {agent_role} Agent Integration"

        return self.create_comprehensive_integration(
            output_dir=output_dir,
            integration_name=integration_name
        )

    def validate_integration(self, integration: ClaudeCodeIntegration) -> Dict[str, Any]:
        """
        Validate integration configuration (minimal implementation).

        Args:
            integration: Integration to validate

        Returns:
            Validation results
        """
        return {
            "valid": True,
            "errors": [],
            "warnings": [
                "ClaudeCodeOrchestrator is deprecated. "
                "Validation is minimal in compatibility mode."
            ],
            "component_counts": {
                "plugins": 0,
                "hooks": 0,
                "subagents": 0,  # Generated by AgentGeneratorService
                "settings": 0,
                "slash_commands": 0,
                "checkpoints": 0,
                "memory_tools": 0
            }
        }

    def get_integration(self, integration_name: str) -> Optional[ClaudeCodeIntegration]:
        """Get integration by name."""
        return self._integration_cache.get(integration_name)

    def list_integrations(self) -> List[str]:
        """List all cached integrations."""
        return list(self._integration_cache.keys())

    def export_integration(
        self,
        integration: ClaudeCodeIntegration,
        output_path: Path,
        format: str = "json"
    ) -> bool:
        """
        Export integration to file (deprecated).

        Args:
            integration: Integration to export
            output_path: Path to export file
            format: Export format (json, yaml)

        Returns:
            True if export successful
        """
        try:
            import json
            if format == "json":
                output_path.write_text(json.dumps(integration.model_dump(), indent=2, default=str))
            elif format == "yaml":
                import yaml
                output_path.write_text(yaml.dump(integration.model_dump(), default_flow_style=False))
            else:
                raise ValueError(f"Unsupported format: {format}")
            return True
        except Exception as e:
            print(f"Error exporting integration: {e}")
            return False

    def import_integration(self, input_path: Path) -> Optional[ClaudeCodeIntegration]:
        """
        Import integration from file (deprecated).

        Args:
            input_path: Path to import file

        Returns:
            Imported integration if successful
        """
        try:
            import json
            if input_path.suffix == ".json":
                data = json.loads(input_path.read_text())
            elif input_path.suffix in [".yaml", ".yml"]:
                import yaml
                data = yaml.safe_load(input_path.read_text())
            else:
                raise ValueError(f"Unsupported file format: {input_path.suffix}")

            integration = ClaudeCodeIntegration(**data)
            self._integration_cache[integration.name] = integration
            return integration
        except Exception as e:
            print(f"Error importing integration: {e}")
            return None

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            "total_integrations": len(self._integration_cache),
            "total_components": 0,  # Deprecated
            "component_breakdown": {},
            "cache_size": len(self._integration_cache),
            "note": "This orchestrator is deprecated. Use AgentGeneratorService."
        }

    def cleanup_integration_cache(self) -> int:
        """Cleanup integration cache."""
        cleaned_count = len(self._integration_cache)
        self._integration_cache.clear()
        return cleaned_count
