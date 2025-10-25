import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.cli.commands.summary.list import list_summaries
from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType


class TestListSummariesCommand:
    """Test the list summaries CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    @pytest.fixture
    def sample_summaries(self):
        """Create sample summaries for testing."""
        return [
            Summary(
                id=1,
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text="First summary about work item progress.",
                context_metadata={"decisions": ["Use React"]},
                session_id="session-123",
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                created_by="agent-1"
            ),
            Summary(
                id=2,
                entity_type=EntityType.PROJECT,
                entity_id=1,
                summary_type=SummaryType.PROJECT_MILESTONE,
                summary_text="Project milestone achieved successfully.",
                context_metadata=None,
                session_id=None,
                created_at=datetime(2024, 1, 15, 11, 30, 0),
                created_by="agent-2"
            ),
            Summary(
                id=3,
                entity_type=EntityType.TASK,
                entity_id=1,
                summary_type=SummaryType.TASK_COMPLETION,
                summary_text="Task completed with all requirements met.",
                context_metadata={"metrics": {"completion": 100.0}},
                session_id="session-456",
                created_at=datetime(2024, 1, 15, 12, 30, 0),
                created_by="agent-1"
            )
        ]
    
    def test_list_summaries_success(self, runner, mock_db_service, sample_summaries):
        """Test successful summary listing."""
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=sample_summaries):
                result = runner.invoke(list_summaries, [])
                
                assert result.exit_code == 0
                assert "Found 3 summaries" in result.output
                assert "ID: 1" in result.output
                assert "ID: 2" in result.output
                assert "ID: 3" in result.output
                assert "work_item (1)" in result.output
                assert "project (1)" in result.output
                assert "task (1)" in result.output
    
    def test_list_summaries_empty(self, runner, mock_db_service):
        """Test listing summaries when none exist."""
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=[]):
                result = runner.invoke(list_summaries, [])
                
                assert result.exit_code == 0
                assert "No summaries found" in result.output
    
    def test_list_summaries_with_entity_type_filter(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries filtered by entity type."""
        work_item_summaries = [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM]
        
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=work_item_summaries):
                result = runner.invoke(list_summaries, ['--entity-type', 'work_item'])
                
                assert result.exit_code == 0
                assert "Found 1 summaries" in result.output
                assert "work_item (1)" in result.output
                assert "project (1)" not in result.output
                assert "task (1)" not in result.output
    
    def test_list_summaries_with_entity_id_filter(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries filtered by entity ID."""
        entity_1_summaries = [s for s in sample_summaries if s.entity_id == 1]
        
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=entity_1_summaries):
                result = runner.invoke(list_summaries, ['--entity-id', '1'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries" in result.output
                assert "ID: 1" in result.output
                assert "ID: 2" in result.output
                assert "ID: 3" in result.output
    
    def test_list_summaries_with_summary_type_filter(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries filtered by summary type."""
        progress_summaries = [s for s in sample_summaries if s.summary_type == SummaryType.WORK_ITEM_PROGRESS]
        
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=progress_summaries):
                result = runner.invoke(list_summaries, ['--summary-type', 'work_item_progress'])
                
                assert result.exit_code == 0
                assert "Found 1 summaries" in result.output
                assert "work_item_progress" in result.output
                assert "project_milestone" not in result.output
                assert "task_completion" not in result.output
    
    def test_list_summaries_with_limit(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries with a limit."""
        limited_summaries = sample_summaries[:2]
        
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=limited_summaries):
                result = runner.invoke(list_summaries, ['--limit', '2'])
                
                assert result.exit_code == 0
                assert "Found 2 summaries" in result.output
                assert "ID: 1" in result.output
                assert "ID: 2" in result.output
                assert "ID: 3" not in result.output
    
    def test_list_summaries_with_multiple_filters(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries with multiple filters."""
        filtered_summaries = [s for s in sample_summaries if s.entity_type == EntityType.WORK_ITEM and s.entity_id == 1]
        
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=filtered_summaries):
                result = runner.invoke(list_summaries, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--limit', '5'
                ])
                
                assert result.exit_code == 0
                assert "Found 1 summaries" in result.output
                assert "work_item (1)" in result.output
    
    def test_list_summaries_invalid_entity_type(self, runner, mock_db_service):
        """Test listing summaries with invalid entity type."""
        result = runner.invoke(list_summaries, ['--entity-type', 'invalid_type'])
        
        assert result.exit_code != 0
        assert "Invalid entity type" in result.output
    
    def test_list_summaries_invalid_entity_id(self, runner, mock_db_service):
        """Test listing summaries with invalid entity ID."""
        result = runner.invoke(list_summaries, ['--entity-id', '0'])
        
        assert result.exit_code != 0
        assert "Entity ID must be greater than 0" in result.output
    
    def test_list_summaries_invalid_summary_type(self, runner, mock_db_service):
        """Test listing summaries with invalid summary type."""
        result = runner.invoke(list_summaries, ['--summary-type', 'invalid_type'])
        
        assert result.exit_code != 0
        assert "Invalid summary type" in result.output
    
    def test_list_summaries_invalid_limit(self, runner, mock_db_service):
        """Test listing summaries with invalid limit."""
        result = runner.invoke(list_summaries, ['--limit', '0'])
        
        assert result.exit_code != 0
        assert "Limit must be greater than 0" in result.output
    
    def test_list_summaries_database_error(self, runner, mock_db_service):
        """Test listing summaries with database error."""
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries') as mock_list:
                mock_list.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(list_summaries, [])
                
                assert result.exit_code != 0
                assert "✗ Error listing summaries" in result.output
                assert "Database connection failed" in result.output
    
    def test_list_summaries_verbose_output(self, runner, mock_db_service, sample_summaries):
        """Test listing summaries with verbose output."""
        with patch('agentpm.cli.commands.summary.list.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.list_summaries', return_value=sample_summaries):
                result = runner.invoke(list_summaries, ['--verbose'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries" in result.output
                # Verbose output should show more details
                assert "Created by: agent-1" in result.output
                assert "Created by: agent-2" in result.output
                assert "Session: session-123" in result.output
                assert "Session: session-456" in result.output
    
    def test_list_summaries_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(list_summaries, ['--help'])
        
        assert result.exit_code == 0
        assert "List summaries" in result.output
        assert "--entity-type" in result.output
        assert "--entity-id" in result.output
        assert "--summary-type" in result.output
        assert "--limit" in result.output
        assert "--verbose" in result.output
