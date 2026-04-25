# Post-Deploy Operations Baseline

## Purpose
- This document defines the `Checkpoint 8C` operations baseline after deployment.
- It closes the previous open question around backup retention and restore drill cadence.

## Scope
- Backup retention policy
- Restore drill cadence and evidence
- Monitoring and alerting baseline

## Backup retention policy
- Keep daily backups for the last `14` days.
- Keep weekly backups for the last `8` weeks.
- Keep monthly backups for the last `12` months.
- Keep at least one successful backup before deleting older files.
- Never delete backup files manually without updating `backup_records` consistency checks.

## Restore drill cadence
- Run one restore drill every `30` days in a throwaway database.
- Every drill must verify:
  - archive contains `manifest.json` and `database/dump.sql`
  - restore command completes successfully
  - row counts for critical tables are non-zero and plausible
  - login works against restored dataset in isolated environment
- Record each drill in `docs/restore-drill-log.md`.

## Monitoring and alerts baseline
- Track at least these operational signals:
  - backup creation failure
  - backup download failure due to auth/path/security checks
  - restore drill failure
  - repeated failed login attempts spike
  - unhandled backend exceptions
- Alert channels should include:
  - primary operations email
  - optional chat channel for immediate awareness
- Severity baseline:
  - `P1`: restore drill failure, backup creation failure
  - `P2`: repeated auth anomalies, elevated 5xx rate
  - `P3`: delayed but successful backups

## Recommended operational schedule
1. Daily: verify backup creation and file presence.
2. Weekly: review backup health summary and storage trend.
3. Monthly: run restore drill and publish verification record.
4. Quarterly: review retention values against storage growth and business needs.

## Security review note
- All backup and restore checks remain authenticated and operational-only.
- No restore UI or destructive in-app restore action is introduced in this checkpoint.
- This checkpoint adds process safety and observability, not new business behavior.
