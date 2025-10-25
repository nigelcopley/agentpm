"""
R1 Quality Gate Integration for Principle-Based Agents

Integrates principle-based agents with the APM (Agent Project Manager) R1 quality gate system.
Provides seamless integration with ReviewTestOrch and quality-gatekeeper.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import time

from .registry import get_registry
from .base import AgentReport, PrincipleViolation, Severity


class R1PrincipleAgentIntegration:
    """
    Integrates principle-based agents with R1 quality gate validation.
    
    This class provides the bridge between the principle agent system
    and the existing APM (Agent Project Manager) quality gate infrastructure.
    """
    
    def __init__(self):
        self.registry = get_registry()
        self.enabled_agents = ['solid', 'dry', 'kiss']  # MVP agents
        self.severity_threshold = Severity.MEDIUM  # Only report MEDIUM and HIGH violations
    
    def analyze_for_r1_gate(self, code_path: str, project_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze code for R1 quality gate validation.
        
        Args:
            code_path: Path to code to analyze
            project_context: Optional project context for framework-specific analysis
            
        Returns:
            R1 gate compatible result dictionary
        """
        start_time = time.time()
        
        # Run principle agent analysis
        agent_reports = self.registry.analyze_with_selected_agents(
            self.enabled_agents, 
            code_path
        )
        
        # Convert to R1 gate format
        r1_result = self._convert_to_r1_format(agent_reports, project_context)
        
        analysis_time = (time.time() - start_time) * 1000
        r1_result['analysis_time_ms'] = analysis_time
        
        return r1_result
    
    def _convert_to_r1_format(self, agent_reports: Dict[str, AgentReport], project_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert agent reports to R1 gate compatible format"""
        
        # Aggregate results
        total_violations = 0
        high_severity_violations = 0
        medium_severity_violations = 0
        all_violations = []
        principle_scores = {}
        overall_passed = True
        
        for agent_name, report in agent_reports.items():
            # Count violations by severity
            agent_violations = [v for v in report.violations if v.severity.value in ['HIGH', 'MEDIUM']]
            total_violations += len(agent_violations)
            
            high_count = len([v for v in agent_violations if v.severity == Severity.HIGH])
            medium_count = len([v for v in agent_violations if v.severity == Severity.MEDIUM])
            
            high_severity_violations += high_count
            medium_severity_violations += medium_count
            
            # Add violations to aggregate list
            all_violations.extend(agent_violations)
            
            # Calculate principle score (0-100, higher is better)
            principle_score = self._calculate_principle_score(report)
            principle_scores[agent_name] = principle_score
            
            # Overall pass if no high severity violations
            if high_count > 0:
                overall_passed = False
        
        # Generate R1 gate result
        r1_result = {
            'gate': 'R1_PRINCIPLE_AGENTS',
            'status': 'PASS' if overall_passed else 'FAIL',
            'passed': overall_passed,
            'summary': self._generate_r1_summary(principle_scores, total_violations, high_severity_violations),
            'violations': self._format_violations_for_r1(all_violations),
            'principle_scores': principle_scores,
            'metrics': {
                'total_violations': total_violations,
                'high_severity': high_severity_violations,
                'medium_severity': medium_severity_violations,
                'agents_run': len(agent_reports),
                'files_analyzed': sum(r.files_analyzed for r in agent_reports.values()),
                'average_analysis_time': sum(r.analysis_time_ms for r in agent_reports.values()) / len(agent_reports) if agent_reports else 0
            },
            'agent_reports': {
                name: {
                    'principle': report.principle,
                    'passed': report.passed,
                    'violations_count': len([v for v in report.violations if v.severity.value in ['HIGH', 'MEDIUM']]),
                    'summary': report.summary,
                    'analysis_time_ms': report.analysis_time_ms
                }
                for name, report in agent_reports.items()
            }
        }
        
        return r1_result
    
    def _calculate_principle_score(self, report: AgentReport) -> int:
        """Calculate a principle score (0-100) based on violations"""
        if not report.violations:
            return 100
        
        # Weight violations by severity
        total_penalty = 0
        for violation in report.violations:
            if violation.severity == Severity.HIGH:
                total_penalty += 20
            elif violation.severity == Severity.MEDIUM:
                total_penalty += 10
            else:  # LOW
                total_penalty += 5
        
        # Cap penalty at 100
        total_penalty = min(total_penalty, 100)
        
        return max(0, 100 - total_penalty)
    
    def _generate_r1_summary(self, principle_scores: Dict[str, int], total_violations: int, high_severity: int) -> str:
        """Generate summary for R1 gate"""
        if total_violations == 0:
            return "✅ All principle-based quality checks passed"
        
        if high_severity > 0:
            return f"❌ {high_severity} high-severity principle violations found"
        
        return f"⚠️  {total_violations} principle violations found (no high-severity issues)"
    
    def _format_violations_for_r1(self, violations: List[PrincipleViolation]) -> List[Dict[str, Any]]:
        """Format violations for R1 gate consumption"""
        formatted_violations = []
        
        for violation in violations:
            formatted_violations.append({
                'principle': violation.principle,
                'severity': violation.severity.value,
                'location': violation.location,
                'issue': violation.issue,
                'recommendation': violation.recommendation,
                'rule_id': violation.rule_id,
                'confidence': violation.confidence
            })
        
        # Sort by severity (HIGH first)
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        formatted_violations.sort(key=lambda v: severity_order.get(v['severity'], 3))
        
        return formatted_violations
    
    def get_principle_agent_status(self) -> Dict[str, Any]:
        """Get status of principle agents for R1 gate"""
        health_status = self.registry.validate_agent_health()
        agent_info = self.registry.get_agent_info()
        
        return {
            'enabled_agents': self.enabled_agents,
            'total_agents': len(agent_info),
            'healthy_agents': sum(1 for healthy in health_status.values() if healthy),
            'agent_health': health_status,
            'agent_info': agent_info
        }
    
    def configure_agents(self, enabled_agents: List[str], severity_threshold: str = 'MEDIUM'):
        """Configure which agents to run and severity threshold"""
        self.enabled_agents = enabled_agents
        self.severity_threshold = Severity(severity_threshold)
    
    def get_rule_mappings(self) -> Dict[str, List[str]]:
        """Get rule mappings for enabled agents"""
        all_mappings = self.registry.get_rule_mappings()
        return {agent: rules for agent, rules in all_mappings.items() if agent in self.enabled_agents}


class QualityGatekeeperEnhancement:
    """
    Enhancement for the existing quality-gatekeeper to include principle agents.
    
    This class provides methods to integrate principle agent results
    with existing quality gate validation.
    """
    
    def __init__(self):
        self.principle_integration = R1PrincipleAgentIntegration()
    
    def enhance_r1_validation(self, existing_results: Dict[str, Any], code_path: str) -> Dict[str, Any]:
        """
        Enhance existing R1 validation with principle agent results.
        
        Args:
            existing_results: Results from existing R1 gate checks
            code_path: Path to code for principle analysis
            
        Returns:
            Enhanced R1 validation results
        """
        # Run principle agent analysis
        principle_results = self.principle_integration.analyze_for_r1_gate(code_path)
        
        # Merge with existing results
        enhanced_results = existing_results.copy()
        
        # Add principle agent results
        enhanced_results['principle_agents'] = principle_results
        
        # Update overall status if principle agents failed
        if not principle_results['passed'] and enhanced_results.get('status') == 'PASS':
            enhanced_results['status'] = 'FAIL'
            enhanced_results['passed'] = False
        
        # Add principle violations to overall violations
        if 'violations' not in enhanced_results:
            enhanced_results['violations'] = []
        
        enhanced_results['violations'].extend(principle_results['violations'])
        
        # Update summary
        if principle_results['violations']:
            principle_summary = f" | Principle Agents: {principle_results['summary']}"
            enhanced_results['summary'] = enhanced_results.get('summary', '') + principle_summary
        
        return enhanced_results
    
    def get_principle_agent_metrics(self) -> Dict[str, Any]:
        """Get metrics about principle agent performance"""
        return self.principle_integration.get_principle_agent_status()


# Global instance for easy access
_r1_integration: Optional[R1PrincipleAgentIntegration] = None
_quality_gatekeeper_enhancement: Optional[QualityGatekeeperEnhancement] = None


def get_r1_integration() -> R1PrincipleAgentIntegration:
    """Get the global R1 integration instance"""
    global _r1_integration
    if _r1_integration is None:
        _r1_integration = R1PrincipleAgentIntegration()
    return _r1_integration


def get_quality_gatekeeper_enhancement() -> QualityGatekeeperEnhancement:
    """Get the global quality gatekeeper enhancement instance"""
    global _quality_gatekeeper_enhancement
    if _quality_gatekeeper_enhancement is None:
        _quality_gatekeeper_enhancement = QualityGatekeeperEnhancement()
    return _quality_gatekeeper_enhancement
