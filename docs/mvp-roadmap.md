# 🎯 FreelanceOS - MVP Roadmap

> **Cíl:** Pracovní OS pro freelancery – time tracking s commit-based workflow  
> **Stack:** Django + DRF + HTML/JS (Django templates) → React (verze 2)  
> **Filosofie:** Jednoduché, funkční, rozšiřitelné

---

## 📐 ARCHITEKTURA

### Backend (Django + DRF)
```
backend/
├── core/               # Hlavní aplikace
│   ├── models.py      # Client, Project, TimeEntry, Activity
│   ├── serializers.py # DRF serializers
│   ├── views.py       # ViewSets a API views
│   ├── urls.py        # API routing
│   └── admin.py       # Django admin interface
├── backend/
│   ├── settings.py    # Konfigurace (DB, CORS, JWT)
│   └── urls.py        # Root URLs
└── manage.py
```

### Frontend (React + TypeScript)
```
frontend/src/
├── components/
│   ├── layout/        # Layout, Sidebar, Header
│   ├── clients/       # Client komponenty
│   ├── projects/      # Project komponenty
│   ├── time-tracking/ # Timer & time entries
│   └── ui/            # shadcn/ui komponenty
├── pages/             # Dashboard, Clients, Projects, etc.
├── hooks/             # Custom React hooks (useClients, useProjects)
├── lib/
│   ├── api.ts         # Axios instance + interceptory
│   └── store.ts       # Zustand stores (auth, timer)
└── types/             # TypeScript interfaces
```

### Datový model (aktuální)
```
User (custom, email-based)
 └── 1:1 UserProfile (timezone, locale)

Workspace ──< WorkspaceMembership (owner/admin/member/viewer)

Client (1) ──────< (N) Project (1) ──────< (N) WorkCommit
                         └── Status: draft → active → paused → pending_payment → completed → archived → cancelled
```

---

## 📅 DENNÍ PLÁN

### **DEN 1 - Backend Foundation** ✅ HOTOVO
**Cíl:** Funkční Django API s databází a admin rozhraním

**Aktivity:**
- [x] Setup: Python venv, Django, DRF, PostgreSQL
- [x] Vytvoř databázové modely (Client, Project, WorkCommit)
- [x] Migrations a databáze
- [x] Django admin: registrace modelů, custom display
- [x] Seed data: testovací klienti a projekty (management command)
- [x] Test: Admin interface funguje, data jsou v DB

**Output:** Funkční Django admin s testovacími daty ✅

---

### **DEN 2 - API Layer** ✅ HOTOVO
**Cíl:** REST API endpointy pro všechny entity

**Aktivity:**
- [x] Vytvoř serializers pro všechny modely (List/Detail/CreateUpdate pattern)
- [x] ViewSets: CRUD operace (Client, Project, WorkCommit)
- [x] URL routing: `/api/v1/clients/`, `/api/v1/projects/`, etc.
- [x] Filtry: status, datum, klient
- [x] Custom actions: start/stop timer, commit workflow
- [x] Test: Všechny endpointy fungují (50+ endpoints)

**Output:** Kompletní REST API s API versioning (/api/v1/) ✅

---

### **DEN 3 - Auth & Dashboard API** ✅ HOTOVO
**Cíl:** Autentizace a dashboard statistiky

**Aktivity:**
- [x] JWT autentizace (SimpleJWT) s token refresh & blacklist
- [x] Auth endpointy: register, login, logout, me, change-password, token/refresh
- [x] Permissions: IsAuthenticated na všech endpoints
- [x] Dashboard API: `/api/v1/dashboard/stats/` s range parametrem
  - Active projects count
  - Earnings this month
  - Hours this week/month
  - Overdue projects
  - Pipeline value
- [x] Test: Login funguje, JWT token v headers, 260 testů

**Output:** Secured API s login a dashboard stats ✅

---

### **DEN 4 - Frontend Setup & Auth** ✅ HOTOVO (Django Templates v1)
**Cíl:** Frontend s přihlášením

**Aktivity (Django Templates v1 místo React):**
- [x] Base layout template (dark theme)
- [x] Login page (Django template + fetch API)
- [x] Register page
- [x] Auth store (localStorage JWT tokens)
- [x] Protected routes (redirect na /accounts/login/)
- [x] API client: fetch API s JWT interceptory
- [x] Test: Přihlášení funguje, redirect na dashboard

**Poznámka:** React + TypeScript je plánované pro v2

**Output:** Fungující login s Django templates ✅

---

