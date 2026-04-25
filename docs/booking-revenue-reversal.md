# Booking Revenue Reversal

## Purpose
- This document explains the automatic reversal workflow added after booking-line revenue recognition.
- The goal is to preserve accounting history while allowing a controlled operational reopen for completed lines.

## Endpoint
- `POST /api/bookings/{booking_id}/lines/{line_id}/reverse-revenue`

## Behavior
- The action is allowed only for booking lines that are currently `completed` and linked to a posted revenue journal entry.
- The backend creates a posted reversing journal entry by swapping debit/credit lines from the original revenue-recognition journal.
- The original revenue-recognition journal status is set to `reversed`.
- The booking line is reopened to `confirmed`.
- The booking line clears `revenue_journal_entry_id` and `revenue_recognized_at`.
- Booking document status is recalculated from all lines.

## Guardrails
- The action is blocked if there are active receivables collections posted for that line after completion behavior.
- This prevents reopening a line while receivables settlements are still active, which could desync customer balances.
- The action is still authenticated/authorized through existing bookings backend permission guards.

## Audit and traceability
- Accounting audit action: `accounting.booking_line_revenue_reversed`
- Booking workflow audit action: `booking.line_revenue_reversed`
- No accounting history is deleted; reversal is additive and explicit.
