# Payment Rules

## Status
- This file now reflects the current payment model after `Checkpoint 7A`.
- Daily payment entry no longer uses single receipts linked to one booking only.

## Current model
- A payment is a payment document header.
- A payment document belongs to one customer and one active branch context.
- A payment document contains one or more allocation lines.

## Allocation rules
- Each allocation points to one booking line.
- One payment document can allocate across multiple booking lines.
- One payment document can allocate across multiple bookings for the same customer.
- Cross-customer and cross-branch allocation mixing is blocked server-side.
- Allocation amount cannot exceed the remaining balance of the target booking line.

## Accounting rules
- Collection allocations on incomplete lines credit `2100 عربون العملاء`.
- Collection allocations on completed lines credit `1200 ذمم العملاء`.
- A payment document can mix both cases in one posted journal.
- Voiding a payment document reverses its linked journal instead of deleting history.

## Editor rules
- Initial payments entered during booking save produce one payment document automatically.
- The payments screen supports smart search by customer or booking number.
- Refund redesign remains deferred for a later dedicated slice.
