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

### Minimální MVP (Den 1–9)
- ✅ Autentizace (login, logout)
- Správa klientů a projektů
- Commit-based timer (core feature)
- Dashboard se statistikami
- Dark theme, jednoduché UI

### Proč commits?
- Přirozený workflow (jak přemýšlíš)
- Automaticky vytváří worklogy pro faktury
- Brání procrastinaci
- Přehledná timeline v projektu

### Single-user MVP
- Bez složité autorizace
- Tvoje data = tvoje projekty
- Multi-user v2.0

## 🚀 Status

| Fáze | Co | Status |
|---|---|---|
| **Den 1** | Auth (login, register, logout) | ✅ HOTOVO |
| **Den 2-3** | Models + API (clients, projects, timer) | ✅ HOTOVO |
| **Den 4-5** | Frontend (layouts, CRUD forms, timer UI) | 🔄 IN PROGRESS |
| **Den 7** | Timer + commit workflow | ⏳ TODO |
| **Den 8-9** | Polish + deploy | ⏳ TODO |

---

### Backend
- **Django 6.0** + Django REST Framework
- **PostgreSQL** – produkční DB
- **SimpleJWT** – autentizace (tokens, blacklist)
- **CORS** – pro frontend

### Frontend (v1)
- **Django templates** – HTML + vanilla JS
- **Fetch API** – bez buildu
- **Dark theme CSS** – připraveno

### Frontend (v2+)
- React + TypeScript (plánované)

---

## 📂 Struktura projektu

```
core/
├── settings.py       # Django config
├── urls.py          # URL routing
├── views.py         # API views
└── wsgi.py

users/
├── models.py        # User, UserProfile
├── serializers.py   # API serializers
├── views.py         # Auth endpoints
├── urls.py          # Auth routing
├── template_views.py   # Template views
└── template_urls.py    # Template URLs

templates/
├── base.html        # Base layout
└── auth/
    ├── login.html
    ├── register.html
    └── dashboard.html

manage.py
```

---

## 🚀 Quick Start

### Instalace

#### 1. Clone & setup
```bash
git clone <repo>
cd freelanceos
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
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

### Auth Endpoints

#### Register
```bash
POST /api/auth/register/
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
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (200): Stejné jako register
```

#### Get Current User
```bash
GET /api/auth/me/
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
POST /api/auth/logout/
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
POST /api/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "securepass123",
  "new_password": "newpass456"
}

Response (200):
{
  "detail": "Heslo bylo úspěšně změněno."
}
```

#### Refresh Token
```bash
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}

Response (200):
{
  "access": "<new_access_token>",
  "refresh": "<new_refresh_token>"  // Optional, if rotation enabled
}
```

### Clients (TBD Den 2-3)
```
GET    /api/clients/         # List
POST   /api/clients/         # Create
GET    /api/clients/{id}/    # Detail
PUT    /api/clients/{id}/    # Update
DELETE /api/clients/{id}/    # Delete
```

### Clients (TBD Den 4-5)
```
GET    /api/clients/         # List
POST   /api/clients/         # Create
GET    /api/clients/{id}/    # Detail
PUT    /api/clients/{id}/    # Update
DELETE /api/clients/{id}/    # Delete
```

### Projects (TBD Den 4-5)
```
GET    /api/projects/        # List (filtry: status, client)
POST   /api/projects/        # Create
GET    /api/projects/{id}/   # Detail (+ commits timeline)
PUT    /api/projects/{id}/   # Update
DELETE /api/projects/{id}/   # Delete
GET    /api/projects/overdue/ # Overdue only
```

### WorkCommits – TIMER (✅ HOTOVO)
```
POST   /api/workcommits/start/        # Start timer
                                      # Body: {"project": 1}
                                      # Response: WorkCommit { id, is_running: true }

POST   /api/workcommits/{id}/commit/  # Finish + continue
                                      # Body: {"description": "...", "continue": true}
                                      # Response: {commit, next_commit}

POST   /api/workcommits/{id}/stop/    # Stop timer (no continue)

GET    /api/workcommits/              # List (filtry: project)

GET    /api/workcommits/running/      # Current running commit

DELETE /api/workcommits/{id}/         # Delete
```

### Dashboard (✅ HOTOVO)
```
GET    /api/dashboard/stats/          # Stats: 
                                      # {
                                      #   active_projects_count: 3,
                                      #   today_hours: 2.5,
                                      #   week_hours: 17,
                                      #   month_hours: 42,
                                      #   month_earnings: 12500,
                                      #   overdue_projects_count: 1
                                      # }
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

## 📊 Database Models (Design)

