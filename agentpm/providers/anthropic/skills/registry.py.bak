"""
Skill Registry - Template Registration and Discovery

Manages skill templates and provides template lookup functionality.
Enables dynamic skill generation from APM (Agent Project Manager) components.

Pattern: Registry pattern with template management
"""

from typing import Dict, Optional, List
from .models import SkillTemplate, SkillCategory


class SkillRegistry:
    """
    Registry for skill templates.
    
    Provides:
    - Template registration and discovery
    - Template lookup by ID
    - Template listing by category
    """
    
    def __init__(self):
        """Initialize registry with empty template store."""
        self._templates: Dict[str, SkillTemplate] = {}
        self._category_index: Dict[SkillCategory, List[str]] = {}
    
    def register_template(self, template: SkillTemplate) -> None:
        """
        Register a skill template.
        
        Args:
            template: Template to register
        """
        self._templates[template.template_id] = template
        
        # Update category index
        if template.category not in self._category_index:
            self._category_index[template.category] = []
        
        if template.template_id not in self._category_index[template.category]:
            self._category_index[template.category].append(template.template_id)
    
    def get_template(self, template_id: str) -> Optional[SkillTemplate]:
        """
        Get template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template if found, None otherwise
        """
        return self._templates.get(template_id)
    
    def list_templates(self, category: Optional[SkillCategory] = None) -> List[SkillTemplate]:
        """
        List templates, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of templates
        """
        if category:
            template_ids = self._category_index.get(category, [])
            return [self._templates[tid] for tid in template_ids if tid in self._templates]
        else:
            return list(self._templates.values())
    
    def get_template_ids(self, category: Optional[SkillCategory] = None) -> List[str]:
        """
        Get template IDs, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of template IDs
        """
        if category:
            return self._category_index.get(category, [])
        else:
            return list(self._templates.keys())
    
    def has_template(self, template_id: str) -> bool:
        """
        Check if template exists.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if template exists, False otherwise
        """
        return template_id in self._templates
    
    def unregister_template(self, template_id: str) -> bool:
        """
        Unregister a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if template was removed, False if not found
        """
        if template_id not in self._templates:
            return False
        
        template = self._templates[template_id]
        
        # Remove from category index
        if template.category in self._category_index:
            if template_id in self._category_index[template.category]:
                self._category_index[template.category].remove(template_id)
        
        # Remove from templates
        del self._templates[template_id]
        
        return True
    
    def clear(self) -> None:
        """Clear all templates."""
        self._templates.clear()
        self._category_index.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with template counts by category
        """
        stats = {
            "total_templates": len(self._templates),
        }
        
        for category in SkillCategory:
            count = len(self._category_index.get(category, []))
            stats[f"{category.value}_templates"] = count
        
        return stats
