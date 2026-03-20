# Security Baseline

## Purpose
- This file defines the minimum security rules that must be followed while developing the project.
- The goal is not enterprise perfection on day one, but to avoid building insecure foundations that are hard to fix later.

## Core rule
- Every new checkpoint must include a small security review before it is considered complete.

## Authentication and session security
- Use server-side protected workflows for every authenticated action.
- Never trust the frontend alone to protect admin-only or privileged actions.
- Store passwords only as strong hashes.
- Session cookies must be `HttpOnly`.
- Session cookies must use `Secure` in production.
- Session cookies must use `SameSite` to reduce CSRF risk.
- Add login throttling or rate limiting once authentication traffic becomes real.

## Authorization
- Every privileged route must check authorization on the backend.
- Do not rely on hidden buttons, hidden tabs, or disabled controls as protection.
- Backup access, user management, settings changes, and future financial posting flows must all be authorization-protected.

## Input and API safety
- Validate all request bodies with explicit schemas.
- Validate IDs, status transitions, and document actions server-side.
- Keep error responses controlled and readable without leaking internals.
- Avoid accepting arbitrary file paths, filenames, or untrusted download targets.

## Database and persistence safety
- Prefer ORM-driven queries and parameterized access.
- Avoid raw SQL unless there is a clear reason.
- Use database constraints for integrity, not frontend checks only.
- Keep migrations small, traceable, and reversible where practical.

## Secrets and configuration
- Keep secrets and environment-specific values outside source code.
- The documented `admin/admin123` default is for first-run local bootstrap only.
- Production deployments must override the secret key, cookie settings, and admin credentials handling.
- Do not log secrets, passwords, or sensitive tokens.

## File handling and backups
- Uploaded files and backup downloads must be authenticated.
- Backup files should not be publicly reachable without authorization.
- File names and paths must be generated or sanitized safely.
- Keep attachment and backup handling simple and auditable.

## Logging and audit
- Log important operational and security-sensitive actions.
- Audit at minimum:
  - user creation and update
  - role or permission changes
  - settings changes
  - backup creation and download
  - future financial posting and reversal actions

## Frontend security reminders
- Treat all frontend state as untrusted from a security perspective.
- Do not place secrets in frontend code.
- Keep API calls explicit and avoid accidental overexposure of admin workflows.

## Security checklist for every checkpoint
- Are protected routes protected on the backend?
- Are inputs validated strictly?
- Are file and backup actions protected?
- Are secrets still only in env/config?
- Did the new code introduce oversized files that are hard to review safely?
- Were docs updated so a future Codex session can understand the security assumptions?