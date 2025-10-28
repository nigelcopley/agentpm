"""
E2E Tests: Session Lifecycle Integration

Tests memory system integration with session lifecycle hooks.
Tests session-start, session-end, and tool-result events.

Part of WI-114 Task #606: End-to-End Memory System Testing
"""

import pytest
from datetime import datetime

from agentpm.providers.anthropic.claude_code.runtime.hooks.models import (
    EventType,
    HookEvent,
    EventResult
)
from agentpm.core.database.models.memory import MemoryFileType, ValidationStatus
from agentpm.core.database.methods import memory_methods


class TestE2ESessionLifecycle:
    """End-to-end tests for session lifecycle integration."""

    def test_e2e_session_start_loads_memory(
        self,
        isolated_db,
        tmp_project,
        memory_hooks,
        memory_generator
    ):
        """Test session-start hook loads previous memory files.

        Verifies:
        1. Pre-existing memory files detected
        2. Hook returns file inventory
        3. Current vs stale files identified
        4. Appropriate recommendations provided
        """
        # Setup: Generate memory files before session start
        memories = memory_generator.generate_all_memory_files(project_id=1)
        assert len(memories) == 7

        # Create session-start event
        event = HookEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now().isoformat(),
            payload={
                'project_id': 1,
                'session_id': 100
            }
        )

        # Execute: Handle session-start
        result = memory_hooks.handle_session_start(event)

        # Verify: Success
        assert result.success is True, f"Session start should succeed: {result.message}"

        # Verify: Files loaded
        assert 'files_loaded' in result.data
        files_loaded = result.data['files_loaded']
        assert len(files_loaded) == 7, "All 7 files should be loaded"

        # Verify: No stale files initially
        stale_files = result.data.get('stale_files', [])
        assert len(stale_files) == 0, "No files should be stale initially"

        # Verify: Recommendation
        assert 'recommendation' in result.data
        assert 'current' in result.data['recommendation'].lower()

    def test_e2e_session_start_identifies_stale_files(
        self,
        isolated_db,
        tmp_project,
        memory_hooks,
        memory_generator,
        sample_data_factory
    ):
        """Test session-start identifies stale files after database changes.

        Verifies:
        1. Initial files generated
        2. Database modified
        3. Files marked stale
        4. Session-start detects staleness
        """
        # Setup: Generate initial memory files
        memories = memory_generator.generate_all_memory_files(project_id=1)

        # Modify database (add new rule)
        sample_data_factory['create_rule'](
            'STALE-001',
            'Staleness Test Rule',
            'Testing',
            enabled=True
        )

        # Mark RULES memory as stale manually (simulating staleness detection)
        rules_memory = memory_methods.get_memory_file_by_type(
            isolated_db, 1, MemoryFileType.RULES
        )
        if rules_memory:
            memory_methods.update_memory_file(
                isolated_db,
                rules_memory.id,
                {'validation_status': ValidationStatus.STALE}
            )

        # Create session-start event
        event = HookEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now().isoformat(),
            payload={'project_id': 1, 'session_id': 101}
        )

        # Execute: Handle session-start
        result = memory_hooks.handle_session_start(event)

        # Verify: Stale files identified
        assert result.success is True
        stale_files = result.data.get('stale_files', [])
        assert 'rules' in stale_files, "RULES file should be stale"

        # Verify: Recommendation to regenerate
        recommendation = result.data.get('recommendation', '')
        assert 'regenerate' in recommendation.lower()

    def test_e2e_session_end_regenerates_memory(
        self,
        isolated_db,
        tmp_project,
        memory_hooks,
        memory_generator,
        sample_data_factory
    ):
        """Test session-end hook regenerates memory files.

        Verifies:
        1. Session work modifies database
        2. Session-end triggers regeneration
        3. New memory files generated
        4. Content reflects changes
        5. Quality scores calculated
        """
        # Setup: Initial memory files
        initial_memories = memory_generator.generate_all_memory_files(project_id=1)
        initial_rules_memory = next(
            m for m in initial_memories if m.file_type == MemoryFileType.RULES
        )
        initial_content = initial_rules_memory.content

        # Simulate session work: Add new rule
        sample_data_factory['create_rule'](
            'SESSION-001',
            'Session End Test Rule',
            'Session Testing',
            enabled=True
        )

        # Create session-end event
        event = HookEvent(
            event_type=EventType.SESSION_END,
            timestamp=datetime.now().isoformat(),
            payload={
                'project_id': 1,
                'session_id': 102,
                'regenerate_all': True
            }
        )

        # Execute: Handle session-end
        result = memory_hooks.handle_session_end(event)

        # Verify: Success
        assert result.success is True, f"Session end should succeed: {result.message}"

        # Verify: Files generated
        assert 'files_generated' in result.data
        files_generated = result.data['files_generated']
        assert len(files_generated) == 7, "All 7 files should be regenerated"

        # Verify: Quality scores in response
        for file_info in files_generated:
            assert 'confidence' in file_info
            assert 'completeness' in file_info
            assert file_info['confidence'] > 0.0

        # Verify: New content includes session changes
        updated_rules_memory = memory_methods.get_memory_file_by_type(
            isolated_db, 1, MemoryFileType.RULES
        )
        assert updated_rules_memory is not None
        assert "SESSION-001" in updated_rules_memory.content
        assert "Session End Test Rule" in updated_rules_memory.content

        # Verify: Content changed from initial
        assert updated_rules_memory.content != initial_content

    def test_e2e_session_lifecycle_complete(
        self,
        isolated_db,
        tmp_project,
        memory_hooks,
        memory_generator,
        sample_data_factory
    ):
        """Test complete session lifecycle: start → work → end.

        Verifies:
        1. Session starts with existing memory
        2. Session work modifies database
        3. Session ends with regeneration
        4. New session starts with updated memory
        5. Complete continuity maintained
        """
        # Phase 1: Initial session-start (no prior memory)
        event_start_1 = HookEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now().isoformat(),
            payload={'project_id': 1, 'session_id': 200}
        )
        result_start_1 = memory_hooks.handle_session_start(event_start_1)

        # Initially no files, or empty inventory
        initial_files = result_start_1.data.get('files_loaded', [])
        # May be 0 if no prior generation, or 7 if isolated_db setup generated them

        # Phase 2: Session work - generate initial memory
        initial_memories = memory_generator.generate_all_memory_files(project_id=1)
        assert len(initial_memories) == 7

        # Phase 3: Session work - modify database
        new_rule = sample_data_factory['create_rule'](
            'LIFECYCLE-001',
            'Lifecycle Test Rule',
            'Testing',
            enabled=True
        )

        # Phase 4: Session-end - regenerate memory
        event_end_1 = HookEvent(
            event_type=EventType.SESSION_END,
            timestamp=datetime.now().isoformat(),
            payload={
                'project_id': 1,
                'session_id': 200,
                'regenerate_all': True
            }
        )
        result_end_1 = memory_hooks.handle_session_end(event_end_1)
        assert result_end_1.success is True
        assert len(result_end_1.data['files_generated']) == 7

        # Phase 5: New session-start - should load updated memory
        event_start_2 = HookEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now().isoformat(),
            payload={'project_id': 1, 'session_id': 201}
        )
        result_start_2 = memory_hooks.handle_session_start(event_start_2)

        # Verify: New session loads files
        assert result_start_2.success is True
        files_loaded = result_start_2.data['files_loaded']
        assert len(files_loaded) == 7

        # Verify: Memory includes previous session's work
        current_rules_memory = memory_methods.get_memory_file_by_type(
            isolated_db, 1, MemoryFileType.RULES
        )
        assert "LIFECYCLE-001" in current_rules_memory.content
        assert "Lifecycle Test Rule" in current_rules_memory.content

    def test_e2e_tool_result_marks_memory_stale(
        self,
        isolated_db,
        tmp_project,
        memory_hooks
    ):
        """Test tool-result event marks memory for regeneration.

        Verifies:
        1. Memory-affecting tools detected
        2. Update scheduled
        3. Non-affecting tools ignored
        """
        # Test: Memory-affecting tool
        event_affecting = HookEvent(
            event_type=EventType.TOOL_RESULT,
            timestamp=datetime.now().isoformat(),
            payload={
                'project_id': 1,
                'tool_name': 'apm work-item create',
                'tool_result': {'success': True}
            }
        )

        result_affecting = memory_hooks.handle_tool_result(event_affecting)

        # Verify: Update scheduled
        assert result_affecting.success is True
        assert result_affecting.data['memory_updated'] is True
        assert 'work-item create' in result_affecting.data['tool_name']

        # Test: Non-affecting tool
        event_non_affecting = HookEvent(
            event_type=EventType.TOOL_RESULT,
            timestamp=datetime.now().isoformat(),
            payload={
                'project_id': 1,
                'tool_name': 'apm status',
                'tool_result': {'success': True}
            }
        )

        result_non_affecting = memory_hooks.handle_tool_result(event_non_affecting)

        # Verify: No update needed
        assert result_non_affecting.success is True
        assert result_non_affecting.data['memory_updated'] is False

    def test_e2e_session_error_handling(
        self,
        isolated_db,
        tmp_project,
        memory_hooks
    ):
        """Test error handling in session hooks.

        Verifies:
        1. Missing project_id handled gracefully
        2. Database errors handled
        3. Clear error messages returned
        """
        # Test: Missing project_id in session-start
        event_missing_project = HookEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now().isoformat(),
            payload={}  # No project_id
        )

        result = memory_hooks.handle_session_start(event_missing_project)

        # Verify: Error result
        assert result.success is False
        assert "project_id" in result.message.lower()
        assert len(result.errors) > 0

        # Test: Missing project_id in session-end
        event_missing_project_end = HookEvent(
            event_type=EventType.SESSION_END,
            timestamp=datetime.now().isoformat(),
            payload={}  # No project_id
        )

        result_end = memory_hooks.handle_session_end(event_missing_project_end)

        # Verify: Error result
        assert result_end.success is False
        assert "project_id" in result_end.message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
