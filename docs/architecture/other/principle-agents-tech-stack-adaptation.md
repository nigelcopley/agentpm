# Principle-Based Agents - Technology Stack Adaptation

**Status**: Design Specification
**Created**: 2025-10-14
**Purpose**: Define how principle-based agents adapt to specific frameworks, languages, and technology stacks

---

## 🎯 Core Concept: Universal Principles + Tech-Specific Implementation

**Philosophy**: Principles are universal, but enforcement mechanisms are framework-specific.

```
Universal Principle (What)
    ↓
Technology Adapter (How)
    ↓
Framework-Specific Checker (Where)
```

**Example**: SOLID Principles
- **Universal**: "Each class should have one reason to change" (SRP)
- **Django Adapter**: Check Django models, views, serializers separately
- **React Adapter**: Check component responsibilities, hook usage
- **Flask Adapter**: Check blueprints, route handlers, services

---

## 🏗️ Architecture: Three-Layer System

### Layer 1: Universal Principle Agent (Framework-Agnostic)
```python
class SOLIDAgent(PrincipleAgent):
    """Universal SOLID principles - framework agnostic"""

    def analyze(self, code_path: str, tech_stack: TechStack) -> AgentReport:
        # Get appropriate adapter for tech stack
        adapter = self._get_adapter(tech_stack)

        # Run universal checks through adapter
        violations = []
        violations.extend(adapter.check_srp(code_path))
        violations.extend(adapter.check_ocp(code_path))
        violations.extend(adapter.check_lsp(code_path))
        violations.extend(adapter.check_isp(code_path))
        violations.extend(adapter.check_dip(code_path))

        return self._generate_report(violations)
```

### Layer 2: Technology Adapter (Framework-Aware)
```python
class DjangoSOLIDAdapter(SOLIDAdapter):
    """Adapts SOLID checks for Django framework"""

    def check_srp(self, code_path: str) -> List[Violation]:
        """
        Django-specific SRP checks:
        - Models: Should only define data structure
        - Views: Should only handle HTTP layer
        - Serializers: Should only handle serialization
        - Managers: Should only handle queries
        - Signals: Should only handle events
        """
        violations = []

        # Check models
        for model in self._find_models(code_path):
            if self._has_business_logic(model):
                violations.append(Violation(
                    principle="SRP",
                    location=f"{model.file}:{model.line}",
                    issue=f"Model {model.name} contains business logic",
                    recommendation="Extract business logic to service layer",
                    framework_specific=True,
                    django_pattern="fat_models_antipattern"
                ))

        return violations
```

### Layer 3: Framework-Specific Checkers (Pattern Detection)
```python
class DjangoPatternChecker:
    """Detects Django-specific patterns and anti-patterns"""

    PATTERNS = {
        'fat_models': {
            'description': 'Business logic in models',
            'detection': lambda model: len(model.methods) > 10,
            'severity': 'HIGH',
            'recommendation': 'Extract to service layer'
        },
        'fat_views': {
            'description': 'Too much logic in views',
            'detection': lambda view: view.complexity > 10,
            'severity': 'HIGH',
            'recommendation': 'Extract to services/forms'
        },
        'n_plus_one': {
            'description': 'N+1 query in ORM',
            'detection': lambda query: has_related_access_in_loop(query),
            'severity': 'CRITICAL',
            'recommendation': 'Use select_related() or prefetch_related()'
        }
    }
```

---

## 🔧 Technology Stack Detection

### Automatic Detection (via AIPM Plugin System)
```python
class TechStackDetector:
    """Detects technology stack from project structure"""

    def detect(self, project_path: str) -> TechStack:
        stack = TechStack()

        # Language detection
        if self._has_file('requirements.txt') or self._has_file('pyproject.toml'):
            stack.language = 'Python'
            stack.version = self._detect_python_version()

        # Backend framework detection
        if self._has_import('django'):
            stack.backend_framework = 'Django'
            stack.framework_version = self._detect_django_version()
        elif self._has_import('flask'):
            stack.backend_framework = 'Flask'
        elif self._has_import('fastapi'):
            stack.backend_framework = 'FastAPI'

        # Frontend framework detection
        if self._has_file('package.json'):
            deps = self._parse_package_json()
            if 'react' in deps:
                stack.frontend_framework = 'React'
            elif 'vue' in deps:
                stack.frontend_framework = 'Vue'
            elif 'angular' in deps:
                stack.frontend_framework = 'Angular'

        # Database detection
        if self._has_config('postgresql'):
            stack.database = 'PostgreSQL'
        elif self._has_config('mysql'):
            stack.database = 'MySQL'
        elif self._has_file('*.db'):
            stack.database = 'SQLite'

        # Testing framework
        if self._has_import('pytest'):
            stack.testing_framework = 'pytest'
        elif self._has_import('unittest'):
            stack.testing_framework = 'unittest'

        return stack
```

