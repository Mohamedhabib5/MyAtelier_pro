# Tax-Aware Revenue Recognition

## Purpose
- This checkpoint adds a narrow tax-aware accounting behavior to booking-line revenue recognition.
- It is not a full tax engine; it focuses only on recognition journal posting.

## Data model additions
- `service_catalog_items.tax_rate_percent` (default `0.00`)
- `booking_lines.tax_rate_percent` snapshot
- `booking_lines.tax_amount` snapshot

## Posting behavior on line completion
- Debits remain gross on customer-side balances:
  - `2100 عربون العملاء` for collected amount
  - `1200 ذمم العملاء` for remaining amount
- Credits are now split:
  - `4100 إيرادات الخدمات` for net revenue
  - `2200 ضريبة المخرجات` for tax amount

## Notes
- Tax values are derived server-side and persisted on booking lines for auditability.
- Existing flows continue to work with zero tax by default.
