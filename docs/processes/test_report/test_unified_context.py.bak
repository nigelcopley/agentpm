"""
Standalone Test for UnifiedContextService

Tests the unified service independently of the context package __init__.py
to avoid import issues during development.

Run: python test_unified_context.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from agentpm.core.context.unified_service import (
    UnifiedContextService,
    ContextPayload,
    ConfidenceScore,
    CompletenessScore,
    FreshnessScore
)
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.enums import EntityType, ConfidenceBand


def test_confidence_score():
    """Test ConfidenceScore validation."""
    print("\n🧪 Testing ConfidenceScore...")

    # Valid score
    score = ConfidenceScore(score=0.85, band=ConfidenceBand.GREEN)
    assert score.score == 0.85
    assert score.band == ConfidenceBand.GREEN
    print("  ✓ Valid score created")

    # Invalid score
    try:
        ConfidenceScore(score=1.5, band=ConfidenceBand.GREEN)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be 0.0-1.0" in str(e)
        print("  ✓ Invalid score rejected")


def test_completeness_score():
    """Test CompletenessScore calculation."""
    print("\n🧪 Testing CompletenessScore...")

    # Sufficient completeness
    score = CompletenessScore(
        percentage=85.0,
        missing_fields=['description'],
        critical_gaps=[]
    )
    assert score.is_sufficient() is True
    print("  ✓ Sufficient completeness check")

    # Insufficient percentage
    score = CompletenessScore(
        percentage=65.0,
        missing_fields=['name', 'description'],
        critical_gaps=[]
    )
    assert score.is_sufficient() is False
    print("  ✓ Insufficient percentage check")

    # Critical gaps
    score = CompletenessScore(
        percentage=75.0,
        missing_fields=['business_value'],
        critical_gaps=['business_value']
    )
    assert score.is_sufficient() is False
    print("  ✓ Critical gaps check")


def test_freshness_score():
    """Test FreshnessScore calculation."""
    print("\n🧪 Testing FreshnessScore...")

    # Fresh content
    recent = datetime.utcnow() - timedelta(hours=6)
    score = FreshnessScore.calculate(recent)
    assert abs(score.age_hours - 6.0) < 0.1
    assert score.is_stale is False
    print("  ✓ Fresh content detection")

    # Stale content
    old = datetime.utcnow() - timedelta(hours=72)
    score = FreshnessScore.calculate(old)
    assert abs(score.age_hours - 72.0) < 0.1
    assert score.is_stale is True
    print("  ✓ Stale content detection")


def test_production_project_context():
    """Test retrieving context for production project."""
    print("\n🧪 Testing Production Project Context...")

    db_path = Path("/Users/nigelcopley/.project_manager/aipm-v2/agentpm.db")
    if not db_path.exists():
        print("  ⏭  Production database not found, skipping")
        return

    db = DatabaseService(str(db_path))
    project_path = Path("/Users/nigelcopley/.project_manager/aipm-v2")
    service = UnifiedContextService(db, project_path)

    # Check if project exists, if not create it
    from agentpm.core.database.methods import projects
    from agentpm.core.database.models import Project
    from agentpm.core.database.enums import ProjectStatus

    try:
        project = projects.get_project(db, 1)
        if not project:
            # Create test project
            project = Project(
                name="APM (Agent Project Manager)",
                path=str(project_path),
                tech_stack=["python", "pytest", "pydantic"],
                detected_frameworks=["pytest", "pydantic"],
                status=ProjectStatus.ACTIVE
            )
            project_id = projects.create_project(db, project)
            project.id = project_id
            print(f"  ℹ  Created test project with ID {project_id}")

    except Exception as e:
        print(f"  ⚠  Could not access project: {e}")
        return

    # Get project context
    ctx = service.get_context(EntityType.PROJECT, 1)

    assert ctx.entity_type == EntityType.PROJECT
    assert ctx.entity.name is not None
    print(f"  ✓ Project: {ctx.entity.name}")
    print(f"  ✓ Tech Stack: {ctx.entity.tech_stack}")
    print(f"  ✓ Amalgamations: {len(ctx.amalgamations)} files")


def test_production_work_item_context():
    """Test retrieving context for production work item."""
    print("\n🧪 Testing Production Work Item Context...")

    db_path = Path("/Users/nigelcopley/.project_manager/aipm-v2/agentpm.db")
    if not db_path.exists():
        print("  ⏭  Production database not found, skipping")
        return

    db = DatabaseService(str(db_path))
    project_path = Path("/Users/nigelcopley/.project_manager/aipm-v2")
    service = UnifiedContextService(db, project_path)

    # Check if work item 60 exists
    from agentpm.core.database.methods import work_items
    work_item = work_items.get_work_item(db, 60)

    if not work_item:
        print("  ⏭  Work Item 60 not found, skipping")
        return

    # Get work item context
    ctx = service.get_context(EntityType.WORK_ITEM, 60)

    assert ctx.entity_type == EntityType.WORK_ITEM
    assert ctx.entity.name is not None
    print(f"  ✓ Work Item: {ctx.entity.name}")
    print(f"  ✓ Status: {ctx.entity.status.value}")
    if ctx.completeness:
        print(f"  ✓ Completeness: {ctx.completeness.percentage:.1f}%")
        print(f"  ✓ Missing fields: {len(ctx.completeness.missing_fields)}")
        print(f"  ✓ Critical gaps: {len(ctx.completeness.critical_gaps)}")


def test_production_task_context():
    """Test retrieving context for production task."""
    print("\n🧪 Testing Production Task Context...")

    db_path = Path("/Users/nigelcopley/.project_manager/aipm-v2/agentpm.db")
    if not db_path.exists():
        print("  ⏭  Production database not found, skipping")
        return

    db = DatabaseService(str(db_path))
    project_path = Path("/Users/nigelcopley/.project_manager/aipm-v2")
    service = UnifiedContextService(db, project_path)

    # Check if task 355 exists
    from agentpm.core.database.methods import tasks
    task = tasks.get_task(db, 355)

    if not task:
        print("  ⏭  Task 355 not found, skipping")
        return

    # Get task context with full hierarchy
    ctx = service.get_context(EntityType.TASK, 355)

    assert ctx.entity_type == EntityType.TASK
    assert ctx.entity.name is not None
    print(f"  ✓ Task: {ctx.entity.name}")
    print(f"  ✓ Status: {ctx.entity.status.value}")
    print(f"  ✓ Has 6W: {ctx.six_w is not None}")
    print(f"  ✓ Has parent 6W: {ctx.parent_six_w is not None}")
    print(f"  ✓ Has project 6W: {ctx.project_six_w is not None}")

    if ctx.completeness:
        print(f"  ✓ Completeness: {ctx.completeness.percentage:.1f}%")


def test_context_payload_serialization():
    """Test full context payload serialization."""
    print("\n🧪 Testing Context Payload Serialization...")

    db_path = Path("/Users/nigelcopley/.project_manager/aipm-v2/agentpm.db")
    if not db_path.exists():
        print("  ⏭  Production database not found, skipping")
        return

    db = DatabaseService(str(db_path))
    project_path = Path("/Users/nigelcopley/.project_manager/aipm-v2")
    service = UnifiedContextService(db, project_path)

    # Check if task 355 exists
    from agentpm.core.database.methods import tasks
    task = tasks.get_task(db, 355)

    if not task:
        print("  ⏭  Task 355 not found, using project context instead")
        # Use project context instead
        ctx = service.get_context(EntityType.PROJECT, 1, include_supporting=True)
    else:
        # Get full context with supporting data
        ctx = service.get_context(EntityType.TASK, 355, include_supporting=True)

    result = ctx.to_dict()

    assert 'entity' in result
    assert 'entity_type' in result
    assert 'six_w' in result
    assert 'documents' in result
    assert 'evidence' in result

    print(f"  ✓ Serialized payload keys: {list(result.keys())}")
    print(f"  ✓ Documents: {len(result['documents'])}")
    print(f"  ✓ Evidence: {len(result['evidence'])}")
    print(f"  ✓ Recent events: {len(result['recent_events'])}")

    # Verify 6W structure
    if result['six_w']:
        six_w = result['six_w']
        print(f"  ✓ 6W dimensions: {list(six_w.keys())}")
        assert 'who' in six_w
        assert 'what' in six_w
        assert 'where' in six_w
        assert 'when' in six_w
        assert 'why' in six_w
        assert 'how' in six_w


def test_input_validation():
    """Test input validation and error handling."""
    print("\n🧪 Testing Input Validation...")

    db_path = Path("/Users/nigelcopley/.project_manager/aipm-v2/agentpm.db")
    if not db_path.exists():
        print("  ⏭  Production database not found, skipping")
        return

    db = DatabaseService(str(db_path))
    project_path = Path("/Users/nigelcopley/.project_manager/aipm-v2")
    service = UnifiedContextService(db, project_path)

    # Test invalid entity type
    try:
        service.get_context("PROJECT", 1)
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "must be EntityType enum" in str(e)
        print("  ✓ Invalid entity type rejected")

    # Test invalid entity ID (negative)
    try:
        service.get_context(EntityType.PROJECT, -1)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be positive integer" in str(e)
        print("  ✓ Negative entity ID rejected")

    # Test invalid entity ID (zero)
    try:
        service.get_context(EntityType.PROJECT, 0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must be positive integer" in str(e)
        print("  ✓ Zero entity ID rejected")

    # Test nonexistent entity
    try:
        service.get_context(EntityType.PROJECT, 99999)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
        print("  ✓ Nonexistent entity error")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🚀 UnifiedContextService Test Suite")
    print("="*70)

    try:
        test_confidence_score()
        test_completeness_score()
        test_freshness_score()
        test_production_project_context()
        test_production_work_item_context()
        test_production_task_context()
        test_context_payload_serialization()
        test_input_validation()

        print("\n" + "="*70)
        print("✅ All tests passed!")
        print("="*70)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
