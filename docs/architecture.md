# FreelanceOS — Architektonická analýza a plán refaktoringu

> Verze: 1.0 | Datum: 2026-03-08
> Autor: Principal Software Architect

---

## 1. ANALÝZA SOUČASNÉ ARCHITEKTURY

### 1.1 Současná struktura

```
freelanceos/
├── core/           ← Django config + dashboard logika (dual responsibility)
├── users/          ← Autentizace, User model, profil
├── clients/        ← CRUD klienti
├── projects/       ← CRUD projekty
├── templates/      ← Django templates frontend
├── e2e/            ← E2E testy (Playwright)
├── scripts/        ← Skripty pro coverage, linting
└── manage.py
```

### 1.2 Co je dobré (zachovat)

| Oblast | Detail |
|--------|--------|
| Custom User model | Email-based auth, dobrý základ |
| Service layer pattern | ClientService, ProjectService oddělují business logiku od views |
| JWT s refresh rotation | Token blacklisting, rotace tokenů |
| Serializer separation | List/Detail/CreateUpdate — správný vzor |
| Database indexy | Indexy na (user, created_at), (user, status) |
| Test coverage | 40+ unit testů, edge cases, E2E |
| Django admin | Registrace modelů s filtry a vyhledáváním |

### 1.3 Datový model (současný)

```
User (email auth)
 ├── 1:1 UserProfile (timezone, locale)
 ├── 1:N Client (user → clients)
 └── 1:N Project (user → projects)
              └── N:1 Client (project → client)
```

---

## 2. IDENTIFIKOVANÉ PROBLÉMY

### 🔴 Kritické (bezpečnost / architektura)

| # | Problém | Dopad |
|---|---------|-------|
| P1 | **Hardcoded SECRET_KEY** v settings.py | Bezpečnostní riziko v produkci |
| P2 | **Hardcoded DB heslo** (`heslo123`) | Přístup k databázi kompromitován |
| P3 | **DEBUG=True** bez env řízení | Framework info leaks v produkci |
| P4 | **Žádná multi-tenancy** | Nelze sdílet workspace mezi uživateli, žádná podpora týmů |
| P5 | **Žádné API versioning** | Breaking changes nelze řešit postupně |
| P6 | **Žádná paginace** | API vrací všechny záznamy → memory overflow při škále |
| P7 | **Žádný rate limiting** | Zranitelnost vůči brute-force a DDoS |

### 🟠 Významné (škálovatelnost / kvalita)

| # | Problém | Dopad |
|---|---------|-------|
| P8 | **N+1 query v dashboard** | `sum(1 for p in projects if p.is_overdue())` — iteruje v Pythonu místo DB |
| P9 | **Žádný base model** | `created_at`/`updated_at` se opakuje v každém modelu |
| P10 | **Žádný soft delete** | CASCADE smaže vše permanentně, žádná obnova |
| P11 | **core/ app dual responsibility** | Konfigurace + business logika (dashboard) v jednom modulu |
| P12 | **Function-based views** | Hodně boilerplate, špatná kompozice permissions |
| P13 | **Žádné custom permissions** | Jen `IsAuthenticated`, žádné object-level/role-based |
| P14 | **Ownership check duplicace** | Kontrola vlastnictví v serializer I v service I ve view |
| P15 | **Ploché app rozvržení** | Všechny apps na root úrovni, neškáluje se |
| P16 | **Žádný structured logging** | Žádná konfigurace logování |
| P17 | **Bare except** v `client_projects` view | `except:` zachytí vše včetně SystemExit |
| P18 | **ValueError pro business exceptions** | Příliš generické, ztráta kontextu |
| P19 | **Cross-app circular imports** | Client importuje Project, Project importuje timetracking |
| P20 | **Jeden settings.py** | Není oddělení dev/prod/test nastavení |
| P21 | **Integer PKs** | Předvídatelné ID, enumeration attack |
| P22 | **Žádný STATICFILES_DIRS** | Static files v templates/ — nestandardní |

