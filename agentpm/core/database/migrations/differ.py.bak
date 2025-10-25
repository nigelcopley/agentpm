"""
Schema Differ

Detects differences between current database schema and target schema.

Identifies:
- Table changes (add, drop, rename)
- Column changes (add, drop, modify)
- Index changes (add, drop)
- Trigger changes (add, drop)

Design:
- Introspects SQLite schema using sqlite_master
- Compares current state with target schema from schema.py
- Generates structured change objects for migration generator

Reference: Task #111 - Migration Auto-Generation
"""

import sqlite3
from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass


class ChangeType(Enum):
    """Type of schema change"""
    ADD_TABLE = "add_table"
    DROP_TABLE = "drop_table"
    RENAME_TABLE = "rename_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_TRIGGER = "add_trigger"
    DROP_TRIGGER = "drop_trigger"


@dataclass
class SchemaChange:
    """
    Base class for schema changes.

    All schema changes include:
    - Type of change
    - Affected object name
    - Reversible flag (can we undo this?)
    - Destructive flag (does this lose data?)
    """
    change_type: ChangeType
    object_name: str
    reversible: bool = True
    destructive: bool = False

    def to_sql(self) -> str:
        """Generate SQL for this change"""
        raise NotImplementedError("Subclass must implement to_sql()")

    def to_rollback_sql(self) -> Optional[str]:
        """Generate rollback SQL (if reversible)"""
        if not self.reversible:
            return None
        raise NotImplementedError("Subclass must implement to_rollback_sql()")


@dataclass
class TableChange(SchemaChange):
    """Table-level schema change"""
    schema: Optional[str] = None  # CREATE TABLE statement (for ADD_TABLE)
    new_name: Optional[str] = None  # New name (for RENAME_TABLE)

    def to_sql(self) -> str:
        if self.change_type == ChangeType.ADD_TABLE:
            return self.schema or f"CREATE TABLE {self.object_name} (id INTEGER PRIMARY KEY)"
        elif self.change_type == ChangeType.DROP_TABLE:
            return f"DROP TABLE {self.object_name}"
        elif self.change_type == ChangeType.RENAME_TABLE:
            return f"ALTER TABLE {self.object_name} RENAME TO {self.new_name}"
        return ""

    def to_rollback_sql(self) -> Optional[str]:
        if not self.reversible:
            return None

        if self.change_type == ChangeType.ADD_TABLE:
            return f"DROP TABLE {self.object_name}"
        elif self.change_type == ChangeType.DROP_TABLE:
            # Cannot easily reverse DROP TABLE (would need schema)
            return None
        elif self.change_type == ChangeType.RENAME_TABLE:
            return f"ALTER TABLE {self.new_name} RENAME TO {self.object_name}"
        return None


@dataclass
class ColumnChange(SchemaChange):
    """Column-level schema change"""
    table_name: str = ""
    column_type: Optional[str] = None  # e.g., "TEXT", "INTEGER"
    nullable: bool = True
    default: Optional[str] = None

    def to_sql(self) -> str:
        if self.change_type == ChangeType.ADD_COLUMN:
            sql = f"ALTER TABLE {self.table_name} ADD COLUMN {self.object_name}"
            if self.column_type:
                sql += f" {self.column_type}"
            if self.default is not None:
                sql += f" DEFAULT {self.default}"
            return sql
        elif self.change_type == ChangeType.DROP_COLUMN:
            # SQLite limitation: Cannot DROP COLUMN directly
            # Must recreate table without column
            return f"-- SQLite limitation: Recreate {self.table_name} without {self.object_name}"
        elif self.change_type == ChangeType.MODIFY_COLUMN:
            return f"-- SQLite limitation: Recreate {self.table_name} with modified {self.object_name}"
        return ""

    def to_rollback_sql(self) -> Optional[str]:
        if not self.reversible:
            return None

        if self.change_type == ChangeType.ADD_COLUMN:
            # SQLite limitation: Cannot DROP COLUMN directly
            return f"-- SQLite limitation: Recreate {self.table_name} without {self.object_name}"
        return None


