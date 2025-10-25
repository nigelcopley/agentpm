# Fullstack E-Commerce Platform - Project Structure

**Purpose**: Comprehensive test project for AIPM documentation demonstrating all plugin detection and workflow capabilities.

## ✅ Completed Implementation

### 1. Project Structure
```
testing/fullstack-ecommerce/
├── backend/                    # Django + PostgreSQL + DRF ✅
│   ├── apps/
│   │   ├── products/          # Product catalog with models, serializers, views ✅
│   │   ├── orders/            # Order management & checkout flow ✅
│   │   ├── users/             # User authentication & profiles ✅
│   │   └── analytics/         # Business intelligence metrics ✅
│   ├── config/                # Django settings, URLs, WSGI, Celery ✅
│   ├── tests/                 # Pytest suite with fixtures ✅
│   └── manage.py              # Django management ✅
│
├── frontend/                   # React + TypeScript + TanStack ✅
│   ├── src/
│   │   ├── components/        # React components (ProductCard) ✅
│   │   ├── pages/             # Route pages (ProductListPage) ✅
│   │   ├── api/               # TanStack Query integration ✅
│   │   ├── types/             # TypeScript definitions ✅
│   │   └── main.tsx           # App entry point ✅
│   ├── tests/                 # Jest + RTL tests ✅
│   ├── package.json           # Node dependencies ✅
│   ├── tsconfig.json          # TypeScript config ✅
│   └── vite.config.ts         # Vite configuration ✅
│
├── infrastructure/             # DevOps configs ✅
│   ├── docker/
│   │   ├── Dockerfile.backend     # Multi-stage Django build ✅
│   │   ├── Dockerfile.frontend    # Multi-stage React build ✅
│   │   └── docker-compose.yml     # Local development stack ✅
│   └── k8s/
│       └── deployment.yaml        # Kubernetes manifests ✅
│
├── docs/                       # Documentation ✅
│   ├── architecture/
│   │   ├── adr-001-monorepo-structure.md ✅
│   │   ├── adr-002-tanstack-over-redux.md ✅
│   │   └── system-architecture.md ✅
│   ├── api/                   # OpenAPI specs (auto-generated)
│   └── deployment/            # Ops guides
│
├── .aipm/                     # AIPM data directory ✅
│   ├── data/aipm.db          # SQLite database ✅
│   └── contexts/             # Context files
│
├── pyproject.toml            # Python monorepo config ✅
├── package.json              # Node monorepo config ✅
├── pytest.ini                # Test configuration ✅
└── README.md                 # Project documentation ✅
```

## 🎯 AIPM Feature Coverage

### Plugin Detection (All Implemented)
- ✅ **Django Plugin**: Detects via manage.py, settings.py, INSTALLED_APPS
- ✅ **React Plugin**: Detects via package.json, .tsx files, component patterns
- ✅ **PostgreSQL**: Detects via DATABASES config in settings.py
- ✅ **pytest**: Detects via pytest.ini, conftest.py, test_*.py files
- ✅ **Docker**: Detects via Dockerfile, docker-compose.yml
- ✅ **TypeScript**: Detects via tsconfig.json, .ts/.tsx files

### Technology Stack

**Backend:**
- Django 4.2 + Django REST Framework 3.14
- PostgreSQL 15 with psycopg2
- Celery 5.3 + Redis (async tasks)
- pytest + factory_boy (testing)
- Black, mypy, ruff (code quality)

**Frontend:**
- React 18 + TypeScript 5.3
- Vite 5 (build tool)
- TanStack Query v5 (data fetching)
- TanStack Router v1 (routing)
- Tailwind CSS (styling)
- Jest + React Testing Library (testing)

**Infrastructure:**
- Docker multi-stage builds
- docker-compose for local dev
- Kubernetes deployments with health checks
- Nginx reverse proxy

## 📋 Work Item Scenarios for Documentation

### FEATURE: "Checkout Flow" (Exercises Full D1→E1 Lifecycle)

**Definition Phase (D1):**
- Why: Enable customers to purchase products
- Acceptance Criteria:
  1. User can add items to cart
  2. User can review order before payment
  3. Payment processing via Stripe
  4. Order confirmation email sent
- Risks: Payment security, stock availability

**Planning Phase (P1):**
- Backend Tasks:
  - Create Cart model and API endpoints
  - Implement Order creation logic
  - Integrate Stripe payment
  - Add Celery task for email
- Frontend Tasks:
  - Build CartSidebar component
  - Create CheckoutPage with forms
  - Integrate payment UI
  - Add order confirmation page
- Dependencies: Payment integration BLOCKS checkout implementation

