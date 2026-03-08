# 🎯 FreelanceOS - Bodový plán implementace (Django verze)

## 📋 FÁZE 0: PŘÍPRAVA & SETUP

### 1. Příprava prostředí
- [ ] Nainstaluj Python 3.11+ (https://www.python.org/downloads/)
- [ ] Nainstaluj PostgreSQL nebo připrav Docker
- [ ] Nainstaluj Git
- [ ] Nainstaluj VS Code + Python extension
- [ ] Vytvoř složku projektu `devcrm/`

### 2. Vytvoř virtuální prostředí
bash cd devcrm python -m venv venv # Windows: venv\Scripts\activate # Mac/Linux: source venv/bin/activate
### 3. Nainstaluj Django a základní dependencies
bash pip install django djangorestframework django-cors-headers psycopg2-binary python-decouple djangorestframework-simplejwt pip freeze > requirements.txt
### 4. Vytvoř Django projekt
bash django-admin startproject backend . python manage.py startapp core
### 5. Nastav PostgreSQL databázi
- [ ] Vytvoř databázi `devcrm`
- [ ] Nastav `settings.py` → DATABASES
- [ ] Nastav `.env` soubor pro secrets

### 6. Základní konfigurace settings.py
- [ ] Přidej `rest_framework`, `corsheaders`, `core` do INSTALLED_APPS
- [ ] Nastav CORS (pro React frontend)
- [ ] Nastav REST_FRAMEWORK defaults
- [ ] Nastav JWT auth

---

## 📋 FÁZE 1: DATABÁZOVÉ MODELY

### 7. Vytvoř model User (custom)
- [ ] Extend AbstractUser nebo použij default
- [ ] Pole: email, password, role
- [ ] V settings.py: `AUTH_USER_MODEL = 'core.User'`

### 8. Vytvoř model Client
- [ ] Pole: name, company, email, phone, notes
- [ ] Timestamps: created_at, updated_at
- [ ] Method: `total_earnings()` → suma paid projektů

### 9. Vytvoř model Lead
- [ ] Pole: name, description, estimated_budget
- [ ] Pole: technologies (JSONField), priority, source
- [ ] Pole: status (CharField s choices: new/contacted/deal/rejected)
- [ ] Pole: expected_close_date, probability
- [ ] ForeignKey: client (nullable)
- [ ] ForeignKey: converted_project (nullable, OneToOne)
- [ ] Timestamps

### 10. Vytvoř model Project
- [ ] Pole: name, description, price, hourly_rate
- [ ] Pole: estimated_hours, deadline
- [ ] Pole: technologies (JSONField), tags (JSONField)
- [ ] Pole: status (CharField s choices: new/in_progress/waiting_client/done/cancelled/invoiced/paid)
- [ ] Pole: notes, checklist (JSONField)
- [ ] ForeignKey: client
- [ ] ForeignKey: lead_source (nullable)
- [ ] Property: `actual_hours()` → suma time entries
- [ ] Timestamps

### 11. Vytvoř model TimeEntry
- [ ] Pole: start (DateTime), end (DateTime, nullable)
- [ ] Pole: description, billable (Boolean), rate
- [ ] ForeignKey: project
- [ ] Property: `duration()` → end - start v minutách
- [ ] Timestamps

### 12. Vytvoř model Activity
- [ ] Pole: type (CharField: note/email/call/meeting/status_change)
- [ ] Pole: content (TextField)
- [ ] ForeignKey: project
- [ ] Timestamp: created_at

### 13. Vytvoř model Invoice (pro později)
- [ ] Pole: number (unique), amount
- [ ] Pole: issue_date, due_date
- [ ] Pole: status (draft/sent/paid)
- [ ] Pole: pdf_url (nullable)
- [ ] ForeignKey: project
- [ ] Timestamps

### 14. Migrations
bash python manage.py makemigrations python manage.py migrate
---

## 📋 FÁZE 2: DJANGO ADMIN

### 15. Zaregistruj modely v admin.py
- [ ] ClientAdmin (list_display, search_fields, list_filter)
- [ ] LeadAdmin (list_display, list_filter podle status/priority)
- [ ] ProjectAdmin (list_display, list_filter podle status/client)
- [ ] TimeEntryAdmin (list_display, list_filter podle project)
- [ ] ActivityAdmin (list_display, list_filter podle type)

### 16. Vytvoř superusera
bash python manage.py createsuperuser
### 17. Otestuj admin
- [ ] Spusť server: `python manage.py runserver`
- [ ] Jdi na http://localhost:8000/admin
- [ ] Přidej testovacího klienta, projekt, time entry

---

## 📋 FÁZE 3: SERIALIZERS (DRF)

### 18. Vytvoř serializers.py v core/
- [ ] ClientSerializer (ModelSerializer)
  - [ ] Přidej `total_earnings` jako SerializerMethodField
  - [ ] Přidaj `projects_count` jako SerializerMethodField

### 19. LeadSerializer
- [ ] Všechna pole
- [ ] Nested client (read-only)
- [ ] Validace: priority musí být low/medium/high

### 20. ProjectSerializer
- [ ] Všechna pole
- [ ] Nested client (read-only nebo jen client_id)
- [ ] Přidej `actual_hours` jako SerializerMethodField
- [ ] Nested timeEntries (nested serializer, read-only)

### 21. TimeEntrySerializer
- [ ] Všechna pole
- [ ] Přidej `duration` jako SerializerMethodField
- [ ] Validace: end > start (pokud end není null)

### 22. ActivitySerializer
- [ ] Všechna pole
- [ ] Read-only project info

### 23. Vytvoř zkrácené serializers (pro listy)
- [ ] ClientListSerializer (jen id, name, email, projects_count)
- [ ] ProjectListSerializer (jen základní info)

---

## 📋 FÁZE 4: VIEWS & VIEWSETS

### 24. Vytvoř views.py v core/
- [ ] ClientViewSet (ModelViewSet)
  - [ ] queryset, serializer_class
  - [ ] filterset_fields (vyhledávání)
  - [ ] ordering_fields
  - [ ] Custom action: `@action` → get_projects (vrať projekty klienta)

### 25. LeadViewSet
- [ ] CRUD operace
- [ ] Filter podle status, priority
- [ ] Custom action: `convert_to_project`
  - [ ] Vytvoř Project z Leadu
  - [ ] Nastav lead.converted_project
  - [ ] Nastav lead.status = 'converted'

### 26. ProjectViewSet
- [ ] CRUD operace
- [ ] Filter podle status, client, deadline (po/před)
- [ ] Search podle názvu
- [ ] Custom action: `get_time_entries`
- [ ] Custom action: `get_activities`

### 27. TimeEntryViewSet
- [ ] CRUD operace
- [ ] Filter podle project, date range
- [ ] Custom action: `stop_timer` (nastav end = now)
- [ ] Custom action: `get_running` (vrať běžící timer)

### 28. ActivityViewSet
- [ ] CRUD operace (create, list, delete)
- [ ] Filter podle project, type

### 29. DashboardView (APIView)
- [ ] Endpoint: `/api/dashboard/stats/`
- [ ] Vrať JSON s:
  - [ ] active_projects_count
  - [ ] earnings_this_month
  - [ ] hours_this_week
  - [ ] hours_this_month
  - [ ] overdue_projects_count
  - [ ] pipeline_value (suma leadů ve stavu 'deal')

### 30. DashboardChartsView (APIView)
- [ ] Endpoint: `/api/dashboard/charts/`
- [ ] Vrať data pro grafy (earnings over time, projects by status)

---

## 📋 FÁZE 5: URLS & ROUTING

### 31. Vytvoř urls.py v core/
python from rest_framework.routers import DefaultRouter router = DefaultRouter() router.register('clients', ClientViewSet) router.register('leads', LeadViewSet) router.register('projects', ProjectViewSet) router.register('time-entries', TimeEntryViewSet) router.register('activities', ActivityViewSet)
### 32. Zahrň do hlavního urls.py
python path('api/', include('core.urls')), path('api/dashboard/', DashboardView.as_view()),
---

## 📋 FÁZE 6: AUTHENTICATION

### 33. Nastav JWT auth
- [ ] V settings.py přidej SimpleJWT config
- [ ] Vytvoř endpoint `/api/auth/login/` (TokenObtainPairView)
- [ ] Vytvoř endpoint `/api/auth/refresh/` (TokenRefreshView)
- [ ] (Nebo použij vlastní login view s custom response)

### 34. Vytvoř AuthViewSet nebo custom views
- [ ] Login endpoint (vrať JWT + user info)
- [ ] Me endpoint (vrať current user)
- [ ] (Single-user v1: žádný signup)

### 35. Nastav permissions
- [ ] Všechny viewsety: `permission_classes = [IsAuthenticated]`
- [ ] (V1: Single user, takže stačí IsAuthenticated)

---

## 📋 FÁZE 7: FRONTEND SETUP

### 36. Vytvoř React aplikaci
bash npm create vite@latest frontend -- --template react-ts cd frontend npm install
### 37. Nainstaluj dependencies
bash npm install axios react-router-dom @tanstack/react-query zustand react-hook-form zod @hookform/resolvers date-fns react-hot-toast
### 38. Nainstaluj Tailwind CSS
bash npm install -D tailwindcss postcss autoprefixer npx tailwindcss init -p
### 39. Nainstaluj shadcn/ui
bash npx shadcn-ui@latest init npx shadcn-ui@latest add button input label card table
### 40. Vytvoř strukturu složek
src/ ├── components/ │ ├── ui/ (shadcn komponenty) │ ├── layout/ │ ├── clients/ │ ├── leads/ │ ├── projects/ │ ├── time-tracking/ │ └── dashboard/ ├── pages/ ├── hooks/ ├── lib/ │ ├── api.ts (axios instance) │ └── utils.ts ├── types/ └── App.tsx
---

## 📋 FÁZE 8: FRONTEND - AUTH

### 41. Vytvoř API client (lib/api.ts)
- [ ] Axios instance s baseURL
- [ ] Request interceptor (přidej JWT token do headers)
- [ ] Response interceptor (handle 401 → redirect na login)

### 42. Vytvoř auth store (Zustand)
- [ ] State: user, token, isAuthenticated
- [ ] Actions: login(), logout(), setUser()
- [ ] Persist token do localStorage

### 43. Vytvoř Login page
- [ ] Formulář: email + password
- [ ] React Hook Form + Zod validace
- [ ] Po úspěšném loginu → redirect na dashboard
- [ ] Toast notifikace (success/error)

### 44. Vytvoř ProtectedRoute component
- [ ] Zkontroluj jestli je user authenticated
- [ ] Pokud ne → redirect na /login

### 45. Setup React Router
tsx <Routes> <Route path="/login" element={<Login />} /> <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}> <Route index element={<Dashboard />} /> <Route path="clients" element={<Clients />} /> <Route path="leads" element={<Leads />} /> <Route path="projects" element={<Projects />} /> <Route path="time" element={<TimeTracking />} /> </Route> </Routes>
---

