# FTS5 Search System Documentation

## Overview

The FTS5 Search System is a comprehensive full-text search solution for APM (Agent Project Manager) that leverages SQLite's built-in FTS5 (Full-Text Search) extension. This system provides fast, relevant search capabilities across all project entities including work items, tasks, ideas, and documents.

## Architecture

### Core Components

#### 1. FTS5 Virtual Table (`search_index`)
- **Purpose**: Centralized full-text search index
- **Columns**: `entity_id`, `entity_type`, `title`, `content`, `tags`, `metadata`
- **Features**: BM25 relevance scoring, highlighting, snippet generation

#### 2. Search Service (`FTS5SearchService`)
- **Location**: `agentpm/core/search/fts5_service.py`
- **Responsibilities**:
  - Query building and execution
  - Result conversion and formatting
  - Performance metrics recording
  - Caching (currently disabled)

#### 3. Database Triggers
- **Purpose**: Automatic index synchronization
- **Coverage**: Work items, tasks, ideas
- **Operations**: INSERT, UPDATE, DELETE

#### 4. Search Models
- **SearchQuery**: Query parameters and filters
- **SearchResults**: Standardized result format
- **SearchFilter**: Entity type and metadata filtering

## Features

### Search Capabilities

#### Basic Text Search
```python
query = SearchQuery(query="authentication", limit=10)
results = search_service.search(query)
```

#### Entity Type Filtering
```python
query = SearchQuery(
    query="user management",
    filters=SearchFilter(entity_types=[EntityType.WORK_ITEM]),
    limit=10
)
```

#### Advanced FTS5 Queries
- **Boolean operators**: `AND`, `OR`, `NOT`
- **Phrase search**: `"exact phrase"`
- **Prefix matching**: `auth*`
- **Field-specific search**: `title:authentication`

### Performance Features

#### Relevance Scoring
- **Algorithm**: BM25 (Best Matching 25)
- **Normalization**: 0.0 to 1.0 scale
- **Ranking**: Results ordered by relevance

#### Highlighting
- **Title highlighting**: `<mark>` tags around matches
- **Content highlighting**: Context-aware highlighting
- **Snippets**: 32-character excerpts with `<b>` tags

#### Metrics and Analytics
- **Search metrics table**: Query performance tracking
- **Execution time**: Millisecond precision
- **Result counts**: Success rate monitoring

## Database Schema

### Search Index Table
```sql
CREATE VIRTUAL TABLE search_index USING fts5(
    entity_id,
    entity_type,
    title,
    content,
    tags,
    metadata
);
```

### Search Metrics Table
```sql
CREATE TABLE search_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    result_count INTEGER NOT NULL,
    execution_time_ms REAL NOT NULL,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Search Cache Table
```sql
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    result_data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Examples

### CLI Search
```bash
# Basic search
apm search "authentication"

# Filtered search
apm search "user management" --entity-types work_item

# Advanced search with options
apm search "OAuth2" --limit 5 --offset 10
```

### Programmatic Usage

```python
from agentpm.core.search.service import SearchService
from agentpm.core.search.models import SearchQuery, SearchFilter
from agentpm.core.database.enums import EntityType

# Initialize service
search_service = SearchService(db_service)

# Basic search
query = SearchQuery(query="authentication", limit=10)
results = search_service.search(query)

# Filtered search
query = SearchQuery(
    query="user management",
    filters=SearchFilter(entity_types=[EntityType.WORK_ITEM]),
    limit=5
)
results = search_service.search(query)

# Access results
for result in results.results:
    print(f"{result.title}: {result.relevance_score}")
```

## Migration and Setup

### Migration 0040: FTS5 Search System
The FTS5 search system is automatically created during database migration:

```python
# Migration creates:
# 1. FTS5 virtual table
# 2. Search metrics table
# 3. Search cache table
# 4. Database triggers
# 5. Initial data population
```

### Manual Setup (if needed)

