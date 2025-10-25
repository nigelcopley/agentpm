# Principle-Based Agents - Technical Implementation Specification

**Work Item**: WI-89
**Task**: #492 (Design Principle Agent Architecture and Infrastructure)
**Created**: 2025-10-14
**Status**: Technical Specification

---

## 1. PrincipleAgent Base Class

### 1.1 Core Interface

```python
"""
Base class for all principle-based code quality agents.

Location: agentpm/agents/base.py
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class ViolationSeverity(Enum):
    """Severity levels for principle violations"""
    CRITICAL = "critical"  # Must fix before merge
    HIGH = "high"  # Should fix before merge
    MEDIUM = "medium"  # Fix in near term
    LOW = "low"  # Nice to have
    INFO = "info"  # Informational only


@dataclass
class PrincipleViolation:
    """Represents a single principle violation"""

    # Core fields
    principle: str  # e.g., "Single Responsibility Principle"
    principle_code: str  # e.g., "SRP", "DRY", "KISS"
    location: str  # file:line format
    issue: str  # What's wrong
    recommendation: str  # How to fix
    severity: ViolationSeverity  # Importance level

    # Rule mapping
    rule_ids: List[str]  # e.g., ["CQ-031", "DP-035"]

    # Framework context
    framework: Optional[str] = None  # e.g., "Django", "React"
    framework_pattern: Optional[str] = None  # e.g., "fat_models", "hooks_rules"

    # Educational content
    explanation: Optional[str] = None  # Why this matters
    before_code: Optional[str] = None  # Code showing violation
    after_code: Optional[str] = None  # Refactored code
    reference_url: Optional[str] = None  # Link to detailed docs

    # Metrics
    complexity_score: Optional[float] = None  # Complexity metric if applicable
    duplication_count: Optional[int] = None  # For DRY violations
    loc_impact: Optional[int] = None  # Lines of code affected


@dataclass
class PrincipleMetrics:
    """Metrics for principle adherence"""

    # Overall score
    principle_score: float  # 0.0-1.0 (1.0 = perfect adherence)
    percentage: int  # 0-100 for display

    # Violation counts
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    # Analysis scope
    files_analyzed: int
    lines_analyzed: int
    functions_analyzed: int
    classes_analyzed: int

    # Specific metrics (vary by agent)
    custom_metrics: Dict[str, Any] = None


@dataclass
class AgentReport:
    """Complete report from a principle agent"""

    # Agent info
    agent_name: str
    agent_version: str
    principle: str  # e.g., "SOLID Principles"

    # Results
    passed: bool  # True if no critical/high violations
    violations: List[PrincipleViolation]
    metrics: PrincipleMetrics

    # Context
    tech_stack: Optional[str] = None  # e.g., "Django 4.2"
    framework_adapter: Optional[str] = None  # e.g., "DjangoSOLIDAdapter"
    analysis_duration_seconds: float = 0.0

    # Summary
    summary: str  # Human-readable summary
    recommendations_summary: str  # Top recommendations


class PrincipleAgent(ABC):
    """
    Base class for all principle-based agents.

    Design Pattern: Template Method
    - analyze() defines the algorithm structure
    - Subclasses implement specific checks

    Usage:
        agent = SOLIDAgent(db_service)
        report = agent.analyze(code_path, tech_stack)
        if not report.passed:
            for violation in report.violations:
                print(f"{violation.location}: {violation.issue}")
    """

    def __init__(self, db_service, config: Optional[Dict[str, Any]] = None):
        """
        Initialize principle agent.

        Args:
            db_service: DatabaseService instance for rule queries
            config: Optional configuration overrides
        """
        self.db = db_service
        self.config = config or {}
        self.version = "1.0.0"

    @abstractmethod
    def get_principle_name(self) -> str:
        """Return human-readable principle name"""
        pass

    @abstractmethod
    def get_principle_code(self) -> str:
        """Return short code (e.g., 'SOLID', 'DRY')"""
        pass

    @abstractmethod
    def get_mapped_rules(self) -> List[str]:
        """Return rule IDs this agent enforces"""
        pass

    @abstractmethod
    def _run_checks(
            self,
            code_path: Path,
            tech_stack: 'TechStack',
            adapter: 'FrameworkAdapter'
    ) -> List[PrincipleViolation]:
        """
        Run principle-specific checks.

        Implemented by subclasses to perform actual analysis.

        Args:
            code_path: Path to code to analyze
            tech_stack: Detected technology stack
            adapter: Framework-specific adapter

        Returns:
            List of violations found
        """
        pass

    def analyze(
            self,
            code_path: str | Path,
            tech_stack: Optional['TechStack'] = None
    ) -> AgentReport:
        """
        Analyze code for principle violations.

        Template method that defines the analysis algorithm:
        1. Detect tech stack (if not provided)
        2. Get appropriate framework adapter
        3. Run principle checks through adapter
        4. Calculate metrics
        5. Generate report

        Args:
            code_path: Path to code directory or file
            tech_stack: Optional pre-detected tech stack

        Returns:
            Complete agent report with violations and metrics
        """
        import time
        start_time = time.time()

        code_path = Path(code_path)

        # 1. Detect tech stack if not provided
        if tech_stack is None:
            from agentpm.core.plugins import detect_tech_stack
            tech_stack = detect_tech_stack(code_path)

        # 2. Get appropriate adapter
        adapter = self._get_adapter(tech_stack)

        # 3. Run checks through adapter
        violations = self._run_checks(code_path, tech_stack, adapter)

        # 4. Calculate metrics
        metrics = self._calculate_metrics(violations, code_path)

        # 5. Generate report
        duration = time.time() - start_time

        return AgentReport(
            agent_name=self.get_principle_name(),
            agent_version=self.version,
            principle=self.get_principle_name(),
            passed=self._check_passed(violations),
            violations=violations,
            metrics=metrics,
            tech_stack=str(tech_stack),
            framework_adapter=adapter.__class__.__name__,
            analysis_duration_seconds=duration,
            summary=self._generate_summary(violations, metrics),
            recommendations_summary=self._generate_recommendations(violations)
        )

    def _get_adapter(self, tech_stack: 'TechStack') -> 'FrameworkAdapter':
        """
        Get appropriate framework adapter for tech stack.

        Looks up adapter in ADAPTER_REGISTRY based on framework.
        Falls back to GenericAdapter if no specific adapter found.

        Args:
            tech_stack: Detected technology stack

        Returns:
            Framework-specific adapter instance
        """
        from agentpm.agents.adapters import ADAPTER_REGISTRY, GenericAdapter

        # Get primary framework (backend or frontend)
        framework = tech_stack.backend_framework or tech_stack.frontend_framework

        # Look up adapter class
        adapter_class = ADAPTER_REGISTRY.get(
            framework,
            GenericAdapter  # Fallback
        )

        return adapter_class(tech_stack, self.config)

    def _calculate_metrics(
            self,
            violations: List[PrincipleViolation],
            code_path: Path
    ) -> PrincipleMetrics:
        """Calculate metrics from violations and code analysis"""

        # Count by severity
        critical = sum(1 for v in violations if v.severity == ViolationSeverity.CRITICAL)
        high = sum(1 for v in violations if v.severity == ViolationSeverity.HIGH)
        medium = sum(1 for v in violations if v.severity == ViolationSeverity.MEDIUM)
        low = sum(1 for v in violations if v.severity == ViolationSeverity.LOW)

        # Analyze scope
        files_count, lines_count = self._count_code_scope(code_path)

        # Calculate score (0-1.0)
        # Formula: 1.0 - (weighted_violations / max_possible_score)
        weighted_violations = (critical * 10) + (high * 5) + (medium * 2) + (low * 1)
        max_score = files_count * 10  # Assume max 1 critical per file
        score = max(0.0, 1.0 - (weighted_violations / max(max_score, 1)))

        return PrincipleMetrics(
            principle_score=score,
            percentage=int(score * 100),
            total_violations=len(violations),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            files_analyzed=files_count,
            lines_analyzed=lines_count,
            functions_analyzed=0,  # Subclasses can override
            classes_analyzed=0,
            custom_metrics={}
        )

    def _check_passed(self, violations: List[PrincipleViolation]) -> bool:
        """
        Determine if analysis passed.

        Default: Pass if no CRITICAL or HIGH violations
        Subclasses can override for stricter/looser criteria
        """
        critical_or_high = [
            v for v in violations
            if v.severity in (ViolationSeverity.CRITICAL, ViolationSeverity.HIGH)
        ]
        return len(critical_or_high) == 0

    def _count_code_scope(self, code_path: Path) -> tuple[int, int]:
        """Count files and lines in code path"""
        if code_path.is_file():
            return 1, len(code_path.read_text().splitlines())

        files = 0
        lines = 0
        for py_file in code_path.rglob("*.py"):
            if "test" not in str(py_file):  # Exclude tests-BAK
                files += 1
                lines += len(py_file.read_text().splitlines())

        return files, lines

    def _generate_summary(
            self,
            violations: List[PrincipleViolation],
            metrics: PrincipleMetrics
    ) -> str:
        """Generate human-readable summary"""
        if not violations:
            return f"✅ {self.get_principle_name()}: Excellent adherence (100%)"

        severity_summary = []
        if metrics.critical_count:
            severity_summary.append(f"{metrics.critical_count} critical")
        if metrics.high_count:
            severity_summary.append(f"{metrics.high_count} high")
        if metrics.medium_count:
            severity_summary.append(f"{metrics.medium_count} medium")

        severity_str = ", ".join(severity_summary)
        return (
            f"{self.get_principle_name()}: {metrics.percentage}% adherence "
            f"({metrics.total_violations} violations: {severity_str})"
        )

    def _generate_recommendations(
            self,
            violations: List[PrincipleViolation]
    ) -> str:
        """Generate top recommendations"""
        if not violations:
            return "No recommendations - excellent principle adherence"

        # Sort by severity and take top 3
        sorted_violations = sorted(
            violations,
            key=lambda v: (v.severity.value, v.location)
        )[:3]

        recs = []
        for i, v in enumerate(sorted_violations, 1):
            recs.append(f"{i}. {v.location}: {v.recommendation}")

        return "\n".join(recs)

    @abstractmethod
    def explain_principle(self) -> str:
        """
        Return educational explanation of the principle.

        Should include:
        - What the principle is
        - Why it matters
        - Common violations
        - How to apply it
        """
        pass
```