---

## 📚 Framework-Specific Adapters Library

### Python Backend Frameworks

#### Django Adapter
```python
class DjangoAdapter:
    """Principle adaptation for Django"""

    # SOLID Principles
    def check_srp_models(self):
        """Models should only define structure"""
        return [
            "No business logic in models",
            "No validation beyond field constraints",
            "No external API calls",
            "Move complex logic to services"
        ]

    def check_srp_views(self):
        """Views should only handle HTTP"""
        return [
            "No database queries in views",
            "No business logic in views",
            "Delegate to forms/serializers/services",
            "Keep views thin (<20 lines)"
        ]

    # DRY Principle
    def check_dry_querysets(self):
        """Detect duplicate querysets"""
        return [
            "Extract common queries to managers",
            "Use model methods for repeated logic",
            "Create custom QuerySets for reusability"
        ]

    # Performance
    def check_n_plus_one(self):
        """Detect N+1 queries"""
        patterns = [
            "for obj in Model.objects.all(): obj.related",
            "template iteration with foreign keys",
            "serializer nested relations without prefetch"
        ]
        return self._detect_patterns(patterns)

    # Security
    def check_security(self):
        """Django-specific security"""
        return [
            "CSRF protection enabled",
            "SQL injection via raw() queries",
            "XSS in mark_safe() usage",
            "Insecure deserialization in pickle",
            "Debug mode in production"
        ]
```

#### Flask Adapter
```python
class FlaskAdapter:
    """Principle adaptation for Flask"""

    # SOLID Principles
    def check_srp_routes(self):
        """Routes should only handle HTTP"""
        return [
            "No business logic in route handlers",
            "Delegate to service layer",
            "Keep routes thin (decorators + delegation)",
            "Use blueprints for organization"
        ]

    # Dependency Injection
    def check_dependency_injection(self):
        """Flask-specific DI patterns"""
        return [
            "Use Flask extensions for services",
            "Avoid global state (use app context)",
            "Use dependency injection via decorators",
            "Application factory pattern"
        ]

    # Security
    def check_security(self):
        """Flask-specific security"""
        return [
            "CSRF protection (Flask-WTF)",
            "SQL injection in raw SQL",
            "Session security (SECRET_KEY)",
            "XSS in Jinja2 templates",
            "Insecure cookie settings"
        ]
```

#### FastAPI Adapter
```python
class FastAPIAdapter:
    """Principle adaptation for FastAPI"""

    # Type Safety
    def check_type_safety(self):
        """FastAPI relies on type hints"""
        return [
            "All route parameters type-hinted",
            "Pydantic models for request/response",
            "No Any types in public APIs",
            "Dependency injection with Depends()",
            "Proper async/await usage"
        ]

    # Performance
    def check_async_patterns(self):
        """Async/await best practices"""
        return [
            "Use async def for I/O operations",
            "Await all database calls",
            "Background tasks for slow operations",
            "Connection pooling configured"
        ]
```

---

### Frontend Frameworks

#### React Adapter
```python
class ReactAdapter:
    """Principle adaptation for React"""

    # SOLID Principles
    def check_srp_components(self):
        """Components should have single responsibility"""
        return [
            "Max 200 lines per component",
            "Extract custom hooks for logic",
            "Separate presentational from container",
            "One component per file"
        ]

    # React-Specific Patterns
    def check_hooks_rules(self):
        """React Hooks best practices"""
        return [
            "Hooks called at top level only",
            "Hooks called in same order",
            "Custom hooks start with 'use'",
            "useEffect dependencies complete",
            "Avoid infinite render loops"
        ]

    # Performance
    def check_performance(self):
        """React performance patterns"""
        return [
            "Use React.memo for expensive components",
            "useMemo for expensive calculations",
            "useCallback for functions in deps",
            "Avoid anonymous functions in props",
            "Key prop for lists"
        ]
```

