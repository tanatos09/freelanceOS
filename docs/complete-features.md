# 📋 FreelanceOS - Seznam funkcí (Complete)

**Stav:** 95% Complete | **Poslední update:** 2026-03-19

## 🔐 Autentizace ✅ HOTOVO
- [x] User registrace
- [x] Login (JWT)
- [x] Logout (token blacklist)
- [x] Token refresh
- [x] Get current user (me endpoint)
- [x] Change password

## 👥 Clients (Klienti) ✅ HOTOVO
- [x] List clients (paginated, search, ordering)
- [x] Create client
- [x] Update client
- [x] Delete client
- [x] Get client detail
- [x] Get client projects
- [x] Search clients (name, email, company)
- [x] Filter clients
- [x] Calculate total earnings per client
- [x] Count projects per client
- [x] Client stats endpoint
- [x] Workspace scoping

## 💼 Leads (Poptávky) ⏳ POST-MVP
- [ ] List leads
- [ ] Create lead
- [ ] Update lead
- [ ] Delete lead
- [ ] Get lead detail
- [ ] Filter by status (new/contacted/deal/rejected)
- [ ] Filter by priority (low/medium/high)
- [ ] Convert lead to project
- [ ] Link lead to client
- [ ] Set expected close date
- [ ] Set probability
- [ ] Add technologies (JSONField)

## 📁 Projects (Projekty) ✅ HOTOVO
- [x] List projects
- [x] Create project
- [x] Update project
- [x] Delete project
- [x] Get project detail
- [x] Filter by status (draft/active/paused/pending_payment/completed/archived/cancelled)
- [x] Filter by client
- [x] Filter by deadline (before/after)
- [x] Search by name
- [x] Get project work commits
- [x] Calculate actual hours
- [x] Calculate progress percentage
- [x] Check if overdue
- [x] Days until deadline
- [x] Budget & hourly rate tracking
- [x] Projects stats endpoint
- [x] Workspace scoping

## ⏱️ Time Tracking (Work Commits) ✅ HOTOVO
- [x] List work commits
- [x] Start timer
- [x] Stop timer (with description - COMMIT)
- [x] Get running timer
- [x] Filter by project
- [x] Filter by date
- [x] Calculate duration (seconds & hours)
- [x] One active timer per user enforced
- [x] Commit-based workflow (core feature)

## 📝 Activities (Log) ⏳ MODEL READY
- [x] Activity model structure
- [x] Activity type field
- [ ] Activity API endpoints (full CRUD)
- [ ] Activity timeline UI

## 📊 Dashboard ✅ HOTOVO
- [x] Get stats overview
  - [x] Active projects count
  - [x] Total earnings this month
  - [x] Hours worked this week
  - [x] Hours worked this month
  - [x] Overdue projects count
- [x] Dashboard API endpoint
- [x] Range parameter (today/week/month)
- [x] Workspace scoping

## 📋 Search & Filtering ✅ HOTOVO
- [x] Client search (by name, email, company)
- [x] Project search (by name, description)
- [x] Filter projects by status
- [x] Filter projects by client
- [x] Filter by dates
- [x] Filter work commits by project
- [x] Filter work commits by date
- [x] django-filter integration

## 🏢 Workspaces (Multi-tenant) ✅ HOTOVO
- [x] Workspace model (name, slug, plan, settings)
- [x] WorkspaceMembership (owner/admin/member/viewer roles)
- [x] WorkspaceMiddleware (header/query param resolution)
- [x] Default workspace creation
- [x] Workspace API endpoints
- [x] Client workspace association
- [x] Project workspace association
- [x] Workspace permissions (IsWorkspaceMember, IsWorkspaceAdmin, IsWorkspaceOwner)

## 🧾 Invoices (Faktury) ⏳ POST-MVP
- [ ] Create invoice
- [ ] List invoices
- [ ] Update invoice
- [ ] Delete invoice
- [ ] Mark as draft/sent/paid
- [ ] Generate PDF
- [ ] Link invoice to project
- [ ] Set payment dates

## 🎨 Frontend (v1 - Django Templates) ⏳ PARTIAL
- [x] Base layout template (dark theme)
- [x] Login page
- [x] Register page
- [x] Logout functionality
- [x] Dashboard template
- [x] Clients list template
- [x] Client detail template
- [x] Projects list template
- [x] Project detail template
- [x] Timer template
- [x] Static JS - API wrapper (fetch)
- [x] Static CSS - Dark theme
- [ ] Advanced CRUD modals
- [ ] Toast notifications
- [ ] Loading states

## 🧪 Testing & QA ✅ HOTOVO
- [x] Unit tests (models) - 56 testů
- [x] Serializer tests - 48 testů
- [x] API integration tests - 92 testů
- [x] Edge case tests - 16 testů
- [x] Legacy compatibility tests - 48 testů
- [x] Test factories (Factory Boy)
- [x] Test fixtures (conftest.py)
- [x] Coverage reports (92.74%)
- [x] Pytest configuration

**Tests:** 260/260 passing ✅
**Coverage:** 92.74% overall ✅

## 🔒 Security ✅ EXCELLENT
- [x] JWT authentication with blacklist
- [x] Token refresh rotation
- [x] Password hashing (PBKDF2 SHA256)
- [x] CORS configuration
- [x] CSRF protection
- [x] Environment variables for secrets (python-decouple)
- [x] Settings split (dev/prod/testing)
- [x] User data isolation
- [x] Rate limiting (100/hr anon, 1000/hr auth)
- [x] Admin panel secured
- [x] Security audit complete (EXCELLENT)

## 🛠️ Infrastructure ✅ HOTOVO
- [x] API versioning (/api/v1/)
- [x] Service layer pattern (ClientService, ProjectService, WorkspaceService)
- [x] Custom pagination
- [x] Custom exceptions
- [x] BaseModel (UUID PK, timestamps)
- [x] SoftDeleteModel (soft delete support)
- [x] Management commands (seed, seed_test)
- [x] Django admin customization (all models)
- [x] Database indexes (optimized queries)
- [x] Database migrations (9 total)
- [x] Scripts (coverage, linting, e2e)
