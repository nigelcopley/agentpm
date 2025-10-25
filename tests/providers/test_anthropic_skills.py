"""
Tests for Anthropic Skills Module

Tests Claude Code Skills generation and management functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.providers.anthropic.skills import (
    ClaudeCodeSkillGenerator,
    SkillDefinition,
    SkillTemplate,
    SkillRegistry,
    SkillCategory,
    SkillType
)
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.enums import AgentTier


class TestSkillDefinition:
    """Test SkillDefinition model."""
    
    def test_skill_definition_creation(self):
        """Test creating a skill definition."""
        skill = SkillDefinition(
            name="Test Skill",
            description="A test skill for testing",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions="Test instructions"
        )
        
        assert skill.name == "Test Skill"
        assert skill.description == "A test skill for testing"
        assert skill.category == SkillCategory.PROJECT_MANAGEMENT
        assert skill.instructions == "Test instructions"
        assert skill.skill_type == SkillType.PROJECT
    
    def test_skill_directory_name(self):
        """Test skill directory name generation."""
        skill = SkillDefinition(
            name="APM (Agent Project Manager) Project Manager",
            description="Test",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions="Test"
        )
        
        assert skill.get_skill_directory_name() == "aipm-v2-project-manager"
    
    def test_skill_markdown_generation(self):
        """Test skill markdown generation."""
        skill = SkillDefinition(
            name="Test Skill",
            description="A test skill",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions="Test instructions",
            allowed_tools=["Read", "Write"]
        )
        
        markdown = skill.to_skill_markdown()
        
        assert "---" in markdown
        assert "name: Test Skill" in markdown
        assert "description: A test skill" in markdown
        assert "allowed-tools:" in markdown
        assert "# Test Skill" in markdown
        assert "## Instructions" in markdown
        assert "Test instructions" in markdown


class TestSkillTemplate:
    """Test SkillTemplate model."""
    
    def test_template_creation(self):
        """Test creating a skill template."""
        template = SkillTemplate(
            template_id="test-template",
            name="Test Template",
            description="A test template",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions_template="Test {{ name }} instructions"
        )
        
        assert template.template_id == "test-template"
        assert template.name == "Test Template"
        assert template.category == SkillCategory.PROJECT_MANAGEMENT
    
    def test_template_rendering(self):
        """Test template rendering."""
        template = SkillTemplate(
            template_id="test-template",
            name="Test Template",
            description="A test template",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions_template="Test {{ name }} instructions"
        )
        
        skill = template.render_skill(name="Test Skill")
        
        assert skill.name == "Test Skill"
        assert skill.instructions == "Test Test Skill instructions"
        assert skill.category == SkillCategory.PROJECT_MANAGEMENT


class TestSkillRegistry:
    """Test SkillRegistry functionality."""
    
    def test_registry_creation(self):
        """Test creating a skill registry."""
        registry = SkillRegistry()
        assert len(registry._templates) == 0
    
    def test_template_registration(self):
        """Test registering templates."""
        registry = SkillRegistry()
        template = SkillTemplate(
            template_id="test-template",
            name="Test Template",
            description="A test template",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions_template="Test instructions"
        )
        
        registry.register_template(template)
        
        assert registry.has_template("test-template")
        assert registry.get_template("test-template") == template
    
    def test_template_lookup(self):
        """Test template lookup by category."""
        registry = SkillRegistry()
        template = SkillTemplate(
            template_id="test-template",
            name="Test Template",
            description="A test template",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions_template="Test instructions"
        )
        
        registry.register_template(template)
        
        templates = registry.list_templates(SkillCategory.PROJECT_MANAGEMENT)
        assert len(templates) == 1
        assert templates[0] == template


class TestClaudeCodeSkillGenerator:
    """Test ClaudeCodeSkillGenerator functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def generator(self, mock_db_service):
        """Create skill generator with mocked dependencies."""
        with patch('agentpm.providers.anthropic.skills.generator.SkillRegistry') as mock_registry:
            mock_registry.return_value = Mock()
            generator = ClaudeCodeSkillGenerator(mock_db_service)
            return generator
    
    def test_generator_initialization(self, mock_db_service):
        """Test generator initialization."""
        with patch('agentpm.providers.anthropic.skills.generator.SkillRegistry'):
            generator = ClaudeCodeSkillGenerator(mock_db_service)
            assert generator.db == mock_db_service
    
    def test_get_template_for_agent(self, generator):
        """Test getting template for agent."""
        # Test orchestrator agent
        agent = Agent(
            role="test-agent",
            display_name="Test Agent",
            description="Test agent",
            tier=AgentTier.ORCHESTRATOR
        )
        
        template_id = generator._get_template_for_agent(agent)
        assert template_id == "agent-specialization"
        
        # Test specialist agent
        agent.tier = AgentTier.SPECIALIST
        template_id = generator._get_template_for_agent(agent)
        assert template_id == "agent-specialization"
        
        # Test sub-agent
        agent.tier = AgentTier.SUB_AGENT
        template_id = generator._get_template_for_agent(agent)
        assert template_id == "agent-specialization"
    
    def test_get_agent_tools(self, generator):
        """Test getting tools for agent."""
        agent = Agent(
            role="test-agent",
            display_name="Test Agent",
            description="Test agent",
            capabilities=["python", "database", "testing"]
        )
        
        tools = generator._get_agent_tools(agent)
        
        # Should include tools from all capabilities
        assert "Read" in tools
        assert "Write" in tools
        assert "Bash" in tools
        assert "Grep" in tools
        assert "Glob" in tools
    
    def test_get_workflow_data(self, generator):
        """Test getting workflow data."""
        workflow_data = generator._get_workflow_data(1)
        
        assert "feature" in workflow_data
        assert "bugfix" in workflow_data
        assert "enhancement" in workflow_data
        
        # Check feature workflow
        feature_workflow = workflow_data["feature"]
        assert "required_tasks" in feature_workflow
        assert "DESIGN" in feature_workflow["required_tasks"]
        assert "IMPLEMENTATION" in feature_workflow["required_tasks"]
        assert "TESTING" in feature_workflow["required_tasks"]
        assert "DOCUMENTATION" in feature_workflow["required_tasks"]
    
    def test_write_skill_to_filesystem(self, generator, tmp_path):
        """Test writing skill to filesystem."""
        skill = SkillDefinition(
            name="Test Skill",
            description="A test skill",
            category=SkillCategory.PROJECT_MANAGEMENT,
            instructions="Test instructions",
            supporting_files={"test.txt": "Test content"}
        )
        
        generator._write_skill_to_filesystem(skill, tmp_path)
        
        # Check skill directory was created
        skill_dir = tmp_path / skill.get_skill_directory_name()
        assert skill_dir.exists()
        assert skill_dir.is_dir()
        
        # Check SKILL.md was created
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.exists()
        assert "Test Skill" in skill_file.read_text()
        
        # Check supporting file was created
        support_file = skill_dir / "test.txt"
        assert support_file.exists()
        assert support_file.read_text() == "Test content"
        
        # Check metadata was created
        metadata_file = skill_dir / "metadata.json"
        assert metadata_file.exists()
        metadata = metadata_file.read_text()
        assert "Test Skill" in metadata
        assert "project-management" in metadata


class TestSkillsIntegration:
    """Test skills module integration."""
    
    def test_skills_module_imports(self):
        """Test that skills module can be imported."""
        from agentpm.providers.anthropic.skills import (
            ClaudeCodeSkillGenerator,
            SkillDefinition,
            SkillTemplate,
            SkillRegistry,
            get_skill_template
        )
        
        # Test that all imports work
        assert ClaudeCodeSkillGenerator is not None
        assert SkillDefinition is not None
        assert SkillTemplate is not None
        assert SkillRegistry is not None
        assert get_skill_template is not None
    
    def test_get_skill_template(self):
        """Test getting skill templates."""
        from agentpm.providers.anthropic.skills import get_skill_template
        
        # Test getting project manager template
        template = get_skill_template("project-manager")
        assert template is not None
        assert template.template_id == "project-manager"
        assert template.category == SkillCategory.PROJECT_MANAGEMENT
        
        # Test getting non-existent template
        template = get_skill_template("non-existent")
        assert template is None
