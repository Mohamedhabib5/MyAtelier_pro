# Decision Log

## Project-wide decisions
- The project is rebuilt as a modular monolith, not as microservices.
- The owner is not a programmer, so Codex must deliver the product in small checkpoints.
- Each checkpoint must stay reviewable, documented, and easy for future Codex sessions to extend.
- Security review is part of every checkpoint, not a final-stage task.
- Files should stay small enough for future Codex review and edits.

## Checkpoint 2A decisions
- Security hardening was implemented before the first business module.
- Session auth remains cookie-based for the internal web app.
- Sensitive downloads such as backups must be validated and audited server-side.

## Checkpoint 2B-2E decisions
- Accounting foundation was built before CRM and bookings.
- Journal posting and trial balance are available before operational modules.
- The first accounting UI remains read-only until later finance workflows exist.

## Checkpoint 3A decisions
- Customers are the first business module after accounting.
- Both `admin` and `user` can manage customers in this phase to match the current product direction.
- Customer phone numbers must be unique within the active company.
- Customer deletion is intentionally deferred to keep the slice small and safer.

## Checkpoint 3B decisions
- Departments and services are implemented together as one small catalog slice.
- The frontend uses one `الخدمات` page with two clear sections to keep navigation simple.
- Both `admin` and `user` can manage the catalog in this phase.
- Delete flows remain deferred to reduce destructive risk early in development.

## Checkpoint 3C decisions
- Dress resources are implemented as one small operational slice before bookings.
- This slice stores image metadata only; actual upload workflow is intentionally deferred.
- Both `admin` and `user` can manage dresses in this phase.
- Dress deletion remains deferred to reduce destructive risk before booking linkage exists.

## Checkpoint 4A decisions
- Bookings are implemented as a document-style operational slice before payments.
- Booking numbers use a dedicated document sequence instead of ad-hoc generated text.
- Dress conflict checking is enforced server-side from the first booking slice.
- Booking deletion remains deferred to reduce destructive risk before payments are linked.

## Checkpoint 4B decisions
- Payments are implemented as receipt-style financial movements linked to bookings.
- The first payment slice supports deposit, payment, and refund using one unified model.
- Remaining balance is calculated server-side and stored on each receipt.
- Payment deletion remains deferred to reduce destructive and audit risk at this stage.

## Checkpoint 4C decisions
- Dashboard parity is implemented as a read-only finance summary slice before broader analytics.
- Both `admin` and `user` can view dashboard metrics through the new `finance.view` permission.
- The dashboard becomes the default landing page after login to match the old product flow more closely.
- Shell navigation now exposes all implemented business pages so the new app shape stays familiar.

## Checkpoint 5A decisions
- Broader reporting is implemented as a read-only slice after the finance dashboard.
- Both `admin` and `user` can view reports through the new `reports.view` permission.
- Reporting stays operational and summary-focused; exports and scheduled reporting remain deferred.
- The reporting page is separate from the dashboard so each page stays small and easier for Codex to maintain.

## Checkpoint 5B decisions
- The active branch is stored in the authenticated session instead of being passed on every request.
- Branch switching is treated as an authenticated settings action and refreshes the current shell context.
- Bookings, payments, dashboard, and reports now respect the active branch by default.
- Company-wide master data such as customers, services, and dresses remain shared in this slice to keep the checkpoint small.

## Checkpoint 5C decisions
- Payment receipts now own the first operational-to-accounting bridge in the product.
- Every new payment receipt auto-posts a journal entry server-side in the same workflow.
- Updating a payment preserves accounting history by reversing the old linked journal and posting a replacement.
- Customer collections in this slice are posted to `2100 عربون العملاء`; revenue recognition is intentionally deferred.
- A small PostgreSQL alignment migration was added so business-table timestamps in live environments match the ORM server defaults.

## Checkpoint 6A decisions
- Exports are introduced as a small CSV-only slice instead of a large reporting rewrite.
- Both `admin` and `user` can download exports through the new `exports.view` permission.
- Customers exports stay company-wide, while bookings and payments exports respect the active branch.
- Export downloads are audited so data extraction stays traceable.

## Checkpoint 6B decisions
- Backend startup now uses FastAPI lifespan instead of deprecated startup events.
- Frontend route loading now uses React lazy-loading with a shared Suspense fallback to stay compatible with `react-router-dom@7`.
- Vendor chunk splitting is explicit so the production build stays cleaner and easier to reason about.
- This checkpoint is treated as technical stabilization, not as another business-feature expansion.

## Checkpoint 6C decisions
- Safe payment voiding is introduced before any generic delete flow.
- Voiding requires a business reason and keeps the original receipt for auditability.
- Voiding a payment reverses its linked journal entry instead of deleting accounting history.
- Voided payments are excluded from financial summaries and remaining-balance calculations.
- Generic destructive delete flows remain deferred until a later, separately designed slice.

## Checkpoint 6D decisions
- Printable exports are implemented as browser print views instead of adding a heavy server-side PDF pipeline now.
- Finance and reports are the first printable views because they are the highest-value summaries.
- Printable routes are kept behind the authenticated frontend guard.
- Server-generated PDF files remain deferred until there is a stronger business need.

## Checkpoint 6E decisions
- Saved export schedules are implemented as a lightweight foundation, not as a background job system.
- Schedule actions are restricted to `exports.manage`, while actual downloads still use the existing authenticated export routes.
- Branch-aware schedule runs reuse backend branch-scope validation and do not trust frontend state alone.
- Run-now returns a safe URL so the product stays simple and Codex-friendly before introducing workers or delivery channels.

