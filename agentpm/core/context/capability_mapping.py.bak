"""
Capability Mapping - Agent Capability to Context Element Mapping

Maps agent capabilities to relevant context elements (file patterns, frameworks).
Used by RoleBasedFilter to scope context delivery to agent-relevant information.

Pattern: Static configuration with utility matching functions
"""

from typing import List, Set


# ─────────────────────────────────────────────────────────────────────
# CAPABILITY → FILE PATTERN MAPPING
# ─────────────────────────────────────────────────────────────────────

# Map agent capabilities to file patterns (amalgamation types)
CAPABILITY_FILE_PATTERNS = {
    # Backend capabilities
    "python": ["classes", "functions", "methods", "modules", "imports"],
    "database": ["models", "schema", "migrations", "queries", "database"],
    "api": ["api", "endpoints", "serializers", "views", "routes"],

    # Testing capabilities
    "testing": ["tests", "fixtures", "test_cases", "test_helpers"],
    "pytest": ["tests", "fixtures", "conftest"],
    "unittest": ["tests", "test_cases"],

    # Frontend capabilities
    "frontend": ["components", "pages", "layouts", "styles"],
    "react": ["components", "hooks", "contexts", "jsx"],
    "vue": ["components", "templates", "composables"],
    "angular": ["components", "services", "modules"],

    # Infrastructure capabilities
    "devops": ["config", "deployment", "infrastructure", "docker"],
    "ci_cd": ["workflows", "pipelines", "deployment"],

    # Documentation capabilities
    "documentation": ["docs", "readme", "guides"],
}


# ─────────────────────────────────────────────────────────────────────
# CAPABILITY → FRAMEWORK MAPPING
# ─────────────────────────────────────────────────────────────────────

# Map capabilities to relevant framework domains
CAPABILITY_FRAMEWORK_MAP = {
    # Backend frameworks
    "python": ["python", "django", "fastapi", "flask", "pydantic"],
    "database": ["sqlalchemy", "sqlite", "postgresql", "mysql", "redis"],
    "api": ["django", "fastapi", "flask", "graphql", "rest_framework"],

    # Testing frameworks
    "testing": ["pytest", "unittest", "jest", "mocha", "cypress"],
    "pytest": ["pytest", "pytest-cov", "pytest-mock"],
    "unittest": ["unittest", "mock"],

    # Frontend frameworks
    "frontend": ["react", "vue", "angular", "svelte", "nextjs"],
    "react": ["react", "nextjs", "gatsby", "redux", "react-router"],
    "vue": ["vue", "nuxt", "vuex", "vue-router"],
    "angular": ["angular", "rxjs", "ngrx"],

    # Infrastructure
    "devops": ["docker", "kubernetes", "terraform", "ansible"],
    "ci_cd": ["github-actions", "gitlab-ci", "jenkins", "circleci"],

    # Documentation
    "documentation": ["sphinx", "mkdocs", "docusaurus", "markdown"],
}


# ─────────────────────────────────────────────────────────────────────
# COMMON CONTEXT (always included regardless of capabilities)
# ─────────────────────────────────────────────────────────────────────

# Always include these amalgamation types (universal context)
COMMON_AMALGAMATION_TYPES = {
    "readme",
    "overview",
    "architecture",
    "structure",
    "project",
}


# ─────────────────────────────────────────────────────────────────────
# CAPABILITY → RULE CATEGORY MAPPING
# ─────────────────────────────────────────────────────────────────────