## 📋 FÁZE 9: FRONTEND - LAYOUT

### 46. Vytvoř Layout component
- [ ] Sidebar s navigací
- [ ] Header (běžící timer, user menu)
- [ ] Main content area (Outlet)

### 47. Vytvoř Sidebar component
- [ ] Navigační menu:
  - Dashboard
  - Klienti
  - Poptávky
  - Projekty
  - Time Tracking
- [ ] Active state (highlight aktuální stránky)

### 48. Vytvoř Header component
- [ ] Logo
- [ ] Běžící timer (pokud aktivní)
- [ ] User dropdown menu (logout)

---

## 📋 FÁZE 10: FRONTEND - CLIENTS

### 49. Vytvoř types (types/index.ts)
typescript export interface Client { id: number name: string company?: string email?: string phone?: string notes?: string total_earnings: number projects_count: number created_at: string updated_at: string }
### 50. Vytvoř useClients hook
- [ ] React Query: useQuery pro fetch clients
- [ ] Mutations: create, update, delete

### 51. Vytvoř Clients page
- [ ] Table s klienty (shadcn/ui Table)
- [ ] Columns: Jméno, Firma, Email, Projekty, Výdělek
- [ ] Search bar (filtrování)
- [ ] Tlačítko "Přidat klienta"