## Checkpoint 6F decisions
- Revenue recognition is triggered through an explicit booking-completion business action, not through free-form status editing.
- Booking completion debits `2100 عربون العملاء` for collected amounts, debits `1200 ذمم العملاء` for the remaining amount, and credits `4100 إيرادات الخدمات` for the full quoted price.
- Completed bookings are locked after recognition in this phase to keep operations and accounting aligned.
- Automatic reversal of booking revenue recognition is intentionally deferred to keep this slice small and auditable.


## Checkpoint 7A decisions
- Bookings are now document headers with multiple service lines instead of single-service records.
- Payments are now payment documents with allocation lines instead of one receipt per booking.
- One payment document may span multiple booking lines and multiple bookings for the same customer and active branch.
- Initial payments entered from the booking editor are converted into one payment document automatically after booking save.
- Paid totals and remaining balances on booking lines are derived from payment allocations, not edited as source-of-truth values.
- Revenue recognition remains line-based and line completion is the explicit business action that triggers it.
- The refund redesign is intentionally deferred so this slice can focus on collections and stay auditable.


## Checkpoint 7B decisions
- Live smoke validation is treated as its own small checkpoint because it surfaced a real production-like schema issue.
- The frontend container now uses Alpine system Chromium for Playwright instead of relying on downloaded Playwright browser binaries inside the dev container.
- A small PostgreSQL-only alignment migration is preferred over another broad booking rewrite because the application code was already correct and only the live schema lagged behind.
- The browser smoke stays intentionally narrow and stable: it validates the end-to-end redesigned flow without becoming a brittle UI detail test.


## Checkpoint 7C decisions
- Backup verification is treated as its own checkpoint because an archive that cannot restore the database is not operationally sufficient.
- Backup archives now include a plain SQL database dump in addition to attachment files.
- There is still no restore UI in the product; restore remains an operational procedure verified against a throwaway database only.
- PostgreSQL dump normalization is preferred over a larger backup rewrite because it keeps the slice small while aligning with the current PostgreSQL 16 runtime.

## Checkpoint 7D decisions
- Arabic wording recovery is implemented with small per-domain text modules instead of introducing a large i18n framework now.
- Backend validation and not-found messages are translated only where they are user-facing; authorization logic and workflow rules stay unchanged.
- Booking dress behavior now depends on stable `department.code` rules instead of display text.
- Text corruption prevention is enforced through UTF-8 guardrails and a source-level integrity check, not through manual review alone.

## Checkpoint 8A decisions
- Production-readiness is implemented as startup guardrails first, not as a large deployment rewrite.
- The app must fail fast in production if secrets, cookie policy, CORS origins, or trusted hosts are unsafe.
- `SESSION_SAME_SITE` values are now validated explicitly, and `SameSite=None` is only allowed with secure cookies.
- Localhost and wildcard frontend origins are blocked in production to reduce accidental overexposure.

## Checkpoint 8B decisions
- Deployment-edge hardening is implemented as runnable infra templates plus a runbook, not as immediate platform-specific lock-in.
- Nginx is used as the reference edge because it is simple for small-team operations and easy to audit.
- HTTPS redirect, forwarded protocol headers, and strict security headers are required defaults in the edge template.
- Post-deploy operations checks are deferred to the next small checkpoint to keep this slice reviewable.

## Checkpoint 8C decisions
- Post-deploy operations confidence is implemented before optional advanced business workflows.
- Backup retention policy is now explicit (`14` daily, `8` weekly, `12` monthly) to avoid ad-hoc cleanup risk.
- Restore drills remain scheduled operational procedures against throwaway databases, not in-app restore actions.
- Alerting is defined first as baseline priorities and channels; specific monitoring stack implementation is deferred to the next small slice.

## Checkpoint 8D decisions
- Alerting-stack implementation starts with authenticated operations endpoints, not with an unauthenticated public metrics surface.
- Webhook alert testing supports dry-run first to keep verification safe in non-production environments.
- Alert test events are always audited for operational traceability.
- Automatic scheduling of stale-backup checks is deferred to keep this slice small and reviewable.

## Checkpoint 8E decisions
- Stale-backup checking is implemented as a callable backend workflow before adding full scheduler infrastructure.
- Scheduler integration is provided through a small runner script so operations can adopt it incrementally per environment.
- Automated check runs are audited (`ops.backup_stale_check_run`) for traceability and post-incident review.
- Environment-specific scheduler wiring remains a separate checkpoint to avoid cross-platform deployment complexity in one slice.

## Checkpoint 8F decisions
- Windows Task Scheduler is implemented first as the concrete scheduler path because current operations environment is Windows-first.
- Scheduler register/unregister scripts are provided to keep rollout and rollback simple for non-programmer operations.
- Linux and Kubernetes scheduler wiring remain separate slices to avoid mixed-platform complexity in one checkpoint.

## Checkpoint 8G decisions
- Linux Cron is implemented as the second concrete scheduler path to achieve cross-platform parity with Windows.
- Cron entries are managed with marker blocks to avoid destructive edits to unrelated crontab lines.
- Kubernetes scheduler wiring remains a separate checkpoint to keep this slice small and infrastructure-agnostic.

## Checkpoint 8H decisions
- Kubernetes CronJob is implemented as the orchestration-native scheduler path after Windows/Linux parity.
- Manifest keeps credentials/config in Secret and ConfigMap placeholders to avoid hardcoding in job command lines.
- Cluster-specific RBAC and namespace hardening remain deployment-owned concerns outside this checkpoint scope.

