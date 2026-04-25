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

## Codex token efficiency rule
- Execution should minimize context and output size to reduce token usage and cost.
- Prefer small, milestone-sized tasks with short responses and focused file reads.
- Avoid dumping long command output unless it is required for a decision or requested by the owner.
- Start a fresh implementation thread for new major tasks when possible to avoid carrying oversized historical context.

## Mandatory final review gate (end of each phase)
- No phase is marked complete until a strict end-to-end review is finished.
- Final review must confirm: functional correctness, integration between modules, data integrity, security posture, and administrative workflow consistency.
- Final review must include code-level checks for coupling correctness, missing links between layers, and regression risk.
- All critical flows must be validated as working successfully before sign-off.
- Any discovered gap or risk must be documented and resolved (or explicitly approved with a mitigation plan) before closure.
