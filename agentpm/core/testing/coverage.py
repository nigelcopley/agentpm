"""
Coverage Calculation System for Category-Specific Testing

Calculates coverage percentages for different testing categories and validates
against category-specific requirements.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .categorization import CodeCategoryDetector, TestingCategory
from .config import load_project_testing_config


@dataclass
class CoverageResult:
    """Result of coverage calculation for a category"""
    category: TestingCategory
    file_count: int
    lines_covered: int
    lines_total: int
    coverage_percent: float
    min_required: float
    meets_requirement: bool
    files: List[str]


class CategoryCoverageCalculator:
    """Calculate coverage for different testing categories"""
    
    def __init__(self, project_path: str):
        """Initialize with project path
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.config = load_project_testing_config(project_path)
        self.detector = CodeCategoryDetector(self.config)
    
    def get_all_source_files(self, extensions: List[str] = None) -> List[str]:
        """Get all source files in the project
        
        Args:
            extensions: List of file extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            List of relative file paths
        """
        if extensions is None:
            extensions = ['.py']  # Default to Python files
        
        source_files = []
        
        for ext in extensions:
            pattern = f"**/*{ext}"
            for file_path in self.project_path.glob(pattern):
                # Skip test files and common exclusions
                if self._should_skip_file(file_path):
                    continue
                
                # Get relative path
                rel_path = file_path.relative_to(self.project_path)
                source_files.append(str(rel_path))
        
        return source_files
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped from coverage calculation
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be skipped
        """
        # Skip test files
        if 'test' in file_path.name.lower():
            return True
        
        # Skip common exclusions
        skip_patterns = [
            '__pycache__',
            '.git',
            '.pytest_cache',
            'node_modules',
            '.venv',
            'venv',
            'env',
            '.env',
            'migrations',
            'static',
            'templates'
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def run_coverage_analysis(self, test_command: str = "pytest") -> Dict[str, any]:
        """Run coverage analysis and return results
        
        Args:
            test_command: Command to run tests (default: pytest)
            
        Returns:
            Coverage results by category
        """
        # Get all source files
        source_files = self.get_all_source_files()
        
        # Run coverage analysis
        coverage_data = self._run_coverage_command(test_command, source_files)
        
        # Calculate category-specific coverage
        return self._calculate_category_coverage(source_files, coverage_data)
    
    def _run_coverage_command(self, test_command: str, source_files: List[str]) -> Dict[str, any]:
        """Run coverage command and parse results
        
        Args:
            test_command: Command to run tests
            source_files: List of source files to analyze
            
        Returns:
            Coverage data from coverage tool
        """
        try:
            # Run coverage with JSON output
            cmd = [
                'python3', '-m', 'coverage', 'run', '--source=.', '-m', 'pytest'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"Warning: Tests failed with return code {result.returncode}")
                print(f"Error: {result.stderr}")
            
            # Get coverage report
            report_cmd = ['python3', '-m', 'coverage', 'json', '-o', '-']
            report_result = subprocess.run(
                report_cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if report_result.returncode == 0:
                return json.loads(report_result.stdout)
            else:
                print(f"Warning: Could not generate coverage report: {report_result.stderr}")
                return {}
                
        except subprocess.TimeoutExpired:
            print("Warning: Coverage analysis timed out")
            return {}
        except Exception as e:
            print(f"Warning: Coverage analysis failed: {e}")
            return {}
    
    def _calculate_category_coverage(
        self, 
        source_files: List[str], 
        coverage_data: Dict[str, any]
    ) -> Dict[str, CoverageResult]:
        """Calculate coverage for each category
        
        Args:
            source_files: List of source files
            coverage_data: Coverage data from coverage tool
            
        Returns:
            Coverage results by category
        """
        results = {}
        
        # Get files by category
        categorized_files = self.detector.categorize_files(source_files)
        
        for category, files in categorized_files.items():
            if not files:
                continue
            
            # Calculate coverage for this category
            lines_covered = 0
            lines_total = 0
            covered_files = []
            
            for file_path in files:
                # Normalize path for coverage data lookup
                normalized_path = file_path.replace('\\', '/')
                
                if normalized_path in coverage_data.get('files', {}):
                    file_coverage = coverage_data['files'][normalized_path]
                    lines_covered += file_coverage.get('summary', {}).get('covered_lines', 0)
                    lines_total += file_coverage.get('summary', {}).get('num_statements', 0)
                    covered_files.append(file_path)
            
            # Calculate coverage percentage
            coverage_percent = (lines_covered / lines_total * 100) if lines_total > 0 else 0.0
            
            # Get minimum required coverage
            min_required = self.detector.get_coverage_requirement(files[0]) if files else 70.0
            
            results[category.value] = CoverageResult(
                category=category,
                file_count=len(files),
                lines_covered=lines_covered,
                lines_total=lines_total,
                coverage_percent=coverage_percent,
                min_required=min_required,
                meets_requirement=coverage_percent >= min_required,
                files=covered_files
            )
        
        return results
    
    def validate_coverage_requirements(self, coverage_results: Dict[str, CoverageResult]) -> Tuple[bool, List[str]]:
        """Validate that all categories meet their coverage requirements
        
        Args:
            coverage_results: Coverage results by category
            
        Returns:
            Tuple of (all_requirements_met, list_of_violations)
        """
        violations = []
        
        for category_name, result in coverage_results.items():
            if not result.meets_requirement:
                violations.append(
                    f"Category '{category_name}' coverage {result.coverage_percent:.1f}% < {result.min_required}% "
                    f"({result.file_count} files)"
                )
        
        return len(violations) == 0, violations
    
    def get_coverage_summary(self, coverage_results: Dict[str, CoverageResult]) -> str:
        """Get human-readable coverage summary
        
        Args:
            coverage_results: Coverage results by category
            
        Returns:
            Formatted summary string
        """
        if not coverage_results:
            return "No coverage data available"
        
        summary_lines = ["Coverage Summary by Category:"]
        summary_lines.append("=" * 50)
        
        total_files = 0
        total_lines_covered = 0
        total_lines = 0
        
        for category_name, result in coverage_results.items():
            status = "✅" if result.meets_requirement else "❌"
            summary_lines.append(
                f"{status} {category_name.replace('_', ' ').title()}: "
                f"{result.coverage_percent:.1f}% ({result.lines_covered}/{result.lines_total} lines, "
                f"{result.file_count} files) - Required: {result.min_required}%"
            )
            
            total_files += result.file_count
            total_lines_covered += result.lines_covered
            total_lines += result.lines_total
        
        # Overall summary
        overall_coverage = (total_lines_covered / total_lines * 100) if total_lines > 0 else 0.0
        summary_lines.append("=" * 50)
        summary_lines.append(f"Overall: {overall_coverage:.1f}% ({total_lines_covered}/{total_lines} lines, {total_files} files)")
        
        return "\n".join(summary_lines)


def category_coverage(project_path: str, category: str) -> Optional[CoverageResult]:
    """Calculate coverage percentage for a specific category
    
    This function is designed to be used by the rules validation system.
    
    Args:
        project_path: Path to project root
        category: Category name (e.g., 'critical_paths', 'user_facing')
        
    Returns:
        CoverageResult object for the category, or None if category not found
    """
    try:
        calculator = CategoryCoverageCalculator(project_path)
        coverage_results = calculator.run_coverage_analysis()
        
        if category in coverage_results:
            return coverage_results[category]
        else:
            return None
            
    except Exception as e:
        print(f"Warning: Could not calculate coverage for category '{category}': {e}")
        return None


def validate_all_categories(project_path: str) -> Tuple[bool, List[str]]:
    """Validate all testing categories meet their requirements
    
    Args:
        project_path: Path to project root
        
    Returns:
        Tuple of (all_requirements_met, list_of_violations)
    """
    try:
        calculator = CategoryCoverageCalculator(project_path)
        coverage_results = calculator.run_coverage_analysis()
        return calculator.validate_coverage_requirements(coverage_results)
    except Exception as e:
        return False, [f"Coverage validation failed: {e}"]


# Example usage
if __name__ == "__main__":
    # Example usage
    project_path = "."
    calculator = CategoryCoverageCalculator(project_path)
    
    # Run coverage analysis
    coverage_results = calculator.run_coverage_analysis()
    
    # Print summary
    print(calculator.get_coverage_summary(coverage_results))
    
    # Validate requirements
    all_met, violations = calculator.validate_coverage_requirements(coverage_results)
    if all_met:
        print("\n✅ All coverage requirements met!")
    else:
        print("\n❌ Coverage requirements not met:")
        for violation in violations:
            print(f"  - {violation}")
