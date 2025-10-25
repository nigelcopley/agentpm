"""
Tests for Agent Loader

Tests YAML parsing, validation, and database insertion.
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import json

from .loader import AgentLoader, AgentDefinition, LoadResult
from ..database.models.agent import Agent
from ..database.enums import AgentTier


class MockDBService:
    """Mock database service for testing"""

    def __init__(self):
        self.agents = []
        self.queries = []
        self.updates = []

    def get_current_project(self):
        """Mock current project"""
        class MockProject:
            id = 1
            name = "Test Project"
        return MockProject()

    def execute_query(self, query, params=None):
        """Mock query execution"""
        self.queries.append((query, params))

        # Return existing roles for conflict detection
        if "SELECT role FROM agents" in query:
            return [(agent['role'],) for agent in self.agents]

        # Return agent ID for update
        if "SELECT id FROM agents" in query:
            project_id, role = params
            for idx, agent in enumerate(self.agents):
                if agent['project_id'] == project_id and agent['role'] == role:
                    return [(idx,)]
            return []

        return []

    def execute_update(self, query, params):
        """Mock update execution"""
        self.updates.append((query, params))

        if "INSERT INTO agents" in query:
            # Store agent data
            agent_data = {
                'project_id': params[0],
                'role': params[1],
                'display_name': params[2],
                'description': params[3],
                'sop_content': params[4],
                'capabilities': params[5],
                'is_active': params[6],
                'agent_type': params[7],
                'tier': params[8],
                'metadata': params[9],
            }
            self.agents.append(agent_data)
        elif "UPDATE agents" in query:
            # Update existing agent
            agent_id = params[-1]
            if agent_id < len(self.agents):
                self.agents[agent_id].update({
                    'display_name': params[0],
                    'description': params[1],
                    'sop_content': params[2],
                    'capabilities': params[3],
                    'is_active': params[4],
                    'agent_type': params[5],
                    'tier': params[6],
                    'metadata': params[7],
                })


# Test Fixtures

@pytest.fixture
def mock_db():
    """Mock database service"""
    return MockDBService()


@pytest.fixture
def sample_yaml():
    """Sample agent YAML content"""
    return """
role: test-agent
display_name: Test Agent
description: A test agent for unit testing
tier: 1
category: sub-agent
sop_content: |
  You are a test agent.
  Do test things.
capabilities:
  - testing
  - validation
tools:
  - Read
  - Write
dependencies:
  - other-agent
triggers:
  - test_needed
examples:
  - "Run test suite"
"""


@pytest.fixture
def multi_agent_yaml():
    """Multi-agent YAML content"""
    return """
agents:
  - role: agent-one
    display_name: Agent One
    description: First test agent
    tier: 1
    category: sub-agent
    sop_content: "Agent one SOP"
    capabilities:
      - capability_one

  - role: agent-two
    display_name: Agent Two
    description: Second test agent
    tier: 2
    category: specialist
    sop_content: "Agent two SOP"
    capabilities:
      - capability_two
    dependencies:
      - agent-one
"""


@pytest.fixture
def invalid_yaml():
    """Invalid YAML (missing required fields)"""
    return """
