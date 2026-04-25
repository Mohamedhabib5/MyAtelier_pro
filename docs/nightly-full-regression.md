# Nightly Full Regression

## Purpose
- Run a broader regression pack daily without slowing pull-request merge gates.
- Catch cross-module issues that are outside the lightweight PR gate profile.

## Workflow
- File: `.github/workflows/nightly-full-regression.yml`
- Triggers:
  - Scheduled daily run (`01:00 UTC`)
  - Manual run (`workflow_dispatch`)

## Job order
1. `backend-focused-tests`
2. `frontend-build`
3. `e2e-smoke` (depends on successful backend and frontend jobs)

## Backend focused test pack
- `tests/test_bookings.py`
- `tests/test_booking_revenue_recognition.py`
- `tests/test_payments.py`
- `tests/test_payment_void.py`
- `tests/test_exports.py`
- `tests/test_custody.py`

## E2E smoke scope
- `tests/e2e/smoke.spec.ts`
- `tests/e2e/lifecycle-archive-restore.spec.ts`

## Runtime notes
- E2E smoke uses SQLite runtime DB (`backend/e2e-runtime.db`) created from SQLAlchemy metadata.
- Backend and frontend servers are started inside runner process and stopped at job end.
- Playwright installs Chromium in CI during the e2e job.

## Artifacts and retention
- Artifacts are uploaded on every run (`if: always()`), including failed runs.
- Current artifacts:
  - `nightly-backend-focused-tests-logs`
  - `nightly-frontend-build-logs`
  - `nightly-e2e-runtime-logs`
  - `nightly-e2e-playwright-report` (when files exist)
- Retention policy:
  - `14` days for nightly artifacts

## Failure summary behavior
- On job failure, a short summary is written to `GITHUB_STEP_SUMMARY`.
- Summary includes:
  - failed job name
  - artifact names to inspect
  - local reproduction command

## Optional failure notifier
- Workflow includes `notify-nightly-failure` stage after all jobs.
- Notification sends only when at least one nightly job fails.
- External notification channel is optional and controlled by repository secret:
  - `NIGHTLY_FAILURE_WEBHOOK_URL`
- Direct MyAtelier ingest channel is optional and controlled by repository secrets:
  - `NIGHTLY_FAILURE_INGEST_URL`
  - `NIGHTLY_FAILURE_INGEST_TOKEN`
- If any optional channel secret is not configured, workflow still succeeds normally and only writes summary logs.
- Payload schema and rollout checklist:
  - `docs/nightly-failure-notifier-contract.md`

## Governance note
- This workflow is **not** a required branch protection check by default.
- Required PR checks remain:
  - `guardrails`
  - `frontend-build` (from guardrail workflow)
