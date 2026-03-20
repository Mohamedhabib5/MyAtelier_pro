# Branch Controls Rules

## Scope of Checkpoint 5B
- This slice introduces active-branch context without redesigning the whole data model.
- The goal is to make branch switching visible and useful while keeping the checkpoint small.

## Included behavior
- The authenticated session stores one `active_branch_id`.
- Login resolves a default branch if the session does not already hold one.
- Settings can create a new branch.
- The shell can switch the active branch for the current session.
- Bookings and payments are now saved under the active branch.
- Dashboard and reports are filtered to the active branch.

## Intentionally shared data in this slice
- Customers remain company-wide.
- Services and departments remain company-wide.
- Dress resources remain company-wide.
- User accounts remain company-wide.

## Validation rules
- A branch code must stay unique within the company.
- A session cannot switch to a branch outside the current company.
- New bookings inherit the current active branch automatically.
- New payments inherit the current active branch automatically.
- Reports must not mix booking or payment totals from another branch.

## Security notes
- Branch switching is an authenticated server-side action.
- The active branch is validated from the database, not trusted from the browser alone.
- Branch-scoped endpoints still require their normal permission checks.
- This slice does not yet implement branch-specific roles or approval chains.

## Deferred after this slice
- branch-specific user permissions
- branch comparison reporting
- branch-scoped inventory or accounting periods
- branch deletion or archival workflows
