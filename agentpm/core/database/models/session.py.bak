"""
Session Model (STUB)

CRITICAL: This is a stub implementation to unblock the CLI.
Full session tracking implementation is required (see WI-XX for tracking).

This stub provides minimal functionality to satisfy imports until
the full session tracking system is implemented.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session status enumeration (stub)."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionType(str, Enum):
    """Session type enumeration (stub)."""
    DEVELOPMENT = "development"
    CODING = "coding"  # Legacy format
    PLANNING = "planning"
    REVIEW = "review"
    OPERATIONS = "operations"


class SessionTool(str, Enum):
    """Session tool enumeration (stub)."""
    CLAUDE_CODE = "claude_code"
    CLAUDE_CODE_LEGACY = "claude-code"  # Legacy format with hyphen
    CURSOR = "cursor"
    CLI = "cli"
    WEB_ADMIN = "web_admin"


class LLMModel(str, Enum):
    """LLM model enumeration (stub)."""
    CLAUDE_SONNET_4_5 = "claude-sonnet-4-5"
    CLAUDE_SONNET_3_5 = "claude-sonnet-3-5"
    GPT4 = "gpt-4"
    NONE = "none"


class SessionMetadata(BaseModel):
    """Session metadata (stub)."""
    agent_count: int = Field(0, description="Number of agents involved")
    task_count: int = Field(0, description="Number of tasks worked on")
    work_item_count: int = Field(0, description="Number of work items touched")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    decisions: List[str] = Field(default_factory=list, description="Decisions made")
    learnings: List[str] = Field(default_factory=list, description="Key learnings")

    class Config:
        """Pydantic config."""
        from_attributes = True


class Session(BaseModel):
    """
    Session entity (STUB).

    CRITICAL: This is a minimal stub. Full implementation pending.
    """

    id: Optional[int] = Field(None, description="Session ID (auto-assigned)")
    session_id: str = Field(..., description="Unique session identifier")
    project_id: int = Field(..., description="Associated project ID")
    status: SessionStatus = Field(SessionStatus.ACTIVE, description="Session status")
    session_type: SessionType = Field(SessionType.DEVELOPMENT, description="Session type")
    tool: SessionTool = Field(SessionTool.CLAUDE_CODE, description="Tool used")
    llm_model: Optional[LLMModel] = Field(None, description="LLM model if applicable")
    metadata: Optional[SessionMetadata] = Field(None, description="Session metadata")
    started_at: Optional[str] = Field(None, description="Start timestamp")
    ended_at: Optional[str] = Field(None, description="End timestamp")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    
    # Additional fields for compatibility with existing database and CLI
    tool_name: Optional[SessionTool] = Field(None, description="Tool name (legacy)")
    tool_version: Optional[str] = Field(None, description="Tool version")
    duration_minutes: Optional[int] = Field(None, description="Session duration in minutes")
    exit_reason: Optional[str] = Field(None, description="Reason for session exit")
    developer_name: Optional[str] = Field(None, description="Developer name")
    developer_email: Optional[str] = Field(None, description="Developer email")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE

    class Config:
        """Pydantic config."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "session_id": "session-2025-10-19-001",
                "project_id": 1,
                "status": "active",
                "session_type": "development",
                "tool": "claude_code",
            }
        }
