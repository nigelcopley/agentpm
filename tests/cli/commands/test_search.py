"""
Tests for CLI Search Command

Comprehensive test suite for the unified search command with all scopes.
"""

import pytest
import tempfile
import os
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from agentpm.cli.commands.search import search
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.search_result import SearchResult, SearchResults
from agentpm.core.database.enums import EntityType, SearchResultType
from agentpm.core.search.models import SearchScope


class TestSearchCommand:
    """Test suite for search CLI command."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create test project
            cursor.execute("""
                INSERT INTO projects (id, name, description, path)
                VALUES (1, 'Test Project', 'Test project', '/tmp/test')
            """)

            # Create test work items
            cursor.execute("""
                INSERT INTO work_items (id, project_id, name, description, type, status, priority)
                VALUES (1, 1, 'OAuth2 Implementation', 'Implement OAuth2 authentication', 'feature', 'active', 1)
            """)

            # Create test tasks
            cursor.execute("""
                INSERT INTO tasks (id, work_item_id, name, description, type, status)
                VALUES (1, 1, 'Database Migration', 'Create OAuth2 tables', 'implementation', 'ready')
            """)

            # Create test session
            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'test-session', 1, 'claude-code', datetime('now'), 'coding')
            """)

            # Create test summaries
            cursor.execute("""
                INSERT INTO summaries (entity_type, entity_id, summary_type, summary_text, created_by)
                VALUES ('work_item', 1, 'work_item_progress', 'OAuth2 implementation in progress', 'agent-1')
            """)

            # Create test evidence
            cursor.execute("""
                INSERT INTO evidence_sources (entity_type, entity_id, url, source_type, excerpt, confidence, created_by)
                VALUES ('work_item', 1, 'https://oauth.net', 'documentation', 'OAuth2 specification', 0.9, 'researcher-1')
            """)

            # Populate search_index for all entities
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'work_item', name, description, '', json_object('type', type, 'status', status)
                FROM work_items
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'task', name, description, '', json_object('type', type, 'status', status)
                FROM tasks
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'summary', summary_type, summary_text, '', json_object('summary_type', summary_type)
                FROM summaries
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'evidence', COALESCE(url, 'Evidence'), excerpt, '', json_object('source_type', source_type)
                FROM evidence_sources
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'session', session_type || ' - ' || tool_name, COALESCE(metadata, ''), '', json_object('session_type', session_type)
                FROM sessions
            """)

            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    @pytest.fixture
    def mock_context(self, temp_db):
        """Create mock context for CLI."""
        db_service, db_path = temp_db
        project_root = os.path.dirname(db_path)

        # Create .aipm directory
        aipm_dir = os.path.join(project_root, '.aipm')
        os.makedirs(aipm_dir, exist_ok=True)

        return {
            'console': Mock(),
            'project_root': project_root,
            'db_service': db_service
        }

    def test_search_basic_query(self, runner, mock_context):
        """Test basic search with default scope (all)."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_all(self, runner, mock_context):
        """Test search with explicit 'all' scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'all'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_work_items(self, runner, mock_context):
        """Test search with work_items scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'work_items'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_tasks(self, runner, mock_context):
        """Test search with tasks scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'tasks'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_ideas(self, runner, mock_context):
        """Test search with ideas scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'ideas'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_documents(self, runner, mock_context):
        """Test search with documents scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'documents'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_summaries(self, runner, mock_context):
        """Test search with summaries scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'summaries'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_evidence(self, runner, mock_context):
        """Test search with evidence scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'evidence'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_scope_sessions(self, runner, mock_context):
        """Test search with sessions scope."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'sessions'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_limit(self, runner, mock_context):
        """Test search with custom limit."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--limit', '5'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_format_table(self, runner, mock_context):
        """Test search with table format (default)."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--format', 'table'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_format_list(self, runner, mock_context):
        """Test search with list format."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--format', 'list'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_format_json(self, runner, mock_context):
        """Test search with JSON format."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--format', 'json'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_min_relevance(self, runner, mock_context):
        """Test search with minimum relevance filter."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--min-relevance', '0.7'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_with_include_content(self, runner, mock_context):
        """Test search with content inclusion flag."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--include-content'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_multiple_words(self, runner, mock_context):
        """Test search with multiple word query."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', 'authentication', 'JWT'], obj=mock_context)

                # Assert
                assert result.exit_code == 0

    def test_search_no_results(self, runner, mock_context):
        """Test search with query that returns no results."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=mock_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=mock_context['db_service']):
                # Act
                result = runner.invoke(search, ['nonexistent_term_xyz'], obj=mock_context)

                # Assert
                assert result.exit_code == 0
                # Should show "no results found" message

    def test_search_invalid_scope(self, runner, mock_context):
        """Test search with invalid scope."""
        # Arrange & Act
        result = runner.invoke(search, ['OAuth2', '--scope', 'invalid_scope'], obj=mock_context)

        # Assert
        assert result.exit_code != 0  # Should fail validation

    def test_search_invalid_format(self, runner, mock_context):
        """Test search with invalid format."""
        # Arrange & Act
        result = runner.invoke(search, ['OAuth2', '--format', 'invalid_format'], obj=mock_context)

        # Assert
        assert result.exit_code != 0  # Should fail validation

    def test_search_invalid_limit(self, runner, mock_context):
        """Test search with invalid limit."""
        # Arrange & Act
        result = runner.invoke(search, ['OAuth2', '--limit', '-1'], obj=mock_context)

        # Assert
        assert result.exit_code != 0  # Should fail validation

    def test_search_invalid_min_relevance(self, runner, mock_context):
        """Test search with invalid min relevance."""
        # Arrange & Act
        result = runner.invoke(search, ['OAuth2', '--min-relevance', '1.5'], obj=mock_context)

        # Assert
        assert result.exit_code != 0  # Should fail validation