@dataclass
class IndexChange(SchemaChange):
    """Index-level schema change"""
    table_name: str = ""
    columns: List[str] = None  # type: ignore
    unique: bool = False

    def __post_init__(self):
        if self.columns is None:
            self.columns = []

    def to_sql(self) -> str:
        if self.change_type == ChangeType.ADD_INDEX:
            unique_clause = "UNIQUE " if self.unique else ""
            columns_str = ", ".join(self.columns)
            return f"CREATE {unique_clause}INDEX {self.object_name} ON {self.table_name}({columns_str})"
        elif self.change_type == ChangeType.DROP_INDEX:
            return f"DROP INDEX {self.object_name}"
        return ""

    def to_rollback_sql(self) -> Optional[str]:
        if not self.reversible:
            return None

        if self.change_type == ChangeType.ADD_INDEX:
            return f"DROP INDEX {self.object_name}"
        elif self.change_type == ChangeType.DROP_INDEX:
            # Cannot easily reverse DROP INDEX (would need columns)
            return None
        return None


@dataclass
class TriggerChange(SchemaChange):
    """Trigger-level schema change"""
    table_name: str = ""
    trigger_sql: Optional[str] = None

    def to_sql(self) -> str:
        if self.change_type == ChangeType.ADD_TRIGGER:
            return self.trigger_sql or f"-- CREATE TRIGGER {self.object_name}"
        elif self.change_type == ChangeType.DROP_TRIGGER:
            return f"DROP TRIGGER {self.object_name}"
        return ""

    def to_rollback_sql(self) -> Optional[str]:
        if not self.reversible:
            return None

        if self.change_type == ChangeType.ADD_TRIGGER:
            return f"DROP TRIGGER {self.object_name}"
        return None


