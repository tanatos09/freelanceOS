# 📋 FreelanceOS - Seznam funkcí (Complete)

## 🔐 Autentizace
- [ ] User registrace (optional - single user)
- [ ] Login (JWT)
- [ ] Logout
- [ ] Token refresh
- [ ] Get current user (me endpoint)

## 👥 Clients (Klienti)
- [ ] List clients
- [ ] Create client
- [ ] Update client
- [ ] Delete client
- [ ] Get client detail
- [ ] Get client projects
- [ ] Search clients
- [ ] Filter clients
- [ ] Calculate total earnings per client
- [ ] Count projects per client

## 💼 Leads (Poptávky)
- [ ] List leads
- [ ] Create lead
- [ ] Update lead
- [ ] Delete lead
- [ ] Get lead detail
- [ ] Filter by status (new/contacted/deal/rejected)
- [ ] Filter by priority (low/medium/high)
- [ ] Convert lead to project
- [ ] Link lead to client
- [ ] Set expected close date
- [ ] Set probability
- [ ] Add technologies (JSONField)

## 📁 Projects (Projekty)
- [ ] List projects
- [ ] Create project
- [ ] Update project
- [ ] Delete project
- [ ] Get project detail
- [ ] Filter by status (new/in_progress/waiting_client/done/cancelled/invoiced/paid)
- [ ] Filter by client
- [ ] Filter by deadline (before/after)
- [ ] Search by name
- [ ] Get project time entries
- [ ] Get project activities
- [ ] Calculate actual hours
- [ ] Calculate progress percentage
- [ ] Check if overdue
- [ ] Project checklist/TODO (JSONField)
- [ ] Add/remove technologies (JSONField)
- [ ] Add/remove tags (JSONField)

## ⏱️ Time Tracking
- [ ] List time entries
- [ ] Create time entry (manual)
- [ ] Update time entry
- [ ] Delete time entry
- [ ] Start timer
- [ ] Stop timer
- [ ] Get running timer
- [ ] Filter by project
- [ ] Filter by date range
- [ ] Calculate duration
- [ ] Calculate earnings (rate × hours)
- [ ] Mark as billable/non-billable
- [ ] Set custom rate

## 📝 Activities (Log)
- [ ] List activities
- [ ] Create activity
- [ ] Delete activity
- [ ] Filter by project
- [ ] Filter by type (note/email/call/meeting/status_change)
- [ ] Activity timeline

## 📊 Dashboard
- [ ] Get stats overview
  - Active projects count
  - Total earnings this month
  - Hours worked this week
  - Hours worked this month
  - Overdue projects count
  - Pipeline value (sum of leads in "deal" status)
- [ ] Get chart data
  - Earnings over time
  - Projects by status
  - Time distribution by project

## 🧾 Invoices (Faktury)
- [ ] List invoices
- [ ] Create invoice
- [ ] Update invoice
- [ ] Delete invoice
- [ ] Get invoice detail
- [ ] Mark as draft/sent/paid
- [ ] Generate PDF
- [ ] Link invoice to project
- [ ] Set payment dates

## 🎨 Frontend Components

### Layout
- [ ] Sidebar navigation
- [ ] Header with running timer
- [ ] User menu
- [ ] Protected routes

### Clients
- [ ] Clients table
- [ ] Client form (modal)
- [ ] Client detail page
- [ ] Client search/filter

### Leads
- [ ] Leads kanban board
- [ ] Leads table view
- [ ] Lead form (modal)
- [ ] Lead detail page
- [ ] Convert to project button

### Projects
- [ ] Projects table/grid
- [ ] Project form (modal)
- [ ] Project detail page with tabs
  - Overview
  - Time Entries
  - Activity Log
- [ ] Status badges (color-coded)
- [ ] Overdue alerts
- [ ] Progress bar
- [ ] Checklist inline edit

### Time Tracking
- [ ] Timer component (in header)
- [ ] Start timer modal
- [ ] Time entries table
- [ ] Manual time entry form
- [ ] Filters (project, date range)

### Dashboard
- [ ] Stats cards
- [ ] Charts (earnings, projects, time)
- [ ] Recent activities widget
- [ ] Quick actions
- [ ] Overdue projects alert

### Common
- [ ] Login page
- [ ] Loading states (skeletons)
- [ ] Empty states
- [ ] Error handling
- [ ] Toast notifications
- [ ] Form validations (Zod)
- [ ] Responsive design

## 🛠️ Utils & Infrastructure
- [ ] API client (Axios)
- [ ] Request/response interceptors
- [ ] Auth store (Zustand)
- [ ] Timer store (Zustand)
- [ ] React Query hooks
- [ ] TypeScript interfaces
- [ ] Django admin customization
- [ ] Seed data command
- [ ] Database migrations
- [ ] CORS configuration
- [ ] JWT configuration
- [ ] Environment variables
