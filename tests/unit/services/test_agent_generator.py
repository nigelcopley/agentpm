"""
Tests for AgentGenerator service.

Tests the automatic agent file generation system that wraps the provider
generator architecture.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from agentpm.core.services.agent_generator import (
    AgentGeneratorService,
    AgentGenerationProgress,
    AgentGenerationSummary,
)
from agentpm.core.database.models import Agent
from agentpm.providers.generators.base import GenerationResult


@pytest.fixture
def mock_db():
    """Mock database service"""
    return Mock()


@pytest.fixture
def project_path(tmp_path):
    """Create temp project path with .claude directory"""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    return tmp_path


@pytest.fixture
def mock_agents():
    """Create mock agent list"""
    return [
        Agent(
            id=1,
            project_id=1,
            role="context-generator",
            display_name="Context Generator",
            description="Assembles session context",
            agent_type="utility",
            is_active=True
        ),
        Agent(
            id=2,
            project_id=1,
            role="database-query-agent",
            display_name="Database Query Agent",
            description="Executes database queries",
            agent_type="utility",
            is_active=True
        ),
        Agent(
            id=3,
            project_id=1,
            role="definition-orch",
            display_name="Definition Orchestrator",
            description="Orchestrates D1 phase",
            agent_type="orchestrator",
            is_active=True
        ),
    ]


@pytest.fixture
def mock_rules():
    """Create mock rules list"""
    from agentpm.core.database.models import Rule
    from agentpm.core.database.enums import EnforcementLevel

    return [
        Rule(
            id=1,
            project_id=1,
            rule_id="DP-001",
            name="time-boxing",
            description="Tasks limited to 4 hours",
            enforcement_level=EnforcementLevel.BLOCK,
            enabled=True
        ),
        Rule(
            id=2,
            project_id=1,
            rule_id="CI-004",
            name="testing-quality",
            description=">90% test coverage required",
            enforcement_level=EnforcementLevel.BLOCK,
            enabled=True
        ),
    ]


class TestAgentGeneratorServiceInit:
    """Test AgentGeneratorService initialization"""

    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_init_with_auto_detected_provider(
        self,
        mock_get_generator,
        mock_detect,
        mock_db,
        project_path
    ):
        """Test initialization with auto-detected provider"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_class = Mock()
        mock_get_generator.return_value = mock_generator_class

        # Create service
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )

        # Verify
        assert service.provider == "claude-code"
        mock_detect.assert_called_once_with(project_path)
        mock_get_generator.assert_called_once_with("claude-code")
        mock_generator_class.assert_called_once()

    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_init_with_explicit_provider(
        self,
        mock_get_generator,
        mock_detect,
        mock_db,
        project_path
    ):
        """Test initialization with explicitly specified provider"""
        # Setup mocks
        mock_generator_class = Mock()
        mock_get_generator.return_value = mock_generator_class

        # Create service with explicit provider
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1,
            provider="cursor"
        )

        # Verify
        assert service.provider == "cursor"
        mock_detect.assert_not_called()  # Should not auto-detect
        mock_get_generator.assert_called_once_with("cursor")

    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    def test_init_fails_if_no_provider_detected(
        self,
        mock_detect,
        mock_db,
        project_path
    ):
        """Test initialization fails if provider cannot be detected"""
        # Setup: detection returns None
        mock_detect.return_value = None

        # Verify raises
        with pytest.raises(RuntimeError, match="Could not detect LLM provider"):
            AgentGeneratorService(
                db=mock_db,
                project_path=project_path,
                project_id=1
            )

    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_init_fails_if_provider_not_available(
        self,
        mock_get_generator,
        mock_detect,
        mock_db,
        project_path
    ):
        """Test initialization fails if provider generator not available"""
        # Setup
        mock_detect.return_value = "claude-code"
        mock_get_generator.return_value = None  # Provider not available

        # Verify raises
        with pytest.raises(RuntimeError, match="Provider 'claude-code' not available"):
            AgentGeneratorService(
                db=mock_db,
                project_path=project_path,
                project_id=1
            )


