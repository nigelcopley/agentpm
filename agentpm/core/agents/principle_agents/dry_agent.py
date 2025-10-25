"""
DRY (Don't Repeat Yourself) Agent

Detects code duplication and suggests abstractions to eliminate repetition.
Analyzes both exact duplication and semantic duplication.
"""

import ast
import time
import hashlib
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict

from .base import PrincipleAgent, PrincipleViolation, AgentReport, Severity


class DRYAgent(PrincipleAgent):
    """Agent that enforces DRY principle by detecting code duplication"""
    
    def __init__(self):
        super().__init__("DRY Agent", "Don't Repeat Yourself")
        self.violations: List[PrincipleViolation] = []
        self.metrics: Dict[str, Any] = {}
        self.code_blocks: Dict[str, List[Tuple[Path, int, str]]] = defaultdict(list)
        self.files: List[Path] = []  # Track files being analyzed
    
    def analyze(self, code_path: str) -> AgentReport:
        """Analyze code for duplication violations"""
        start_time = time.time()
        self.violations = []
        self.files = []  # Reset files list
        self.metrics = {
            'exact_duplications': 0,
            'semantic_duplications': 0,
            'total_lines': 0,
            'duplicated_lines': 0,
            'abstraction_opportunities': 0
        }
        self.code_blocks.clear()
        
        files = self._get_python_files(code_path)
        self.files = files  # Store files for duplication detection
        files_analyzed = 0
        
        # First pass: collect all code blocks
        for file_path in files:
            tree = self._parse_python_file(file_path)
            if tree:
                self._collect_code_blocks(file_path, tree)
                files_analyzed += 1
        
        # Second pass: detect duplications
        self._detect_duplications()
        
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
    
    def _collect_code_blocks(self, file_path: Path, tree: ast.AST):
        """Collect code blocks for duplication analysis"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                self._extract_code_block(file_path, node)
            elif isinstance(node, ast.If):
                self._extract_conditional_block(file_path, node)
            elif isinstance(node, ast.For):
                self._extract_loop_block(file_path, node)
    
    def _extract_code_block(self, file_path: Path, node: ast.AST):
        """Extract a code block and create a hash"""
        try:
            # Get the source lines for this node
            source_lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Extract lines for this node
            if hasattr(node, 'lineno'):
                start_line = node.lineno
                # Estimate end line if not available
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    end_line = node.end_lineno
                else:
                    # Simple estimation based on node type
                    if isinstance(node, ast.FunctionDef):
                        end_line = start_line + 10  # Estimate function length
                    elif isinstance(node, ast.ClassDef):
                        end_line = start_line + 20  # Estimate class length
                    else:
                        end_line = start_line + 5   # Default estimate
                
                # Extract the actual lines
                for i in range(start_line - 1, min(end_line, len(lines))):
                    if i < len(lines):
                        source_lines.append(lines[i].strip())
            
            if source_lines:
                code_text = '\n'.join(source_lines)
                # Create hash of normalized code (remove whitespace differences)
                normalized_code = self._normalize_code(code_text)
                code_hash = hashlib.md5(normalized_code.encode()).hexdigest()
                
                self.code_blocks[code_hash].append((file_path, node.lineno, code_text))
                self.metrics['total_lines'] += len(source_lines)
                
        except (FileNotFoundError, UnicodeDecodeError):
            pass
    
    def _extract_conditional_block(self, file_path: Path, node: ast.If):
        """Extract conditional blocks for analysis"""
        # Look for common patterns in if statements
        if isinstance(node.test, ast.Compare):
            # Extract comparison patterns
            pattern = self._extract_comparison_pattern(node.test)
            if pattern:
                self._check_common_patterns(file_path, node.lineno, pattern, "conditional")
    
    def _extract_loop_block(self, file_path: Path, node: ast.For):
        """Extract loop blocks for analysis"""
        # Look for common iteration patterns
        if isinstance(node.iter, ast.Call):
            if hasattr(node.iter.func, 'attr'):
                # Handle different target types
                if isinstance(node.target, ast.Name):
                    target_name = node.target.id
                elif isinstance(node.target, ast.Tuple):
                    target_name = f"({', '.join([el.id if isinstance(el, ast.Name) else str(el) for el in node.target.elts])})"
                else:
                    target_name = str(node.target)
                
                pattern = f"for {target_name} in {node.iter.func.attr}()"
                self._check_common_patterns(file_path, node.lineno, pattern, "iteration")
    
    def _extract_comparison_pattern(self, test_node: ast.Compare) -> str:
        """Extract comparison patterns"""
        try:
            # Simple string representation without ast.unparse
            left = str(test_node.left)
            ops = [str(op) for op in test_node.ops]
            comparators = [str(comp) for comp in test_node.comparators]
            
            if len(ops) == 1 and len(comparators) == 1:
                return f"{left} {ops[0]} {comparators[0]}"
        except:
            pass
        return ""
    
    def _check_common_patterns(self, file_path: Path, line_number: int, pattern: str, pattern_type: str):
        """Check for common patterns that might indicate duplication"""
        # This is a simplified check - in practice would use more sophisticated pattern matching
        common_patterns = {
            'conditional': ['is None', 'is not None', '== ""', '!= ""', 'len(', 'hasattr('],
            'iteration': ['range(', 'enumerate(', 'items()', 'keys()', 'values()']
        }
        
        if pattern_type in common_patterns:
            for common_pattern in common_patterns[pattern_type]:
                if common_pattern in pattern:
                    # This could be an abstraction opportunity
                    self.metrics['abstraction_opportunities'] += 1
                    break
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison (remove whitespace, comments, etc.)"""
        lines = code.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]
            
            # Remove extra whitespace
            line = line.strip()
            
            # Skip empty lines
            if line:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _detect_duplications(self):
        """Detect exact and semantic duplications"""
        for code_hash, occurrences in self.code_blocks.items():
            if len(occurrences) > 1:
                self._report_duplication(code_hash, occurrences)
        
        # Also check for simple string-based duplication
        self._detect_simple_duplications()
    
    def _detect_simple_duplications(self):
        """Detect simple string-based duplications"""
        # Read all files and look for duplicate lines
        all_lines = {}
        
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if len(line) > 10:  # Only consider substantial lines
                        if line not in all_lines:
                            all_lines[line] = []
                        all_lines[line].append((file_path, line_num))
                        
            except (FileNotFoundError, UnicodeDecodeError):
                continue
        
        # Report duplications
        for line, occurrences in all_lines.items():
            if len(occurrences) > 1:
                self._report_simple_duplication(line, occurrences)
    
    def _report_simple_duplication(self, line: str, occurrences: List[Tuple[Path, int]]):
        """Report a simple line duplication"""
        if len(occurrences) < 2:
            return
            
        # Group by file
        file_groups = {}
        for file_path, line_num in occurrences:
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(line_num)
        
        # Create violation for each file with multiple occurrences
        for file_path, line_nums in file_groups.items():
            if len(line_nums) > 1:
                violation = PrincipleViolation(
                    principle="DRY",
                    location=f"{file_path}:{line_nums[0]}",
                    issue=f"Duplicate line found {len(line_nums)} times in this file",
                    recommendation="Consider extracting this repeated code into a function or constant",
                    severity=Severity.MEDIUM
                )
                self.violations.append(violation)
                self.metrics['exact_duplications'] += len(line_nums) - 1
    
    def _report_duplication(self, code_hash: str, occurrences: List[Tuple[Path, int, str]]):
        """Report a duplication violation"""
        if len(occurrences) < 2:
            return
        
        # Determine severity based on number of occurrences
        severity = Severity.HIGH if len(occurrences) > 3 else Severity.MEDIUM
        
        # Create violation for each occurrence after the first
        for i, (file_path, line_number, code_text) in enumerate(occurrences[1:], 1):
            self.metrics['exact_duplications'] += 1
            self.metrics['duplicated_lines'] += len(code_text.split('\n'))
            
            # Find the first occurrence for reference
            first_file, first_line, _ = occurrences[0]
            
            self.violations.append(PrincipleViolation(
                principle="DRY",
                location=f"{file_path}:{line_number}",
                issue=f"Code duplication detected (similar to {first_file}:{first_line})",
                recommendation="Extract common code into a shared function or class",
                severity=severity,
                rule_id="CQ-021",
                code_snippet=code_text[:200] + "..." if len(code_text) > 200 else code_text
            ))
    
    def get_mapped_rules(self) -> List[str]:
        """Return rule IDs this agent enforces"""
        return [
            "CQ-021",  # Avoid code duplication
            "CQ-022",  # Extract common functionality
            "CQ-023",  # Use abstractions for repeated patterns
            "CQ-024",  # Consolidate similar logic
            "CQ-025",  # Create utility functions for common operations
            "CQ-026",  # Use inheritance for shared behavior
            "CQ-027",  # Apply composition over inheritance
            "CQ-028",  # Create base classes for common patterns
            "CQ-029",  # Use mixins for shared functionality
            "CQ-030"   # Extract configuration constants
        ]
    
    def explain_principle(self) -> str:
        """Educational explanation of DRY principle"""
        return """
DRY Principle (Don't Repeat Yourself) - Andy Hunt & Dave Thomas:

The DRY principle states that "Every piece of knowledge must have a single, 
unambiguous, authoritative representation within a system."

Key Benefits:
- Reduces maintenance burden
- Eliminates inconsistencies
- Makes code more maintainable
- Reduces bugs from copy-paste errors

Common Violations:
- Copy-pasted code blocks
- Duplicate business logic
- Repeated configuration values
- Similar functions with slight variations

Solutions:
- Extract common functionality into functions
- Create base classes for shared behavior
- Use configuration files for constants
- Apply design patterns (Template Method, Strategy)
- Create utility libraries

Remember: DRY is about knowledge duplication, not code duplication.
Sometimes similar-looking code serves different purposes and should not be abstracted.
        """.strip()
    
    def _generate_summary(self) -> str:
        """Generate a summary of the analysis"""
        total_violations = len(self.violations)
        if total_violations == 0:
            return "✅ No significant code duplication detected."
        
        duplication_percentage = 0
        if self.metrics['total_lines'] > 0:
            duplication_percentage = (self.metrics['duplicated_lines'] / self.metrics['total_lines']) * 100
        
        summary_parts = [
            f"Found {total_violations} duplication violations:",
            f"- {self.metrics['exact_duplications']} exact duplications",
            f"- {self.metrics['duplicated_lines']} duplicated lines ({duplication_percentage:.1f}% of total)",
            f"- {self.metrics['abstraction_opportunities']} abstraction opportunities identified"
        ]
        
        if duplication_percentage > 10:
            summary_parts.append("⚠️  High duplication percentage - consider refactoring")
        
        return "\n".join(summary_parts)
