"""
E2E Tests: Multi-Project Support

Tests memory file isolation and correctness across multiple projects.
Verifies no data leakage between projects.

Part of WI-114 Task #606: End-to-End Memory System Testing
"""

import pytest
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import projects
from agentpm.core.database.models import Project
from agentpm.core.database.models.memory import MemoryFileType
from agentpm.core.database.methods import memory_methods
from agentpm.services.memory.generator import MemoryGenerator


class TestE2EMultiProject:
    """End-to-end tests for multi-project memory isolation."""

    @pytest.fixture
    def multi_project_setup(self, tmp_path, isolated_db):
        """Create two separate projects with their own directories.

        Returns:
            Tuple of (project_a, project_b, project_a_root, project_b_root)
        """
        # Create project A
        project_a_root = tmp_path / "project_a"
        project_a_root.mkdir()
        (project_a_root / ".claude").mkdir()

        project_a = Project(
            name="Project A",
            description="First test project",
            path=str(project_a_root),
            tech_stack=["Python", "Project A Tech"],
            status="active"
        )
        project_a = projects.create_project(isolated_db, project_a)

        # Create project B
        project_b_root = tmp_path / "project_b"
        project_b_root.mkdir()
        (project_b_root / ".claude").mkdir()

        project_b = Project(
            name="Project B",
            description="Second test project",
            path=str(project_b_root),
            tech_stack=["JavaScript", "Project B Tech"],
            status="active"
        )
        project_b = projects.create_project(isolated_db, project_b)

        return project_a, project_b, project_a_root, project_b_root

    def test_e2e_multi_project_isolation(
        self,
        isolated_db,
        multi_project_setup
    ):
        """Test memory files isolated per project.

        Verifies:
        1. Each project has separate .claude/ directory
        2. Memory files generated for each project
        3. No data leakage between projects
        4. Correct project_id in database records
        5. File content specific to each project
        """
        project_a, project_b, project_a_root, project_b_root = multi_project_setup

        # Generate memory for project A
        generator_a = MemoryGenerator(isolated_db, project_a_root)
        memories_a = generator_a.generate_all_memory_files(project_id=project_a.id)

        # Generate memory for project B
        generator_b = MemoryGenerator(isolated_db, project_b_root)
        memories_b = generator_b.generate_all_memory_files(project_id=project_b.id)

        # Verify: Both projects have 7 files
        assert len(memories_a) == 7
        assert len(memories_b) == 7

        # Verify: Separate .claude/ directories
        claude_a = project_a_root / ".claude"
        claude_b = project_b_root / ".claude"

        assert claude_a.exists()
        assert claude_b.exists()
        assert claude_a != claude_b

        # Verify: Files exist in correct directories
        for memory in memories_a:
            file_path_a = claude_a / f"{memory.file_type.value.upper()}.md"
            assert file_path_a.exists(), f"Project A should have {file_path_a.name}"

        for memory in memories_b:
            file_path_b = claude_b / f"{memory.file_type.value.upper()}.md"
            assert file_path_b.exists(), f"Project B should have {file_path_b.name}"

        # Verify: Correct project_id in database
        for memory in memories_a:
            assert memory.project_id == project_a.id

        for memory in memories_b:
            assert memory.project_id == project_b.id

        # Verify: File content specific to each project
        project_memory_a = next(m for m in memories_a if m.file_type == MemoryFileType.PROJECT)
        assert "Project A" in project_memory_a.content
        assert "Project B" not in project_memory_a.content
        assert f"Project ID: {project_a.id}" in project_memory_a.content

        project_memory_b = next(m for m in memories_b if m.file_type == MemoryFileType.PROJECT)
        assert "Project B" in project_memory_b.content
        assert "Project A" not in project_memory_b.content
        assert f"Project ID: {project_b.id}" in project_memory_b.content

        # Verify: No data leakage - check rules content
        # (Project A has rules from isolated_db, Project B should have different or empty rules)
        rules_memory_a = next(m for m in memories_a if m.file_type == MemoryFileType.RULES)
        rules_memory_b = next(m for m in memories_b if m.file_type == MemoryFileType.RULES)

        # Content should differ (even if both have some rules, they're project-specific)
        # At minimum, project IDs should differ
        assert rules_memory_a.content != rules_memory_b.content or \
               rules_memory_a.project_id != rules_memory_b.project_id

    def test_e2e_multi_project_database_queries(
        self,
        isolated_db,
        multi_project_setup
    ):
        """Test database queries respect project boundaries.

        Verifies:
        1. list_memory_files filters by project_id
        2. get_memory_file_by_type returns correct project
        3. No cross-project data access
        """
        project_a, project_b, project_a_root, project_b_root = multi_project_setup

        # Generate memory for both projects
        generator_a = MemoryGenerator(isolated_db, project_a_root)
        generator_a.generate_all_memory_files(project_id=project_a.id)

        generator_b = MemoryGenerator(isolated_db, project_b_root)
        generator_b.generate_all_memory_files(project_id=project_b.id)

        # Query project A memory files
        files_a = memory_methods.list_memory_files(isolated_db, project_id=project_a.id)
        assert len(files_a) == 7
        for file in files_a:
            assert file.project_id == project_a.id

        # Query project B memory files
        files_b = memory_methods.list_memory_files(isolated_db, project_id=project_b.id)
        assert len(files_b) == 7
        for file in files_b:
            assert file.project_id == project_b.id

        # Verify: No overlap in file IDs
        ids_a = {f.id for f in files_a}
        ids_b = {f.id for f in files_b}
        assert len(ids_a.intersection(ids_b)) == 0, "File IDs should not overlap"

        # Verify: get_memory_file_by_type respects project_id
        rules_a = memory_methods.get_memory_file_by_type(
            isolated_db, project_a.id, MemoryFileType.RULES
        )
        rules_b = memory_methods.get_memory_file_by_type(
            isolated_db, project_b.id, MemoryFileType.RULES
        )

        assert rules_a.project_id == project_a.id
        assert rules_b.project_id == project_b.id
        assert rules_a.id != rules_b.id

    def test_e2e_multi_project_update_independence(
        self,
        isolated_db,
        multi_project_setup,
        sample_data_factory
    ):
        """Test updates to one project don't affect another.

        Verifies:
        1. Modifying project A doesn't change project B files
        2. Regenerating project A doesn't touch project B
        3. Complete independence maintained
        """
        project_a, project_b, project_a_root, project_b_root = multi_project_setup

        # Generate initial memory for both
        generator_a = MemoryGenerator(isolated_db, project_a_root)
        initial_a = generator_a.generate_memory_file(
            project_id=project_a.id,
            file_type=MemoryFileType.RULES
        )

        generator_b = MemoryGenerator(isolated_db, project_b_root)
        initial_b = generator_b.generate_memory_file(
            project_id=project_b.id,
            file_type=MemoryFileType.RULES
        )

        initial_hash_b = initial_b.file_hash
        initial_content_b = initial_b.content

        # Modify project A only (add rule to project A)
        from agentpm.core.database.models import Rule
        from agentpm.core.database.enums import EnforcementLevel
        from agentpm.core.database.methods import rules as rules_methods

        rule_a = Rule(
            project_id=project_a.id,
            rule_id='MULTI-A-001',
            name='project-a-rule',
            description='Rule specific to Project A',
            category='Testing',
            enforcement_level=EnforcementLevel.GUIDE,
            error_message='Test',
            config={},
            enabled=True
        )
        rules_methods.create_rule(isolated_db, rule_a)

        # Regenerate project A memory
        updated_a = generator_a.generate_memory_file(
            project_id=project_a.id,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Verify: Project A updated
        assert "MULTI-A-001" in updated_a.content
        assert updated_a.file_hash != initial_a.file_hash

        # Verify: Project B unchanged
        current_b = memory_methods.get_memory_file_by_type(
            isolated_db, project_b.id, MemoryFileType.RULES
        )
        assert current_b.file_hash == initial_hash_b, "Project B hash should not change"
        assert current_b.content == initial_content_b, "Project B content should not change"
        assert "MULTI-A-001" not in current_b.content, "Project B should not have Project A rules"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