## Checkpoint 8I decisions
- Due export schedules are executed through an explicit backend batch endpoint instead of implicit startup hooks.
- Batch execution supports `dry_run` and `limit` to reduce risk during operations rollout.
- Background schedule execution remains authorization-protected under `exports.manage`.

## Checkpoint 8J decisions
- Delivery-channel expansion starts with webhook handoff to keep integration lightweight and environment-agnostic.
- Delivery remains optional (`notify=false` by default) to preserve existing schedule-run behavior.
- Delivery tests rely on dry-run mode first to avoid external network dependency in core test suite.

## Checkpoint 8K decisions
- Server-generated PDF exports are implemented with a lightweight backend generator to avoid introducing heavy rendering dependencies now.
- Finance and reports are the first server-generated PDF endpoints because they are the highest-value summary outputs.
- PDF generation stays read-only and authorization-protected under existing export permissions.

## Checkpoint 8L decisions
- Revenue-recognition reversal is implemented as an explicit booking-line business action, not as free-form status editing.
- Reversal creates a posted reversing journal and marks the original revenue journal as `reversed` to preserve accounting history.
- After a successful reversal, the booking line reopens to `confirmed` and removes the linked revenue-journal reference.
- Reversal is blocked when active receivables collections exist for the line to avoid inconsistent customer-balance state.

## Checkpoint 8M decisions
- Tax behavior is introduced as a narrow accounting slice, not as a full tax engine.
- Tax rate is stored at service level and snapshotted on booking lines to preserve historical posting context.
- Revenue recognition now credits net service revenue to `4100` and credits tax payable to `2200`.
- Recognition still debits advances/receivables using full gross line amount, keeping customer-balance behavior consistent.

## Checkpoint 8N decisions
- Heavy operational tables move to dedicated paged endpoints instead of changing the legacy list endpoints in place.
- Server-side search, filter, sort, and paging are introduced first for bookings and payments because they are the largest day-to-day document lists.
- Column visibility and order remain a frontend preference concern for now and are stored locally to avoid adding user-preference persistence in the same slice.

## Checkpoint 8O decisions
- `AG Grid Community` is now the single grid engine for the frontend so the product has one consistent table behavior across list screens and editor grids.
- We intentionally stay on the free community edition and keep `XLSX` export in the backend while using AG Grid CSV export in the browser.
- Bookings and payments keep server-driven paging/search/filter contracts, while smaller screens use client-side AG Grid to avoid unnecessary backend churn.
- Booking and payment editor tables also move to AG Grid, but validation and business rules remain in the existing form/service layers instead of being embedded in grid logic.
- Table preferences remain local-storage based in this checkpoint to keep the migration reviewable and avoid mixing UI migration with user-profile persistence.

## Planned Checkpoint 9 roadmap decisions
- Auditability becomes the next product-wide foundation before any broader delete rollout, custody expansion, or optional UX polish.
- The product follows a QuickBooks-style lifecycle:
  - archive / inactive for master data
  - corrective hard delete only for eligible wrong operational entries
  - void / reverse for financially effective history
- Hard delete is allowed, but only as a guarded backend business action with explicit reason, impact checks, and full tombstone audit evidence.
- Audit trail must be append-only and should preserve who acted, when they acted, what changed, why it changed, and the request context of the action.
- Mutable entities should adopt shared `created_by`, `updated_by`, and `entity_version` tracking so unlimited saved revisions stay visible over time.
- Login success, login failure, logout, permission-denied, and post-closing-date override actions are treated as audit-relevant events, not just business writes.
- Closing-date / period-lock behavior should land before broader destructive workflow rollout so late changes do not weaken financial control.
- Custody should be built only after the audit and data-lifecycle foundation is in place, because custody adds multi-step operational state plus compensation-related financial linkage.
- Backend-persisted table preferences and exact heavy-table export parity remain valuable, but they move below the audit/data-lifecycle roadmap in priority.

## Checkpoint 9A implementation decisions
- Request context capture is implemented once at middleware level (`request_id`, `session_id`, IP, user agent) so all service-layer audit writes can reuse it consistently.
- Permission-denied auth failures are now audited as explicit security events, not only returned as API errors.
- Authentication events (login success, login failure, logout) are now first-class audit events to support incident review and accountability.

## Checkpoint 9B implementation decisions (phase 1)
- Tracked-entity rollout starts with `customers` as a small vertical slice before extending to all mutable modules.
- `created_by_user_id`, `updated_by_user_id`, and `entity_version` are set in service-layer business workflows, not by UI assumptions.
- `entity_version` increments on every saved update to preserve an unlimited revision sequence that maps cleanly to audit history.

## Checkpoint 9B implementation decisions (phase 2)
- The same tracked-entity standard is now applied to `catalog` tables (`departments`, `service_catalog_items`) to keep auditability consistent across master data.
- Catalog create/update workflows now stamp actor IDs and bump `entity_version` on saved edits.
- API responses expose tracked metadata so future timeline screens can be built without schema rework.

## Checkpoint 9B implementation decisions (phase 3)
- Dress resource workflows now follow the same tracked-entity pattern (`created_by_user_id`, `updated_by_user_id`, `entity_version`).
- Every dress update increments `entity_version` and records the latest editor user ID.
- Dress API responses now expose tracked metadata for future audit timeline drill-down without additional breaking changes.