class TestAgentGeneratorServiceGenerateAll:
    """Test AgentGeneratorService.generate_all()"""

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.RuleAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_all_success(
        self,
        mock_get_generator,
        mock_detect,
        mock_rule_adapter,
        mock_agent_adapter,
        mock_db,
        project_path,
        mock_agents,
        mock_rules
    ):
        """Test successful generation of all agents"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_instance = Mock()
        mock_generator_class = Mock(return_value=mock_generator_instance)
        mock_get_generator.return_value = mock_generator_class

        # Setup agent and rule adapters
        mock_agent_adapter.list.return_value = mock_agents
        mock_rule_adapter.list.return_value = mock_rules

        # Setup generator responses
        def mock_get_output_path(role, path):
            return path / ".claude" / "agents" / f"{role}.md"

        mock_generator_instance.get_output_path.side_effect = mock_get_output_path

        def mock_generate(context):
            return GenerationResult(
                agent_role=context.agent.role,
                output_path=mock_get_output_path(context.agent.role, project_path),
                content=f"# {context.agent.role}\n\nAgent SOP",
                success=True
            )

        mock_generator_instance.generate_agent_file.side_effect = mock_generate

        # Create service
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )

        # Generate all
        summary = service.generate_all()

        # Verify results
        assert summary.total_generated == 3
        assert summary.total_failed == 0
        assert len(summary.failed_agents) == 0

        # Verify files were written
        for agent in mock_agents:
            agent_file = project_path / ".claude" / "agents" / f"{agent.role}.md"
            assert agent_file.exists()
            content = agent_file.read_text()
            assert agent.role in content

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.RuleAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_all_no_agents(
        self,
        mock_get_generator,
        mock_detect,
        mock_rule_adapter,
        mock_agent_adapter,
        mock_db,
        project_path
    ):
        """Test generation when no agents in database"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_class = Mock()
        mock_get_generator.return_value = mock_generator_class

        # No agents in database
        mock_agent_adapter.list.return_value = []

        # Create service
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )

        # Generate all
        summary = service.generate_all()

        # Verify results
        assert summary.total_generated == 0
        assert summary.total_failed == 0
        assert len(summary.warnings) == 1
        assert "No agents found" in summary.warnings[0]

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.RuleAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_all_with_failures(
        self,
        mock_get_generator,
        mock_detect,
        mock_rule_adapter,
        mock_agent_adapter,
        mock_db,
        project_path,
        mock_agents,
        mock_rules
    ):
        """Test generation with some failures"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_instance = Mock()
        mock_generator_class = Mock(return_value=mock_generator_instance)
        mock_get_generator.return_value = mock_generator_class

        mock_agent_adapter.list.return_value = mock_agents
        mock_rule_adapter.list.return_value = mock_rules

        def mock_get_output_path(role, path):
            return path / ".claude" / "agents" / f"{role}.md"

        mock_generator_instance.get_output_path.side_effect = mock_get_output_path

        # Make first agent fail, others succeed
        def mock_generate(context):
            if context.agent.role == "context-generator":
                return GenerationResult(
                    agent_role=context.agent.role,
                    output_path=mock_get_output_path(context.agent.role, project_path),
                    content="",
                    success=False,
                    error="Mock generation error"
                )
            else:
                return GenerationResult(
                    agent_role=context.agent.role,
                    output_path=mock_get_output_path(context.agent.role, project_path),
                    content=f"# {context.agent.role}\n\nAgent SOP",
                    success=True
                )

        mock_generator_instance.generate_agent_file.side_effect = mock_generate

        # Create service and generate
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )
        summary = service.generate_all()

        # Verify
        assert summary.total_generated == 2
        assert summary.total_failed == 1
        assert "context-generator" in summary.failed_agents

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.RuleAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_all_progress_callback(
        self,
        mock_get_generator,
        mock_detect,
        mock_rule_adapter,
        mock_agent_adapter,
        mock_db,
        project_path,
        mock_agents,
        mock_rules
    ):
        """Test progress callback is called during generation"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_instance = Mock()
        mock_generator_class = Mock(return_value=mock_generator_instance)
        mock_get_generator.return_value = mock_generator_class

        mock_agent_adapter.list.return_value = mock_agents
        mock_rule_adapter.list.return_value = mock_rules

        def mock_get_output_path(role, path):
            return path / ".claude" / "agents" / f"{role}.md"

        mock_generator_instance.get_output_path.side_effect = mock_get_output_path
        mock_generator_instance.generate_agent_file.return_value = GenerationResult(
            agent_role="test",
            output_path=project_path / "test.md",
            content="test",
            success=True
        )

        # Track progress callbacks
        progress_updates = []

        def progress_callback(progress: AgentGenerationProgress):
            progress_updates.append(progress)

        # Create service with callback
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1,
            progress_callback=progress_callback
        )

        # Generate all
        service.generate_all()

        # Verify progress callbacks
        assert len(progress_updates) == 3  # One per agent
        assert progress_updates[0].current == 1
        assert progress_updates[0].total == 3
        assert progress_updates[2].current == 3
        assert progress_updates[2].total == 3