# Map capabilities to relevant rule categories
CAPABILITY_RULE_CATEGORIES = {
    # Backend/development capabilities
    "python": [
        "Development Principles",
        "Code Quality",
        "Testing Standards",
        "Security Standards",
        "Technical Standards",
    ],
    "database": [
        "Development Principles",
        "Security Standards",
        "Data Governance",
        "Technical Standards",
    ],
    "api": [
        "Development Principles",
        "Code Quality",
        "Security Standards",
        "API Standards",
    ],

    # Testing capabilities
    "testing": [
        "Testing Standards",
        "Code Quality",
        "Development Principles",
    ],
    "pytest": [
        "Testing Standards",
        "Code Quality",
    ],
    "quality_assurance": [
        "Testing Standards",
        "Code Quality",
        "Documentation Standards",
    ],

    # Frontend capabilities
    "frontend": [
        "Development Principles",
        "Code Quality",
        "Testing Standards",
        "UI/UX Standards",
    ],
    "react": [
        "Development Principles",
        "Code Quality",
        "Testing Standards",
    ],

    # Infrastructure/DevOps capabilities
    "devops": [
        "Deployment Standards",
        "Security Standards",
        "Infrastructure Standards",
    ],
    "ci_cd": [
        "Deployment Standards",
        "Testing Standards",
    ],
    "infrastructure": [
        "Deployment Standards",
        "Security Standards",
        "Infrastructure Standards",
    ],

    # Documentation capabilities
    "documentation": [
        "Documentation Standards",
        "Code Quality",
    ],
    "technical_writing": [
        "Documentation Standards",
    ],

    # Quality/review capabilities
    "code_review": [
        "Code Quality",
        "Development Principles",
        "Testing Standards",
        "Security Standards",
    ],
    "static_analysis": [
        "Code Quality",
        "Security Standards",
    ],
}

# Universal rule categories (always included)
UNIVERSAL_RULE_CATEGORIES = {
    "Workflow Rules",
    "Time-Boxing Rules",
    "Project Management",
}


# ─────────────────────────────────────────────────────────────────────
# UTILITY CLASS - Capability Matching Logic
# ─────────────────────────────────────────────────────────────────────