### 52. Vytvoř ClientForm component (modal)
- [ ] React Hook Form + Zod validace
- [ ] Pole: name, company, email, phone, notes
- [ ] Mode: create / edit
- [ ] Submit → API call → refetch clients → close modal

### 53. Vytvoř ClientDetail page
- [ ] Detail info klienta
- [ ] Seznam projektů klienta
- [ ] Edit/Delete tlačítka
- [ ] Statistiky (celkový výdělek, počet projektů)

---

## 📋 FÁZE 11: FRONTEND - LEADS

### 54. Vytvoř types pro Lead
typescript export interface Lead { id: number name: string description?: string estimated_budget?: number technologies: string[] priority: 'low' | 'medium' | 'high' source?: string status: 'new' | 'contacted' | 'deal' | 'rejected' expected_close_date?: string probability?: number client?: Client created_at: string }
### 55. Vytvoř useLeads hook
- [ ] useQuery pro fetch leads
- [ ] Mutations: create, update, delete, convert

### 56. Vytvoř Leads page
- [ ] Kanban board (podle status) nebo Table
- [ ] Filter podle status, priority
- [ ] Tlačítko "Přidat poptávku"

### 57. Vytvoř LeadForm component
- [ ] Formulář s všemi poli
- [ ] Multi-select pro technologies (nebo input s tagy)
- [ ] Select pro priority, source
- [ ] DatePicker pro expected_close_date

