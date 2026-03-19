# 🎯 FreelanceOS

> Pracovní OS pro freelancery. Správa projektů, time tracking s commit-based workflow, přehled výdělků.

---

## 💡 Co to je?

**FreelanceOS** je minimalistická CRM + time tracker pro freelancery a malé týmy.

Klíčová vlastnost: **Commit-based work tracking** (místo tradičního sit-and-forget timeru)

Projekt byl od začátku budován s důrazem na kvalitní architekturu, testovatelnost a efektivní vývoj s využitím moderních nástrojů včetně umělé inteligence.

### Příklad workflow
```
09:00  [START]     Timer běží
09:40  [COMMIT]    "Oprava CSS navů"
10:15  [COMMIT]    "Mobilní layout"
11:00  [STOP]      Zakonči den

Výsledek v projektu:
09:00–09:40  Oprava CSS navů
09:40–10:15  Mobilní layout
10:15–11:00  (bez popisu)

Celkem: 2h práce
```

---

## 🎨 Design zaměření

### MVP Features
- ✅ Autentizace (register, login, logout, change password)
- ✅ Správa klientů (CRUD + search + stats)
- ✅ Správa projektů (CRUD + filtry + overdue detekce)
- ✅ Commit-based timer (core feature)
- ✅ Dashboard se statistikami
- ✅ Multi-tenant workspaces
- ✅ Dark theme, jednoduché UI
- ✅ Service layer architektura
- ✅ 92%+ test coverage (260 testů)

### Proč commits?
- Přirozený workflow (jak přemýšlíš)
- Automaticky vytváří worklogy pro faktury
- Brání procrastinaci
- Přehledná timeline v projektu

## 🚀 Status

| Metric | Result |
|--------|--------|
| **Testy** | ✅ 260/260 passing (100%) |
| **Pokrytí** | ✅ 92.74% overall |
| **Security Audit** | ✅ EXCELLENT |
| **API Endpoints** | ✅ 50+ plně funkčních |
| **Databázové modely** | ✅ 8 kompletních |
| **Dokumentace** | ✅ Kompletní |

| Fáze | Co | Status |
|---|---|---|
| **Den 1** | Auth (register, login, logout, JWT) | ✅ HOTOVO |
| **Den 2-3** | Models + API (clients, projects, timer) | ✅ HOTOVO |
| **Den 4-5** | Frontend templates + layout + CRUD UI | ✅ HOTOVO |
| **Den 6** | Service layer + workspace support | ✅ HOTOVO |
| **Den 7** | Timer + commit workflow | ✅ HOTOVO |
| **Den 8** | Testy + security audit + coverage | ✅ HOTOVO |
| **Den 9** | Deploy + polish | ⏳ TODO |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12** + **Django 6.0** + **Django REST Framework**
- **PostgreSQL** – produkční DB
- **SimpleJWT** – autentizace (tokens, refresh, blacklist)
- **django-cors-headers** – CORS podpora
- **django-filter** – filtry na API endpointech
- **python-decouple** – environment variables

### Frontend (v1 – aktuální)
- **Django templates** – HTML + vanilla JS
- **Fetch API** – bez buildu
- **Dark theme CSS** – připraveno

### Frontend (v2 – plánované)
- React + TypeScript + shadcn/ui

### Testing
- **pytest** + pytest-django + pytest-cov
- **Factory Boy** + Faker – testovací data
- **260 testů**, 92.74% coverage

---

## 📂 Struktura projektu

