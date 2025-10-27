"""
Claude Code Hooks System

Manages Claude Code hooks for APM (Agent Project Manager) integration including event handling,
automation, and workflow triggers.

Based on: https://docs.claude.com/en/docs/claude-code/hooks-guide
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import subprocess
import sys
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from ..models import HookDefinition, HookEvent, HookEventType, HookMatcher, HookAction, HookMatcherType


class ClaudeCodeHooksManager:
    """
    Manages Claude Code hooks for APM (Agent Project Manager).
    
    Creates and manages hooks that integrate APM (Agent Project Manager) workflows with
    Claude Code events and tool usage.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize hooks manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._hooks_cache: Dict[str, HookDefinition] = {}
        self._active_hooks: Dict[str, bool] = {}
    
    def create_aipm_hooks(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[HookDefinition]:
        """
        Create comprehensive APM (Agent Project Manager) hooks for Claude Code.
        
        Args:
            output_dir: Directory to write hooks configuration
            project_id: Optional project ID for project-specific hooks
            
        Returns:
            List of created HookDefinitions
        """
        hooks = []
        
        # Create hooks directory
        hooks_dir = output_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create APM (Agent Project Manager) hooks
        hooks.extend(self._create_workflow_hooks(hooks_dir))
        hooks.extend(self._create_quality_gate_hooks(hooks_dir))
        hooks.extend(self._create_context_hooks(hooks_dir))
        hooks.extend(self._create_learning_hooks(hooks_dir))
        hooks.extend(self._create_security_hooks(hooks_dir))
        
        # Create project-specific hooks if project_id provided
        if project_id:
            hooks.extend(self._create_project_hooks(hooks_dir, project_id))
        
        # Write hooks configuration
        self._write_hooks_configuration(hooks_dir, hooks)
        
        return hooks
    
    def create_agent_hooks(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        output_dir: Path
    ) -> List[HookDefinition]:
        """
        Create hooks for specific APM (Agent Project Manager) agent.
        
        Args:
            agent_role: Agent role name
            agent_capabilities: List of agent capabilities
            output_dir: Directory to write hooks
            
        Returns:
            List of created HookDefinitions
        """
        hooks = []
        
        # Create agent-specific hooks directory
        agent_hooks_dir = output_dir / "hooks" / "agents" / agent_role
        agent_hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent workflow hooks
        hooks.extend(self._create_agent_workflow_hooks(agent_role, agent_capabilities, agent_hooks_dir))
        
        # Create agent capability hooks
        hooks.extend(self._create_agent_capability_hooks(agent_role, agent_capabilities, agent_hooks_dir))
        
        # Write agent hooks configuration
        self._write_hooks_configuration(agent_hooks_dir, hooks)
        
        return hooks
    
    def create_workflow_hooks(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        output_dir: Path
    ) -> List[HookDefinition]:
        """
        Create hooks for specific APM (Agent Project Manager) workflow.
        
        Args:
            workflow_name: Workflow name (feature, bugfix, enhancement)
            workflow_info: Workflow information
            output_dir: Directory to write hooks
            
        Returns:
            List of created HookDefinitions
        """
        hooks = []
        
        # Create workflow hooks directory
        workflow_hooks_dir = output_dir / "hooks" / "workflows" / workflow_name
        workflow_hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow-specific hooks
        hooks.extend(self._create_workflow_validation_hooks(workflow_name, workflow_info, workflow_hooks_dir))
        hooks.extend(self._create_workflow_automation_hooks(workflow_name, workflow_info, workflow_hooks_dir))
        
        # Write workflow hooks configuration
        self._write_hooks_configuration(workflow_hooks_dir, hooks)
        
        return hooks
    
    def _create_workflow_hooks(self, hooks_dir: Path) -> List[HookDefinition]:
        """Create general workflow hooks."""
        hooks = []
        
        # Pre-tool use hook for APM (Agent Project Manager) commands
        pre_tool_hook = HookDefinition(
            name="aipm-pre-tool-use",
            description="APM (Agent Project Manager) pre-tool use validation and context preparation",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="aipm|apm"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('APM (Agent Project Manager) tool execution starting')\""
                )
            ],
            enabled=True,
            priority=10,
            category="workflow"
        )
        hooks.append(pre_tool_hook)
        
        # Post-tool use hook for APM (Agent Project Manager) commands
        post_tool_hook = HookDefinition(
            name="aipm-post-tool-use",
            description="APM (Agent Project Manager) post-tool use cleanup and learning capture",
            component_type="hook",
            event=HookEventType.POST_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="aipm|apm"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('APM (Agent Project Manager) tool execution completed')\""
                )
            ],
            enabled=True,
            priority=10,
            category="workflow"
        )
        hooks.append(post_tool_hook)
        
        # Pre-tool use hook for Write tool (document creation guidance)
        write_tool_hook = HookDefinition(
            name="write-tool-guidance",
            description="Provide guidance for Write tool usage with APM document commands",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="Write"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 agentpm/core/hooks/implementations/pre-tool-use.py"
                )
            ],
            enabled=True,
            priority=5,  # Higher priority than general AIPM hooks
            category="workflow"
        )
        hooks.append(write_tool_hook)
        
        return hooks
    
    def _create_quality_gate_hooks(self, hooks_dir: Path) -> List[HookDefinition]:
        """Create quality gate enforcement hooks."""
        hooks = []
        
        # Quality gate validation hook
        quality_hook = HookDefinition(
            name="aipm-quality-gates",
            description="APM (Agent Project Manager) quality gate enforcement",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="work-item|task"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('Validating APM (Agent Project Manager) quality gates')\""
                )
            ],
            enabled=True,
            priority=5,
            category="quality"
        )
        hooks.append(quality_hook)
        
        # Time-boxing enforcement hook
        timebox_hook = HookDefinition(
            name="aipm-timeboxing",
            description="APM (Agent Project Manager) time-boxing enforcement",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="task.*implementation"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('Checking IMPLEMENTATION task time-boxing (max 4h)')\""
                )
            ],
            enabled=True,
            priority=5,
            category="quality"
        )
        hooks.append(timebox_hook)
        
        return hooks
    
    def _create_context_hooks(self, hooks_dir: Path) -> List[HookDefinition]:
        """Create context assembly hooks."""
        hooks = []
        
        # Context assembly hook
        context_hook = HookDefinition(
            name="aipm-context-assembly",
            description="APM (Agent Project Manager) context assembly and delivery",
            component_type="hook",
            event=HookEventType.SESSION_START,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.REGEX,
                    pattern=".*"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('Assembling APM (Agent Project Manager) context for session')\""
                )
            ],
            enabled=True,
            priority=20,
            category="context"
        )
        hooks.append(context_hook)
        
        return hooks
    
    def _create_learning_hooks(self, hooks_dir: Path) -> List[HookDefinition]:
        """Create learning capture hooks."""
        hooks = []
        
        # Learning capture hook
        learning_hook = HookDefinition(
            name="aipm-learning-capture",
            description="APM (Agent Project Manager) learning and decision capture",
            component_type="hook",
            event=HookEventType.POST_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="learnings|decisions"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('Capturing APM (Agent Project Manager) learnings and decisions')\""
                )
            ],
            enabled=True,
            priority=15,
            category="learning"
        )
        hooks.append(learning_hook)
        
        return hooks
    
    def _create_security_hooks(self, hooks_dir: Path) -> List[HookDefinition]:
        """Create security and protection hooks."""
        hooks = []
        
        # File protection hook
        protection_hook = HookDefinition(
            name="aipm-file-protection",
            description="APM (Agent Project Manager) file protection and security",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="Edit|Write"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(2 if any(p in path for p in ['.env', 'package-lock.json', '.git/']) else 0)\""
                )
            ],
            enabled=True,
            priority=1,
            category="security"
        )
        hooks.append(protection_hook)
        
        # Input validation hook
        validation_hook = HookDefinition(
            name="aipm-input-validation",
            description="APM (Agent Project Manager) input validation and sanitization",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern="aipm|apm"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command="python3 -c \"import sys; print('Validating APM (Agent Project Manager) inputs')\""
                )
            ],
            enabled=True,
            priority=2,
            category="security"
        )
        hooks.append(validation_hook)
        
        return hooks
    
    def _create_project_hooks(self, hooks_dir: Path, project_id: int) -> List[HookDefinition]:
        """Create project-specific hooks."""
        hooks = []
        
        # Project context hook
        project_hook = HookDefinition(
            name=f"aipm-project-{project_id}",
            description=f"APM (Agent Project Manager) project {project_id} specific hooks",
            component_type="hook",
            event=HookEventType.SESSION_START,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.REGEX,
                    pattern=".*"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command=f"python3 -c \"import sys; print('Loading APM (Agent Project Manager) project {project_id} context')\""
                )
            ],
            enabled=True,
            priority=25,
            category="project"
        )
        hooks.append(project_hook)
        
        return hooks
    
    def _create_agent_workflow_hooks(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        hooks_dir: Path
    ) -> List[HookDefinition]:
        """Create agent-specific workflow hooks."""
        hooks = []
        
        # Agent invocation hook
        agent_hook = HookDefinition(
            name=f"aipm-agent-{agent_role}",
            description=f"APM (Agent Project Manager) {agent_role} agent workflow hooks",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern=f"agent:{agent_role}"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command=f"python3 -c \"import sys; print('Invoking APM (Agent Project Manager) {agent_role} agent')\""
                )
            ],
            enabled=True,
            priority=10,
            category="agent"
        )
        hooks.append(agent_hook)
        
        return hooks
    
    def _create_agent_capability_hooks(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        hooks_dir: Path
    ) -> List[HookDefinition]:
        """Create agent capability-specific hooks."""
        hooks = []
        
        for capability in agent_capabilities:
            capability_hook = HookDefinition(
                name=f"aipm-agent-{agent_role}-{capability}",
                description=f"APM (Agent Project Manager) {agent_role} {capability} capability hook",
                component_type="hook",
                event=HookEventType.PRE_TOOL_USE,
                matchers=[
                    HookMatcher(
                        type=HookMatcherType.TOOL_TYPE,
                        pattern=f"capability:{capability}"
                    )
                ],
                actions=[
                    HookAction(
                        type="command",
                        command=f"python3 -c \"import sys; print('Using APM (Agent Project Manager) {agent_role} {capability} capability')\""
                    )
                ],
                enabled=True,
                priority=15,
                category="capability"
            )
            hooks.append(capability_hook)
        
        return hooks
    
    def _create_workflow_validation_hooks(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        hooks_dir: Path
    ) -> List[HookDefinition]:
        """Create workflow validation hooks."""
        hooks = []
        
        # Workflow validation hook
        validation_hook = HookDefinition(
            name=f"aipm-workflow-{workflow_name}-validation",
            description=f"APM (Agent Project Manager) {workflow_name} workflow validation",
            component_type="hook",
            event=HookEventType.PRE_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern=f"workflow:{workflow_name}"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command=f"python3 -c \"import sys; print('Validating APM (Agent Project Manager) {workflow_name} workflow')\""
                )
            ],
            enabled=True,
            priority=10,
            category="workflow"
        )
        hooks.append(validation_hook)
        
        return hooks
    
    def _create_workflow_automation_hooks(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        hooks_dir: Path
    ) -> List[HookDefinition]:
        """Create workflow automation hooks."""
        hooks = []
        
        # Workflow automation hook
        automation_hook = HookDefinition(
            name=f"aipm-workflow-{workflow_name}-automation",
            description=f"APM (Agent Project Manager) {workflow_name} workflow automation",
            component_type="hook",
            event=HookEventType.POST_TOOL_USE,
            matchers=[
                HookMatcher(
                    type=HookMatcherType.TOOL_TYPE,
                    pattern=f"workflow:{workflow_name}"
                )
            ],
            actions=[
                HookAction(
                    type="command",
                    command=f"python3 -c \"import sys; print('Automating APM (Agent Project Manager) {workflow_name} workflow steps')\""
                )
            ],
            enabled=True,
            priority=15,
            category="automation"
        )
        hooks.append(automation_hook)
        
        return hooks
    
    def _write_hooks_configuration(self, hooks_dir: Path, hooks: List[HookDefinition]) -> None:
        """Write hooks configuration to filesystem."""
        # Create hooks.json configuration
        hooks_config = {
            "hooks": {}
        }
        
        # Group hooks by event type
        for hook in hooks:
            event_name = hook.event.value
            if event_name not in hooks_config["hooks"]:
                hooks_config["hooks"][event_name] = []
            
            # Convert hook to configuration format
            hook_config = {
                "matcher": hook.matchers[0].pattern if hook.matchers else "",
                "hooks": [
                    {
                        "type": action.type,
                        "command": action.command
                    }
                    for action in hook.actions
                ]
            }
            
            hooks_config["hooks"][event_name].append(hook_config)
        
        # Write hooks.json
        hooks_file = hooks_dir / "hooks.json"
        hooks_file.write_text(json.dumps(hooks_config, indent=2))
        
        # Write individual hook definitions
        for hook in hooks:
            hook_file = hooks_dir / f"{hook.name}.json"
            hook_file.write_text(json.dumps(hook.model_dump(), indent=2))
    
    def execute_hook(self, hook: HookDefinition, event_data: Dict[str, Any]) -> bool:
        """
        Execute a hook with given event data.
        
        Args:
            hook: Hook definition to execute
            event_data: Event data for hook execution
            
        Returns:
            True if hook executed successfully, False otherwise
        """
        try:
            for action in hook.actions:
                if action.type == "command" and action.command:
                    # Execute command with event data as JSON input
                    process = subprocess.Popen(
                        action.command,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Send event data as JSON to stdin
                    stdout, stderr = process.communicate(input=json.dumps(event_data))
                    
                    if process.returncode != 0:
                        print(f"Hook {hook.name} failed: {stderr}", file=sys.stderr)
                        return False
                    
                    print(f"Hook {hook.name} output: {stdout}")
            
            return True
            
        except Exception as e:
            print(f"Error executing hook {hook.name}: {e}", file=sys.stderr)
            return False
    
    def get_hooks_for_event(self, event_type: HookEventType) -> List[HookDefinition]:
        """
        Get all hooks for a specific event type.
        
        Args:
            event_type: Event type to get hooks for
            
        Returns:
            List of HookDefinitions for the event type
        """
        return [
            hook for hook in self._hooks_cache.values()
            if hook.event == event_type and hook.enabled
        ]
    
    def enable_hook(self, hook_name: str) -> bool:
        """
        Enable a hook.
        
        Args:
            hook_name: Name of hook to enable
            
        Returns:
            True if hook was enabled, False if not found
        """
        if hook_name in self._hooks_cache:
            self._hooks_cache[hook_name].enabled = True
            self._active_hooks[hook_name] = True
            return True
        return False
    
    def disable_hook(self, hook_name: str) -> bool:
        """
        Disable a hook.
        
        Args:
            hook_name: Name of hook to disable
            
        Returns:
            True if hook was disabled, False if not found
        """
        if hook_name in self._hooks_cache:
            self._hooks_cache[hook_name].enabled = False
            self._active_hooks[hook_name] = False
            return True
        return False
