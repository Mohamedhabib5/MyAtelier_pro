# Export Schedules Background Execution

## Purpose
- This document defines the `Checkpoint 8I` background execution baseline for saved export schedules.
- It enables unattended execution of due schedules through a backend batch endpoint.

## Implemented backend endpoint
- `POST /api/exports/schedules/run-due`

## Behavior
- Runs only active schedules with `next_run_on <= today`.
- Supports `dry_run` mode for safe preview.
- Supports execution `limit` to cap batch size per run.
- Updates `last_run_at` and advances `next_run_on` for executed schedules.
- Records audit event `export.schedules_run_due`.

## Runner scripts
- Windows: `infra/scripts/run-due-export-schedules.ps1`
- Linux: `infra/scripts/run-due-export-schedules.sh`

## Security note
- Endpoint requires authenticated access with `exports.manage`.
- No public batch execution endpoint is exposed.
- Batch runs are auditable and permission-guarded server-side.
