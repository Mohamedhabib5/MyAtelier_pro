# Nightly Failure Notifier Contract

## Purpose
- Define a stable payload contract for optional nightly-failure webhook notifications.
- Provide a simple rollout and verification checklist for operators.

## Source of truth
- Workflow file:
  - `.github/workflows/nightly-full-regression.yml`
- Job:
  - `notify-nightly-failure`
- Secret gate:
  - `NIGHTLY_FAILURE_WEBHOOK_URL`
- Optional in-app receiver (implemented in backend):
  - `POST /api/settings/ops/nightly/failure-report`
  - header: `X-Nightly-Token: <NIGHTLY_FAILURE_INGEST_TOKEN>`
  - snapshot read endpoint (settings permission required):
    - `GET /api/settings/ops/nightly/latest`
- GitHub Actions secrets for direct in-app ingest:
  - `NIGHTLY_FAILURE_INGEST_URL` (full URL to `/api/settings/ops/nightly/failure-report`)
  - `NIGHTLY_FAILURE_INGEST_TOKEN` (matches backend `NIGHTLY_FAILURE_INGEST_TOKEN`)

## Delivery behavior
- Notification is sent only when at least one nightly job fails.
- Notification is skipped (without failing workflow) when webhook secret is missing.
- Success-only nightly runs do not trigger webhook sends.
- In-app ingest send is skipped (without failing workflow) when ingest URL/token secrets are missing.

## Payload schema (v1)
- `event` (`string`): fixed value `nightly_full_regression_failed`
- `repository` (`string`): `<owner>/<repo>`
- `ref` (`string`): git ref used by workflow run
- `run_id` (`string`): GitHub Actions run id
- `run_attempt` (`string`): run attempt number
- `run_url` (`string`): direct URL to workflow run
- `results` (`object`):
  - `backend_focused_tests` (`string`): `success|failure|cancelled|skipped`
  - `frontend_build` (`string`): `success|failure|cancelled|skipped`
  - `e2e_smoke` (`string`): `success|failure|cancelled|skipped`
- `failed_at_utc` (`string`): UTC timestamp in ISO-8601 format

## Example payload
```json
{
  "event": "nightly_full_regression_failed",
  "repository": "example-org/myatelier_pro",
  "ref": "refs/heads/main",
  "run_id": "1234567890",
  "run_attempt": "1",
  "run_url": "https://github.com/example-org/myatelier_pro/actions/runs/1234567890",
  "results": {
    "backend_focused_tests": "success",
    "frontend_build": "failure",
    "e2e_smoke": "skipped"
  },
  "failed_at_utc": "2026-04-03T09:15:42Z"
}
```

## Receiver-side expectations
- Accept HTTP `POST` with JSON body.
- Return `2xx` for successful receipt.
- Keep processing idempotent using (`run_id`, `run_attempt`) as unique event key.
- Treat unknown fields as forward-compatible (ignore, do not fail).
- For MyAtelier backend receiver:
  - Require `X-Nightly-Token` and reject missing/invalid token with `403`.
  - Store latest payload snapshot for admin review and write audit event `ops.nightly_failure_reported`.

## Manual rollout and verification checklist
1. Confirm nightly workflow is enabled and visible in GitHub Actions.
2. Add repository secret `NIGHTLY_FAILURE_WEBHOOK_URL` with HTTPS endpoint.
3. Add repository secrets for in-app ingest:
   - `NIGHTLY_FAILURE_INGEST_URL`
   - `NIGHTLY_FAILURE_INGEST_TOKEN`
4. Set backend env `NIGHTLY_FAILURE_INGEST_TOKEN` to the same value used in GitHub secret.
5. Trigger `Nightly Full Regression` manually using `workflow_dispatch`.
6. Validate a success run does not call the webhook.
7. Trigger a controlled failure run (for example, temporary failing assertion on a throwaway branch).
8. Verify webhook receiver gets one payload with:
   - `event=nightly_full_regression_failed`
   - correct `run_url`
   - expected job `results` statuses
9. Confirm workflow summary shows notifier stage status and secret-configured flag.
10. Remove temporary failure change and rerun nightly workflow.
11. Document receiver ownership and on-call contact in operations notes.

## Token rotation and rollback
- Rotation:
  1. Generate a new strong token value.
  2. Update backend `NIGHTLY_FAILURE_INGEST_TOKEN`.
  3. Update GitHub secret `NIGHTLY_FAILURE_INGEST_TOKEN`.
  4. Trigger manual nightly run and verify ingest success.
- Rollback:
  - If ingest fails, temporarily clear `NIGHTLY_FAILURE_INGEST_URL` secret to disable direct ingest without touching other nightly jobs.
  - Keep `NIGHTLY_FAILURE_WEBHOOK_URL` enabled as fallback channel during incident handling.

## Security notes
- Keep webhook endpoint HTTPS-only.
- Do not include sensitive database or user payloads in notification body.
- Use endpoint-side authentication/validation when available (for example token/IP policy).
