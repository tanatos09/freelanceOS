# Roadmap FreelanceOS

## MVP (hotovo)

- [x] **Auth** — registrace, login, logout, JWT refresh, change password
- [x] **Klienti** — CRUD, vyhledávání, statistiky, hourly rate
- [x] **Projekty** — CRUD, 7 statusů, overdue detekce, filtry
- [x] **Timer** — start/stop/commit workflow, aktivní timer, duration tracking
- [x] **Dashboard** — earnings, aktivní projekty, overdue count
- [x] **Workspaces** — multi-tenant, role-based membership
- [x] **Frontend** — Django templates, dark theme, responsive
- [x] **Testy** — 260+ testů, 92%+ coverage, Factory Boy
- [x] **Security** — JWT blacklist, CSRF, rate limiting, data isolation

## Další kroky (MVP+)

- [ ] Deploy na produkční server (Gunicorn + PostgreSQL + HTTPS)
- [ ] Editace času (úprava start/end time u work commitů)
- [ ] Export dat (CSV/JSON)
- [ ] Faktury (PDF generování z work commitů)

## Budoucnost (v2)

- [ ] React + TypeScript frontend
- [ ] Grafy a reporty (earnings over time)
- [ ] Leads / poptávky (kanban board)
- [ ] Multi-user týmy
- [ ] Keyboard shortcuts
