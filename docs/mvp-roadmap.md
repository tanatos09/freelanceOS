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

### Datový model
```
Client (1) ──────< (N) Project (1) ──────< (N) TimeEntry
                         ├──────< (N) Activity
                         └── Status: new → in_progress → done → paid
```

---

## 📅 DENNÍ PLÁN

### **DEN 1 - Backend Foundation**
**Cíl:** Funkční Django API s databází a admin rozhraním

**Aktivity:**
- [ ] Setup: Python venv, Django, DRF, PostgreSQL
- [ ] Vytvoř databázové modely (Client, Project, TimeEntry, Activity)
- [ ] Migrations a databáze
- [ ] Django admin: registrace modelů, custom display
- [ ] Seed data: testovací klienti a projekty
- [ ] Test: Admin interface funguje, data jsou v DB

**Output:** Funkční Django admin s testovacími daty

---

### **DEN 2 - API Layer**
**Cíl:** REST API endpointy pro všechny entity

**Aktivity:**
- [ ] Vytvoř serializers pro všechny modely
- [ ] ViewSets: CRUD operace (Client, Project, TimeEntry, Activity)
- [ ] URL routing: `/api/clients/`, `/api/projects/`, etc.
- [ ] Filtry: status, datum, klient
- [ ] Custom actions: start/stop timer, konverze lead → projekt
- [ ] Test: Postman/Insomnia - všechny endpointy fungují

**Output:** Kompletní REST API (DRF browsable API na localhost:8000/api/)

---

### **DEN 3 - Auth & Dashboard API**
**Cíl:** Autentizace a dashboard statistiky

**Aktivity:**
- [ ] JWT autentizace (SimpleJWT)
- [ ] Auth endpointy: `/api/auth/login/`, `/api/auth/me/`
- [ ] Permissions: IsAuthenticated na všech endpoints
- [ ] Dashboard API: `/api/dashboard/stats/`
  - Active projects count
  - Earnings this month
  - Hours this week/month
  - Overdue projects
  - Pipeline value
- [ ] Test: Login funguje, JWT token v headers

**Output:** Secured API s login a dashboard stats

---

### **DEN 4 - Frontend Setup & Auth**
**Cíl:** React aplikace s přihlášením

**Aktivity:**
- [ ] Vytvoř Vite + React + TypeScript projekt
- [ ] Install dependencies: axios, react-router, react-query, zustand
- [ ] Setup Tailwind CSS + shadcn/ui
- [ ] Složková struktura (components, pages, hooks, lib)
- [ ] API client: axios instance s JWT interceptory
- [ ] Auth store (Zustand): login, logout, user state
- [ ] Login page: formulář + React Hook Form
- [ ] Protected routes: redirect na /login pokud není auth
- [ ] Test: Přihlášení funguje, redirect na dashboard

**Output:** Fungující login, chráněné routy

---

### **DEN 5 - Dashboard & Layout**
**Cíl:** Hlavní layout a dashboard se statistikami

**Aktivity:**
- [ ] Layout komponent: Sidebar + Header + main content
- [ ] Sidebar navigace: Dashboard, Clients, Projects, Time Tracking
- [ ] Header: logo + user menu + běžící timer indikátor
- [ ] Dashboard page:
  - Stats cards (projekty, výdělek, hodiny)
  - Alert pro overdue projekty
  - Recent activities list
- [ ] React Query setup: fetch dashboard stats
- [ ] Test: Dashboard zobrazuje správná čísla z API

**Output:** Funkční dashboard s real-time daty

---

### **DEN 6 - Clients & Projects**
**Cíl:** CRUD pro klienty a projekty

**Aktivity:**
- [ ] **Clients:**
  - List page: tabulka s klienty
  - Client form (modal): create/edit
  - Client detail: info + seznam projektů
  - Search & filter
- [ ] **Projects:**
  - List page: tabulka s projekty
  - Project form (modal): všechna pole
  - Status badges (color-coded)
  - Filter podle status, client, deadline
  - Overdue alert (červená)
