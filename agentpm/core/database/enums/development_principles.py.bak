"""
Development Principles - Enum Definitions

Defines all software development principles from the Pyramid of Software Development Principles.
Each principle has its own definition, application guidance, and examples.

Based on Bartosz Krajka's Pyramid: https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PrincipleDefinition:
    """Definition of a software development principle"""
    name: str
    description: str
    application: str
    examples: List[str]
    priority: int  # Lower number = higher priority in pyramid
    category: str


class DevelopmentPrinciple(str, Enum):
    """
    The Pyramid of Software Development Principles
    
    Hierarchy (bottom to top, lower number = higher priority):
    1. Make it Work (Foundation)
    2. YAGNI (Second)
    3. Principle of Least Surprise (Third)
    4. KISS (Fourth)
    5. Be Consistent (Fifth)
    6. DRY (Sixth)
    7. Clean Code (Seventh)
    8. SOLID (Eighth)
    9. Design Patterns (Ninth)
    10. Agile Practices (Tenth)
    11. Boy Scout Rule (Eleventh)
    12. Make it Fast (Twelfth)
    """
    
    # Foundation Layer
    MAKE_IT_WORK = "make_it_work"
    
    # Core Principles
    YAGNI = "yagni"
    PRINCIPLE_OF_LEAST_SURPRISE = "principle_of_least_surprise"
    KISS = "kiss"
    BE_CONSISTENT = "be_consistent"
    DRY = "dry"
    
    # Quality Principles
    CLEAN_CODE = "clean_code"
    SOLID = "solid"
    
    # Advanced Principles
    DESIGN_PATTERNS = "design_patterns"
    AGILE_PRACTICES = "agile_practices"
    BOY_SCOUT_RULE = "boy_scout_rule"
    MAKE_IT_FAST = "make_it_fast"
    
    # Additional Principles
    AHA_RULE_OF_THREE = "aha_rule_of_three"
    SINGLE_SOURCE_OF_TRUTH = "single_source_of_truth"
    BUILD_VS_BUY_VS_REUSE = "build_vs_buy_vs_reuse"
    
    @classmethod
    def get_priority(cls, principle: 'DevelopmentPrinciple') -> int:
        """Get the priority order of a principle (lower = higher priority)"""
        priorities = {
            cls.MAKE_IT_WORK: 1,
            cls.YAGNI: 2,
            cls.PRINCIPLE_OF_LEAST_SURPRISE: 3,
            cls.KISS: 4,
            cls.BE_CONSISTENT: 5,
            cls.DRY: 6,
            cls.CLEAN_CODE: 7,
            cls.SOLID: 8,
            cls.DESIGN_PATTERNS: 9,
            cls.AGILE_PRACTICES: 10,
            cls.BOY_SCOUT_RULE: 11,
            cls.MAKE_IT_FAST: 12,
            cls.AHA_RULE_OF_THREE: 13,
            cls.SINGLE_SOURCE_OF_TRUTH: 14,
            cls.BUILD_VS_BUY_VS_REUSE: 15,
        }
        return priorities.get(principle, 999)
    
    @classmethod
    def get_definition(cls, principle: 'DevelopmentPrinciple') -> PrincipleDefinition:
        """Get the complete definition of a principle"""
        definitions = {
            cls.MAKE_IT_WORK: PrincipleDefinition(
                name="Make it Work",
                description="Code must work correctly before any other principle applies",
                application="All other principles are secondary to functional correctness",
                examples=[
                    "Fix bugs before refactoring",
                    "Ensure tests pass before optimization",
                    "Working code is better than perfect code that doesn't work"
                ],
                priority=1,
                category="Foundation"
            ),
            
            cls.YAGNI: PrincipleDefinition(
                name="YAGNI (You Aren't Gonna Need It)",
                description="Don't build features for imagined future needs",
                application="Delete code that isn't actively used",
                examples=[
                    "Remove unused imports and functions",
                    "Don't create abstractions until needed",
                    "Build only what's required for current work items"
                ],
                priority=2,
                category="Core"
            ),
            
            cls.PRINCIPLE_OF_LEAST_SURPRISE: PrincipleDefinition(
                name="Principle of Least Surprise",
                description="Code should behave as expected by other developers/agents",
                application="Predictable APIs, consistent naming, expected behavior",
                examples=[
                    "Context assembly should always return the same structure",
                    "API endpoints follow consistent patterns",
                    "Function names clearly indicate their behavior"
                ],
                priority=3,
                category="Core"
            ),
            
            cls.KISS: PrincipleDefinition(
                name="KISS (Keep It Simple, Stupid)",
                description="Always choose the simplest solution that works",
                application="Start with simplest solution, add complexity only when proven necessary",
                examples=[
                    "Use Python standard library before external packages",
                    "Single responsibility per service",
                    "Clear, readable code over clever code"
                ],
                priority=4,
                category="Core"
            ),
            
            cls.BE_CONSISTENT: PrincipleDefinition(
                name="Be Consistent",
                description="Maintain consistency across the codebase",
                application="Use same patterns, naming conventions, and structures",
                examples=[
                    "All services follow DatabaseService pattern",
                    "Consistent naming across modules",
                    "Same error handling patterns everywhere"
                ],
                priority=5,
                category="Core"
            ),
            
            cls.DRY: PrincipleDefinition(
                name="DRY (Don't Repeat Yourself)",
                description="Reuse existing code and eliminate duplication",
                application="Search existing code BEFORE implementing",
                examples=[
                    "Use DatabaseService pattern for all services",
                    "Share common utilities across modules",
                    "Consolidate similar functionality"
                ],
                priority=6,
                category="Core"
            ),
            
            cls.CLEAN_CODE: PrincipleDefinition(
                name="Clean Code",
                description="Write meaningful names, short methods, clear structure",
                application="Code should be self-documenting and easy to read",
                examples=[
                    "Descriptive variable and function names",
                    "Short, focused methods",
                    "Clear comments where needed"
                ],
                priority=7,
                category="Quality"
            ),
            
            cls.SOLID: PrincipleDefinition(
                name="SOLID",
                description="Apply when it doesn't violate higher principles",
                application="Single responsibility per service, no premature abstractions",
                examples=[
                    "ContextAssemblyService has single responsibility",
                    "Plugin interface is open for extension",
                    "Database models depend on abstractions"
                ],
                priority=8,
                category="Quality"
            ),
            
            cls.DESIGN_PATTERNS: PrincipleDefinition(
                name="Design Patterns",
                description="Add complexity only where you've identified common issues",
                application="Use patterns to solve real problems, not speculative ones",
                examples=[
                    "Factory pattern for plugin creation",
                    "Observer pattern for event handling",
                    "Strategy pattern for different algorithms"
                ],
                priority=9,
                category="Advanced"
            ),
            
            cls.AGILE_PRACTICES: PrincipleDefinition(
                name="Agile Practices",
                description="Add complexity for predicted future needs",
                application="Adaptive software with speculative abstractions",
                examples=[
                    "Plugin system for future frameworks",
                    "Extensible context system",
                    "Configurable rules system"
                ],
                priority=10,
                category="Advanced"
            ),
            
            cls.BOY_SCOUT_RULE: PrincipleDefinition(
                name="Boy Scout Rule",
                description="Clean up code when you encounter it, but not at the expense of higher principles",
                application="Leave code better than you found it, but only if it's quick",
                examples=[
                    "Fix obvious issues during development",
                    "Refactor when making related changes",
                    "Don't spend time on non-critical improvements"
                ],
                priority=11,
                category="Advanced"
            ),
            
            cls.MAKE_IT_FAST: PrincipleDefinition(
                name="Make it Fast",
                description="Optimize for performance after everything else is working",
                application="Measure first, optimize second",
                examples=[
                    "Profile before optimizing",
                    "Cache frequently accessed data",
                    "Optimize hot paths only"
                ],
                priority=12,
                category="Advanced"
            ),
            
            cls.AHA_RULE_OF_THREE: PrincipleDefinition(
                name="AHA (Avoid Hasty Abstractions) & Rule of Three",
                description="Before inventing a new abstraction, check current usages; if it's only 1-2 cases, prefer reusing/duplicating lightly rather than creating a brand-new general thing",
                application="Wait for three instances before abstracting",
                examples=[
                    "Don't create a generic 'DataProcessor' after seeing it used twice",
                    "Prefer copying and modifying code over premature abstraction",
                    "Abstract only when you see the same pattern three times",
                    "Use composition over inheritance for 1-2 use cases"
                ],
                priority=13,
                category="Advanced"
            ),
            
            cls.SINGLE_SOURCE_OF_TRUTH: PrincipleDefinition(
                name="Single Source of Truth (SSOT)",
                description="Centralize knowledge; reference the canonical artifact rather than making another version",
                application="One authoritative source for each piece of information",
                examples=[
                    "Store configuration in one place, reference elsewhere",
                    "Use database as source of truth, not cached copies",
                    "Documentation should reference code, not duplicate it",
                    "API specifications should be the single source for client code"
                ],
                priority=14,
                category="Advanced"
            ),
            
            cls.BUILD_VS_BUY_VS_REUSE: PrincipleDefinition(
                name="Build vs Buy vs Reuse Heuristic",
                description="Many teams formalize: Reuse > Buy > Build",
                application="Prefer existing solutions over custom development",
                examples=[
                    "Use existing libraries before writing custom code",
                    "Buy commercial solutions before building in-house",
                    "Reuse existing components before creating new ones",
                    "Evaluate open source before proprietary solutions"
                ],
                priority=15,
                category="Advanced"
            ),
        }
        return definitions.get(principle)
    
    @classmethod
    def get_all_definitions(cls) -> Dict['DevelopmentPrinciple', PrincipleDefinition]:
        """Get all principle definitions"""
        return {principle: cls.get_definition(principle) for principle in cls}
    
    @classmethod
    def get_by_priority(cls) -> List['DevelopmentPrinciple']:
        """Get all principles ordered by priority (highest to lowest)"""
        return sorted(cls, key=cls.get_priority)
    
    @classmethod
    def get_by_category(cls, category: str) -> List['DevelopmentPrinciple']:
        """Get all principles in a specific category"""
        return [
            principle for principle in cls
            if cls.get_definition(principle).category == category
        ]
    
    @classmethod
    def resolve_conflict(cls, principle1: 'DevelopmentPrinciple', principle2: 'DevelopmentPrinciple') -> 'DevelopmentPrinciple':
        """
        Resolve conflict between two principles by choosing the one with higher priority (lower number)
        
        Args:
            principle1: First principle
            principle2: Second principle
            
        Returns:
            The principle with higher priority (should be chosen)
        """
        priority1 = cls.get_priority(principle1)
        priority2 = cls.get_priority(principle2)
        
        if priority1 < priority2:
            return principle1
        elif priority2 < priority1:
            return principle2
        else:
            # Same priority - this shouldn't happen, but return first one
            return principle1
    
    @classmethod
    def get_foundation_principles(cls) -> List['DevelopmentPrinciple']:
        """Get foundation principles (Make it Work)"""
        return [cls.MAKE_IT_WORK]
    
    @classmethod
    def get_core_principles(cls) -> List['DevelopmentPrinciple']:
        """Get core principles (YAGNI through DRY)"""
        return [cls.YAGNI, cls.PRINCIPLE_OF_LEAST_SURPRISE, cls.KISS, cls.BE_CONSISTENT, cls.DRY]
    
    @classmethod
    def get_quality_principles(cls) -> List['DevelopmentPrinciple']:
        """Get quality principles (Clean Code, SOLID)"""
        return [cls.CLEAN_CODE, cls.SOLID]
    
    @classmethod
    def get_advanced_principles(cls) -> List['DevelopmentPrinciple']:
        """Get advanced principles (Design Patterns through Make it Fast)"""
        return [cls.DESIGN_PATTERNS, cls.AGILE_PRACTICES, cls.BOY_SCOUT_RULE, cls.MAKE_IT_FAST]
    
    @classmethod
    def get_ai_agent_principles(cls) -> List['DevelopmentPrinciple']:
        """Get principles most important for AI agent enablement"""
        return [
            cls.MAKE_IT_WORK,  # Foundation
            cls.PRINCIPLE_OF_LEAST_SURPRISE,  # Predictability
            cls.BE_CONSISTENT,  # Consistent behavior
            cls.CLEAN_CODE,  # Readable code
        ]
    
    def __str__(self) -> str:
        """String representation of the principle"""
        definition = self.get_definition(self)
        return f"{definition.name}: {definition.description}"
    
    def __repr__(self) -> str:
        """Detailed representation of the principle"""
        definition = self.get_definition(self)
        return f"DevelopmentPrinciple.{self.value} (Priority: {definition.priority}, Category: {definition.category})"


class PrincipleCategory(str, Enum):
    """Categories of development principles"""
    FOUNDATION = "foundation"
    CORE = "core"
    QUALITY = "quality"
    ADVANCED = "advanced"


class PrinciplePriority(str, Enum):
    """Priority levels for development principles"""
    CRITICAL = "critical"      # Priority 1-3
    HIGH = "high"             # Priority 4-6
    MEDIUM = "medium"         # Priority 7-9
    LOW = "low"              # Priority 10-12
    
    @classmethod
    def from_priority_number(cls, priority: int) -> 'PrinciplePriority':
        """Get priority level from priority number"""
        if priority <= 3:
            return cls.CRITICAL
        elif priority <= 6:
            return cls.HIGH
        elif priority <= 9:
            return cls.MEDIUM
        else:
            return cls.LOW


# Convenience functions for common operations
def get_principle_definition(principle: DevelopmentPrinciple) -> PrincipleDefinition:
    """Get the definition of a development principle"""
    return DevelopmentPrinciple.get_definition(principle)


def resolve_principle_conflict(principle1: DevelopmentPrinciple, principle2: DevelopmentPrinciple) -> DevelopmentPrinciple:
    """Resolve conflict between two principles"""
    return DevelopmentPrinciple.resolve_conflict(principle1, principle2)


def get_principles_by_priority() -> List[DevelopmentPrinciple]:
    """Get all principles ordered by priority"""
    return DevelopmentPrinciple.get_by_priority()


def get_principles_for_ai_agents() -> List[DevelopmentPrinciple]:
    """Get principles most important for AI agent enablement"""
    return DevelopmentPrinciple.get_ai_agent_principles()
