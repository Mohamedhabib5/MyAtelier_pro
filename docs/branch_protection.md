# Branch Protection Rules

For the **MyAtelier Pro** repository, the following branch protection rules MUST be enforced on the `main` branch to ensure a high-security standard (targeting 9.5/10 rating) and prevent accidental or malicious changes.

## 1. Require Pull Request reviews before merging
* **Required approving reviews**: `1` (or `2` for critical repositories).
* **Dismiss stale pull request approvals when new commits are pushed**: `Enabled`
* **Require review from Code Owners**: `Enabled` 
  *(This relies on `.github/CODEOWNERS` to ensure backend code is reviewed by the backend team, security changes by the security team, etc.)*
* **Restrict who can dismiss pull request reviews**: `Enabled` (Only Admin/Tech Lead).

## 2. Require status checks to pass before merging
* **Require branches to be up to date before merging**: `Enabled`
* **Status checks that are required**:
  - `backend-test` (from `.github/workflows/ci.yml`)
  - `frontend-test` (from `.github/workflows/ci.yml`)
  *(All Guardrail tests and functional tests must pass.)*

## 3. Require conversation resolution before merging
* `Enabled`
*(All PR comments must be resolved before the code can be merged.)*

## 4. Require signed commits
* `Enabled`
*(Ensures all commits are verified via GPG/SSH keys.)*

## 5. Include administrators
* `Enabled`
*(Branch protection rules apply to repository administrators as well, preventing admins from bypassing CI or code review.)*

## 6. Restrict who can push to matching branches
* `Enabled` (Only designated release managers or specific service accounts can directly push/merge after approval.)

---

*Note: Enforcing these rules is critical to passing the final production-ready security audit.*
