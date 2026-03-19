# 📋 FreelanceOS - Checklist funkcí (MVP)

> **Stav:** 95% COMPLETE | **Testy:** 260/260 | **Coverage:** 92.74%

## 🔐 Autentizace ✅ HOTOVO
- [x] Login
- [x] Logout
- [x] Get current user (/api/v1/auth/me/)
- [x] JWT token handling
- [x] Register endpoint
- [x] Change password
- [x] Token blacklist (logout)
- [x] Token refresh
- [x] Protected template pages (Django)

## 👥 Clients ✅ HOTOVO
- [x] List clients (paginated, search, ordering)
- [x] Create client
- [x] Update client
- [x] Delete client
- [x] View client detail
- [x] Search clients (name, email, company)
- [x] Calculate total earnings
- [x] Count projects
- [x] Client stats endpoint
- [x] Client projects endpoint
- [x] Workspace scoping

## 📁 Projects ✅ HOTOVO
- [x] List projects
- [x] Create project
- [x] Update project
- [x] Delete project
- [x] View project detail
- [x] Filter by status (draft/active/paused/pending_payment/completed/archived/cancelled)
- [x] Filter by client
- [x] Search by name
- [x] Status badges (7 statusů)
- [x] Overdue detection (is_overdue method)
- [x] Calculate actual hours
- [x] Progress calculation (progress_percent)
- [x] Days until deadline
- [x] Budget & hourly rate tracking
- [x] Projects stats endpoint

## ⏱️ Time Tracking (Work Commits) ✅ HOTOVO
- [x] Start timer
- [x] Stop timer (with commit description)
- [x] Get running timer
- [x] List work commits
- [x] Filter by project
- [x] Filter by date
- [x] Calculate duration (duration_seconds, duration_hours)
- [x] One active timer per user enforced
- [x] Commit-based workflow (core feature)

## 📊 Dashboard ✅ HOTOVO
- [x] Active projects count
- [x] Earnings this month
- [x] Hours this week
- [x] Hours this month
- [x] Overdue projects count
- [x] Range parameter (today/week/month)
- [x] Workspace scoping

## 🏢 Workspaces ✅ HOTOVO
- [x] Workspace model (name, slug, plan, settings)
- [x] Workspace membership (owner/admin/member/viewer)
- [x] WorkspaceMiddleware (header/query param resolution)
- [x] Default workspace creation
- [x] Workspace API endpoints
- [x] Client workspace association
- [x] Project workspace association
- [x] Workspace permissions

## 🎨 Frontend - Pages (Django Templates v1)
- [x] Login page
- [x] Register page
- [x] Dashboard page
- [x] Clients list page
- [x] Client detail page
- [x] Projects list page
- [x] Project detail page
- [x] Timer page

## 🛠️ Backend - Django ✅ HOTOVO
- [x] User model (custom, email-based)
- [x] UserProfile (timezone, locale, auto-created via signal)
- [x] Client model (with workspace FK, unique email per user)
- [x] Project model (7 statusů, overdue, progress)
- [x] WorkCommit model (commit-based timer)
- [x] Workspace & WorkspaceMembership models
- [x] BaseModel (UUID PK, timestamps)
- [x] SoftDeleteModel (soft delete support)
- [x] Admin interface (all models registered)
- [x] Seed data command (python manage.py seed)
- [x] Database migrations (9 total)
- [x] CORS configuration
- [x] JWT configuration
- [x] Environment variables (python-decouple)
- [x] Split settings (base/dev/prod/testing)

## 🛠️ Backend - API ✅ HOTOVO
- [x] Auth endpoints (register, login, logout, me, change-password, token/refresh)
- [x] Clients CRUD + stats + projects
- [x] Projects CRUD + stats
- [x] WorkCommits (start, stop, commit, running, list)
- [x] Dashboard stats endpoint (with range param)
- [x] Workspaces CRUD
- [x] Filters & search (django-filter)
- [x] Pagination
- [x] Rate limiting
- [x] API versioning (/api/v1/)
- [x] Service layer (ClientService, ProjectService, WorkspaceService)

## 🧪 Testing ✅ HOTOVO
- [x] Unit tests (models) - 56 testů
- [x] Serializer tests - 48 testů
- [x] API integration tests - 92 testů
- [x] Edge case tests - 16 testů
- [x] Legacy compatibility tests - 48 testů
- [x] Factory Boy (UserFactory, ClientFactory, ProjectFactory)
- [x] Pytest fixtures (conftest.py global + per-app)
- [x] Coverage reports (92.74%)
- [x] pytest-xdist parallel support

## 🔒 Security ✅ HOTOVO
- [x] JWT authentication with blacklist
- [x] Password hashing (PBKDF2 SHA256)
- [x] CORS configuration
- [x] CSRF protection
- [x] Rate limiting
- [x] User data isolation (all queries scoped to user)
- [x] Environment variables for secrets
- [x] Security audit completed (EXCELLENT)

## 🚀 Deployment ⏳ TODO
- [ ] Backend to Railway/Render
- [ ] PostgreSQL database (production)
- [ ] Environment variables (production)
- [x] Production settings (config/settings/production.py)
- [ ] Gunicorn setup
- [ ] Static files (collectstatic)
- [ ] HTTPS + domain

## ⏳ Post-MVP (v2.0)
- Leads/Poptávky (kanban board)
- Faktury (PDF generování)
- Grafy (charts - earnings over time)
- Export dat (CSV)
- React + TypeScript frontend
- Dark mode toggle
- Keyboard shortcuts
- Multi-user teams