## Checkpoint 9B implementation decisions (phase 4)
- Booking headers and booking lines now adopt the tracked-entity standard so booking revisions can be traced at both document and line levels.
- Booking create/update and line state actions (complete/cancel/reverse) now stamp `updated_by_user_id` and increment `entity_version`.
- Booking responses now expose tracked metadata for both header and line payloads to support future audit timeline UI.

## Checkpoint 9B implementation decisions (phase 5)
- Payment documents and payment allocations now adopt the tracked-entity standard (`created_by_user_id`, `updated_by_user_id`, `entity_version`).
- Payment create/update/void workflows now increment payment-document `entity_version` and stamp the latest editor user.
- Payment responses now expose tracked metadata in both document and allocation payloads for audit timeline continuity.

## Checkpoint 9B implementation decisions (phase 6)
- Booking line materialization and initial-payment creation were extracted to `bookings/line_mutations.py` to keep service-layer files small and easier to review.
- `bookings/rules.py` now keeps normalized Arabic validation messages in UTF-8 so user-facing text remains readable and consistent.
- Booking service remains the orchestration layer while mutation details live in focused helpers, preserving the modular-monolith service boundary.

## Checkpoint 9B implementation decisions (phase 7)
- Payments service logic was split into focused helpers (`payments/rules.py`, `payments/allocation_builder.py`, `payments/document_access.py`) so business orchestration remains readable and easier to validate.
- Booking-origin payment creation was moved to a dedicated bridge (`payments/booking_bridge.py`) and called from bookings line mutations, keeping service files under the file-size discipline targets.
- Payment write workflows still keep actor stamping and `entity_version` increments, while module boundaries are now clearer for future audit and delete-policy extensions.

## Checkpoint 9C implementation decisions (phase 1)
- Customer archive/restore is implemented as explicit business actions, not as implicit side effects of generic update screens.
- Customer list filtering now supports `all`, `active`, and `inactive` states through backend query controls to prepare frontend archive-focused workflows.
- Archive and restore operations are audited with actor, reason, and `entity_version` so inactive-state transitions remain fully traceable.

## Checkpoint 9C implementation decisions (phase 2)
- Catalog archive/restore workflows for departments and services are implemented as explicit backend actions, with audit evidence for each state transition.
- Dresses archive/restore now follows the same pattern as customers and catalog, including status filtering on list endpoints.
- List APIs for customers, departments, services, and dresses now share one backend filtering contract (`status=all|active|inactive`) to keep frontend behavior predictable.

## Checkpoint 9C implementation decisions (phase 3)
- Frontend master-data screens now expose archive/restore as explicit user actions instead of relying only on edit forms.
- Customers and dresses pages now request server-filtered records by operational status while preserving existing local business filters.
- Catalog sections now support archive/restore actions in-place and keep status filter controls aligned with backend list contracts.

## Checkpoint 9D implementation decisions (phase 1)
- Corrective-delete foundation starts with a shared destructive-reason catalog so `void`, future `hard delete`, and archive workflows can use consistent reason codes.
- Reason-code catalog is exposed through one guarded settings endpoint to keep UI flows simple and avoid duplicating constants in frontend modules.
- Payment void now validates `reason_code` against the shared catalog and records structured `reason_code` in audit diff payloads while preserving existing free-text reason behavior.

## Checkpoint 9D implementation decisions (phase 2)
- Hard-delete rollout now adds a mandatory impact-preview step before execution so users can see dependencies and blockers first.
- Impact preview is currently enabled for `customer`, `department`, `service`, and `dress`, with conservative eligibility rules that block deletion when operational history exists.
- Preview action itself is audited (`destructive.previewed`) with reason code, computed impact, and eligibility outcome to preserve decision traceability.

## Checkpoint 9D implementation decisions (phase 3)
- Hard delete execution is now implemented as a guarded backend business action and is allowed only after the same server-side impact computation confirms eligibility.
- Delete execution re-validates impact at request time (no trust in old preview results) to reduce stale-decision risk.
- Deletion remains permission-gated (`destructive.manage`) and audited (`destructive.deleted`) with reason metadata and impact summary.

## Checkpoint 9D implementation decisions (phase 4)
- Hard-delete audit entries now include a tombstone-style `before snapshot` of the deleted entity so deletion evidence remains queryable after the row is removed.
- Tombstone payload currently records entity identity, business fields, tracking metadata, delete timestamp, and reason metadata inside the audit diff payload.
- Reason metadata is now written in both structured audit columns (`reason_code`, `reason_text`) and diff payload for easier reporting and backward compatibility.

## Checkpoint 9D implementation decisions (phase 5a)
- Frontend destructive flow starts with dresses as a small vertical slice before rolling the same pattern across customers and catalog.
- Corrective delete UI now enforces `reason -> preview -> confirm` sequence; delete action stays disabled unless backend preview marks the target eligible.
- File-size discipline is preserved by extracting dress form dialog and destructive dialog into focused components instead of growing the page into a catch-all module.

## Checkpoint 9D implementation decisions (phase 5b)
- The same frontend corrective-delete sequence is now extended to customers, departments, and services for lifecycle parity across master-data screens.
- Corrective-delete UI remains backend-driven for eligibility: blocked entities still show preview blockers and cannot execute delete.
- Additional form sections were extracted into focused dialog components to keep page complexity manageable while extending destructive controls.

## Checkpoint 9D implementation decisions (phase 5c)
- Destructive confirmation UX now surfaces impact counters in the dialog so users can review dependency scope before confirming delete.
- Frontend file-size discipline remains enforced while extending destructive controls; `CustomersPage` and `ServicesSection` were kept at the size target with extracted form-dialog components.
- This phase focuses on polish and consistency, while backend delete policy remains unchanged and fully server-authoritative.

