# Booking Revenue Recognition Rules

## Purpose
- This document defines the first booking-to-revenue accounting slice.
- The goal is to recognize revenue at booking completion without introducing a full invoicing subsystem yet.

## Included behavior
- booking completion is an explicit backend business action
- completion creates a posted journal entry immediately
- collected amounts debit `2100 عربون العملاء`
- remaining amounts debit `1200 ذمم العملاء`
- net service amount credits `4100 إيرادات الخدمات`
- tax amount credits `2200 ضريبة المخرجات` when line tax is greater than zero
- completed bookings expose the linked revenue journal number in the booking response and UI
- completed bookings are locked after revenue recognition in this slice

## Recognition assumptions
- recognition date is the completion action date
- quoted price must be positive to recognize revenue
- active payments exclude voided payments
- refunds reduce the collected amount before recognition is computed
- if no money was collected yet, the full quoted price is recognized to receivables and revenue

## Validation rules
- completion is blocked for cancelled bookings
- completion is blocked when revenue was already recognized for the booking
- direct status editing to `completed` is blocked; the completion action must be used
- completed bookings cannot be edited afterward in this slice
- fiscal-period checks still apply to the generated journal entry

## Security notes
- completion is guarded server-side by the existing bookings permission
- revenue posting runs in backend business logic and cannot be skipped from the browser
- the linked journal entry and booking completion action are both audited

## Deferred after this slice
- invoice document workflow
- write-off handling for bad debts
