# Export Rules

## Purpose
- This document defines the export slices in the rebuilt product.
- The goal is to provide simple downloads and printable views without introducing a heavy reporting subsystem.

## Scope through Checkpoint 6E
- customers CSV export
- bookings CSV export
- payments CSV export
- one export page inside the shell
- authenticated and audited export actions
- printable finance view
- printable reports view
- saved export schedules foundation

## Export behavior
- customers export is company-wide
- bookings export is scoped to the active branch by default and can also run against a validated branch id
- payments export is scoped to the active branch by default and can also run against a validated branch id
- bookings and payments exports now accept the same table filters used by heavy-grid endpoints (`search`, status, date range, sort fields, and sort direction)
- `/api/exports/payment-documents.csv|xlsx` remains an alias for payments exports and must keep filter parity with `/api/exports/payments.csv|xlsx`
- `/api/exports/booking-lines.csv|xlsx` now accepts the same booking-table filters and applies them before expanding booking document lines
- `/api/exports/payment-allocations.csv|xlsx` now accepts the same payment-table filters and applies them before expanding payment allocations
- export-center UI now offers booking/payment filter inputs and should pass them to related summary + detail export links in the same action group
- payments export includes linked journal entry number and status when present
- CSV files are emitted as UTF-8 with BOM for better Excel compatibility
- printable views open in a separate tab and rely on the browser print dialog
- printable views can be saved manually as PDF from the browser
- saved schedules store export type, cadence, branch scope, next run date, active state, and last run timestamp
- run-now returns a safe URL that reuses the existing authenticated export and print endpoints
- bookings/payments grid XLSX actions should always include active filters in their URL so operators export what they are currently reviewing

## Security rules
- all export routes require an authenticated session
- export downloads require `exports.view`
- schedule management requires `exports.manage`
- permissions are enforced server-side
- export actions are audited
- branch-scoped exports must not leak data from another active branch
- printable routes stay inside the authenticated frontend shell guard
- schedule runs reuse backend branch validation and do not trust frontend-only state

## Out of scope
- unattended background execution of schedules
- email, WhatsApp, or other delivery channels
- server-generated PDF files
- cross-branch comparison exports
- background export jobs
