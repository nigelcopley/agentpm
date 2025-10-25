"""
Integration test suite for migration sequence 0020→0027→0029.

Tests the complete migration sequence that fixes the agents.metadata issue:
- Migration 0020: Recreated agents table (omitted metadata column)
- Migration 0027: Adds metadata column back
- Migration 0029: Uses metadata column for utility agents

Coverage Target: ≥90% (TEST-023)
"""

import pytest
import sqlite3
import json
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.migrations.manager import MigrationManager, MigrationInfo


class TestFreshDatabaseMigrationSequence:
    """Test Suite 1: Fresh database migration sequence."""

    def test_fresh_database_full_migration_sequence(
        self,
        empty_db_service,
        schema_inspector,
        test_project_factory
    ):
        """
        Test complete migration sequence on fresh database.

        Arrange:
            - Empty database with only schema_migrations table
            - Create a test project (required for migration 0029)
        Act:
            - Run all migrations from start to 0029
        Assert:
            - All migrations applied successfully
            - agents.metadata column exists
            - 5 utility agents inserted
        """
        # Arrange: Empty database
        # Act: Run all pending migrations
        manager = MigrationManager(empty_db_service)
        success_count, failure_count = manager.run_all_pending()

        # Assert: All migrations successful
        assert failure_count == 0
        assert success_count > 0

        # Create a project for migration 0029 to use
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        # Run migration 0029 again now that a project exists
        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        with empty_db_service.connect() as conn:
            # Verify agents.metadata column exists
            assert schema_inspector.column_exists(conn, "agents", "metadata")

            # Verify 5 utility agents exist
            cursor = conn.execute("""
                SELECT COUNT(*) FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)
            utility_agent_count = cursor.fetchone()[0]
            assert utility_agent_count == 5

    def test_utility_agents_have_metadata(
        self,
        empty_db_service,
        test_project_factory
    ):
        """
        Test that utility agents inserted by migration 0029 have metadata populated.

        Arrange:
            - Fresh database with all migrations
            - Project created for migration 0029
        Act:
            - Query utility agents
        Assert:
            - Each has metadata field populated
            - metadata contains behavioral_rules
        """
        # Arrange: Run all migrations
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Create project and run migration 0029 again
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Act & Assert: Check each utility agent
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT role, metadata FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)

            agents = cursor.fetchall()
            assert len(agents) == 5

            for role, metadata_str in agents:
                # Verify metadata is valid JSON
                metadata = json.loads(metadata_str)

                # Verify behavioral_rules present
                assert 'behavioral_rules' in metadata
                assert isinstance(metadata['behavioral_rules'], list)
                assert len(metadata['behavioral_rules']) > 0

    def test_utility_agents_metadata_structure(
        self,
        empty_db_service,
        test_project_factory
    ):
        """
        Test specific metadata structure for utility agents.

        Arrange:
            - Fresh database with all migrations
            - Project for migration 0029
        Act:
            - Query context-generator agent
        Assert:
            - Metadata has expected behavioral_rules
        """
        # Arrange
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Create project and run migration 0029
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Act
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT metadata FROM agents
                WHERE role = 'context-generator'
            """)
            row = cursor.fetchone()

            # Assert
            assert row is not None
            metadata = json.loads(row[0])

            # Check specific behavioral rules for context-generator
            behavioral_rules = metadata['behavioral_rules']
            assert any('confidence' in rule.lower() for rule in behavioral_rules)
            assert any('context' in rule.lower() for rule in behavioral_rules)


class TestExistingDatabaseMigration:
    """Test Suite 2: Migration on existing database."""

    def test_migration_0027_on_database_with_existing_agents(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory,
        test_agent_factory,
        schema_inspector
    ):
        """
        Test migration 0027 adds metadata column to database with existing agents.

        Arrange:
            - Database with migrations up to 0026
            - Existing test agents
        Act:
            - Run migration 0027
        Assert:
            - metadata column added
            - Existing agents preserved with default metadata
        """
        # Arrange: Setup database at migration 0026 with test data
        manager = migration_state_factory(empty_db_service, "0026")

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")

            # Create test agents
            agent1_id = test_agent_factory(
                conn,
                project_id,
                role="existing-agent-1",
                display_name="Existing Agent 1"
            )
            agent2_id = test_agent_factory(
                conn,
                project_id,
                role="existing-agent-2",
                display_name="Existing Agent 2"
            )
            conn.commit()

        # Act: Run migration 0027
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert: Column added, existing agents preserved
        with empty_db_service.connect() as conn:
            # Verify column exists
            assert schema_inspector.column_exists(conn, "agents", "metadata")

            # Verify existing agents have default metadata
            cursor = conn.execute("SELECT id, role, metadata FROM agents ORDER BY id")
            agents = cursor.fetchall()

            assert len(agents) == 2
            assert agents[0][1] == "existing-agent-1"
            assert agents[0][2] == "{}"  # Default metadata
            assert agents[1][1] == "existing-agent-2"
            assert agents[1][2] == "{}"  # Default metadata

    def test_migration_0029_adds_utility_agents_after_0027(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory,
        test_agent_factory
    ):
        """
        Test that migration 0029 successfully adds utility agents after 0027.

        Arrange:
            - Database with migrations up to 0027
            - Existing test agents
        Act:
            - Run migration 0029
        Assert:
            - 5 utility agents added
            - Existing agents unchanged
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0027")

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")
            test_agent_id = test_agent_factory(
                conn,
                project_id,
                role="test-agent",
                display_name="Test Agent"
            )
            conn.commit()

            # Count agents before migration 0029
            cursor = conn.execute("SELECT COUNT(*) FROM agents")
            count_before = cursor.fetchone()[0]
            assert count_before == 1

        # Act: Run migration 0029
        migration_0029_info = MigrationInfo(
            version="0029",
            description="Add five new utility agents",
            applied=False
        )
        manager.run_migration(migration_0029_info)

        # Assert: 5 new agents added
        with empty_db_service.connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM agents")
            count_after = cursor.fetchone()[0]
            assert count_after == 6  # 1 test agent + 5 utility agents

            # Verify utility agents
            cursor = conn.execute("""
                SELECT role FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)
            utility_agents = cursor.fetchall()
            assert len(utility_agents) == 5

            # Verify test agent still exists
            cursor = conn.execute("SELECT id, role FROM agents WHERE role = 'test-agent'")
            test_agent = cursor.fetchone()
            assert test_agent is not None
            assert test_agent[0] == test_agent_id