### 🟡 Menší (konvence / DX)

| # | Problém |
|---|---------|
| P23 | Smíšený jazyk (české help_text + anglický kód) |
| P24 | Žádné django-filter FilterSet třídy |
| P25 | Testy v jednom souboru místo test package |
| P26 | Seed příkazy v core/ místo vlastní app |

---

## 3. NÁVRH IDEÁLNÍ ARCHITEKTURY

### 3.1 Architektonické principy

1. **Domain-Driven App Structure** — každá app = jeden bounded context
2. **Multi-tenant first** — Workspace model jako základ všech dat
3. **Service Layer** — views jsou tenké, business logika v services
4. **Explicit permissions** — RBAC s workspace roles
5. **Soft delete default** — žádná permanentní ztráta dat
6. **UUID primary keys** — bezpečné, nepředvídatelné
7. **Environment-based config** — settings per environment
8. **API versioning** — `/api/v1/` prefix
9. **Standard pagination** — cursor/page-based na všech list endpointech
10. **Query optimization** — select_related, prefetch_related, database-level filtering

### 3.2 Cílová struktura projektu

```
freelanceos/
│
├── config/                              # ← přejmenováno z core/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                      # Sdílené nastavení
│   │   ├── development.py               # DEBUG=True, logování
│   │   ├── production.py                # Security, HTTPS, cache
│   │   └── testing.py                   # In-memory SQLite, fast
│   ├── urls.py                          # Root URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                                # Všechny Django aplikace
│   ├── __init__.py
│   │
│   ├── common/                          # Sdílený kód (base models, mixins)
│   │   ├── __init__.py
│   │   ├── models.py                    # BaseModel, SoftDeleteModel
│   │   ├── mixins.py                    # WorkspaceOwnedMixin
│   │   ├── exceptions.py               # BusinessError, PermissionDenied
│   │   ├── permissions.py              # WorkspacePermission, RolePermission
│   │   ├── pagination.py               # StandardPagination
│   │   ├── throttling.py               # AnonThrottle, UserThrottle
│   │   ├── middleware.py               # WorkspaceMiddleware
│   │   └── utils.py
│   │
│   ├── accounts/                        # ← přejmenováno z users/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # User, UserProfile
│   │   ├── serializers.py
│   │   ├── services.py                  # AuthService
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── signals.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_services.py
│   │
│   ├── workspaces/                      # 🆕 Multi-tenant workspace
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # Workspace, WorkspaceMembership
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── clients/                         # Client management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py                   # 🆕 django-filter FilterSets
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── projects/                        # Project management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── timetracking/                    # 🆕 Time tracking (budoucí)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # TimeEntry
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── billing/                         # 🆕 Fakturace (budoucí)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # Invoice, InvoiceItem
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── activities/                      # 🆕 Audit log (budoucí)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # Activity
│   │   ├── services.py
│   │   └── tests/
│   │
│   └── dashboard/                       # 🆕 Dashboard & analytics
│       ├── __init__.py
│       ├── apps.py
│       ├── serializers.py
│       ├── services.py                  # DashboardService
│       ├── views.py
│       ├── urls.py
│       └── tests/
│
├── templates/                           # Django templates (MVP frontend)
├── static/                              # Static files (CSS, JS, images)
├── e2e/                                 # E2E testy
├── scripts/                             # Management skripty
│
├── manage.py
├── pyproject.toml
└── requirements/
    ├── base.txt                         # Produkční závislosti
    ├── development.txt                  # Dev tools (black, flake8, ...)
    └── testing.txt                      # Test runners
```

---

## 4. NÁVRH MODELŮ

### 4.1 BaseModel a SoftDeleteModel

```python
# apps/common/models.py
import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Základ pro všechny modely v systému."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(BaseModel):
    """Model s podporou soft delete."""
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])
```

