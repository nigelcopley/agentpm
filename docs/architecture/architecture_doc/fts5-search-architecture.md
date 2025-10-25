# FTS5 Search Architecture Design

## Executive Summary

This document defines the architecture for implementing SQLite FTS5 (Full-Text Search) in APM (Agent Project Manager), replacing the current basic LIKE-based search with a high-performance, feature-rich search system.

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FTS5 Search System                       │
├─────────────────────────────────────────────────────────────┤
│  Search Service Layer                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   SearchQuery   │  │  SearchResults  │  │ SearchConfig │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  FTS5 Virtual Tables                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  search_index   │  │ search_metrics  │  │ search_cache │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Content Synchronization                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Triggers      │  │   Adapters      │  │   Methods    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Entity Integration                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Work Items     │  │     Tasks       │  │    Ideas     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. FTS5 Virtual Tables

#### Primary Search Index
```sql
CREATE VIRTUAL TABLE search_index USING fts5(
    entity_id,
    entity_type,
    title,
    content,
    tags,
    metadata,
    content='main_entities',
    content_rowid='id'
);
```

**Columns:**
- `entity_id`: Primary key reference to source entity
- `entity_type`: Type of entity (work_item, task, idea)
- `title`: Searchable title/name
- `content`: Main searchable content (description, details)
- `tags`: Comma-separated tags for filtering
- `metadata`: JSON metadata for advanced filtering

#### Search Metrics Table
```sql
CREATE TABLE search_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    result_count INTEGER NOT NULL,
    execution_time_ms REAL NOT NULL,
    user_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### Search Cache Table
```sql
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    result_data TEXT NOT NULL, -- JSON serialized results
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);
```

### 2. Content Synchronization

#### Database Triggers
```sql
-- Work Items
CREATE TRIGGER work_items_search_insert AFTER INSERT ON work_items BEGIN
    INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
    VALUES (
        NEW.id, 
        'work_item', 
        NEW.name, 
        COALESCE(NEW.description, '') || ' ' || COALESCE(NEW.business_context, ''),
        COALESCE(NEW.tags, ''),
        json_object('status', NEW.status, 'type', NEW.type, 'priority', NEW.priority)
    );
END;

CREATE TRIGGER work_items_search_update AFTER UPDATE ON work_items BEGIN
    UPDATE search_index 
    SET 
        title = NEW.name,
        content = COALESCE(NEW.description, '') || ' ' || COALESCE(NEW.business_context, ''),
        tags = COALESCE(NEW.tags, ''),
        metadata = json_object('status', NEW.status, 'type', NEW.type, 'priority', NEW.priority)
    WHERE entity_id = NEW.id AND entity_type = 'work_item';
END;

CREATE TRIGGER work_items_search_delete AFTER DELETE ON work_items BEGIN
    DELETE FROM search_index WHERE entity_id = OLD.id AND entity_type = 'work_item';
END;

-- Tasks
CREATE TRIGGER tasks_search_insert AFTER INSERT ON tasks BEGIN
    INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
    VALUES (
        NEW.id, 
        'task', 
        NEW.name, 
        COALESCE(NEW.description, ''),
        COALESCE(NEW.tags, ''),
        json_object('status', NEW.status, 'type', NEW.type, 'work_item_id', NEW.work_item_id)
    );
END;

-- Ideas
CREATE TRIGGER ideas_search_insert AFTER INSERT ON ideas BEGIN
    INSERT INTO search_index(entity_id, entity_type, title, content, tags, metadata)
    VALUES (
        NEW.id, 
        'idea', 
        NEW.title, 
        COALESCE(NEW.description, ''),
        COALESCE(NEW.tags, ''),
        json_object('status', NEW.status, 'type', NEW.type)
    );
