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
- `Checkpoint 10O (phase 1)` is the latest implemented slice.
- `Checkpoint 9C` archive/restore workflows across customers, catalog, and dresses are completed underneath it.
- `Checkpoint 8O` remains the frontend heavy-table baseline underneath the 9x audit/lifecycle work.

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

## Checkpoint 8A scope
- startup guardrails for production secrets and cookie policy
- production validation for explicit CORS origins and trusted hosts
- rejection of wildcard and localhost origins in production settings
- `SESSION_SAME_SITE` validation with `SameSite=None` + secure-cookie enforcement
- focused backend security tests for invalid production configuration
- focused docs updates and handoff

## Checkpoint 8B scope
- reverse-proxy template for edge TLS and HTTPS redirect
- production compose template with explicit `edge` service
- deployment-edge runbook for host/protocol forwarding and secure-cookie verification
- infra docs alignment for deployment artifacts
- focused docs updates and handoff

## Checkpoint 8C scope
- post-deploy operations baseline for backup retention, restore drills, and alerting priorities
- documented retention policy with daily/weekly/monthly windows
- restore drill evidence log template
- retention cleanup script example for backup directory operations
- focused docs updates and handoff

## Checkpoint 8D scope
- authenticated operations metrics endpoint for backup and audit snapshot
- webhook alert test endpoint with dry-run mode and audit visibility
- production guardrail for webhook URL transport (`https` in production)
- focused backend tests for operations metrics and alert test behavior
- focused docs updates and handoff

## Checkpoint 8E scope
- stale-backup check endpoint with conditional alert triggering
- audit logging for each stale-check run
- scheduler-ready PowerShell runner with deterministic exit codes
- focused backend tests for stale/no-stale alert run behavior
- focused docs updates and handoff

## Checkpoint 8F scope
- Windows Task Scheduler registration script for periodic stale-backup checks
- Windows Task Scheduler removal script for rollback and cleanup
- concrete Windows wiring runbook with validation steps
- infra docs updates for scheduler operation
- focused docs updates and handoff

## Checkpoint 8G scope
- Linux runner script for periodic stale-backup alert checks
- Linux Cron register/unregister scripts with safe marker-based updates
- concrete Linux Cron wiring runbook with validation steps
- infra docs updates for Linux scheduler operation
- focused docs updates and handoff

## Checkpoint 8H scope
- Kubernetes CronJob manifest for stale-backup alert checks
- secret/config map placeholders for endpoint credentials and run flags
- concrete Kubernetes runbook with apply/validate/remove flow
- infra docs updates for orchestrated scheduler operation
- focused docs updates and handoff

## Checkpoint 8I scope
- backend batch endpoint to run due export schedules
- dry-run and limit controls for safer unattended execution
- audit logging for export schedule batch runs
- Windows/Linux runner scripts for unattended execution
- focused backend tests and docs updates

## Checkpoint 8J scope
- optional delivery webhook channel for due export batch runs
- delivery dry-run control and explicit delivery result fields
- production guardrail for export delivery webhook URL
- focused backend tests for delivery dry-run behavior
- focused docs updates and handoff

## Checkpoint 8K scope
- server-generated finance summary PDF endpoint
- server-generated reports overview PDF endpoint
- lightweight backend PDF generation helper
- focused backend tests for PDF content-type and file payload
- focused docs updates and handoff

## Checkpoint 8L scope
- booking-line revenue reversal endpoint for completed lines
- automatic reversal posting for linked revenue-recognition journal entries
- operational reopen behavior after successful reversal
- guardrails to block reversal when post-completion receivables collections exist
- focused backend tests and docs updates

## Checkpoint 8M scope
- service-level tax rate field for catalog workflows
- booking-line tax snapshot fields for stable accounting evidence
- tax-aware recognition split between revenue and tax payable accounts
- chart-of-accounts update with tax payable account `2200`
- focused backend tests and docs updates

## Checkpoint 8N scope
- paged bookings table endpoint with server-side search, status/date filters, and sorting
- paged payments table endpoint with server-side search, kind/status/date filters, and sorting
- bookings and payments pages updated to use server-driven table queries
- column visibility/order controls retained on both heavy screens
- focused backend tests and frontend production build verification

