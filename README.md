# FreelanceOS

> Time tracking s commit-based workflow pro freelancery.

## 🚧 Aktuální vývoj (checklist)

Tato sekce bude obsahovat seznam aktuálních úkolů rozdělený podle priority.

### 🔴 MUST (kritické opravy)

* Opravit validaci formulářů (zobrazovat chyby přímo v UI, ne jen v network)
* Opravit flow vytváření projektu (nejdřív klient, pak projekt)
* Opravit nekonzistenci timeru (frontend vs backend čas)
* Opravit náhodné selhání ukládání projektu

### 🟡 SHOULD (UX vylepšení)

* Přidat datepicker pro výběr datumu
* Přidat pause funkci pro timer
* Opravit "odpracováno dnes" (neaktualizuje se správně)
* Vylepšit notifikace (viditelnost a konzistence)

### 🟢 NICE TO HAVE (budoucí vylepšení)

* Přidat onboarding pro nové uživatele
* Přidat podporu pro tým / zaměstnance
* Vylepšit chování na mobilu (taby, background)
* Přidat empty states a tooltipy

## Co to je

**FreelanceOS** je minimalistické CRM + time tracker. Klíčová vlastnost: **commit-based time tracking** — místo klasického timeru commituješ práci průběžně (jako git).

```
09:00  [START]     Timer běží
09:40  [COMMIT]    "Oprava CSS navů"
10:15  [COMMIT]    "Mobilní layout"
11:00  [STOP]      Konec dne → 2h práce
```

## MVP Features

- **Auth** — registrace, login, logout, JWT tokeny
- **Klienti** — CRUD, vyhledávání, statistiky
- **Projekty** — CRUD, 7 statusů, overdue detekce
- **Timer** — start/stop/commit workflow
- **Dashboard** — přehled výdělků a aktivních projektů
- **Workspaces** — multi-tenant podpora

## Tech Stack

- **Backend:** Python 3.12, Django 5.0+, Django REST Framework
- **DB:** PostgreSQL
- **Auth:** JWT (SimpleJWT)
- **Frontend:** Django templates + vanilla JS
- **Testy:** pytest, Factory Boy, 92%+ coverage

## Quick Start

```bash
# 1. Setup
git clone https://github.com/tanatos09/freelanceOS
cd freelanceos
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS
pip install -r requirements-dev.txt

# 2. Environment
cp .env.example .env
# Edituj .env (SECRET_KEY, DB credentials)

# 3. Database
python manage.py migrate
python manage.py createsuperuser

# 4. Run
python manage.py runserver 8000
# → http://localhost:8000/accounts/login/
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`  
Auth: `Authorization: Bearer <jwt_token>`

| Modul | Endpoints |
|-------|-----------|
| **Auth** | `POST register/`, `POST login/`, `POST logout/`, `GET me/`, `POST change-password/`, `POST token/refresh/` |
| **Clients** | `GET/POST /clients/`, `GET/PUT/DELETE /clients/{id}/`, `GET /clients/{id}/stats/` |
| **Projects** | `GET/POST /projects/`, `GET/PUT/DELETE /projects/{id}/`, `GET /projects/stats/` |
| **Timer** | `GET /workcommits/`, `GET /workcommits/running/`, `POST /workcommits/start/`, `POST /workcommits/{id}/commit/`, `POST /workcommits/{id}/stop/` |
| **Dashboard** | `GET /dashboard/stats/?range=today\|week\|month` |
| **Workspaces** | `GET/POST /workspaces/`, `GET/PUT/DELETE /workspaces/{id}/` |

## Struktura projektu

```
freelanceos/
├── config/settings/        # Split settings (base/dev/prod/testing)
├── core/                   # Dashboard API, URL routing
├── users/                  # Auth + User model
├── clients/                # Client CRUD + service layer
├── projects/               # Project CRUD + service layer
├── workcommits/            # Timer (start/stop/commit)
├── apps/common/            # BaseModel, middleware, permissions
├── apps/workspaces/        # Multi-tenant workspaces
├── templates/              # Django HTML templates
├── static/                 # CSS + JS
├── tests/                  # Fixtures, factories
├── docs/                   # Architektura, roadmap, testing
└── scripts/                # Coverage, linting, e2e
```

## Příkazy

```bash
pytest                         # Všechny testy
pytest -m unit                 # Jen unit testy
pytest --cov --cov-report=html # Coverage
python manage.py seed          # Test data
python manage.py runserver     # Dev server
```

## Dokumentace

- [ARCHITECTURE.md](ARCHITECTURE.md) — struktura projektu a jak spolu části komunikují
- [ROADMAP.md](ROADMAP.md) — co je hotové, co je plán
- [TESTING.md](TESTING.md) — jak spustit testy
- [CONTRIBUTING.md](CONTRIBUTING.md) — jak přispívat
- [SECURITY.md](SECURITY.md) — bezpečnostní politika

## License

MIT

tanatos09@gmail.com

---

**Made with ❤️ for freelancers who want to own their data.**