role: invalid-agent
display_name: Invalid Agent
# Missing: description, tier, category, sop_content
"""


# Tests

class TestAgentDefinition:
    """Test AgentDefinition Pydantic model"""

    def test_valid_agent_definition(self):
        """Valid agent definition parses correctly"""
        data = {
            'role': 'test-agent',
            'display_name': 'Test Agent',
            'description': 'A test agent',
            'tier': 1,
            'category': 'sub-agent',
            'sop_content': 'You are a test agent',
            'capabilities': ['testing'],
            'tools': ['Read'],
        }
        agent_def = AgentDefinition(**data)
        assert agent_def.role == 'test-agent'
        assert agent_def.tier == 1
        assert agent_def.category == 'sub-agent'

    def test_role_validation(self):
        """Role must be lowercase with hyphens"""
        data = {
            'role': 'Test-Agent',  # Mixed case
            'display_name': 'Test Agent',
            'description': 'A test agent',
            'tier': 1,
            'category': 'sub-agent',
            'sop_content': 'SOP content',
        }
        agent_def = AgentDefinition(**data)
        assert agent_def.role == 'test-agent'  # Converted to lowercase

    def test_invalid_category(self):
        """Invalid category raises validation error"""
        data = {
            'role': 'test-agent',
            'display_name': 'Test Agent',
            'description': 'A test agent',
            'tier': 1,
            'category': 'invalid-category',  # Invalid
            'sop_content': 'SOP content',
        }
        with pytest.raises(ValueError, match="Category must be one of"):
            AgentDefinition(**data)

    def test_invalid_tier(self):
        """Invalid tier raises validation error"""
        data = {
            'role': 'test-agent',
            'display_name': 'Test Agent',
            'description': 'A test agent',
            'tier': 5,  # Invalid (must be 1-3)
            'category': 'sub-agent',
            'sop_content': 'SOP content',
        }
        with pytest.raises(ValueError, match="Tier must be one of"):
            AgentDefinition(**data)

    def test_to_agent_model(self):
        """Convert to Agent model correctly"""
        data = {
            'role': 'test-agent',
            'display_name': 'Test Agent',
            'description': 'A test agent',
            'tier': 1,
            'category': 'sub-agent',
            'sop_content': 'SOP content',
            'capabilities': ['testing', 'validation'],
            'tools': ['Read', 'Write'],
            'dependencies': ['other-agent'],
            'triggers': ['test_needed'],
        }
        agent_def = AgentDefinition(**data)
        agent = agent_def.to_agent_model(project_id=1)

        assert agent.project_id == 1
        assert agent.role == 'test-agent'
        assert agent.display_name == 'Test Agent'
        assert agent.tier == AgentTier.TIER_1
        assert agent.capabilities == ['testing', 'validation']

        # Check metadata
        metadata = json.loads(agent.metadata)
        assert metadata['category'] == 'sub-agent'
        assert metadata['dependencies'] == ['other-agent']
        assert metadata['triggers'] == ['test_needed']
        assert metadata['tools'] == ['Read', 'Write']


class TestAgentLoader:
    """Test AgentLoader functionality"""

    def test_load_single_agent(self, mock_db, sample_yaml, tmp_path):
        """Load single agent from YAML"""
        # Create temporary YAML file
        yaml_file = tmp_path / "test-agent.yaml"
        yaml_file.write_text(sample_yaml)

        # Load agent
        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=False)

        # Verify success
        assert result.success
        assert result.loaded_count == 1
        assert result.error_count == 0
        assert len(mock_db.agents) == 1

        # Verify agent data
        agent = mock_db.agents[0]
        assert agent['role'] == 'test-agent'
        assert agent['tier'] == 1

    def test_load_multi_agent(self, mock_db, multi_agent_yaml, tmp_path):
        """Load multiple agents from single YAML"""
        yaml_file = tmp_path / "agents.yaml"
        yaml_file.write_text(multi_agent_yaml)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=False)

        assert result.success
        assert result.loaded_count == 2
        assert len(mock_db.agents) == 2

        # Check both agents loaded
        roles = [agent['role'] for agent in mock_db.agents]
        assert 'agent-one' in roles
        assert 'agent-two' in roles

    def test_validate_only(self, mock_db, sample_yaml, tmp_path):
        """Validation mode doesn't insert to database"""
        yaml_file = tmp_path / "test-agent.yaml"
        yaml_file.write_text(sample_yaml)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=True)

        assert result.success
        assert result.loaded_count == 1  # Would load 1 agent
        assert len(mock_db.agents) == 0  # But didn't insert

    def test_invalid_yaml(self, mock_db, invalid_yaml, tmp_path):
        """Invalid YAML produces validation errors"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(invalid_yaml)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=True)

        assert not result.success
        assert result.error_count > 0
        assert len(result.errors) > 0

    def test_conflict_detection(self, mock_db, sample_yaml, tmp_path):
        """Detects conflicts with existing agents"""
        yaml_file = tmp_path / "test-agent.yaml"
        yaml_file.write_text(sample_yaml)

        # Pre-populate existing agent
        mock_db.agents.append({
            'project_id': 1,
            'role': 'test-agent',
            'display_name': 'Existing Agent',
        })

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=False)

        assert not result.success
        assert result.skipped_count == 1
        assert 'test-agent' in result.conflicts

    def test_force_overwrite(self, mock_db, sample_yaml, tmp_path):
        """Force flag overwrites existing agents"""
        yaml_file = tmp_path / "test-agent.yaml"
        yaml_file.write_text(sample_yaml)

        # Pre-populate existing agent
        mock_db.agents.append({
            'project_id': 1,
            'role': 'test-agent',
            'display_name': 'Old Agent',
        })

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(
            yaml_file,
            project_id=1,
            dry_run=False,
            force=True
        )

        assert result.success
        assert result.loaded_count == 1

        # Check agent was updated (not duplicated)
        assert len(mock_db.agents) == 1
        assert mock_db.agents[0]['display_name'] == 'Test Agent'

    def test_dependency_warnings(self, mock_db, tmp_path):
        """Warns about missing dependencies"""
        yaml_content = """
