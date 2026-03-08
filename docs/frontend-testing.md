# FreelanceOS Frontend Testing Guide

## ✅ Quick Start

### 1. Start the Server
```powershell
cd c:\Users\frank\Desktop\freelanceos
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Access the Application
- **Login**: http://localhost:8000/accounts/login/
- **Dashboard**: http://localhost:8000/accounts/dashboard/
- **Clients**: http://localhost:8000/accounts/clients/
- **Projects**: http://localhost:8000/accounts/projects/

**Test credentials**: test@example.com / any password (from seed data)

---

## 🧪 Testing Workflow

### A. Login & Dashboard

1. ✅ Navigate to `http://localhost:8000/accounts/login/`
2. ✅ Enter email: `test@example.com`
3. ✅ Enter password: (any text)
4. ✅ Click "Přihlásit se" (Sign in)
5. ✅ Should redirect to Dashboard
6. ✅ See email in top-right corner
7. ✅ See 4 stat cards:
   - Aktivní projekty: ✓ (should show a number)
   - Klienti: ✓ (should show 1+ from seed data)
   - Všechny projekty: ✓ (should show 3+ from seed data)
   - Po termínu: ✓ (should show 0+)

---

### B. Clients Page - Full CRUD

#### **READ: View Clients**
1. ✅ Click "Klienti" in navbar
2. ✅ Table loads with existing clients
3. ✅ See "Acme Corporation" and other seeded clients
4. ✅ Table shows: Název | Email | Projektů | Vytvořeno | Akce

#### **SEARCH: Find Client**
1. ✅ Type "acme" in search box
2. ✅ Table filters in real-time
3. ✅ Clear search - all clients return

#### **CREATE: Add New Client**
1. ✅ Click "+ Přidat klienta" button
2. ✅ Modal opens with form:
   - Jméno (required)
   - Email (required)
   - Společnost (optional)
   - Telefon (optional)
   - Poznámky (optional)
3. ✅ Fill form:
   - Name: "Test Client XYZ"
   - Email: "test-client@example.com"
   - Company: "Test Company Ltd"
   - Phone: "+420 123 456 789"
   - Notes: "Test notes"
4. ✅ Click "Uložit" (Save)
5. ✅ Success message appears: "Klient přidán"
6. ✅ Modal closes
7. ✅ New client appears in table
8. ✅ Can search for newly created client

#### **UPDATE: Edit Client**
1. ✅ Click "Upravit" button on any client row
2. ✅ Modal opens with client's current data
3. ✅ Modal title changes to "Upravit klienta"
4. ✅ Form is pre-filled with client data
5. ✅ Change company name to "New Company Name"
6. ✅ Click "Uložit"
7. ✅ Success message: "Klient upraven"
8. ✅ Table updates with new company name

#### **DELETE: Remove Client**
1. ✅ Click "Smazat" button on any client
2. ✅ Confirmation dialog appears
3. ✅ Click OK to confirm
4. ✅ Success message: "Klient smazán"
5. ✅ Client row disappears from table
6. ✅ Client's projects are also deleted (cascade)

#### **Error Handling**
1. ✅ Try adding client without email
   - Form validation shows error below email field
2. ✅ Try adding client with duplicate email (if you have one)
   - Error message appears: "Email already exists"
3. ✅ Network error test:
   - Open DevTools (F12) → Network tab → Offline
   - Try to add client
   - Error toast appears

---

### C. Projects Page - Full CRUD + Filters

#### **READ: View Projects**
1. ✅ Click "Projekty" in navbar
2. ✅ Table loads with existing projects
3. ✅ See "Website Redesign" and "Mobile App Development" from seed data
4. ✅ Table shows: Název | Klient | Status | Deadline | Rozpočet | Akce
5. ✅ Status badges show colored badges (green=active, gray=draft, etc)
6. ✅ Overdue projects highlighted in red background

#### **FILTER: Projects by Status**
1. ✅ See dropdown "Všechny statusy" (top right, second dropdown)
2. ✅ Select "Aktivní" (Active)
3. ✅ Table shows only active projects
4. ✅ Select "Hotovo" (Completed)
5. ✅ Table shows only completed projects
6. ✅ Select "Všechny statusy" - shows all again

#### **FILTER: Projects by Client**
1. ✅ See dropdown "Všichni klienti" (top right, third dropdown)
2. ✅ Select "Acme Corporation"
3. ✅ Table shows only Acme's projects
4. ✅ Select "Všichni klienti" - shows all clients' projects again

#### **SEARCH: Find Project**
1. ✅ Type "website" in search box
2. ✅ Table filters to "Website Redesign"
3. ✅ Clear search or type "xyz" - no results
4. ✅ Empty state shows: "Žádné projekty" with button

#### **CREATE: Add New Project**
1. ✅ Click "+ Nový projekt" button
2. ✅ Modal opens with form:
   - Název (required)
   - Klient (required, dropdown populated from clients)
   - Popis (optional)
   - Status (select, default=active)
   - Rozpočet (number, in CZK)
   - Odhadnuté hodiny (number)
   - Datum začátku (optional date)
   - Deadline (optional date)
3. ✅ Fill form:
   - Name: "API Integration"
   - Client: Select "Acme Corporation" (or first client)
   - Status: "active"
   - Budget: "15000"
   - Hours: "50"
   - Start date: 2026-03-10
   - End date: 2026-04-10
4. ✅ Click "Uložit"
5. ✅ Success message: "Projekt vytvořen"
6. ✅ Modal closes
7. ✅ New project appears in table
8. ✅ Can filter/search for the new project

