# Pydantic Types Exposure via CLI

## Overview

APM (Agent Project Manager) now exposes all Pydantic models and enums via CLI commands, enabling AI agents and users to discover valid values without hardcoding. This feature provides comprehensive type information across all command groups.

## Implementation

### Command Structure

Each CLI command group now includes a `types` subcommand that exposes relevant Pydantic models and enums:

```bash
# Document types and formats
apm document types
apm document types --type=document-type
apm document types --type=document-format

# Work item types and statuses  
apm work-item types
apm work-item types --type=work-item-type
apm work-item types --type=phase

# Task types and effort limits
apm task types
apm task types --type=task-type
apm task types --type=effort-limits

# Agent tiers and confidence bands
apm agents types
apm agents types --type=tier
apm agents types --type=confidence-band

# Summary types by entity
apm summary types
apm summary types --entity-type=project
apm summary types --entity-type=work-item
```

### Output Formats

All types commands support multiple output formats:

- **Table** (default): Rich formatted tables with descriptions
- **List**: Simple bullet-point lists
- **JSON**: Machine-readable JSON output

```bash
apm document types --format=table    # Rich tables (default)
apm document types --format=list     # Simple lists
apm document types --format=json     # JSON output
```

## Available Types by Command Group

### Document Types (`apm document types`)

**Document Types** (24 types):
- `idea`, `requirements`, `architecture`, `design`, `specification`
- `api_doc`, `user_guide`, `admin_guide`, `troubleshooting`
- `adr`, `test_plan`, `migration_guide`, `runbook`
- `business_pillars_analysis`, `market_research_report`
- `competitive_analysis`, `quality_gates_specification`
- `stakeholder_analysis`, `technical_specification`
- `implementation_plan`, `other`

**Document Formats** (9 formats):
- `markdown`, `yaml`, `json`, `pdf`, `html`
- `docx`, `xlsx`, `pptx`, `text`, `other`

**Document Statuses** (5 statuses):
- `draft`, `review`, `approved`, `superseded`, `archived`

### Work Item Types (`apm work-item types`)

**Work Item Types** (13 types):
- `feature`, `enhancement`, `bugfix`, `research`, `analysis`
- `planning`, `refactoring`, `infrastructure`, `maintenance`
- `monitoring`, `documentation`, `security`, `fix_bugs_issues`

**Work Item Statuses** (7 statuses):
- `proposed`, `validated`, `accepted`, `in_progress`
- `review`, `completed`, `cancelled`

**Project Types** (4 types):
- `greenfield`, `brownfield`, `maintenance`, `research`

**Project Phases** (6 phases):
- `D1_discovery`, `P1_plan`, `I1_implementation`
- `R1_review`, `O1_operations`, `E1_evolution`

**Development Philosophies** (13 philosophies):
- `kiss_first`, `yagni`, `dry`, `solid`, `behaviour_driven`
- `design_driven`, `test_driven`, `agile`, `professional_standards`
- `context_aware`, `domain_driven`, `data_driven`, `data_aware`

**Project Management Philosophies** (4 philosophies):
- `lean`, `agile`, `pmbok`, `aipm_hybrid`

### Task Types (`apm task types`)

**Task Types** (20 types):
- `design`, `implementation`, `testing`, `bugfix`, `refactoring`
- `documentation`, `deployment`, `review`, `analysis`, `research`
- `maintenance`, `optimization`, `integration`, `training`
- `meeting`, `planning`, `dependency`, `blocker`, `simple`, `other`

**Task Statuses** (7 statuses):
- `proposed`, `validated`, `accepted`, `in_progress`
- `review`, `completed`, `cancelled`

**Enforcement Levels** (4 levels):
- `BLOCK`, `LIMIT`, `GUIDE`, `ENHANCE`

**Effort Limits** (20 task types with time limits):
- `implementation`: 4h (STRICT)
- `design`: 8h
- `testing`: 6h
- `documentation`: 6h
- `bugfix`: 4h
- `refactoring`: 6h
- `deployment`: 8h
- `review`: 4h
- `analysis`: 6h
- `research`: 8h
- `maintenance`: 4h
- `optimization`: 6h
- `integration`: 8h
- `training`: 4h
- `meeting`: 2h
- `planning`: 6h
- `dependency`: 2h
- `blocker`: 4h
- `simple`: 1h
- `other`: 4h

### Agent Types (`apm agents types`)

**Agent Tiers** (3 tiers):
- `TIER_1`: Universal specialists (work on any project)
- `TIER_2`: Tech stack specialists (language/framework specific)
- `TIER_3`: Domain specialists (business domain specific)

