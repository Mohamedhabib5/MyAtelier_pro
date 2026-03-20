# Docs Index

## Current reference docs
- `architecture.md`: system structure, checkpoint rules, and module boundaries.
- `beauty_erp_v3_rebuild_plan.md`: long-form rebuild plan for the whole product.
- `current-checkpoint.md`: exact state of the latest implemented checkpoint.
- `milestones.md`: checkpoint history and recommended next slice.
- `decision-log.md`: important decisions that future Codex sessions must keep.
- `security-baseline.md`: security rules that apply to all implementation slices.
- `acceptance-scenarios.md`: current acceptance expectations for implemented slices.
- `customers-rules.md`: customer-module scope, validation, and security rules.
- `services-and-departments-rules.md`: catalog-module scope, validation, and security rules.
- `dress-resources-rules.md`: dresses-module scope, validation, and security rules.
- `booking-rules.md`: bookings-module scope, validation, and security rules.
- `booking-revenue-recognition-rules.md`: booking completion accounting rules and completion-lock behavior.
- `payment-rules.md`: payments module scope, validation, voiding rules, and security rules.
- `payment-accounting-link-rules.md`: payment-to-accounting bridge assumptions and safeguards.
- `finance-dashboard-rules.md`: dashboard KPI scope, validation, and security rules.
- `reporting-rules.md`: broader reporting scope, validation, and security rules.
- `branch-controls-rules.md`: active-branch context, branch scoping, and branch-control security rules.
- `accounting-rules.md`: accounting foundation, trial balance, and posting assumptions.
- `export-rules.md`: export-center scope, CSV behavior, printable views, saved schedules, and export security rules.
- `arabic-text-integrity.md`: root cause, glossary choices, guardrails, and validation for Arabic text recovery.

## Handoff docs
- `session-handoff-2026-03-14.md`: early scaffold and planning handoff.
- `session-handoff-2026-03-15.md`: security hardening handoff.
- `session-handoff-2026-03-15-checkpoint-2b.md`: accounting foundation handoff.
- `session-handoff-2026-03-15-checkpoint-2c.md`: journal workflow handoff.
- `session-handoff-2026-03-15-checkpoint-2d.md`: trial balance handoff.
- `session-handoff-2026-03-15-checkpoint-2e.md`: accounting UI handoff.
- `session-handoff-2026-03-16-checkpoint-3a.md`: customers module handoff.
- `session-handoff-2026-03-16-checkpoint-3b.md`: services and departments handoff.
- `session-handoff-2026-03-16-checkpoint-3c.md`: dress resources handoff.
- `session-handoff-2026-03-16-checkpoint-4a.md`: bookings handoff.
- `session-handoff-2026-03-16-checkpoint-4b.md`: payments handoff.
- `session-handoff-2026-03-16-checkpoint-4c.md`: finance dashboard handoff.
- `session-handoff-2026-03-16-checkpoint-5a.md`: broader reporting handoff.
- `session-handoff-2026-03-16-checkpoint-5b.md`: branch-aware controls handoff.
- `session-handoff-2026-03-16-checkpoint-5c.md`: payment-accounting link handoff.
- `session-handoff-2026-03-16-checkpoint-6a.md`: export center handoff.
- `session-handoff-2026-03-16-checkpoint-6b.md`: technical cleanup and stability handoff.
- `session-handoff-2026-03-16-checkpoint-6c.md`: safe payment voiding handoff.
- `session-handoff-2026-03-16-checkpoint-6d.md`: printable export handoff.
- `session-handoff-2026-03-16-checkpoint-6e.md`: saved export schedules handoff.
- `session-handoff-2026-03-16-checkpoint-6f.md`: booking revenue-recognition handoff.
- `session-handoff-2026-03-17-checkpoint-7c.md`: backup-restore verification handoff.
- `session-handoff-2026-03-17-checkpoint-7d.md`: Arabic text integrity handoff.

## Rule for future docs
- Each new checkpoint must update the docs above if the current system behavior changes.
- Each major business module should get its own rules doc once implementation starts.
- Handoff docs should summarize exactly what was built, what was validated, and what remains next.