### 4.2 Workspace (Multi-Tenancy)

```python
# apps/workspaces/models.py
from apps.common.models import BaseModel

class Workspace(BaseModel):
    """Workspace = organizace / tenant. Základ multi-tenancy."""

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='owned_workspaces',
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspaces_workspace'

    def __str__(self):
        return self.name


class WorkspaceMembership(BaseModel):
    """Členství uživatele ve workspace s rolí."""

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='workspace_memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspaces_membership'
        unique_together = ('workspace', 'user')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['workspace', 'role']),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.workspace.name} ({self.role})"
```

### 4.3 WorkspaceOwnedMixin

```python
# apps/common/mixins.py
from django.db import models


class WorkspaceOwnedMixin(models.Model):
    """Mixin pro všechny modely patřící do workspace."""
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)ss',
    )

    class Meta:
        abstract = True
```

### 4.4 User model (vylepšený)

```python
# apps/accounts/models.py
from apps.common.models import BaseModel

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Custom user model s UUID PK a email autentizací."""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Pozor: BaseModel přidá created_at/updated_at + UUID id

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'accounts_user'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Preferences
    timezone = models.CharField(max_length=64, default='UTC')
    locale = models.CharField(max_length=16, default='cs')
    avatar_url = models.URLField(blank=True)

    # Default workspace (rychlý přístup)
    default_workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'accounts_userprofile'
```

### 4.5 Client model (workspace-aware)

```python
# apps/clients/models.py
from apps.common.models import SoftDeleteModel
from apps.common.mixins import WorkspaceOwnedMixin

class Client(SoftDeleteModel, WorkspaceOwnedMixin):
    """Klient patřící do workspace."""

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    # Kontaktní osoba (volitelné)
    contact_person = models.CharField(max_length=255, blank=True)

    # Business fields
    vat_id = models.CharField(max_length=30, blank=True)  # IČO / VAT
    address = models.TextField(blank=True)
    default_currency = models.CharField(max_length=3, default='CZK')
    default_hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )

    class Meta:
        db_table = 'clients_client'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['workspace', 'email'],
                condition=models.Q(email__gt='', deleted_at__isnull=True),
                name='unique_workspace_client_email',
            ),
        ]
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
            models.Index(fields=['workspace', 'name']),
        ]
```

### 4.6 Project model (workspace-aware)

```python
# apps/projects/models.py
from apps.common.models import SoftDeleteModel
from apps.common.mixins import WorkspaceOwnedMixin

class Project(SoftDeleteModel, WorkspaceOwnedMixin):
    """Projekt patřící do workspace, přiřazený klientovi."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('cancelled', 'Cancelled'),
    ]

    BILLING_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate'),
        ('retainer', 'Monthly Retainer'),
    ]

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,     # PROTECT místo CASCADE!
        related_name='projects',
    )
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_projects',
    )

    # Core
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Billing
    billing_type = models.CharField(
        max_length=20, choices=BILLING_TYPE_CHOICES, default='fixed',
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )
    currency = models.CharField(max_length=3, default='CZK')
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'projects_project'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['workspace', 'status', '-end_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]
```

### 4.7 TimeEntry model (budoucí)

```python
# apps/timetracking/models.py
from apps.common.models import BaseModel
from apps.common.mixins import WorkspaceOwnedMixin

class TimeEntry(BaseModel, WorkspaceOwnedMixin):
    """Záznam odpracovaného času."""

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='time_entries',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='time_entries',
    )

    description = models.CharField(max_length=500, blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)  # NULL = running timer
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Calculated on stop. Manual entries set this directly.',
    )
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )

    class Meta:
        db_table = 'timetracking_timeentry'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['project', '-started_at']),
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['workspace', '-started_at']),
        ]
```

### 4.8 Invoice model (budoucí)

