"""
Tests for Common Patterns Module

Comprehensive test coverage for shared patterns used across provider generators.
"""

import pytest
from datetime import datetime
from typing import List

from agentpm.providers.common.patterns import (
    UniversalContext,
    ProjectContext,
    WorkItemContext,
    TaskContext,
    CommonExclusions,
    CommonRuleCategories,
)
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.models.rule import Rule, EnforcementLevel
from agentpm.core.database.enums import AgentTier


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_project_context():
    """Sample project context"""
    return ProjectContext(
        id=1,
        name="Test Project",
        description="Test project description",
        tech_stack=["python", "pytest", "sqlite"],
        frameworks=["pydantic", "click"],
        root_path="/path/to/project",
    )


@pytest.fixture
def sample_work_item_context():
    """Sample work item context"""
    return WorkItemContext(
        id=100,
        name="Implement Feature X",
        type="feature",
        status="in_progress",
        phase="I1_IMPLEMENTATION",
        business_context="Improve user experience",
        effort_estimate_hours=8.0,
        priority=1,
    )


@pytest.fixture
def sample_task_context():
    """Sample task context"""
    return TaskContext(
        id=200,
        name="Write unit tests",
        type="testing",
        status="active",
        description="Create comprehensive test suite",
        effort_hours=4.0,
        priority=2,
        assigned_to="aipm-testing-specialist",
        quality_metadata={"coverage_target": 90},
    )


@pytest.fixture
def sample_rules():
    """Sample rules list"""
    return [
        Rule(
            id=1,
            project_id=1,
            rule_id="DP-001",
            name="hexagonal-architecture",
            description="Follow hexagonal architecture",
            enforcement_level=EnforcementLevel.BLOCK,
            category="development_principles",
            enabled=True,
        ),
        Rule(
            id=2,
            project_id=1,
            rule_id="TES-001",
            name="test-coverage",
            description="Maintain 90% test coverage",
            enforcement_level=EnforcementLevel.LIMIT,
            category="testing_standards",
            enabled=True,
        ),
        Rule(
            id=3,
            project_id=1,
            rule_id="SEC-001",
            name="input-validation",
            description="Validate all inputs",
            enforcement_level=EnforcementLevel.BLOCK,
            category="security_requirements",
            enabled=True,
        ),
    ]


@pytest.fixture
def sample_agents():
    """Sample agents list"""
    return [
        Agent(
            id=1,
            project_id=1,
            role="aipm-python-cli-developer",
            display_name="Python/CLI Developer",
            description="Implements Python code and CLI commands",
            capabilities=["python", "cli", "pydantic"],
            tier=AgentTier.TIER_2,
            is_active=True,
        ),
        Agent(
            id=2,
            project_id=1,
            role="aipm-testing-specialist",
            display_name="Testing Specialist",
            description="Creates comprehensive test suites",
            capabilities=["pytest", "coverage", "fixtures"],
            tier=AgentTier.TIER_2,
            is_active=True,
        ),
    ]


# ============================================================================
# ProjectContext Tests
# ============================================================================


class TestProjectContext:
    """Test ProjectContext dataclass"""

    def test_create_minimal(self):
        """Test creating project context with minimal fields"""
        ctx = ProjectContext(id=1, name="Test Project")
        assert ctx.id == 1
        assert ctx.name == "Test Project"
        assert ctx.description is None
        assert ctx.tech_stack == []
        assert ctx.frameworks == []
        assert ctx.root_path is None

    def test_create_full(self, sample_project_context):
        """Test creating project context with all fields"""
        ctx = sample_project_context
        assert ctx.id == 1
        assert ctx.name == "Test Project"
        assert ctx.description == "Test project description"
        assert "python" in ctx.tech_stack
        assert "pydantic" in ctx.frameworks
        assert ctx.root_path == "/path/to/project"

    def test_to_dict(self, sample_project_context):
        """Test serialization to dictionary"""
        result = sample_project_context.to_dict()
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Test Project"
        assert result["description"] == "Test project description"
        assert result["tech_stack"] == ["python", "pytest", "sqlite"]
        assert result["frameworks"] == ["pydantic", "click"]
        assert result["root_path"] == "/path/to/project"


# ============================================================================
# WorkItemContext Tests
# ============================================================================


