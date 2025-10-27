"""
Claude Code Checkpointing System

Manages Claude Code checkpointing for APM (Agent Project Manager) integration including
checkpoint creation, restoration, and management.

Based on: https://docs.claude.com/en/docs/claude-code/checkpointing
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import shutil
import gzip
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from ..models import CheckpointDefinition, CheckpointType, ClaudeCodeComponentType


class ClaudeCodeCheckpointingManager:
    """
    Manages Claude Code checkpointing for APM (Agent Project Manager).
    
    Creates and manages checkpoints for APM (Agent Project Manager) workflows, sessions,
    and milestones.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize checkpointing manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._checkpoints_cache: Dict[str, CheckpointDefinition] = {}
        self._active_checkpoints: Dict[str, bool] = {}
        self._checkpoint_storage: Path = Path(".claude/checkpoints")
    
    def create_aipm_checkpoints(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[CheckpointDefinition]:
        """
        Create comprehensive APM (Agent Project Manager) checkpoints for Claude Code.
        
        Args:
            output_dir: Directory to write checkpoint definitions
            project_id: Optional project ID for project-specific checkpoints
            
        Returns:
            List of created CheckpointDefinitions
        """
        checkpoints = []
        
        # Create checkpoints directory
        checkpoints_dir = output_dir / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Create APM (Agent Project Manager) checkpoints
        checkpoints.extend(self._create_session_checkpoints(checkpoints_dir))
        checkpoints.extend(self._create_workflow_checkpoints(checkpoints_dir))
        checkpoints.extend(self._create_milestone_checkpoints(checkpoints_dir))
        checkpoints.extend(self._create_quality_checkpoints(checkpoints_dir))
        
        # Create project-specific checkpoints if project_id provided
        if project_id:
            checkpoints.extend(self._create_project_checkpoints(checkpoints_dir, project_id))
        
        return checkpoints
    
    def create_workflow_checkpoints(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        output_dir: Path
    ) -> List[CheckpointDefinition]:
        """
        Create checkpoints for specific APM (Agent Project Manager) workflow.
        
        Args:
            workflow_name: Workflow name
            workflow_info: Workflow information
            output_dir: Directory to write checkpoints
            
        Returns:
            List of created CheckpointDefinitions
        """
        checkpoints = []
        
        # Create workflow checkpoints directory
        workflow_checkpoints_dir = output_dir / "checkpoints" / "workflows" / workflow_name
        workflow_checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workflow-specific checkpoints
        checkpoints.extend(self._create_workflow_step_checkpoints(workflow_name, workflow_info, workflow_checkpoints_dir))
        checkpoints.extend(self._create_workflow_validation_checkpoints(workflow_name, workflow_info, workflow_checkpoints_dir))
        
        return checkpoints
    
    def create_agent_checkpoints(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        output_dir: Path
    ) -> List[CheckpointDefinition]:
        """
        Create checkpoints for specific APM (Agent Project Manager) agent.
        
        Args:
            agent_role: Agent role name
            agent_capabilities: List of agent capabilities
            output_dir: Directory to write checkpoints
            
        Returns:
            List of created CheckpointDefinitions
        """
        checkpoints = []
        
        # Create agent checkpoints directory
        agent_checkpoints_dir = output_dir / "checkpoints" / "agents" / agent_role
        agent_checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent-specific checkpoints
        checkpoints.extend(self._create_agent_task_checkpoints(agent_role, agent_capabilities, agent_checkpoints_dir))
        checkpoints.extend(self._create_agent_capability_checkpoints(agent_role, agent_capabilities, agent_checkpoints_dir))
        
        return checkpoints
    
    def _create_session_checkpoints(self, checkpoints_dir: Path) -> List[CheckpointDefinition]:
        """Create session checkpoints."""
        checkpoints = []
        
        # Session start checkpoint
        session_start_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Session Start",
            description="Checkpoint at session start with APM (Agent Project Manager) context",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.SESSION,
            trigger_conditions=["session_start", "context_assembly"],
            retention_policy={
                "max_age_days": 30,
                "max_count": 100,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="session",
            keywords=["session", "start", "context", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "session-start.json"
        checkpoint_content = self._create_session_start_checkpoint_content(session_start_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(session_start_checkpoint)
        
        # Session end checkpoint
        session_end_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Session End",
            description="Checkpoint at session end with APM (Agent Project Manager) state",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.SESSION,
            trigger_conditions=["session_end", "learning_capture"],
            retention_policy={
                "max_age_days": 90,
                "max_count": 50,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="session",
            keywords=["session", "end", "state", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "session-end.json"
        checkpoint_content = self._create_session_end_checkpoint_content(session_end_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(session_end_checkpoint)
        
        return checkpoints
    
    def _create_workflow_checkpoints(self, checkpoints_dir: Path) -> List[CheckpointDefinition]:
        """Create workflow checkpoints."""
        checkpoints = []
        
        # Workflow start checkpoint
        workflow_start_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Workflow Start",
            description="Checkpoint at workflow start with work item context",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.MANUAL,
            trigger_conditions=["workflow_start", "work_item_created"],
            retention_policy={
                "max_age_days": 60,
                "max_count": 200,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="workflow",
            keywords=["workflow", "start", "work-item", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "workflow-start.json"
        checkpoint_content = self._create_workflow_start_checkpoint_content(workflow_start_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(workflow_start_checkpoint)
        
        # Workflow completion checkpoint
        workflow_completion_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Workflow Completion",
            description="Checkpoint at workflow completion with results",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.MANUAL,
            trigger_conditions=["workflow_completion", "quality_gate_passed"],
            retention_policy={
                "max_age_days": 180,
                "max_count": 100,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="workflow",
            keywords=["workflow", "completion", "results", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "workflow-completion.json"
        checkpoint_content = self._create_workflow_completion_checkpoint_content(workflow_completion_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(workflow_completion_checkpoint)
        
        return checkpoints
    
    def _create_milestone_checkpoints(self, checkpoints_dir: Path) -> List[CheckpointDefinition]:
        """Create milestone checkpoints."""
        checkpoints = []
        
        # Quality gate milestone checkpoint
        quality_gate_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Quality Gate Milestone",
            description="Checkpoint at quality gate milestones",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.MILESTONE,
            trigger_conditions=["quality_gate_passed", "task_completed"],
            retention_policy={
                "max_age_days": 365,
                "max_count": 500,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="milestone",
            keywords=["milestone", "quality-gate", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "quality-gate-milestone.json"
        checkpoint_content = self._create_quality_gate_milestone_checkpoint_content(quality_gate_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(quality_gate_checkpoint)
        
        # Learning milestone checkpoint
        learning_milestone_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Learning Milestone",
            description="Checkpoint at learning and decision milestones",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.MILESTONE,
            trigger_conditions=["learning_captured", "decision_recorded"],
            retention_policy={
                "max_age_days": 365,
                "max_count": 1000,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=False,
            compression=True,
            category="milestone",
            keywords=["milestone", "learning", "decision", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "learning-milestone.json"
        checkpoint_content = self._create_learning_milestone_checkpoint_content(learning_milestone_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(learning_milestone_checkpoint)
        
        return checkpoints
    
    def _create_quality_checkpoints(self, checkpoints_dir: Path) -> List[CheckpointDefinition]:
        """Create quality checkpoints."""
        checkpoints = []
        
        # Quality validation checkpoint
        quality_validation_checkpoint = CheckpointDefinition(
            name="APM (Agent Project Manager) Quality Validation",
            description="Checkpoint before quality validation",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.AUTO,
            trigger_conditions=["pre_quality_validation", "work_item_validation"],
            retention_policy={
                "max_age_days": 30,
                "max_count": 200,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=True,
            compression=True,
            category="quality",
            keywords=["quality", "validation", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / "quality-validation.json"
        checkpoint_content = self._create_quality_validation_checkpoint_content(quality_validation_checkpoint)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(quality_validation_checkpoint)
        
        return checkpoints
    
    def _create_project_checkpoints(self, checkpoints_dir: Path, project_id: int) -> List[CheckpointDefinition]:
        """Create project-specific checkpoints."""
        checkpoints = []
        
        # Project state checkpoint
        project_state_checkpoint = CheckpointDefinition(
            name=f"APM (Agent Project Manager) Project {project_id} State",
            description=f"Checkpoint for project {project_id} state",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.MANUAL,
            trigger_conditions=[f"project_{project_id}_state_change"],
            retention_policy={
                "max_age_days": 90,
                "max_count": 100,
                "auto_cleanup": True
            },
            auto_create=False,
            auto_restore=False,
            compression=True,
            category="project",
            keywords=[f"project-{project_id}", "state", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / f"project-{project_id}-state.json"
        checkpoint_content = self._create_project_state_checkpoint_content(project_state_checkpoint, project_id)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(project_state_checkpoint)
        
        return checkpoints
    
    def _create_workflow_step_checkpoints(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        checkpoints_dir: Path
    ) -> List[CheckpointDefinition]:
        """Create workflow step checkpoints."""
        checkpoints = []
        
        # Workflow step checkpoint
        workflow_step_checkpoint = CheckpointDefinition(
            name=f"APM (Agent Project Manager) {workflow_name} Step",
            description=f"Checkpoint for {workflow_name} workflow steps",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.AUTO,
            trigger_conditions=[f"{workflow_name}_step_completed"],
            retention_policy={
                "max_age_days": 60,
                "max_count": 200,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=True,
            compression=True,
            category="workflow",
            keywords=[workflow_name, "step", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / f"{workflow_name}-step.json"
        checkpoint_content = self._create_workflow_step_checkpoint_content(workflow_step_checkpoint, workflow_name, workflow_info)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(workflow_step_checkpoint)
        
        return checkpoints
    
    def _create_workflow_validation_checkpoints(
        self,
        workflow_name: str,
        workflow_info: Dict[str, Any],
        checkpoints_dir: Path
    ) -> List[CheckpointDefinition]:
        """Create workflow validation checkpoints."""
        checkpoints = []
        
        # Workflow validation checkpoint
        workflow_validation_checkpoint = CheckpointDefinition(
            name=f"APM (Agent Project Manager) {workflow_name} Validation",
            description=f"Checkpoint for {workflow_name} workflow validation",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.AUTO,
            trigger_conditions=[f"{workflow_name}_validation"],
            retention_policy={
                "max_age_days": 30,
                "max_count": 100,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=True,
            compression=True,
            category="workflow",
            keywords=[workflow_name, "validation", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / f"{workflow_name}-validation.json"
        checkpoint_content = self._create_workflow_validation_checkpoint_content(workflow_validation_checkpoint, workflow_name, workflow_info)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(workflow_validation_checkpoint)
        
        return checkpoints
    
    def _create_agent_task_checkpoints(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        checkpoints_dir: Path
    ) -> List[CheckpointDefinition]:
        """Create agent task checkpoints."""
        checkpoints = []
        
        # Agent task checkpoint
        agent_task_checkpoint = CheckpointDefinition(
            name=f"APM (Agent Project Manager) {agent_role} Task",
            description=f"Checkpoint for {agent_role} agent tasks",
            component_type=ClaudeCodeComponentType.CHECKPOINT,
            checkpoint_type=CheckpointType.AUTO,
            trigger_conditions=[f"{agent_role}_task_completed"],
            retention_policy={
                "max_age_days": 60,
                "max_count": 200,
                "auto_cleanup": True
            },
            auto_create=True,
            auto_restore=True,
            compression=True,
            category="agent",
            keywords=[agent_role, "task", "aipm"]
        )
        
        checkpoint_file = checkpoints_dir / f"{agent_role}-task.json"
        checkpoint_content = self._create_agent_task_checkpoint_content(agent_task_checkpoint, agent_role, agent_capabilities)
        checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
        checkpoints.append(agent_task_checkpoint)
        
        return checkpoints
    
    def _create_agent_capability_checkpoints(
        self,
        agent_role: str,
        agent_capabilities: List[str],
        checkpoints_dir: Path
    ) -> List[CheckpointDefinition]:
        """Create agent capability checkpoints."""
        checkpoints = []
        
        for capability in agent_capabilities:
            capability_checkpoint = CheckpointDefinition(
                name=f"APM (Agent Project Manager) {agent_role} {capability}",
                description=f"Checkpoint for {agent_role} {capability} capability",
                component_type=ClaudeCodeComponentType.CHECKPOINT,
                checkpoint_type=CheckpointType.AUTO,
                trigger_conditions=[f"{agent_role}_{capability}_completed"],
                retention_policy={
                    "max_age_days": 60,
                    "max_count": 200,
                    "auto_cleanup": True
                },
                auto_create=True,
                auto_restore=True,
                compression=True,
                category="capability",
                keywords=[agent_role, capability, "aipm"]
            )
            
            checkpoint_file = checkpoints_dir / f"{agent_role}-{capability}.json"
            checkpoint_content = self._create_agent_capability_checkpoint_content(capability_checkpoint, agent_role, capability)
            checkpoint_file.write_text(json.dumps(checkpoint_content, indent=2))
            checkpoints.append(capability_checkpoint)
        
        return checkpoints
    
    def create_checkpoint(
        self,
        checkpoint_name: str,
        checkpoint_data: Dict[str, Any],
        checkpoint_type: CheckpointType = CheckpointType.MANUAL
    ) -> bool:
        """
        Create a checkpoint with given data.
        
        Args:
            checkpoint_name: Name of the checkpoint
            checkpoint_data: Data to checkpoint
            checkpoint_type: Type of checkpoint
            
        Returns:
            True if checkpoint created successfully, False otherwise
        """
        try:
            # Create checkpoint directory
            checkpoint_dir = self._checkpoint_storage / checkpoint_name
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Create checkpoint metadata
            checkpoint_metadata = {
                "name": checkpoint_name,
                "type": checkpoint_type.value,
                "created_at": datetime.now().isoformat(),
                "data": checkpoint_data
            }
            
            # Write checkpoint data
            checkpoint_file = checkpoint_dir / "checkpoint.json"
            if checkpoint_type == CheckpointType.MANUAL and self._check_compression_enabled():
                # Compress checkpoint data
                compressed_data = gzip.compress(json.dumps(checkpoint_metadata).encode())
                checkpoint_file.write_bytes(compressed_data)
            else:
                checkpoint_file.write_text(json.dumps(checkpoint_metadata, indent=2))
            
            return True
            
        except Exception as e:
            print(f"Error creating checkpoint {checkpoint_name}: {e}")
            return False
    
    def restore_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """
        Restore a checkpoint by name.
        
        Args:
            checkpoint_name: Name of the checkpoint to restore
            
        Returns:
            Checkpoint data if restored successfully, None otherwise
        """
        try:
            checkpoint_dir = self._checkpoint_storage / checkpoint_name
            checkpoint_file = checkpoint_dir / "checkpoint.json"
            
            if not checkpoint_file.exists():
                return None
            
            # Read checkpoint data
            if self._check_compression_enabled():
                # Decompress checkpoint data
                compressed_data = checkpoint_file.read_bytes()
                decompressed_data = gzip.decompress(compressed_data)
                checkpoint_metadata = json.loads(decompressed_data.decode())
            else:
                checkpoint_metadata = json.loads(checkpoint_file.read_text())
            
            return checkpoint_metadata.get("data")
            
        except Exception as e:
            print(f"Error restoring checkpoint {checkpoint_name}: {e}")
            return None
    
    def list_checkpoints(self) -> List[str]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint names
        """
        try:
            if not self._checkpoint_storage.exists():
                return []
            
            return [d.name for d in self._checkpoint_storage.iterdir() if d.is_dir()]
            
        except Exception as e:
            print(f"Error listing checkpoints: {e}")
            return []
    
    def delete_checkpoint(self, checkpoint_name: str) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint to delete
            
        Returns:
            True if checkpoint deleted successfully, False otherwise
        """
        try:
            checkpoint_dir = self._checkpoint_storage / checkpoint_name
            
            if checkpoint_dir.exists():
                shutil.rmtree(checkpoint_dir)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting checkpoint {checkpoint_name}: {e}")
            return False
    
    def cleanup_old_checkpoints(self, max_age_days: int = 30) -> int:
        """
        Cleanup old checkpoints based on age.
        
        Args:
            max_age_days: Maximum age in days for checkpoints
            
        Returns:
            Number of checkpoints cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            
            for checkpoint_dir in self._checkpoint_storage.iterdir():
                if checkpoint_dir.is_dir():
                    checkpoint_file = checkpoint_dir / "checkpoint.json"
                    if checkpoint_file.exists():
                        file_time = checkpoint_file.stat().st_mtime
                        if file_time < cutoff_time:
                            shutil.rmtree(checkpoint_dir)
                            cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up checkpoints: {e}")
            return 0
    
    def _check_compression_enabled(self) -> bool:
        """Check if compression is enabled for checkpoints."""
        # This would typically check a setting or configuration
        return True
    
    # Checkpoint content creation methods
    def _create_session_start_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create session start checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "session_start_time": "{{timestamp}}",
                "aipm_context": "{{aipm_context}}",
                "project_state": "{{project_state}}",
                "agent_state": "{{agent_state}}"
            }
        }
    
    def _create_session_end_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create session end checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "session_end_time": "{{timestamp}}",
                "aipm_state": "{{aipm_state}}",
                "learnings_captured": "{{learnings_captured}}",
                "decisions_recorded": "{{decisions_recorded}}",
                "work_items_completed": "{{work_items_completed}}",
                "tasks_completed": "{{tasks_completed}}"
            }
        }
    
    def _create_workflow_start_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create workflow start checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "workflow_start_time": "{{timestamp}}",
                "work_item_id": "{{work_item_id}}",
                "work_item_type": "{{work_item_type}}",
                "work_item_context": "{{work_item_context}}",
                "required_tasks": "{{required_tasks}}",
                "quality_gates": "{{quality_gates}}"
            }
        }
    
    def _create_workflow_completion_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create workflow completion checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "workflow_completion_time": "{{timestamp}}",
                "work_item_id": "{{work_item_id}}",
                "work_item_status": "{{work_item_status}}",
                "tasks_completed": "{{tasks_completed}}",
                "quality_gates_passed": "{{quality_gates_passed}}",
                "learnings_captured": "{{learnings_captured}}",
                "results": "{{results}}"
            }
        }
    
    def _create_quality_gate_milestone_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create quality gate milestone checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "milestone_time": "{{timestamp}}",
                "quality_gate_type": "{{quality_gate_type}}",
                "quality_gate_status": "{{quality_gate_status}}",
                "validation_results": "{{validation_results}}",
                "compliance_score": "{{compliance_score}}",
                "next_steps": "{{next_steps}}"
            }
        }
    
    def _create_learning_milestone_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create learning milestone checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "milestone_time": "{{timestamp}}",
                "learning_type": "{{learning_type}}",
                "learning_content": "{{learning_content}}",
                "evidence": "{{evidence}}",
                "business_value": "{{business_value}}",
                "confidence_score": "{{confidence_score}}",
                "impact_assessment": "{{impact_assessment}}"
            }
        }
    
    def _create_quality_validation_checkpoint_content(self, checkpoint: CheckpointDefinition) -> Dict[str, Any]:
        """Create quality validation checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "validation_time": "{{timestamp}}",
                "validation_type": "{{validation_type}}",
                "validation_target": "{{validation_target}}",
                "validation_criteria": "{{validation_criteria}}",
                "validation_results": "{{validation_results}}",
                "validation_status": "{{validation_status}}"
            }
        }
    
    def _create_project_state_checkpoint_content(self, checkpoint: CheckpointDefinition, project_id: int) -> Dict[str, Any]:
        """Create project state checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "checkpoint_time": "{{timestamp}}",
                "project_id": project_id,
                "project_state": "{{project_state}}",
                "work_items": "{{work_items}}",
                "tasks": "{{tasks}}",
                "context_quality": "{{context_quality}}",
                "agent_activity": "{{agent_activity}}"
            }
        }
    
    def _create_workflow_step_checkpoint_content(self, checkpoint: CheckpointDefinition, workflow_name: str, workflow_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow step checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "step_time": "{{timestamp}}",
                "workflow_name": workflow_name,
                "step_name": "{{step_name}}",
                "step_status": "{{step_status}}",
                "step_results": "{{step_results}}",
                "next_step": "{{next_step}}",
                "workflow_progress": "{{workflow_progress}}"
            }
        }
    
    def _create_workflow_validation_checkpoint_content(self, checkpoint: CheckpointDefinition, workflow_name: str, workflow_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow validation checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "validation_time": "{{timestamp}}",
                "workflow_name": workflow_name,
                "validation_type": "{{validation_type}}",
                "validation_results": "{{validation_results}}",
                "compliance_status": "{{compliance_status}}",
                "quality_score": "{{quality_score}}"
            }
        }
    
    def _create_agent_task_checkpoint_content(self, checkpoint: CheckpointDefinition, agent_role: str, agent_capabilities: List[str]) -> Dict[str, Any]:
        """Create agent task checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "task_time": "{{timestamp}}",
                "agent_role": agent_role,
                "task_name": "{{task_name}}",
                "task_status": "{{task_status}}",
                "task_results": "{{task_results}}",
                "capabilities_used": "{{capabilities_used}}",
                "quality_metrics": "{{quality_metrics}}"
            }
        }
    
    def _create_agent_capability_checkpoint_content(self, checkpoint: CheckpointDefinition, agent_role: str, capability: str) -> Dict[str, Any]:
        """Create agent capability checkpoint content."""
        return {
            "name": checkpoint.name,
            "description": checkpoint.description,
            "type": checkpoint.checkpoint_type.value,
            "trigger_conditions": checkpoint.trigger_conditions,
            "retention_policy": checkpoint.retention_policy,
            "auto_create": checkpoint.auto_create,
            "auto_restore": checkpoint.auto_restore,
            "compression": checkpoint.compression,
            "category": checkpoint.category,
            "keywords": checkpoint.keywords,
            "checkpoint_data": {
                "capability_time": "{{timestamp}}",
                "agent_role": agent_role,
                "capability": capability,
                "capability_status": "{{capability_status}}",
                "capability_results": "{{capability_results}}",
                "performance_metrics": "{{performance_metrics}}"
            }
        }