### **DEN 5 - Dashboard & Layout** ✅ HOTOVO
**Cíl:** Hlavní layout a dashboard se statistikami

**Aktivity:**
- [x] Layout komponent: Base template + sidebar + header
- [x] Sidebar navigace: Dashboard, Clients, Projects, Time Tracking
- [x] Dashboard page:
  - Stats cards (projekty, výdělek, hodiny)
  - Alert pro overdue projekty
- [x] Dashboard API: fetch stats z /api/v1/dashboard/stats/
- [x] Test: Dashboard zobrazuje správná čísla z API

**Output:** Funkční dashboard s real-time daty ✅

---

### **DEN 6 - Clients & Projects** ✅ HOTOVO
**Cíl:** CRUD pro klienty a projekty + Service Layer + Workspaces

**Aktivity:**
- [x] **Clients:**
  - List API s paginací, search, ordering
  - Create/Update/Delete s validací
  - Client detail + stats endpoint
  - Client projects endpoint
  - Service layer (ClientService)
- [x] **Projects:**
  - List API s filtrováním (status, client, overdue)
  - Create/Update/Delete s validací
  - Status badges (7 statusů)
  - Overdue detection (is_overdue method)
  - Service layer (ProjectService)
- [x] **Multi-tenant Workspaces:**
  - Workspace + WorkspaceMembership modely
  - WorkspaceMiddleware (header/query param)
  - Workspace permissions (owner/admin/member/viewer)
  - All resources scoped to user + workspace
- [x] Test: 88 testů pro clients + projects (100% pass)

**Output:** Kompletní CRUD + workspace multi-tenancy ✅

---

### **DEN 7 - Time Tracking (Commit-Based)** ✅ HOTOVO
**Cíl:** Timer a správa časových záznamů s commit workflow

**Aktivity:**
- [x] WorkCommit model (start_time, end_time nullable = running)
- [x] Timer page (Django template)
- [x] Start timer API endpoint
- [x] Stop/Commit timer API endpoints
- [x] Running timer detection (is_running property)
- [x] Filter by project, date
- [x] Duration calculation (duration_seconds, duration_hours)
- [x] One active timer per user enforced
- [x] Test: Start → commit → stop workflow funguje

**Output:** Funkční commit-based time tracking ✅

---

### **DEN 8 - Testing & Security Audit** ✅ HOTOVO
**Cíl:** Kompletní test coverage + security audit

**Aktivity:**
- [x] 260 testů (100% pass rate)
- [x] 92.74% code coverage
- [x] Unit testy: modely, serializers
- [x] Integration testy: API endpoints
- [x] Edge case testy: unicode, SQL injection, boundary values
- [x] Factory Boy: UserFactory, ClientFactory, ProjectFactory
- [x] Pytest fixtures: conftest.py (global + per-app)
- [x] Security audit: EXCELLENT
- [x] Rate limiting configured
- [x] Soft delete support (BaseModel, SoftDeleteModel)

**Output:** Production-ready backend s kompletním testováním ✅

---

### **DEN 9 - Polish & Deploy** ⏳ TODO
**Cíl:** UX improvements a produkční deployment

**Aktivity:**
- [x] **Backend:**
  - Production settings (config/settings/production.py)
  - Split settings (base/dev/prod/testing)
  - Environment variables (python-decouple)
- [x] **Documentation:**
  - README kompletní
  - API docs
  - Architecture docs
  - Testing guides
- [ ] **Deploy:**
  - Backend: Railway/Render
  - PostgreSQL: Railway/Supabase
  - Environment variables v produkci
  - CORS config pro production
  - Gunicorn setup
  - Static files (collectstatic)
- [ ] **Frontend v1 Polish:**
  - Clients CRUD UI (templates)
  - Projects CRUD UI (templates)
  - Timer advanced UI

**Output:** Aplikace live v produkci

---

## 🔑 CORE FEATURES (MVP)

### ✅ Musí fungovat
- [x] Přihlášení (register, login, logout, change password)
- [x] CRUD: Clients, Projects (kompletní API)
- [x] Time tracking: start/stop timer, commit workflow
- [x] Dashboard: stats + overdue alerts
- [x] Základní filtry a search
- [x] Multi-tenant workspaces
- [x] Security audit (EXCELLENT)
- [x] 260 testů, 92.74% coverage

### ⏳ Nice to have (post-MVP)
- Faktury (PDF generování)
- Poptávky/Leads (kanban board)
- Grafy (earnings over time)
- Export dat (CSV)
- Dark mode
- Keyboard shortcuts

---

