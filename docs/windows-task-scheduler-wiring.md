# Windows Task Scheduler Wiring

## Purpose
- This document is the `Checkpoint 8F` runbook for wiring stale-backup checks on Windows.
- It provides one concrete scheduler path without introducing extra platform dependencies.

## Scripts
- Register task: `infra/scripts/register-backup-stale-alert-task.ps1`
- Runner task action: `infra/scripts/run-backup-stale-alert-check.ps1`
- Remove task: `infra/scripts/unregister-backup-stale-alert-task.ps1`

## Register scheduled task
```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/register-backup-stale-alert-task.ps1 `
  -BaseUrl "http://localhost:8000" `
  -Username "admin" `
  -Password "admin123" `
  -IntervalMinutes 60
```

## Register with explicit service user
```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/register-backup-stale-alert-task.ps1 `
  -BaseUrl "http://localhost:8000" `
  -Username "ops.user" `
  -Password "secure-app-password" `
  -IntervalMinutes 60 `
  -RunAsUser "MYDOMAIN\\svc_myatelier" `
  -RunAsPassword "secure-windows-password"
```

## Validate task behavior
1. Open Task Scheduler and confirm task `MyAtelier-BackupStaleAlertCheck` exists.
2. Run the task manually once.
3. Confirm task result is `0x0` for success.
4. Confirm backend audit log includes `ops.backup_stale_check_run`.
5. Confirm alert behavior based on stale/non-stale backup status.

## Remove scheduled task
```powershell
powershell -ExecutionPolicy Bypass -File infra/scripts/unregister-backup-stale-alert-task.ps1
```

## Security note
- Use a dedicated low-privilege Windows service account for task execution.
- Replace default credentials before production use.
- Keep webhook URL and app credentials in secure ops secret management where possible.