class TestMigration0029Idempotency:
    """Test Suite 3: Idempotency of migration 0029."""

    def test_migration_0029_idempotent(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory
    ):
        """
        Test that running migration 0029 twice doesn't duplicate agents.

        Arrange:
            - Database with migration 0029 already applied
            - Project exists
        Act:
            - Run migration 0029 again directly
        Assert:
            - No duplicate agents created
            - Still only 5 utility agents
        """
        # Arrange: Apply migration 0029
        manager = migration_state_factory(empty_db_service, "0029")

        # Create project and run migration 0029
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        with empty_db_service.connect() as conn:
            # Count utility agents before re-running
            cursor = conn.execute("""
                SELECT COUNT(*) FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)
            count_before = cursor.fetchone()[0]
            assert count_before == 5

        # Act: Run migration 0029 again directly
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Assert: Still only 5 utility agents (no duplicates)
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)
            count_after = cursor.fetchone()[0]
            assert count_after == 5  # No duplicates

    def test_migration_0029_skips_if_agents_exist(
        self,
        empty_db_service,
        migration_state_factory,
        capfd
    ):
        """
        Test that migration 0029 detects existing agents and skips.

        Arrange:
            - Database with migration 0029 already applied
        Act:
            - Run migration 0029 again
        Assert:
            - Migration prints skip message
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0029")

        # Act: Run migration again
        from agentpm.core.database.migrations.files import migration_0029

        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Assert: Check output for skip message
        captured = capfd.readouterr()
        assert "already exist" in captured.out or "skipping" in captured.out


class TestMigrationSequenceValidation:
    """Test Suite 4: Schema validation after full sequence."""

    def test_agents_table_schema_after_sequence(
        self,
        empty_db_service,
        schema_inspector
    ):
        """
        Test complete agents table schema after migration sequence.

        Arrange:
            - Fresh database
        Act:
            - Run all migrations
        Assert:
            - All expected columns exist
            - metadata column has correct type and default
        """
        # Arrange & Act
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Assert: Verify complete schema
        with empty_db_service.connect() as conn:
            columns = schema_inspector.get_table_columns(conn, "agents")
            column_names = {col['name'] for col in columns}

            # Expected columns after all migrations
            expected_columns = {
                'id', 'project_id', 'role', 'display_name', 'description',
                'sop_content', 'capabilities', 'is_active', 'agent_type',
                'file_path', 'generated_at', 'tier', 'metadata',
                'created_at', 'updated_at'
            }

            assert expected_columns.issubset(column_names)

            # Verify metadata column details
            metadata_col = next(col for col in columns if col['name'] == 'metadata')
            assert metadata_col['type'] == 'TEXT'
            assert metadata_col['dflt_value'] == "'{}'"

    def test_agents_table_indexes_after_sequence(
        self,
        empty_db_service,
        schema_inspector
    ):
        """
        Test that agents table has proper indexes after migration sequence.

        Arrange:
            - Fresh database
        Act:
            - Run all migrations
        Assert:
            - Expected indexes exist
        """
        # Arrange & Act
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Assert: Verify indexes
        with empty_db_service.connect() as conn:
            indexes = schema_inspector.get_table_indexes(conn, "agents")

            # Expected indexes
            expected_indexes = [
                'idx_agents_project',
                'idx_agents_role',
                'idx_agents_active',
                'idx_agents_type'
            ]

            for expected_index in expected_indexes:
                assert expected_index in indexes


class TestMigration0029NoProject:
    """Test Suite 5: Edge case - no project exists."""

    def test_migration_0029_skips_if_no_project(
        self,
        empty_db_service,
        migration_state_factory,
        capfd
    ):
        """
        Test that migration 0029 skips gracefully if no project exists.

        Arrange:
            - Database with migration 0027 but NO project
        Act:
            - Run migration 0029
        Assert:
            - Migration skips with warning
            - No agents created
        """
        # Arrange: Apply migrations up to 0027
        manager = migration_state_factory(empty_db_service, "0027")

        # Ensure no projects exist
        with empty_db_service.connect() as conn:
            conn.execute("DELETE FROM projects")
            conn.commit()

        # Act: Run migration 0029
        from agentpm.core.database.migrations.files import migration_0029

        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Assert: No agents created
        with empty_db_service.connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM agents")
            agent_count = cursor.fetchone()[0]
            assert agent_count == 0

        # Check for warning message
        captured = capfd.readouterr()
        assert "No project found" in captured.out or "skipping" in captured.out


class TestMigrationChainIntegrity:
    """Test Suite 6: Migration chain integrity."""

    def test_migration_chain_has_expected_gaps(
        self,
        empty_db_service,
        test_project_factory
    ):
        """
        Test migration chain after running full sequence.

        Note: Migration 0018 consolidated 0001-0017, so gaps exist (expected).
        Validation will return False due to gaps, which is correct behavior.

        Arrange:
            - Fresh database
            - Project for migration 0029
        Act:
            - Run all migrations
        Assert:
            - Migration files exist for 0018+
            - Validation detects gaps (0001-0017 missing) as expected
        """
        # Arrange & Act
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Create project for migration 0029
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        # Assert: Validation detects expected gaps from consolidated migration
        # This is expected behavior - migration 0018 replaced 0001-0017
        is_valid = manager.validate_migration_chain()
        assert is_valid == False  # Expected due to consolidation

        # But verify that all migrations from 0018 onwards exist
        migrations = manager.discover_migrations()
        versions = sorted([int(m.version) for m in migrations])

        # Check we have 0018 and onwards
        assert 18 in versions
        assert 27 in versions
        assert 29 in versions

    def test_all_migrations_recorded(
        self,
        empty_db_service
    ):
        """
        Test that all migrations are recorded in schema_migrations table.

        Arrange:
            - Fresh database
        Act:
            - Run all migrations
        Assert:
            - Migrations 0027 and 0029 recorded
        """
        # Arrange & Act
        manager = MigrationManager(empty_db_service)
        success_count, failure_count = manager.run_all_pending()

        # Assert: Check specific migrations recorded
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT version FROM schema_migrations
                WHERE version IN ('0027', '0029')
                ORDER BY version
            """)
            recorded_migrations = [row[0] for row in cursor.fetchall()]

            assert '0027' in recorded_migrations
            assert '0029' in recorded_migrations

    def test_pending_migrations_empty_after_sequence(
        self,
        empty_db_service
    ):
        """
        Test that no pending migrations remain after running all.

        Arrange:
            - Fresh database
        Act:
            - Run all migrations
        Assert:
            - get_pending_migrations() returns empty list
        """
        # Arrange & Act
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Assert: No pending migrations
        pending = manager.get_pending_migrations()
        assert len(pending) == 0


class TestUtilityAgentDetails:
    """Test Suite 7: Verify utility agent details."""

    def test_context_generator_agent_details(
        self,
        empty_db_service,
        test_project_factory
    ):
        """
        Test context-generator agent details.

        Arrange:
            - Fresh database with all migrations
            - Project for migration 0029
        Act:
            - Query context-generator agent
        Assert:
            - Has correct display_name, description, and metadata
        """
        # Arrange
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Create project and run migration 0029
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Act & Assert
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT display_name, description, metadata
                FROM agents
                WHERE role = 'context-generator'
            """)
            row = cursor.fetchone()

            assert row is not None
            assert row[0] == "Context Assembly Specialist"
            assert "session context" in row[1].lower()

            metadata = json.loads(row[2])
            assert 'behavioral_rules' in metadata
            assert len(metadata['behavioral_rules']) >= 3

    def test_all_utility_agents_active(
        self,
        empty_db_service,
        test_project_factory
    ):
        """
        Test that all utility agents are active by default.

        Arrange:
            - Fresh database with all migrations
            - Project for migration 0029
        Act:
            - Query all utility agents
        Assert:
            - All have is_active = 1
        """
        # Arrange
        manager = MigrationManager(empty_db_service)
        manager.run_all_pending()

        # Create project and run migration 0029
        with empty_db_service.connect() as conn:
            test_project_factory(conn, "Test Project")
            conn.commit()

        from agentpm.core.database.migrations.files import migration_0029
        with empty_db_service.connect() as conn:
            migration_0029.upgrade(conn)
            conn.commit()

        # Act & Assert
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT role, is_active FROM agents
                WHERE role IN (
                    'context-generator',
                    'agent-builder',
                    'database-query-agent',
                    'file-operations-agent',
                    'workflow-coordinator'
                )
            """)
            agents = cursor.fetchall()

            assert len(agents) == 5

            for role, is_active in agents:
                assert is_active == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
