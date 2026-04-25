# Linux Cron Wiring

## Purpose
- This document is the `Checkpoint 8G` runbook for wiring stale-backup checks on Linux.
- It provides a concrete Cron path with register/unregister scripts.

## Scripts
- Register cron task: `infra/scripts/register-backup-stale-alert-cron.sh`
- Runner command: `infra/scripts/run-backup-stale-alert-check.sh`
- Remove cron task: `infra/scripts/unregister-backup-stale-alert-cron.sh`

## Register cron task (hourly)
```bash
bash infra/scripts/register-backup-stale-alert-cron.sh
```

## Register with explicit settings
```bash
TASK_NAME=myatelier_backup_stale_alert_check \
INTERVAL_MINUTES=30 \
BASE_URL=http://localhost:8000 \
USERNAME=ops.user \
PASSWORD=secure-app-password \
DRY_RUN=false \
FORCE=false \
bash infra/scripts/register-backup-stale-alert-cron.sh
```

## Validate behavior
1. Run `crontab -l` and confirm marker block exists.
2. Execute runner manually once:
```bash
bash infra/scripts/run-backup-stale-alert-check.sh
```
3. Confirm exit code `0` on healthy/no-alert path.
4. Confirm backend audit log includes `ops.backup_stale_check_run`.

## Remove cron task
```bash
bash infra/scripts/unregister-backup-stale-alert-cron.sh
```

## Security note
- Prefer a dedicated low-privilege Linux service account.
- Replace default credentials before production usage.
- Keep webhook and credentials in secure secret storage.