## Checkpoint 9E implementation decisions (phase 1)
- Period lock is implemented as a lightweight backend settings foundation using `app_settings`, so rollout remains migration-light and easy to review.
- Closing-date lock edits are restricted by a dedicated permission (`period_lock.manage`) while period-lock reads remain under existing authenticated settings access.
- Financial-correction and destructive actions now enforce period lock server-side (`payment.update`, `payment.void`, `booking.line_revenue_reversed`, `destructive.delete`) so frontend visibility cannot bypass control.
- Period-lock changes are auditable through explicit `period_lock.updated` records with before/after lock date evidence.

## Checkpoint 9E implementation decisions (phase 2)
- Closing-date override is now an explicit server-side path (`override_lock + override_reason`) instead of an implicit bypass.
- Using override requires `period_lock.manage` even when the user already has module-level manage permissions.
- Successful override actions create dedicated audit evidence (`period_lock.override_used`) with action key, locked-through date, action date, and override reason.
- Exception reporting is exposed through `/api/settings/period-lock/exceptions` for controlled operational review.

## Checkpoint 9E implementation decisions (phase 3)
- Period-lock management and exception-report visibility are now exposed in the frontend settings screen through a dedicated section.
- UI keeps period-lock controls in a focused component to preserve file-size discipline and reduce future maintenance risk.
- Frontend destructive delete and payment-void workflows now expose optional override inputs so approved exceptions can be executed without backend rule bypasses.
- Booking revenue-reversal UI now supports a controlled override retry path when the first attempt is blocked by period lock.

## Checkpoint 9E implementation decisions (phase 4)
- Booking revenue-reversal override flow now uses a dedicated dialog instead of browser prompt/confirm for safer and more consistent UX.
- Payment-document update now supports period-lock override from frontend when lock blocks correction.
- Payments page was split with a dedicated table section component to keep file-size discipline aligned with the architecture rules.

## Checkpoint 9F implementation decisions (phase 1)
- Custody foundation starts with a small, auditable `custody_cases` backend module (list/create/detail) before workflow expansion.
- Custody access is permissioned explicitly through `custody.view` and `custody.manage`.
- Initial custody numbering uses a simple branch-scoped sequence pattern (`CUS-000001`) to keep the first slice minimal and reviewable.
- Frontend custody page is intentionally lightweight: create form + list table, leaving status-timeline actions for the next checkpoint.

## Checkpoint 9G implementation decisions (phase 1)
- Custody workflow transitions are exposed as explicit backend actions (`/api/custody/{case_id}/actions`) instead of free-form status edits.
- Transition guardrails are enforced server-side with allowed action maps per status.
- Each workflow action writes a dedicated custody audit event (`custody.<action_key>`) with previous/next status evidence.

## Checkpoint 9G implementation decisions (phase 2)
- Custody compensation collection is implemented as an explicit backend business action (`POST /api/custody/{case_id}/compensation`) instead of ad-hoc payment creation.
- Compensation collection requires both custody-management and payment-management permissions to protect financial operations.
- Compensation creates a linked `payment_document` of kind `custody_compensation` with a direct amount (without booking-line allocations) and auto-posts accounting evidence.
- Custody case keeps direct evidence of the compensation linkage (`amount`, `collection date`, `payment document id`) and blocks duplicate collection.

## Checkpoint 9G implementation decisions (phase 3)
- Custody timeline is exposed as a dedicated endpoint (`GET /api/custody/{case_id}/timeline`) instead of embedding raw audit queries in generic settings routes.
- Timeline combines custody-case events with compensation-linked payment/accounting events so operational and financial evidence remain connected.
- Frontend timeline view is implemented as a focused custody feature component to keep page file sizes under control and preserve maintainability.

## Checkpoint 9H implementation decisions (phase 1)
- Cross-entity drill-down starts from custody as a narrow vertical slice to keep delivery small and verifiable.
- Custody drill-down endpoint returns linked customer, dress, and compensation-payment details together so users can inspect operational and financial context quickly.
- Frontend drill-down section is implemented as a dedicated custody feature component to preserve file-size discipline on the main custody page.

## Checkpoint 9H implementation decisions (phase 2)
- Custody drill-down response now includes recent bookings and recent payments linked to the same customer in the active branch.
- This keeps cross-entity navigation lightweight without requiring users to leave the custody page for basic linkage checks.
- Recent-link tables are kept read-oriented and compact so backend contracts stay simple and frontend file-size discipline remains intact.

## Checkpoint 9I implementation decisions (phase 1)
- Finance chart parity is implemented in frontend using lightweight bar-chart components without introducing a new chart library dependency.
- Existing dashboard API contracts and totals remain unchanged; charts are visualizations of already-available backend metrics.
- Daily income, department income, and top services cards now show both compact chart and list views for quick visual scan plus exact values.

## Checkpoint 9J implementation decisions (phase 1)
- Audit explorer foundation is implemented as a dedicated backend route (`/api/audit/events`) guarded by `audit.view`.
- Filtering is server-side (actor/action/target/branch/date/search) to keep large audit logs queryable without loading all rows to the browser.
- Frontend audit explorer page is kept read-only and table-driven for safe first delivery, with admin-focused navigation exposure.

## Checkpoint 9J implementation decisions (phase 2)
- Destructive-actions reporting is implemented as a dedicated audit endpoint (`/api/audit/destructive-actions`) using a server-side curated action set.
- Audit explorer UI now supports a destructive-only mode toggle without changing existing all-events query behavior.
- Custody export refinement adds native CSV/XLSX custody datasets to the export center so operations can extract custody workflow evidence directly.