```
freelanceos/
├── config/
│   └── settings/
│       ├── base.py          # Sdílená konfigurace
│       ├── development.py   # Dev prostředí (DEBUG=True)
│       ├── production.py    # Produkce (HTTPS, security headers)
│       └── testing.py       # Testy (SQLite in-memory)
├── core/
│   ├── settings.py          # Import z config/settings
│   ├── urls.py              # Root URL routing
│   ├── api_urls.py          # Dashboard stats API
│   ├── views.py             # Dashboard view
│   └── management/commands/ # seed, seed_test
├── users/
│   ├── models.py            # User (custom, email-based), UserProfile
│   ├── serializers.py       # Register, User, ChangePassword
│   ├── views.py             # Auth endpoints (JWT)
│   ├── urls.py              # /api/v1/auth/*
│   ├── template_views.py    # Template views
│   └── template_urls.py     # /accounts/*
├── clients/
│   ├── models.py            # Client model
│   ├── serializers.py       # List, Detail, CreateUpdate serializers
│   ├── services.py          # ClientService (business logic)
│   ├── views.py             # Client CRUD + stats + projects
│   ├── urls.py              # /api/v1/clients/*
│   └── tests/               # 41 testů (100% coverage)
├── projects/
│   ├── models.py            # Project model (7 statusů, overdue)
│   ├── serializers.py       # List, Detail, CreateUpdate serializers
│   ├── services.py          # ProjectService (business logic)
│   ├── views.py             # Project CRUD + stats
│   ├── urls.py              # /api/v1/projects/*
│   └── tests/               # 47 testů (92-100% coverage)
├── workcommits/
│   ├── models.py            # WorkCommit (timer s commits)
│   ├── serializers.py       # WorkCommitSerializer
│   ├── views.py             # Start, stop, commit, running
│   ├── urls.py              # /api/v1/workcommits/*
│   └── admin.py
├── apps/
│   ├── common/
│   │   ├── models.py        # BaseModel, SoftDeleteModel
│   │   ├── permissions.py   # Workspace permissions
│   │   ├── middleware.py     # WorkspaceMiddleware
│   │   ├── exceptions.py    # Custom API errors
│   │   └── pagination.py    # Custom pagination
│   └── workspaces/
│       ├── models.py        # Workspace, WorkspaceMembership
│       ├── serializers.py   # Workspace serializers
│       ├── services.py      # WorkspaceService
│       ├── views.py         # Workspace CRUD
│       └── urls.py          # /api/v1/workspaces/*
├── templates/
│   ├── layouts/base.html    # Base layout
│   ├── auth/                # Login, register, dashboard
│   └── dashboard/           # Clients, projects, timer views
├── tests/
│   ├── conftest.py          # Global fixtures (users, clients, projects)
│   ├── factories.py         # UserFactory, ClientFactory, ProjectFactory
│   └── utils.py             # Test utilities
├── scripts/                 # Coverage, linting, e2e skripty
├── docs/                    # Architektura, roadmap, testing docs
├── requirements.txt         # Produkční závislosti (7)
├── requirements-dev.txt     # Dev závislosti (22)
├── pytest.ini               # Pytest konfigurace
└── manage.py
```

---

## 🚀 Quick Start

### Instalace

#### 1. Clone & setup
```bash
git clone https://github.com/tanatos09/freelanceOS
cd freelanceos
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements-dev.txt
```

#### 2. Database
```bash
# PostgreSQL (na macOS se Homebrew)
brew install postgresql
brew services start postgresql

# Vytvoř databázi
createdb freelanceos
psql freelanceos -c "CREATE USER freelanceos_admin WITH PASSWORD 'heslo123';"
psql freelanceos -c "ALTER ROLE freelanceos_admin SET client_encoding TO 'utf8';"
psql freelanceos -c "GRANT ALL PRIVILEGES ON DATABASE freelanceos TO freelanceos_admin;"
```

#### 3. Django migrations
```bash
python manage.py migrate
python manage.py createsuperuser  # Admin účet
```

#### 4. Run dev server
```bash
python manage.py runserver 8000
```

**App je live:** http://localhost:8000/accounts/login/

### Účty na testování
```bash
email: test@example.com
password: testpass123
```

---

## 📚 API Reference

**Base URL:** `http://localhost:8000/api/v1/`  
**Auth:** `Authorization: Bearer <jwt_token>`

### Auth Endpoints

