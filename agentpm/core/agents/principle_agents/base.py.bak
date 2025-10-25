"""
Base Classes for Principle-Based Agents

Provides the foundation for all principle-based agents that analyze code
against specific software engineering principles and patterns.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import ast
import os
from pathlib import Path


class Severity(Enum):
    """Severity levels for principle violations"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PrincipleViolation:
    """Represents a violation of a software engineering principle"""
    principle: str
    location: str  # file:line
    issue: str
    recommendation: str
    severity: Severity
    rule_id: Optional[str] = None  # Maps to rules catalog
    code_snippet: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class AgentReport:
    """Report from a principle agent analysis"""
    agent_name: str
    principle: str
    passed: bool
    violations: List[PrincipleViolation]
    metrics: Dict[str, Any]
    summary: str
    analysis_time_ms: float
    files_analyzed: int


class PrincipleAgent(ABC):
    """Base class for principle-based agents"""
    
    def __init__(self, name: str, principle: str):
        self.name = name
        self.principle = principle
    
    @abstractmethod
    def analyze(self, code_path: str) -> AgentReport:
        """
        Analyze code against the principle.
        
        Args:
            code_path: Path to code file or directory
            
        Returns:
            AgentReport with violations and metrics
        """
        pass
    
    @abstractmethod
    def get_mapped_rules(self) -> List[str]:
        """Return rule IDs this agent enforces"""
        pass
    
    @abstractmethod
    def explain_principle(self) -> str:
        """Educational explanation of the principle"""
        pass
    
    def _get_python_files(self, path: str) -> List[Path]:
        """Get all Python files in a directory"""
        path_obj = Path(path)
        if path_obj.is_file() and path_obj.suffix == '.py':
            return [path_obj]
        elif path_obj.is_dir():
            return list(path_obj.rglob('*.py'))
        return []
    
    def _parse_python_file(self, file_path: Path) -> Optional[ast.AST]:
        """Parse a Python file into an AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            return None
    
    def _get_line_number(self, node: ast.AST) -> int:
        """Get line number for an AST node"""
        return getattr(node, 'lineno', 0)
    
    def _get_source_line(self, file_path: Path, line_number: int) -> Optional[str]:
        """Get source code line by line number"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 1 <= line_number <= len(lines):
                    return lines[line_number - 1].strip()
        except (FileNotFoundError, UnicodeDecodeError):
            pass
        return None
