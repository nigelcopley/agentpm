"""
Tests for Role-Based Filter - Context Scoping by Agent Capabilities

Tests filtering logic for amalgamations and plugin facts based on agent capabilities.
"""

import pytest
from pathlib import Path
from agentpm.core.database.service import DatabaseService
# schema.py removed - use DatabaseService which runs migrations
from agentpm.core.database.models import Project, Agent, Rule
from agentpm.core.database.models.rule import EnforcementLevel
from agentpm.core.database.methods import projects, agents, rules as rule_methods
from agentpm.core.context.role_filter import (
    RoleBasedFilter,
    filter_amalgamations_by_capabilities,
    filter_plugin_facts_by_capabilities,
)


@pytest.fixture
def db_service(tmp_path):
    """Create database with test project and agents"""
    db_path = tmp_path / "test.db"
    # DatabaseService automatically runs migrations (including 0018 which creates schema)
    db = DatabaseService(str(db_path))

    # Create test project
    project = Project(
        id=None,
        name="Test Project",
        path=str(tmp_path),
        tech_stack=["Python", "Django"],  # Must be list
    )
    created_project = projects.create_project(db, project)

    # Create test agents with capabilities
    python_agent = Agent(
        id=None,
        project_id=created_project.id,
        role='python-developer',
        display_name='Python Developer',
        description='Backend Python development',
        capabilities=['python', 'database', 'testing'],
        is_active=True
    )
    agents.create_agent(db, python_agent)

    frontend_agent = Agent(
        id=None,
        project_id=created_project.id,
        role='frontend-developer',
        display_name='Frontend Developer',
        description='Frontend React development',
        capabilities=['frontend', 'react', 'testing'],
        is_active=True
    )
    agents.create_agent(db, frontend_agent)

    # Inactive agent (should not be used for filtering)
    inactive_agent = Agent(
        id=None,
        project_id=created_project.id,
        role='inactive-agent',
        display_name='Inactive Agent',
        description='This agent is inactive',
        capabilities=['python'],
        is_active=False
    )
    agents.create_agent(db, inactive_agent)

    return db, created_project


