"""
Claude Code Models - Pydantic Domain Models

Type-safe models for all Claude Code integrations including plugins, hooks,
subagents, settings, slash commands, checkpointing, and memory tools.

Based on Claude Code documentation and specifications.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ClaudeCodeComponentType(str, Enum):
    """Types of Claude Code components."""
    PLUGIN = "plugin"
    HOOK = "hook"
    SUBAGENT = "subagent"
    SETTING = "setting"
    SLASH_COMMAND = "slash_command"
    CHECKPOINT = "checkpoint"
    MEMORY_TOOL = "memory_tool"
    SKILL = "skill"


class HookEventType(str, Enum):
    """Claude Code hook event types."""
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    NOTIFICATION = "Notification"
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    FILE_OPEN = "FileOpen"
    FILE_SAVE = "FileSave"
    COMMAND_EXECUTE = "CommandExecute"


class HookMatcherType(str, Enum):
    """Hook matcher types."""
    COMMAND = "command"
    FILE_PATTERN = "file_pattern"
    TOOL_TYPE = "tool_type"
    REGEX = "regex"


class SubagentCapability(str, Enum):
    """Subagent capabilities."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    ANALYSIS = "analysis"
    RESEARCH = "research"


class SettingType(str, Enum):
    """Setting types."""
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    ARRAY = "array"
    OBJECT = "object"


class CheckpointType(str, Enum):
    """Checkpoint types."""
    MANUAL = "manual"
    AUTO = "auto"
    SESSION = "session"
    MILESTONE = "milestone"


class MemoryToolType(str, Enum):
    """Memory tool types."""
    PERSISTENT = "persistent"
    SESSION = "session"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"


# Base model for all Claude Code components
class ClaudeCodeComponent(BaseModel):
    """Base model for Claude Code components."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )
    
    # Core fields
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    component_type: ClaudeCodeComponentType
    
    # Metadata
    version: str = Field(default="1.0.0")
    author: str = Field(default="APM (Agent Project Manager)")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    # APM (Agent Project Manager) integration
    source_agent_id: Optional[int] = Field(default=None)
    source_workflow_id: Optional[int] = Field(default=None)
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


# Plugin Models
class PluginDefinition(ClaudeCodeComponent):
    """Claude Code plugin definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.PLUGIN)
    
    # Plugin structure
    commands: List[str] = Field(default_factory=list)
    agents: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    mcp_servers: List[str] = Field(default_factory=list)
    
    # Plugin configuration
    dependencies: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    
    # Plugin metadata
    category: str = Field(default="utility")
    keywords: List[str] = Field(default_factory=list)
    homepage: Optional[str] = Field(default=None)
    repository: Optional[str] = Field(default=None)
    license: Optional[str] = Field(default=None)


class MarketplaceDefinition(BaseModel):
    """Claude Code marketplace definition."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )
    
    # Marketplace metadata
    name: str = Field(..., min_length=1, max_length=100)
    owner: Dict[str, str] = Field(..., description="Owner information")
    description: Optional[str] = Field(default=None)
    
    # Plugins in marketplace
    plugins: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Marketplace configuration
    version: str = Field(default="1.0.0")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


# Hook Models
class HookMatcher(BaseModel):
    """Hook matcher configuration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )
    
    type: HookMatcherType
    pattern: str = Field(..., description="Pattern to match")
    case_sensitive: bool = Field(default=False)
    invert: bool = Field(default=False)


class HookAction(BaseModel):
    """Hook action configuration."""
    
    model_config = ConfigDict(
        validate_assignment=True,
    )
    
    type: str = Field(..., description="Action type (command, script, etc.)")
    command: Optional[str] = Field(default=None)
    script: Optional[str] = Field(default=None)
    timeout: Optional[int] = Field(default=None)
    working_directory: Optional[str] = Field(default=None)
    environment: Dict[str, str] = Field(default_factory=dict)


