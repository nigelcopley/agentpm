"""
Tests for Memory File Generator

Tests the MemoryGenerator service in agentpm/services/memory/generator.py
"""

import pytest
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.services.memory.generator import MemoryGenerator
from agentpm.core.database.models.memory import MemoryFileType, ValidationStatus
from agentpm.core.database.methods import projects, work_items, tasks, rules as rules_methods, agents as agent_methods, ideas as idea_methods
from agentpm.core.database.models import Project, WorkItem, Task, Rule, Agent, Idea
from agentpm.core.database.enums import WorkItemStatus, WorkItemType, TaskStatus, EnforcementLevel, IdeaStatus, IdeaSource


@pytest.fixture
def db(tmp_path):
    """Create a test database with sample data using proper methods."""
    db_path = tmp_path / "test.db"
    db = DatabaseService(str(db_path))

    # Create test project using methods
    project = Project(
        name="Test Project",
        description="A test project",
        path="/test/path",
        tech_stack='["Python", "SQLite"]',
        status="active"
    )
    project = projects.create_project(db, project)

    # Create test rules
    test_rules = [
        Rule(project_id=project.id, rule_id='DP-001', name='Time-boxing', description='All work must be time-boxed', category='Development Principles', enforcement_level=EnforcementLevel.BLOCK, error_message='Violation', config='{}', enabled=True),
        Rule(project_id=project.id, rule_id='DP-002', name='Quality Gates', description='Use quality gates', category='Development Principles', enforcement_level=EnforcementLevel.BLOCK, error_message='Violation', config='{}', enabled=True),
        Rule(project_id=project.id, rule_id='CQ-001', name='Code Quality', description='Maintain code quality', category='Code Quality', enforcement_level=EnforcementLevel.GUIDE, error_message='Warning', config='{}', enabled=True),
    ]
    for rule in test_rules:
        rules_methods.create_rule(db, rule)

    # Create test work items
    wi1 = WorkItem(
        project_id=project.id,
        name='Test Feature',
        description='A test feature',
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.ACTIVE,
        phase='I1_implementation',
        effort_estimate_hours=8.0,
        priority=1
    )
    wi1 = work_items.create_work_item(db, wi1)

    wi2 = WorkItem(
        project_id=project.id,
        name='Test Bug Fix',
        description='A bug fix',
        type=WorkItemType.FIX,
        status=WorkItemStatus.DONE,
        phase='R1_review',
        effort_estimate_hours=2.0,
        priority=2
    )
    wi2 = work_items.create_work_item(db, wi2)

    # Create test tasks
    task1 = Task(
        work_item_id=wi1.id,
        name='Task 1',
        description='First task',
        type='implementation',
        status=TaskStatus.TODO,
        assigned_to='dev',
        effort_hours=4.0,
        priority=1
    )
    tasks.create_task(db, task1)

    task2 = Task(
        work_item_id=wi1.id,
        name='Task 2',
        description='Second task',
        type='testing',
        status=TaskStatus.IN_PROGRESS,
        assigned_to='tester',
        effort_hours=2.0,
        priority=2
    )
    tasks.create_task(db, task2)

    # Create test agents
    agent = Agent(
        project_id=project.id,
        role='test-agent',
        display_name='Test Agent',
        description='A test agent',
        sop_content='SOP content',
        capabilities='["test"]',
        is_active=True,
        agent_type='sub-agent',
        tier='sub-agent'
    )
    agent_methods.create_agent(db, agent)

    # Create test contexts directly
    with db.connect() as conn:
        conn.execute("""
            INSERT INTO contexts (project_id, context_type, entity_type, entity_id, six_w_data, confidence_score, confidence_band, confidence_factors, context_data, created_at, updated_at)
            VALUES (?, 'work_item', 'work_item', ?, '{}', 0.8, 'high', '{}', '{}', '2025-10-21', '2025-10-21')
        """, (project.id, wi1.id))
        conn.commit()

    # Create test ideas
    idea1 = Idea(
        project_id=project.id,
        title='Test Idea',
        description='An innovative idea',
        status=IdeaStatus.IDEA,
        source=IdeaSource.CUSTOMER_FEEDBACK,
        votes=5
    )
    idea_methods.create_idea(db, idea1)

    idea2 = Idea(
        project_id=project.id,
        title='Another Idea',
        description='Another innovative idea',
        status=IdeaStatus.ACCEPTED,
        source=IdeaSource.INTERNAL,
        votes=10
    )
    idea_methods.create_idea(db, idea2)

    return db