---

## 2. Framework Adapter System

### 2.1 Adapter Base Class

```python
"""
Framework adapter base class.

Location: agentpm/agents/adapters/base.py
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from agentpm.agents.base import PrincipleViolation


@dataclass
class TechStack:
    """Technology stack detected from project"""

    # Languages
    language: Optional[str] = None  # Python, TypeScript, etc.
    language_version: Optional[str] = None  # 3.11, ES2022

    # Frameworks
    backend_framework: Optional[str] = None  # Django, Flask, FastAPI
    frontend_framework: Optional[str] = None  # React, Vue, Angular
    framework_version: Optional[str] = None

    # Database
    database: Optional[str] = None  # PostgreSQL, MySQL, SQLite
    database_version: Optional[str] = None

    # Testing
    testing_framework: Optional[str] = None  # pytest, jest

    # Other
    architecture_style: Optional[str] = None  # hexagonal, microservices
    deployment_platform: Optional[str] = None  # AWS, GCP, Heroku

    def __str__(self) -> str:
        parts = []
        if self.backend_framework:
            parts.append(f"{self.backend_framework} {self.framework_version or ''}")
        if self.frontend_framework:
            parts.append(f"{self.frontend_framework}")
        if self.database:
            parts.append(f"{self.database}")
        return " + ".join(parts) if parts else "Generic"


class FrameworkAdapter(ABC):
    """
    Base class for framework-specific principle adapters.

    Each framework adapter translates universal principles into
    framework-specific checks and recommendations.

    Design Pattern: Adapter Pattern
    - Universal principles (SOLID, DRY, KISS) stay the same
    - Framework adapters translate to framework-specific patterns
    """

    def __init__(self, tech_stack: TechStack, config: Dict[str, Any]):
        """
        Initialize framework adapter.

        Args:
            tech_stack: Detected technology stack
            config: Configuration options
        """
        self.tech_stack = tech_stack
        self.config = config

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return framework name (e.g., 'Django', 'React')"""
        pass

    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """
        Return list of framework patterns this adapter detects.

        Example for Django:
            ['fat_models', 'n_plus_one', 'raw_sql', 'signal_abuse']
        """
        pass

    # Helper methods for common operations
    def find_python_files(self, code_path: Path) -> List[Path]:
        """Find all Python files in path"""
        if code_path.is_file() and code_path.suffix == '.py':
            return [code_path]
        return list(code_path.rglob("*.py"))

    def find_typescript_files(self, code_path: Path) -> List[Path]:
        """Find all TypeScript/JavaScript files"""
        if code_path.is_file() and code_path.suffix in ('.ts', '.tsx', '.js', '.jsx'):
            return [code_path]

        files = []
        for ext in ('.ts', '.tsx', '.js', '.jsx'):
            files.extend(code_path.rglob(f"*{ext}"))
        return files

    def parse_python_ast(self, file_path: Path):
        """Parse Python file to AST"""
        import ast
        return ast.parse(file_path.read_text())

    def get_framework_example(
            self,
            pattern: str,
            before: str,
            after: str
    ) -> Dict[str, str]:
        """
        Generate framework-specific example.

        Args:
            pattern: Framework pattern name
            before: Code showing violation
            after: Refactored code

        Returns:
            Dict with formatted example
        """
        return {
            'framework': self.get_framework_name(),
            'pattern': pattern,
            'before': before,
            'after': after
        }


class GenericAdapter(FrameworkAdapter):
    """Fallback adapter for unknown frameworks"""

    def get_framework_name(self) -> str:
        return "Generic"

    def get_supported_patterns(self) -> List[str]:
        return []
```

