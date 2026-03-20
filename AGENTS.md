# AGENTS.md

## Project Scope
- New project root: `MyAtelier_pro`
- Architecture target: modular monolith
- Backend: FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL
- Frontend: React + TypeScript + Vite + MUI

## Delivery Constraint
- This project is being built with Codex as the primary implementation agent.
- The owner is not a programmer, so the product must be built in small, understandable, testable pieces.
- Prefer milestone-sized slices that can be reviewed and verified independently.
- Avoid large all-at-once rewrites or broad unfinished scaffolding without a usable checkpoint.
- Every implementation slice should leave the project in a clearer, runnable, or better-documented state.

## Working Rules
- Keep module boundaries clear from day one.
- Business rules belong in service layer, not routes or UI.
- Favor explicit workflows over generic CRUD abstractions.
- Use Arabic-first labels/messages in the UI.
- Keep files focused and avoid large catch-all modules.

## File Size Discipline
- Keep files small enough for fast Codex review and safe future edits.
- Preferred target size:
  - backend routes, services, repositories, schemas, and models: `<= 250` lines
  - frontend pages, components, hooks, and API files: `<= 250` lines
  - test files: `<= 250` lines
- Split files before they exceed roughly `350` lines unless they are almost entirely simple declarations.
- If a file starts holding more than one responsibility, split it immediately.
- Prefer multiple small readable files over fewer large files.

## Security Rules
- Every privileged operation must enforce authentication and authorization on the server side.
- Never rely on hidden buttons or disabled UI elements as security.
- Validate request data strictly and keep response schemas explicit.
- Keep secrets in environment variables; only documented local bootstrap defaults may be hardcoded.
- Session cookies must remain `HttpOnly`, `SameSite`, and `Secure` in production.
- Restrict CORS to known frontend origins.
- Avoid raw SQL unless there is a clear reason and the query is fully parameterized.
- Audit security-sensitive actions such as user changes, settings changes, backup creation, and future financial posting actions.
- File download and backup endpoints must always be authenticated and authorized.
- Each checkpoint must include a small security review before it is marked complete.

## Validation Defaults
- Backend: run pytest for changed backend behavior.
- Frontend: run build/tests when dependencies are installed.
- Prefer Docker Compose for integrated local runs.

## Documentation Rules
- Update `docs/decision-log.md` when making architectural decisions.
- Keep `docs/milestones.md` and `docs/acceptance-scenarios.md` aligned with implementation.