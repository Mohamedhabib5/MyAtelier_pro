# Guardrail Release Gate

## Purpose
- Define one fast, deterministic quality gate that runs on every pull request.
- Block merges that break architecture guardrails before broader regression suites run.

## CI command
- Guardrail profile command:
  - `cd backend && python -m pytest -m guardrail`
- Frontend build command:
  - `cd frontend && npm run build`
- GitHub Actions workflow:
  - `.github/workflows/guardrails.yml`

## Pass criteria
- `guardrails` job is `green` (all marked tests pass).
- `frontend-build` job is `green` (production build passes).
- No guardrail test is skipped due to missing config or runtime errors.

## Fail criteria
- Any guardrail test fails.
- Frontend build fails.
- Guardrail workflow fails to start or complete.
- Any guarded file-size boundary exceeds its configured limit.
- Any guarded module-boundary rule is violated (for example, API routes importing helper modules directly).

## What the guardrail profile covers now
- Write-route audit inventory alignment and explicit audit action declaration.
- Audit evidence checks for key write actions.
- Backend module boundary and service-size guardrails.
- Arabic/text integrity guardrails for user-facing critical paths.
- Frontend heavy-page size guardrails for operational screens.

## Operator action on failure
1. Fix the violating code or split oversized files.
2. Re-run locally:
   - `cd backend && python -m pytest -m guardrail`
   - `cd frontend && npm run build`
3. Push updated commit and confirm workflow is green before merge.

## Gate order
1. `guardrails` job runs first.
2. `frontend-build` runs only after `guardrails` succeeds.

## Branch protection
- Apply required checks using:
  - `guardrails`
  - `frontend-build`
- Rollout instructions:
  - `docs/branch-protection-guardrails.md`
- CI timing and troubleshooting runbook:
  - `docs/ci-gate-runbook.md`

## Scope note
- This release gate is intentionally narrow and fast.
- It does not replace broader module regression tests or full E2E validation.
- Broader nightly validation is defined separately:
  - `docs/nightly-full-regression.md`
- Nightly troubleshooting and artifact handling:
  - `docs/ci-gate-runbook.md`
