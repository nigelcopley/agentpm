import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.cli.commands.summary.search import search_summaries
from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType


class TestSearchSummariesCommand:
    """Test the search summaries CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    @pytest.fixture
    def sample_search_results(self):
        """Create sample search results for testing."""
        return [
            Summary(
                id=1,
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text="Made significant progress on the React implementation. Used hooks for state management.",
                context_metadata={"decisions": ["Use React hooks"]},
                session_id="session-123",
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                created_by="agent-1"
            ),
            Summary(
                id=2,
                entity_type=EntityType.TASK,
                entity_id=1,
                summary_type=SummaryType.TASK_COMPLETION,
                summary_text="Completed the React component implementation with TypeScript support.",
                context_metadata={"metrics": {"completion": 100.0}},
                session_id="session-456",
                created_at=datetime(2024, 1, 15, 11, 30, 0),
                created_by="agent-2"
            ),
            Summary(
                id=3,
                entity_type=EntityType.PROJECT,
                entity_id=1,
                summary_type=SummaryType.PROJECT_MILESTONE,
                summary_text="Project milestone achieved. React frontend is now complete and ready for testing.",
                context_metadata=None,
                session_id=None,
                created_at=datetime(2024, 1, 15, 12, 30, 0),
                created_by="agent-1"
            )
        ]
    
    def test_search_summaries_success(self, runner, mock_db_service, sample_search_results):
        """Test successful summary search."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=sample_search_results):
                result = runner.invoke(search_summaries, ['React'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries matching 'React'" in result.output
                assert "ID: 1" in result.output
                assert "ID: 2" in result.output
                assert "ID: 3" in result.output
                assert "React implementation" in result.output
                assert "React component" in result.output
                assert "React frontend" in result.output
    
    def test_search_summaries_empty_results(self, runner, mock_db_service):
        """Test search when no summaries match the query."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=[]):
                result = runner.invoke(search_summaries, ['nonexistent'])
                
                assert result.exit_code == 0
                assert "No summaries found matching 'nonexistent'" in result.output
    
    def test_search_summaries_with_limit(self, runner, mock_db_service, sample_search_results):
        """Test search with a limit on results."""
        limited_results = sample_search_results[:2]
        
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=limited_results):
                result = runner.invoke(search_summaries, ['React', '--limit', '2'])
                
                assert result.exit_code == 0
                assert "Found 2 summaries matching 'React'" in result.output
                assert "ID: 1" in result.output
                assert "ID: 2" in result.output
                assert "ID: 3" not in result.output
    
    def test_search_summaries_with_entity_type_filter(self, runner, mock_db_service, sample_search_results):
        """Test search with entity type filter."""
        work_item_results = [s for s in sample_search_results if s.entity_type == EntityType.WORK_ITEM]
        
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=work_item_results):
                result = runner.invoke(search_summaries, ['React', '--entity-type', 'work_item'])
                
                assert result.exit_code == 0
                assert "Found 1 summaries matching 'React'" in result.output
                assert "work_item (1)" in result.output
                assert "task (1)" not in result.output
                assert "project (1)" not in result.output
    
    def test_search_summaries_with_summary_type_filter(self, runner, mock_db_service, sample_search_results):
        """Test search with summary type filter."""
        progress_results = [s for s in sample_search_results if s.summary_type == SummaryType.WORK_ITEM_PROGRESS]
        
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=progress_results):
                result = runner.invoke(search_summaries, ['React', '--summary-type', 'work_item_progress'])
                
                assert result.exit_code == 0
                assert "Found 1 summaries matching 'React'" in result.output
                assert "work_item_progress" in result.output
                assert "task_completion" not in result.output
                assert "project_milestone" not in result.output
    
    def test_search_summaries_with_multiple_filters(self, runner, mock_db_service, sample_search_results):
        """Test search with multiple filters."""
        filtered_results = [s for s in sample_search_results if s.entity_type == EntityType.WORK_ITEM and s.summary_type == SummaryType.WORK_ITEM_PROGRESS]
        
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=filtered_results):
                result = runner.invoke(search_summaries, [
                    'React',
                    '--entity-type', 'work_item',
                    '--summary-type', 'work_item_progress',
                    '--limit', '5'
                ])
                
                assert result.exit_code == 0
                assert "Found 1 summaries matching 'React'" in result.output
                assert "work_item (1)" in result.output
                assert "work_item_progress" in result.output
    
    def test_search_summaries_case_insensitive(self, runner, mock_db_service, sample_search_results):
        """Test that search is case insensitive."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=sample_search_results):
                result = runner.invoke(search_summaries, ['react'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries matching 'react'" in result.output
    
    def test_search_summaries_multiple_keywords(self, runner, mock_db_service, sample_search_results):
        """Test search with multiple keywords."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=sample_search_results):
                result = runner.invoke(search_summaries, ['React TypeScript'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries matching 'React TypeScript'" in result.output
    
    def test_search_summaries_empty_query(self, runner, mock_db_service):
        """Test search with empty query."""
        result = runner.invoke(search_summaries, [''])
        
        assert result.exit_code != 0
        assert "Query cannot be empty" in result.output
    
    def test_search_summaries_whitespace_only_query(self, runner, mock_db_service):
        """Test search with whitespace-only query."""
        result = runner.invoke(search_summaries, ['   '])
        
        assert result.exit_code != 0
        assert "Query cannot be empty" in result.output
    
    def test_search_summaries_invalid_entity_type(self, runner, mock_db_service):
        """Test search with invalid entity type."""
        result = runner.invoke(search_summaries, ['React', '--entity-type', 'invalid_type'])
        
        assert result.exit_code != 0
        assert "Invalid entity type" in result.output
    
    def test_search_summaries_invalid_summary_type(self, runner, mock_db_service):
        """Test search with invalid summary type."""
        result = runner.invoke(search_summaries, ['React', '--summary-type', 'invalid_type'])
        
        assert result.exit_code != 0
        assert "Invalid summary type" in result.output
    
    def test_search_summaries_invalid_limit(self, runner, mock_db_service):
        """Test search with invalid limit."""
        result = runner.invoke(search_summaries, ['React', '--limit', '0'])
        
        assert result.exit_code != 0
        assert "Limit must be greater than 0" in result.output
    
    def test_search_summaries_database_error(self, runner, mock_db_service):
        """Test search with database error."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries') as mock_search:
                mock_search.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(search_summaries, ['React'])
                
                assert result.exit_code != 0
                assert "✗ Error searching summaries" in result.output
                assert "Database connection failed" in result.output
    
    def test_search_summaries_verbose_output(self, runner, mock_db_service, sample_search_results):
        """Test search with verbose output."""
        with patch('agentpm.cli.commands.summary.search.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.search_summaries', return_value=sample_search_results):
                result = runner.invoke(search_summaries, ['React', '--verbose'])
                
                assert result.exit_code == 0
                assert "Found 3 summaries matching 'React'" in result.output
                # Verbose output should show more details
                assert "Created by: agent-1" in result.output
                assert "Created by: agent-2" in result.output
                assert "Session: session-123" in result.output
                assert "Session: session-456" in result.output
    
    def test_search_summaries_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(search_summaries, ['--help'])
        
        assert result.exit_code == 0
        assert "Search summaries by keywords" in result.output
        assert "QUERY" in result.output
        assert "--entity-type" in result.output
        assert "--summary-type" in result.output
        assert "--limit" in result.output
        assert "--verbose" in result.output
