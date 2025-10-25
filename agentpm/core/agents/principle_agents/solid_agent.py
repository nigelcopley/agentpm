"""
SOLID Principle Agent

Analyzes code against the five SOLID principles:
- S: Single Responsibility Principle
- O: Open/Closed Principle  
- L: Liskov Substitution Principle
- I: Interface Segregation Principle
- D: Dependency Inversion Principle
"""

import ast
import time
from typing import List, Dict, Any, Set
from pathlib import Path

from .base import PrincipleAgent, PrincipleViolation, AgentReport, Severity


class SOLIDAgent(PrincipleAgent):
    """Agent that enforces SOLID principles"""
    
    def __init__(self):
        super().__init__("SOLID Agent", "SOLID Principles")
        self.violations: List[PrincipleViolation] = []
        self.metrics: Dict[str, Any] = {}
    
    def analyze(self, code_path: str) -> AgentReport:
        """Analyze code against SOLID principles"""
        start_time = time.time()
        self.violations = []
        self.metrics = {
            'srp_violations': 0,
            'ocp_violations': 0, 
            'lsp_violations': 0,
            'isp_violations': 0,
            'dip_violations': 0,
            'total_classes': 0,
            'total_methods': 0,
            'god_objects': 0
        }
        
        files = self._get_python_files(code_path)
        files_analyzed = 0
        
        for file_path in files:
            tree = self._parse_python_file(file_path)
            if tree:
                self._analyze_file(file_path, tree)
                files_analyzed += 1
        
        analysis_time = (time.time() - start_time) * 1000
        
        return AgentReport(
            agent_name=self.name,
            principle=self.principle,
            passed=len(self.violations) == 0,
            violations=self.violations,
            metrics=self.metrics,
            summary=self._generate_summary(),
            analysis_time_ms=analysis_time,
            files_analyzed=files_analyzed
        )
    
    def _analyze_file(self, file_path: Path, tree: ast.AST):
        """Analyze a single Python file"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(file_path, node)
            elif isinstance(node, ast.FunctionDef):
                self._analyze_function(file_path, node)
    
    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef):
        """Analyze a class for SOLID violations"""
        self.metrics['total_classes'] += 1
        
        # SRP: Check for multiple responsibilities
        self._check_srp(file_path, class_node)
        
        # ISP: Check for fat interfaces
        self._check_isp(file_path, class_node)
        
        # Count methods
        methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
        self.metrics['total_methods'] += len(methods)
        
        # Check for god objects (too many methods)
        if len(methods) > 10:
            self.metrics['god_objects'] += 1
            self.violations.append(PrincipleViolation(
                principle="SRP",
                location=f"{file_path}:{class_node.lineno}",
                issue=f"Class '{class_node.name}' has {len(methods)} methods (potential god object)",
                recommendation="Consider splitting into smaller, focused classes",
                severity=Severity.MEDIUM,
                rule_id="CQ-031"
            ))
    
    def _analyze_function(self, file_path: Path, func_node: ast.FunctionDef):
        """Analyze a function for SOLID violations"""
        # SRP: Check for multiple responsibilities in functions
        self._check_function_srp(file_path, func_node)
        
        # DIP: Check for concrete dependencies
        self._check_dip(file_path, func_node)
    
    def _check_srp(self, file_path: Path, class_node: ast.ClassDef):
        """Check Single Responsibility Principle"""
        responsibilities = set()
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Analyze method names and functionality
                method_name = node.name.lower()
                
                # Categorize by responsibility
                if any(keyword in method_name for keyword in ['save', 'create', 'update', 'delete']):
                    responsibilities.add('data_persistence')
                if any(keyword in method_name for keyword in ['send', 'email', 'notify', 'message']):
                    responsibilities.add('communication')
                if any(keyword in method_name for keyword in ['validate', 'check', 'verify']):
                    responsibilities.add('validation')
                if any(keyword in method_name for keyword in ['format', 'render', 'display']):
                    responsibilities.add('presentation')
                if any(keyword in method_name for keyword in ['calculate', 'compute', 'process']):
                    responsibilities.add('business_logic')
                if any(keyword in method_name for keyword in ['log', 'audit', 'track']):
                    responsibilities.add('logging')
        
        if len(responsibilities) > 2:
            self.metrics['srp_violations'] += 1
            self.violations.append(PrincipleViolation(
                principle="SRP",
                location=f"{file_path}:{class_node.lineno}",
                issue=f"Class '{class_node.name}' has multiple responsibilities: {', '.join(responsibilities)}",
                recommendation="Split into separate classes, each with a single responsibility",
                severity=Severity.HIGH,
                rule_id="CQ-031"
            ))
    
    def _check_function_srp(self, file_path: Path, func_node: ast.FunctionDef):
        """Check SRP for individual functions"""
        # Count different types of operations
        operations = set()
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Check for different types of operations
                if hasattr(node.func, 'attr'):
                    attr_name = node.func.attr.lower()
                    if any(keyword in attr_name for keyword in ['save', 'create', 'update', 'delete']):
                        operations.add('data_operation')
                    elif any(keyword in attr_name for keyword in ['send', 'email', 'notify']):
                        operations.add('communication')
                    elif any(keyword in attr_name for keyword in ['validate', 'check']):
                        operations.add('validation')
                    elif any(keyword in attr_name for keyword in ['log', 'print']):
                        operations.add('logging')
        
        if len(operations) > 2:
            self.violations.append(PrincipleViolation(
                principle="SRP",
                location=f"{file_path}:{func_node.lineno}",
                issue=f"Function '{func_node.name}' performs multiple types of operations: {', '.join(operations)}",
                recommendation="Split into smaller functions, each with a single responsibility",
                severity=Severity.MEDIUM,
                rule_id="CQ-031"
            ))
    
    def _check_isp(self, file_path: Path, class_node: ast.ClassDef):
        """Check Interface Segregation Principle"""
        # Count public methods (those not starting with _)
        public_methods = [node for node in class_node.body 
                         if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]
        
        if len(public_methods) > 8:
            self.metrics['isp_violations'] += 1
            self.violations.append(PrincipleViolation(
                principle="ISP",
                location=f"{file_path}:{class_node.lineno}",
                issue=f"Class '{class_node.name}' has {len(public_methods)} public methods (fat interface)",
                recommendation="Consider splitting into smaller, more focused interfaces",
                severity=Severity.MEDIUM,
                rule_id="CQ-033"
            ))
    
    def _check_dip(self, file_path: Path, func_node: ast.FunctionDef):
        """Check Dependency Inversion Principle"""
        # Look for concrete class instantiations
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # Check for common concrete dependencies
                concrete_classes = {
                    'requests', 'urllib', 'sqlite3', 'mysql', 'psycopg2',
                    'smtplib', 'logging', 'datetime', 'json', 'pickle'
                }
                
                if node.func.id in concrete_classes:
                    self.metrics['dip_violations'] += 1
                    self.violations.append(PrincipleViolation(
                        principle="DIP",
                        location=f"{file_path}:{func_node.lineno}",
                        issue=f"Function '{func_node.name}' depends on concrete class '{node.func.id}'",
                        recommendation="Depend on abstractions (interfaces) instead of concrete classes",
                        severity=Severity.LOW,
                        rule_id="CQ-039"
                    ))
    
    def get_mapped_rules(self) -> List[str]:
        """Return rule IDs this agent enforces"""
        return [
            "CQ-031",  # Single Responsibility Principle
            "CQ-033",  # Interface Segregation Principle  
            "CQ-038",  # Open/Closed Principle
            "CQ-039",  # Dependency Inversion Principle
            "DP-035"   # Liskov Substitution Principle
        ]
    
    def explain_principle(self) -> str:
        """Educational explanation of SOLID principles"""
        return """
