# Reporting Rules

## Scope of Checkpoint 5A
- This checkpoint adds a read-only reporting page beyond the finance dashboard.
- The scope stays limited to operational summaries across customers, services, dresses, bookings, and payments.
- No edits, exports, branch filters, or scheduled reports are included yet.

## Included behavior
- `GET /api/reports/overview` returns one overview payload for the active company.
- The frontend page is available at `/reports`.
- Both `admin` and `user` can view the reports page in this phase.

## Report rules
- `active_customers` counts customers where `is_active = true`.
- `active_services` counts services where `is_active = true`.
- `available_dresses` counts dresses where `is_active = true` and `status = available`.
- `upcoming_bookings` counts non-cancelled bookings with `event_date >= today`.
- `booking_status_counts` groups all bookings by status.
- `payment_type_totals` groups net payment values by payment type, with refunds reducing totals.
- voided payments are excluded from reporting totals.
- `dress_status_counts` groups dresses by current status.
- `department_service_counts` groups services by their department.
- `upcoming_booking_items` shows the next five non-cancelled bookings by date.

## Security rules
- Reports are protected by the server-side permission `reports.view`.
- The reporting slice is read-only and introduces no new write or delete actions.
- Anonymous access must continue to fail through the existing session-auth guard.

## Explicitly deferred
- PDF or Excel export
- branch-aware filtering
- trend comparisons
- scheduled or emailed reports
- drill-down into accounting postings
