# MyAtelier_pro

`MyAtelier_pro` is the new-generation rebuild of MyAtelier on a modular monolith architecture using FastAPI, React, TypeScript, and PostgreSQL.

## Stack
- Backend: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- Frontend: React, TypeScript, Vite, React Router, TanStack Query, MUI
- Database: PostgreSQL 16
- Testing: pytest, Playwright
- Local development: Docker Compose

## Delivery Model
- This project is intended to be built and evolved with Codex as the main implementation partner.
- Because the owner is not a programmer, development must happen in small, reviewable pieces.
- Each milestone should be understandable on its own and leave behind a usable checkpoint.
- Future work should prefer incremental slices over large all-at-once builds.
- **AI Rules**: All AI development must follow the [Comprehensive AI Rules](file:///d:/Programing%20project/MyAtelier_pro/ai_rules.md).

## Current Status
- The repository currently includes `Checkpoint 8M`.
- Implemented slices now cover auth and security hardening, accounting foundation and UI, customers, catalog, dresses, bookings and payments redesign, dashboard and reports, branch scoping, exports and print views, booking revenue recognition plus guarded reversal and tax-aware posting split, backup-restore verification, Arabic text integrity guardrails, production/deployment guardrails, post-deploy operations baseline, alerting baseline endpoints, stale-backup automated checks, Windows/Linux/Kubernetes scheduler wiring, unattended due-export batch execution, optional delivery webhook handoff, and server-generated PDF exports.
- Development continues in small checkpoints so each step remains reviewable and testable.

## Core Scope Implemented So Far
- Identity and session auth
- Users and settings workflows
- Company and branch context
- Accounting foundation and journal workflows
- Customers, services, dresses, bookings, payments
- Dashboard, reports, exports, and printable views
- Backup creation/download and restore verification
- Security, Arabic text integrity, and production/deployment guardrails

## Quick Start
1. Copy `.env.example` to `.env`
2. Start Docker Desktop or a compatible Docker daemon
3. Run `docker compose up --build`
4. Open:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

## Default First-Run Admin
- Username: `admin`
- Password: `admin123`

The default admin is seeded once only on an empty database.

## Guardrail CI Profile
- Fast guardrail suite (backend + architecture boundaries):
  - `cd backend && python -m pytest -m guardrail`
- Frontend build gate:
  - `cd frontend && npm run build`
- GitHub Actions workflow:
  - `.github/workflows/guardrails.yml`
- Release gate criteria:
  - `docs/guardrail-release-gate.md`
- Branch protection rollout:
  - `docs/branch-protection-guardrails.md`
- CI troubleshooting runbook:
  - `docs/ci-gate-runbook.md`
- Optional nightly full regression:
  - `.github/workflows/nightly-full-regression.yml`
  - `docs/nightly-full-regression.md`
  - Optional failure notifier secret: `NIGHTLY_FAILURE_WEBHOOK_URL`
