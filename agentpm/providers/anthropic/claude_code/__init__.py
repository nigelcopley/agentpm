"""
Claude Code Integration (Simplified)

Use the new template-based generator:

```python
from agentpm.providers.anthropic.claude_code.generator import ClaudeCodeGenerator
generator = ClaudeCodeGenerator(db_service)
result = generator.generate_from_agents(agents, rules, project, output_dir)
```

Or use the high-level service:

```python
from agentpm.core.services.agent_generator import AgentGeneratorService
generator = AgentGeneratorService(db_service, project_path)
summary = generator.generate_all()
```
"""

# New template-based generator (recommended)
from .generator import ClaudeCodeGenerator

# Legacy orchestrator (now a thin compatibility wrapper)
from .orchestrator import ClaudeCodeOrchestrator

# Models (still useful for data structures)
from .models import ClaudeCodeIntegration

__all__ = [
    # New template-based generator (recommended)
    "ClaudeCodeGenerator",

    # Core (maintained for compatibility)
    "ClaudeCodeOrchestrator",
    "ClaudeCodeIntegration",
]
