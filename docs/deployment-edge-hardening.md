# Deployment Edge Hardening

## Purpose
- This document is the `Checkpoint 8B` deployment-edge runbook.
- It focuses on reverse proxy, TLS, trusted host flow, and pre-go-live checks.

## Infra artifacts
- Reverse proxy template: `infra/nginx/myatelier.conf.example`
- Production compose template: `infra/docker-compose.prod.example.yml`
- Baseline app config guardrails: `docs/production-readiness-checklist.md`

## Reverse proxy requirements
- Terminate TLS at the edge.
- Redirect all HTTP traffic to HTTPS.
- Forward the original host and client IP headers.
- Forward `X-Forwarded-Proto=https` to backend.
- Keep `Strict-Transport-Security` enabled in production.
- Expose backend only through the edge network path.

## Required production env values
- `APP_ENV=production`
- `APP_DEBUG=false`
- `APP_SECRET_KEY` as random 32+ chars
- `DEFAULT_ADMIN_PASSWORD` as non-default value
- `APP_FRONTEND_ORIGINS` with explicit HTTPS domain(s)
- `ALLOWED_HOSTS` with explicit backend host(s)
- `SESSION_HTTPS_ONLY=true`
- `SESSION_SAME_SITE=lax` unless cross-site requirement exists

## Deployment verification
1. Start stack using production env values and edge proxy.
2. Confirm backend starts without config validation errors.
3. Verify `Set-Cookie` includes `HttpOnly`, `Secure`, and intended `SameSite`.
4. Verify auth endpoints return `Cache-Control: no-store`.
5. Verify API requests through edge include expected host and protocol behavior.
6. Confirm direct public access to backend container port is disabled.

## Security review note
- This checkpoint adds deployment guidance and runnable infra templates.
- Authorization logic and business workflows were not changed.
- Startup guardrails from `Checkpoint 8A` remain the primary safety gate for production env mistakes.
