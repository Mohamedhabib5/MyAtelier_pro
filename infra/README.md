# Infra Notes

- `docker-compose.yml` is the default local orchestration entry point.
- PostgreSQL 16 is the primary database target for local/dev parity.
- `docker-compose.prod.example.yml` provides a production-style compose template with `edge` (Nginx), frontend preview, backend, and PostgreSQL.
- `nginx/myatelier.conf.example` provides a reverse-proxy template with HTTPS redirect, TLS placeholders, and forwarded headers.
- `scripts/backup-retention-example.ps1` provides a retention cleanup example aligned with post-deploy operations baseline.
- `scripts/run-backup-stale-alert-check.ps1` provides a schedulable runner for periodic stale-backup alert checks.
- `scripts/register-backup-stale-alert-task.ps1` wires stale-backup checks into Windows Task Scheduler.
- `scripts/unregister-backup-stale-alert-task.ps1` removes the scheduled task safely.
- `scripts/run-backup-stale-alert-check.sh` provides a Linux runner for periodic stale-backup alert checks.
- `scripts/register-backup-stale-alert-cron.sh` wires stale-backup checks into Linux Cron.
- `scripts/unregister-backup-stale-alert-cron.sh` removes the Cron registration safely.
- `k8s/backup-stale-alert-cronjob.example.yaml` provides a Kubernetes CronJob baseline for stale-backup alert checks.
- `scripts/run-due-export-schedules.ps1` runs due export schedules in unattended mode (Windows runner).
- `scripts/run-due-export-schedules.sh` runs due export schedules in unattended mode (Linux runner).
- Replace example domains and certificate paths before any real production deployment.
