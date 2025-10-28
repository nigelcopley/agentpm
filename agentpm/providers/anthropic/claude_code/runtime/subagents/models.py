"""
Subagent Models

Data models for Claude Code subagent orchestration.
Defines subagent specifications, invocation requests, and results.

Pattern: Pydantic models for type safety and validation
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SubagentCapability(str, Enum):
    """
    Subagent capability categories.

    Defines what types of work a subagent can perform.
    """
    DISCOVERY = "discovery"              # D1 phase work
    PLANNING = "planning"                # P1 phase work
    IMPLEMENTATION = "implementation"    # I1 phase work
    TESTING = "testing"                  # Test creation/execution
    REVIEW = "review"                    # R1 phase work
    OPERATIONS = "operations"            # O1 phase work
    EVOLUTION = "evolution"              # E1 phase work
    DOCUMENTATION = "documentation"      # Doc writing
    ANALYSIS = "analysis"                # Code/data analysis
    VALIDATION = "validation"            # Quality checks


class SubagentSpec(BaseModel):
    """
    Subagent specification.

    Defines a registered AIPM subagent that can be invoked by Claude Code.

    Attributes:
        name: Unique subagent identifier (e.g., "code-implementer")
        description: Natural language description of what the subagent does
        capabilities: List of capability categories
        tier: Agent tier (0=orchestrator, 1=specialist, 2=sub-agent, 3=utility)
        invocation_template: Example invocation for Claude Code
        metadata: Additional agent metadata

    Example:
        spec = SubagentSpec(
            name="code-implementer",
            description="Implements production code following AIPM patterns",
            capabilities=[SubagentCapability.IMPLEMENTATION],
            tier=1,
            invocation_template="Implement [feature] following [patterns]"
        )
    """
    name: str = Field(..., description="Unique subagent identifier")
    description: str = Field(..., description="What this subagent does")
    capabilities: List[SubagentCapability] = Field(default_factory=list)
    tier: int = Field(default=1, ge=0, le=3, description="Agent tier (0-3)")
    invocation_template: str = Field(..., description="Example invocation")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""
        use_enum_values = True


class SubagentInvocationRequest(BaseModel):
    """
    Subagent invocation request.

    Represents a request from Claude Code to invoke an AIPM subagent.

    Attributes:
        subagent_name: Name of subagent to invoke
        task_description: Natural language description of task
        context: Contextual data for the subagent
        session_id: Claude session identifier
        correlation_id: Request correlation ID
        metadata: Additional request metadata

    Example:
        request = SubagentInvocationRequest(
            subagent_name="test-implementer",
            task_description="Create unit tests for UserService",
            context={"service": "UserService", "coverage_target": 0.9},
            session_id="session-123",
            correlation_id="req-456"
        )
    """
    subagent_name: str = Field(..., description="Subagent to invoke")
    task_description: str = Field(..., description="What to do")
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: str = Field(..., description="Claude session ID")
    correlation_id: str = Field(..., description="Request correlation ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubagentInvocationResult(BaseModel):
    """
    Subagent invocation result.

    Represents the result of a subagent invocation.

    Attributes:
        success: Whether invocation succeeded
        subagent_name: Name of invoked subagent
        message: Human-readable result message
        data: Result data
        artifacts: Generated artifacts (files, etc.)
        errors: Error messages if any
        metadata: Additional result metadata

    Example:
        result = SubagentInvocationResult(
            success=True,
            subagent_name="test-implementer",
            message="Created 15 unit tests with 95% coverage",
            data={"tests_created": 15, "coverage": 0.95},
            artifacts=["tests/test_user_service.py"]
        )
    """
    success: bool = Field(..., description="Invocation succeeded")
    subagent_name: str = Field(..., description="Invoked subagent")
    message: str = Field(..., description="Result message")
    data: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list, description="Generated files")
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def success_result(
        cls,
        subagent_name: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
    ) -> SubagentInvocationResult:
        """
        Create success result.

        Args:
            subagent_name: Subagent name
            message: Success message
            data: Result data
            artifacts: Generated artifacts

        Returns:
            Success result
        """
        return cls(
            success=True,
            subagent_name=subagent_name,
            message=message,
            data=data or {},
            artifacts=artifacts or [],
            errors=[]
        )

    @classmethod
    def error_result(
        cls,
        subagent_name: str,
        message: str,
        errors: Optional[List[str]] = None,
    ) -> SubagentInvocationResult:
        """
        Create error result.

        Args:
            subagent_name: Subagent name
            message: Error message
            errors: Detailed errors

        Returns:
            Error result
        """
        return cls(
            success=False,
            subagent_name=subagent_name,
            message=message,
            data={},
            artifacts=[],
            errors=errors or [message]
        )