class SchemaDiffer:
    """
    Detects schema differences between current database and target schema.

    Usage:
        from agentpm.core.database import DatabaseService
        from agentpm.core.database.migrations import SchemaDiffer

        db = DatabaseService("path/to/db.sqlite")
        differ = SchemaDiffer(db)

        # Compare with target schema
        changes = differ.compare_schemas(target_schema_sql)

        for change in changes:
            print(f"{change.change_type}: {change.object_name}")
            print(f"  SQL: {change.to_sql()}")
    """

    def __init__(self, db_service: 'DatabaseService'):  # type: ignore
        """
        Initialize schema differ.

        Args:
            db_service: Database service instance
        """
        self.db_service = db_service

    def compare_schemas(self, target_schema_ddl: str) -> List[SchemaChange]:
        """
        Compare current schema with target schema DDL.

        Args:
            target_schema_ddl: Target schema SQL (CREATE TABLE statements)

        Returns:
            List of schema changes needed to reach target
        """
        changes: List[SchemaChange] = []

        # Get current schema state
        current_tables = self._get_current_tables()
        current_indexes = self._get_current_indexes()
        current_triggers = self._get_current_triggers()

        # Parse target schema (simplified - assumes one CREATE TABLE per line)
        target_tables = self._parse_target_tables(target_schema_ddl)
        target_indexes = self._parse_target_indexes(target_schema_ddl)
        target_triggers = self._parse_target_triggers(target_schema_ddl)

        # Detect table changes
        changes.extend(self.detect_table_changes(current_tables, target_tables))

        # Detect index changes
        changes.extend(self.detect_index_changes(current_indexes, target_indexes))

        # Detect trigger changes
        changes.extend(self.detect_trigger_changes(current_triggers, target_triggers))

        return changes

    def detect_table_changes(
        self,
        current_tables: Set[str],
        target_tables: Dict[str, str]
    ) -> List[TableChange]:
        """
        Detect table additions and deletions.

        Args:
            current_tables: Set of existing table names
            target_tables: Dict of target table names → CREATE TABLE SQL

        Returns:
            List of table changes
        """
        changes: List[TableChange] = []

        target_names = set(target_tables.keys())

        # Tables to add
        for table_name in target_names - current_tables:
            changes.append(TableChange(
                change_type=ChangeType.ADD_TABLE,
                object_name=table_name,
                schema=target_tables[table_name],
                reversible=True,
                destructive=False
            ))

        # Tables to drop
        for table_name in current_tables - target_names:
            changes.append(TableChange(
                change_type=ChangeType.DROP_TABLE,
                object_name=table_name,
                reversible=False,  # Cannot easily reverse DROP TABLE
                destructive=True   # Loses data
            ))

        return changes

    def detect_column_changes(
        self,
        table_name: str,
        current_columns: List[Dict],
        target_columns: List[Dict]
    ) -> List[ColumnChange]:
        """
        Detect column additions, deletions, modifications within a table.

        Args:
            table_name: Table being compared
            current_columns: List of current column metadata
            target_columns: List of target column metadata

        Returns:
            List of column changes
        """
        changes: List[ColumnChange] = []

        current_names = {col['name'] for col in current_columns}
        target_names = {col['name'] for col in target_columns}

        # Columns to add
        for col in target_columns:
            if col['name'] not in current_names:
                changes.append(ColumnChange(
                    change_type=ChangeType.ADD_COLUMN,
                    object_name=col['name'],
                    table_name=table_name,
                    column_type=col.get('type', 'TEXT'),
                    nullable=col.get('notnull', 0) == 0,
                    default=col.get('dflt_value'),
                    reversible=False,  # SQLite limitation
                    destructive=False
                ))

        # Columns to drop (SQLite limitation: requires table recreation)
        for col in current_columns:
            if col['name'] not in target_names:
                changes.append(ColumnChange(
                    change_type=ChangeType.DROP_COLUMN,
                    object_name=col['name'],
                    table_name=table_name,
                    reversible=False,  # SQLite limitation
                    destructive=True
                ))

        return changes

    def detect_index_changes(
        self,
        current_indexes: Dict[str, Dict],
        target_indexes: Dict[str, Dict]
    ) -> List[IndexChange]:
        """
        Detect index additions and deletions.

        Args:
            current_indexes: Dict of current index name → metadata
            target_indexes: Dict of target index name → metadata

        Returns:
            List of index changes
        """
        changes: List[IndexChange] = []

        current_names = set(current_indexes.keys())
        target_names = set(target_indexes.keys())

        # Indexes to add
        for index_name in target_names - current_names:
            idx = target_indexes[index_name]
            changes.append(IndexChange(
                change_type=ChangeType.ADD_INDEX,
                object_name=index_name,
                table_name=idx.get('table', ''),
                columns=idx.get('columns', []),
                unique=idx.get('unique', False),
                reversible=True,
                destructive=False
            ))

        # Indexes to drop
        for index_name in current_names - target_names:
            changes.append(IndexChange(
                change_type=ChangeType.DROP_INDEX,
                object_name=index_name,
                reversible=False,
                destructive=False
            ))

        return changes

    def detect_trigger_changes(
        self,
        current_triggers: Dict[str, str],
        target_triggers: Dict[str, str]
    ) -> List[TriggerChange]:
        """
        Detect trigger additions and deletions.

        Args:
            current_triggers: Dict of current trigger name → SQL
            target_triggers: Dict of target trigger name → SQL

        Returns:
            List of trigger changes
        """
        changes: List[TriggerChange] = []

        current_names = set(current_triggers.keys())
        target_names = set(target_triggers.keys())

        # Triggers to add
        for trigger_name in target_names - current_names:
            changes.append(TriggerChange(
                change_type=ChangeType.ADD_TRIGGER,
                object_name=trigger_name,
                trigger_sql=target_triggers[trigger_name],
                reversible=True,
                destructive=False
            ))

        # Triggers to drop
        for trigger_name in current_names - target_names:
            changes.append(TriggerChange(
                change_type=ChangeType.DROP_TRIGGER,
                object_name=trigger_name,
                reversible=True,
                destructive=False
            ))

        return changes

    def detect_conflicts(self, changes: List[SchemaChange]) -> List[str]:
        """
        Detect conflicting changes that cannot be applied together.

        Args:
            changes: List of schema changes

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Group changes by object identifier (for columns: table.column, otherwise object_name)
        changes_by_identifier: Dict[str, List[SchemaChange]] = {}
        for change in changes:
            # For columns, use table.column as identifier
            if isinstance(change, ColumnChange):
                identifier = f"{change.table_name}.{change.object_name}"
            else:
                identifier = change.object_name

            if identifier not in changes_by_identifier:
                changes_by_identifier[identifier] = []
            changes_by_identifier[identifier].append(change)

        # Check for conflicts within same object
        for identifier, object_changes in changes_by_identifier.items():
            if len(object_changes) <= 1:
                continue

            change_types = [c.change_type for c in object_changes]

            # Conflict: ADD_TABLE + DROP_TABLE on same object
            if ChangeType.ADD_TABLE in change_types and ChangeType.DROP_TABLE in change_types:
                conflicts.append(
                    f"Conflict: {identifier} has both ADD and DROP table operations"
                )

            # Conflict: ADD_COLUMN + DROP_COLUMN on same column
            if ChangeType.ADD_COLUMN in change_types and ChangeType.DROP_COLUMN in change_types:
                conflicts.append(
                    f"Conflict: {identifier} has both ADD and DROP column operations"
                )

        return conflicts

    def _get_current_tables(self) -> Set[str]:
        """Get list of current table names"""
        with self.db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            return {row[0] for row in cursor.fetchall()}

    def _get_current_indexes(self) -> Dict[str, Dict]:
        """Get current indexes with metadata"""
        indexes = {}

        with self.db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT name, tbl_name, sql FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)

            for row in cursor.fetchall():
                indexes[row[0]] = {
                    'table': row[1],
                    'sql': row[2],
                    'columns': [],  # Would need to parse SQL for columns
                    'unique': 'UNIQUE' in (row[2] or '').upper()
                }

        return indexes

    def _get_current_triggers(self) -> Dict[str, str]:
        """Get current triggers with SQL"""
        triggers = {}

        with self.db_service.connect() as conn:
            cursor = conn.execute("""
                SELECT name, sql FROM sqlite_master
                WHERE type='trigger'
                ORDER BY name
            """)

            for row in cursor.fetchall():
                triggers[row[0]] = row[1] or ''

        return triggers

    def _get_table_columns(self, table_name: str) -> List[Dict]:
        """Get column metadata for a table"""
        with self.db_service.connect() as conn:
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                })
            return columns

    def _parse_target_tables(self, ddl: str) -> Dict[str, str]:
        """
        Parse CREATE TABLE statements from DDL.

        Simplified parser - production version would use SQL parser.
        """
        tables = {}
        current_table = None
        current_sql = []

        for line in ddl.split('\n'):
            line = line.strip()

            if line.startswith('CREATE TABLE'):
                # Extract table name
                parts = line.split()
                if len(parts) >= 3:
                    table_name = parts[2].rstrip('(')
                    current_table = table_name
                    current_sql = [line]
            elif current_table and line:
                current_sql.append(line)

                # End of CREATE TABLE
                if line.endswith(');') or line.endswith(')'):
                    tables[current_table] = '\n'.join(current_sql)
                    current_table = None
                    current_sql = []

        return tables

    def _parse_target_indexes(self, ddl: str) -> Dict[str, Dict]:
        """Parse CREATE INDEX statements from DDL"""
        indexes = {}

        for line in ddl.split('\n'):
            line = line.strip()

            if line.startswith('CREATE INDEX') or line.startswith('CREATE UNIQUE INDEX'):
                # Extract index name (simplified)
                parts = line.split()
                unique = 'UNIQUE' in line.upper()

                # Find index name and table name
                if 'ON' in parts:
                    on_idx = parts.index('ON')
                    index_name = parts[on_idx - 1]
                    table_name = parts[on_idx + 1].split('(')[0]

                    indexes[index_name] = {
                        'table': table_name,
                        'unique': unique,
                        'columns': [],  # Would need to parse for actual columns
                        'sql': line
                    }

        return indexes

    def _parse_target_triggers(self, ddl: str) -> Dict[str, str]:
        """Parse CREATE TRIGGER statements from DDL"""
        triggers = {}
        current_trigger = None
        current_sql = []

        for line in ddl.split('\n'):
            line = line.strip()

            if line.startswith('CREATE TRIGGER'):
                parts = line.split()
                if len(parts) >= 3:
                    trigger_name = parts[2]
                    current_trigger = trigger_name
                    current_sql = [line]
            elif current_trigger:
                current_sql.append(line)

                if line.upper() == 'END;':
                    triggers[current_trigger] = '\n'.join(current_sql)
                    current_trigger = None
                    current_sql = []

        return triggers
