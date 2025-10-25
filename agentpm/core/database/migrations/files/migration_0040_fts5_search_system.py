"""
Migration 0040: FTS5 Full-Text Search System

Implements SQLite FTS5 full-text search system to replace basic LIKE queries
with high-performance, feature-rich search capabilities.

New Tables:
- search_index: FTS5 virtual table for full-text search
- search_metrics: Search performance and usage tracking
- search_cache: Query result caching for performance

Features:
- BM25 relevance scoring
- Boolean queries (AND, OR, NOT)
- Phrase search with quotes
- Prefix matching with wildcards
- Text highlighting and snippets
- Entity type filtering
- Metadata-based filtering

Migration 0040
Dependencies: Migration 0039 (document content)
"""

import sqlite3
import json
from typing import List, Tuple


def upgrade(conn: sqlite3.Connection) -> None:
    """Create FTS5 search system tables and triggers"""
    print("Migration 0040: Create FTS5 search system")
    
    # Check FTS5 availability
    if not _check_fts5_availability(conn):
        print("⚠️  FTS5 not available - creating fallback tables only")
        _create_fallback_tables(conn)
        return
    
    print("✅ FTS5 available - creating full search system")
    
    # Create FTS5 virtual table
    _create_search_index_table(conn)
    
    # Create search metrics table
    _create_search_metrics_table(conn)
    
    # Create search cache table
    _create_search_cache_table(conn)
    
    # Create content synchronization triggers
    _create_synchronization_triggers(conn)
    
    # Populate initial data
    _populate_initial_data(conn)
    
    print("✅ FTS5 search system created successfully")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove FTS5 search system"""
    print("Migration 0040: Remove FTS5 search system")
    
    # Drop triggers
    _drop_synchronization_triggers(conn)
    
    # Drop tables
    _drop_search_tables(conn)
    
    print("✅ FTS5 search system removed")


def _check_fts5_availability(conn: sqlite3.Connection) -> bool:
    """Check if FTS5 is available in this SQLite build"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT fts5(?)", ("test",))
        return True
    except sqlite3.OperationalError:
        return False


def _create_search_index_table(conn: sqlite3.Connection) -> None:
    """Create FTS5 virtual table for search index"""
    cursor = conn.cursor()
    
    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS search_index")
    
    # Create FTS5 virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE search_index USING fts5(
            entity_id,
            entity_type,
            title,
            content,
            tags,
            metadata
        )
    """)
    
    print("✅ Created search_index FTS5 virtual table")


def _create_search_metrics_table(conn: sqlite3.Connection) -> None:
    """Create search metrics tracking table"""
    cursor = conn.cursor()
    
    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS search_metrics")
    
    cursor.execute("""
        CREATE TABLE search_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL DEFAULT 1,
            query_text TEXT NOT NULL,
            result_count INTEGER NOT NULL,
            execution_time_ms REAL NOT NULL,
            user_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    # Create index for performance
    cursor.execute("""
        CREATE INDEX idx_search_metrics_timestamp 
        ON search_metrics(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX idx_search_metrics_project_id 
        ON search_metrics(project_id)
    """)
    
    print("✅ Created search_metrics table")


def _create_search_cache_table(conn: sqlite3.Connection) -> None:
    """Create search result cache table"""
    cursor = conn.cursor()
    
    # Drop if exists (for idempotent migration)
    cursor.execute("DROP TABLE IF EXISTS search_cache")
    
    cursor.execute("""
        CREATE TABLE search_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_hash TEXT UNIQUE NOT NULL,
            query_text TEXT NOT NULL,
            result_data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL
        )
    """)
    
    # Create index for cache cleanup
    cursor.execute("""
        CREATE INDEX idx_search_cache_expires_at 
        ON search_cache(expires_at)
    """)
    
    cursor.execute("""
        CREATE INDEX idx_search_cache_query_hash 
        ON search_cache(query_hash)
    """)
    
    print("✅ Created search_cache table")


