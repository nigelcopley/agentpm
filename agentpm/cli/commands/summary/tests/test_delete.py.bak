import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch

from agentpm.cli.commands.summary.delete import delete_summary


class TestDeleteSummaryCommand:
    """Test the delete summary CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    def test_delete_summary_success(self, runner, mock_db_service):
        """Test successful summary deletion."""
        with patch('agentpm.cli.commands.summary.delete.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.delete_summary', return_value=True):
                result = runner.invoke(delete_summary, ['1'])
                
                assert result.exit_code == 0
                assert "✓ Summary 1 deleted successfully" in result.output
    
    def test_delete_summary_not_found(self, runner, mock_db_service):
        """Test deletion when summary doesn't exist."""
        with patch('agentpm.cli.commands.summary.delete.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.delete_summary', return_value=False):
                result = runner.invoke(delete_summary, ['999'])
                
                assert result.exit_code != 0
                assert "✗ Summary with ID 999 not found" in result.output
    
    def test_delete_summary_invalid_id(self, runner, mock_db_service):
        """Test deletion with invalid ID."""
        result = runner.invoke(delete_summary, ['0'])
        
        assert result.exit_code != 0
        assert "Summary ID must be greater than 0" in result.output
    
    def test_delete_summary_non_numeric_id(self, runner, mock_db_service):
        """Test deletion with non-numeric ID."""
        result = runner.invoke(delete_summary, ['abc'])
        
        assert result.exit_code != 0
        assert "Summary ID must be a number" in result.output
    
    def test_delete_summary_database_error(self, runner, mock_db_service):
        """Test deletion with database error."""
        with patch('agentpm.cli.commands.summary.delete.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.delete_summary') as mock_delete:
                mock_delete.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(delete_summary, ['1'])
                
                assert result.exit_code != 0
                assert "✗ Error deleting summary" in result.output
                assert "Database connection failed" in result.output
    
    def test_delete_summary_force_flag(self, runner, mock_db_service):
        """Test deletion with force flag."""
        with patch('agentpm.cli.commands.summary.delete.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.delete_summary', return_value=True):
                result = runner.invoke(delete_summary, ['1', '--force'])
                
                assert result.exit_code == 0
                assert "✓ Summary 1 deleted successfully" in result.output
    
    def test_delete_summary_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(delete_summary, ['--help'])
        
        assert result.exit_code == 0
        assert "Delete a summary" in result.output
        assert "SUMMARY_ID" in result.output
        assert "--force" in result.output