---

## 3. SOLID Agent Implementation (Pilot)

### 3.1 SOLIDAgent Class

```python
"""
SOLID Principles agent.

Location: agentpm/agents/principle/solid_agent.py
"""

from agentpm.agents.base import PrincipleAgent, PrincipleViolation, ViolationSeverity
from agentpm.agents.adapters.solid_adapter import SOLIDAdapter


class SOLIDAgent(PrincipleAgent):
    """
    Enforces SOLID principles across codebase.

    Checks:
    - Single Responsibility Principle (SRP)
    - Open/Closed Principle (OCP)
    - Liskov Substitution Principle (LSP)
    - Interface Segregation Principle (ISP)
    - Dependency Inversion Principle (DIP)
    """

    def get_principle_name(self) -> str:
        return "SOLID Principles"

    def get_principle_code(self) -> str:
        return "SOLID"

    def get_mapped_rules(self) -> List[str]:
        return [
            "CQ-031",  # class-single-responsibility
            "CQ-033",  # class-composition-over-inheritance
            "CQ-038",  # class-interface-segregation
            "CQ-039",  # class-dependency-injection
            "DP-035"  # code-single-responsibility
        ]

    def _run_checks(
            self,
            code_path: Path,
            tech_stack: TechStack,
            adapter: SOLIDAdapter
    ) -> List[PrincipleViolation]:
        """Run all SOLID principle checks"""

        violations = []

        # Run each SOLID principle check through adapter
        violations.extend(adapter.check_srp(code_path))  # Single Responsibility
        violations.extend(adapter.check_ocp(code_path))  # Open/Closed
        violations.extend(adapter.check_lsp(code_path))  # Liskov Substitution
        violations.extend(adapter.check_isp(code_path))  # Interface Segregation
        violations.extend(adapter.check_dip(code_path))  # Dependency Inversion

        return violations

    def explain_principle(self) -> str:
        return """
        SOLID Principles (Robert C. Martin / Uncle Bob)

        Five principles for object-oriented design that create maintainable,
        flexible, and testable software:

        **S** - Single Responsibility Principle
            Each class should have one, and only one, reason to change.
            A class should do one thing and do it well.

        **O** - Open/Closed Principle
            Software entities should be open for extension, but closed for modification.
            Add new functionality by extending, not changing existing code.

        **L** - Liskov Substitution Principle
            Derived classes must be substitutable for their base classes.
            Subclasses should strengthen, not weaken, the base class contract.

        **I** - Interface Segregation Principle
            Clients should not be forced to depend on interfaces they don't use.
            Many small, focused interfaces are better than one large interface.

        **D** - Dependency Inversion Principle
            Depend on abstractions, not concretions.
            High-level modules should not depend on low-level modules.

        Benefits:
        - Easier to maintain and modify
        - Better testability
        - Reduced coupling
        - Improved flexibility
        - Clearer architecture

        References:
        - "Agile Software Development, Principles, Patterns, and Practices" - Robert C. Martin
        - "Clean Architecture" - Robert C. Martin
        """
```

### 3.2 Django SOLID Adapter

