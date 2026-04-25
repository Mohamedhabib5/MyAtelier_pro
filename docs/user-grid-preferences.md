# User Grid Preferences

## Purpose
- Persist AG Grid preferences per authenticated user on the backend.
- Reduce preference drift when users switch devices or browsers.

## Implemented Scope (`Checkpoint 10A - phase 1/2`)
- New user-scoped preference API:
  - `GET /api/users/me/grid-preferences/{table_key}`
  - `PUT /api/users/me/grid-preferences/{table_key}`
- Backend persistence model:
  - table: `user_grid_preferences`
  - unique key: `(user_id, table_key)`
  - payload: JSON state (`columnState`, `filterModel`, `pageSize`)
- Audit coverage:
  - update action: `user.grid_preferences_updated`
  - write-route policy includes the new `PUT` route.
- Frontend integration:
  - grid hook now loads/saves server preferences for authenticated users.
  - local storage remains a fallback cache per user/table key.
  - conflict strategy is now explicit: newer state wins on initial hydration (`local.savedAt` vs `server.updated_at`).
  - save loop is debounced and avoids redundant writes when state already matches last synced payload.

## Conflict and Migration Strategy
- Local format now stores an envelope:
  - `state`
  - `savedAt` (epoch ms)
- Legacy local state (without envelope) is still accepted and normalized.
- During hydration:
  - if server preference is newer, server state is applied
  - if local cache is newer, local state is kept and re-synced to backend
- This allows safe migration from local-only history without dropping user tweaks.

## Validation
- Backend tests:
  - `backend/tests/test_user_grid_preferences.py`
  - `backend/tests/test_audit_route_inventory_guardrails.py`
- Frontend validation:
  - `npm.cmd run build` (passed)
- Persistence smoke coverage:
  - backend logout/login persistence test added
  - Playwright scenario added: `frontend/tests/e2e/grid-preferences-persistence.spec.ts`
