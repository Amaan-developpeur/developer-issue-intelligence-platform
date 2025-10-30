# Developer Issue Intelligence Platform (DIIP)

> **Flagship Django Backend System**  
> Full-cycle issue aggregation, analysis, and insight delivery system for developer productivity and team intelligence.  
> **Goal:** Demonstrate employability-level backend mastery — authentication, APIs, background tasks, error handling, logging, analytics, integration, and scalability.

---

## Problem Understanding

Modern software teams rely on multiple tools — GitHub, Jira, Slack, Stack Overflow, etc. — to track and resolve issues.  
These tools generate **fragmented data** and create major inefficiencies:

- Bug reports scattered across repositories and projects  
- No unified dashboard for issue trends or bottlenecks  
- Time wasted on duplicate or low-priority triage  
- No proactive alerts for spikes or degradation  

---

## Vision

To build a **Developer Issue Intelligence Platform (DIIP)** — an intelligent backend that unifies developer issue data, normalizes it, analyzes trends, and surfaces actionable insights.

### Current Phase (v1)
> Focused on backend fundamentals — authentication, API design, observability, and Celery-based background processing.

### Future Phase (v2+)
> Introduce ML-based prediction for duplicate issues, bottleneck identification, and resolution prioritization.

---

## System Goals

| Goal | Description |
|------|--------------|
| ✅ Unified Data | Centralize issues from GitHub, Jira, and other APIs |
| ✅ Developer-first Design | Secure registration, JWT auth, and multi-project ownership |
| ✅ Reliability | Graceful handling of API failures and rate limits |
| ✅ Observability | Logs, metrics, and admin dashboards |
| ✅ Scalability | Celery + Redis-based async tasks |
| ✅ Insightful Analytics | Real-time and aggregated issue metrics |

---

## System Overview

### Core Functional Modules
- **Authentication & User Management** — JWT auth, registration, and roles  
- **Project & Integration Management** — Link GitHub/Jira securely  
- **Data Ingestion & Synchronization** — Periodic background jobs via Celery  
- **Analytics Engine** — Compute summaries and spikes  
- **Error Logging & Monitoring** — Structured logs, retries, and health checks  
- **Admin Console** — Health status, degraded integrations  

---

## Low-Level Architecture

### 5.1 Actors
- **Developer/User** — Registers, links projects, views analytics  
- **Admin** — Monitors system, manages degraded integrations  
- **External APIs** — GitHub, Jira, StackOverflow  
- **System Components** — Django, Celery, Redis, PostgreSQL  

### 5.2 Components
| Component | Description |
|------------|-------------|
| Django + DRF | Core REST API |
| Celery + Redis | Background jobs |
| PostgreSQL | Database |
| Redis | Message broker + cache |
| Sentry | Observability |
| Gunicorn / Nginx | Deployment-ready stack |

---

## Data Flow (Step-by-Step)

1. **User Registration** → `/api/auth/register/`  
   Creates user and issues JWT on login  

2. **Integration Setup** → `/api/projects/{id}/integrations/github/connect/`  
   Token stored securely (Fernet encryption)  

3. **Issue Sync (Celery Task)** → `sync_project_issues(project_id)`  
   Fetch → Normalize → Store → Log  

4. **Analytics Aggregation** → `aggregate_analytics(project_id)`  
   Compute totals, averages, and spikes  

5. **Error Handling** → Retries, exponential backoff, mark as degraded  

6. **Visualization** → `/api/projects/{id}/analytics/summary/`  

---

## Database Schema (Simplified)

| Table | Fields |
|--------|---------|
| **User** | id, email, password_hash, is_active, created_at |
| **Project** | id, owner_id, name, repo_identifier, last_synced_at |
| **Integration** | id, project_id, provider, token_encrypted, status |
| **Issue** | id, project_id, title, body, source_issue_id, status |
| **ApiLog** | id, integration_id, endpoint, status_code, response_time_ms, success |
| **AnalyticsSummary** | id, project_id, total_issues, avg_resolution_time, spike_detected |

