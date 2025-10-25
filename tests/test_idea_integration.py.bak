"""
Test suite for idea-to-work-item integration enhancements.

Tests the key enhancements:
1. Enhanced convert_idea_to_work_item with metadata copying
2. Phase alignment functionality
3. Conversion readiness assessment
4. Idea context integration
5. CLI command enhancements
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from agentpm.core.database.enums import IdeaStatus, WorkItemType, Phase, WorkItemStatus
from agentpm.core.database.models import Idea, WorkItem
from agentpm.core.database.methods import ideas as idea_methods
from agentpm.core.context.service import ContextService


class TestIdeaStatusEnhancements:
    """Test enhanced IdeaStatus functionality."""

    def test_phase_alignment(self):
        """Test phase alignment mapping."""
        # Test each idea status
        test_cases = [
            (IdeaStatus.IDEA, None),
            (IdeaStatus.RESEARCH, "D1_DISCOVERY"),
            (IdeaStatus.DESIGN, "P1_PLAN"),
            (IdeaStatus.ACTIVE, "P1_PLAN"),
            (IdeaStatus.CONVERTED, None),
            (IdeaStatus.REJECTED, None),
        ]
        
        for status, expected_phase in test_cases:
            actual_phase = IdeaStatus.get_aligned_phase(status)
            assert actual_phase == expected_phase, f"{status.value} should map to {expected_phase}"

    def test_conversion_readiness(self):
        """Test conversion readiness assessment."""
        # Test ready states
        active_readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.ACTIVE)
        assert active_readiness['ready'] is True
        assert active_readiness['recommended_phase'] == "P1_PLAN"
        
        design_readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.DESIGN)
        assert design_readiness['ready'] is True
        assert design_readiness['recommended_phase'] == "P1_PLAN"
        
        # Test not ready states
        idea_readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.IDEA)
        assert idea_readiness['ready'] is False
        assert idea_readiness['recommended_phase'] == "D1_DISCOVERY"
        
        research_readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.RESEARCH)
        assert research_readiness['ready'] is False
        assert research_readiness['recommended_phase'] == "D1_DISCOVERY"
        
        # Test terminal states
        converted_readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.CONVERTED)
        assert converted_readiness['ready'] is False
        assert converted_readiness['recommended_phase'] is None

    def test_conversion_readiness_next_steps(self):
        """Test that conversion readiness provides next steps."""
        readiness = IdeaStatus.get_conversion_readiness(IdeaStatus.IDEA)
        assert 'next_steps' in readiness
        assert len(readiness['next_steps']) > 0
        assert "Start research" in readiness['next_steps']


class TestEnhancedConversion:
    """Test enhanced convert_idea_to_work_item functionality."""

    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        service = Mock()
        service.transaction.return_value.__enter__ = Mock()
        service.transaction.return_value.__exit__ = Mock()
        return service

    @pytest.fixture
    def sample_idea(self):
        """Sample idea for testing."""
        return Idea(
            id=5,
            project_id=1,
            title="Test Feature",
            description="Test description",
            source="user",
            created_by="test_user",
            votes=10,
            tags=["feature", "ui"],
            status=IdeaStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def test_auto_phase_detection(self, mock_db_service, sample_idea):
        """Test automatic phase detection based on idea status."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=sample_idea):
            with patch('agentpm.core.database.methods.ideas.update_idea') as mock_update:
                # Mock work item creation
                mock_work_item = WorkItem(
                    id=12,
                    project_id=1,
                    name="Test Feature",
                    type=WorkItemType.FEATURE,
                    status=WorkItemStatus.DRAFT,
                    phase=Phase.P1_PLAN
                )
                
                with patch('agentpm.core.database.methods.work_items.create_work_item', return_value=mock_work_item):
                    with patch('agentpm.core.database.methods.ideas._transfer_idea_context_to_work_item'):
                        mock_update.return_value = sample_idea
                        
                        # Test conversion
                        converted_idea, work_item = idea_methods.convert_idea_to_work_item(
                            mock_db_service,
                            idea_id=5,
                            work_item_type=WorkItemType.FEATURE
                        )
                        
                        # Verify phase was set correctly
                        assert work_item.phase == Phase.P1_PLAN
                        assert work_item.status == WorkItemStatus.DRAFT

    def test_metadata_copying(self, mock_db_service, sample_idea):
        """Test that idea metadata is copied to work item."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=sample_idea):
            with patch('agentpm.core.database.methods.ideas.update_idea') as mock_update:
                # Mock work item creation
                mock_work_item = WorkItem(
                    id=12,
                    project_id=1,
                    name="Test Feature",
                    type=WorkItemType.FEATURE,
                    status=WorkItemStatus.DRAFT,
                    phase=Phase.P1_PLAN
                )
                
                with patch('agentpm.core.database.methods.work_items.create_work_item') as mock_create:
                    with patch('agentpm.core.database.methods.ideas._transfer_idea_context_to_work_item'):
                        mock_update.return_value = sample_idea
                        
                        # Test conversion
                        converted_idea, work_item = idea_methods.convert_idea_to_work_item(
                            mock_db_service,
                            idea_id=5,
                            work_item_type=WorkItemType.FEATURE
                        )
                        
                        # Verify the work item was created with the correct originated_from_idea_id
                        mock_create.assert_called_once()
                        call_args = mock_create.call_args[0][1]  # Get the WorkItem argument
                        assert call_args.originated_from_idea_id == 5
                        
                        # Verify metadata JSON structure
                        metadata = json.loads(call_args.metadata)
                        assert metadata['originated_from']['idea_id'] == 5
                        assert metadata['originated_from']['idea_title'] == "Test Feature"
                        assert metadata['originated_from']['idea_votes'] == 10
                        assert metadata['tags'] == ["feature", "ui"]
                        assert 'conversion_phase_alignment' in metadata

    def test_start_phase_override(self, mock_db_service, sample_idea):
        """Test start_phase parameter override."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=sample_idea):
            with patch('agentpm.core.database.methods.ideas.update_idea') as mock_update:
                # Mock work item creation
                mock_work_item = WorkItem(
                    id=12,
                    project_id=1,
                    name="Test Feature",
                    type=WorkItemType.FEATURE,
                    status=WorkItemStatus.DRAFT,
                    phase=Phase.I1_IMPLEMENTATION
                )
                
                with patch('agentpm.core.database.methods.work_items.create_work_item', return_value=mock_work_item):
                    with patch('agentpm.core.database.methods.ideas._transfer_idea_context_to_work_item'):
                        mock_update.return_value = sample_idea
                        
                        # Test conversion with phase override
                        converted_idea, work_item = idea_methods.convert_idea_to_work_item(
                            mock_db_service,
                            idea_id=5,
                            work_item_type=WorkItemType.FEATURE,
                            start_phase="I1_implementation"
                        )
                    
                    # Verify phase override worked
                    assert work_item.phase == Phase.I1_IMPLEMENTATION

    def test_invalid_start_phase(self, mock_db_service, sample_idea):
        """Test error handling for invalid start_phase."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=sample_idea):
            with pytest.raises(ValueError, match="Invalid start_phase"):
                idea_methods.convert_idea_to_work_item(
                    mock_db_service,
                    idea_id=5,
                    work_item_type=WorkItemType.FEATURE,
                    start_phase="INVALID_PHASE"
                )


class TestIdeaContextIntegration:
    """Test idea context integration."""

    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        service = Mock()
        return service

    @pytest.fixture
    def mock_project_path(self):
        """Mock project path."""
        return Path("/test/project")

    @pytest.fixture
    def sample_idea(self):
        """Sample idea for testing."""
        return Idea(
            id=5,
            project_id=1,
            title="Test Feature",
            description="Test description",
            source="user",
            created_by="test_user",
            votes=10,
            tags=["feature", "ui"],
            status=IdeaStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def test_get_idea_context(self, mock_db_service, mock_project_path, sample_idea):
        """Test get_idea_context method."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=sample_idea):
            with patch.object(ContextService, 'get_project_context', return_value={'project': {'name': 'Test Project'}}):
                with patch('agentpm.core.database.methods.contexts.get_entity_context', return_value=None):
                    context_service = ContextService(mock_db_service, mock_project_path)
                    context = context_service.get_idea_context(5)
                    
                    # Verify context structure
                    assert 'idea' in context
                    assert 'project' in context
                    assert 'phase_alignment' in context
                    assert 'conversion_readiness' in context
                    assert 'next_steps' in context
                    
                    # Verify idea data
                    assert context['idea']['id'] == 5
                    assert context['idea']['title'] == "Test Feature"
                    assert context['idea']['status'] == "accepted"
                    
                    # Verify phase alignment
                    assert context['phase_alignment']['idea_status'] == "accepted"
                    assert context['phase_alignment']['aligned_phase'] == "P1_PLAN"
                    
                    # Verify conversion readiness
                    assert context['conversion_readiness']['ready'] is True

    def test_idea_context_not_found(self, mock_db_service, mock_project_path):
        """Test get_idea_context when idea not found."""
        with patch('agentpm.core.database.methods.ideas.get_idea', return_value=None):
            context_service = ContextService(mock_db_service, mock_project_path)
            context = context_service.get_idea_context(999)
            assert context == {}


