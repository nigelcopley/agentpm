# Rich Context System API Documentation

## Overview

This document provides comprehensive API documentation for the Rich Context System in APM (Agent Project Manager). The API includes database methods, service interfaces, and CLI commands for managing rich context data.

## Database Models

### Context Model

The `Context` model represents a context entry in the system.

```python
class Context(BaseModel):
    id: Optional[int] = None
    project_id: int
    context_type: ContextType
    entity_type: Optional[EntityType] = None
    entity_id: Optional[int] = None
    six_w_data: Optional[str] = None
    confidence_score: Optional[float] = None
    confidence_band: Optional[str] = None
    confidence_factors: Optional[str] = None
    context_data: Optional[str] = None
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    resource_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Enums

#### ContextType

```python
class ContextType(str, Enum):
    # Legacy context types
    RESOURCE_FILE = "resource_file"
    PROJECT_CONTEXT = "project_context"
    WORK_ITEM_CONTEXT = "work_item_context"
    TASK_CONTEXT = "task_context"
    
    # Rich context types
    BUSINESS_PILLARS_CONTEXT = "business_pillars_context"
    MARKET_RESEARCH_CONTEXT = "market_research_context"
    COMPETITIVE_ANALYSIS_CONTEXT = "competitive_analysis_context"
    QUALITY_GATES_CONTEXT = "quality_gates_context"
    STAKEHOLDER_CONTEXT = "stakeholder_context"
    TECHNICAL_CONTEXT = "technical_context"
    IMPLEMENTATION_CONTEXT = "implementation_context"
    IDEA_CONTEXT = "idea_context"
    IDEA_TO_WORK_ITEM_MAPPING = "idea_to_work_item_mapping"
```

#### EntityType

```python
class EntityType(str, Enum):
    PROJECT = "project"
    WORK_ITEM = "work_item"
    TASK = "task"
    IDEA = "idea"
```

#### DocumentType

```python
class DocumentType(str, Enum):
    # Legacy document types
    BUSINESS_PILLARS_ANALYSIS = "business_pillars_analysis"
    MARKET_RESEARCH_REPORT = "market_research_report"
    COMPETITIVE_ANALYSIS_REPORT = "competitive_analysis_report"
    QUALITY_GATES_REPORT = "quality_gates_report"
    STAKEHOLDER_ANALYSIS = "stakeholder_analysis"
    TECHNICAL_SPECIFICATION = "technical_specification"
    IMPLEMENTATION_GUIDE = "implementation_guide"
    IDEA_ANALYSIS = "idea_analysis"
```

## Database Methods

### Context Methods

#### `create_rich_context()`

Creates a new rich context entry.

```python
def create_rich_context(
    service: DatabaseService,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType,
    context_data: Dict[str, Any]
) -> Context:
    """
    Create a new rich context entry.
    
    Args:
        service: Database service instance
        entity_type: Type of entity (PROJECT, WORK_ITEM, TASK, IDEA)
        entity_id: ID of the entity
        context_type: Type of context to create
        context_data: Rich context data as dictionary
    
    Returns:
        Created Context object
    
    Raises:
        ValidationError: If entity doesn't exist or validation fails
        DatabaseError: If database operation fails
    
    Example:
        context = create_rich_context(
            service=db,
            entity_type=EntityType.WORK_ITEM,
            entity_id=123,
            context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
            context_data={
                "analysis": "Business analysis",
                "stakeholders": ["CEO", "CTO"],
                "priority": "high"
            }
        )
    """
```

#### `get_rich_contexts_by_entity()`

Retrieves all rich contexts for an entity.

```python
def get_rich_contexts_by_entity(
    service: DatabaseService,
    entity_type: EntityType,
    entity_id: int
) -> List[Context]:
    """
    Get all rich contexts for an entity.
    
    Args:
        service: Database service instance
        entity_type: Type of entity
        entity_id: ID of the entity
    
    Returns:
        List of Context objects for the entity
    
    Example:
        contexts = get_rich_contexts_by_entity(
            service=db,
            entity_type=EntityType.WORK_ITEM,
            entity_id=123
        )
    """
```

#### `validate_rich_context_completeness()`

Validates that an entity has complete rich context.

```python
def validate_rich_context_completeness(
    service: DatabaseService,
    entity_type: EntityType,
    entity_id: int,
    required_types: Optional[List[ContextType]] = None
) -> Dict[str, Any]:
    """
    Validate rich context completeness for an entity.
    
    Args:
        service: Database service instance
        entity_type: Type of entity
        entity_id: ID of the entity
        required_types: List of required context types (optional)
    
    Returns:
        Dictionary with validation results:
        {
            "is_complete": bool,
            "missing_types": List[ContextType],
            "present_types": List[ContextType],
            "completeness_score": float
        }
    
    Example:
        result = validate_rich_context_completeness(
            service=db,
            entity_type=EntityType.WORK_ITEM,
            entity_id=123,
            required_types=[
                ContextType.BUSINESS_PILLARS_CONTEXT,
                ContextType.TECHNICAL_CONTEXT
            ]
        )
    """
