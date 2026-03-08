# FreelanceOS Frontend - Quick Reference

## 📂 File Structure

```
freelanceos/
├── templates/
│   ├── base.html                    ← Enhanced with navbar, CSS, JS imports
│   ├── auth/
│   │   ├── login.html              (unchanged)
│   │   ├── register.html           (unchanged)
│   │   └── dashboard.html          ← Updated with navbar, stats
│   └── dashboard/                  ← NEW folder
│       ├── clients.html            ← Clients list & CRUD modal
│       └── projects.html           ← Projects list & CRUD modal
│
├── static/js/                       ← NEW folder
│   ├── api.js                       ← API client (HTTP + JWT auth)
│   ├── app.js                       ← UI utilities (modal, alerts, forms)
│   ├── clients.js                   ← Clients CRUD logic
│   └── projects.js                  ← Projects CRUD logic
│
├── users/
│   ├── template_urls.py             ← Updated: added /accounts/clients/, /accounts/projects/
│   ├── template_views.py            ← Updated: added clients_page(), projects_page()
│   └── ... (unchanged)
│
├── clients/                         (unchanged, API endpoints)
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py
│   └── urls.py
│
├── projects/                        (unchanged, API endpoints)
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py
│   └── urls.py
│
├── core/                            (unchanged)
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── FRONTEND_TESTING_GUIDE.md        ← NEW: Testing checklist & walkthrough
├── IMPLEMENTATION_COMPLETE.md       ← NEW: Full architecture documentation
├── manage.py
├── requirements-dev.txt
└── ...
```

---

## 🔍 What Each File Does

### Templates

#### `base.html`
**Purpose**: Base template inherited by all pages
**What's New**:
- Navigation bar with links (Dashboard | Clients | Projects)
- Enhanced CSS with:
  - Navbar styles
  - Table styles
  - Modal styles
  - Form styles
  - Status badges
  - Empty states
- JavaScript imports:
  - `<script src="/static/js/api.js"></script>`
  - `<script src="/static/js/app.js"></script>`

#### `auth/dashboard.html`
**Purpose**: Dashboard homepage (after login)
**Updated**:
- Added navbar (same as other pages)
- Added JavaScript to load stats:
  - Active projects count
  - Total clients
  - Total projects
  - Overdue projects
- Links to client/project pages

#### `dashboard/clients.html` (NEW)
**Purpose**: Client management page
**Contains**:
- Navbar
- Page title + "Add Client" button
- Search input
- Clients table (name, email, projects count, created date, actions)
- Empty state (when no clients)
- Modal form (add/edit client)
- Import: `<script src="/static/js/clients.js"></script>`

#### `dashboard/projects.html` (NEW)
**Purpose**: Project management page
**Contains**:
- Navbar
- Page title + "New Project" button
- Search input
- Status filter dropdown
- Client filter dropdown
- Projects table (name, client, status badge, deadline, budget, actions)
- Empty state (when no projects)
- Modal form (add/edit project)
- Import: `<script src="/static/js/projects.js"></script>`

---

### JavaScript Files

#### `api.js`
**Purpose**: API client with JWT authentication
**Key Classes**: `APIClient`
**Main Methods**:
```javascript
api.get(endpoint)           // GET request
api.post(endpoint, body)    // POST request
api.put(endpoint, body)     // PUT request
api.delete(endpoint)        // DELETE request

api.request(endpoint, opts) // Generic request (handles auth, refresh)

api.clients.list(search)    // GET /api/clients/?search=...
api.clients.get(id)
api.clients.create(data)    // POST /api/clients/
api.clients.update(id, data) // PUT /api/clients/{id}/
api.clients.delete(id)      // DELETE /api/clients/{id}/

api.projects.list(filters)  // GET /api/projects/?status=...&client_id=...
api.projects.get(id)
api.projects.create(data)   // POST /api/projects/
api.projects.update(id, data) // PUT /api/projects/{id}/
api.projects.delete(id)     // DELETE /api/projects/{id}/
```

**Token Handling**:
- Reads tokens from localStorage
- Adds Bearer token to all requests
- Auto-refreshes token on 401
- Logs user out if refresh fails

**Error Handling**:
- Catches network errors
- Parses API error messages
- Throws descriptive errors with status codes

#### `app.js`
**Purpose**: UI utilities, modal management, form helpers
**Key Classes**: `UIManager`, `FormHelper`

**UIManager Methods**:
```javascript
UIManager.error(message)        // Show red toast
UIManager.success(message)      // Show green toast
UIManager.alert(msg, type)      // Generic alert

UIManager.modal.open(id)        // Open modal
UIManager.modal.close(id)       // Close modal
UIManager.modal.closeAll()      // Close all modals

UIManager.formatDate(dateStr)   // Format date
UIManager.formatCurrency(val)   // Format currency (CZK)
UIManager.statusBadge(status)   // Get HTML badge

UIManager.isAuthenticated()     // Check if logged in
UIManager.requireAuth()         // Redirect if not auth
UIManager.loadUser()            // Fetch user from API
UIManager.setActiveNav(pageName) // Highlight nav link
```

