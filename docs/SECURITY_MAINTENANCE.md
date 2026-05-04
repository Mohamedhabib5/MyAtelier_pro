# Security Maintenance Guide: MyAtelier Pro

This guide outlines the essential tasks for maintaining the security of the MyAtelier Pro system in production.

## 1. Secret Management
- **Key Rotation**: Rotate `APP_SECRET_KEY` every 6-12 months. Note that this will logout all current users.
- **DB Passwords**: Change database passwords periodically and ensure they are never committed to version control.
- **Environment Variables**: Always use the `.env.prod.example` template for production.

## 2. Updates & Patching
- **Dependency Audit**: Run `npm audit` (frontend) and `pip-audit` (backend) monthly.
- **Container Updates**: Update the base images in `Dockerfile` periodically (e.g., from `python:3.13-slim` to newer patches).
- **System Patches**: Ensure the host server (VPS) has automatic security updates enabled.

## 3. Database & Backups
- **Off-site Backups**: Ensure backups generated in `storage/backups` are periodically moved to a separate, secure location (e.g., S3, Google Cloud Storage).
- **Encryption**: Verify that the production database uses SSL/TLS for all connections.

## 4. Monitoring & Logging
- **Audit Logs**: Regularly review the `audit_logs` table for suspicious activities (e.g., multiple failed login attempts).
- **Resource Monitoring**: Monitor server CPU/Memory to detect potential DDoS or resource exhaustion attacks.
- **Error Logs**: Monitor `uvicorn` and `nginx` error logs for unusual patterns.

## 5. Security Checklist for Deployment
- [ ] `APP_ENV` is set to `production`.
- [ ] `APP_DEBUG` is set to `false`.
- [ ] All default passwords have been changed.
- [ ] DB port `5432` is not exposed to the public internet.
- [ ] Nginx is configured with valid SSL/TLS certificates (Let's Encrypt).
- [ ] `HTTPS_ONLY` is set to `true` for sessions.
