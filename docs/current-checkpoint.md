# Current Checkpoint

## Purpose
- This file defines what has already been implemented so the project stays aligned with the Codex-first incremental delivery rule.
- The owner is not a programmer, so the repository must remain understandable as a sequence of small checkpoints.

## Current checkpoint
- The current repository state is `Checkpoint 7D`.
- `Checkpoint 7D` is the Arabic text integrity and encoding-guardrail slice.
- It restores critical Arabic wording, translates remaining user-facing backend validation messages, and adds source-level guardrails so corrupted text does not silently return.

## Included in Checkpoint 7D
- everything that was already included in `Checkpoint 7C`
- small Arabic text modules for critical flows such as auth, bookings, payments, and users
- restored Arabic wording in the booking and payment redesign flows
- Arabic translations for remaining user-facing backend messages in accounting, backup download, and export schedules
- booking dress behavior now depends on stable `department.code` rules instead of display text
- a source-level text-integrity check for `???`, replacement characters, mojibake patterns, and leftover English date-validation messages
- focused backend and Playwright validation for Arabic text integrity
- focused docs updates for the root cause and guardrails

## Explicitly not included yet
- end-user restore screen or restore button in the app
- unattended background execution for saved export schedules
- automatic reversal of booking revenue recognition
- tax-aware revenue recognition rules
- cross-branch comparison analytics
- customer-facing or mobile experiences
- final production environment checklist and deployment hardening

## Security review note
- text integrity is now guarded by automated source checks instead of visual review alone
- booking dress behavior no longer depends on fragile Arabic display names
- translated backend validation messages do not change any authorization or workflow enforcement
- reports, exports, and backup downloads still rely on backend authorization rather than frontend state

## Rule for next work
- The next Codex session should again select one small slice only.
- The best next slice is a short `production-readiness review` covering env values, cookies, CORS, secrets, and deployment notes.
- After that, only optional advanced workflows should remain.