```python
# apps/billing/models.py
from apps.common.models import SoftDeleteModel
from apps.common.mixins import WorkspaceOwnedMixin

class Invoice(SoftDeleteModel, WorkspaceOwnedMixin):
    """Faktura."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='invoices')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')

    number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='CZK')

    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'billing_invoice'
        constraints = [
            models.UniqueConstraint(
                fields=['workspace', 'number'],
                name='unique_workspace_invoice_number',
            ),
        ]


class InvoiceItem(BaseModel):
    """Řádek faktury."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'billing_invoiceitem'
```

### 4.9 Activity model (budoucí)

```python
# apps/activities/models.py
from apps.common.models import BaseModel
from apps.common.mixins import WorkspaceOwnedMixin

class Activity(BaseModel, WorkspaceOwnedMixin):
    """Audit log / activity feed."""

    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('comment', 'Comment'),
        ('time_logged', 'Time Logged'),
        ('invoice_sent', 'Invoice Sent'),
    ]

    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)

    # Generic relation (content_type + object_id)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Snapshot of changes (optional)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activities_activity'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['actor', '-created_at']),
        ]
```

### 4.10 Kompletní ER Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         WORKSPACE (tenant)                           │
│  id (UUID) | name | slug | owner_id → User | plan | settings        │
└──────┬───────────────────────────┬───────────────────────────────────┘
       │                           │
       │ 1:N                       │ 1:N
       ▼                           ▼
┌─────────────────┐     ┌─────────────────────────┐
│ WorkspaceMember  │     │        Client            │
│ workspace → WS   │     │ workspace → WS           │
│ user → User      │     │ name | email | company   │
│ role             │     │ vat_id | address          │
└─────────────────┘     │ default_hourly_rate       │
       │                └──────────┬──────────────┘
       │                           │
       ▼                           │ 1:N
┌─────────────────┐                ▼
│      User        │     ┌─────────────────────────┐
│ email | password │     │       Project            │
│ first/last_name  │     │ workspace → WS           │
│ is_active        │     │ client → Client (PROTECT) │
└──────┬──────────┘     │ assigned_to → User        │
       │                 │ name | status | budget    │
       │ 1:1             │ billing_type | hourly_rate│
       ▼                 │ start_date | end_date     │
┌─────────────────┐     └──────────┬──────────────┘
│  UserProfile     │               │
│ user → User      │               │ 1:N
│ timezone | locale│               ▼
│ default_workspace│     ┌─────────────────────────┐
└─────────────────┘     │     TimeEntry            │
                         │ workspace → WS           │
                         │ project → Project        │
                         │ user → User              │
                         │ started_at | ended_at    │
                         │ duration_minutes         │
                         │ is_billable              │
                         └─────────────────────────┘
                                    │
                         ┌──────────┴──────────────┐
                         ▼                          ▼
              ┌─────────────────┐      ┌──────────────────┐
              │    Invoice      │      │    Activity       │
              │ workspace → WS  │      │ workspace → WS   │
              │ client → Client │      │ actor → User     │
              │ project → Proj  │      │ action | changes │
              │ number | status │      │ content_type     │
              │ total | due_date│      │ object_id (UUID) │
              └─────────────────┘      └──────────────────┘
```

---

## 5. NÁVRH SERVISNÍ VRSTVY

### 5.1 Pravidla service layer

```
View → Serializer (validace) → Service (business logika) → Model (persistence)
                                       ↓
                              Activity log (side-effect)
