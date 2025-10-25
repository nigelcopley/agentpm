"""
Migration 0041: FTS5 Indexes for Evidence Sources and Sessions

Implements SQLite FTS5 full-text search indexes for evidence_sources and
sessions tables to enable fast, powerful search capabilities.

New Virtual Tables:
- evidence_fts: FTS5 index for evidence sources (url, excerpt, source_type)
- sessions_fts: FTS5 index for sessions (developer_name, session_type, metadata)

Features:
- Full-text search across evidence excerpts and URLs
- Session search by developer, type, and metadata content
- Automatic synchronization via triggers
- BM25 relevance scoring
- Unicode tokenization with diacritics removal
- UNINDEXED columns for non-searchable ID fields

Migration 0041
Dependencies: Migration 0040 (FTS5 search system)
"""

import sqlite3
import json
from typing import List, Tuple


def upgrade(conn: sqlite3.Connection) -> None:
    """Create FTS5 indexes for evidence_sources and sessions tables"""
    print("Migration 0041: Create FTS5 indexes for evidence_sources and sessions")

    # Check FTS5 availability
    if not _check_fts5_availability(conn):
        print("⚠️  FTS5 not available - skipping virtual table creation")
        return

    print("✅ FTS5 available - creating evidence and sessions FTS indexes")

    # Create evidence FTS5 virtual table
    _create_evidence_fts_table(conn)

    # Create sessions FTS5 virtual table
    _create_sessions_fts_table(conn)

    # Create triggers for evidence_sources
    _create_evidence_triggers(conn)

    # Create triggers for sessions
    _create_sessions_triggers(conn)

    # Populate initial data
    _populate_evidence_fts(conn)
    _populate_sessions_fts(conn)

    print("✅ FTS5 indexes created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove FTS5 indexes for evidence_sources and sessions"""
    print("Migration 0041: Remove FTS5 indexes for evidence_sources and sessions")

    # Drop triggers
    _drop_evidence_triggers(conn)
    _drop_sessions_triggers(conn)

    # Drop virtual tables
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS evidence_fts")
    cursor.execute("DROP TABLE IF EXISTS sessions_fts")

    print("✅ FTS5 indexes removed")


def _check_fts5_availability(conn: sqlite3.Connection) -> bool:
    """Check if FTS5 is available in this SQLite build"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT fts5(?)", ("test",))
        return True
    except sqlite3.OperationalError:
        return False


def _create_evidence_fts_table(conn: sqlite3.Connection) -> None:
    """
    Create FTS5 virtual table for evidence_sources

    Searchable fields:
    - entity_type: Type of entity (project, work_item, task, idea)
    - source_type: Type of source (documentation, research, etc.)
    - url: Source URL
    - excerpt: Content excerpt

    Non-searchable fields (UNINDEXED):
    - evidence_id: Primary key from evidence_sources table
    - entity_id: Foreign key to entity
    """
    cursor = conn.cursor()

    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS evidence_fts")

    # Create FTS5 virtual table with unicode61 tokenizer
    cursor.execute("""
        CREATE VIRTUAL TABLE evidence_fts USING fts5(
            evidence_id UNINDEXED,
            entity_type,
            entity_id UNINDEXED,
            source_type,
            url,
            excerpt,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    print("✅ Created evidence_fts FTS5 virtual table")


def _create_sessions_fts_table(conn: sqlite3.Connection) -> None:
    """
    Create FTS5 virtual table for sessions

    Searchable fields:
    - session_type: Type of session (coding, review, planning, etc.)
    - developer_name: Developer who created the session
    - tool_name: Tool used (claude-code, cursor, etc.)
    - llm_model: LLM model used
    - exit_reason: Why session ended
    - metadata_text: Extracted JSON metadata as searchable text

    Non-searchable fields (UNINDEXED):
    - session_id: Primary key from sessions table
    - project_id: Foreign key to project
    """
    cursor = conn.cursor()

    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS sessions_fts")

    # Create FTS5 virtual table with unicode61 tokenizer
    cursor.execute("""
        CREATE VIRTUAL TABLE sessions_fts USING fts5(
            session_id UNINDEXED,
            project_id UNINDEXED,
            session_type,
            developer_name,
            tool_name,
            llm_model,
            exit_reason,
            metadata_text,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    print("✅ Created sessions_fts FTS5 virtual table")


def _create_evidence_triggers(conn: sqlite3.Connection) -> None:
    """Create triggers for automatic evidence_sources FTS synchronization"""
    cursor = conn.cursor()

    # Drop existing triggers (for idempotent migration)
    _drop_evidence_triggers(conn)

    # INSERT trigger
    cursor.execute("""
        CREATE TRIGGER evidence_fts_insert AFTER INSERT ON evidence_sources
        BEGIN
            INSERT INTO evidence_fts(
                evidence_id,
                entity_type,
                entity_id,
                source_type,
                url,
                excerpt
            )
            VALUES (
                NEW.id,
                NEW.entity_type,
                NEW.entity_id,
                COALESCE(NEW.source_type, ''),
                COALESCE(NEW.url, ''),
                COALESCE(NEW.excerpt, '')
            );
        END
    """)

    # UPDATE trigger
    cursor.execute("""
        CREATE TRIGGER evidence_fts_update AFTER UPDATE ON evidence_sources
        BEGIN
            UPDATE evidence_fts
            SET
                entity_type = NEW.entity_type,
                entity_id = NEW.entity_id,
                source_type = COALESCE(NEW.source_type, ''),
                url = COALESCE(NEW.url, ''),
                excerpt = COALESCE(NEW.excerpt, '')
            WHERE evidence_id = NEW.id;
        END
    """)

    # DELETE trigger
    cursor.execute("""
        CREATE TRIGGER evidence_fts_delete AFTER DELETE ON evidence_sources
        BEGIN
            DELETE FROM evidence_fts WHERE evidence_id = OLD.id;
        END
    """)

    print("✅ Created evidence_sources FTS triggers")


def _create_sessions_triggers(conn: sqlite3.Connection) -> None:
    """Create triggers for automatic sessions FTS synchronization"""
    cursor = conn.cursor()

    # Drop existing triggers (for idempotent migration)
    _drop_sessions_triggers(conn)

    # INSERT trigger - extract metadata JSON into searchable text
    cursor.execute("""
        CREATE TRIGGER sessions_fts_insert AFTER INSERT ON sessions
        BEGIN
            INSERT INTO sessions_fts(
                session_id,
                project_id,
                session_type,
                developer_name,
                tool_name,
                llm_model,
                exit_reason,
                metadata_text
            )
            VALUES (
                NEW.id,
                NEW.project_id,
                COALESCE(NEW.session_type, ''),
                COALESCE(NEW.developer_name, ''),
                COALESCE(NEW.tool_name, ''),
                COALESCE(NEW.llm_model, ''),
                COALESCE(NEW.exit_reason, ''),
                COALESCE(NEW.metadata, '{}')
            );
        END
    """)

    # UPDATE trigger
    cursor.execute("""
        CREATE TRIGGER sessions_fts_update AFTER UPDATE ON sessions
        BEGIN
            UPDATE sessions_fts
            SET
                project_id = NEW.project_id,
                session_type = COALESCE(NEW.session_type, ''),
                developer_name = COALESCE(NEW.developer_name, ''),
                tool_name = COALESCE(NEW.tool_name, ''),
                llm_model = COALESCE(NEW.llm_model, ''),
                exit_reason = COALESCE(NEW.exit_reason, ''),
                metadata_text = COALESCE(NEW.metadata, '{}')
            WHERE session_id = NEW.id;
        END
    """)

    # DELETE trigger
    cursor.execute("""
        CREATE TRIGGER sessions_fts_delete AFTER DELETE ON sessions
        BEGIN
            DELETE FROM sessions_fts WHERE session_id = OLD.id;
        END
    """)

    print("✅ Created sessions FTS triggers")


def _populate_evidence_fts(conn: sqlite3.Connection) -> None:
    """Populate evidence_fts with existing evidence_sources data"""
    cursor = conn.cursor()

    print("📊 Populating evidence_fts with existing data...")

    cursor.execute("""
        INSERT INTO evidence_fts(
            evidence_id,
            entity_type,
            entity_id,
            source_type,
            url,
            excerpt
        )
        SELECT
            id,
            entity_type,
            entity_id,
            COALESCE(source_type, ''),
            COALESCE(url, ''),
            COALESCE(excerpt, '')
        FROM evidence_sources
    """)

    count = cursor.rowcount
    print(f"  ✅ Indexed {count} evidence sources")


def _populate_sessions_fts(conn: sqlite3.Connection) -> None:
    """Populate sessions_fts with existing sessions data"""
    cursor = conn.cursor()

    print("📊 Populating sessions_fts with existing data...")

    cursor.execute("""
        INSERT INTO sessions_fts(
            session_id,
            project_id,
            session_type,
            developer_name,
            tool_name,
            llm_model,
            exit_reason,
            metadata_text
        )
        SELECT
            id,
            project_id,
            COALESCE(session_type, ''),
            COALESCE(developer_name, ''),
            COALESCE(tool_name, ''),
            COALESCE(llm_model, ''),
            COALESCE(exit_reason, ''),
            COALESCE(metadata, '{}')
        FROM sessions
    """)

    count = cursor.rowcount
    print(f"  ✅ Indexed {count} sessions")


def _drop_evidence_triggers(conn: sqlite3.Connection) -> None:
    """Drop evidence_sources FTS triggers"""
    cursor = conn.cursor()

    triggers = [
        'evidence_fts_insert',
        'evidence_fts_update',
        'evidence_fts_delete'
    ]

    for trigger_name in triggers:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")


def _drop_sessions_triggers(conn: sqlite3.Connection) -> None:
    """Drop sessions FTS triggers"""
    cursor = conn.cursor()

    triggers = [
        'sessions_fts_insert',
        'sessions_fts_update',
        'sessions_fts_delete'
    ]

    for trigger_name in triggers:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")


# Migration metadata
MIGRATION_ID = "0041"
MIGRATION_NAME = "evidence_sessions_fts"
DEPENDENCIES = ["0040"]  # fts5_search_system
DESCRIPTION = "Add FTS5 full-text search indexes for evidence_sources and sessions tables"