```python
# users/models.py
User
├── email (unique)
├── password (hashed)
├── is_active
├── is_staff
├── created_at

UserProfile (1:1 s User)
├── timezone
├── locale

# core/models.py (TBD)
Client
├── user (FK)
├── name
├── email
├── phone
├── notes

Project
├── user (FK)
├── client (FK)
├── name
├── status (new/in_progress/done/paid)
├── rate (CZK/hour, optional)
├── deadline
├── notes
├── created_at

WorkCommit
├── user (FK)
├── project (FK)
├── start_time
├── end_time (nullable – timer běží)
├── description (max 100 chars)
├── duration_seconds (auto)
├── created_at
```

---

## 📅 Development Roadmap

| Den | Fáze | Status |
|-----|------|--------|
| 1   | Auth (register, login, logout) | ✅ **HOTOVO** |
| 2   | Models: Client, Project, WorkCommit | 🔄 IN PROGRESS |
| 3   | REST API + Dashboard stats | ⏳ TODO |
| 4-5 | Frontend: sidebar, CRUD forms | ⏳ TODO |
| 7   | Timer & commit workflow | ⏳ TODO |
| 8-9 | Polish + deploy | ⏳ TODO |

---

## 🎯 Co Se Musí Zvládnout (MVP)

- ✅ Registrace a login
- ✅ Odhlášení (token blacklist)
- ⏳ CRUD: Clients, Projects
- ⏳ **Timer s commits** (core feature)
- ⏳ Dashboard se stats
- ⏳ Overdue alerts
- ⏳ Export do CSV

---

## 🚀 Deployment

### Produkční checklist
- [ ] `.env` file (nepublikuj!)
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` z .env
- [ ] `ALLOWED_HOSTS` = tvá doména
- [ ] PostgreSQL backups
- [ ] Gunicorn service (systemd)
- [ ] HTTPS + domain

### Deploy na Railway/Render
```bash
# Postup (později v roadmapě)
1. Vytvoř .env file
2. Git push na Railway/Render
3. Automatic deploy
4. PostgreSQL backups setup
```

---

## � Security

📖 **See [SECURITY.md](SECURITY.md) and [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md) for detailed security information.**

### Quick Security Checklist

- ✅ **JWT Authentication** - Tokens with 60-minute lifetime
- ✅ **Password Hashing** - PBKDF2 with 260,000 iterations
- ✅ **CSRF Protection** - Middleware enabled for all POST/PUT/DELETE
- ✅ **Rate Limiting** - 100 req/hour (anon), 1,000 req/hour (auth)
- ✅ **User Data Isolation** - Users see only their own data
- ✅ **HTTPS/SSL** - Enforced in production
- ✅ **Environment Variables** - All secrets from .env (never in code)

### Setup Environment Variables

```bash
# Development: Copy template
cp .env.example .env

# Edit with your values (NEVER commit .env!)
nano .env

# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Before Publishing to GitHub

1. ✅ Remove `.env` from git history
2. ✅ Verify `.env` is in `.gitignore`
3. ✅ No secrets in code
4. ✅ `DEBUG=False` for production config
5. ✅ Strong database passwords set

**See [SECURITY_ACTION_PLAN.md](SECURITY_ACTION_PLAN.md) for step-by-step deployment security checklist.**

---

## �💻 Development Commands

### Django shell
```bash
python manage.py shell
>>> from users.models import User
>>> User.objects.all()
```

### Create test data
```bash
python manage.py createsuperuser
email: admin@test.cz
password: admin123
```

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run tests (TBD)
```bash
python manage.py test
```

---

## 🐛 Troubleshooting

### Port 8000 je obsazený
```bash
python manage.py runserver 8001
```

### PostgreSQL se neconnectuje
```bash
# Zkontroluj credentials v settings.py
NAME = 'freelanceos'
USER = 'freelanceos_admin'
PASSWORD = 'heslo123'
HOST = 'localhost'
PORT = '5432'
```

### CORS error
Zkontroluj `CORS_ALLOWED_ORIGINS` v settings.py

---

## 📝 Poznámky k Vývoji

### Proč Django templates?
- Deploy v jednom serveru (test + produkcí)
- Žádný build proces
- Snadné a rychlé
- React můžeš přidat později (v2)

### Proč single-user MVP?
- Bez složité autorizace
- Snadnější vývoj
- Ověření value propositions
- Multi-user v2.0

### Proč commits?
- Přirozený workflow
- Data-driven insights
- Podklad pro faktury
- Sebeuvědomění práce

---

## 🤝 Contributing

```bash
# Vytvoř branch
git checkout -b feature/new-feature

# Push a otevři PR
```

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

frank@example.com

---

**Made with ❤️ for freelancers who want to own their data.**
