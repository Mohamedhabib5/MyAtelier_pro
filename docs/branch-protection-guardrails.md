# Branch Protection For Guardrail Gates

## Purpose
- Make CI gates enforceable at merge time, not optional.
- Ensure no PR is merged unless required checks are green.

## Required checks (exact job names)
- `guardrails`
- `frontend-build`

## Non-required nightly workflow
- Nightly broader regression remains optional and should not be required for PR merge:
  - `.github/workflows/nightly-full-regression.yml`

## Recommended GitHub settings
1. Open repository `Settings` -> `Branches`.
2. Create or edit branch protection rule for your default branch (`main` or `master`).
3. Enable:
   - `Require a pull request before merging`
   - `Require status checks to pass before merging`
4. Add required status checks:
   - `guardrails`
   - `frontend-build`
5. Enable:
   - `Require branches to be up to date before merging`
   - `Do not allow bypassing the above settings` (for non-owner roles, if governance requires strict enforcement)

## Operational notes
- Workflow file: `.github/workflows/guardrails.yml`
- Gate order is enforced by CI dependency (`frontend-build` depends on `guardrails`).
- If a required check name changes in workflow, update this doc and branch rule immediately.

## Rollout checklist
1. Merge workflow and docs updates to default branch.
2. Run one PR to confirm both checks appear in GitHub status checks.
3. Add both checks to branch protection required list.
4. Verify merge is blocked when either check fails.
5. Record completion in next checkpoint handoff.
