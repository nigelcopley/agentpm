"""
Claude Code Settings System

Manages Claude Code settings for APM (Agent Project Manager) integration including configuration
management, project settings, and user preferences.

Based on: https://docs.claude.com/en/docs/claude-code/settings
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from ..models import SettingsDefinition, SettingDefinition, SettingType, ClaudeCodeComponentType


class ClaudeCodeSettingsManager:
    """
    Manages Claude Code settings for APM (Agent Project Manager).
    
    Creates and manages settings configurations for APM (Agent Project Manager) integration
    with Claude Code.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize settings manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._settings_cache: Dict[str, SettingsDefinition] = {}
        self._active_settings: Dict[str, Any] = {}
    
    def create_aipm_settings(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> SettingsDefinition:
        """
        Create comprehensive APM (Agent Project Manager) settings for Claude Code.
        
        Args:
            output_dir: Directory to write settings configuration
            project_id: Optional project ID for project-specific settings
            
        Returns:
            SettingsDefinition for APM (Agent Project Manager) settings
        """
        # Create settings directory
        settings_dir = output_dir / ".claude"
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Create APM (Agent Project Manager) settings
        settings = SettingsDefinition(
            name="APM (Agent Project Manager) Settings",
            description="APM (Agent Project Manager) settings configuration for Claude Code integration",
            component_type=ClaudeCodeComponentType.SETTING,
            scope="project" if project_id else "user",
            settings=[
                # Core APM (Agent Project Manager) settings
                SettingDefinition(
                    key="aipm.project_id",
                    name="Project ID",
                    description="APM (Agent Project Manager) project ID for context",
                    setting_type=SettingType.INTEGER,
                    default_value=project_id,
                    required=bool(project_id),
                    category="core"
                ),
                SettingDefinition(
                    key="aipm.database_path",
                    name="Database Path",
                    description="Path to APM (Agent Project Manager) database",
                    setting_type=SettingType.STRING,
                    default_value="./agentpm.db",
                    required=True,
                    category="core"
                ),
                SettingDefinition(
                    key="aipm.context_quality_threshold",
                    name="Context Quality Threshold",
                    description="Minimum context quality score (0.0-1.0)",
                    setting_type=SettingType.FLOAT,
                    default_value=0.8,
                    validation_rules={"min": 0.0, "max": 1.0},
                    category="context"
                ),
                SettingDefinition(
                    key="aipm.auto_context_refresh",
                    name="Auto Context Refresh",
                    description="Automatically refresh context when stale",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="context"
                ),
                SettingDefinition(
                    key="aipm.quality_gates_enabled",
                    name="Quality Gates Enabled",
                    description="Enable APM (Agent Project Manager) quality gates enforcement",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="quality"
                ),
                SettingDefinition(
                    key="aipm.timeboxing_enabled",
                    name="Time-boxing Enabled",
                    description="Enable APM (Agent Project Manager) time-boxing enforcement",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="quality"
                ),
                SettingDefinition(
                    key="aipm.auto_learning_capture",
                    name="Auto Learning Capture",
                    description="Automatically capture learnings and decisions",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="learning"
                ),
                SettingDefinition(
                    key="aipm.agent_specialization",
                    name="Agent Specialization",
                    description="Enable APM (Agent Project Manager) agent specialization",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="agents"
                ),
                SettingDefinition(
                    key="aipm.workflow_automation",
                    name="Workflow Automation",
                    description="Enable APM (Agent Project Manager) workflow automation",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="workflow"
                ),
                SettingDefinition(
                    key="aipm.plugin_integration",
                    name="Plugin Integration",
                    description="Enable APM (Agent Project Manager) plugin integration",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="plugins"
                ),
                SettingDefinition(
                    key="aipm.hooks_enabled",
                    name="Hooks Enabled",
                    description="Enable APM (Agent Project Manager) hooks system",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="hooks"
                ),
                SettingDefinition(
                    key="aipm.subagents_enabled",
                    name="Subagents Enabled",
                    description="Enable APM (Agent Project Manager) subagents system",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="subagents"
                ),
                SettingDefinition(
                    key="aipm.checkpointing_enabled",
                    name="Checkpointing Enabled",
                    description="Enable APM (Agent Project Manager) checkpointing system",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="checkpointing"
                ),
                SettingDefinition(
                    key="aipm.memory_tools_enabled",
                    name="Memory Tools Enabled",
                    description="Enable APM (Agent Project Manager) memory tools",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="memory"
                ),
                SettingDefinition(
                    key="aipm.verbose_logging",
                    name="Verbose Logging",
                    description="Enable verbose logging for APM (Agent Project Manager)",
                    setting_type=SettingType.BOOLEAN,
                    default_value=False,
                    category="logging"
                ),
                SettingDefinition(
                    key="aipm.debug_mode",
                    name="Debug Mode",
                    description="Enable debug mode for APM (Agent Project Manager)",
                    setting_type=SettingType.BOOLEAN,
                    default_value=False,
                    category="logging"
                ),
                SettingDefinition(
                    key="aipm.performance_monitoring",
                    name="Performance Monitoring",
                    description="Enable performance monitoring",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="performance"
                ),
                SettingDefinition(
                    key="aipm.security_validation",
                    name="Security Validation",
                    description="Enable security validation for inputs and outputs",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="security"
                ),
                SettingDefinition(
                    key="aipm.backup_enabled",
                    name="Backup Enabled",
                    description="Enable automatic backups",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="backup"
                ),
                SettingDefinition(
                    key="aipm.backup_interval",
                    name="Backup Interval",
                    description="Backup interval in hours",
                    setting_type=SettingType.INTEGER,
                    default_value=24,
                    validation_rules={"min": 1, "max": 168},
                    category="backup"
                )
            ],
            categories=["core", "context", "quality", "learning", "agents", "workflow", "plugins", "hooks", "subagents", "checkpointing", "memory", "logging", "performance", "security", "backup"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write settings configuration
        self._write_settings_configuration(settings_dir, settings)
        
        # Cache settings
        self._settings_cache["aipm-v2"] = settings
        
        return settings
    
    def create_project_settings(
        self,
        project_id: int,
        project_info: Dict[str, Any],
        output_dir: Path
    ) -> SettingsDefinition:
        """
        Create project-specific settings for Claude Code.
        
        Args:
            project_id: Project ID
            project_info: Project information
            output_dir: Directory to write settings
            
        Returns:
            SettingsDefinition for project settings
        """
        # Create project settings directory
        project_settings_dir = output_dir / ".claude" / "projects" / str(project_id)
        project_settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project-specific settings
        project_settings = SettingsDefinition(
            name=f"APM (Agent Project Manager) Project {project_id} Settings",
            description=f"APM (Agent Project Manager) project {project_id} specific settings",
            component_type=ClaudeCodeComponentType.SETTING,
            scope="project",
            settings=[
                SettingDefinition(
                    key=f"aipm.project_{project_id}.name",
                    name="Project Name",
                    description=f"Name of project {project_id}",
                    setting_type=SettingType.STRING,
                    default_value=project_info.get("name", f"Project {project_id}"),
                    required=True,
                    category="project"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.description",
                    name="Project Description",
                    description=f"Description of project {project_id}",
                    setting_type=SettingType.STRING,
                    default_value=project_info.get("description", ""),
                    category="project"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.tech_stack",
                    name="Tech Stack",
                    description=f"Technology stack for project {project_id}",
                    setting_type=SettingType.ARRAY,
                    default_value=project_info.get("tech_stack", []),
                    category="project"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.frameworks",
                    name="Frameworks",
                    description=f"Frameworks used in project {project_id}",
                    setting_type=SettingType.ARRAY,
                    default_value=project_info.get("frameworks", []),
                    category="project"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.quality_standards",
                    name="Quality Standards",
                    description=f"Quality standards for project {project_id}",
                    setting_type=SettingType.OBJECT,
                    default_value=project_info.get("quality_standards", {}),
                    category="quality"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.workflow_preferences",
                    name="Workflow Preferences",
                    description=f"Workflow preferences for project {project_id}",
                    setting_type=SettingType.OBJECT,
                    default_value=project_info.get("workflow_preferences", {}),
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.project_{project_id}.agent_preferences",
                    name="Agent Preferences",
                    description=f"Agent preferences for project {project_id}",
                    setting_type=SettingType.OBJECT,
                    default_value=project_info.get("agent_preferences", {}),
                    category="agents"
                )
            ],
            categories=["project", "quality", "workflow", "agents"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write project settings configuration
        self._write_settings_configuration(project_settings_dir, project_settings)
        
        # Cache project settings
        self._settings_cache[f"project-{project_id}"] = project_settings
        
        return project_settings
    
    def create_agent_settings(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        output_dir: Path
    ) -> SettingsDefinition:
        """
        Create agent-specific settings for Claude Code.
        
        Args:
            agent_role: Agent role name
            agent_capabilities: List of agent capabilities
            output_dir: Directory to write settings
            
        Returns:
            SettingsDefinition for agent settings
        """
        # Create agent settings directory
        agent_settings_dir = output_dir / ".claude" / "agents" / agent_role
        agent_settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent-specific settings
        agent_settings = SettingsDefinition(
            name=f"APM (Agent Project Manager) {agent_role} Agent Settings",
            description=f"APM (Agent Project Manager) {agent_role} agent specific settings",
            component_type=ClaudeCodeComponentType.SETTING,
            scope="user",
            settings=[
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.enabled",
                    name="Agent Enabled",
                    description=f"Enable {agent_role} agent",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.auto_invoke",
                    name="Auto Invoke",
                    description=f"Automatically invoke {agent_role} agent",
                    setting_type=SettingType.BOOLEAN,
                    default_value=False,
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.priority",
                    name="Priority",
                    description=f"Priority for {agent_role} agent (0-100)",
                    setting_type=SettingType.INTEGER,
                    default_value=50,
                    validation_rules={"min": 0, "max": 100},
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.max_concurrent",
                    name="Max Concurrent",
                    description=f"Maximum concurrent tasks for {agent_role} agent",
                    setting_type=SettingType.INTEGER,
                    default_value=1,
                    validation_rules={"min": 1, "max": 10},
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.capabilities",
                    name="Capabilities",
                    description=f"Capabilities for {agent_role} agent",
                    setting_type=SettingType.ARRAY,
                    default_value=agent_capabilities,
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.tools",
                    name="Tools",
                    description=f"Available tools for {agent_role} agent",
                    setting_type=SettingType.ARRAY,
                    default_value=["Read", "Write", "Bash", "Grep", "Glob"],
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.timeout",
                    name="Timeout",
                    description=f"Timeout for {agent_role} agent tasks (seconds)",
                    setting_type=SettingType.INTEGER,
                    default_value=300,
                    validation_rules={"min": 30, "max": 3600},
                    category="agent"
                ),
                SettingDefinition(
                    key=f"aipm.agent.{agent_role}.retry_count",
                    name="Retry Count",
                    description=f"Number of retries for {agent_role} agent",
                    setting_type=SettingType.INTEGER,
                    default_value=3,
                    validation_rules={"min": 0, "max": 10},
                    category="agent"
                )
            ],
            categories=["agent"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write agent settings configuration
        self._write_settings_configuration(agent_settings_dir, agent_settings)
        
        # Cache agent settings
        self._settings_cache[f"agent-{agent_role}"] = agent_settings
        
        return agent_settings
    
    def create_workflow_settings(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        output_dir: Path
    ) -> SettingsDefinition:
        """
        Create workflow-specific settings for Claude Code.
        
        Args:
            workflow_name: Workflow name
            workflow_info: Workflow information
            output_dir: Directory to write settings
            
        Returns:
            SettingsDefinition for workflow settings
        """
        # Create workflow settings directory
        workflow_settings_dir = output_dir / ".claude" / "workflows" / workflow_name
        workflow_settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow-specific settings
        workflow_settings = SettingsDefinition(
            name=f"APM (Agent Project Manager) {workflow_name} Workflow Settings",
            description=f"APM (Agent Project Manager) {workflow_name} workflow specific settings",
            component_type=ClaudeCodeComponentType.SETTING,
            scope="project",
            settings=[
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.enabled",
                    name="Workflow Enabled",
                    description=f"Enable {workflow_name} workflow",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.auto_validation",
                    name="Auto Validation",
                    description=f"Automatically validate {workflow_name} workflow",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.required_tasks",
                    name="Required Tasks",
                    description=f"Required tasks for {workflow_name} workflow",
                    setting_type=SettingType.ARRAY,
                    default_value=workflow_info.get("required_tasks", []),
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.time_limits",
                    name="Time Limits",
                    description=f"Time limits for {workflow_name} workflow",
                    setting_type=SettingType.OBJECT,
                    default_value=workflow_info.get("time_limits", {}),
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.quality_gates",
                    name="Quality Gates",
                    description=f"Quality gates for {workflow_name} workflow",
                    setting_type=SettingType.OBJECT,
                    default_value=workflow_info.get("quality_gates", {}),
                    category="workflow"
                ),
                SettingDefinition(
                    key=f"aipm.workflow.{workflow_name}.automation_enabled",
                    name="Automation Enabled",
                    description=f"Enable automation for {workflow_name} workflow",
                    setting_type=SettingType.BOOLEAN,
                    default_value=True,
                    category="workflow"
                )
            ],
            categories=["workflow"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write workflow settings configuration
        self._write_settings_configuration(workflow_settings_dir, workflow_settings)
        
        # Cache workflow settings
        self._settings_cache[f"workflow-{workflow_name}"] = workflow_settings
        
        return workflow_settings
    
    def _write_settings_configuration(self, settings_dir: Path, settings: SettingsDefinition) -> None:
        """Write settings configuration to filesystem."""
        # Create settings.json configuration
        settings_config = {
            "name": settings.name,
            "description": settings.description,
            "version": settings.version,
            "author": settings.author,
            "scope": settings.scope,
            "settings": {}
        }
        
        # Convert settings to configuration format
        for setting in settings.settings:
            setting_config = {
                "name": setting.name,
                "description": setting.description,
                "type": setting.setting_type.value,
                "default": setting.default_value,
                "required": setting.required,
                "validation": setting.validation_rules,
                "category": setting.category
            }
            settings_config["settings"][setting.key] = setting_config
        
        # Write settings.json
        settings_file = settings_dir / "settings.json"
        settings_file.write_text(json.dumps(settings_config, indent=2))
        
        # Write individual setting definitions
        for setting in settings.settings:
            setting_file = settings_dir / f"{setting.key.replace('.', '_')}.json"
            setting_file.write_text(json.dumps(setting.model_dump(), indent=2))
    
    def get_setting_value(self, key: str, default: Any = None) -> Any:
        """
        Get setting value by key.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        return self._active_settings.get(key, default)
    
    def set_setting_value(self, key: str, value: Any) -> None:
        """
        Set setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._active_settings[key] = value
    
    def load_settings_from_file(self, settings_file: Path) -> bool:
        """
        Load settings from file.
        
        Args:
            settings_file: Path to settings file
            
        Returns:
            True if settings loaded successfully, False otherwise
        """
        try:
            if settings_file.exists():
                settings_data = json.loads(settings_file.read_text())
                if "settings" in settings_data:
                    for key, setting_config in settings_data["settings"].items():
                        if "default" in setting_config:
                            self._active_settings[key] = setting_config["default"]
                return True
        except Exception as e:
            print(f"Error loading settings from {settings_file}: {e}")
        return False
    
    def save_settings_to_file(self, settings_file: Path) -> bool:
        """
        Save settings to file.
        
        Args:
            settings_file: Path to settings file
            
        Returns:
            True if settings saved successfully, False otherwise
        """
        try:
            settings_data = {
                "settings": self._active_settings,
                "timestamp": datetime.now().isoformat()
            }
            settings_file.write_text(json.dumps(settings_data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving settings to {settings_file}: {e}")
            return False
    
    def validate_setting(self, key: str, value: Any) -> bool:
        """
        Validate setting value.
        
        Args:
            key: Setting key
            value: Setting value to validate
            
        Returns:
            True if value is valid, False otherwise
        """
        # Find setting definition
        for settings_def in self._settings_cache.values():
            for setting in settings_def.settings:
                if setting.key == key:
                    return self._validate_setting_value(setting, value)
        return True  # Unknown setting, assume valid
    
    def _validate_setting_value(self, setting: SettingDefinition, value: Any) -> bool:
        """Validate setting value against definition."""
        try:
            # Type validation
            if setting.setting_type == SettingType.BOOLEAN:
                return isinstance(value, bool)
            elif setting.setting_type == SettingType.INTEGER:
                return isinstance(value, int)
            elif setting.setting_type == SettingType.FLOAT:
                return isinstance(value, (int, float))
            elif setting.setting_type == SettingType.STRING:
                return isinstance(value, str)
            elif setting.setting_type == SettingType.ARRAY:
                return isinstance(value, list)
            elif setting.setting_type == SettingType.OBJECT:
                return isinstance(value, dict)
            
            # Custom validation rules
            if setting.validation_rules:
                if "min" in setting.validation_rules and value < setting.validation_rules["min"]:
                    return False
                if "max" in setting.validation_rules and value > setting.validation_rules["max"]:
                    return False
            
            return True
        except Exception:
            return False