#### Vue Adapter
```python
class VueAdapter:
    """Principle adaptation for Vue"""

    # Component Design
    def check_component_design(self):
        """Vue component best practices"""
        return [
            "Composition API over Options API",
            "Max 300 lines per component",
            "Extract composables for reusability",
            "Props validation required",
            "Emit events for parent communication"
        ]

    # Reactivity
    def check_reactivity(self):
        """Vue reactivity patterns"""
        return [
            "Use ref() for primitives",
            "Use reactive() for objects",
            "Avoid mutating props",
            "Computed for derived state",
            "Watch with proper cleanup"
        ]
```

---

### Database Adapters

#### PostgreSQL Adapter
```python
class PostgreSQLAdapter:
    """Principle adaptation for PostgreSQL"""

    # Performance
    def check_indexes(self):
        """Index optimization"""
        return [
            "Foreign keys have indexes",
            "WHERE clause columns indexed",
            "Partial indexes for filtered queries",
            "Avoid index on high-cardinality columns",
            "EXPLAIN ANALYZE for slow queries"
        ]

    # Schema Design
    def check_schema_design(self):
        """PostgreSQL-specific schema patterns"""
        return [
            "Use JSONB for semi-structured data",
            "Array types for collections",
            "Constraints at database level",
            "Proper normalization (3NF minimum)",
            "Enums for fixed value sets"
        ]
```

---

## 🎨 Example: SOLID Agent Across Tech Stacks

### Scenario: Analyzing an E-commerce Application

**Detected Tech Stack**:
```yaml
backend:
  language: Python 3.11
  framework: Django 4.2
  database: PostgreSQL 15
  testing: pytest

frontend:
  framework: React 18
  state_management: Redux Toolkit
  testing: Jest + React Testing Library
```

**SOLID Agent Analysis**:

#### 1. Django Backend
```python
# VIOLATION: Fat Model (SRP)
class Order(models.Model):
    user = models.ForeignKey(User)
    total = models.DecimalField()

    def calculate_total(self):  # ❌ Business logic in model
        ...

    def send_confirmation_email(self):  # ❌ Side effect in model
        ...

    def charge_payment(self):  # ❌ External API in model
        ...

# RECOMMENDATION (Django-specific)
class Order(models.Model):
    user = models.ForeignKey(User)
    total = models.DecimalField()
    # Model only has data structure

# services/order_service.py
class OrderService:
    def calculate_total(self, order): ...
    def send_confirmation_email(self, order): ...

# services/payment_service.py
class PaymentService:
    def charge_payment(self, order): ...
```

#### 2. React Frontend
```typescript
// VIOLATION: Component doing too much (SRP)
function OrderPage() {  // ❌ Handles data fetching, business logic, and UI
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Data fetching
        fetchOrders().then(setOrders);
    }, []);

    const calculateTotal = (order) => {  // Business logic
        return order.items.reduce((sum, item) => sum + item.price, 0);
    };

    return (
        <div>
            {/* Complex UI rendering */}
        </div>
    );
}

// RECOMMENDATION (React-specific)
// Custom hook for data fetching
function useOrders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchOrders().then(setOrders);
    }, []);

    return { orders, loading };
}

// Business logic in utility
const calculateTotal = (order) =>
    order.items.reduce((sum, item) => sum + item.price, 0);

// Presentational component
function OrderPage() {
    const { orders, loading } = useOrders();

    return <OrderList orders={orders} loading={loading} />;
}
```

---

## 🔌 Plugin Architecture for New Frameworks

### Adding a New Framework Adapter

**Step 1: Define Framework Profile**
```yaml
# configs/frameworks/nestjs.yaml
framework: NestJS
language: TypeScript
patterns:
  - name: "Dependency Injection"
    markers: ["@Injectable()", "@Module()"]
  - name: "Controller Pattern"
    markers: ["@Controller()", "@Get()"]
  - name: "Service Layer"
    markers: ["@Injectable() class.*Service"]

conventions:
  naming:
    controllers: "*.controller.ts"
    services: "*.service.ts"
    modules: "*.module.ts"

  srp_rules:
    - "Controllers handle HTTP only"
    - "Services contain business logic"
    - "Repositories handle data access"
```