```

#### `merge_rich_contexts_hierarchically()`

Merges rich contexts from project down to entity.

```python
def merge_rich_contexts_hierarchically(
    service: DatabaseService,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType
) -> Dict[str, Any]:
    """
    Merge rich contexts hierarchically from project to entity.
    
    Args:
        service: Database service instance
        entity_type: Type of entity
        entity_id: ID of the entity
        context_type: Type of context to merge
    
    Returns:
        Dictionary with merged context data:
        {
            "project": Dict[str, Any],
            "work_item": Dict[str, Any],
            "task": Dict[str, Any],
            "merged": Dict[str, Any]
        }
    
    Example:
        merged = merge_rich_contexts_hierarchically(
            service=db,
            entity_type=EntityType.TASK,
            entity_id=456,
            context_type=ContextType.BUSINESS_PILLARS_CONTEXT
        )
    """
```

#### `generate_documents_from_rich_context()`

Generates documents from rich context data.

```python
def generate_documents_from_rich_context(
    service: DatabaseService,
    entity_type: EntityType,
    entity_id: int,
    context_type: ContextType,
    document_type: DocumentType
) -> Dict[str, Any]:
    """
    Generate documents from rich context data.
    
    Args:
        service: Database service instance
        entity_type: Type of entity
        entity_id: ID of the entity
        context_type: Type of context to use
        document_type: Type of document to generate
    
    Returns:
        Dictionary with generated document:
        {
            "success": bool,
            "document_type": str,
            "content": str,
            "metadata": Dict[str, Any]
        }
    
    Example:
        doc = generate_documents_from_rich_context(
            service=db,
            entity_type=EntityType.WORK_ITEM,
            entity_id=123,
            context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
            document_type=DocumentType.BUSINESS_PILLARS_ANALYSIS
        )
    """
```

## Context Assembly Service

### `ContextAssemblyService`

The main service for assembling rich context.

```python
class ContextAssemblyService:
    def __init__(self, db_service: DatabaseService, project_path: Path):
        """
        Initialize context assembly service.
        
        Args:
            db_service: Database service instance
            project_path: Path to the project
        """
```

#### `assemble_rich_context()`

Assembles rich context for an entity.

```python
def assemble_rich_context(
    self,
    entity_type: EntityType,
    entity_id: int,
    context_types: Optional[List[ContextType]] = None
) -> Dict[str, Any]:
    """
    Assemble rich context for an entity.
    
    Args:
        entity_type: Type of entity (PROJECT, WORK_ITEM, TASK, IDEA)
        entity_id: ID of the entity
        context_types: List of context types to assemble (optional)
    
    Returns:
        Dictionary containing assembled context data:
        {
            "entity_type": str,
            "entity_id": int,
            "contexts": {
                "business_pillars_context": Dict[str, Any],
                "technical_context": Dict[str, Any],
                ...
            },
            "completeness": {
                "score": float,
                "missing_types": List[str],
                "present_types": List[str]
            }
        }
    
    Example:
        assembly_service = ContextAssemblyService(db, project_path)
        context = assembly_service.assemble_rich_context(
            entity_type=EntityType.TASK,
            entity_id=456,
            context_types=[
                ContextType.BUSINESS_PILLARS_CONTEXT,
                ContextType.TECHNICAL_CONTEXT
            ]
        )
    """
```

#### `assemble_hierarchical_rich_context()`

Assembles hierarchical context from project down to entity.

```python
def assemble_hierarchical_rich_context(
    self,
    entity_type: EntityType,
    entity_id: int
) -> Dict[str, Any]:
    """
    Assemble hierarchical context from project to entity.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
    
    Returns:
        Dictionary with hierarchical context structure:
        {
            "project": {
                "id": int,
                "contexts": Dict[str, Any]
            },
            "work_item": {
                "id": int,
                "contexts": Dict[str, Any]
            },
            "task": {
                "id": int,
                "contexts": Dict[str, Any]
            },
            "hierarchical_merge": Dict[str, Any]
        }
    
    Example:
        hierarchical = assembly_service.assemble_hierarchical_rich_context(
            entity_type=EntityType.TASK,
            entity_id=456
        )
    """
```

#### `assemble_document_driven_context()`

Assembles context from associated documents.

```python
def assemble_document_driven_context(
    self,
    entity_type: EntityType,
    entity_id: int
) -> Dict[str, Any]:
    """
    Assemble context from associated documents.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
    
    Returns:
        Dictionary with document-driven context:
        {
            "documents": List[Dict[str, Any]],
            "extracted_context": Dict[str, Any],
            "confidence_score": float
        }
    
    Example:
        doc_context = assembly_service.assemble_document_driven_context(
            entity_type=EntityType.WORK_ITEM,
            entity_id=123
        )
    """
