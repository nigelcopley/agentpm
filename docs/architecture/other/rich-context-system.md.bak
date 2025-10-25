# Rich Context System Documentation

## Overview

The Rich Context System in APM (Agent Project Manager) provides comprehensive contextual information for work items, tasks, and ideas. This system extends the basic context functionality with rich, structured data that enables AI agents to operate more effectively with deeper understanding of project context.

## Architecture

### Core Components

1. **Context Model Extensions**: Enhanced `Context` model with `context_data` field
2. **Rich Context Types**: New context types for different aspects of project context
3. **Context Assembly Service**: Service for assembling hierarchical context
4. **Database Methods**: CRUD operations for rich context data
5. **CLI Commands**: User interface for rich context operations

### Data Flow

```
Idea → Work Item → Task
  ↓        ↓        ↓
Rich Context Assembly
  ↓
Context Data Storage
  ↓
Agent Context Delivery
```

## Rich Context Types

### Business Pillars Context
Stores business analysis, stakeholder information, and strategic context.

```json
{
  "analysis": "Business analysis content",
  "stakeholders": ["CEO", "CTO", "Product Manager"],
  "priority": "high",
  "business_value": "Revenue impact analysis",
  "risks": ["Technical risk", "Market risk"]
}
```

### Market Research Context
Contains market analysis, competitive intelligence, and customer insights.

```json
{
  "market_size": "£10M TAM",
  "competitors": ["Competitor A", "Competitor B"],
  "customer_segments": ["Enterprise", "SMB"],
  "trends": ["AI adoption", "Cloud migration"],
  "opportunities": ["Feature gap", "Pricing advantage"]
}
```

### Competitive Analysis Context
Stores competitive positioning and differentiation analysis.

```json
{
  "competitive_landscape": "Market analysis",
  "differentiation": "Unique value proposition",
  "strengths": ["Technical advantage", "Team expertise"],
  "weaknesses": ["Market presence", "Brand recognition"],
  "threats": ["New entrants", "Technology disruption"]
}
```

### Quality Gates Context
Contains quality requirements, testing criteria, and compliance information.

```json
{
  "quality_requirements": ["Performance", "Security", "Usability"],
  "testing_criteria": ["Unit tests-BAK", "Integration tests-BAK", "E2E tests-BAK"],
  "compliance": ["GDPR", "SOC2", "ISO27001"],
  "acceptance_criteria": ["Feature complete", "Performance targets met"]
}
```

### Stakeholder Context
Stores stakeholder information, communication preferences, and influence mapping.

```json
{
  "stakeholders": [
    {
      "name": "John Doe",
      "role": "Product Manager",
      "influence": "high",
      "interest": "high",
      "communication_preference": "email"
    }
  ],
  "communication_plan": "Weekly updates via email",
  "decision_makers": ["John Doe", "Jane Smith"]
}
```

### Technical Context
Contains technical specifications, architecture decisions, and implementation details.

```json
{
  "architecture": "Microservices architecture",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "dependencies": ["External API", "Database"],
  "performance_requirements": ["<100ms response time", "99.9% uptime"],
  "security_requirements": ["Authentication", "Authorization", "Encryption"]
}
```

### Implementation Context
Stores implementation details, code patterns, and development guidelines.

```json
{
  "implementation_approach": "Test-driven development",
  "code_patterns": ["Repository pattern", "Factory pattern"],
  "development_guidelines": ["Code review required", "Unit tests-BAK required"],
  "deployment_strategy": "Blue-green deployment",
  "monitoring": ["Application metrics", "Error tracking"]
}
```

### Idea Context
Contains idea-specific context including business case, feasibility analysis, and implementation planning.

```json
{
  "business_case": "Revenue opportunity analysis",
  "feasibility": "High technical feasibility",
  "implementation_plan": "3-month development timeline",
  "success_metrics": ["User adoption", "Revenue impact"],
  "assumptions": ["Market demand exists", "Technical resources available"]
}
```

## Context Assembly

### Hierarchical Context Assembly

The system assembles context hierarchically from Project → Work Item → Task:

```python
# Example context assembly
context = assembly_service.assemble_rich_context(
    entity_type=EntityType.TASK,
    entity_id=task_id,
    context_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT,
        ContextType.QUALITY_GATES_CONTEXT
    ]
)
```

### Context Inheritance

Context data flows down the hierarchy:
- **Project Context**: Applies to all work items and tasks
- **Work Item Context**: Applies to all tasks within the work item
- **Task Context**: Specific to the individual task

### Context Merging

When multiple contexts exist at different levels, they are merged with task-level context taking precedence:

```python
merged_context = {
    "project": project_context,
    "work_item": work_item_context,
    "task": task_context,
    "merged": merge_contexts(project_context, work_item_context, task_context)
}
```

## Database Schema

### Contexts Table Extensions

The `contexts` table has been extended with:

```sql
-- New context types
context_type TEXT CHECK(context_type IN (
    'resource_file', 'project_context', 'work_item_context', 'task_context',
    'business_pillars_context', 'market_research_context', 
    'competitive_analysis_context', 'quality_gates_context',
    'stakeholder_context', 'technical_context', 'implementation_context',
    'idea_context', 'idea_to_work_item_mapping'
))

-- New entity type
entity_type TEXT CHECK(entity_type IN ('project', 'work_item', 'task', 'idea'))

-- Rich context data storage
context_data TEXT  -- JSON: rich context data
```

### Context Data Storage

Rich context data is stored as JSON in the `context_data` field:

