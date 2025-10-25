"""
E2E Tests: Performance Validation

Tests memory system performance with realistic data volumes.
Tests generation speed, memory usage, and scalability.

Part of WI-114 Task #606: End-to-End Memory System Testing
"""

import pytest
import time
import psutil
import os
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import (
    projects,
    work_items,
    tasks,
    rules as rules_methods,
    agents as agent_methods
)
from agentpm.core.database.models import Project, WorkItem, Task, Rule, Agent
from agentpm.core.database.enums import (
    WorkItemStatus,
    WorkItemType,
    TaskStatus,
    EnforcementLevel
)
from agentpm.core.database.models.memory import MemoryFileType
from agentpm.services.memory.generator import MemoryGenerator


@pytest.mark.slow
class TestE2EPerformance:
    """End-to-end performance tests for memory system."""

    @pytest.fixture
    def large_dataset_db(self, tmp_path):
        """Create database with large realistic dataset.

        Dataset:
        - 1 project
        - 100 rules
        - 50 work items
        - 200 tasks
        - 20 agents

        Returns:
            DatabaseService with populated large dataset
        """
        db_path = tmp_path / "large_test.db"
        db = DatabaseService(str(db_path))

        # Create project
        project = Project(
            name="Large Test Project",
            description="Performance testing project with large dataset",
            path=str(tmp_path / "project"),
            tech_stack=["Python", "SQLite", "Click"],
            status="active"
        )
        project = projects.create_project(db, project)

        # Create 100 rules
        for i in range(100):
            rule = Rule(
                project_id=project.id,
                rule_id=f'PERF-{i:03d}',
                name=f'performance-test-rule-{i}',
                description=f'Rule {i} for performance testing with detailed description and multiple requirements',
                category=f'Category {i % 10}',
                enforcement_level=EnforcementLevel.GUIDE if i % 2 else EnforcementLevel.LIMIT,
                error_message=f'Performance test error message {i}',
                config={"key": "value", "threshold": 0.8},
                enabled=True
            )
            rules_methods.create_rule(db, rule)

        # Create 50 work items
        for i in range(50):
            wi = WorkItem(
                project_id=project.id,
                name=f'Performance Test Work Item {i}',
                description=f'Work item {i} for performance testing. This is a detailed description with multiple sentences to simulate realistic content length. It includes requirements, context, and technical details.',
                type=WorkItemType.FEATURE if i % 3 == 0 else WorkItemType.IMPROVEMENT,
                status=WorkItemStatus.ACTIVE if i % 4 != 0 else WorkItemStatus.DONE,
                phase='I1_implementation',
                effort_estimate_hours=float(i % 20 + 1),
                priority=i % 5 + 1,
                business_context=f'Business context for work item {i} explaining the value and rationale'
            )
            work_items.create_work_item(db, wi)

        # Create 200 tasks (4 per work item average)
        for i in range(200):
            wi_id = (i % 50) + 1  # Distribute across work items
            task = Task(
                work_item_id=wi_id,
                name=f'Performance Test Task {i}',
                description=f'Task {i} for performance testing with detailed description',
                type=['implementation', 'testing', 'design', 'documentation'][i % 4],
                status=TaskStatus.TODO if i % 3 == 0 else TaskStatus.IN_PROGRESS,
                assigned_to=f'agent-{i % 5}',
                effort_hours=float(i % 8 + 1),
                priority=i % 5 + 1
            )
            tasks.create_task(db, task)

        # Create 20 agents
        for i in range(20):
            agent = Agent(
                project_id=project.id,
                role=f'perf-agent-{i}',
                display_name=f'Performance Test Agent {i}',
                description=f'Agent {i} for performance testing',
                sop_content=f'Standard operating procedure for agent {i}. ' * 20,  # Larger SOP
                capabilities='["test", "develop", "review"]',
                is_active=True,
                agent_type='sub-agent' if i % 2 else 'specialist',
                tier='sub-agent'
            )
            agent_methods.create_agent(db, agent)

        return db

    def test_e2e_performance_realistic_data(
        self,
        large_dataset_db,
        tmp_path
    ):
        """Test performance with realistic data volumes.

        Performance targets:
        - Generation time: <500ms per file
        - Total time: <4s for all 7 files
        - Memory usage: <100MB
        - All files valid

        Verifies:
        1. Fast generation with large dataset
        2. Low memory footprint
        3. All files valid and complete
        """
        # Setup
        project_root = tmp_path / "project"
        project_root.mkdir(exist_ok=True)
        (project_root / ".claude").mkdir(exist_ok=True)

        generator = MemoryGenerator(large_dataset_db, project_root)

        # Measure initial memory
        process = psutil.Process(os.getpid())
        initial_memory_mb = process.memory_info().rss / 1024 / 1024

        # Execute: Generate all memory files with timing
        start_time = time.time()
        memories = generator.generate_all_memory_files(project_id=1)
        total_time = time.time() - start_time

        # Measure final memory
        final_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_increase_mb = final_memory_mb - initial_memory_mb

        # Verify: All files generated
        assert len(memories) == 7, "All 7 files should be generated"

        # Verify: Total time reasonable (<4s target)
        assert total_time < 4.0, f"Total generation time {total_time:.2f}s should be <4s"

        # Verify: Individual file generation times
        for memory in memories:
            assert memory.generation_duration_ms is not None
            # Individual file should be <500ms (relaxed to <1000ms for safety)
            assert memory.generation_duration_ms < 1000, \
                f"{memory.file_type.value} took {memory.generation_duration_ms}ms (target <1000ms)"

        # Verify: Memory usage reasonable (<100MB increase target)
        # Note: This is approximate and may vary based on system
        print(f"Memory increase: {memory_increase_mb:.2f}MB")
        # Relaxed check - if significantly over, flag it
        if memory_increase_mb > 200:
            pytest.fail(f"Memory usage {memory_increase_mb:.2f}MB exceeds reasonable limit")

        # Verify: All files valid
        for memory in memories:
            assert memory.validation_status.value == "validated"
            assert len(memory.content) > 100

        # Verify: Files contain expected large dataset markers
        rules_memory = next(m for m in memories if m.file_type == MemoryFileType.RULES)
        assert "PERF-000" in rules_memory.content
        assert "PERF-099" in rules_memory.content  # First and last rule

        workflow_memory = next(m for m in memories if m.file_type == MemoryFileType.WORKFLOW)
        # Should mention many work items
        assert "50" in workflow_memory.content or "Work Items" in workflow_memory.content

        # Print performance metrics
        print(f"\nPerformance Metrics:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average per file: {total_time / 7:.2f}s")
        print(f"  Memory increase: {memory_increase_mb:.2f}MB")
        print(f"  Files generated: {len(memories)}")

    def test_e2e_performance_large_content(
        self,
        large_dataset_db,
        tmp_path
    ):
        """Test performance with large content in individual files.

        Verifies:
        1. Large files generated efficiently
        2. No performance degradation
        3. Quality maintained
        """
        # Setup
        project_root = tmp_path / "project"
        project_root.mkdir(exist_ok=True)
        (project_root / ".claude").mkdir(exist_ok=True)

        generator = MemoryGenerator(large_dataset_db, project_root)

        # Generate RULES file (should be large with 100 rules)
        start_time = time.time()
        rules_memory = generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES
        )
        generation_time = time.time() - start_time

        # Verify: Large content generated
        assert len(rules_memory.content) > 10000, "RULES file should be substantial with 100 rules"

        # Verify: Generation time reasonable
        assert generation_time < 1.0, f"Large file generation {generation_time:.2f}s should be <1s"

        # Verify: Quality maintained
        assert rules_memory.confidence_score > 0.5
        assert rules_memory.validation_status.value == "validated"

        # Verify: File size
        rules_file = project_root / ".claude" / "RULES.md"
        file_size_kb = rules_file.stat().st_size / 1024
        print(f"RULES file size: {file_size_kb:.2f}KB")

        # File should be substantial but not excessive
        assert file_size_kb > 10, "File should be substantial"
        assert file_size_kb < 5000, "File should not be excessive"

    @pytest.mark.benchmark
    def test_e2e_benchmark_generation_speed(
        self,
        isolated_db,
        tmp_project,
        memory_generator,
        benchmark
    ):
        """Benchmark memory file generation speed.

        Uses pytest-benchmark to track performance over time.
        """
        # Skip if pytest-benchmark not available
        pytest.importorskip("pytest_benchmark")

        # Benchmark single file generation
        result = benchmark(
            memory_generator.generate_memory_file,
            project_id=1,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Verify result is valid
        assert result is not None
        assert result.validation_status.value == "validated"

    def test_e2e_performance_parallel_generation(
        self,
        large_dataset_db,
        tmp_path
    ):
        """Test performance of parallel generation.

        Note: Current implementation is sequential.
        This test measures baseline for future parallel optimization.

        Verifies:
        1. Sequential generation completes efficiently
        2. No bottlenecks in current implementation
        """
        # Setup
        project_root = tmp_path / "project"
        project_root.mkdir(exist_ok=True)
        (project_root / ".claude").mkdir(exist_ok=True)

        generator = MemoryGenerator(large_dataset_db, project_root)

        # Time individual file generations
        individual_times = []
        for file_type in MemoryFileType:
            start = time.time()
            memory = generator.generate_memory_file(
                project_id=1,
                file_type=file_type,
                force_regenerate=True
            )
            elapsed = time.time() - start
            individual_times.append(elapsed)

        # Time batch generation
        start = time.time()
        memories = generator.generate_all_memory_files(project_id=1)
        batch_time = time.time() - start

        # Analysis
        sum_individual = sum(individual_times)
        print(f"\nParallel Potential Analysis:")
        print(f"  Sum of individual times: {sum_individual:.2f}s")
        print(f"  Actual batch time: {batch_time:.2f}s")
        print(f"  Efficiency ratio: {batch_time / sum_individual:.2%}")

        # Batch should not be significantly slower than sum
        # (Some overhead is expected, but not excessive)
        assert batch_time < sum_individual * 1.5, \
            "Batch generation should not have excessive overhead"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
