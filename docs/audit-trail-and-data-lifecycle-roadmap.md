# Audit Trail and Data Lifecycle Roadmap

## Purpose
- This roadmap defines the next implementation wave after `Checkpoint 8O`.
- The goal is to make auditability, archive/delete policy, and financial correction behavior consistent across the whole product.
- The design follows a QuickBooks-style lifecycle:
  - `Archive / Inactive` for master and reference data.
  - `Void / Reverse` for financial history.
  - `Corrective Hard Delete` only for wrong operational or early-stage records, while keeping a full audit tombstone.

## Product-wide goals
- Every saved create, update, archive, restore, delete, void, reverse, post, completion, cancellation, export, backup, and privileged auth action must create an audit event.
- Every tracked entity must show who created it, who last updated it, when it happened, and how many saved revisions it has gone through.
- Every destructive action must require a reason and leave a searchable trace.
- No posted or financially effective history should disappear from the operational or accounting timeline.
- Every slice must remain small, reviewable, and testable for a non-programmer owner.

## QuickBooks-style action policy
| Situation | Default action | Why |
|---|---|---|
| Customer, service, department, dress, branch no longer active | `Archive / Inactive` | Keeps history while removing the record from active workflows |
| Operational record entered by mistake and still safe to remove | `Corrective Hard Delete` | Clears bad data from day-to-day screens without losing traceability |
| Financial document with business mistake | `Void` or `Reverse` | Preserves accounting history instead of removing evidence |
| Posted journal or recognized revenue | `Reverse` | Keeps the original posting visible and creates an explicit counter-entry |
| Change after closing date / locked period | `Override` only | Forces an explicit exception path with stronger audit evidence |

## Hard delete guardrails
- Hard delete is allowed only through backend business actions, never through raw CRUD deletion from the UI.
- Hard delete requires:
  - `destructive.manage` permission.
  - explicit reason code and free-text reason.
  - impact preview with dependency checks.
  - full `before_json` snapshot in the audit trail.
  - lock-period validation.
  - rejection if the entity still has posted or active financial effects.
- Hard delete should be rare and treated as a corrective action, not a cleanup shortcut.

## Audit model target
- Expand `audit_logs` into an append-only system record with:
  - `occurred_at`, `actor_user_id`, `actor_name_snapshot`
  - `company_id`, `branch_id`
  - `request_id`, `session_id`, `ip_address`, `user_agent`
  - `source_layer`, `action_category`, `action_key`
  - `entity_type`, `entity_id`, `entity_label`
  - `version_before`, `version_after`
  - `reason_code`, `reason_text`
  - `before_json`, `after_json`, `diff_json`
  - `related_entities_json`
  - `success`, `error_code`
- Add tracked-entity fields to mutable business tables:
  - `created_by_user_id`, `updated_by_user_id`, `entity_version`
- Add archive fields to master and operational tables where restore is useful:
  - `is_archived`, `archived_at`, `archived_by_user_id`, `archive_reason`
- Add delete tombstone behavior through audit snapshots instead of keeping deleted rows in place.

## Permissions to add
- `audit.view`: read audit explorer, entity timelines, and destructive action reports.
- `destructive.manage`: run corrective hard delete for eligible entities.
- `destructive.restore`: restore archived entities.
- `period_lock.manage`: set or edit closing dates and approve overrides.
- `custody.view`: read custody lists and details.
- `custody.manage`: create and progress custody workflows.

## Product-wide audit coverage target
| Area | Required audited actions |
|---|---|
| Auth and session | login success, login failure, logout, forced session invalidation, language change |
| Identity | user create, user update, password reset, role assignment, activation changes |
| Organization | company update, branch create, branch switch, branch update |
| Customers | create, update, archive, restore, corrective delete |
| Catalog | department/service create, update, archive, restore, corrective delete |
| Dresses | create, update, archive, restore, corrective delete, operational status change |
| Bookings | create, update, complete line, cancel line, reverse revenue, archive, corrective delete when eligible |
| Payments | create, update, void, print/download, any future refund or correction action |
| Accounting | journal create, post, reverse, close-period exception |
| Custody | create, handover, customer return, laundry send/receive, settlement, compensation collection, archive |
| Exports and files | export download, PDF generation, schedule create/run/toggle, delivery handoff, backup create/download |
| Ops automation | alert test, stale-backup run, export batch run, scheduler-triggered jobs |

## Likely implementation touchpoints
- Backend platform foundation:
  - `backend/app/modules/core_platform/models.py`
  - `backend/app/modules/core_platform/service.py`
  - `backend/app/modules/core_platform/repository.py`
  - `backend/app/modules/core_platform/schemas.py`
- Backend request/auth integration:
  - `backend/app/main.py`
  - `backend/app/api/deps.py`
  - `backend/app/api/routes/auth.py`
- Backend business modules:
  - `backend/app/modules/identity/`
  - `backend/app/modules/organization/`
  - `backend/app/modules/customers/`
  - `backend/app/modules/catalog/`
  - `backend/app/modules/dresses/`
  - `backend/app/modules/bookings/`
  - `backend/app/modules/payments/`
  - `backend/app/modules/accounting/`
  - `backend/app/modules/exports/`
  - new `backend/app/modules/custody/`