class TestAgentGeneratorServiceGenerateOne:
    """Test AgentGeneratorService.generate_one()"""

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.RuleAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_one_success(
        self,
        mock_get_generator,
        mock_detect,
        mock_rule_adapter,
        mock_agent_adapter,
        mock_db,
        project_path,
        mock_agents,
        mock_rules
    ):
        """Test successful generation of single agent"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_instance = Mock()
        mock_generator_class = Mock(return_value=mock_generator_instance)
        mock_get_generator.return_value = mock_generator_class

        # Return specific agent
        mock_agent_adapter.get_by_role.return_value = mock_agents[0]
        mock_rule_adapter.list.return_value = mock_rules

        output_path = project_path / ".claude" / "agents" / "context-generator.md"
        mock_generator_instance.get_output_path.return_value = output_path
        mock_generator_instance.generate_agent_file.return_value = GenerationResult(
            agent_role="context-generator",
            output_path=output_path,
            content="# Context Generator\n\nAgent SOP",
            success=True
        )

        # Create service and generate
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )
        result = service.generate_one("context-generator")

        # Verify
        assert result.success
        assert result.agent_role == "context-generator"
        assert output_path.exists()
        assert "Context Generator" in output_path.read_text()

    @patch('agentpm.core.services.agent_generator.AgentAdapter')
    @patch('agentpm.core.services.agent_generator.detect_current_provider')
    @patch('agentpm.core.services.agent_generator.get_provider_generator')
    def test_generate_one_agent_not_found(
        self,
        mock_get_generator,
        mock_detect,
        mock_agent_adapter,
        mock_db,
        project_path
    ):
        """Test generation fails when agent not found"""
        # Setup mocks
        mock_detect.return_value = "claude-code"
        mock_generator_class = Mock()
        mock_get_generator.return_value = mock_generator_class

        # Agent not found
        mock_agent_adapter.get_by_role.return_value = None

        # Create service
        service = AgentGeneratorService(
            db=mock_db,
            project_path=project_path,
            project_id=1
        )

        # Verify raises
        with pytest.raises(ValueError, match="Agent 'nonexistent' not found"):
            service.generate_one("nonexistent")


class TestAgentGenerationSummary:
    """Test AgentGenerationSummary dataclass"""

    def test_summary_creation(self, project_path):
        """Test creation of generation summary"""
        summary = AgentGenerationSummary(
            total_generated=10,
            total_failed=2,
            agents_by_type={"orchestrator": 3, "utility": 7},
            failed_agents=["agent-1", "agent-2"],
            warnings=["Warning 1", "Warning 2"],
            output_directory=project_path / ".claude" / "agents"
        )

        assert summary.total_generated == 10
        assert summary.total_failed == 2
        assert len(summary.failed_agents) == 2
        assert len(summary.warnings) == 2
        assert summary.agents_by_type["orchestrator"] == 3
