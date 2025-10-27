"""
Unit tests for CodexGenerator class.

Tests configuration generation for OpenAI Codex including:
- config.toml generation
- .codexignore generation
- AGENTS.md validation
- Configuration validation
- Context formatting
- Error handling

Coverage target: >90%
Pattern: AAA (Arrange-Act-Assert)
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys

# Python 3.11+ has tomllib built-in, older versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from agentpm.providers.openai.codex.generator import CodexGenerator
from agentpm.providers.base import GenerationResult, FileOutput
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule
from agentpm.core.database.models.project import Project
from agentpm.core.database.enums import (
    AgentTier,
    AgentFunctionalCategory,
    EnforcementLevel,
    ProjectStatus
)


class TestCodexGeneratorBasics:
    """Test basic CodexGenerator functionality."""

    def test_provider_name(self, db_service):
        """
        GIVEN CodexGenerator instance
        WHEN accessing provider_name property
        THEN returns 'codex'
        """
        # Arrange
        generator = CodexGenerator(db_service)

        # Act
        name = generator.provider_name

        # Assert
        assert name == "codex"

    def test_config_directory(self, db_service):
        """
        GIVEN CodexGenerator instance
        WHEN accessing config_directory property
        THEN returns '.codex'
        """
        # Arrange
        generator = CodexGenerator(db_service)

        # Act
        directory = generator.config_directory

        # Assert
        assert directory == ".codex"

    def test_initialization_with_valid_db(self, db_service):
        """
        GIVEN valid DatabaseService
        WHEN creating CodexGenerator
        THEN initialization succeeds
        """
        # Arrange & Act
        generator = CodexGenerator(db_service)

        # Assert
        assert generator.db == db_service
        assert generator.provider_name == "codex"
        assert hasattr(generator, 'env')  # Jinja2 environment initialized


class TestCodexGeneratorConfigToml:
    """Test config.toml generation."""

    def test_generate_config_toml_success(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN valid agents, rules, and project
        WHEN generating config.toml
        THEN file is created successfully
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        assert result.success is True
        assert len(result.errors) == 0
        assert len(result.files) >= 1  # At least config.toml

        # Verify config.toml exists
        config_toml = output_dir / ".codex" / "config.toml"
        assert config_toml.exists()

    def test_config_toml_content_valid(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN generated config.toml
        WHEN parsing with tomli
        THEN content is valid TOML
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        config_toml = output_dir / ".codex" / "config.toml"
        with open(config_toml, "rb") as f:
            config = tomllib.load(f)

        assert "model" in config
        assert "approval_policy" in config
        assert "sandbox_mode" in config
        assert "profiles" in config

    def test_config_toml_has_required_profiles(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN generated config.toml
        WHEN checking profiles section
        THEN planning, implementation, testing profiles exist
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        config_toml = output_dir / ".codex" / "config.toml"
        with open(config_toml, "rb") as f:
            config = tomllib.load(f)

        assert "planning" in config["profiles"]
        assert "implementation" in config["profiles"]
        assert "testing" in config["profiles"]
        assert "documentation" in config["profiles"]
        assert "review" in config["profiles"]

    def test_config_toml_planning_profile_uses_o3(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN generated config.toml
        WHEN checking planning profile
        THEN uses o3 model with high reasoning effort
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        config_toml = output_dir / ".codex" / "config.toml"
        with open(config_toml, "rb") as f:
            config = tomllib.load(f)

        planning = config["profiles"]["planning"]
        assert planning["model"] == "o3"
        assert planning["model_reasoning_effort"] == "high"
        assert planning["sandbox_mode"] == "read-only"

    def test_config_toml_custom_model(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN custom model specified in kwargs
        WHEN generating config.toml
        THEN custom model is used
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir,
            model="gpt-4o"
        )

        # Assert
        config_toml = output_dir / ".codex" / "config.toml"
        with open(config_toml, "rb") as f:
            config = tomllib.load(f)

        assert config["model"] == "gpt-4o"


class TestCodexGeneratorCodexignore:
    """Test .codexignore generation."""

    def test_generate_codexignore_success(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN valid project
        WHEN generating .codexignore
        THEN file is created with exclusion patterns
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        codexignore = output_dir / ".codex" / ".codexignore"
        assert codexignore.exists()

        content = codexignore.read_text()
        assert ".agentpm/" in content
        assert ".git/" in content
        assert "__pycache__/" in content
        assert ".codex/" in content

    def test_codexignore_optional(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN include_ignore=False
        WHEN generating configuration
        THEN .codexignore is not created
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir,
            include_ignore=False
        )

        # Assert
        codexignore = output_dir / ".codex" / ".codexignore"
        assert not codexignore.exists()


class TestCodexGeneratorValidation:
    """Test configuration validation."""

    def test_validate_config_success(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN valid Codex configuration
        WHEN validating
        THEN no errors returned
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Generate config first
        generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Create AGENTS.md (required by Codex)
        agents_md = output_dir / "AGENTS.md"
        agents_md.write_text("# AGENTS.md\nProject instructions here.")

        # Act
        errors = generator.validate_config(output_dir / ".codex")

        # Assert
        assert len(errors) == 0

    def test_validate_config_missing_directory(self, db_service, tmp_path):
        """
        GIVEN .codex directory does not exist
        WHEN validating
        THEN error is returned
        """
        # Arrange
        generator = CodexGenerator(db_service)
        nonexistent_dir = tmp_path / "nonexistent" / ".codex"

        # Act
        errors = generator.validate_config(nonexistent_dir)

        # Assert
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_validate_config_missing_agents_md(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN AGENTS.md does not exist
        WHEN validating
        THEN error is returned (required by Codex)
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Generate config without AGENTS.md
        generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Act
        errors = generator.validate_config(output_dir / ".codex")

        # Assert
        assert any("AGENTS.md" in error for error in errors)

    def test_validate_config_missing_config_toml(self, db_service, tmp_path):
        """
        GIVEN config.toml does not exist
        WHEN validating
        THEN error is returned
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        codex_dir = output_dir / ".codex"
        codex_dir.mkdir(parents=True)

        # Act
        errors = generator.validate_config(codex_dir)

        # Assert
        assert any("config.toml" in error for error in errors)

    def test_validate_config_invalid_toml(self, db_service, tmp_path):
        """
        GIVEN invalid TOML in config.toml
        WHEN validating
        THEN error is returned
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        codex_dir = output_dir / ".codex"
        codex_dir.mkdir(parents=True)

        # Create invalid TOML
        config_toml = codex_dir / "config.toml"
        config_toml.write_text("invalid [toml content")

        # Act
        errors = generator.validate_config(codex_dir)

        # Assert
        assert any("Invalid config.toml" in error for error in errors)


class TestCodexGeneratorContextFormatting:
    """Test context formatting for real-time updates."""

    def test_format_context_with_project_only(self, db_service, sample_project):
        """
        GIVEN project context
        WHEN formatting context
        THEN project information is included
        """
        # Arrange
        generator = CodexGenerator(db_service)

        # Act
        context = generator.format_context(sample_project, None, None)

        # Assert
        assert "## Current Context" in context
        assert sample_project.name in context
        assert "Project" in context

    def test_format_context_with_work_item(self, db_service, sample_project, sample_work_item):
        """
        GIVEN project and work item
        WHEN formatting context
        THEN both are included
        """
        # Arrange
        generator = CodexGenerator(db_service)

        # Act
        context = generator.format_context(sample_project, sample_work_item, None)

        # Assert
        assert "Current Work Item" in context
        assert str(sample_work_item.id) in context
        assert sample_work_item.name in context

    def test_format_context_with_task(self, db_service, sample_project, sample_work_item, sample_task):
        """
        GIVEN project, work item, and task
        WHEN formatting context
        THEN all are included
        """
        # Arrange
        generator = CodexGenerator(db_service)

        # Act
        context = generator.format_context(sample_project, sample_work_item, sample_task)

        # Assert
        assert "Current Task" in context
        assert str(sample_task.id) in context
        assert sample_task.name in context


class TestCodexGeneratorErrorHandling:
    """Test error handling and edge cases."""

    def test_generate_with_empty_agents(self, db_service, sample_rules, sample_project, tmp_path):
        """
        GIVEN no agents
        WHEN generating configuration
        THEN succeeds (agents not required for config.toml)
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=[],
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        assert result.success is True

    def test_generate_with_empty_rules(self, db_service, sample_agents, sample_project, tmp_path):
        """
        GIVEN no rules
        WHEN generating configuration
        THEN succeeds (rules not required for config.toml)
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=[],
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        assert result.success is True

    def test_generation_result_structure(self, db_service, sample_agents, sample_rules, sample_project, tmp_path):
        """
        GIVEN successful generation
        WHEN checking result
        THEN has correct structure with statistics
        """
        # Arrange
        generator = CodexGenerator(db_service)
        output_dir = tmp_path / "project"
        output_dir.mkdir()

        # Act
        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=output_dir
        )

        # Assert
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert isinstance(result.files, list)
        assert isinstance(result.errors, list)
        assert isinstance(result.statistics, dict)
        assert "duration_ms" in result.statistics
        assert "generation_time" in result.statistics


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_project():
    """Create sample project for testing."""
    return Project(
        id=1,
        name="Test Project",
        description="Test project description",
        path="/tmp/test-project",
        status=ProjectStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_agents(sample_project):
    """Create sample agents for testing."""
    return [
        Agent(
            id=1,
            project_id=sample_project.id,
            role="python-developer",
            display_name="Python Developer",
            description="Python development specialist",
            tier=AgentTier.TIER_2,
            functional_category=AgentFunctionalCategory.IMPLEMENTATION,
            sop_content="# Python Developer SOP\nDevelops Python code.",
            capabilities=["python", "testing", "documentation"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Agent(
            id=2,
            project_id=sample_project.id,
            role="testing-specialist",
            display_name="Testing Specialist",
            description="Testing and quality assurance",
            tier=AgentTier.TIER_2,
            functional_category=AgentFunctionalCategory.TESTING,
            sop_content="# Testing Specialist SOP\nCreates comprehensive tests.",
            capabilities=["pytest", "coverage", "tdd"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]


@pytest.fixture
def sample_rules():
    """Create sample rules for testing."""
    return [
        Rule(
            id=1,
            rule_id="DP-001",
            name="Hexagonal Architecture",
            description="Use hexagonal architecture pattern",
            category="development_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Rule(
            id=2,
            rule_id="TES-001",
            name="Test Coverage",
            description="Maintain >90% test coverage",
            category="testing_standards",
            enforcement_level=EnforcementLevel.LIMIT,
            enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]


@pytest.fixture
def sample_work_item():
    """Create sample work item for testing."""
    from agentpm.core.database.models.work_item import WorkItem
    from agentpm.core.database.enums import WorkItemType, WorkItemStatus, WorkItemPhase

    return WorkItem(
        id=100,
        name="Test Feature",
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.ACTIVE,
        phase=WorkItemPhase.I1_IMPLEMENTATION,
        business_context="Test business context",
        project_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_task():
    """Create sample task for testing."""
    from agentpm.core.database.models.task import Task
    from agentpm.core.database.enums import TaskType, TaskStatus

    return Task(
        id=200,
        name="Test Task",
        type=TaskType.IMPLEMENTATION,
        status=TaskStatus.ACTIVE,
        description="Test task description",
        work_item_id=100,
        effort_hours=2.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