**FormHelper Methods**:
```javascript
FormHelper.getData(form)        // Get form values as object
FormHelper.populate(form, data) // Fill form with data
FormHelper.clear(form)          // Clear form and errors
FormHelper.showErrors(form, errs) // Show validation errors
FormHelper.setLoading(form, bool) // Disable during submit
```

**Auto-Initialization**:
- Runs on page load
- Checks authentication
- Loads current user
- Sets up modal close handlers
- Sets up navbar click handlers
- Sets up logout button

#### `clients.js`
**Purpose**: Client CRUD logic and table management
**Key Class**: `ClientsManager`
**Main Methods**:
```javascript
clientsManager.loadClients()    // Fetch all clients from API
clientsManager.renderTable()    // Render table with current clients
clientsManager.openAddModal()   // Show add client form
clientsManager.openEditModal(id) // Show edit form with data
clientsManager.handleFormSubmit() // Save client (create/update)
clientsManager.delete(id)       // Delete client with confirmation
clientsManager.getFilteredClients() // Apply search filter
```

**Data Flow**:
1. Page loads → `loadClients()` fetches from API
2. User searches → debounced search filters table
3. User clicks "+ Add" → `openAddModal()` shows form
4. User fills form → `handleFormSubmit()` POSTs to API
5. Success → `loadClients()` refreshes table

**Features**:
- Search with 300ms debounce
- Modal form for add/edit
- Edit loads existing data into form
- Delete with confirmation
- Error handling with inline form errors

#### `projects.js`
**Purpose**: Project CRUD logic, filtering, and table management
**Key Class**: `ProjectsManager`
**Main Methods**:
```javascript
projectsManager.loadClients()    // Populate client dropdown
projectsManager.loadProjects()   // Fetch all projects from API
projectsManager.applyFilters()   // Filter table by status/client/search
projectsManager.getFilteredProjects() // Apply all filters
projectsManager.renderTable()    // Render filtered table
projectsManager.openAddModal()   // Show add project form
projectsManager.openEditModal(id) // Show edit form with data
projectsManager.handleFormSubmit() // Save project
projectsManager.delete(id)       // Delete project
```

**Data Flow**:
1. Page loads → load clients + projects from API
2. Populate client dropdown from clients list
3. User filters by status/client/search → `applyFilters()` updates table
4. User clicks "+ New" → `openAddModal()` shows form
5. Form auto-selects client dropdown options
6. User fills form → `handleFormSubmit()` POSTs to API
7. Success → `loadProjects()` refreshes table

**Features**:
- Dropdown populated from clients
- Search with 300ms debounce
- Filter by status (5 options)
- Filter by client (auto-populated)
- Stacked filters work together
- Overdue highlighting (red background)
- Days until deadline calculation

---

## 🔗 API Endpoints

All endpoints require JWT authentication (`Authorization: Bearer {token}`)

### Clients
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/clients/` | List all clients (with `?search=...`) |
| POST | `/api/clients/` | Create new client |
| GET | `/api/clients/{id}/` | Get client detail |
| PUT | `/api/clients/{id}/` | Update client |
| DELETE | `/api/clients/{id}/` | Delete client |
| GET | `/api/clients/{id}/stats/` | Client statistics |

### Projects
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/projects/` | List all projects (with filters) |
| POST | `/api/projects/` | Create new project |
| GET | `/api/projects/{id}/` | Get project detail |
| PUT | `/api/projects/{id}/` | Update project |
| DELETE | `/api/projects/{id}/` | Delete project |
| GET | `/api/projects/stats/` | Projects statistics |

### Query Parameters
**Projects List**:
- `search=string` - Search project name
- `status=draft|active|completed|archived|cancelled` - Filter by status
- `client_id=123` - Filter by client
- `overdue=true` - Show only overdue

**Clients List**:
- `search=string` - Search client name/email/company

---

## 🔌 Routes (URL Mapping)

### Frontend Routes (Django Templates)
| URL | View | Template | Purpose |
|-----|------|----------|---------|
| `/accounts/login/` | `login_page` | `auth/login.html` | Login form |
| `/accounts/register/` | `register_page` | `auth/register.html` | Register form |
| `/accounts/dashboard/` | `dashboard_page` | `auth/dashboard.html` | Dashboard |
| `/accounts/clients/` | `clients_page` | `dashboard/clients.html` | Clients page |
| `/accounts/projects/` | `projects_page` | `dashboard/projects.html` | Projects page |

### Backend API Routes (DRF)
```
/api/auth/           - User authentication (login, me, token refresh)
/api/clients/        - Client CRUD endpoints
/api/projects/       - Project CRUD endpoints
```

---

## 🔄 Data Models