```

## CLI Commands

### Rich Context Commands

#### `apm context rich create`

Create a new rich context entry.

```bash
apm context rich create [OPTIONS]

Options:
  --entity-type [project|work_item|task|idea]  Type of entity
  --entity-id INTEGER                          ID of the entity
  --context-type TEXT                          Type of context
  --data TEXT                                  Context data as JSON string
  --file PATH                                  Path to JSON file with context data
  --help                                       Show help message
```

**Examples:**

```bash
# Create business context from JSON string
apm context rich create \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --data '{"analysis": "Business analysis", "stakeholders": ["CEO"]}'

# Create context from file
apm context rich create \
  --entity-type task \
  --entity-id 456 \
  --context-type technical_context \
  --file context-data.json
```

#### `apm context rich list`

List rich contexts for an entity.

```bash
apm context rich list [OPTIONS]

Options:
  --entity-type [project|work_item|task|idea]  Type of entity
  --entity-id INTEGER                          ID of the entity
  --context-type TEXT                          Filter by context type
  --format [table|json|yaml]                   Output format
  --help                                       Show help message
```

**Examples:**

```bash
# List all contexts for work item
apm context rich list --entity-type work_item --entity-id 123

# List specific context type
apm context rich list \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context

# Output as JSON
apm context rich list \
  --entity-type task \
  --entity-id 456 \
  --format json
```

#### `apm context rich assemble`

Assemble rich context for an entity.

```bash
apm context rich assemble [OPTIONS]

Options:
  --entity-type [project|work_item|task|idea]  Type of entity
  --entity-id INTEGER                          ID of the entity
  --context-types TEXT                         Comma-separated context types
  --hierarchical                               Assemble hierarchical context
  --format [table|json|yaml]                   Output format
  --help                                       Show help message
```

**Examples:**

```bash
# Assemble all context types
apm context rich assemble --entity-type task --entity-id 456

# Assemble specific context types
apm context rich assemble \
  --entity-type work_item \
  --entity-id 123 \
  --context-types business_pillars_context,technical_context

# Assemble hierarchical context
apm context rich assemble \
  --entity-type task \
  --entity-id 456 \
  --hierarchical
```

#### `apm context rich validate`

Validate rich context completeness.

```bash
apm context rich validate [OPTIONS]

Options:
  --entity-type [project|work_item|task|idea]  Type of entity
  --entity-id INTEGER                          ID of the entity
  --required-types TEXT                        Comma-separated required types
  --format [table|json|yaml]                   Output format
  --help                                       Show help message
```

**Examples:**

```bash
# Validate context completeness
apm context rich validate --entity-type work_item --entity-id 123

# Validate with required types
apm context rich validate \
  --entity-type work_item \
  --entity-id 123 \
  --required-types business_pillars_context,technical_context
```

#### `apm context rich generate-docs`

Generate documents from rich context.

```bash
apm context rich generate-docs [OPTIONS]

Options:
  --entity-type [project|work_item|task|idea]  Type of entity
  --entity-id INTEGER                          ID of the entity
  --context-type TEXT                          Type of context to use
  --document-type TEXT                         Type of document to generate
  --output PATH                                Output file path
  --format [markdown|html|pdf]                 Document format
  --help                                       Show help message
```

**Examples:**

```bash
# Generate business analysis document
apm context rich generate-docs \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --document-type business_pillars_analysis

# Generate document to file
apm context rich generate-docs \
  --entity-type work_item \
  --entity-id 123 \
  --context-type technical_context \
  --document-type technical_specification \
  --output tech-spec.md
```

## Error Handling

### Common Exceptions

#### `ValidationError`

Raised when validation fails.

```python
class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
```

**Common causes:**
- Entity doesn't exist
- Invalid context type
- Invalid entity type
- Malformed context data

#### `DatabaseError`

Raised when database operations fail.

```python
class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
```

**Common causes:**
- Database connection issues
- Constraint violations
- Transaction failures

### Error Response Format

CLI commands return structured error responses:

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ValidationError",
  "details": {
    "entity_type": "work_item",
    "entity_id": 123,
    "context_type": "business_pillars_context"
  }
}
```

## Data Validation

### Context Data Schema

Each context type has a recommended schema:

#### Business Pillars Context

```json
{
  "analysis": "string (required)",
  "stakeholders": ["string"],
  "priority": "string (high|medium|low)",
  "business_value": "string",
  "risks": ["string"],
  "success_metrics": ["string"]
}
```

#### Technical Context

```json
{
  "architecture": "string",
  "tech_stack": ["string"],
  "dependencies": ["string"],
  "performance_requirements": ["string"],
  "security_requirements": ["string"],
  "scalability_considerations": ["string"]
}
```

