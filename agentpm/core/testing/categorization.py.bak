"""
Code Categorization System for Testing

Automatically categorizes code files into testing categories for value-based testing.
Each category has different coverage requirements based on business value.

Categories:
- Critical Paths (95% coverage): Core business logic
- User-Facing Code (85% coverage): APIs, CLI, web interfaces
- Data Layer (90% coverage): Database, models, storage
- Security (95% coverage): Authentication, validation, crypto
- Utilities (70% coverage): Helper functions, common utilities
- Framework Integration (50% coverage): External framework code
"""

import json
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class TestingCategory(Enum):
    """Testing categories with different coverage requirements"""
    CRITICAL_PATHS = "critical_paths"
    USER_FACING = "user_facing"
    DATA_LAYER = "data_layer"
    SECURITY = "security"
    UTILITIES = "utilities"
    FRAMEWORK_INTEGRATION = "framework_integration"


@dataclass
class CategoryConfig:
    """Configuration for a testing category"""
    category: TestingCategory
    min_coverage: float
    path_patterns: List[str]
    description: str


class CodeCategoryDetector:
    """Detect which testing category code belongs to"""
    
    def __init__(self, project_config: Dict[str, any]):
        """Initialize with project-specific configuration
        
        Args:
            project_config: Project configuration with testing categories
        """
        self.config = project_config
        self._category_configs = self._load_category_configs()
    
    def _load_category_configs(self) -> Dict[TestingCategory, CategoryConfig]:
        """Load category configurations from project config"""
        configs = {}
        
        # Default configurations (can be overridden by project config)
        default_configs = {
            TestingCategory.CRITICAL_PATHS: CategoryConfig(
                category=TestingCategory.CRITICAL_PATHS,
                min_coverage=95.0,
                path_patterns=["**/core/**", "**/business/**", "**/critical/**"],
                description="Core business logic that drives the application"
            ),
            TestingCategory.USER_FACING: CategoryConfig(
                category=TestingCategory.USER_FACING,
                min_coverage=85.0,
                path_patterns=["**/api/**", "**/cli/**", "**/web/**", "**/ui/**"],
                description="Code that directly interacts with users"
            ),
            TestingCategory.DATA_LAYER: CategoryConfig(
                category=TestingCategory.DATA_LAYER,
                min_coverage=90.0,
                path_patterns=["**/database/**", "**/models/**", "**/storage/**"],
                description="Data persistence and integrity"
            ),
            TestingCategory.SECURITY: CategoryConfig(
                category=TestingCategory.SECURITY,
                min_coverage=95.0,
                path_patterns=["**/security/**", "**/auth/**", "**/validation/**"],
                description="Security-critical code"
            ),
            TestingCategory.UTILITIES: CategoryConfig(
                category=TestingCategory.UTILITIES,
                min_coverage=70.0,
                path_patterns=["**/utils/**", "**/helpers/**", "**/common/**"],
                description="Helper functions and common utilities"
            ),
            TestingCategory.FRAMEWORK_INTEGRATION: CategoryConfig(
                category=TestingCategory.FRAMEWORK_INTEGRATION,
                min_coverage=50.0,
                path_patterns=["**/framework/**", "**/integration/**"],
                description="Integration with external frameworks"
            )
        }
        
        # Override with project-specific configuration if available
        if 'testing_categories' in self.config:
            project_categories = self.config['testing_categories']
            for category_name, category_config in project_categories.items():
                try:
                    category = TestingCategory(category_name)
                    configs[category] = CategoryConfig(
                        category=category,
                        min_coverage=category_config.get('min_coverage', default_configs[category].min_coverage),
                        path_patterns=category_config.get('path_patterns', default_configs[category].path_patterns),
                        description=category_config.get('description', default_configs[category].description)
                    )
                except ValueError:
                    # Unknown category, skip
                    continue
        
        # Add any missing categories from defaults
        for category, default_config in default_configs.items():
            if category not in configs:
                configs[category] = default_config
        
        return configs
    
    def get_category(self, file_path: str) -> TestingCategory:
        """Get testing category for a file
        
        Args:
            file_path: Path to the file (relative to project root)
            
        Returns:
            TestingCategory that the file belongs to
        """
        # Normalize path separators
        normalized_path = file_path.replace('\\', '/')
        
        # Check each category in order of priority (most specific first)
        priority_order = [
            TestingCategory.SECURITY,
            TestingCategory.CRITICAL_PATHS,
            TestingCategory.USER_FACING,
            TestingCategory.DATA_LAYER,
            TestingCategory.FRAMEWORK_INTEGRATION,
            TestingCategory.UTILITIES
        ]
        
        for category in priority_order:
            if category in self._category_configs:
                config = self._category_configs[category]
                if self._matches_patterns(normalized_path, config.path_patterns):
                    return category
        
        # Default to utilities if no pattern matches
        return TestingCategory.UTILITIES
    
    def _matches_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches any of the patterns
        
        Args:
            file_path: Normalized file path
            patterns: List of glob patterns
            
        Returns:
            True if file matches any pattern
        """
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
    
    def get_coverage_requirement(self, file_path: str) -> float:
        """Get coverage requirement for a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Minimum coverage percentage required
        """
        category = self.get_category(file_path)
        if category in self._category_configs:
            return self._category_configs[category].min_coverage
        return 70.0  # Default coverage requirement
    
    def get_category_config(self, category: TestingCategory) -> Optional[CategoryConfig]:
        """Get configuration for a specific category
        
        Args:
            category: Testing category
            
        Returns:
            CategoryConfig or None if not found
        """
        return self._category_configs.get(category)
    
    def get_all_categories(self) -> Dict[TestingCategory, CategoryConfig]:
        """Get all category configurations
        
        Returns:
            Dictionary of category configurations
        """
        return self._category_configs.copy()
    
    def categorize_files(self, file_paths: List[str]) -> Dict[TestingCategory, List[str]]:
        """Categorize multiple files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary mapping categories to lists of files
        """
        categorized = {category: [] for category in TestingCategory}
        
        for file_path in file_paths:
            category = self.get_category(file_path)
            categorized[category].append(file_path)
        
        return categorized
    
    def get_category_summary(self, file_paths: List[str]) -> Dict[str, any]:
        """Get summary of file categorization
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            Summary with counts and coverage requirements
        """
        categorized = self.categorize_files(file_paths)
        summary = {}
        
        for category, files in categorized.items():
            if files:  # Only include categories with files
                config = self._category_configs.get(category)
                summary[category.value] = {
                    'file_count': len(files),
                    'min_coverage': config.min_coverage if config else 70.0,
                    'description': config.description if config else 'Unknown category',
                    'files': files[:10]  # Show first 10 files
                }
        
        return summary


def load_project_testing_config(project_path: str) -> Dict[str, any]:
    """Load project-specific testing configuration (backward compatibility)
    
    Args:
        project_path: Path to project root
        
    Returns:
        Project configuration dictionary
    """
    from .config import load_project_testing_config as load_config
    return load_config(project_path)


def create_agentpm_testing_config() -> Dict[str, any]:
    """Create APM (Agent Project Manager) specific testing configuration
    
    Returns:
        APM (Agent Project Manager) testing configuration
    """
    return {
        'testing_categories': {
            'critical_paths': {
                'min_coverage': 95.0,
                'path_patterns': [
                    'agentpm/core/workflow/**',
                    'agentpm/core/context/**',
                    'agentpm/core/database/**',
                    'agentpm/core/rules/**'
                ],
                'description': 'Core APM (Agent Project Manager) business logic and workflow engine'
            },
            'user_facing': {
                'min_coverage': 85.0,
                'path_patterns': [
                    'agentpm/cli/**',
                    'agentpm/web/**'
                ],
                'description': 'CLI commands and web interface'
            },
            'data_layer': {
                'min_coverage': 90.0,
                'path_patterns': [
                    'agentpm/core/database/**',
                    'agentpm/core/models/**'
                ],
                'description': 'Database operations and data models'
            },
            'security': {
                'min_coverage': 95.0,
                'path_patterns': [
                    'agentpm/core/security/**',
                    'agentpm/cli/utils/security.py'
                ],
                'description': 'Security validation and authentication'
            },
            'utilities': {
                'min_coverage': 70.0,
                'path_patterns': [
                    'agentpm/utils/**',
                    'agentpm/hooks/**'
                ],
                'description': 'Helper functions and utilities'
            },
            'framework_integration': {
                'min_coverage': 50.0,
                'path_patterns': [
                    'agentpm/templates/**',
                    'agentpm/web/static/**'
                ],
                'description': 'Template and static file handling'
            }
        }
    }


# Example usage
if __name__ == "__main__":
    # Load APM (Agent Project Manager) configuration
    config = create_agentpm_testing_config()
    detector = CodeCategoryDetector(config)
    
    # Example files
    test_files = [
        'agentpm/core/workflow/service.py',
        'agentpm/cli/commands/work_item.py',
        'agentpm/core/database/models/task.py',
        'agentpm/utils/helpers.py',
        'agentpm/templates/agents/tester.md'
    ]
    
    # Categorize files
    for file_path in test_files:
        category = detector.get_category(file_path)
        coverage_req = detector.get_coverage_requirement(file_path)
        print(f"{file_path} -> {category.value} ({coverage_req}% coverage)")
    
    # Get summary
    summary = detector.get_category_summary(test_files)
    print("\nCategory Summary:")
    for category, info in summary.items():
        print(f"  {category}: {info['file_count']} files, {info['min_coverage']}% coverage")
