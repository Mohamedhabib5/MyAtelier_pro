# Operational Readiness Checklist (Final)

## Purpose
- This checklist is the final go-live gate after roadmap closeout.
- It should be reviewed and signed before production rollout.

## A. Environment and Security Gate
- [ ] `APP_ENV=production` and `APP_DEBUG=false`.
- [ ] Strong `APP_SECRET_KEY` configured (32+ chars).
- [ ] Non-default `DEFAULT_ADMIN_PASSWORD` configured.
- [ ] `APP_FRONTEND_ORIGINS` uses explicit HTTPS origins only.
- [ ] `ALLOWED_HOSTS` uses explicit hostnames only.
- [ ] Secure session cookie policy verified (`HttpOnly`, `Secure`, intended `SameSite`).
- [ ] Production startup passes with no validation guardrail errors.

Reference: `docs/production-readiness-checklist.md`

## B. Data and Backup Gate
- [ ] Backup creation and download tested in staging.
- [ ] Restore drill executed against throwaway database and documented.
- [ ] Backup retention policy applied (daily/weekly/monthly windows).
- [ ] Stale-backup check endpoint tested (`/api/settings/ops/alerts/run-backup-check`).

References:
- `docs/post-deploy-operations-baseline.md`
- `docs/restore-drill-log.md`

## C. Audit and Control Gate
- [ ] Audit explorer access verified for authorized roles only.
- [ ] Destructive report endpoint verified (`/api/audit/destructive-actions`).
- [ ] Period-lock update/override/exception workflows verified.
- [ ] Automation job audit events verified (`automation.job_run` with `job_key` and `trigger_source`).
- [ ] Write-route audit guardrail tests included in CI path.

References:
- `docs/acceptance-scenarios.md`
- `docs/roadmap-9l-closeout.md`

## D. Runtime Validation Gate
- [ ] Backend focused test suite for changed workflows passes.
- [ ] Frontend production build passes.
- [ ] Focused Playwright smoke passes:
  - `smoke.spec.ts`
  - `lifecycle-archive-restore.spec.ts`
- [ ] Any environment-specific startup notes are recorded in release handoff.

## E. Deployment and Scheduler Gate
- [ ] Edge/TLS forwarding configuration validated in target environment.
- [ ] One scheduler wiring path selected and validated:
  - Windows Task Scheduler
  - Linux Cron
  - Kubernetes CronJob
- [ ] Scheduler account uses least privilege.

References:
- `docs/deployment-edge-hardening.md`
- `docs/windows-task-scheduler-wiring.md`
- `docs/linux-cron-wiring.md`
- `docs/kubernetes-cronjob-wiring.md`

## F. Release Decision
- [ ] Product owner signoff.
- [ ] Operations signoff.
- [ ] Security signoff (or explicit risk acceptance logged).
- [ ] Go-live date/time approved.
- [ ] Rollback owner and rollback steps confirmed.