```

**Pravidla:**
1. Views NIKDY nepřistupují přímo k ORM (žádný `Model.objects.filter()` ve views)
2. Services vrací objekty nebo raises `BusinessError`
3. Serializers validují vstup, services validují business pravidla
4. Ownership/permission kontroly v jednom místě (permission class + service)

### 5.2 Exceptions

```python
# apps/common/exceptions.py
from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessError(APIException):
    """Base exception pro business logiku."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Chyba v business logice.'


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Objekt nenalezen.'


class PermissionDeniedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Nemáte oprávnění k této akci.'
```

### 5.3 Permissions

```python
# apps/common/permissions.py
from rest_framework.permissions import BasePermission


class IsWorkspaceMember(BasePermission):
    """Uživatel musí být členem aktivního workspace."""

    def has_permission(self, request, view):
        workspace = request.workspace  # Set by WorkspaceMiddleware
        if not workspace:
            return False
        return workspace.memberships.filter(
            user=request.user, is_active=True,
        ).exists()


class IsWorkspaceAdmin(BasePermission):
    """Uživatel musí mít roli admin nebo owner."""

    def has_permission(self, request, view):
        workspace = request.workspace
        if not workspace:
            return False
        return workspace.memberships.filter(
            user=request.user,
            role__in=['admin', 'owner'],
            is_active=True,
        ).exists()


class IsWorkspaceOwner(BasePermission):
    """Uživatel musí být owner workspace."""

    def has_permission(self, request, view):
        workspace = request.workspace
        return workspace and workspace.owner == request.user
```

### 5.4 Workspace Middleware

```python
# apps/common/middleware.py

class WorkspaceMiddleware:
    """
    Nastaví request.workspace na základě:
    1. Header X-Workspace-Id
    2. Query param ?workspace=<slug>
    3. Default workspace z profilu uživatele
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.workspace = None

        if hasattr(request, 'user') and request.user.is_authenticated:
            workspace_id = (
                request.headers.get('X-Workspace-Id')
                or request.GET.get('workspace')
            )
            if workspace_id:
                from apps.workspaces.models import Workspace
                try:
                    request.workspace = Workspace.objects.get(
                        id=workspace_id,
                        memberships__user=request.user,
                        memberships__is_active=True,
                        is_active=True,
                    )
                except (Workspace.DoesNotExist, ValueError):
                    pass
            elif hasattr(request.user, 'profile') and request.user.profile.default_workspace:
                request.workspace = request.user.profile.default_workspace

        return self.get_response(request)
```

### 5.5 Příklad service pattern (ClientService)

```python
# apps/clients/services.py
from apps.common.exceptions import NotFoundError, PermissionDeniedError
from apps.activities.services import ActivityService
from .models import Client


class ClientService:
    """Business logika pro klienty. Vše workspace-scoped."""

    @staticmethod
    def list(workspace, filters=None):
        qs = Client.objects.filter(workspace=workspace)
        if filters:
            if filters.get('search'):
                qs = qs.filter(
                    Q(name__icontains=filters['search']) |
                    Q(email__icontains=filters['search']) |
                    Q(company__icontains=filters['search'])
                )
        return qs

    @staticmethod
    def get(workspace, client_id):
        try:
            return Client.objects.get(id=client_id, workspace=workspace)
        except Client.DoesNotExist:
            raise NotFoundError('Klient nenalezen.')

    @staticmethod
    def create(workspace, actor, **data):
        client = Client.objects.create(workspace=workspace, **data)
        ActivityService.log(workspace, actor, 'created', client)
        return client

    @staticmethod
    def update(workspace, actor, client_id, **data):
        client = ClientService.get(workspace, client_id)
        for key, value in data.items():
            setattr(client, key, value)
        client.save()
        ActivityService.log(workspace, actor, 'updated', client, changes=data)
        return client

    @staticmethod
    def delete(workspace, actor, client_id):
        client = ClientService.get(workspace, client_id)
        client.delete()  # soft delete
        ActivityService.log(workspace, actor, 'deleted', client)

    @staticmethod
    def stats(workspace, client_id):
        client = ClientService.get(workspace, client_id)
        projects = client.projects.all()
        return {
            'project_count': projects.count(),
            'total_budget': projects.aggregate(Sum('budget'))['budget__sum'] or 0,
            'active_projects': projects.filter(status='active').count(),
        }
