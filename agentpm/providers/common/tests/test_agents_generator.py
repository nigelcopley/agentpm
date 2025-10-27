"""
Tests for AGENTS.md Generator

Tests the AGENTSMDGenerator class to ensure it correctly generates
the universal AGENTS.md format from database entities.

Coverage:
- Context building from database
- YAML frontmatter generation
- Agent directory generation (by functional_category)
- Development standards generation (by rule category)
- Work context generation (active work item + task)
- Provider-specific instruction blocks
- File output (optional)

Pattern: pytest with fixtures for database setup
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models import Agent, Rule, Project, WorkItem, Task
from agentpm.core.database.enums import (
    AgentFunctionalCategory,
    EnforcementLevel,
    WorkItemStatus,
    WorkItemType,
    TaskStatus,
    TaskType,
    Phase,
)
from agentpm.providers.common.agents_generator import AGENTSMDGenerator


@pytest.fixture
def mock_db_service():
    """Create mock DatabaseService for testing."""
    return MagicMock(spec=DatabaseService)


@pytest.fixture
def sample_project():
    """Create sample project for testing."""
    return Project(
        id=1,
        name="TestProject",
        description="Test project for AGENTS.md generation",
        path="/test/project",
        tech_stack=["Python", "SQLite"],
        detected_frameworks=["pytest"],
    )


@pytest.fixture
def sample_agents():
    """Create sample agents across all functional categories."""
    return [
        Agent(
            id=1,
            project_id=1,
            role="definition-orch",
            display_name="Definition Orchestrator",
            description="Requirements gathering and 6W analysis",
            functional_category=AgentFunctionalCategory.PLANNING,
            is_active=True,
        ),
        Agent(
            id=2,
            project_id=1,
            role="aipm-python-cli-developer",
            display_name="APM Python CLI Developer",
            description="Python CLI command implementation specialist",
            functional_category=AgentFunctionalCategory.IMPLEMENTATION,
            is_active=True,
        ),
        Agent(
            id=3,
            project_id=1,
            role="aipm-testing-specialist",
            display_name="APM Testing Specialist",
            description="Test creation and coverage analysis",
            functional_category=AgentFunctionalCategory.TESTING,
            is_active=True,
        ),
        Agent(
            id=4,
            project_id=1,
            role="aipm-documentation-specialist",
            display_name="APM Documentation Specialist",
            description="Documentation writing and curation",
            functional_category=AgentFunctionalCategory.DOCUMENTATION,
            is_active=True,
        ),
        Agent(
            id=5,
            project_id=1,
            role="context-delivery",
            display_name="Context Delivery",
            description="Context assembly and session initialization",
            functional_category=AgentFunctionalCategory.UTILITIES,
            is_active=True,
        ),
        # Agent without functional_category (for uncategorized test)
        Agent(
            id=6,
            project_id=1,
            role="legacy-agent",
            display_name="Legacy Agent",
            description="Agent without functional category",
            functional_category=None,
            is_active=True,
        ),
    ]


@pytest.fixture
def sample_rules():
    """Create sample rules across different categories."""
    return [
        Rule(
            id=1,
            project_id=1,
            rule_id="DP-001",
            name="hexagonal-architecture",
            description="Use hexagonal architecture pattern",
            category="development_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            enabled=True,
        ),
        Rule(
            id=2,
            project_id=1,
            rule_id="TES-001",
            name="project-relative-imports",
            description="Use project-relative imports in tests",
            category="testing_standards",
            enforcement_level=EnforcementLevel.GUIDE,
            enabled=True,
        ),
        Rule(
            id=3,
            project_id=1,
            rule_id="SEC-001",
            name="input-validation",
            description="Validate all user inputs",
            category="security_requirements",
            enforcement_level=EnforcementLevel.BLOCK,
            enabled=True,
        ),
    ]


@pytest.fixture
def sample_work_item():
    """Create sample work item for context."""
    return WorkItem(
        id=100,
        project_id=1,
        name="Implement AGENTS.md Generator",
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.ACTIVE,
        phase=Phase.I1_IMPLEMENTATION,
        business_context="Generate universal agent directory from database",
        priority=1,
        effort_estimate_hours=8.0,
    )


@pytest.fixture
def sample_task():
    """Create sample task for context."""
    return Task(
        id=200,
        work_item_id=100,
        project_id=1,
        name="Create AGENTSMDGenerator class",
        type=TaskType.IMPLEMENTATION,
        status=TaskStatus.ACTIVE,
        description="Implement generator with database queries and markdown output",
        priority=1,
        effort_hours=4.0,
        assigned_to="aipm-python-cli-developer",
        quality_metadata={"tests_passing": True, "coverage_percent": 95},
    )


class TestAGENTSMDGenerator:
    """Test suite for AGENTSMDGenerator."""

    def test_init(self, mock_db_service):
        """Test generator initialization."""
        generator = AGENTSMDGenerator(mock_db_service)
        assert generator.db == mock_db_service

    @patch('agentpm.providers.common.agents_generator.project_methods')
    @patch('agentpm.providers.common.agents_generator.agent_methods')
    @patch('agentpm.providers.common.agents_generator.rule_methods')
    @patch('agentpm.providers.common.agents_generator.work_item_methods')
    @patch('agentpm.providers.common.agents_generator.task_methods')
    def test_build_universal_context(
        self,
        mock_task_methods,
        mock_work_item_methods,
        mock_rule_methods,
        mock_agent_methods,
        mock_project_methods,
        mock_db_service,
        sample_project,
        sample_agents,
        sample_rules,
        sample_work_item,
        sample_task,
    ):
        """Test building UniversalContext from database."""
        # Setup mocks
        mock_project_methods.get_project.return_value = sample_project
        mock_agent_methods.list_agents.return_value = sample_agents
        mock_rule_methods.list_rules.return_value = sample_rules
        mock_work_item_methods.list_work_items.return_value = [sample_work_item]
        mock_task_methods.list_tasks.return_value = [sample_task]

        # Generate context
        generator = AGENTSMDGenerator(mock_db_service)
        context = generator._build_universal_context(project_id=1, provider="claude-code")

        # Verify context structure
        assert context.version == "1.0"
        assert context.project.id == 1
        assert context.project.name == "TestProject"
        assert len(context.agents) == 6
        assert len(context.rules) == 3
        assert context.work_item is not None
        assert context.work_item.id == 100
        assert context.task is not None
        assert context.task.id == 200

    def test_generate_frontmatter(self, mock_db_service):
        """Test YAML frontmatter generation."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(
                id=1,
                name="TestProject",
                tech_stack=["Python", "SQLite"],
            ),
            generated=datetime(2025, 10, 27, 10, 30, 0),
            providers=["claude-code"],
            tech_stack=["Python", "SQLite"],  # Add tech_stack to context
        )

        frontmatter = generator._generate_frontmatter(context)

        # Verify frontmatter structure
        assert "---" in frontmatter
        assert 'version: "1.0"' in frontmatter
        assert "architecture: flat" in frontmatter
        # Check for ISO format timestamp (not exact match due to milliseconds)
        assert "2025-10-27" in frontmatter
        assert "id: 1" in frontmatter
        assert 'name: "TestProject"' in frontmatter
        assert '"Python"' in frontmatter
        assert '"SQLite"' in frontmatter

    def test_generate_header(self, mock_db_service, sample_agents, sample_rules):
        """Test header section generation."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime(2025, 10, 27, 10, 30, 0),
            providers=["claude-code"],
            agents=sample_agents,
            rules=sample_rules,
        )

        header = generator._generate_header(context)

        # Verify header content
        assert "# APM Agent System" in header
        assert "TestProject" in header
        assert "Total Active Agents**: 6" in header
        assert "Active Rules**: 3" in header
        assert "2025-10-27 10:30:00" in header

    def test_generate_agent_directory(self, mock_db_service, sample_agents):
        """Test agent directory generation with functional categories."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime.utcnow(),
            providers=["claude-code"],
            agents=sample_agents,
        )

        directory = generator._generate_agent_directory(context)

        # Verify directory structure
        assert "## Subagent Directory (Flat - Organized by Function)" in directory

        # Verify category headers
        assert "### Planning & Analysis (1)" in directory
        assert "### Implementation (1)" in directory
        assert "### Testing & Quality (1)" in directory
        assert "### Documentation (1)" in directory
        assert "### Utilities (1)" in directory
        assert "### Uncategorized (1)" in directory

        # Verify agent entries
        assert "- **definition-orch**: Definition Orchestrator" in directory
        assert "- **aipm-python-cli-developer**: APM Python CLI Developer" in directory
        assert "- **aipm-testing-specialist**: APM Testing Specialist" in directory
        assert "- **aipm-documentation-specialist**: APM Documentation Specialist" in directory
        assert "- **context-delivery**: Context Delivery" in directory
        assert "- **legacy-agent**: Legacy Agent" in directory

    def test_generate_development_standards(self, mock_db_service, sample_rules):
        """Test development standards generation with rule categories."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime.utcnow(),
            providers=["claude-code"],
            rules=sample_rules,
        )

        standards = generator._generate_development_standards(context)

        # Verify standards structure
        assert "## Development Standards" in standards

        # Verify category headers
        assert "### Development Principles" in standards
        assert "### Testing Standards" in standards
        assert "### Security Requirements" in standards

        # Verify rule entries
        assert "- **DP-001** (BLOCK):" in standards
        assert "- **TES-001** (GUIDE):" in standards
        assert "- **SEC-001** (BLOCK):" in standards

    def test_generate_work_context(self, mock_db_service, sample_work_item, sample_task):
        """Test work context generation with active work item and task."""
        from agentpm.providers.common.patterns import (
            ProjectContext,
            UniversalContext,
            WorkItemContext,
            TaskContext,
        )

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime.utcnow(),
            providers=["claude-code"],
            work_item=WorkItemContext(
                id=100,
                name="Implement AGENTS.md Generator",
                type="feature",
                status="active",
                phase="I1_IMPLEMENTATION",
                business_context="Generate universal agent directory",
                priority=1,
                effort_estimate_hours=8.0,
            ),
            task=TaskContext(
                id=200,
                name="Create AGENTSMDGenerator class",
                type="implementation",
                status="active",
                description="Implement generator",
                priority=1,
                effort_hours=4.0,
                assigned_to="aipm-python-cli-developer",
                quality_metadata={"tests_passing": True},
            ),
        )

        work_context = generator._generate_work_context(context)

        # Verify work context structure
        assert "## Current Work Context" in work_context
        assert "### Active Work Item: #100" in work_context
        assert "Implement AGENTS.md Generator" in work_context
        assert "### Current Task: #200" in work_context
        assert "Create AGENTSMDGenerator class" in work_context
        assert "aipm-python-cli-developer" in work_context

    def test_generate_work_context_empty(self, mock_db_service):
        """Test work context generation with no active work."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime.utcnow(),
            providers=["claude-code"],
            work_item=None,
            task=None,
        )

        work_context = generator._generate_work_context(context)

        # Should return empty string
        assert work_context == ""

    def test_generate_provider_instructions(self, mock_db_service):
        """Test provider-specific instruction blocks."""
        from agentpm.providers.common.patterns import ProjectContext, UniversalContext

        generator = AGENTSMDGenerator(mock_db_service)

        context = UniversalContext(
            version="1.0",
            project=ProjectContext(id=1, name="TestProject"),
            generated=datetime.utcnow(),
            providers=["claude-code"],
        )

        instructions = generator._generate_provider_instructions(context, "claude-code")

        # Verify provider-specific blocks
        assert "## Provider-Specific Instructions" in instructions

        # Claude Code block
        assert "<!-- [CLAUDE_CODE] -->" in instructions
        assert "<!-- [/CLAUDE_CODE] -->" in instructions
        assert "Task(" in instructions

        # Cursor block
        assert "<!-- [CURSOR] -->" in instructions
        assert "<!-- [/CURSOR] -->" in instructions

        # Codex block
        assert "<!-- [CODEX] -->" in instructions
        assert "<!-- [/CODEX] -->" in instructions

        # Gemini block
        assert "<!-- [GEMINI] -->" in instructions
        assert "<!-- [/GEMINI] -->" in instructions

    @patch('agentpm.providers.common.agents_generator.project_methods')
    @patch('agentpm.providers.common.agents_generator.agent_methods')
    @patch('agentpm.providers.common.agents_generator.rule_methods')
    @patch('agentpm.providers.common.agents_generator.work_item_methods')
    @patch('agentpm.providers.common.agents_generator.task_methods')
    def test_generate_full_content(
        self,
        mock_task_methods,
        mock_work_item_methods,
        mock_rule_methods,
        mock_agent_methods,
        mock_project_methods,
        mock_db_service,
        sample_project,
        sample_agents,
        sample_rules,
        sample_work_item,
        sample_task,
    ):
        """Test full AGENTS.md generation."""
        # Setup mocks
        mock_project_methods.get_project.return_value = sample_project
        mock_agent_methods.list_agents.return_value = sample_agents
        mock_rule_methods.list_rules.return_value = sample_rules
        mock_work_item_methods.list_work_items.return_value = [sample_work_item]
        mock_task_methods.list_tasks.return_value = [sample_task]

        # Generate content
        generator = AGENTSMDGenerator(mock_db_service)
        content = generator.generate(project_id=1, provider="claude-code")

        # Verify content structure
        assert content.startswith("---")
        assert "# APM Agent System" in content
        assert "## Subagent Directory" in content
        assert "## Development Standards" in content
        assert "## Current Work Context" in content
        assert "## Provider-Specific Instructions" in content

    @patch('agentpm.providers.common.agents_generator.project_methods')
    @patch('agentpm.providers.common.agents_generator.agent_methods')
    @patch('agentpm.providers.common.agents_generator.rule_methods')
    @patch('agentpm.providers.common.agents_generator.work_item_methods')
    @patch('agentpm.providers.common.agents_generator.task_methods')
    def test_generate_with_file_output(
        self,
        mock_task_methods,
        mock_work_item_methods,
        mock_rule_methods,
        mock_agent_methods,
        mock_project_methods,
        mock_db_service,
        sample_project,
        sample_agents,
        sample_rules,
        tmp_path,
    ):
        """Test AGENTS.md generation with file output."""
        # Setup mocks (no active work)
        mock_project_methods.get_project.return_value = sample_project
        mock_agent_methods.list_agents.return_value = sample_agents
        mock_rule_methods.list_rules.return_value = sample_rules
        mock_work_item_methods.list_work_items.return_value = []
        mock_task_methods.list_tasks.return_value = []

        # Generate with file output
        output_path = tmp_path / "AGENTS.md"
        generator = AGENTSMDGenerator(mock_db_service)
        content = generator.generate(
            project_id=1,
            output_path=output_path,
            provider="claude-code"
        )

        # Verify file was created
        assert output_path.exists()

        # Verify file content matches returned content
        file_content = output_path.read_text(encoding='utf-8')
        assert file_content == content

    @patch('agentpm.providers.common.agents_generator.project_methods')
    def test_generate_project_not_found(self, mock_project_methods, mock_db_service):
        """Test error handling when project not found."""
        mock_project_methods.get_project.return_value = None

        generator = AGENTSMDGenerator(mock_db_service)

        with pytest.raises(ValueError, match="Project 999 not found"):
            generator.generate(project_id=999)
