import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from agentpm.core.database.service import DatabaseService, ValidationError
from agentpm.core.database.models import Summary, Project, WorkItem, Task, Idea
from agentpm.core.database.enums import EntityType, SummaryType
from agentpm.core.database.methods import summaries


class TestSummariesMethods:
    """Test the summaries database methods."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock DatabaseService."""
        service = Mock(spec=DatabaseService)
        service.transaction.return_value.__enter__ = Mock()
        service.transaction.return_value.__exit__ = Mock(return_value=None)
        return service
    
    @pytest.fixture
    def sample_summary(self):
        """Create a sample summary for testing."""
        return Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary for database operations.",
            context_metadata={"decisions": ["Use React"]},
            session_id=123,
            created_by="agent-1"
        )
    
    def test_create_summary_success(self, mock_service, sample_summary):
        """Test successful summary creation."""
        # Mock the entity validation
        with patch('agentpm.core.database.methods.summaries._check_entity_exists', return_value=True):
            # Mock the database cursor
            mock_cursor = Mock()
            mock_cursor.lastrowid = 1
            mock_service.transaction.return_value.__enter__.return_value.execute.return_value = mock_cursor
            
            # Mock get_summary to return the created summary
            expected_summary = sample_summary.model_copy()
            expected_summary.id = 1
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=expected_summary):
                result = summaries.create_summary(mock_service, sample_summary)
                
                assert result.id == 1
                assert result.entity_type == sample_summary.entity_type
                assert result.entity_id == sample_summary.entity_id
                assert result.summary_type == sample_summary.summary_type
                assert result.summary_text == sample_summary.summary_text
    
    def test_create_summary_entity_validation_failure(self, mock_service, sample_summary):
        """Test summary creation with invalid entity."""
        # Mock entity validation to return False (entity doesn't exist)
        with patch('agentpm.core.database.methods.summaries._check_entity_exists', return_value=False):
            with pytest.raises(ValidationError) as exc_info:
                summaries.create_summary(mock_service, sample_summary)
            
            assert "work_item 1 does not exist" in str(exc_info.value)
    
    def test_get_summary_success(self, mock_service):
        """Test successful summary retrieval."""
        # Mock database row
        mock_row = {
            "id": 1,
            "entity_type": "work_item",
            "entity_id": 1,
            "summary_type": "work_item_progress",
            "summary_text": "Test summary from database.",
            "context_metadata": None,
            "session_id": 123,
            "created_at": "2024-01-15T10:30:00",
            "created_by": "agent-1"
        }
        
        mock_service.get_connection.return_value.execute.return_value.fetchone.return_value = mock_row
        
        result = summaries.get_summary(mock_service, 1)
        
        assert result is not None
        assert result.id == 1
        assert result.entity_type == EntityType.WORK_ITEM
        assert result.entity_id == 1
        assert result.summary_type == SummaryType.WORK_ITEM_PROGRESS
    
    def test_get_summary_not_found(self, mock_service):
        """Test summary retrieval when summary doesn't exist."""
        mock_service.get_connection.return_value.execute.return_value.fetchone.return_value = None
        
        result = summaries.get_summary(mock_service, 999)
        
        assert result is None
    
    def test_list_summaries_success(self, mock_service):
        """Test successful summary listing."""
        # Mock database rows
        mock_rows = [
            {
                "id": 1,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_progress",
                "summary_text": "First summary.",
                "context_metadata": None,
                "session_id": "session-123",
                "created_at": "2024-01-15T10:30:00",
                "created_by": "agent-1"
            },
            {
                "id": 2,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_milestone",
                "summary_text": "Second summary.",
                "context_metadata": '{"decisions": ["Use React"]}',
                "session_id": "session-456",
                "created_at": "2024-01-15T11:30:00",
                "created_by": "agent-2"
            }
        ]
        
        mock_service.get_connection.return_value.execute.return_value.fetchall.return_value = mock_rows
        
        result = summaries.list_summaries(mock_service, limit=10)
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].summary_type == SummaryType.WORK_ITEM_PROGRESS
        assert result[1].id == 2
        assert result[1].summary_type == SummaryType.WORK_ITEM_MILESTONE
        assert result[1].context_metadata == {"decisions": ["Use React"]}
    
    def test_list_summaries_with_filters(self, mock_service):
        """Test summary listing with entity type and ID filters."""
        mock_rows = [
            {
                "id": 1,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_progress",
                "summary_text": "Filtered summary.",
                "context_metadata": None,
                "session_id": "session-123",
                "created_at": "2024-01-15T10:30:00",
                "created_by": "agent-1"
            }
        ]
        
        mock_service.get_connection.return_value.execute.return_value.fetchall.return_value = mock_rows
        
        result = summaries.list_summaries(
            mock_service,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            limit=10
        )
        
        assert len(result) == 1
        assert result[0].entity_type == EntityType.WORK_ITEM
        assert result[0].entity_id == 1
    
    def test_update_summary_success(self, mock_service, sample_summary):
        """Test successful summary update."""
        # Mock the entity validation
        with patch('agentpm.core.database.methods.summaries._validate_entity_exists'):
            # Mock the database cursor
            mock_cursor = Mock()
            mock_cursor.rowcount = 1
            mock_service.transaction.return_value.__enter__.return_value.execute.return_value = mock_cursor
            
            sample_summary.id = 1
            sample_summary.summary_text = "Updated summary text."
            
            result = summaries.update_summary(mock_service, sample_summary)
            
            assert result.summary_text == "Updated summary text."
    
    def test_update_summary_not_found(self, mock_service, sample_summary):
        """Test summary update when summary doesn't exist."""
        # Mock the entity validation
        with patch('agentpm.core.database.methods.summaries._validate_entity_exists'):
            # Mock the database cursor to return 0 rows affected
            mock_cursor = Mock()
            mock_cursor.rowcount = 0
            mock_service.transaction.return_value.__enter__.return_value.execute.return_value = mock_cursor
            
            sample_summary.id = 999
            
            with pytest.raises(ValidationError) as exc_info:
                summaries.update_summary(mock_service, sample_summary)
            
            assert "Summary with ID 999 not found" in str(exc_info.value)
    
    def test_delete_summary_success(self, mock_service):
        """Test successful summary deletion."""
        # Mock the database cursor
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_service.transaction.return_value.__enter__.return_value.execute.return_value = mock_cursor
        
        result = summaries.delete_summary(mock_service, 1)
        
        assert result is True
    
    def test_delete_summary_not_found(self, mock_service):
        """Test summary deletion when summary doesn't exist."""
        # Mock the database cursor to return 0 rows affected
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        mock_service.transaction.return_value.__enter__.return_value.execute.return_value = mock_cursor
        
        result = summaries.delete_summary(mock_service, 999)
        
        assert result is False
    
    def test_get_summaries_for_entity_success(self, mock_service):
        """Test getting summaries for a specific entity."""
        mock_rows = [
            {
                "id": 1,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_progress",
                "summary_text": "Entity summary.",
                "context_metadata": None,
                "session_id": "session-123",
                "created_at": "2024-01-15T10:30:00",
                "created_by": "agent-1"
            }
        ]
        
        mock_service.get_connection.return_value.execute.return_value.fetchall.return_value = mock_rows
        
        result = summaries.get_summaries_for_entity(
            mock_service,
            EntityType.WORK_ITEM,
            1,
            limit=10
        )
        
        assert len(result) == 1
        assert result[0].entity_type == EntityType.WORK_ITEM
        assert result[0].entity_id == 1
    
    def test_get_recent_summaries_success(self, mock_service):
        """Test getting recent summaries across all entities."""
        mock_rows = [
            {
                "id": 1,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_progress",
                "summary_text": "Recent summary.",
                "context_metadata": None,
                "session_id": "session-123",
                "created_at": "2024-01-15T10:30:00",
                "created_by": "agent-1"
            }
        ]
        
        mock_service.get_connection.return_value.execute.return_value.fetchall.return_value = mock_rows
        
        result = summaries.get_recent_summaries(mock_service, limit=10)
        
        assert len(result) == 1
        assert result[0].summary_text == "Recent summary."
    
    def test_search_summaries_success(self, mock_service):
        """Test searching summaries by keywords."""
        mock_rows = [
            {
                "id": 1,
                "entity_type": "work_item",
                "entity_id": 1,
                "summary_type": "work_item_progress",
                "summary_text": "Summary about React implementation.",
                "context_metadata": None,
                "session_id": "session-123",
                "created_at": "2024-01-15T10:30:00",
                "created_by": "agent-1"
            }
        ]
        
        mock_service.get_connection.return_value.execute.return_value.fetchall.return_value = mock_rows
        
        result = summaries.search_summaries(mock_service, "React", limit=10)
        
        assert len(result) == 1
        assert "React" in result[0].summary_text
    
    def test_validate_entity_exists_project(self, mock_service):
        """Test entity validation for project."""
        with patch('agentpm.core.database.methods.projects.get_project') as mock_get:
            mock_get.return_value = Project(id=1, name="Test Project")
            
            # Should return True
            from agentpm.core.database.methods.summaries import _check_entity_exists
            result = _check_entity_exists(mock_service, EntityType.PROJECT, 1)
            assert result is True
    
    def test_validate_entity_exists_work_item(self, mock_service):
        """Test entity validation for work item."""
        with patch('agentpm.core.database.methods.work_items.get_work_item') as mock_get:
            mock_get.return_value = WorkItem(id=1, name="Test Work Item")
            
            # Should return True
            from agentpm.core.database.methods.summaries import _check_entity_exists
            result = _check_entity_exists(mock_service, EntityType.WORK_ITEM, 1)
            assert result is True
    
    def test_validate_entity_exists_task(self, mock_service):
        """Test entity validation for task."""
        with patch('agentpm.core.database.methods.tasks.get_task') as mock_get:
            mock_get.return_value = Task(id=1, name="Test Task")
            
            # Should return True
            from agentpm.core.database.methods.summaries import _check_entity_exists
            result = _check_entity_exists(mock_service, EntityType.TASK, 1)
            assert result is True
    
    def test_validate_entity_exists_idea(self, mock_service):
        """Test entity validation for idea."""
        with patch('agentpm.core.database.methods.ideas.get_idea') as mock_get:
            mock_get.return_value = Idea(id=1, title="Test Idea")
            
            # Should return True
            from agentpm.core.database.methods.summaries import _check_entity_exists
            result = _check_entity_exists(mock_service, EntityType.IDEA, 1)
            assert result is True
    
    def test_validate_entity_exists_not_found(self, mock_service):
        """Test entity validation when entity doesn't exist."""
        with patch('agentpm.core.database.methods.work_items.get_work_item') as mock_get:
            mock_get.return_value = None
            
            # Should return False
            from agentpm.core.database.methods.summaries import _check_entity_exists
            result = _check_entity_exists(mock_service, EntityType.WORK_ITEM, 999)
            assert result is False
    
    def test_validate_entity_exists_unsupported_type(self, mock_service):
        """Test entity validation with unsupported entity type."""
        # Should return False for unsupported entity type
        from agentpm.core.database.methods.summaries import _check_entity_exists
        result = _check_entity_exists(mock_service, "unsupported", 1)
        assert result is False
