# Server-Generated PDF Exports

## Purpose
- This document defines the `Checkpoint 8K` server-generated PDF export baseline.
- It introduces backend-generated PDF downloads for key operational summaries.

## Implemented endpoints
- `GET /api/exports/finance.pdf`
- `GET /api/exports/reports.pdf`

## Behavior
- Endpoints generate PDF content server-side.
- Endpoints return downloadable attachment responses with `application/pdf`.
- Current PDF layout is intentionally lightweight and summary-focused.

## Security note
- Both endpoints require backend authorization through `exports.view`.
- No public PDF endpoint is exposed.
