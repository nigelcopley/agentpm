# Deprecated Claude Code Orchestrator Components

**Date Deprecated**: 2025-10-27
**Replaced By**: `ClaudeCodeGenerator` + `AgentGeneratorService` (template-based architecture)

## Why These Files Were Deprecated

These files implemented a complex manager-based architecture for generating Claude Code integration files:

- `plugins.py` (718 LOC) - 12 template methods for plugin generation
- `hooks.py` (679 LOC) - 10 template methods for hook generation
- `subagents.py` (1,135 LOC) - 18 template methods for subagent generation
- `settings.py` (694 LOC) - 8 template methods for settings generation
- `slash_commands.py` (1,565 LOC) - 28 template methods for slash command generation
- `checkpointing.py` (923 LOC) - 10 template methods for checkpoint generation
- `memory_tool.py` (867 LOC) - 8 template methods for memory tool generation

**Total**: 7 files, 6,581 LOC, 94 template methods

This architecture had several issues:

1. **Duplication**: Each manager duplicated template rendering logic
2. **Maintainability**: Changes required updates across multiple files
3. **Testing complexity**: 94 template methods required extensive test coverage
4. **No extensibility**: Hard to add new providers (Cursor, Codex, etc.)

## Replacement Architecture

The new template-based generator system provides:

1. **Single Generator Class**: `ClaudeCodeGenerator` (~200 LOC)
2. **Jinja2 Templates**: Separate templates for each component type
3. **Provider Registry**: Extensible architecture for multiple providers
4. **Service Layer**: `AgentGeneratorService` wraps generator with DB access

**Benefits**:
- 80% code reduction (6,581 → ~1,500 LOC)
- Centralized template management
- Easy to add new providers
- Simpler testing (template files + generator logic)
- Better separation of concerns

## Migration Path

If you need to use these deprecated managers:

```python
# OLD (deprecated)
from agentpm.providers.anthropic.claude_code import ClaudeCodeOrchestrator
orchestrator = ClaudeCodeOrchestrator(db_service)
integration = orchestrator.create_comprehensive_integration(output_dir)

# NEW (recommended)
from agentpm.core.services.agent_generator import AgentGeneratorService
generator = AgentGeneratorService(db_service, project_path)
summary = generator.generate_all()
```

## Do NOT Delete These Files

These files are kept for reference and backward compatibility during the transition period. They will be permanently removed in a future major version.

See: Work Item #165, Task #1098