class CapabilityMatcher:
    """
    Match context elements (files, frameworks) to agent capabilities.

    Used by RoleBasedFilter to determine if a context element is
    relevant for an agent's capabilities.

    Example:
        >>> matcher = CapabilityMatcher()
        >>> matcher.matches_file('models', ['python', 'database'])
        True  # 'models' matches 'database' capability

        >>> matcher.matches_framework('react', ['python', 'database'])
        False  # 'react' doesn't match backend capabilities
    """

    @staticmethod
    def matches_file(
        amalgamation_type: str,
        capabilities: List[str]
    ) -> bool:
        """
        Check if amalgamation type matches any capability.

        Args:
            amalgamation_type: Amalgamation type (e.g., 'classes', 'components')
            capabilities: List of agent capabilities (e.g., ['python', 'database'])

        Returns:
            True if amalgamation type matches any capability

        Example:
            >>> CapabilityMatcher.matches_file('classes', ['python'])
            True
            >>> CapabilityMatcher.matches_file('components', ['python'])
            False

        Performance: <1ms (simple set intersection)
        """
        amalgamation_lower = amalgamation_type.lower()

        # Check if it's a common type (always include)
        if amalgamation_lower in COMMON_AMALGAMATION_TYPES:
            return True

        # Check if amalgamation type matches any capability's file patterns
        for capability in capabilities:
            capability_lower = capability.lower()

            # Direct capability match (e.g., 'tests' matches 'testing')
            if capability_lower in amalgamation_lower or amalgamation_lower in capability_lower:
                return True

            # Check mapped file patterns for this capability
            file_patterns = CAPABILITY_FILE_PATTERNS.get(capability_lower, [])
            for pattern in file_patterns:
                if pattern.lower() in amalgamation_lower or amalgamation_lower in pattern.lower():
                    return True

        return False

    @staticmethod
    def matches_framework(
        framework_name: str,
        capabilities: List[str]
    ) -> bool:
        """
        Check if framework matches any capability.

        Args:
            framework_name: Framework name (e.g., 'django', 'react')
            capabilities: List of agent capabilities (e.g., ['python', 'database'])

        Returns:
            True if framework matches any capability

        Example:
            >>> CapabilityMatcher.matches_framework('django', ['python'])
            True
            >>> CapabilityMatcher.matches_framework('react', ['python'])
            False

        Performance: <1ms (simple set intersection)
        """
        framework_lower = framework_name.lower()

        # Check if framework matches any capability's framework mappings
        for capability in capabilities:
            capability_lower = capability.lower()

            # Direct capability match
            if capability_lower in framework_lower or framework_lower in capability_lower:
                return True

            # Check mapped frameworks for this capability
            frameworks = CAPABILITY_FRAMEWORK_MAP.get(capability_lower, [])
            for mapped_framework in frameworks:
                if mapped_framework.lower() in framework_lower or framework_lower in mapped_framework.lower():
                    return True

        return False

    @staticmethod
    def get_relevant_file_patterns(capabilities: List[str]) -> Set[str]:
        """
        Get all file patterns relevant to capabilities.

        Args:
            capabilities: List of agent capabilities

        Returns:
            Set of relevant file pattern keywords

        Example:
            >>> patterns = CapabilityMatcher.get_relevant_file_patterns(['python', 'testing'])
            >>> 'classes' in patterns
            True
            >>> 'tests' in patterns
            True
            >>> 'components' in patterns
            False
        """
        patterns = set(COMMON_AMALGAMATION_TYPES)  # Always include common

        for capability in capabilities:
            capability_lower = capability.lower()
            file_patterns = CAPABILITY_FILE_PATTERNS.get(capability_lower, [])
            patterns.update(p.lower() for p in file_patterns)

        return patterns

    @staticmethod
    def get_relevant_frameworks(capabilities: List[str]) -> Set[str]:
        """
        Get all frameworks relevant to capabilities.

        Args:
            capabilities: List of agent capabilities

        Returns:
            Set of relevant framework names

        Example:
            >>> frameworks = CapabilityMatcher.get_relevant_frameworks(['python', 'database'])
            >>> 'django' in frameworks
            True
            >>> 'react' in frameworks
            False
        """
        frameworks = set()

        for capability in capabilities:
            capability_lower = capability.lower()
            framework_names = CAPABILITY_FRAMEWORK_MAP.get(capability_lower, [])
            frameworks.update(f.lower() for f in framework_names)

        return frameworks

    @staticmethod
    def matches_rule_category(
        rule_category: str,
        capabilities: List[str]
    ) -> bool:
        """
        Check if rule category matches any capability.

        Args:
            rule_category: Rule category (e.g., 'Development Principles', 'Testing Standards')
            capabilities: List of agent capabilities (e.g., ['python', 'database'])

        Returns:
            True if rule category matches any capability or is universal

        Example:
            >>> CapabilityMatcher.matches_rule_category('Testing Standards', ['python', 'testing'])
            True
            >>> CapabilityMatcher.matches_rule_category('Deployment Standards', ['python'])
            False
            >>> CapabilityMatcher.matches_rule_category('Workflow Rules', ['python'])
            True  # Universal category

        Performance: <1ms (simple set lookup)
        """
        # Check if it's a universal category (always include)
        if rule_category in UNIVERSAL_RULE_CATEGORIES:
            return True

        # Check if category matches any capability's rule categories
        for capability in capabilities:
            capability_lower = capability.lower()

            # Get mapped categories for this capability
            categories = CAPABILITY_RULE_CATEGORIES.get(capability_lower, [])
            if rule_category in categories:
                return True

        return False

    @staticmethod
    def get_relevant_rule_categories(capabilities: List[str]) -> Set[str]:
        """
        Get all rule categories relevant to capabilities.

        Args:
            capabilities: List of agent capabilities

        Returns:
            Set of relevant rule categories

        Example:
            >>> categories = CapabilityMatcher.get_relevant_rule_categories(['python', 'testing'])
            >>> 'Testing Standards' in categories
            True
            >>> 'Workflow Rules' in categories
            True  # Universal
            >>> 'Deployment Standards' in categories
            False
        """
        categories = set(UNIVERSAL_RULE_CATEGORIES)  # Always include universal

        for capability in capabilities:
            capability_lower = capability.lower()
            rule_categories = CAPABILITY_RULE_CATEGORIES.get(capability_lower, [])
            categories.update(rule_categories)

        return categories
