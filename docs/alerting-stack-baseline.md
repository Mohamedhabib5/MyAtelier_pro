# Alerting Stack Baseline

## Purpose
- This document defines the `Checkpoint 8D` alerting implementation baseline.
- It adds a minimal metrics and notification wiring path without introducing a heavy observability platform yet.

## Implemented backend endpoints
- `GET /api/settings/ops/metrics`
- `POST /api/settings/ops/alerts/test`
- `POST /api/settings/ops/alerts/run-backup-check`

## Access control
- Both endpoints require authenticated access with `settings.manage`.
- No public metrics endpoint is exposed in this checkpoint.

## Metrics snapshot fields
- `backups_total`
- `backups_last_24h`
- `last_backup_at`
- `last_backup_age_hours`
- `backup_stale_threshold_hours`
- `backup_stale`
- `audit_logs_total`

## Alert test behavior
- Reads webhook URL from `OPS_ALERT_WEBHOOK_URL`.
- Supports `dry_run=true` to validate payload flow without sending HTTP requests.
- Records an audit event `ops.alert_test` with severity and send result.

## Automated stale-backup check behavior
- `run-backup-check` evaluates backup staleness against `OPS_BACKUP_STALE_THRESHOLD_HOURS`.
- Sends webhook alert only when stale (or when `force=true`).
- Returns no-alert response when backup is within threshold.
- Records an audit event `ops.backup_stale_check_run`.
- Runner script: `infra/scripts/run-backup-stale-alert-check.ps1`.
- Windows scheduler wiring: `docs/windows-task-scheduler-wiring.md`.
- Linux scheduler wiring: `docs/linux-cron-wiring.md`.
- Kubernetes scheduler wiring: `docs/kubernetes-cronjob-wiring.md`.

## Environment values
- `OPS_BACKUP_STALE_THRESHOLD_HOURS`
- `OPS_ALERT_WEBHOOK_URL`

## Deferred to future checkpoint
- Prometheus/OpenTelemetry exporters.
- Multi-channel alert fan-out (email/chat/incident tools).
