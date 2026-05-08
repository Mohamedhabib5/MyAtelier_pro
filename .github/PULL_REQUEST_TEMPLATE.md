# Enterprise Change Request (CR) / Pull Request

## 0) Summary of Changes
[Provide a high-level summary of what this PR accomplishes]

## 1) Golden Baseline Verification
- [ ] I have run the full backend test suite (`pytest`) and it is 100% green.
- [ ] I have run the E2E smoke tests and they are passing.
- [ ] This PR does not break existing features (Non-Regression).

## 2) Traceability & Audit
- [ ] Every new 'Write' route has been added to `WRITE_ROUTE_AUDIT_POLICY`.
- [ ] Every business mutation includes a `record_audit` call with a literal action string.
- [ ] I have verified that the `test_audit_route_inventory_guardrails.py` test passes.

## 3) Database & Schema
- [ ] Any schema changes are accompanied by an Alembic migration.
- [ ] Mandatory fields added to models are also added to Test Factories and E2E payloads.

## 4) Documentation
- [ ] I have updated `ai_rules.md` if new architectural patterns were introduced.
