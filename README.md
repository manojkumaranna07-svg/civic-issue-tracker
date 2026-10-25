# Civic Issue Tracker

A full-stack web app for reporting, tracking and resolving community issues:
potholes, garbage, broken streetlights, water leaks, campus equipment faults
and more. Citizens report problems (with photo and map pin), support each
other's reports with a "Me Too" upvote, and follow every status change.
Administrators review, assign, update statuses, broadcast announcements and
watch live analytics. Department staff resolve what is assigned to them.

## Problem statement

Civic complaints are scattered across phone calls, paper registers and social
media. There is no single place to report an issue, see whether others face it
too, or know what is being done. Civic Issue Tracker centralises reporting,
makes support visible through upvotes, and keeps an auditable trail from
report to resolution.

## Objectives

- One simple public reporting flow with validation and photo evidence.
- Transparent statuses: Reported > Under Review > In Progress > Resolved
  (or Rejected with a reason).
- Community prioritisation through duplicate-safe upvotes.
- Map-based view of user-pinned issue locations (OpenStreetMap).
- Admin tooling: assignments, catalog management, dashboard analytics.
- In-app notification history for every important event.

## Main features

| Area | What works |
| --- | --- |
| Auth | Register/login, bcrypt hashing, JWT tokens, role-based access (citizen / admin / staff), enforced on the backend |
| Reporting | Multipart form, sector-dependent categories, optional map pin, optional image (JPEG/PNG/WEBP/GIF, 5 MB, content-sniffed, stored under generated safe names) |
| Tracking | Public IDs (CIV-YYYY-NNNNN), status history timeline, comments with official markers |
| Upvotes | One vote per user per issue (DB unique constraint), removable, used for "most supported" sorting and admin insight |
| Map | Leaflet + OpenStreetMap, status-coloured markers, sector/status filters. Only user-pinned issues appear; unpinned issues stay in lists |
| Admin | Dashboard (live DB stats, charts), issue management table, assignments to departments/staff, catalog management, announcements |
| Notifications | In-app feed for submissions, status changes, admin comments, resolutions, announcements; unread badge, mark read/all |
| API docs | FastAPI Swagger UI at `/docs` |

## User roles

- **Citizen**: register, report, upvote, comment, track, get notified.
- **Administrator**: everything a citizen can do, plus status changes,
  assignments, catalog and user management, announcements, dashboard.
- **Department staff** (optional role, implemented): sees issues assigned to
  them, sets In Progress / Resolved, records resolution notes.

## Technology stack

- Frontend: React 18, Vite, React Router, Recharts, Leaflet + react-leaflet
- Backend: Python 3.10+, FastAPI, SQLAlchemy 2, PyJWT, bcrypt, Pillow
- Database: SQLite (file at `backend/civic.db`)
- Testing: pytest (86 backend tests), Vitest + Testing Library (10 frontend tests)
- Diagrams: PlantUML (sources in `docs/diagrams/`)

## Project structure

```
civic-issue-tracker/
  frontend/          React app (src/pages, src/components)
  backend/
    app/
      api/           FastAPI routers (auth, users, meta, issues, map, notifications, dashboard)
      models/        SQLAlchemy models - 12 tables
      schemas/       Pydantic request/response schemas
      services/      auth, image, notification, stats, issue helpers
      database/      engine/session + declarative base
      seed.py        demo data (fictional reports at real Chennai anchors)
    tests/           pytest suite (86 tests)
    uploads/         stored issue images (git-ignored)
  docs/diagrams/     PlantUML sources + PNG exports + README
  scripts/           init_db, run_backend, run_frontend_dev, run_tests, build_frontend
  .env.example       environment template
  requirements.txt
```

## Database schema (12 tables)

users, sectors, categories, departments, issues, issue_images,
issue_status_history, upvotes, issue_assignments, notifications, comments,
announcements - with primary/foreign keys, unique constraints (email,
sector+category name, one upvote per user/issue), and indexes on the common
filter columns. See `docs/diagrams/` (class diagram) and
`backend/app/models/`.

## Installation & running (local demo)

Requirements: Python 3.10+, Node 18+.

```bash
# 1. Backend deps
pip install -r requirements.txt

# 2. Frontend deps + production build
cd frontend && npm install && npm run build && cd ..

# 3. Create the database with demo data
./scripts/init_db.sh

# 4. Run everything (API + built frontend)
./scripts/run_backend.sh
```

Open http://localhost:8000 - the backend serves the built React app.
Interactive API docs: http://localhost:8000/docs

For frontend development with hot reload, run `./scripts/run_backend.sh` and
`./scripts/run_frontend_dev.sh` together; the Vite dev server on :5173
proxies API calls to :8000.

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Citizen | citizen@example.com | Citizen@123 |
| Citizen | meena@example.com | Citizen@123 |
| Citizen | arun@example.com | Citizen@123 |
| Department staff | staff@example.com | Staff@123 |
| Administrator | admin@example.com | Admin@123 |

These exist only in the local seed data. To change them, edit
`DEMO_PASSWORDS` in `backend/app/seed.py` and re-run `./scripts/init_db.sh`
(this recreates the database). Emails use the reserved `example.com` domain
because validators reject undeliverable custom local domains.

## Configuration

Copy `.env.example` to `.env` (or export the variables). `SECRET_KEY` signs
JWT tokens - change it for any real deployment. `BCRYPT_ROUNDS` exists only
so the test suite can hash quickly; do not lower it in production.

## Running the tests

```bash
./scripts/run_tests.sh
# or separately:
cd backend && python3 -m pytest tests/ -q     # 86 passed
cd frontend && npm test                        # 10 passed
```

The backend suite covers registration/login, RBAC, issue validation, image
upload security (fake image, EXE-in-.png, SVG, oversize), duplicate upvote
prevention, status transitions and history, notifications, dashboard stats,
map rules, catalog management and error handling. Tests run against a
temporary isolated database.

## Diagrams

See `docs/diagrams/README.md`: Data Flow Diagram (Levels 0, 1 and 2), Use
Case Diagram, Class Diagram and Activity Diagram - PlantUML sources plus
black-and-white PNG exports, all consistent with the implemented code.

## Demo data note

Seeded issues are fictional demonstration reports. Pinned ones use real,
publicly known Chennai locations (Marina Beach, T. Nagar, Nungambakkam,
Guindy, Adyar, Velachery, Anna University, Semmozhi Poonga, Cathedral Road)
purely so the map view is meaningful in a demo. No real incidents or personal
data are represented.

## Security notes

- Passwords hashed with bcrypt; JWTs expire after `TOKEN_EXPIRE_HOURS`.
- Every protected endpoint checks the token; admin/staff rules are enforced
  in the backend, not the UI.
- Uploads are content-sniffed with Pillow, size-limited, stored under
  generated names; SVGs are rejected (script-injection risk).
- Coordinates are stored only as an explicit user-picked pair; issues without
  a pair never get a map marker.
- Secrets come from environment variables. Serve over HTTPS in any real
  deployment (e.g. behind a reverse proxy with TLS).

## Limitations and future enhancements

- In-app notifications only; the notification service interface is ready for
  email/push delivery later.
- No image thumbnails; originals are shown (small demo scale).
- SQLite suits the demo; swap `DATABASE_URL` for PostgreSQL in production.
- Map tiles require internet access (OpenStreetMap); everything else works
  offline.
- Vite warns the JS bundle exceeds 500 kB (recharts + leaflet); code
  splitting would trim initial load.
- Email addresses are syntax-checked only; no verification flow exists.
