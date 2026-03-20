# Acceptance Scenarios

## Cross-cutting rules
- Every checkpoint must remain small, reviewable, and understandable to a non-programmer owner.
- Every checkpoint must update the relevant docs before it is considered complete.
- Every checkpoint must include focused validation and a brief security review note.

## Implemented acceptance scenarios
- First run on an empty database creates the default `admin / admin123` user exactly once.
- `admin` can manage all users, while `user` only sees and updates their own profile.
- Settings can update company details and create downloadable backup files.
- Accounting supports chart seeding, journal create/list/detail, posting, reversal, and trial balance read views.
- Customers can be created and updated by both `admin` and `user`.
- Departments and services can be created and updated by both `admin` and `user`.
- Dress resources can be created and updated by both `admin` and `user`.
- Bookings can be created and updated by both `admin` and `user` before completion.
- The same dress cannot be booked twice on the same date.
- Booking completion now creates a posted revenue-recognition journal entry.
- Completed bookings are locked after revenue recognition.
- Payments support deposit, payment, and refund while enforcing remaining-balance validation.
- Every new payment now auto-posts a linked journal entry.
- Updating a payment reverses the old linked journal and posts a replacement journal.
- Payments can be voided safely with a reason instead of being deleted.
- Voiding a payment reverses its linked journal entry and removes the payment from financial totals.
- The finance dashboard shows KPI totals and summary breakdowns to both `admin` and `user`.
- The reports page shows broader read-only operational summaries to both `admin` and `user`.
- The authenticated session now stores an active branch.
- Branches can be created from settings and switched from the shell selector.
- Bookings, payments, finance dashboard, and reports now change with the active branch.
- Customers, bookings, and payments can now be downloaded as CSV exports.
- Bookings and payments exports respect the active branch.
- Printable finance and reports pages now open in separate tabs and can be saved as PDF from the browser.
- `admin` can create, list, run, and toggle saved export schedules.
- Saved schedule runs for bookings, payments, finance print, and reports print respect backend branch scoping.
- `user` cannot access export schedule management actions.
- Backend startup now boots and shuts down through `lifespan` without deprecated startup events.
- Frontend pages now load lazily and still build successfully for production.

## Still deferred
- unattended background execution of export schedules
- email, WhatsApp, or other delivery channels for export schedules
- automatic reversal for booking revenue recognition
- server-generated PDF exports
- delete flows for business documents beyond payment voiding
- customer or mobile portals

- Bookings can now be created and updated as one document with multiple service lines.
- Quick customer creation is available from inside the booking editor flow.
- Suggested price is auto-filled per booking line and can be edited into the agreed actual price.
- Initial payments across one or more booking lines create one payment document automatically.
- One payment document can allocate across multiple lines and multiple bookings for the same customer and active branch.
- Cross-customer payment mixing and over-allocation are blocked server-side.
- Booking completion and revenue recognition now run per line instead of per booking header.
- Reports and upcoming bookings are line-aware.
- Exports now include booking lines and payment allocations in addition to summary documents.
- Live Playwright smoke now passes against the Docker stack for login plus the redesigned multi-line booking and multi-allocation payment flow.
- The live PostgreSQL schema is now aligned with the redesigned booking header so creating new booking documents no longer fails on legacy `NOT NULL` columns.
- Backup archives now include a real database dump and can be restored successfully into a throwaway verification database.
- Critical Arabic UI pages now render stable labels for login, users, bookings, and payments.
- Booking date validation now returns Arabic messages such as `التاريخ مطلوب`.
- Booking dress behavior now depends on `department.code`, so text corruption in display labels cannot break the rule.
- The text-integrity source check now blocks `???`, replacement characters, mojibake patterns, and leftover English date-validation strings.
