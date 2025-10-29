# Developer Issue Intelligence Platform (DIIP) — Backend Progress

This repository documents the backend foundation of **DIIP**, a Django-based system that powers secure developer analytics, observability, and task intelligence services.

---

## Current Milestone: Authentication + Access Control Layer

### Features Implemented
- **JWT Authentication** — via `SimpleJWT` for secure token-based access.
- **Role-Based Access Control (RBAC)** — custom roles (`admin`, `developer`, `analyst`, `viewer`).
- **Protected Endpoints**
  - `/tasks/dashboard/` — accessible only to admins.
- **Custom DRF Permission Class**
  - `IsAdminOrReadOnly` restricts access by `is_staff` or `user.role`.
- **Superuser + Normal User Testing**
  - Admin access returns `200 OK`
  - Developer/non-admin access returns `403 Forbidden`
  - Unauthenticated requests return `401 Unauthorized`

---

## Architecture Overview
| Layer | Technology | Purpose |
|--------|-------------|----------|
| Framework | Django 5.x + Django REST Framework | Core backend APIs |
| Auth | JWT (via SimpleJWT) | Token-based authentication |
| Access Control | Custom DRF Permissions + Roles | Role-scoped authorization |
| Observability | `/tasks/dashboard/` endpoint | Metrics and administrative insights |
| Users | Default Django `User` model | Extended with `role` field |

---

## Implementation Summary

### 1. JWT Authentication Setup
- Added token issuance endpoint at `/api/token/`.
- Implemented access and refresh token exchange flow.

### 2. Protected Task Dashboard Endpoint
- `/tasks/dashboard/` route restricted to authenticated users.
- Custom `IsAdminOrReadOnly` permission applied.

### 3. Role Management
- Added dynamic `role` field to `User` model using `User.add_to_class`.
- Created migration and assigned roles through Django shell.

### 4. Verification
| Test Case | Expected | Result |
|------------|-----------|--------|
| No Token | `401 Unauthorized` | ✅ |
| Normal User | `403 Forbidden` | ✅ |
| Admin User | `200 OK` | ✅ |

---

## Tech Stack
- **Python 3.13**
- **Django 5.x**
- **Django REST Framework**
- **SimpleJWT**
- **PostgreySQL**
- **Thunder Client / Postman** for API testing

---

## Next Steps
Planned implementation phases:
1. **Audit Trail Middleware** — immutable access logs for sensitive endpoints.
2. **API Key Scopes** — scoped machine access.
3. **Rate Limiting** — per-user throttling and endpoint hardening.
4. **Celery Integration** — background job scheduling for session cleanup.

---



---