### 58. Vytvoř LeadDetail page
- [ ] Detail info
- [ ] Tlačítko "Konvertovat na projekt"
- [ ] Při kliknutí → API call `/leads/:id/convert_to_project/`
- [ ] Redirect na nově vytvořený projekt

---

## 📋 FÁZE 12: FRONTEND - PROJECTS

### 59. Vytvoř types pro Project
typescript export interface Project { id: number name: string description?: string client: Client technologies: string[] tags: string[] price?: number hourly_rate?: number estimated_hours?: number actual_hours: number deadline?: string status: 'new' | 'in_progress' | 'waiting_client' | 'done' | 'cancelled' | 'invoiced' | 'paid' notes?: string checklist?: any created_at: string updated_at: string }
### 60. Vytvoř useProjects hook
- [ ] useQuery (s filtry: status, client)
- [ ] Mutations

### 61. Vytvoř Projects page
- [ ] Table nebo Grid view
- [ ] Columns: Název, Klient, Status, Deadline, Hodiny, Cena
- [ ] Color-coded status badges
- [ ] Filter podle status, klienta
- [ ] Search podle názvu
- [ ] Alert pro overdue projekty (červená)

### 62. Vytvoř ProjectForm component
- [ ] Všechna pole
- [ ] Select pro klienta
- [ ] Multi-select pro technologies, tags
- [ ] DatePicker pro deadline
- [ ] Select pro status

### 63. Vytvoř ProjectDetail page
- [ ] Detail info
- [ ] Tabs:
  - Overview (info + checklist)
  - Time Entries (tabulka časů)
  - Activity Log (timeline)
- [ ] Edit/Delete tlačítka
- [ ] Progress bar (actual_hours / estimated_hours)

### 64. Implementuj checklist (TODO list)
- [ ] Checkbox komponenta
- [ ] Přidání nového TODO
- [ ] Mark as done
- [ ] Uložení jako JSON do project.checklist

