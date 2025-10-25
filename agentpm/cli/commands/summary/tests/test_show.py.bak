import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.cli.commands.summary.show import show_summary
from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType


class TestShowSummaryCommand:
    """Test the show summary CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    @pytest.fixture
    def sample_summary(self):
        """Create a sample summary for testing."""
        return Summary(
            id=1,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="This is a detailed summary of the work item progress. It includes information about the decisions made, blockers encountered, and the current status of the implementation.",
            context_metadata={
                "decisions": [
                    {"decision": "Use React hooks", "rationale": "Better state management"},
                    {"decision": "Use TypeScript", "rationale": "Type safety"}
                ],
                "blockers": [
                    {"blocker": "API not ready", "resolution": "Mock data for now"}
                ],
                "metrics": {
                    "completion_percentage": 75.5,
                    "estimated_hours": 8.0
                }
            },
            session_id="session-123",
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            created_by="agent-1"
        )
    
    def test_show_summary_success(self, runner, mock_db_service, sample_summary):
        """Test successful summary display."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=sample_summary):
                result = runner.invoke(show_summary, ['1'])
                
                assert result.exit_code == 0
                assert "Summary #1" in result.output
                assert "Entity: work_item (1)" in result.output
                assert "Type: work_item_progress" in result.output
                assert "Created: 2024-01-15 10:30:00" in result.output
                assert "Created by: agent-1" in result.output
                assert "Session: session-123" in result.output
                assert "This is a detailed summary" in result.output
    
    def test_show_summary_with_metadata(self, runner, mock_db_service, sample_summary):
        """Test summary display with context metadata."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=sample_summary):
                result = runner.invoke(show_summary, ['1'])
                
                assert result.exit_code == 0
                assert "Context Metadata:" in result.output
                assert "Decisions:" in result.output
                assert "Use React hooks" in result.output
                assert "Better state management" in result.output
                assert "Use TypeScript" in result.output
                assert "Type safety" in result.output
                assert "Blockers:" in result.output
                assert "API not ready" in result.output
                assert "Mock data for now" in result.output
                assert "Metrics:" in result.output
                assert "completion_percentage: 75.5" in result.output
                assert "estimated_hours: 8.0" in result.output
    
    def test_show_summary_without_metadata(self, runner, mock_db_service):
        """Test summary display without context metadata."""
        summary_without_metadata = Summary(
            id=2,
            entity_type=EntityType.PROJECT,
            entity_id=1,
            summary_type=SummaryType.PROJECT_MILESTONE,
            summary_text="Project milestone achieved successfully.",
            context_metadata=None,
            session_id=None,
            created_at=datetime(2024, 1, 15, 11, 30, 0),
            created_by="agent-2"
        )
        
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=summary_without_metadata):
                result = runner.invoke(show_summary, ['2'])
                
                assert result.exit_code == 0
                assert "Summary #2" in result.output
                assert "Entity: project (1)" in result.output
                assert "Type: project_milestone" in result.output
                assert "Project milestone achieved successfully" in result.output
                assert "Context Metadata: None" in result.output
                assert "Session: None" in result.output
    
    def test_show_summary_not_found(self, runner, mock_db_service):
        """Test summary display when summary doesn't exist."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=None):
                result = runner.invoke(show_summary, ['999'])
                
                assert result.exit_code != 0
                assert "✗ Summary with ID 999 not found" in result.output
    
    def test_show_summary_invalid_id(self, runner, mock_db_service):
        """Test summary display with invalid ID."""
        result = runner.invoke(show_summary, ['0'])
        
        assert result.exit_code != 0
        assert "Summary ID must be greater than 0" in result.output
    
    def test_show_summary_non_numeric_id(self, runner, mock_db_service):
        """Test summary display with non-numeric ID."""
        result = runner.invoke(show_summary, ['abc'])
        
        assert result.exit_code != 0
        assert "Summary ID must be a number" in result.output
    
    def test_show_summary_database_error(self, runner, mock_db_service):
        """Test summary display with database error."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary') as mock_get:
                mock_get.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(show_summary, ['1'])
                
                assert result.exit_code != 0
                assert "✗ Error retrieving summary" in result.output
                assert "Database connection failed" in result.output
    
    def test_show_summary_verbose_output(self, runner, mock_db_service, sample_summary):
        """Test summary display with verbose output."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=sample_summary):
                result = runner.invoke(show_summary, ['1', '--verbose'])
                
                assert result.exit_code == 0
                assert "Summary #1" in result.output
                assert "Entity: work_item (1)" in result.output
                assert "Type: work_item_progress" in result.output
                assert "Created: 2024-01-15 10:30:00" in result.output
                assert "Created by: agent-1" in result.output
                assert "Session: session-123" in result.output
                assert "This is a detailed summary" in result.output
                assert "Context Metadata:" in result.output
    
    def test_show_summary_raw_output(self, runner, mock_db_service, sample_summary):
        """Test summary display with raw output format."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=sample_summary):
                result = runner.invoke(show_summary, ['1', '--raw'])
                
                assert result.exit_code == 0
                # Raw output should show the summary text without formatting
                assert "This is a detailed summary of the work item progress" in result.output
                assert "Summary #1" not in result.output  # No header in raw mode
                assert "Entity:" not in result.output  # No metadata in raw mode
    
    def test_show_summary_json_output(self, runner, mock_db_service, sample_summary):
        """Test summary display with JSON output format."""
        with patch('agentpm.cli.commands.summary.show.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.get_summary', return_value=sample_summary):
                result = runner.invoke(show_summary, ['1', '--json'])
                
                assert result.exit_code == 0
                # JSON output should be valid JSON
                import json
                json_data = json.loads(result.output)
                assert json_data["id"] == 1
                assert json_data["entity_type"] == "work_item"
                assert json_data["entity_id"] == 1
                assert json_data["summary_type"] == "work_item_progress"
                assert json_data["summary_text"] == "This is a detailed summary of the work item progress. It includes information about the decisions made, blockers encountered, and the current status of the implementation."
                assert json_data["context_metadata"] is not None
                assert json_data["session_id"] == "session-123"
                assert json_data["created_by"] == "agent-1"
    
    def test_show_summary_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(show_summary, ['--help'])
        
        assert result.exit_code == 0
        assert "Show details of a specific summary" in result.output
        assert "SUMMARY_ID" in result.output
        assert "--verbose" in result.output
        assert "--raw" in result.output
        assert "--json" in result.output