```python
"""
Django-specific SOLID principle adapter.

Location: agentpm/agents/adapters/django.py
"""

import ast
from pathlib import Path
from typing import List
from agentpm.agents.adapters.base import FrameworkAdapter
from agentpm.agents.base import PrincipleViolation, ViolationSeverity


class DjangoSOLIDAdapter(FrameworkAdapter):
    """
    SOLID principles adapted for Django framework.

    Django-specific patterns:
    - Fat models (SRP violation)
    - Fat views (SRP violation)
    - Concrete ORM usage (DIP violation)
    - N+1 queries (performance + design)
    """

    def get_framework_name(self) -> str:
        return "Django"

    def get_supported_patterns(self) -> List[str]:
        return [
            'fat_models',
            'fat_views',
            'n_plus_one_queries',
            'concrete_dependencies',
            'signal_abuse'
        ]

    def check_srp(self, code_path: Path) -> List[PrincipleViolation]:
        """
        Check Single Responsibility Principle for Django.

        Django-specific checks:
        - Models should only define data structure
        - Views should only handle HTTP layer
        - Business logic belongs in service layer
        """
        violations = []

        for py_file in self.find_python_files(code_path):
            if 'models.py' in str(py_file) or '/models/' in str(py_file):
                violations.extend(self._check_fat_models(py_file))
            elif 'views.py' in str(py_file) or '/views/' in str(py_file):
                violations.extend(self._check_fat_views(py_file))

        return violations

    def _check_fat_models(self, file_path: Path) -> List[PrincipleViolation]:
        """Detect fat models (business logic in models)"""
        violations = []

        try:
            tree = self.parse_python_ast(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a Django model
                    if self._is_django_model(node):
                        # Check for business logic methods
                        business_methods = self._find_business_logic_methods(node)

                        if len(business_methods) > 3:  # Threshold
                            violations.append(PrincipleViolation(
                                principle="Single Responsibility Principle",
                                principle_code="SRP",
                                location=f"{file_path}:{node.lineno}",
                                issue=f"Model {node.name} contains {len(business_methods)} business logic methods",
                                recommendation="Extract business logic to service layer (Django 'skinny models, fat services' pattern)",
                                severity=ViolationSeverity.HIGH,
                                rule_ids=["CQ-031", "DP-035"],
                                framework="Django",
                                framework_pattern="fat_models",
                                explanation=self._srp_explanation(),
                                before_code=self._generate_fat_model_example_before(),
                                after_code=self._generate_fat_model_example_after(),
                                reference_url="https://docs.aipm.dev/principles/solid/srp-django"
                            ))

        except Exception as e:
            # Log error but don't fail entire analysis
            pass

        return violations

    def _is_django_model(self, class_node: ast.ClassDef) -> bool:
        """Check if class inherits from models.Model"""
        for base in class_node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == 'Model' and isinstance(base.value, ast.Name):
                    if base.value.id == 'models':
                        return True
        return False

    def _find_business_logic_methods(self, class_node: ast.ClassDef) -> List[str]:
        """Find methods that look like business logic"""
        business_methods = []

        # Exclude Django model methods
        django_methods = {
            'save', 'delete', '__str__', '__repr__', 'get_absolute_url',
            'clean', 'clean_fields', 'full_clean', 'validate_unique'
        }

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name

                # Skip private, Django builtin, and property methods
                if (method_name.startswith('_') or
                        method_name in django_methods or
                        self._has_decorator(item, 'property')):
                    continue

                # These are likely business logic
                business_methods.append(method_name)

        return business_methods

    def _has_decorator(self, func_node: ast.FunctionDef, decorator_name: str) -> bool:
        """Check if function has specific decorator"""
        for dec in func_node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == decorator_name:
                return True
        return False

    def _srp_explanation(self) -> str:
        return """
        In Django, models should follow the "skinny models, fat services" pattern.
        Models define data structure and simple field-level behavior only.
        Business logic, complex validation, and external API calls belong in the service layer.
        """

    def _generate_fat_model_example_before(self) -> str:
        return """
        # ❌ Fat Model - Multiple Responsibilities
        class Order(models.Model):
            user = models.ForeignKey(User)
            items = models.JSONField()

            def calculate_total(self):  # Business logic
                return sum(item['price'] for item in self.items)

            def send_confirmation_email(self):  # External API
                send_email(self.user.email, "Order confirmed")

            def charge_payment(self):  # External API
                stripe.charge(self.user.payment_method)
        """

    def _generate_fat_model_example_after(self) -> str:
        return """
        # ✅ Skinny Model - Data structure only
        class Order(models.Model):
            user = models.ForeignKey(User)
            items = models.JSONField()
            total = models.DecimalField()

        # services/order_service.py - Business logic
        class OrderService:
            def create_order(self, user, items):
                order = Order.objects.create(
                    user=user,
                    items=items,
                    total=self._calculate_total(items)
                )
                NotificationService.send_confirmation(order)
                PaymentService.charge(order)
                return order
        """

    def check_ocp(self, code_path: Path) -> List[PrincipleViolation]:
        """Check Open/Closed Principle for Django"""
        # Implementation: Detect modification of existing classes vs extension
        return []  # Placeholder

    def check_lsp(self, code_path: Path) -> List[PrincipleViolation]:
        """Check Liskov Substitution Principle for Django"""
        # Implementation: Check Django model inheritance
        return []  # Placeholder

    def check_isp(self, code_path: Path) -> List[PrincipleViolation]:
        """Check Interface Segregation Principle for Django"""
        # Implementation: Check for fat interfaces/mixins
        return []  # Placeholder

    def check_dip(self, code_path: Path) -> List[PrincipleViolation]:
        """
        Check Dependency Inversion Principle for Django.

        Django-specific: Check for concrete ORM dependencies
        """
        # Implementation: Detect direct ORM usage vs repository pattern
        return []  # Placeholder
```

---

## 4. Principle Agent Registry

### 4.1 Registry Design