## Checkpoint 9K implementation decisions (phase 1)
- Audit-coverage enforcement starts as focused guardrail tests over high-value write workflows instead of trying to inventory every route in one large slice.
- Guardrail assertions verify both action existence and request-context linkage (`x-request-id`) so audit records remain traceable to API calls.
- First enforced workflows are customer lifecycle writes (`create/update/archive/restore`) and payment voiding with structured reason-code evidence.

## Checkpoint 9K implementation decisions (phase 2)
- Background and automation workflows now write one standardized audit action (`automation.job_run`) instead of fragmented per-endpoint action names.
- Standardized automation audit records use `target_type=automation_job` and `target_id=<job_key>` so report filtering remains simple and consistent.
- Each automation audit payload now includes both `job_key` and `trigger_source` (`manual` or `automation`) to distinguish user-triggered runs from scheduler-triggered runs.

## Checkpoint 9K implementation decisions (phase 3)
- Write-route governance now uses a centralized policy inventory (`write_route_audit_policy`) that maps each mutable API route to explicit expected audit action keys.
- A guardrail test now compares runtime-registered write routes against the policy inventory; any new mutation route fails CI until audit policy is declared.
- Session-language updates and active-branch switching are now explicitly audited to close write-route coverage gaps in user-session operations.

## Checkpoint 9L implementation decisions (phase 1)
- Mobile responsiveness now prioritizes correction-heavy workflows (destructive delete, archive/restore reason dialogs, period-lock override, and payment void) before broader cosmetic layout changes.
- Critical dialogs now switch to full-screen mode on small breakpoints with stacked full-width action buttons to reduce accidental taps and improve readability in Arabic/RTL layouts.
- Custody action sections now favor full-width mobile actions and compact responsive field grouping so operational workflows remain practical on phone-sized screens.

## Checkpoint 9L implementation decisions (phase 2)
- Final smoke validation is executed as focused Playwright scenarios (`smoke` + `lifecycle`) instead of broad flaky suites, to keep close-out deterministic.
- Lifecycle smoke was updated to match current product behavior (dialog/API-driven archive/restore flow) and to remove legacy prompt-dialog assumptions.
- Local E2E execution now follows a controlled temporary runtime bootstrap (SQLite-backed backend + local Vite frontend) with explicit shutdown after test completion.

## Roadmap closeout decisions
- Final roadmap closure is documented through a dedicated handoff summary plus a final operational readiness checklist.
- Future work should move to a new checkpoint series instead of extending the 9x roadmap.
- The first post-roadmap candidate remains backend-persisted table preferences to reduce local-device preference drift risk.

## Checkpoint 10A implementation decisions (phase 1)
- Grid preferences are now persisted per authenticated user in backend storage, while local storage remains a fallback cache for resilience.
- Preference persistence is modeled by `(user_id, table_key)` to isolate preferences across users and grids without over-generalized settings blobs.
- Preference updates are audited (`user.grid_preferences_updated`) and included in write-route audit policy to preserve mutation-governance guarantees.

## Checkpoint 10A implementation decisions (phase 2)
- Preference hydration now compares local cache timestamp against backend `updated_at` and applies the newer source to reduce accidental stale overwrites.
- Legacy local preference shape is still accepted and normalized so existing users do not lose prior table setup after migration.
- Sync behavior is debounced and skips redundant writes when state matches the last synced payload, lowering unnecessary backend churn.

## Checkpoint 10B implementation decisions (phase 1)
- Export parity is implemented by reusing the same server-side table contracts (`list_booking_page` and `list_payment_page`) so filter/sort behavior stays consistent between grid and export.
- Export routes accept table-equivalent query filters directly, while branch scope and authorization remain server-enforced in the existing export service workflow.
- Route-level filter parsing is centralized through small dependency helpers to avoid duplicated parameter wiring and keep `exports.py` under the file-size discipline target.

## Checkpoint 10B implementation decisions (phase 2)
- Frontend XLSX actions on heavy tables now send the same active server-side filters and sort fields as the currently visible grid state, so exports match operator context.
- Export URL composition for bookings and payments is centralized in `features/exports/api.ts` through typed filter payloads to reduce link drift between pages.
- Export parity validation now includes alias-route behavior (`payment-documents.csv`) and deterministic booking sort-direction checks to harden the export contract.

## Checkpoint 10B implementation decisions (phase 3)
- Export parity now extends to line/allocation datasets by reusing filtered booking/payment row collectors before resolving detailed document lines and allocations.
- Booking-lines exports now inherit booking table filters; payment-allocation exports now inherit payment table filters, preserving one operational filtering contract.
- `exports/service.py` was reduced and split into `exports/row_collectors.py` so export orchestration and data collection remain readable and under size-discipline control.

## Checkpoint 10C implementation decisions (phase 1)
- Export Center now exposes lightweight filter controls for bookings and payments so operators can run filtered CSV/XLSX exports without leaving the export screen.
- Filtered-link composition was extended for booking-lines and payment-allocation endpoints to keep all related export actions aligned to one filter contract.
- A dedicated in-page hint was added to reinforce “current view export” behavior and reduce accidental full-dataset extraction.

## Checkpoint 10C implementation decisions (phase 2)
- Export-center link parity is now covered by dedicated Playwright E2E tests that assert query-string propagation from UI filter inputs.
- Initial E2E scope targets the highest-risk links first (`bookings.csv` and `payment-allocations.csv`) before broadening to all export endpoints.
- E2E assertions focus on URL contract stability (request query evidence), while backend export content correctness remains covered by existing backend tests.

