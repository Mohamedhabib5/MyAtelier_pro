# Session Handoff — 2026-03-16 — Checkpoint 3A

## What was completed
- finished the customers module as the first business slice after accounting
- connected the customers router into the FastAPI app
- added the Alembic migration for the `customers` table
- added backend tests for create/list/update and duplicate-phone behavior
- added a small Arabic customers page in the React shell
- updated checkpoint docs and added a dedicated customer rules doc

## Backend scope
- model: `customers`
- API: `GET /api/customers`, `POST /api/customers`, `PATCH /api/customers/{id}`
- permissions: `customers.view`, `customers.manage`
- roles: both `admin` and `user` currently receive these permissions
- validation: unique phone per company, trimmed required values, nullable optional fields

## Frontend scope
- nav item: `العملاء`
- page: list customers, open add dialog, open edit dialog
- both roles can use the customers page in this checkpoint

## Security review note
- all customer endpoints require authenticated sessions
- permissions are enforced server-side through dependency guards
- no delete flow was added in this slice, which reduces accidental or malicious destructive changes
- company scoping is enforced in the service layer before reads and writes

## Recommended next checkpoint
- `Checkpoint 3B` should build services and departments as the next small catalog slice.