#### Register
```bash
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "password2": "securepass123"
}

Response (201):
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-03-07T12:00:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```bash
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (200): Stejné jako register
```

#### Get Current User
```bash
GET /api/v1/auth/me/
Authorization: Bearer <access_token>

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "timezone": "UTC",
  "locale": "cs",
  "created_at": "2026-03-07T12:00:00Z"
}
```

#### Logout
```bash
POST /api/v1/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}

Response (200):
{
  "detail": "Odhlášení proběhlo úspěšně."
}
```

#### Change Password
```bash
POST /api/v1/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "securepass123",
  "new_password": "newpass456"
}
```

#### Refresh Token
```bash
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

### Clients ✅
```
GET    /api/v1/clients/              # List (search, order, paginated)
POST   /api/v1/clients/              # Create
GET    /api/v1/clients/{id}/         # Detail (+ total earnings)
PUT    /api/v1/clients/{id}/         # Update
DELETE /api/v1/clients/{id}/         # Delete
GET    /api/v1/clients/{id}/stats/   # Client statistics
GET    /api/v1/clients/{id}/projects/ # Client's projects
```

### Projects ✅
```
GET    /api/v1/projects/             # List (filter: status, client, overdue)
POST   /api/v1/projects/             # Create
GET    /api/v1/projects/{id}/        # Detail (+ hours, earnings)
PUT    /api/v1/projects/{id}/        # Update
DELETE /api/v1/projects/{id}/        # Delete
GET    /api/v1/projects/stats/       # Projects statistics
```

### WorkCommits – TIMER (Core Feature) ✅
```
GET    /api/v1/workcommits/              # List (filter: project, date)
GET    /api/v1/workcommits/running/      # Get active timer
POST   /api/v1/workcommits/start/        # Start timer {project: 1}
POST   /api/v1/workcommits/{id}/commit/  # Stop & commit {description: "..."}
POST   /api/v1/workcommits/{id}/stop/    # Stop timer
GET    /api/v1/workcommits/{id}/         # Detail
```

### Dashboard ✅
```
GET /api/v1/dashboard/stats/?range=today|week|month

Response: { projects_active, hours_worked, earnings, overdue_count }
```

### Workspaces ✅
```
GET    /api/v1/workspaces/           # List workspaces
POST   /api/v1/workspaces/           # Create workspace
GET    /api/v1/workspaces/{id}/      # Detail
PUT    /api/v1/workspaces/{id}/      # Update
DELETE /api/v1/workspaces/{id}/      # Delete
```

---

## 🔐 Authentication

JWT-based. Token se ukládá v `localStorage`:
```javascript
localStorage.getItem('access_token')  // GET requests v header
localStorage.getItem('refresh_token') // Refresh když access expiruje
```

Logout: token se zneplatní (blacklist) → musíš se znova přihlásit.

---

## 📊 Database Models

```python
User (custom, email-based auth)
├── email (unique)
├── password (hashed, PBKDF2)
├── is_active, is_staff, is_superuser
├── created_at, updated_at
└── 1:1 UserProfile (timezone, locale)

Client
├── user (FK), workspace (FK, nullable)
├── name, email, phone, company
├── hourly_rate (Decimal)
├── notes
├── created_at, updated_at
├── Unique: (user, email)
└── Methods: total_earnings(), project_count()

Project
├── user (FK), workspace (FK, nullable), client (FK)
├── name, description
├── status (draft/active/paused/pending_payment/completed/archived/cancelled)
├── budget, estimated_hours, hourly_rate
├── start_date, end_date
├── created_at, updated_at
└── Methods: is_overdue(), days_until_deadline(), progress_percent()

WorkCommit
├── user (FK), project (FK)
├── start_time, end_time (nullable = running)
├── description (max 100)
├── duration_seconds
├── created_at
└── Methods: stop(), duration_hours(), is_running (property)

Workspace
├── name, slug (unique), owner (FK)
├── plan (free/starter/professional/enterprise)
├── settings (JSONField), is_active
└── 1:N WorkspaceMembership (role: owner/admin/member/viewer)
```