## Checkpoint 10D implementation decisions (phase 1)
- Frontend file-size hardening starts with `BookingsPage` by extracting table rendering, page header, and override dialog wrappers into focused feature components.
- Refactor preserves existing booking behavior and query/mutation contracts while reducing single-file cognitive load for future Codex edits.
- Build validation is run immediately after the split to catch import/type regressions before moving to the next page-splitting slice.

## Checkpoint 10D implementation decisions (phase 2)
- Booking action orchestration (`create/update/line actions/override`) is centralized in `useBookingActions` so page components focus on state wiring and rendering only.
- The page-size target is treated as an explicit engineering constraint; component + hook extraction continues until `BookingsPage` is comfortably below the preferred threshold.
- Behavior parity is protected by preserving the same backend API contracts and running frontend production build validation after refactor.

## Checkpoint 10E implementation decisions (phase 1)
- Refactor safety for heavy pages is validated with focused Playwright runtime checks (`bookings-dialog` and `booking-payment-redesign`) instead of broad E2E suites.
- Local E2E execution uses temporary backend/frontend listeners with explicit teardown so the slice remains reproducible and low risk.
- Backend route-size discipline is now verified as compliant (`exports.py` and `settings.py` are both below `250` lines), so the next size-hardening target moves to oversized service files.

## Checkpoint 10E implementation decisions (phase 2)
- Export service hardening starts by extracting format/render/audit helpers into a dedicated module so export business flows stay readable and reusable.
- Master-data export actions (customers/custody) now live in a focused module, while `exports.service` remains the stable import surface for API routes.
- Size target enforcement is measured per slice; `exports/service.py` is now below the preferred limit before moving to the next oversized service file.
- Payment custody-compensation creation was moved to its own module so `payments.service` focuses on core payment-document workflows.
- Booking service now delegates sequence/scope lookup and list/page queries to dedicated modules, reducing service coupling and keeping write workflows easier to reason about.
- After this phase, all backend module files satisfy the preferred `<=250`-line target.

## Checkpoint 10F implementation decisions (phase 1)
- New guardrail tests now enforce file-size targets for key service entrypoints (`bookings`, `payments`, `exports`) so regressions fail fast in CI.
- API route boundary discipline is now test-enforced: routes must import stable service entrypoints and cannot depend directly on helper modules.
- Export line/allocation detail workflows moved into `exports/detail_exports.py` to keep `exports.service` as a lightweight orchestration and import surface module.

## Checkpoint 10F implementation decisions (phase 2)
- Guardrail tests now use one dedicated pytest marker (`guardrail`) so CI can run fast architecture-quality checks with one command.
- Frontend guardrails target operationally critical heavy pages first (`Bookings`, `Payments`, `Exports`, `Custody`, `Settings`) to keep this slice small and non-blocking.
- `UsersPage.tsx` currently remains above the preferred size target and is intentionally deferred to the next isolated refactor slice.

## Checkpoint 10F implementation decisions (phase 3)
- `UsersPage` refactor is delivered as UI-composition extraction (admin table, profile section, and admin dialog) to reduce page size without changing business behavior.
- Frontend size guardrails now include `UsersPage.tsx` after refactor completion so future growth is blocked automatically.
- Guardrail profile remains fast and stable (`pytest -m guardrail`) while now covering both backend service boundaries and selected frontend heavy pages.

## Checkpoint 10G implementation decisions (phase 1)
- CI guardrail enforcement is introduced as a dedicated GitHub Actions workflow (`.github/workflows/guardrails.yml`) with one explicit command path (`python -m pytest -m guardrail`).
- Guardrail workflow is treated as a required pre-merge gate and is intentionally kept fast by limiting scope to marker-selected tests.
- Release-gate policy is documented in one standalone doc (`docs/guardrail-release-gate.md`) so pass/fail rules and operator response stay consistent across sessions.

## Checkpoint 10G implementation decisions (phase 2)
- CI release gate now runs in ordered stages: backend guardrail profile first, frontend production build second.
- Frontend build job depends on guardrail success (`needs: guardrails`) to fail fast and reduce unnecessary CI runtime on broken guardrail branches.
- Release-gate documentation now treats both checks as merge criteria, with explicit local rerun commands for operator recovery.

## Checkpoint 10H implementation decisions (phase 1)
- Workflow runtime is optimized without widening scope by enabling pip dependency cache and cancel-in-progress concurrency for same-ref reruns.
- Branch-protection rollout is documented as a dedicated operational guide with exact required check names to avoid configuration drift.
- Release-gate policy now links to branch-protection instructions so quality checks become enforceable governance, not just advisory CI signals.

## Checkpoint 10H implementation decisions (phase 2)
- CI operator support is documented through one runbook containing timing benchmarks, local reproduction commands, and repeatable troubleshooting rules.
- Gate troubleshooting guidance stays operational (no code-level policy changes), keeping this slice lightweight and low-risk.
- Release-gate docs now explicitly route operators to the CI runbook so failure response remains consistent across maintainers.

## Checkpoint 10I implementation decisions (phase 1)
- Broader regression validation is introduced as a separate nightly/manual workflow so PR merge gates remain fast and deterministic.
- Nightly workflow scope is intentionally focused: selected backend high-risk modules, frontend production build, and smoke E2E scenarios.
- Nightly results are advisory for platform confidence and do not replace required branch-protection checks (`guardrails`, `frontend-build`) on pull requests.

