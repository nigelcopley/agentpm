"""
Claude Code Generator

Generates Claude Code compatible agent files (.claude/agents/*.md) from
database agent records.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from ..base import (
    TemplateBasedGenerator,
    GenerationContext,
)


class ClaudeCodeGenerator(TemplateBasedGenerator):
    """
    Generate Claude Code agent files from database records.

    Output format: .claude/agents/{role}.md
    Template: agent_file.md.j2
    """

    provider_name = "claude-code"
    file_extension = ".md"
    template_name = "agent_file.md.j2"

    def get_output_path(
        self,
        agent_role: str,
        project_path: Optional[Path] = None
    ) -> Path:
        """
        Determine output path for Claude Code agent file.

        Args:
            agent_role: Agent role identifier
            project_path: Optional project root path

        Returns:
            Path: .claude/agents/{role}.md
        """
        if project_path is None:
            project_path = Path.cwd()
        else:
            project_path = Path(project_path)

        # Create .claude/agents/ directory structure
        agents_dir = project_path / '.claude' / 'agents'
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename from role
        # e.g., 'context-delivery' -> 'context-delivery.md'
        filename = f"{agent_role}{self.file_extension}"

        return agents_dir / filename

    def prepare_template_context(
        self,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Prepare context for Claude Code template.

        Adds Claude-specific formatting and structures.
        Maps Agent model fields to template variables.
        """
        base_context = super().prepare_template_context(context)

        # Group rules by category for better organization
        rules_by_category = {}
        for rule in context.project_rules:
            category = getattr(rule, 'category', 'general')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)

        # Extract behavioral rules from agent metadata
        behavioral_rules = []
        if hasattr(context.agent, 'metadata') and context.agent.metadata:
            import json
            try:
                metadata_dict = json.loads(context.agent.metadata) if isinstance(context.agent.metadata, str) else context.agent.metadata
                behavioral_rules = metadata_dict.get('behavioral_rules', [])
            except (json.JSONDecodeError, AttributeError):
                behavioral_rules = []

        # Create agent context with persona mapping
        # Map display_name to persona for template compatibility
        agent_context = base_context['agent']

        # Get agent dict (handle both Pydantic and regular objects)
        if hasattr(agent_context, 'model_dump'):
            agent_dict = agent_context.model_dump()
        else:
            agent_dict = agent_context.__dict__

        agent_with_persona = {
            **agent_dict,
            'persona': context.agent.display_name,  # Map display_name → persona
            'success_metrics': getattr(context.agent, 'sop_content', None),  # SOP as success metrics
        }

        # Add Claude-specific context
        base_context.update({
            'agent': type('Agent', (), agent_with_persona)(),  # Create object with persona
            'rules_by_category': rules_by_category,
            'behavioral_rules': behavioral_rules,
            'agent_type': self._infer_agent_type(context.agent.role),
            'has_universal_rules': bool(context.universal_rules),
        })

        return base_context

    def _infer_agent_type(self, role: str) -> str:
        """
        Infer agent type from role name.

        Args:
            role: Agent role identifier

        Returns:
            Agent type: orchestrator, specialist, utility, or sub-agent
        """
        role_lower = role.lower()

        if 'orch' in role_lower or 'orchestrator' in role_lower:
            return 'orchestrator'
        elif any(word in role_lower for word in ['sub', 'helper', 'assistant']):
            return 'sub-agent'
        elif any(word in role_lower for word in ['writer', 'reader', 'logger', 'validator']):
            return 'utility'
        else:
            return 'specialist'

    def supports_agent_type(self, agent_type: str) -> bool:
        """Claude Code supports all agent types"""
        return True
