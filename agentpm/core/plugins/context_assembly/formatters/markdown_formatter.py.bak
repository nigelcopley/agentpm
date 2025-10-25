"""
Markdown Formatter - Universal Markdown Output

Provides platform-agnostic markdown formatting for context assembly.
This is a universal formatter that works across all AI platforms.
"""

from typing import List, Dict, Any
from datetime import datetime

from agentpm.core.context.assembly_service import ContextPayload
from agentpm.core.database.models.context import UnifiedSixW


class MarkdownFormatter:
    """
    Universal markdown formatter for context assembly.
    
    Provides structured markdown output that is readable by any AI platform
    without platform-specific optimizations.
    """
    
    def format_task_context(self, payload: ContextPayload) -> str:
        """
        Format task context as markdown.
        
        Args:
            payload: Context payload to format
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        # Task header
        task = payload.task
        lines.append(f"**Task #{task.get('id')}**: {task.get('name')} "
                    f"({task.get('type')}, {task.get('effort_hours')}h)")
        lines.append(f"**Work Item**: WI-{task.get('work_item_id')}")
        
        if payload.assigned_agent:
            lines.append(f"**Agent**: {payload.assigned_agent}")
        
        lines.append("")
        
        # Merged 6W context
        if payload.merged_6w:
            lines.extend(self._format_6w_context(payload.merged_6w))
        
        # Plugin facts (tech stack)
        if payload.plugin_facts:
            lines.extend(self._format_plugin_facts(payload.plugin_facts))
        
        # Agent SOP
        if payload.agent_sop:
            lines.append("### 📝 Agent SOP")
            lines.append("")
            lines.append(payload.agent_sop[:500] + "..." if len(payload.agent_sop) > 500 else payload.agent_sop)
            lines.append("")
        
        # Temporal context
        if payload.temporal_context:
            lines.extend(self._format_temporal_context(payload.temporal_context))
        
        # Confidence score
        lines.append(f"**Context Confidence**: {payload.confidence_score:.0%} "
                    f"({payload.confidence_band.value.upper()})")
        lines.append(f"**Assembly Time**: {payload.assembly_time_ms:.0f}ms")
        
        # Warnings
        if payload.warnings:
            lines.append("")
            lines.append("⚠️ **Warnings**:")
            for warning in payload.warnings[:3]:
                lines.append(f"- {warning}")
        
        lines.append("")
        return "\n".join(lines)
    
    def format_session_context(self, contexts: List[ContextPayload]) -> str:
        """
        Format session context as markdown.
        
        Args:
            contexts: List of context payloads
            
        Returns:
            Formatted markdown string
        """
        lines = []
        
        lines.append("## 🎯 Project Context Loaded")
        lines.append("")
        lines.append(f"**Session Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        if contexts:
            lines.append("### 🎯 Current Task Context")
            lines.append("")
            
            for context in contexts:
                lines.append(self.format_task_context(context))
        
        return "\n".join(lines)
    
    def _format_6w_context(self, merged_6w: UnifiedSixW) -> List[str]:
        """Format merged 6W context as markdown."""
        lines = []
        lines.append("### 🔍 Merged Context (Task → Work Item → Project)")
        lines.append("")
        
        if merged_6w.who:
            lines.append(f"**WHO**: {merged_6w.who}")
        if merged_6w.what:
            lines.append(f"**WHAT**: {merged_6w.what}")
        if merged_6w.when:
            lines.append(f"**WHEN**: {merged_6w.when}")
        if merged_6w.where:
            lines.append(f"**WHERE**: {merged_6w.where}")
        if merged_6w.why:
            lines.append(f"**WHY**: {merged_6w.why}")
        if merged_6w.how:
            lines.append(f"**HOW**: {merged_6w.how}")
        
        lines.append("")
        return lines
    
    def _format_plugin_facts(self, plugin_facts: Dict[str, Any]) -> List[str]:
        """Format plugin facts as markdown."""
        lines = []
        lines.append("### 🔌 Tech Stack")
        lines.append("")
        
        for framework, facts in plugin_facts.items():
            if isinstance(facts, dict) and 'version' in facts:
                lines.append(f"- {framework}: {facts.get('version')}")
            else:
                lines.append(f"- {framework}")
        
        lines.append("")
        return lines
    
    def _format_temporal_context(self, temporal_context: List[Dict[str, Any]]) -> List[str]:
        """Format temporal context as markdown."""
        lines = []
        lines.append("### 🕒 Recent Sessions")
        lines.append("")
        
        for summary in temporal_context[:3]:
            text = summary.get('summary_text', '')
            created = summary.get('created_at')
            
            if created:
                delta = datetime.now() - created
                hours_ago = int(delta.total_seconds() / 3600)
                time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{delta.days}d ago"
                lines.append(f"- {time_str}: \"{text[:60]}...\"" if len(text) > 60 else f"- {time_str}: \"{text}\"")
            else:
                lines.append(f"- {text[:60]}..." if len(text) > 60 else f"- {text}")
        
        lines.append("")
        return lines


