"""
Claude Code Provider

Unified provider for Claude Code integration in APM (Agent Project Manager).

Architecture:
- generation/: Template generation (skills, memory, configs)
- runtime/: Orchestration (sessions, hooks, plugins)

Use template-based generator:

```python
from agentpm.providers.anthropic.claude_code.generation import ClaudeCodeGenerator
generator = ClaudeCodeGenerator(db_service)
result = generator.generate_from_agents(agents, rules, project, output_dir)
```

Use runtime orchestrator:

```python
from agentpm.providers.anthropic.claude_code.runtime import (
    ClaudeCodeOrchestrator,
    get_orchestrator
)
orchestrator = get_orchestrator(db, project_id=1)
```

Or use the high-level service:

```python
from agentpm.core.services.agent_generator import AgentGeneratorService
generator = AgentGeneratorService(db_service, project_path)
summary = generator.generate_all()
```
"""

# Generation module (templates)
from .generation import ClaudeCodeGenerator, SkillGenerator, MemoryGenerator

# Runtime module (orchestration)
from .runtime import ClaudeCodeOrchestrator, get_orchestrator, reset_orchestrator

# Models (data structures)
from .models import ClaudeCodeIntegration

__all__ = [
    # Generation
    "ClaudeCodeGenerator",
    "SkillGenerator",
    "MemoryGenerator",

    # Runtime
    "ClaudeCodeOrchestrator",
    "get_orchestrator",
    "reset_orchestrator",

    # Models
    "ClaudeCodeIntegration",
]
