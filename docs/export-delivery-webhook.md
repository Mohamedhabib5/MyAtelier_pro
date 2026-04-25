# Export Delivery Webhook

## Purpose
- This document defines the `Checkpoint 8J` delivery-channel expansion baseline.
- It introduces optional webhook delivery for due export schedule batch runs.

## Endpoint
- `POST /api/exports/schedules/run-due`

## Delivery options
- `notify`: enables delivery webhook step.
- `delivery_dry_run`: validates delivery flow without sending HTTP request.

## Environment value
- `EXPORT_DELIVERY_WEBHOOK_URL`

## Response fields
- `delivery_sent`
- `delivery_detail`

## Security note
- Batch execution remains protected by `exports.manage`.
- Delivery webhook URL is validated as `https` in production mode.
- Delivery execution result is recorded in batch audit logs.