## Checkpoint 10I implementation decisions (phase 2)
- Nightly workflow observability is improved by always uploading artifacts for logs/runtime evidence and Playwright report bundles with a fixed retention window.
- Failure handling now includes concise job-level summaries in `GITHUB_STEP_SUMMARY` to reduce triage time and standardize first response.
- Operator documentation now explicitly aligns nightly troubleshooting with artifact names and retention policy.

## Checkpoint 10J implementation decisions (phase 1)
- Nightly notifier is implemented as an optional post-run stage so notifications do not affect core test job execution order.
- Notification delivery is secret-gated (`NIGHTLY_FAILURE_WEBHOOK_URL`) and skipped gracefully when not configured.
- Payload remains summary-focused (job results + run URL) to support lightweight external handoff without leaking full logs.

## Checkpoint 10J implementation decisions (phase 2)
- Notifier payload is now documented as an explicit contract (`docs/nightly-failure-notifier-contract.md`) so receiver integrations remain stable across future workflow edits.
- Receiver guidance requires idempotency on (`run_id`, `run_attempt`) to avoid duplicate incident creation during reruns.
- Notifier rollout uses a manual verification checklist (success-no-send + controlled-failure-send) before production activation.

## Checkpoint 10K implementation decisions (phase 1)
- Nightly webhook ingestion is implemented as a dedicated backend route with shared-secret header guard (`X-Nightly-Token`) instead of session auth, because the caller is GitHub Actions automation.
- Ingested nightly failure payload is preserved as latest snapshot for admin read access and also written to audit trail (`ops.nightly_failure_reported`) for traceability.
- Latest nightly status is exposed as a small read-only settings API contract before any frontend UI expansion, keeping the slice small and independently testable.

## Checkpoint 10K implementation decisions (phase 2)
- Nightly operational visibility is added as a dedicated read-only settings section so operators can inspect status without leaving the app.
- The panel remains non-mutating and depends only on existing backend snapshot API to avoid adding new write paths or security surface.
- Stage results are displayed as simple status chips plus direct run URL link, prioritizing fast triage over heavy dashboard complexity.

## Checkpoint 10K implementation decisions (phase 3)
- Nightly notifier keeps external webhook support while adding optional direct-ingest channel to MyAtelier backend, so rollout can be incremental and reversible.
- Direct ingest is secrets-gated (`NIGHTLY_FAILURE_INGEST_URL`, `NIGHTLY_FAILURE_INGEST_TOKEN`) and skipped gracefully when not configured.
- Operations runbook now treats token rotation and channel-disable rollback as first-class procedures to reduce incident risk during notifier maintenance.

## Checkpoint 10L implementation decisions (phase 1)
- Nightly operations review is implemented as a dedicated audit preset endpoint instead of relying on manual action-key text filters.
- Preset scope intentionally includes both failure intake (`ops.nightly_failure_reported`) and automation follow-up runs (`automation.job_run`) to keep incident context together.
- Frontend uses mode-based toggle (`all`, `destructive`, `nightly_ops`) so preset behavior stays explicit and does not overload existing destructive mode semantics.

## Checkpoint 10L implementation decisions (phase 2)
- Audit explorer adds date shortcuts as explicit UI actions (`today`, `last 24h`, `last 7d`) to reduce manual date input during incident response.
- Shortcut behavior is intentionally mode-agnostic so operators can keep one mental model across all audit modes.
- Date formatting uses local calendar values (`YYYY-MM-DD`) instead of UTC slicing to avoid off-by-one confusion in timezone-sensitive usage.

## Checkpoint 10M implementation decisions (phase 1)
- Nightly-ops CSV export is implemented as a dedicated audit endpoint (`/api/audit/nightly-ops.csv`) instead of generic table dump to keep scope tight and predictable.
- Export reuses the same nightly-ops filter contract so operators get parity between on-screen review and exported evidence.
- Frontend export action is shown only in `nightly_ops` mode to avoid accidental misuse and keep audit explorer controls clear.

## Checkpoint 10M implementation decisions (phase 2)
- Nightly CSV export now embeds export-note rows (`exported_at`, `exported_rows`, `active_filters`) to preserve evidence context with the file itself.
- Response headers mirror the same summary (`X-Exported-Rows`, `X-Active-Filters`) for lightweight integration diagnostics.
- UI surfaces the same summary before export so operators can sanity-check scope before generating evidence files.

## Checkpoint 10N implementation decisions (phase 1)
- Nightly CSV evidence extraction is now itself auditable through dedicated action `audit.nightly_ops_exported`.
- Export audit payload captures actor context plus filter/row/limit evidence so investigations can reconstruct what was exported.
- Export auditing is implemented in backend route layer where final filtered row count is known, avoiding drift between UI intent and actual exported result.

## Checkpoint 10N implementation decisions (phase 2)
- Nightly-ops investigation flow now includes export-audit actions in the same preset so failure signals and evidence-extraction actions stay correlated.
- A compact recent-export summary panel was added in explorer UI to reduce operator time-to-verify during incident reviews.
- Summary remains read-only and derived from existing audit records, avoiding new write surfaces.

## Checkpoint 10O implementation decisions (phase 1)
- Nightly CSV export reason is optional and stored in audit `reason_text` so governance improves without blocking urgent export workflows.
- Reason capture is wired end-to-end from UI to backend route (`export_reason`) and persisted under the existing `audit.nightly_ops_exported` action.
- This phase intentionally uses a lightweight capture interaction first; UX polish is deferred to the next small slice.