END;
```

### 3. Search Service Architecture

#### SearchQuery Model
```python
@dataclass
class SearchQuery:
    query_text: str
    entity_types: Optional[List[EntityType]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = 50
    offset: int = 0
    include_highlights: bool = True
    include_snippets: bool = True
    sort_by: SearchSortBy = SearchSortBy.RELEVANCE
```

#### SearchResults Model
```python
@dataclass
class SearchResults:
    results: List[SearchResult]
    total_count: int
    query_time_ms: float
    query_text: str
    filters_applied: Dict[str, Any]
    suggestions: Optional[List[str]] = None
```

#### SearchResult Model
```python
@dataclass
class SearchResult:
    entity_id: int
    entity_type: EntityType
    title: str
    content: str
    relevance_score: float
    highlighted_title: Optional[str] = None
    highlighted_content: Optional[str] = None
    snippet: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 4. Search Service Implementation

#### Core Search Service
```python
class FTS5SearchService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.cache = SearchCache()
        self.metrics = SearchMetrics()
    
    def search(self, query: SearchQuery) -> SearchResults:
        # 1. Check cache
        cached_result = self.cache.get(query)
        if cached_result:
            return cached_result
        
        # 2. Build FTS5 query
        fts5_query = self._build_fts5_query(query)
        
        # 3. Execute search with timing
        start_time = time.time()
        results = self._execute_search(fts5_query, query)
        execution_time = (time.time() - start_time) * 1000
        
        # 4. Record metrics
        self.metrics.record_search(query.query_text, len(results), execution_time)
        
        # 5. Cache results
        self.cache.store(query, results)
        
        return results
    
    def _build_fts5_query(self, query: SearchQuery) -> str:
        """Build FTS5 query string with entity type filtering."""
        fts5_query = query.query_text
        
        # Add entity type filtering
        if query.entity_types:
            entity_filters = [f'entity_type:{et.value}' for et in query.entity_types]
            fts5_query += f' AND ({" OR ".join(entity_filters)})'
        
        # Add metadata filtering
        if query.filters:
            for key, value in query.filters.items():
                fts5_query += f' AND metadata.{key}:{value}'
        
        return fts5_query
    
    def _execute_search(self, fts5_query: str, query: SearchQuery) -> List[SearchResult]:
        """Execute FTS5 search and return results."""
        sql = """
        SELECT 
            entity_id,
            entity_type,
            title,
            content,
            bm25(search_index) as relevance_score,
            highlight(search_index, 1, '<mark>', '</mark>') as highlighted_title,
            highlight(search_index, 2, '<mark>', '</mark>') as highlighted_content,
            snippet(search_index, 2, '<b>', '</b>', '...', 32) as snippet,
            metadata
        FROM search_index 
        WHERE search_index MATCH ?
        ORDER BY relevance_score
        LIMIT ? OFFSET ?
        """
        
        # Execute query and convert to SearchResult objects
        # Implementation details...
```

### 5. Search Adapters

#### Entity Search Adapters
```python
class WorkItemSearchAdapter:
    def to_search_content(self, work_item: WorkItem) -> Dict[str, str]:
        return {
            'title': work_item.name,
            'content': f"{work_item.description or ''} {work_item.business_context or ''}",
            'tags': work_item.tags or '',
            'metadata': json.dumps({
                'status': work_item.status.value,
                'type': work_item.type.value,
                'priority': work_item.priority.value if work_item.priority else None
            })
        }

class TaskSearchAdapter:
    def to_search_content(self, task: Task) -> Dict[str, str]:
        return {
            'title': task.name,
            'content': task.description or '',
            'tags': task.tags or '',
            'metadata': json.dumps({
                'status': task.status.value,
                'type': task.type.value,
                'work_item_id': task.work_item_id
            })
        }

class IdeaSearchAdapter:
    def to_search_content(self, idea: Idea) -> Dict[str, str]:
        return {
            'title': idea.title,
            'content': idea.description or '',
            'tags': idea.tags or '',
            'metadata': json.dumps({
                'status': idea.status.value,
                'type': idea.type.value
            })
        }
```

### 6. Migration Strategy

#### Phase 1: Parallel Implementation
1. Create FTS5 virtual tables
2. Implement search service alongside existing search
3. Add feature flags for A/B testing

#### Phase 2: Data Migration
1. Populate FTS5 indexes from existing data
2. Set up synchronization triggers
3. Validate data consistency

#### Phase 3: Cutover
1. Switch search service to use FTS5
2. Monitor performance and accuracy
3. Remove old search implementation

### 7. Performance Optimizations

#### Indexing Strategy
- **Content Index**: Full-text index on title and content
- **Metadata Index**: JSON metadata for filtering
- **Entity Type Index**: Fast filtering by entity type

#### Caching Strategy
- **Query Cache**: Cache frequent search results
- **Metadata Cache**: Cache entity metadata for filtering
- **Result Cache**: Cache formatted results with highlights

#### Query Optimization
- **Query Parsing**: Validate and optimize FTS5 queries
- **Result Limiting**: Implement pagination and result limits
- **Relevance Tuning**: Adjust BM25 parameters for optimal ranking

### 8. Error Handling and Fallbacks

#### FTS5 Unavailable Fallback
```python
class SearchService:
    def __init__(self, db_service: DatabaseService):
        self.fts5_available = self._check_fts5_availability()
        self.fallback_service = LikeSearchService(db_service)
    
    def search(self, query: SearchQuery) -> SearchResults:
        if self.fts5_available:
            return self.fts5_service.search(query)
        else:
            return self.fallback_service.search(query)
```

#### Query Validation
```python
def validate_fts5_query(query_text: str) -> bool:
    """Validate FTS5 query syntax."""
    try:
        # Test query syntax
        test_query = f"SELECT 1 FROM search_index WHERE search_index MATCH '{query_text}' LIMIT 1"
        # Execute test query
        return True
    except Exception:
        return False
```

### 9. Monitoring and Metrics

#### Search Metrics
- Query execution time
- Result count and relevance
- User search patterns
- Error rates and fallback usage

#### Performance Monitoring
- FTS5 index size and growth
- Cache hit rates
- Database query performance
- Memory usage patterns

### 10. Testing Strategy

#### Unit Tests
- Search service functionality
- Query building and parsing
- Result formatting and highlighting
- Error handling and fallbacks

#### Integration Tests
- End-to-end search workflows
- Database trigger functionality
- Cache behavior
- Performance benchmarks

#### Load Tests
- Large dataset performance
- Concurrent search requests
- Memory usage under load
- Cache effectiveness

## Implementation Plan

### Task Breakdown
1. **Create FTS5 Virtual Tables Migration** (Task #704)
2. **Update Search Adapters for FTS5** (Task #705)
3. **Create FTS5 Search Tests** (Task #706)
4. **Document FTS5 Search System** (Task #707)

### Dependencies
- Database migration system
- Existing search service refactoring
- Test framework integration
- Documentation system

### Success Criteria
- 10x+ performance improvement over LIKE queries
- Advanced search features (boolean, phrase, relevance)
- Seamless fallback for unsupported SQLite versions
- Comprehensive test coverage (>90%)
- Complete documentation and user guides

## Risk Mitigation

### Technical Risks
- **FTS5 Unavailable**: Implement LIKE query fallback
- **Performance Issues**: Comprehensive benchmarking and optimization
- **Data Consistency**: Robust trigger system and validation

### Implementation Risks
- **Migration Complexity**: Phased rollout with rollback capability
- **User Experience**: A/B testing and gradual feature rollout
- **Maintenance**: Clear documentation and monitoring

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-20  
**Author**: APM (Agent Project Manager) Development Team  
**Status**: Architecture Design Complete - Ready for Implementation
