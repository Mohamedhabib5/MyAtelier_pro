# Migration Note: 36c89d0494e1

**Migration ID**: `36c89d0494e1`
**Original Name**: `add_groom_bride_to_customers`
**New Name**: `refactor_bookings_to_lines_and_drop_payment_receipts`

## Context
This migration was originally named `add_groom_bride_to_customers`, but it contained major destructive schema changes:
- Dropping `payment_receipts` table.
- Dropping legacy `bookings` columns (e.g. `service_id`, `dress_id`, `event_date`) as part of refactoring to `booking_lines`.

In addition, its `downgrade()` function incorrectly re-created tables (`custody_cases` and `export_schedules`) that it did not drop, breaking the downgrade chain.

## Actions Taken
1. **Renamed File**: Renamed the file to accurately reflect its destructive operations.
2. **Fixed Downgrade**: Removed the re-creation of `custody_cases` and `export_schedules` to ensure `alembic downgrade -1` works symmetrically.
3. **Preserved Revision ID**: The revision ID (`36c89d0494e1`) was deliberately kept the same so that databases which already applied this migration are not broken.

## ⚠️ Team Coordination (Mandatory)
If you already have this repository cloned and this migration was applied locally, **you must** run the following commands to resync your Alembic state and apply the fixed downgrade function locally:

```bash
alembic downgrade -1
alembic upgrade head
```

Do **NOT** run `alembic downgrade` on production without explicit owner approval.
