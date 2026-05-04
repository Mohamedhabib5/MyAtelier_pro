# Production Readiness Checklist: MyAtelier Pro

Use this checklist before going live to ensure all security and reliability measures are in place.

## 1. Infrastructure & Docker
- [ ] Non-root users are configured in all Dockerfiles.
- [ ] `.dockerignore` is present and excludes `.env`, `db.sqlite3`, and `storage/`.
- [ ] DB port `5432` is NOT mapped to the host in `docker-compose.yml`.
- [ ] Health checks are enabled for `db` and `backend` services.
- [ ] Docker log rotation is configured in `/etc/docker/daemon.json` (max-size, max-file).

## 2. Configuration & Secrets
- [ ] `APP_ENV` is set to `production`.
- [ ] `APP_DEBUG` is set to `false`.
- [ ] `APP_SECRET_KEY` is a unique, random 32+ character string.
- [ ] `DATABASE_URL` uses PostgreSQL with a strong password.
- [ ] `REDIS_URL` is configured for distributed rate limiting.

## 3. Web & Network Security
- [ ] Nginx is configured with SSL/TLS (Let's Encrypt).
- [ ] HSTS, X-Frame-Options, and CSP headers are active.
- [ ] `SESSION_HTTPS_ONLY` is set to `true`.
- [ ] Rate limiting is active on all API endpoints.
- [ ] API documentation (`/docs`, `/redoc`) is disabled.

## 4. Database & Reliability
- [ ] All critical database indexes have been applied.
- [ ] Automated daily backup script (`prod-db-backup.sh`) is configured in crontab.
- [ ] Health monitor script (`monitor_health.py`) is scheduled to run every 5-10 minutes.
- [ ] Audit logging is active for all sensitive actions.

## 5. Deployment Workflow
- [ ] `.env.prod` is correctly configured on the server.
- [ ] Database migrations have been applied (`alembic upgrade head`).
- [ ] All environment variables are validated by the app on startup.

---
**Status: READY FOR DEPLOYMENT**
