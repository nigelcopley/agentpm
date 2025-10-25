"""
Claude Code Orchestrator

Orchestrates all Claude Code integrations for APM (Agent Project Manager) including
plugins, hooks, subagents, settings, slash commands, checkpointing,
and memory tools.

Provides unified interface for managing Claude Code components.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from .models import (
    ClaudeCodeIntegration,
    PluginDefinition,
    HookDefinition,
    SubagentDefinition,
    SettingsDefinition,
    SlashCommandDefinition,
    CheckpointDefinition,
    MemoryToolDefinition,
)
from .plugins import ClaudeCodePluginManager
from .hooks import ClaudeCodeHooksManager
from .subagents import ClaudeCodeSubagentsManager
from .settings import ClaudeCodeSettingsManager
from .slash_commands import ClaudeCodeSlashCommandsManager
from .checkpointing import ClaudeCodeCheckpointingManager
from .memory_tool import ClaudeCodeMemoryToolManager


class ClaudeCodeOrchestrator:
    """
    Orchestrates all Claude Code integrations for APM (Agent Project Manager).
    
    Provides unified interface for managing Claude Code components
    and generating comprehensive Claude Code configurations.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize Claude Code orchestrator.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        
        # Initialize component managers
        self.plugin_manager = ClaudeCodePluginManager(db_service)
        self.hook_manager = ClaudeCodeHooksManager(db_service)
        self.subagent_manager = ClaudeCodeSubagentsManager(db_service)
        self.settings_manager = ClaudeCodeSettingsManager(db_service)
        self.slash_command_manager = ClaudeCodeSlashCommandsManager(db_service)
        self.checkpointing_manager = ClaudeCodeCheckpointingManager(db_service)
        self.memory_tool_manager = ClaudeCodeMemoryToolManager(db_service)
        
        # Integration state
        self._integration_cache: Dict[str, ClaudeCodeIntegration] = {}
        self._component_cache: Dict[str, List[Any]] = {}
    
    def create_comprehensive_integration(
        self,
        output_dir: Path,
        project_id: Optional[int] = None,
        integration_name: str = "APM (Agent Project Manager) Claude Code Integration"
    ) -> ClaudeCodeIntegration:
        """
        Create comprehensive Claude Code integration for APM (Agent Project Manager).
        
        Args:
            output_dir: Directory to write integration files
            project_id: Optional project ID for project-specific components
            integration_name: Name of the integration
            
        Returns:
            Complete ClaudeCodeIntegration
        """
        # Create output directory structure
        claude_dir = output_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        
        # Create component directories
        (claude_dir / "plugins").mkdir(exist_ok=True)
        (claude_dir / "hooks").mkdir(exist_ok=True)
        (claude_dir / "subagents").mkdir(exist_ok=True)
        (claude_dir / "settings").mkdir(exist_ok=True)
        (claude_dir / "slash-commands").mkdir(exist_ok=True)
        (claude_dir / "checkpoints").mkdir(exist_ok=True)
        (claude_dir / "memory").mkdir(exist_ok=True)
        (claude_dir / "skills").mkdir(exist_ok=True)
        
        # Generate all components
        plugins = self._generate_plugins(claude_dir, project_id)
        hooks = self._generate_hooks(claude_dir, project_id)
        subagents = self._generate_subagents(claude_dir, project_id)
        settings = self._generate_settings(claude_dir, project_id)
        slash_commands = self._generate_slash_commands(claude_dir, project_id)
        checkpoints = self._generate_checkpoints(claude_dir, project_id)
        memory_tools = self._generate_memory_tools(claude_dir, project_id)
        
        # Create comprehensive integration
        integration = ClaudeCodeIntegration(
            name=integration_name,
            description="Comprehensive APM (Agent Project Manager) integration with Claude Code",
            version="1.0.0",
            plugins=plugins,
            hooks=hooks,
            subagents=subagents,
            settings=settings,
            slash_commands=slash_commands,
            checkpoints=checkpoints,
            memory_tools=memory_tools,
            dependencies=[
                "agentpm",
                "claude-code",
                "anthropic"
            ],
            requirements=[
                "python>=3.8",
                "pydantic>=2.0.0",
                "click>=8.0.0",
                "rich>=13.0.0"
            ],
            permissions=[
                "read_project_files",
                "write_claude_config",
                "execute_commands",
                "access_database"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write integration manifest
        self._write_integration_manifest(claude_dir, integration)
        
        # Cache integration
        self._integration_cache[integration_name] = integration
        
        return integration
    
    def generate_project_integration(
        self,
        project_id: int,
        output_dir: Path
    ) -> ClaudeCodeIntegration:
        """
        Generate Claude Code integration for specific project.
        
        Args:
            project_id: Project ID
            output_dir: Directory to write integration files
            
        Returns:
            Project-specific ClaudeCodeIntegration
        """
        integration_name = f"APM (Agent Project Manager) Project {project_id} Integration"
        
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
        Generate Claude Code integration for specific agent.
        
        Args:
            agent_role: Agent role name
            output_dir: Directory to write integration files
            
        Returns:
            Agent-specific ClaudeCodeIntegration
        """
        integration_name = f"APM (Agent Project Manager) {agent_role} Agent Integration"
        
        return self.create_comprehensive_integration(
            output_dir=output_dir,
            integration_name=integration_name
        )
    
    def update_integration(
        self,
        integration_name: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update existing integration.
        
        Args:
            integration_name: Name of integration to update
            updates: Updates to apply
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if integration_name not in self._integration_cache:
                return False
            
            integration = self._integration_cache[integration_name]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(integration, key):
                    setattr(integration, key, value)
            
            # Update timestamp
            integration.updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error updating integration {integration_name}: {e}")
            return False
    
    def get_integration(self, integration_name: str) -> Optional[ClaudeCodeIntegration]:
        """
        Get integration by name.
        
        Args:
            integration_name: Name of integration
            
        Returns:
            Integration if found, None otherwise
        """
        return self._integration_cache.get(integration_name)
    
    def list_integrations(self) -> List[str]:
        """
        List all cached integrations.
        
        Returns:
            List of integration names
        """
        return list(self._integration_cache.keys())
    
    def validate_integration(self, integration: ClaudeCodeIntegration) -> Dict[str, Any]:
        """
        Validate integration configuration.
        
        Args:
            integration: Integration to validate
            
        Returns:
            Validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "component_counts": {
                "plugins": len(integration.plugins),
                "hooks": len(integration.hooks),
                "subagents": len(integration.subagents),
                "settings": len(integration.settings),
                "slash_commands": len(integration.slash_commands),
                "checkpoints": len(integration.checkpoints),
                "memory_tools": len(integration.memory_tools)
            }
        }
        
        try:
            # Validate required fields
            if not integration.name:
                validation_results["errors"].append("Integration name is required")
                validation_results["valid"] = False
            
            if not integration.description:
                validation_results["warnings"].append("Integration description is missing")
            
            # Validate components
            for plugin in integration.plugins:
                if not plugin.name:
                    validation_results["errors"].append(f"Plugin name is required")
                    validation_results["valid"] = False
            
            for hook in integration.hooks:
                if not hook.name:
                    validation_results["errors"].append(f"Hook name is required")
                    validation_results["valid"] = False
            
            for subagent in integration.subagents:
                if not subagent.name:
                    validation_results["errors"].append(f"Subagent name is required")
                    validation_results["valid"] = False
            
            # Check for duplicate names
            all_names = []
            all_names.extend([p.name for p in integration.plugins])
            all_names.extend([h.name for h in integration.hooks])
            all_names.extend([s.name for s in integration.subagents])
            
            duplicate_names = [name for name in all_names if all_names.count(name) > 1]
            if duplicate_names:
                validation_results["warnings"].append(f"Duplicate component names: {duplicate_names}")
            
        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            validation_results["valid"] = False
        
        return validation_results
    
    def export_integration(
        self,
        integration: ClaudeCodeIntegration,
        output_path: Path,
        format: str = "json"
    ) -> bool:
        """
        Export integration to file.
        
        Args:
            integration: Integration to export
            output_path: Path to export file
            format: Export format (json, yaml)
            
        Returns:
            True if export successful, False otherwise
        """
        try:
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
        Import integration from file.
        
        Args:
            input_path: Path to import file
            
        Returns:
            Imported integration if successful, None otherwise
        """
        try:
            if input_path.suffix == ".json":
                data = json.loads(input_path.read_text())
            elif input_path.suffix in [".yaml", ".yml"]:
                import yaml
                data = yaml.safe_load(input_path.read_text())
            else:
                raise ValueError(f"Unsupported file format: {input_path.suffix}")
            
            integration = ClaudeCodeIntegration(**data)
            
            # Cache imported integration
            self._integration_cache[integration.name] = integration
            
            return integration
            
        except Exception as e:
            print(f"Error importing integration: {e}")
            return None
    
    def _generate_plugins(self, claude_dir: Path, project_id: Optional[int]) -> List[PluginDefinition]:
        """Generate plugin definitions."""
        try:
            return self.plugin_manager.create_aipm_plugins(claude_dir / "plugins", project_id)
        except Exception as e:
            print(f"Error generating plugins: {e}")
            return []
    
    def _generate_hooks(self, claude_dir: Path, project_id: Optional[int]) -> List[HookDefinition]:
        """Generate hook definitions."""
        try:
            return self.hook_manager.create_aipm_hooks(claude_dir / "hooks", project_id)
        except Exception as e:
            print(f"Error generating hooks: {e}")
            return []
    
    def _generate_subagents(self, claude_dir: Path, project_id: Optional[int]) -> List[SubagentDefinition]:
        """Generate subagent definitions."""
        try:
            return self.subagent_manager.create_aipm_subagents(claude_dir / "subagents", project_id)
        except Exception as e:
            print(f"Error generating subagents: {e}")
            return []
    
    def _generate_settings(self, claude_dir: Path, project_id: Optional[int]) -> List[SettingsDefinition]:
        """Generate settings definitions."""
        try:
            return self.settings_manager.create_aipm_settings(claude_dir / "settings", project_id)
        except Exception as e:
            print(f"Error generating settings: {e}")
            return []
    
    def _generate_slash_commands(self, claude_dir: Path, project_id: Optional[int]) -> List[SlashCommandDefinition]:
        """Generate slash command definitions."""
        try:
            return self.slash_command_manager.create_aipm_slash_commands(claude_dir / "slash-commands", project_id)
        except Exception as e:
            print(f"Error generating slash commands: {e}")
            return []
    
    def _generate_checkpoints(self, claude_dir: Path, project_id: Optional[int]) -> List[CheckpointDefinition]:
        """Generate checkpoint definitions."""
        try:
            return self.checkpointing_manager.create_aipm_checkpoints(claude_dir, project_id)
        except Exception as e:
            print(f"Error generating checkpoints: {e}")
            return []
    
    def _generate_memory_tools(self, claude_dir: Path, project_id: Optional[int]) -> List[MemoryToolDefinition]:
        """Generate memory tool definitions."""
        try:
            return self.memory_tool_manager.create_aipm_memory_configs(claude_dir, project_id)
        except Exception as e:
            print(f"Error generating memory tools: {e}")
            return []
    
    def _write_integration_manifest(self, claude_dir: Path, integration: ClaudeCodeIntegration) -> None:
        """Write integration manifest file."""
        try:
            manifest = {
                "name": integration.name,
                "description": integration.description,
                "version": integration.version,
                "created_at": integration.created_at.isoformat() if integration.created_at else None,
                "updated_at": integration.updated_at.isoformat() if integration.updated_at else None,
                "components": {
                    "plugins": len(integration.plugins),
                    "hooks": len(integration.hooks),
                    "subagents": len(integration.subagents),
                    "settings": len(integration.settings),
                    "slash_commands": len(integration.slash_commands),
                    "checkpoints": len(integration.checkpoints),
                    "memory_tools": len(integration.memory_tools)
                },
                "dependencies": integration.dependencies,
                "requirements": integration.requirements,
                "permissions": integration.permissions
            }
            
            manifest_file = claude_dir / "integration.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
        except Exception as e:
            print(f"Error writing integration manifest: {e}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """
        Get integration statistics.
        
        Returns:
            Dictionary with integration statistics
        """
        try:
            total_components = 0
            component_breakdown = {}
            
            for integration in self._integration_cache.values():
                total_components += (
                    len(integration.plugins) +
                    len(integration.hooks) +
                    len(integration.subagents) +
                    len(integration.settings) +
                    len(integration.slash_commands) +
                    len(integration.checkpoints) +
                    len(integration.memory_tools)
                )
                
                component_breakdown[integration.name] = {
                    "plugins": len(integration.plugins),
                    "hooks": len(integration.hooks),
                    "subagents": len(integration.subagents),
                    "settings": len(integration.settings),
                    "slash_commands": len(integration.slash_commands),
                    "checkpoints": len(integration.checkpoints),
                    "memory_tools": len(integration.memory_tools)
                }
            
            return {
                "total_integrations": len(self._integration_cache),
                "total_components": total_components,
                "component_breakdown": component_breakdown,
                "cache_size": len(self._component_cache)
            }
            
        except Exception as e:
            print(f"Error getting integration stats: {e}")
            return {}
    
    def cleanup_integration_cache(self) -> int:
        """
        Cleanup integration cache.
        
        Returns:
            Number of integrations cleaned up
        """
        try:
            cleaned_count = len(self._integration_cache)
            self._integration_cache.clear()
            self._component_cache.clear()
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up integration cache: {e}")
            return 0
