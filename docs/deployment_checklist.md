# MyAtelier Pro - Production Deployment Checklist

## 1. Infrastructure & Environment
- [ ] Ensure the PostgreSQL database is running version 15+ and is configured for high availability.
- [ ] Ensure Redis is running and secured (requires authentication, no public exposure).
- [ ] Verify `APP_SECRET_KEY` is a strong, cryptographically secure random string (at least 32 bytes) and is NOT the default value.
- [ ] Verify `ENVIRONMENT` is set to `production`.
- [ ] Ensure all debug modes (`DEBUG=False`) and backdoor testing flags are strictly disabled.

## 2. Security Configuration
- [ ] Configure `ALLOWED_HOSTS` and CORS origins to only allow legitimate frontend domains.
- [ ] Configure the reverse proxy (Nginx/Traefik) to handle SSL/TLS termination and enforce HTTPS.
- [ ] Verify `FORWARDED_ALLOW_IPS` is restricted to trusted load balancers/proxies to prevent IP spoofing.
- [ ] Verify rate limiting is active and configured correctly using Redis.
- [ ] Ensure CSRF tokens are enforced on all mutating requests from browsers.

## 3. Database & Migrations
- [ ] Take a full backup of the production database before deployment.
- [ ] Apply Alembic migrations using `alembic upgrade head`.
- [ ] Verify database roles and ensure the application connects with a user that has restricted privileges (least privilege principle).

## 4. Application Verification
- [ ] Run the full test suite (`pytest -m "not e2e"`) and ensure 100% pass rate.
- [ ] Run Guardrail tests (`pytest -m guardrail`) and ensure all security constraints are met.
- [ ] Start the FastAPI server using a production-ready ASGI server like Uvicorn with Gunicorn workers.

## 5. Monitoring & Audit
- [ ] Verify application logs are being collected and shipped to the centralized logging system.
- [ ] Ensure the `record_audit` function is capturing critical security and business events.
- [ ] Setup alerts for repeated authentication failures, 500 internal server errors, and database connection issues.

## 6. Final Sign-off
- [ ] Lead Developer approval.
- [ ] Security Team approval.
- [ ] Operations Team approval.
