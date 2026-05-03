# Finance Dashboard — Backend API

A production-deployed, role-based finance management REST API built with Django and Django REST Framework. The system supports multi-role user access, complete financial transaction management, and aggregated dashboard analytics — designed to serve a real-world finance dashboard frontend.

> **Swagger Docs:** `https://financedashboardbackend.up.railway.app/api/docs/`

> **Health Check:** `https://financedashboardbackend.up.railway.app/api/health/`

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Architecture & Design](#architecture--design)
3. [Local Setup](#local-setup)
4. [API Overview](#api-overview)
5. [Role Access Matrix](#role-access-matrix)
6. [Performance & Database](#performance--database)
7. [Security](#security)
8. [Deployment](#deployment)
9. [Testing](#testing)
10. [Assumptions & Tradeoffs](#assumptions--tradeoffs)

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Language | Python 3.12 | Stability, ecosystem |
| Framework | Django 5.0 + DRF 3.15 | Reliable ORM, rapid API development |
| Database | PostgreSQL 16 | Relational integrity, powerful aggregation |
| Auth | JWT (SimpleJWT) | Stateless, rotation-safe, frontend-friendly |
| API Docs | drf-spectacular + Swagger UI | Spec always in sync with code |
| Rate Limiting | django-ratelimit | Abuse prevention on write endpoints |
| Filtering | django-filter | Clean, declarative query filtering |
| CORS | django-cors-headers | Cross-origin frontend compatibility |
| Testing | pytest + pytest-django | Superior fixture system, readable output |
| Deployment | Railway + Gunicorn + Whitenoise | Zero-config PaaS, production-grade WSGI |

## Architecture & Design

### Project Structure

```
.
├── core/                        # Django project config
│   ├── settings/
│   │   ├── base.py              # Shared settings
│   │   ├── development.py       # Local dev overrides
│   │   ├── production.py        # Production overrides
│   │   └── test.py              # Test overrides
│   ├── exceptions.py            # Global error response formatter
│   ├── health.py                # Health check endpoint
│   └── urls.py                  # Root URL config
│
└── apps/
    ├── users/                   # Auth, user management, permissions
    │   ├── models.py
    │   ├── serializers.py
    │   ├── permissions.py
    │   ├── views/
    │   └── urls/
    │
    ├── finance/                 # Transaction management
    │   ├── models.py
    │   ├── serializers.py
    │   ├── filters.py
    │   └── views.py
    │
    └── dashboard/               # Analytics
        ├── services.py
        └── views.py
```

### Key Design Decisions

**Vertical App Slicing** — Each app owns its domain completely. User auth logic never bleeds into financial transaction handling. Clear boundaries make the codebase navigable and testable in isolation.

**Service Layer Pattern** — Dashboard analytics live in `apps/dashboard/services.py` as pure Python functions. Views just call services and return responses. This means business logic can be unit-tested without HTTP context and reused from background tasks.

**Custom Permission Classes** — Role enforcement is done via dedicated DRF `BasePermission` classes rather than inline `if` checks. Each view declares its permission requirement explicitly via `get_permissions()`, making access control auditable at a glance.

**Global Error Contract** — A custom exception handler ensures every error response follows `{"success": false, "error": {"status_code": ..., "detail": ...}}`. No HTML 500 dumps ever reach the client.

---

## Local Setup

### Prerequisites
- Python 3.12
- Docker Desktop (for PostgreSQL)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/finance_dashboard_backend.git
cd finance_dashboard_backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```

The defaults in `.env.example` work out of the box for local development. No changes needed to get started.

### 4. Start PostgreSQL
```bash
docker compose up -d
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create an admin user
```bash
python manage.py shell -c "
from apps.users.models import User
User.objects.create_user(
    email='admin@.com',
    password='AdminPass123!',
    role='admin',
    is_active=True
)
print('Admin created.')
"
```

### 7. Start the development server
```bash
python manage.py runserver
```

**API available at:** `http://localhost:8000`
**Swagger UI at:** `http://localhost:8000/api/docs/`

---

## API Overview

### Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register/` | Public | Register a new user |
| POST | `/api/auth/login/` | Public | Login, receive access + refresh tokens |
| POST | `/api/auth/refresh/` | Public | Refresh access token |
| POST | `/api/auth/logout/` | Authenticated | Blacklist refresh token |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/users/` | Admin | List all users |
| GET | `/api/users/me/` | Authenticated | Get current user profile |
| GET | `/api/users/:id/` | Admin | Retrieve a user |
| PATCH | `/api/users/:id/` | Admin | Update role or active status |
| DELETE | `/api/users/:id/` | Admin | Delete a user |

### Transactions
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/transactions/` | Analyst, Admin | List transactions |
| POST | `/api/transactions/` | Admin | Create a transaction |
| GET | `/api/transactions/:id/` | Analyst, Admin | Retrieve a transaction |
| PATCH | `/api/transactions/:id/` | Admin | Update a transaction |
| DELETE | `/api/transactions/:id/` | Admin | Soft delete a transaction |

#### Query Parameters for `GET /api/transactions/`
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search notes, category, or type |
| `type` | string | `income` or `expense` |
| `category` | string | `salary`, `rent`, `groceries`, etc. |
| `date_from` | date | `YYYY-MM-DD` |
| `date_to` | date | `YYYY-MM-DD` |
| `amount_min` | number | Minimum amount |
| `amount_max` | number | Maximum amount |
| `ordering` | string | `date`, `-date`, `amount`, `-amount` |
| `page` | integer | Page number |
| `page_size` | integer | Results per page (default: 20, max: 100) |

### Dashboard
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/dashboard/summary/` | All authenticated | Total income, expenses, net balance |
| GET | `/api/dashboard/categories/` | Analyst, Admin | Breakdown by category |
| GET | `/api/dashboard/trends/monthly/` | Analyst, Admin | Monthly income vs expense |
| GET | `/api/dashboard/trends/weekly/` | Analyst, Admin | Weekly income vs expense |
| GET | `/api/dashboard/activity/` | Analyst, Admin | Recent transactions feed |

---

## Role Access Matrix

| Action | Viewer | Analyst | Admin |
|--------|:------:|:-------:|:-----:|
| View dashboard summary | ✅ | ✅ | ✅ |
| View trends + category breakdown | ❌ | ✅ | ✅ |
| View recent activity | ❌ | ✅ | ✅ |
| List + retrieve transactions | ❌ | ✅ | ✅ |
| Create transaction | ❌ | ❌ | ✅ |
| Update + delete transaction | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## Performance & Database

### N+1 Query Prevention
All transaction queries use `.select_related("created_by")`. Serializing 100 transactions with user data costs **1 SQL query**, not 101.

### Aggregation Pushed to PostgreSQL
Dashboard metrics (`get_monthly_trends`, `get_category_breakdown`, `get_summary`) use Django ORM aggregation with `TruncMonth`, `TruncWeek`, `Sum`, and `Count`. PostgreSQL handles the computation — not Python loops over thousands of objects.

### Database Indexing
The `is_deleted` flag on transactions is indexed (`db_index=True`) since every list query filters on it. The `created_by` foreign key and `date` field benefit from PostgreSQL's automatic B-tree indexing, keeping filtered and paginated queries fast.

### Pagination
Transaction list responses are paginated (default 20 per page, max 100). Responses include `count`, `total_pages`, `current_page`, `next`, and `previous` for full client-side navigation support.

---

## Security

### JWT with Refresh Token Blacklisting
Access tokens are short-lived (60 min). Refresh tokens rotate on every use and are blacklisted on logout via SimpleJWT's token blacklist app — preventing token reuse after a user signs out.

### Multi-Layer RBAC
Three custom permission classes (`IsAdmin`, `IsAnalystOrAbove`, `IsAnyAuthenticatedUser`) are applied at the view level via `get_permissions()`. Role enforcement is explicit, auditable, and never implicit.

### Rate Limiting
Auth endpoints (register, login) are rate-limited to 10 requests/minute per IP. Write endpoints are rate-limited to 60 requests/minute per user. Backed by Django's cache framework.

### Soft Deletes
Deleted transactions are flagged (`is_deleted=True`) rather than removed. A custom model manager (`ActiveTransactionManager`) filters them from all default queries automatically. Data is recoverable and audit trails are preserved.

### Environment Isolation
All secrets (database credentials, JWT secret key) are managed via `python-decouple` and never committed to source control. Settings are split across `base`, `development`, `production`, and `test` modules.

### CORS
`django-cors-headers` is configured with explicit allowed origins. Only known frontend origins can make cross-origin requests.

---

## Deployment

The API is deployed on **Railway** and publicly accessible:

| | URL |
|---|---|
| **Base URL** | `https://financedashboardbackend.up.railway.app` |
| **Swagger Docs** | `https://financedashboardbackend.up.railway.app/api/docs/` |
| **Health Check** | `https://financedashboardbackend.up.railway.app/api/health/` |

### Deployment Stack
- **WSGI Server:** Gunicorn
- **Database:** PostgreSQL (Railway managed)
- **Static Files:** Whitenoise (served directly from Gunicorn)
- **Configuration:** Environment variables via Railway dashboard
- **Python Version:** 3.12

### To redeploy
Push to the `main` branch. Railway auto-deploys on every push.

---

## Testing
```bash
# Run all tests with coverage
pytest

# Run without coverage (faster)
pytest --no-cov -q

# Run specific app
pytest apps/users/
pytest apps/finance/
pytest apps/dashboard/
```

**52 tests** covering all endpoints, role-based access scenarios, filtering, pagination, search, and soft delete behavior.

---

## Assumptions & Tradeoffs

**Roles are flat** — Three levels (Viewer, Analyst, Admin) cover the assignment requirements cleanly without needing a polymorphic permission table. A `permissions` join table would add flexibility but unnecessary complexity at this scope.

**Categories are an enum** — Keeps data consistent and filterable without a separate `Category` model. Trivial to migrate to a relational model if user-defined categories are needed later.

**Soft deletes** — Transactions are flagged via `is_deleted` rather than hard-deleted. A custom manager hides them from all default queries. Data is recoverable and audit trails are preserved. A separate admin-only restore endpoint could be added trivially.

**In-memory rate limit cache** — `django-ratelimit` uses Django's local memory cache. In a multi-instance production setup this would be backed by Redis to share rate limit state across workers.

**No background tasks** — Dashboard aggregations run synchronously. For very large datasets, these would move to Celery tasks with Redis caching. The service layer pattern makes this migration straightforward — services are already decoupled from HTTP.

**CORS origins are configurable** — Allowed origins are driven by the `CORS_ALLOWED_ORIGINS` environment variable, making it trivial to add new frontend origins without code changes.