**Confidence Bands** (3 bands):
- `RED`: < 0.5 - Insufficient context, agent cannot operate
- `YELLOW`: 0.5 - 0.8 - Adequate context, agent can operate with limitations
- `GREEN`: > 0.8 - High-quality context, agent fully enabled

### Summary Types (`apm summary types`)

**Summary Types by Entity**:

**Project-level** (4 types):
- `project_milestone`, `project_retrospective`
- `project_status_report`, `project_strategic_review`

**Work Item-level** (4 types):
- `work_item_progress`, `work_item_milestone`
- `work_item_decision`, `work_item_retrospective`

**Task-level** (4 types):
- `task_completion`, `task_progress`
- `task_blocker_resolution`, `task_technical_notes`

**Session-level** (4 types):
- `session_handover`, `session_progress`
- `session_error_analysis`, `session_decision_log`

**Entity Types** (4 types):
- `project`, `work_item`, `task`, `idea`

## Benefits

### For AI Agents

1. **Dynamic Discovery**: Agents can discover valid values without hardcoding
2. **Validation Help**: Clear error messages with valid options
3. **Context Awareness**: Agents understand available types for each command
4. **Consistency**: Ensures CLI and models stay in sync

### For Users

1. **Interactive Discovery**: Users can explore available options
2. **Documentation**: Self-documenting CLI with type information
3. **Validation**: Clear understanding of valid values
4. **Help System**: Integrated help for all type-related commands

### For Development

1. **Type Safety**: Ensures CLI commands use valid enum values
2. **Maintainability**: Single source of truth for all types
3. **Extensibility**: Easy to add new types and commands
4. **Testing**: Comprehensive type validation

## Usage Examples

### AI Agent Usage

```python
# Agent discovers valid work item types
import subprocess
result = subprocess.run(['apm', 'work-item', 'types', '--type=work-item-type', '--format=json'], 
                       capture_output=True, text=True)
work_item_types = json.loads(result.stdout)['work_item_types']

# Agent uses discovered types
for work_item_type in work_item_types:
    if 'feature' in work_item_type['value']:
        # Use feature type for new functionality
        pass
```

### User Discovery

```bash
# Discover available document types
apm document types --type=document-type

# Check effort limits for tasks
apm task types --type=effort-limits

# See summary types for work items
apm summary types --entity-type=work-item

# Get all agent information
apm agents types
```

### Validation Help

```bash
# When creating a work item, see valid types
apm work-item types --type=work-item-type

# When creating a task, see effort limits
apm task types --type=effort-limits

# When creating a document, see valid formats
apm document types --type=document-format
```

## Implementation Details

### File Structure

```
agentpm/cli/commands/
├── document/types.py      # Document types command
├── work_item/types.py     # Work item types command
├── task/types.py          # Task types command
├── agents/types.py        # Agent types command
└── summary/types.py       # Summary types command
```

### Command Registration

Each command group registers the types command:

```python
# In __init__.py files
from .types import types
command_group.add_command(types)
```

### Rich Output

All commands use Rich formatting for beautiful, consistent output:

- **Tables**: Formatted tables with headers and styling
- **Panels**: Grouped information with clear titles
- **Colors**: Consistent color scheme across all commands
- **Emojis**: Visual indicators for different command groups

### Error Handling

Commands include comprehensive error handling:

- **Invalid Types**: Clear error messages with valid options
- **Missing Enums**: Graceful fallback for missing enum values
- **Import Errors**: Proper error handling for missing dependencies

## Future Enhancements

### Additional Command Groups

- `idea types` - Idea-related types and statuses
- `context types` - Context types and confidence bands
- `session types` - Session types and statuses
- `rules types` - Rule types and enforcement levels

### Enhanced Features

- **Interactive Mode**: Interactive type selection
- **Validation**: Real-time validation of type values
- **Search**: Search within types and descriptions
- **Export**: Export types to various formats
- **Integration**: Integration with IDE autocomplete

### Performance Optimizations

- **Caching**: Cache type information for faster access
- **Lazy Loading**: Load types only when needed
- **Compression**: Compress large type lists
- **Indexing**: Index types for faster searching

## Conclusion

The Pydantic types exposure via CLI provides a comprehensive, user-friendly way to discover and validate all type information in APM (Agent Project Manager). This feature significantly enhances the developer experience and enables AI agents to work more effectively with the system.

The implementation follows APM (Agent Project Manager)'s principles of:
- **Agent Enablement**: Clear, structured outputs for AI agents
- **User Experience**: Intuitive, discoverable interface
- **Type Safety**: Comprehensive validation and error handling
- **Maintainability**: Single source of truth for all types
- **Extensibility**: Easy to add new types and commands

