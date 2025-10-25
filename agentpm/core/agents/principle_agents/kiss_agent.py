"""
KISS (Keep It Simple, Stupid) Agent

Measures code complexity and suggests simplifications.
Analyzes cyclomatic complexity, function length, nesting depth, and other complexity metrics.
"""

import ast
import time
from typing import List, Dict, Any, Set
from pathlib import Path

from .base import PrincipleAgent, PrincipleViolation, AgentReport, Severity


class KISSAgent(PrincipleAgent):
    """Agent that enforces KISS principle by measuring and reducing complexity"""
    
    def __init__(self):
        super().__init__("KISS Agent", "Keep It Simple, Stupid")
        self.violations: List[PrincipleViolation] = []
        self.metrics: Dict[str, Any] = {}
    
    def analyze(self, code_path: str) -> AgentReport:
        """Analyze code for complexity violations"""
        start_time = time.time()
        self.violations = []
        self.metrics = {
            'high_complexity_functions': 0,
            'long_functions': 0,
            'deep_nesting': 0,
            'complex_conditionals': 0,
            'total_functions': 0,
            'total_classes': 0,
            'average_complexity': 0,
            'max_complexity': 0
        }
        
        files = self._get_python_files(code_path)
        files_analyzed = 0
        complexity_scores = []
        
        for file_path in files:
            tree = self._parse_python_file(file_path)
            if tree:
                self._analyze_file(file_path, tree, complexity_scores)
                files_analyzed += 1
        
        # Calculate average complexity
        if complexity_scores:
            self.metrics['average_complexity'] = sum(complexity_scores) / len(complexity_scores)
            self.metrics['max_complexity'] = max(complexity_scores)
        
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
    
    def _analyze_file(self, file_path: Path, tree: ast.AST, complexity_scores: List[int]):
        """Analyze a single Python file for complexity"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(file_path, node, complexity_scores)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(file_path, node)
    
    def _analyze_function(self, file_path: Path, func_node: ast.FunctionDef, complexity_scores: List[int]):
        """Analyze a function for complexity violations"""
        self.metrics['total_functions'] += 1
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(func_node)
        complexity_scores.append(complexity)
        
        # Check for high complexity
        if complexity > 10:
            self.metrics['high_complexity_functions'] += 1
            severity = Severity.HIGH if complexity > 15 else Severity.MEDIUM
            
            self.violations.append(PrincipleViolation(
                principle="KISS",
                location=f"{file_path}:{func_node.lineno}",
                issue=f"Function '{func_node.name}' has high cyclomatic complexity ({complexity})",
                recommendation="Break down into smaller, simpler functions",
                severity=severity,
                rule_id="CQ-041"
            ))
        
        # Check function length
        function_length = self._get_function_length(func_node)
        if function_length > 50:
            self.metrics['long_functions'] += 1
            severity = Severity.HIGH if function_length > 100 else Severity.MEDIUM
            
            self.violations.append(PrincipleViolation(
                principle="KISS",
                location=f"{file_path}:{func_node.lineno}",
                issue=f"Function '{func_node.name}' is too long ({function_length} lines)",
                recommendation="Split into smaller functions with single responsibilities",
                severity=severity,
                rule_id="CQ-042"
            ))
        
        # Check nesting depth
        max_nesting = self._get_max_nesting_depth(func_node)
        if max_nesting > 4:
            self.metrics['deep_nesting'] += 1
            
            self.violations.append(PrincipleViolation(
                principle="KISS",
                location=f"{file_path}:{func_node.lineno}",
                issue=f"Function '{func_node.name}' has deep nesting ({max_nesting} levels)",
                recommendation="Extract nested blocks into separate functions or use early returns",
                severity=Severity.MEDIUM,
                rule_id="CQ-043"
            ))
        
        # Check for complex conditionals
        complex_conditionals = self._find_complex_conditionals(func_node)
        if complex_conditionals:
            self.metrics['complex_conditionals'] += len(complex_conditionals)
            
            for line_number in complex_conditionals:
                self.violations.append(PrincipleViolation(
                    principle="KISS",
                    location=f"{file_path}:{line_number}",
                    issue="Complex conditional expression detected",
                    recommendation="Extract complex conditions into well-named boolean variables or functions",
                    severity=Severity.LOW,
                    rule_id="CQ-044"
                ))
    
    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef):
        """Analyze a class for complexity"""
        self.metrics['total_classes'] += 1
        
        # Check class size (number of methods)
        methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
        if len(methods) > 15:
            self.violations.append(PrincipleViolation(
                principle="KISS",
                location=f"{file_path}:{class_node.lineno}",
                issue=f"Class '{class_node.name}' has too many methods ({len(methods)})",
                recommendation="Consider splitting into smaller, more focused classes",
                severity=Severity.MEDIUM,
                rule_id="CQ-045"
            ))
    
    def _calculate_cyclomatic_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # Each boolean operator adds complexity
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Compare):
                # Each comparison operator adds complexity
                complexity += len(node.ops)
        
        return complexity
    
    def _get_function_length(self, func_node: ast.FunctionDef) -> int:
        """Get the length of a function in lines"""
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            return func_node.end_lineno - func_node.lineno + 1
        else:
            # Fallback: count body nodes
            return len(func_node.body)
    
    def _get_max_nesting_depth(self, func_node: ast.FunctionDef) -> int:
        """Get the maximum nesting depth in a function"""
        max_depth = 0
        
        def check_nesting(node: ast.AST, current_depth: int):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                    check_nesting(child, current_depth + 1)
                else:
                    check_nesting(child, current_depth)
        
        check_nesting(func_node, 0)
        return max_depth
    
    def _find_complex_conditionals(self, func_node: ast.FunctionDef) -> List[int]:
        """Find complex conditional expressions"""
        complex_lines = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                # Check if the condition is complex
                if self._is_complex_condition(node.test):
                    complex_lines.append(node.lineno)
            elif isinstance(node, ast.BoolOp):
                # Check for complex boolean operations
                if len(node.values) > 2:
                    complex_lines.append(node.lineno)
        
        return complex_lines
    
    def _is_complex_condition(self, condition_node: ast.AST) -> bool:
        """Check if a condition is complex"""
        # Count the number of operations in the condition
        operation_count = 0
        
        for node in ast.walk(condition_node):
            if isinstance(node, (ast.Compare, ast.BoolOp, ast.UnaryOp)):
                operation_count += 1
        
        # Consider complex if more than 3 operations
        return operation_count > 3
    
    def get_mapped_rules(self) -> List[str]:
        """Return rule IDs this agent enforces"""
        return [
            "CQ-041",  # Keep functions simple and focused
            "CQ-042",  # Limit function length
            "CQ-043",  # Avoid deep nesting
            "CQ-044",  # Simplify complex conditionals
            "CQ-045",  # Keep classes focused
            "CQ-046",  # Use clear, descriptive names
            "CQ-047",  # Avoid unnecessary abstractions
            "CQ-048",  # Prefer composition over inheritance
            "CQ-049",  # Use simple data structures
            "CQ-050"   # Minimize cognitive load
        ]
    
    def explain_principle(self) -> str:
        """Educational explanation of KISS principle"""
        return """