### Client
```javascript
{
  id: 1,
  name: "Acme Corporation",
  email: "acme@example.com",
  company: "Acme Inc.",
  phone: "+420 123 456 789",
  notes: "Important client",
  project_count: 3,
  total_earnings: 200000.00,
  created_at: "2026-03-08T13:46:55.607592Z",
  updated_at: "2026-03-08T13:46:55.607592Z"
}
```

### Project
```javascript
{
  id: 1,
  name: "Website Redesign",
  description: "Full website redesign...",
  client: 1,
  client_name: "Acme Corporation",
  status: "active",
  status_display: "Aktivní",
  budget: "50000.00",
  estimated_hours: "200.00",
  start_date: "2026-03-08",
  end_date: "2026-05-07",
  is_overdue: false,
  days_until_deadline: 60,
  progress: 0,
  actual_hours: 0,
  hourly_rate: 250.0,
  created_at: "2026-03-08T13:46:55.608594Z",
  updated_at: "2026-03-08T13:46:55.608594Z"
}
```

---

## 🎯 Common Tasks

### Add a new table column
1. Edit template (e.g., `clients.html`)
2. Add `<th>` in table header
3. Add `<td>` in table body (in renderTable or templates)
4. Make sure API returns the field

### Add a form field
1. Edit template modal form
2. Add `<input>` or `<select>` with `name="fieldname"`
3. Add to `FormHelper.populate()` for edit mode
4. Backend serializer must accept it

### Add a new filter
1. Add dropdown/input to template
2. Add event listener to update filter state
3. Call `applyFilters()` to re-render
4. Adjust `getFiltered()` method to check new filter

### Add error validation
1. Submit form without required field
2. Backend returns 400 with error
3. `FormHelper.showErrors()` displays inline
4. User fixes field and retries

---

## 💡 Key Concepts

### Modal Forms (No Page Reload)
```javascript
// Instead of form submission → page reload
// We use fetch API & modal:

1. User clicks button → UIManager.modal.open('clientModal')
2. Modal slides in with form
3. User fills form
4. Form submit event → handleFormSubmit()
5. fetch POST/PUT to API
6. Success → UIManager.modal.close() + reload table
7. Error → show inline errors
```

### Real-time Search (Debounced)
```javascript
// Without debounce: search fires on every keystroke (bad for API)
// With debounce: wait 300ms after user stops typing (better)

searchInput.addEventListener('input',
  UIManager.debounce((e) => {
    this.searchQuery = e.target.value
    this.renderTable()
  }, 300) // Wait 300ms after user stops typing
)
```

### Token Refresh (Automatic)
```javascript
// User token expires: 401 error
// What happens:
1. API returns 401
2. api.request() catches it
3. Call refreshAccessToken() with refresh_token
4. Get new access_token
5. Retry original request with new token
6. User doesn't notice anything
```

### Inline Form Errors
```javascript
// Backend returns: { email: ["Email already exists"] }
// FormHelper.showErrors() creates:
// <div class="form-error">Email already exists</div>
// Attached below the email input
// User sees error inline (no dialog box)
```

---

## 🚀 Quick Commands

### Start Development Server
```powershell
cd c:\Users\frank\Desktop\freelanceos
.\venv\Scripts\Activate.ps1
python manage.py runserver
# Then: http://localhost:8000/accounts/login/
```

### Test API (Python Script)
```powershell
python test_api.py
```

### Clear Database & Reset
```powershell
python manage.py migrate --plan
python manage.py migrate
python manage.py seed_test  # Reload test data
```

### Django Shell (Test API Manually)
```powershell
python manage.py shell
# Then:
# from clients.models import Client
# Client.objects.all()
```

---

## 📚 Learning Resources in This Project

- **JWT Authentication**: See `api.js` class
- **Modal Forms**: See `app.js` UIManager + `clients.js` modal open/close
- **Real-time Search**: See debounce in `clients.js` and `projects.js`
- **Fetch API with Error Handling**: See `api.js` request() method
- **Form Validation**: See `FormHelper` in `app.js`
- **Django Templates**: See `base.html`, `clients.html`, `projects.html`
- **Dark CSS Theme**: See `base.html` styles section
- **Component Architecture**: Modal, form, table, navbar all separate objects

---

## ✨ Next Developer Tips

1. **Keep API client in api.js**: Don't hardcode URLs elsewhere
2. **Keep UI logic in Manager classes**: One class per page
3. **Use FormHelper for all forms**: Consistent error handling
4. **Use UIManager for alerts**: Consistent toast style
5. **Test in real browser**: Use DevTools Network tab to debug
6. **Check Django logs**: See full error stack trace there
7. **Keep templates simple**: Heavy logic goes in JS
8. **Comment complex code**: Help future developers (yourself!)
9. **Test CRUD once per page**: Add, edit, delete, search
10. **Clear cache if stuck**: `localStorage.clear()` on browser console

---

**This is your reference guide. Keep it handy! 📖**
