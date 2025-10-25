"""
Slash Command Models

Pydantic models for slash command system.

Pattern: Three-layer architecture - Models layer
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum


class CommandStatus(str, Enum):
    """Command execution status."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class SlashCommand(BaseModel):
    """
    Slash command definition.

    Represents a registered slash command with its handler and metadata.

    Attributes:
        name: Command name (without leading slash, e.g., "aipm:context")
        description: Human-readable description
        usage: Usage string (e.g., "/aipm:context [--work-item=ID]")
        handler: Command handler function (not serializable)
        enabled: Whether command is currently enabled

    Example:
        command = SlashCommand(
            name="aipm:context",
            description="Load AIPM context",
            usage="/aipm:context [--work-item=ID]",
            handler=context_handler,
            enabled=True
        )
    """
    name: str = Field(..., description="Command name without leading slash")
    description: str = Field(..., description="Human-readable description")
    usage: str = Field(..., description="Usage string with examples")
    handler: Optional[Any] = Field(
        default=None,
        description="Handler function (not serializable)",
        exclude=True
    )
    enabled: bool = Field(default=True, description="Whether command is enabled")

    class Config:
        arbitrary_types_allowed = True


class CommandResult(BaseModel):
    """
    Slash command execution result.

    Contains status, message, and optional data from command execution.

    Attributes:
        status: Execution status (success/error/partial)
        message: Human-readable result message
        data: Optional structured data (JSON-serializable)
        error: Optional error message if status is error

    Example:
        result = CommandResult(
            status=CommandStatus.SUCCESS,
            message="Context loaded successfully",
            data={"work_item_id": 123, "tasks": [456, 789]}
        )
    """
    status: CommandStatus = Field(..., description="Execution status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured result data"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if status is error"
    )


class CommandError(Exception):
    """
    Slash command execution error.

    Raised when command execution fails.

    Attributes:
        command: Command name that failed
        message: Error message
        details: Optional additional error details

    Example:
        raise CommandError(
            command="aipm:context",
            message="Work item not found",
            details={"work_item_id": 123}
        )
    """
    def __init__(
        self,
        command: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.command = command
        self.message = message
        self.details = details or {}
        super().__init__(f"{command}: {message}")
