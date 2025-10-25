# Fullstack E-Commerce Platform

A comprehensive Django + React monorepo demonstrating modern fullstack architecture with AIPM integration.

## Architecture

**Backend**: Django 4.2 + PostgreSQL + Celery + Redis
**Frontend**: React 18 + TypeScript + TanStack (Query + Router) + Vite
**Infrastructure**: Docker + Kubernetes + GitHub Actions

## Project Structure

```
├── backend/           # Django REST API
│   ├── apps/         # Django applications
│   │   ├── products/ # Product catalog & search
│   │   ├── orders/   # Order management & checkout
│   │   ├── users/    # Authentication & profiles
│   │   └── analytics/# Business intelligence
│   └── config/       # Django settings
│
├── frontend/         # React SPA
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/      # Route pages
│   │   ├── hooks/      # Custom React hooks
│   │   ├── api/        # TanStack Query integration
│   │   └── stores/     # State management
│   └── tests/         # Jest + RTL tests
│
├── infrastructure/   # DevOps configs
│   ├── docker/      # Dockerfiles & compose
│   ├── k8s/         # Kubernetes manifests
│   └── scripts/     # Deployment scripts
│
└── docs/            # Documentation
    ├── architecture/# ADRs & design docs
    ├── api/         # OpenAPI specs
    └── deployment/  # Ops guides
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Development
```bash
docker-compose up
```

## Features

- **Product Catalog**: Search, filter, detailed views
- **Shopping Cart**: Add/remove items, quantity management
- **Checkout Flow**: Payment integration, order confirmation
- **User Authentication**: JWT-based auth, user profiles
- **Order Management**: Order history, status tracking
- **Analytics Dashboard**: Sales metrics, user behavior

## Testing

**Backend**: pytest with factory_boy fixtures
**Frontend**: Jest + React Testing Library + Playwright
**Coverage Target**: >90% for core business logic

## AIPM Integration

This project demonstrates AIPM's capabilities:

- **Multi-technology detection**: Django, React, PostgreSQL, Docker
- **Work item management**: Features spanning backend + frontend
- **Task dependencies**: API → UI implementation flows
- **Phase workflow**: D1 (Definition) → E1 (Evolution)
- **Context assembly**: Backend, frontend, infrastructure contexts

## API Documentation

- **OpenAPI Schema**: `/api/schema/`
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`

## License

MIT - This is a demonstration project for AIPM documentation.
