"""
Detection Analysis Models - Database Layer

Pydantic models for static code analysis results.

Architecture:
- Database Layer: Domain models with type safety
- Supports JSON serialization for caching
- Used by Detection Services (Layer 3)

Models:
- FileAnalysis: Single file metrics
- ProjectAnalysis: Aggregated project metrics
- ComplexityReport: Complexity analysis results
- MaintainabilityReport: Maintainability analysis results

Author: APM (Agent Project Manager) Detection Pack
Version: 1.0.0
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, field_validator


class FileAnalysis(BaseModel):
    """
    Analysis results for a single Python file.

    Contains all key metrics for code quality assessment:
    - Line counts (total, code, comments, blanks)
    - Complexity metrics (average, maximum)
    - Function and class counts
    - Maintainability index (0-100 scale)

    Attributes:
        file_path: Absolute path to analyzed file
        total_lines: Total lines in file (including blanks)
        code_lines: Executable code lines only
        comment_lines: Comment and docstring lines
        blank_lines: Empty lines
        complexity_avg: Average cyclomatic complexity
        complexity_max: Maximum cyclomatic complexity
        function_count: Number of functions defined
        class_count: Number of classes defined
        maintainability_index: MI score (0-100, higher is better)
        functions: Detailed function metrics
        classes: Detailed class metrics

    Example:
        >>> analysis = FileAnalysis(
        ...     file_path="/path/to/file.py",
        ...     total_lines=100,
        ...     code_lines=70,
        ...     comment_lines=20,
        ...     blank_lines=10,
        ...     complexity_avg=3.5,
        ...     complexity_max=8,
        ...     function_count=5,
        ...     class_count=2,
        ...     maintainability_index=72.5
        ... )
        >>> print(f"MI: {analysis.maintainability_index:.1f}")
        MI: 72.5
    """
    file_path: str = Field(..., description="Absolute path to file")
    total_lines: int = Field(..., ge=0, description="Total lines in file")
    code_lines: int = Field(..., ge=0, description="Executable code lines")
    comment_lines: int = Field(0, ge=0, description="Comment lines")
    blank_lines: int = Field(0, ge=0, description="Blank lines")
    complexity_avg: float = Field(..., ge=0.0, description="Average cyclomatic complexity")
    complexity_max: int = Field(..., ge=0, description="Maximum cyclomatic complexity")
    function_count: int = Field(..., ge=0, description="Number of functions")
    class_count: int = Field(..., ge=0, description="Number of classes")
    maintainability_index: float = Field(..., ge=0.0, le=100.0, description="MI score (0-100)")
    functions: List[Dict[str, Any]] = Field(default_factory=list, description="Function details")
    classes: List[Dict[str, Any]] = Field(default_factory=list, description="Class details")

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path is absolute."""
        path = Path(v)
        if not path.is_absolute():
            raise ValueError(f"File path must be absolute: {v}")
        return v

    @property
    def is_high_complexity(self) -> bool:
        """Check if file exceeds complexity threshold (>10)."""
        return self.complexity_max > 10

    @property
    def is_low_maintainability(self) -> bool:
        """Check if file is below maintainability threshold (<65)."""
        return self.maintainability_index < 65.0

    @property
    def quality_score(self) -> float:
        """
        Calculate overall quality score (0-100).

        Weighted combination:
        - 60% maintainability index
        - 30% complexity (normalized)
        - 10% code/comment ratio
        """
        # Normalize complexity (lower is better, cap at 20)
        complexity_score = max(0, 100 - (self.complexity_max * 5))

        # Code/comment ratio (target: 3:1, higher ratio is better)
        if self.code_lines > 0:
            comment_ratio = (self.comment_lines / self.code_lines) * 100
            comment_score = min(100, comment_ratio * 3)  # 33% comments = 100 score
        else:
            comment_score = 0

        # Weighted average
        return (
            self.maintainability_index * 0.6 +
            complexity_score * 0.3 +
            comment_score * 0.1
        )


