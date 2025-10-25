"""
E2E Tests: Validation Integration

Tests complete validation workflow from detection to repair.
Tests file validation, hash verification, and repair workflows.

Part of WI-114 Task #606: End-to-End Memory System Testing
"""

import pytest
import hashlib
from pathlib import Path

from agentpm.core.database.models.memory import MemoryFileType, ValidationStatus
from agentpm.core.database.methods import memory_methods


class TestE2EValidation:
    """End-to-end tests for validation workflows."""

    def test_e2e_validation_complete_workflow(
        self,
        isolated_db,
        tmp_project,
        memory_generator
    ):
        """Test complete validation workflow.

        Workflow:
        1. Generate files
        2. Validate all files (should pass)
        3. Modify one file
        4. Validate again (should detect mismatch)
        5. Regenerate
        6. Validate again (should pass)

        Verifies:
        1. Fresh files validate successfully
        2. Modified files detected
        3. Hash mismatches identified
        4. Regeneration repairs issues
        """
        # Step 1: Generate files
        memories = memory_generator.generate_all_memory_files(project_id=1)
        assert len(memories) == 7

        # Step 2: Validate all files (should pass)
        validation_results_1 = []
        for memory in memories:
            file_path = tmp_project / ".claude" / f"{memory.file_type.value.upper()}.md"
            assert file_path.exists()

            # Read file and verify hash
            disk_content = file_path.read_text(encoding='utf-8')
            disk_hash = hashlib.sha256(disk_content.encode()).hexdigest()

            validation_results_1.append({
                'type': memory.file_type.value,
                'hash_match': disk_hash == memory.file_hash,
                'file_exists': file_path.exists(),
                'content_match': disk_content == memory.content
            })

        # Verify: All files valid initially
        for result in validation_results_1:
            assert result['file_exists'] is True
            assert result['hash_match'] is True
            assert result['content_match'] is True

        # Step 3: Modify one file (RULES.md)
        rules_file = tmp_project / ".claude" / "RULES.md"
        modified_content = "MODIFIED CONTENT - INVALID"
        rules_file.write_text(modified_content, encoding='utf-8')

        # Step 4: Validate again (should detect mismatch)
        rules_memory = next(m for m in memories if m.file_type == MemoryFileType.RULES)
        disk_content_modified = rules_file.read_text(encoding='utf-8')
        modified_hash = hashlib.sha256(disk_content_modified.encode()).hexdigest()

        # Verify: Hash mismatch detected
        assert modified_hash != rules_memory.file_hash, "Modified file should have different hash"
        assert disk_content_modified != rules_memory.content, "Content should differ"

        # Step 5: Regenerate to repair
        repaired_memory = memory_generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Step 6: Validate again (should pass)
        disk_content_repaired = rules_file.read_text(encoding='utf-8')
        repaired_hash = hashlib.sha256(disk_content_repaired.encode()).hexdigest()

        # Verify: Repaired file valid
        assert repaired_hash == repaired_memory.file_hash
        assert disk_content_repaired == repaired_memory.content
        assert "MODIFIED CONTENT" not in disk_content_repaired
        assert "APM (Agent Project Manager) Governance Rules" in disk_content_repaired

    def test_e2e_validation_repair_workflow(
        self,
        isolated_db,
        tmp_project,
        memory_generator
    ):
        """Test validation → repair workflow for multiple files.

        Verifies:
        1. Multiple files can be validated
        2. Issues detected across files
        3. Batch repair possible
        4. All files restored to valid state
        """
        # Generate initial files
        memories = memory_generator.generate_all_memory_files(project_id=1)

        # Introduce issues in multiple files
        corrupted_types = [MemoryFileType.RULES, MemoryFileType.WORKFLOW, MemoryFileType.AGENTS]

        for file_type in corrupted_types:
            file_path = tmp_project / ".claude" / f"{file_type.value.upper()}.md"
            file_path.write_text(f"CORRUPTED {file_type.value.upper()}", encoding='utf-8')

        # Validate all files (detect issues)
        issues = []
        for memory in memories:
            file_path = tmp_project / ".claude" / f"{memory.file_type.value.upper()}.md"
            disk_content = file_path.read_text(encoding='utf-8')
            disk_hash = hashlib.sha256(disk_content.encode()).hexdigest()

            if disk_hash != memory.file_hash:
                issues.append(memory.file_type)

        # Verify: Issues detected
        assert len(issues) == 3, "Should detect 3 corrupted files"
        assert set(issues) == set(corrupted_types)

        # Repair all corrupted files
        repaired = []
        for file_type in issues:
            repaired_memory = memory_generator.generate_memory_file(
                project_id=1,
                file_type=file_type,
                force_regenerate=True
            )
            repaired.append(repaired_memory)

        # Verify: All files repaired
        assert len(repaired) == 3

        for memory in repaired:
            file_path = tmp_project / ".claude" / f"{memory.file_type.value.upper()}.md"
            disk_content = file_path.read_text(encoding='utf-8')
            disk_hash = hashlib.sha256(disk_content.encode()).hexdigest()

            # Verify: File is now valid
            assert disk_hash == memory.file_hash
            assert disk_content == memory.content
            assert "CORRUPTED" not in disk_content

    def test_e2e_validation_missing_file_detection(
        self,
        isolated_db,
        tmp_project,
        memory_generator
    ):
        """Test detection of missing files.

        Verifies:
        1. Missing files detected
        2. Regeneration creates missing files
        3. All files present after repair
        """
        # Generate files
        memories = memory_generator.generate_all_memory_files(project_id=1)

        # Delete a file
        rules_file = tmp_project / ".claude" / "RULES.md"
        rules_file.unlink()
        assert not rules_file.exists()

        # Detect missing file
        rules_memory = next(m for m in memories if m.file_type == MemoryFileType.RULES)
        file_exists = rules_file.exists()

        # Verify: Missing detected
        assert file_exists is False

        # Repair by regenerating
        repaired_memory = memory_generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Verify: File recreated
        assert rules_file.exists()
        disk_content = rules_file.read_text(encoding='utf-8')
        assert len(disk_content) > 100
        assert "APM (Agent Project Manager) Governance Rules" in disk_content

    def test_e2e_validation_database_consistency(
        self,
        isolated_db,
        tmp_project,
        memory_generator
    ):
        """Test database and filesystem consistency validation.

        Verifies:
        1. Database records match filesystem
        2. Inconsistencies detected
        3. Consistency restored after repair
        """
        # Generate files
        memories = memory_generator.generate_all_memory_files(project_id=1)

        # Verify: Database and filesystem consistent
        for memory in memories:
            file_path = tmp_project / ".claude" / f"{memory.file_type.value.upper()}.md"

            # Database record exists
            db_record = memory_methods.get_memory_file_by_type(
                isolated_db, 1, memory.file_type
            )
            assert db_record is not None

            # File exists
            assert file_path.exists()

            # Content matches
            disk_content = file_path.read_text(encoding='utf-8')
            assert disk_content == db_record.content

            # Hash matches
            disk_hash = hashlib.sha256(disk_content.encode()).hexdigest()
            assert disk_hash == db_record.file_hash

        # Introduce inconsistency (modify file but not database)
        rules_file = tmp_project / ".claude" / "RULES.md"
        rules_file.write_text("INCONSISTENT STATE", encoding='utf-8')

        # Detect inconsistency
        rules_memory = memory_methods.get_memory_file_by_type(
            isolated_db, 1, MemoryFileType.RULES
        )
        disk_content = rules_file.read_text(encoding='utf-8')
        disk_hash = hashlib.sha256(disk_content.encode()).hexdigest()

        # Verify: Inconsistency detected
        assert disk_hash != rules_memory.file_hash
        assert disk_content != rules_memory.content

        # Repair: Regenerate from database truth
        repaired = memory_generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Verify: Consistency restored
        disk_content_repaired = rules_file.read_text(encoding='utf-8')
        disk_hash_repaired = hashlib.sha256(disk_content_repaired.encode()).hexdigest()

        assert disk_hash_repaired == repaired.file_hash
        assert disk_content_repaired == repaired.content
        assert "INCONSISTENT STATE" not in disk_content_repaired

    def test_e2e_validation_status_lifecycle(
        self,
        isolated_db,
        tmp_project,
        memory_generator
    ):
        """Test validation status lifecycle.

        States: validated → stale → validated

        Verifies:
        1. New files start as validated
        2. Can be marked stale
        3. Regeneration returns to validated
        4. Status transitions tracked
        """
        # Generate file (should be validated)
        memory = memory_generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES
        )

        # Verify: Initially validated
        assert memory.validation_status == ValidationStatus.VALIDATED
        assert memory.is_stale is False

        # Mark as stale
        memory_methods.update_memory_file(
            isolated_db,
            memory.id,
            {'validation_status': ValidationStatus.STALE}
        )

        # Verify: Now stale
        stale_memory = memory_methods.get_memory_file(isolated_db, memory.id)
        assert stale_memory.validation_status == ValidationStatus.STALE
        assert stale_memory.is_stale is True

        # Regenerate (should return to validated)
        fresh_memory = memory_generator.generate_memory_file(
            project_id=1,
            file_type=MemoryFileType.RULES,
            force_regenerate=True
        )

        # Verify: Back to validated
        assert fresh_memory.validation_status == ValidationStatus.VALIDATED
        assert fresh_memory.is_stale is False
        assert fresh_memory.id != memory.id  # New record created


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