## Checkpoint 8O scope
- `AG Grid Community` frontend dependency and shared grid infrastructure
- one shared AG Grid shell with toolbar, column controls, CSV export, RTL support, and local preference persistence
- migration of client-side business tables to the shared AG Grid layer
- migration of bookings and payments pages to AG Grid while preserving server-side paging/filtering/sorting
- migration of booking and payment editor tables to AG Grid-based editable cell layouts
- removal of unused legacy table helpers and docs alignment
- frontend build validation, backend table/export regression tests, and browser smoke verification

## Checkpoint 9A scope
- expanded append-only audit log schema with request, session, branch, reason, and before/after payload support
- shared audit-context helper and backend middleware for `request_id`, `session_id`, `ip_address`, and `user_agent`
- audited login success, login failure, logout, and permission-denied events
- new `audit.view` and `destructive.manage` permission foundation
- focused backend tests and docs updates

## Checkpoint 9B scope
- tracked-entity standard with `created_by`, `updated_by`, and `entity_version`
- adoption of tracked-entity fields across mutable business tables
- shared create/update audit helpers for service-layer mutations
- focused migration tests and docs updates

## Checkpoint 9C scope
- archive / inactive workflow foundation for customers, departments, services, and dresses
- restore workflow for archived master data
- active/inactive list filtering in affected frontend screens
- focused backend/frontend validation and docs updates

## Checkpoint 9D scope
- corrective hard-delete framework for eligible operational and master-data mistakes
- dependency and impact preview before destructive actions
- tombstone audit snapshots for hard-deleted records
- destructive reason catalog and shared confirmation dialog foundation
- focused security tests and docs updates

## Checkpoint 9E scope
- closing-date / period-lock foundation
- override permission and exception-report workflow
- lock enforcement on bookings, payments, accounting reversal, and corrective delete flows
- focused backend tests and docs updates

## Checkpoint 9F scope
- custody data model, migration, list/create/detail API, and permissions
- custody page and shell navigation foundation
- shared search, filter, and detail drawer for custody cases
- focused backend/frontend validation and docs updates

## Checkpoint 9G scope
- custody workflow actions: handover, customer return, laundry send/receive, settlement, and compensation collection
- safe payment/accounting linkage for custody compensation workflows
- custody status timeline coverage in audit records
- focused backend tests and docs updates

## Checkpoint 9H scope
- cross-entity detail drill-downs between customers, dresses, bookings, payments, and custody
- entity audit timeline panel in the frontend
- focused backend/frontend validation and docs updates

## Checkpoint 9I scope
- finance chart parity for daily income, department income, and top services
- dashboard UI enhancement without changing accounting source-of-truth behavior
- focused frontend build validation and docs updates

## Checkpoint 9J scope
- audit explorer backend endpoints with filters for actor, action, entity, date, and branch
- destructive-actions report and custody export endpoints
- frontend audit explorer page and timeline navigation
- focused backend/frontend validation and docs updates

## Checkpoint 9K scope
- audit coverage enforcement across all write routes
- route inventory and validation guardrails so new mutations cannot land without audit evidence
- standardized audit events for background jobs and automation workflows
- focused backend validation and docs updates

## Checkpoint 9L scope
- responsive/mobile polish for bookings, payments, custody, and destructive dialogs
- browser smoke around archive, delete, void, custody workflow, and entity timelines
- final roadmap docs updates and handoff

## Checkpoint 10A scope
- backend-persisted AG Grid preferences per user
- user-scoped preference API and frontend hook integration
- audit coverage for preference updates
- migration-safe preference hydration and conflict strategy (`local` vs `server`)
- persistence validation across logout/login cycle
- focused backend/frontend validation and docs updates

## Checkpoint 10E scope
- focused Playwright runtime coverage for refactored bookings/payments pages
- temporary local E2E bootstrap with explicit startup and shutdown steps
- validation evidence logging for the new focused E2E slice
- backend route-size compliance check against architecture target (`<=250`)
- identify next backend file-size hardening targets outside routes

## Checkpoint 10J scope
- `phase 1`: optional nightly failure notifier stage (`notify-nightly-failure`) with secret-gated webhook delivery (`NIGHTLY_FAILURE_WEBHOOK_URL`)
- `phase 1`: summary-focused payload creation from nightly job results with run URL context
- `phase 2`: notifier payload contract documentation (`docs/nightly-failure-notifier-contract.md`)
- `phase 2`: manual rollout and verification checklist for production-safe notifier enablement
- `phase 2`: CI/nightly runbook references aligned to the same payload contract source