---

## 📋 FÁZE 13: FRONTEND - TIME TRACKING

### 65. Vytvoř types pro TimeEntry
typescript export interface TimeEntry { id: number project: Project start: string end?: string duration?: number // v minutách description?: string billable: boolean rate?: number created_at: string }
### 66. Vytvoř useTimeEntries hook
- [ ] useQuery (filter podle project, date range)
- [ ] Mutations: create, update, delete, stop

### 67. Vytvoř useTimer hook (pro běžící timer)
- [ ] Zustand store: runningEntry, elapsedTime
- [ ] Funkce: startTimer(), stopTimer()
- [ ] useEffect: každou sekundu zvyšuj elapsedTime

### 68. Vytvoř Timer component (v Header nebo sticky)
- [ ] Zobraz běžící timer (pokud existuje)
- [ ] Format: "Projekt XYZ - 01:23:45"
- [ ] Tlačítko Stop
- [ ] Kliknutím na timer → otevři modal s detaily

### 69. Vytvoř TimeTracking page
- [ ] Velké tlačítko "Start Timer"
- [ ] Modal: vyber projekt, popis
- [ ] Tabulka všech time entries
- [ ] Columns: Projekt, Start, End, Duration, Billable, Rate, Výdělek
- [ ] Filter podle projektu, date range
- [ ] Možnost manuálně přidat time entry

### 70. Vytvoř TimeEntryForm component
- [ ] Select projekt
- [ ] DateTimePicker pro start, end
- [ ] Input popis
- [ ] Checkbox billable
- [ ] Input rate

---

## 📋 FÁZE 14: FRONTEND - ACTIVITY LOG

### 71. Vytvoř types pro Activity
typescript export interface Activity { id: number project: Project type: 'note' | 'email' | 'call' | 'meeting' | 'status_change' content: string created_at: string }
### 72. Vytvoř useActivities hook
- [ ] useQuery (filter podle project)
- [ ] Mutations: create, delete

### 73. Vytvoř ActivityLog component (pro ProjectDetail)
- [ ] Timeline layout
- [ ] Icons podle type (note: 📝, email: ✉️, call: 📞, meeting: 🤝)
- [ ] Timestamp formatting (date-fns)

### 74. Vytvoř ActivityForm component
- [ ] Select type
- [ ] Textarea content
- [ ] Submit → vytvoř aktivitu → refetch

---

## 📋 FÁZE 15: FRONTEND - DASHBOARD

### 75. Vytvoř useDashboard hook
- [ ] useQuery → fetch `/api/dashboard/stats/`
- [ ] useQuery → fetch `/api/dashboard/charts/`

### 76. Vytvoř Dashboard page - Stats Cards
- [ ] Card: Aktivní projekty (count + link)
- [ ] Card: Výdělek tento měsíc (Kč)
- [ ] Card: Hodiny tento týden
- [ ] Card: Hodiny tento měsíc
- [ ] Card: Projekty po deadline (červená, alert)
- [ ] Card: Pipeline value (suma leadů)

### 77. Vytvoř grafy (Recharts)
- [ ] Nainstaluj: `npm install recharts`
- [ ] Line chart: Výdělek v čase (měsíčně)
- [ ] Pie chart: Rozdělení času podle projektů
- [ ] Bar chart: Projekty podle stavu

### 78. Vytvoř Recent Activities widget
- [ ] Posledních 10 aktivit
- [ ] Link na detail projektu

### 79. Vytvoř Quick Actions
- [ ] Tlačítko "Start timer" (otevře modal)
- [ ] Tlačítko "Přidat klienta"
- [ ] Tlačítko "Přidat poptávku"

---

## 📋 FÁZE 16: POLISH & UX

### 80. Loading states
- [ ] Skeleton loaders pro tabulky
- [ ] Spinner pro tlačítka při submitu
- [ ] Page-level loader (při přepínání stránek)

### 81. Empty states
- [ ] Žádní klienti → friendly message + CTA "Přidat prvního klienta"
- [ ] Žádné projekty
- [ ] Žádný běžící timer

### 82. Error handling
- [ ] Try-catch v API calls
- [ ] Toast chybové hlášky (user-friendly)
- [ ] 404 stránka
- [ ] 500 error fallback

### 83. Validace formulářů
- [ ] Real-time validace (Zod + React Hook Form)
- [ ] Error messages pod fieldy

### 84. Optimistic updates
- [ ] Při create → okamžitě přidej do UI (před API response)
- [ ] Při delete → okamžitě odeber z UI

### 85. Keyboard shortcuts (volitelné)
- [ ] Cmd/Ctrl + K → global search
- [ ] Cmd/Ctrl + N → nový klient/projekt (podle stránky)

### 86. Responzivita
- [ ] Desktop priorita
- [ ] Mobile: skryj sidebar → hamburger menu

---

## 📋 FÁZE 17: BACKEND - BUSINESS LOGIKA

### 87. Auto-calculations
- [ ] Client.total_earnings: signal při Project.save() (pokud status=paid)
- [ ] Project.actual_hours: property method sumující TimeEntry
- [ ] TimeEntry.duration: property method (end - start)

### 88. Validace v modelech/serializerech
- [ ] Lead.priority musí být low/medium/high
- [ ] TimeEntry: end > start (pokud end není null)
- [ ] Nelze spustit timer pokud už nějaký běží (check v create)

### 89. Convert Lead → Project logika
- [ ] V LeadViewSet custom action
- [ ] Vytvoř Project z Leadu (zkopíruj data)
- [ ] Nastav lead.converted_project
- [ ] Nastav lead.status (nebo přidej status 'converted')
- [ ] Return created project

### 90. Dashboard calculations
- [ ] Earnings this month: filtr Project (status=paid, created_at tento měsíc)
- [ ] Hours this week: filtr TimeEntry (start tento týden), suma duration
- [ ] Overdue projects: filtr Project (deadline < today, status != done)
- [ ] Pipeline value: filtr Lead (status=deal), suma estimated_budget

---

## 📋 FÁZE 18: TESTING & BUGFIXES

### 91. Backend testy (pytest-django)
- [ ] Nainstaluj: `pip install pytest pytest-django`
- [ ] Testuj models (vytvoření, validace)
- [ ] Testuj API endpoints (CRUD)
- [ ] Testuj business logiku (convert lead)

### 92. Frontend testy (volitelné v MVP)
- [ ] Vitest + React Testing Library
- [ ] Testuj kritické komponenty (ClientForm, ProjectForm)

### 93. Manual testing checklist
- [ ] Přidání klienta → zobrazí se v listu
- [ ] Vytvoření projektu → vidím v listu
- [ ] Start timer → běží v headeru → stop → zobrazí se v time entries
- [ ] Konverze leadu → vytvoří projekt
- [ ] Dashboard stats → správná čísla
- [ ] Overdue projekty → červená hláška
- [ ] Edit/delete funguje všude

### 94. Oprav bugy
- [ ] CORS issues
- [ ] Timezone issues (UTC vs local)
- [ ] Null handling (optional fields)
- [ ] 404 při refresh stránky (React Router config)

---

## 📋 FÁZE 19: DEPLOYMENT PREP

### 95. Environment variables
- [ ] Backend: `.env.example` (template)
- [ ] Frontend: `.env.example`
- [ ] Dokumentuj všechny env vars v README

### 96. Django production settings
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS = [...]`
- [ ] `SECRET_KEY` z env
- [ ] Static files setup (`STATIC_ROOT`, `collectstatic`)

### 97. Docker setup (volitelné)
- [ ] `Dockerfile` pro backend
- [ ] `docker-compose.yml` (backend + postgres)
- [ ] Frontend: Dockerfile (nginx + build)

### 98. README.md
- [ ] Popis projektu
- [ ] Tech stack
- [ ] Prerequisites (Python, Node, Postgres)
- [ ] Installation steps
- [ ] Development commands
- [ ] API dokumentace (nebo link na DRF browsable API)

---

## 📋 FÁZE 20: DEPLOYMENT

### 99. Database
- [ ] Railway PostgreSQL nebo Supabase
- [ ] Spusť migrations v produkci

### 100. Backend deployment
- [ ] Railway / Render / DigitalOcean
- [ ] Nastav env variables
- [ ] `python manage.py collectstatic`
- [ ] Gunicorn jako WSGI server

### 101. Frontend deployment
- [ ] Build: `npm run build`
- [ ] Deploy na Vercel / Netlify
- [ ] Nastav `VITE_API_URL` na production backend URL
- [ ] Nastav redirects pro React Router

### 102. CORS v production
- [ ] Django: `CORS_ALLOWED_ORIGINS = ['https://frontend-url.com']`

### 103. SSL/HTTPS
- [ ] Backend: Railway/Render automaticky
- [ ] Frontend: Vercel/Netlify automaticky

---

## 📋 FÁZE 21: POST-LAUNCH

### 104. Monitoring
- [ ] Django logging (errors do souboru nebo Sentry)
- [ ] Sleduj API performance (slow queries)

### 105. Backup
- [ ] PostgreSQL backup strategy
- [ ] Nightly backups (Railway má auto backups)

### 106. User feedback
- [ ] Používej aplikaci sám 1-2 týdny
- [ ] Zapiš si co chybí / co vadí
- [ ] Prioritizuj improvements

### 107. Fáze 2 planning
- [ ] Faktury (PDF generation)
- [ ] Export dat (CSV)
- [ ] Tagy & filtry
- [ ] Notifikace
- [ ] Dark mode

---

## 🎯 QUICK START CHECKLIST (První den)

**Dnes udělej:**
- [ ] ✅ Bod 1-6: Setup prostředí + Django projekt
- [ ] ✅ Bod 7-14: Databázové modely + migrations
- [ ] ✅ Bod 15-17: Django admin + testovací data
- [ ] ✅ Bod 18-23: Serializers

**Zítra udělej:**
- [ ] Bod 24-30: Views & ViewSets
- [ ] Bod 31-32: URLs
- [ ] Otestuj API v Postman/Insomnia nebo DRF browsable API

**Pozítří:**
- [ ] Bod 33-35: Auth (JWT)
- [ ] Bod 36-40: Frontend setup
- [ ] Bod 41-45: Frontend auth

**A pak postupně podle plánu!** 🚀

---

## 📝 POZNÁMKY

### Django specifika:
- **Použij Django REST Framework browsable API** (máš dokumentaci zdarma!)
- **Django admin** = instant CRUD UI (používej pro testování)
- **Signals** pro auto-calculations (post_save na Project → update Client.total_earnings)
- **Django ORM** = jednodušší než Prisma, ale méně type-safe
- **JSONField** pro technologies, tags, checklist (Postgres support)

### Tipy:
- Nejdřív **backend (API)**, pak **frontend** → testuj průběžně v Postman
- **DRF browsable API** je tvůj kamarád → jdi na http://localhost:8000/api/
- Django admin je **mega rychlý** na prototypování
- Nedělej premature optimization → nejdřív udělej funkční MVP

### Časový odhad:
- **Týden 1:** Setup + modely + admin + API (body 1-35)
- **Týden 2:** Frontend setup + auth + clients + leads (body 36-58)
- **Týden 3:** Projects + time tracking (body 59-74)
- **Týden 4:** Dashboard + polish + deploy (body 75-103)

---

# 🚀 TEĎ ZAČNI S BODEM 1!
**Tohle je tvůj action plan.** Postupuj bod po bodu a máš hotovo. Django bude rychlejší než NestJS protože: - Django admin = instant UI - DRF = méně boilerplate - Python znáš = rychlejší development