**Step 2: Create Adapter Class**
```python
class NestJSAdapter(SOLIDAdapter):
    """SOLID principles for NestJS"""

    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.ast_parser = TypeScriptParser()

    def check_srp(self, code_path: str) -> List[Violation]:
        violations = []

        # Check controllers
        for controller in self._find_controllers(code_path):
            if self._has_business_logic(controller):
                violations.append(Violation(
                    principle="SRP",
                    location=f"{controller.file}:{controller.line}",
                    issue=f"Controller {controller.name} contains business logic",
                    recommendation="Extract to service layer using @Injectable()",
                    tech_stack="NestJS",
                    example=self._generate_nestjs_example(controller)
                ))

        return violations

    def _generate_nestjs_example(self, controller):
        return """
        // ❌ BEFORE (Business logic in controller)
        @Controller('orders')
        export class OrdersController {
            @Post()
            async create(@Body() dto: CreateOrderDto) {
                // Business logic here ❌
                const total = dto.items.reduce(...);
                const order = await this.db.save(...);
                return order;
            }
        }

        // ✅ AFTER (Delegated to service)
        @Controller('orders')
        export class OrdersController {
            constructor(private orderService: OrdersService) {}

            @Post()
            async create(@Body() dto: CreateOrderDto) {
                return this.orderService.create(dto);
            }
        }

        @Injectable()
        export class OrdersService {
            async create(dto: CreateOrderDto) {
                // Business logic in service ✅
                const total = this.calculateTotal(dto);
                return this.repository.save(...);
            }
        }
        """
```

**Step 3: Register in Agent System**
```python
# agents/solid_agent.py
ADAPTERS = {
    'Django': DjangoAdapter,
    'Flask': FlaskAdapter,
    'FastAPI': FastAPIAdapter,
    'Express': ExpressAdapter,
    'NestJS': NestJSAdapter,  # ✅ New adapter registered
    'React': ReactAdapter,
    'Vue': VueAdapter,
    'Angular': AngularAdapter
}

class SOLIDAgent(PrincipleAgent):
    def _get_adapter(self, tech_stack: TechStack):
        framework = tech_stack.backend_framework or tech_stack.frontend_framework
        adapter_class = ADAPTERS.get(framework, GenericAdapter)
        return adapter_class(tech_stack)
```

---

## 🎓 Framework-Specific Educational Content

### Example: Django SRP Violation

**Generic Explanation**:
```yaml
principle: "Single Responsibility Principle"
violation: "Class has multiple responsibilities"
recommendation: "Extract separate classes for each responsibility"
```

**Django-Specific Explanation**:
```yaml
principle: "Single Responsibility Principle (Django)"
violation: "Django Model contains business logic, validation, and external API calls"

django_context: |
  In Django, models should follow the "skinny models, fat services" pattern.
  Models define data structure and simple field-level behavior only.

recommendation: |
  Extract responsibilities to appropriate Django components:
  - Business logic → Service layer (services/*.py)
  - Complex validation → Form classes or Serializers
  - External APIs → Separate service classes
  - Queries → Custom Managers/QuerySets

example_before: |
  # ❌ Fat Model - Multiple Responsibilities
  class Order(models.Model):
      user = models.ForeignKey(User)
      items = models.JSONField()

      def calculate_total(self):  # Business logic
          return sum(item['price'] for item in self.items)

      def validate_items(self):  # Validation
          if not self.items:
              raise ValueError("Order must have items")

      def send_confirmation(self):  # External API
          send_email(self.user.email, "Order confirmed")

      def charge_payment(self):  # External API
          stripe.charge(self.user.payment_method)

example_after: |
  # ✅ Skinny Model - Data structure only
  class Order(models.Model):
      user = models.ForeignKey(User)
      items = models.JSONField()
      total = models.DecimalField()

      objects = OrderManager()  # Custom manager for queries

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

      def _calculate_total(self, items):
          return sum(item['price'] for item in items)

  # services/notification_service.py - Email handling
  class NotificationService:
      @staticmethod
      def send_confirmation(order):
          send_email(order.user.email, "Order confirmed")

  # services/payment_service.py - Payment handling
  class PaymentService:
      @staticmethod
      def charge(order):
          stripe.charge(order.user.payment_method, order.total)

django_best_practices: |
  1. **Skinny Models**: Only data structure and simple properties
  2. **Fat Services**: Business logic in service layer
  3. **Custom Managers**: Complex queries
  4. **Serializers**: API serialization and validation
  5. **Forms**: Web form validation
  6. **Signals**: Decoupled event handling (use sparingly)

references:
  - "Two Scoops of Django: Best Practices"
  - "Django Design Patterns and Best Practices"
  - "https://docs.djangoproject.com/en/stable/topics/db/models/"
```

---

## 📊 Tech Stack Impact Matrix

### How Each Principle Maps to Tech Stacks