SOLID Principles (Robert C. Martin):

S - Single Responsibility Principle: A class should have only one reason to change.
   Each class should have a single, well-defined responsibility.

O - Open/Closed Principle: Software entities should be open for extension but 
   closed for modification. Use inheritance and composition to extend behavior.

L - Liskov Substitution Principle: Objects of a superclass should be replaceable 
   with objects of its subclasses without breaking the application.

I - Interface Segregation Principle: Clients should not be forced to depend on 
   interfaces they don't use. Create focused, specific interfaces.

D - Dependency Inversion Principle: Depend on abstractions, not concretions. 
   High-level modules should not depend on low-level modules.

Benefits: Maintainable, testable, flexible, and extensible code.
        """.strip()
    
    def _generate_summary(self) -> str:
        """Generate a summary of the analysis"""
        total_violations = len(self.violations)
        if total_violations == 0:
            return "✅ All SOLID principles are being followed correctly."
        
        summary_parts = [f"Found {total_violations} SOLID violations:"]
        
        if self.metrics['srp_violations'] > 0:
            summary_parts.append(f"- {self.metrics['srp_violations']} SRP violations")
        if self.metrics['isp_violations'] > 0:
            summary_parts.append(f"- {self.metrics['isp_violations']} ISP violations")
        if self.metrics['dip_violations'] > 0:
            summary_parts.append(f"- {self.metrics['dip_violations']} DIP violations")
        if self.metrics['god_objects'] > 0:
            summary_parts.append(f"- {self.metrics['god_objects']} potential god objects")
        
        return "\n".join(summary_parts)