## Checkpoint 10K scope
- `phase 1`: backend nightly-failure ingest endpoint (`POST /api/settings/ops/nightly/failure-report`) with token guard (`X-Nightly-Token`)
- `phase 1`: backend latest nightly snapshot endpoint (`GET /api/settings/ops/nightly/latest`) for authenticated settings users
- `phase 1`: audit evidence for ingest events (`ops.nightly_failure_reported`) and write-route inventory onboarding
- `phase 1`: focused backend tests for token validation, ingest success, snapshot read, and audit write behavior
- `phase 2`: settings page read-only nightly status panel using `/api/settings/ops/nightly/latest`
- `phase 2`: nightly panel shows availability, run metadata, stage results, and direct run URL link
- `phase 2`: frontend production build validation with unchanged settings workflows
- `phase 3`: nightly workflow now supports direct MyAtelier ingest channel with token header (`X-Nightly-Token`)
- `phase 3`: optional GitHub secrets added for ingest wiring (`NIGHTLY_FAILURE_INGEST_URL`, `NIGHTLY_FAILURE_INGEST_TOKEN`)
- `phase 3`: notifier contract/runbook updated with token rotation and rollback guidance

## Checkpoint 10L scope
- `phase 1`: backend audit preset endpoint added (`GET /api/audit/nightly-ops`) for nightly failures + automation follow-up actions
- `phase 1`: preset action set includes `ops.nightly_failure_reported` and `automation.job_run` with existing `audit.view` permission guard
- `phase 1`: frontend audit explorer mode toggle now supports `Nightly ops` beside `All actions` and `Destructive only`
- `phase 1`: focused backend tests and frontend production build validation passed
- `phase 2`: audit explorer now includes quick date shortcuts (`today`, `last 24h`, `last 7d`) for faster triage
- `phase 2`: shortcuts apply across all explorer modes, including `nightly_ops`
- `phase 2`: frontend build validation passed and page file-size discipline preserved

## Checkpoint 10M scope
- `phase 1`: backend CSV export endpoint added for nightly ops audit preset (`GET /api/audit/nightly-ops.csv`)
- `phase 1`: CSV export honors active nightly filters (`search`, actor/target/branch, date range) with bounded `limit`
- `phase 1`: frontend audit explorer now shows compact `Export nightly CSV` action in nightly-ops mode
- `phase 1`: backend test and frontend production build validation passed
- `phase 2`: nightly CSV now prepends export-note rows for `exported_at`, `exported_rows`, and `active_filters`
- `phase 2`: nightly CSV response includes summary headers (`X-Exported-Rows`, `X-Active-Filters`) for operator/integration traceability
- `phase 2`: nightly-ops UI now displays export summary hints (matching rows + active filters) before export action

## Checkpoint 10N scope
- `phase 1`: nightly CSV export download now writes audit event (`audit.nightly_ops_exported`)
- `phase 1`: export audit payload includes actor, exported rows, and active filter summary for evidence traceability
- `phase 1`: focused backend audit-explorer tests passed with export-audit assertions
- `phase 2`: audit explorer now surfaces latest nightly-export entries in a compact summary panel during `nightly_ops` mode
- `phase 2`: summary highlights who exported and when, reducing manual filter reconstruction for operators
- `phase 2`: backend nightly-ops preset now includes `audit.nightly_ops_exported` action in addition to failure/automation signals

## Checkpoint 10O scope
- `phase 1`: nightly CSV export now accepts optional export reason (`export_reason`) and persists it as audit `reason_text`
- `phase 1`: export-audit evidence (`audit.nightly_ops_exported`) now supports governance context beyond filter/row metadata
- `phase 1`: backend tests verify reason capture and frontend flow passes production build checks

## Recommended next checkpoint
- The next work should stay small and improve usability while preserving governance.
- The best candidate now is `Checkpoint 10O (phase 2)`: replace browser prompt with compact inline export-reason input in nightly mode for cleaner operator UX.

## Deferred after Checkpoint 8N
- extend the same server-driven table contract to accounting and report-heavy screens
- make XLSX/CSV export endpoints honor the exact active table filters for bookings and payments

## Deferred after Checkpoint 8O
- exact heavy-table export parity with active grid filters now sits behind the audit/data-lifecycle roadmap
- make backend XLSX exports honor the exact active grid filters for heavy screens
- add optional chart/report grouping views that complement AG Grid Community without enterprise-only features
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