class TestWorkItemContext:
    """Test WorkItemContext dataclass"""

    def test_create_minimal(self):
        """Test creating work item context with minimal fields"""
        ctx = WorkItemContext(
            id=100, name="Test Work Item", type="feature", status="draft"
        )
        assert ctx.id == 100
        assert ctx.name == "Test Work Item"
        assert ctx.type == "feature"
        assert ctx.status == "draft"
        assert ctx.phase is None
        assert ctx.priority == 3  # Default

    def test_create_full(self, sample_work_item_context):
        """Test creating work item context with all fields"""
        ctx = sample_work_item_context
        assert ctx.id == 100
        assert ctx.name == "Implement Feature X"
        assert ctx.phase == "I1_IMPLEMENTATION"
        assert ctx.business_context == "Improve user experience"
        assert ctx.effort_estimate_hours == 8.0
        assert ctx.priority == 1

    def test_to_dict(self, sample_work_item_context):
        """Test serialization to dictionary"""
        result = sample_work_item_context.to_dict()
        assert isinstance(result, dict)
        assert result["id"] == 100
        assert result["name"] == "Implement Feature X"
        assert result["type"] == "feature"
        assert result["status"] == "in_progress"
        assert result["phase"] == "I1_IMPLEMENTATION"
        assert result["priority"] == 1


# ============================================================================
# TaskContext Tests
# ============================================================================


class TestTaskContext:
    """Test TaskContext dataclass"""

    def test_create_minimal(self):
        """Test creating task context with minimal fields"""
        ctx = TaskContext(id=200, name="Test Task", type="implementation", status="draft")
        assert ctx.id == 200
        assert ctx.name == "Test Task"
        assert ctx.type == "implementation"
        assert ctx.status == "draft"
        assert ctx.description is None
        assert ctx.priority == 3  # Default

    def test_create_full(self, sample_task_context):
        """Test creating task context with all fields"""
        ctx = sample_task_context
        assert ctx.id == 200
        assert ctx.name == "Write unit tests"
        assert ctx.type == "testing"
        assert ctx.assigned_to == "aipm-testing-specialist"
        assert ctx.quality_metadata == {"coverage_target": 90}

    def test_to_dict(self, sample_task_context):
        """Test serialization to dictionary"""
        result = sample_task_context.to_dict()
        assert isinstance(result, dict)
        assert result["id"] == 200
        assert result["name"] == "Write unit tests"
        assert result["assigned_to"] == "aipm-testing-specialist"
        assert result["quality_metadata"] == {"coverage_target": 90}


# ============================================================================
# UniversalContext Tests
# ============================================================================


class TestUniversalContext:
    """Test UniversalContext dataclass"""

    def test_create_minimal(self, sample_project_context):
        """Test creating universal context with minimal fields"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic"],
        )
        assert ctx.version == "1.0.0"
        assert ctx.project == sample_project_context
        assert "anthropic" in ctx.providers
        assert ctx.work_item is None
        assert ctx.task is None
        assert ctx.rules == []
        assert ctx.agents == []

    def test_create_full(
        self,
        sample_project_context,
        sample_work_item_context,
        sample_task_context,
        sample_rules,
        sample_agents,
    ):
        """Test creating universal context with all fields"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic", "cursor", "openai"],
            work_item=sample_work_item_context,
            task=sample_task_context,
            rules=sample_rules,
            agents=sample_agents,
            tech_stack=["python", "pytest"],
            detected_frameworks=["pydantic"],
        )
        assert ctx.work_item == sample_work_item_context
        assert ctx.task == sample_task_context
        assert len(ctx.rules) == 3
        assert len(ctx.agents) == 2
        assert "python" in ctx.tech_stack
        assert "pydantic" in ctx.detected_frameworks

    def test_to_dict(
        self,
        sample_project_context,
        sample_work_item_context,
        sample_task_context,
        sample_rules,
        sample_agents,
    ):
        """Test serialization to dictionary"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime(2025, 1, 1, 12, 0, 0),
            providers=["anthropic"],
            work_item=sample_work_item_context,
            task=sample_task_context,
            rules=sample_rules,
            agents=sample_agents,
            tech_stack=["python"],
            detected_frameworks=["pydantic"],
        )
        result = ctx.to_dict()
        assert isinstance(result, dict)
        assert result["version"] == "1.0.0"
        assert result["project"]["id"] == 1
        assert result["work_item"]["id"] == 100
        assert result["task"]["id"] == 200
        assert len(result["rules"]) == 3
        assert len(result["agents"]) == 2
        assert result["generated"] == "2025-01-01T12:00:00"

    def test_get_blocking_rules(self, sample_project_context, sample_rules):
        """Test filtering BLOCK-level rules"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic"],
            rules=sample_rules,
        )
        blocking = ctx.get_blocking_rules()
        assert len(blocking) == 2  # DP-001 and SEC-001
        assert all(r.enforcement_level == EnforcementLevel.BLOCK for r in blocking)

    def test_get_rules_by_category(self, sample_project_context, sample_rules):
        """Test filtering rules by category"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic"],
            rules=sample_rules,
        )
        security_rules = ctx.get_rules_by_category("security_requirements")
        assert len(security_rules) == 1
        assert security_rules[0].rule_id == "SEC-001"

    def test_get_agents_by_tier(self, sample_project_context, sample_agents):
        """Test filtering agents by tier"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic"],
            agents=sample_agents,
        )
        specialists = ctx.get_agents_by_tier(2)  # TIER_2 = 2
        assert len(specialists) == 2
        assert all(a.tier == AgentTier.TIER_2 for a in specialists)


