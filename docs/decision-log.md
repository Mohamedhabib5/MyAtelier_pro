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