| Principle | Django | Flask | FastAPI | React | Vue | Express |
|-----------|--------|-------|---------|-------|-----|---------|
| **SOLID/SRP** | Models/Views/Serializers | Routes/Services | Routes/Depends | Components/Hooks | Components/Composables | Routes/Services |
| **DRY** | Managers/Mixins | Blueprints/Extensions | Dependencies | Custom Hooks | Composables | Middleware |
| **KISS** | Querysets | Simple routes | Type hints | Functional components | Composition API | Express middleware |
| **Dependency Injection** | Settings/Apps | Flask extensions | Depends() | Props/Context | Provide/Inject | Constructor injection |
| **Test Pyramid** | pytest-django | pytest-flask | pytest + TestClient | Jest + RTL | Vitest + VTU | Jest + Supertest |

---

## 🚀 Real-World Usage Example

### Multi-Stack Application Analysis

**Project Structure**:
```
ecommerce/
├── backend/          # Django REST API
├── frontend/         # React SPA
├── mobile/           # React Native
└── admin/            # Vue.js admin panel
```

**Agent Configuration**:
```python
# Configure agents for multi-stack project
config = PrincipleAgentConfig(
    tech_stacks=[
        TechStack(path='backend/', framework='Django', language='Python'),
        TechStack(path='frontend/', framework='React', language='TypeScript'),
        TechStack(path='mobile/', framework='React Native', language='TypeScript'),
        TechStack(path='admin/', framework='Vue', language='TypeScript')
    ]
)

# Run SOLID agent across all stacks
solid_agent = SOLIDAgent(config)
results = solid_agent.analyze_multi_stack()

# Results grouped by tech stack
for stack, report in results.items():
    print(f"\n{stack.framework} ({stack.path}):")
    print(f"  SOLID Score: {report.score}%")
    print(f"  Violations: {len(report.violations)}")

    for violation in report.violations[:3]:  # Top 3
        print(f"    - {violation.location}: {violation.issue}")
```

**Output**:
```
Django (backend/):
  SOLID Score: 78%
  Violations: 12
    - models/order.py:45: Model contains business logic (SRP)
    - views/checkout.py:23: View has multiple responsibilities (SRP)
    - services/payment.py:12: Depends on concrete Stripe class (DIP)

React (frontend/):
  SOLID Score: 85%
  Violations: 8
    - components/OrderPage.tsx:34: Component handles data + UI (SRP)
    - hooks/useCart.ts:56: Hook has side effects (SRP)
    - utils/api.ts:23: Concrete fetch implementation (DIP)

React Native (mobile/):
  SOLID Score: 82%
  Violations: 9
    - Similar patterns to React frontend

Vue (admin/):
  SOLID Score: 88%
  Violations: 5
    - components/Dashboard.vue:78: Component too complex (SRP)
    - composables/useOrders.ts:34: Mixed concerns (SRP)
```

---

## 🎯 Benefits of Tech-Specific Adaptation

### 1. **Contextual Recommendations**
- ❌ Generic: "Extract this to a separate class"
- ✅ Django: "Extract to service layer following Django's skinny models pattern"
- ✅ React: "Extract to custom hook with 'use' prefix"

### 2. **Framework Best Practices**
- Enforces established patterns (Django's MTV, React Hooks rules)
- Detects framework-specific anti-patterns
- Suggests framework-appropriate solutions

### 3. **Educational Value**
- Teaches framework-specific patterns
- Shows real-world examples in context
- Links to framework documentation

### 4. **Accurate Detection**
- Understands framework conventions
- Recognizes valid framework patterns
- Reduces false positives

---

## 🔮 Future Enhancements

### Framework Coverage Expansion
- **Backend**: Ruby on Rails, Laravel, Spring Boot, ASP.NET
- **Frontend**: Svelte, Angular, Next.js, Nuxt
- **Mobile**: Flutter, SwiftUI, Jetpack Compose
- **Full-Stack**: Remix, SvelteKit, Astro

### AI-Powered Adaptation
- Learn project-specific patterns
- Adapt to team conventions
- Generate framework-specific refactorings automatically

### Framework Version Support
- Track breaking changes between versions
- Migrate patterns (Class components → Hooks)
- Version-specific best practices

---

**Document Status**: ✅ Design Complete
**Next Steps**:
1. Implement core adapter system
2. Create Django + React adapters (MVP)
3. Build plugin system for community adapters
4. Test with multi-stack projects

---

*Generated: 2025-10-14 by Claude Code*
*Related: principle-agents-catalog.md*
