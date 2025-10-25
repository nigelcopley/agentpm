"""
Test Rules Integration into Context Assembly

Verifies Phase 1: Rules are loaded and included in ContextPayload.

Tests:
1. Rules are loaded from database
2. Rules filtered by task type
3. Blocking rules separated
4. Rule summary formatted correctly
5. Graceful degradation if rules fail to load
"""

import pytest
from datetime import datetime
from pathlib import Path

from agentpm.core.context.assembly_service import ContextAssemblyService
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models import Project, WorkItem, Task, Rule
from agentpm.core.database.enums import (
    TaskStatus,
    TaskType,
    WorkItemStatus,
    WorkItemType,
    EnforcementLevel
)


@pytest.fixture
def db_service(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test.db"
    # DatabaseService auto-initializes schema on creation
    service = DatabaseService(str(db_path))
    return service


@pytest.fixture
def test_project(db_service):
    """Create test project."""
    from agentpm.core.database.methods import projects

    project = Project(
        name="Test Project",
        path="/tmp/test",
        description="Test project for rules integration"
    )
    return projects.create_project(db_service, project)


@pytest.fixture
def test_work_item(db_service, test_project):
    """Create test work item."""
    from agentpm.core.database.methods import work_items

    work_item = WorkItem(
        project_id=test_project.id,
        name="Test Feature",
        description="Test feature for rules",
        type=WorkItemType.FEATURE,
        status=WorkItemStatus.ACTIVE
    )
    return work_items.create_work_item(db_service, work_item)


@pytest.fixture
def test_task(db_service, test_work_item):
    """Create test task."""
    from agentpm.core.database.methods import tasks

    task = Task(
        work_item_id=test_work_item.id,
        name="Implement feature",
        description="Implementation task",
        type=TaskType.IMPLEMENTATION,
        status=TaskStatus.ACTIVE,
        effort_hours=3.0
    )
    return tasks.create_task(db_service, task)


@pytest.fixture
def test_rules(db_service, test_project):
    """Create test rules with different enforcement levels."""
    from agentpm.core.database.methods import rules as rule_methods

    rules = [
        # BLOCK rule (applies to all tasks)
        Rule(
            project_id=test_project.id,
            rule_id="DP-001",
            name="time-boxing-implementation",
            description="IMPLEMENTATION tasks must be ≤4 hours",
            category="development_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            config={"max_hours": 4.0, "task_type": ["IMPLEMENTATION"]},
            enabled=True
        ),
        # BLOCK rule (applies to IMPLEMENTATION tasks only)
        Rule(
            project_id=test_project.id,
            rule_id="CI-004",
            name="testing-quality",
            description="All code changes must have tests",
            category="core_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            config={"task_type": ["IMPLEMENTATION", "BUGFIX"]},
            enabled=True
        ),
        # GUIDE rule (applies to all tasks)
        Rule(
            project_id=test_project.id,
            rule_id="GR-001",
            name="search-before-create",
            description="Search existing code before creating new",
            category="general_rules",
            enforcement_level=EnforcementLevel.GUIDE,
            config={},
            enabled=True
        ),
        # LIMIT rule (task type specific)
        Rule(
            project_id=test_project.id,
            rule_id="WR-001",
            name="feature-requires-design",
            description="FEATURE work items require DESIGN task",
            category="workflow_rules",
            enforcement_level=EnforcementLevel.LIMIT,
            config={"task_type": ["DESIGN"]},
            enabled=True
        ),
        # Disabled rule (should not be loaded)
        Rule(
            project_id=test_project.id,
            rule_id="DP-999",
            name="disabled-rule",
            description="This rule is disabled",
            category="development_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            config={},
            enabled=False
        ),
    ]

    created_rules = []
    for rule in rules:
        created_rules.append(rule_methods.create_rule(db_service, rule))

    return created_rules


def test_rules_loaded_in_context(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that rules are loaded and included in context payload."""
    # Create assembly service
    service = ContextAssemblyService(db_service, tmp_path)

    # Assemble context
    payload = service.assemble_task_context(test_task.id)

    # Verify rules are loaded
    assert len(payload.applicable_rules) > 0, "No rules loaded"
    assert len(payload.blocking_rules) > 0, "No blocking rules loaded"
    assert payload.rule_summary != "", "Rule summary is empty"

    # Verify disabled rule is not included
    rule_ids = [r.rule_id for r in payload.applicable_rules]
    assert "DP-999" not in rule_ids, "Disabled rule should not be loaded"


def test_rules_filtered_by_task_type(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that rules are filtered by task type."""
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    rule_ids = [r.rule_id for r in payload.applicable_rules]

    # Should include rules that apply to IMPLEMENTATION tasks
    assert "DP-001" in rule_ids, "DP-001 should apply to IMPLEMENTATION tasks"
    assert "CI-004" in rule_ids, "CI-004 should apply to IMPLEMENTATION tasks"

    # Should include rules with no task_type filter (apply to all)
    assert "GR-001" in rule_ids, "GR-001 should apply to all tasks"

    # Should NOT include rules for other task types
    assert "WR-001" not in rule_ids, "WR-001 should only apply to DESIGN tasks"


def test_blocking_rules_separated(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that BLOCK-level rules are separated."""
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    # All blocking rules should have BLOCK enforcement level
    for rule in payload.blocking_rules:
        assert rule.enforcement_level == EnforcementLevel.BLOCK

    # Blocking rules should be subset of applicable rules
    blocking_ids = {r.rule_id for r in payload.blocking_rules}
    applicable_ids = {r.rule_id for r in payload.applicable_rules}
    assert blocking_ids.issubset(applicable_ids)


def test_rule_summary_format(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that rule summary is formatted correctly."""
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    summary = payload.rule_summary

    # Verify structure
    assert "## Applicable Rules" in summary
    assert "BLOCK" in summary
    assert "GUIDE" in summary

    # Verify BLOCK rules are listed
    assert "DP-001" in summary
    assert "CI-004" in summary

    # Verify GUIDE rules are listed
    assert "GR-001" in summary


def test_rule_summary_prioritizes_blocking_rules(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that rule summary prioritizes BLOCK rules."""
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    summary = payload.rule_summary

    # BLOCK section should appear before GUIDE section
    block_pos = summary.find("BLOCK Rules")
    guide_pos = summary.find("GUIDE Rules")

    assert block_pos > 0, "BLOCK rules section not found"
    assert guide_pos > 0, "GUIDE rules section not found"
    assert block_pos < guide_pos, "BLOCK rules should appear before GUIDE rules"


def test_graceful_degradation_no_rules(db_service, test_project, test_task, tmp_path):
    """Test graceful degradation when no rules are configured."""
    # Don't create any rules
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    # Should not fail, just have empty rule lists
    assert payload.applicable_rules == []
    assert payload.blocking_rules == []
    assert "No rules applicable" in payload.rule_summary or payload.rule_summary == ""


def test_multiple_task_types_in_rule_config(db_service, test_project, test_work_item, test_rules, tmp_path):
    """Test rules that apply to multiple task types."""
    from agentpm.core.database.methods import tasks

    # Create BUGFIX task (CI-004 should apply to both IMPLEMENTATION and BUGFIX)
    bugfix_task = Task(
        work_item_id=test_work_item.id,
        name="Fix bug",
        description="Bug fix task",
        type=TaskType.BUGFIX,
        status=TaskStatus.ACTIVE,
        effort_hours=2.0
    )
    bugfix_task = tasks.create_task(db_service, bugfix_task)

    # Assemble context for bugfix task
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(bugfix_task.id)

    rule_ids = [r.rule_id for r in payload.applicable_rules]

    # CI-004 should apply to BUGFIX tasks
    assert "CI-004" in rule_ids, "CI-004 should apply to BUGFIX tasks"


def test_rule_summary_truncates_long_descriptions(db_service, test_project, test_task, tmp_path):
    """Test that long rule descriptions are truncated in summary."""
    from agentpm.core.database.methods import rules as rule_methods

    # Create rule with very long description
    long_rule = Rule(
        project_id=test_project.id,
        rule_id="LR-001",
        name="long-description-rule",
        description="This is a very long description that should be truncated in the summary to keep the context lean and avoid overwhelming agents with too much text that they don't need to read in full detail right now.",
        category="test",
        enforcement_level=EnforcementLevel.BLOCK,
        config={"task_type": ["IMPLEMENTATION"]},
        enabled=True
    )
    rule_methods.create_rule(db_service, long_rule)

    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    # Verify description is truncated with ellipsis
    assert "..." in payload.rule_summary


def test_rules_warning_in_payload(db_service, test_project, test_task, test_rules, tmp_path):
    """Test that rules loading adds informational warning."""
    service = ContextAssemblyService(db_service, tmp_path)
    payload = service.assemble_task_context(test_task.id)

    # Should have warning about loaded rules
    rule_warnings = [w for w in payload.warnings if "rules" in w.lower()]
    assert len(rule_warnings) > 0, "No warning about loaded rules"

    # Warning should indicate count
    assert any("BLOCK" in w for w in rule_warnings), "Warning should mention BLOCK rules"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
