"""
Testing Rule Configuration Service

Configures generic testing rules with project-specific path patterns.
This bridges the gap between generic rules and project-specific implementations.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..database.service import DatabaseService
from ..database.methods import rules as rule_methods
from .config import TestingConfigManager, load_project_testing_config


class TestingRuleConfigurator:
    """Configures generic testing rules with project-specific path patterns"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.config_manager = TestingConfigManager()
    
    def configure_project_rules(self, project_id: int, project_path: str) -> Dict[str, Any]:
        """Configure generic testing rules with project-specific path patterns
        
        Args:
            project_id: ID of the project
            project_path: Path to the project root
            
        Returns:
            Configuration results with updated rules count
        """
        try:
            # Load project-specific testing configuration
            project_config = load_project_testing_config(project_path)
            testing_categories = project_config.get('testing_categories', {})
            
            # Get all testing rules from database
            all_rules = rule_methods.list_rules(self.db, enabled_only=False)
            testing_rules = [r for r in all_rules if r.rule_id.startswith('TEST-02')]
            
            updated_rules = []
            skipped_rules = []
            
            for rule in testing_rules:
                # Map rule to category
                category_name = self._get_category_from_rule(rule)
                if not category_name or category_name not in testing_categories:
                    skipped_rules.append(rule.rule_id)
                    continue
                
                # Get project-specific configuration
                category_config = testing_categories[category_name]
                project_path_patterns = category_config.get('path_patterns', [])
                project_min_coverage = category_config.get('min_coverage', 95.0)
                
                # Update rule configuration
                updated_config = rule.config.copy() if rule.config else {}
                updated_config.update({
                    'min_coverage': project_min_coverage,
                    'path_patterns': project_path_patterns,
                    'project_specific': True,
                    'configured_for': project_path
                })
                
                # Update rule in database
                rule_methods.update_rule(
                    self.db,
                    rule.id,
                    config=updated_config
                )
                
                updated_rules.append({
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'category': category_name,
                    'min_coverage': project_min_coverage,
                    'path_patterns': project_path_patterns
                })
            
            return {
                'success': True,
                'updated_rules': len(updated_rules),
                'skipped_rules': len(skipped_rules),
                'project_path': project_path,
                'rules': updated_rules,
                'skipped': skipped_rules
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'updated_rules': 0,
                'skipped_rules': 0
            }
    
    def _get_category_from_rule(self, rule) -> Optional[str]:
        """Map rule ID to category name
        
        Args:
            rule: Rule object
            
        Returns:
            Category name or None if not mappable
        """
        category_mapping = {
            'TEST-021': 'critical_paths',
            'TEST-022': 'user_facing', 
            'TEST-023': 'data_layer',
            'TEST-024': 'security',
            'TEST-025': 'utilities',
            'TEST-026': 'framework_integration'
        }
        
        return category_mapping.get(rule.rule_id)
    
    def get_configured_rules(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all configured testing rules for a project
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of configured rules with their project-specific settings
        """
        try:
            all_rules = rule_methods.list_rules(self.db, enabled_only=False)
            testing_rules = [r for r in all_rules if r.rule_id.startswith('TEST-02')]
            
            configured_rules = []
            for rule in testing_rules:
                if rule.config and rule.config.get('project_specific'):
                    category_name = self._get_category_from_rule(rule)
                    configured_rules.append({
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'category': category_name,
                        'min_coverage': rule.config.get('min_coverage', 0),
                        'path_patterns': rule.config.get('path_patterns', []),
                        'enabled': rule.enabled,
                        'configured_for': rule.config.get('configured_for', 'Unknown')
                    })
            
            return configured_rules
            
        except Exception as e:
            print(f"Error getting configured rules: {e}")
            return []
    
    def reset_to_generic_rules(self, project_id: int) -> Dict[str, Any]:
        """Reset testing rules to generic configuration
        
        Args:
            project_id: ID of the project
            
        Returns:
            Reset results
        """
        try:
            all_rules = rule_methods.list_rules(self.db, enabled_only=False)
            testing_rules = [r for r in all_rules if r.rule_id.startswith('TEST-02')]
            
            reset_rules = []
            for rule in testing_rules:
                # Reset to generic configuration
                generic_config = self._get_generic_config_for_rule(rule.rule_id)
                if generic_config:
                    rule_methods.update_rule(
                        self.db,
                        rule.id,
                        config=generic_config
                    )
                    reset_rules.append(rule.rule_id)
            
            return {
                'success': True,
                'reset_rules': len(reset_rules),
                'rules': reset_rules
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'reset_rules': 0
            }
    
    def _get_generic_config_for_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get generic configuration for a rule
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Generic configuration or None
        """
        generic_configs = {
            'TEST-021': {
                'min_coverage': 95.0,
                'path_patterns': ['**/core/**', '**/business/**', '**/critical/**', '**/engine/**', '**/workflow/**', '**/rules/**']
            },
            'TEST-022': {
                'min_coverage': 85.0,
                'path_patterns': ['**/api/**', '**/cli/**', '**/web/**', '**/ui/**', '**/endpoints/**', '**/routes/**']
            },
            'TEST-023': {
                'min_coverage': 90.0,
                'path_patterns': ['**/database/**', '**/models/**', '**/storage/**', '**/persistence/**', '**/repositories/**', '**/adapters/**']
            },
            'TEST-024': {
                'min_coverage': 95.0,
                'path_patterns': ['**/security/**', '**/auth/**', '**/validation/**', '**/crypto/**', '**/permissions/**', '**/middleware/**']
            },
            'TEST-025': {
                'min_coverage': 70.0,
                'path_patterns': ['**/utils/**', '**/helpers/**', '**/common/**', '**/lib/**', '**/shared/**']
            },
            'TEST-026': {
                'min_coverage': 50.0,
                'path_patterns': ['**/framework/**', '**/integration/**', '**/adapters/**', '**/templates/**', '**/static/**', '**/assets/**']
            }
        }
        
        return generic_configs.get(rule_id)
    
    def validate_configuration(self, project_path: str) -> Dict[str, Any]:
        """Validate that project configuration matches rules
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Validation results
        """
        try:
            # Load project configuration
            project_config = load_project_testing_config(project_path)
            testing_categories = project_config.get('testing_categories', {})
            
            # Get configured rules
            all_rules = rule_methods.list_rules(self.db, enabled_only=False)
            testing_rules = [r for r in all_rules if r.rule_id.startswith('TEST-02')]
            
            validation_results = []
            all_valid = True
            
            for rule in testing_rules:
                category_name = self._get_category_from_rule(rule)
                if not category_name:
                    continue
                
                if category_name not in testing_categories:
                    validation_results.append({
                        'rule_id': rule.rule_id,
                        'category': category_name,
                        'valid': False,
                        'issue': 'Category not found in project configuration'
                    })
                    all_valid = False
                    continue
                
                category_config = testing_categories[category_name]
                rule_config = rule.config or {}
                
                # Check if configurations match
                project_coverage = category_config.get('min_coverage', 0)
                rule_coverage = rule_config.get('min_coverage', 0)
                
                project_patterns = set(category_config.get('path_patterns', []))
                rule_patterns = set(rule_config.get('path_patterns', []))
                
                coverage_match = project_coverage == rule_coverage
                patterns_match = project_patterns == rule_patterns
                
                validation_results.append({
                    'rule_id': rule.rule_id,
                    'category': category_name,
                    'valid': coverage_match and patterns_match,
                    'coverage_match': coverage_match,
                    'patterns_match': patterns_match,
                    'project_coverage': project_coverage,
                    'rule_coverage': rule_coverage,
                    'project_patterns': list(project_patterns),
                    'rule_patterns': list(rule_patterns)
                })
                
                if not (coverage_match and patterns_match):
                    all_valid = False
            
            return {
                'valid': all_valid,
                'results': validation_results,
                'total_rules': len(testing_rules),
                'valid_rules': len([r for r in validation_results if r['valid']])
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'results': [],
                'total_rules': 0,
                'valid_rules': 0
            }


# Example usage
if __name__ == "__main__":
    # Test the configurator
    from agentpm.core.database.service import DatabaseService
    
    db = DatabaseService("test.db")
    configurator = TestingRuleConfigurator(db)
    
    # Configure rules for current project
    result = configurator.configure_project_rules(1, ".")
    print(f"Configuration result: {result}")
    
    # Get configured rules
    rules = configurator.get_configured_rules(1)
    print(f"Configured rules: {len(rules)}")
    
    # Validate configuration
    validation = configurator.validate_configuration(".")
    print(f"Validation result: {validation}")