```python
"""
Principle Agent Registry - Maps rules to agents.

Location: agentpm/agents/registry.py
"""

from typing import Dict, List, Type, Set
from agentpm.agents.base import PrincipleAgent
from agentpm.core.database import DatabaseService


class PrincipleAgentRegistry:
    """
    Registry mapping rules to principle agents.

    Responsibilities:
    - Map rule IDs → agent classes
    - Activate agents based on enabled rules
    - Provide agent instances for analysis

    Usage:
        registry = PrincipleAgentRegistry(db_service)
        active_agents = registry.get_active_agents()
        for agent in active_agents:
            report = agent.analyze(code_path)
    """

    # Static mapping: rule_ids → agent_class
    RULE_TO_AGENT_MAP: Dict[tuple, Type[PrincipleAgent]] = {}

    def __init__(self, db_service: DatabaseService):
        """
        Initialize registry.

        Args:
            db_service: Database service for rule queries
        """
        self.db = db_service
        self._agent_cache: Dict[str, PrincipleAgent] = {}

    @classmethod
    def register_agent(
            cls,
            agent_class: Type[PrincipleAgent],
            rule_ids: List[str]
    ):
        """
        Register an agent class with its rule IDs.

        Args:
            agent_class: PrincipleAgent subclass
            rule_ids: List of rule IDs this agent enforces

        Example:
            PrincipleAgentRegistry.register_agent(
                SOLIDAgent,
                ["CQ-031", "CQ-033", "CQ-038", "CQ-039", "DP-035"]
            )
        """
        cls.RULE_TO_AGENT_MAP[tuple(rule_ids)] = agent_class

    def get_active_agents(self) -> List[PrincipleAgent]:
        """
        Get list of agents to run based on enabled rules.

        Queries database for enabled rules, matches to agents,
        and returns agent instances.

        Returns:
            List of active PrincipleAgent instances
        """
        # Get enabled rules from database
        enabled_rules = self._get_enabled_rules()

        # Find matching agents
        active_agents = []
        seen_agents = set()

        for rule_ids, agent_class in self.RULE_TO_AGENT_MAP.items():
            # Check if any of the agent's rules are enabled
            if any(rule_id in enabled_rules for rule_id in rule_ids):
                agent_name = agent_class.__name__

                # Avoid duplicates
                if agent_name not in seen_agents:
                    # Get or create agent instance
                    agent = self._get_agent_instance(agent_class)
                    active_agents.append(agent)
                    seen_agents.add(agent_name)

        return active_agents

    def _get_enabled_rules(self) -> Set[str]:
        """Query database for enabled rules"""
        with self.db.connect() as conn:
            cursor = conn.execute("""
                SELECT rule_id
                FROM rules
                WHERE enabled = 1
            """)
            return {row[0] for row in cursor.fetchall()}

    def _get_agent_instance(self, agent_class: Type[PrincipleAgent]) -> PrincipleAgent:
        """
        Get or create agent instance (cached).

        Args:
            agent_class: Agent class to instantiate

        Returns:
            Agent instance (cached for performance)
        """
        agent_name = agent_class.__name__

        if agent_name not in self._agent_cache:
            self._agent_cache[agent_name] = agent_class(self.db)

        return self._agent_cache[agent_name]


# Auto-register agents on module load
def _register_all_agents():
    """Register all available principle agents"""
    from agentpm.agents.principle.solid_agent import SOLIDAgent
    from agentpm.agents.principle.dry_agent import DRYAgent
    from agentpm.agents.principle.kiss_agent import KISSAgent

    # SOLID Agent
    PrincipleAgentRegistry.register_agent(
        SOLIDAgent,
        ["CQ-031", "CQ-033", "CQ-038", "CQ-039", "DP-035"]
    )

    # DRY Agent
    PrincipleAgentRegistry.register_agent(
        DRYAgent,
        [f"CQ-{i:03d}" for i in range(21, 31)]  # CQ-021 to CQ-030
    )

    # KISS Agent
    PrincipleAgentRegistry.register_agent(
        KISSAgent,
        ["DP-021", "DP-022", "DP-023", "DP-024", "CQ-023", "CQ-024"]
    )


# Register on import
_register_all_agents()
```

---

## 5. R1 Gate Integration

### 5.1 Enhanced Quality-Gatekeeper

```markdown
<!-- .claude/agents/sub-agents/quality-gatekeeper.md -->

## Enhanced Validation (Principle Agents) ⭐ NEW

### Principle Agent Integration

If principle agents are enabled (via rules database):
1. Query PrincipleAgentRegistry for active agents
2. Run each agent's analysis (parallel execution recommended)
3. Collect all principle reports
4. Add to validation criteria

### Gate Decision Logic (Enhanced)

PASS if:
- All existing checks pass (unchanged):
  - All AC verified
  - Tests passing
  - Coverage ≥90%
  - Static analysis clean
  - Security clean

- AND principle checks pass (new):
  - No CRITICAL principle violations
  - Principle score ≥ configured threshold (default: 70%)

FAIL if:
- Any existing check fails (unchanged)
- OR any CRITICAL principle violation found (new)
- OR principle score < threshold (new, configurable)

### Output Format (Enhanced)

```yaml
gate: R1
status: PASS | FAIL

# Existing criteria (unchanged)
criteria_validation:
  acceptance_criteria: { ... }
  tests: { ... }
  coverage: { ... }
  static_analysis: { ... }
  security: { ... }

# NEW: Principle analysis
principle_analysis:
  enabled: true
  agents_run: 3

  solid:
    score: 78%
    status: WARNING  # No critical, but has violations
    violations: 3
    critical: 0
    high: 2
    medium: 1

  dry:
    score: 92%
    status: PASS
    violations: 1
    critical: 0
    high: 0
    medium: 1

  kiss:
    score: 75%
    status: WARNING
    violations: 2
    critical: 0
    high: 1
    medium: 1

  overall_principle_score: 82%
  threshold: 70%
  threshold_met: true

