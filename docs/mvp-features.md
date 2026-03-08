# 📋 FreelanceOS - Checklist funkcí (MVP)

> Den 1 ✅ | Den 2-9 🔄

## 🔐 Autentizace (Den 1) ✅
- [x] Login
- [x] Logout
- [x] Get current user (/api/auth/me/)
- [x] JWT token handling
- [x] Register endpoint
- [x] Change password
- [x] Token blacklist (logout)
- [x] Protected template pages (Django)

## 👥 Clients (Den 6)
- [ ] List clients
- [ ] Create client
- [ ] Update client
- [ ] Delete client
- [ ] View client detail
- [ ] Search clients
- [ ] Calculate total earnings
- [ ] Count projects

## 📁 Projects (Den 6)
- [ ] List projects
- [ ] Create project
- [ ] Update project
- [ ] Delete project
- [ ] View project detail
- [ ] Filter by status
- [ ] Filter by client
- [ ] Search by name
- [ ] Status badges (color-coded)
- [ ] Overdue detection
- [ ] Calculate actual hours
- [ ] Progress calculation

## ⏱️ Time Tracking (Den 7)
- [ ] Start timer
- [ ] Stop timer
- [ ] Display running timer (in header)
- [ ] List time entries
- [ ] Create time entry (manual)
- [ ] Delete time entry
- [ ] Filter by project
- [ ] Filter by date range
- [ ] Calculate duration
- [ ] Mark as billable

## 📝 Activities (Den 8)
- [ ] List activities
- [ ] Create activity
- [ ] Delete activity
- [ ] Activity types (note/email/call/meeting)
- [ ] Timeline view
- [ ] Filter by project

## 📊 Dashboard (Den 5)
- [ ] Active projects count
- [ ] Earnings this month
- [ ] Hours this week
- [ ] Hours this month
- [ ] Overdue projects alert
- [ ] Recent activities list

## 🎨 Frontend - Pages
- [ ] Login page
- [ ] Dashboard page
- [ ] Clients list page
- [ ] Client detail page
- [ ] Projects list page
- [ ] Project detail page (with tabs)
- [ ] Time tracking page

## 🎨 Frontend - Components

### Layout (Den 5)
- [ ] Sidebar with navigation
- [ ] Header with timer & user menu
- [ ] Main content area
- [ ] Mobile-responsive menu

### Forms
- [ ] Client form (modal)
- [ ] Project form (modal)
- [ ] Activity form
- [ ] Time entry form (modal)
- [ ] Form validation (Zod)

### UI Components
- [ ] Stats cards
- [ ] Status badges
- [ ] Timer display
- [ ] Activity timeline
- [ ] Progress bar
- [ ] Search bar
- [ ] Filter dropdowns
- [ ] Toast notifications
- [ ] Loading states
- [ ] Empty states

## 🛠️ Backend - Django
- [ ] User model
- [ ] Client model
- [ ] Project model
- [ ] TimeEntry model
- [ ] Activity model
- [ ] Admin interface
- [ ] Seed data command

## 🛠️ Backend - API
- [ ] Auth endpoints (login, me)
- [ ] Clients CRUD
- [ ] Projects CRUD
- [ ] Time entries CRUD
- [ ] Activities CRUD
- [ ] Dashboard stats endpoint
- [ ] Start/stop timer endpoints
- [ ] Filters & search
- [ ] CORS configuration

## 🛠️ Frontend - Infrastructure
- [ ] Vite setup
- [ ] React Router
- [ ] Axios instance
- [ ] Auth store (Zustand)
- [ ] Timer store (Zustand)
- [ ] React Query setup
- [ ] TypeScript interfaces
- [ ] Tailwind CSS
- [ ] shadcn/ui components

## 🚀 Deployment (Den 9)
- [ ] Backend to Railway/Render
- [ ] Frontend to Vercel/Netlify
- [ ] PostgreSQL database
- [ ] Environment variables
- [ ] Production settings
- [ ] CORS for production

## ⏳ Post-MVP (Nice to have)
- Leads/Poptávky
- Faktury (PDF)
- Grafy (charts)
- Export dat (CSV)
- Checklist v projektech
- Dark mode
- Keyboard shortcuts