```

---

## 6. NÁVRH API STRUKTURY

### 6.1 URL Layout (versioned, workspace-scoped)

```
/api/v1/
│
├── auth/
│   ├── POST   register/                    # Registrace
│   ├── POST   login/                       # Přihlášení → JWT
│   ├── POST   logout/                      # Blacklist refresh token
│   ├── GET    me/                          # Přihlášený uživatel
│   ├── POST   change-password/             # Změna hesla
│   └── POST   token/refresh/              # Refresh token
│
├── workspaces/
│   ├── GET    /                            # List user's workspaces
│   ├── POST   /                            # Create workspace
│   ├── GET    {id}/                        # Workspace detail
│   ├── PUT    {id}/                        # Update workspace
│   ├── GET    {id}/members/               # List members
│   ├── POST   {id}/members/               # Invite member
│   ├── PUT    {id}/members/{user_id}/     # Change role
│   └── DELETE {id}/members/{user_id}/     # Remove member
│
├── clients/                                # Workspace-scoped (Header: X-Workspace-Id)
│   ├── GET    /                            # List (paginated, filterable)
│   ├── POST   /                            # Create
│   ├── GET    {id}/                        # Detail
│   ├── PUT    {id}/                        # Update
│   ├── PATCH  {id}/                        # Partial update
│   ├── DELETE {id}/                        # Soft delete
│   └── GET    {id}/stats/                 # Client statistics
│
├── projects/                               # Workspace-scoped
│   ├── GET    /                            # List (filters: status, client, search, overdue)
│   ├── POST   /                            # Create
│   ├── GET    {id}/                        # Detail
│   ├── PUT    {id}/                        # Update
│   ├── PATCH  {id}/                        # Partial update
│   ├── DELETE {id}/                        # Soft delete
│   ├── GET    stats/                       # Project statistics
│   └── GET    {id}/time-entries/          # Time entries for project
│
├── time-entries/                           # Workspace-scoped (budoucí)
│   ├── GET    /                            # List (filters: project, date range)
│   ├── POST   /                            # Create / start timer
│   ├── GET    {id}/                        # Detail
│   ├── PUT    {id}/                        # Update
│   ├── DELETE {id}/                        # Delete
│   ├── POST   {id}/stop/                  # Stop running timer
│   └── GET    running/                     # Get running timer
│
├── invoices/                               # Workspace-scoped (budoucí)
│   ├── GET    /
│   ├── POST   /
│   ├── GET    {id}/
│   ├── PUT    {id}/
│   ├── DELETE {id}/
│   └── POST   {id}/send/                  # Mark as sent
│
├── activities/                             # Workspace-scoped (budoucí)
│   └── GET    /                            # Activity feed (filtered by object, date)
│
└── dashboard/
    ├── GET    stats/                       # Overview statistics
    └── GET    charts/                      # Chart data (budoucí)
```

### 6.2 Standardní response format

```json
// List endpoint (paginated)
{
  "count": 42,
  "next": "https://api.example.com/api/v1/clients/?page=2",
  "previous": null,
  "results": [
    { "id": "uuid", "name": "...", ... }
  ]
}

// Detail endpoint
{
  "id": "a1b2c3d4-...",
  "name": "Client Name",
  "email": "client@example.com",
  "created_at": "2026-03-08T12:00:00Z",
  "updated_at": "2026-03-08T12:00:00Z"
}

// Error response
{
  "detail": "Klient nenalezen.",
  "code": "not_found"
}

// Validation error
{
  "email": ["Tento email již máš v klientech."],
  "budget": ["Rozpočet nemůže být záporný."]
}
```

### 6.3 Class-Based Views (ViewSets)

```python
# apps/clients/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsWorkspaceMember
from apps.common.pagination import StandardPagination
from .models import Client
from .serializers import ClientListSerializer, ClientDetailSerializer, ClientWriteSerializer
from .services import ClientService
from .filters import ClientFilterSet