role: dependent-agent
display_name: Dependent Agent
description: Has missing dependency
tier: 1
category: sub-agent
sop_content: "SOP"
dependencies:
  - missing-agent
"""
        yaml_file = tmp_path / "dependent.yaml"
        yaml_file.write_text(yaml_content)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_from_yaml(yaml_file, project_id=1, dry_run=True)

        assert result.success
        assert len(result.warnings) > 0
        assert any('missing-agent' in w for w in result.warnings)

    def test_load_directory(self, mock_db, sample_yaml, multi_agent_yaml, tmp_path):
        """Load all YAML files from directory"""
        # Create multiple YAML files
        (tmp_path / "agent1.yaml").write_text(sample_yaml)
        (tmp_path / "agent2.yaml").write_text(multi_agent_yaml)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_all(tmp_path, project_id=1, dry_run=False)

        assert result.success
        assert result.loaded_count == 3  # 1 + 2 agents
        assert len(mock_db.agents) == 3

    def test_duplicate_role_across_files(self, mock_db, tmp_path):
        """Detects duplicate roles across multiple files"""
        yaml1 = """
role: duplicate-agent
display_name: Agent 1
description: First
tier: 1
category: sub-agent
sop_content: "SOP 1"
"""
        yaml2 = """
role: duplicate-agent
display_name: Agent 2
description: Second
tier: 1
category: sub-agent
sop_content: "SOP 2"
"""
        (tmp_path / "agent1.yaml").write_text(yaml1)
        (tmp_path / "agent2.yaml").write_text(yaml2)

        loader = AgentLoader(mock_db, project_id=1)
        result = loader.load_all(tmp_path, project_id=1, dry_run=True)

        assert not result.success
        assert 'duplicate-agent' in result.conflicts


class TestLoadResult:
    """Test LoadResult dataclass"""

    def test_success_summary(self):
        """Success result generates correct summary"""
        result = LoadResult(
            success=True,
            loaded_count=3,
            skipped_count=0,
            error_count=0,
            agents=[],
            errors=[],
            warnings=[],
            conflicts={},
            dependency_graph={}
        )

        summary = result.summary()
        assert "SUCCESS" in summary
        assert "Loaded: 3" in summary

    def test_failure_summary(self):
        """Failure result includes errors and conflicts"""
        result = LoadResult(
            success=False,
            loaded_count=0,
            skipped_count=1,
            error_count=1,
            agents=[],
            errors=["Validation failed"],
            warnings=["Missing dependency"],
            conflicts={'agent-1': ["Already exists"]},
            dependency_graph={}
        )

        summary = result.summary()
        assert "FAILURE" in summary
        assert "Validation failed" in summary
        assert "Missing dependency" in summary
        assert "agent-1" in summary
