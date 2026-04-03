# Zorvyn Finance Backend API

A secure, performance-optimized REST API built with Django and Django REST Framework, designed to handle financial transaction tracking, automated role-based access control (RBAC), and aggregated dashboard analytics.


---

## 1. Architecture & Design Decisions

### Modular Domain-Driven Apps
The backend is aggressively decoupled into isolated domain spaces (`users`, `finance`, `dashboard`). This vertical slicing strictly bounds contexts, ensuring that user authentication logic does not bleed into financial transaction handling. 

### Service-Layer Pattern
Business logic for complex dashboard metrics is abstracted away from HTTP views and placed in pure Python functions (`apps/dashboard/services.py`).
- **Why:** Keeps controllers ("views") incredibly thin and ensures that business logic can be independently unit-tested or called from background tasks without mocking HTTP requests.

### Global Exception Handling
A custom exception handler (`core/exceptions.py`) intercepts DRF failures before they are rendered.
- **Why:** Ensures the API *always* returns a standardized `{"success": False, "error": {...}}` contract to the frontend, preventing edge-case 500 HTML dumps from breaking client parsers.

---

## 2. Technology Stack & Justifications

* **Django 6.0 & DRF:** Chosen for its extremely reliable ORM, out-of-the-box SQL injection protection, and speed of iterating on relational models.
* **PostgreSQL:** Essential for robust relational schema tracking, and critical for performing the heavy, timezone-aware date aggregations required by the dashboard.
* **Pytest:** Chosen over standard `unittest` for its superior fixture management, readable error outputs, and expressive test creation.
* **JWT (Simple JWT):** Provides stateless, secure authentication required for separated microservice/frontend architectures, with automatic refresh rotation.

---

## 3. API Design Standards

* **RESTful Principles:** Paths use nouns (`/api/transactions`), utilizing standard HTTP verbs (`GET`, `POST`, `PATCH`, `DELETE`) to denote intent. 
* **Strict Validation Layers:** All field-level validations (checking against choices, > 0 amounts) are enforced strictly inside Serializers. The views merely invoke `.is_valid(raise_exception=True)`.
* **Automated Swagger Documentation:** Integrated `drf-spectacular` alongside views leveraging `@extend_schema`. This guarantees our OpenAPI specification never drifts out of sync with our code.

---

## 4. Performance & Database Optimizations

### Query Defusing (Solving N+1)
Transactions explicitly use `.select_related('created_by')` at the query execution level, ensuring that serializing user data alongside 100 transactions results in **1 SQL query** instead of **101**.

### Pushing Computation to PostgreSQL
Instead of iterating through thousands of Python objects in memory, dashboard statistics (`get_monthly_trends`, `get_category_breakdown`) utilize `TruncMonth`, `Sum`, and `Count`. PostgreSQL handles the aggregation massively faster than the application layer ever could.

---

## 5. Security & Risk Management

### Multi-tiered RBAC Permissions
Role-Based Access Control is enforced system-wide using custom DRF `BasePermission` classes:
- `IsAdmin`: Write, edit, delete access.
- `IsAnalystOrAbove`: Read access to datasets and aggregation analytics.
- `IsAnyAuthenticatedUser`: Minimal access, blocked from underlying datasets.

### Defense in Depth
- **Rate Limiting:** Data-mutating endpoints (e.g., `POST` transaction creation) are throttled via `django-ratelimit` to mitigate spam, abuse, and brute-force insertion.
- **Environment Separation:** Secret keys and Database URIs are rigorously stripped from source code via `python-decouple`.

---

## 6. Trade-offs & Compromises

Engineering is inherently about balancing time, scope, and perfection. The following comprises were made:

1. **Pagination Deferred:** Currently, `TransactionListView` generates its query and serializes the result broadly. While acceptable for a prototype, this lacks a pagination cursor. This is recognized as an unscalable approach for production datasets.
2. **Database-only Containerization:** The `docker-compose.yml` provides a deterministic local database, but stops short of containerizing the Django service itself. Full push-button deployment configuration was deferred in favor of prioritizing core business logic execution.
3. **Implicit CORS:** `django-cors-headers` was intentionally omitted as the deployment URL origins for the consuming frontends were unknown. This must be configured prior to live client consumption.

---