class ClientViewSet(viewsets.ModelViewSet):
    """CRUD pro klienty (workspace-scoped)."""
    permission_classes = [IsWorkspaceMember]
    pagination_class = StandardPagination
    filterset_class = ClientFilterSet
    lookup_field = 'id'

    def get_queryset(self):
        return Client.objects.filter(workspace=self.request.workspace)

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ClientWriteSerializer
        return ClientDetailSerializer

    def perform_create(self, serializer):
        ClientService.create(
            workspace=self.request.workspace,
            actor=self.request.user,
            **serializer.validated_data,
        )

    def perform_destroy(self, instance):
        ClientService.delete(
            workspace=self.request.workspace,
            actor=self.request.user,
            client_id=instance.id,
        )

    @action(detail=True, methods=['get'])
    def stats(self, request, id=None):
        data = ClientService.stats(request.workspace, id)
        return Response(data)
```

### 6.4 Pagination

```python
# apps/common/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 6.5 Filters

```python
# apps/clients/filters.py
import django_filters
from .models import Client


class ClientFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Client
        fields = ['search', 'created_after', 'created_before']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value) |
            Q(company__icontains=value)
        )
```

---

## 7. PLÁN REFAKTORINGU (KROK ZA KROKEM)

### Přehled fází

| Fáze | Název | Popis | Riziko |
|------|-------|-------|--------|
| 1 | Foundation | Settings, base models, env config | Nízké |
| 2 | Workspace | Multi-tenancy model, middleware | Střední |
| 3 | Migration | Přesun apps do apps/, přejmenování | Střední |
| 4 | API Upgrade | ViewSets, pagination, versioning | Střední |
| 5 | New Modules | Timetracking, billing, activities | Nízké |
| 6 | Production | Security hardening, deployment | Nízké |

---

### FÁZE 1: Foundation (Bezpečnost + Base Models)

**Cíl:** Opravit kritické bezpečnostní problémy a vytvořit sdílený základ pro modely.

**Kroky:**

1.1 **Přidat python-decouple**
```python
# .env (root)
SECRET_KEY=generate-new-strong-key-here
DEBUG=True
DATABASE_URL=postgres://freelanceos_admin:heslo123@localhost:5432/freelanceos
ALLOWED_HOSTS=localhost,127.0.0.1
```

1.2 **Rozdělit settings.py**
```
config/settings/
├── __init__.py          # from .development import *  (default)
├── base.py              # Sdílené
├── development.py       # DEBUG, verbose logging
├── production.py        # Security, HTTPS
└── testing.py           # SQLite, fast
```

