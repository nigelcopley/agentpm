"""
Checkpoint System for Claude Code Integration

Provides session state checkpointing and restoration capabilities.

Components:
- models: Pydantic models for checkpoints
- manager: Checkpoint creation and restoration logic
- adapters: Database conversion layer
- methods: Database operations

Example:
    from agentpm.services.claude_integration.checkpoints import CheckpointManager

    manager = CheckpointManager(db)
    checkpoint = manager.create_checkpoint(session_id=1, name="before-refactor")

    # Later...
    manager.restore_checkpoint(checkpoint.id)
"""

from .models import SessionCheckpoint
from .manager import CheckpointManager

__all__ = ["SessionCheckpoint", "CheckpointManager"]
