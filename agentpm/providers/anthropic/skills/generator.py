"""
Claude Code Skill Generator

Generates Claude Code Skills from APM (Agent Project Manager) agents, workflows, and capabilities.
Converts APM (Agent Project Manager)'s structured project management into discoverable Skills
for Claude Code.

Pattern: Generator with template-based rendering
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from agentpm.core.database.models.agent import Agent
from agentpm.core.database.service import DatabaseService
from .models import SkillDefinition, SkillTemplate, SkillCategory, SkillType
from .templates import get_skill_template
from .registry import SkillRegistry


class ClaudeCodeSkillGenerator:
    """
    Generates Claude Code Skills from APM (Agent Project Manager) components.
    
    Converts:
    - APM (Agent Project Manager) agents → Agent specialization Skills
    - APM (Agent Project Manager) workflows → Workflow Skills  
    - APM (Agent Project Manager) capabilities → Capability Skills
    - APM (Agent Project Manager) frameworks → Framework-specific Skills
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize skill generator.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self.registry = SkillRegistry()
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all available skill templates."""
        # Load built-in templates
        self.registry.register_template(
            get_skill_template("project-manager")
        )
        self.registry.register_template(
            get_skill_template("framework-specific")
        )
        self.registry.register_template(
            get_skill_template("agent-specialization")
        )
        self.registry.register_template(
            get_skill_template("workflow")
        )
        self.registry.register_template(
            get_skill_template("quality-assurance")
        )
    
    def generate_skills_from_agents(
        self, 
        project_id: int,
        output_dir: Path,
        skill_type: SkillType = SkillType.PROJECT
    ) -> List[SkillDefinition]:
        """
        Generate Skills from APM (Agent Project Manager) agents.
        
        Args:
            project_id: Project ID to generate Skills for
            output_dir: Directory to write Skills to
            skill_type: Type of Skills to generate
            
        Returns:
            List of generated SkillDefinitions
        """
        from agentpm.core.database.methods import agents
        
        # Get all agents for project
        project_agents = agents.list_agents(self.db, project_id)
        
        generated_skills = []
        
        for agent in project_agents:
            if not agent.is_active:
                continue
            
            # Determine template based on agent tier and category
            template_id = self._get_template_for_agent(agent)
            template = self.registry.get_template(template_id)
            
            if not template:
                continue
            
            # Generate skill from agent
            skill = self._generate_skill_from_agent(agent, template, skill_type)
            generated_skills.append(skill)
            
            # Write skill to filesystem
            self._write_skill_to_filesystem(skill, output_dir)
        
        return generated_skills
    
    def generate_workflow_skills(
        self,
        project_id: int,
        output_dir: Path,
        skill_type: SkillType = SkillType.PROJECT
    ) -> List[SkillDefinition]:
        """
        Generate Skills from APM (Agent Project Manager) workflows.
        
        Args:
            project_id: Project ID to generate Skills for
            output_dir: Directory to write Skills to
            skill_type: Type of Skills to generate
            
        Returns:
            List of generated SkillDefinitions
        """
        # Get workflow data from database
        from agentpm.core.database.methods import work_items
        
        # Get work item types and their required tasks
        workflow_data = self._get_workflow_data(project_id)
        
        generated_skills = []
        
        for workflow_name, workflow_info in workflow_data.items():
            template = self.registry.get_template("workflow")
            if not template:
                continue
            
            # Generate skill from workflow
            skill = self._generate_skill_from_workflow(
                workflow_name, 
                workflow_info, 
                template, 
                skill_type
            )
            generated_skills.append(skill)
            
            # Write skill to filesystem
            self._write_skill_to_filesystem(skill, output_dir)
        
        return generated_skills
    
    def generate_framework_skills(
        self,
        project_id: int,
        output_dir: Path,
        skill_type: SkillType = SkillType.PROJECT
    ) -> List[SkillDefinition]:
        """
        Generate Skills from detected frameworks.
        
        Args:
            project_id: Project ID to generate Skills for
            output_dir: Directory to write Skills to
            skill_type: Type of Skills to generate
            
        Returns:
            List of generated SkillDefinitions
        """
        from agentpm.core.database.methods import projects
        
        # Get project and detected frameworks
        project = projects.get_project(self.db, project_id)
        if not project:
            return []
        
        # Get detected technologies from project
        detected_tech = self._get_detected_technologies(project)
        
        generated_skills = []
        
        for tech_name, tech_info in detected_tech.items():
            template = self.registry.get_template("framework-specific")
            if not template:
                continue
            
            # Generate skill from framework
            skill = self._generate_skill_from_framework(
                tech_name,
                tech_info,
                template,
                skill_type
            )
            generated_skills.append(skill)
            
            # Write skill to filesystem
            self._write_skill_to_filesystem(skill, output_dir)
        
        return generated_skills
    
    def generate_core_skills(
        self,
        project_id: int,
        output_dir: Path,
        skill_type: SkillType = SkillType.PROJECT
    ) -> List[SkillDefinition]:
        """
        Generate core APM (Agent Project Manager) Skills.
        
        Args:
            project_id: Project ID to generate Skills for
            output_dir: Directory to write Skills to
            skill_type: Type of Skills to generate
            
        Returns:
            List of generated SkillDefinitions
        """
        generated_skills = []
        
        # Core project manager skill
        template = self.registry.get_template("project-manager")
        if template:
            skill = self._generate_core_project_manager_skill(
                project_id, template, skill_type
            )
            generated_skills.append(skill)
            self._write_skill_to_filesystem(skill, output_dir)
        
        # Quality assurance skill
        template = self.registry.get_template("quality-assurance")
        if template:
            skill = self._generate_quality_assurance_skill(
                project_id, template, skill_type
            )
            generated_skills.append(skill)
            self._write_skill_to_filesystem(skill, output_dir)
        
        return generated_skills
    
    def generate_all_skills(
        self,
        project_id: int,
        output_dir: Path,
        skill_type: SkillType = SkillType.PROJECT
    ) -> List[SkillDefinition]:
        """
        Generate all Skills for a project.
        
        Args:
            project_id: Project ID to generate Skills for
            output_dir: Directory to write Skills to
            skill_type: Type of Skills to generate
            
        Returns:
            List of all generated SkillDefinitions
        """
        all_skills = []
        
        # Generate core skills
        all_skills.extend(
            self.generate_core_skills(project_id, output_dir, skill_type)
        )
        
        # Generate agent skills
        all_skills.extend(
            self.generate_skills_from_agents(project_id, output_dir, skill_type)
        )
        
        # Generate workflow skills
        all_skills.extend(
            self.generate_workflow_skills(project_id, output_dir, skill_type)
        )
        
        # Generate framework skills
        all_skills.extend(
            self.generate_framework_skills(project_id, output_dir, skill_type)
        )
        
        return all_skills
    
    def _get_template_for_agent(self, agent: Agent) -> str:
        """Get appropriate template for agent."""
        # Map agent tiers to templates
        if agent.tier and agent.tier.value == 3:  # Orchestrator
            return "agent-specialization"
        elif agent.tier and agent.tier.value == 2:  # Specialist
            return "agent-specialization"
        else:  # Sub-agent
            return "agent-specialization"
    
    def _generate_skill_from_agent(
        self, 
        agent: Agent, 
        template: SkillTemplate,
        skill_type: SkillType
    ) -> SkillDefinition:
        """Generate skill from APM (Agent Project Manager) agent."""
        return template.render_skill(
            name=f"APM (Agent Project Manager) {agent.display_name}",
            description=f"{agent.description}. Use when working with {agent.role} tasks or when you need {agent.display_name.lower()} capabilities.",
            source_agent_id=agent.id,
            agent_role=agent.role,
            agent_display_name=agent.display_name,
            agent_description=agent.description,
            agent_sop=agent.sop_content or "",
            agent_capabilities=agent.capabilities,
            agent_tools=self._get_agent_tools(agent),
            skill_type=skill_type.value
        )
    
    def _generate_skill_from_workflow(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        template: SkillTemplate,
        skill_type: SkillType
    ) -> SkillDefinition:
        """Generate skill from APM (Agent Project Manager) workflow."""
        return template.render_skill(
            name=f"APM (Agent Project Manager) {workflow_name.title()} Workflow",
            description=f"Follow APM (Agent Project Manager) {workflow_name} workflow with quality gates and task structure. Use when working on {workflow_name} work items.",
            workflow_name=workflow_name,
            workflow_info=workflow_info,
            skill_type=skill_type.value
        )
    
    def _generate_skill_from_framework(
        self,
        tech_name: str,
        tech_info: Dict[str, Any],
        template: SkillTemplate,
        skill_type: SkillType
    ) -> SkillDefinition:
        """Generate skill from detected framework."""
        return template.render_skill(
            name=f"APM (Agent Project Manager) {tech_name.title()} Development",
            description=f"{tech_name.title()} development with APM (Agent Project Manager) project management. Use when working on {tech_name} projects that need structured development workflow.",
            framework_name=tech_name,
            framework_info=tech_info,
            skill_type=skill_type.value
        )
    
    def _generate_core_project_manager_skill(
        self,
        project_id: int,
        template: SkillTemplate,
        skill_type: SkillType
    ) -> SkillDefinition:
        """Generate core project manager skill."""
        return template.render_skill(
            name="APM (Agent Project Manager) Project Manager",
            description="Comprehensive Agent Project Manager for managing work items, tasks, and context. Use when working on projects that need structured project management, work item tracking, or quality gate enforcement.",
            project_id=project_id,
            skill_type=skill_type.value
        )
    
    def _generate_quality_assurance_skill(
        self,
        project_id: int,
        template: SkillTemplate,
        skill_type: SkillType
    ) -> SkillDefinition:
        """Generate quality assurance skill."""
        return template.render_skill(
            name="APM (Agent Project Manager) Quality Assurance",
            description="Quality assurance and testing with APM (Agent Project Manager) standards. Use when writing tests, checking code quality, or ensuring compliance with APM (Agent Project Manager) quality gates.",
            project_id=project_id,
            skill_type=skill_type.value
        )
    
    def _get_agent_tools(self, agent: Agent) -> List[str]:
        """Get tools for agent based on capabilities."""
        # Map capabilities to tools
        tool_mapping = {
            "python": ["Read", "Write", "Bash", "Grep", "Glob"],
            "database": ["Read", "Write", "Bash", "Grep"],
            "testing": ["Read", "Write", "Bash", "Grep", "Glob"],
            "documentation": ["Read", "Write", "Grep", "Glob"],
            "analysis": ["Read", "Grep", "Glob"],
        }
        
        tools = set()
        for capability in agent.capabilities:
            if capability.lower() in tool_mapping:
                tools.update(tool_mapping[capability.lower()])
        
        return list(tools) if tools else ["Read", "Write", "Bash", "Grep", "Glob"]
    
    def _get_workflow_data(self, project_id: int) -> Dict[str, Any]:
        """Get workflow data from project."""
        # This would typically come from the database
        # For now, return static workflow definitions
        return {
            "feature": {
                "required_tasks": ["DESIGN", "IMPLEMENTATION", "TESTING", "DOCUMENTATION"],
                "time_limits": {"IMPLEMENTATION": 4},
                "description": "Feature development workflow"
            },
            "bugfix": {
                "required_tasks": ["ANALYSIS", "BUGFIX", "TESTING"],
                "time_limits": {"BUGFIX": 4},
                "description": "Bug fix workflow"
            },
            "enhancement": {
                "required_tasks": ["DESIGN", "IMPLEMENTATION", "TESTING"],
                "time_limits": {"IMPLEMENTATION": 4},
                "description": "Enhancement workflow"
            }
        }
    
    def _get_detected_technologies(self, project) -> Dict[str, Any]:
        """Get detected technologies from project."""
        # This would typically come from the detection service
        # For now, return empty dict
        return {}
    
    def _write_skill_to_filesystem(
        self, 
        skill: SkillDefinition, 
        output_dir: Path
    ) -> None:
        """
        Write skill to filesystem in Claude Code format.
        
        Args:
            skill: Skill to write
            output_dir: Base output directory
        """
        # Create skill directory
        skill_dir = output_dir / skill.get_skill_directory_name()
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill.to_skill_markdown())
        
        # Write supporting files
        for filename, content in skill.supporting_files.items():
            support_file = skill_dir / filename
            support_file.write_text(content)
        
        # Write metadata
        metadata_file = skill_dir / "metadata.json"
        metadata = {
            "name": skill.name,
            "description": skill.description,
            "category": skill.category.value,
            "version": skill.version,
            "author": skill.author,
            "created_at": skill.created_at.isoformat() if skill.created_at else None,
            "updated_at": skill.updated_at.isoformat() if skill.updated_at else None,
            "source_agent_id": skill.source_agent_id,
            "source_workflow_id": skill.source_workflow_id,
            "capabilities": skill.capabilities,
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))