#### Quality Gates Context

```json
{
  "quality_requirements": ["string"],
  "testing_criteria": ["string"],
  "compliance": ["string"],
  "acceptance_criteria": ["string"],
  "review_process": "string"
}
```

### Validation Rules

1. **Required Fields**: Each context type has required fields
2. **Data Types**: Fields must match expected data types
3. **Enum Values**: Enum fields must use valid values
4. **JSON Format**: Context data must be valid JSON
5. **Entity Existence**: Referenced entities must exist

## Performance Considerations

### Optimization Tips

1. **Batch Operations**: Use batch operations for multiple contexts
2. **Selective Assembly**: Only assemble needed context types
3. **Caching**: Cache assembled context for repeated access
4. **Indexing**: Ensure proper database indexing

### Performance Metrics

- **Context Creation**: < 100ms per context
- **Context Assembly**: < 500ms for typical entity
- **Context Validation**: < 200ms per entity
- **Document Generation**: < 1s per document

## Security Considerations

### Data Protection

1. **Input Validation**: All input is validated before storage
2. **SQL Injection**: Parameterized queries prevent SQL injection
3. **Access Control**: Context access follows entity permissions
4. **Data Sanitization**: Output is sanitized for display

### Privacy

1. **Sensitive Data**: Avoid storing sensitive information in context
2. **Data Retention**: Implement data retention policies
3. **Audit Trail**: Track context modifications
4. **Encryption**: Consider encryption for sensitive context data

## Migration and Compatibility

### Database Migrations

The system includes migration 0017 for rich context support:

```sql
-- Add context_data column
ALTER TABLE contexts ADD COLUMN context_data TEXT;

-- Update CHECK constraints
-- (Handled by schema updates)
```

### Backward Compatibility

- Existing context entries continue to work
- New context types are additive
- Legacy context types remain supported
- API changes are backward compatible

## Testing

### Unit Tests

```python
def test_create_rich_context():
    """Test creating rich context entry."""
    context = create_rich_context(
        service=db,
        entity_type=EntityType.WORK_ITEM,
        entity_id=123,
        context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
        context_data={"analysis": "Test analysis"}
    )
    assert context.id is not None
    assert context.context_type == ContextType.BUSINESS_PILLARS_CONTEXT
```

### Integration Tests

```python
def test_context_assembly_integration():
    """Test context assembly integration."""
    assembly_service = ContextAssemblyService(db, project_path)
    context = assembly_service.assemble_rich_context(
        entity_type=EntityType.TASK,
        entity_id=456
    )
    assert "contexts" in context
    assert "completeness" in context
```

### CLI Tests

```python
def test_cli_create_context():
    """Test CLI context creation."""
    result = runner.invoke(cli, [
        "context", "rich", "create",
        "--entity-type", "work_item",
        "--entity-id", "123",
        "--context-type", "business_pillars_context",
        "--data", '{"analysis": "Test"}'
    ])
    assert result.exit_code == 0
```

## Examples

### Complete Workflow Example

```python
from agentpm.core.database.methods import contexts as context_methods
from agentpm.core.context.assembly_service import ContextAssemblyService
from agentpm.core.database.enums import EntityType, ContextType

# 1. Create business context
business_context = context_methods.create_rich_context(
    service=db,
    entity_type=EntityType.WORK_ITEM,
    entity_id=123,
    context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
    context_data={
        "analysis": "This feature will improve user engagement",
        "stakeholders": ["Product Manager", "Engineering Lead"],
        "priority": "high",
        "business_value": "Expected 25% increase in user retention"
    }
)

# 2. Create technical context
technical_context = context_methods.create_rich_context(
    service=db,
    entity_type=EntityType.WORK_ITEM,
    entity_id=123,
    context_type=ContextType.TECHNICAL_CONTEXT,
    context_data={
        "architecture": "Microservices with API gateway",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "dependencies": ["Authentication service", "Notification service"],
        "performance_requirements": ["<200ms API response", "99.9% uptime"]
    }
)

# 3. Assemble complete context
assembly_service = ContextAssemblyService(db, project_path)
complete_context = assembly_service.assemble_rich_context(
    entity_type=EntityType.WORK_ITEM,
    entity_id=123,
    context_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT
    ]
)

# 4. Validate context completeness
validation_result = context_methods.validate_rich_context_completeness(
    service=db,
    entity_type=EntityType.WORK_ITEM,
    entity_id=123,
    required_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT
    ]
)

print(f"Context completeness: {validation_result['completeness_score']:.2f}")
print(f"Missing types: {validation_result['missing_types']}")
```

This API documentation provides comprehensive coverage of the Rich Context System, including all methods, commands, and usage examples. Use this as a reference for implementing rich context functionality in your applications.


