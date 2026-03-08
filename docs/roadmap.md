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

## 🔜 NEXT: DEN 4-5

### **DEN 4-5 - Frontend (Django Templates)**

**Cíl:** Jednoduché HTML stránky s vanilla JS (bez React)

**Chybí:**
- [ ] Sidebar + navbar layout
- [ ] Clients list page (fetch API)
- [ ] Clients CRUD modály
- [ ] Projects list page (filtry status)
- [ ] Projects CRUD modály (create/edit)
- [ ] Project detail page (timeline + stats)
- [ ] Timer widget (header + start/stop/commit UI)
- [ ] Dashboard stats refresh
- [ ] Responzivita

**Proč Django templates v MVP?**
- Deploy: jeden server (no separate frontend app)
- Build process: žádný
- React v2: bez major refactoru backendu

---

## 📊 STATISTIKY STAVU

| Komponenta | Status | % Done |
|---|---|---|
| Backend - Models | ✅ | 100% |
| Backend - Admin | ✅ | 100% |
| Backend - API | ✅ | 100% |
| Backend - Auth | ✅ | 100% |
| Frontend - Layouts | 🔄 | 0% |
| Frontend - CRUD | 🔄 | 0% |
| Frontend - Timer UI | 🔄 | 0% |
| Deploy | ⏳ | 0% |

**MVP % Done: ~60%** (backend done, frontend starting)

---

## 🚀 DEN CELKEM

| Den | Co | Status |
|---|---|---|
| 1 | Auth (register, login, JWT) | ✅ |
| 2 | Models (Client, Project, WorkCommit) | ✅ |
| 3 | API (CRUD, dashboard, timer) | ✅ |
| 4-5 | Frontend (sidebar, CRUD, timer) | 🔄 |
| 7 | Timer UI + commit workflow | ⏳ |
| 8-9 | Polish + deploy | ⏳ |

---

## 📐 ARCHITEKTURA

### Backend
```
core/
├── models.py         ✅ Client, Project, WorkCommit
├── serializers.py    ✅ DRF serializers
├── views.py          ✅ ViewSets, dashboard stats
├── api_urls.py       ✅ REST routing
├── admin.py          ✅ Django admin
└── management/
    └── commands/
        └── seed.py   ✅ Test data

users/
├── models.py         ✅ User, UserProfile
├── serializers.py    ✅ Register, Login
├── views.py          ✅ Auth endpoints
└── urls.py           ✅ Auth routing
```

### Frontend
```
templates/
├── base.html         ✅ Layout (dark theme)
└── auth/
    ├── login.html    ✅ 
    ├── register.html ✅
    └── dashboard.html ✅ (placeholder)

core/templates/    (TBD)
├── clients.html
├── projects.html
├── project_detail.html
└── timer.html
```

---

## 💾 DATABASE MODEL

```
User (1) ──────< (N) Project
              ├──────< (N) WorkCommit
              └── Status: new/in_progress/done/paid

Client (1) ──────< (N) Project

Project properties:
- total_hours (sum commits)
- total_earnings (hours * rate)
- is_overdue (deadline < now and status != done)
- commits_count

WorkCommit properties:
- duration_seconds (end_time - start_time)
- is_running (end_time is None)
```

---

## 🎯 CORE FEATURES (MVP)

✅ **HOTOVO:**
- Registrace + Login
- Logout (token blacklist)
- CRUD: Clients, Projects
- Commit-based timer (API ready)

⏳ **ZBÝVÁ:**
- Frontend pro timer
- Project timeline v UI
- Dashboard s stats
- Overdue alerts

🚀 **DEPLOYMENT:**
- Production settings
- Railway/Render backend

---

## 🔧 DEV TOOLS

### Commands
```bash
# Seed data
python manage.py seed

# Admin
python manage.py createsuperuser

# Dev server
python manage.py runserver 8000

# API browser
http://localhost:8000/api/

# Admin
http://localhost:8000/admin/
```

### Test Account
```
Email: frank@test.cz
Password: testpass123
```

### API Test (PowerShell)
```powershell
# Login
$body = @{email="frank@test.cz";password="testpass123"} | ConvertTo-Json
$resp = Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/auth/login/" `
  -ContentType "application/json" -Body $body -UseBasicParsing
$token = ($resp.Content | ConvertFrom-Json).access

# Get projects
$header = @{"Authorization"="Bearer $token"}
Invoke-WebRequest -Method Get -Uri "http://localhost:8000/api/projects/" `
  -Headers $header -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## ✨ NOTES

- **Commit-based timer** je core feature - přirozen workflow
- **Single-user MVP** - bez multi-tenant complexity
- **Django templates** - no build process, fast iteration
- **React v2** - pode easy migrate (API je ready)
- **Overdue detection** - deadline < today and status != done
- **Auto stats** - duration_seconds se počítá v PROPERTY

---

## 🎉 SUCCESS CRITERIA (DEN 9)

✅ App je live (Railway/Render)
✅ Můžeš se přihlásit
✅ Přidat klienta → projekt
✅ Spustit timer, dát commitů, vidět timeline
✅ Dashboard ukazuje stats (hodiny, earnings)
✅ Overdue projekty jsou barevně
✅ Export commitů do CSV

**Wow faktor:** Nemusíš nic ručně psát - timeline se vytváří ze saves commitů 🚀