class TestSearchCommandIntegration:
    """Integration tests for search CLI command."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def integration_db(self):
        """Create database with realistic test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        db_service = DatabaseService(db_path)

        with db_service.connect() as conn:
            cursor = conn.cursor()

            # Create comprehensive test data
            cursor.execute("""
                INSERT INTO projects (id, name, description, path)
                VALUES (1, 'Integration Project', 'Project for integration tests', '/tmp/integration')
            """)

            # Add work items
            for i in range(5):
                cursor.execute("""
                    INSERT INTO work_items (id, project_id, name, description, type, status, priority)
                    VALUES (?, 1, ?, ?, 'feature', 'active', 1)
                """, (i + 1, f'Feature {i}', f'OAuth2 related feature {i}'))

            # Add tasks
            for i in range(5):
                cursor.execute("""
                    INSERT INTO tasks (id, work_item_id, name, description, type, status)
                    VALUES (?, ?, ?, ?, 'implementation', 'ready')
                """, (i + 1, (i % 5) + 1, f'Task {i}', f'Implementation task {i} for OAuth2'))

            # Add session
            cursor.execute("""
                INSERT INTO sessions (id, session_id, project_id, tool_name, start_time, session_type)
                VALUES (1, 'int-session', 1, 'claude-code', datetime('now'), 'coding')
            """)

            # Add summaries
            for i in range(5):
                cursor.execute("""
                    INSERT INTO summaries (entity_type, entity_id, summary_type, summary_text, created_by)
                    VALUES ('work_item', ?, 'work_item_progress', ?, ?)
                """, ((i % 5) + 1, f'Summary {i}: OAuth2 progress update', f'agent-{i}'))

            # Add evidence
            for i in range(5):
                cursor.execute("""
                    INSERT INTO evidence_sources (entity_type, entity_id, url, source_type, excerpt, confidence, created_by)
                    VALUES ('work_item', ?, ?, 'documentation', ?, 0.8, ?)
                """, ((i % 5) + 1, f'https://example.com/doc{i}', f'OAuth2 documentation excerpt {i}', f'researcher-{i}'))

            # Populate search_index for all entities
            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'work_item', name, description, '', json_object('type', type, 'status', status)
                FROM work_items
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'task', name, description, '', json_object('type', type, 'status', status)
                FROM tasks
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'summary', summary_type, summary_text, '', json_object('summary_type', summary_type)
                FROM summaries
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'evidence', COALESCE(url, 'Evidence'), excerpt, '', json_object('source_type', source_type)
                FROM evidence_sources
            """)

            cursor.execute("""
                INSERT INTO search_index (entity_id, entity_type, title, content, tags, metadata)
                SELECT id, 'session', session_type || ' - ' || tool_name, COALESCE(metadata, ''), '', json_object('session_type', session_type)
                FROM sessions
            """)

            conn.commit()

        yield db_service, db_path

        os.unlink(db_path)

    @pytest.fixture
    def integration_context(self, integration_db):
        """Create integration test context."""
        db_service, db_path = integration_db
        project_root = os.path.dirname(db_path)

        aipm_dir = os.path.join(project_root, '.aipm')
        os.makedirs(aipm_dir, exist_ok=True)

        return {
            'console': Mock(),
            'project_root': project_root,
            'db_service': db_service
        }

    def test_integration_search_all_scopes(self, runner, integration_context):
        """Test searching across all scopes returns results from different entity types."""
        # Arrange
        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=integration_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=integration_context['db_service']):
                # Act
                result = runner.invoke(search, ['OAuth2', '--scope', 'all', '--limit', '20'], obj=integration_context)

                # Assert
                assert result.exit_code == 0

    def test_integration_search_each_scope_individually(self, runner, integration_context):
        """Test each scope individually to ensure they all work."""
        # Arrange
        scopes = ['work_items', 'tasks', 'summaries', 'evidence', 'sessions']

        with patch('agentpm.cli.commands.search.ensure_project_root', return_value=integration_context['project_root']):
            with patch('agentpm.cli.commands.search.get_database_service', return_value=integration_context['db_service']):
                for scope in scopes:
                    # Act
                    result = runner.invoke(search, ['OAuth2', '--scope', scope], obj=integration_context)

                    # Assert
                    assert result.exit_code == 0, f"Search failed for scope: {scope}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