# ============================================================================
# CommonExclusions Tests
# ============================================================================


class TestCommonExclusions:
    """Test CommonExclusions patterns"""

    def test_standard_exclusions(self):
        """Test standard exclusions are defined"""
        assert isinstance(CommonExclusions.STANDARD, list)
        assert len(CommonExclusions.STANDARD) > 0
        assert ".git/" in CommonExclusions.STANDARD
        assert "__pycache__/" in CommonExclusions.STANDARD
        assert "node_modules/" in CommonExclusions.STANDARD

    def test_claude_code_exclusions(self):
        """Test Claude Code specific exclusions"""
        assert ".claude/cache/" in CommonExclusions.CLAUDE_CODE
        assert ".claude/memory/" in CommonExclusions.CLAUDE_CODE
        # Should include standard exclusions
        assert ".git/" in CommonExclusions.CLAUDE_CODE

    def test_cursor_exclusions(self):
        """Test Cursor specific exclusions"""
        assert ".cursor/" in CommonExclusions.CURSOR
        # Should include standard exclusions
        assert ".git/" in CommonExclusions.CURSOR

    def test_codex_exclusions(self):
        """Test OpenAI Codex specific exclusions"""
        assert ".codex/" in CommonExclusions.CODEX
        # Should include standard exclusions
        assert ".git/" in CommonExclusions.CODEX

    def test_gemini_exclusions(self):
        """Test Google Gemini specific exclusions"""
        assert ".gemini/" in CommonExclusions.GEMINI
        assert ".gemini/checkpoints/" in CommonExclusions.GEMINI
        # Should include standard exclusions
        assert ".git/" in CommonExclusions.GEMINI

    def test_get_for_provider_anthropic(self):
        """Test getting exclusions for Anthropic provider"""
        exclusions = CommonExclusions.get_for_provider("anthropic")
        assert exclusions == CommonExclusions.CLAUDE_CODE
        assert ".claude/cache/" in exclusions

    def test_get_for_provider_cursor(self):
        """Test getting exclusions for Cursor provider"""
        exclusions = CommonExclusions.get_for_provider("cursor")
        assert exclusions == CommonExclusions.CURSOR
        assert ".cursor/" in exclusions

    def test_get_for_provider_openai(self):
        """Test getting exclusions for OpenAI provider"""
        exclusions = CommonExclusions.get_for_provider("openai")
        assert exclusions == CommonExclusions.CODEX

    def test_get_for_provider_google(self):
        """Test getting exclusions for Google provider"""
        exclusions = CommonExclusions.get_for_provider("google")
        assert exclusions == CommonExclusions.GEMINI

    def test_get_for_provider_unknown(self):
        """Test getting exclusions for unknown provider (returns STANDARD)"""
        exclusions = CommonExclusions.get_for_provider("unknown-provider")
        assert exclusions == CommonExclusions.STANDARD

    def test_get_for_provider_case_insensitive(self):
        """Test provider name matching is case-insensitive"""
        exclusions = CommonExclusions.get_for_provider("ANTHROPIC")
        assert exclusions == CommonExclusions.CLAUDE_CODE


# ============================================================================
# CommonRuleCategories Tests
# ============================================================================


