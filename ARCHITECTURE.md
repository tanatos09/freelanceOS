# Architektura FreelanceOS

## Přehled

Django REST API backend + Django template frontend. Vše v jednom serveru.

```
Browser  →  Django Templates (HTML + JS)
                    ↓
              Fetch API (JS)
                    ↓
         Django REST Framework (API)
                    ↓
            Service Layer (business logika)
                    ↓
              Django ORM → PostgreSQL
```

## Struktura projektu

```
freelanceos/
├── config/settings/        # base.py, development.py, production.py, testing.py
├── core/                   # URL routing, dashboard API, seed commands
├── users/                  # Custom User (email auth), JWT, profil
├── clients/                # Client model + CRUD API + ClientService
├── projects/               # Project model + CRUD API + ProjectService
├── workcommits/            # WorkCommit model + timer API (start/stop/commit)
├── apps/
│   ├── common/             # BaseModel, middleware, permissions, exceptions, pagination
│   └── workspaces/         # Workspace + membership + WorkspaceService
├── templates/              # Django HTML templates (login, dashboard, CRUD)
├── static/                 # CSS, JS
├── tests/                  # Globální fixtures a factories
├── scripts/                # Coverage, linting, e2e skripty
└── docs/                   # Detailní dokumentace
```

## Klíčové vzory

### Service Layer

Views → Service → ORM. Business logika je v `services.py`, ne ve views.

```
views.py          # HTTP request/response, validace, serializace
services.py       # Business pravidla, queries, validace dat
models.py         # Datový model, field validace
serializers.py    # Input/output transformace
```

### Modely

Všechny modely dědí z `BaseModel` (UUID PK + timestamps):

```
User → UserProfile (1:1)
Client → Project (1:N) → WorkCommit (1:N)
Workspace → WorkspaceMembership (1:N)
```

### URL routing

```
/admin/                     → Django admin
/api/v1/auth/*              → JWT auth (login, register, logout)
/api/v1/clients/*           → Client CRUD
/api/v1/projects/*          → Project CRUD
/api/v1/workcommits/*       → Timer API
/api/v1/workspaces/*        → Workspace CRUD
/api/v1/dashboard/stats/    → Dashboard statistiky
/accounts/*                 → Django template frontend
```

### Settings

Zpracovány přes `config/settings/`:
- `base.py` — sdílená konfigurace (INSTALLED_APPS, middleware, DRF, JWT)
- `development.py` — DEBUG=True, SQL logging
- `production.py` — DEBUG=False, HTTPS, security headers
- `testing.py` — fast password hasher, no throttling

`core/settings.py` je shim, který importuje z `config/settings/`.

### Multi-tenancy

`WorkspaceMiddleware` resolvuje workspace z:
1. `X-Workspace-Id` hlavičky
2. `?workspace=` query parametru
3. Default workspace uživatele

Data jsou izolována per-user přes `request.user` filtrování.