missing_elements: []
recommendation: "PASS with principle improvement recommendations"
```

### Implementation Pattern

```python
# In quality-gatekeeper agent logic

def aggregate_results(existing_results, principle_results=None):
    """
    Aggregate all validation results including principles.

    Args:
        existing_results: List of results from existing sub-agents
        principle_results: Optional list of principle agent reports

    Returns:
        Complete R1 gate validation result
    """

    # Check existing criteria (unchanged)
    existing_passed = all(r.passed for r in existing_results)

    # Check principle criteria (new)
    principle_passed = True
    principle_score = 100

    if principle_results:
        # Check for critical violations
        has_critical = any(
            v.severity == ViolationSeverity.CRITICAL
            for report in principle_results
            for v in report.violations
        )

        if has_critical:
            principle_passed = False

        # Calculate overall principle score
        scores = [r.metrics.principle_score for r in principle_results]
        principle_score = sum(scores) / len(scores) * 100 if scores else 100

        # Check threshold
        threshold = get_config('principle_score_threshold', 70)
        if principle_score < threshold:
            principle_passed = False

    # Overall gate decision
    gate_passed = existing_passed and principle_passed

    return {
        'gate': 'R1',
        'status': 'PASS' if gate_passed else 'FAIL',
        'existing_criteria': existing_results,
        'principle_analysis': principle_results,
        'overall_principle_score': principle_score,
        'recommendation': _generate_recommendation(gate_passed, principle_results)
    }
```
```

---

## 6. Performance Requirements

### 6.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Per-agent analysis time** | <2 seconds | 95th percentile |
| **3 agents (MVP)** | <6 seconds total | Parallel execution |
| **15 agents (full MVP)** | <30 seconds total | Parallel execution |
| **File parsing** | <0.1s per file | AST parsing |
| **Memory usage** | <100MB per agent | Process memory |

### 6.2 Optimization Strategies

**1. Parallel Execution**
```python
# Run multiple agents concurrently
from concurrent.futures import ThreadPoolExecutor

def run_principle_agents_parallel(agents, code_path):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(agent.analyze, code_path)
            for agent in agents
        ]
        return [f.result() for f in futures]

# 3 agents @ 2s each = 2s total (not 6s)
```

**2. Caching**
```python
# Cache AST parsing results
@lru_cache(maxsize=128)
def parse_file_cached(file_path: str):
    return ast.parse(Path(file_path).read_text())
```

**3. Incremental Analysis**
```python
# Only analyze changed files
def analyze_incremental(agent, changed_files):
    return agent.analyze(changed_files, incremental=True)
```

---

## 7. Testing Strategy

### 7.1 Test Levels

**Unit Tests** (agentpm/agents/tests/):
```python
# test_solid_agent.py
def test_solid_agent_detects_fat_model():
    """Test SOLID agent detects Django fat models"""
    agent = SOLIDAgent(mock_db)

    # Sample fat model code
    code = """
    class Order(models.Model):
        def calculate_total(self): ...
        def send_email(self): ...
        def charge_payment(self): ...
    """

    report = agent.analyze(code, TechStack(backend_framework='Django'))

    assert len(report.violations) > 0
    assert any('Fat model' in v.issue for v in report.violations)
    assert report.metrics.principle_score < 1.0


def test_solid_agent_performance():
    """Test SOLID agent meets performance target"""
    agent = SOLIDAgent(mock_db)

    start = time.time()
    report = agent.analyze(sample_django_project)
    duration = time.time() - start

    assert duration < 2.0, f"Agent took {duration}s (target: <2s)"
```

**Integration Tests** (tests/integration/):
```python
# test_principle_agents_r1_integration.py
def test_principle_agents_in_r1_gate(real_project_fixture):
    """Test principle agents integrate with R1 quality gate"""

    # Enable SOLID rules
    db = real_project_fixture['db_service']
    db.rules.enable(['CQ-031', 'CQ-033'])

    # Run ReviewTestOrch
    result = review_test_orch.execute(build_bundle)

    # Verify principle analysis included
    assert 'principle_analysis' in result
    assert 'solid' in result['principle_analysis']
    assert result['principle_analysis']['solid']['score'] is not None
```

**Framework-Specific Tests**:
```python
# test_django_adapter.py
def test_django_adapter_fat_models():
    """Test Django adapter detects fat models specifically"""
    adapter = DjangoSOLIDAdapter(
        TechStack(backend_framework='Django'),
        config={}
    )

    violations = adapter.check_srp(django_project_path)

    # Should detect fat models
    fat_model_violations = [
        v for v in violations
        if v.framework_pattern == 'fat_models'
    ]
    assert len(fat_model_violations) > 0
```

### 7.2 Test Coverage Targets

- **Overall coverage**: ≥90%
- **Base classes**: 100% (PrincipleAgent, FrameworkAdapter)
- **Agent implementations**: ≥90%
- **Framework adapters**: ≥85%
- **Integration tests**: All critical paths

---

## 8. API Contracts

### 8.1 Public API