class ProjectAnalysis(BaseModel):
    """
    Aggregated analysis for entire project.

    Contains project-wide metrics and per-file results.

    Attributes:
        project_path: Root path of analyzed project
        total_files: Number of Python files analyzed
        total_lines: Sum of all lines across files
        total_code_lines: Sum of code lines across files
        avg_complexity: Average cyclomatic complexity
        max_complexity: Maximum complexity found
        avg_maintainability: Average maintainability index
        files: List of individual file analyses
        analyzed_at: Timestamp of analysis

    Example:
        >>> analysis = ProjectAnalysis(
        ...     project_path="/path/to/project",
        ...     total_files=10,
        ...     total_lines=1000,
        ...     total_code_lines=700,
        ...     avg_complexity=4.2,
        ...     max_complexity=12,
        ...     avg_maintainability=68.5,
        ...     files=[]
        ... )
        >>> print(f"Analyzed {analysis.total_files} files")
        Analyzed 10 files
    """
    project_path: str = Field(..., description="Root project path")
    total_files: int = Field(..., ge=0, description="Number of files analyzed")
    total_lines: int = Field(..., ge=0, description="Total lines across all files")
    total_code_lines: int = Field(..., ge=0, description="Total code lines")
    avg_complexity: float = Field(..., ge=0.0, description="Average complexity")
    max_complexity: int = Field(..., ge=0, description="Maximum complexity found")
    avg_maintainability: float = Field(..., ge=0.0, le=100.0, description="Average MI")
    files: List[FileAnalysis] = Field(default_factory=list, description="File analyses")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    @field_validator('project_path')
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """Validate project path is absolute."""
        path = Path(v)
        if not path.is_absolute():
            raise ValueError(f"Project path must be absolute: {v}")
        return v

    @property
    def high_complexity_count(self) -> int:
        """Count files with high complexity (>10)."""
        return sum(1 for f in self.files if f.is_high_complexity)

    @property
    def low_maintainability_count(self) -> int:
        """Count files with low maintainability (<65)."""
        return sum(1 for f in self.files if f.is_low_maintainability)

    @property
    def quality_score(self) -> float:
        """Calculate overall project quality score (0-100)."""
        if not self.files:
            return 0.0
        return sum(f.quality_score for f in self.files) / len(self.files)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get human-readable summary of analysis.

        Returns:
            Dictionary with formatted metrics
        """
        return {
            "project": self.project_path,
            "files_analyzed": self.total_files,
            "total_lines": self.total_lines,
            "code_lines": self.total_code_lines,
            "avg_complexity": round(self.avg_complexity, 2),
            "max_complexity": self.max_complexity,
            "avg_maintainability": round(self.avg_maintainability, 1),
            "quality_score": round(self.quality_score, 1),
            "high_complexity_files": self.high_complexity_count,
            "low_maintainability_files": self.low_maintainability_count,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class ComplexityReport(BaseModel):
    """
    Detailed complexity analysis report.

    Identifies high-complexity files and functions for refactoring.

    Attributes:
        threshold: Complexity threshold used (default: 10)
        high_complexity_files: Files exceeding threshold
        hotspots: Top 10 most complex functions
        total_violations: Count of complexity violations

    Example:
        >>> report = ComplexityReport(
        ...     threshold=10,
        ...     high_complexity_files=[],
        ...     hotspots=[],
        ...     total_violations=0
        ... )
    """
    threshold: int = Field(10, ge=1, description="Complexity threshold")
    high_complexity_files: List[FileAnalysis] = Field(
        default_factory=list,
        description="Files exceeding threshold"
    )
    hotspots: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top complex functions"
    )
    total_violations: int = Field(0, ge=0, description="Violation count")

    @property
    def has_violations(self) -> bool:
        """Check if any violations found."""
        return self.total_violations > 0


class MaintainabilityReport(BaseModel):
    """
    Detailed maintainability analysis report.

    Identifies files below maintainability threshold.

    MI Scale:
    - 85-100: Excellent (green)
    - 65-84: Good (yellow)
    - <65: Needs attention (red)

    Attributes:
        threshold: MI threshold used (default: 65.0)
        low_maintainability_files: Files below threshold
        total_violations: Count of violations

    Example:
        >>> report = MaintainabilityReport(
        ...     threshold=65.0,
        ...     low_maintainability_files=[],
        ...     total_violations=0
        ... )
    """
    threshold: float = Field(65.0, ge=0.0, le=100.0, description="MI threshold")
    low_maintainability_files: List[FileAnalysis] = Field(
        default_factory=list,
        description="Files below threshold"
    )
    total_violations: int = Field(0, ge=0, description="Violation count")

    @property
    def has_violations(self) -> bool:
        """Check if any violations found."""
        return self.total_violations > 0
