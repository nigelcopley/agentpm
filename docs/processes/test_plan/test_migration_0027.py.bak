"""
Test suite for migration 0027: Add metadata column to agents table.

Tests cover:
- Schema validation (column exists, type, default)
- Idempotency (running twice doesn't error)
- Data preservation (existing agents unchanged)
- Upgrade/downgrade cycle
- Edge cases (empty table, populated table)

Coverage Target: ≥90% (TEST-023)
"""

import pytest
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.migrations.manager import MigrationManager, MigrationInfo
from agentpm.core.database.migrations.files import migration_0027


class TestMigration0027SchemaChanges:
    """Test Suite 1: Schema validation for migration 0027."""

    def test_metadata_column_added_to_agents_table(
        self,
        empty_db_service,
        migration_state_factory,
        schema_inspector
    ):
        """
        Test that migration 0027 adds metadata column to agents table.

        Arrange:
            - Database with migrations up to 0026
        Act:
            - Run migration 0027
        Assert:
            - metadata column exists
            - Column type is TEXT
            - Default value is '{}'
        """
        # Arrange: Apply migrations up to 0026
        manager = migration_state_factory(empty_db_service, "0026")

        with empty_db_service.connect() as conn:
            # Verify metadata column does NOT exist yet
            assert not schema_inspector.column_exists(conn, "agents", "metadata")

        # Act: Run migration 0027
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert: metadata column now exists with correct schema
        with empty_db_service.connect() as conn:
            assert schema_inspector.column_exists(conn, "agents", "metadata")

            # Get column details
            col_info = schema_inspector.get_column_info(conn, "agents", "metadata")
            assert col_info['type'] == 'TEXT'
            assert col_info['dflt_value'] == "'{}'"

    def test_metadata_column_nullable(
        self,
        empty_db_service,
        migration_state_factory,
        schema_inspector
    ):
        """
        Test that metadata column is nullable for backwards compatibility.

        Arrange:
            - Database with migrations up to 0026
        Act:
            - Run migration 0027
        Assert:
            - metadata column is nullable (notnull=0)
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0026")

        # Act
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert
        with empty_db_service.connect() as conn:
            col_info = schema_inspector.get_column_info(conn, "agents", "metadata")
            assert col_info['notnull'] == 0  # Column is nullable


class TestMigration0027Idempotency:
    """Test Suite 2: Idempotency - running migration 0027 multiple times."""

    def test_migration_0027_idempotent(
        self,
        empty_db_service,
        migration_state_factory,
        schema_inspector
    ):
        """
        Test that running migration 0027 twice doesn't error.

        Arrange:
            - Database with migration 0027 already applied
        Act:
            - Run migration 0027 again directly
        Assert:
            - No error raised
            - metadata column still exists
            - No duplicate columns
        """
        # Arrange: Apply migration 0027
        manager = migration_state_factory(empty_db_service, "0027")

        # Act: Run migration 0027 again directly
        with empty_db_service.connect() as conn:
            # Should not raise exception
            migration_0027.upgrade(conn)
            conn.commit()

        # Assert: Column still exists, no duplicates
        with empty_db_service.connect() as conn:
            columns = schema_inspector.get_table_columns(conn, "agents")
            metadata_columns = [col for col in columns if col['name'] == 'metadata']
            assert len(metadata_columns) == 1  # Only one metadata column

    def test_migration_0027_skips_if_column_exists(
        self,
        empty_db_service,
        migration_state_factory,
        capfd
    ):
        """
        Test that migration 0027 detects existing column and skips gracefully.

        Arrange:
            - Database with migration 0027 already applied
        Act:
            - Run migration 0027 again
        Assert:
            - Migration prints skip message
            - No ALTER TABLE executed
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0027")

        # Act: Run migration again
        with empty_db_service.connect() as conn:
            migration_0027.upgrade(conn)
            conn.commit()

        # Assert: Check output for skip message
        captured = capfd.readouterr()
        assert "metadata column already exists, skipping" in captured.out