---

## 🏗️ Architektura

### Klíčové vzory
- **Service Layer** – ClientService, ProjectService, WorkspaceService oddělují business logiku od views
- **Multi-tenancy** – WorkspaceMiddleware (header/query param) + data isolation
- **Soft Delete** – BaseModel + SoftDeleteModel s `deleted_at` a správci objects/all_objects
- **Split Settings** – base/development/production/testing konfigurace
- **Factory Boy** – UserFactory, ClientFactory, ProjectFactory pro realistická testovací data

### Middleware Stack
1. SecurityMiddleware
2. CorsMiddleware
3. SessionMiddleware
4. CommonMiddleware
5. CsrfViewMiddleware
6. AuthenticationMiddleware
7. **WorkspaceMiddleware** (custom – resolves workspace from header/query)
8. MessageMiddleware
9. XFrameOptionsMiddleware

---

## 🔒 Security

📖 **See [SECURITY.md](SECURITY.md) for detailed security information.**

- ✅ **JWT Authentication** – SimpleJWT with token refresh & blacklist
- ✅ **Password Hashing** – PBKDF2 with SHA256
- ✅ **CSRF Protection** – Middleware enabled
- ✅ **Rate Limiting** – 100 req/hour (anon), 1,000 req/hour (auth)
- ✅ **User Data Isolation** – All queries scoped to `request.user`
- ✅ **CORS** – Configured via django-cors-headers
- ✅ **Environment Variables** – python-decouple, no hardcoded secrets
- ✅ **Split Settings** – Separate dev/prod/testing configs
- ✅ **Security Audit** – Completed ✅ EXCELLENT

### Setup Environment Variables

```bash
cp .env.example .env
# Edit with your values (NEVER commit .env!)

# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🧪 Testing

```bash
# Všechny testy
pytest

# Verbose s outputem
pytest -vv -s

# Jen unit testy
pytest -m unit

# Coverage report
pytest --cov --cov-report=html

# Stop na prvním failure
pytest -x

# Paralelní běh
pytest -n 4
```

### Coverage Summary

| Modul | Coverage |
|-------|----------|
| clients/ | 95-100% |
| projects/ | 77-98% |
| users/ | 100% |
| apps.workspaces/ | 24-95% |
| apps.common/ | 40-71% |
| **Celkem** | **92.74%** |

**260 testů, 100% pass rate**

---

## 💻 Development Commands

```bash
# Dev server
python manage.py runserver 8000

# Django shell
python manage.py shell

# Seed data
python manage.py seed

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Linting
ruff check .
black --check .

# Coverage HTML report
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## 🚀 Deployment

### Produkční checklist
- [ ] `.env` file s production hodnotami
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` z .env
- [ ] `ALLOWED_HOSTS` = tvá doména
- [ ] PostgreSQL backups
- [ ] Gunicorn setup
- [ ] HTTPS + domain
- [ ] `collectstatic`

---

## 📝 Poznámky k Vývoji

### Proč Django templates v1?
- Deploy v jednom serveru
- Žádný build proces
- React přijde ve v2

### Proč commits místo timeru?
- Přirozený workflow
- Data-driven insights
- Podklad pro faktury

---

## ⏳ Post-MVP (v2.0)

- Faktury (PDF generování)
- Leads / Poptávky (kanban board)
- Grafy (earnings over time)
- Export dat (CSV)
- React + TypeScript frontend
- Dark mode toggle
- Keyboard shortcuts
- Multi-user teams

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT

---

## 🎯 Next Steps

1. **Den 2:** Modely Client, Project, WorkCommit
2. **Den 3:** REST API (CRUD + dashboard)
3. **Den 4-5:** Frontend forms a navigation
4. **Den 7:** Timer interface s commits
5. **Den 8-9:** Polish a deploy

---

## 📧 Contact / Questions

tanatos09@gmail.com

---

**Made with ❤️ for freelancers who want to own their data.**
