"""
Role-Based Filter - Context Scoping by Agent Capabilities

Filters context to scope delivery to agent-relevant information only.
Reduces noise by matching amalgamations and plugin facts to agent capabilities.

Performance Target: <10ms overhead per filter operation
Pattern: Service class with database integration for agent lookup

Example:
    >>> filter = RoleBasedFilter(db)
    >>> filtered_amalgs = filter.filter_amalgamations(
    ...     'python-developer',
    ...     {'classes': 'classes.txt', 'components': 'components.txt'}
    ... )
    >>> # Returns: {'classes': 'classes.txt'} - excluded frontend 'components'
"""

from typing import Dict, Any, List, Optional
from .capability_mapping import CapabilityMatcher, COMMON_AMALGAMATION_TYPES


class RoleBasedFilter:
    """
    Filter context based on agent role and capabilities.

    Reduces context noise by including only information relevant to
    the assigned agent's capabilities and domain expertise.

    Filtering rules:
    1. Code files: Match agent capabilities (python-dev → .py files, not .jsx)
    2. Frameworks: Match agent domain (backend-dev → Django, not React)
    3. Plugin facts: Relevant frameworks only
    4. Always include common/universal context (README, architecture, etc.)

    Performance: <10ms overhead per filter operation
    """

    def __init__(self, db):
        """
        Initialize role-based filter.

        Args:
            db: DatabaseService instance for agent lookup
        """
        self.db = db
        self.matcher = CapabilityMatcher()

    # ─────────────────────────────────────────────────────────────────
    # PUBLIC API - Context Filtering
    # ─────────────────────────────────────────────────────────────────

    def filter_amalgamations(
        self,
        project_id: int,
        agent_role: str,
        amalgamations: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Filter code amalgamations by agent capabilities.

        Strategy:
        1. Load agent from database to get capabilities
        2. Keep amalgamations matching any capability
        3. Always include common types (readme, overview, architecture)
        4. Return filtered dict

        Args:
            project_id: Project ID (for agent lookup)
            agent_role: Agent role name (e.g., 'python-developer')
            amalgamations: All available amalgamations {type: path}

        Returns:
            Filtered amalgamations dict

        Example:
            Input:
                agent_role = 'database-developer'
                amalgamations = {
                    'classes': '.aipm/contexts/classes.txt',
                    'models': '.aipm/contexts/models.txt',
                    'components': '.aipm/contexts/components.txt',
                    'readme': '.aipm/contexts/readme.txt'
                }

            Output:
                {
                    'models': '.aipm/contexts/models.txt',  # Relevant to database
                    'readme': '.aipm/contexts/readme.txt'   # Common (always included)
                }
                # Excluded 'components' (frontend, not database)

        Performance: <5ms (dict filtering + database query)
        """
        if not amalgamations:
            return {}

        # Get agent capabilities
        capabilities = self._get_agent_capabilities(project_id, agent_role)

        if not capabilities:
            # No capabilities found - no filtering (return all)
            return amalgamations

        # Filter: Keep amalgamations matching capabilities
        filtered = {}

        for amalg_type, amalg_path in amalgamations.items():
            if self.matcher.matches_file(amalg_type, capabilities):
                filtered[amalg_type] = amalg_path

        return filtered

    def filter_plugin_facts(
        self,
        project_id: int,
        agent_role: str,
        plugin_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter plugin facts by agent capabilities.

        Strategy:
        1. Load agent from database to get capabilities
        2. Keep plugin facts for frameworks matching capabilities
        3. Return filtered dict

        Args:
            project_id: Project ID (for agent lookup)
            agent_role: Agent role name (e.g., 'python-developer')
            plugin_facts: All available plugin facts {framework: facts}

        Returns:
            Filtered plugin facts dict

        Example:
            Input:
                agent_role = 'python-developer'
                plugin_facts = {
                    'python': {'version': '3.9', ...},
                    'django': {'version': '4.2', ...},
                    'react': {'version': '18.2', ...}
                }

            Output:
                {
                    'python': {'version': '3.9', ...},
                    'django': {'version': '4.2', ...}
                }
                # Excluded 'react' (frontend framework, not backend)

        Performance: <5ms (dict filtering + database query)
        """
        if not plugin_facts:
            return {}

        # Get agent capabilities
        capabilities = self._get_agent_capabilities(project_id, agent_role)

        if not capabilities:
            # No capabilities found - no filtering (return all)
            return plugin_facts

        # Filter: Keep facts matching capabilities
        filtered = {}

        for framework_name, facts in plugin_facts.items():
            if self.matcher.matches_framework(framework_name, capabilities):
                filtered[framework_name] = facts

        return filtered

    def filter_rules(
        self,
        project_id: int,
        agent_role: str,
        rules: List['Rule']
    ) -> List['Rule']:
        """
        Filter rules by agent capabilities.

        Strategy:
        1. Load agent from database to get capabilities
        2. Keep rules in universal categories (always apply)
        3. Keep rules matching any capability's domain
        4. Return filtered list

        Args:
            project_id: Project ID (for agent lookup)
            agent_role: Agent role name (e.g., 'python-cli-developer')
            rules: All project rules

        Returns:
            Filtered rules list relevant to agent's work domain

        Example:
            Input:
                agent_role = 'python-cli-developer'
                rules = [
                    Rule(category='Development Principles', ...),  # INCLUDE (python capability)
                    Rule(category='Testing Standards', ...),        # INCLUDE (python capability)
                    Rule(category='Deployment Standards', ...),     # EXCLUDE (devops only)
                    Rule(category='Workflow Rules', ...),           # INCLUDE (universal)
                ]

            Output:
                [
                    Rule(category='Development Principles', ...),
                    Rule(category='Testing Standards', ...),
                    Rule(category='Workflow Rules', ...),
                ]
                # Excluded 'Deployment Standards' (not relevant to python-cli-developer)

        Performance: <5ms (list filtering + database query)
        """
        if not rules:
            return []

        # Get agent capabilities
        capabilities = self._get_agent_capabilities(project_id, agent_role)

        if not capabilities:
            # No capabilities found - no filtering (return all)
            return rules

        # Filter: Keep rules matching capabilities
        filtered = []

        for rule in rules:
            # Always include rules without category (legacy compatibility)
            if not rule.category:
                filtered.append(rule)
                continue

            # Check if rule category matches agent capabilities
            if self.matcher.matches_rule_category(rule.category, capabilities):
                filtered.append(rule)

        return filtered

    def calculate_filter_effectiveness(
        self,
        original_count: int,
        filtered_count: int
    ) -> float:
        """
        Calculate filtering effectiveness (percentage reduction).

        Args:
            original_count: Original item count
            filtered_count: Filtered item count

        Returns:
            Percentage reduction (0.0-1.0)

        Example:
            >>> filter.calculate_filter_effectiveness(10, 5)
            0.5  # 50% reduction
        """
        if original_count == 0:
            return 0.0

        reduction = (original_count - filtered_count) / original_count
        return max(0.0, min(1.0, reduction))  # Clamp to [0.0, 1.0]

    # ─────────────────────────────────────────────────────────────────
    # PRIVATE - Agent Capability Lookup
    # ─────────────────────────────────────────────────────────────────

    def _get_agent_capabilities(
        self,
        project_id: int,
        agent_role: str
    ) -> List[str]:
        """
        Get capabilities for agent role.

        Strategy:
        1. Query database for agent by role
        2. Return agent.capabilities list
        3. Fallback to empty list (no filtering)

        Args:
            project_id: Project ID
            agent_role: Agent role name

        Returns:
            List of capability keywords (e.g., ['python', 'database', 'testing'])

        Performance: <2ms (indexed database query)
        """
        from ..database.methods import agents

        try:
            agent = agents.get_agent_by_role(self.db, project_id, agent_role)

            if not agent:
                # Agent not found - no filtering
                return []

            if not agent.is_active:
                # Inactive agent - no filtering (graceful degradation)
                return []

            # Return capabilities list
            return agent.capabilities or []

        except Exception:
            # Database error - graceful degradation (no filtering)
            return []


# ─────────────────────────────────────────────────────────────────────
# CONVENIENCE FUNCTIONS - Standalone filtering without service
# ─────────────────────────────────────────────────────────────────────

def filter_amalgamations_by_capabilities(
    amalgamations: Dict[str, str],
    capabilities: List[str]
) -> Dict[str, str]:
    """
    Filter amalgamations by explicit capabilities (no database lookup).

    Use when capabilities are already known (e.g., testing, CLI).

    Args:
        amalgamations: All available amalgamations
        capabilities: Agent capabilities (e.g., ['python', 'database'])

    Returns:
        Filtered amalgamations dict

    Example:
        >>> filter_amalgamations_by_capabilities(
        ...     {'classes': 'classes.txt', 'components': 'components.txt'},
        ...     ['python', 'database']
        ... )
        {'classes': 'classes.txt'}  # Excluded 'components'
    """
    if not capabilities:
        return amalgamations

    matcher = CapabilityMatcher()
    filtered = {}

    for amalg_type, amalg_path in amalgamations.items():
        if matcher.matches_file(amalg_type, capabilities):
            filtered[amalg_type] = amalg_path

    return filtered


def filter_plugin_facts_by_capabilities(
    plugin_facts: Dict[str, Any],
    capabilities: List[str]
) -> Dict[str, Any]:
    """
    Filter plugin facts by explicit capabilities (no database lookup).

    Use when capabilities are already known (e.g., testing, CLI).

    Args:
        plugin_facts: All available plugin facts
        capabilities: Agent capabilities (e.g., ['python', 'database'])

    Returns:
        Filtered plugin facts dict

    Example:
        >>> filter_plugin_facts_by_capabilities(
        ...     {'python': {...}, 'react': {...}},
        ...     ['python', 'database']
        ... )
        {'python': {...}}  # Excluded 'react'
    """
    if not capabilities:
        return plugin_facts

    matcher = CapabilityMatcher()
    filtered = {}

    for framework_name, facts in plugin_facts.items():
        if matcher.matches_framework(framework_name, capabilities):
            filtered[framework_name] = facts

    return filtered
