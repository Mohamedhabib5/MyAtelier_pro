# CI Gate Runbook

## Purpose
- Provide a quick operator guide for expected CI gate timing and common failure recovery.
- Keep pull-request gate handling consistent across sessions.

## Gate sequence
1. `guardrails` (backend marker profile)
2. `frontend-build` (depends on `guardrails`)

Workflow reference:
- `.github/workflows/guardrails.yml`

## Expected timing benchmarks
- `guardrails`:
  - Typical: `2-5` minutes
  - Slow-path (cold cache or heavy queue): up to `8` minutes
- `frontend-build`:
  - Typical: `2-6` minutes
  - Slow-path (cold npm cache): up to `10` minutes
- Combined expected end-to-end:
  - Typical: `5-11` minutes
  - Slow-path: `12-18` minutes

## Fast local reproduction
1. Backend guardrails:
   - `cd backend && python -m pytest -m guardrail`
2. Frontend production build:
   - `cd frontend && npm run build`

## Common failure patterns and fixes
- `guardrails` fails with size-limit assertion:
  - Split oversized module/page into focused helper components.
  - Re-run local guardrail profile.
- `guardrails` fails with module-boundary import assertion:
  - Move route-level direct helper imports back to stable service entrypoints.
  - Re-run local guardrail profile.
- `guardrails` fails with audit-route inventory mismatch:
  - Update write-route policy inventory and expected actions for new write routes.
  - Re-run local guardrail profile.
- `frontend-build` fails with TypeScript error:
  - Fix types or imports introduced in the PR and re-run `npm run build`.
- `frontend-build` fails with missing dependency lock mismatch:
  - Run `npm install` locally, verify lockfile consistency, and commit lock updates when needed.

## Flaky failure handling
1. Re-run failed jobs once from GitHub Actions UI.
2. If the same failure repeats, treat as deterministic and fix code/docs.
3. If failure differs between reruns, capture logs and annotate PR with:
   - failing job
   - failing step
   - first failing line
   - rerun count

## Escalation guideline
- Escalate to maintainer review when:
  - repeated workflow infra/network failures exceed `3` reruns in the same PR, or
  - required checks are green locally but red in CI after two full reruns.

## Nightly workflow triage
- Nightly workflow reference:
  - `.github/workflows/nightly-full-regression.yml`
- Inspect artifacts first when nightly fails:
  - `nightly-backend-focused-tests-logs`
  - `nightly-frontend-build-logs`
  - `nightly-e2e-runtime-logs`
  - `nightly-e2e-playwright-report`
- Artifact retention:
  - `14` days
- Optional notifier secret:
  - `NIGHTLY_FAILURE_WEBHOOK_URL`
- Optional direct-ingest secrets:
  - `NIGHTLY_FAILURE_INGEST_URL`
  - `NIGHTLY_FAILURE_INGEST_TOKEN`
- Notifier payload contract and rollout checklist:
  - `docs/nightly-failure-notifier-contract.md`
