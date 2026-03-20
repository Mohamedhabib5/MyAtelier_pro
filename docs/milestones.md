# Milestones

## Delivery rule
- Every milestone must be implementable in small Codex-friendly slices.
- Each slice should be understandable to a non-programmer owner and end with a usable checkpoint.
- Do not plan future work as one large all-at-once build.

## Mandatory checkpoint gate
- The scope must be small enough for one clean Codex implementation slice.
- File size discipline must still be respected after implementation.
- Docs must be updated before the checkpoint is considered done.
- Focused validation must be run.
- A small security review must be completed.

## Current implemented checkpoint
- `Checkpoint 7D` is the latest implemented slice.
- `Checkpoint 7C` remains the backup-restore confidence base underneath it.
- `Checkpoint 7D` should be treated as the current stable handoff point before a short production-readiness review.

## Checkpoint 1 scope
- repository scaffold
- documentation baseline
- docker compose baseline
- backend scaffold
- frontend scaffold
- PostgreSQL and Alembic baseline
- auth/session foundation
- default admin seed
- users/settings foundation
- backup create/download/history foundation
- backend tests
- frontend shell and route guards
- Playwright smoke scaffold

## Checkpoint 2A scope
- RTL layout correction for the Arabic frontend shell
- env-driven CORS and trusted-host configuration
- production-aware session cookie settings
- security headers middleware
- session-fixation mitigation on login
- explicit permission guards for users and settings actions
- validated backup download path handling
- backup download audit logging
- focused security tests and updated docs

## Checkpoint 2B scope
- accounting rules document
- chart-of-accounts data model
- journal entry header and line models
- journal sequence foundation
- read-only accounting chart endpoint
- accounting foundation seeding and tests

## Checkpoint 2C scope
- journal entry create/list/detail workflow
- journal posting workflow
- journal reversal workflow
- posted-entry immutability rules
- `accounting.manage` permission and route guards
- backend tests and docs for journal workflow

## Checkpoint 2D scope
- read-only trial balance endpoint
- filtering by date and fiscal period
- movement and balance aggregation by account
- backend tests and docs for trial balance behavior

## Checkpoint 2E scope
- read-only accounting page in the frontend
- shell navigation to accounting
- chart, journals, and trial balance presentation
- lightweight trial-balance filters in the UI
- frontend build validation and docs updates

## Checkpoint 3A scope
- customers data model and migration
- customers list, create, and update API
- customers permissions for both `admin` and `user`
- customers page in the frontend shell
- customer rules doc and focused tests

## Checkpoint 3B scope
- departments and services data model with migration
- catalog list, create, and update API
- catalog permissions for both `admin` and `user`
- services page in the frontend shell with sections for departments and services
- services-and-departments rules doc and focused tests

## Checkpoint 3C scope
- dress resources data model with migration
- dresses list, create, and update API
- dresses permissions for both `admin` and `user`
- dresses page in the frontend shell
- dress-resources rules doc and focused tests

## Checkpoint 4A scope
- bookings data model with migration
- bookings list, create, and update API
- bookings permissions for both `admin` and `user`
- booking sequence generation
- dress-date conflict prevention
- bookings page in the frontend shell
- booking rules doc and focused tests

## Checkpoint 4B scope
- payment receipts data model with migration
- payments list, create, and update API
- payments permissions for both `admin` and `user`
- payment sequence generation
- deposit, payment, and refund validation
- payments page in the frontend shell
- payment rules doc and focused tests

## Checkpoint 4C scope
- finance dashboard API and `finance.view` permission
- KPI summary for total income, total remaining, and total bookings
- breakdown lists for daily income, department income, and top services
- dashboard page as the default post-login route
- shell navigation aligned more closely with the old Dash product layout
- focused dashboard tests and docs updates

## Checkpoint 5A scope
- reports overview API and `reports.view` permission
- read-only summary metrics across current operational modules
- reporting page in the frontend shell
- upcoming bookings list in the reporting UI
- focused reports tests and docs updates

