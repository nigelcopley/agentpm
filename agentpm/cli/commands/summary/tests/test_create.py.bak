import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch

from agentpm.cli.commands.summary.create import create_summary
from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType


class TestCreateSummaryCommand:
    """Test the create summary CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mock database service."""
        return Mock()
    
    def test_create_summary_success(self, runner, mock_db_service):
        """Test successful summary creation."""
        # Mock the summary creation
        created_summary = Summary(
            id=1,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary created via CLI.",
            created_by="test-user"
        )
        
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary', return_value=created_summary):
                result = runner.invoke(create_summary, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--summary-type', 'work_item_progress',
                    '--text', 'Test summary created via CLI.',
                    '--created-by', 'test-user'
                ])
                
                assert result.exit_code == 0
                assert "✓ Summary created successfully" in result.output
                assert "ID: 1" in result.output
                assert "Entity: work_item (1)" in result.output
                assert "Type: work_item_progress" in result.output
    
    def test_create_summary_with_metadata(self, runner, mock_db_service):
        """Test summary creation with context metadata."""
        metadata = '{"decisions": ["Use React"], "blockers": []}'
        created_summary = Summary(
            id=1,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with metadata.",
            context_metadata={"decisions": ["Use React"], "blockers": []},
            created_by="test-user"
        )
        
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary', return_value=created_summary):
                result = runner.invoke(create_summary, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--summary-type', 'work_item_progress',
                    '--text', 'Test summary with metadata.',
                    '--metadata', metadata,
                    '--created-by', 'test-user'
                ])
                
                assert result.exit_code == 0
                assert "✓ Summary created successfully" in result.output
    
    def test_create_summary_with_session_id(self, runner, mock_db_service):
        """Test summary creation with session ID."""
        created_summary = Summary(
            id=1,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.SESSION_HANDOVER,
            summary_text="Session handover summary.",
            session_id="session-123",
            created_by="test-user"
        )
        
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary', return_value=created_summary):
                result = runner.invoke(create_summary, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--summary-type', 'session_handover',
                    '--text', 'Session handover summary.',
                    '--session-id', 'session-123',
                    '--created-by', 'test-user'
                ])
                
                assert result.exit_code == 0
                assert "✓ Summary created successfully" in result.output
                assert "Session: session-123" in result.output
    
    def test_create_summary_invalid_entity_type(self, runner, mock_db_service):
        """Test summary creation with invalid entity type."""
        result = runner.invoke(create_summary, [
            '--entity-type', 'invalid_type',
            '--entity-id', '1',
            '--summary-type', 'work_item_progress',
            '--text', 'Test summary with invalid entity type.'
        ])
        
        assert result.exit_code != 0
        assert "Invalid entity type" in result.output
    
    def test_create_summary_invalid_entity_id(self, runner, mock_db_service):
        """Test summary creation with invalid entity ID."""
        result = runner.invoke(create_summary, [
            '--entity-type', 'work_item',
            '--entity-id', '0',  # Invalid: must be > 0
            '--summary-type', 'work_item_progress',
            '--text', 'Test summary with invalid entity ID.'
        ])
        
        assert result.exit_code != 0
        assert "Entity ID must be greater than 0" in result.output
    
    def test_create_summary_invalid_summary_type(self, runner, mock_db_service):
        """Test summary creation with invalid summary type."""
        result = runner.invoke(create_summary, [
            '--entity-type', 'work_item',
            '--entity-id', '1',
            '--summary-type', 'invalid_type',
            '--text', 'Test summary with invalid summary type.'
        ])
        
        assert result.exit_code != 0
        assert "Invalid summary type" in result.output
    
    def test_create_summary_short_text(self, runner, mock_db_service):
        """Test summary creation with text that's too short."""
        result = runner.invoke(create_summary, [
            '--entity-type', 'work_item',
            '--entity-id', '1',
            '--summary-type', 'work_item_progress',
            '--text', 'Short'  # Too short: must be at least 10 characters
        ])
        
        assert result.exit_code != 0
        assert "Summary text must be at least 10 characters" in result.output
    
    def test_create_summary_invalid_json_metadata(self, runner, mock_db_service):
        """Test summary creation with invalid JSON metadata."""
        result = runner.invoke(create_summary, [
            '--entity-type', 'work_item',
            '--entity-id', '1',
            '--summary-type', 'work_item_progress',
            '--text', 'Test summary with invalid JSON metadata.',
            '--metadata', 'invalid json {'
        ])
        
        assert result.exit_code != 0
        assert "Invalid JSON in metadata" in result.output
    
    def test_create_summary_validation_error(self, runner, mock_db_service):
        """Test summary creation with validation error from database."""
        from agentpm.core.database.service import ValidationError
        
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary') as mock_create:
                mock_create.side_effect = ValidationError("Work Item with ID 1 does not exist.")
                
                result = runner.invoke(create_summary, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--summary-type', 'work_item_progress',
                    '--text', 'Test summary with validation error.'
                ])
                
                assert result.exit_code != 0
                assert "✗ Error creating summary" in result.output
                assert "Work Item with ID 1 does not exist" in result.output
    
    def test_create_summary_database_error(self, runner, mock_db_service):
        """Test summary creation with database error."""
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary') as mock_create:
                mock_create.side_effect = Exception("Database connection failed.")
                
                result = runner.invoke(create_summary, [
                    '--entity-type', 'work_item',
                    '--entity-id', '1',
                    '--summary-type', 'work_item_progress',
                    '--text', 'Test summary with database error.'
                ])
                
                assert result.exit_code != 0
                assert "✗ Error creating summary" in result.output
                assert "Database connection failed" in result.output
    
    def test_create_summary_interactive_mode(self, runner, mock_db_service):
        """Test summary creation in interactive mode."""
        created_summary = Summary(
            id=1,
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Interactive summary creation.",
            created_by="test-user"
        )
        
        with patch('agentpm.cli.commands.summary.create.get_db_service', return_value=mock_db_service):
            with patch('agentpm.core.database.methods.summaries.create_summary', return_value=created_summary):
                # Simulate interactive input
                result = runner.invoke(create_summary, input="work_item\n1\nwork_item_progress\nInteractive summary creation.\ntest-user\n")
                
                assert result.exit_code == 0
                assert "✓ Summary created successfully" in result.output
    
    def test_create_summary_help(self, runner):
        """Test that the help message is displayed correctly."""
        result = runner.invoke(create_summary, ['--help'])
        
        assert result.exit_code == 0
        assert "Create a new summary" in result.output
        assert "--entity-type" in result.output
        assert "--entity-id" in result.output
        assert "--summary-type" in result.output
        assert "--text" in result.output