class TestMigration0027DataPreservation:
    """Test Suite 3: Data preservation during migration."""

    def test_existing_agent_data_preserved(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory,
        test_agent_factory
    ):
        """
        Test that existing agent records are preserved when adding metadata column.

        Arrange:
            - Database with migrations up to 0026
            - Insert test agent data
        Act:
            - Run migration 0027
        Assert:
            - All existing agent data unchanged
            - metadata column populated with default '{}'
        """
        # Arrange: Setup database with test data
        manager = migration_state_factory(empty_db_service, "0026")

        with empty_db_service.connect() as conn:
            # Create test project
            project_id = test_project_factory(conn, "Test Project")

            # Create test agents
            agent1_id = test_agent_factory(
                conn,
                project_id,
                role="test-agent-1",
                display_name="Test Agent 1"
            )
            agent2_id = test_agent_factory(
                conn,
                project_id,
                role="test-agent-2",
                display_name="Test Agent 2"
            )
            conn.commit()

            # Store original data for comparison
            cursor = conn.execute(
                "SELECT id, role, display_name, description FROM agents ORDER BY id"
            )
            original_agents = cursor.fetchall()

        # Act: Run migration 0027
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert: Verify data preserved
        with empty_db_service.connect() as conn:
            cursor = conn.execute(
                "SELECT id, role, display_name, description, metadata FROM agents ORDER BY id"
            )
            migrated_agents = cursor.fetchall()

            # Should have same number of agents
            assert len(migrated_agents) == len(original_agents)

            # Verify each agent's core data unchanged
            for i, (orig, migrated) in enumerate(zip(original_agents, migrated_agents)):
                assert migrated[0] == orig[0]  # id
                assert migrated[1] == orig[1]  # role
                assert migrated[2] == orig[2]  # display_name
                assert migrated[3] == orig[3]  # description

                # metadata should default to '{}'
                assert migrated[4] == '{}'

    def test_metadata_default_value_for_new_agents(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory
    ):
        """
        Test that new agents after migration get default metadata value.

        Arrange:
            - Database with migration 0027 applied
        Act:
            - Insert new agent WITHOUT specifying metadata
        Assert:
            - Agent's metadata field is '{}'
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0027")

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")

            # Act: Insert agent without metadata
            cursor = conn.execute("""
                INSERT INTO agents (
                    project_id, role, display_name, description,
                    is_active, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                "new-agent",
                "New Agent",
                "Created after migration",
                1,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            agent_id = cursor.lastrowid
            conn.commit()

            # Assert: metadata has default value
            cursor = conn.execute("SELECT metadata FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()
            assert row[0] == '{}'


class TestMigration0027UpgradeDowngrade:
    """Test Suite 4: Upgrade/downgrade cycle testing."""

    def test_upgrade_then_downgrade_cycle(
        self,
        empty_db_service,
        migration_state_factory,
        schema_inspector,
        test_project_factory,
        test_agent_factory
    ):
        """
        Test complete upgrade/downgrade cycle for migration 0027.

        Arrange:
            - Database with migrations up to 0026
            - Insert test data
        Act:
            - Run upgrade (migration 0027)
            - Verify metadata column exists
            - Run downgrade
        Assert:
            - metadata column removed
            - Other agent data preserved
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0026")

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")
            agent_id = test_agent_factory(
                conn,
                project_id,
                role="test-agent",
                display_name="Test Agent"
            )
            conn.commit()

        # Act: Upgrade
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert: metadata column exists after upgrade
        with empty_db_service.connect() as conn:
            assert schema_inspector.column_exists(conn, "agents", "metadata")

        # Act: Downgrade
        manager.rollback_migration("0027", reason="Testing downgrade")

        # Assert: metadata column removed, data preserved
        with empty_db_service.connect() as conn:
            assert not schema_inspector.column_exists(conn, "agents", "metadata")

            # Verify agent still exists with core fields
            cursor = conn.execute("SELECT id, role, display_name FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()
            assert row is not None
            assert row[1] == "test-agent"
            assert row[2] == "Test Agent"

    def test_downgrade_preserves_non_metadata_fields(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory,
        test_agent_factory
    ):
        """
        Test that downgrade preserves all non-metadata fields.

        Arrange:
            - Database with migration 0027 applied
            - Agent with metadata populated
        Act:
            - Downgrade migration 0027
        Assert:
            - All agent fields preserved except metadata
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0027")

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")

            # Create agent with all fields populated
            cursor = conn.execute("""
                INSERT INTO agents (
                    project_id, role, display_name, description,
                    sop_content, capabilities, is_active, agent_type,
                    file_path, tier, metadata,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                "full-agent",
                "Full Agent",
                "Agent with all fields",
                "SOP content here",
                json.dumps(["code", "test"]),
                1,
                "specialist",
                "/path/to/agent.md",
                2,
                json.dumps({"behavioral_rules": ["rule1", "rule2"]}),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            agent_id = cursor.lastrowid
            conn.commit()

        # Act: Downgrade
        manager.rollback_migration("0027", reason="Testing field preservation")

        # Assert: All fields preserved except metadata
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT
                    role, display_name, description, sop_content,
                    capabilities, is_active, agent_type, file_path, tier
                FROM agents
                WHERE id = ?
            """, (agent_id,))
            row = cursor.fetchone()

            assert row[0] == "full-agent"
            assert row[1] == "Full Agent"
            assert row[2] == "Agent with all fields"
            assert row[3] == "SOP content here"
            assert json.loads(row[4]) == ["code", "test"]
            assert row[5] == 1
            assert row[6] == "specialist"
            assert row[7] == "/path/to/agent.md"
            assert row[8] == 2


class TestMigration0027EdgeCases:
    """Test Suite 5: Edge cases and error conditions."""

    def test_migration_on_empty_agents_table(
        self,
        empty_db_service,
        migration_state_factory,
        schema_inspector
    ):
        """
        Test migration 0027 works with empty agents table.

        Arrange:
            - Database with migrations up to 0026
            - agents table exists but is empty
        Act:
            - Run migration 0027
        Assert:
            - metadata column added successfully
            - No errors
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0026")

        with empty_db_service.connect() as conn:
            # Verify table is empty
            cursor = conn.execute("SELECT COUNT(*) FROM agents")
            count = cursor.fetchone()[0]
            assert count == 0

        # Act
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert
        with empty_db_service.connect() as conn:
            assert schema_inspector.column_exists(conn, "agents", "metadata")

    def test_metadata_can_store_json(
        self,
        empty_db_service,
        migration_state_factory,
        test_project_factory
    ):
        """
        Test that metadata column can store complex JSON.

        Arrange:
            - Database with migration 0027 applied
        Act:
            - Insert agent with complex metadata JSON
        Assert:
            - JSON stored correctly
            - JSON can be retrieved and parsed
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0027")

        complex_metadata = {
            "behavioral_rules": [
                "Rule 1: Always validate input",
                "Rule 2: Log all operations"
            ],
            "config": {
                "timeout": 30,
                "retries": 3,
                "enabled": True
            },
            "tags": ["production", "critical"]
        }

        with empty_db_service.connect() as conn:
            project_id = test_project_factory(conn, "Test Project")

            # Act: Insert agent with complex metadata
            cursor = conn.execute("""
                INSERT INTO agents (
                    project_id, role, display_name, metadata,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                "json-test-agent",
                "JSON Test Agent",
                json.dumps(complex_metadata),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            agent_id = cursor.lastrowid
            conn.commit()

            # Assert: Retrieve and verify JSON
            cursor = conn.execute("SELECT metadata FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()
            retrieved_metadata = json.loads(row[0])

            assert retrieved_metadata == complex_metadata
            assert len(retrieved_metadata['behavioral_rules']) == 2
            assert retrieved_metadata['config']['timeout'] == 30

    def test_migration_recorded_in_registry(
        self,
        empty_db_service,
        migration_state_factory
    ):
        """
        Test that migration 0027 is recorded in schema_migrations table.

        Arrange:
            - Database with migrations up to 0026
        Act:
            - Run migration 0027
        Assert:
            - Migration recorded in schema_migrations
            - Version, description, applied_at populated
        """
        # Arrange
        manager = migration_state_factory(empty_db_service, "0026")

        # Act
        migration_0027_info = MigrationInfo(
            version="0027",
            description="Add metadata column to agents table",
            applied=False
        )
        manager.run_migration(migration_0027_info)

        # Assert
        with empty_db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT version, description, applied_at
                FROM schema_migrations
                WHERE version = '0027'
            """)
            row = cursor.fetchone()

            assert row is not None
            assert row[0] == "0027"
            assert "metadata column" in row[1]
            assert row[2] is not None  # applied_at timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
