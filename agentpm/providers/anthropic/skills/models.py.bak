"""
Skill Models - Pydantic Domain Models for Claude Code Skills

Type-safe models for Claude Code Skills generation and management.
Based on Claude Code Skills specification from docs.claude.com.

Pattern: Pydantic BaseModel with Field validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SkillType(str, Enum):
    """Types of Claude Code Skills."""
    PERSONAL = "personal"
    PROJECT = "project"
    PLUGIN = "plugin"


class SkillCategory(str, Enum):
    """Categories of APM (Agent Project Manager) Skills."""
    PROJECT_MANAGEMENT = "project-management"
    FRAMEWORK_SPECIFIC = "framework-specific"
    AGENT_SPECIALIZATION = "agent-specialization"
    WORKFLOW = "workflow"
    QUALITY_ASSURANCE = "quality-assurance"
    CONTEXT_ASSEMBLY = "context-assembly"


class SkillDefinition(BaseModel):
    """
    Claude Code Skill definition.
    
    Represents a complete Claude Code Skill with metadata, instructions,
    and supporting files.
    
    Based on Claude Code Skills specification:
    https://docs.claude.com/en/docs/claude-code/skills
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )
    
    # Core Skill metadata
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Skill name (e.g., 'APM (Agent Project Manager) Project Manager')"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Brief description of what this Skill does and when to use it"
    )
    
    # Skill configuration
    skill_type: SkillType = Field(
        default=SkillType.PROJECT,
        description="Type of Skill (personal, project, plugin)"
    )
    category: SkillCategory = Field(
        ...,
        description="APM (Agent Project Manager) category for this Skill"
    )
    
    # Tool permissions (Claude Code specific)
    allowed_tools: Optional[List[str]] = Field(
        default=None,
        description="List of tools Claude can use when this Skill is active"
    )
    
    # Content
    instructions: str = Field(
        ...,
        min_length=50,
        description="Markdown instructions for the Skill"
    )
    examples: Optional[str] = Field(
        default=None,
        description="Usage examples in Markdown"
    )
    requirements: Optional[str] = Field(
        default=None,
        description="Required packages or dependencies"
    )
    
    # Supporting files
    supporting_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional files (scripts, templates, etc.)"
    )
    
    # APM (Agent Project Manager) integration
    source_agent_id: Optional[int] = Field(
        default=None,
        description="ID of APM (Agent Project Manager) agent this Skill is based on"
    )
    source_workflow_id: Optional[int] = Field(
        default=None,
        description="ID of APM (Agent Project Manager) workflow this Skill represents"
    )
    capabilities: List[str] = Field(
        default_factory=list,
        description="APM (Agent Project Manager) capabilities this Skill provides"
    )
    
    # Metadata
    version: str = Field(
        default="1.0.0",
        description="Skill version"
    )
    author: str = Field(
        default="APM (Agent Project Manager)",
        description="Skill author"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    
    def get_skill_directory_name(self) -> str:
        """Get directory name for this Skill."""
        # Convert to lowercase, replace spaces with hyphens
        return self.name.lower().replace(" ", "-").replace("_", "-")
    
    def get_skill_file_path(self, base_path: str) -> str:
        """Get full path to SKILL.md file."""
        return f"{base_path}/{self.get_skill_directory_name()}/SKILL.md"
    
    def to_skill_markdown(self) -> str:
        """Convert to Claude Code Skill markdown format."""
        # YAML frontmatter
        frontmatter = {
            "name": self.name,
            "description": self.description,
        }
        
        if self.allowed_tools:
            frontmatter["allowed-tools"] = self.allowed_tools
        
        # Build YAML frontmatter
        yaml_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                yaml_lines.append(f"{key}:")
                for item in value:
                    yaml_lines.append(f"  - {item}")
            else:
                yaml_lines.append(f"{key}: {value}")
        yaml_lines.append("---")
        yaml_lines.append("")
        
        # Markdown content
        content_lines = [
            f"# {self.name}",
            "",
            "## Instructions",
            self.instructions,
            ""
        ]
        
        if self.examples:
            content_lines.extend([
                "## Examples",
                self.examples,
                ""
            ])
        
        if self.requirements:
            content_lines.extend([
                "## Requirements",
                self.requirements,
                ""
            ])
        
        if self.supporting_files:
            content_lines.extend([
                "## Supporting Files",
                ""
            ])
            for filename, description in self.supporting_files.items():
                content_lines.append(f"- `{filename}`: {description}")
            content_lines.append("")
        
        return "\n".join(yaml_lines + content_lines)


class SkillTemplate(BaseModel):
    """
    Template for generating Claude Code Skills.
    
    Provides reusable templates for different types of APM (Agent Project Manager) Skills.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )
    
    # Template metadata
    template_id: str = Field(
        ...,
        description="Unique template identifier"
    )
    name: str = Field(
        ...,
        description="Template name"
    )
    description: str = Field(
        ...,
        description="Template description"
    )
    category: SkillCategory = Field(
        ...,
        description="Skill category this template is for"
    )
    
    # Template content
    instructions_template: str = Field(
        ...,
        description="Jinja2 template for instructions"
    )
    examples_template: Optional[str] = Field(
        default=None,
        description="Jinja2 template for examples"
    )
    requirements_template: Optional[str] = Field(
        default=None,
        description="Jinja2 template for requirements"
    )
    
    # Template variables
    required_variables: List[str] = Field(
        default_factory=list,
        description="Required template variables"
    )
    optional_variables: List[str] = Field(
        default_factory=list,
        description="Optional template variables"
    )
    
    # Default values
    default_allowed_tools: Optional[List[str]] = Field(
        default=None,
        description="Default allowed tools for this template"
    )
    default_capabilities: List[str] = Field(
        default_factory=list,
        description="Default capabilities for this template"
    )
    
    def render_skill(self, **variables) -> SkillDefinition:
        """
        Render template into a SkillDefinition.
        
        Args:
            **variables: Template variables
            
        Returns:
            Rendered SkillDefinition
            
        Raises:
            ValueError: If required variables are missing
        """
        # Validate required variables
        missing_vars = [var for var in self.required_variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Render templates
        from jinja2 import Template
        
        instructions = Template(self.instructions_template).render(**variables)
        examples = None
        if self.examples_template:
            examples = Template(self.examples_template).render(**variables)
        requirements = None
        if self.requirements_template:
            requirements = Template(self.requirements_template).render(**variables)
        
        # Create SkillDefinition
        return SkillDefinition(
            name=variables.get("name", self.name),
            description=variables.get("description", self.description),
            category=self.category,
            allowed_tools=self.default_allowed_tools,
            instructions=instructions,
            examples=examples,
            requirements=requirements,
            capabilities=self.default_capabilities,
            source_agent_id=variables.get("source_agent_id"),
            source_workflow_id=variables.get("source_workflow_id"),
        )
