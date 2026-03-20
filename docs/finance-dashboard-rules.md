# Finance Dashboard Rules

## Scope of Checkpoint 4C
- This checkpoint adds a simple Arabic finance dashboard page that mirrors the main indicators from the old Dash app.
- The scope stays limited to KPI summaries and lightweight breakdown lists.
- It does not add advanced charts, exports, or branch-level analytics yet.

## Included behavior
- `GET /api/dashboard/finance` returns the finance summary for the active company.
- The frontend page is available at `/dashboard` and becomes the default landing page after login.
- The shell navigation now exposes the operational pages already implemented so the app shape stays closer to the previous product.
- Both `admin` and `user` can view the finance dashboard in this phase.

## KPI rules
- `total_income` is the net of deposits and payments minus refunds.
- voided payments are excluded from dashboard totals.
- `total_remaining` is the remaining amount across non-cancelled bookings only.
- `total_bookings` is the current count of bookings in the system.
- `daily_income` is grouped by payment date and shown in chronological order.
- `department_income` is grouped by the department of the booked service.
- `top_services` is grouped by booking count.

## Security rules
- Dashboard data is protected by the server-side permission `finance.view`.
- Anonymous access must be rejected by the existing session auth flow.
- The dashboard is read-only in this checkpoint.

## Explicitly deferred
- graphical charts beyond simple lists
- export or print actions
- branch-aware dashboard filters
- comparison periods and trends
- accounting-to-dashboard drilldown links