@pytest.fixture
def generator(db, tmp_path):
    """Create a MemoryGenerator instance."""
    return MemoryGenerator(db, tmp_path)


class TestMemoryGenerator:
    """Test suite for MemoryGenerator class."""

    def test_generate_rules_memory_file(self, generator):
        """Test RULES memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.RULES
        assert memory.file_path == ".claude/RULES.md"
        assert len(memory.content) > 100
        assert "APM (Agent Project Manager) Governance Rules" in memory.content
        assert "Development Principles" in memory.content
        assert "DP-001" in memory.content
        assert memory.source_tables == ["rules"]
        assert memory.confidence_score > 0.7

    def test_generate_principles_memory_file(self, generator):
        """Test PRINCIPLES memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.PRINCIPLES
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.PRINCIPLES
        assert "Development Principles Pyramid" in memory.content
        assert "DP-001" in memory.content
        assert memory.source_tables == ["rules"]

    def test_generate_workflow_memory_file(self, generator):
        """Test WORKFLOW memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.WORKFLOW
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.WORKFLOW
        assert "APM (Agent Project Manager) Workflow System" in memory.content
        assert "Quality-Gated Workflow" in memory.content
        assert "Total Work Items: 2" in memory.content
        assert "Total Tasks: 2" in memory.content
        assert memory.source_tables == ["work_items", "tasks"]

    def test_generate_agents_memory_file(self, generator):
        """Test AGENTS memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.AGENTS
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.AGENTS
        assert "APM (Agent Project Manager) Agent System" in memory.content
        assert "Total Active Agents: 1" in memory.content
        assert "test-agent" in memory.content
        assert memory.source_tables == ["agents"]

    def test_generate_context_memory_file(self, generator):
        """Test CONTEXT memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.CONTEXT
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.CONTEXT
        assert "APM (Agent Project Manager) Context System" in memory.content
        assert "6W Context Framework" in memory.content
        assert "Total Contexts: 1" in memory.content
        assert memory.source_tables == ["contexts"]

    def test_generate_project_memory_file(self, generator):
        """Test PROJECT memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.PROJECT
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.PROJECT
        assert "Test Project" in memory.content
        assert "Project ID: 1" in memory.content
        assert "Python" in memory.content
        assert memory.source_tables == ["projects"]

    def test_generate_ideas_memory_file(self, generator):
        """Test IDEAS memory file generation."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.IDEAS
        )

        assert memory.id is not None
        assert memory.file_type == MemoryFileType.IDEAS
        assert "APM (Agent Project Manager) Ideas System" in memory.content
        assert "Total Ideas: 2" in memory.content
        assert "Test Idea" in memory.content
        assert memory.source_tables == ["ideas"]

    def test_generate_all_memory_files(self, generator):
        """Test generating all 7 memory file types."""
        memories = generator.generate_all_memory_files(project_id=1)

        assert len(memories) == 7

        # Check all file types generated
        file_types = {m.file_type for m in memories}
        assert MemoryFileType.RULES in file_types
        assert MemoryFileType.PRINCIPLES in file_types
        assert MemoryFileType.WORKFLOW in file_types
        assert MemoryFileType.AGENTS in file_types
        assert MemoryFileType.CONTEXT in file_types
        assert MemoryFileType.PROJECT in file_types
        assert MemoryFileType.IDEAS in file_types

    def test_memory_file_written_to_disk(self, generator, tmp_path):
        """Test that memory files are written to .claude/ directory."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES
        )

        file_path = tmp_path / ".claude" / "RULES.md"
        assert file_path.exists()

        content = file_path.read_text()
        assert content == memory.content
        assert "APM (Agent Project Manager) Governance Rules" in content

    def test_quality_scores_calculated(self, generator):
        """Test that confidence and completeness scores are calculated."""
        memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES
        )

        assert memory.confidence_score >= 0.0
        assert memory.confidence_score <= 1.0
        assert memory.completeness_score >= 0.0
        assert memory.completeness_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