class TestCommonRuleCategories:
    """Test CommonRuleCategories constants"""

    def test_all_categories_defined(self):
        """Test all standard categories are defined"""
        categories = CommonRuleCategories.all_categories()
        assert isinstance(categories, list)
        assert len(categories) == 8
        assert CommonRuleCategories.ARCHITECTURE in categories
        assert CommonRuleCategories.TESTING in categories
        assert CommonRuleCategories.SECURITY in categories
        assert CommonRuleCategories.DOCUMENTATION in categories
        assert CommonRuleCategories.WORKFLOW in categories
        assert CommonRuleCategories.CODE_QUALITY in categories
        assert CommonRuleCategories.PERFORMANCE in categories
        assert CommonRuleCategories.CI_CD in categories

    def test_category_values(self):
        """Test category constant values"""
        assert CommonRuleCategories.ARCHITECTURE == "development_principles"
        assert CommonRuleCategories.TESTING == "testing_standards"
        assert CommonRuleCategories.SECURITY == "security_requirements"
        assert CommonRuleCategories.DOCUMENTATION == "documentation_standards"
        assert CommonRuleCategories.WORKFLOW == "workflow_governance"
        assert CommonRuleCategories.CODE_QUALITY == "code_quality"
        assert CommonRuleCategories.PERFORMANCE == "performance_requirements"
        assert CommonRuleCategories.CI_CD == "continuous_integration"

    def test_get_display_name_architecture(self):
        """Test getting display name for architecture category"""
        display = CommonRuleCategories.get_display_name(
            CommonRuleCategories.ARCHITECTURE
        )
        assert display == "Development Principles"

    def test_get_display_name_testing(self):
        """Test getting display name for testing category"""
        display = CommonRuleCategories.get_display_name(CommonRuleCategories.TESTING)
        assert display == "Testing Standards"

    def test_get_display_name_security(self):
        """Test getting display name for security category"""
        display = CommonRuleCategories.get_display_name(CommonRuleCategories.SECURITY)
        assert display == "Security Requirements"

    def test_get_display_name_unknown(self):
        """Test getting display name for unknown category (fallback)"""
        display = CommonRuleCategories.get_display_name("unknown_category")
        assert display == "Unknown Category"

    def test_get_display_name_all_categories(self):
        """Test getting display names for all categories"""
        for category in CommonRuleCategories.all_categories():
            display = CommonRuleCategories.get_display_name(category)
            assert isinstance(display, str)
            assert len(display) > 0
            assert display != category  # Should be formatted


# ============================================================================
# Integration Tests
# ============================================================================


class TestPatternsIntegration:
    """Integration tests for patterns working together"""

    def test_universal_context_full_lifecycle(
        self,
        sample_project_context,
        sample_work_item_context,
        sample_task_context,
        sample_rules,
        sample_agents,
    ):
        """Test creating and using universal context through full lifecycle"""
        # Create context
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic", "cursor"],
            work_item=sample_work_item_context,
            task=sample_task_context,
            rules=sample_rules,
            agents=sample_agents,
            tech_stack=["python", "pytest", "sqlite"],
            detected_frameworks=["pydantic", "click"],
        )

        # Test serialization
        data = ctx.to_dict()
        assert data["version"] == "1.0.0"
        assert data["project"]["name"] == "Test Project"

        # Test rule filtering
        blocking_rules = ctx.get_blocking_rules()
        assert len(blocking_rules) == 2

        security_rules = ctx.get_rules_by_category(CommonRuleCategories.SECURITY)
        assert len(security_rules) == 1

        # Test agent filtering
        specialists = ctx.get_agents_by_tier(2)
        assert len(specialists) == 2

    def test_exclusions_with_provider_context(self):
        """Test exclusions working with provider selection"""
        providers = ["anthropic", "cursor", "openai", "google"]
        for provider in providers:
            exclusions = CommonExclusions.get_for_provider(provider)
            assert isinstance(exclusions, list)
            assert len(exclusions) > len(CommonExclusions.STANDARD)
            # All should have standard exclusions
            assert ".git/" in exclusions
            assert "__pycache__/" in exclusions

    def test_rule_categories_with_context_filtering(
        self, sample_project_context, sample_rules
    ):
        """Test rule categories used for context filtering"""
        ctx = UniversalContext(
            version="1.0.0",
            project=sample_project_context,
            generated=datetime.now(),
            providers=["anthropic"],
            rules=sample_rules,
        )

        # Get rules by each category
        for category in CommonRuleCategories.all_categories():
            filtered_rules = ctx.get_rules_by_category(category)
            assert isinstance(filtered_rules, list)
            # Each rule in filtered list should match category
            for rule in filtered_rules:
                assert rule.category == category
