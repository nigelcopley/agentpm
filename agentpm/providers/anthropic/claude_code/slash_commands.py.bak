"""
Claude Code Slash Commands System

Manages Claude Code slash commands for APM (Agent Project Manager) integration including
command creation, execution, and management.

Based on: https://docs.claude.com/en/docs/claude-code/slash-commands
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from .models import SlashCommandDefinition, ClaudeCodeComponentType


class ClaudeCodeSlashCommandsManager:
    """
    Manages Claude Code slash commands for APM (Agent Project Manager).
    
    Creates and manages slash commands that provide APM (Agent Project Manager) functionality
    directly in Claude Code.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize slash commands manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._commands_cache: Dict[str, SlashCommandDefinition] = {}
        self._active_commands: Dict[str, bool] = {}
    
    def create_aipm_commands(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[SlashCommandDefinition]:
        """
        Create comprehensive APM (Agent Project Manager) slash commands for Claude Code.
        
        Args:
            output_dir: Directory to write command definitions
            project_id: Optional project ID for project-specific commands
            
        Returns:
            List of created SlashCommandDefinitions
        """
        commands = []
        
        # Create commands directory
        commands_dir = output_dir / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create core APM (Agent Project Manager) commands
        commands.extend(self._create_core_commands(commands_dir))
        commands.extend(self._create_work_item_commands(commands_dir))
        commands.extend(self._create_task_commands(commands_dir))
        commands.extend(self._create_context_commands(commands_dir))
        commands.extend(self._create_learning_commands(commands_dir))
        commands.extend(self._create_agent_commands(commands_dir))
        commands.extend(self._create_workflow_commands(commands_dir))
        
        # Create project-specific commands if project_id provided
        if project_id:
            commands.extend(self._create_project_commands(commands_dir, project_id))
        
        return commands
    
    def create_agent_commands(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        output_dir: Path
    ) -> List[SlashCommandDefinition]:
        """
        Create slash commands for specific APM (Agent Project Manager) agent.
        
        Args:
            agent_role: Agent role name
            agent_capabilities: List of agent capabilities
            output_dir: Directory to write commands
            
        Returns:
            List of created SlashCommandDefinitions
        """
        commands = []
        
        # Create agent commands directory
        agent_commands_dir = output_dir / "commands" / "agents" / agent_role
        agent_commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent-specific commands
        commands.extend(self._create_agent_workflow_commands(agent_role, agent_capabilities, agent_commands_dir))
        commands.extend(self._create_agent_capability_commands(agent_role, agent_capabilities, agent_commands_dir))
        
        return commands
    
    def create_workflow_commands(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        output_dir: Path
    ) -> List[SlashCommandDefinition]:
        """
        Create slash commands for specific APM (Agent Project Manager) workflow.
        
        Args:
            workflow_name: Workflow name
            workflow_info: Workflow information
            output_dir: Directory to write commands
            
        Returns:
            List of created SlashCommandDefinitions
        """
        commands = []
        
        # Create workflow commands directory
        workflow_commands_dir = output_dir / "commands" / "workflows" / workflow_name
        workflow_commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow-specific commands
        commands.extend(self._create_workflow_execution_commands(workflow_name, workflow_info, workflow_commands_dir))
        commands.extend(self._create_workflow_validation_commands(workflow_name, workflow_info, workflow_commands_dir))
        
        return commands
    
    def _create_core_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create core APM (Agent Project Manager) commands."""
        commands = []
        
        # Status command
        status_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Status",
            description="Show APM (Agent Project Manager) project status and health dashboard",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-status",
            parameters=[
                {
                    "name": "project_id",
                    "type": "integer",
                    "description": "Project ID (optional)",
                    "required": False
                }
            ],
            examples=[
                "/aipm-status",
                "/aipm-status 123"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="core",
            keywords=["status", "dashboard", "health", "aipm"]
        )
        
        command_file = commands_dir / "aipm-status.md"
        command_content = self._create_status_command_content(status_command)
        command_file.write_text(command_content)
        commands.append(status_command)
        
        # Context command
        context_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Context",
            description="Get hierarchical project context for AI agents",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-context",
            parameters=[
                {
                    "name": "task_id",
                    "type": "integer",
                    "description": "Task ID for context",
                    "required": False
                },
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID for context",
                    "required": False
                },
                {
                    "name": "agent",
                    "type": "string",
                    "description": "Agent specialization for context",
                    "required": False
                }
            ],
            examples=[
                "/aipm-context",
                "/aipm-context --task-id=123",
                "/aipm-context --work-item-id=456",
                "/aipm-context --agent=rapid-prototyper"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=60,
            category="context",
            keywords=["context", "hierarchical", "agent", "aipm"]
        )
        
        command_file = commands_dir / "aipm-context.md"
        command_content = self._create_context_command_content(context_command)
        command_file.write_text(command_content)
        commands.append(context_command)
        
        # Learnings command
        learnings_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Learnings",
            description="Record and manage learnings, decisions, and patterns",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-learnings",
            parameters=[
                {
                    "name": "type",
                    "type": "string",
                    "description": "Learning type (decision, pattern, learning, discovery)",
                    "required": True
                },
                {
                    "name": "content",
                    "type": "string",
                    "description": "Learning content",
                    "required": True
                },
                {
                    "name": "evidence",
                    "type": "string",
                    "description": "Supporting evidence",
                    "required": False
                },
                {
                    "name": "business_value",
                    "type": "string",
                    "description": "Business value and impact",
                    "required": False
                },
                {
                    "name": "confidence",
                    "type": "float",
                    "description": "Confidence score (0.0-1.0)",
                    "required": False
                }
            ],
            examples=[
                "/aipm-learnings --type=decision --content=\"Use Django for backend\" --evidence=\"Team expertise\"",
                "/aipm-learnings --type=pattern --content=\"Database service pattern\" --when-to-use=\"For new services\"",
                "/aipm-learnings --type=learning --content=\"Key insights from implementation\""
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="learning",
            keywords=["learnings", "decisions", "patterns", "evidence", "aipm"]
        )
        
        command_file = commands_dir / "aipm-learnings.md"
        command_content = self._create_learnings_command_content(learnings_command)
        command_file.write_text(command_content)
        commands.append(learnings_command)
        
        return commands
    
    def _create_work_item_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create work item management commands."""
        commands = []
        
        # Work item list command
        work_item_list_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Work Item List",
            description="List APM (Agent Project Manager) work items with status and details",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-work-items",
            parameters=[
                {
                    "name": "type",
                    "type": "string",
                    "description": "Work item type filter (feature, bugfix, enhancement, research)",
                    "required": False
                },
                {
                    "name": "status",
                    "type": "string",
                    "description": "Status filter (proposed, validated, accepted, in_progress, review, completed)",
                    "required": False
                },
                {
                    "name": "search",
                    "type": "string",
                    "description": "Search term for work item names",
                    "required": False
                }
            ],
            examples=[
                "/aipm-work-items",
                "/aipm-work-items --type=feature",
                "/aipm-work-items --status=in_progress",
                "/aipm-work-items --search=authentication"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="work-items",
            keywords=["work-items", "list", "filter", "aipm"]
        )
        
        command_file = commands_dir / "aipm-work-items.md"
        command_content = self._create_work_item_list_command_content(work_item_list_command)
        command_file.write_text(command_content)
        commands.append(work_item_list_command)
        
        # Work item create command
        work_item_create_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Work Item Create",
            description="Create new APM (Agent Project Manager) work item with proper structure",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-work-item-create",
            parameters=[
                {
                    "name": "name",
                    "type": "string",
                    "description": "Work item name",
                    "required": True
                },
                {
                    "name": "type",
                    "type": "string",
                    "description": "Work item type (feature, bugfix, enhancement, research)",
                    "required": True
                },
                {
                    "name": "description",
                    "type": "string",
                    "description": "Work item description",
                    "required": False
                },
                {
                    "name": "priority",
                    "type": "string",
                    "description": "Priority (P1, P2, P3, P4)",
                    "required": False
                }
            ],
            examples=[
                "/aipm-work-item-create --name=\"User Authentication\" --type=feature",
                "/aipm-work-item-create --name=\"Fix Login Bug\" --type=bugfix --priority=P1",
                "/aipm-work-item-create --name=\"Performance Optimization\" --type=enhancement"
            ],
            enabled=True,
            requires_confirmation=True,
            timeout=30,
            category="work-items",
            keywords=["work-item", "create", "feature", "bugfix", "aipm"]
        )
        
        command_file = commands_dir / "aipm-work-item-create.md"
        command_content = self._create_work_item_create_command_content(work_item_create_command)
        command_file.write_text(command_content)
        commands.append(work_item_create_command)
        
        return commands
    
    def _create_task_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create task management commands."""
        commands = []
        
        # Task list command
        task_list_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Task List",
            description="List APM (Agent Project Manager) tasks with status and time-boxing",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-tasks",
            parameters=[
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID filter",
                    "required": False
                },
                {
                    "name": "type",
                    "type": "string",
                    "description": "Task type filter (design, implementation, testing, documentation, analysis, bugfix)",
                    "required": False
                },
                {
                    "name": "status",
                    "type": "string",
                    "description": "Status filter (pending, in_progress, completed, blocked)",
                    "required": False
                }
            ],
            examples=[
                "/aipm-tasks",
                "/aipm-tasks --work-item-id=123",
                "/aipm-tasks --type=implementation",
                "/aipm-tasks --status=in_progress"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="tasks",
            keywords=["tasks", "list", "time-boxing", "aipm"]
        )
        
        command_file = commands_dir / "aipm-tasks.md"
        command_content = self._create_task_list_command_content(task_list_command)
        command_file.write_text(command_content)
        commands.append(task_list_command)
        
        # Task create command
        task_create_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Task Create",
            description="Create new APM (Agent Project Manager) task with time-boxing validation",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-task-create",
            parameters=[
                {
                    "name": "name",
                    "type": "string",
                    "description": "Task name",
                    "required": True
                },
                {
                    "name": "type",
                    "type": "string",
                    "description": "Task type (design, implementation, testing, documentation, analysis, bugfix)",
                    "required": True
                },
                {
                    "name": "effort",
                    "type": "integer",
                    "description": "Effort in hours",
                    "required": True
                },
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Parent work item ID",
                    "required": True
                }
            ],
            examples=[
                "/aipm-task-create --name=\"Design Authentication\" --type=design --effort=6 --work-item-id=123",
                "/aipm-task-create --name=\"Implement Authentication\" --type=implementation --effort=4 --work-item-id=123",
                "/aipm-task-create --name=\"Test Authentication\" --type=testing --effort=4 --work-item-id=123"
            ],
            enabled=True,
            requires_confirmation=True,
            timeout=30,
            category="tasks",
            keywords=["task", "create", "time-boxing", "aipm"]
        )
        
        command_file = commands_dir / "aipm-task-create.md"
        command_content = self._create_task_create_command_content(task_create_command)
        command_file.write_text(command_content)
        commands.append(task_create_command)
        
        return commands
    
    def _create_context_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create context management commands."""
        commands = []
        
        # Context refresh command
        context_refresh_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Context Refresh",
            description="Refresh APM (Agent Project Manager) context for current session",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-context-refresh",
            parameters=[
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID to refresh context for",
                    "required": False
                },
                {
                    "name": "force",
                    "type": "boolean",
                    "description": "Force refresh even if context is fresh",
                    "required": False
                }
            ],
            examples=[
                "/aipm-context-refresh",
                "/aipm-context-refresh --work-item-id=123",
                "/aipm-context-refresh --force"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=60,
            category="context",
            keywords=["context", "refresh", "session", "aipm"]
        )
        
        command_file = commands_dir / "aipm-context-refresh.md"
        command_content = self._create_context_refresh_command_content(context_refresh_command)
        command_file.write_text(command_content)
        commands.append(context_refresh_command)
        
        return commands
    
    def _create_learning_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create learning management commands."""
        commands = []
        
        # Learning list command
        learning_list_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Learning List",
            description="List APM (Agent Project Manager) learnings, decisions, and patterns",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-learning-list",
            parameters=[
                {
                    "name": "type",
                    "type": "string",
                    "description": "Learning type filter (decision, pattern, learning, discovery)",
                    "required": False
                },
                {
                    "name": "recent",
                    "type": "boolean",
                    "description": "Show only recent learnings",
                    "required": False
                },
                {
                    "name": "search",
                    "type": "string",
                    "description": "Search term for learning content",
                    "required": False
                }
            ],
            examples=[
                "/aipm-learning-list",
                "/aipm-learning-list --type=decision",
                "/aipm-learning-list --recent",
                "/aipm-learning-list --search=django"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="learning",
            keywords=["learnings", "list", "decisions", "patterns", "aipm"]
        )
        
        command_file = commands_dir / "aipm-learning-list.md"
        command_content = self._create_learning_list_command_content(learning_list_command)
        command_file.write_text(command_content)
        commands.append(learning_list_command)
        
        return commands
    
    def _create_agent_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create agent management commands."""
        commands = []
        
        # Agent list command
        agent_list_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Agent List",
            description="List APM (Agent Project Manager) agents with capabilities and status",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-agents",
            parameters=[
                {
                    "name": "tier",
                    "type": "string",
                    "description": "Agent tier filter (orchestrator, specialist, sub-agent)",
                    "required": False
                },
                {
                    "name": "capability",
                    "type": "string",
                    "description": "Capability filter",
                    "required": False
                },
                {
                    "name": "active",
                    "type": "boolean",
                    "description": "Show only active agents",
                    "required": False
                }
            ],
            examples=[
                "/aipm-agents",
                "/aipm-agents --tier=specialist",
                "/aipm-agents --capability=python",
                "/aipm-agents --active"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="agents",
            keywords=["agents", "list", "capabilities", "aipm"]
        )
        
        command_file = commands_dir / "aipm-agents.md"
        command_content = self._create_agent_list_command_content(agent_list_command)
        command_file.write_text(command_content)
        commands.append(agent_list_command)
        
        return commands
    
    def _create_workflow_commands(self, commands_dir: Path) -> List[SlashCommandDefinition]:
        """Create workflow management commands."""
        commands = []
        
        # Workflow validate command
        workflow_validate_command = SlashCommandDefinition(
            name="APM (Agent Project Manager) Workflow Validate",
            description="Validate APM (Agent Project Manager) workflow compliance and quality gates",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command="/aipm-workflow-validate",
            parameters=[
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID to validate",
                    "required": True
                },
                {
                    "name": "strict",
                    "type": "boolean",
                    "description": "Use strict validation mode",
                    "required": False
                }
            ],
            examples=[
                "/aipm-workflow-validate --work-item-id=123",
                "/aipm-workflow-validate --work-item-id=123 --strict"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="workflow",
            keywords=["workflow", "validate", "quality-gates", "aipm"]
        )
        
        command_file = commands_dir / "aipm-workflow-validate.md"
        command_content = self._create_workflow_validate_command_content(workflow_validate_command)
        command_file.write_text(command_content)
        commands.append(workflow_validate_command)
        
        return commands
    
    def _create_project_commands(self, commands_dir: Path, project_id: int) -> List[SlashCommandDefinition]:
        """Create project-specific commands."""
        commands = []
        
        # Project status command
        project_status_command = SlashCommandDefinition(
            name=f"APM (Agent Project Manager) Project {project_id} Status",
            description=f"Show status for APM (Agent Project Manager) project {project_id}",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command=f"/aipm-project-{project_id}-status",
            parameters=[],
            examples=[
                f"/aipm-project-{project_id}-status"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="project",
            keywords=[f"project-{project_id}", "status", "aipm"]
        )
        
        command_file = commands_dir / f"aipm-project-{project_id}-status.md"
        command_content = self._create_project_status_command_content(project_status_command, project_id)
        command_file.write_text(command_content)
        commands.append(project_status_command)
        
        return commands
    
    def _create_agent_workflow_commands(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        commands_dir: Path
    ) -> List[SlashCommandDefinition]:
        """Create agent-specific workflow commands."""
        commands = []
        
        # Agent invoke command
        agent_invoke_command = SlashCommandDefinition(
            name=f"APM (Agent Project Manager) {agent_role} Invoke",
            description=f"Invoke APM (Agent Project Manager) {agent_role} agent for specialized tasks",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command=f"/aipm-{agent_role}-invoke",
            parameters=[
                {
                    "name": "task",
                    "type": "string",
                    "description": "Task description for agent",
                    "required": True
                },
                {
                    "name": "context",
                    "type": "string",
                    "description": "Additional context for agent",
                    "required": False
                }
            ],
            examples=[
                f"/aipm-{agent_role}-invoke --task=\"Implement user authentication\"",
                f"/aipm-{agent_role}-invoke --task=\"Review code quality\" --context=\"Python Django project\""
            ],
            enabled=True,
            requires_confirmation=True,
            timeout=300,
            category="agent",
            keywords=[agent_role, "invoke", "agent", "aipm"]
        )
        
        command_file = commands_dir / f"aipm-{agent_role}-invoke.md"
        command_content = self._create_agent_invoke_command_content(agent_invoke_command, agent_role, agent_capabilities)
        command_file.write_text(command_content)
        commands.append(agent_invoke_command)
        
        return commands
    
    def _create_agent_capability_commands(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        commands_dir: Path
    ) -> List[SlashCommandDefinition]:
        """Create agent capability-specific commands."""
        commands = []
        
        for capability in agent_capabilities:
            capability_command = SlashCommandDefinition(
                name=f"APM (Agent Project Manager) {agent_role} {capability}",
                description=f"Use APM (Agent Project Manager) {agent_role} {capability} capability",
                component_type=ClaudeCodeComponentType.SLASH_COMMAND,
                command=f"/aipm-{agent_role}-{capability}",
                parameters=[
                    {
                        "name": "input",
                        "type": "string",
                        "description": f"Input for {capability} capability",
                        "required": True
                    }
                ],
                examples=[
                    f"/aipm-{agent_role}-{capability} --input=\"Your input here\""
                ],
                enabled=True,
                requires_confirmation=False,
                timeout=180,
                category="capability",
                keywords=[agent_role, capability, "aipm"]
            )
            
            command_file = commands_dir / f"aipm-{agent_role}-{capability}.md"
            command_content = self._create_capability_command_content(capability_command, agent_role, capability)
            command_file.write_text(command_content)
            commands.append(capability_command)
        
        return commands
    
    def _create_workflow_execution_commands(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        commands_dir: Path
    ) -> List[SlashCommandDefinition]:
        """Create workflow execution commands."""
        commands = []
        
        # Workflow execute command
        workflow_execute_command = SlashCommandDefinition(
            name=f"APM (Agent Project Manager) {workflow_name} Execute",
            description=f"Execute APM (Agent Project Manager) {workflow_name} workflow",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command=f"/aipm-{workflow_name}-execute",
            parameters=[
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID to execute workflow for",
                    "required": True
                },
                {
                    "name": "auto_approve",
                    "type": "boolean",
                    "description": "Auto-approve workflow steps",
                    "required": False
                }
            ],
            examples=[
                f"/aipm-{workflow_name}-execute --work-item-id=123",
                f"/aipm-{workflow_name}-execute --work-item-id=123 --auto-approve"
            ],
            enabled=True,
            requires_confirmation=True,
            timeout=600,
            category="workflow",
            keywords=[workflow_name, "execute", "workflow", "aipm"]
        )
        
        command_file = commands_dir / f"aipm-{workflow_name}-execute.md"
        command_content = self._create_workflow_execute_command_content(workflow_execute_command, workflow_name, workflow_info)
        command_file.write_text(command_content)
        commands.append(workflow_execute_command)
        
        return commands
    
    def _create_workflow_validation_commands(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        commands_dir: Path
    ) -> List[SlashCommandDefinition]:
        """Create workflow validation commands."""
        commands = []
        
        # Workflow validate command
        workflow_validate_command = SlashCommandDefinition(
            name=f"APM (Agent Project Manager) {workflow_name} Validate",
            description=f"Validate APM (Agent Project Manager) {workflow_name} workflow compliance",
            component_type=ClaudeCodeComponentType.SLASH_COMMAND,
            command=f"/aipm-{workflow_name}-validate",
            parameters=[
                {
                    "name": "work_item_id",
                    "type": "integer",
                    "description": "Work item ID to validate",
                    "required": True
                }
            ],
            examples=[
                f"/aipm-{workflow_name}-validate --work-item-id=123"
            ],
            enabled=True,
            requires_confirmation=False,
            timeout=30,
            category="workflow",
            keywords=[workflow_name, "validate", "workflow", "aipm"]
        )
        
        command_file = commands_dir / f"aipm-{workflow_name}-validate.md"
        command_content = self._create_workflow_validate_command_content(workflow_validate_command, workflow_name, workflow_info)
        command_file.write_text(command_content)
        commands.append(workflow_validate_command)
        
        return commands
    
    # Command content creation methods
    def _create_status_command_content(self, command: SlashCommandDefinition) -> str:
        """Create status command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## APM (Agent Project Manager) Integration

This command provides comprehensive project status including:
- Work item status and progress
- Task completion and time-boxing compliance
- Quality gate status
- Context quality indicators
- Agent activity and performance

## Quality Gates

- Always check project health before starting work
- Verify all quality gates are met
- Review time-boxing compliance
- Check for blocked or stalled work items
"""
    
    def _create_context_command_content(self, command: SlashCommandDefinition) -> str:
        """Create context command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## APM (Agent Project Manager) Integration

This command provides hierarchical context including:
- Project context (tech stack, frameworks, patterns)
- Work item context (scope, requirements, dependencies)
- Task context (implementation details, constraints)
- Agent context (specialization, capabilities)

## Context Quality

- **GREEN** (>0.8): Excellent context, proceed with confidence
- **YELLOW** (0.6-0.8): Adequate context, proceed with caution
- **RED** (<0.6): Insufficient context, request additional information

## Quality Gates

- Always get context before starting work
- Check context quality indicators
- Review dependencies and blockers
- Follow established patterns
"""
    
    def _create_learnings_command_content(self, command: SlashCommandDefinition) -> str:
        """Create learnings command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Learning Types

- **decision**: Architectural and design decisions
- **pattern**: Reusable solutions and approaches
- **learning**: Insights and lessons learned
- **discovery**: New findings and realizations

## APM (Agent Project Manager) Integration

This command enables evidence-based development by:
- Recording decisions with supporting evidence
- Capturing patterns for future reuse
- Tracking business value and impact
- Maintaining confidence scores
- Building organizational knowledge

## Quality Gates

- Always record decisions with evidence
- Link decisions to business value
- Track confidence scores
- Validate against acceptance criteria
"""
    
    def _create_work_item_list_command_content(self, command: SlashCommandDefinition) -> str:
        """Create work item list command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Work Item Types

- **FEATURE**: New functionality (DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION)
- **ENHANCEMENT**: Improvement to existing functionality (DESIGN + IMPLEMENTATION + TESTING)
- **BUGFIX**: Bug fixes (ANALYSIS + BUGFIX + TESTING)
- **RESEARCH**: Research and analysis (RESEARCH + ANALYSIS + DOCUMENTATION)

## APM (Agent Project Manager) Integration

This command provides comprehensive work item management:
- Filter by type, status, and search terms
- Show work item dependencies and blockers
- Display quality gate compliance
- Track progress and completion

## Quality Gates

- Always check work item dependencies
- Verify required tasks are present
- Ensure quality gate compliance
- Review acceptance criteria
"""
    
    def _create_work_item_create_command_content(self, command: SlashCommandDefinition) -> str:
        """Create work item create command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Work Item Structure

This command automatically creates the proper task structure:
- **FEATURE**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX**: ANALYSIS + BUGFIX + TESTING
- **RESEARCH**: RESEARCH + ANALYSIS + DOCUMENTATION

## APM (Agent Project Manager) Integration

This command ensures:
- Proper work item structure and tasks
- Quality gate compliance
- Time-boxing validation
- Dependency management
- Acceptance criteria setup

## Quality Gates

- Always create work items with proper structure
- Set appropriate priority levels
- Define clear acceptance criteria
- Check for dependencies
"""
    
    def _create_task_list_command_content(self, command: SlashCommandDefinition) -> str:
        """Create task list command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Task Types

- **DESIGN**: System and component design (max 8h)
- **IMPLEMENTATION**: Code implementation (max 4h)
- **TESTING**: Test development and execution (max 6h)
- **DOCUMENTATION**: Documentation creation (max 6h)
- **ANALYSIS**: Problem analysis and investigation (max 4h)
- **BUGFIX**: Bug fixing and resolution (max 4h)

## APM (Agent Project Manager) Integration

This command provides:
- Task status and progress tracking
- Time-boxing compliance monitoring
- Dependency and blocker identification
- Quality gate validation

## Quality Gates

- Always check time-boxing compliance
- Verify task dependencies are met
- Ensure quality gates are satisfied
- Review task completion criteria
"""
    
    def _create_task_create_command_content(self, command: SlashCommandDefinition) -> str:
        """Create task create command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Time-Boxing Limits

- **DESIGN**: Maximum 8 hours
- **IMPLEMENTATION**: Maximum 4 hours (enforced)
- **TESTING**: Maximum 6 hours
- **DOCUMENTATION**: Maximum 6 hours
- **ANALYSIS**: Maximum 4 hours
- **BUGFIX**: Maximum 4 hours

## APM (Agent Project Manager) Integration

This command ensures:
- Proper time-boxing compliance
- Task dependency validation
- Quality gate enforcement
- Work item structure compliance

## Quality Gates

- Always respect time-boxing limits
- Check task dependencies before creation
- Ensure work item structure compliance
- Validate effort estimates
"""
    
    def _create_context_refresh_command_content(self, command: SlashCommandDefinition) -> str:
        """Create context refresh command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## APM (Agent Project Manager) Integration

This command refreshes:
- Project context and tech stack
- Work item context and dependencies
- Task context and constraints
- Agent context and capabilities
- Plugin facts and code amalgamations

## Context Quality

- **GREEN** (>0.8): Excellent context, proceed with confidence
- **YELLOW** (0.6-0.8): Adequate context, proceed with caution
- **RED** (<0.6): Insufficient context, request additional information

## Quality Gates

- Always refresh context when stale
- Check context quality indicators
- Verify context completeness
- Update agent context as needed
"""
    
    def _create_learning_list_command_content(self, command: SlashCommandDefinition) -> str:
        """Create learning list command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Learning Types

- **decision**: Architectural and design decisions with evidence
- **pattern**: Reusable solutions and approaches
- **learning**: Insights and lessons learned
- **discovery**: New findings and realizations

## APM (Agent Project Manager) Integration

This command provides:
- Comprehensive learning and decision history
- Pattern recognition and reuse
- Evidence-based decision tracking
- Business value and impact analysis

## Quality Gates

- Always review relevant learnings before decisions
- Check for existing patterns and solutions
- Validate decisions against evidence
- Track business value and impact
"""
    
    def _create_agent_list_command_content(self, command: SlashCommandDefinition) -> str:
        """Create agent list command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Agent Tiers

- **ORCHESTRATOR**: High-level coordination and management
- **SPECIALIST**: Domain-specific expertise and capabilities
- **SUB-AGENT**: Focused task execution and support

## APM (Agent Project Manager) Integration

This command provides:
- Agent capabilities and specializations
- Agent status and availability
- Agent performance and usage
- Agent coordination and orchestration

## Quality Gates

- Always check agent capabilities before assignment
- Verify agent availability and status
- Review agent performance and quality
- Ensure proper agent coordination
"""
    
    def _create_workflow_validate_command_content(self, command: SlashCommandDefinition) -> str:
        """Create workflow validate command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## APM (Agent Project Manager) Integration

This command validates:
- Work item structure and required tasks
- Time-boxing compliance
- Quality gate enforcement
- Dependency resolution
- Acceptance criteria completion

## Quality Gates

- Always validate workflows before execution
- Check all required tasks are present
- Verify time-boxing compliance
- Ensure quality gate satisfaction
- Validate dependency resolution
"""
    
    def _create_project_status_command_content(self, command: SlashCommandDefinition, project_id: int) -> str:
        """Create project status command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## APM (Agent Project Manager) Integration

This command provides project-specific status:
- Project {project_id} work items and progress
- Project-specific context and quality
- Project agent activity and performance
- Project workflow compliance

## Quality Gates

- Always check project health before work
- Verify project-specific quality gates
- Review project context quality
- Ensure project workflow compliance
"""
    
    def _create_agent_invoke_command_content(self, command: SlashCommandDefinition, agent_role: str, agent_capabilities: List[str]) -> str:
        """Create agent invoke command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Agent Capabilities

{chr(10).join(f"- {capability}" for capability in agent_capabilities)}

## APM (Agent Project Manager) Integration

This command invokes the {agent_role} agent for:
- Specialized task execution
- Domain-specific expertise
- Capability-based problem solving
- Quality gate enforcement

## Quality Gates

- Always check agent capabilities match task requirements
- Verify agent availability and status
- Ensure proper task context and constraints
- Validate agent output quality
"""
    
    def _create_capability_command_content(self, command: SlashCommandDefinition, agent_role: str, capability: str) -> str:
        """Create capability command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Capability: {capability}

This command uses the {agent_role} agent's {capability} capability for specialized task execution.

## APM (Agent Project Manager) Integration

This command provides:
- Capability-specific task execution
- Domain expertise application
- Quality gate enforcement
- Evidence-based decision making

## Quality Gates

- Always verify capability matches task requirements
- Check agent availability and status
- Ensure proper input validation
- Validate output quality and compliance
"""
    
    def _create_workflow_execute_command_content(self, command: SlashCommandDefinition, workflow_name: str, workflow_info: Dict[str, Any]) -> str:
        """Create workflow execute command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Workflow: {workflow_name}

{workflow_info.get('description', f'APM (Agent Project Manager) {workflow_name} workflow')}

## Required Tasks

{chr(10).join(f"- {task}" for task in workflow_info.get('required_tasks', []))}

## Time Limits

{chr(10).join(f"- {task_type}: Max {hours} hours" for task_type, hours in workflow_info.get('time_limits', {}).items())}

## APM (Agent Project Manager) Integration

This command executes the {workflow_name} workflow with:
- Proper task sequencing and dependencies
- Quality gate enforcement
- Time-boxing compliance
- Progress tracking and validation

## Quality Gates

- Always validate workflow before execution
- Check all required tasks are present
- Verify time-boxing compliance
- Ensure quality gate satisfaction
- Track progress and completion
"""
    
    def _create_workflow_validate_command_content(self, command: SlashCommandDefinition, workflow_name: str, workflow_info: Dict[str, Any]) -> str:
        """Create workflow validate command content."""
        return f"""---
description: {command.description}
---

# {command.name}

{command.description}

## Usage

{command.command}

## Parameters

{chr(10).join(f"- `{param['name']}` ({param['type']}): {param['description']}" + (" (required)" if param.get('required') else "") for param in command.parameters)}

## Examples

{chr(10).join(f"```bash{chr(10)}{example}{chr(10)}```" for example in command.examples)}

## Workflow: {workflow_name}

{workflow_info.get('description', f'APM (Agent Project Manager) {workflow_name} workflow')}

## Required Tasks

{chr(10).join(f"- {task}" for task in workflow_info.get('required_tasks', []))}

## Time Limits

{chr(10).join(f"- {task_type}: Max {hours} hours" for task_type, hours in workflow_info.get('time_limits', {}).items())}

## APM (Agent Project Manager) Integration

This command validates the {workflow_name} workflow:
- Work item structure compliance
- Required task presence
- Time-boxing compliance
- Quality gate satisfaction
- Dependency resolution

## Quality Gates

- Always validate workflows before execution
- Check all required tasks are present
- Verify time-boxing compliance
- Ensure quality gate satisfaction
- Validate dependency resolution
"""
