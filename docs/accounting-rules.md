# Accounting Rules

## Purpose
- This file defines the accounting assumptions introduced across the accounting checkpoints.
- The current implementation now includes the chart-of-accounts foundation, journal create/post/reverse workflows, a read-only trial balance, and automatic journal posting for payment receipts.

## Scope through Checkpoint 5C
- read-only trial balance endpoint
- trial balance filtering by date and fiscal period
- inclusion of posted and reversed journal effects only
- balance aggregation by account
- automatic posted journals for payment receipts
- reversal and replacement of linked journals when payment receipts are updated

## Out of scope after Checkpoint 5C
- tax engine
- inventory valuation
- customer invoice integration
- automatic revenue recognition from booking completion
- advanced financial statements
- branch-specific accounting ledgers

## Core accounting assumptions
- The accounting engine is company-scoped.
- Every journal entry belongs to exactly one company and one fiscal period.
- Journal entry lines are double-entry lines: a line cannot be both debit and credit, and cannot be zero on both sides.
- Journal statuses currently used are `draft`, `posted`, and `reversed`.
- Only `draft` manual entries may be updated.
- Reversal is done by creating a separate posted reversing entry, not by deleting history.
- Trial balance excludes `draft` entries and includes both `posted` and `reversed` entries because reversed entries remain part of accounting history.

## Chart of accounts foundation
The first default chart is intentionally small and operationally useful:
- `1000` الصندوق
- `1100` البنك
- `1200` ذمم العملاء
- `2100` عربون العملاء
- `3100` حقوق الملكية
- `4100` إيرادات الخدمات
- `5100` مصروفات تشغيلية

## Payment posting assumption in Checkpoint 5C
- all customer collections created from the payments module currently credit `2100 عربون العملاء`
- refunds from the payments module currently debit `2100 عربون العملاء`
- this keeps customer cash movements traceable without recognizing revenue too early
- final recognition into `4100 إيرادات الخدمات` is deferred to a later operational completion slice

## Trial balance interpretation
- `movement_debit` and `movement_credit` show period movement included in the report scope.
- `balance_debit` and `balance_credit` show the net balance side for each account.
- Zero rows may be hidden by default and shown explicitly through `include_zero_accounts=true`.

## Sequence foundation
- Journal entries reserve the document-sequence key `journal_entry`.
- The current default prefix is `JV`.
- Entry numbers are reserved when draft manual journals are created.
- Payment auto-posting also uses the same journal-entry sequence.

## Security and audit expectations
- Accounting routes must remain authenticated and authorized on the backend.
- Read access uses `accounting.view`.
- Create, post, update, and reverse actions use `accounting.manage`.
- Payment auto-posting is triggered server-side from `payments.manage` workflows and still records accounting audit entries.
- Posting and reversal actions must be audited.
- Posted financial documents must not be silently mutable.
