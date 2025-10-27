"""
Claude Code Subagents System

Manages Claude Code subagents for APM (Agent Project Manager) integration including agent creation,
specialization, and orchestration.

Based on: https://docs.claude.com/en/docs/claude-code/sub-agents
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.agent import Agent
from agentpm.core.database.enums import AgentTier, AgentFunctionalCategory
from ..models import SubagentDefinition, SubagentCapability, ClaudeCodeComponentType


class ClaudeCodeSubagentsManager:
    """
    Manages Claude Code subagents for APM (Agent Project Manager).
    
    Converts APM (Agent Project Manager) agents into Claude Code subagents with specialized
    capabilities and orchestration.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize subagents manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._subagents_cache: Dict[str, SubagentDefinition] = {}
        self._active_subagents: Dict[str, bool] = {}
    
    def create_subagents_from_agents(
        self,
        agents: List[Agent],
        output_dir: Path
    ) -> List[SubagentDefinition]:
        """
        Create Claude Code subagents from APM (Agent Project Manager) agents.
        
        Args:
            agents: List of APM (Agent Project Manager) agents to convert
            output_dir: Directory to write subagent definitions
            
        Returns:
            List of created SubagentDefinitions
        """
        subagents = []
        
        # Create subagents directory
        subagents_dir = output_dir / "agents"
        subagents_dir.mkdir(parents=True, exist_ok=True)
        
        for agent in agents:
            if not agent.is_active:
                continue
            
            # Create subagent definition
            subagent = self._create_subagent_from_agent(agent, subagents_dir)
            subagents.append(subagent)
            
            # Cache subagent
            self._subagents_cache[agent.role] = subagent
        
        return subagents
    
    def create_specialized_subagents(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[SubagentDefinition]:
        """
        Create specialized APM (Agent Project Manager) subagents for different domains.
        
        Args:
            output_dir: Directory to write subagent definitions
            project_id: Optional project ID for project-specific subagents
            
        Returns:
            List of created SubagentDefinitions
        """
        subagents = []
        
        # Create subagents directory
        subagents_dir = output_dir / "agents"
        subagents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create specialized subagents
        subagents.extend(self._create_project_management_subagents(subagents_dir))
        subagents.extend(self._create_development_subagents(subagents_dir))
        subagents.extend(self._create_quality_assurance_subagents(subagents_dir))
        subagents.extend(self._create_analysis_subagents(subagents_dir))
        
        # Create project-specific subagents if project_id provided
        if project_id:
            subagents.extend(self._create_project_specific_subagents(subagents_dir, project_id))
        
        return subagents
    
    def create_orchestrator_subagent(
        self,
        output_dir: Path,
        managed_subagents: List[str]
    ) -> SubagentDefinition:
        """
        Create orchestrator subagent to manage other subagents.
        
        Args:
            output_dir: Directory to write subagent definition
            managed_subagents: List of subagent roles to manage
            
        Returns:
            SubagentDefinition for the orchestrator
        """
        # Create subagents directory
        subagents_dir = output_dir / "agents"
        subagents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create orchestrator subagent
        orchestrator = SubagentDefinition(
            name="APM (Agent Project Manager) Orchestrator",
            description="APM (Agent Project Manager) orchestrator subagent for managing specialized subagents and workflows",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="orchestrator",
            capabilities=[
                SubagentCapability.ANALYSIS,
                SubagentCapability.CODE_REVIEW,
                SubagentCapability.DEBUGGING
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=True,
            priority=100,
            max_concurrent=1,
            category="orchestration",
            keywords=["orchestration", "management", "coordination", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write orchestrator definition
        orchestrator_file = subagents_dir / "orchestrator.md"
        orchestrator_content = self._create_orchestrator_definition(orchestrator, managed_subagents)
        orchestrator_file.write_text(orchestrator_content)
        
        # Cache orchestrator
        self._subagents_cache["orchestrator"] = orchestrator
        
        return orchestrator
    
    def _create_subagent_from_agent(
        self,
        agent: Agent,
        output_dir: Path
    ) -> SubagentDefinition:
        """Create subagent definition from APM (Agent Project Manager) agent."""
        # Map agent capabilities to subagent capabilities
        subagent_capabilities = self._map_agent_capabilities(agent.capabilities)

        # Determine auto-invoke based on functional category or tier
        auto_invoke = self._get_auto_invoke_from_category(agent.functional_category, agent.tier)

        # Determine priority based on functional category (preferred) or tier (fallback)
        priority = self._get_priority_from_category(agent.functional_category, agent.tier)

        # Get category string for subagent
        category = self._get_category_string(agent.functional_category, agent.tier)

        # Create subagent definition
        subagent = SubagentDefinition(
            name=agent.display_name,
            description=agent.description or f"APM (Agent Project Manager) {agent.display_name} subagent",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role=agent.role,
            capabilities=subagent_capabilities,
            tools=self._get_tools_for_capabilities(agent.capabilities),
            auto_invoke=auto_invoke,
            priority=priority,
            max_concurrent=1,
            category=category,
            keywords=[agent.role] + agent.capabilities,
            source_agent_id=agent.id,
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Write subagent definition
        subagent_file = output_dir / f"{agent.role}.md"
        subagent_content = self._create_subagent_definition(subagent, agent)
        subagent_file.write_text(subagent_content)
        
        return subagent
    
    def _create_project_management_subagents(self, output_dir: Path) -> List[SubagentDefinition]:
        """Create project management subagents."""
        subagents = []
        
        # Project Manager subagent
        project_manager = SubagentDefinition(
            name="APM (Agent Project Manager) Project Manager",
            description="APM (Agent Project Manager) project management subagent for work items, tasks, and quality gates",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="project-manager",
            capabilities=[
                SubagentCapability.ANALYSIS,
                SubagentCapability.CODE_REVIEW
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=90,
            max_concurrent=1,
            category="project-management",
            keywords=["project-management", "work-items", "tasks", "quality-gates", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "project-manager.md"
        subagent_content = self._create_project_manager_definition(project_manager)
        subagent_file.write_text(subagent_content)
        subagents.append(project_manager)
        
        # Work Item Manager subagent
        work_item_manager = SubagentDefinition(
            name="APM (Agent Project Manager) Work Item Manager",
            description="APM (Agent Project Manager) work item management subagent for features, bugs, and enhancements",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="work-item-manager",
            capabilities=[
                SubagentCapability.ANALYSIS,
                SubagentCapability.CODE_REVIEW
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=85,
            max_concurrent=1,
            category="project-management",
            keywords=["work-items", "features", "bugs", "enhancements", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "work-item-manager.md"
        subagent_content = self._create_work_item_manager_definition(work_item_manager)
        subagent_file.write_text(subagent_content)
        subagents.append(work_item_manager)
        
        return subagents
    
    def _create_development_subagents(self, output_dir: Path) -> List[SubagentDefinition]:
        """Create development subagents."""
        subagents = []
        
        # Rapid Prototyper subagent
        rapid_prototyper = SubagentDefinition(
            name="APM (Agent Project Manager) Rapid Prototyper",
            description="APM (Agent Project Manager) rapid prototyping subagent for MVP development with time constraints",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="rapid-prototyper",
            capabilities=[
                SubagentCapability.CODE_GENERATION,
                SubagentCapability.REFACTORING
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=80,
            max_concurrent=2,
            category="development",
            keywords=["rapid-prototyping", "mvp", "time-constrained", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "rapid-prototyper.md"
        subagent_content = self._create_rapid_prototyper_definition(rapid_prototyper)
        subagent_file.write_text(subagent_content)
        subagents.append(rapid_prototyper)
        
        # Enterprise Architect subagent
        enterprise_architect = SubagentDefinition(
            name="APM (Agent Project Manager) Enterprise Architect",
            description="APM (Agent Project Manager) enterprise architecture subagent for large systems and compliance",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="enterprise-architect",
            capabilities=[
                SubagentCapability.ANALYSIS,
                SubagentCapability.CODE_REVIEW,
                SubagentCapability.REFACTORING
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=75,
            max_concurrent=1,
            category="architecture",
            keywords=["enterprise", "architecture", "compliance", "large-systems", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "enterprise-architect.md"
        subagent_content = self._create_enterprise_architect_definition(enterprise_architect)
        subagent_file.write_text(subagent_content)
        subagents.append(enterprise_architect)
        
        return subagents
    
    def _create_quality_assurance_subagents(self, output_dir: Path) -> List[SubagentDefinition]:
        """Create quality assurance subagents."""
        subagents = []
        
        # Quality Engineer subagent
        quality_engineer = SubagentDefinition(
            name="APM (Agent Project Manager) Quality Engineer",
            description="APM (Agent Project Manager) quality engineering subagent for testing and quality assurance",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="quality-engineer",
            capabilities=[
                SubagentCapability.TESTING,
                SubagentCapability.CODE_REVIEW,
                SubagentCapability.DEBUGGING
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=70,
            max_concurrent=2,
            category="quality",
            keywords=["quality", "testing", "assurance", "coverage", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "quality-engineer.md"
        subagent_content = self._create_quality_engineer_definition(quality_engineer)
        subagent_file.write_text(subagent_content)
        subagents.append(quality_engineer)
        
        # Production Specialist subagent
        production_specialist = SubagentDefinition(
            name="APM (Agent Project Manager) Production Specialist",
            description="APM (Agent Project Manager) production specialist subagent for bug fixes and incident response",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="production-specialist",
            capabilities=[
                SubagentCapability.DEBUGGING,
                SubagentCapability.CODE_REVIEW,
                SubagentCapability.TESTING
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=95,
            max_concurrent=1,
            category="production",
            keywords=["production", "bug-fixes", "incident-response", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "production-specialist.md"
        subagent_content = self._create_production_specialist_definition(production_specialist)
        subagent_file.write_text(subagent_content)
        subagents.append(production_specialist)
        
        return subagents
    
    def _create_analysis_subagents(self, output_dir: Path) -> List[SubagentDefinition]:
        """Create analysis subagents."""
        subagents = []
        
        # Research Engineer subagent
        research_engineer = SubagentDefinition(
            name="APM (Agent Project Manager) Research Engineer",
            description="APM (Agent Project Manager) research engineering subagent for technology evaluation and proof of concept",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role="research-engineer",
            capabilities=[
                SubagentCapability.RESEARCH,
                SubagentCapability.ANALYSIS,
                SubagentCapability.CODE_GENERATION
            ],
            tools=["Read", "Write", "Bash", "Grep", "Glob"],
            auto_invoke=False,
            priority=60,
            max_concurrent=1,
            category="research",
            keywords=["research", "technology-evaluation", "proof-of-concept", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / "research-engineer.md"
        subagent_content = self._create_research_engineer_definition(research_engineer)
        subagent_file.write_text(subagent_content)
        subagents.append(research_engineer)
        
        return subagents
    
    def _create_project_specific_subagents(
        self,
        output_dir: Path,
        project_id: int
    ) -> List[SubagentDefinition]:
        """Create project-specific subagents."""
        subagents = []
        
        # Project Context subagent
        project_context = SubagentDefinition(
            name=f"APM (Agent Project Manager) Project {project_id} Context",
            description=f"APM (Agent Project Manager) project {project_id} context subagent for project-specific knowledge",
            component_type=ClaudeCodeComponentType.SUBAGENT,
            role=f"project-{project_id}-context",
            capabilities=[
                SubagentCapability.ANALYSIS,
                SubagentCapability.RESEARCH
            ],
            tools=["Read", "Grep", "Glob"],
            auto_invoke=False,
            priority=50,
            max_concurrent=1,
            category="project",
            keywords=[f"project-{project_id}", "context", "knowledge", "aipm"],
            version="1.0.0",
            author="APM (Agent Project Manager)",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subagent_file = output_dir / f"project-{project_id}-context.md"
        subagent_content = self._create_project_context_definition(project_context, project_id)
        subagent_file.write_text(subagent_content)
        subagents.append(project_context)
        
        return subagents
    
    def _map_agent_capabilities(self, agent_capabilities: List[str]) -> List[SubagentCapability]:
        """Map APM (Agent Project Manager) agent capabilities to subagent capabilities."""
        capability_mapping = {
            "python": [SubagentCapability.CODE_GENERATION, SubagentCapability.REFACTORING],
            "database": [SubagentCapability.CODE_GENERATION, SubagentCapability.ANALYSIS],
            "testing": [SubagentCapability.TESTING, SubagentCapability.DEBUGGING],
            "documentation": [SubagentCapability.DOCUMENTATION],
            "analysis": [SubagentCapability.ANALYSIS, SubagentCapability.RESEARCH],
            "debugging": [SubagentCapability.DEBUGGING, SubagentCapability.CODE_REVIEW],
            "refactoring": [SubagentCapability.REFACTORING, SubagentCapability.CODE_REVIEW],
            "research": [SubagentCapability.RESEARCH, SubagentCapability.ANALYSIS]
        }
        
        subagent_capabilities = set()
        for capability in agent_capabilities:
            if capability.lower() in capability_mapping:
                subagent_capabilities.update(capability_mapping[capability.lower()])
        
        return list(subagent_capabilities) if subagent_capabilities else [SubagentCapability.ANALYSIS]
    
    def _get_tools_for_capabilities(self, capabilities: List[str]) -> List[str]:
        """Get tools for agent capabilities."""
        tool_mapping = {
            "python": ["Read", "Write", "Bash", "Grep", "Glob"],
            "database": ["Read", "Write", "Bash", "Grep"],
            "testing": ["Read", "Write", "Bash", "Grep", "Glob"],
            "documentation": ["Read", "Write", "Grep", "Glob"],
            "analysis": ["Read", "Grep", "Glob"],
            "debugging": ["Read", "Write", "Bash", "Grep", "Glob"],
            "refactoring": ["Read", "Write", "Bash", "Grep", "Glob"],
            "research": ["Read", "Grep", "Glob"]
        }
        
        tools = set()
        for capability in capabilities:
            if capability.lower() in tool_mapping:
                tools.update(tool_mapping[capability.lower()])
        
        return list(tools) if tools else ["Read", "Write", "Bash", "Grep", "Glob"]
    
    def _get_priority_from_category(
        self,
        functional_category: Optional[AgentFunctionalCategory],
        tier: Optional[AgentTier]
    ) -> int:
        """Get priority from agent functional category (preferred) or tier (fallback)."""
        # Use functional_category if available
        if functional_category:
            category_priorities = {
                AgentFunctionalCategory.PLANNING: 90,      # High priority - orchestrators
                AgentFunctionalCategory.IMPLEMENTATION: 75, # Medium-high - builders
                AgentFunctionalCategory.TESTING: 70,       # Medium - verifiers
                AgentFunctionalCategory.DOCUMENTATION: 60,  # Medium-low - writers
                AgentFunctionalCategory.UTILITIES: 50,     # Low - support
            }
            return category_priorities.get(functional_category, 50)

        # Fallback to tier (deprecated)
        if tier == AgentTier.TIER_3:  # Master/Orchestrator
            return 100
        elif tier == AgentTier.TIER_2:  # Specialist
            return 75
        else:  # SUB_AGENT (TIER_1)
            return 50

    def _get_auto_invoke_from_category(
        self,
        functional_category: Optional[AgentFunctionalCategory],
        tier: Optional[AgentTier]
    ) -> bool:
        """Determine auto-invoke based on functional category or tier."""
        # Use functional_category if available
        if functional_category:
            # Only planning agents (orchestrators) auto-invoke
            return functional_category == AgentFunctionalCategory.PLANNING

        # Fallback to tier (deprecated)
        return tier == AgentTier.TIER_3 if tier else False

    def _get_category_string(
        self,
        functional_category: Optional[AgentFunctionalCategory],
        tier: Optional[AgentTier]
    ) -> str:
        """Get category string from functional category (preferred) or tier (fallback)."""
        if functional_category:
            return functional_category.value

        # Fallback to tier (deprecated)
        if tier == AgentTier.TIER_3:
            return "orchestration"
        elif tier == AgentTier.TIER_2:
            return "specialist"
        else:
            return "sub-agent"
    
    def _create_subagent_definition(
        self,
        subagent: SubagentDefinition,
        agent: Agent
    ) -> str:
        """Create subagent definition content."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: {subagent.role}

This subagent provides {subagent.role.replace('-', ' ')} capabilities within the APM (Agent Project Manager) framework.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Standard Operating Procedure

{agent.sop_content or "No SOP available."}

## Usage

This subagent is {'automatically invoked' if subagent.auto_invoke else 'manually invoked'} when tasks require {subagent.role.replace('-', ' ')} capabilities.

## APM (Agent Project Manager) Integration

- **Source Agent ID**: {agent.id}
- **Agent Capabilities**: {', '.join(agent.capabilities)}
- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
"""
    
    def _create_orchestrator_definition(
        self,
        orchestrator: SubagentDefinition,
        managed_subagents: List[str]
    ) -> str:
        """Create orchestrator subagent definition."""
        return f"""---
name: {orchestrator.name}
description: {orchestrator.description}
role: {orchestrator.role}
capabilities: {[cap.value for cap in orchestrator.capabilities]}
tools: {orchestrator.tools}
auto_invoke: {str(orchestrator.auto_invoke).lower()}
priority: {orchestrator.priority}
max_concurrent: {orchestrator.max_concurrent}
---

# {orchestrator.name}

{orchestrator.description}

## Role: Orchestrator

This subagent orchestrates and coordinates other specialized subagents within the APM (Agent Project Manager) framework.

## Managed Subagents

{chr(10).join(f"- {subagent}" for subagent in managed_subagents)}

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in orchestrator.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in orchestrator.tools)}

## Orchestration Strategy

1. **Analyze Request**: Determine which subagents are needed
2. **Coordinate Execution**: Manage subagent invocation and coordination
3. **Synthesize Results**: Combine outputs from multiple subagents
4. **Quality Assurance**: Ensure all quality gates are met

## Usage

This orchestrator is automatically invoked for complex tasks requiring multiple subagents.

## APM (Agent Project Manager) Integration

- **Priority**: {orchestrator.priority} (highest)
- **Max Concurrent**: {orchestrator.max_concurrent}
- **Auto Invoke**: {orchestrator.auto_invoke}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Coordinate subagent execution
"""
    
    def _create_project_manager_definition(self, subagent: SubagentDefinition) -> str:
        """Create project manager subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Project Manager

This subagent manages APM (Agent Project Manager) project management workflows including work items, tasks, and quality gates.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Project Management Functions

1. **Work Item Management**: Create, update, and manage work items
2. **Task Management**: Create tasks with proper time-boxing
3. **Quality Gate Enforcement**: Ensure compliance with APM (Agent Project Manager) standards
4. **Dependency Management**: Track and manage work item dependencies
5. **Context Assembly**: Provide hierarchical project context

## Usage

Use this subagent when you need project management capabilities or when working with APM (Agent Project Manager) workflows.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
"""
    
    def _create_work_item_manager_definition(self, subagent: SubagentDefinition) -> str:
        """Create work item manager subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Work Item Manager

This subagent specializes in APM (Agent Project Manager) work item management including features, bugs, enhancements, and research.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Work Item Functions

1. **Feature Management**: Create and manage feature work items
2. **Bug Management**: Handle bug reports and fixes
3. **Enhancement Management**: Manage enhancement requests
4. **Research Management**: Handle research and analysis work items
5. **Dependency Tracking**: Manage work item dependencies

## Work Item Types

- **FEATURE**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT**: DESIGN + IMPLEMENTATION + TESTING
- **BUGFIX**: ANALYSIS + BUGFIX + TESTING
- **RESEARCH**: RESEARCH + ANALYSIS + DOCUMENTATION

## Usage

Use this subagent when working with work items or when you need work item management capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
"""
    
    def _create_rapid_prototyper_definition(self, subagent: SubagentDefinition) -> str:
        """Create rapid prototyper subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Rapid Prototyper

This subagent specializes in rapid prototyping and MVP development with strict time constraints.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Rapid Prototyping Functions

1. **MVP Development**: Create minimum viable products quickly
2. **Time-Constrained Development**: Work within strict time limits
3. **Prototype Generation**: Generate working prototypes rapidly
4. **Iterative Development**: Focus on core functionality first
5. **Quick Validation**: Validate ideas and concepts quickly

## Development Principles

- **Make it Work**: Focus on functionality over perfection
- **Time-Boxing**: Strict adherence to time limits
- **Core Features First**: Implement essential features only
- **Iterative Improvement**: Build, test, iterate quickly

## Usage

Use this subagent for MVP development, time-critical projects, or when you need rapid prototyping capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Focus on core functionality
"""
    
    def _create_enterprise_architect_definition(self, subagent: SubagentDefinition) -> str:
        """Create enterprise architect subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Enterprise Architect

This subagent specializes in enterprise architecture, large systems design, and compliance requirements.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Enterprise Architecture Functions

1. **System Design**: Design large, complex systems
2. **Architecture Review**: Review and validate system architectures
3. **Compliance Management**: Ensure compliance with enterprise standards
4. **Scalability Planning**: Plan for system scalability and growth
5. **Integration Design**: Design system integrations and APIs

## Architecture Principles

- **Scalability**: Design for growth and scale
- **Maintainability**: Ensure long-term maintainability
- **Security**: Implement enterprise-grade security
- **Compliance**: Meet regulatory and enterprise requirements
- **Performance**: Optimize for enterprise performance needs

## Usage

Use this subagent for large system design, architecture reviews, or when you need enterprise-level capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Ensure enterprise compliance
"""
    
    def _create_quality_engineer_definition(self, subagent: SubagentDefinition) -> str:
        """Create quality engineer subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Quality Engineer

This subagent specializes in quality assurance, testing, and ensuring APM (Agent Project Manager) quality standards.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Quality Engineering Functions

1. **Test Development**: Create comprehensive test suites
2. **Quality Assurance**: Ensure code quality and standards
3. **Coverage Analysis**: Maintain >90% test coverage
4. **Code Review**: Review code for quality and standards
5. **Debugging**: Debug and fix quality issues

## Quality Standards

- **Test Coverage**: >90% coverage required
- **Code Quality**: Follow APM (Agent Project Manager) coding standards
- **Security**: Ensure security best practices
- **Performance**: Validate performance requirements
- **Documentation**: Ensure comprehensive documentation

## Usage

Use this subagent for testing, quality assurance, or when you need quality engineering capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Maintain >90% test coverage
"""
    
    def _create_production_specialist_definition(self, subagent: SubagentDefinition) -> str:
        """Create production specialist subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Production Specialist

This subagent specializes in production issues, bug fixes, and incident response.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Production Functions

1. **Bug Fixes**: Quickly identify and fix production bugs
2. **Incident Response**: Respond to production incidents
3. **Hotfixes**: Deploy critical fixes to production
4. **Monitoring**: Monitor production systems and health
5. **Recovery**: Recover from production failures

## Production Principles

- **Safety First**: Ensure production stability
- **Minimal Change**: Make minimal changes to fix issues
- **Rapid Resolution**: Resolve issues as quickly as possible
- **Rollback Ready**: Always be ready to rollback changes
- **Documentation**: Document all production changes

## Usage

Use this subagent for production issues, bug fixes, or when you need production support capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority} (high for production issues)
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Ensure production stability
"""
    
    def _create_research_engineer_definition(self, subagent: SubagentDefinition) -> str:
        """Create research engineer subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Research Engineer

This subagent specializes in research, technology evaluation, and proof of concept development.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Research Functions

1. **Technology Evaluation**: Evaluate new technologies and frameworks
2. **Proof of Concept**: Create proof of concept implementations
3. **Research Analysis**: Analyze research findings and trends
4. **Innovation**: Explore innovative solutions and approaches
5. **Documentation**: Document research findings and recommendations

## Research Principles

- **Evidence-Based**: Base decisions on research evidence
- **Innovation**: Explore new and innovative approaches
- **Documentation**: Thoroughly document research findings
- **Validation**: Validate research findings through experimentation
- **Knowledge Sharing**: Share research knowledge with the team

## Usage

Use this subagent for research tasks, technology evaluation, or when you need research capabilities.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Document research findings
"""
    
    def _create_project_context_definition(
        self,
        subagent: SubagentDefinition,
        project_id: int
    ) -> str:
        """Create project context subagent definition."""
        return f"""---
name: {subagent.name}
description: {subagent.description}
role: {subagent.role}
capabilities: {[cap.value for cap in subagent.capabilities]}
tools: {subagent.tools}
auto_invoke: {str(subagent.auto_invoke).lower()}
priority: {subagent.priority}
max_concurrent: {subagent.max_concurrent}
---

# {subagent.name}

{subagent.description}

## Role: Project Context Specialist

This subagent provides project-specific context and knowledge for APM (Agent Project Manager) project {project_id}.

## Capabilities

{chr(10).join(f"- {cap.value}" for cap in subagent.capabilities)}

## Tools Available

{chr(10).join(f"- {tool}" for tool in subagent.tools)}

## Project Context Functions

1. **Context Assembly**: Assemble project-specific context
2. **Knowledge Management**: Manage project knowledge and decisions
3. **Pattern Recognition**: Recognize project-specific patterns
4. **Context Delivery**: Deliver context to other subagents
5. **Knowledge Sharing**: Share project knowledge across the team

## Project-Specific Knowledge

- **Project ID**: {project_id}
- **Project Context**: Project-specific context and knowledge
- **Historical Decisions**: Past decisions and their rationale
- **Patterns**: Project-specific patterns and conventions
- **Dependencies**: Project dependencies and relationships

## Usage

Use this subagent when you need project-specific context or knowledge for APM (Agent Project Manager) project {project_id}.

## APM (Agent Project Manager) Integration

- **Priority**: {subagent.priority}
- **Max Concurrent**: {subagent.max_concurrent}
- **Category**: {subagent.category}
- **Project ID**: {project_id}

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence
- Maintain project context accuracy
"""