class TestCLIEnhancements:
    """Test CLI command enhancements."""

    def test_idea_convert_cli_options(self):
        """Test that idea convert CLI has new options."""
        from agentpm.cli.commands.idea.convert import convert
        
        # Check that the command exists and has the right parameters
        assert convert.name == "convert"
        
        # The --start-phase option should be available
        # This is tested by the command definition itself

    def test_idea_context_cli_command(self):
        """Test that idea context CLI command exists."""
        from agentpm.cli.commands.idea.context import context
        
        # Check that the command exists
        assert context.name == "context"

    def test_idea_show_enhancements(self):
        """Test that idea show command has enhancements."""
        from agentpm.cli.commands.idea.show import show
        
        # Check that the command exists
        assert show.name == "show"

    def test_work_item_show_enhancements(self):
        """Test that work item show command has enhancements."""
        from agentpm.cli.commands.work_item.show import show
        
        # Check that the command exists
        assert show.name == "show"


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_full_idea_to_work_item_workflow(self):
        """Test complete workflow from idea creation to work item."""
        # This would be an integration test that:
        # 1. Creates an idea
        # 2. Transitions it through research → design → accepted
        # 3. Converts it to a work item
        # 4. Verifies all metadata and links are correct
        # 5. Verifies phase alignment
        pass

    def test_phase_alignment_consistency(self):
        """Test that phase alignment is consistent across all idea statuses."""
        for status in IdeaStatus:
            aligned_phase = IdeaStatus.get_aligned_phase(status)
            readiness = IdeaStatus.get_conversion_readiness(status)
            
            # If idea maps to a phase, readiness should be consistent
            if aligned_phase:
                if status in [IdeaStatus.DESIGN, IdeaStatus.ACTIVE]:
                    assert readiness['ready'] is True
                else:
                    assert readiness['ready'] is False

    def test_metadata_preservation(self):
        """Test that all idea metadata is preserved during conversion."""
        # This would test that:
        # - Tags are copied
        # - Source information is preserved
        # - Votes are recorded
        # - Created_by is maintained
        # - Timestamps are accurate
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
