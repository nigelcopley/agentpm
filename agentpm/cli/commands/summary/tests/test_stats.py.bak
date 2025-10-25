import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch

from agentpm.cli.commands.summary.stats import summary_stats


class TestSummaryStatsCommand:
    """Test the summary stats CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    def test_summary_stats_success(self, runner, mock_db_service):
        """Test successful summary statistics display."""
        # Mock the database query results
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.execute.return_value = mock_cursor
        
        # Mock total count
        mock_cursor.fetchone.return_value = (25,)
        
        # Mock entity type breakdown
        mock_cursor.fetchall.return_value = [
            ('work_item', 15),
            ('project', 5),
            ('task', 3),
            ('idea', 2)
        ]
        
        mock_db_service.get_connection.return_value = mock_connection
        
        with patch('agentpm.cli.commands.summary.stats.get_db_service', return_value=mock_db_service):
            result = runner.invoke(summary_stats, [])
            
            assert result.exit_code == 0
            assert "Summary Statistics" in result.output
            assert "Total summaries: 25" in result.output
            assert "Entity Type Breakdown:" in result.output
            assert "work_item: 15" in result.output
            assert "project: 5" in result.output
            assert "task: 3" in result.output
            assert "idea: 2" in result.output
    
    def test_summary_stats_empty_database(self, runner, mock_db_service):
        """Test statistics when no summaries exist."""
        # Mock the database query results
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.execute.return_value = mock_cursor
        
        # Mock total count
        mock_cursor.fetchone.return_value = (0,)
        
        # Mock entity type breakdown
        mock_cursor.fetchall.return_value = []
        
        mock_db_service.get_connection.return_value = mock_connection
        
        with patch('agentpm.cli.commands.summary.stats.get_db_service', return_value=mock_db_service):
            result = runner.invoke(summary_stats, [])
            
            assert result.exit_code == 0
            assert "Summary Statistics" in result.output
            assert "Total summaries: 0" in result.output
            assert "Entity Type Breakdown:" in result.output
            assert "No summaries found" in result.output
    
    def test_summary_stats_database_error(self, runner, mock_db_service):
        """Test statistics with database error."""
        with patch('agentpm.cli.commands.summary.stats.get_db_service', return_value=mock_db_service):
            with patch('agentpm.cli.commands.summary.stats.get_db_service') as mock_get_db:
                mock_get_db.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(summary_stats, [])
                
                assert result.exit_code != 0
                assert "✗ Error retrieving summary statistics" in result.output
                assert "Database connection failed" in result.output
    
    def test_summary_stats_verbose_output(self, runner, mock_db_service):
        """Test statistics with verbose output."""
        # Mock the database query results
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.execute.return_value = mock_cursor
        
        # Mock total count
        mock_cursor.fetchone.return_value = (25,)
        
        # Mock entity type breakdown
        mock_cursor.fetchall.return_value = [
            ('work_item', 15),
            ('project', 5),
            ('task', 3),
            ('idea', 2)
        ]
        
        mock_db_service.get_connection.return_value = mock_connection
        
        with patch('agentpm.cli.commands.summary.stats.get_db_service', return_value=mock_db_service):
            result = runner.invoke(summary_stats, ['--verbose'])
            
            assert result.exit_code == 0
            assert "Summary Statistics" in result.output
            assert "Total summaries: 25" in result.output
            assert "Entity Type Breakdown:" in result.output
            assert "work_item: 15" in result.output
            assert "project: 5" in result.output
            assert "task: 3" in result.output
            assert "idea: 2" in result.output
    
    def test_summary_stats_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(summary_stats, ['--help'])
        
        assert result.exit_code == 0
        assert "Display summary statistics" in result.output
        assert "--verbose" in result.output
