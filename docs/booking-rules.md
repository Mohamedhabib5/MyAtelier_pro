# Booking Rules

## Status
- This file now reflects the current booking model after `Checkpoint 7A`.
- Bookings are no longer single-service records.

## Current model
- A booking is a document header.
- A booking contains one customer and one booking date.
- A booking contains one or more booking lines.

## Booking line rules
- Each line represents one service entry.
- Each line stores its own department, service, service date, optional dress, suggested price, actual price, status, and notes.
- Dress selection is allowed only on dress-related lines.
- The same dress cannot be booked twice on the same service date.
- Paid total and remaining amount are derived from payment allocations, not typed in manually as source-of-truth values.

## Status rules
- Line status is independent per line.
- Booking document status is derived from the line set.
- Completed lines are locked after revenue recognition.
- Cancelled lines cannot receive payments.

## UI rules
- Booking entry uses a full-page editor.
- The editor supports quick customer creation.
- Suggested price is auto-filled from the selected service.
- Actual price remains editable.
- Optional initial payments can be entered on lines during booking save.