```python
# agentpm/agents/__init__.py

"""
Public API for principle-based agents.

Usage:
    from agentpm.agents import analyze_code, get_active_agents

    # Analyze code with all active agents
    reports = analyze_code(code_path)

    # Get specific agent
    solid_agent = get_agent('SOLID')
    report = solid_agent.analyze(code_path)
"""

from agentpm.agents.base import (
    PrincipleAgent,
    PrincipleViolation,
    ViolationSeverity,
    AgentReport,
    PrincipleMetrics
)
from agentpm.agents.registry import PrincipleAgentRegistry


def analyze_code(
        code_path: str,
        db_service: 'DatabaseService',
        agents: Optional[List[str]] = None
) -> List[AgentReport]:
    """
    Analyze code with principle agents.

    Args:
        code_path: Path to code to analyze
        db_service: Database service
        agents: Optional list of agent names to run (default: all active)

    Returns:
        List of agent reports
    """
    registry = PrincipleAgentRegistry(db_service)

    if agents:
        # Run specific agents
        agent_instances = [registry.get_agent(name) for name in agents]
    else:
        # Run all active agents (based on enabled rules)
        agent_instances = registry.get_active_agents()

    return [agent.analyze(code_path) for agent in agent_instances]


def get_active_agents(db_service: 'DatabaseService') -> List[PrincipleAgent]:
    """Get list of active agents based on enabled rules"""
    registry = PrincipleAgentRegistry(db_service)
    return registry.get_active_agents()


def get_agent(
        agent_name: str,
        db_service: 'DatabaseService'
) -> PrincipleAgent:
    """Get specific agent by name"""
    registry = PrincipleAgentRegistry(db_service)
    return registry.get_agent(agent_name)
```

---

## 9. Integration Sequence Diagrams

### 9.1 R1 Gate with Principle Agents

```
┌─────────────────┐
│ ReviewTestOrch  │
└────────┬────────┘
         │
         │ 1. Run existing checks
         ├──────────────────────────────┐
         │                              ▼
    ┌────▼────────┐              ┌──────────────┐
    │ test-runner │              │ ac-verifier  │
    └────┬────────┘              └──────┬───────┘
         │                              │
         │ 2. Get active principle agents
         ▼
    ┌──────────────────────┐
    │ PrincipleAgentRegistry│
    └──────────┬───────────┘
               │ Queries enabled rules
               ▼
        ┌─────────────┐
        │ Database    │
        │ rules table │
        └──────┬──────┘
               │ Returns: SOLID, DRY, KISS enabled
               ▼
    ┌──────────────────────┐
    │ 3. Run agents (parallel)
    ├──────────────────────┤
    │ solid-agent.analyze()│
    │ dry-agent.analyze()  │
    │ kiss-agent.analyze() │
    └──────────┬───────────┘
               │ 3 reports
               ▼
    ┌──────────────────────┐
    │ 4. quality-gatekeeper│
    │    aggregates ALL    │
    ├──────────────────────┤
    │ • Existing results   │
    │ • Principle results  │
    └──────────┬───────────┘
               │
               ▼
         R1 Gate Decision
         PASS with scores
```

### 9.2 Agent Analysis Flow

```
┌───────────────┐
│ SOLIDAgent    │
│ .analyze()    │
└───────┬───────┘
        │
        │ 1. Detect tech stack
        ▼
    ┌────────────────┐
    │ Plugin System  │
    │ (existing)     │
    └───────┬────────┘
            │ Returns: Django 4.2
            │
        │ 2. Get adapter
        ▼
    ┌──────────────────┐
    │ DjangoSOLIDAdapter│
    └───────┬──────────┘
            │
        │ 3. Run checks
        ├─────────────────────┐
        │                     │
        ▼                     ▼
  check_srp()           check_dip()
  (fat models)          (concrete deps)
        │                     │
        └──────────┬──────────┘
                   │ List[Violation]
                   │
        │ 4. Calculate metrics
        ▼
    ┌──────────────┐
    │ Score: 78%   │
    │ Violations:3 │
    └───────┬──────┘
            │
        │ 5. Generate report
        ▼
    ┌──────────────────┐
    │ AgentReport      │
    │ (educational)    │
    └──────────────────┘
```

---

## 10. Directory Structure

```
agentpm/
├── agents/                          ⭐ NEW DIRECTORY
│   ├── __init__.py                  # Public API
│   ├── base.py                      # PrincipleAgent base class
│   ├── registry.py                  # PrincipleAgentRegistry
│   │
│   ├── principle/                   # Principle agent implementations
│   │   ├── __init__.py
│   │   ├── solid_agent.py           # SOLID principles
│   │   ├── dry_agent.py             # Don't Repeat Yourself
│   │   ├── kiss_agent.py            # Keep It Simple
│   │   ├── yagni_agent.py           # You Aren't Gonna Need It
│   │   ├── security_first_agent.py
│   │   ├── test_pyramid_agent.py
│   │   └── ... (more agents)
│   │
│   ├── adapters/                    # Framework-specific adapters
│   │   ├── __init__.py              # ADAPTER_REGISTRY
│   │   ├── base.py                  # FrameworkAdapter base
│   │   ├── solid_adapter.py         # SOLID adapter base
│   │   ├── django.py                # DjangoSOLIDAdapter
│   │   ├── flask.py                 # FlaskSOLIDAdapter
│   │   ├── fastapi.py               # FastAPISOLIDAdapter
│   │   ├── react.py                 # ReactSOLIDAdapter
│   │   └── python.py                # GenericPythonAdapter
│   │
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── ast_helpers.py           # AST parsing utilities
│       ├── metrics_calculator.py    # Metric calculations
│       └── report_formatter.py      # Report generation

tests/agents/                        ⭐ NEW TEST DIRECTORY
├── __init__.py
├── conftest.py                      # Test fixtures
│
├── test_base.py                     # PrincipleAgent base tests
├── test_registry.py                 # Registry tests
│
├── principle/
│   ├── test_solid_agent.py
│   ├── test_dry_agent.py
│   └── test_kiss_agent.py
│
├── adapters/
│   ├── test_django_adapter.py
│   ├── test_python_adapter.py
│   └── test_adapter_selection.py
│
└── integration/
    ├── test_r1_gate_integration.py  # R1 gate tests
    └── test_multi_framework.py      # Multi-stack tests
```

---

## 11. Configuration

### 11.1 Agent Configuration

