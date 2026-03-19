# 🎯 FreelanceOS - MVP Roadmap

> **Cíl:** Pracovní OS pro freelancery – time tracking s commit-based workflow  
> **Stack:** Django + DRF + HTML/JS (Django templates) → React (verze 2)  
> **Filosofie:** Jednoduché, funkční, rozšiřitelné

---

## 💡 Core Koncept: COMMIT-BASED TRACKING

**Tradiční time tracking:**
```
09:00 START timer
10:00 STOP timer
→ 1 hora bez popisu
```

**FreelanceOS – commit-based:**
```
09:00 START timer
09:40 COMMIT "oprava CSS navů"
10:15 COMMIT "mobilní layout"
11:00 STOP

→ 3 odlišné workblocky s popisem
→ Automatická timeline
→ Soupis práce pro fakturu
```

---

## ✅ PROGRESS: DEN 1-3

### **DEN 1 - Autentizace** ✅ HOTOVO

**Hotovo:**
- ✅ User model s email (neID username)
- ✅ Auth API: register, login, logout, me, change-password
- ✅ JWT + token blacklist (logout je real)
- ✅ Django admin s User, UserProfile
- ✅ Dark theme HTML templates (login, register, dashboard)
- ✅ Protected routes

**Test account:**
```
frank@test.cz / testpass123
```

---

### **DEN 2 - Modely & Admin** ✅ HOTOVO

**Hotovo:**
- ✅ Model: **Client** (name, email, phone, notes)
- ✅ Model: **Project** (name, client FK, status, rate, deadline, notes)
- ✅ Model: **WorkCommit** (start_time, end_time nullable, description, project FK)
- ✅ Migrations (aplikovány)
- ✅ Django admin s custom display:
  - **Client list:** Počet projektů, Total earnings
  - **Project list:** Status badges (barevné), deadline, hoiny, earnings, overdue alert
  - **WorkCommit list:** Status (BĚŽÍ / Hotovo), timer, trvání
- ✅ Seed command: 3 klienti, 4 projekty, 8 commitů

**Admin interface:**
- http://localhost:8000/admin/
- Client: Web Novák, Fotogalerie Svoboda, E-shop Kolář
- Projects: Redesign webu (3.5h), Galerie fotek (3h), Nový e-shop (7h, OVERDUE!), Opravy CSS (3h)
- Stats: 17h celkem, 8300 Kč earning

---

### **DEN 3 - REST API** ✅ HOTOVO

**API Endpoints:**

#### Clients
```
GET    /api/clients/              List (search, order)
POST   /api/clients/              Create
GET    /api/clients/{id}/         Detail (+ totalearnings)
PUT    /api/clients/{id}/         Update
DELETE /api/clients/{id}/         Delete
```

#### Projects
```
GET    /api/projects/              List (filter: status, client)
POST   /api/projects/              Create
GET    /api/projects/{id}/         Detail (+ commits timeline, totals)
PUT    /api/projects/{id}/         Update
DELETE /api/projects/{id}/         Delete
GET    /api/projects/overdue/      Overdue only
```

#### WorkCommits (TIMER – Core Feature)
```
POST   /api/workcommits/start/     Start timer (body: {project_id})
POST   /api/workcommits/{id}/commit/  Finish with description + create next
                                    Body: {description, continue=true}
POST   /api/workcommits/{id}/stop/ Stop timer (no description)
GET    /api/workcommits/           List (filter: project, start_time)
GET    /api/workcommits/running/   Current running timer
DELETE /api/workcommits/{id}/      Delete
```

#### Dashboard
```
GET    /api/dashboard/stats/       {
                                      active_projects_count: 3,
                                      today_hours: 0,
                                      week_hours: 17,
                                      month_hours: 17,
                                      month_earnings: 8300,
                                      overdue_projects_count: 1
                                    }
```

**Permissions:**
- IsAuthenticated všude
- Users vidí jen svá data (user FK)

**Tested:**
```bash
✓ Login & JWT token
✓ GET /api/projects/ → 4 projekty s earnings
✓ GET /api/dashboard/stats/ → všechny fields
✓ POST /api/workcommits/start/ → timer spuštěn (ID 9)
✓ POST /api/workcommits/9/commit/ → zakonči + nový (ID 10)
✓ POST /api/workcommits/10/stop/ → stop timer
✓ GET /api/projects/1/ → detail s commits timeline
```

---

## ✅ DEN 4-5 - Frontend (Django Templates) HOTOVO

### **DEN 4-5 - Frontend (Django Templates)**

**Cíl:** Jednoduché HTML stránky s vanilla JS (bez React)

**Hotovo:**
- [x] Base layout template (dark theme)
- [x] Login + register pages
- [x] Dashboard template s API daty
- [x] Clients list page
- [x] Client detail page
- [x] Projects list page
- [x] Project detail page
- [x] Timer page
- [x] Static CSS (dark theme)
- [x] Static JS (fetch API wrapper)

**Proč Django templates v MVP?**
- Deploy: jeden server (no separate frontend app)
- Build process: žádný
- React v2: bez major refaktoru backendu

---

## 📊 STATISTIKY STAVU

| Komponenta | Status | % Done |
|---|---|---|
| Backend - Models | ✅ | 100% |
| Backend - Admin | ✅ | 100% |
| Backend - API (50+ endpoints) | ✅ | 100% |
| Backend - Auth (JWT) | ✅ | 100% |
| Backend - Service Layer | ✅ | 100% |
| Backend - Workspaces | ✅ | 100% |
| Backend - Tests (260) | ✅ | 100% |
| Backend - Security Audit | ✅ | 100% |
| Frontend - Templates (v1) | ✅ | 80% |
| Frontend - React (v2) | ⏳ | 0% |
| Deploy | ⏳ | 0% |