class HookDefinition(ClaudeCodeComponent):
    """Claude Code hook definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.HOOK)
    
    # Hook configuration
    event: HookEventType
    matchers: List[HookMatcher] = Field(default_factory=list)
    actions: List[HookAction] = Field(default_factory=list)
    
    # Hook behavior
    enabled: bool = Field(default=True)
    priority: int = Field(default=0, ge=0, le=100)
    async_execution: bool = Field(default=False)
    
    # Hook metadata
    category: str = Field(default="utility")
    tags: List[str] = Field(default_factory=list)


class HookEvent(BaseModel):
    """Claude Code hook event."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )
    
    event_type: HookEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)


# Subagent Models
class SubagentDefinition(ClaudeCodeComponent):
    """Claude Code subagent definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.SUBAGENT)
    
    # Subagent configuration
    role: str = Field(..., description="Subagent role")
    capabilities: List[SubagentCapability] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    
    # Subagent behavior
    auto_invoke: bool = Field(default=False)
    priority: int = Field(default=0, ge=0, le=100)
    max_concurrent: int = Field(default=1, ge=1)
    
    # Subagent metadata
    category: str = Field(default="utility")
    keywords: List[str] = Field(default_factory=list)


# Settings Models
class SettingDefinition(BaseModel):
    """Claude Code setting definition."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )
    
    # Setting metadata
    key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    setting_type: SettingType
    
    # Setting configuration
    default_value: Any = Field(default=None)
    required: bool = Field(default=False)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    
    # Setting metadata
    category: str = Field(default="general")
    tags: List[str] = Field(default_factory=list)


class SettingsDefinition(ClaudeCodeComponent):
    """Claude Code settings definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.SETTING)
    
    # Settings configuration
    settings: List[SettingDefinition] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    # Settings metadata
    scope: str = Field(default="project", description="Settings scope (project, user, global)")


# Slash Command Models
class SlashCommandDefinition(ClaudeCodeComponent):
    """Claude Code slash command definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.SLASH_COMMAND)
    
    # Command configuration
    command: str = Field(..., description="Slash command (e.g., '/hello')")
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    
    # Command behavior
    enabled: bool = Field(default=True)
    requires_confirmation: bool = Field(default=False)
    timeout: Optional[int] = Field(default=None)
    
    # Command metadata
    category: str = Field(default="utility")
    keywords: List[str] = Field(default_factory=list)


# Checkpointing Models
class CheckpointDefinition(ClaudeCodeComponent):
    """Claude Code checkpoint definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.CHECKPOINT)
    
    # Checkpoint configuration
    checkpoint_type: CheckpointType
    trigger_conditions: List[str] = Field(default_factory=list)
    retention_policy: Dict[str, Any] = Field(default_factory=dict)
    
    # Checkpoint behavior
    auto_create: bool = Field(default=False)
    auto_restore: bool = Field(default=False)
    compression: bool = Field(default=True)
    
    # Checkpoint metadata
    category: str = Field(default="session")
    tags: List[str] = Field(default_factory=list)


# Memory Tool Models
class MemoryToolDefinition(ClaudeCodeComponent):
    """Claude Code memory tool definition."""
    
    component_type: ClaudeCodeComponentType = Field(default=ClaudeCodeComponentType.MEMORY_TOOL)
    
    # Memory tool configuration
    memory_type: MemoryToolType
    storage_backend: str = Field(default="file")
    storage_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Memory tool behavior
    auto_save: bool = Field(default=True)
    auto_load: bool = Field(default=True)
    compression: bool = Field(default=True)
    encryption: bool = Field(default=False)
    
    # Memory tool metadata
    category: str = Field(default="persistence")
    tags: List[str] = Field(default_factory=list)


# Integration Models
class ClaudeCodeIntegration(BaseModel):
    """Complete Claude Code integration definition."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
    )
    
    # Integration metadata
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    version: str = Field(default="1.0.0")
    
    # Components
    plugins: List[PluginDefinition] = Field(default_factory=list)
    hooks: List[HookDefinition] = Field(default_factory=list)
    subagents: List[SubagentDefinition] = Field(default_factory=list)
    settings: List[SettingsDefinition] = Field(default_factory=list)
    slash_commands: List[SlashCommandDefinition] = Field(default_factory=list)
    checkpoints: List[CheckpointDefinition] = Field(default_factory=list)
    memory_tools: List[MemoryToolDefinition] = Field(default_factory=list)
    
    # Integration configuration
    dependencies: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    
    # Integration metadata
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