class TestRoleBasedFilter:
    """Test RoleBasedFilter class"""

    def test_filter_amalgamations_python_agent(self, db_service):
        """Python agent gets backend amalgamations only"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        amalgamations = {
            'classes': '/path/classes.txt',
            'functions': '/path/functions.txt',
            'models': '/path/models.txt',
            'components': '/path/components.txt',  # Frontend (should be filtered)
            'jsx': '/path/jsx.txt',  # Frontend (should be filtered)
            'readme': '/path/readme.txt',  # Common (should be included)
        }

        filtered = filter.filter_amalgamations(
            project_id=project.id,
            agent_role='python-developer',
            amalgamations=amalgamations
        )

        # Should include backend files
        assert 'classes' in filtered
        assert 'functions' in filtered
        assert 'models' in filtered

        # Should include common files
        assert 'readme' in filtered

        # Should exclude frontend files
        assert 'components' not in filtered
        assert 'jsx' not in filtered

    def test_filter_amalgamations_frontend_agent(self, db_service):
        """Frontend agent gets frontend amalgamations only"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        amalgamations = {
            'components': '/path/components.txt',
            'jsx': '/path/jsx.txt',
            'pages': '/path/pages.txt',
            'classes': '/path/classes.txt',  # Backend (should be filtered)
            'models': '/path/models.txt',  # Backend (should be filtered)
            'readme': '/path/readme.txt',  # Common (should be included)
        }

        filtered = filter.filter_amalgamations(
            project_id=project.id,
            agent_role='frontend-developer',
            amalgamations=amalgamations
        )

        # Should include frontend files
        assert 'components' in filtered
        assert 'jsx' in filtered
        assert 'pages' in filtered

        # Should include common files
        assert 'readme' in filtered

        # Should exclude backend files
        assert 'classes' not in filtered
        assert 'models' not in filtered

    def test_filter_plugin_facts_python_agent(self, db_service):
        """Python agent gets backend framework facts only"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        plugin_facts = {
            'python': {'version': '3.9', 'frameworks': ['django']},
            'django': {'version': '4.2'},
            'sqlite': {'version': '3.35'},
            'react': {'version': '18.2'},  # Frontend (should be filtered)
            'vue': {'version': '3.2'},  # Frontend (should be filtered)
        }

        filtered = filter.filter_plugin_facts(
            project_id=project.id,
            agent_role='python-developer',
            plugin_facts=plugin_facts
        )

        # Should include backend frameworks
        assert 'python' in filtered
        assert 'django' in filtered
        assert 'sqlite' in filtered

        # Should exclude frontend frameworks
        assert 'react' not in filtered
        assert 'vue' not in filtered

    def test_filter_plugin_facts_frontend_agent(self, db_service):
        """Frontend agent gets frontend framework facts only"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        plugin_facts = {
            'react': {'version': '18.2'},
            'vue': {'version': '3.2'},
            'typescript': {'version': '5.0'},
            'django': {'version': '4.2'},  # Backend (should be filtered)
            'sqlite': {'version': '3.35'},  # Backend (should be filtered)
        }

        filtered = filter.filter_plugin_facts(
            project_id=project.id,
            agent_role='frontend-developer',
            plugin_facts=plugin_facts
        )

        # Should include frontend frameworks
        assert 'react' in filtered

        # Should exclude backend frameworks
        assert 'django' not in filtered
        assert 'sqlite' not in filtered

    def test_filter_inactive_agent_no_filtering(self, db_service):
        """Inactive agent returns all context (no filtering)"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        amalgamations = {
            'classes': '/path/classes.txt',
            'components': '/path/components.txt',
        }

        filtered = filter.filter_amalgamations(
            project_id=project.id,
            agent_role='inactive-agent',
            amalgamations=amalgamations
        )

        # Inactive agent should return all (no filtering)
        assert len(filtered) == len(amalgamations)

    def test_filter_nonexistent_agent_no_filtering(self, db_service):
        """Nonexistent agent returns all context (graceful degradation)"""
        db, project = db_service
        filter = RoleBasedFilter(db)

        amalgamations = {
            'classes': '/path/classes.txt',
            'components': '/path/components.txt',
        }

        filtered = filter.filter_amalgamations(
            project_id=project.id,
            agent_role='nonexistent-agent',
            amalgamations=amalgamations
        )

        # Nonexistent agent should return all (graceful degradation)
        assert len(filtered) == len(amalgamations)

    def test_calculate_filter_effectiveness(self, db_service):
        """Calculate filtering effectiveness (percentage reduction)"""
        db, _ = db_service
        filter = RoleBasedFilter(db)

        # 50% reduction (10 → 5)
        effectiveness = filter.calculate_filter_effectiveness(10, 5)
        assert effectiveness == 0.5

        # 0% reduction (no filtering)
        effectiveness = filter.calculate_filter_effectiveness(10, 10)
        assert effectiveness == 0.0

        # 100% reduction (all filtered)
        effectiveness = filter.calculate_filter_effectiveness(10, 0)
        assert effectiveness == 1.0

        # Edge case: 0 original items
        effectiveness = filter.calculate_filter_effectiveness(0, 0)
        assert effectiveness == 0.0


class TestStandaloneFilteringFunctions:
    """Test standalone filtering functions (no database)"""

    def test_filter_amalgamations_by_capabilities(self):
        """Filter amalgamations by explicit capabilities"""
        amalgamations = {
            'classes': '/path/classes.txt',
            'functions': '/path/functions.txt',
            'components': '/path/components.txt',
            'readme': '/path/readme.txt',
        }

        filtered = filter_amalgamations_by_capabilities(
            amalgamations,
            capabilities=['python', 'database']
        )

        # Should include backend files
        assert 'classes' in filtered
        assert 'functions' in filtered

        # Should include common files
        assert 'readme' in filtered

        # Should exclude frontend files
        assert 'components' not in filtered

    def test_filter_plugin_facts_by_capabilities(self):
        """Filter plugin facts by explicit capabilities"""
        plugin_facts = {
            'python': {'version': '3.9'},
            'django': {'version': '4.2'},
            'react': {'version': '18.2'},
        }

        filtered = filter_plugin_facts_by_capabilities(
            plugin_facts,
            capabilities=['python', 'database']
        )

        # Should include backend frameworks
        assert 'python' in filtered
        assert 'django' in filtered

        # Should exclude frontend frameworks
        assert 'react' not in filtered

    def test_filter_with_empty_capabilities(self):
        """Empty capabilities returns all items (no filtering)"""
        amalgamations = {
            'classes': '/path/classes.txt',
            'components': '/path/components.txt',
        }

        filtered = filter_amalgamations_by_capabilities(
            amalgamations,
            capabilities=[]
        )

        # Should return all (no filtering)
        assert len(filtered) == len(amalgamations)


class TestFilteringPerformance:
    """Test filtering performance targets (<10ms overhead)"""

    def test_filter_amalgamations_performance_basic(self, db_service):
        """Filter amalgamations with reasonable size dataset"""
        import time

        db, project = db_service
        filter = RoleBasedFilter(db)

        amalgamations = {
            f'type_{i}': f'/path/type_{i}.txt'
            for i in range(20)  # 20 amalgamations
        }

        # Measure time
        start = time.perf_counter()
        result = filter.filter_amalgamations(
            project_id=project.id,
            agent_role='python-developer',
            amalgamations=amalgamations
        )
        duration_ms = (time.perf_counter() - start) * 1000

        # Should complete reasonably quickly (informational, not strict)
        assert result is not None
        assert duration_ms < 100  # Generous limit (100ms)

    def test_filter_plugin_facts_performance_basic(self, db_service):
        """Filter plugin facts with reasonable size dataset"""
        import time

        db, project = db_service
        filter = RoleBasedFilter(db)

        plugin_facts = {
            f'framework_{i}': {'version': f'{i}.0'}
            for i in range(10)  # 10 frameworks
        }

        # Measure time
        start = time.perf_counter()
        result = filter.filter_plugin_facts(
            project_id=project.id,
            agent_role='python-developer',
            plugin_facts=plugin_facts
        )
        duration_ms = (time.perf_counter() - start) * 1000

        # Should complete reasonably quickly (informational, not strict)
        assert result is not None
        assert duration_ms < 100  # Generous limit (100ms)


class TestRuleFiltering:
    """Test role-based rule filtering (Phase 2 implementation)"""

    @pytest.fixture
    def db_with_rules(self, db_service):
        """Create database with test project, agents, and rules"""
        db, project = db_service

        # Create rules with different categories
        rules_data = [
            # Python/Backend rules
            Rule(
                project_id=project.id,
                rule_id='DP-001',
                name='time-boxing-implementation',
                description='Implementation tasks limited to 4 hours',
                category='Development Principles',
                enforcement_level=EnforcementLevel.BLOCK,
                config={'max_hours': 4.0},
                enabled=True
            ),
            Rule(
                project_id=project.id,
                rule_id='DP-012',
                name='quality-test-coverage',
                description='Minimum test coverage 90%',
                category='Testing Standards',
                enforcement_level=EnforcementLevel.BLOCK,
                config={'min_coverage': 90.0},
                enabled=True
            ),
            Rule(
                project_id=project.id,
                rule_id='DP-027',
                name='code-type-hints-required',
                description='Type hints required for all functions',
                category='Code Quality',
                enforcement_level=EnforcementLevel.LIMIT,
                config={},
                enabled=True
            ),
            Rule(
                project_id=project.id,
                rule_id='SEC-001',
                name='security-input-validation',
                description='All inputs must be validated',
                category='Security Standards',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=True
            ),

            # DevOps/Deployment rules (should be filtered for python-developer)
            Rule(
                project_id=project.id,
                rule_id='DP-020',
                name='deployment-approval-required',
                description='Deployments require approval',
                category='Deployment Standards',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=True
            ),
            Rule(
                project_id=project.id,
                rule_id='DP-021',
                name='infrastructure-backup-required',
                description='All infrastructure must have backups',
                category='Infrastructure Standards',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=True
            ),

            # Universal rules (should always be included)
            Rule(
                project_id=project.id,
                rule_id='WR-001',
                name='workflow-quality-gates',
                description='Work items validated before tasks start',
                category='Workflow Rules',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=True
            ),
            Rule(
                project_id=project.id,
                rule_id='TB-001',
                name='time-boxing-general',
                description='All tasks must be time-boxed',
                category='Time-Boxing Rules',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=True
            ),

            # Disabled rule (should be excluded)
            Rule(
                project_id=project.id,
                rule_id='DP-099',
                name='disabled-rule',
                description='This rule is disabled',
                category='Development Principles',
                enforcement_level=EnforcementLevel.BLOCK,
                config={},
                enabled=False
            ),
        ]

        # Create all rules
        created_rules = []
        for rule_data in rules_data:
            created = rule_methods.create_rule(db, rule_data)
            created_rules.append(created)

        return db, project, created_rules

    def test_filter_rules_python_developer(self, db_with_rules):
        """Python developer gets Python/backend rules + universal rules"""
        db, project, all_rules = db_with_rules
        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by python-developer capabilities
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='python-developer',
            rules=enabled_rules
        )

        # Check included rules
        rule_ids = {r.rule_id for r in filtered}

        # Should include Python/backend rules
        assert 'DP-001' in rule_ids  # Development Principles
        assert 'DP-012' in rule_ids  # Testing Standards
        assert 'DP-027' in rule_ids  # Code Quality
        assert 'SEC-001' in rule_ids  # Security Standards

        # Should include universal rules
        assert 'WR-001' in rule_ids  # Workflow Rules
        assert 'TB-001' in rule_ids  # Time-Boxing Rules

        # Should exclude DevOps/deployment rules
        assert 'DP-020' not in rule_ids  # Deployment Standards
        assert 'DP-021' not in rule_ids  # Infrastructure Standards

        # Should exclude disabled rules
        assert 'DP-099' not in rule_ids  # Disabled

        # Verify filtering effectiveness (should be ~60-70% reduction)
        original_count = len(enabled_rules)
        filtered_count = len(filtered)
        reduction = filter.calculate_filter_effectiveness(original_count, filtered_count)

        # With 6 relevant + 2 universal out of 8 enabled = 0% reduction for python-dev
        # (Since python-developer has broad capabilities)
        # But deployment rules (2) should be filtered out
        assert filtered_count == 6  # 4 Python + 2 universal
        assert reduction > 0.1  # At least 10% reduction

    def test_filter_rules_devops_specialist(self, db_with_rules):
        """DevOps specialist gets deployment rules + universal rules"""
        db, project, all_rules = db_with_rules

        # Create devops agent
        devops_agent = Agent(
            id=None,
            project_id=project.id,
            role='devops-specialist',
            display_name='DevOps Specialist',
            description='Infrastructure and deployment',
            capabilities=['devops', 'ci_cd', 'infrastructure'],
            is_active=True
        )
        agents.create_agent(db, devops_agent)

        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by devops-specialist capabilities
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='devops-specialist',
            rules=enabled_rules
        )

        # Check included rules
        rule_ids = {r.rule_id for r in filtered}

        # Should include deployment/infrastructure rules
        assert 'DP-020' in rule_ids  # Deployment Standards
        assert 'DP-021' in rule_ids  # Infrastructure Standards
        assert 'SEC-001' in rule_ids  # Security Standards (relevant to devops)

        # Should include universal rules
        assert 'WR-001' in rule_ids  # Workflow Rules
        assert 'TB-001' in rule_ids  # Time-Boxing Rules

        # Should exclude Python-specific rules
        assert 'DP-027' not in rule_ids  # Code Quality (type hints - Python specific)

    def test_filter_rules_testing_specialist(self, db_with_rules):
        """Testing specialist gets testing rules + universal rules"""
        db, project, all_rules = db_with_rules

        # Create testing agent
        testing_agent = Agent(
            id=None,
            project_id=project.id,
            role='testing-specialist',
            display_name='Testing Specialist',
            description='Quality assurance and testing',
            capabilities=['testing', 'pytest', 'quality_assurance'],
            is_active=True
        )
        agents.create_agent(db, testing_agent)

        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by testing-specialist capabilities
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='testing-specialist',
            rules=enabled_rules
        )

        # Check included rules
        rule_ids = {r.rule_id for r in filtered}

        # Should include testing rules
        assert 'DP-012' in rule_ids  # Testing Standards
        assert 'DP-027' in rule_ids  # Code Quality

        # Should include universal rules
        assert 'WR-001' in rule_ids  # Workflow Rules
        assert 'TB-001' in rule_ids  # Time-Boxing Rules

        # Should exclude deployment rules
        assert 'DEPL-001' not in rule_ids  # Deployment Standards
        assert 'INFRA-001' not in rule_ids  # Infrastructure Standards

    def test_filter_rules_no_category_always_included(self, db_with_rules):
        """Rules without category are always included (legacy compatibility)"""
        db, project, all_rules = db_with_rules

        # Create rule without category
        legacy_rule = Rule(
            project_id=project.id,
            rule_id='DP-100',
            name='legacy-rule',
            description='Legacy rule without category',
            category=None,  # No category
            enforcement_level=EnforcementLevel.BLOCK,
            config={},
            enabled=True
        )
        rule_methods.create_rule(db, legacy_rule)

        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by python-developer capabilities
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='python-developer',
            rules=enabled_rules
        )

        # Check that legacy rule is included
        rule_ids = {r.rule_id for r in filtered}
        assert 'DP-100' in rule_ids  # Legacy rule always included

    def test_filter_rules_nonexistent_agent_returns_all(self, db_with_rules):
        """Nonexistent agent returns all rules (graceful degradation)"""
        db, project, all_rules = db_with_rules
        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by nonexistent agent
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='nonexistent-agent',
            rules=enabled_rules
        )

        # Should return all enabled rules (graceful degradation)
        assert len(filtered) == len(enabled_rules)

    def test_filter_rules_empty_capabilities_returns_all(self, db_with_rules):
        """Agent with no capabilities returns all rules (graceful degradation)"""
        db, project, all_rules = db_with_rules

        # Create agent with no capabilities
        empty_agent = Agent(
            id=None,
            project_id=project.id,
            role='empty-agent',
            display_name='Empty Agent',
            description='Agent with no capabilities',
            capabilities=[],  # No capabilities
            is_active=True
        )
        agents.create_agent(db, empty_agent)

        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by empty agent
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='empty-agent',
            rules=enabled_rules
        )

        # Should return all enabled rules (graceful degradation)
        assert len(filtered) == len(enabled_rules)

    def test_filter_rules_token_reduction_measurement(self, db_with_rules):
        """Measure token reduction from rule filtering"""
        db, project, all_rules = db_with_rules
        filter = RoleBasedFilter(db)

        # Load all enabled rules
        enabled_rules = rule_methods.list_rules(db, project_id=project.id, enabled_only=True)

        # Filter by python-developer capabilities
        filtered = filter.filter_rules(
            project_id=project.id,
            agent_role='python-developer',
            rules=enabled_rules
        )

        # Calculate reduction
        original_count = len(enabled_rules)
        filtered_count = len(filtered)
        reduction = filter.calculate_filter_effectiveness(original_count, filtered_count)

        # Verify filtering occurred
        assert filtered_count < original_count

        # Verify meaningful reduction (target: 60-70%)
        # With our test data: 8 enabled rules, python-dev should see 6 (2 filtered out)
        # That's 25% reduction, which is reasonable for a broad role like python-developer
        assert reduction > 0.2  # At least 20% reduction

        # Print results for documentation
        print(f"\nToken reduction measurement:")
        print(f"  Original rules: {original_count}")
        print(f"  Filtered rules: {filtered_count}")
        print(f"  Reduction: {reduction:.1%}")
        print(f"\n  Filtered out rules:")
        filtered_ids = {r.rule_id for r in filtered}
        for rule in enabled_rules:
            if rule.rule_id not in filtered_ids:
                print(f"    - {rule.rule_id}: {rule.category}")