- [ ] React Query: mutations (create, update, delete)
- [ ] Toast notifikace (success/error)
- [ ] Test: Vytvoření klienta → projekt → viditelné v listu

**Output:** Kompletní CRUD pro clients a projects

---

### **DEN 7 - Time Tracking**
**Cíl:** Timer a správa časových záznamů

**Aktivity:**
- [ ] Timer hook (Zustand): startTimer, stopTimer, elapsedTime
- [ ] Timer component v headeru: zobraz běžící timer
- [ ] Time Tracking page:
  - Start timer button (modal: vyber projekt + popis)
  - Time entries tabulka
  - Manual time entry form
  - Filter podle projektu, date range
- [ ] API integrace: start/stop timer endpoints
- [ ] Persistence: běžící timer přetrvá reload
- [ ] Test: Start timer → běží v headeru → stop → uloží se

**Output:** Funkční time tracking system

---

### **DEN 8 - Project Detail & Activities**
**Cíl:** Detailní view projektu s logem aktivit

**Aktivity:**
- [ ] Project detail page: tabs (Overview, Time Entries, Activity)
- [ ] Overview tab:
  - Info karty (cena, hodiny, deadline)
  - Progress bar (actual vs estimated hours)
  - Checklist/TODO list (inline edit)
- [ ] Time Entries tab: seznam časů pro daný projekt
- [ ] Activity tab:
  - Timeline layout
  - Icons podle typu (note, email, call, meeting)
  - Add activity form
- [ ] Activity API: create, list, delete
- [ ] Test: Vytvoř aktivitu → zobrazí se v timeline

**Output:** Kompletní project detail s aktivitami

---

### **DEN 9 - Polish & Deploy**
**Cíl:** UX improvements a produkční deployment

**Aktivity:**
- [ ] **UX Polish:**
  - Loading states (skeletons, spinners)
  - Empty states (friendly messages + CTA)
  - Error handling (toast pro API errors)
  - Form validace (Zod schemas)
  - Responzivita (mobile menu)
- [ ] **Backend:**
  - Production settings (DEBUG=False, ALLOWED_HOSTS)
  - Gunicorn setup
  - Static files (collectstatic)
- [ ] **Deploy:**
  - Backend: Railway/Render
  - Frontend: Vercel/Netlify
  - PostgreSQL: Railway/Supabase
  - Environment variables
  - CORS config pro production
- [ ] **Testing:**
  - Manual smoke test všech features
  - Oprav kritické bugy
- [ ] **README:** instalace, setup, API docs

**Output:** Aplikace live v produkci ✅

---

## 🔑 CORE FEATURES (MVP)

### ✅ Musí fungovat
- [ ] Přihlášení (single user)
- [ ] CRUD: Clients, Projects
- [ ] Time tracking: start/stop timer, manual entries
- [ ] Dashboard: stats + overdue alerts
- [ ] Project detail: info + activities
- [ ] Základní filtry a search

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

**Po 9 dnech máš:**
- ✅ Aplikaci v produkci (URL)
- ✅ Login + dashboard funguje
- ✅ Můžeš přidat klienta → projekt → trackovat čas
- ✅ Vidíš kolik hodin/peněz na čem děláš
- ✅ Overdue projekty jsou červeně označené

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
- [ ] DEBUG=False
- [ ] SECRET_KEY v .env (ne hardcoded)
- [ ] ALLOWED_HOSTS nastaven
- [ ] CORS_ALLOWED_ORIGINS = production URL
- [ ] Database backups enabled
- [ ] Gunicorn installed
- [ ] Static files (collectstatic)

**Frontend:**
- [ ] VITE_API_URL = production backend URL
- [ ] Error boundaries (catch React errors)
- [ ] Toast pro všechny API errors
- [ ] Loading states všude

**Testing:**
- [ ] Login funguje
- [ ] CRUD operace fungují
- [ ] Timer starts & stops
- [ ] Dashboard stats correct
- [ ] Mobile responsive

---

# ✨ TEĎ JDI KÓDOVAT!

**Začni Den 1** → Python venv → Django → Modely → Admin → Seed data

Po každém dni máš **funkční feature** → vidíš progress → motivace ⬆️
