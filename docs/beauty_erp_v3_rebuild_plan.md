# Beauty ERP v3 Rebuild Plan

## Delivery constraint
- This app must be built with Codex as the main implementation partner because the owner is not a programmer.
- The system must be delivered in small, reviewable, testable checkpoints rather than large all-at-once rewrites.
- Each checkpoint must end in a usable state with updated docs and clear next steps.

## Current implementation status
- The repository currently includes `Checkpoint 6F`.
- Implemented slices now cover security hardening, accounting foundation, accounting UI, customers, catalog, dresses, bookings, payments, a finance dashboard summary, broader reporting, branch-aware controls, the first payment-to-accounting bridge, a small export center, technical cleanup for startup and bundle loading, safe payment voiding, printable export views, saved export schedules, and booking-completion revenue recognition.
- The system already resembles the old Dash app in navigation order and main operational modules, while the remaining work is now mostly final quality work and optional advanced workflows.

## High-level target
- Backend: `FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic`
- Frontend: `React + TypeScript + Vite + React Router + TanStack Query + MUI`
- Database: `PostgreSQL`
- Runtime: `Docker Compose`
- UI direction: Arabic-first RTL

## Remaining major stages
- final operational polish such as end-to-end expansion, backup-restore verification, and production-readiness checks
- optional workflow refinements such as unattended export delivery, automatic reversal logic, and tax-aware revenue rules

## Build rules
- Keep backend, frontend, and test files small enough for future Codex review.
- Prefer one business slice per checkpoint.
- Update docs, tests, and security notes with every checkpoint.