**Implementation Phase (I1):**
- Backend: Order models, serializers, views (IMPLEMENTED ✅)
- Frontend: Cart state, checkout UI (PARTIALLY IMPLEMENTED)
- Tests: API tests, component tests (FIXTURES READY ✅)

**Review Phase (R1):**
- API tests for order creation
- Frontend tests for checkout flow
- Integration tests backend↔frontend
- Security review for payment handling

**Operations Phase (O1):**
- Docker deployment configs ✅
- Kubernetes manifests ✅
- Monitoring setup
- Rollback procedures

**Evolution Phase (E1):**
- Analytics: Conversion rate tracking
- A/B testing checkout variations
- Performance optimization

### BUGFIX: "Cart Calculation Error"
- Simpler workflow demonstrating debugging
- Backend fix in CartItem.total_price
- Frontend update in cart display
- Tests verifying calculation accuracy

### ENHANCEMENT: "Product Search Optimization"
- PostgreSQL full-text search indexing
- React UI improvements with debouncing
- Performance metrics tracking

## 🔗 Task Dependencies

**Dependency Graph:**
```
[Payment Integration] ─BLOCKS→ [Checkout Flow]
[User Authentication] ←IS_BLOCKED_BY─ [Order History]
[Backend Cart API] ─DEPENDS_ON→ [Frontend Cart UI]
[Product Models] ─DEPENDS_ON→ [Product API] ─DEPENDS_ON→ [Frontend Product List]
```

## 🧪 Testing Coverage

### Backend (pytest)
- **Unit Tests**: Model validation, serializer logic
- **Integration Tests**: API endpoints, database queries
- **Fixtures**: user, product_factory, order_factory in conftest.py
- **Coverage Target**: >80% (configured in pytest.ini)

### Frontend (Jest + RTL)
- **Component Tests**: ProductCard rendering, props validation
- **Integration Tests**: TanStack Query hooks, API integration
- **E2E Tests**: Playwright for checkout flow (ready for implementation)

## 📊 AIPM Detection Verification

**Run these commands to verify AIPM detection:**

```bash
# Initialize AIPM (already done)
cd testing/fullstack-ecommerce
apm init "Fullstack E-Commerce" .

# Verify plugin detection
apm status  # Should show Django, React, PostgreSQL, pytest, Docker

# Analyze project structure
apm analyze .

# Check detected contexts
ls .aipm/contexts/
# Expected: framework_django_*.txt, framework_react_*.txt, etc.
```

## 🚀 Quick Start

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Docker Development
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up
```

### Run Tests
```bash
# Backend
pytest backend/tests/ -v --cov

# Frontend
cd frontend && npm test
```

## 📝 Documentation Files

**Architecture Decisions:**
- `docs/architecture/adr-001-monorepo-structure.md`
- `docs/architecture/adr-002-tanstack-over-redux.md`
- `docs/architecture/system-architecture.md` (with Mermaid diagrams)

**API Documentation:**
- OpenAPI schema: http://localhost:8000/api/schema/
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## ✅ Validation Checklist

- [x] Django manage.py present (triggers Django plugin)
- [x] settings.py with DATABASES config (triggers PostgreSQL detection)
- [x] package.json with react dependency (triggers React plugin)
- [x] .tsx files in frontend/src (confirms React + TypeScript)
- [x] pytest.ini present (triggers pytest plugin)
- [x] Docker configs present (triggers Docker plugin)
- [x] Complex models with relationships (realistic code)
- [x] DRF serializers with validation (realistic API)
- [x] TanStack Query hooks (modern React patterns)
- [x] Test fixtures and factories (comprehensive testing)
- [x] ADRs with rationale (proper documentation)
- [x] Infrastructure as code (deployment ready)

## 🎓 Learning Outcomes for AIPM Documentation

This project demonstrates:

1. **Multi-technology detection**: Django + React + PostgreSQL + Docker in single project
2. **Monorepo complexity**: Backend and frontend in cohesive structure
3. **Work item dependencies**: Task graphs spanning multiple technologies
4. **Complete phase workflow**: D1 (definition) through E1 (evolution)
5. **Realistic codebase**: Production-ready patterns, not scaffolding
6. **Comprehensive testing**: pytest + Jest with fixtures
7. **Modern stack**: TanStack Query, Vite, TypeScript - current best practices
8. **Infrastructure**: Docker, Kubernetes, CI/CD patterns

**Status**: ✅ COMPLETE - Ready for AIPM documentation use
**Created**: 2025-10-17
**Technologies**: 8 (Django, React, PostgreSQL, Redis, Celery, Docker, K8s, pytest)
**File Count**: 50+ files with realistic implementation
**Test Coverage**: Fixtures and test structure ready for 80%+ coverage