- Frontend touchpoints:
  - `frontend/src/components/AppShell.tsx`
  - `frontend/src/pages/CustomersPage.tsx`
  - `frontend/src/pages/DressesPage.tsx`
  - `frontend/src/pages/BookingsPage.tsx`
  - `frontend/src/pages/PaymentsPage.tsx`
  - `frontend/src/pages/FinanceDashboardPage.tsx`
  - new audit explorer page and custody page
- Test coverage touchpoints:
  - `backend/tests/`
  - `frontend/tests/e2e/`
  - focused regression around destructive actions, auth audit, and period locks

## Checkpoint roadmap

### Checkpoint 9A: Audit foundation and request context
- Backend:
  - expand `audit_logs` schema
  - create a shared `AuditContext`
  - add middleware for `request_id`, `session_id`, `ip_address`, `user_agent`, and active branch capture
  - audit login success, login failure, logout, and permission-denied events
- Frontend:
  - no major UI work beyond handling audited auth flows cleanly
- Validation:
  - backend tests for request-context capture and auth audit events
  - docs updates

### Checkpoint 9B: Entity tracking standard
- Backend:
  - add `created_by`, `updated_by`, and `entity_version` to mutable entities
  - adopt shared tracked-entity helpers across organization, identity, customers, catalog, dresses, bookings, payments, and accounting-linked records
- Frontend:
  - surface basic created/updated metadata where already natural
- Validation:
  - migration tests
  - focused service tests confirming version increments

### Checkpoint 9C: Archive / inactive framework
- Backend:
  - add archive fields and business actions for customers, departments, services, dresses, and later other eligible master data
  - add restore workflow
- Frontend:
  - archive and restore dialogs
  - active/inactive filters on affected screens
- Validation:
  - backend permission tests
  - frontend build validation

### Checkpoint 9D: Corrective hard delete framework
- Backend:
  - create a shared corrective-delete policy service
  - add eligibility rules, dependency checks, and audit tombstones
  - reject delete when the record is financially posted, period-locked, or still referenced by protected flows
- Frontend:
  - destructive confirmation dialog with impact preview and reason capture
- Validation:
  - backend tests for allow/block scenarios
  - docs updates

### Checkpoint 9E: Period lock and exception reporting
- Backend:
  - add closing date / period lock settings
  - add override workflow and exception audit action
  - protect bookings, payments, accounting reversal, and corrective delete from post-close silent changes
- Frontend:
  - settings UI for lock dates
  - exceptions-to-closing-date reporting entry point
- Validation:
  - focused backend tests
  - focused frontend verification

### Checkpoint 9F: Custody foundation
- Backend:
  - add `custody` module, migration, permissions, repository, service, and routes
  - create list/create/detail workflows
- Frontend:
  - custody page and shell navigation
  - list, search, and detail drawer foundation
- Validation:
  - backend API tests
  - frontend build validation

### Checkpoint 9G: Custody workflow and financial safeguards
- Backend:
  - implement custody actions: create, handover, customer return, laundry send/receive, settlement, compensation collection
  - link compensation safely to payment documents and accounting history
- Frontend:
  - custody workflow dialogs and action buttons
  - status timeline on custody detail
- Validation:
  - end-to-end custody workflow tests
  - accounting consistency checks

### Checkpoint 9H: Details drill-down and entity timeline
- Backend:
  - add audit query endpoints and cross-entity detail endpoints where useful
- Frontend:
  - customer -> bookings
  - dress -> bookings
  - booking -> payments / custody
  - entity audit timeline panel
- Validation:
  - focused backend tests
  - focused UI validation

### Checkpoint 9I: Finance chart parity
- Backend:
  - reuse existing dashboard data contracts where possible
- Frontend:
  - add daily income chart
  - add department income chart
  - add top services chart
- Validation:
  - UI verification that chart totals match existing summaries

### Checkpoint 9J: Audit explorer and reporting
- Backend:
  - add searchable audit list endpoints
  - add destructive-actions report endpoint
  - add custody export endpoint(s)
- Frontend:
  - audit explorer page
  - filters by actor, action, entity, date, branch, and risk category
  - destructive actions report
- Validation:
  - backend tests
  - frontend build validation

### Checkpoint 9K: Audit coverage enforcement
- Backend:
  - route inventory for all write endpoints
  - coverage tests or guardrails that fail when a write route produces no audit event
  - standardize background-job audit records
- Validation:
  - route-level audit assertions
  - docs updates and handoff

### Checkpoint 9L: Mobile polish and final hardening
- Frontend:
  - responsive polish for the highest-frequency flows: bookings, payments, custody, destructive dialogs, drill-down panels
- Validation:
  - browser smoke around archive, delete, void, custody, and timeline visibility
  - final roadmap handoff

## Out of scope for this roadmap
- public customer portal
- WhatsApp or external messaging workflow expansion
- large BI-style analytics stack
- enterprise-only grid features

## Delivery rule
- The roadmap is intentionally split into small checkpoints.
- The correct next slice is `Checkpoint 9A`, not a large all-at-once rebuild.
