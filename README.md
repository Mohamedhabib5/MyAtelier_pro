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

## Current Status
- The repository currently contains only the first foundation checkpoint.
- What is implemented so far is intentionally limited to Milestone 0 + the first part of Milestone 1.
- The current checkpoint covers scaffold, auth/users foundation, settings foundation, backup foundation, docs, and initial tests.
- CRM, bookings, dresses, payments, finance parity, and later ERP modules are still intentionally deferred.
- Future Codex sessions should extend the app one small reviewed slice at a time.

## Initial Scope
- Identity and session auth
- Users management and self-account mode
- Settings foundation
- Company and branch foundation
- Backup create/download/history foundation
- Project documentation and milestone framework

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