#### **UPDATE: Edit Project**
1. ✅ Click "Upravit" on any project
2. ✅ Modal opens with "Upravit projekt" title
3. ✅ Form is pre-filled
4. ✅ Change status to "completed"
5. ✅ Change budget to "20000"
6. ✅ Click "Uložit"
7. ✅ Success: "Projekt upraven"
8. ✅ Table updates with new values

#### **DELETE: Remove Project**
1. ✅ Click "Smazat" on any project
2. ✅ Confirmation dialog: "Opravdu chcete smazat projekt XYZ?"
3. ✅ Click OK
4. ✅ Success: "Projekt smazán"
5. ✅ Project disappears from table

#### **Overdue Highlighting**
1. ✅ Create a project with deadline = 2026-03-01 (past date)
2. ✅ Set status to "active"
3. ✅ Save
4. ✅ Table row should have red background
5. ✅ Should show warning: "⚠ Po termínu"
6. ✅ Days until deadline shows negative number

---

### D. Navigation & Auth

#### **Navigation Bar**
1. ✅ Navbar visible on all pages (Dashboard, Clients, Projects)
2. ✅ Current page shows underline on nav link
3. ✅ Click Dashboard link - redirects to dashboard
4. ✅ Click Clients link - redirects to clients
5. ✅ Click Projects link - redirects to projects
6. ✅ Email shown in top-right corner

#### **Logout**
1. ✅ Click "Odhlásit se" (Logout) button
2. ✅ Redirects to login page
3. ✅ localStorage tokens are cleared
4. ✅ Try accessing /accounts/dashboard/ while logged out
5. ✅ Auto-redirects to login

#### **Token Refresh**
1. ✅ Open DevTools (F12) → Application → Local Storage
2. ✅ See `access_token` and `refresh_token` stored
3. ✅ Delete `access_token` manually
4. ✅ Try to add a client
5. ✅ Should auto-refresh token and complete action
6. ✅ New `access_token` in localStorage

---

### E. UI & Responsiveness

#### **Modals**
1. ✅ Click outside modal → modal closes
2. ✅ Click X button in modal → modal closes
3. ✅ Click "Zrušit" → modal closes
4. ✅ Modal content centered on screen
5. ✅ Modal content has nice animation (slides in)

#### **Alerts/Toasts**
1. ✅ Successful action shows green toast in top-right
2. ✅ Error shows red toast in top-right
3. ✅ Toast auto-disappears after 4 seconds
4. ✅ Can have multiple toasts visible

#### **Forms**
1. ✅ Required fields show asterisk (*)
2. ✅ Submit button says "Uložit" on save
3. ✅ Submit button gets disabled while saving (grayed out)
4. ✅ Text in button changes to "…" (loading indicator)
5. ✅ Form inputs are disabled while saving
6. ✅ Form clears after successful save (on add form)

#### **Tables**
1. ✅ Table rows highlight on hover (subtle)
2. ✅ Action buttons have hover effects
3. ✅ Delete buttons are red on hover
4. ✅ Text is selectable (can copy email, names)

#### **Empty States**
1. ✅ When no clients exist, show empty state with icon and button
2. ✅ When no projects exist, show empty state with icon and button
3. ✅ Empty state button works same as "+" button

---

## 🐛 Troubleshooting

### Issue: Pages show "Načítám..." forever
**Solution**: Check browser console (F12 → Console)
- If you see CORS error: Check that API endpoints are accessible
- If you see JWT error: Clear localStorage and login again

### Issue: Login page not loading
**Solution**:
1. Check Django server is running
2. Run `python manage.py check`
3. Check for template errors in server output

### Issue: Create/Edit form doesn't work
**Solution**:
1. Open DevTools (F12)
2. Go to Network tab
3. Submit form
4. Check API request
5. If 400/401: Check response message
6. If 500: Check Django server logs

### Issue: Logout not working
**Solution**: Clear localStorage manually:
```javascript
// Run in console
localStorage.clear()
window.location.href = '/accounts/login/'
```

---

## 📝 Example Test Data

To test, you can use:
- **Existing client**: Acme Corporation (acme@example.com)
- **Existing projects**: Website Redesign, Mobile App Development

Or create your own:
1. Name: "New Client", Email: "new@example.com"
2. Project: "Test Project", Budget: "5000", Hours: "20"

---

## ✨ Success Criteria Checklist

- [ ] All pages load without errors
- [ ] Can add client via modal form
- [ ] Can edit client details
- [ ] Can delete client (with confirmation)
- [ ] Client search works real-time
- [ ] Can add project via modal form
- [ ] Can edit project details
- [ ] Can delete project (with confirmation)
- [ ] Project filters work (status, client)
- [ ] Project search works real-time
- [ ] Navigation bar works on all pages
- [ ] Logout works properly
- [ ] Modals close with X button and background click
- [ ] Toast notifications appear
- [ ] Overdue projects highlighted
- [ ] Responsive design (try different window sizes)
- [ ] Dark theme applied throughout

---

## 🚀 What's Working

✅ **Backend**: Django API (DRF)
✅ **Frontend**: React-free, vanilla JS
✅ **Auth**: JWT tokens with auto-refresh
✅ **CRUD**: Clients & Projects
✅ **Filtering**: Status, Client, Search
✅ **Modals**: Add, Edit forms
✅ **UI**: Dark theme, minimal, functional
✅ **Database**: SQLite (dev), Django ORM

---

## Next Steps (Optional Features)

Once you confirm everything works:
1. Add project details page (click project name to see full details)
2. Add client details page with all their projects
3. Add time tracking (capture hours worked)
4. Add project analytics (budget vs actual hours)
5. Add export to CSV
6. Add project templates
7. Add invoice generation

---

**You now have a fully functional freelancer dashboard! 🎉**