def _create_synchronization_triggers(conn: sqlite3.Connection) -> None:
    """Create triggers for automatic content synchronization"""
    cursor = conn.cursor()
    
    # Drop existing triggers (for idempotent migration)
    _drop_synchronization_triggers(conn)
    
    # Work Items triggers
    cursor.execute("""
        CREATE TRIGGER work_items_search_insert AFTER INSERT ON work_items BEGIN
            INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
            VALUES (
                NEW.id, 
                'work_item', 
                NEW.name, 
                COALESCE(NEW.description, '') || ' ' || COALESCE(NEW.business_context, ''),
                '',
                json_object('status', NEW.status, 'type', NEW.type, 'priority', COALESCE(NEW.priority, ''))
            );
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER work_items_search_update AFTER UPDATE ON work_items BEGIN
            UPDATE search_index 
            SET 
                title = NEW.name,
                content = COALESCE(NEW.description, '') || ' ' || COALESCE(NEW.business_context, ''),
                tags = '',
                metadata = json_object('status', NEW.status, 'type', NEW.type, 'priority', COALESCE(NEW.priority, ''))
            WHERE entity_id = NEW.id AND entity_type = 'work_item';
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER work_items_search_delete AFTER DELETE ON work_items BEGIN
            DELETE FROM search_index WHERE entity_id = OLD.id AND entity_type = 'work_item';
        END
    """)
    
    # Tasks triggers
    cursor.execute("""
        CREATE TRIGGER tasks_search_insert AFTER INSERT ON tasks BEGIN
            INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
            VALUES (
                NEW.id, 
                'task', 
                NEW.name, 
                COALESCE(NEW.description, ''),
                '',
                json_object('status', NEW.status, 'type', NEW.type, 'work_item_id', NEW.work_item_id)
            );
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER tasks_search_update AFTER UPDATE ON tasks BEGIN
            UPDATE search_index 
            SET 
                title = NEW.name,
                content = COALESCE(NEW.description, ''),
                tags = '',
                metadata = json_object('status', NEW.status, 'type', NEW.type, 'work_item_id', NEW.work_item_id)
            WHERE entity_id = NEW.id AND entity_type = 'task';
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER tasks_search_delete AFTER DELETE ON tasks BEGIN
            DELETE FROM search_index WHERE entity_id = OLD.id AND entity_type = 'task';
        END
    """)
    
    # Ideas triggers
    cursor.execute("""
        CREATE TRIGGER ideas_search_insert AFTER INSERT ON ideas BEGIN
            INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
            VALUES (
                NEW.id, 
                'idea', 
                NEW.title, 
                COALESCE(NEW.description, ''),
                COALESCE(NEW.tags, ''),
                json_object('status', NEW.status, 'source', COALESCE(NEW.source, ''))
            );
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER ideas_search_update AFTER UPDATE ON ideas BEGIN
            UPDATE search_index 
            SET 
                title = NEW.title,
                content = COALESCE(NEW.description, ''),
                tags = COALESCE(NEW.tags, ''),
                metadata = json_object('status', NEW.status, 'source', COALESCE(NEW.source, ''))
            WHERE entity_id = NEW.id AND entity_type = 'idea';
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER ideas_search_delete AFTER DELETE ON ideas BEGIN
            DELETE FROM search_index WHERE entity_id = OLD.id AND entity_type = 'idea';
        END
    """)
    
    print("✅ Created content synchronization triggers")


def _populate_initial_data(conn: sqlite3.Connection) -> None:
    """Populate FTS5 index with existing data"""
    cursor = conn.cursor()
    
    print("📊 Populating search index with existing data...")
    
    # Populate work items
    cursor.execute("""
        INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
        SELECT 
            id,
            'work_item',
            name,
            COALESCE(description, '') || ' ' || COALESCE(business_context, ''),
            '',
            json_object('status', status, 'type', type, 'priority', COALESCE(priority, ''))
        FROM work_items
    """)
    work_items_count = cursor.rowcount
    print(f"  ✅ Indexed {work_items_count} work items")
    
    # Populate tasks
    cursor.execute("""
        INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
        SELECT 
            id,
            'task',
            name,
            COALESCE(description, ''),
            '',
            json_object('status', status, 'type', type, 'work_item_id', work_item_id)
        FROM tasks
    """)
    tasks_count = cursor.rowcount
    print(f"  ✅ Indexed {tasks_count} tasks")
    
    # Populate ideas
    cursor.execute("""
        INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
        SELECT 
            id,
            'idea',
            title,
            COALESCE(description, ''),
            COALESCE(tags, ''),
            json_object('status', status, 'source', COALESCE(source, ''))
        FROM ideas
    """)
    ideas_count = cursor.rowcount
    print(f"  ✅ Indexed {ideas_count} ideas")
    
    total_count = work_items_count + tasks_count + ideas_count
    print(f"✅ Total indexed: {total_count} entities")


def _create_fallback_tables(conn: sqlite3.Connection) -> None:
    """Create fallback tables when FTS5 is not available"""
    cursor = conn.cursor()
    
    # Create simple search index table (without FTS5)
    cursor.execute("DROP TABLE IF EXISTS search_index")
    cursor.execute("""
        CREATE TABLE search_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for LIKE queries
    cursor.execute("CREATE INDEX idx_search_index_entity_type ON search_index(entity_type)")
    cursor.execute("CREATE INDEX idx_search_index_title ON search_index(title)")
    cursor.execute("CREATE INDEX idx_search_index_content ON search_index(content)")
    
    # Create other tables normally
    _create_search_metrics_table(conn)
    _create_search_cache_table(conn)
    
    print("⚠️  Created fallback search tables (FTS5 not available)")


def _drop_synchronization_triggers(conn: sqlite3.Connection) -> None:
    """Drop all search synchronization triggers"""
    cursor = conn.cursor()
    
    triggers_to_drop = [
        'work_items_search_insert',
        'work_items_search_update', 
        'work_items_search_delete',
        'tasks_search_insert',
        'tasks_search_update',
        'tasks_search_delete',
        'ideas_search_insert',
        'ideas_search_update',
        'ideas_search_delete'
    ]
    
    for trigger_name in triggers_to_drop:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
    
    print("✅ Dropped synchronization triggers")


def _drop_search_tables(conn: sqlite3.Connection) -> None:
    """Drop all search-related tables"""
    cursor = conn.cursor()
    
    tables_to_drop = [
        'search_index',
        'search_metrics', 
        'search_cache'
    ]
    
    for table_name in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    print("✅ Dropped search tables")


# Migration metadata
MIGRATION_ID = "0040"
MIGRATION_NAME = "fts5_search_system"
DEPENDENCIES = ["0039"]  # document_content
DESCRIPTION = "Implement FTS5 full-text search system with virtual tables, triggers, and caching"
