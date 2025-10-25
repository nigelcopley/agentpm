"""
Claude Code Settings Models

Type-safe Pydantic models for Claude Code integration settings.
Follows APM (Agent Project Manager) three-layer architecture (Models layer).
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class MemoryGenerationFrequency(str, Enum):
    """When to generate memory snapshots."""

    SESSION_END = "session_end"
    """Generate at end of each session"""

    MANUAL = "manual"
    """Only generate when manually triggered"""

    SCHEDULED = "scheduled"
    """Generate on a schedule"""


class HooksSettings(BaseModel):
    """
    Settings for Claude lifecycle hooks.

    Controls which hooks are enabled and their behavior.
    """

    enabled: Dict[str, bool] = Field(
        default_factory=lambda: {
            "session_start": True,
            "session_end": True,
            "prompt_submit": True,
            "tool_result": False,
            "pre_tool_use": False,
            "post_tool_use": False,
            "stop": True,
            "subagent_stop": True,
        },
        description="Hook enable/disable flags by event type"
    )

    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum time for hook execution"
    )

    retry_on_failure: bool = Field(
        default=False,
        description="Retry failed hooks"
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed hooks"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "enabled": {
                    "session_start": True,
                    "session_end": True,
                    "prompt_submit": True,
                },
                "timeout_seconds": 30,
                "retry_on_failure": False,
                "max_retries": 3,
            }
        }


class MemorySettings(BaseModel):
    """
    Settings for Claude memory/context management.

    Controls memory generation, retention, and caching.
    """

    auto_load_memory: bool = Field(
        default=True,
        description="Automatically load memory at session start"
    )

    auto_generate_memory: bool = Field(
        default=True,
        description="Automatically generate memory snapshots"
    )

    generation_frequency: MemoryGenerationFrequency = Field(
        default=MemoryGenerationFrequency.SESSION_END,
        description="When to generate memory snapshots"
    )

    retention_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Days to retain memory snapshots"
    )

    max_file_size_kb: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="Maximum memory file size in KB"
    )

    cache_duration_minutes: int = Field(
        default=60,
        ge=5,
        le=1440,
        description="Cache duration for memory data"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "auto_load_memory": True,
                "auto_generate_memory": True,
                "generation_frequency": "session_end",
                "retention_days": 90,
                "max_file_size_kb": 500,
                "cache_duration_minutes": 60,
            }
        }


class SubagentSettings(BaseModel):
    """
    Settings for Claude subagent execution.

    Controls parallel execution, timeouts, and resource limits.
    """

    enabled: bool = Field(
        default=True,
        description="Enable subagent system"
    )

    max_parallel: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum parallel subagent executions"
    )

    timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Subagent execution timeout"
    )

    auto_cleanup: bool = Field(
        default=True,
        description="Automatically cleanup completed subagents"
    )

    max_depth: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum subagent nesting depth"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "enabled": True,
                "max_parallel": 3,
                "timeout_seconds": 300,
                "auto_cleanup": True,
                "max_depth": 3,
            }
        }


class PerformanceSettings(BaseModel):
    """
    Settings for performance tuning and optimization.

    Controls caching, concurrency, and resource usage.
    """

    enable_caching: bool = Field(
        default=True,
        description="Enable response caching"
    )

    cache_ttl_seconds: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Cache time-to-live"
    )

    max_concurrent_requests: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent API requests"
    )

    request_timeout_seconds: int = Field(
        default=120,
        ge=30,
        le=600,
        description="API request timeout"
    )

    enable_metrics: bool = Field(
        default=True,
        description="Enable performance metrics collection"
    )

    metrics_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Metrics collection interval"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "enable_caching": True,
                "cache_ttl_seconds": 300,
                "max_concurrent_requests": 5,
                "request_timeout_seconds": 120,
                "enable_metrics": True,
                "metrics_interval_seconds": 60,
            }
        }


class ClaudeCodeSettings(BaseModel):
    """
    Comprehensive Claude Code integration settings.

    Top-level settings container with all subsystem configurations.
    Follows Pydantic v2 patterns for validation and serialization.

    Example:
        settings = ClaudeCodeSettings(
            plugin_enabled=True,
            hooks=HooksSettings(
                enabled={"session_start": True}
            ),
            memory=MemorySettings(
                retention_days=90
            )
        )
    """

    # Core plugin settings
    plugin_enabled: bool = Field(
        default=True,
        description="Enable Claude Code plugin system"
    )

    verbose_logging: bool = Field(
        default=False,
        description="Enable verbose debug logging"
    )

    # Subsystem settings
    hooks: HooksSettings = Field(
        default_factory=HooksSettings,
        description="Lifecycle hooks configuration"
    )

    memory: MemorySettings = Field(
        default_factory=MemorySettings,
        description="Memory/context management configuration"
    )

    subagents: SubagentSettings = Field(
        default_factory=SubagentSettings,
        description="Subagent execution configuration"
    )

    performance: PerformanceSettings = Field(
        default_factory=PerformanceSettings,
        description="Performance tuning configuration"
    )

    # Project-specific overrides
    project_id: Optional[int] = Field(
        default=None,
        description="APM project ID for context"
    )

    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom user-defined settings"
    )

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate project ID is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("project_id must be positive")
        return v

    def get_hook_enabled(self, hook_name: str) -> bool:
        """
        Check if a specific hook is enabled.

        Args:
            hook_name: Name of the hook event type

        Returns:
            True if hook is enabled

        Example:
            if settings.get_hook_enabled("session_start"):
                # Execute hook
        """
        return self.hooks.enabled.get(hook_name, False)

    def set_hook_enabled(self, hook_name: str, enabled: bool) -> None:
        """
        Enable or disable a specific hook.

        Args:
            hook_name: Name of the hook event type
            enabled: Enable flag

        Example:
            settings.set_hook_enabled("session_start", True)
        """
        self.hooks.enabled[hook_name] = enabled

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "plugin_enabled": True,
                "verbose_logging": False,
                "hooks": {
                    "enabled": {
                        "session_start": True,
                        "session_end": True,
                    },
                    "timeout_seconds": 30,
                },
                "memory": {
                    "auto_load_memory": True,
                    "retention_days": 90,
                },
                "subagents": {
                    "max_parallel": 3,
                    "timeout_seconds": 300,
                },
                "performance": {
                    "enable_caching": True,
                    "cache_ttl_seconds": 300,
                },
                "project_id": 1,
            }
        }
