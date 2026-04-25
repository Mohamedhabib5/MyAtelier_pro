# Session Handoff - 2026-03-21 - Checkpoint 8G

## What was completed
- Promoted repository state to `Checkpoint 8G`.
- Added Linux runner script for stale-backup alert checks.
- Added Linux Cron register script with marker-based safe updates.
- Added Linux Cron unregister script for rollback and cleanup.
- Added dedicated Linux Cron wiring runbook.
- Updated docs and checkpoint status alignment to reflect Linux scheduler parity.

## Why this checkpoint mattered
- `Checkpoint 8F` completed Windows scheduler wiring, but non-Windows deployments still needed a concrete scheduler path.
- Linux Cron is the simplest and most common baseline for VM-based Linux environments.
- This slice completes cross-platform scheduler parity without pulling in orchestration-specific tooling.

## Validation run
- `python -m pytest backend/tests/test_ops_alerting.py -q`
- `python -m pytest backend/tests/test_security_hardening.py -q`
- `python -m pytest backend/tests/test_foundation.py backend/tests/test_language_preferences.py backend/tests/test_text_integrity_guardrails.py -q`

## Files touched in this checkpoint
- `infra/scripts/run-backup-stale-alert-check.sh`
- `infra/scripts/register-backup-stale-alert-cron.sh`
- `infra/scripts/unregister-backup-stale-alert-cron.sh`
- `docs/linux-cron-wiring.md`
- `infra/README.md`
- `docs/alerting-stack-baseline.md`
- `docs/current-checkpoint.md`
- `docs/milestones.md`
- `docs/decision-log.md`
- `docs/acceptance-scenarios.md`
- `docs/docs-index.md`
- `docs/beauty_erp_v3_rebuild_plan.md`
- `docs/production-readiness-checklist.md`
- `docs/session-handoff-2026-03-21-checkpoint-8g.md`

## Security note
- Linux scheduler workflow still uses authenticated backend endpoints and permission checks.
- Cron registration scripts avoid destructive replacement of unrelated crontab entries.
- Runbook recommends low-privilege account and secure credential handling.

## Best next slice
- Keep next work small: Kubernetes CronJob wiring for orchestrated environments.
- After that, continue with optional advanced workflows.