---

## API Endpoints

| Category | Endpoint | Method | Description |
|-----------|-----------|--------|--------------|
| Auth | `/api/auth/register/` | POST | User registration |
| Auth | `/api/auth/login/` | POST | Get JWT token |
| Auth | `/api/auth/refresh/` | POST | Refresh JWT |
| Projects | `/api/projects/` | GET/POST | Manage projects |
| Integrations | `/api/projects/{id}/integrations/github/connect/` | POST | Connect GitHub |
| Issues | `/api/projects/{id}/issues/` | GET | List issues |
| Analytics | `/api/projects/{id}/analytics/summary/` | GET | Project analytics |
| Admin | `/api/admin/health/` | GET | Health status |
| Admin | `/tasks/dashboard/` | GET | Admin-only Celery dashboard |

---

## Background Tasks (Celery)

- `sync_project_issues` → Fetch and store issues  
- `process_issue` → Normalize and enrich  
- `aggregate_analytics` → Compute summaries  
- `notify_spike` → Send alerts  
- `retry_failed_api` → Retry failed API calls  

> All tasks are idempotent, logged, and fault-tolerant.

---

## Security & Reliability

- Passwords hashed (PBKDF2 / Argon2)  
- Tokens encrypted using Fernet  
- JWT-based access and refresh tokens  
- Role-based permissions (admin, developer)  
- Rate-limit aware API calls  
- CSRF and CORS protection configured  

---

## Observability

- Structured logging (user_id, project_id, integration_id)  
- **Sentry** integration for exception tracking  
- `/api/admin/health/` for system status (DB, Redis, Celery)  
- Alerts via email or Slack webhook for degraded systems  

---

## Deployment

```bash
# PostgreSQL + Redis installation
sudo apt install postgresql redis-server

# Environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker
celery -A diip worker -l info --pool=solo

# (Optional) Celery beat for periodic jobs
celery -A diip beat -l info


```
## Implementation Roadmap & Progress

###  Implementation Roadmap

| Milestone | Deliverable                        |
| --------- | ---------------------------------- |
| M1        | Project setup + PostgreSQL + Redis |
| M2        | User registration + JWT auth       |
| M3        | Project & Integration models       |
| M4        | GitHub sync (manual token)         |
| M5        | Celery background jobs             |
| M6        | Analytics module                   |
| M7        | Error handling + logging           |
| M8        | Admin dashboard + health checks    |
| M9        | Deployment configuration           |
| M10       | Integrate Jira/StackOverflow       |
| M11       | Add ML-based duplicate detection   |

---

### Current Progress (Phase-1)

✅ Django project scaffolding complete  
✅ JWT authentication implemented  
✅ Role-based access (`IsAdminOrReadOnly`) added  
✅ Celery + Redis operational for background tasks  
✅ Periodic cleanup via Celery Beat configured  
✅ Structured reliability layer (auto-retry + logging) in progress  
🛡️ Security & Governance module initiated — endpoint hardening, audit controls  
🔜 Next: GitHub + Jira integration and issue ingestion pipeline  

---

### Local Testing Example

```bash
# Get JWT token
POST http://127.0.0.1:8000/api/token/
{
  "username": "admin",
  "password": "password"
}

# Test admin-only endpoint
GET http://127.0.0.1:8000/tasks/dashboard/
Authorization: Bearer <access_token>
```
## Tech Stack Overview

| Category   | Technology                     |
| ---------- | ------------------------------ |
| Language   | Python 3.13                    |
| Framework  | Django + Django REST Framework |
| Async      | Celery                         |
| Broker     | Redis                          |
| Auth       | SimpleJWT                      |
| DB         | SQLite / PostgreSQL            |
| Testing    | Thunder Client                 |
| Deployment | Gunicorn + Nginx (optional)    |

---



