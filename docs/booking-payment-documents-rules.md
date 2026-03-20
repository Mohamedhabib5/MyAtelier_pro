# Booking and Payment Documents Rules

## Purpose
- This document records the redesigned operational model introduced in `Checkpoint 7A`.
- It is the main reference for the new booking and payment workflows.

## Booking document
- One booking document belongs to one customer.
- The booking header stores booking number, booking date, customer, notes, branch, and derived status.
- Booking lines store department, service, service date, optional dress, suggested price, actual price, line status, notes, and revenue-recognition references.

## Financial behavior on booking lines
- Suggested price is pulled from the selected service.
- Actual price is editable.
- Paid total is computed from payment allocations.
- Remaining amount is computed as actual price minus paid total.
- Initial payment is optional on booking save.
- If one or more initial payments are entered, the backend creates one payment document with one allocation per paid line.

## Payment document
- One payment document belongs to one customer.
- One payment document can allocate to multiple booking lines and multiple bookings.
- In `v1`, allocations must remain inside the same active branch.
- Payment allocations are the financial source of truth for collected amounts on lines.

## Revenue recognition
- Revenue is recognized per booking line when that line is completed.
- Completion debits customer advances for collected amounts, debits customer receivables for the remaining amount, and credits service revenue for the full line price.
- After recognition, the completed line is locked from free-form edits.

## Reporting and export behavior
- Booking lists remain document-based.
- Operational summaries and upcoming bookings are line-aware.
- Exports now include booking summaries, booking lines, payment document summaries, and payment allocations.

## Security and integrity
- Same-customer and same-branch validation is enforced in the backend for payment allocations.
- Over-allocation is blocked server-side.
- Cancelled lines cannot receive payments.
- Completed lines cannot be silently edited from the booking editor.
