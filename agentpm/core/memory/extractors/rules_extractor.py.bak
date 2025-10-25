"""
Rules Extractor - Extract governance rules data for RULES.md

Extracts data from rules table and rules_catalog.yaml to generate
comprehensive governance rules information for Claude memory.
"""

from typing import Dict, Any, List
from datetime import datetime
import yaml
from pathlib import Path

from .base_extractor import BaseExtractor
from ...database.service import DatabaseService


class RulesExtractor(BaseExtractor):
    """
    Extractor for governance rules data.
    
    Extracts project-specific rules from database and catalog rules
    from YAML file to generate comprehensive rules information.
    """
    
    def __init__(self, db_service: DatabaseService):
        """Initialize rules extractor."""
        super().__init__(db_service)
        self.catalog_path = Path("agentpm/core/rules/config/rules_catalog.yaml")
    
    def extract(self, project_id: int) -> Dict[str, Any]:
        """
        Extract rules data for memory file generation.
        
        Args:
            project_id: Project ID to extract rules for
            
        Returns:
            Rules data dictionary
        """
        try:
            # Extract project-specific rules
            project_rules = self._extract_project_rules(project_id)
            
            # Load catalog rules
            catalog_data = self._load_catalog_rules()
            
            # Extract rule categories
            categories = self._extract_categories(catalog_data)
            
            # Extract presets
            presets = self._extract_presets(catalog_data)
            
            # Combine and format data
            return {
                'project_rules': project_rules,
                'catalog_data': catalog_data,
                'categories': categories,
                'presets': presets,
                'total_rules': len(catalog_data.get('rules', [])),
                'extraction_timestamp': self._format_timestamp(datetime.now())
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'project_rules': [],
                'catalog_data': {},
                'categories': {},
                'presets': {},
                'total_rules': 0,
                'extraction_timestamp': self._format_timestamp(datetime.now())
            }
    
    def get_source_tables(self) -> List[str]:
        """Get list of database tables this extractor uses."""
        return ['rules']
    
    def _extract_project_rules(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Extract project-specific rules from database.
        
        Args:
            project_id: Project ID to extract rules for
            
        Returns:
            List of project rules
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        rule_id,
                        name,
                        description,
                        category,
                        enforcement_level,
                        validation_logic,
                        error_message,
                        config,
                        enabled,
                        created_at,
                        updated_at
                    FROM rules 
                    WHERE project_id = ? AND enabled = 1
                    ORDER BY category, rule_id
                """, (project_id,))
                
                rules = []
                for row in cursor.fetchall():
                    rules.append({
                        'rule_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'category': row[3],
                        'enforcement_level': row[4],
                        'validation_logic': row[5],
                        'error_message': row[6],
                        'config': row[7],
                        'enabled': bool(row[8]),
                        'created_at': row[9],
                        'updated_at': row[10]
                    })
                
                return rules
                
        except Exception as e:
            return []
    
    def _load_catalog_rules(self) -> Dict[str, Any]:
        """
        Load rules catalog from YAML file.
        
        Returns:
            Catalog data dictionary
        """
        try:
            if self.catalog_path.exists():
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return {}
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_categories(self, catalog_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract rule categories from catalog data.
        
        Args:
            catalog_data: Catalog data dictionary
            
        Returns:
            Categories dictionary
        """
        categories = {}
        
        if 'rules' in catalog_data:
            for rule in catalog_data['rules']:
                category = rule.get('category', 'Unknown')
                if category not in categories:
                    categories[category] = {
                        'name': category,
                        'code': self._get_category_code(category),
                        'rules': [],
                        'count': 0
                    }
                
                categories[category]['rules'].append(rule)
                categories[category]['count'] += 1
        
        return categories
    
    def _extract_presets(self, catalog_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract presets from catalog data.
        
        Args:
            catalog_data: Catalog data dictionary
            
        Returns:
            Presets dictionary
        """
        return catalog_data.get('presets', {})
    
    def _get_category_code(self, category: str) -> str:
        """
        Get category code from category name.
        
        Args:
            category: Category name
            
        Returns:
            Category code
        """
        category_codes = {
            'Development Principles': 'DP',
            'Workflow Rules': 'WR',
            'Code Quality': 'CQ',
            'Documentation': 'DOC',
            'Workflow & Process': 'WF',
            'Technology Constraints': 'TC',
            'Operations': 'OPS',
            'Governance': 'GOV',
            'Testing Requirements': 'TEST'
        }
        
        return category_codes.get(category, 'UNK')
    
    def _format_enforcement_level(self, level: str) -> str:
        """
        Format enforcement level for display.
        
        Args:
            level: Enforcement level
            
        Returns:
            Formatted enforcement level
        """
        level_descriptions = {
            'BLOCK': 'Hard constraint - operation fails if rule violated',
            'LIMIT': 'Soft constraint - warning but operation succeeds',
            'GUIDE': 'Suggestion - informational only',
            'ENHANCE': 'Context enrichment - adds intelligence, no enforcement'
        }
        
        return level_descriptions.get(level, level)
    
    def _format_config(self, config: str) -> Dict[str, Any]:
        """
        Format rule configuration.
        
        Args:
            config: Configuration JSON string
            
        Returns:
            Formatted configuration
        """
        try:
            if config:
                import json
                return json.loads(config)
            else:
                return {}
        except Exception:
            return {}
    
    def get_rules_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Get summary of rules for quick reference.
        
        Args:
            project_id: Project ID to get summary for
            
        Returns:
            Rules summary
        """
        try:
            data = self.extract(project_id)
            
            return {
                'total_catalog_rules': data.get('total_rules', 0),
                'project_rules_count': len(data.get('project_rules', [])),
                'categories_count': len(data.get('categories', {})),
                'presets_count': len(data.get('presets', {})),
                'extraction_time': data.get('extraction_timestamp')
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_catalog_rules': 0,
                'project_rules_count': 0,
                'categories_count': 0,
                'presets_count': 0
            }