```python
context = Context(
    project_id=1,
    context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
    entity_type=EntityType.WORK_ITEM,
    entity_id=123,
    context_data=json.dumps({
        "analysis": "Business analysis",
        "stakeholders": ["CEO", "CTO"],
        "priority": "high"
    })
)
```

## API Reference

### Context Assembly Service

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
        Dictionary containing assembled context data
    """
```

#### `assemble_hierarchical_rich_context()`

Assembles hierarchical context from project down to task.

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
        Dictionary with hierarchical context structure
    """
```

### Database Methods

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
        entity_type: Type of entity
        entity_id: ID of the entity
        context_type: Type of context
        context_data: Rich context data
    
    Returns:
        Created Context object
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
        List of Context objects
    """
```

## CLI Commands

### Rich Context Commands

#### `apm context rich create`

Create a new rich context entry.

```bash
apm context rich create \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --data '{"analysis": "Business analysis", "stakeholders": ["CEO"]}'
```

#### `apm context rich list`

List rich contexts for an entity.

```bash
apm context rich list --entity-type work_item --entity-id 123
```

#### `apm context rich assemble`

Assemble rich context for an entity.

```bash
apm context rich assemble --entity-type task --entity-id 456
```

#### `apm context rich validate`

Validate rich context completeness.

```bash
apm context rich validate --entity-type work_item --entity-id 123
```

#### `apm context rich generate-docs`

Generate documents from rich context.

```bash
apm context rich generate-docs \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --document-type business_pillars_analysis
```

## Usage Examples

### Creating Rich Context

```python
from agentpm.core.database.methods import contexts as context_methods
from agentpm.core.database.enums import EntityType, ContextType

# Create business pillars context
context_data = {
    "analysis": "This feature will increase user engagement by 25%",
    "stakeholders": ["Product Manager", "Engineering Lead"],
    "priority": "high",
    "business_value": "£50K additional revenue per quarter"
}

context = context_methods.create_rich_context(
    service=db_service,
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item_id,
    context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
    context_data=context_data
)
```

### Assembling Context for AI Agents

```python
from agentpm.core.context.assembly_service import ContextAssemblyService

# Create assembly service
assembly_service = ContextAssemblyService(db_service, project_path)

# Assemble rich context for a task
rich_context = assembly_service.assemble_rich_context(
    entity_type=EntityType.TASK,
    entity_id=task_id,
    context_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT,
        ContextType.QUALITY_GATES_CONTEXT
    ]
)

# Use context for AI agent
agent_context = {
    "task": task_data,
    "business_context": rich_context.get("business_pillars_context", {}),
    "technical_context": rich_context.get("technical_context", {}),
    "quality_requirements": rich_context.get("quality_gates_context", {})
}
```

### Ideas Integration

```python
# Create idea with rich context
idea_context = {
    "business_case": "Addresses customer pain point",
    "feasibility": "High - existing technology stack",
    "implementation_plan": "2-week development cycle",
    "success_metrics": ["User adoption", "Performance improvement"]
}

context_methods.create_rich_context(
    service=db_service,
    entity_type=EntityType.IDEA,
    entity_id=idea_id,
    context_type=ContextType.IDEA_CONTEXT,
    context_data=idea_context
)

# Convert idea to work item with context transfer
work_item = idea_methods.convert_idea_to_work_item(
    service=db_service,
    idea_id=idea_id,
    transfer_context=True
)
```

## Best Practices

### Context Data Structure

1. **Consistent Schema**: Use consistent field names across context types
2. **Structured Data**: Store data in structured format (arrays, objects)
3. **Validation**: Validate context data before storage
4. **Versioning**: Consider versioning for context data evolution

### Context Assembly

1. **Selective Assembly**: Only assemble needed context types for performance
2. **Caching**: Cache assembled context for frequently accessed entities
3. **Hierarchical Merging**: Use hierarchical merging for comprehensive context
4. **Error Handling**: Handle missing context gracefully

### Performance Considerations

1. **Lazy Loading**: Load context data only when needed
2. **Batch Operations**: Use batch operations for multiple context operations
3. **Indexing**: Ensure proper database indexing for context queries
4. **Cleanup**: Regularly clean up unused context data

## Migration Guide

### From Basic Context to Rich Context

1. **Identify Context Types**: Determine which rich context types are needed
2. **Migrate Existing Data**: Convert existing context data to rich format
3. **Update Code**: Update code to use rich context assembly
4. **Test Thoroughly**: Test context assembly and data integrity

### Database Migration

The system includes migration 0017 that adds the `context_data` column:

```sql
ALTER TABLE contexts ADD COLUMN context_data TEXT;
```

## Troubleshooting

### Common Issues

1. **Missing Context Data**: Check if context was created with correct entity type/ID
2. **Context Assembly Errors**: Verify context types are valid and entity exists
3. **Performance Issues**: Consider caching and selective context assembly
4. **Data Validation Errors**: Ensure context data matches expected schema

### Debug Commands

```bash
# Check context data
apm context rich list --entity-type work_item --entity-id 123

# Validate context completeness
apm context rich validate --entity-type work_item --entity-id 123

# Assemble context with debug info
apm context rich assemble --entity-type task --entity-id 456 --verbose
```

## Future Enhancements

1. **Context Templates**: Predefined context templates for common scenarios
2. **Context Analytics**: Analytics on context usage and effectiveness
3. **Context Recommendations**: AI-powered context suggestions
4. **Context Versioning**: Version control for context data evolution
5. **Context Sharing**: Share context between projects and teams
