import pytest

from agentpm.core.database.enums import SummaryType, EntityType


class TestSummaryTypeEnum:
    """Test the SummaryType enum."""
    
    def test_all_summary_types_exist(self):
        """Test that all expected summary types are defined."""
        expected_types = [
            # Project-level summaries
            "project_milestone",
            "project_retrospective", 
            "project_status_report",
            "project_strategic_review",
            
            # Session-level summaries
            "session_handover",
            "session_progress",
            "session_error_analysis",
            "session_decision_log",
            
            # Work item-level summaries
            "work_item_progress",
            "work_item_milestone",
            "work_item_decision",
            "work_item_retrospective",
            
            # Task-level summaries
            "task_completion",
            "task_progress",
            "task_blocker_resolution",
            "task_technical_notes",
            
            # Legacy support
            "session",
            "milestone",
            "decision",
            "retrospective"
        ]
        
        for expected_type in expected_types:
            assert hasattr(SummaryType, expected_type.upper())
            assert getattr(SummaryType, expected_type.upper()).value == expected_type
    
    def test_choices_method(self):
        """Test that choices() returns all enum values."""
        choices = SummaryType.choices()
        
        assert isinstance(choices, list)
        assert len(choices) > 0
        
        # Check that all choices are strings
        for choice in choices:
            assert isinstance(choice, str)
        
        # Check that specific values are present
        assert "project_milestone" in choices
        assert "session_handover" in choices
        assert "work_item_progress" in choices
        assert "task_completion" in choices
        assert "session" in choices  # Legacy support
    
    def test_from_string_valid(self):
        """Test from_string with valid values."""
        # Test project-level types
        assert SummaryType.from_string("project_milestone") == SummaryType.PROJECT_MILESTONE
        assert SummaryType.from_string("project_retrospective") == SummaryType.PROJECT_RETROSPECTIVE
        
        # Test session-level types
        assert SummaryType.from_string("session_handover") == SummaryType.SESSION_HANDOVER
        assert SummaryType.from_string("session_progress") == SummaryType.SESSION_PROGRESS
        
        # Test work item-level types
        assert SummaryType.from_string("work_item_progress") == SummaryType.WORK_ITEM_PROGRESS
        assert SummaryType.from_string("work_item_milestone") == SummaryType.WORK_ITEM_MILESTONE
        
        # Test task-level types
        assert SummaryType.from_string("task_completion") == SummaryType.TASK_COMPLETION
        assert SummaryType.from_string("task_progress") == SummaryType.TASK_PROGRESS
        
        # Test legacy types
        assert SummaryType.from_string("session") == SummaryType.SESSION
        assert SummaryType.from_string("milestone") == SummaryType.MILESTONE
    
    def test_from_string_invalid(self):
        """Test from_string with invalid values."""
        with pytest.raises(ValueError) as exc_info:
            SummaryType.from_string("invalid_type")
        
        assert "Invalid SummaryType" in str(exc_info.value)
        assert "invalid_type" in str(exc_info.value)
        assert "Valid:" in str(exc_info.value)
    
    def test_labels_method(self):
        """Test that labels() returns human-readable labels."""
        labels = SummaryType.labels()
        
        assert isinstance(labels, dict)
        assert len(labels) > 0
        
        # Check that all labels are strings
        for label in labels.values():
            assert isinstance(label, str)
        
        # Check specific labels
        assert SummaryType.PROJECT_MILESTONE.value in labels
        assert "Project Milestone" in labels[SummaryType.PROJECT_MILESTONE.value]
        
        assert SummaryType.SESSION_HANDOVER.value in labels
        assert "Session Handover" in labels[SummaryType.SESSION_HANDOVER.value]
        
        assert SummaryType.WORK_ITEM_PROGRESS.value in labels
        assert "Work Item Progress" in labels[SummaryType.WORK_ITEM_PROGRESS.value]
        
        assert SummaryType.TASK_COMPLETION.value in labels
        assert "Task Completion" in labels[SummaryType.TASK_COMPLETION.value]
    
    def test_get_appropriate_types_project(self):
        """Test get_appropriate_types for project entity."""
        appropriate_types = SummaryType.get_appropriate_types(EntityType.PROJECT)
        
        assert isinstance(appropriate_types, list)
        assert len(appropriate_types) > 0
        
        # Should include project-level types
        assert SummaryType.PROJECT_MILESTONE in appropriate_types
        assert SummaryType.PROJECT_RETROSPECTIVE in appropriate_types
        assert SummaryType.PROJECT_STATUS_REPORT in appropriate_types
        assert SummaryType.PROJECT_STRATEGIC_REVIEW in appropriate_types
        
        # Should not include other entity types
        assert SummaryType.SESSION_HANDOVER not in appropriate_types
        assert SummaryType.WORK_ITEM_PROGRESS not in appropriate_types
        assert SummaryType.TASK_COMPLETION not in appropriate_types
    
    def test_get_appropriate_types_work_item(self):
        """Test get_appropriate_types for work item entity."""
        appropriate_types = SummaryType.get_appropriate_types(EntityType.WORK_ITEM)
        
        assert isinstance(appropriate_types, list)
        assert len(appropriate_types) > 0
        
        # Should include work item-level types
        assert SummaryType.WORK_ITEM_PROGRESS in appropriate_types
        assert SummaryType.WORK_ITEM_MILESTONE in appropriate_types
        assert SummaryType.WORK_ITEM_DECISION in appropriate_types
        assert SummaryType.WORK_ITEM_RETROSPECTIVE in appropriate_types
        
        # Should include legacy types for migration
        assert SummaryType.SESSION in appropriate_types
        assert SummaryType.MILESTONE in appropriate_types
        assert SummaryType.DECISION in appropriate_types
        assert SummaryType.RETROSPECTIVE in appropriate_types
        
        # Should not include other entity types
        assert SummaryType.PROJECT_MILESTONE not in appropriate_types
        assert SummaryType.SESSION_HANDOVER not in appropriate_types
        assert SummaryType.TASK_COMPLETION not in appropriate_types
    
    def test_get_appropriate_types_task(self):
        """Test get_appropriate_types for task entity."""
        appropriate_types = SummaryType.get_appropriate_types(EntityType.TASK)
        
        assert isinstance(appropriate_types, list)
        assert len(appropriate_types) > 0
        
        # Should include task-level types
        assert SummaryType.TASK_COMPLETION in appropriate_types
        assert SummaryType.TASK_PROGRESS in appropriate_types
        assert SummaryType.TASK_BLOCKER_RESOLUTION in appropriate_types
        assert SummaryType.TASK_TECHNICAL_NOTES in appropriate_types
        
        # Should not include other entity types
        assert SummaryType.PROJECT_MILESTONE not in appropriate_types
        assert SummaryType.SESSION_HANDOVER not in appropriate_types
        assert SummaryType.WORK_ITEM_PROGRESS not in appropriate_types
    
    def test_get_appropriate_types_idea(self):
        """Test get_appropriate_types for idea entity."""
        appropriate_types = SummaryType.get_appropriate_types(EntityType.IDEA)
        
        assert isinstance(appropriate_types, list)
        assert len(appropriate_types) > 0
        
        # For idea entity, should return all types (fallback behavior)
        assert SummaryType.PROJECT_MILESTONE in appropriate_types
        assert SummaryType.SESSION_HANDOVER in appropriate_types
        assert SummaryType.WORK_ITEM_PROGRESS in appropriate_types
        assert SummaryType.TASK_COMPLETION in appropriate_types
    
    def test_get_appropriate_types_other_entity(self):
        """Test get_appropriate_types for other entity types."""
        # Create a mock entity type for testing
        class MockEntityType:
            pass
        
        appropriate_types = SummaryType.get_appropriate_types(MockEntityType)
        
        assert isinstance(appropriate_types, list)
        assert len(appropriate_types) > 0
        
        # Should return all types (fallback behavior)
        assert SummaryType.PROJECT_MILESTONE in appropriate_types
        assert SummaryType.SESSION_HANDOVER in appropriate_types
        assert SummaryType.WORK_ITEM_PROGRESS in appropriate_types
        assert SummaryType.TASK_COMPLETION in appropriate_types
    
    def test_enum_values_are_strings(self):
        """Test that all enum values are strings."""
        for summary_type in SummaryType:
            assert isinstance(summary_type.value, str)
            assert len(summary_type.value) > 0
    
    def test_enum_values_are_unique(self):
        """Test that all enum values are unique."""
        values = [summary_type.value for summary_type in SummaryType]
        assert len(values) == len(set(values))
    
    def test_enum_names_are_unique(self):
        """Test that all enum names are unique."""
        names = [summary_type.name for summary_type in SummaryType]
        assert len(names) == len(set(names))
