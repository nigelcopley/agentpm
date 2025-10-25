# Google Gemini Formatter Implementation

## Overview

The GoogleFormatter class provides context payload formatting optimized for Google Gemini's 32K token context window, following the established Anthropic pattern but with token-efficient optimizations.

## Implementation Details

### Token Budget Optimization

**Context Window**: 32K tokens (vs Anthropic's 200K)
**Allocation Strategy**:
- 55% system context (17.6K tokens)
- 35% user content (11.2K tokens)
- 10% assistant response buffer (3.2K tokens)

### Key Features

1. **Compact Formatting**
   - SOP limited to 400 chars (vs 500 for Anthropic)
   - Temporal context limited to 5 recent sessions
   - Active work items limited to 10 per session
   - Summary text truncated to 200 chars max

2. **6W Context Integration**
   - Hierarchical merge: Task → Work Item → Project
   - Properties extracted from UnifiedSixW dataclass
   - Support for all six dimensions (WHO, WHAT, WHEN, WHERE, WHY, HOW)

3. **Plugin Intelligence**
   - Tech stack rendering with version info
   - Compact bullet format

4. **Error Handling**
   - Graceful degradation for missing data
   - Fallback to payload values when metadata not provided
   - Empty section omission (no warnings if warnings=[])

## Architecture

```
GoogleFormatter (LLMContextFormatter)
├── format_task() - Task-level context formatting
├── format_session() - Session/project-level context
└── Helper Methods
    ├── _format_6w_context() - 6W dimension rendering
    ├── _format_plugin_facts() - Tech stack rendering
    └── _format_temporal_context() - Session history (compact)
```

## Usage

```python
from agentpm.providers.google.formatter import GoogleFormatter
from agentpm.core.context.models import ContextPayload

formatter = GoogleFormatter()

# Format task context
result = formatter.format_task(
    payload=context_payload,
    assembly_duration_ms=125.5,
    warnings=["Context older than 7 days"]
)

# Format session context
result = formatter.format_session(
    history="",
    project={"name": "APM (Agent Project Manager)", "status": "active"},
    active_work=[...]
)
```

## Token Efficiency Features

### Compared to Anthropic Formatter

| Feature | Anthropic | Google | Savings |
|---------|-----------|--------|---------|
| SOP max chars | 500 | 400 | 20% |
| Temporal sessions | ∞ | 5 | Bounded |
| Active work items | ∞ | 10 | Bounded |
| Summary truncation | No | 200 chars | Variable |
| Key decisions | 3 | 2 | 33% |
| Next steps | 3 | 2 | 33% |

## Testing

Comprehensive test suite with 28 tests covering:

- Basic initialization and attributes
- Task formatting (minimal and complete)
- Session formatting
- Helper methods
- Token optimization features
- Edge cases and error handling

**Test Coverage**: 99.42% (173 statements, 1 miss)

## Integration

The formatter is automatically registered with the provider registry:

```python
# agentpm/providers/google/__init__.py
from ..base import register_formatter
register_formatter("google", GoogleFormatter)
```

## UnifiedSixW Integration

The implementation required adding convenience properties to UnifiedSixW dataclass:

- `who` - Combines implementers, reviewers, end_users
- `what` - Functional requirements + acceptance criteria
- `where` - Services, repositories, deployment targets
- `when` - Deadline + dependencies timeline
- `why` - Business value + risk if delayed
- `how` - Suggested approach + existing patterns

These properties provide backward compatibility with the Anthropic formatter pattern while maintaining the structured dataclass approach.

## Future Enhancements

1. **Adaptive Token Budgeting**: Dynamic allocation based on content richness
2. **Gemini-Specific Markdown**: Leverage Gemini's enhanced markdown capabilities
3. **Multilingual Support**: Optimize for non-English contexts
4. **Caching Strategy**: Intelligent context reuse for multi-turn conversations

## References

- **Anthropic Formatter**: `agentpm/providers/anthropic/formatter.py` (reference implementation)
- **Context Models**: `agentpm/core/context/models.py`
- **UnifiedSixW**: `agentpm/core/database/models/context.py`
- **Tests**: `tests/providers/test_google_formatter.py`

## Changelog

**v1.0.0** (2025-01-21)
- Initial implementation following Anthropic pattern
- Token budget optimization for 32K context window
- Comprehensive test suite (28 tests, 99.42% coverage)
- UnifiedSixW property integration
- Provider registry integration