1.3 **Vytvořit apps/common/**
- BaseModel (UUID + timestamps)
- SoftDeleteModel
- StandardPagination
- Custom exceptions (BusinessError, NotFoundError)

1.4 **Vytvořit requirements/**
```
requirements/
├── base.txt
├── development.txt
└── testing.txt
```

**Kompatibilita:** Stávající app zůstávají na místě. Nové modely dědí z BaseModel.

---

### FÁZE 2: Workspace Model (Multi-Tenancy)

**Cíl:** Přidat Workspace a WorkspaceMembership. Připravit přechod z user→workspace.

**Kroky:**

2.1 **Vytvořit app `workspaces`**
- Workspace model
- WorkspaceMembership model
- API endpoints (CRUD + members)
- WorkspaceMiddleware

2.2 **Migrace dat**
```python
# Data migration: pro každého existujícího usera vytvořit default workspace
def migrate_users_to_workspaces(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Workspace = apps.get_model('workspaces', 'Workspace')
    Membership = apps.get_model('workspaces', 'WorkspaceMembership')

    for user in User.objects.all():
        ws = Workspace.objects.create(
            name=f"{user.email}'s Workspace",
            slug=slugify(user.email),
            owner=user,
        )
        Membership.objects.create(workspace=ws, user=user, role='owner')
```

2.3 **Přidat workspace FK do Client a Project**
```python
# Přidat nullable workspace FK, pak data migration, pak NOT NULL
class Migration:
    # Step 1: Add nullable field
    # Step 2: Populate from user's default workspace
    # Step 3: Make NOT NULL
```

2.4 **Aktualizovat services** — filtrovat podle workspace místo user

**Kompatibilita:** Stará data dostanou default workspace. API zůstane funkční, workspace se nastaví z middleware (default workspace z profilu).

---

### FÁZE 3: Restructure Apps

**Cíl:** Přesunout apps do apps/ adresáře. Oddělit config od business logiky.

**Kroky:**

3.1 **Přesunout users/ → apps/accounts/**
3.2 **Přesunout clients/ → apps/clients/**
3.3 **Přesunout projects/ → apps/projects/**
3.4 **Extrahovat dashboard do apps/dashboard/**
3.5 **Aktualizovat všechny importy a app configs**

**Alternativa:** Pokud je přesouvání příliš disruptivní, ponechat apps na root úrovni a pouze přejmenovat `core` → `config`. Přesun lze udělat až později.

---

### FÁZE 4: API Upgrade

**Cíl:** Přejít na ViewSets, přidat paginaci, versioning, throttling.

**Kroky:**

4.1 **Přejít na ViewSets + Routers**
4.2 **Přidat API versioning** (`/api/v1/`)
4.3 **Přidat StandardPagination** na všechny list endpointy
4.4 **Přidat django-filter FilterSets**
4.5 **Přidat throttling** (anon: 100/day, user: 1000/day)
4.6 **Přidat PATCH support** (partial update)

**Kompatibilita:** Starý frontend se aktualizuje zároveň. Nebo se zachová `/api/` redirecting na `/api/v1/`.

---

### FÁZE 5: New Modules

**Cíl:** Implementovat timetracking, activities, billing.

**Kroky:**
5.1 **apps/timetracking/** — TimeEntry model, running timer
5.2 **apps/activities/** — Activity log, generic relations
5.3 **apps/billing/** — Invoice, InvoiceItem
5.4 **apps/dashboard/** — Složitější statistiky, chart data

---

### FÁZE 6: Production Hardening

**Cíl:** Security a deployment readiness.

**Kroky:**
6.1 **HTTPS enforcement** (SECURE_SSL_REDIRECT, HSTS)
6.2 **CORS production config**
6.3 **Database connection pooling** (django-db-connection-pool)
6.4 **Static files** (WhiteNoise nebo S3)
6.5 **Structured logging** (JSON logging)
6.6 **Health check endpoint**
6.7 **Sentry error tracking**
6.8 **CI/CD pipeline** (GitHub Actions)
6.9 **Docker + docker-compose**

---

## 8. PRIORITNÍ DOPORUČENÍ

### Okamžitě (dnes):
1. ✅ Odstranit hardcoded SECRET_KEY a DB heslo → `.env` + `python-decouple`
2. ✅ Vytvořit `apps/common/` s BaseModel a exceptions
3. ✅ Přidat paginaci do REST_FRAMEWORK config

### Tento týden:
4. Rozdělit settings na base/development/production
5. Vytvořit Workspace model a middleware
6. Přidat rate limiting

### Tento měsíc:
7. Migrace na ViewSets + Router
8. Implementace timetracking
9. Activity log

---

## ZÁVĚR

Současná architektura je **dobrý MVP základ** — service layer, JWT auth, serializer separation. Hlavní mezery jsou:

1. **Žádná multi-tenancy** (kritické pro SaaS)
2. **Security config** (hardcoded secrets)
3. **Žádná paginace** (nebude škálovat)
4. **Žádné RBAC** (jen IsAuthenticated)

Navržený plán zachovává zpětnou kompatibilitu a umožňuje postupný refactoring bez rozbití MVP. Klíčový je přechod z `user`-scoped dat na `workspace`-scoped data — to je architektonický posun z "single-user tool" na "multi-tenant SaaS".