## Checkpoint 5B scope
- session-level active branch context
- branch create and active-branch switch API
- active branch details in the authenticated user payload
- branch-aware filtering for bookings, payments, finance dashboard, and reports
- branch selector in the shell
- settings page support for branch creation and branch visibility
- focused branch-scope tests and docs updates

## Checkpoint 5C scope
- linked journal entry reference on payment receipts
- automatic posted journal creation for payment receipts
- automatic reversal and replacement of linked journals on payment update
- payment response visibility for journal number and status
- payment-page UI note about accounting replacement on edit
- focused payment-accounting tests and docs updates

## Checkpoint 6A scope
- customers CSV export
- bookings CSV export
- payments CSV export
- `exports.view` permission and guarded download endpoints
- export center page in the frontend shell
- branch-aware export scope for bookings and payments
- focused export tests and docs updates

## Checkpoint 6B scope
- backend lifespan startup and shutdown handling
- removal of deprecated `on_event` startup usage
- route-level lazy loading for frontend pages
- router loading fallback for lazy routes
- Vite manual chunk splitting for vendor bundles
- focused validation and docs updates

## Checkpoint 6C scope
- payment receipt `active/voided` status foundation
- `POST /api/payments/{payment_id}/void` business action
- required void reason and audit logging for void actions
- automatic reversal of linked journal entries on payment voiding
- prevention of updating already-voided payments
- dashboard and reports exclusion of voided payments from totals
- payments export visibility for void status and reason
- focused validation and docs updates

## Checkpoint 6D scope
- printable finance summary page
- printable reports page
- shared print-layout component for PDF-ready pages
- export-center links to open printable routes in separate tabs
- browser-based print/save-as-PDF workflow without heavy backend PDF generation
- focused validation and docs updates

## Checkpoint 6E scope
- export schedule data model and migration
- list/create/run/toggle schedule API
- `exports.manage` permission and guarded schedule actions
- branch-aware run-now URLs for bookings, payments, finance print, and reports print
- export-center UI for saved schedules
- focused validation and docs updates

## Checkpoint 6F scope
- booking revenue-recognition data model and migration
- explicit booking completion business action
- posted journal creation on booking completion
- use of customer advances and receivables in revenue recognition
- booking UI visibility for linked revenue journal number
- operational locking of completed bookings after recognition
- focused validation and docs updates

## Checkpoint 7B scope
- Playwright-ready frontend container alignment
- dedicated `test:e2e` frontend script
- live smoke coverage for login and redesigned booking/payment flow
- PostgreSQL schema-fix migration for legacy booking header constraints
- focused docs updates and stable handoff after live validation

## Checkpoint 7C scope
- database dump included in backup archive
- PostgreSQL dump compatibility normalization
- automated restore test against throwaway SQLite database
- live restore verification against throwaway PostgreSQL database
- focused docs updates and handoff

## Checkpoint 7D scope
- glossary-backed Arabic wording recovery for critical UI flows
- small shared text modules for auth, bookings, payments, and users
- Arabic translation of remaining user-facing backend messages
- removal of booking dress-logic dependence on Arabic display names
- UTF-8 and text-integrity guardrails
- focused backend and Playwright validation
- focused docs updates and handoff

## Recommended next checkpoint
- The next work should stay small and focus on final operational confidence rather than another broad module.
- The best candidate now is a short production-readiness review for envs, secrets, cookies, CORS, and deployment notes.

## Deferred after Checkpoint 7D
- unattended background execution of export schedules
- server-generated PDF exports
- automatic reversal for booking revenue recognition
- tax-aware revenue recognition
- industry presets


## Checkpoint 7A scope
- booking header + booking lines data model and migration
- payment document + payment allocations data model and migration
- migration path from legacy single-line bookings and single receipts
- booking document API with line-level complete/cancel actions
- payment search targets and payment document API
- booking editor redesign with multi-line entry and quick customer add
- automatic payment document creation from initial line payments
- line-aware dashboard, reports, and CSV export updates
- focused validation and docs updates