```python
from agentpm.core.database.migrations.manager import MigrationManager

# Run migration
migration_manager = MigrationManager(db_service)
migration_manager.run_migrations()
```

## Performance Characteristics

### Benchmarks
- **Small datasets** (< 1,000 entities): < 10ms average
- **Medium datasets** (1,000-10,000 entities): < 50ms average
- **Large datasets** (> 10,000 entities): < 100ms average

### Optimization Features
- **Index optimization**: Automatic FTS5 optimization
- **Query caching**: Configurable result caching
- **Connection pooling**: Efficient database connections

## Configuration

### Search Configuration

```python
from agentpm.core.search.models import SearchConfig

config = SearchConfig(
    default_limit=10,
    max_limit=100,
    cache_enabled=False,  # Currently disabled
    cache_ttl_seconds=300
)
```

### FTS5 Configuration
- **Tokenizer**: `unicode61` (default)
- **Diacritics**: Removed for better matching
- **Case sensitivity**: Case-insensitive by default

## Troubleshooting

### Common Issues

#### 1. FTS5 Not Available
```python
# Check FTS5 availability
service = FTS5SearchService(db_service)
if not service.fts5_available:
    print("FTS5 not available - using fallback search")
```

#### 2. Empty Search Results
- Verify data is indexed: Check `search_index` table
- Check query syntax: Ensure proper FTS5 syntax
- Verify entity types: Confirm entity type filters

#### 3. Performance Issues
- Check index optimization: Run `OPTIMIZE search_index`
- Monitor metrics: Review `search_metrics` table
- Consider caching: Enable result caching for repeated queries

### Debug Commands
```bash
# Check FTS5 availability
apm search --check-fts5

# View search metrics
apm search --metrics

# Clear search cache
apm search --clear-cache
```

## Testing

### Test Coverage
The FTS5 search system includes comprehensive tests:

- **Unit tests**: Core functionality testing
- **Integration tests**: End-to-end search testing
- **Performance tests**: Speed and accuracy validation
- **Migration tests**: Database setup verification

### Running Tests
```bash
# Run all FTS5 tests
pytest tests/core/test_fts5_service.py -v

# Run specific test categories
pytest tests/core/test_fts5_service.py::TestFTS5SearchService -v
pytest tests/core/test_fts5_service.py::TestFTS5Integration -v
```

## Future Enhancements

### Planned Features
1. **Advanced filtering**: Date ranges, custom metadata
2. **Search suggestions**: Auto-complete functionality
3. **Search analytics**: Usage patterns and optimization
4. **Multi-language support**: Internationalization
5. **Fuzzy matching**: Typo tolerance

### Performance Improvements
1. **Result caching**: Redis-based caching
2. **Index optimization**: Periodic maintenance
3. **Query optimization**: Advanced query planning
4. **Distributed search**: Multi-database support

## API Reference

### SearchService
```python
class SearchService:
    def search(self, query: SearchQuery) -> SearchResults
    def get_search_suggestions(self, prefix: str, limit: int = 10) -> List[str]
    def get_search_metrics(self, days: int = 7) -> Dict[str, Any]
```

### FTS5SearchService
```python
class FTS5SearchService:
    def search(self, query: SearchQuery) -> SearchResults
    def _build_fts5_query(self, query: SearchQuery) -> str
    def _execute_fts5_search(self, query: SearchQuery) -> FTS5SearchResults
    def _convert_to_search_results(self, fts5_results: FTS5SearchResults) -> SearchResults
```

## Related Documentation

- [FTS5 Research and Capabilities](./fts5-research-and-capabilities.md)
- [Search Architecture Design](./fts5-search-architecture.md)
- [Database Migration Guide](../database/migrations.md)
- [CLI Search Commands](../../cli/commands/search.md)

## Support

For issues or questions regarding the FTS5 search system:

1. Check the troubleshooting section above
2. Review test cases for usage examples
3. Consult the API reference for detailed method signatures
4. Check migration logs for setup issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Maintainer**: APM (Agent Project Manager) Development Team
