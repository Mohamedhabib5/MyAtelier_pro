# Production Readiness Checklist

## Purpose
- This checklist captures the minimum production configuration required by `Checkpoint 8A`.
- It is written for short operational verification before deployment.

## Backend env checklist
- Set `APP_ENV=production`.
- Set `APP_DEBUG=false`.
- Set `APP_SECRET_KEY` to a random value with at least 32 characters.
- Set `DEFAULT_ADMIN_PASSWORD` to a non-default value before first production boot.
- Set `APP_FRONTEND_ORIGINS` to explicit HTTPS frontend origin(s), comma-separated.
- Do not use localhost origins in `APP_FRONTEND_ORIGINS`.
- Do not use `*` in `APP_FRONTEND_ORIGINS`.
- Set `ALLOWED_HOSTS` to explicit backend hostnames.
- Do not use `*` in `ALLOWED_HOSTS`.
- Keep `SESSION_HTTPS_ONLY=true`.
- Use `SESSION_SAME_SITE=lax` by default unless a specific cross-site flow requires `none`.
- If `SESSION_SAME_SITE=none`, keep secure cookies enabled.
- Set `OPS_BACKUP_STALE_THRESHOLD_HOURS` to your expected backup frequency threshold.
- Set `OPS_ALERT_WEBHOOK_URL` to HTTPS webhook endpoint (or keep empty until ready).
- Set `EXPORT_DELIVERY_WEBHOOK_URL` to HTTPS endpoint if delivery handoff is enabled.

## Deployment notes
- Terminate TLS at a trusted reverse proxy or load balancer.
- Forward only trusted host headers to the backend service.
- Restrict backend network access to known frontend and operations networks.
- Keep storage volumes for backups and attachments private and non-public.
- Run database backups and restore verification on a defined schedule.

## Verification flow
1. Start backend with production env values.
2. Confirm app startup succeeds with no config validation errors.
3. Run focused security tests for production config guardrails.
4. Verify login response sets `HttpOnly`, `Secure`, and intended `SameSite` cookie flags.
5. Record deployment values and verification result in the next checkpoint handoff.
6. Continue with post-deploy operations baseline in `docs/post-deploy-operations-baseline.md`.
7. Validate operations alerting endpoints from `docs/alerting-stack-baseline.md`.
8. Run one stale-backup check via `/api/settings/ops/alerts/run-backup-check` before enabling scheduler.
9. Wire scheduler using one concrete path.
Windows path: `docs/windows-task-scheduler-wiring.md`
Linux path: `docs/linux-cron-wiring.md`
Kubernetes path: `docs/kubernetes-cronjob-wiring.md`