```yaml
# .aipm/config/principle_agents.yaml (optional)

principle_agents:
  enabled: true

  # Global settings
  parallel_execution: true
  max_workers: 5
  cache_enabled: true
  cache_ttl_seconds: 3600

  # Score thresholds
  thresholds:
    principle_score_minimum: 70  # Percentage
    critical_violations_allowed: 0
    high_violations_allowed: 5

  # Agent-specific settings
  agents:
    solid:
      enabled: true  # Can override via rules
      severity_weights:
        fat_models: HIGH
        concrete_dependencies: MEDIUM

    dry:
      enabled: true
      duplication_threshold: 0.85  # 85% similarity = duplication

    kiss:
      enabled: true
      complexity_threshold: 10
      nesting_threshold: 3

  # Framework-specific settings
  frameworks:
    django:
      patterns:
        fat_models:
          max_methods: 10
          exclude_methods: ['save', 'delete', '__str__']

    react:
      patterns:
        component_complexity:
          max_lines: 200
          max_hooks: 5
```

---

## 12. Error Handling

### 12.1 Graceful Degradation

```python
class PrincipleAgent(ABC):
    """Base class with error handling"""

    def analyze(self, code_path, tech_stack=None) -> AgentReport:
        """Analysis with graceful error handling"""

        try:
            # Normal analysis flow
            violations = self._run_checks(code_path, tech_stack, adapter)
            metrics = self._calculate_metrics(violations, code_path)

        except FileNotFoundError as e:
            # File doesn't exist - return empty report
            return self._error_report(f"File not found: {e}")

        except SyntaxError as e:
            # Invalid syntax - report but don't fail
            return self._warning_report(f"Syntax error (skipping): {e}")

        except Exception as e:
            # Unknown error - log and return error report
            logger.error(f"{self.get_principle_name()} failed: {e}")
            return self._error_report(f"Analysis failed: {e}")

    def _error_report(self, error_message: str) -> AgentReport:
        """Generate error report without failing gate"""
        return AgentReport(
            agent_name=self.get_principle_name(),
            agent_version=self.version,
            principle=self.get_principle_name(),
            passed=True,  # Don't fail gate due to agent errors
            violations=[],
            metrics=PrincipleMetrics(...),
            summary=f"⚠️ Analysis skipped: {error_message}"
        )
```

---

## 13. Acceptance Criteria Validation

### Task #492 Acceptance Criteria Status

- [x] **PrincipleAgent base class designed** ✅
  - Complete interface with analyze(), abstract methods
  - Violation, Metrics, Report dataclasses defined
  - Error handling and graceful degradation

- [x] **Framework adapter interface defined** ✅
  - FrameworkAdapter base class
  - TechStack detection integration
  - Django/Python adapter specifications

- [x] **Agent-to-rule mapping strategy documented** ✅
  - PrincipleAgentRegistry design
  - Auto-registration pattern
  - Rule-based activation logic

- [x] **R1 gate integration approach specified** ✅
  - Enhanced quality-gatekeeper design
  - Parallel execution strategy
  - Backward compatibility maintained

- [x] **Performance requirements defined** ✅
  - <2s per agent target
  - Parallel execution (<6s for 3 agents)
  - Caching and optimization strategies

- [x] **Tech stack detection integration plan** ✅
  - Reuses existing AIPM plugin system
  - TechStack dataclass design
  - Adapter selection logic

- [x] **Test strategy defined** ✅
  - Unit tests for agents and adapters
  - Integration tests for R1 gate
  - Performance tests (<2s target)
  - Framework-specific test cases

---

## 14. Implementation Checklist (Task #493)

### Files to Create (SOLID Agent Pilot)

```bash
# Core classes
[ ] agentpm/agents/__init__.py
[ ] agentpm/agents/base.py (PrincipleAgent, dataclasses)
[ ] agentpm/agents/registry.py (PrincipleAgentRegistry)

# SOLID agent
[ ] agentpm/agents/principle/__init__.py
[ ] agentpm/agents/principle/solid_agent.py

# Adapters
[ ] agentpm/agents/adapters/__init__.py (ADAPTER_REGISTRY)
[ ] agentpm/agents/adapters/base.py (FrameworkAdapter)
[ ] agentpm/agents/adapters/solid_adapter.py (SOLIDAdapter base)
[ ] agentpm/agents/adapters/django.py (DjangoSOLIDAdapter)
[ ] agentpm/agents/adapters/python.py (GenericPythonAdapter)

# Utilities
[ ] agentpm/agents/utils/__init__.py
[ ] agentpm/agents/utils/ast_helpers.py

# Tests
[ ] tests-BAK/agents/conftest.py (fixtures)
[ ] tests-BAK/agents/test_base.py
[ ] tests-BAK/agents/test_registry.py
[ ] tests-BAK/agents/principle/test_solid_agent.py
[ ] tests-BAK/agents/adapters/test_django_adapter.py
```

---

## 15. Next Steps

### Immediate (Task #493 - SOLID Agent)
1. Implement `PrincipleAgent` base class
2. Implement `SOLIDAgent` with SRP check only (pilot)
3. Implement `DjangoSOLIDAdapter` for fat models detection
4. Create comprehensive tests (90%+ coverage)
5. Validate performance (<2s target)

### Then (Task #494 - DRY/KISS)
1. Implement `DRYAgent` (duplication detection)
2. Implement `KISSAgent` (complexity analysis)
3. Extend adapters for DRY/KISS checks
4. Add tests for both agents

### Then (Task #495 - Integration)
1. Enhance quality-gatekeeper
2. Integrate with ReviewTestOrch
3. Test end-to-end R1 gate flow
4. Validate rule-driven activation

---

**Specification Status**: ✅ COMPLETE
**Ready for Implementation**: YES
**Next Task**: #493 (Implement SOLID Agent)

---

*Generated: 2025-10-14*
*Task: #492 - Design Principle Agent Architecture*
*Work Item: WI-89 - Implement Principle-Based Agents System*
