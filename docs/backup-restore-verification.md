# Backup Restore Verification

## Purpose
- This document explains what the backup now contains and what was verified in `Checkpoint 7C`.
- There is still no end-user restore screen in the product at this stage.

## Current backup contents
- `manifest.json`
- `database/dump.sql`
- `attachments/`

## What changed in Checkpoint 7C
- The backup archive now includes a real database SQL dump instead of attachments-only backup content.
- PostgreSQL dumps are normalized to stay restorable against the current `PostgreSQL 16` runtime used by the project.
- Restore verification was executed against a throwaway database, not the live application database.

## Live verification summary
- Created a backup through the authenticated settings API.
- Downloaded the ZIP archive.
- Confirmed the archive contains `database/dump.sql`.
- Restored the dump into a throwaway database named `myatelier_restore_verify`.
- Verified restored counts for:
  - `users`
  - `booking_lines`
  - `payment_documents`
  - `backup_records`

## Security note
- Download protection remains authenticated and authorized.
- Restore verification is intentionally operational-only and does not expose a restore action in the UI.
- Using a throwaway database avoids destructive risk to the live dataset.

## Still deferred
- End-user restore UI
- One-click restore workflow
- Automated scheduled restore drills
- Managed execution of retention cleanup with operations scheduling and alerting integration
