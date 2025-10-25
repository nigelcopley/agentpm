"""
Principle Agent Registry

Manages the collection of principle-based agents and provides
integration with the APM (Agent Project Manager) quality gate system.
"""

from typing import Dict, List, Type, Optional, Any
from pathlib import Path

from .base import PrincipleAgent, AgentReport
from .solid_agent import SOLIDAgent
from .dry_agent import DRYAgent
from .kiss_agent import KISSAgent


class PrincipleAgentRegistry:
    """Registry for managing principle-based agents"""
    
    def __init__(self):
        self._agents: Dict[str, PrincipleAgent] = {}
        self._agent_classes: Dict[str, Type[PrincipleAgent]] = {
            'solid': SOLIDAgent,
            'dry': DRYAgent,
            'kiss': KISSAgent,
        }
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        for name, agent_class in self._agent_classes.items():
            self._agents[name] = agent_class()
    
    def get_agent(self, name: str) -> Optional[PrincipleAgent]:
        """Get an agent by name"""
        return self._agents.get(name)
    
    def get_all_agents(self) -> Dict[str, PrincipleAgent]:
        """Get all registered agents"""
        return self._agents.copy()
    
    def get_agent_names(self) -> List[str]:
        """Get list of all agent names"""
        return list(self._agents.keys())
    
    def analyze_with_agent(self, agent_name: str, code_path: str) -> Optional[AgentReport]:
        """Analyze code with a specific agent"""
        agent = self.get_agent(agent_name)
        if agent:
            return agent.analyze(code_path)
        return None
    
    def analyze_with_all_agents(self, code_path: str) -> Dict[str, AgentReport]:
        """Analyze code with all available agents"""
        reports = {}
        for name, agent in self._agents.items():
            try:
                reports[name] = agent.analyze(code_path)
            except Exception as e:
                # Create error report
                reports[name] = AgentReport(
                    agent_name=name,
                    principle=agent.principle,
                    passed=False,
                    violations=[],
                    metrics={'error': str(e)},
                    summary=f"Analysis failed: {str(e)}",
                    analysis_time_ms=0,
                    files_analyzed=0
                )
        return reports
    
    def analyze_with_selected_agents(self, agent_names: List[str], code_path: str) -> Dict[str, AgentReport]:
        """Analyze code with selected agents only"""
        reports = {}
        for name in agent_names:
            if name in self._agents:
                try:
                    reports[name] = self._agents[name].analyze(code_path)
                except Exception as e:
                    reports[name] = AgentReport(
                        agent_name=name,
                        principle=self._agents[name].principle,
                        passed=False,
                        violations=[],
                        metrics={'error': str(e)},
                        summary=f"Analysis failed: {str(e)}",
                        analysis_time_ms=0,
                        files_analyzed=0
                    )
        return reports
    
    def get_rule_mappings(self) -> Dict[str, List[str]]:
        """Get rule mappings for all agents"""
        mappings = {}
        for name, agent in self._agents.items():
            mappings[name] = agent.get_mapped_rules()
        return mappings
    
    def get_principle_explanations(self) -> Dict[str, str]:
        """Get principle explanations for all agents"""
        explanations = {}
        for name, agent in self._agents.items():
            explanations[name] = agent.explain_principle()
        return explanations
    
    def get_agent_info(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive information about all agents"""
        info = {}
        for name, agent in self._agents.items():
            info[name] = {
                'name': agent.name,
                'principle': agent.principle,
                'mapped_rules': agent.get_mapped_rules(),
                'explanation': agent.explain_principle()
            }
        return info
    
    def register_agent(self, name: str, agent: PrincipleAgent):
        """Register a new agent"""
        self._agents[name] = agent
    
    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent"""
        if name in self._agents:
            del self._agents[name]
            return True
        return False
    
    def get_agents_for_framework(self, framework: str) -> List[str]:
        """Get agents that are relevant for a specific framework"""
        # This could be extended to have framework-specific agent selection
        # For now, return all agents
        return list(self._agents.keys())
    
    def get_agents_for_phase(self, phase: str) -> List[str]:
        """Get agents that are relevant for a specific development phase"""
        phase_mappings = {
            'design': ['solid', 'kiss'],
            'implementation': ['solid', 'dry', 'kiss'],
            'testing': ['solid', 'kiss'],
            'review': ['solid', 'dry', 'kiss'],
            'refactoring': ['solid', 'dry', 'kiss']
        }
        return phase_mappings.get(phase, list(self._agents.keys()))
    
    def get_priority_agents(self) -> List[str]:
        """Get high-priority agents for MVP"""
        return ['solid', 'dry', 'kiss']
    
    def validate_agent_health(self) -> Dict[str, bool]:
        """Validate that all agents are working correctly"""
        health_status = {}
        for name, agent in self._agents.items():
            try:
                # Try to analyze a simple test case
                test_code = "def test(): pass"
                agent.analyze(test_code)
                health_status[name] = True
            except Exception:
                health_status[name] = False
        return health_status


# Global registry instance
_global_registry: Optional[PrincipleAgentRegistry] = None


def get_registry() -> PrincipleAgentRegistry:
    """Get the global principle agent registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = PrincipleAgentRegistry()
    return _global_registry


def reset_registry():
    """Reset the global registry (mainly for testing)"""
    global _global_registry
    _global_registry = None
