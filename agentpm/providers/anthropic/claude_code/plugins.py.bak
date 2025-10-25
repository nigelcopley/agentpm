"""
Claude Code Plugins System

Manages Claude Code plugins including plugin creation, installation, and management.
Converts APM (Agent Project Manager) components into Claude Code plugins.

Based on: https://docs.claude.com/en/docs/claude-code/plugins
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.agent import Agent
from .models import PluginDefinition, MarketplaceDefinition, ClaudeCodeComponentType


class ClaudeCodePluginManager:
    """
    Manages Claude Code plugins for APM (Agent Project Manager).
    
    Converts APM (Agent Project Manager) components into Claude Code plugins and manages
    plugin marketplaces for team distribution.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize plugin manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._plugin_cache: Dict[str, PluginDefinition] = {}
        self._marketplace_cache: Dict[str, MarketplaceDefinition] = {}
    
    def create_plugin_from_agent(
        self, 
        agent: Agent, 
        output_dir: Path,
        include_skills: bool = True,
        include_hooks: bool = True
    ) -> PluginDefinition:
        """
        Create Claude Code plugin from APM (Agent Project Manager) agent.
        
        Args:
            agent: APM (Agent Project Manager) agent to convert
            output_dir: Directory to create plugin in
            include_skills: Whether to include agent skills
            include_hooks: Whether to include agent hooks
            
        Returns:
            PluginDefinition for the created plugin
        """
        # Create plugin directory structure
        plugin_dir = output_dir / agent.role
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .claude-plugin directory
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir(exist_ok=True)
        
        # Create plugin manifest
        plugin_manifest = self._create_plugin_manifest(agent)
        manifest_file = claude_plugin_dir / "plugin.json"
        manifest_file.write_text(json.dumps(plugin_manifest, indent=2))
        
        # Create plugin components
        components = []
        
        # Create slash command for agent
        if agent.sop_content:
            command_file = plugin_dir / "commands" / f"{agent.role}.md"
            command_file.parent.mkdir(exist_ok=True)
            command_content = self._create_agent_command(agent)
            command_file.write_text(command_content)
            components.append(f"commands/{agent.role}.md")
        
        # Create subagent definition
        if agent.capabilities:
            agent_file = plugin_dir / "agents" / f"{agent.role}.md"
            agent_file.parent.mkdir(exist_ok=True)
            agent_content = self._create_subagent_definition(agent)
            agent_file.write_text(agent_content)
            components.append(f"agents/{agent.role}.md")
        
        # Create skills if requested
        if include_skills and agent.sop_content:
            skill_dir = plugin_dir / "skills" / agent.role
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_content = self._create_agent_skill(agent)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(skill_content)
            components.append(f"skills/{agent.role}/SKILL.md")
        
        # Create hooks if requested
        if include_hooks and agent.capabilities:
            hooks_file = plugin_dir / "hooks" / "hooks.json"
            hooks_file.parent.mkdir(exist_ok=True)
            hooks_content = self._create_agent_hooks(agent)
            hooks_file.write_text(json.dumps(hooks_content, indent=2))
            components.append("hooks/hooks.json")
        
        # Create plugin definition
        plugin = PluginDefinition(
            name=agent.role,
            description=agent.description or f"APM (Agent Project Manager) {agent.display_name} plugin",
            component_type=ClaudeCodeComponentType.PLUGIN,
            commands=components if "commands/" in str(components) else [],
            agents=components if "agents/" in str(components) else [],
            skills=components if "skills/" in str(components) else [],
            hooks=components if "hooks/" in str(components) else [],
            source_agent_id=agent.id,
            capabilities=agent.capabilities,
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Cache plugin
        self._plugin_cache[agent.role] = plugin
        
        return plugin
    
    def create_workflow_plugin(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        output_dir: Path
    ) -> PluginDefinition:
        """
        Create Claude Code plugin from APM (Agent Project Manager) workflow.
        
        Args:
            workflow_name: Name of the workflow
            workflow_info: Workflow information
            output_dir: Directory to create plugin in
            
        Returns:
            PluginDefinition for the created plugin
        """
        # Create plugin directory structure
        plugin_dir = output_dir / f"aipm-{workflow_name}-workflow"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .claude-plugin directory
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir(exist_ok=True)
        
        # Create plugin manifest
        plugin_manifest = {
            "name": f"aipm-{workflow_name}-workflow",
            "description": f"APM (Agent Project Manager) {workflow_name} workflow plugin",
            "version": "1.0.0",
            "author": {
                "name": "APM (Agent Project Manager)"
            },
            "category": "workflow",
            "keywords": ["aipm", "workflow", workflow_name]
        }
        
        manifest_file = claude_plugin_dir / "plugin.json"
        manifest_file.write_text(json.dumps(plugin_manifest, indent=2))
        
        # Create workflow command
        command_file = plugin_dir / "commands" / f"{workflow_name}.md"
        command_file.parent.mkdir(exist_ok=True)
        command_content = self._create_workflow_command(workflow_name, workflow_info)
        command_file.write_text(command_content)
        
        # Create workflow skill
        skill_dir = plugin_dir / "skills" / f"{workflow_name}-workflow"
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_content = self._create_workflow_skill(workflow_name, workflow_info)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)
        
        # Create plugin definition
        plugin = PluginDefinition(
            name=f"aipm-{workflow_name}-workflow",
            description=f"APM (Agent Project Manager) {workflow_name} workflow plugin",
            component_type=ClaudeCodeComponentType.PLUGIN,
            commands=[f"commands/{workflow_name}.md"],
            skills=[f"skills/{workflow_name}-workflow/SKILL.md"],
            capabilities=[workflow_name, "workflow", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return plugin
    
    def create_core_plugin(
        self,
        output_dir: Path
    ) -> PluginDefinition:
        """
        Create core APM (Agent Project Manager) plugin with essential functionality.
        
        Args:
            output_dir: Directory to create plugin in
            
        Returns:
            PluginDefinition for the core plugin
        """
        # Create plugin directory structure
        plugin_dir = output_dir / "aipm-v2-core"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .claude-plugin directory
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir(exist_ok=True)
        
        # Create plugin manifest
        plugin_manifest = {
            "name": "aipm-v2-core",
            "description": "APM (Agent Project Manager) Core - Essential project management capabilities",
            "version": "1.0.0",
            "author": {
                "name": "APM (Agent Project Manager)"
            },
            "category": "project-management",
            "keywords": ["aipm", "project-management", "work-items", "tasks", "context"]
        }
        
        manifest_file = claude_plugin_dir / "plugin.json"
        manifest_file.write_text(json.dumps(plugin_manifest, indent=2))
        
        # Create core commands
        commands = [
            "status.md",
            "work-item.md", 
            "task.md",
            "context.md",
            "learnings.md"
        ]
        
        for command in commands:
            command_file = plugin_dir / "commands" / command
            command_file.parent.mkdir(exist_ok=True)
            command_content = self._create_core_command(command.replace(".md", ""))
            command_file.write_text(command_content)
        
        # Create core skills
        skills = [
            "project-manager",
            "quality-assurance",
            "context-assembly"
        ]
        
        for skill in skills:
            skill_dir = plugin_dir / "skills" / skill
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_content = self._create_core_skill(skill)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(skill_content)
        
        # Create core hooks
        hooks_file = plugin_dir / "hooks" / "hooks.json"
        hooks_file.parent.mkdir(exist_ok=True)
        hooks_content = self._create_core_hooks()
        hooks_file.write_text(json.dumps(hooks_content, indent=2))
        
        # Create plugin definition
        plugin = PluginDefinition(
            name="aipm-v2-core",
            description="APM (Agent Project Manager) Core - Essential project management capabilities",
            component_type=ClaudeCodeComponentType.PLUGIN,
            commands=[f"commands/{cmd}" for cmd in commands],
            skills=[f"skills/{skill}/SKILL.md" for skill in skills],
            hooks=["hooks/hooks.json"],
            capabilities=["project-management", "work-items", "tasks", "context", "quality-gates"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return plugin
    
    def create_marketplace(
        self,
        marketplace_name: str,
        plugins: List[PluginDefinition],
        output_dir: Path
    ) -> MarketplaceDefinition:
        """
        Create Claude Code marketplace with plugins.
        
        Args:
            marketplace_name: Name of the marketplace
            plugins: List of plugins to include
            output_dir: Directory to create marketplace in
            
        Returns:
            MarketplaceDefinition for the created marketplace
        """
        # Create marketplace directory
        marketplace_dir = output_dir / marketplace_name
        marketplace_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .claude-plugin directory
        claude_plugin_dir = marketplace_dir / ".claude-plugin"
        claude_plugin_dir.mkdir(exist_ok=True)
        
        # Create marketplace manifest
        marketplace_manifest = {
            "name": marketplace_name,
            "owner": {
                "name": "APM (Agent Project Manager)"
            },
            "description": f"APM (Agent Project Manager) {marketplace_name} plugin marketplace",
            "plugins": []
        }
        
        # Add plugins to marketplace
        for plugin in plugins:
            plugin_info = {
                "name": plugin.name,
                "source": f"./{plugin.name}",
                "description": plugin.description
            }
            marketplace_manifest["plugins"].append(plugin_info)
        
        manifest_file = claude_plugin_dir / "marketplace.json"
        manifest_file.write_text(json.dumps(marketplace_manifest, indent=2))
        
        # Create marketplace definition
        marketplace = MarketplaceDefinition(
            name=marketplace_name,
            owner={"name": "APM (Agent Project Manager)"},
            description=f"APM (Agent Project Manager) {marketplace_name} plugin marketplace",
            plugins=marketplace_manifest["plugins"],
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Cache marketplace
        self._marketplace_cache[marketplace_name] = marketplace
        
        return marketplace
    
    def create_aipm_plugins(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[PluginDefinition]:
        """
        Create comprehensive APM (Agent Project Manager) plugins for Claude Code.
        
        Args:
            output_dir: Directory to write plugin definitions
            project_id: Optional project ID for project-specific plugins
            
        Returns:
            List of created PluginDefinitions
        """
        plugins = []
        
        # Create plugins directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create core plugins
        plugins.extend(self._create_core_plugins(output_dir))
        
        # Create workflow plugins if project_id provided
        if project_id:
            plugins.extend(self._create_workflow_plugins(output_dir, project_id))
        
        # Create agent plugins
        plugins.extend(self._create_agent_plugins(output_dir))
        
        return plugins
    
    def _create_core_plugins(self, output_dir: Path) -> List[PluginDefinition]:
        """Create core APM (Agent Project Manager) plugins."""
        plugins = []
        
        # Core APM (Agent Project Manager) plugin
        core_plugin = self.create_core_plugin(
            name="APM (Agent Project Manager) Core",
            description="Core APM (Agent Project Manager) functionality for Claude Code",
            output_dir=output_dir
        )
        plugins.append(core_plugin)
        
        return plugins
    
    def _create_workflow_plugins(self, output_dir: Path, project_id: int) -> List[PluginDefinition]:
        """Create workflow-specific plugins."""
        plugins = []
        
        # Workflow management plugin
        workflow_plugin = self.create_workflow_plugin(
            name=f"APM (Agent Project Manager) Project {project_id} Workflow",
            description=f"Workflow management for project {project_id}",
            project_id=project_id,
            output_dir=output_dir
        )
        plugins.append(workflow_plugin)
        
        return plugins
    
    def _create_agent_plugins(self, output_dir: Path) -> List[PluginDefinition]:
        """Create agent-specific plugins."""
        plugins = []
        
        # Get agents from database
        try:
            agents = self.db.get_all_agents()
            for agent in agents:
                agent_plugin = self.create_plugin_from_agent(
                    agent=agent,
                    output_dir=output_dir
                )
                plugins.append(agent_plugin)
        except Exception as e:
            print(f"Error creating agent plugins: {e}")
        
        return plugins
    
    def _create_plugin_manifest(self, agent: Agent) -> Dict[str, Any]:
        """Create plugin manifest for agent."""
        return {
            "name": agent.role,
            "description": agent.description or f"APM (Agent Project Manager) {agent.display_name} plugin",
            "version": "1.0.0",
            "author": {
                "name": "APM (Agent Project Manager)"
            },
            "category": "agent",
            "keywords": ["aipm", "agent", agent.role] + agent.capabilities
        }
    
    def _create_agent_command(self, agent: Agent) -> str:
        """Create slash command for agent."""
        return f"""---
description: {agent.description or f"Execute {agent.display_name} tasks"}
---

# {agent.display_name} Command

{agent.description or f"Execute tasks using the {agent.display_name} agent."}

## Capabilities

{chr(10).join(f"- {capability}" for capability in agent.capabilities)}

## Usage

Use this command when you need {agent.display_name.lower()} capabilities or when working with {agent.role} tasks.

## Standard Operating Procedure

{agent.sop_content or "No SOP available."}
"""
    
    def _create_subagent_definition(self, agent: Agent) -> str:
        """Create subagent definition for agent."""
        return f"""---
name: {agent.display_name}
description: {agent.description or f"APM (Agent Project Manager) {agent.display_name} subagent"}
role: {agent.role}
capabilities: {agent.capabilities}
auto_invoke: false
priority: 50
---

# {agent.display_name}

{agent.description or f"APM (Agent Project Manager) {agent.display_name} subagent for specialized tasks."}

## Capabilities

{chr(10).join(f"- {capability}" for capability in agent.capabilities)}

## Standard Operating Procedure

{agent.sop_content or "No SOP available."}

## Usage

This subagent is automatically invoked when tasks require {agent.display_name.lower()} capabilities.
"""
    
    def _create_agent_skill(self, agent: Agent) -> str:
        """Create skill for agent."""
        return f"""---
name: APM (Agent Project Manager) {agent.display_name}
description: {agent.description or f"{agent.display_name} capabilities with APM (Agent Project Manager) project management"}. Use when working with {agent.role} tasks or when you need {agent.display_name.lower()} capabilities.
allowed-tools: Read, Write, Bash, Grep, Glob
---

# APM (Agent Project Manager) {agent.display_name}

## Role: {agent.role}

{agent.description or f"APM (Agent Project Manager) {agent.display_name} for specialized tasks."}

## Capabilities

{chr(10).join(f"- {capability}" for capability in agent.capabilities)}

## Standard Operating Procedure

{agent.sop_content or "No SOP available."}

## Instructions

1. **Get Context**: `apm context show --task-id=<task_id>`
2. **Follow SOP**: Adhere to the Standard Operating Procedure above
3. **Use Capabilities**: Leverage your specialised capabilities
4. **Record Decisions**: `apm learnings record --type=decision --content="Decision with rationale"`

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
"""
    
    def _create_agent_hooks(self, agent: Agent) -> Dict[str, Any]:
        """Create hooks for agent."""
        return {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": f"agent:{agent.role}",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"echo 'Executing {agent.role} task'"
                            }
                        ]
                    }
                ]
            }
        }
    
    def _create_workflow_command(self, workflow_name: str, workflow_info: Dict[str, Any]) -> str:
        """Create command for workflow."""
        return f"""---
description: Execute APM (Agent Project Manager) {workflow_name} workflow
---

# {workflow_name.title()} Workflow Command

Execute the APM (Agent Project Manager) {workflow_name} workflow with proper quality gates and task structure.

## Workflow Information

{workflow_info.get('description', f'APM (Agent Project Manager) {workflow_name} workflow')}

## Required Tasks

{chr(10).join(f"- {task}" for task in workflow_info.get('required_tasks', []))}

## Time Limits

{chr(10).join(f"- {task_type}: Max {hours} hours" for task_type, hours in workflow_info.get('time_limits', {}).items())}

## Usage

Use this command when working on {workflow_name} work items or when you need to follow the {workflow_name} workflow.

## Instructions

1. **Create Work Item**: `apm work-item create "Name" --type {workflow_name}`
2. **Add Required Tasks**: Ensure all required tasks are present
3. **Check Dependencies**: `apm work-item list-dependencies <id>`
4. **Follow Workflow**: Execute tasks in proper sequence
5. **Validate Quality**: `apm work-item validate <id>`
"""
    
    def _create_workflow_skill(self, workflow_name: str, workflow_info: Dict[str, Any]) -> str:
        """Create skill for workflow."""
        return f"""---
name: APM (Agent Project Manager) {workflow_name.title()} Workflow
description: Follow APM (Agent Project Manager) {workflow_name} workflow with quality gates and task structure. Use when working on {workflow_name} work items.
allowed-tools: Read, Write, Bash, Grep, Glob
---

# APM (Agent Project Manager) {workflow_name.title()} Workflow

## Workflow Overview

{workflow_info.get('description', f'APM (Agent Project Manager) {workflow_name} workflow')}

## Required Tasks

{chr(10).join(f"- **{task}**: Required for {workflow_name} workflow" for task in workflow_info.get('required_tasks', []))}

## Time Limits

{chr(10).join(f"- **{task_type}**: Max {hours} hours" for task_type, hours in workflow_info.get('time_limits', {}).items())}

## Instructions

1. **Create Work Item**: `apm work-item create "Name" --type {workflow_name}`
2. **Add Required Tasks**: Ensure all required tasks are present
3. **Check Dependencies**: `apm work-item list-dependencies <id>`
4. **Follow Workflow**: Execute tasks in proper sequence
5. **Validate Quality**: `apm work-item validate <id>`

## Quality Gates

- All required tasks must be present
- Time-boxing limits must be respected
- Dependencies must be resolved before task start
- Acceptance criteria must be met before completion
"""
    
    def _create_core_command(self, command_name: str) -> str:
        """Create core APM (Agent Project Manager) command."""
        commands = {
            "status": "Show project status and health dashboard",
            "work-item": "Manage work items (features, bugs, research, planning)",
            "task": "Manage tasks with strict time-boxing and quality gates",
            "context": "Access hierarchical project context for AI agents",
            "learnings": "Record and manage learnings, decisions, and patterns"
        }
        
        return f"""---
description: {commands.get(command_name, f"APM (Agent Project Manager) {command_name} command")}
---

# APM (Agent Project Manager) {command_name.title()} Command

{commands.get(command_name, f"APM (Agent Project Manager) {command_name} command for project management.")}

## Usage

Use this command to {command_name.replace('-', ' ')} with APM (Agent Project Manager) project management.

## Examples

```bash
# {command_name} examples
apm {command_name} --help
```

## Quality Gates

- Always follow APM (Agent Project Manager) quality gates
- Check dependencies before starting work
- Record decisions with evidence
- Maintain >90% test coverage
"""
    
    def _create_core_skill(self, skill_name: str) -> str:
        """Create core APM (Agent Project Manager) skill."""
        skills = {
            "project-manager": "Comprehensive AI Project Manager for managing work items, tasks, and context",
            "quality-assurance": "Quality assurance and testing with APM (Agent Project Manager) standards",
            "context-assembly": "Hierarchical context assembly for AI agents"
        }
        
        return f"""---
name: APM (Agent Project Manager) {skill_name.replace('-', ' ').title()}
description: {skills.get(skill_name, f"APM (Agent Project Manager) {skill_name} capabilities")}. Use when working with APM (Agent Project Manager) project management.
allowed-tools: Read, Write, Bash, Grep, Glob
---

# APM (Agent Project Manager) {skill_name.replace('-', ' ').title()}

{skills.get(skill_name, f"APM (Agent Project Manager) {skill_name} capabilities for project management.")}

## Instructions

1. **Get Context**: `apm context show --task-id=<task_id>`
2. **Follow APM (Agent Project Manager) Patterns**: Use established project management patterns
3. **Check Quality Gates**: Ensure compliance with APM (Agent Project Manager) standards
4. **Record Decisions**: `apm learnings record --type=decision --content="Decision with rationale"`

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
"""
    
    def _create_core_hooks(self) -> Dict[str, Any]:
        """Create core APM (Agent Project Manager) hooks."""
        return {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "aipm",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo 'APM (Agent Project Manager) tool execution'"
                            }
                        ]
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "aipm",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo 'APM (Agent Project Manager) tool completed'"
                            }
                        ]
                    }
                ]
            }
        }
