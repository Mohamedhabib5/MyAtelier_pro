# Beauty ERP v3 Rebuild Plan

## Delivery constraint
- This app must be built with Codex as the main implementation partner because the owner is not a programmer.
- The system must be delivered in small, reviewable, testable checkpoints rather than large all-at-once rewrites.
- Each checkpoint must end in a usable state with updated docs and clear next steps.

## Current implementation status
- The repository currently includes `Checkpoint 8M`.
- Implemented slices now cover security hardening, accounting foundation, accounting UI, customers, catalog, dresses, bookings, payments, finance dashboard, broader reporting, branch-aware controls, payment-accounting links, export center flows, technical cleanup, safe payment voiding, printable views, saved export schedules, booking revenue recognition plus guarded revenue reversal and tax-aware split posting, backup-restore verification, Arabic text integrity guardrails, production-readiness startup validation, deployment-edge templates/runbook, post-deploy operations baseline, alerting endpoints, stale-check automation, Windows scheduler wiring, Linux Cron wiring, Kubernetes CronJob wiring, unattended due-export batch execution, optional delivery webhook handoff, and server-generated PDF exports.
- The system now resembles the old Dash app in navigation order and main operational modules, while the remaining work is mostly industry presets and optional advanced workflows.

## High-level target
- Backend: `FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic`
- Frontend: `React + TypeScript + Vite + React Router + TanStack Query + MUI`
- Database: `PostgreSQL`
- Runtime: `Docker Compose`
- UI direction: Arabic-first RTL

## Remaining major stages
- final operational polish such as end-to-end expansion, backup-restore verification, and production-readiness checks
- optional workflow refinements such as industry presets

## Build rules
- Keep backend, frontend, and test files small enough for future Codex review.
- Prefer one business slice per checkpoint.
- Update docs, tests, and security notes with every checkpoint.