KISS Principle (Keep It Simple, Stupid) - Kelly Johnson:

The KISS principle states that systems work best when they are kept simple 
rather than made complex. Simplicity should be a key goal and unnecessary 
complexity should be avoided.

Key Metrics:
- Cyclomatic Complexity: Should be ≤ 10 per function
- Function Length: Should be ≤ 50 lines
- Nesting Depth: Should be ≤ 4 levels
- Class Size: Should be ≤ 15 methods

Benefits of Simplicity:
- Easier to understand and maintain
- Fewer bugs and errors
- Faster development and testing
- Better performance
- Easier to debug and modify

Common Complexity Sources:
- Long functions with multiple responsibilities
- Deep nesting and complex conditionals
- Over-engineering and premature optimization
- Unnecessary abstractions
- Complex inheritance hierarchies

Solutions:
- Break large functions into smaller ones
- Use early returns to reduce nesting
- Extract complex conditions into variables
- Prefer composition over inheritance
- Use simple data structures
- Write self-documenting code

Remember: Simple doesn't mean simplistic. It means the most direct 
solution that meets the requirements.
        """.strip()
    
    def _generate_summary(self) -> str:
        """Generate a summary of the analysis"""
        total_violations = len(self.violations)
        if total_violations == 0:
            return "✅ Code complexity is within acceptable limits."
        
        summary_parts = [
            f"Found {total_violations} complexity violations:",
            f"- {self.metrics['high_complexity_functions']} high complexity functions",
            f"- {self.metrics['long_functions']} long functions",
            f"- {self.metrics['deep_nesting']} functions with deep nesting",
            f"- {self.metrics['complex_conditionals']} complex conditionals"
        ]
        
        if self.metrics['average_complexity'] > 8:
            summary_parts.append(f"⚠️  High average complexity: {self.metrics['average_complexity']:.1f}")
        
        if self.metrics['max_complexity'] > 15:
            summary_parts.append(f"🚨 Very high maximum complexity: {self.metrics['max_complexity']}")
        
        return "\n".join(summary_parts)
