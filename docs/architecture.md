# Architecture

## Why modular monolith
- One backend, one frontend, one database in v1.
- Clear module boundaries without the cost of microservices.
- Easier to evolve with AI-assisted development and human review.

## Delivery constraint
- This product must be built in pieces, not as one large pass.
- The project is intended to be developed with Codex as the primary implementation agent.
- The owner is not a programmer, so every implementation phase should be small, reviewable, and verifiable.
- Each slice should leave behind a stable checkpoint with working code, docs, or tests before the next slice begins.

## Runtime shape
- FastAPI backend exposing explicit business APIs.
- React TypeScript frontend for workflow-heavy operational screens.
- PostgreSQL as the source of truth.
- Cookie-based session auth for internal web usage.

## Initial modules
- `core_platform`: health, backups, audit, app settings, shared infra hooks
- `organization`: company, branch, fiscal period, sequences
- `identity`: auth, users, roles, permissions

## Design rules
- Routes validate input and orchestrate services only.
- Services hold business rules.
- Repositories handle persistence.
- Posted/final financial workflows will be immutable when those modules land.
- Operational state must stay distinct from financial state.

## File size discipline
- The codebase must stay easy for Codex to reread and change.
- Backend files should normally stay at or below `250` lines.
- Frontend files should normally stay at or below `250` lines.
- Test files should normally stay at or below `250` lines.
- Files approaching `350` lines should be split unless they are mostly simple declarations.
- Pages should delegate to smaller components, and services should delegate to helpers or repositories before they become large.

## Security baseline
- Authentication and authorization must be enforced on the backend for every protected workflow.
- Security-sensitive actions must be auditable.
- Input validation must be explicit and strict.
- Session security, CORS restrictions, secret handling, and backup protection are part of the architecture, not optional polish.
- Every milestone should include a lightweight security review before completion.