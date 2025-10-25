import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.core.context.unified_service import UnifiedContextService, ContextPayload
from agentpm.core.database.models import Summary, Project, WorkItem, Task, Idea
from agentpm.core.database.enums import EntityType, SummaryType


class TestUnifiedContextServiceSummaries:
    """Test the summary integration in UnifiedContextService."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    @pytest.fixture
    def mock_context_service(self, mock_db_service):
        """Create a mock context service."""
        return UnifiedContextService(mock_db_service)
    
    @pytest.fixture
    def sample_summaries(self):
        """Create sample summaries for testing."""
        return [
            Summary(
                id=1,
                entity_type=EntityType.PROJECT,
                entity_id=1,
                summary_type=SummaryType.PROJECT_MILESTONE,
                summary_text="Project milestone achieved successfully.",
                context_metadata={"decisions": ["Use React"]},
                session_id="session-123",
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                created_by="agent-1"
            ),
            Summary(
                id=2,
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text="Work item progress update.",
                context_metadata={"blockers": ["API not ready"]},
                session_id="session-456",
                created_at=datetime(2024, 1, 15, 11, 30, 0),
                created_by="agent-2"
            ),
            Summary(
                id=3,
                entity_type=EntityType.TASK,
                entity_id=1,
                summary_type=SummaryType.TASK_COMPLETION,
                summary_text="Task completed successfully.",
                context_metadata=None,
                session_id=None,
                created_at=datetime(2024, 1, 15, 12, 30, 0),
                created_by="agent-1"
            )
        ]
    
    def test_load_summaries_success(self, mock_context_service, sample_summaries):
        """Test successful summary loading."""
        with patch('agentpm.core.context.unified_service.summary_methods.get_summaries_for_entity', return_value=sample_summaries):
            result = mock_context_service._load_summaries(EntityType.WORK_ITEM, 1)
            
            assert len(result) == 3
            assert result[0].id == 1
            assert result[1].id == 2
            assert result[2].id == 3
    
    def test_load_summaries_empty(self, mock_context_service):
        """Test summary loading when no summaries exist."""
        with patch('agentpm.core.context.unified_service.summary_methods.get_summaries_for_entity', return_value=[]):
            result = mock_context_service._load_summaries(EntityType.WORK_ITEM, 1)
            
            assert result == []
    
    def test_load_summaries_exception(self, mock_context_service):
        """Test summary loading with exception (graceful degradation)."""
        with patch('agentpm.core.context.unified_service.summary_methods.get_summaries_for_entity', side_effect=Exception("Database error")):
            result = mock_context_service._load_summaries(EntityType.WORK_ITEM, 1)
            
            # Should return empty list on exception
            assert result == []
    
    def test_load_hierarchical_summaries_success(self, mock_context_service, sample_summaries):
        """Test successful hierarchical summary loading."""
        with patch('agentpm.core.context.unified_service.summary_methods.get_summaries_for_entity', return_value=sample_summaries):
            with patch('agentpm.core.context.unified_service.summary_methods.get_recent_summaries', return_value=sample_summaries):
                result = mock_context_service._load_hierarchical_summaries(EntityType.WORK_ITEM, 1)
                
                assert isinstance(result, dict)
                assert 'project_summaries' in result
                assert 'session_summaries' in result
                assert 'work_item_summaries' in result
                assert 'task_summaries' in result
                assert 'recent_summaries' in result
                assert 'summary_timeline' in result
                
                # Check categorization
                assert len(result['project_summaries']) == 1
                assert len(result['work_item_summaries']) == 1
                assert len(result['task_summaries']) == 1
                assert len(result['recent_summaries']) == 3
                assert len(result['summary_timeline']) == 6  # 3 from entity + 3 from recent
    
    def test_load_hierarchical_summaries_exception(self, mock_context_service):
        """Test hierarchical summary loading with exception (graceful degradation)."""
        with patch('agentpm.core.context.unified_service.summary_methods.get_summaries_for_entity', side_effect=Exception("Database error")):
            result = mock_context_service._load_hierarchical_summaries(EntityType.WORK_ITEM, 1)
            
            # Should return empty lists on exception
            assert isinstance(result, dict)
            assert result['project_summaries'] == []
            assert result['session_summaries'] == []
            assert result['work_item_summaries'] == []
            assert result['task_summaries'] == []
            assert result['recent_summaries'] == []
            assert result['summary_timeline'] == []
    
    def test_context_payload_with_summaries(self, sample_summaries):
        """Test ContextPayload with summary fields."""
        project = Project(id=1, name="Test Project")
        
        payload = ContextPayload(
            entity=project,
            entity_type=EntityType.PROJECT,
            summaries=sample_summaries,
            project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            session_summaries=[],
            work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
            recent_summaries=sample_summaries,
            summary_timeline=sample_summaries
        )
        
        assert len(payload.summaries) == 3
        assert len(payload.project_summaries) == 1
        assert len(payload.work_item_summaries) == 1
        assert len(payload.task_summaries) == 1
        assert len(payload.recent_summaries) == 3
        assert len(payload.summary_timeline) == 3
    
    def test_context_payload_to_dict_with_summaries(self, sample_summaries):
        """Test ContextPayload.to_dict() with summary fields."""
        project = Project(id=1, name="Test Project")
        
        payload = ContextPayload(
            entity=project,
            entity_type=EntityType.PROJECT,
            summaries=sample_summaries,
            project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            session_summaries=[],
            work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
            recent_summaries=sample_summaries,
            summary_timeline=sample_summaries
        )
        
        data = payload.to_dict()
        
        assert 'summaries' in data
        assert 'project_summaries' in data
        assert 'session_summaries' in data
        assert 'work_item_summaries' in data
        assert 'task_summaries' in data
        assert 'recent_summaries' in data
        assert 'summary_timeline' in data
        
        # Check that summaries are serialized correctly
        assert len(data['summaries']) == 3
        assert len(data['project_summaries']) == 1
        assert len(data['work_item_summaries']) == 1
        assert len(data['task_summaries']) == 1
        assert len(data['recent_summaries']) == 3
        assert len(data['summary_timeline']) == 3
        
        # Check that summary data is properly serialized
        assert data['summaries'][0]['id'] == 1
        assert data['summaries'][0]['entity_type'] == 'project'
        assert data['summaries'][0]['summary_type'] == 'project_milestone'
        assert data['summaries'][0]['summary_text'] == "Project milestone achieved successfully."
    
    def test_get_task_context_with_summaries(self, mock_context_service, sample_summaries):
        """Test get_task_context with summary integration."""
        task = Task(id=1, name="Test Task")
        
        with patch.object(mock_context_service, '_load_hierarchical_summaries', return_value={
            'project_summaries': [s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            'session_summaries': [],
            'work_item_summaries': [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            'task_summaries': [s for s in sample_summaries if s.entity_type == EntityType.TASK],
            'recent_summaries': sample_summaries,
            'summary_timeline': sample_summaries
        }):
            with patch.object(mock_context_service, '_get_task_context', return_value=ContextPayload(
                entity=task,
                entity_type=EntityType.TASK,
                summaries=sample_summaries,
                project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
                session_summaries=[],
                work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
                task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
                recent_summaries=sample_summaries,
                summary_timeline=sample_summaries
            )):
                result = mock_context_service.get_task_context(1)
                
                assert result is not None
                assert len(result.summaries) == 3
                assert len(result.project_summaries) == 1
                assert len(result.work_item_summaries) == 1
                assert len(result.task_summaries) == 1
                assert len(result.recent_summaries) == 3
                assert len(result.summary_timeline) == 3
    
    def test_get_work_item_context_with_summaries(self, mock_context_service, sample_summaries):
        """Test get_work_item_context with summary integration."""
        work_item = WorkItem(id=1, name="Test Work Item")
        
        with patch.object(mock_context_service, '_load_hierarchical_summaries', return_value={
            'project_summaries': [s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            'session_summaries': [],
            'work_item_summaries': [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            'task_summaries': [s for s in sample_summaries if s.entity_type == EntityType.TASK],
            'recent_summaries': sample_summaries,
            'summary_timeline': sample_summaries
        }):
            with patch.object(mock_context_service, '_get_work_item_context', return_value=ContextPayload(
                entity=work_item,
                entity_type=EntityType.WORK_ITEM,
                summaries=sample_summaries,
                project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
                session_summaries=[],
                work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
                task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
                recent_summaries=sample_summaries,
                summary_timeline=sample_summaries
            )):
                result = mock_context_service.get_work_item_context(1)
                
                assert result is not None
                assert len(result.summaries) == 3
                assert len(result.project_summaries) == 1
                assert len(result.work_item_summaries) == 1
                assert len(result.task_summaries) == 1
                assert len(result.recent_summaries) == 3
                assert len(result.summary_timeline) == 3
    
    def test_get_project_context_with_summaries(self, mock_context_service, sample_summaries):
        """Test get_project_context with summary integration."""
        project = Project(id=1, name="Test Project")
        
        with patch.object(mock_context_service, '_load_hierarchical_summaries', return_value={
            'project_summaries': [s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            'session_summaries': [],
            'work_item_summaries': [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            'task_summaries': [s for s in sample_summaries if s.entity_type == EntityType.TASK],
            'recent_summaries': sample_summaries,
            'summary_timeline': sample_summaries
        }):
            with patch.object(mock_context_service, '_get_project_context', return_value=ContextPayload(
                entity=project,
                entity_type=EntityType.PROJECT,
                summaries=sample_summaries,
                project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
                session_summaries=[],
                work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
                task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
                recent_summaries=sample_summaries,
                summary_timeline=sample_summaries
            )):
                result = mock_context_service.get_project_context(1)
                
                assert result is not None
                assert len(result.summaries) == 3
                assert len(result.project_summaries) == 1
                assert len(result.work_item_summaries) == 1
                assert len(result.task_summaries) == 1
                assert len(result.recent_summaries) == 3
                assert len(result.summary_timeline) == 3
    
    def test_get_idea_context_with_summaries(self, mock_context_service, sample_summaries):
        """Test get_idea_context with summary integration."""
        idea = Idea(id=1, title="Test Idea")
        
        with patch.object(mock_context_service, '_load_hierarchical_summaries', return_value={
            'project_summaries': [s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
            'session_summaries': [],
            'work_item_summaries': [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
            'task_summaries': [s for s in sample_summaries if s.entity_type == EntityType.TASK],
            'recent_summaries': sample_summaries,
            'summary_timeline': sample_summaries
        }):
            with patch.object(mock_context_service, '_get_idea_context', return_value=ContextPayload(
                entity=idea,
                entity_type=EntityType.IDEA,
                summaries=sample_summaries,
                project_summaries=[s for s in sample_summaries if s.entity_type == EntityType.PROJECT],
                session_summaries=[],
                work_item_summaries=[s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM],
                task_summaries=[s for s in sample_summaries if s.entity_type == EntityType.TASK],
                recent_summaries=sample_summaries,
                summary_timeline=sample_summaries
            )):
                result = mock_context_service.get_idea_context(1)
                
                assert result is not None
                assert len(result.summaries) == 3
                assert len(result.project_summaries) == 1
                assert len(result.work_item_summaries) == 1
                assert len(result.task_summaries) == 1
                assert len(result.recent_summaries) == 3
                assert len(result.summary_timeline) == 3