## 🛠️ TECH STACK & DŮVODY

### Backend: Django + DRF
**Proč:**
- Django admin = instant UI pro testování
- DRF browsable API = built-in dokumentace
- Méně boilerplate než NestJS
- Python = rychlý development

### Frontend: React + TypeScript
**Proč:**
- TypeScript = type safety
- React = známý ekosystém
- Vite = rychlý build
- shadcn/ui = hezké komponenty out-of-box

### Databáze: PostgreSQL
**Proč:**
- JSONField support (pro tags, checklist)
- Production-ready
- Free tier na Railway/Supabase

### State management
- **React Query:** server state (data fetching, cache)
- **Zustand:** client state (auth, timer)
- **React Hook Form:** form state

---

## 📊 SUCCESS METRICS

**Aktuální stav (Den 8 hotovo):**
- ✅ Login + dashboard funguje
- ✅ Můžeš přidat klienta → projekt → trackovat čas
- ✅ Vidíš kolik hodin/peněz na čem děláš
- ✅ Overdue projekty detekce
- ✅ 260 testů, 92.74% coverage
- ✅ Security audit EXCELLENT
- ⏳ Produkční deployment (Den 9)

**První týden používání:**
- Trackuješ čas na všech projektech
- Máš přehled o finančních příjmech
- Identifikuješ co chybí → prioritizuješ v2

---

## 💡 TIPY PRO RYCHLÝ DEVELOPMENT

### Django
- Používej **Django admin** pro testování modelů (nelog se do Postmanu)
- **DRF browsable API** ti ukáže všechny endpointy
- **Signals** pro auto-calculations (post_save hook)

### React
- **shadcn/ui** = copy-paste komponenty (tlačítka, modaly)
- **React Query** = automatický cache + refetch
- **Zustand** = jednodušší než Redux

### Debugging
- Backend: Django Debug Toolbar
- Frontend: React DevTools + Persist checkbox
- API: DRF browsable API (localhost:8000/api/)

### Deploy
- Railway = easiest backend deploy (auto HTTPS, env vars)
- Vercel = easiest frontend deploy (auto preview)
- Oba mají free tier

---

## 🚀 QUICK START

**Dnes (Den 1):**
```
1. Python venv + Django install
2. PostgreSQL databáze (Docker nebo native)
3. Definice modelů (Client, Project, TimeEntry, Activity)
4. Migrations
5. Django admin + seed data
6. Test: Admin interface funguje
```

**Zítra (Den 2):**
```
1. DRF serializers
2. ViewSets (CRUD API)
3. URL routing
4. Test: Postman - všechny endpointy OK
```

**Po 9 dnech:**
```
🎉 Aplikace v produkci + trackuješ své projekty
```

---

## 🎯 ARCHITEKTURA ROZHODNUTÍ

### Proč single-user v MVP?
- Žádná složitá autorizace (row-level permissions)
- Rychlejší development
- Tvoje data = tvoje projekty
- Multi-tenant přidáš později

### Proč ne Leads v MVP?
- Client + Project stačí na začátek
- Přidáš až když budeš mít workflow
- MVP = prove value fast

### Proč ne Invoices v MVP?
- PDF generování = extra complexity
- Tracked hours + price vidíš i bez faktury
- Export do excelu stačí na začátek

### Proč Timer v MVP?
- Core value proposition
- Vidíš kolik času konzumuješ
- Data-driven decisions o projektech

---

## 📋 CHECKLIST PŘED DEPLOYEM

**Backend:**
- [x] SECRET_KEY v .env (ne hardcoded) – python-decouple
- [x] ALLOWED_HOSTS nastaven (z env)
- [x] Settings split (base/development/production/testing)
- [ ] DEBUG=False v produkci
- [ ] CORS_ALLOWED_ORIGINS = production URL
- [ ] Database backups enabled
- [ ] Gunicorn installed
- [ ] Static files (collectstatic)

**Frontend:**
- [x] Django templates fungují (v1)
- [ ] React + TypeScript (v2 – plánované)

**Testing:**
- [x] Login funguje (36 testů)
- [x] CRUD operace fungují (88 testů clients + projects)
- [x] Timer starts & stops (WorkCommit API)
- [x] Dashboard stats correct
- [x] 260/260 testů passing (100%)
- [x] 92.74% code coverage

---

# ✨ STAV: Den 1-8 HOTOVO!

**Zbývá:** Den 9 – Produkční deployment + frontend polish

**Backend je production-ready:** 260 testů, 92.74% coverage, security audit EXCELLENT ✅