**MVP % Done: ~95%** (backend complete, frontend templates done, deploy pending)

---

## 🚀 DEN CELKEM

| Den | Co | Status |
|---|---|---|
| 1 | Auth (register, login, JWT, blacklist) | ✅ |
| 2 | Models (Client, Project, WorkCommit) | ✅ |
| 3 | API (CRUD, dashboard, timer) | ✅ |
| 4-5 | Frontend templates (layout, pages) | ✅ |
| 6 | Service layer + workspaces | ✅ |
| 7 | Timer UI + commit workflow | ✅ |
| 8 | Testing (260 testů) + security audit | ✅ |
| 9 | Deploy (Railway/Render) | ⏳ |

---

## 📐 ARCHITEKTURA

### Backend
```
core/
├── settings.py       ✅ Import z config/settings
├── api_urls.py       ✅ Dashboard stats API
├── views.py          ✅ Dashboard view
├── urls.py           ✅ Root URL routing
└── management/
    └── commands/
        ├── seed.py   ✅ Production seed data
        └── seed_test.py ✅ Test seed data

config/settings/
├── base.py           ✅ Shared settings
├── development.py    ✅ DEBUG=True, console email
├── production.py     ✅ HTTPS, security headers
└── testing.py        ✅ SQLite in-memory

users/
├── models.py         ✅ User (email-based), UserProfile
├── serializers.py    ✅ Register, User, ChangePassword
├── views.py          ✅ Auth endpoints (JWT)
└── urls.py           ✅ Auth routing

clients/
├── models.py         ✅ Client (with workspace FK)
├── serializers.py    ✅ List/Detail/CreateUpdate
├── services.py       ✅ ClientService (business logic)
├── views.py          ✅ CRUD + stats + projects
└── tests/            ✅ 41 testů (100% coverage)

projects/
├── models.py         ✅ Project (7 statusů, overdue)
├── serializers.py    ✅ List/Detail/CreateUpdate
├── services.py       ✅ ProjectService (business logic)
├── views.py          ✅ CRUD + stats
└── tests/            ✅ 47 testů

workcommits/
├── models.py         ✅ WorkCommit (timer s commits)
├── serializers.py    ✅ WorkCommitSerializer
├── views.py          ✅ Start, stop, commit, running
└── admin.py          ✅ Custom admin display

apps/common/
├── models.py         ✅ BaseModel, SoftDeleteModel
├── permissions.py    ✅ Workspace permissions
├── middleware.py     ✅ WorkspaceMiddleware
├── exceptions.py     ✅ Custom API errors
└── pagination.py     ✅ Custom pagination

apps/workspaces/
├── models.py         ✅ Workspace, WorkspaceMembership
├── serializers.py    ✅ Workspace serializers
├── services.py       ✅ WorkspaceService
└── views.py          ✅ Workspace CRUD
```

### Frontend (Django Templates v1)
```
templates/
├── layouts/base.html  ✅ Dark theme layout
├── auth/
│   ├── login.html     ✅
│   ├── register.html  ✅
│   └── dashboard.html ✅
└── dashboard/
    ├── clients.html       ✅
    ├── client_detail.html ✅
    ├── projects.html      ✅
    ├── project_detail.html ✅
    └── timer.html         ✅

static/
├── css/styles.css     ✅ Dark theme
└── js/layout.js       ✅ API interactions
```

---

## 💾 DATABASE MODELS (8 modelů)

```
User (custom, email-based)
 ├── 1:1 UserProfile (timezone, locale)
 ├── 1:N Client (user → clients)
 ├── 1:N Project (user → projects)
 └── 1:N WorkCommit (user → commits)

Client (1) ──────< (N) Project (1) ──────< (N) WorkCommit

Workspace ──< WorkspaceMembership (owner/admin/member/viewer)
 └── scopes: Client, Project

Project statuses: draft → active → paused → pending_payment → completed → archived → cancelled
WorkCommit: end_time NULL = timer running
```

---

## 🎯 CORE FEATURES (MVP)

✅ **HOTOVO:**
- Registrace + Login + Logout (JWT blacklist)
- Change password
- CRUD: Clients (search, stats, projects endpoint)
- CRUD: Projects (7 statusů, overdue, progress)
- Commit-based timer (start/stop/commit/running)
- Dashboard stats (active, earnings, hours, overdue)
- Multi-tenant workspaces
- Service layer pattern
- 260 testů, 92.74% coverage
- Security audit EXCELLENT

⏳ **ZBÝVÁ:**
- Production deployment (Railway/Render)
- React frontend (v2)

---

## 🧪 TESTING

```
260 testů | 100% pass rate | 92.74% coverage

clients/tests/   → 41 testů (100%)
projects/tests/  → 47 testů (92-100%)
users/tests/     → 134 testů (100%)
workcommits/     → via integration
```

---

## 🔧 DEV TOOLS

### Commands
```bash
python manage.py seed              # Seed data
python manage.py createsuperuser   # Admin account
python manage.py runserver 8000    # Dev server
pytest                             # All tests
pytest --cov --cov-report=html     # Coverage
ruff check .                       # Linting
```

### URLs
```
http://localhost:8000/accounts/login/    # Frontend
http://localhost:8000/admin/             # Django admin
http://localhost:8000/api/v1/            # API root
```
