"""
Principles Extractor - Extract development principles data for PRINCIPLES.md

Extracts data from development_principles.py enum to generate
comprehensive development principles pyramid information for Claude memory.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_extractor import BaseExtractor
from ...database.service import DatabaseService
from ...database.enums.development_principles import DevelopmentPrinciple, PrincipleDefinition


class PrinciplesExtractor(BaseExtractor):
    """
    Extractor for development principles data.
    
    Extracts principles from the DevelopmentPrinciple enum to generate
    comprehensive principles pyramid information.
    """
    
    def __init__(self, db_service: DatabaseService):
        """Initialize principles extractor."""
        super().__init__(db_service)
    
    def extract(self, project_id: int) -> Dict[str, Any]:
        """
        Extract principles data for memory file generation.
        
        Args:
            project_id: Project ID (not used for principles)
            
        Returns:
            Principles data dictionary
        """
        try:
            # Extract all principles
            principles = self._extract_all_principles()
            
            # Organize by priority tiers
            tiers = self._organize_by_tiers(principles)
            
            # Extract additional principles
            additional = self._extract_additional_principles()
            
            return {
                'principles': principles,
                'tiers': tiers,
                'additional_principles': additional,
                'total_principles': len(principles),
                'extraction_timestamp': self._format_timestamp(datetime.now())
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'principles': [],
                'tiers': {},
                'additional_principles': [],
                'total_principles': 0,
                'extraction_timestamp': self._format_timestamp(datetime.now())
            }
    
    def get_source_tables(self) -> List[str]:
        """Get list of database tables this extractor uses."""
        return []  # Principles come from enum, not database
    
    def _extract_all_principles(self) -> List[Dict[str, Any]]:
        """
        Extract all development principles from enum.
        
        Returns:
            List of principle dictionaries
        """
        principles = []
        
        for principle in DevelopmentPrinciple:
            try:
                definition = DevelopmentPrinciple.get_definition(principle)
                priority = DevelopmentPrinciple.get_priority(principle)
                
                principles.append({
                    'name': principle.value,
                    'display_name': self._format_display_name(principle.value),
                    'priority': priority,
                    'category': definition.category,
                    'description': definition.description,
                    'when_to_apply': definition.when_to_apply,
                    'examples': definition.examples
                })
            except Exception as e:
                # Skip principles that can't be extracted
                continue
        
        # Sort by priority
        principles.sort(key=lambda x: x['priority'])
        
        return principles
    
    def _organize_by_tiers(self, principles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize principles by priority tiers.
        
        Args:
            principles: List of principle dictionaries
            
        Returns:
            Dictionary organized by tiers
        """
        tiers = {
            'Foundation Layer': [],
            'Core Principles': [],
            'Quality Principles': [],
            'Advanced Principles': []
        }
        
        for principle in principles:
            priority = principle['priority']
            
            if priority <= 1:
                tiers['Foundation Layer'].append(principle)
            elif priority <= 6:
                tiers['Core Principles'].append(principle)
            elif priority <= 8:
                tiers['Quality Principles'].append(principle)
            else:
                tiers['Advanced Principles'].append(principle)
        
        return tiers
    
    def _extract_additional_principles(self) -> List[Dict[str, Any]]:
        """
        Extract additional principles not in main pyramid.
        
        Returns:
            List of additional principle dictionaries
        """
        additional = [
            {
                'name': 'AHA Rule of Three',
                'description': 'Extract abstraction after third occurrence',
                'when_to_apply': 'When you see repeated code patterns',
                'examples': "Don't abstract too early, wait for pattern to emerge"
            },
            {
                'name': 'Single Source of Truth',
                'description': 'Each piece of data should have one authoritative source',
                'when_to_apply': 'Data management and configuration',
                'examples': 'Centralized configuration, single database'
            },
            {
                'name': 'Build vs Buy vs Reuse',
                'description': 'Evaluate options before implementing',
                'when_to_apply': 'When adding new functionality',
                'examples': 'Use existing libraries, evaluate third-party solutions'
            }
        ]
        
        return additional
    
    def _format_display_name(self, principle_name: str) -> str:
        """
        Format principle name for display.
        
        Args:
            principle_name: Principle name from enum
            
        Returns:
            Formatted display name
        """
        # Convert snake_case to Title Case
        words = principle_name.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)
    
    def _get_priority_description(self, priority: int) -> str:
        """
        Get description for priority level.
        
        Args:
            priority: Priority number
            
        Returns:
            Priority description
        """
        if priority == 1:
            return "Foundation"
        elif priority <= 6:
            return "Core"
        elif priority <= 8:
            return "Quality"
        else:
            return "Advanced"
    
    def get_principles_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Get summary of principles for quick reference.
        
        Args:
            project_id: Project ID (not used for principles)
            
        Returns:
            Principles summary
        """
        try:
            data = self.extract(project_id)
            
            return {
                'total_principles': data.get('total_principles', 0),
                'tiers_count': len(data.get('tiers', {})),
                'additional_principles_count': len(data.get('additional_principles', [])),
                'extraction_time': data.get('extraction_timestamp')
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_principles': 0,
                'tiers_count': 0,
                'additional_principles_count': 0
            }
    
    def get_principle_by_name(self, principle_name: str) -> Dict[str, Any]:
        """
        Get specific principle by name.
        
        Args:
            principle_name: Name of principle to get
            
        Returns:
            Principle dictionary
        """
        try:
            data = self.extract(0)  # Project ID not needed
            
            for principle in data.get('principles', []):
                if principle['name'] == principle_name:
                    return principle
            
            return {}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_priority_matrix(self) -> Dict[str, List[str]]:
        """
        Get priority decision matrix for common situations.
        
        Returns:
            Priority matrix dictionary
        """
        return {
            'New Feature': ['Make it Work', 'YAGNI'],
            'Code Review': ['Clean Code', 'Be Consistent'],
            'Performance Issue': ['Make it Fast', 'Make it Work'],
            'Duplicate Code': ['DRY', 'Clean Code'],
            'Complex Problem': ['KISS', 'Design Patterns']
        }
