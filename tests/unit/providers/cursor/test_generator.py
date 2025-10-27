"""
Tests for CursorGenerator

Validates Cursor-specific configuration generation from AGENTS.md.

Test Coverage:
- Generator initialization
- .cursorrules generation (plain text transformation)
- .cursorignore generation (CommonExclusions.CURSOR)
- Agent grouping by functional category
- Configuration validation
- Context formatting
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from agentpm.providers.cursor.generator import CursorGenerator
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule
from agentpm.core.database.models.project import Project
from agentpm.core.database.enums import (
    AgentFunctionalCategory,
    EnforcementLevel,
)


@pytest.fixture
def mock_db_service():
    """Create mock database service"""
    return Mock()


@pytest.fixture
def sample_project():
    """Create sample project for testing"""
    return Project(
        id=1,
        name="TestProject",
        description="A test project for Cursor generation",
        tech_stack=["python", "sqlite", "pytest"],
        path="/test/project"
    )


@pytest.fixture
def sample_agents():
    """Create sample agents grouped by functional category"""
    return [
        Agent(
            id=1,
            project_id=1,
            role="aipm-python-cli-developer",
            display_name="Python CLI Developer",
            description="Implements Python CLI commands",
            sop_content="Follow TDD and write tests first",
            capabilities=["python", "cli", "testing"],
            functional_category=AgentFunctionalCategory.IMPLEMENTATION,
            is_active=True
        ),
        Agent(
            id=2,
            project_id=1,
            role="aipm-testing-specialist",
            display_name="Testing Specialist",
            description="Creates comprehensive test suites",
            sop_content="Write AAA pattern tests with fixtures",
            capabilities=["pytest", "coverage", "fixtures"],
            functional_category=AgentFunctionalCategory.TESTING,
            is_active=True
        ),
        Agent(
            id=3,
            project_id=1,
            role="planning-orch",
            display_name="Planning Orchestrator",
            description="Breaks down work into tasks",
            sop_content="Create tasks with acceptance criteria",
            capabilities=["planning", "task-breakdown"],
            functional_category=AgentFunctionalCategory.PLANNING,
            is_active=True
        ),
        Agent(
            id=4,
            project_id=1,
            role="inactive-agent",
            display_name="Inactive Agent",
            description="Should not be included",
            sop_content="Should be filtered out",
            capabilities=[],
            functional_category=AgentFunctionalCategory.UTILITIES,
            is_active=False  # Inactive
        ),
    ]


@pytest.fixture
def sample_rules():
    """Create sample rules for testing"""
    return [
        Rule(
            id=1,
            project_id=1,
            rule_id="DP-001",
            name="hexagonal-architecture",
            description="Use hexagonal architecture pattern",
            enforcement_level=EnforcementLevel.BLOCK,
            category="development_principles",
            guidance="Separate core logic from adapters",
            enabled=True
        ),
        Rule(
            id=2,
            project_id=1,
            rule_id="TES-001",
            name="test-coverage",
            description="Maintain >90% test coverage",
            enforcement_level=EnforcementLevel.LIMIT,
            category="testing_standards",
            guidance="Write tests before implementation",
            enabled=True
        ),
    ]


class TestCursorGeneratorInit:
    """Test CursorGenerator initialization"""

    def test_init_with_valid_db_service(self, mock_db_service):
        """Should initialize with valid database service"""
        generator = CursorGenerator(mock_db_service)

        assert generator.db == mock_db_service
        assert generator.provider_name == "cursor"
        assert generator.config_directory == ""
        assert generator.env is not None  # Jinja2 environment initialized

    def test_init_creates_jinja2_environment(self, mock_db_service):
        """Should create Jinja2 environment with correct settings"""
        generator = CursorGenerator(mock_db_service)

        # Verify environment exists
        assert hasattr(generator, 'env')

        # Verify filters are registered
        assert 'kebab_case' in generator.env.filters
        assert 'snake_case' in generator.env.filters
        assert 'flatten_agents' in generator.env.filters


class TestCursorGeneratorProperties:
    """Test CursorGenerator properties"""

    def test_provider_name(self, mock_db_service):
        """Should return 'cursor' as provider name"""
        generator = CursorGenerator(mock_db_service)
        assert generator.provider_name == "cursor"

    def test_config_directory(self, mock_db_service):
        """Should return empty string (files at project root)"""
        generator = CursorGenerator(mock_db_service)
        assert generator.config_directory == ""


class TestGenerateFromAgents:
    """Test generate_from_agents method"""

    def test_generate_from_agents_success(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should generate both .cursorrules and .cursorignore successfully"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        assert result.success is True
        assert len(result.files) == 2
        assert len(result.errors) == 0
        assert result.statistics["agents_generated"] == 4
        assert result.statistics["rules_included"] == 2

    def test_generate_creates_cursorrules_file(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should create .cursorrules file at project root"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        cursorrules_path = tmp_path / ".cursorrules"
        assert cursorrules_path.exists()

        content = cursorrules_path.read_text(encoding="utf-8")
        assert "TestProject" in content
        assert "hexagonal-architecture" in content or "Hexagonal Architecture" in content
        assert "IMPLEMENTATION EXPERT MODE" in content

    def test_generate_creates_cursorignore_file(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should create .cursorignore file at project root"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        cursorignore_path = tmp_path / ".cursorignore"
        assert cursorignore_path.exists()

        content = cursorignore_path.read_text(encoding="utf-8")
        assert ".agentpm/" in content
        assert ".git/" in content
        assert ".cursor/" in content

    def test_generate_filters_inactive_agents(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should exclude inactive agents from .cursorrules"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        cursorrules_path = tmp_path / ".cursorrules"
        content = cursorrules_path.read_text(encoding="utf-8")

        # Active agents should be present
        assert "Python CLI Developer" in content
        assert "Testing Specialist" in content

        # Inactive agent should NOT be present
        assert "Inactive Agent" not in content

    def test_generate_groups_agents_by_category(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should group agents by functional category in .cursorrules"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        cursorrules_path = tmp_path / ".cursorrules"
        content = cursorrules_path.read_text(encoding="utf-8")

        # Check category headers
        assert "PLANNING EXPERT MODE" in content
        assert "IMPLEMENTATION EXPERT MODE" in content
        assert "TESTING EXPERT MODE" in content

    def test_generate_includes_all_rules(
        self, mock_db_service, sample_project, sample_agents, sample_rules, tmp_path
    ):
        """Should include all rules in .cursorrules"""
        generator = CursorGenerator(mock_db_service)

        result = generator.generate_from_agents(
            agents=sample_agents,
            rules=sample_rules,
            project=sample_project,
            output_dir=tmp_path
        )

        cursorrules_path = tmp_path / ".cursorrules"
        content = cursorrules_path.read_text(encoding="utf-8")

        # Check all rules are present (check description, not name)
        assert "Use hexagonal architecture pattern" in content
        assert "Maintain >90% test coverage" in content
        assert "BLOCK" in content
        assert "LIMIT" in content


class TestGroupAgentsByCategory:
    """Test _group_agents_by_category method"""

    def test_group_agents_by_category(self, mock_db_service, sample_agents):
        """Should group agents by functional category correctly"""
        generator = CursorGenerator(mock_db_service)

        grouped = generator._group_agents_by_category(sample_agents)

        assert len(grouped["planning"]) == 1
        assert len(grouped["implementation"]) == 1
        assert len(grouped["testing"]) == 1
        assert len(grouped["documentation"]) == 0
        assert len(grouped["utilities"]) == 0  # Inactive agent filtered

    def test_group_filters_inactive_agents(self, mock_db_service, sample_agents):
        """Should exclude inactive agents from grouping"""
        generator = CursorGenerator(mock_db_service)

        grouped = generator._group_agents_by_category(sample_agents)

        # Inactive agent should not appear in any category
        all_agents = []
        for agents in grouped.values():
            all_agents.extend(agents)

        assert len(all_agents) == 3  # Only 3 active agents

    def test_group_handles_none_category(self, mock_db_service):
        """Should default to utilities for agents without category"""
        agent_no_category = Agent(
            id=1,
            project_id=1,
            role="no-category-agent",
            display_name="No Category Agent",
            description="Agent without functional_category",
            functional_category=None,  # No category
            is_active=True
        )

        generator = CursorGenerator(mock_db_service)
        grouped = generator._group_agents_by_category([agent_no_category])

        assert len(grouped["utilities"]) == 1
        assert grouped["utilities"][0].role == "no-category-agent"


class TestValidateConfig:
    """Test validate_config method"""

    def test_validate_config_success(self, mock_db_service, tmp_path):
        """Should validate correct configuration without errors"""
        # Create valid files
        (tmp_path / ".cursorrules").write_text("Valid rules", encoding="utf-8")
        (tmp_path / ".cursorignore").write_text("*.pyc", encoding="utf-8")

        generator = CursorGenerator(mock_db_service)
        errors = generator.validate_config(tmp_path)

        assert len(errors) == 0

    def test_validate_config_missing_cursorrules(self, mock_db_service, tmp_path):
        """Should report error if .cursorrules is missing"""
        generator = CursorGenerator(mock_db_service)
        errors = generator.validate_config(tmp_path)

        assert len(errors) == 1
        assert ".cursorrules file not found" in errors[0]

    def test_validate_config_invalid_utf8_cursorrules(self, mock_db_service, tmp_path):
        """Should report error if .cursorrules is not valid UTF-8"""
        # Write invalid UTF-8
        (tmp_path / ".cursorrules").write_bytes(b'\xff\xfe\xfd')

        generator = CursorGenerator(mock_db_service)
        errors = generator.validate_config(tmp_path)

        assert len(errors) > 0
        assert any("UTF-8" in error for error in errors)

    def test_validate_config_cursorignore_optional(self, mock_db_service, tmp_path):
        """Should not error if .cursorignore is missing"""
        # Only create .cursorrules
        (tmp_path / ".cursorrules").write_text("Valid rules", encoding="utf-8")

        generator = CursorGenerator(mock_db_service)
        errors = generator.validate_config(tmp_path)

        assert len(errors) == 0

    def test_validate_config_invalid_utf8_cursorignore(self, mock_db_service, tmp_path):
        """Should report error if .cursorignore exists but is not valid UTF-8"""
        (tmp_path / ".cursorrules").write_text("Valid rules", encoding="utf-8")
        (tmp_path / ".cursorignore").write_bytes(b'\xff\xfe\xfd')

        generator = CursorGenerator(mock_db_service)
        errors = generator.validate_config(tmp_path)

        assert len(errors) > 0
        assert any("cursorignore" in error.lower() for error in errors)


class TestFormatContext:
    """Test format_context method"""

    def test_format_context_with_project_only(self, mock_db_service, sample_project):
        """Should format context with project info only"""
        generator = CursorGenerator(mock_db_service)

        context = generator.format_context(
            project=sample_project,
            work_item=None,
            task=None
        )

        assert "=== CURRENT CONTEXT ===" in context
        assert "Project: TestProject" in context
        assert "Description: A test project" in context

    def test_format_context_with_work_item(self, mock_db_service, sample_project):
        """Should format context with work item info"""
        work_item = Mock()
        work_item.id = 123
        work_item.name = "Implement feature X"
        work_item.phase = "I1_implementation"
        work_item.status = "in_progress"

        generator = CursorGenerator(mock_db_service)
        context = generator.format_context(
            project=sample_project,
            work_item=work_item,
            task=None
        )

        assert "Work Item: #123 - Implement feature X" in context
        assert "Phase: I1_implementation" in context
        assert "Status: in_progress" in context

    def test_format_context_with_task(self, mock_db_service, sample_project):
        """Should format context with task info"""
        task = Mock()
        task.id = 456
        task.name = "Write unit tests"
        task.type = "testing"
        task.status = "in_progress"

        generator = CursorGenerator(mock_db_service)
        context = generator.format_context(
            project=sample_project,
            work_item=None,
            task=task
        )

        assert "Task: #456 - Write unit tests" in context
        assert "Type: testing" in context
        assert "Status: in_progress" in context

    def test_format_context_complete(self, mock_db_service, sample_project):
        """Should format context with all info (project + work item + task)"""
        work_item = Mock()
        work_item.id = 123
        work_item.name = "Implement feature X"
        work_item.phase = "I1_implementation"
        work_item.status = "in_progress"

        task = Mock()
        task.id = 456
        task.name = "Write unit tests"
        task.type = "testing"
        task.status = "in_progress"

        generator = CursorGenerator(mock_db_service)
        context = generator.format_context(
            project=sample_project,
            work_item=work_item,
            task=task
        )

        # Should contain all sections
        assert "Project: TestProject" in context
        assert "Work Item: #123" in context
        assert "Task: #456" in context
